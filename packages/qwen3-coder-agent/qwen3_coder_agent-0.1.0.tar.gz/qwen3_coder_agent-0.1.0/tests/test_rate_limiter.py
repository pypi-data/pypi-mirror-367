"""Tests for rate_limiter.py"""
import time
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from qwen3_coder.rate_limiter import RateLimiter
from qwen3_coder.exceptions import RateLimitError

@pytest.fixture
def rate_limiter():
    """Fixture providing a clean RateLimiter instance for each test."""
    return RateLimiter()

def test_initialization(rate_limiter):
    """Test that RateLimiter initializes with default values."""
    assert rate_limiter.rpm_limit == 60
    assert rate_limiter.tpm_limits['input'] == 90000
    assert rate_limiter.tpm_limits['output'] == 30000
    assert rate_limiter.safety_margin == 0.8
    assert rate_limiter.min_wait_time == 0.1
    assert rate_limiter.total_requests == 0
    assert rate_limiter.total_tokens['input'] == 0
    assert rate_limiter.total_tokens['output'] == 0

def test_record_request(rate_limiter):
    """Test recording a request updates the appropriate counters."""
    rate_limiter.record_request(input_tokens=100, output_tokens=50)
    
    assert rate_limiter.total_requests == 1
    assert rate_limiter.total_tokens['input'] == 100
    assert rate_limiter.total_tokens['output'] == 50
    assert len(rate_limiter.request_timestamps) == 1
    assert len(rate_limiter.token_windows['input']) == 1
    assert len(rate_limiter.token_windows['output']) == 1
    assert rate_limiter.token_windows['input'][0][1] == 100
    assert rate_limiter.token_windows['output'][0][1] == 50

def test_prune_old_requests(rate_limiter):
    """Test that old requests are pruned from tracking."""
    # Add some old requests
    old_time = time.time() - 120  # 2 minutes ago
    rate_limiter.request_timestamps.append(old_time)
    rate_limiter.token_windows['input'].append((old_time, 100))
    rate_limiter.token_windows['output'].append((old_time, 50))
    
    # Add a recent request
    rate_limiter.record_request(input_tokens=200, output_tokens=100)
    
    # Old requests should be pruned
    assert len(rate_limiter.request_timestamps) == 1
    assert len(rate_limiter.token_windows['input']) == 1
    assert len(rate_limiter.token_windows['output']) == 1

def test_get_current_usage(rate_limiter):
    """Test getting current usage statistics."""
    # Add some requests
    for _ in range(3):
        rate_limiter.record_request(input_tokens=100, output_tokens=50)
    
    usage = rate_limiter.get_current_usage()
    
    assert usage['rpm'] == 3
    assert usage['tpm_input'] == 300
    assert usage['tpm_output'] == 150
    assert 0 < usage['rpm_pct'] <= 100
    assert 0 < usage['tpm_input_pct'] <= 100
    assert 0 < usage['tpm_output_pct'] <= 100

def test_calculate_wait_time_rpm(rate_limiter):
    """Test calculating wait time based on RPM limits."""
    # Fill up the RPM limit
    for _ in range(60):  # Default limit is 60 RPM
        rate_limiter.record_request()
    
    # Should need to wait about 60 seconds for the window to slide
    wait_time = rate_limiter.calculate_wait_time()
    assert 50 < wait_time <= 60  # Should be close to 60 seconds

def test_calculate_wait_time_tpm(rate_limiter):
    """Test calculating wait time based on TPM limits."""
    # Use up most of the input token limit
    rate_limiter.record_request(input_tokens=80000)  # 80% of 100k default
    
    # Request that would put us over the limit
    wait_time = rate_limiter.calculate_wait_time(expected_input_tokens=30000)
    assert wait_time > 0  # Should need to wait

def test_check_rate_limit_rpm(rate_limiter):
    """Test RPM rate limit checking."""
    # Fill up the RPM limit
    for _ in range(60):  # Default limit is 60 RPM
        rate_limiter.record_request()
    
    # Next request should be rate limited
    with pytest.raises(RateLimitError) as exc_info:
        rate_limiter.check_rate_limit()
    
    assert "RPM" in str(exc_info.value)
    assert exc_info.value.retry_after > 0

def test_check_rate_limit_tpm(rate_limiter):
    """Test TPM rate limit checking."""
    # Use up the input token limit
    rate_limiter.record_request(input_tokens=90000)  # Default limit is 90k
    
    # Next request should be rate limited
    with pytest.raises(RateLimitError) as exc_info:
        rate_limiter.check_rate_limit(expected_input_tokens=10000)
    
    assert "Input token limit" in str(exc_info.value)
    assert exc_info.value.retry_after > 0

@pytest.mark.asyncio
async def test_wait_if_needed(rate_limiter):
    """Test async waiting when rate limits are approached."""
    # Set up the rate limiter to think we're close to the limit
    with patch.object(rate_limiter, 'calculate_wait_time', return_value=0.1):
        start_time = time.time()
        await rate_limiter.wait_if_needed(expected_input_tokens=1000)
        elapsed = time.time() - start_time
        
        # Should have waited about 0.1 seconds
        assert 0.09 <= elapsed <= 0.15
        assert rate_limiter.rate_limit_hits == 1

def test_update_limits_from_headers(rate_limiter):
    """Test updating rate limits from HTTP headers."""
    headers = {
        'X-RateLimit-Limit-RPM': '120',
        'X-RateLimit-Limit-TPM-INPUT': '180000',
        'X-RateLimit-Limit-TPM-OUTPUT': '60000'
    }
    
    rate_limiter.update_limits(headers)
    
    assert rate_limiter.rpm_limit == 120
    assert rate_limiter.tpm_limits['input'] == 180000
    assert rate_limiter.tpm_limits['output'] == 60000

    # Test with partial headers
    rate_limiter.update_limits({'X-RateLimit-Limit-RPM': '60'})
    assert rate_limiter.rpm_limit == 60
    # Other limits should remain unchanged
    assert rate_limiter.tpm_limits['input'] == 180000
    assert rate_limiter.tpm_limits['output'] == 60000

def test_get_stats(rate_limiter):
    """Test getting rate limiting statistics."""
    # Record some usage
    rate_limiter.record_request(input_tokens=3000, output_tokens=1500)
    rate_limiter.record_request(input_tokens=3000, output_tokens=1500)
    
    stats = rate_limiter.get_stats()
    
    assert stats['total_requests'] == 2
    assert stats['total_input_tokens'] == 6000
    assert stats['total_output_tokens'] == 3000
    assert stats['current_rpm'] == 2
    assert stats['current_tpm_input'] == 6000
    assert stats['current_tpm_output'] == 3000
    assert stats['rate_limit_hits'] == 0

def test_min_wait_time(rate_limiter):
    """Test that minimum wait time between requests is enforced."""
    # First request
    rate_limiter.record_request()
    
    # Should need to wait at least min_wait_time
    wait_time = rate_limiter.calculate_wait_time()
    assert 0.09 <= wait_time <= 0.11  # Should be about 0.1 seconds
    
    # After waiting, should be able to proceed
    time.sleep(0.11)
    wait_time = rate_limiter.calculate_wait_time()
    assert wait_time == 0

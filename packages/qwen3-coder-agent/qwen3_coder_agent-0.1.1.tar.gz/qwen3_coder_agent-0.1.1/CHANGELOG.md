# Changelog

All notable changes to the Qwen3-Coder Terminal Agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-08-07

### Fixed
- Resolved dependency conflict between autopep8 and flake8 by explicitly requiring pycodestyle>=2.12.0
- Updated installation documentation to help users resolve common dependency issues
- Improved error handling for dependency resolution during installation

## [0.1.0] - 2025-08-07

### Added
- Initial release of Qwen3-Coder Terminal Agent
- Core chat interface with Qwen3-Coder model integration
- Secure API key management via environment variables
- Hybrid token counting with local estimation and API validation
- Adaptive rate limiting with predictive throttling
- Context management with dynamic windowing
- Session persistence (save/load conversations)
- Terminal commands: /clear, /tokens, /sessions, /save, /load
- Real-time token usage display
- Comprehensive test suite

### Changed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

from setuptools import setup, find_packages
import pathlib

# Read the contents of README.md
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="qwen3-coder-agent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based agent for interacting with Qwen3-Coder models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/qwen3-coder-agent",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        'qwen3_coder': ['*.json', '*.md', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'qwen3c=qwen3_coder.cli:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.3.1',
            'pytest-cov>=4.0.0',
            'mypy>=1.3.0',
            'black>=23.3.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Terminals",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
    keywords='qwen3 coder ai assistant terminal cli code generation',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/qwen3-coder-agent/issues',
        'Source': 'https://github.com/yourusername/qwen3-coder-agent',
        'Documentation': 'https://github.com/yourusername/qwen3-coder-agent#readme',
    },
)

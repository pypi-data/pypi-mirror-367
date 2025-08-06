# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-01-27

### Fixed
- **Dependency Resolution**: Fixed Python version compatibility issues that were causing dependency resolution failures
- **Python Version Support**: Updated `requires-python` to explicitly exclude Python 3.13 (`>=3.11,<3.13`)
- **Lock File**: Regenerated `uv.lock` with correct Python version constraints
- **Tool Configuration**: Updated Black target version to support Python 3.11 and 3.12

### Changed
- Updated Python version requirements to prevent compatibility issues with Python 3.13
- Improved dependency resolution for better package installation experience

## [0.2.1] - Previous Release

### Added
- Initial release with core functionality
- LangGraph-based agent for parsing result files
- Support for multiple LLM providers (GROQ, OpenAI, Anthropic, Google, Ollama)
- CLI interface with comprehensive options
- YAML configuration support
- Structured JSON output for extracted metrics

### Features
- Intelligent parsing of raw result files
- Support for various file formats
- Configurable metrics extraction
- Verbose logging and debugging options
- Pretty-printed JSON output
- Comprehensive test coverage

## [0.1.0] - Initial Development

- Initial project setup and development 
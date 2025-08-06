# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with `pyproject.toml`
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline
- Multi-environment testing with tox
- Comprehensive contributing guidelines
- Automated release workflow
- Security scanning in CI

### Changed
- Migrated from `setup.py` to `pyproject.toml`
- Updated Python version support to 3.8-3.13
- Improved test coverage and organization

## [0.1.0a1] - 2024-01-XX

### Added
- Initial pre-release of PromptLifter
- LangGraph-powered context expansion
- Support for multiple LLM providers (OpenAI, Anthropic, Google, Custom)
- Tavily web search integration
- Pinecone vector search with configurable relevance scoring
- Subtask decomposition and parallel processing
- Structured output generation
- Comprehensive test suite (28 tests, 40% coverage)
- Configuration validation and error handling
- Logging and debugging capabilities

### Features
- **LLM Integration**: Support for OpenAI, Anthropic, Google, and custom LLM endpoints
- **Search Capabilities**: Web search via Tavily and vector search via Pinecone
- **Workflow Orchestration**: LangGraph-based workflow management
- **Parallel Processing**: Concurrent execution of search and LLM tasks
- **Configurable Relevance**: Pinecone similarity threshold filtering
- **Error Handling**: Graceful degradation and comprehensive error reporting
- **Documentation**: Comprehensive README and setup guide

### Technical Details
- **Python Version**: 3.8+
- **Dependencies**: LangGraph, httpx, python-dotenv, OpenAI, Anthropic, Google AI, Pinecone, Tavily
- **Architecture**: Modular node-based workflow with async processing
- **Testing**: pytest with async support and coverage reporting 
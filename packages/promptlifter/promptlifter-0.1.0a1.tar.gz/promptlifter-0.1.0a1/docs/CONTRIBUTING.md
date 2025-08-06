# Contributing to PromptLifter

Thank you for your interest in contributing to PromptLifter! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/promptlifter.git
   cd promptlifter
   ```
3. **Set up development environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## 🧪 Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/promptlifter.git
cd promptlifter

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Environment Configuration
Create a `.env` file with your API keys:
```env
# Required for development
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
TAVILY_API_KEY=your-tavily-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX=your-index-name
```

## 📝 Code Style

We use several tools to maintain code quality:

### Black (Code Formatting)
```bash
# Format code
black promptlifter tests

# Check formatting
black --check promptlifter tests
```

### isort (Import Sorting)
```bash
# Sort imports
isort promptlifter tests

# Check import sorting
isort --check-only --diff promptlifter tests
```

### Flake8 (Linting)
```bash
# Run linter
flake8 promptlifter tests
```

### MyPy (Type Checking)
```bash
# Run type checker
mypy promptlifter
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=promptlifter --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test class
pytest tests/test_config.py::TestConfigValidation

# Run specific test
pytest tests/test_config.py::TestConfigValidation::test_validate_url_valid
```

### Test Categories
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **Slow tests**: Tests that take longer to run (marked with `@pytest.mark.slow`)
- **LLM tests**: Tests requiring LLM services (marked with `@pytest.mark.llm`)
- **Search tests**: Tests requiring search services (marked with `@pytest.mark.search`)

### Writing Tests
1. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

2. **Use descriptive test names**:
   ```python
   def test_validate_url_with_valid_https_url():
       # Test implementation
   ```

3. **Use appropriate markers**:
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       # Async test implementation
   ```

4. **Mock external dependencies**:
   ```python
   @patch('promptlifter.nodes.run_tavily_search.httpx.AsyncClient')
   async def test_tavily_search_success(self, mock_client):
       # Test with mocked client
   ```

## 🔄 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write code following the style guidelines
- Add tests for new functionality
- Update documentation if needed

### 3. Run Quality Checks
```bash
# Run all checks
tox

# Or run individual checks
tox -e lint
tox -e type-check
tox -e py311
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 📋 Pull Request Guidelines

### Before Submitting
1. **Ensure all tests pass**:
   ```bash
   pytest
   ```
2. **Run quality checks**:
   ```bash
   tox
   ```
3. **Update documentation** if needed
4. **Add tests** for new functionality

### Pull Request Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏗️ Project Structure

```
promptlifter/
├── promptlifter/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application entry point
│   ├── graph.py           # LangGraph workflow
│   ├── config.py          # Configuration
│   └── nodes/             # Workflow nodes
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/               # GitHub workflows
├── pyproject.toml         # Project configuration
├── tox.ini               # Multi-environment testing
└── .pre-commit-config.yaml # Code quality hooks
```

## 🐛 Bug Reports

When reporting bugs, please include:
1. **Environment details**: Python version, OS, dependencies
2. **Steps to reproduce**: Clear, step-by-step instructions
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Error messages**: Full error traceback if applicable

## 💡 Feature Requests

When requesting features, please include:
1. **Use case**: Why this feature is needed
2. **Proposed solution**: How you think it should work
3. **Alternatives considered**: Other approaches you've thought about

## 📞 Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Documentation**: Check the README and setup guide first

## 📄 License

By contributing to PromptLifter, you agree that your contributions will be licensed under the MIT License. 
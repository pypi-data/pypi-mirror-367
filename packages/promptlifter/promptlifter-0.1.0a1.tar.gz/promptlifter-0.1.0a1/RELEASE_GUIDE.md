# PromptLifter Release Guide

This guide walks you through the process of releasing PromptLifter to PyPI.

## 🚀 Pre-Release Checklist

### 1. Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install release dependencies
pip install -e ".[dev]"
```

### 2. Quality Assurance

```bash
# Run all tests
pytest tests/ -v

# Run quality checks
black --check promptlifter tests
flake8 promptlifter tests --max-line-length=88
mypy promptlifter

# Run full test suite with tox
tox
```

### 3. Version Management

Update version numbers in:
- `pyproject.toml` - `version = "0.1.0a1"`
- `promptlifter/__init__.py` - `__version__ = "0.1.0a1"`
- `docs/CHANGELOG.md` - Add release entry with date

### 4. Documentation Updates

- [ ] README.md is up to date
- [ ] CHANGELOG.md has release notes
- [ ] All documentation links work
- [ ] Installation instructions are correct

## 📦 Building the Package

### 1. Clean Build Environment

```bash
# Remove previous builds
rm -rf build/ dist/ *.egg-info/
```

### 2. Build Package

```bash
# Build source distribution and wheel
python -m build
```

### 3. Verify Package

```bash
# Check package for issues
python -m twine check dist/*

# List package contents
tar -tzf dist/promptlifter-*.tar.gz
```

## 🔐 PyPI Setup

### 1. Create PyPI Account

1. Go to [PyPI](https://pypi.org/account/register/)
2. Create an account
3. Enable two-factor authentication

### 2. Create TestPyPI Account

1. Go to [TestPyPI](https://test.pypi.org/account/register/)
2. Create an account
3. Enable two-factor authentication

### 3. Generate API Tokens

#### PyPI Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name (e.g., "PromptLifter Release")
4. Select "Entire account (all projects)"
5. Copy the token

#### TestPyPI Token
1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name (e.g., "PromptLifter Test Release")
4. Select "Entire account (all projects)"
5. Copy the token

### 4. Configure Credentials

#### Option 1: Environment Variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
export TWINE_REPOSITORY_URL=https://upload.pypi.org/legacy/
```

#### Option 2: .pypirc File
```bash
# Run setup script
python scripts/setup_pypi.py

# Edit ~/.pypirc with your tokens
nano ~/.pypirc
```

Example `.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-actual-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

## 🧪 Test Release

### 1. Upload to TestPyPI

```bash
# Using the release script
python scripts/release.py test

# Or manually
python -m twine upload --repository testpypi dist/*
```

### 2. Test Installation

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ promptlifter

# Test functionality
python -c "import promptlifter; print(promptlifter.__version__)"
```

### 3. Verify TestPyPI

1. Go to [TestPyPI PromptLifter](https://test.pypi.org/project/promptlifter/)
2. Verify package details
3. Check installation instructions

## 🚀 Production Release

### 1. Final Verification

```bash
# Run all checks one more time
python scripts/release.py test
```

### 2. Upload to PyPI

```bash
# Using the release script
python scripts/release.py release

# Or manually
python -m twine upload dist/*
```

### 3. Verify Release

1. Go to [PyPI PromptLifter](https://pypi.org/project/promptlifter/)
2. Verify package details
3. Test installation:
   ```bash
   pip install promptlifter
   python -c "import promptlifter; print(promptlifter.__version__)"
   ```

## 🔄 Automated Releases

### GitHub Actions Setup

1. Add repository secrets:
   - `PYPI_TOKEN`: Your PyPI API token
   - `TEST_PYPI_TOKEN`: Your TestPyPI API token

2. Create a release tag:
   ```bash
   git tag v0.1.0a1
   git push origin v0.1.0a1
   ```

3. GitHub Actions will automatically:
   - Run tests
   - Build package
   - Upload to PyPI

## 📋 Release Checklist

### Pre-Release
- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Linting passes (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] Version numbers are updated
- [ ] CHANGELOG.md is updated

### Build
- [ ] Clean build environment
- [ ] Build package successfully
- [ ] Package validation passes
- [ ] Package contents are correct

### Test Release
- [ ] Upload to TestPyPI
- [ ] Install from TestPyPI
- [ ] Basic functionality test
- [ ] Verify TestPyPI page

### Production Release
- [ ] Upload to PyPI
- [ ] Verify PyPI page
- [ ] Install from PyPI
- [ ] Test command-line interface
- [ ] Test import functionality

### Post-Release
- [ ] Update GitHub release notes
- [ ] Announce on social media
- [ ] Update documentation links
- [ ] Monitor for issues

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clean and rebuild
rm -rf build/ dist/ *.egg-info/
python -m build
```

#### Upload Errors
```bash
# Check credentials
python -m twine check dist/*

# Verify token permissions
# Ensure token has "Entire account" scope
```

#### Installation Issues
```bash
# Test with verbose output
pip install -v promptlifter

# Check Python version compatibility
python --version
```

### Version Conflicts

If a version already exists:
1. Update version in `pyproject.toml`
2. Update version in `promptlifter/__init__.py`
3. Update `CHANGELOG.md`
4. Rebuild and upload

## 📞 Support

For release issues:
1. Check [PyPI Help](https://pypi.org/help/)
2. Review [Twine Documentation](https://twine.readthedocs.io/)
3. Check GitHub Issues for similar problems

## 🎯 Next Steps

After successful release:
1. Monitor PyPI download statistics
2. Respond to user feedback
3. Plan next release features
4. Update development roadmap 
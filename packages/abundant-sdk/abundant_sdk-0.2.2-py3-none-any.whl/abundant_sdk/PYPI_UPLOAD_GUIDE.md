# PyPI Upload Guide for Abundant SDK

This guide walks you through the process of uploading the Abundant SDK to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **Test PyPI Account**: Create an account on [Test PyPI](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens for both PyPI and Test PyPI
4. **Build Tools**: Install required build tools

## Setup

### 1. Install Build Dependencies

```bash
pip install -r requirements-build.txt
```

### 2. Configure Twine

Create a `~/.pypirc` file with your credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Building and Uploading

### Option 1: Using the Build Script

```bash
# Build and upload to Test PyPI (recommended first)
python scripts/build_and_upload.py --test

# Build and upload to production PyPI
python scripts/build_and_upload.py
```

### Option 2: Manual Steps

```bash
# 1. Clean previous builds
python -m build --clean

# 2. Build the package
python -m build

# 3. Check the built package
python -m twine check dist/*

# 4. Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# 5. Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ abundant-sdk

# 6. Test the import
python test_import.py

# 7. Upload to production PyPI
python -m twine upload dist/*
```

## Verification

### Test Installation

After uploading to Test PyPI, test the installation:

```bash
# Create a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ abundant-sdk
```

### Test Usage

Create a simple test script:

```python
import asyncio
from abundant_sdk import Client

async def test_sdk():
    # This will fail without a real API key, but tests the import
    client = Client(api_key="test")
    print("✓ Client created successfully")

asyncio.run(test_sdk())
```

## Version Management

### Updating Version

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.2.1"  # Increment as needed
   ```

2. Update version in `src/abundant_sdk/__init__.py`:
   ```python
   __version__ = "0.2.1"
   ```

3. Update version history in `README.md`

### Version Numbering

- **Major.Minor.Patch** (e.g., 0.2.1)
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your API tokens in `~/.pypirc`
   - Ensure tokens have upload permissions

2. **Package Already Exists**
   - Increment version number
   - Delete old builds: `rm -rf dist/ build/`

3. **Import Errors After Installation**
   - Check that all files are included in `MANIFEST.in`
   - Verify package structure in `pyproject.toml`

4. **Build Errors**
   - Check Python version compatibility
   - Verify all dependencies are available

### Useful Commands

```bash
# Check package structure
python -c "import abundant_sdk; print(abundant_sdk.__file__)"

# List installed package info
pip show abundant-sdk

# Uninstall for testing
pip uninstall abundant-sdk

# Check package metadata
python -m twine check dist/*
```

## Security Notes

- Never commit API tokens to version control
- Use environment variables for CI/CD pipelines
- Regularly rotate API tokens
- Test on Test PyPI before production

## CI/CD Integration

For automated releases, consider using GitHub Actions:

```yaml
name: Upload to PyPI
on:
  release:
    types: [published]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements-build.txt
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m build
        python -m twine upload dist/*
``` 
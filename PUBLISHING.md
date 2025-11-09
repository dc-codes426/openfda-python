# Publishing Guide for openfda-python

This guide explains how to publish the `openfda-python` package to PyPI.

## Prerequisites

1. Install build tools:
```bash
pip install build twine
```

2. Create accounts (if you haven't already):
   - PyPI account: https://pypi.org/account/register/
   - TestPyPI account (for testing): https://test.pypi.org/account/register/

3. Set up API tokens (recommended over passwords):
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

## Before Publishing

### 1. Update Version

Edit `pyproject.toml` and update the version number:
```toml
[project]
version = "0.1.0"  # Update this
```

### 2. Update CHANGELOG.md

Add entry for the new version:
```markdown
## [0.1.0] - 2025-11-08
### Added
- Feature descriptions
```

### 3. Update Personal Information

Edit `pyproject.toml` to replace placeholder information:
- Author name and email
- GitHub repository URL
- Any other project-specific details

### 4. Run Tests

Ensure all tests pass:
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code quality
ruff check src/
black --check src/
```

### 5. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

## Build the Package

Build both source distribution and wheel:

```bash
python -m build
```

This creates two files in the `dist/` directory:
- `openfda_python-0.1.0.tar.gz` (source distribution)
- `openfda_python-0.1.0-py3-none-any.whl` (wheel)

## Verify the Build

Check the package contents:

```bash
# List contents of wheel
unzip -l dist/openfda_python-0.1.0-py3-none-any.whl

# Check package metadata
twine check dist/*
```

## Test on TestPyPI (Recommended)

Before publishing to the real PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps openfda-python

# Test the package
python -c "from api_client import FDAClient; print('Import successful!')"
```

## Publish to PyPI

Once you've verified everything works on TestPyPI:

```bash
# Upload to PyPI
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## After Publishing

1. Create a git tag for the release:
```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

2. Create a GitHub release (optional but recommended):
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Select the tag you just created
   - Add release notes from CHANGELOG.md

3. Verify installation from PyPI:
```bash
pip install openfda-python
```

## Using .pypirc (Optional)

Create `~/.pypirc` to store credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourActualTokenHere

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestPyPITokenHere
```

**Security Note**: Keep your `.pypirc` secure and never commit it to version control!

## Updating the Package

To publish a new version:

1. Make your code changes
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Clean, build, and publish:
```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*
```

## Common Issues

### Issue: "File already exists"
**Solution**: You cannot re-upload the same version. Increment the version number.

### Issue: "Invalid distribution"
**Solution**: Run `twine check dist/*` to identify issues.

### Issue: "403 Forbidden"
**Solution**: Check your API token is correct and has upload permissions.

### Issue: Package name already taken
**Solution**: Choose a different package name and update `pyproject.toml`.

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 517/518 - Build System](https://www.python.org/dev/peps/pep-0517/)

## Quick Reference

```bash
# Complete publishing workflow
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Then publish for real
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

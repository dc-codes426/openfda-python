# Pre-Publish Checklist

Use this checklist before publishing to PyPI to ensure everything is ready.

## Code Quality

- [ ] All tests pass (`pytest tests/`)
- [ ] Code is formatted (`black src/`)
- [ ] Linting passes (`ruff check src/`)
- [ ] No obvious bugs or issues
- [ ] Example code in README works

## Documentation

- [ ] README.md is complete and accurate
- [ ] All usage examples work
- [ ] Installation instructions are correct
- [ ] API documentation is clear
- [ ] CHANGELOG.md is updated with latest changes
- [ ] License information is correct

## Package Metadata (pyproject.toml)

- [ ] Package name is correct and available on PyPI
- [ ] Version number is updated appropriately
- [ ] Author name and email are correct (not placeholders)
- [ ] Repository URLs are updated (not placeholders)
- [ ] Description is accurate
- [ ] Keywords are relevant
- [ ] Classifiers are appropriate
- [ ] Dependencies are correct and minimal
- [ ] Python version requirements are accurate

## Package Structure

- [ ] All necessary files are included in MANIFEST.in
- [ ] __init__.py properly exports main classes
- [ ] No unnecessary files in the package
- [ ] .gitignore excludes build artifacts
- [ ] Test files are excluded from distribution

## Legal

- [ ] LICENSE file is included and correct
- [ ] All code is yours or properly licensed
- [ ] No confidential or proprietary information included
- [ ] Attribution for any third-party code

## Build and Test

- [ ] Clean build directory (`rm -rf dist/ build/ *.egg-info`)
- [ ] Package builds successfully (`python -m build`)
- [ ] Build artifacts look correct (`ls -lh dist/`)
- [ ] Package passes twine check (`twine check dist/*`)
- [ ] Test installation locally (`pip install dist/*.whl`)
- [ ] Imports work correctly after installation
- [ ] Tested on TestPyPI first

## Version Control

- [ ] All changes committed to git
- [ ] Working directory is clean (`git status`)
- [ ] Pushed to remote repository
- [ ] GitHub repository is public (if open source)

## Security

- [ ] No API keys or secrets in code
- [ ] No .env files included
- [ ] No personal credentials in repository
- [ ] Dependencies have no known vulnerabilities

## Optional but Recommended

- [ ] GitHub Actions/CI setup
- [ ] Code coverage report
- [ ] Badges in README (build status, coverage, version, etc.)
- [ ] Contributing guidelines
- [ ] Code of conduct
- [ ] GitHub release notes prepared
- [ ] Project homepage/documentation site

## After Publishing

- [ ] Verify package on PyPI looks correct
- [ ] Test installation: `pip install openfda-python`
- [ ] Create git tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Create GitHub release
- [ ] Announce release (if applicable)
- [ ] Update documentation links

## Notes

- Remember: You cannot delete or re-upload a version once published
- Use semantic versioning: MAJOR.MINOR.PATCH
- Test on TestPyPI first to catch issues
- Keep CHANGELOG.md updated for users

## Quick Pre-flight Commands

```bash
# Run all checks
pytest tests/
black --check src/
ruff check src/
python -m build
twine check dist/*

# If all pass, you're ready to publish!
```

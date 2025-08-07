# pycaddy PyPI Publishing Guide

## Initial PyPI Setup

### 1. Create PyPI Account
- Go to https://pypi.org/account/register/
- Create account and verify email
- Go to https://pypi.org/manage/account/token/
- Generate API token (save it securely)

### 2. Install Publishing Tools
```bash
uv pip install twine
```

### 3. Configure Credentials
Create `~/.pypirc` file:
```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

## First-Time Publishing Checklist

### Pre-Publishing Verification
- [ ] Package name `pycaddy` verified available on PyPI
- [ ] All tests passing: `python -m pytest tests/ -v`
- [ ] Code quality checks passing: `ruff check .`
- [ ] Version number set in `pyproject.toml`
- [ ] README.md includes installation and basic usage
- [ ] LICENSE file present (MIT)

### Publishing Steps

#### Option A: Direct to PyPI (if confident)
```bash
# Clean and build
rm -rf dist/ build/
python -m build

# Upload to PyPI
twine upload dist/*

# Verify installation
pip install pycaddy
python -c "import pycaddy.project; print('Success!')"
```

#### Option B: Test First (recommended for first release)
```bash
# Clean and build
rm -rf dist/ build/
python -m build

# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pycaddy

# If everything works, upload to real PyPI
twine upload dist/*
```

## Releasing New Versions

### Version Update Workflow

1. **Update version in pyproject.toml**
   ```toml
   version = "0.2.0"  # or whatever new version
   ```

2. **Test everything**
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Check code quality
   ruff check .
   
   # Test imports work
   python -c "import pycaddy.project; import pycaddy.ledger; print('All good')"
   ```

3. **Build and publish**
   ```bash
   # Clean old builds
   rm -rf dist/ build/
   
   # Build new distribution
   python -m build
   
   # Upload to PyPI
   twine upload dist/*
   ```

4. **Verify release**
   ```bash
   # Test installation of new version
   pip install --upgrade pycaddy
   python -c "import pycaddy; print('Version updated successfully')"
   ```

5. **Tag the release (optional but recommended)**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

## Version Numbering Strategy

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### pycaddy Version History
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes (example)
- `0.2.0` - New features (example)
- `1.0.0` - Stable API (future)

## Quick Commands Reference

```bash
# Full release workflow
rm -rf dist/ build/
python -m build
twine upload dist/*

# Check what's in the package
tar -tzf dist/pycaddy-*.tar.gz

# Install locally for testing
pip install -e .

# Emergency: Delete a release (only works within first few hours)
# Contact PyPI support or use web interface
```

## Troubleshooting

### Common Issues
- **"Package already exists"**: Update version number in pyproject.toml
- **"Invalid credentials"**: Check ~/.pypirc or regenerate API token
- **"Build failed"**: Run `python -m build` locally first to debug
- **"Import errors"**: Verify `__all__` declarations in `__init__.py` files

### Emergency Contacts
- PyPI Support: https://pypi.org/help/
- Package Issues: https://github.com/HutoriHunzu/pycaddy/issues

---

*Generated for pycaddy v0.1.0 - Update this guide as needed*
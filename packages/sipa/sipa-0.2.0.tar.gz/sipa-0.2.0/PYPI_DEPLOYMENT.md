# PyPI Deployment Instructions for SIPA v0.2.0

## Key Features of Version 0.2.0

- **Dual Usage Modes**: Both GUI application and Python library
- **Backward Compatibility**: Supports legacy `from Functions import SIP` syntax  
- **Modern Import Structure**: New `import sipa` syntax for cleaner code
- **Enhanced Documentation**: Comprehensive examples and usage guides

## Prerequisites

1. Install required packages:
```bash
pip install build twine
```

2. Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (for production)
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)

## Building the Package

1. Navigate to the project root directory:
```bash
cd "f:\code\My GitHub\simple-image-processing-application"
```

2. Clean previous builds:
```bash
rm -rf build/ dist/ *.egg-info/
```

3. Build the package:
```bash
python -m build
```

This will create:
- `dist/sipa-0.1.0.tar.gz` (source distribution)
- `dist/sipa-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing the Package

### Upload to TestPyPI first:
```bash
python -m twine upload --repository testpypi dist/*
```

### Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ sipa
```

### Test the installation:
```bash
sipa  # Should launch the GUI application
```

Or test in Python:
```python
import sipa
print(sipa.__version__)
```

## Publishing to PyPI

Once testing is successful:

```bash
python -m twine upload dist/*
```

## Post-Publishing

1. Install from PyPI:
```bash
pip install sipa
```

2. Test the final installation:
```bash
sipa
```

## Version Management

To release a new version:

1. Update version in:
   - `setup.py`
   - `pyproject.toml`
   - `sipa/__init__.py`

2. Rebuild and upload:
```bash
python -m build
python -m twine upload dist/*
```

## Authentication

### Using API Tokens (Recommended)

1. Generate API tokens from PyPI/TestPyPI account settings
2. Use tokens when uploading:
```bash
python -m twine upload --repository testpypi dist/* --username __token__ --password your-api-token
```

### Using .pypirc file

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-pypi-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-api-token
```

## Package Structure Verification

The final package structure should be:
```
sipa/
├── __init__.py
├── main.py
├── core/
│   ├── __init__.py
│   ├── arithmetic.py
│   ├── colors.py
│   ├── filters.py
│   ├── histogram.py
│   └── rotate.py
└── gui/
    ├── __init__.py
    ├── main_window.py
    └── ui_main_window.py
```

## Troubleshooting

### Common Issues:

1. **Import errors**: Ensure all `__init__.py` files are present
2. **Missing dependencies**: Check `install_requires` in setup.py
3. **Version conflicts**: Ensure version numbers match across all files
4. **Entry point issues**: Verify console_scripts entry point in setup.py

### Testing Entry Points:
```bash
pip install -e .  # Install in development mode
sipa              # Test console entry point
```

## File Checklist

Before publishing, ensure these files exist:
- [ ] `setup.py`
- [ ] `pyproject.toml`
- [ ] `README.md` (or `README_PyPI.md`)
- [ ] `LICENSE`
- [ ] `sipa/__init__.py`
- [ ] `sipa/main.py`
- [ ] All core modules
- [ ] GUI modules

## Notes

- The package name "sipa" should be available on PyPI
- Update email addresses in setup files
- Consider adding more comprehensive tests
- Add type hints for better IDE support
- Consider adding documentation with Sphinx

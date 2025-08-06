# Publishing raxodus to PyPI

## Pre-flight Checklist

- [x] Remove all hardcoded credentials
- [x] Update version in `src/raxodus/version.py`
- [x] Update `pyproject.toml` with correct metadata
- [x] Create LICENSE file
- [x] Write comprehensive README
- [x] Test installation locally with `uvx`
- [x] Build package with `uv build`
- [x] Create GitHub Actions workflow

## Publishing Steps

### 1. Create GitHub Repository

```bash
# Option A: Using GitHub CLI
gh repo create bdmorin/raxodus --public \
    --description "Escape from Rackspace ticket hell - a minimal CLI for ticket management" \
    --source=. --push

# Option B: Manual
# Create at https://github.com/new
# Then:
git remote add origin git@github.com:bdmorin/raxodus.git
git push -u origin main
```

### 2. Get PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope "Entire account" or project-specific
3. Copy the token (starts with `pypi-`)

### 3. Add Token to GitHub Secrets

1. Go to https://github.com/bdmorin/raxodus/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI token

### 4. Create and Push Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0: Mondain - The dark wizard"
git push origin v0.1.0

# Create GitHub release (triggers PyPI publish)
gh release create v0.1.0 \
    --title "v0.1.0: Mondain" \
    --notes "## 🗡️ Mondain Release

The first release of raxodus, named after the dark wizard whose defeat marked the beginning of the Age of Darkness in Ultima III.

### Features
- 🎫 List and view Rackspace support tickets
- 📊 Multiple output formats (JSON, table, CSV)
- 🚀 Fast and lightweight
- 🔐 Secure credential handling via environment variables
- 💾 Response caching for better performance

### Installation
\`\`\`bash
uvx install raxodus
# or
pip install raxodus
\`\`\`

### Avatar
![Mondain](https://api.dicebear.com/9.x/bottts/svg?seed=Mondain)
"
```

### 5. Manual PyPI Upload (if GitHub Actions fails)

```bash
# Install tools
uv pip install build twine

# Build
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI first (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Post-Publishing

### Verify Installation

```bash
# Wait ~1 minute for PyPI to update, then:
uvx raxodus --version

# Or with pip
pip install raxodus
raxodus --version
```

### Update Documentation

- Add PyPI badge to README: `[![PyPI version](https://badge.fury.io/py/raxodus.svg)](https://pypi.org/project/raxodus/)`
- Tweet/announce the release
- Update any documentation sites

## Future Releases

For future releases (e.g., v0.2.0 "Minax"):

1. Update version in `src/raxodus/version.py`
2. Update codename and tagline
3. Add release notes to `RELEASES.md`
4. Commit changes
5. Tag and push: `git tag -a v0.2.0 -m "Release v0.2.0: Minax"`
6. GitHub Actions will automatically publish to PyPI

## Troubleshooting

### "Package already exists"
- You can't republish the same version
- Bump the version number and try again

### GitHub Actions fails
- Check the PYPI_API_TOKEN secret is set correctly
- Ensure the token has the right permissions
- Check build logs for specific errors

### Installation doesn't work
- Wait a few minutes for PyPI CDN to update
- Try clearing pip cache: `pip cache purge`
- Check https://pypi.org/project/raxodus/ directly
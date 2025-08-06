#!/bin/bash
# Manual PyPI upload script

VERSION=$(grep '__version__' src/raxodus/version.py | cut -d'"' -f2)

echo "📦 Manual PyPI Upload for raxodus v${VERSION}"
echo ""

# Check if dist files exist
if [ ! -f "dist/raxodus-${VERSION}-py3-none-any.whl" ]; then
    echo "❌ Distribution files not found. Run: uv build"
    exit 1
fi

# Install twine if needed
echo "📥 Installing twine..."
uv pip install --quiet twine

# Check the package
echo "🔍 Checking package..."
twine check dist/*

echo ""
echo "📤 Uploading to PyPI..."
echo "   You'll be prompted for your PyPI username and password"
echo "   Username: __token__"
echo "   Password: <your-pypi-token>"
echo ""

# Upload to PyPI
twine upload dist/raxodus-${VERSION}*

echo ""
echo "✅ Upload complete!"
echo ""
echo "🔗 View at: https://pypi.org/project/raxodus/${VERSION}/"
echo ""
echo "Test installation:"
echo "  pip install raxodus==${VERSION}"
echo "  uvx raxodus --version"
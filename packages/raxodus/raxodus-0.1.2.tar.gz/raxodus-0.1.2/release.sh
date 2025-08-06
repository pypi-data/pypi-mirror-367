#!/bin/bash
# Quick release script for raxodus

VERSION=$(grep '__version__' src/raxodus/version.py | cut -d'"' -f2)
CODENAME=$(grep '__codename__' src/raxodus/version.py | cut -d'"' -f2)

echo "🚀 Releasing raxodus v${VERSION} - ${CODENAME}"
echo ""

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes. Commit them first!"
    git status -s
    exit 1
fi

# Initialize git if needed
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: raxodus v${VERSION}"
fi

# Add remote if not exists
if ! git remote | grep -q origin; then
    echo "📦 Adding GitHub remote..."
    git remote add origin git@github.com:bdmorin/raxodus.git
fi

# Create and push tag
echo "🏷️  Creating tag v${VERSION}..."
git tag -a "v${VERSION}" -m "Release v${VERSION}: ${CODENAME}"

echo "📤 Pushing to GitHub..."
git push origin main --tags

# Create GitHub release if gh is available
if command -v gh &> /dev/null; then
    echo "📝 Creating GitHub release..."
    gh release create "v${VERSION}" \
        --title "v${VERSION}: ${CODENAME}" \
        --notes "## 🗡️ ${CODENAME} Release (v${VERSION})

### What's Changed
- Cleaned repository structure
- Removed unnecessary files from distribution
- Improved package organization
- All search functionality removed (unreliable API)

### Installation
\`\`\`bash
pip install raxodus==${VERSION}
# or
uvx install raxodus
\`\`\`

### Avatar
![${CODENAME}](https://api.dicebear.com/9.x/bottts/svg?seed=${CODENAME})
" \
        dist/*.whl dist/*.tar.gz
else
    echo ""
    echo "⚠️  GitHub CLI not installed. Create release manually at:"
    echo "   https://github.com/bdmorin/raxodus/releases/new"
fi

echo ""
echo "✅ Release v${VERSION} complete!"
echo ""
echo "📦 Package files ready for PyPI:"
echo "   dist/raxodus-${VERSION}-py3-none-any.whl"
echo "   dist/raxodus-${VERSION}.tar.gz"
echo ""
echo "🔑 Don't forget to add PYPI_API_TOKEN to GitHub secrets!"
#!/bin/bash
# Setup GitHub repository for raxodus

echo "🚀 Setting up GitHub repository for raxodus..."

# Initialize git if not already
if [ ! -d .git ]; then
    git init
    echo "✅ Git initialized"
fi

# Add all files
git add .
git commit -m "Initial commit: raxodus v0.1.0 - Mondain release

- Minimal Rackspace ticket CLI
- Read-only ticket operations
- JSON/CSV/table output formats
- Optimized for n8n automation
- Ultima-themed release system"

# Create GitHub repo (requires gh CLI)
if command -v gh &> /dev/null; then
    echo "📦 Creating GitHub repository..."
    gh repo create bdmorin/raxodus \
        --public \
        --description "Escape from Rackspace ticket hell - a minimal CLI for ticket management" \
        --source=. \
        --remote=origin \
        --push
else
    echo "⚠️  GitHub CLI not found. Please install with: brew install gh"
    echo "    Then run: gh auth login"
    echo ""
    echo "Or manually create the repo at: https://github.com/new"
    echo "Repository name: raxodus"
    echo ""
    echo "Then run:"
    echo "  git remote add origin git@github.com:bdmorin/raxodus.git"
    echo "  git push -u origin main"
fi

echo ""
echo "📝 Next steps:"
echo "1. Go to https://pypi.org/manage/account/token/ and create an API token"
echo "2. Add the token as PYPI_API_TOKEN secret in GitHub repo settings"
echo "3. Create a release on GitHub to trigger PyPI publish"
echo ""
echo "To create a release:"
echo "  git tag -a v0.1.0 -m 'Release v0.1.0: Mondain'"
echo "  git push origin v0.1.0"
echo "  gh release create v0.1.0 --title 'v0.1.0: Mondain' --notes-file RELEASES.md"
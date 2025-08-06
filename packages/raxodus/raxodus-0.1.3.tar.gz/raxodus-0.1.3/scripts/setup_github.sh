#!/bin/bash
# Setup GitHub repository for raxodus

set -e

echo "🚀 Setting up GitHub repository for raxodus"

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Create repository
echo "📦 Creating repository..."
gh repo create bdmorin/raxodus \
    --public \
    --description "Escape from Rackspace ticket hell - A minimal CLI for Rackspace tickets" \
    --homepage "https://pypi.org/project/raxodus/" \
    --push \
    --source . \
    --remote origin

echo "✅ Repository created"

# Set repository topics
echo "🏷️ Setting repository topics..."
gh repo edit bdmorin/raxodus --add-topic rackspace
gh repo edit bdmorin/raxodus --add-topic cli
gh repo edit bdmorin/raxodus --add-topic python
gh repo edit bdmorin/raxodus --add-topic automation
gh repo edit bdmorin/raxodus --add-topic n8n

echo "✅ Topics set"

# Create initial labels
echo "🏷️ Creating labels..."
gh label create "rackspace-api" --description "Issues with the Rackspace API itself" --color "FFA500"
gh label create "dependencies" --description "Dependency updates" --color "0366d6"
gh label create "good first issue" --description "Good for newcomers" --color "7057ff"

echo "✅ Labels created"

# Set branch protection (optional, requires pro/org account)
echo "🔒 Setting branch protection..."
gh api repos/bdmorin/raxodus/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["test"]}' \
    --field enforce_admins=false \
    --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
    --field restrictions=null \
    --field allow_force_pushes=false \
    --field allow_deletions=false \
    2>/dev/null || echo "⚠️  Branch protection requires GitHub Pro/Organization account"

# Add secrets for PyPI publishing
echo ""
echo "📝 Next steps:"
echo "1. Go to: https://github.com/bdmorin/raxodus/settings/secrets/actions"
echo "2. Add secret: PYPI_API_TOKEN"
echo "3. Get token from: https://pypi.org/manage/account/token/"
echo ""
echo "Then create the first release:"
echo "  git tag v0.1.1"
echo "  git push --tags"
echo ""
echo "🎉 GitHub repository setup complete!"
echo "View at: https://github.com/bdmorin/raxodus"
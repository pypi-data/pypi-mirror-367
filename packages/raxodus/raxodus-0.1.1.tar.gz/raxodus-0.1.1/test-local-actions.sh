#!/bin/bash
# Test GitHub Actions locally with act

echo "🎬 Testing GitHub Actions locally with act"
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "⚠️  act not installed. Install with: brew install act"
    exit 1
fi

# Test the build job without publishing
echo "🧪 Testing build workflow..."
act -j build-and-publish \
    --dryrun \
    --secret PYPI_API_TOKEN="test-token-not-real"

echo ""
echo "💡 To run for real (without dryrun):"
echo "   act -j build-and-publish"
echo ""
echo "📦 To test a release event:"
echo "   act release"
echo ""
echo "🔍 To list all workflows:"
echo "   act -l"
echo ""
echo "🎯 To test with specific Python version:"
echo "   act -j build-and-publish --matrix python-version:3.11"
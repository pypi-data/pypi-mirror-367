#!/bin/bash
# Quick act test script

echo "🎬 Testing act with raxodus workflows"
echo ""

# Test listing workflows
echo "📋 Available workflows:"
act -l -W /Users/bdmorin/src/raxodus/.github/workflows

echo ""
echo "🧪 To test workflows:"
echo ""
echo "1. Test the build (without actually publishing):"
echo "   act -W /Users/bdmorin/src/raxodus/.github/workflows release --dryrun"
echo ""
echo "2. Test the test workflow:"
echo "   act -W /Users/bdmorin/src/raxodus/.github/workflows push -j test"
echo ""
echo "3. Run with container architecture for M1/M2:"
echo "   act -W /Users/bdmorin/src/raxodus/.github/workflows --container-architecture linux/amd64 push"
echo ""
echo "💡 Note: First run will be slow as it downloads Docker images"
echo ""
echo "⚠️  If act hangs, try:"
echo "   - Restart Docker Desktop"
echo "   - Run with: act --rm --pull=false"
echo "   - Use smaller image: -P ubuntu-latest=node:16-slim"
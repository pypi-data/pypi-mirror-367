# Raxodus Development Status

## Current Version: 0.1.1 (Mondain)

### What We Built
- **raxodus** - A minimal CLI for Rackspace ticket management
- Read-only ticket operations (list, get)
- JSON/CSV/table output formats
- Timing metadata with `--debug` flag for tracking API performance
- Ultima III themed release system
- Ready for PyPI publication

### Key Discoveries About Rackspace API

1. **The API is fundamentally broken**:
   - OPTIONS says PATCH/PUT work, but they return 404
   - Invalid dates in responses (`0001-01-01T00:00:00Z`)
   - Inconsistent field names (`ticketId` vs `id`, `created` vs `createdAt`)
   - Using "demo.ticketing.api.rackspace.com" in production
   - 30+ second response times for simple queries

2. **Undocumented behavior**:
   - `/tickets?subject=text` works for filtering (not documented)
   - No actual search endpoint despite common patterns
   - Service catalog missing most services

3. **Access limitations**:
   - Read-only access to tickets (no updates/comments)
   - No access to CloudFeeds or DNS APIs
   - Only ticketing, monitoring, and metrics APIs available

### Development Setup

#### Tools Configured
- **mise** for task automation (`.mise.toml`)
- **act** for local GitHub Actions testing (`.actrc`)
- **uv** for Python package management
- **hatchling** for building

#### Key Commands
```bash
# Development
mise -C /Users/bdmorin/src/raxodus run up        # Full setup
mise -C /Users/bdmorin/src/raxodus run build     # Build package
mise -C /Users/bdmorin/src/raxodus run test-cli  # Test CLI

# Release
mise -C /Users/bdmorin/src/raxodus run release-check
mise -C /Users/bdmorin/src/raxodus run ship      # Publish to PyPI
```

### Files Created/Modified

#### Core Package (`/Users/bdmorin/src/raxodus/`)
- `src/raxodus/cli.py` - CLI with --debug flag for timing
- `src/raxodus/client.py` - API client with timing tracking
- `src/raxodus/models.py` - Pydantic models with metadata support
- `src/raxodus/version.py` - v0.1.1 with Ultima theming

#### Configuration
- `.mise.toml` - Task automation setup
- `.actrc` - Local GitHub Actions config
- `.github/workflows/publish.yml` - PyPI publishing
- `.github/workflows/test.yml` - Testing workflow

#### Documentation
- `README.md` - User documentation
- `RELEASES.md` - Ultima-themed release notes
- `CLAUDE.md` - v1.0 release criteria (won't release until Rackspace fixes API)
- `docs/RACKSPACE_API_ISSUES.md` - Detailed API problems for Rackspace

### Publishing Status

**NOT YET PUBLISHED** - Ready but waiting for user approval

- GitHub repo: Not created yet (will be github.com/bdmorin/raxodus)
- PyPI: Not published yet
- Package built: `dist/raxodus-0.1.1-py3-none-any.whl`

### Known Issues Resolved

1. **Build caching**: `uvx --from` caches old versions
   - Solution: Use mise tasks that force clean rebuilds
   
2. **Debug flag not showing**: Click decorators weren't being applied
   - Solution: Clean rebuild with cache clearing

3. **act + Colima**: Docker socket mismatch
   - Solution: Set DOCKER_HOST or use Docker Desktop

### Next Steps When Ready

1. Create GitHub repository: `./docs/setup_github.sh`
2. Add PyPI token to GitHub secrets
3. Create release: `git tag v0.1.1 && git push --tags`
4. Publish: `mise run ship` or GitHub Actions will auto-publish

### Why v1.0 is Blocked

Per `CLAUDE.md`, we won't release v1.0 until:
- Rackspace fixes their API inconsistencies
- Write operations actually work
- Production endpoints (not "demo")
- Response times under 2 seconds
- 3+ months of production use

The tool works but is a workaround for a broken API.
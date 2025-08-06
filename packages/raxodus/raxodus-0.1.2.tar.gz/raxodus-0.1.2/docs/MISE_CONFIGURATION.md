# mise Configuration Guide

## Environment Variables

mise provides flexible environment variable management for raxodus development.

### Quick Start

1. Copy the example file:
```bash
cp .mise.local.toml.example .mise.local.toml
```

2. Edit `.mise.local.toml` with your real credentials:
```toml
[env]
RACKSPACE_USERNAME = "your-username"
RACKSPACE_API_KEY = "your-api-key"
RACKSPACE_ACCOUNT = "123456"
```

3. Test it works:
```bash
mise run test-cli
```

### Configuration Hierarchy

mise loads configuration in this order (later overrides earlier):

1. Global config: `~/.config/mise/config.toml`
2. Project config: `.mise.toml` (committed to git)
3. Local config: `.mise.local.toml` (git-ignored)
4. Environment files: `.env`, `.env.local`
5. Shell environment variables

### File Patterns

| File | Purpose | Git Status |
|------|---------|------------|
| `.mise.toml` | Project config, tasks, tools | ✅ Committed |
| `.mise.local.toml` | Personal overrides, secrets | ❌ Ignored |
| `.mise.*.local.toml` | Any local mise config | ❌ Ignored |
| `.env` | Dotenv format variables | ❌ Ignored |
| `.env.local` | Local dotenv overrides | ❌ Ignored |

### Common Use Cases

#### Development with Real Credentials
```toml
# .mise.local.toml
[env]
RACKSPACE_USERNAME = "brian@example.com"
RACKSPACE_API_KEY = "abc123..."
RACKSPACE_ACCOUNT = "987654"
```

#### Testing Different Environments
```toml
# .mise.staging.local.toml
[env]
RACKSPACE_TICKET_API_URL = "https://staging.ticketing.api.rackspace.com/v2"

# .mise.prod.local.toml
[env]
RACKSPACE_TICKET_API_URL = "https://ticketing.api.rackspace.com/v2"
```

Load with: `mise -c .mise.staging.local.toml run test-cli`

#### CI/CD Variables
```toml
# .mise.local.toml
[env]
TWINE_USERNAME = "__token__"
TWINE_PASSWORD = "pypi-AgEIcH..."
GITHUB_TOKEN = "ghp_..."
```

### Tips

1. **Never commit `.mise.local.toml`** - It's automatically gitignored
2. **Use `.mise.local.toml.example`** as a template for team members
3. **Override specific vars**: `RACKSPACE_USERNAME=test mise run test-cli`
4. **Check loaded env**: `mise env` shows all active variables
5. **Multiple profiles**: Create `.mise.dev.local.toml`, `.mise.prod.local.toml` etc.

### Security Best Practices

- Store production credentials only in `.mise.local.toml`
- Use environment-specific files for different stages
- Rotate API keys regularly
- Consider using a secrets manager for production

### Debugging

```bash
# Show all environment variables
mise env

# Show where a variable comes from
mise env | grep RACKSPACE_USERNAME

# Test with override
RACKSPACE_USERNAME=debug mise run test-cli

# Use specific config file
mise --config .mise.staging.local.toml run test-cli
```
# 🗡️ Raxodus

[![PyPI version](https://badge.fury.io/py/raxodus.svg)](https://badge.fury.io/py/raxodus)
[![Python versions](https://img.shields.io/pypi/pyversions/raxodus.svg)](https://pypi.org/project/raxodus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bdmorin/raxodus/actions/workflows/test.yml/badge.svg)](https://github.com/bdmorin/raxodus/actions/workflows/test.yml)

> *"Neither demon nor machine, but something altogether different"* - Ultima III

**Raxodus** - Escape from Rackspace ticket hell. A minimal CLI for managing Rackspace support tickets, built specifically for automation and n8n workflow integration.

## 🎯 Why Raxodus?

The Rackspace ticket API is broken in numerous ways (30+ second response times, inconsistent field names, "demo" endpoints in production). This tool works around those issues to give you reliable ticket access.

## ✨ Features

- **🎫 Read-Only Ticket Access** - List and view Rackspace support tickets
- **📊 Multiple Output Formats** - JSON, table, or CSV output  
- **🚀 Fast & Lightweight** - Minimal dependencies, quick responses (when API allows)
- **🔐 Secure by Design** - No CLI credential flags, environment variables only
- **⏱️ Debug Mode** - Track API performance with timing metadata
- **🔄 n8n Ready** - JSON output perfect for workflow automation
- **🐚 Shell Completions** - Bash, Zsh, and Fish support
- **💾 Smart Caching** - Work around slow API responses
- **🛡️ Type Safe** - Pydantic models handle API inconsistencies

## 📦 Installation

```bash
# Quick run without installation (recommended)
uvx raxodus --version

# Install with pip
pip install raxodus

# Install with uv
uv pip install raxodus
```

## 🚀 Quick Start

### 1. Set Credentials

```bash
# Required environment variables
export RACKSPACE_USERNAME="your-username"
export RACKSPACE_API_KEY="your-api-key"
export RACKSPACE_ACCOUNT="123456"  # Optional default account
```

⚠️ **Security Note**: Never pass credentials as command-line arguments. This is by design for security.

### 2. Test Authentication

```bash
# Verify your credentials work
raxodus auth test
```

### 3. List Tickets

```bash
# List all tickets (table format)
raxodus tickets list --format table

# List open tickets from last 7 days
raxodus tickets list --status open --days 7

# JSON output for automation
raxodus tickets list --format json

# CSV for spreadsheets
raxodus tickets list --format csv > tickets.csv

# With debug timing info
raxodus tickets list --debug --format json
```

### 4. Get Specific Ticket

```bash
# View single ticket
raxodus tickets get 250625-02866

# As JSON
raxodus tickets get 250625-02866 --format json
```

## 📚 Complete Command Reference

### Main Commands

```bash
raxodus --help                    # Show help
raxodus --version                  # Show version info
```

### Authentication Commands

```bash
# Test credentials
raxodus auth test

# Example output:
# ✓ Authentication successful
# ✓ Token expires: 2025-01-07 15:30:00
```

### Ticket Commands

```bash
# List tickets with ALL options
raxodus tickets list \
    --account 123456 \           # Specific account (overrides env)
    --status open \              # Filter: open, closed, pending
    --days 30 \                  # Tickets from last N days
    --page 1 \                   # Pagination
    --per-page 100 \             # Results per page (max 100)
    --format json \              # Output: json, table, csv
    --debug                      # Include timing metadata

# Get single ticket
raxodus tickets get TICKET-ID \
    --format json \              # Output: json, table
    --debug                      # Include timing metadata
```

### Shell Completions

```bash
# Install completions for your shell
raxodus completion install

# Or manually add to your shell config
raxodus completion show >> ~/.bashrc     # Bash
raxodus completion show >> ~/.zshrc      # Zsh
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
RACKSPACE_USERNAME="your-username"       # Your Rackspace username
RACKSPACE_API_KEY="your-api-key"        # Your API key

# Optional
RACKSPACE_ACCOUNT="123456"               # Default account number
RACKSPACE_REGION="us"                    # API region (default: us)
RAXODUS_CACHE_DIR="~/.cache/raxodus"    # Cache directory
RAXODUS_CACHE_TTL="300"                 # Cache TTL in seconds
```

## 🤖 n8n Integration

### Execute Command Node

```json
{
  "nodes": [{
    "name": "List Tickets",
    "type": "n8n-nodes-base.executeCommand",
    "parameters": {
      "command": "raxodus tickets list --format json --debug",
      "env": {
        "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
        "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}",
        "RACKSPACE_ACCOUNT": "={{ $credentials.rackspace.account }}"
      }
    }
  }]
}
```

### Process JSON Output

```javascript
// Code node to process tickets
const output = JSON.parse($input.item.json.stdout);
const openTickets = output.tickets.filter(t => t.status === 'open');

// Check performance
if (output.elapsed_seconds > 30) {
  console.warn(`Slow API response: ${output.elapsed_seconds}s`);
}

return openTickets;
```

### Complete n8n Workflow Example

```json
{
  "name": "Monitor Rackspace Tickets",
  "nodes": [
    {
      "name": "Every 15 minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "minutes", "value": 15}]
        }
      }
    },
    {
      "name": "Get Open Tickets",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "uvx raxodus tickets list --status open --format json",
        "env": {
          "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
          "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}"
        }
      }
    },
    {
      "name": "Parse and Filter",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "code": "const data = JSON.parse($input.item.json.stdout);\nreturn data.tickets.filter(t => t.severity === 'urgent');"
      }
    },
    {
      "name": "Send Alert",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#alerts",
        "text": "Urgent ticket: {{ $json.subject }}"
      }
    }
  ]
}
```

## 📊 Output Format Examples

### JSON Format
```json
{
  "tickets": [
    {
      "ticketId": "250625-02866",
      "subject": "Server connectivity issue",
      "status": "open",
      "severity": "normal",
      "created": "2025-06-25T14:30:00Z",
      "modified": "2025-06-26T09:15:00Z"
    }
  ],
  "elapsed_seconds": 31.5,
  "from_cache": false
}
```

### Table Format
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Ticket ID    ┃ Subject                 ┃ Status┃ Severity ┃ Modified   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 250625-02866 │ Server connectivity...  │ open  │ normal   │ 2025-06-26 │
└──────────────┴─────────────────────────┴───────┴──────────┴────────────┘
```

### CSV Format
```csv
ticketId,subject,status,severity,created,modified
250625-02866,Server connectivity issue,open,normal,2025-06-25T14:30:00Z,2025-06-26T09:15:00Z
```

## ⚠️ Known Issues & Workarounds

### Rackspace API Problems

1. **30+ Second Response Times** - Use `--debug` to track performance
2. **Invalid Dates in Responses** - Pydantic models handle gracefully
3. **Inconsistent Field Names** - Abstracted in our models
4. **No Write Access** - API claims to support updates but returns 404

### Workarounds

```bash
# Use debug flag to track slow responses
raxodus tickets list --debug --format json

# Cache results to avoid repeated slow calls
export RAXODUS_CACHE_TTL=600  # 10 minute cache

# Use pagination for large result sets
raxodus tickets list --page 1 --per-page 50
```

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/bdmorin/raxodus
cd raxodus

# Install for development
uv pip install -e ".[dev]"

# Run tests
pytest

# Check linting
ruff check src/

# Build package
uv build
```

## 🎮 Why "Raxodus"?

Like the villain Exodus from Ultima III - neither demon nor machine, but something altogether different - Rackspace tickets exist in a frustrating limbo between automated systems and human support. This tool helps you escape that hell.

Each release is named after an Ultima III character:
- v0.1.x - "Mondain" (The dark wizard)
- v0.2.x - "Minax" (The enchantress)
- v0.3.x - "Exodus" (Neither demon nor machine)

## 📝 License

MIT - See [LICENSE](LICENSE) file

## 🤝 Contributing

Pull requests welcome! Please ensure:
- All tests pass
- Code follows existing style
- New features include tests
- API workarounds are documented

## ⚖️ Disclaimer

This is an **unofficial** tool and is not affiliated with or supported by Rackspace Technology. Use at your own risk.

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/bdmorin/raxodus/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/bdmorin/raxodus/issues)
- **Security Issues**: Please email privately

## 📈 Project Status

**Current Version**: v0.1.2 (Mondain)

The tool is functional but limited by Rackspace API issues. We maintain 0.x versioning to indicate these limitations. Version 1.0 will only be released when Rackspace fixes their API.

See [CLAUDE.md](CLAUDE.md) for v1.0 release criteria.
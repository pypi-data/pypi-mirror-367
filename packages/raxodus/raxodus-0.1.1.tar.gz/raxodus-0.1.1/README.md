# 🗡️ Raxodus

[![PyPI version](https://badge.fury.io/py/raxodus.svg)](https://badge.fury.io/py/raxodus)
[![Python versions](https://img.shields.io/pypi/pyversions/raxodus.svg)](https://pypi.org/project/raxodus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> *"Neither demon nor machine, but something altogether different"* - Ultima III

Escape from Rackspace ticket hell. A minimal CLI for managing Rackspace support tickets, optimized for automation and integration with n8n workflows.

## Features

- 🎯 **Minimal & Fast** - Just the essentials, no bloat
- 🔄 **n8n Ready** - JSON output perfect for workflow automation
- 🔐 **Secure** - Credentials via environment variables
- 📊 **Multiple Formats** - JSON, table, or CSV output
- ⚡ **Rate Limited** - Built-in retry logic and backoff
- 🛡️ **Type Safe** - Pydantic models prevent runtime errors

## Installation

```bash
# Install with uvx (recommended)
uvx install raxodus

# Or with pip
pip install raxodus

# Or with uv
uv pip install raxodus
```

## Quick Start

```bash
# Set your credentials
export RACKSPACE_USERNAME="your-username"
export RACKSPACE_API_KEY="your-api-key"
export RACKSPACE_ACCOUNT="123456"  # Optional default account

# List recent tickets
raxodus tickets list --days 7

# Get specific ticket
raxodus tickets get 250625-02866

# Output as JSON for n8n
raxodus tickets list --format json | jq '.tickets[] | select(.status == "open")'
```

## n8n Integration

Use the Execute Command node in n8n:

```json
{
  "command": "raxodus tickets list --format json --status open",
  "cwd": "/tmp"
}
```

Then parse the JSON output in subsequent nodes for automation.

## Output Formats

### JSON (Default)
```bash
raxodus tickets list --format json
```

### Table (Human Readable)
```bash
raxodus tickets list --format table
```

### CSV (Excel/Sheets)
```bash
raxodus tickets list --format csv > tickets.csv
```

## Configuration

### Environment Variables
```bash
RACKSPACE_USERNAME    # Your Rackspace username (required)
RACKSPACE_API_KEY     # Your API key (required)
RACKSPACE_ACCOUNT     # Default account number (optional)
RACKSPACE_REGION      # API region (default: us)
RAXODUS_CACHE_DIR     # Cache directory (default: ~/.cache/raxodus)
RAXODUS_CACHE_TTL     # Cache TTL in seconds (default: 300)
```

### Config File (Optional)
```toml
# ~/.config/raxodus/config.toml
[auth]
username = "your-username"
account = "123456"

[cache]
enabled = true
ttl = 300
```

## Commands

### Authentication
```bash
# Test your credentials
raxodus auth test

# List available accounts
raxodus auth accounts
```

### Tickets
```bash
# List tickets with filters
raxodus tickets list [OPTIONS]
  --account TEXT     Rackspace account number
  --status TEXT      Filter by status (open, closed, pending)
  --days INTEGER     Show tickets from last N days
  --format TEXT      Output format (json, table, csv)

# Get single ticket
raxodus tickets get TICKET_ID [OPTIONS]
  --format TEXT      Output format (json, table)
```

## Development

```bash
# Clone the repo
git clone https://github.com/bdmorin/raxodus
cd raxodus

# Install with uv
uv pip install -e ".[dev]"

# Run tests
pytest

# Run integration tests (requires credentials)
hurl --test tests/*.hurl
```

## Why "raxodus"?

Like the villain Exodus from Ultima III, Rackspace tickets are neither purely technical problems nor simple service requests, but something altogether more frustrating. This tool helps you escape.

## License

MIT - See LICENSE file

## Contributing

Pull requests welcome! Please ensure all tests pass and add coverage for new features.

## Support

This is an unofficial tool and is not affiliated with or supported by Rackspace Technology.
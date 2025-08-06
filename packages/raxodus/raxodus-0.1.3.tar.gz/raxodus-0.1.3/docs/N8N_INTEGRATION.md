# n8n Integration Guide

## Quick Start

### 1. Install raxodus in n8n

Add to your n8n Docker image or server:
```bash
pip install raxodus
# or
uvx install raxodus
```

### 2. Create n8n Credentials

In n8n UI:
1. Go to Credentials → New
2. Create "Generic Credential" type
3. Add fields:
   - `username`: Your Rackspace username
   - `apiKey`: Your Rackspace API key  
   - `account`: Your Rackspace account number

### 3. Execute Command Node Setup

## Method 1: Environment Variables (REQUIRED - Most Secure)

```json
{
  "nodes": [
    {
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
    }
  ]
}
```

## Method 2: Using uvx (No Installation Required)

```json
{
  "name": "Get Ticket",
  "type": "n8n-nodes-base.executeCommand",
  "parameters": {
    "command": "uvx raxodus tickets get {{ $json.ticket_id }} --format json",
    "env": {
      "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
      "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}",
      "RACKSPACE_ACCOUNT": "={{ $credentials.rackspace.account }}"
    }
  }
}
```

## Method 3: Docker Container

Create a custom n8n Docker image:

```dockerfile
FROM n8nio/n8n:latest
RUN pip install raxodus
```

## Example n8n Workflows

### Ticket Monitor Workflow

```json
{
  "name": "Rackspace Ticket Monitor",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{ "field": "minutes", "value": 15 }]
        }
      }
    },
    {
      "name": "List Open Tickets",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "raxodus tickets list --status open --format json",
        "env": {
          "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
          "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}",
          "RACKSPACE_ACCOUNT": "={{ $credentials.rackspace.account }}"
        }
      }
    },
    {
      "name": "Parse JSON",
      "type": "n8n-nodes-base.itemLists",
      "parameters": {
        "operation": "splitIntoItems",
        "fieldToSplitOut": "tickets"
      }
    },
    {
      "name": "Check New Tickets",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.is_new }}",
              "value2": true
            }
          ]
        }
      }
    },
    {
      "name": "Send Slack Alert",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#support",
        "text": "New ticket: {{ $json.subject }}"
      }
    }
  ]
}
```

### Ticket Details Enrichment

```javascript
// Code node to process tickets
const tickets = items[0].json.tickets;

for (const ticket of tickets) {
  // Get full ticket details
  const result = await $executor.executeCommand({
    command: `raxodus tickets get ${ticket.id} --format json`,
    env: {
      RACKSPACE_USERNAME: $credentials.rackspace.username,
      RACKSPACE_API_KEY: $credentials.rackspace.apiKey,
      RACKSPACE_ACCOUNT: $credentials.rackspace.account
    }
  });
  
  ticket.full_details = JSON.parse(result);
}

return tickets;
```

## Security Best Practices

### ✅ DO:
- Use n8n's built-in credential management
- Set environment variables for auth
- Use the `--format json` flag for parsing
- Enable `--debug` flag for timing metadata

### ❌ DON'T:
- Pass credentials as CLI arguments (NOT SUPPORTED - by design for security)
- Store credentials in workflow JSON  
- Use plain text credentials in code nodes
- Try to use --username or --api-key flags (they don't exist)

## Handling Rackspace API Issues

The Rackspace API can be slow (30+ seconds). Use these strategies:

1. **Set appropriate timeouts** in n8n Execute Command node:
```json
{
  "timeout": 60000,  // 60 seconds
  "continueOnFail": true
}
```

2. **Use debug flag** to track performance:
```bash
raxodus tickets list --debug --format json
```

This adds timing metadata:
```json
{
  "tickets": [...],
  "elapsed_seconds": 31.5,
  "from_cache": false
}
```

3. **Implement caching** in n8n:
- Store results in n8n's static data
- Check timestamp before calling API
- Only refresh if data is stale

## Troubleshooting

### Command not found
```bash
# Install globally
pip install raxodus

# Or use uvx (no install needed)
uvx raxodus tickets list
```

### Authentication fails
Check environment variables are set:
```javascript
// In n8n Code node
console.log(process.env.RACKSPACE_USERNAME ? 'Username set' : 'Username missing');
```

### Slow response times
- Normal for Rackspace API (30+ seconds)
- Use `--debug` flag to see actual times
- Consider caching results in n8n

### JSON parsing errors
Always use `--format json` for n8n integration:
```bash
raxodus tickets list --format json
```

## Advanced: Custom n8n Node

For production use, consider creating a custom n8n node:

```typescript
// n8n-nodes-raxodus/RaxodusNode.node.ts
import { IExecuteFunctions } from 'n8n-core';
import { INodeType, INodeTypeDescription } from 'n8n-workflow';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class Raxodus implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Rackspace Tickets',
    name: 'raxodus',
    group: ['transform'],
    version: 1,
    description: 'Manage Rackspace tickets',
    defaults: {
      name: 'Rackspace Tickets',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'rackspaceApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          { name: 'List Tickets', value: 'list' },
          { name: 'Get Ticket', value: 'get' },
        ],
        default: 'list',
      },
      // ... more properties
    ],
  };

  async execute(this: IExecuteFunctions) {
    const credentials = await this.getCredentials('rackspaceApi');
    const operation = this.getNodeParameter('operation', 0) as string;
    
    const env = {
      RACKSPACE_USERNAME: credentials.username as string,
      RACKSPACE_API_KEY: credentials.apiKey as string,
      RACKSPACE_ACCOUNT: credentials.account as string,
    };

    let command = 'raxodus tickets ';
    
    switch (operation) {
      case 'list':
        command += 'list --format json --debug';
        break;
      case 'get':
        const ticketId = this.getNodeParameter('ticketId', 0) as string;
        command += `get ${ticketId} --format json`;
        break;
    }

    const { stdout } = await execAsync(command, { env });
    const result = JSON.parse(stdout);
    
    return [this.helpers.returnJsonArray([result])];
  }
}
```

## Performance Optimization

Given Rackspace API's slow response times (30+ seconds), consider:

1. **Batch operations** when possible
2. **Cache results** in n8n's static data or external cache
3. **Use webhooks** if Rackspace supports them (they don't currently)
4. **Run in parallel** for multiple accounts
5. **Set appropriate timeouts** (60+ seconds)

## Example: Caching Pattern

```javascript
// n8n Code node with caching
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Check cache
const cached = $getWorkflowStaticData('ticketCache');
if (cached && cached.timestamp > Date.now() - CACHE_DURATION) {
  return cached.data;
}

// Fetch fresh data
const result = await $executor.executeCommand({
  command: 'raxodus tickets list --format json --debug',
  env: {
    RACKSPACE_USERNAME: $credentials.rackspace.username,
    RACKSPACE_API_KEY: $credentials.rackspace.apiKey,
    RACKSPACE_ACCOUNT: $credentials.rackspace.account
  },
  timeout: 60000
});

const data = JSON.parse(result);

// Cache result
$setWorkflowStaticData('ticketCache', {
  timestamp: Date.now(),
  data: data
});

return data;
```
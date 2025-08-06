# n8n Security Best Practices for Raxodus

## Authentication Methods Ranked by Security

### ✅ 1. Environment Variables (RECOMMENDED)

**Most secure and n8n-native approach:**

```json
{
  "name": "List Tickets",
  "type": "n8n-nodes-base.executeCommand", 
  "parameters": {
    "command": "raxodus tickets list --format json",
    "env": {
      "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
      "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}",
      "RACKSPACE_ACCOUNT": "={{ $credentials.rackspace.account }}"
    }
  }
}
```

**Why this is secure:**
- Credentials are NOT visible in process lists
- n8n handles credential encryption
- No credentials in logs (unless debug mode)
- Standard practice for CI/CD and automation

### ⚠️ 2. Stdin (Alternative - More Complex)

**For advanced users only:**

```javascript
// n8n Code node
const authJson = JSON.stringify({
  username: $credentials.rackspace.username,
  api_key: $credentials.rackspace.apiKey,
  account: $credentials.rackspace.account
});

const result = await $executor.executeCommand({
  command: 'raxodus --auth-stdin tickets list --format json',
  stdin: authJson
});
```

**Considerations:**
- More complex to implement in n8n
- Still secure (not in process list)
- Requires custom code node

### ❌ 3. CLI Arguments (NEVER USE)

**DO NOT DO THIS:**

```bash
# INSECURE - Visible in process lists, logs, history
raxodus --username="user" --api-key="secret" tickets list

# This exposes credentials to:
# - Process monitoring (ps, top, htop)
# - Shell history
# - System logs
# - Anyone with system access
```

## Security Rules Implemented

### 1. No CLI Credential Arguments

Raxodus deliberately does NOT support:
- `--username` flag
- `--api-key` flag  
- `--account` flag
- `--password` flag

This prevents accidental credential exposure.

### 2. Debug Mode Security

When `--debug` flag is used:
- Timing metadata is included
- API endpoints are shown
- But credentials are STILL not exposed
- Safe to use in production

### 3. Environment Variable Validation

Raxodus checks for required environment variables:
- `RACKSPACE_USERNAME`
- `RACKSPACE_API_KEY`
- `RACKSPACE_ACCOUNT`

If missing, provides clear error without exposing partial credentials.

## n8n Credential Storage

### Setting Up Credentials in n8n

1. **Create Custom Credential Type:**

```json
{
  "name": "Rackspace API",
  "displayName": "Rackspace API",
  "properties": [
    {
      "displayName": "Username",
      "name": "username",
      "type": "string",
      "default": ""
    },
    {
      "displayName": "API Key", 
      "name": "apiKey",
      "type": "string",
      "typeOptions": {
        "password": true
      },
      "default": ""
    },
    {
      "displayName": "Account Number",
      "name": "account",
      "type": "string",
      "default": ""
    }
  ]
}
```

2. **Store Credentials Securely:**
   - Use n8n's encrypted credential store
   - Never hardcode in workflows
   - Use credential references: `{{ $credentials.rackspace }}`

### Credential Rotation

Best practices for credential management:

1. **Regular Rotation:**
   - Rotate API keys every 90 days
   - Update in n8n credentials UI
   - No workflow changes needed

2. **Audit Trail:**
   - n8n logs credential usage
   - Monitor for unauthorized access
   - Review execution logs regularly

3. **Principle of Least Privilege:**
   - Use read-only API keys when possible
   - Separate credentials per environment
   - Limit credential access to specific workflows

## Logging and Monitoring

### Safe Logging Practices

```javascript
// n8n Code node - Safe logging
console.log('Executing Rackspace API call...');
console.log(`Account: ${$credentials.rackspace.account}`);
// Never log the actual API key
console.log('API Key: [REDACTED]');

const result = await $executor.executeCommand({
  command: 'raxodus tickets list --format json --debug',
  env: {
    RACKSPACE_USERNAME: $credentials.rackspace.username,
    RACKSPACE_API_KEY: $credentials.rackspace.apiKey,
    RACKSPACE_ACCOUNT: $credentials.rackspace.account
  }
});

// Log only non-sensitive data
const data = JSON.parse(result);
console.log(`Retrieved ${data.tickets.length} tickets in ${data.elapsed_seconds}s`);
```

### Error Handling

```javascript
// Safe error handling
try {
  const result = await $executor.executeCommand({
    command: 'raxodus tickets list --format json',
    env: {
      RACKSPACE_USERNAME: $credentials.rackspace.username,
      RACKSPACE_API_KEY: $credentials.rackspace.apiKey,
      RACKSPACE_ACCOUNT: $credentials.rackspace.account
    }
  });
} catch (error) {
  // Log error without credentials
  console.error('Rackspace API call failed');
  console.error(`Error: ${error.message}`);
  // Do NOT log the full error object (may contain env vars)
  throw new Error('Failed to retrieve tickets - check credentials');
}
```

## Docker Security

When using raxodus in n8n Docker:

### Secure Dockerfile

```dockerfile
FROM n8nio/n8n:latest

# Install raxodus
RUN pip install --no-cache-dir raxodus

# Create non-root user for n8n
USER node

# Never include credentials in image
# ENV RACKSPACE_USERNAME=xxx  # DON'T DO THIS
```

### Docker Compose with Secrets

```yaml
version: '3.8'

services:
  n8n:
    image: n8n-with-raxodus
    environment:
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    secrets:
      - rackspace_creds
    volumes:
      - n8n_data:/home/node/.n8n

secrets:
  rackspace_creds:
    file: ./secrets/rackspace.json  # Never commit this file
```

## Security Checklist

Before deploying to production:

- [ ] Credentials stored in n8n's encrypted store
- [ ] Using environment variables, not CLI arguments
- [ ] No credentials in workflow JSON exports
- [ ] No credentials in logs or error messages
- [ ] API keys have minimum required permissions
- [ ] Regular credential rotation scheduled
- [ ] Monitoring for failed authentication attempts
- [ ] n8n instance itself is secured (HTTPS, auth)
- [ ] Docker images don't contain credentials
- [ ] Backup/restore doesn't expose credentials

## Incident Response

If credentials are exposed:

1. **Immediately:**
   - Rotate the exposed API key
   - Update n8n credentials
   - Check audit logs for unauthorized use

2. **Investigation:**
   - Review how exposure occurred
   - Check all log files
   - Audit workflow exports

3. **Prevention:**
   - Update workflows to prevent recurrence
   - Add monitoring for credential exposure
   - Review this security guide with team

## Summary

**Always use environment variables for credentials in n8n.**

The raxodus CLI is designed to be secure by default:
- No credential CLI flags (prevents accidents)
- Environment variables only (standard practice)
- Clear error messages without credential leaks
- Debug mode safe for production use

This approach ensures your Rackspace credentials remain secure throughout the automation pipeline.
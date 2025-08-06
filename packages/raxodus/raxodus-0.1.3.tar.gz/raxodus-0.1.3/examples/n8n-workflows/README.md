# n8n Workflow Examples for Raxodus

This directory contains ready-to-use n8n workflows for Rackspace ticket automation using raxodus.

## Available Workflows

### 1. Ticket Monitor (`ticket-monitor.json`)
- **Purpose**: Monitor for urgent tickets and send Slack alerts
- **Schedule**: Every 15 minutes
- **Features**:
  - Checks for open tickets
  - Filters for urgent/emergency severity
  - Sends Slack notifications for urgent tickets
  - Tracks API performance

### 2. Daily Ticket Report (`daily-ticket-report.json`)
- **Purpose**: Generate and email daily ticket summary reports
- **Schedule**: Daily at 9 AM
- **Features**:
  - Collects tickets from last 24 hours
  - Generates statistics (open/closed/pending)
  - Groups by severity
  - Formats as markdown report
  - Emails to support team

## How to Import

1. Open your n8n instance
2. Click "Workflows" → "Import from File"
3. Select the JSON file you want to import
4. Configure credentials (see below)

## Required Credentials

### Rackspace Credentials
Create a "Generic Credential" in n8n with:
- `username`: Your Rackspace username
- `apiKey`: Your Rackspace API key
- `account`: Your Rackspace account number (optional)

### Additional Credentials

For **ticket-monitor.json**:
- Slack OAuth2 credentials

For **daily-ticket-report.json**:
- SMTP credentials for email sending

## Customization Tips

### Adjusting Schedule
- Change the trigger node's interval/cron expression
- For ticket-monitor: Adjust minutes value (5, 10, 15, 30, 60)
- For daily-report: Modify cron expression (e.g., "0 14 * * *" for 2 PM)

### Filtering Tickets
Modify the execute command parameters:
```bash
# Filter by status
--status open|closed|pending

# Filter by days
--days 7  # Last week

# Add debug info
--debug

# Change output format
--format json|csv|table
```

### Notification Channels
- **Slack**: Change channel in Slack node settings
- **Email**: Update recipient addresses in Email node
- **Teams/Discord**: Replace Slack node with appropriate integration

## Performance Considerations

- Rackspace API can take 30+ seconds to respond
- Use `--debug` flag to track response times
- Consider increasing n8n timeout settings for Execute Command nodes
- Cache results when possible (set RAXODUS_CACHE_TTL environment variable)

## Troubleshooting

### Command Not Found
If `raxodus` command is not found:
1. Use `uvx raxodus` instead (no installation needed)
2. Or install globally: `pip install raxodus`

### Authentication Fails
- Verify environment variables are set correctly in Execute Command node
- Test credentials with: `raxodus auth test`

### Slow Performance
- Normal for Rackspace API (30+ seconds is common)
- Check `elapsed_seconds` in debug output
- Consider caching: `export RAXODUS_CACHE_TTL=600`

## Creating Custom Workflows

Basic template for Execute Command node:
```json
{
  "command": "uvx raxodus tickets list --format json",
  "env": {
    "RACKSPACE_USERNAME": "={{ $credentials.rackspace.username }}",
    "RACKSPACE_API_KEY": "={{ $credentials.rackspace.apiKey }}",
    "RACKSPACE_ACCOUNT": "={{ $credentials.rackspace.account }}"
  }
}
```

Parse JSON output in Code node:
```javascript
const output = JSON.parse($input.item.json.stdout);
const tickets = output.tickets;
// Process tickets...
```
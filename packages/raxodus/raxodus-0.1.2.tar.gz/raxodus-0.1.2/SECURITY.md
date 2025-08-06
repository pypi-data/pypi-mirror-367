# Security Policy

## Supported Versions

Currently supporting:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**DO NOT** create a public issue if you find a security vulnerability.

Instead, please email the maintainers directly or use GitHub's private vulnerability reporting feature.

## Security Best Practices

### For Users

1. **Never commit credentials**
   - Use `.mise.local.toml` for local credentials
   - Use environment variables in production
   - Never use CLI flags for credentials (we don't support them for this reason)

2. **API Key Management**
   - Use read-only API keys when possible
   - Rotate keys regularly
   - Limit key permissions to minimum required

3. **Environment Security**
   - Keep your Python and dependencies updated
   - Use virtual environments
   - Review dependencies before installing

### For Contributors

1. **No credential storage in code**
2. **No credential logging**
3. **Validate all inputs**
4. **Use secure defaults**
5. **Document security implications of changes**

## Known Security Considerations

### Rackspace API

The Rackspace API itself has several security considerations:

1. **Credentials are transmitted over HTTPS** - Always verify SSL certificates
2. **API keys have full account access** - There's no way to limit permissions
3. **No OAuth or temporary tokens** - API keys are long-lived
4. **Rate limiting is unclear** - Be careful with automation

### This Tool

Raxodus is designed with security in mind:

1. **No credential storage** - All credentials from environment
2. **No credential CLI flags** - Prevents exposure in process lists
3. **No credential logging** - Even in debug mode
4. **HTTPS only** - All API calls use HTTPS

## Response Timeline

- **Critical vulnerabilities**: Addressed within 24 hours
- **High severity**: Addressed within 7 days  
- **Medium/Low severity**: Addressed in next release

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help keep raxodus secure.
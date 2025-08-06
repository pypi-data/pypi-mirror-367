# Test authentication with Rackspace API
# Run with: hurl --test tests/auth.hurl

# Test successful authentication
POST https://api.rackspace.com/v2.0/tokens
Content-Type: application/json
{
  "auth": {
    "RAX-KSKEY:apiKeyCredentials": {
      "username": "{{RACKSPACE_USERNAME}}",
      "apiKey": "{{RACKSPACE_API_KEY}}"
    }
  }
}

HTTP 200
[Asserts]
jsonpath "$.access.token.id" exists
jsonpath "$.access.token.expires" exists
jsonpath "$.access.user.id" exists

[Captures]
token: jsonpath "$.access.token.id"
user_id: jsonpath "$.access.user.id"


# Test with invalid credentials (should fail)
POST https://api.rackspace.com/v2.0/tokens
Content-Type: application/json
{
  "auth": {
    "RAX-KSKEY:apiKeyCredentials": {
      "username": "invalid_user",
      "apiKey": "invalid_key"
    }
  }
}

HTTP 401
[Asserts]
jsonpath "$.unauthorized" exists
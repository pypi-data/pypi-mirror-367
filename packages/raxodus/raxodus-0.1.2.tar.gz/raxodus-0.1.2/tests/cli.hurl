# Test CLI output formats
# Requires raxodus to be installed
# Run with: hurl --test tests/cli.hurl

# Test JSON output
GET exec://raxodus
[QueryStringParams]
cmd: tickets list --format json --days 7

HTTP 0
[Asserts]
jsonpath "$.tickets" exists
jsonpath "$.total" isInteger
jsonpath "$.page" == 1
jsonpath "$.per_page" == 100


# Test auth test command
GET exec://raxodus
[QueryStringParams]
cmd: auth test

HTTP 0
[Asserts]
body contains "Authentication successful"
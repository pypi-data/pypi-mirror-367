---
name: Rackspace API Issue
about: Report a new Rackspace API problem or inconsistency
title: '[API ISSUE] '
labels: 'rackspace-api'
assignees: ''
---

**API Endpoint**
Which Rackspace API endpoint is misbehaving?
- [ ] Authentication (identity.api.rackspacecloud.com)
- [ ] Tickets (demo.ticketing.api.rackspace.com)
- [ ] Other: ___

**Describe the issue**
What's wrong with the API?

**Expected API behavior**
What should the API do according to documentation or common sense?

**Actual API behavior**
What does it actually do?

**Example request/response**
```bash
# Request
curl -X GET "https://demo.ticketing.api.rackspace.com/v2/..." \
  -H "Authorization: Bearer ..."

# Response
{
  "weird": "response"
}
```

**Response time**
How long does this endpoint take to respond?

**Workaround**
Have you found a way to work around this issue?

**Should we report to Rackspace?**
- [ ] Yes, this should be reported
- [ ] No, it's documented behavior
- [ ] Already reported (link: ___)

**Additional notes**
Any other context about this API quirk?
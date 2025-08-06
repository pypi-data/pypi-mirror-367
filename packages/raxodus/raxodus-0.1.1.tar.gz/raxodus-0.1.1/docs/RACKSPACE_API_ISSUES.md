# Rackspace API Issues and Inconsistencies Report

**To:** Rackspace Support / API Team  
**From:** Brian Morin (bmorin-provision)  
**Account:** hybrid:844792  
**Date:** January 6, 2025  
**Subject:** Critical API Documentation and Functionality Issues

## Executive Summary

While developing an automation tool for managing Rackspace support tickets, I've discovered numerous critical issues with the Rackspace Ticketing API that make it unsuitable for production use. The API documentation is inaccurate, the implementation is inconsistent, and basic functionality that the API claims to support does not work.

**This is embarrassing for a company that helped create OpenStack and pioneered cloud APIs.** The current state of your API infrastructure would be unacceptable for a startup, let alone an established hosting provider.

## Issues Identified

### 1. Write Operations Don't Work Despite Being Documented

**Problem:** The API documentation claims support for updating tickets via PATCH/PUT methods, but these operations return 404 errors when attempted.

**Evidence:**
```bash
# OPTIONS request shows these methods are allowed:
OPTIONS /tickets/{ticketId}
Response Headers: Allow: GET, PATCH, PUT

# But actual PATCH/PUT requests fail:
PATCH /tickets/250722-03057
Response: 404 Not Found

PUT /tickets/250722-03057  
Response: 404 Not Found
```

**Impact:** We cannot update ticket status, add comments, or modify tickets programmatically, making automation impossible.

### 2. Inconsistent API Response Structure

**Problem:** The API returns different field names and structures between list and detail views of the same resource.

**List View Issues:**
- Returns `createdAt` field with invalid date: `"0001-01-01T00:00:00Z"`
- Uses `ticketId` instead of standard `id` field
- Returns `modified` instead of standard `updated_at`

**Detail View Issues:**
- Returns `created` (different from list's `createdAt`)
- Omits `createdAt` entirely
- Different field availability between views

**Example:**
```json
// List view ticket
{
  "ticketId": "250722-03057",
  "createdAt": "0001-01-01T00:00:00Z",  // Invalid date!
  "modified": "2025-08-05T21:56:32.000Z"
}

// Same ticket in detail view
{
  "ticketId": "250722-03057",
  "created": "2025-07-22T20:45:18.000Z",  // Different field name, valid date
  "modified": "2025-08-05T21:56:32.000Z"
}
```

### 3. Undocumented Search Functionality

**Problem:** The API documentation doesn't mention any search capability, but the `/tickets` endpoint accepts a `subject` parameter that filters results.

**What We Found Through Trial and Error:**
- `/tickets?subject=backup` - Works but undocumented
- `/tickets/search` - Returns 404 (doesn't exist despite being a common pattern)
- No documentation on search parameters, operators, or limitations

### 4. SSL Certificate Issues

**Problem:** The main Rackspace domain has SSL certificate problems.

**Evidence:**
- `https://api.rackspace.com` - SSL certificate expired/invalid
- Had to discover alternative endpoints through trial and error:
  - `https://identity.api.rackspacecloud.com` (works)
  - `https://demo.ticketing.api.rackspace.com` (works)

### 5. Service Catalog is a Disaster

**Problem:** The service catalog is an inconsistent mess that makes API discovery impossible.

**What's Wrong:**
- Service named "ticketingDemo" in production - DEMO? Really? Is this production or not?
- No clear versioning - are we using v1.0, v2, or something else?
- Services that Rackspace documentation mentions don't appear in the catalog
- No way to discover what APIs are actually available without trial and error
- Account has "admin" and "Full Access Admin Role" but can't access basic services

**Service Catalog Returns Only:**
```
- ticketingDemo (seriously, "demo" in production?)
- cloudMonitoring 
- cloudMetrics
```

**Services Completely Missing from Catalog:**
- ❌ Cloud DNS (even though we manage glic.io through Rackspace)
- ❌ CloudFeeds (documented but invisible)
- ❌ Any production ticketing endpoint (not "demo")
- ❌ Identity service endpoints
- ❌ Billing APIs
- ❌ Any v2 APIs mentioned in documentation

**Why This Matters:**
- The service catalog is supposed to be the source of truth for API discovery
- OpenStack standardized this pattern years ago - Rackspace helped create it!
- Without a proper catalog, we're forced to guess URLs and endpoints
- "Demo" in a production service name suggests this isn't even the right API

### 6. API Timeout Issues

**Problem:** The ticketing API frequently times out with the default timeout values, requiring extended timeout periods (30+ seconds) for basic list operations.

**This is unacceptable:**
- A simple list operation should return in < 1 second
- We're requesting 100 tickets, not 10,000
- Even with caching, responses take 30+ seconds
- This suggests serious backend infrastructure problems

### 7. No API Standardization

**Problem:** Complete lack of consistency with industry standards.

**Examples of Non-Standard Behavior:**
- Using `ticketId` instead of `id` (violates REST conventions)
- Invalid dates like `0001-01-01T00:00:00Z` (not even valid ISO 8601)
- Mixing camelCase and snake_case in the same response
- No pagination standards (where's Link headers? Where's next/prev?)
- No standard error responses (just raw 404s, no error details)
- OPTIONS claims methods exist that return 404

**What Modern APIs Do:**
- Consistent field naming (snake_case or camelCase, pick one!)
- Valid ISO 8601 dates or Unix timestamps
- Proper HTTP status codes with error details
- Standard pagination (Link headers, cursor-based, etc.)
- OpenAPI/Swagger documentation that actually matches the implementation

## Specific Requests

1. **Fix Write Operations:** Either implement the PATCH/PUT endpoints as documented, or update the documentation to clearly state the API is read-only.

2. **Consistent Response Structure:** Standardize field names and data types across all views:
   - Use `id` not `ticketId`
   - Use `created_at` and `updated_at` not `created`/`createdAt`/`modified`
   - Fix invalid dates in list views

3. **Document Search Functionality:** If search is supported, document it properly. If not, implement it - it's a basic requirement for any ticket system.

4. **Update API Documentation:** The current documentation at https://docs.rackspace.com/reference/ticketing-api-reference appears to be incorrect or outdated.

5. **Fix SSL Certificates:** Ensure all documented API endpoints have valid SSL certificates.

6. **Enable CloudFeeds:** The ticket event feed would be invaluable for automation and monitoring.

## Business Impact

These issues prevent us from:
- Building reliable automation for ticket management
- Integrating with workflow tools like n8n
- Reducing manual workload on support staff
- Maintaining consistent ticket handling processes
- Building dashboards and monitoring systems
- Having any confidence in Rackspace's API infrastructure
- Trusting that Rackspace understands modern API development

**The state of this API suggests:**
- Rackspace has abandoned API development
- No one at Rackspace actually uses these APIs
- The documentation team doesn't talk to the development team
- Quality assurance is non-existent for API services

## Testing Methodology

All issues were discovered through systematic testing using:
- Direct HTTP requests via httpx/Python
- OPTIONS requests to discover allowed methods
- Comparison of actual responses vs documentation
- Testing with valid authentication tokens

Test scripts and evidence are available upon request.

## Recommendations

1. **Immediate:** Update API documentation to reflect actual functionality
2. **Short-term:** Fix response structure inconsistencies
3. **Medium-term:** Implement proper write operations or clearly document read-only status
4. **Long-term:** Provide a modern, RESTful API with proper documentation

**Or just be honest:** If Rackspace has given up on APIs, tell your customers so we can plan accordingly instead of wasting time trying to build on broken infrastructure.

## Questions

1. Is the ticketing API officially supported for customer use?
2. Are there plans to implement write operations?
3. Can our account be given access to CloudFeeds for ticket events?
4. Is there a different API endpoint we should be using for production (not "demo")?
5. Where can we find accurate, up-to-date API documentation?

## Contact

I'm happy to provide test scripts, detailed logs, or demonstrate these issues in a screen-sharing session. This report is intended to help improve the Rackspace API experience for all customers attempting to automate their support workflows.

Please let me know how we can work together to resolve these issues.

Best regards,  
Brian Morin  
VP, ProvisionIAM  
Account: hybrid:844792  

---

## Appendix: Test Results Summary

```
✅ Working:
- GET /tickets (list)
- GET /tickets/{ticketId} (detail)
- Authentication via identity.api.rackspacecloud.com

❌ Not Working:
- PATCH /tickets/{ticketId} (404)
- PUT /tickets/{ticketId} (404)
- POST /tickets/{ticketId}/comments (404)
- Any write operations

⚠️ Inconsistent:
- Field names between views
- Date formats and validity
- OPTIONS showing methods that don't work
- Undocumented search parameters
```
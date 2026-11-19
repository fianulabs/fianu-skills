# Fianu API conventions

All Fianu API calls in this plugin share these conventions.

## Prefer the CLI

Where the `fianu` CLI is available, `fianu api <endpoint>` is the supported
transport — it handles the token exchange, the mandatory `/api` prefix, JSON
encoding, pagination, and exit codes. Load `using-fianu-api` for its contract
and for the index of reachable routes.

Everything below describes the **raw-HTTP fallback**, for environments where
the CLI is not installed.

## Base URL

The base URL is configured per environment by the harness and provided to the
agent via the `FIANU_API_BASE` environment variable. Skills MUST read it from
the environment, never hardcode it.

## Authentication

All requests carry a bearer token in the `Authorization` header:

```
Authorization: Bearer <token>
```

The token is provided to the agent at session start. The token's subject
determines the `actor` recorded on any write operation — **the agent does
not set `actor` in the request body.** For agents acting as the platform
agent, the token's subject is configured per environment.

## Common write operations: actor is NOT in the body

When posting a ticket activity:

```http
POST /tickets/:uuid/activities
Authorization: Bearer <token>
Content-Type: application/json

{
  "activityType": "comment",
  "body": "..."
}
```

The server extracts `actor` from the token via `h.User()`. Skills MUST NOT
include `"actor": "..."` in the request body. See
`skills/working-with-tickets/SKILL.md` for the full ticket write contract.

## Error response shape

Errors are a flat JSON object (not nested under `error`):

```json
{ "error": "ticket not found", "error_id": "...", "code": "F_71001", "message": "ticket not found", "detail": "...", "service": "console" }
```

`code` is a registry code of the form `F_<number>`, not a status name; branch
on the HTTP status.

- `400` — schema validation failed
- `401` — token missing or expired
- `403` — actor lacks permission
- `404` — referenced entity does not exist
- `409` — version conflict on entity update
- `422` — semantic validation failed (e.g. policy fails template schema)

## Pagination

List endpoints page with `limit` and `page` query parameters:

```
GET /tickets?limit=50&page=2
```

Keep requesting the next `page` until a page comes back short or empty. Skills MUST follow
pagination when iterating (e.g. the `analyzing-tickets` queue loop).

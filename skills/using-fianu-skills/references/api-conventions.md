# Fianu API conventions

All Fianu API calls in this plugin share these conventions.

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

Errors follow:

```json
{ "error": { "code": "NOT_FOUND", "message": "ticket not found" } }
```

Common codes:

- `400 BAD_REQUEST` — schema validation failed
- `401 UNAUTHORIZED` — token missing or expired
- `403 FORBIDDEN` — actor lacks permission
- `404 NOT_FOUND` — referenced entity does not exist
- `409 CONFLICT` — version conflict on entity update
- `422 UNPROCESSABLE_ENTITY` — semantic validation failed (e.g. policy fails template schema)

## Pagination

List endpoints use cursor pagination:

```
GET /tickets?limit=50&cursor=<opaque>
```

Response includes `nextCursor` if more results exist. Skills MUST follow
pagination when iterating (e.g. the `analyzing-tickets` queue loop).

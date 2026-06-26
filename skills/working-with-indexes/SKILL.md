---
name: working-with-indexes
description: "Use when reading, creating, previewing, or archiving Fianu indexes via /entities/indexes — the materialized CEL asset scopes that gates and policy criteria reference. Covers list / get / members / examine, draft preview vs saved preview, the recompute lifecycle, and the typed F_72xxx errors."
---

# Working with Indexes

## Overview

An **index** is a named, reusable asset scope defined by CEL expressions over
an asset type — "all production repositories", "every module owned by an
engineering team". Policies and gates reference an index by `path` or `id`
instead of repeating CEL, and the platform **materializes** the member set
asynchronously via a worker. Inline policy/gate criteria also auto-spawn a
private index behind the scenes.

This skill is the canonical home for the index entity's **live HTTP surface
and compute lifecycle**. It does NOT own how you *author* an index from
source: the YAML file shape lives in `deploying-entities-yaml`, the
`fianu_index` Terraform resource in `deploying-entities-terraform`, and the
CEL expression language in `writing-cel-expressions`.

Response shapes are **client-observed**; see `## Maintenance`.

## Read endpoints

```
GET /entities/indexes?entityStatus=&recomputeStatus=&assetTypePath=&indexType=&page=&limit=&includeArchived=
GET /entities/indexes/:key?includeArchived=
GET /entities/indexes/:key/members?page=&limit=
GET /entities/indexes/:key/examine
```

| Endpoint | Use |
|---|---|
| `GET /entities/indexes` | List/filter indexes. Filters: `entityStatus` (`active` \| `archived`), `recomputeStatus` (`current` \| `stale` \| `computing` \| `error`), `assetTypePath`, `indexType`, `includeArchived`. |
| `GET /entities/indexes/:key` | Fetch one (with its compute state). `:key` is a UUID **or** a path — the backend routes on `IsValidUUID`, so forward the segment unchanged. |
| `GET /entities/indexes/:key/members` | The assets the worker has matched to this index (paged). |
| `GET /entities/indexes/:key/examine` | Ops-triage detail. **Not** part of the user-facing surface — use only for debugging. |

## Write endpoints

```
POST   /entities/indexes
PATCH  /entities/indexes/:key
DELETE /entities/indexes/:key
```

- `POST` body is the StandardEntity envelope (the same shape the entity
  mappers produce). The backend currently **wraps the response** as
  `{ "index": { … } }` — unwrap to get the bare entity.
- `DELETE` is a **soft-delete / archive**, not a hard delete.

Like other entities, writes enter as drafts and open an approval ticket — see
`working-with-entities` for the draft → approval flow.

## Preview — drafts vs. saved

Two distinct preview paths; pick by whether the index is saved yet:

```
POST /entities/indexes/preview                     ← UNSAVED drafts (compile-only)
GET  /entities/indexes/:key/preview/assets?page=&limit=&search=   ← SAVED index
```

| Path | When | Notes |
|---|---|---|
| `POST /entities/indexes/preview` | Previewing a draft / unsaved expression set. | Compiles the CEL and matches live — **pagination rides in the request BODY** (`page`, `limit`); a query string is silently ignored. Optional `search`; never send `search=""`. |
| `GET /entities/indexes/:key/preview/assets` | Previewing a **saved** index. | Reads the worker-materialized members — no CEL re-translation. Same `{ items, pagination }` envelope as the draft preview. |

## Compute lifecycle

An index is materialized asynchronously, so it carries a recompute state:

| `recomputeStatus` | Meaning |
|---|---|
| `current` | Members are up to date. |
| `stale` | Source changed; recompute pending. |
| `computing` | Worker is matching now. |
| `error` | Recompute failed (see `examine`). |

`visibility` is `private` for the auto-created indexes that back inline
policy/gate criteria, vs. named indexes authored from source. `kind` is
server-controlled — the public deploy path forces user indexes to `write`;
`default` (the per-asset-type catch-all) and `write-ahead` are reserved (see
`deploying-entities-yaml`).

## Typed errors (saved preview)

| Code | HTTP | Meaning |
|---|---|---|
| `F_72006` IndexReferenceNotFound | 404 | No index at that key. |
| `F_72007` IndexReferenceArchived | 422 | Index exists but is archived. |
| `F_72008` IndexRecomputeError | 503 | Members couldn't be computed. |
| `F_40008` InvalidPreviewPagination | 400 | Bad `page`/`limit`. |

## Edge cases

### Draft preview pagination ignored
If draft preview returns the wrong page, you sent pagination in the query
string — it must be in the **body**.

### Wrapped create/update response
`POST` / `PATCH` return `{ index: { … } }`, not the bare entity. Unwrap.

### `:key` as UUID or path
Both resolve. A path key does not need encoding beyond normal URL rules.

## Maintenance — keeping this skill accurate

Endpoint paths + params are grounded in the Fianu web client
(`src/functions/api.js`, "Indexes API — CORE-2541"). Response shapes are
client-observed. Confirm before release:

| Source of truth | What it grounds |
|---|---|
| `../core/external/transport/indexes/requests.go` | `PreviewRequest` (body pagination), list filters, the typed `F_72xxx` errors. |
| `../core/server/console/routes.go` | Index deployer registration + the CEL compile hook the preview/deploy path depends on. |
| `../core/external/db/types/fianu/entities/indexes.go` | Index detail model and the criteria converter that dedups inline expressions onto a private index. |

## See also

- `writing-cel-expressions` — the CEL dialect an index's expressions are written in.
- `deploying-entities-yaml` — the on-disk index file shape (`expressions[].source`, `combineWith`).
- `deploying-entities-terraform` — the `fianu_index` resource.
- `working-with-release-gating` and `working-with-entities` — gates and policy criteria that reference indexes.
- `using-fianu-best-practices` → FIANU.md §Policy Layering — how indexed scopes compose.

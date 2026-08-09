# Fianu API index

GENERATED — do not hand-edit. Regenerate with `./scripts/gen-api-index.sh`.

Source: `core@6995bce04` `cmd/proxy/kodata/config/proxies/*/proxies.yaml`
Routes: 900

**Grep this file. Do not read it whole** — it is ~139KB.

    grep -i ticket references/api-index.md
    grep -E '^GET .*/attestations' references/api-index.md

Columns: `METHOD  PATH  DEST  SERVICE  AUTH`

- `PATH` is the external path — what you call. Pass it to `fianu api`
  **without** the leading `/api`; that prefix is added for you.
- `DEST` is the internal path the proxy forwards to. You never call it, but
  **other skills in this library document endpoints by DEST**, so this column
  is how you match a path quoted elsewhere to a callable one. Grep both.
- `AUTH` is what the **proxy** admits on: `feature:<name>` (token needs
  read/write on that feature), `role:<name>`, `token` (any valid token), or
  `ungated` (proxy does not gate it — the service behind it may still require a
  token, so always send one). A `feature:` or `role:` you lack is a 403, not a 404.
- `(alias)` marks an alternate path onto the same handler.

This index carries paths, methods, and auth only — **not** request bodies or
response shapes. For those, load the skill that owns the endpoint (see
`using-fianu-skills`), or probe with a GET first.

```
POST   /api/.well-known/wif/exchange                                  /.well-known/wif/exchange                            dictator         ungated
GET    /api/abstract-assets                                           /abstract_assets                                     onboarder        ungated
POST   /api/abstract-assets                                           /abstract_assets                                     onboarder        role:internal:system:admin
GET    /api/abstract-assets-categories                                /abstract_asset_categories                           onboarder        ungated
POST   /api/abstract-assets-categories                                /abstract_asset_categories                           onboarder        role:internal:system:admin
GET    /api/abstract-assets-categories/:asset_ref                     /abstract_asset_categories/:asset_ref                onboarder        ungated
PATCH  /api/abstract-assets-categories/:uuid                          /abstract_asset_categories/:uuid                     onboarder        role:internal:system:admin
GET    /api/abstract-assets-categories/assets                         /abstract_asset_categories/assets                    onboarder        ungated
GET    /api/abstract-assets/:asset/labels                             /abstract_assets/:asset/labels                       onboarder        role:internal:system:admin
POST   /api/abstract-assets/:asset/labels                             /abstract_assets/:asset/labels                       onboarder        role:internal:system:admin
DELETE /api/abstract-assets/:asset/properties/:uuid                   /abstract_assets/:asset/properties/:uuid             onboarder        role:internal:system:admin
PATCH  /api/abstract-assets/:asset/properties/:uuid                   /abstract_assets/:asset/properties/:uuid             onboarder        role:internal:system:admin
GET    /api/abstract-assets/:asset_ref                                /abstract_assets/:asset_ref                          onboarder        ungated
DELETE /api/abstract-assets/:uuid                                     /abstract_assets/:uuid                               onboarder        role:internal:system:admin
PATCH  /api/abstract-assets/:uuid                                     /abstract_assets/:uuid                               onboarder        role:internal:system:admin
POST   /api/abstract-assets/:uuid/properties                          /abstract_assets/:uuid/properties                    onboarder        role:internal:system:admin
GET    /api/abstract-assets/properties/:asset_ref                     /abstract_assets/properties/:asset_ref               onboarder        ungated
DELETE /api/abstract_assets/:abstract_asset/labels/:label_uuid        /abstract_assets/:abstract_asset/labels/:label_uuid  onboarder        role:internal:system:admin
GET    /api/abstract_assets/:abstract_asset/labels/:label_uuid        /abstract_assets/:abstract_asset/labels/:label_uuid  onboarder        role:internal:system:admin
GET    /api/admin/tickets                                             /admin/tickets                                       console          role:internal:system:admin
POST   /api/agent/analyze-ticket/:uuid                                /analyze-ticket/:uuid                                agent            role:internal:system:admin
POST   /api/agent/confirm-action/:token                               /confirm-action/:token                               agent            role:internal:system:admin
POST   /api/agent/entities/controls/generate                          /entities/controls/generate                          agent            feature:controls
POST   /api/agent/entities/controls/refine                            /entities/controls/refine                            agent            feature:controls
POST   /api/agent/entities/controls/suggest                           /entities/controls/suggest                           agent            feature:controls
POST   /api/agent/entities/controls/suggest-sources                   /entities/controls/suggest-sources                   agent            feature:controls
GET    /api/agent/health                                              /health                                              agent            ungated
POST   /api/agent/import-framework                                    /import-framework                                    agent            role:internal:system:admin
GET    /api/agent/notes/attestations/:uuid/findings/:finding_id/summarize /notes/attestations/:uuid/findings/:finding_id/summarize agent            role:internal:system:admin
POST   /api/agent/notes/attestations/:uuid/findings/:finding_id/summarize /notes/attestations/:uuid/findings/:finding_id/summarize agent            role:internal:system:admin
POST   /api/agent/process-queue                                       /process-queue                                       agent            role:internal:system:admin
GET    /api/applications                                              /applications                                        consulta         ungated
POST   /api/applications                                              /applications                                        onboarder        feature:assets
GET    /api/applications/:code                                        /applications/:code                                  consulta         ungated (alias)
PATCH  /api/applications/:uuid                                        /applications/:uuid                                  onboarder        feature:assets
GET    /api/applications/:uuid/metrics/commits                        /applications/:uuid/metrics/commits                  consulta         ungated
GET    /api/applications/:uuid/snapshot                               /applications/:uuid/snapshot                         consulta         feature:badge_results
GET    /api/applications/attestations/by-assets                       /applications/attestations/by-assets                 consulta         feature:badge_results
GET    /api/applications/schemes                                      /applications/schemes                                consulta         ungated
DELETE /api/approval                                                  /approval                                            console          ungated
GET    /api/approval                                                  /approval                                            console          ungated
POST   /api/approval                                                  /approval                                            console          ungated
GET    /api/approval-workflows                                        /approval-workflows                                  onboarder        ungated
PATCH  /api/approval-workflows/:uuid/approve                          /approval-workflows/:uuid/approve                    onboarder        ungated
PATCH  /api/approval-workflows/:uuid/decline                          /approval-workflows/:uuid/decline                    onboarder        ungated
PATCH  /api/approval-workflows/:uuid/expire                           /approval-workflows/:uuid/expire                     onboarder        ungated
PATCH  /api/approval-workflows/:uuid/reject                           /approval-workflows/:uuid/reject                     onboarder        ungated
PATCH  /api/approval-workflows/:uuid/stage                            /approval-workflows/:uuid/stage                      onboarder        ungated
GET    /api/approval-workflows/:workflow_key                          /approval-workflows/:workflow_key                    onboarder        ungated
POST   /api/approval-workflows/:workflow_type                         /approval-workflows/:workflow_type                   onboarder        ungated
POST   /api/asset/:asset/domain                                       /assets/:asset/domains                               onboarder        feature:assets
PATCH  /api/asset/:asset/domain/close                                 /assets/:asset/domains/close                         onboarder        feature:assets
GET    /api/assets                                                    /assets                                              onboarder        feature:assets
POST   /api/assets                                                    /assets                                              onboarder        role:internal:system:admin
GET    /api/assets/:asset/annotations/:note                           /assets/:asset/annotations/:note/export              consulta         feature:data_export (alias)
GET    /api/assets/:asset/annotations/:note/export                    /assets/:asset/annotations/:note/export              consulta         feature:data_export
GET    /api/assets/:asset/annotations/export                          /assets/:asset/annotations/export                    consulta         feature:data_export
GET    /api/assets/:asset/commits                                     /assets/:asset/commits                               consulta         feature:badge_results
GET    /api/assets/:asset/commits/:commit                             /assets/:asset/commits/:commit                       consulta         feature:badge_results
GET    /api/assets/:asset/commits/latest                              /assets/:asset/commits/latest                        consulta         feature:badge_results
GET    /api/assets/:asset/controls/:control/meta                      /assets/:asset/controls/:control/meta                consulta         feature:policies
GET    /api/assets/:asset/controls/:control/policy                    /assets/:asset/controls/:control/policy              consulta         ungated
GET    /api/assets/:asset/controls/:control/policy/test               /assets/:asset/controls/:control/policy/test         consulta         ungated
POST   /api/assets/:asset/controls/:control/policy/test               /assets/:asset/controls/:control/policy/test         consulta         ungated
GET    /api/assets/:asset/controls/required/latest                    /assets/:asset/controls/required/latest              consulta         ungated
GET    /api/assets/:asset/gates/policies/controls                     /assets/:asset/gates/policies/controls               onboarder        feature:controls
PATCH  /api/assets/:asset/inheritances/:parent                        /assets/:asset/inheritances/:parent                  onboarder        role:internal:system:admin
GET    /api/assets/:asset/policies/latest                             /assets/:asset/policies/latest                       consulta         ungated
GET    /api/assets/:asset/policies/required                           /component/:asset/compliance                         consulta         ungated
PATCH  /api/assets/:asset/workflows/children/resync                   /assets/:asset/workflows/children/resync             onboarder        role:internal:system:admin
GET    /api/assets/:asset_type/:asset_key/commits/:sha/diff           /assets/:asset_type/:asset_key/commits/:sha/diff     onboarder        feature:assets
GET    /api/assets/:asset_type/:asset_key/diff/:comparison            /assets/:asset_type/:asset_key/diff/:comparison      onboarder        feature:assets
GET    /api/assets/:asset_type/:asset_key/files/:revision/*           /assets/:asset_type/:asset_key/files/:revision/:*1   onboarder        feature:assets
POST   /api/assets/:asset_type/:asset_key/tags/sync                   /assets/:asset_type/:asset_key/tags/sync             onboarder        feature:assets
GET    /api/assets/:asset_type/:asset_uuid/commits                    /assets/:asset_type/:asset_uuid/commits              onboarder        feature:assets
PATCH  /api/assets/:asset_type/:asset_uuid/commits                    /assets/:asset_type/:asset_uuid/commits              onboarder        feature:assets
POST   /api/assets/:asset_type/:asset_uuid/commits                    /assets/:asset_type/:asset_uuid/commits              onboarder        feature:assets
GET    /api/assets/:asset_type/:asset_uuid/commits/:git_ref           /assets/:asset_type/:asset_uuid/commits/:git_ref     onboarder        feature:assets
GET    /api/assets/:asset_type/:asset_uuid/tags                       /assets/:asset_type/:asset_uuid/tags                 onboarder        feature:assets
GET    /api/assets/:asset_uuid                                        /assets/:asset_uuid                                  onboarder        ungated
PATCH  /api/assets/:asset_uuid                                        /assets/:asset_uuid                                  onboarder        feature:assets
PUT    /api/assets/:asset_uuid                                        /assets/:asset_uuid                                  onboarder        feature:assets
GET    /api/assets/:asset_uuid/changelog                              /assets/:asset_uuid/changelog                        onboarder        feature:assets
GET    /api/assets/:asset_uuid/graph                                  /assets/:asset_uuid/graph                            onboarder        feature:assets
GET    /api/assets/:asset_uuid/labels                                 /assets/:asset_uuid/labels                           onboarder        feature:assets
DELETE /api/assets/:asset_uuid/labels/:label_uuid                     /assets/:asset_uuid/labels/:label_uuid               onboarder        feature:assets
POST   /api/assets/:asset_uuid/labels/:label_uuid                     /assets/:asset_uuid/labels/:label_uuid               onboarder        feature:assets
PUT    /api/assets/:asset_uuid/labels/:label_uuid                     /assets/:asset_uuid/labels/:label_uuid               onboarder        feature:assets
GET    /api/assets/:asset_uuid/membership                             /assets/:asset_uuid/membership                       onboarder        feature:assets
GET    /api/assets/:asset_uuid/permissions                            /assets/:asset_uuid/permissions                      onboarder        feature:assets
GET    /api/assets/:asset_uuid/repository                             /assets/:asset_uuid/repository                       consulta         feature:badge_results
GET    /api/assets/:asset_uuid/repository/:commit_diff                /assets/:asset_uuid/repository/:commit_diff          consulta         ungated
GET    /api/assets/:asset_uuid/tokens                                 /assets/:asset_uuid/tokens                           consulta         role:internal:system:admin
PATCH  /api/assets/:asset_uuid/workflows/close                        /assets/:asset_uuid/workflows/close                  onboarder        role:internal:system:admin
PATCH  /api/assets/:asset_uuid/workflows/open                         /assets/:asset_uuid/workflows/open                   onboarder        role:internal:system:admin
GET    /api/assets/:component/controls/required                       /component/:component/controls/required              consulta         ungated (alias)
POST   /api/assets/:source_asset/edges/:target_asset                  /assets/:source_asset/edges/:target_asset            onboarder        feature:assets
DELETE /api/assets/:target_asset/edges                                /assets/:target_asset/edges                          onboarder        feature:assets
GET    /api/assets/:target_asset/edges                                /assets/:target_asset/edges                          onboarder        feature:assets
PATCH  /api/assets/:target_asset/edges                                /assets/:target_asset/edges                          onboarder        feature:assets
POST   /api/assets/:type/search                                       /assets/:type/search                                 onboarder        ungated
DELETE /api/assets/:uuid/archive                                      /assets/:uuid/archive                                onboarder        feature:assets
GET    /api/assets/:uuid/attributes                                   /assets/:uuid/attributes                             consulta         ungated
GET    /api/assets/:uuid/attributes/latest                            /assets/:uuid/attributes/latest                      consulta         ungated
GET    /api/assets/:uuid/domains                                      /assets/:uuid/domains                                consulta         ungated
POST   /api/assets/:uuid/link                                         /components/:uuid/link                               onboarder        feature:assets
GET    /api/assets/:uuid/metrics/commits                              /assets/:uuid/metrics/commits                        consulta         ungated
GET    /api/assets/:uuid/metrics/signatures                           /assets/:uuid/metrics/signatures                     consulta         ungated
GET    /api/assets/:uuid/modules/domains                              /assets/:uuid/modules/domains                        consulta         ungated
PATCH  /api/assets/archive/application/:uuid                          /applications/:uuid/archive                          onboarder        feature:assets
GET    /api/assets/children/:asset/gates/policies/controls            /assets/children/:asset/gates/policies/controls      onboarder        feature:controls
DELETE /api/assets/delete/application/:uuid                           /applications/:uuid                                  onboarder        ungated
DELETE /api/assets/delete/applications/:uuid                          /applications/:uuid                                  onboarder        ungated (alias)
DELETE /api/assets/edges/:node_id                                     /assets/edges/:node_id                               onboarder        feature:assets
PATCH  /api/assets/edges/:node_id                                     /assets/edges/:node_id                               onboarder        feature:assets
GET    /api/assets/evaluate/filter                                    /registry/components/filter                          consulta         ungated
GET    /api/assets/organizations/:uuid/metrics/commits                /applications/:uuid/metrics/commits                  consulta         ungated (alias)
POST   /api/assets/policies                                           /component/policies/assign                           consulta         ungated
POST   /api/assets/policies/by-payload                                /component/policies/match                            consulta         ungated
DELETE /api/assets/relationships/:child                               /assets/relationships/:child                         onboarder        role:internal:system:admin
DELETE /api/assets/relationships/:child/to/:parent                    /assets/relationships/:child/to/:parent              onboarder        role:internal:system:admin
POST   /api/assets/relationships/:child/to/:parent                    /assets/relationships/:child/to/:parent              onboarder        role:internal:system:admin
GET    /api/assets/releases/:id                                       /releases/:id                                        consulta         feature:badge_results
POST   /api/assets/releases/:release_id/evidence/modifiers            /assets/releases/:release_id/evidence/modifiers      onboarder        feature:badge_results
POST   /api/assets/releases/:release_id/evidence/resync               /assets/releases/:release_id/evidence/resync         onboarder        feature:assets
POST   /api/assets/releases/:release_id/evidence/scan                 /assets/releases/:release_id/evidence/scan           onboarder        feature:badge_results
GET    /api/assets/releases/:release_identifier/status                /assets/releases/:release_identifier/status          onboarder        feature:assets
PATCH  /api/assets/releases/:release_identifier/status                /assets/releases/:release_identifier/status          onboarder        feature:assets
POST   /api/assets/releases/issues/preview                            /releases/issues/preview                             consulta         feature:badge_results
POST   /api/assets/releases/series/preview                            /releases/series/preview                             consulta         feature:badge_results
GET    /api/assets/reports/:uuid/commit/:commit                       /pdf/:uuid/:commit                                   pdfgenerator     feature:data_export
POST   /api/assets/reports/pdf                                        /pdf                                                 pdfgenerator     feature:data_export
POST   /api/assets/repository/sync                                    /components/sync                                     onboarder        feature:assets
POST   /api/assets/search/by-property                                 /assets/search/by-property                           onboarder        ungated
GET    /api/assets/summaries                                          /assets                                              onboarder        feature:assets
GET    /api/assets/teams/:team_uuid/members                           /assets/teams/:team_uuid/members                     dictator         feature:assets
POST   /api/assets/teams/:team_uuid/members                           /assets/teams/:team_uuid/members                     dictator         feature:assets
DELETE /api/assets/teams/:team_uuid/members/:principal_uuid           /assets/teams/:team_uuid/members/:principal_uuid     dictator         feature:assets
GET    /api/assets/tokens/:token                                      /assets/tokens/:token                                consulta         ungated
POST   /api/assets/workflows/:instance_name/:asset_type/import        /assets/workflows/:instance_name/:asset_type/import  onboarder        role:internal:system:admin
POST   /api/assets/workflows/apps/:app_type/installation              /assets/workflows/apps/:app_type/installation        onboarder        role:internal:system:admin
POST   /api/assets/workflows/apps/github/installation                 /assets/workflows/apps/github/installation           onboarder        role:internal:system:admin
POST   /api/assets/workflows/onboard                                  /assets/workflows/onboard                            onboarder        role:internal:system:admin
GET    /api/badges                                                    /badges                                              badges           ungated
GET    /api/badges/charts/radial                                      /badges/charts/radial_with_badges                    badges           ungated
GET    /api/badges/charts/radial/single                               /badges/charts/radial                                badges           ungated
GET    /api/billing/licenses                                          /billing/licenses                                    consulta         role:internal:system:admin
POST   /api/billing/licenses                                          /billing/licenses                                    consulta         role:internal:system:superuser
GET    /api/billing/licenses/:licenseId                               /billing/licenses/:licenseId                         consulta         role:internal:system:admin
PATCH  /api/billing/licenses/:licenseId                               /billing/licenses/:licenseId                         consulta         role:internal:system:superuser
GET    /api/billing/licenses/:licenseId/invoices                      /billing/licenses/:licenseId/invoices                consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/invoices/:invoiceId           /billing/licenses/:licenseId/invoices/:invoiceId     consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/invoices/:invoiceId/download  /billing/licenses/:licenseId/invoices/:invoiceId/download consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/invoices/upcoming             /billing/licenses/:licenseId/invoices/upcoming       consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage                         /billing/licenses/:licenseId/usage                   consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/aggregate               /billing/licenses/:licenseId/usage/aggregate         consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/monthly-averages        /billing/licenses/:licenseId/usage/monthly-averages  consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/top                     /billing/licenses/:licenseId/usage/top               consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/upcoming                /billing/licenses/:licenseId/usage/upcoming          consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/upcoming/aggregate      /billing/licenses/:licenseId/usage/upcoming/aggregate consulta         role:internal:system:admin
GET    /api/billing/licenses/:licenseId/usage/ytd-summary             /billing/licenses/:licenseId/usage/ytd-summary       consulta         role:internal:system:admin
POST   /api/billing/report-invoice                                    /billing/report-invoice                              consulta         role:internal:system:superuser
GET    /api/billing/usage                                             /billing/usage                                       consulta         role:internal:system:admin
GET    /api/billing/usage/aggregate                                   /billing/usage/aggregate                             consulta         role:internal:system:admin
GET    /api/brokers                                                   /brokers                                             instances        feature:instances
POST   /api/brokers                                                   /brokers                                             instances        feature:instances
DELETE /api/brokers/:key                                              /brokers/:key                                        instances        feature:instances
GET    /api/brokers/:key                                              /brokers/:key                                        instances        feature:instances
DELETE /api/commits/:sha/tags                                         /commits/:sha/tags                                   onboarder        role:internal:system:admin
POST   /api/compliance/artifacts/check                                /compliance/artifacts/check                          gate_controller  ungated
POST   /api/compliance/artifacts/check/:change_type                   /compliance/artifacts/check/:change_type             gate_controller  ungated
GET    /api/component/:component/build                                /component/:component/build                          consulta         feature:badge_results
GET    /api/component/:component/controls/required                    /component/:component/controls/required              consulta         ungated
GET    /api/component/:component/snapshot                             /component/:component/snapshot                       consulta         feature:badge_results
GET    /api/component/:component/versions                             /component/:component/versions                       consulta         feature:badge_results
POST   /api/connect                                                   /connect                                             dictator         ungated
PATCH  /api/console/activate/collections/:id                          /activate/collection/:id                             console          feature:collections (alias)
PATCH  /api/console/activate/controls/:id                             /activate/control/:id                                console          feature:controls (alias)
PATCH  /api/console/activate/domains/:id                              /activate/domain/:id                                 console          feature:domains (alias)
PATCH  /api/console/activate/environments/:id                         /activate/environment/:id                            console          feature:environments
PATCH  /api/console/activate/exceptions/:id                           /activate/policy_exception/:id                       console          feature:policies (alias)
PATCH  /api/console/activate/gate/:id                                 /activate/gate/:id                                   console          feature:gates (alias)
PATCH  /api/console/activate/gates/:id                                /activate/gate/:id                                   console          feature:gates (alias)
PATCH  /api/console/activate/plugins/:id                              /activate/plugin/:id                                 console          role:internal:system:admin (alias)
PATCH  /api/console/activate/policies/:id                             /activate/policy/:id                                 console          feature:policies (alias)
PATCH  /api/console/activate/targets/:id                              /activate/target/:id                                 console          feature:targets
DELETE /api/console/archive/collections/:id                           /archive/collection/:id                              console          feature:collections (alias)
DELETE /api/console/archive/controls/:id                              /archive/control/:id                                 console          feature:controls (alias)
DELETE /api/console/archive/domains/:id                               /archive/domain/:id                                  console          feature:domains (alias)
DELETE /api/console/archive/environments/:id                          /archive/environment/:id                             console          feature:environments (alias)
DELETE /api/console/archive/exceptions/:id                            /archive/policy_exception/:id                        console          feature:policies (alias)
DELETE /api/console/archive/forms/:id                                 /archive/form/:id                                    console          feature:forms (alias)
DELETE /api/console/archive/gate/:id                                  /archive/gate/:id                                    console          feature:gates (alias)
DELETE /api/console/archive/gates/:id                                 /archive/gate/:id                                    console          feature:gates (alias)
DELETE /api/console/archive/policies/:id                              /archive/policy/:id                                  console          feature:policies (alias)
DELETE /api/console/archive/targets/:id                               /archive/target/:id                                  console          feature:targets (alias)
GET    /api/console/classes                                           /classes                                             consulta         feature:classes (alias)
GET    /api/console/classes/:name                                     /classes/:name                                       consulta         feature:classes (alias)
GET    /api/console/collections                                       /collections                                         console          feature:collections (alias)
POST   /api/console/collections                                       /create/collection                                   console          feature:collections (alias)
GET    /api/console/collections/:entity_id/permissions                /entities/collection/:entity_id/permissions          console          feature:collections
GET    /api/console/collections/:name                                 /collections/:name                                   console          feature:collections (alias)
GET    /api/console/controls                                          /controls                                            console          feature:controls (alias)
POST   /api/console/controls                                          /create/control                                      console          feature:controls (alias)
DELETE /api/console/controls/:control_path/group                      /controls/:control_path/group                        console          feature:controls
GET    /api/console/controls/:entity_id/permissions                   /entities/control/:entity_id/permissions             console          feature:controls
DELETE /api/console/controls/:entity_id/references/:reference_uuid    /references/:reference_uuid/bind/:entity_id          console          feature:controls
POST   /api/console/controls/:entity_id/references/:reference_uuid    /references/:reference_uuid/bind/:entity_id          console          feature:controls
POST   /api/console/controls/:entity_key/attestations/:note_uuid/templates/preview /controls/:entity_key/attestations/:note_uuid/templates/preview consulta         feature:controls (alias)
GET    /api/console/controls/:entity_key/policies/history             /controls/:entity_key/policies/history               console          feature:policies,feature:controls (alias)
GET    /api/console/controls/:entity_key/schemas                      /controls/:entity_key/schemas                        console          feature:controls (alias)
POST   /api/console/controls/:entity_key/templates/export             /controls/:entity_key/templates/export               console          feature:controls (alias)
POST   /api/console/controls/:entity_key/templates/preview            /controls/:entity_key/templates/preview              consulta         feature:controls (alias)
GET    /api/console/controls/:entity_uuid/versions/:version/workflows /controls/:entity_uuid/versions/:version/workflows   consulta         feature:controls
GET    /api/console/controls/:id/policy                               /control/:id/policy                                  consulta         ungated (alias)
GET    /api/console/controls/:path                                    /controls/:path                                      console          feature:controls (alias)
PATCH  /api/console/controls/:path                                    /controls/:path                                      console          feature:controls (alias)
PUT    /api/console/controls/:path                                    /controls/:path                                      console          feature:controls (alias)
GET    /api/console/controls/:path/versions                           /controls/:path/versions                             consulta         feature:controls (alias)
PATCH  /api/console/controls/group                                    /controls/group                                      console          feature:controls
POST   /api/console/controls/group                                    /controls/group                                      console          feature:controls
DELETE /api/console/controls/group/:group_identifier                  /controls/group/:group_identifier                    console          feature:controls
GET    /api/console/controls/versions/:version_uuid/rule              /controls/versions/:version_uuid/rule                consulta         feature:controls
DELETE /api/console/deactivate/collections/:id                        /deactivate/collection/:id                           console          feature:collections (alias)
PATCH  /api/console/deactivate/collections/:id                        /deactivate/collection/:id                           console          feature:collections (alias)
DELETE /api/console/deactivate/controls/:id                           /deactivate/control/:id                              console          feature:controls (alias)
PATCH  /api/console/deactivate/controls/:id                           /deactivate/control/:id                              console          feature:controls (alias)
DELETE /api/console/deactivate/domains/:id                            /deactivate/domain/:id                               console          feature:domains (alias)
PATCH  /api/console/deactivate/domains/:id                            /deactivate/domain/:id                               console          feature:domains (alias)
DELETE /api/console/deactivate/environments/:id                       /deactivate/environment/:id                          console          feature:environments
PATCH  /api/console/deactivate/environments/:id                       /deactivate/environment/:id                          console          feature:environments
DELETE /api/console/deactivate/forms/:id                              /deactivate/form/:id                                 console          feature:forms (alias)
PATCH  /api/console/deactivate/forms/:id                              /deactivate/form/:id                                 console          feature:forms (alias)
DELETE /api/console/deactivate/gate/:id                               /deactivate/gate/:id                                 console          feature:gates (alias)
PATCH  /api/console/deactivate/gate/:id                               /deactivate/gate/:id                                 console          feature:gates (alias)
DELETE /api/console/deactivate/gates/:id                              /deactivate/gate/:id                                 console          feature:gates (alias)
PATCH  /api/console/deactivate/gates/:id                              /deactivate/gate/:id                                 console          feature:gates (alias)
DELETE /api/console/deactivate/policies/:id                           /deactivate/policy/:id                               console          feature:policies (alias)
PATCH  /api/console/deactivate/policies/:id                           /deactivate/policy/:id                               console          feature:policies (alias)
DELETE /api/console/deactivate/targets/:id                            /deactivate/target/:id                               console          feature:targets
PATCH  /api/console/deactivate/targets/:id                            /deactivate/target/:id                               console          feature:targets
DELETE /api/console/delete/collections/:id                            /delete/collection/:id                               console          feature:collections (alias)
DELETE /api/console/delete/controls/:id                               /delete/control/:id                                  console          feature:controls (alias)
DELETE /api/console/delete/controls/:id/versions/:version             /delete/control/:id/versions/:version                console          feature:controls (alias)
DELETE /api/console/delete/domains/:id                                /delete/domain/:id                                   console          feature:domains (alias)
DELETE /api/console/delete/environments/:id                           /delete/environment/:id                              console          feature:environments (alias)
DELETE /api/console/delete/exceptions/:id                             /delete/policy_exception/:id                         console          feature:policies (alias)
DELETE /api/console/delete/exceptions/:id/versions/:version           /delete/policy_exception/:id/versions/:version       console          feature:policies (alias)
DELETE /api/console/delete/forms/:id                                  /delete/form/:id                                     console          feature:forms (alias)
DELETE /api/console/delete/gate/:id                                   /delete/gate/:id                                     console          feature:gates (alias)
DELETE /api/console/delete/gates/:id                                  /delete/gate/:id                                     console          feature:gates (alias)
DELETE /api/console/delete/policies/:id                               /delete/policy/:id                                   console          feature:policies (alias)
DELETE /api/console/delete/policies/:id/versions/:version             /delete/policy/:id/versions/:version                 console          feature:policies (alias)
DELETE /api/console/delete/targets/:id                                /delete/target/:id                                   console          feature:targets (alias)
DELETE /api/console/delete/templates/:id                              /delete/template/:id                                 console          feature:templates (alias)
GET    /api/console/domains                                           /domains                                             console          feature:domains (alias)
POST   /api/console/domains                                           /create/domain                                       console          feature:domains (alias)
GET    /api/console/domains/:entity_id/assets                         /domains/:entity_id/assets                           consulta         feature:domains
GET    /api/console/domains/:entity_id/permissions                    /entities/domain/:entity_id/permissions              console          feature:domains
GET    /api/console/domains/:name                                     /domains/:name                                       console          feature:domains (alias)
GET    /api/console/entities                                          /entities                                            console          ungated
GET    /api/console/entities/:entity_id                               /entities/:entity_id                                 console          ungated
GET    /api/console/entities/:entity_key/references                   /entities/:entity_key/references                     console          ungated
GET    /api/console/entities/:entity_key/requests/events              /entities/:entity_key/requests/events                console          ungated
GET    /api/console/entities/:entity_key/requests/logs                /entities/:entity_key/requests/logs                  console          ungated
GET    /api/console/environments                                      /environments                                        console          feature:environments (alias)
POST   /api/console/environments                                      /create/environment                                  console          feature:environments (alias)
GET    /api/console/environments/:key                                 /environments/:key                                   console          feature:environments (alias)
GET    /api/console/exceptions                                        /policy_exceptions                                   console          feature:policies (alias)
POST   /api/console/exceptions                                        /create/policy_exception                             console          feature:policies (alias)
GET    /api/console/exceptions/:entity_key/preview/assets             /policy_exceptions/:entity_key/preview/assets        console          feature:assets (alias)
GET    /api/console/exceptions/:name                                  /policy_exceptions/:name                             console          feature:policies (alias)
GET    /api/console/forms                                             /forms                                               console          feature:forms (alias)
GET    /api/console/forms/:path                                       /forms/:path                                         console          feature:forms (alias)
GET    /api/console/gates                                             /gates                                               console          feature:gates (alias)
POST   /api/console/gates                                             /commit/controls/gates                               console          feature:gates (alias)
GET    /api/console/gates/:entity_id/permissions                      /entities/gate/:entity_id/permissions                console          feature:gates
GET    /api/console/gates/:entity_key/policies/controls               /console/gates/:entity_key/policies/controls         consulta         feature:controls
GET    /api/console/gates/:path                                       /gates/:path                                         console          feature:gates (alias)
PATCH  /api/console/gates/:path                                       /gates/:path                                         console          feature:gates (alias)
PUT    /api/console/gates/:path                                       /gates/:path                                         console          feature:gates (alias)
PATCH  /api/console/gates/:path/pause                                 /gates/:path/pause                                   console          feature:gates (alias)
POST   /api/console/gates/:path/preview/assets                        /gates/:path/preview/assets                          console          feature:assets (alias)
GET    /api/console/gates/match-schema                                /gates/match-schema                                  console          feature:gates (alias)
GET    /api/console/groups                                            /groups                                              console          feature:controls
GET    /api/console/groups                                            /groups                                              consulta         feature:groups (alias)
GET    /api/console/groups/:group_identifier                          /groups/:group_identifier                            console          feature:controls
GET    /api/console/groups/:name                                      /groups/:name                                        consulta         feature:groups (alias)
GET    /api/console/indexes/:entity_id/permissions                    /entities/index/:entity_id/permissions               console          feature:indexes
PATCH  /api/console/integrations/activate/webhooks/:id                /activate/instance_webhook/:id                       console          feature:controls (alias)
DELETE /api/console/integrations/deactivate/webhooks/:id              /deactivate/instance_webhook/:id                     console          feature:instances (alias)
PATCH  /api/console/integrations/deactivate/webhooks/:id              /deactivate/instance_webhook/:id                     console          feature:instances (alias)
GET    /api/console/integrations/instances                            /instances                                           consulta         feature:instances (alias)
POST   /api/console/integrations/instances                            /instances                                           console          feature:instances (alias)
GET    /api/console/integrations/instances/:instance                  /instances/:instance                                 consulta         feature:instances (alias)
PUT    /api/console/integrations/instances/:instance/credentials      /integrations/instances/:instance/credentials        instances        feature:instances
DELETE /api/console/integrations/instances/credentials/:uuid          /integrations/instances/credentials/:uuid            instances        feature:instances
PATCH  /api/console/integrations/instances/credentials/:uuid          /integrations/instances/credentials/:uuid            instances        feature:instances
GET    /api/console/integrations/instances/network/domains            /instances/platforms/domains                         consulta         feature:instances (alias)
GET    /api/console/integrations/platforms                            /platforms                                           console          feature:platforms (alias)
POST   /api/console/integrations/platforms                            /platforms                                           console          feature:platforms (alias)
GET    /api/console/integrations/platforms/instances                  /platforms/instances                                 consulta         feature:instances (alias)
GET    /api/console/integrations/platforms/types                      /platform_types                                      consulta         feature:instances (alias)
GET    /api/console/integrations/tools                                /tools                                               console          feature:tools (alias)
POST   /api/console/integrations/tools                                /tools                                               console          feature:tools (alias)
GET    /api/console/integrations/tools/:entity_key                    /tools/:entity_key                                   console          feature:tools (alias)
GET    /api/console/integrations/webhooks                             /instances/webhooks                                  console          feature:instances (alias)
POST   /api/console/integrations/webhooks                             /instances/webhooks                                  console          feature:instances (alias)
GET    /api/console/integrations/webhooks/:entity_key                 /instances/webhooks/:entity_key                      console          feature:instances (alias)
GET    /api/console/plugins                                           /plugins                                             console          ungated (alias)
GET    /api/console/plugins/:name                                     /plugins/:name                                       console          ungated (alias)
GET    /api/console/plugins/:name/sample                              /plugins/:name/sample                                console          feature:controls (alias)
GET    /api/console/policies                                          /policies                                            console          feature:policies (alias)
POST   /api/console/policies                                          /create/policy                                       console          feature:policies (alias)
DELETE /api/console/policies/:entity_id/references/:reference_uuid    /references/:reference_uuid/bind/:entity_id          console          feature:policies
POST   /api/console/policies/:entity_id/references/:reference_uuid    /references/:reference_uuid/bind/:entity_id          console          feature:policies
GET    /api/console/policies/:entity_key/preview/assets               /policies/:entity_key/preview/assets                 console          feature:assets (alias)
GET    /api/console/policies/:name                                    /policies/:name                                      console          feature:policies (alias)
GET    /api/console/references                                        /references                                          console          ungated
POST   /api/console/references                                        /references                                          console          role:internal:system:admin,internal:system:qa
DELETE /api/console/references/:uuid                                  /references/:uuid                                    console          role:internal:system:admin,internal:system:qa
GET    /api/console/references/:uuid                                  /references/:uuid                                    console          ungated
PATCH  /api/console/references/:uuid                                  /references/:uuid                                    console          role:internal:system:admin,internal:system:qa
GET    /api/console/references/:uuid/entities                         /references/:uuid/entities                           console          ungated
POST   /api/console/references/entities/search                        /references/entities/search                          console          ungated
POST   /api/console/requests/controls                                 /request/control                                     console          feature:controls (alias)
PUT    /api/console/requests/controls                                 /request/control                                     console          feature:controls (alias)
POST   /api/console/requests/exceptions                               /request/policy_exception                            console          feature:policies (alias)
PUT    /api/console/requests/exceptions                               /request/policy_exception                            console          feature:policies (alias)
POST   /api/console/requests/policies                                 /request/policy                                      console          feature:policies (alias)
PUT    /api/console/requests/policies                                 /request/policy                                      console          feature:policies (alias)
GET    /api/console/targets                                           /targets                                             console          feature:targets (alias)
POST   /api/console/targets                                           /create/target                                       console          feature:targets (alias)
GET    /api/console/targets/:key                                      /targets/:key                                        console          feature:targets (alias)
GET    /api/console/targets/:key/environment                          /targets/:key/environment                            consulta         feature:targets,feature:environments
GET    /api/console/templates                                         /templates                                           console          feature:templates (alias)
POST   /api/console/templates                                         /templates                                           console          feature:templates (alias)
GET    /api/console/templates/:entity_id                              /templates/:entity_id                                console          feature:templates (alias)
GET    /api/console/workflows                                         /workflow/definitions                                console          feature:workflows (alias)
POST   /api/console/workflows                                         /workflow/definitions                                console          feature:workflows (alias)
GET    /api/console/workflows/:path                                   /workflow/definitions/:path                          console          feature:workflows (alias)
GET    /api/consulta/agent/status                                     /health                                              consulta         ungated
GET    /api/controls/:entity_id/attestations                          /entities/:entity_id/attestations                    consulta         feature:badge_results
GET    /api/controls/:entity_id/attestations/summary                  /entities/:entity_id/attestations/summary            consulta         feature:badge_results
POST   /api/create/applications                                       /applications                                        console          ungated
GET    /api/customers/attestations-since                              /customers/attestations-since                        consulta         ungated
GET    /api/customers/usage-statistics                                /customers/usage-statistics                          consulta         ungated
GET    /api/data/attestations/:uuid/download                          /attestations/:uuid/download                         consulta         feature:data_export
POST   /api/data/attestations/download                                /attestations/download                               consulta         feature:data_export
POST   /api/deployments/:uuid/complete                                /deployments/:uuid                                   gate_controller  feature:event_ingestion
GET    /api/deployments/records/:uuid                                 /deployments/records/:uuid                           consulta         ungated
POST   /api/devconsole/evaluate                                       /evaluate                                            evaluator        ungated
POST   /api/devconsole/transform                                      /transform                                           evaluator        ungated
POST   /api/devconsole/transform/:key                                 /transform/:key                                      evaluator        ungated
GET    /api/domains/instance                                          /domains/instance                                    instances        feature:instances
GET    /api/entities/:entity_id/history                               /entities/:entity_id/history                         console          ungated
PATCH  /api/entities/activate/collection/:id                          /activate/collection/:id                             console          feature:collections
PATCH  /api/entities/activate/collections/:id                         /activate/collection/:id                             console          feature:collections (alias)
PATCH  /api/entities/activate/control/:id                             /activate/control/:id                                console          feature:controls
PATCH  /api/entities/activate/controls/:id                            /activate/control/:id                                console          feature:controls (alias)
PATCH  /api/entities/activate/domain/:id                              /activate/domain/:id                                 console          feature:domains
PATCH  /api/entities/activate/domains/:id                             /activate/domain/:id                                 console          feature:domains (alias)
PATCH  /api/entities/activate/exception/:id                           /activate/policy_exception/:id                       console          feature:policies
PATCH  /api/entities/activate/exceptions/:id                          /activate/policy_exception/:id                       console          feature:policies (alias)
PATCH  /api/entities/activate/gates/:id                               /activate/gate/:id                                   console          feature:gates
PATCH  /api/entities/activate/plugin/:id                              /activate/plugin/:id                                 console          role:internal:system:admin
PATCH  /api/entities/activate/policies/:id                            /activate/policy/:id                                 console          feature:policies (alias)
PATCH  /api/entities/activate/policy/:id                              /activate/policy/:id                                 console          feature:policies
PATCH  /api/entities/activate/policy_exception/:id                    /activate/policy/:id                                 console          feature:policies (alias)
PATCH  /api/entities/activate/policy_exception/:id                    /activate/policy_exception/:id                       console          feature:policies (alias)
GET    /api/entities/applications/:code                               /applications/:code                                  consulta         ungated
DELETE /api/entities/archive/collection/:id                           /archive/collection/:id                              console          feature:collections
DELETE /api/entities/archive/collections/:id                          /archive/collection/:id                              console          feature:collections (alias)
DELETE /api/entities/archive/control/:id                              /archive/control/:id                                 console          feature:controls
DELETE /api/entities/archive/controls/:id                             /archive/control/:id                                 console          feature:controls (alias)
DELETE /api/entities/archive/domain/:id                               /archive/domain/:id                                  console          feature:domains
DELETE /api/entities/archive/domains/:id                              /archive/domain/:id                                  console          feature:domains (alias)
DELETE /api/entities/archive/environments/:id                         /archive/environment/:id                             console          feature:environments
DELETE /api/entities/archive/exception/:id                            /archive/policy_exception/:id                        console          feature:policies
DELETE /api/entities/archive/exceptions/:id                           /archive/policy_exception/:id                        console          feature:policies (alias)
DELETE /api/entities/archive/forms/:id                                /archive/form/:id                                    console          feature:forms
DELETE /api/entities/archive/gates/:id                                /archive/gate/:id                                    console          feature:gates
DELETE /api/entities/archive/policies/:id                             /archive/policy/:id                                  console          feature:policies (alias)
DELETE /api/entities/archive/policy/:id                               /archive/policy/:id                                  console          feature:policies
DELETE /api/entities/archive/targets/:id                              /archive/target/:id                                  console          feature:targets
POST   /api/entities/artifacts/deploy                                 /entities/artifacts/deploy                           console          feature:event_ingestion
GET    /api/entities/artifacts/exceptions/:entity_id/raw              /entities/artifacts/policy_exception/:entity_id/raw  console          ungated
GET    /api/entities/artifacts/policies/:entity_id/raw                /entities/artifacts/policy/:entity_id/raw            console          ungated
POST   /api/entities/artifacts/test                                   /entities/artifacts/test                             console          feature:event_ingestion
GET    /api/entities/classes                                          /classes                                             consulta         feature:classes
GET    /api/entities/classes/:name                                    /classes/:name                                       consulta         feature:classes
GET    /api/entities/collections                                      /collections                                         console          feature:collections
GET    /api/entities/collections/:name                                /collections/:name                                   console          feature:collections
GET    /api/entities/collections/all/controls                         /collections/controls                                consulta         feature:controls,feature:collections
POST   /api/entities/commit/control                                   /commit/control                                      console          feature:controls
POST   /api/entities/commit/gate                                      /commit/controls/gates                               console          feature:gates
GET    /api/entities/compare/*                                        /entities/compare/:*1                                console          ungated
GET    /api/entities/control/:id/policy                               /control/:id/policy                                  consulta         ungated
GET    /api/entities/controls                                         /controls                                            console          feature:controls
POST   /api/entities/controls/:entity_key/attestations/:note_uuid/templates/preview /controls/:entity_key/attestations/:note_uuid/templates/preview consulta         feature:controls
GET    /api/entities/controls/:entity_key/policies/history            /controls/:entity_key/policies/history               console          feature:policies,feature:controls
GET    /api/entities/controls/:entity_key/schemas                     /controls/:entity_key/schemas                        console          feature:controls
POST   /api/entities/controls/:entity_key/templates/export            /controls/:entity_key/templates/export               console          feature:controls
POST   /api/entities/controls/:entity_key/templates/preview           /controls/:entity_key/templates/preview              consulta         feature:controls
GET    /api/entities/controls/:path                                   /controls/:path                                      console          feature:controls
PATCH  /api/entities/controls/:path                                   /controls/:path                                      console          feature:controls
PUT    /api/entities/controls/:path                                   /controls/:path                                      console          feature:controls
GET    /api/entities/controls/:path/versions                          /controls/:path/versions                             consulta         feature:controls
GET    /api/entities/controls/id/:id                                  /controls/id/:id                                     consulta         feature:controls
POST   /api/entities/create/collection                                /create/collection                                   console          feature:collections
POST   /api/entities/create/control                                   /create/control                                      console          feature:controls
POST   /api/entities/create/domain                                    /create/domain                                       console          feature:domains
POST   /api/entities/create/environment                               /create/environment                                  console          feature:environments
POST   /api/entities/create/form                                      /create/form                                         console          feature:forms
POST   /api/entities/create/policy                                    /create/policy                                       console          feature:policies
POST   /api/entities/create/target                                    /create/target                                       console          feature:targets
POST   /api/entities/create/template                                  /templates                                           console          feature:templates
DELETE /api/entities/deactivate/collection/:id                        /deactivate/collection/:id                           console          feature:collections
PATCH  /api/entities/deactivate/collection/:id                        /deactivate/collection/:id                           console          feature:collections
DELETE /api/entities/deactivate/collections/:id                       /deactivate/collection/:id                           console          feature:collections (alias)
PATCH  /api/entities/deactivate/collections/:id                       /deactivate/collection/:id                           console          feature:collections (alias)
DELETE /api/entities/deactivate/control/:id                           /deactivate/control/:id                              console          feature:controls
PATCH  /api/entities/deactivate/control/:id                           /deactivate/control/:id                              console          feature:controls
DELETE /api/entities/deactivate/controls/:id                          /deactivate/control/:id                              console          feature:controls (alias)
PATCH  /api/entities/deactivate/controls/:id                          /deactivate/control/:id                              console          feature:controls (alias)
DELETE /api/entities/deactivate/domain/:id                            /deactivate/domain/:id                               console          feature:domains
PATCH  /api/entities/deactivate/domain/:id                            /deactivate/domain/:id                               console          feature:domains
DELETE /api/entities/deactivate/domains/:id                           /deactivate/domain/:id                               console          feature:domains (alias)
PATCH  /api/entities/deactivate/domains/:id                           /deactivate/domain/:id                               console          feature:domains (alias)
DELETE /api/entities/deactivate/forms/:id                             /deactivate/form/:id                                 console          feature:forms
DELETE /api/entities/deactivate/forms/:id                             /deactivate/form/:id                                 console          feature:forms (alias)
PATCH  /api/entities/deactivate/forms/:id                             /deactivate/form/:id                                 console          feature:forms
PATCH  /api/entities/deactivate/forms/:id                             /deactivate/form/:id                                 console          feature:forms (alias)
DELETE /api/entities/deactivate/gates/:id                             /deactivate/gate/:id                                 console          feature:gates
PATCH  /api/entities/deactivate/gates/:id                             /deactivate/gate/:id                                 console          feature:gates
DELETE /api/entities/deactivate/policies/:id                          /deactivate/policy/:id                               console          feature:policies (alias)
PATCH  /api/entities/deactivate/policies/:id                          /deactivate/policy/:id                               console          feature:policies (alias)
DELETE /api/entities/deactivate/policy/:id                            /deactivate/policy/:id                               console          feature:policies
PATCH  /api/entities/deactivate/policy/:id                            /deactivate/policy/:id                               console          feature:policies
DELETE /api/entities/delete/collection/:id                            /delete/collection/:id                               console          feature:collections
DELETE /api/entities/delete/collections/:id                           /delete/collection/:id                               console          feature:collections (alias)
DELETE /api/entities/delete/control/:id                               /delete/control/:id                                  console          feature:controls
DELETE /api/entities/delete/control/:id/versions/:version             /delete/control/:id/versions/:version                console          feature:controls
DELETE /api/entities/delete/controls/:id                              /delete/control/:id                                  console          feature:controls (alias)
DELETE /api/entities/delete/controls/:id/versions/:version            /delete/control/:id/versions/:version                console          feature:controls (alias)
DELETE /api/entities/delete/domain/:id                                /delete/domain/:id                                   console          feature:domains
DELETE /api/entities/delete/domains/:id                               /delete/domain/:id                                   console          feature:domains (alias)
DELETE /api/entities/delete/environments/:id                          /delete/environment/:id                              console          feature:environments
DELETE /api/entities/delete/exception/:id                             /delete/policy_exception/:id                         console          feature:policies
DELETE /api/entities/delete/exception/:id/versions/:version           /delete/policy_exception/:id/versions/:version       console          feature:policies
DELETE /api/entities/delete/exceptions/:id                            /delete/policy_exception/:id                         console          feature:policies (alias)
DELETE /api/entities/delete/exceptions/:id/versions/:version          /delete/policy_exception/:id/versions/:version       console          feature:policies (alias)
DELETE /api/entities/delete/forms/:id                                 /delete/form/:id                                     console          feature:forms
DELETE /api/entities/delete/gates/:id                                 /delete/gate/:id                                     console          feature:gates
DELETE /api/entities/delete/policies/:id                              /delete/policy/:id                                   console          feature:policies (alias)
DELETE /api/entities/delete/policies/:id/versions/:version            /delete/policy/:id/versions/:version                 console          feature:policies (alias)
DELETE /api/entities/delete/policy/:id                                /delete/policy/:id                                   console          feature:policies
DELETE /api/entities/delete/policy/:id/versions/:version              /delete/policy/:id/versions/:version                 console          feature:policies
DELETE /api/entities/delete/policy_exception/:id                      /delete/policy_exception/:id                         console          feature:policies (alias)
DELETE /api/entities/delete/policy_exception/:id/versions/:version    /delete/policy_exception/:id/versions/:version       console          feature:policies (alias)
DELETE /api/entities/delete/targets/:id                               /delete/target/:id                                   console          feature:targets
DELETE /api/entities/delete/template/:id                              /delete/template/:id                                 console          feature:templates
DELETE /api/entities/delete/templates/:id                             /delete/template/:id                                 console          feature:templates (alias)
GET    /api/entities/domains                                          /domains                                             console          feature:domains
GET    /api/entities/domains/:name                                    /domains/:name                                       console          feature:domains
GET    /api/entities/environments                                     /environments                                        console          feature:environments
GET    /api/entities/environments/:key                                /environments/:key                                   console          feature:environments
GET    /api/entities/exceptions                                       /policy_exceptions                                   console          feature:policies
POST   /api/entities/exceptions                                       /create/policy_exception                             console          feature:policies
GET    /api/entities/exceptions/:entity_key/preview/assets            /policy_exceptions/:entity_key/preview/assets        console          feature:assets
GET    /api/entities/exceptions/:name                                 /policy_exceptions/:name                             console          feature:policies
DELETE /api/entities/files/:name                                      /entities/files/:name                                governance       role:internal:system:admin
POST   /api/entities/files/deploy                                     /entities/files/deploy                               governance       feature:event_ingestion
GET    /api/entities/forms                                            /forms                                               console          feature:forms
GET    /api/entities/forms/:path                                      /forms/:path                                         console          feature:forms
GET    /api/entities/gates                                            /gates                                               console          feature:gates
GET    /api/entities/gates/:path                                      /gates/:path                                         console          feature:gates
PATCH  /api/entities/gates/:path                                      /gates/:path                                         console          feature:gates
PUT    /api/entities/gates/:path                                      /gates/:path                                         console          feature:gates
PATCH  /api/entities/gates/:path/pause                                /gates/:path/pause                                   console          feature:gates
POST   /api/entities/gates/:path/preview/assets                       /gates/:path/preview/assets                          console          feature:assets
GET    /api/entities/gates/id/:id                                     /gates/id/:id                                        consulta         feature:controls
GET    /api/entities/gates/match-schema                               /gates/match-schema                                  console          feature:gates
GET    /api/entities/groups                                           /groups                                              consulta         feature:groups
GET    /api/entities/groups/:name                                     /groups/:name                                        consulta         feature:groups
GET    /api/entities/indexes                                          /indexes                                             console          feature:indexes
POST   /api/entities/indexes                                          /indexes                                             console          feature:indexes
GET    /api/entities/indexes/:entity_key/preview/assets               /indexes/:entity_key/preview/assets                  console          feature:indexes
DELETE /api/entities/indexes/:key                                     /indexes/:key                                        console          role:internal:system:admin
GET    /api/entities/indexes/:key                                     /indexes/:key                                        console          feature:indexes
PATCH  /api/entities/indexes/:key                                     /indexes/:key                                        console          role:internal:system:admin
GET    /api/entities/indexes/:key/examine                             /indexes/:key/examine                                console          feature:indexes
GET    /api/entities/indexes/:key/members                             /indexes/:key/members                                console          feature:indexes
POST   /api/entities/indexes/:key/refresh                             /indexes/:key/refresh                                console          role:internal:system:admin
POST   /api/entities/indexes/preview                                  /indexes/preview                                     console          feature:indexes
GET    /api/entities/instances/:instance                              /instances/:instance                                 consulta         feature:instances
POST   /api/entities/packages/deploy                                  /packages/deploy                                     console          feature:event_ingestion
POST   /api/entities/packages/deploy/:entity                          /packages/deploy/:entity                             console          feature:event_ingestion
POST   /api/entities/packages/deploy/:entity/validate                 /packages/deploy/:entity/validate                    console          feature:event_ingestion
GET    /api/entities/plugins                                          /plugins                                             console          ungated
GET    /api/entities/plugins/:name                                    /plugins/:name                                       console          ungated
GET    /api/entities/plugins/:name/sample                             /plugins/:name/sample                                console          feature:controls
GET    /api/entities/policies                                         /policies                                            console          feature:policies
GET    /api/entities/policies/:entity_key/preview/assets              /policies/:entity_key/preview/assets                 console          feature:assets
GET    /api/entities/policies/:name                                   /policies/:name                                      console          feature:policies
POST   /api/entities/request/control                                  /request/control                                     console          feature:controls
PUT    /api/entities/request/control                                  /request/control                                     console          feature:controls
POST   /api/entities/request/exception                                /request/policy_exception                            console          feature:policies
PUT    /api/entities/request/exception                                /request/policy_exception                            console          feature:policies
POST   /api/entities/request/gate                                     /request/gate                                        console          feature:gates
PUT    /api/entities/request/gate                                     /request/gate                                        console          feature:gates
POST   /api/entities/request/policy                                   /request/policy                                      console          feature:policies
PUT    /api/entities/request/policy                                   /request/policy                                      console          feature:policies
GET    /api/entities/resources/jobs                                   /entities/jobs                                       console          ungated
GET    /api/entities/resources/jobs/:uuid                             /entities/jobs/:uuid                                 console          ungated
GET    /api/entities/resources/jobs/:uuid/subscriptions               /entities/jobs/:uuid                                 console          ungated
GET    /api/entities/targets                                          /targets                                             console          feature:targets
GET    /api/entities/targets/:key                                     /targets/:key                                        console          feature:targets
GET    /api/entities/templates                                        /templates                                           console          feature:templates
GET    /api/entities/templates/:entity_id                             /templates/:entity_id                                console          feature:templates
GET    /api/entities/tools                                            /tools                                               console          feature:tools
POST   /api/entities/tools                                            /tools                                               console          feature:tools
GET    /api/entities/tools/:entity_key                                /tools/:entity_key                                   console          feature:tools
GET    /api/entities/workflows                                        /workflow/definitions                                console          feature:workflows
POST   /api/entities/workflows                                        /workflow/definitions                                console          feature:workflows
GET    /api/entities/workflows/:path                                  /workflow/definitions/:path                          console          feature:workflows
GET    /api/events/:type                                              /events/:type                                        consulta         ungated
DELETE /api/events/registry/:uuid                                     /events/registry/:uuid                               collector        ungated
DELETE /api/events/registry/path/:path                                /events/registry/path/:path                          collector        ungated
GET    /api/evidence/activity/:entity_type/chart                      /evidence/activity/:entity_type/chart                consulta         role:internal:system:admin
GET    /api/evidence/activity/:entity_type/recent                     /evidence/activity/:entity_type/recent               consulta         role:internal:system:admin
GET    /api/evidence/assets/:asset/annotations                        /assets/:asset/annotations/export                    consulta         feature:data_export (alias)
GET    /api/evidence/assets/:asset/attestations/snapshot              /evidence/assets/:asset/attestations/snapshot        consulta         feature:badge_results
POST   /api/evidence/assets/:asset/attestations/snapshot              /evidence/assets/:asset/attestations/snapshot        consulta         feature:badge_results
GET    /api/evidence/assets/:asset/children/attestations/snapshot     /evidence/assets/:asset/children/attestations/snapshot consulta         feature:badge_results
GET    /api/evidence/assets/:asset/children/controls                  /evidence/assets/:asset/children/controls            consulta         feature:badge_results
GET    /api/evidence/assets/:asset/children/popular                   /evidence/assets/:asset/children/popular             consulta         feature:badge_results
GET    /api/evidence/assets/:asset/children/rollup                    /evidence/assets/:asset/children/rollup              consulta         feature:badge_results
GET    /api/evidence/assets/:asset/children/summary                   /evidence/assets/:asset/children/summary             consulta         feature:badge_results
GET    /api/evidence/assets/:asset/releases                           /evidence/assets/:asset/releases                     consulta         feature:badge_results
GET    /api/evidence/assets/:asset/violations                         /evidence/assets/:asset/violations                   consulta         feature:badge_results
GET    /api/evidence/assets/:asset_type/:asset_uuid/links/snapshot    /evidence/assets/:asset_type/:asset_uuid/links/snapshot onboarder        feature:badge_results
GET    /api/evidence/assets/:component/attestations                   /component/:component/snapshot                       consulta         feature:badge_results (alias)
GET    /api/evidence/assets/:uuid/modules/attestations                /evidence/assets/:asset/children/attestations/snapshot consulta         feature:badge_results (alias)
GET    /api/evidence/assets/:uuid/organizations/attestations          /applications/:uuid/snapshot                         consulta         feature:badge_results (alias)
GET    /api/evidence/assets/:uuid/reports/attestations                /assets/:uuid/attestations/export                    consulta         feature:data_export (alias)
POST   /api/evidence/assets/:uuid/reports/attestations                /assets/:uuid/attestations/export                    consulta         feature:data_export (alias)
GET    /api/evidence/assets/applications/:application/attestations    /evidence/assets/applications/:application/attestations consulta         feature:badge_results
POST   /api/evidence/assets/attestations                              /evidence/assets/attestations                        consulta         feature:badge_results
POST   /api/evidence/assets/batch/snapshot                            /evidence/assets/batch/snapshot                      consulta         feature:badge_results
POST   /api/evidence/assets/by-series                                 /evidence/assets/by-series                           consulta         ungated
GET    /api/evidence/assets/compliance                                /applications/attestations/by-assets                 consulta         feature:badge_results (alias)
POST   /api/evidence/assets/reports/pdf                               /pdf                                                 pdfgenerator     feature:data_export (alias)
GET    /api/evidence/attestations/:uuid/blobs                         /evidence/attestations/:uuid/blobs                   consulta         ungated
GET    /api/evidence/attestations/:uuid/files/download                /attestations/:uuid/download                         consulta         feature:data_export (alias)
POST   /api/evidence/attestations/by-commits                          /evidence/attestations/by-commits                    consulta         feature:badge_results
POST   /api/evidence/attestations/by-series                           /evidence/attestations/by-series                     consulta         feature:badge_results
POST   /api/evidence/attestations/files/download                      /attestations/download                               consulta         feature:data_export (alias)
GET    /api/evidence/deployments/assets/:uuid/environments            /deployments/assets/:uuid/environments               consulta         feature:badge_results
GET    /api/evidence/deployments/assets/:uuid/environments/:environment /deployments/assets/:uuid/environments/:environment  consulta         feature:badge_results
GET    /api/evidence/notes                                            /notes                                               consulta         feature:badge_results,feature:badge_drill_down (alias)
DELETE /api/evidence/notes/:uuid                                      /notes/:uuid                                         collector        role:internal:system:admin (alias)
GET    /api/evidence/notes/:uuid                                      /notes/:uuid                                         consulta         feature:badge_results (alias)
GET    /api/evidence/notes/:uuid/chain                                /notes/:uuid/chain                                   consulta         feature:badge_results,feature:badge_drill_down (alias)
PUT    /api/evidence/notes/:uuid/replay                               /notes/:uuid/replay                                  collector        feature:badge_results (alias)
POST   /api/evidence/notes/:uuid/restore                              /notes/:uuid/restore                                 collector        role:internal:system:admin (alias)
PUT    /api/evidence/notes/:uuid/retry                                /notes/:uuid/retry                                   collector        feature:badge_results (alias)
GET    /api/evidence/notes/attestations/:uuid/policy                  /note/:uuid/policy                                   consulta         ungated (alias)
POST   /api/evidence/notes/attestations/by-series                     /evidence/attestations/by-series                     consulta         feature:badge_results (alias)
POST   /api/evidence/replay                                           /evidence/replay                                     collector        feature:badge_results
GET    /api/evidence/replay/:job_id                                   /evidence/replay/:job_id                             collector        feature:badge_results
POST   /api/evidence/submit/:control_entity_key                       /evidence/submit/:control_entity_key                 evaluator        role:internal:system:admin
POST   /api/favorites                                                 /favorites                                           dictator         ungated
DELETE /api/favorites/:key                                            /favorites/:key                                      dictator         ungated
GET    /api/gate/status                                               /                                                    gate_controller  ungated
GET    /api/gates/:entity_id/attestations                             /gates/:entity_id/attestations                       consulta         role:internal:system:admin
GET    /api/gates/:entity_id/attestations/summary                     /gates/:entity_id/attestations/summary               consulta         role:internal:system:admin
POST   /api/gates/check                                               /gates/check                                         gate_controller  ungated
POST   /api/gates/check/:gate                                         /gates/check/:gate                                   gate_controller  ungated
POST   /api/gates/dependencies/check                                  /gates/dependencies/check                            gate_controller  ungated
POST   /api/gates/dependencies/check/:gate                            /gates/dependencies/check/:gate                      gate_controller  ungated
POST   /api/gates/dependencies/enforce                                /gates/dependencies/enforce                          gate_controller  ungated
POST   /api/gates/dependencies/enforce/:gate                          /gates/dependencies/enforce/:gate                    gate_controller  ungated
POST   /api/gates/enforce                                             /gates/enforce                                       gate_controller  ungated
POST   /api/gates/enforce/:gate                                       /gates/enforce/:gate                                 gate_controller  ungated
POST   /api/gates/manifests/check                                     /gates/manifests/check                               gate_controller  ungated
POST   /api/gates/manifests/check/:gate                               /gates/manifests/check/:gate                         gate_controller  ungated
POST   /api/gates/manifests/enforce                                   /gates/manifests/enforce                             gate_controller  ungated
POST   /api/gates/manifests/enforce/:gate                             /gates/manifests/enforce/:gate                       gate_controller  ungated
POST   /api/ingest/:org_identity/artifactory                          /                                                    webhooksrc_artifactory token
POST   /api/ingest/:org_identity/checkmarx                            /                                                    webhooksrc_checkmarx-hook token
POST   /api/ingest/:org_identity/cloudsmith                           /                                                    webhooksrc_cloudsmith token
POST   /api/ingest/:org_identity/gitlab                               /v1/gitlab/hook                                      scmintegration   ungated
POST   /api/ingest/:org_identity/jira                                 /                                                    webhooksrc_jira  token
POST   /api/ingest/:org_identity/sonarqube                            /                                                    webhooksrc_sonarqube token
POST   /api/ingest/:org_identity/testrail                             /                                                    webhooksrc_testrail token
POST   /api/ingest/:org_identity/xray                                 /                                                    webhooksrc_artifactory token
POST   /api/ingest/asset                                              /                                                    webhooksrc_asset feature:event_ingestion
POST   /api/ingest/blackduck                                          /                                                    webhooksrc_synopsys-blackduck feature:event_ingestion
POST   /api/ingest/blob                                               /                                                    webhooksrc_blob  feature:event_ingestion
POST   /api/ingest/checkmarx                                          /                                                    webhooksrc_checkmarx-cli feature:event_ingestion
POST   /api/ingest/containerscan                                      /                                                    webhooksrc_containerscan feature:event_ingestion
POST   /api/ingest/dast                                               /                                                    webhooksrc_dast  feature:event_ingestion
POST   /api/ingest/deployment                                         /                                                    webhooksrc_deployment feature:event_ingestion
POST   /api/ingest/deployment-package                                 /                                                    webhooksrc_deployment-package feature:event_ingestion
POST   /api/ingest/generic                                            /                                                    webhooksrc_generic feature:event_ingestion
POST   /api/ingest/helm                                               /                                                    webhooksrc_helm  feature:event_ingestion
POST   /api/ingest/iac                                                /                                                    webhooksrc_iac   feature:event_ingestion
POST   /api/ingest/keycloak                                           /                                                    webhooksrc_keycloak ungated
POST   /api/ingest/lacework                                           /                                                    webhooksrc_lacework-cli feature:event_ingestion
POST   /api/ingest/lacework/hook                                      /                                                    webhooksrc_lacework-source feature:event_ingestion
POST   /api/ingest/pipeline                                           /                                                    webhooksrc_pipeline feature:event_ingestion
POST   /api/ingest/sast                                               /                                                    webhooksrc_sast  feature:event_ingestion
POST   /api/ingest/sca                                                /                                                    webhooksrc_sca   feature:event_ingestion
POST   /api/ingest/scan                                               /                                                    webhooksrc_scan  feature:event_ingestion
POST   /api/ingest/signature                                          /                                                    webhooksrc_signature feature:event_ingestion
POST   /api/ingest/snyk                                               /                                                    webhooksrc_snyk-cli feature:event_ingestion
POST   /api/ingest/testing                                            /                                                    webhooksrc_testing feature:event_ingestion
POST   /api/ingest/wiz                                                /                                                    webhooksrc_wiz   feature:event_ingestion
GET    /api/instances                                                 /instances                                           instances        feature:instances
POST   /api/instances                                                 /instances                                           console          feature:instances
PUT    /api/instances/:instanceKey/broker                             /instances/:instanceKey/broker                       instances        feature:instances
POST   /api/instances/parse                                           /parse                                               instances        ungated
GET    /api/instances/platform                                        /instances/platform                                  instances        feature:instances,feature:platforms
GET    /api/instances/platform/:name                                  /platform/:name                                      instances        feature:platforms
GET    /api/instances/platform/type/:type                             /platform/type/:type                                 instances        feature:platforms
GET    /api/instances/platforms/:uuid/logo                            /platforms/:uuid/logo                                instances        ungated
GET    /api/instances/status                                          /                                                    instances        ungated
POST   /api/instances/stores/:instance_key/upload                     /stores/:instance_key/upload                         instances        feature:instances
GET    /api/instances/stores/secrets                                  /stores/secrets                                      instances        feature:instances
GET    /api/integrations/:uuid/logo                                   /integrations/:uuid/logo                             consulta         ungated
PATCH  /api/integrations/activate/webhooks/:id                        /activate/instance_webhook/:id                       console          feature:controls
DELETE /api/integrations/archive/instances/:id                        /archive/instance/:id                                console          feature:instances
PATCH  /api/integrations/archive/instances/:id                        /archive/instance/:id                                console          feature:instances
DELETE /api/integrations/archive/platforms/:id                        /archive/platform/:id                                console          feature:platforms
PATCH  /api/integrations/archive/platforms/:id                        /archive/platform/:id                                console          feature:platforms
DELETE /api/integrations/archive/webhooks/:id                         /archive/instance_webhook/:id                        console          feature:instances
PATCH  /api/integrations/archive/webhooks/:id                         /archive/instance_webhook/:id                        console          feature:instances
DELETE /api/integrations/deactivate/webhooks/:id                      /deactivate/instance_webhook/:id                     console          feature:instances
PATCH  /api/integrations/deactivate/webhooks/:id                      /deactivate/instance_webhook/:id                     console          feature:instances
DELETE /api/integrations/delete/instances/:id                         /delete/instance/:id                                 console          feature:instances
DELETE /api/integrations/delete/platforms/:id                         /delete/platform/:id                                 console          feature:platforms
DELETE /api/integrations/delete/webhooks/:id                          /delete/instance_webhook/:id                         console          feature:instances
GET    /api/integrations/instance_domains                             /instance_domains                                    consulta         feature:instance_domains
GET    /api/integrations/instances                                    /instances                                           consulta         feature:instances
POST   /api/integrations/instances                                    /instances                                           console          feature:instances
GET    /api/integrations/instances/:uuid/logo                         /instances/:uuid/logo                                consulta         ungated
GET    /api/integrations/instances/platforms/domains                  /instances/platforms/domains                         consulta         feature:instances
GET    /api/integrations/notifications                                /integrations/notifications                          dictator         feature:settings
DELETE /api/integrations/notifications/:channel                       /integrations/notifications/:channel                 dictator         feature:settings
GET    /api/integrations/notifications/:channel/destinations          /integrations/notifications/:channel/destinations    dictator         feature:settings
POST   /api/integrations/notifications/:channel/oauth/callback        /integrations/notifications/:channel/oauth/callback  dictator         feature:settings
GET    /api/integrations/notifications/:channel/oauth/url             /integrations/notifications/:channel/oauth/url       dictator         feature:settings
GET    /api/integrations/notifications/health                         /integrations/notifications/health                   dictator         feature:settings
GET    /api/integrations/platform_types                               /platform_types                                      consulta         feature:instances
GET    /api/integrations/platforms                                    /platforms                                           console          feature:platforms
GET    /api/integrations/platforms                                    /platforms                                           console          feature:platforms (alias)
POST   /api/integrations/platforms                                    /platforms                                           console          feature:platforms
GET    /api/integrations/platforms/:key                               /platforms/:key                                      console          feature:platforms
GET    /api/integrations/platforms/:uuid/logo                         /platforms/:uuid/logo                                consulta         ungated
GET    /api/integrations/platforms/instances                          /platforms/instances                                 consulta         feature:instances
POST   /api/integrations/stores/:instance/upload                      /stores/:instance/upload                             instances        feature:instances
GET    /api/integrations/stores/secrets                               /stores/secrets                                      instances        feature:instances
GET    /api/integrations/webhooks                                     /instances/webhooks                                  console          feature:instances
POST   /api/integrations/webhooks                                     /instances/webhooks                                  console          feature:instances
GET    /api/integrations/webhooks/:entity_key                         /instances/webhooks/:entity_key                      console          feature:instances
POST   /api/internal/upload/:control_entity_key/attestations/:action  /internal/upload/:control_entity_key/attestations/:action evaluator        role:internal:system:admin
POST   /api/inventory/landscape/tools                                 /inventory/landscape/tools                           consulta         feature:platforms,feature:tools
GET    /api/inventory/sunburst/asset                                  /inventory/sunburst/asset                            consulta         feature:badge_results
GET    /api/inventory/v2/sunburst/asset                               /inventory/v2/sunburst/asset                         consulta         feature:badge_results
GET    /api/ledger/attestations/:attestation_uuid/blobs/verification  /ledger/attestations/:attestation_uuid/blobs/verification consulta         ungated
POST   /api/ledger/entry                                              /v1/rekor/entry                                      consulta         ungated
GET    /api/ledger/root                                               /                                                    tuf              ungated
GET    /api/ledger/root/*                                             /:*1                                                 tuf              ungated
GET    /api/ledger/workload/:type/:uuid/verification                  /ledger/workload/:type/:uuid/verification            consulta         ungated
POST   /api/ledger/workloads/verification                             /ledger/verify/notes                                 consulta         ungated
GET    /api/logs                                                      /logs                                                dictator         ungated
POST   /api/logs                                                      /logs                                                dictator         ungated
GET    /api/logs/:log_id                                              /logs/:log_id                                        dictator         ungated
GET    /api/metrics/builds/by-assets                                  /metrics/builds/by-assets                            consulta         feature:badge_results
GET    /api/metrics/landscape/controls/matrix                         /metrics/landscape/controls/matrix                   consulta         ungated
GET    /api/metrics/landscape/orchestrations                          /metrics/landscape/orchestrations                    consulta         ungated
GET    /api/metrics/landscape/orchestrations/distribution             /metrics/landscape/orchestrations/distribution       consulta         ungated
GET    /api/metrics/landscape/platforms/matrix                        /metrics/landscape/platforms/matrix                  consulta         ungated
GET    /api/metrics/landscape/repositories                            /metrics/landscape/repositories                      consulta         ungated
GET    /api/metrics/performance/:performance_selection                /metrics/performance/:performance_selection          consulta         feature:badge_results
GET    /api/metrics/trends/heatbar/asset                              /metrics/trends/heatbar/asset                        consulta         feature:badge_results
GET    /api/metrics/trends/heatbar/control                            /metrics/trends/heatbar/control                      consulta         feature:badge_results
GET    /api/metrics/v2/performance/:performance_selection             /metrics/v2/performance/:performance_selection       consulta         feature:badge_results
GET    /api/metrics/v2/trends/:performance_selection/asset/control/:control_identifier /metrics/v2/trends/:performance_selection/asset/control/:control_identifier consulta         feature:badge_results
GET    /api/metrics/v2/trends/heatbar/asset                           /metrics/v2/trends/heatbar/asset                     consulta         feature:badge_results
GET    /api/metrics/v2/trends/heatbar/control                         /metrics/v2/trends/heatbar/control                   consulta         feature:badge_results
POST   /api/module                                                    /modules                                             onboarder        feature:assets
POST   /api/module/:asset/domain                                      /assets/:asset/domains                               onboarder        feature:assets
PATCH  /api/module/:asset/domain/close                                /assets/:asset/domains/close                         onboarder        feature:assets
GET    /api/module/:token/token                                       /module/:token/token                                 consulta         ungated
PATCH  /api/module/:token/token                                       /module/:token/token                                 onboarder        feature:assets
DELETE /api/module/:uuid                                              /modules/:uuid                                       onboarder        feature:assets
PATCH  /api/module/:uuid                                              /modules/:uuid                                       onboarder        feature:assets
PATCH  /api/module/:uuid/activate                                     /modules/:uuid/activate                              onboarder        feature:assets
PATCH  /api/module/:uuid/archive                                      /modules/:uuid/archive                               onboarder        feature:assets
GET    /api/module/uuid/:uuid                                         /module/uuid/:uuid                                   consulta         ungated
GET    /api/modules                                                   /modules                                             consulta         ungated
POST   /api/modules/:module/applications/:app/link                    /modules/:module/applications/:app/link              onboarder        feature:assets
DELETE /api/modules/:module/applications/unlink                       /modules/:module/applications/unlink                 onboarder        feature:assets
GET    /api/note/:uuid/chain                                          /notes/:uuid/chain                                   consulta         feature:badge_results,feature:badge_drill_down
GET    /api/note/:uuid/policy                                         /note/:uuid/policy                                   consulta         ungated
GET    /api/note/chain/source/:uuid                                   /note/chain/source/:uuid                             consulta         ungated
GET    /api/note/origin/source/:uuid                                  /note/origin/source/:uuid                            consulta         ungated
GET    /api/notes                                                     /notes                                               consulta         feature:badge_results,feature:badge_drill_down
DELETE /api/notes/:note/annotations                                   /notes/:note/annotations                             collector        role:internal:system:admin
GET    /api/notes/:note/annotations                                   /notes/:note/annotations                             consulta         feature:badge_drill_down
POST   /api/notes/:note/annotations                                   /notes/:note/annotations                             collector        feature:badge_results,feature:badge_drill_down
DELETE /api/notes/:note/annotations/:uuid                             /notes/:note/annotations/:uuid                       collector        role:internal:system:admin
GET    /api/notes/:note/controls                                      /notes/:note/controls                                collector        feature:controls
GET    /api/notes/:note/controls/evaluations/:file_name               /notes/:note/controls/evaluations/:file_name         collector        feature:controls
DELETE /api/notes/:note_uuid                                          /notes/:note_uuid                                    collector        role:internal:system:admin
GET    /api/notes/:note_uuid/history                                  /notes/:note_uuid/history                            consulta         feature:badge_results
POST   /api/notes/:note_uuid/restore                                  /notes/:note_uuid/restore                            collector        role:internal:system:admin
DELETE /api/notes/:uuid                                               /notes/:uuid                                         collector        role:internal:system:admin
GET    /api/notes/:uuid                                               /notes/:uuid                                         consulta         feature:badge_results
GET    /api/notes/:uuid/appendix/download                             /notes/:uuid/appendix/download                       consulta         feature:badge_results
GET    /api/notes/:uuid/appendix/download/:file_name                  /notes/:uuid/appendix/download/:file_name            consulta         feature:badge_results
GET    /api/notes/:uuid/appendix/download/:file_name/verify           /notes/:uuid/appendix/download/:file_name/verify     consulta         feature:badge_results
GET    /api/notes/:uuid/findings                                      /notes/:uuid/findings                                consulta         feature:badge_results
GET    /api/notes/:uuid/logs                                          /notes/:uuid/logs                                    consulta         feature:badge_results,feature:badge_drill_down
PUT    /api/notes/:uuid/replay                                        /notes/:uuid/replay                                  collector        feature:badge_results
POST   /api/notes/:uuid/restore                                       /notes/:uuid/restore                                 collector        role:internal:system:admin
PUT    /api/notes/:uuid/retry                                         /notes/:uuid/retry                                   collector        feature:badge_results
GET    /api/notes/attestations/:uuid/meta                             /notes/attestations/:uuid/meta                       consulta         feature:policies
GET    /api/notes/attestations/:uuid/policies                         /notes/attestations/:uuid/policies                   consulta         feature:badge_results
POST   /api/notes/retry                                               /                                                    retrysrc_plugins feature:badge_results
GET    /api/notifications/catalog                                     /notifications/catalog                               dictator         feature:settings
GET    /api/notifications/channels                                    /notifications/channels                              dictator         feature:settings
GET    /api/notifications/config                                      /notifications/config                                dictator         feature:settings
GET    /api/notifications/config/:type                                /notifications/config/:type                          dictator         feature:settings
GET    /api/notifications/inbox                                       /notifications/inbox                                 dictator         ungated
PATCH  /api/notifications/inbox/:uuid/read                            /notifications/inbox/:uuid/read                      dictator         ungated
PATCH  /api/notifications/inbox/read                                  /notifications/inbox/read                            dictator         ungated
GET    /api/notifications/inbox/unread-count                          /notifications/inbox/unread-count                    dictator         ungated
GET    /api/notifications/membership                                  /notifications/membership                            dictator         feature:assets
POST   /api/pinned                                                    /pinned                                              dictator         ungated
DELETE /api/pinned/:key                                               /pinned/:key                                         dictator         ungated
GET    /api/platform_types/:platform_type_match_parameter/platforms   /integrations/platform_types/:platform_type_match_parameter/platforms consulta         ungated
GET    /api/platforms                                                 /platforms                                           console          feature:platforms
GET    /api/platforms/:entity_key                                     /platforms/:entity_key                               console          feature:platforms
GET    /api/plugins/:entity_id/attestations                           /entities/:entity_id/attestations                    consulta         feature:badge_results
GET    /api/plugins/:entity_id/attestations/summary                   /entities/:entity_id/attestations/summary            consulta         feature:badge_results
GET    /api/plugins/outputs                                           /plugins/outputs                                     consulta         ungated
GET    /api/pods/assets/:asset_uuid                                   /pods/assets/:asset_uuid                             dictator         feature:assets
DELETE /api/pods/assets/:asset_uuid/:type/:key                        /pods/assets/:asset_uuid/:type/:key                  dictator         feature:assets
GET    /api/pods/assets/:asset_uuid/:type/:key                        /pods/assets/:asset_uuid/:type/:key                  dictator         feature:assets
PUT    /api/pods/assets/:asset_uuid/:type/:key                        /pods/assets/:asset_uuid/:type/:key                  dictator         feature:assets
PUT    /api/pods/assets/:asset_uuid/batch                             /pods/assets/:asset_uuid/batch                       dictator         feature:assets
GET    /api/pods/entities                                             /pods/entities                                       dictator         feature:settings
GET    /api/pods/entities/:entity_id                                  /pods/entities/:entity_id                            dictator         feature:settings
DELETE /api/pods/entities/:entity_id/:type/:key                       /pods/entities/:entity_id/:type/:key                 dictator         feature:settings
GET    /api/pods/entities/:entity_id/:type/:key                       /pods/entities/:entity_id/:type/:key                 dictator         feature:settings
PUT    /api/pods/entities/:entity_id/:type/:key                       /pods/entities/:entity_id/:type/:key                 dictator         feature:settings
PUT    /api/pods/entities/:entity_id/batch                            /pods/entities/:entity_id/batch                      dictator         feature:settings
PUT    /api/pods/entities/batch                                       /pods/entities/batch                                 dictator         feature:settings
GET    /api/pods/tenant                                               /pods/tenant                                         dictator         ungated
DELETE /api/pods/tenant/:type/:key                                    /pods/tenant/:type/:key                              dictator         feature:settings
GET    /api/pods/tenant/:type/:key                                    /pods/tenant/:type/:key                              dictator         ungated
PUT    /api/pods/tenant/:type/:key                                    /pods/tenant/:type/:key                              dictator         feature:settings
PUT    /api/pods/tenant/batch                                         /pods/tenant/batch                                   dictator         feature:settings
GET    /api/pods/users/:user_id                                       /pods/users/:user_id                                 dictator         feature:users
POST   /api/pods/users/:user_id/:type                                 /pods/users/:user_id/:type                           dictator         feature:users
DELETE /api/pods/users/:user_id/:type/:key                            /pods/users/:user_id/:type/:key                      dictator         feature:users
GET    /api/pods/users/:user_id/:type/:key                            /pods/users/:user_id/:type/:key                      dictator         feature:users
PUT    /api/pods/users/:user_id/:type/:key                            /pods/users/:user_id/:type/:key                      dictator         feature:users
PUT    /api/pods/users/:user_id/batch                                 /pods/users/:user_id/batch                           dictator         feature:users
GET    /api/pods/users/:user_id/for-you                               /pods/users/:user_id/for-you                         dictator         feature:users
GET    /api/pods/users/:user_id/inventory                             /pods/users/:user_id/inventory                       dictator         feature:users
GET    /api/pods/users/:user_id/upcoming-releases                     /pods/users/:user_id/upcoming-releases               dictator         feature:users
POST   /api/policy/test                                               /test                                                evaluator        ungated
GET    /api/project/:project/snapshot                                 /project/:project/snapshot                           consulta         feature:badge_results
GET    /api/registry                                                  /registry/components                                 consulta         ungated
GET    /api/registry/:uuid                                            /registry/components/:uuid                           consulta         ungated
GET    /api/registry/search                                           /registry/search                                     consulta         ungated
POST   /api/release                                                   /release                                             gate_controller  feature:event_ingestion
GET    /api/releases                                                  /assets                                              onboarder        feature:assets
POST   /api/releases                                                  /assets                                              onboarder        role:internal:system:admin,external:system:provider,internal:system:developer
GET    /api/releases/:release/suggestions/:platform/issues            /releases/:release/suggestions/:platform/issues      consulta         ungated
GET    /api/reportgenerator/health                                    /                                                    pdfgenerator     ungated
GET    /api/reporting/catalog/v1/blocks                               /reporting/catalog/v1/blocks                         consulta         ungated
GET    /api/reporting/catalog/v1/blocks/:blockName                    /reporting/catalog/v1/blocks/:blockName              consulta         ungated
GET    /api/reporting/catalog/v1/functions                            /reporting/catalog/v1/functions                      consulta         ungated
GET    /api/reporting/catalog/v1/functions/:funcName                  /reporting/catalog/v1/functions/:funcName            consulta         ungated
GET    /api/reporting/catalog/v1/meta                                 /reporting/catalog/v1/meta                           consulta         ungated
GET    /api/reports                                                   /reports                                             consulta         role:internal:system:admin
GET    /api/reports/:id                                               /reports/:id                                         consulta         role:internal:system:admin
GET    /api/reports/:id/metadata                                      /reports/:id/metadata                                consulta         role:internal:system:admin
POST   /api/reports/:template/export                                  /reports/:template/export                            consulta         feature:data_export
POST   /api/reports/:template/preview                                 /reports/:template/preview                           consulta         feature:data_export
GET    /api/reports/asset/:uuid/attestations/export                   /assets/:uuid/attestations/export                    consulta         feature:data_export
POST   /api/reports/asset/:uuid/attestations/export                   /assets/:uuid/attestations/export                    consulta         feature:data_export
GET    /api/reports/asset/:uuid/commit/:commit                        /pdf/:uuid/:commit                                   pdfgenerator     feature:data_export
GET    /api/request/execute                                           /request/execute                                     instances        feature:instances
GET    /api/resource-uris/collection/:collection                      /resource-uris/collection/:collection                consulta         ungated
GET    /api/resources/:resource_type/:name                            /resources/:resource_type/:name                      governance       ungated
GET    /api/resources/:resource_type/statuses                         /resources/:resource_type/statuses                   governance       ungated
GET    /api/resources/status                                          /                                                    console          ungated
PATCH  /api/rules                                                     /rules                                               onboarder        role:internal:system:admin
DELETE /api/rules/:organization/:rule_name                            /rules/:organization/:rule_name                      onboarder        role:internal:system:admin
GET    /api/series/:series_id/suggestions/:platform/issues            /series/:series_id/suggestions/:platform/issues      consulta         ungated
GET    /api/service-accounts                                          /service-accounts                                    dictator         role:internal:system:admin
POST   /api/service-accounts                                          /service-accounts                                    dictator         role:internal:system:admin
DELETE /api/service-accounts/:client_id                               /service-accounts/:client_id                         dictator         role:internal:system:admin
GET    /api/service-accounts/:client_id                               /service-accounts/:client_id                         dictator         role:internal:system:admin
PATCH  /api/service-accounts/:client_id                               /service-accounts/:client_id                         dictator         role:internal:system:admin
POST   /api/service-accounts/:client_id/rotate-secret                 /service-accounts/:client_id/rotate-secret           dictator         role:internal:system:admin
GET    /api/service-accounts/:client_id/wif-providers                 /service-accounts/:client_id/wif-providers           dictator         role:internal:system:admin
POST   /api/service-accounts/:client_id/wif-providers                 /service-accounts/:client_id/wif-providers           dictator         role:internal:system:admin
DELETE /api/service-accounts/:client_id/wif-providers/:name           /service-accounts/:client_id/wif-providers/:name     dictator         role:internal:system:admin
GET    /api/service-accounts/:client_id/wif-providers/:name           /service-accounts/:client_id/wif-providers/:name     dictator         role:internal:system:admin
PATCH  /api/service-accounts/:client_id/wif-providers/:name           /service-accounts/:client_id/wif-providers/:name     dictator         role:internal:system:admin
GET    /api/settings                                                  /settings                                            consulta         ungated
GET    /api/settings/global                                           /settings/global                                     dictator         ungated
DELETE /api/settings/global/:setting_key                              /settings/global/:setting_key                        dictator         role:internal:system:admin
GET    /api/settings/global/:setting_key                              /settings/global/:setting_key                        dictator         role:internal:system:admin
PUT    /api/settings/global/:setting_key                              /settings/global/:setting_key                        dictator         role:internal:system:admin
PUT    /api/settings/global/warnings/:setting_key                     /settings/global/warnings/:setting_key               dictator         feature:assets
GET    /api/settings/tenant                                           /settings/tenant                                     dictator         feature:settings
GET    /api/settings/tenant/:key                                      /settings/tenant/:key                                dictator         feature:settings
PUT    /api/settings/tenant/:key                                      /settings/tenant/:key                                dictator         feature:settings
GET    /api/signatures/:uuid                                          /signatures/:uuid                                    consulta         ungated
GET    /api/sources                                                   /catalog                                             consulta         ungated
GET    /api/sources/:key                                              /catalog/:key                                        consulta         ungated
POST   /api/statistics/timeseries/controls/by-result                  /statistics/timeseries/controls/by-result            consulta         feature:badge_results
GET    /api/stores/:store/authorization-models                        /stores/:store/authorization-models                  openfga          role:internal:system:admin
POST   /api/stores/:store/authorization-models                        /stores/:store/authorization-models                  openfga          role:internal:system:admin
POST   /api/stores/:store/batch-check                                 /stores/:store/batch-check                           openfga          role:internal:system:admin
GET    /api/stores/:store/changes                                     /stores/:store/changes                               openfga          role:internal:system:admin
POST   /api/stores/:store/check                                       /stores/:store/check                                 openfga          role:internal:system:admin
POST   /api/stores/:store/expand                                      /stores/:store/expand                                openfga          role:internal:system:admin
POST   /api/stores/:store/list-objects                                /stores/:store/list-objects                          openfga          role:internal:system:admin
POST   /api/stores/:store/list-users                                  /stores/:store/list-users                            openfga          role:internal:system:admin
POST   /api/stores/:store/read                                        /stores/:store/read                                  openfga          role:internal:system:admin
POST   /api/stores/:store/streamed-list-objects                       /stores/:store/streamed-list-objects                 openfga          role:internal:system:admin
POST   /api/stores/:store/write                                       /stores/:store/write                                 openfga          role:internal:system:admin
GET    /api/team/groups/:group_id/members                             /team/groups/:group_id/members                       dictator         role:internal:system:admin
GET    /api/team/groups/:group_id/roles                               /team/groups/:group_id/roles                         dictator         role:internal:system:admin
PATCH  /api/team/groups/:group_id/roles                               /team/groups/:group_id/roles                         dictator         role:internal:system:admin
GET    /api/team/invitations                                          /team/invitations                                    dictator         ungated
POST   /api/team/invitations                                          /team/invitations                                    dictator         role:internal:system:admin
DELETE /api/team/invitations/:invitation_id                           /team/invitations/:invitation_id                     dictator         role:internal:system:admin
POST   /api/team/invitations/:invitation_id/resend                    /team/invitations/:invitation_id/resend              dictator         role:internal:system:admin
GET    /api/team/members                                              /team/members                                        dictator         ungated
DELETE /api/team/members/:user_id                                     /team/members/:user_id                               dictator         role:internal:system:admin
PATCH  /api/team/members/:user_id                                     /team/members/:user_id                               dictator         role:internal:system:admin
POST   /api/team/members/:user_id/roles                               /team/members/:user_id/roles                         dictator         role:internal:system:admin
PATCH  /api/teams/:team_uuid/permissions/:resource_level/:resource_category/:resource_key /teams/:team_uuid/permissions/:resource_level/:resource_category/:resource_key dictator         token
GET    /api/tenants                                                   /tenants                                             dictator         ungated
POST   /api/tenants                                                   /tenants                                             dictator         role:internal:system:admin
DELETE /api/tenants/:tenant_id                                        /tenants/:tenant_id                                  dictator         role:internal:system:admin
GET    /api/tenants/:tenant_id                                        /tenants/:tenant_id                                  dictator         ungated
PATCH  /api/tenants/:tenant_id/activate                               /tenants/:tenant_id/activate                         dictator         role:internal:system:admin
POST   /api/tenants/apps/github/installations                         /github/installations                                instances        token
GET    /api/tickets                                                   /tickets                                             console          ungated
GET    /api/tickets/:uuid                                             /tickets/:uuid                                       console          ungated
GET    /api/tickets/:uuid/activities                                  /tickets/:uuid/activities                            console          ungated
POST   /api/tickets/:uuid/activities                                  /tickets/:uuid/activities                            console          ungated
GET    /api/tickets/:uuid/conditions                                  /tickets/:uuid/conditions                            console          ungated
POST   /api/tickets/:uuid/refresh                                     /tickets/:uuid/refresh                               console          ungated
POST   /api/tickets/stage/gating                                      /tickets/stage/gating                                console          ungated
POST   /api/token                                                     /tokens                                              onboarder        feature:assets
GET    /api/token/:token/valid                                        /token/:token/valid                                  consulta         ungated
DELETE /api/token/:uuid                                               /tokens/:uuid                                        onboarder        feature:assets
PATCH  /api/token/:uuid/revoke                                        /tokens/:uuid/revoke                                 onboarder        feature:assets
GET    /api/tokens                                                    /tokens                                              consulta         ungated
GET    /api/tokens/:token                                             /token/:token                                        consulta         ungated
GET    /api/tokens/assets/:asset                                      /tokens/assets/:asset                                consulta         ungated
GET    /api/tokens/assets/:asset/by-module                            /tokens/assets/:asset/by-module                      consulta         ungated
GET    /api/tokens/uuid/:uuid                                         /token/uuid/:uuid                                    consulta         ungated
GET    /api/user/:user/assets                                         /user/:user/assets                                   consulta         ungated
GET    /api/user/:user/favorites                                      /user/:user/assets/favorites                         consulta         ungated
GET    /api/user/:user/pinned                                         /user/:user/assets/pinned                            consulta         ungated
GET    /api/users                                                     /users                                               consulta         ungated
DELETE /api/users/:id                                                 /users/:id                                           dictator         ungated
GET    /api/users/:id                                                 /users/:id                                           dictator         ungated
PUT    /api/users/:user/tenants/:tenant                               /users/:user/tenants/:tenant                         dictator         ungated
GET    /api/users/:user_sub/assets/permissions                        /users/:user_sub/assets/permissions                  dictator         ungated
GET    /api/users/:user_sub/entities/permissions                      /users/:user_sub/entities/permissions                dictator         ungated
GET    /api/users/:user_sub/permissions                               /users/:user_sub/permissions                         dictator         ungated
PATCH  /api/users/:user_sub/permissions/:resource_level/:resource_category/:resource_key /users/:user_sub/permissions/:resource_level/:resource_category/:resource_key dictator         token
PATCH  /api/users/:user_sub/system/permissions/:resource_level/:resource_category/:resource_key /users/:user_sub/system/permissions/:resource_level/:resource_category/:resource_key dictator         token
GET    /api/users/:user_sub/teams                                     /users/:user_sub/teams                               dictator         ungated
POST   /api/users/link                                                /users/link                                          dictator         ungated
POST   /api/users/register                                            /users/register                                      dictator         ungated
POST   /api/v1/github/hook                                            /v1/github/hook                                      scmintegration   ungated
GET    /api/v2/environments/:entity_id/preview                        /v2/environments/:entity_id/preview                  consulta         feature:badge_results
GET    /api/v2/findings                                               /v2/findings                                         consulta         feature:badge_results
GET    /api/v2/findings/:node_id/blast-radius                         /v2/findings/:node_id/blast-radius                   consulta         feature:badge_results
GET    /api/v2/findings/:node_id/lifecycle                            /v2/findings/:node_id/lifecycle                      consulta         feature:badge_results
GET    /api/v2/graph/nodes/:node_id/neighborhood                      /v2/graph/nodes/:node_id/neighborhood                consulta         feature:badge_results
GET    /api/workflow/executions                                       /workflow/executions                                 console          feature:workflows
POST   /api/workflow/executions                                       /workflow/executions                                 console          ungated
POST   /api/workflow/executions/:execution_id/parameters/:parameter_id/action /api/workflow/executions/:execution_id/parameters/:parameter_id/action console          ungated
GET    /api/workflow/executions/:id                                   /workflow/executions/:id                             console          feature:workflows
```

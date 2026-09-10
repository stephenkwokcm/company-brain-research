# Governance, ACLs, retention and erasure — the "company" half of a company brain

**Dimension key:** `g05-governance-acl`
**Researched:** 2026-09-10
**Method:** primary sources only — a local clone of `garrytan/gbrain` at commit `43597b19` (v0.48.5.0), the Onyx source tree via `gh api`, OWASP's own GitHub repos, vendor docs, and the GDPR text. WebSearch budget for this session was exhausted before I started, so everything below was reached by direct URL fetch, `curl`, or `gh api`. Where I could not reach a primary source I say so.

---

## TL;DR

1. **GBrain's access-control granularity is the *source*, not the document.** A read grant is an array of source ids on an OAuth client (`oauth_clients.federated_read`); a write grant is one source id plus an optional slug prefix. GBrain's own company-brain tutorial states the limit plainly: *"Read scoping stays source-granular in both models — within a shared source, everyone entitled to the source can read every folder."* There is no per-document ACL, no group model, no identity beyond "which OAuth client is this".
2. **GBrain's Row-Level Security is not a permission system.** `docs/guides/rls-and-you.md` is explicit: RLS is enabled on every public table with **zero policies**, purely to deny the Supabase anon key; gbrain's own connection holds `BYPASSRLS`. It is an exfiltration guard against PostgREST, not row-level authorization. The schema's actual ACL slot, `sources.config.access_policy`, is commented **"forward-compat slot, no enforcement in v0.17"** and is still unreferenced by any code in `src/` at v0.48.5.0.
3. **The reference design for permission-aware retrieval already exists in open source and GBrain does not implement it.** Onyx mirrors per-document `{external_user_emails, external_user_group_ids, is_public}` from Google Drive / Slack / Confluence / SharePoint / Jira / GitHub / Box / Teams / Gmail / Canvas, refreshes it every 5–30 minutes, fails closed when permissions can't be resolved, and injects the querying user's ACL entry list as an `OR`-within / `AND`-with-everything-else filter on the vector index. Glean's Indexing API is the same shape (`allowedUsers`, `allowedGroups`, `allowAnonymousAccess`, plus a `checkdocumentaccess` endpoint), and is likewise asynchronous — Glean warns of "a small delay before documents are visible to groups / users."
4. **A git-backed brain is erasable only by history rewrite, and the erasure does not stay local.** GBrain says so itself, under the heading *"Honest forget semantics"*: *"The repo is git history — append-only… To truly remove something: rewrite history (`git filter-repo --path <file> --invert-paths` or `--replace-text`), force-push, and re-clone on other machines."* GitHub adds that the data stays reachable by SHA-1 in cached views and in **every fork** — which GitHub cannot help you contact — until you file a Support ticket. Meanwhile `forget` in GBrain is a *fence rewrite* that keeps `~~the claim text~~` in the file plus a `forgotten: <reason>` annotation; the permanent path is documented as hand-editing the markdown. That is retraction-with-audit, which is the **opposite** of GDPR Art. 17 erasure.
5. **Two audit gaps are load-bearing.** (a) `mcp_request_log` is written only on the HTTP-MCP path — stdio MCP and local CLI access are unlogged, and GBrain's own "Model B" (one agent serves the whole team) runs through exactly those paths. (b) Its `params` column is redacted to *declared key names and bucketed byte counts* by `summarizeMcpParams`, and no result identities are stored — so the log can tell you *client X called `recall` at 14:02*, and cannot tell you *what was asked or which pages came back*. And there is no `DELETE FROM mcp_request_log` anywhere in `src/`: the retention sweep is a TODO, so the one audit table grows forever.
6. **GBrain's guardrail seam cannot enforce anything, by design.** `runGuardrails()` returns `void`, callers never branch on a verdict, and every failure mode is swallowed: *"A guardrail registered through this interface cannot block, rewrite, drop, retry, or reorder GBrain behavior."* Against OWASP's ASI06 Memory & Context Poisoning — whose first mitigation is "scan insertions for anomalies **before committing them**" — an observe-only seam is a detector, not a control. Enforcement has to live in a wrapper upstream of `gbrain import`.
7. **Recommendation for 25 people: don't buy a permission system, buy a boundary.** Three corpus zones (OPEN / SENSITIVE / EXCLUDED), default-deny at ingest, one GBrain source per zone, git for OPEN only and `db_only` for everything person-identifying, a weekly roster-to-grant reconciliation cron, a real audit table you write yourself, and a 30/90/365-day retention schedule. Roughly two engineer-days to stand up, ~2 hours/month to run. Full spec in §8.

---

## 1. What "permission-aware retrieval" means, from the systems that ship it

There are four places a permission can be enforced in a retrieval stack, and the choice determines almost everything else:

| Enforcement point | Mechanism | Cost | Failure mode |
|---|---|---|---|
| **At ingest** | don't index what the requester shouldn't see | free at query time | one index per audience; combinatorial |
| **At index partition** | namespace / collection / tenant shard per audience | cheap, strong isolation | audiences must be disjoint and few |
| **At query (pre-filter)** | ACL entries as a filter predicate ANDed into the ANN query | one join + a filter | recall collapses if the filter is post-applied (§2) |
| **At post-processing (censoring)** | drop or redact chunks after retrieval | trivial to add | the data already left the store; leaks on any bypass |

**Onyx** (open source, `onyx-dot-app/onyx`, 31,998 stars, checked 2026-09-09) is the cleanest readable implementation, and it uses points 3 and 4 together. Its permission model is a frozen dataclass in `backend/onyx/access/models.py`:

```python
@dataclass(frozen=True)
class ExternalAccess:
    MAX_NUM_ENTRIES = 5000   # "not internally enforced ... the caller can check this"
    external_user_emails: set[str]
    external_user_group_ids: set[str]
    is_public: bool
```

Four details are worth stealing outright:

- **Fail closed on unknown.** `ExternalAccess.empty()` exists specifically so that *"some document's permissions aren't able to be determined (for whatever reason). Setting its `ExternalAccess` to 'private' is a feasible fallback."*
- **Namespaced principals.** `backend/onyx/access/utils.py` prefixes every principal so identifiers from different systems cannot collide: `user_email:`, `group:`, `external_group:`, `domain:`, and external group names are further prefixed with their source (`build_ext_group_name_for_onyx`).
- **ACL is a first-class filter category.** `backend/onyx/document_index/FILTER_SEMANTICS.md` documents the join logic: ACL entries are `OR`'d within the category and `AND`'d with everything else, alongside a separate `tenant_id` category. `build_access_filters_for_user` computes the user's ACL list from Postgres at query time and hands it to the vector index.
- **Permissions are mirrored on a clock, per connector.** `backend/ee/onyx/external_permissions/sync_params.py` binds a `doc_sync` and a `group_sync` function to each source. Defaults from `ee/onyx/configs/app_configs.py`: Google Drive / Slack / Teams / GitHub / Gmail doc sync **300 s**; Confluence / Jira / Canvas / Box / SharePoint doc sync **1800 s**; group syncs 300–1800 s. Salesforce gets no doc sync at all — it gets `post_query_censoring` instead (point 4).

Note the directory: `backend/**ee**/onyx/external_permissions`. Permission syncing lives in Onyx's enterprise-edition tree under a separate licence, not in the MIT core. **The one governance feature everyone needs is the one that is monetised**, in the leading open-source product in this category. That is a market fact worth stating in the synthesis.

**Glean** models the same thing declaratively at the Indexing API: `allowAnonymousAccess` (visible to any Glean user in the org), `allowedUsers`, `allowedGroups`, `allowAllDatasourceUsersAccess`, with users and groups indexed as separate objects first, plus a `checkdocumentaccess` endpoint to verify after the fact. Glean's docs state that *"permissions and memberships are processed asynchronously, there might be a small delay before documents are visible to groups / users in Glean searches."*

**The consequence nobody states loudly enough:** every mirrored-ACL system has a *revocation lag* equal to its sync period. Between the moment HR revokes a Drive share and the moment the doc sync runs, the brain will still return the document. Onyx's is 5–30 minutes by default; Glean's is "a small delay". That is the real security property of permission mirroring, and it is the number to put in a risk register — not "we have ACLs".

---

## 2. The mechanical trap: ANN indexes and ACL filters do not compose for free

This is the part that bites teams who *do* add a permission filter, and it is a correctness bug before it is a security bug. From the **pgvector** README (the canonical source, `pgvector/pgvector`):

> "With approximate indexes, filtering is applied **after** the index is scanned. If a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only 4 rows will match on average."

So a naive `WHERE acl && $user_acl ORDER BY embedding <=> $q LIMIT 10` against an HNSW index does not return the ten best documents the user may see — it returns however many of the global top-40 happen to be visible to them, which for a narrowly-scoped person is frequently zero. The brain then confidently answers "I have nothing on that", which is indistinguishable from a genuine gap and therefore never gets reported as a bug. pgvector's own fixes: `SET hnsw.iterative_scan = strict_order` (pgvector ≥ 0.8.0, bounded by `hnsw.max_scan_tuples`), partial indexes when there are few distinct values, or list partitioning when there are many.

pgvector is also explicit about the isolation limit of a shared index:

> "For applications with multiple tenants, sharing an approximate index between tenants means vectors from one tenant can affect recall (and speed) for other tenants. For tenant isolation, use list partitioning or separate tables."

The managed vector stores have converged on partitioning for the same reason. **Pinecone** recommends *"one namespace per tenant on a serverless index"*, citing physical separation, no cross-tenant performance interference, and near-instant offboarding by namespace deletion — and explicitly warns that metadata-filter-based tenancy carries "significant performance and cost tradeoffs" (their example: querying a 1 GB namespace costs 1 RU; filtering the same tenant out of a shared 100 GB index costs 100 RU). **Qdrant** recommends the opposite default — payload partitioning on a `group_id` keyword index marked `is_tenant=true`, which co-locates a tenant's vectors on disk — and explicitly discourages collection-per-tenant (*"rarely the most efficient approach"*, with a 1000-collection default cap per Cloud cluster), reserving dedicated shards for large tenants.

The synthesis of those three: **partition by audience, filter within an audience.** Audiences are few and stable (a 25-person company has maybe three); users are many and churn. Partitioning on the small stable axis and filtering on the large one is the only combination that avoids both the index-explosion problem and the post-filter recall collapse.

### Postgres RLS, precisely

Since GBrain is Postgres-backed and the critic's brief names RLS, the exact semantics matter (postgresql.org, current docs):

- `ENABLE ROW LEVEL SECURITY` turns on default-deny; **`FORCE ROW LEVEL SECURITY`** is additionally required to subject the *table owner* to its own policies.
- Superusers and any role with `BYPASSRLS` always bypass policies — so RLS constrains only the roles you deliberately downgrade.
- Permissive policies combine with `OR`; restrictive policies combine with `AND`. `USING` gates SELECT/UPDATE/DELETE visibility, `WITH CHECK` gates INSERT/UPDATE writes. `TRUNCATE` and `REFERENCES` bypass RLS entirely.
- Documented leak channels: unique/PK/FK constraint checks bypass RLS (so a constraint violation can reveal an invisible row's existence); the planner may apply `leakproof` functions *before* the RLS check; and policies that sub-SELECT another table are subject to read-committed races unless you take `FOR SHARE` or use a security-definer function.
- `SET row_security = off` makes any query that *would* be filtered raise an error instead — the correct setting for backup jobs, and a good canary in tests.

RLS is genuinely the cheapest correct place to put a permission model in a Postgres-backed brain — but only if the application connects **as the end user's role or with a per-request session variable**, and only with `FORCE` set on brain-owned tables. GBrain does neither.

---

## 3. Where GBrain actually is

This is an audit of the shipped code and docs at `43597b19`, not a criticism of the talk. GBrain is a single-operator personal brain that grew a multi-user story; the gaps below are the shape of that history.

| Governance control | GBrain state at v0.48.5.0 | Primary source |
|---|---|---|
| Document-level ACL | **Absent.** Read grants are per-source arrays (`oauth_clients.federated_read TEXT[]`). "Within a shared source, everyone entitled to the source can read every folder." | `src/schema.sql:660-661`; `docs/tutorials/company-brain.md` §4 |
| Group / role model | **Absent.** No groups table; the principal is an OAuth client. | `src/schema.sql` (grep: no group DDL) |
| Per-user identity in the data | **Absent.** `facts` carries `source_id` + `visibility ∈ {private, world}` and **no owner/user column**. | `src/core/migrate.ts:2384-2419` |
| Write scoping | **Present, real.** `bound_slug_prefixes` rejects slug-mutating writes outside the prefix with `permission_denied`; also `bound_tools`, `bound_source_id`, `surface`, `budget_usd_per_day`. | `src/schema.sql:660-673`; tutorial §5 |
| Row-level security | **Present but not a permission model.** RLS enabled on all public tables, **no policies**, gbrain's role has `BYPASSRLS`, `ENABLE` not `FORCE`. Purpose is denying the Supabase anon key via PostgREST. Skipped entirely on PGLite. | `docs/guides/rls-and-you.md` |
| Declared ACL slot | `sources.config.access_policy` — **"forward-compat slot, no enforcement in v0.17"**; grep finds zero readers in `src/` besides the schema comment itself. | `src/schema.sql:19-24` |
| Permission mirroring from Slack/Drive/etc. | **Absent.** Connectors ingest; they do not carry ACLs. The `daily-driver` preset's read grant is *"a snapshot of all non-archived sources at registration time"* — a source added next month is not readable until you re-grant. | tutorial §5 |
| Content-level privacy | **Present, and good.** Three-layer strip: chunker strips `visibility != world` facts *before embedding*, so private text never reaches `content_chunks` or search; `get_page` strips fences when `ctx.remote === true`; git tracking is the operator's choice, with `db_only` dirs auto-gitignored. **Local CLI (`ctx.remote === false`) sees everything.** | `docs/architecture/system-of-record.md` §"The privacy boundary" |
| Audit log | **Partial.** `mcp_request_log(token_name, agent_name, operation, latency_ms, status, params, error_message)` — HTTP transport only; params redacted to declared key names + bucketed byte counts; no result identities. Described in the SoR doc as "Audit trail. Volatile by design." | `src/schema.sql:633-643`; `src/mcp/dispatch.ts:282`; `src/commands/serve-http.ts` |
| Audit retention | **None shipped.** No `DELETE FROM mcp_request_log` in `src/`. The sweep is a comment: *"The retention sweep that bounds audit-table growth (Eng D8) lives in the autopilot cycle's `purge` phase, not here."* `src/core/surface-audit.ts` says it "rides … the retention TODO". | `src/core/migrate.ts:4346`; `src/core/surface-audit.ts:10` |
| Version history retention | **None.** `page_versions` snapshots every `pages` UPDATE with no TTL, cascading only on page delete. | `src/schema.sql:569-577` |
| Erasure | **Retraction, not erasure** (§4). | `docs/architecture/system-of-record.md` §"The forget contract" |
| Legal hold / DSAR / GDPR | **Zero mentions** in `docs/` or `src/`. | grep |
| Ingest enforcement | **Observe-only by contract** (§6). | `docs/guardrails.md` |
| Credential lifecycle | Revocation exists (`gbrain auth revoke-client`), and the docs are honest that **"Rotation is not revocation — outstanding access tokens stay valid until they expire"** (default 30-day TTL on `agent register`). | tutorial §5 |

Two things GBrain does that are genuinely better than the field and worth copying regardless of what you build:

- **The RLS exemption escape hatch is "write it in blood."** To make a table anon-readable you must, in psql as a `BYPASSRLS` role, set a table comment starting `GBRAIN:RLS_EXEMPT reason=<≥4 chars>`. There is deliberately no CLI: *"A CLI command would make it easy for an agent to silently open a table to anon reads."* And `gbrain doctor` re-enumerates every exemption by name on every run — *"The escape hatch is not a one-time sign-off, it's a recurring reminder."* That is a better design than most enterprise RBAC consoles.
- **Provenance is a NOT NULL column.** `facts.source TEXT NOT NULL`, and the `remember` verb errors `provenance_required` on empty. Half of OWASP's ASI06 mitigation list is "require source attribution" and "track knowledge lineage"; GBrain enforces it at the type level.

---

## 4. Is a git-backed brain erasable at all?

**Short answer: yes, but only by a rewrite that fans out beyond your control, and GBrain's `forget` is not that rewrite.**

### What `forget` actually does

From `docs/architecture/system-of-record.md`, §"The forget contract":

> `gbrain forget <id>` and the MCP `forget_fact` op rewrite the fence row with strikethrough + `valid_until = today` + `context: "forgotten: <reason>"`. … Both encodings keep the row in the markdown for audit history. **To permanently delete a fact, edit the fence directly in markdown and remove the row.** The next `extract_facts` cycle wipes the DB row.

There is a good engineering reason for this shape — `src/core/facts/forget.ts` fixed a bug class where a forget implemented as a DB `UPDATE` **evaporated on the next rebuild**, because the markdown fence is canonical and the nightly cycle reconstructed the fact. Making the forget a fence rewrite is the correct fix for *durability*. It is the wrong primitive for *erasure*, and it fails in three distinct ways at once:

1. **The claim text survives.** `~~claim~~` is still the claim. Anyone reading the file, and any future model re-ingesting it, sees it.
2. **The tombstone is itself a record about the person.** `context: "forgotten: <reason>"` next to a struck-through claim about a named individual is arguably more sensitive than the original row, and it is now permanent.
3. **The DB keeps its own copy anyway.** `page_versions` snapshots `compiled_truth` on every `pages` UPDATE with no TTL. Even the "permanent" path — hand-editing the fence — leaves the pre-edit text in `page_versions` until the page row is deleted.

### What the git layer adds

GBrain's bootstrap guide says it under the heading *"Honest forget semantics"*, and the honesty is real:

> "The repo is git history — append-only. Deleting a line removes it from the working tree, not from history. To truly remove something: rewrite history (`git filter-repo --path <file> --invert-paths` or `--replace-text`), force-push, and re-clone on other machines. `MEMORY.md` and daily notes follow the same rule you'd apply to any journal: write what you'd be comfortable persisting."

GitHub's own guidance on removing sensitive data spells out what "force-push and re-clone" costs:

- Rewriting "will change the hashes of the commits that introduced the sensitive data **and all commits that came after**", and force-pushing "is forcibly updating all branches, tags, and refs … discarding any changes others may have made."
- The data "may still be accessible … directly via their SHA-1 hashes in **cached views** on GitHub." Removing those, and the diff refs in closed pull requests, requires **contacting GitHub Support**, and Support will only help "in cases where we determine that the risk can't be mitigated by rotating affected credentials" — a bar a personal-data erasure request does not obviously clear.
- **Forks are the killer:** "If the commit that introduced the sensitive data exists in any forks, it will continue to be accessible there. You will need to coordinate with the owners of the forks… **GitHub cannot provide contact information for these owners.**"

### The legal frame

GDPR **Art. 17(1)** obliges erasure "without undue delay" on any of six grounds — including consent withdrawal and "the personal data are no longer necessary in relation to the purposes for which they were collected", which is the default state of an ex-employee's Slack messages sitting in a company brain. **Art. 17(2)** goes further: a controller who made the data public must take "reasonable steps, including technical measures, to inform" other controllers processing it. The **Art. 17(3)** carve-outs (freedom of expression, legal obligation, public health, Art. 89(1) archiving/research/statistics, legal claims) do not naturally cover "our AI works better with it". **Art. 5(1)(d)** independently requires that inaccurate personal data "are erased or rectified without delay", and **Art. 5(1)(e)** (storage limitation) requires data be kept in identifiable form "no longer than is necessary".

Putting those side by side: a git-backed brain's *system of record is an append-only log distributed to every clone*, and its erasure primitive is a *tombstone that preserves the text*. These are not reconcilable by tuning. The reconciliation has to be architectural.

### The architectural answer (and it is cheap)

**Do not write erasable data to git.** GBrain already ships the mechanism — `gbrain.yml` declares `db_tracked` dirs (committed) vs `db_only` dirs (DB-persisted, auto-gitignored, restorable via `gbrain export --restore-only`). The rule that makes a git-backed brain compliant is one line in a config file:

> Any page whose content is *about a person* and not *authored as company doctrine* lives under a `db_only` path.

Then erasure is `DELETE FROM pages WHERE …` plus a `page_versions` cascade — a single transaction, no history rewrite, no fork coordination, no Support ticket. Git keeps what git is good at: versioned, reviewable, permanent company doctrine. The DB keeps what the DB is good at: mutable, deletable records about people. The `db_only` tier was built for a storage-cost reason; its highest-value use is as the **erasability boundary**.

Caveat, from GBrain's own docs: on PGLite the tiering promise is *"technically vacuous"* because the DB is a local file alongside everything else — the split only becomes real on Postgres/Supabase. A company brain that needs erasure needs `gbrain init --supabase`, not PGLite.

---

## 5. Retention and audit logs

### Retention

GBrain has retention knobs, but they are scattered and none of them cover knowledge:

| Object | Retention | Where |
|---|---|---|
| Session transcripts (local, 0700, outside repo) | `dream.synthesize.corpus_retention_days`, default **30** | `docs/guides/bootstrap.md` |
| Stop-hook buffers | **7 days** (`STOP_BUFFER_RETENTION_MS`) | `src/commands/hook.ts:120` |
| Soft-deleted pages / archived sources | **72 h** recovery window, then `purge` hard-deletes | `src/schema.sql:38-45` |
| `dream_verdicts` | 30-day `expires_at` TTL, swept by synthesize | SoR doc |
| Fact confidence | per-kind exponential half-life: event 7 d, commitment 90 d, preference 90 d, belief/fact/idea 365 d | `src/core/facts/decay.ts` |
| Shell-job / schema-mutation audit JSONL | ISO-week rotation under `~/.gbrain/audit/` | `docs/architecture/KEY_FILES.md` |
| **`mcp_request_log`** | **none** | — |
| **`page_versions`** | **none** | — |
| **Pages, facts, takes, timeline** | **none** — decay reduces confidence, it does not delete | `decay.ts` |

The half-life table is the important conceptual move and it is right: *confidence* decay is not *retention*. `KEY_FILES.md` states the distinction explicitly — "`valid_until` is temporal validity, not retention". A fact whose confidence has decayed to 0.01 is still personal data on disk. **Storage limitation is a separate axis and GBrain does not implement it for knowledge.**

### Audit

Three findings, all verifiable by grep:

1. **Coverage is transport-shaped, not access-shaped.** `INSERT INTO mcp_request_log` appears in `src/mcp/http-transport.ts` and `src/commands/serve-http.ts` — and, as a documented exception, in `src/core/surface-audit.ts` for surface mutations. Nowhere else. `surface-audit.ts` says it plainly: *"CLI-actor rows are written even though stdio ops don't otherwise log."* So the local CLI and the stdio MCP server — the paths a Claude Code plugin install and GBrain's own "Model B" fat-agent-serves-everyone pattern use — produce **no access records at all**.
2. **The log cannot answer the question you will actually be asked.** `summarizeMcpParams` (`src/mcp/dispatch.ts:282`) returns `{redacted: true, kind, declared_keys: [...], unknown_key_count, approx_bytes}` — key *names* intersected with the operation's declared schema, plus a 1 KB byte bucket "for size-probe defense". No query text, no slugs, and nothing at all about the *response*. After an incident you can prove that client `alice-daily` called `recall` 41 times on Tuesday. You cannot prove whether it saw the performance reviews.
3. **It never expires.** No delete statement against that table exists in `src/`. Combined with (2), the log accumulates timing and frequency metadata about every employee's agent usage, forever, in a table the SoR doc calls "volatile by design".

OWASP's Agentic Security Initiative had a candidate risk for exactly this — **ASI08 Repudiation & Untraceability** in the 0.5 candidate set — whose mitigations read like a spec for the missing half: "log all delegation events with scope, originator, and receiver metadata", "implement deterministic replay systems for post-incident forensics", "tag outputs with agent ID, time, and execution context". Notably, that candidate **did not survive consolidation into the first public draft** (where ASI08 is Cascading Failures), which is itself a signal about how the field is prioritising: traceability got folded away while poisoning stayed. LLM08:2025 keeps the requirement, calling for "detailed **immutable** logs of retrieval activities".

---

## 6. Memory poisoning, and what an observe-only guardrail implies

### The threat, from primary sources

**MINJA** (arXiv:2503.03704, submitted 2025-03-05, v5 revised 2026-02-12) is the load-bearing result: an attacker injects malicious records into an agent's memory bank *"without assuming that the attacker can directly modify the memory bank"* — only "by interacting with the agent via queries and output observations", using bridging steps and a progressively-shortened indication prompt so the malicious record is retrieved naturally on a later victim query. The authors' framing is the one that matters for a company brain: *"MINJA enables **any user** to influence agent memory."*

The follow-up study (arXiv:2601.05504, Jan 2026) is the more useful one operationally. It quotes MINJA's headline as ">95% injection success rate and 70% attack success rate **under idealized conditions**", then shows that *"realistic conditions with pre-existing legitimate memories dramatically reduce attack effectiveness"*, and that both of their defenses — composite-trust I/O moderation, and memory sanitization with temporal decay + trust-aware retrieval — need careful threshold calibration to avoid "overly conservative rejection (blocking all entries)". So: a mature, populated brain is meaningfully harder to poison than a fresh one, and defenses over-block before they under-block.

**OWASP.** A precision note, because the prior report in this corpus (`memory-hygiene.md`) says "OWASP lists Memory Poisoning as **T1**": in the **0.5 initial candidates** it is `ASI01_Memory Poisoning.md`, and in the **first public draft of the Top 10 for Agentic Applications** it has been renumbered and broadened to **ASI06 — Memory & Context Poisoning**. Both files are in `OWASP/www-project-top-10-for-large-language-model-applications`. The "T1" label comes from the Feb 2025 *Agentic AI – Threats and Mitigations* paper's own T-numbering, which is now superseded. **The synthesis should cite it as ASI06.**

ASI01/ASI06's mitigation list is effectively a governance checklist for a company brain, and it maps cleanly onto what GBrain has and lacks:

| OWASP ASI06 mitigation | GBrain |
|---|---|
| "scan insertions for anomalies **before committing them**" | seam exists, **cannot block** (§ below) |
| "restrict memory persistence to trusted sources" | ✅ source-authority ladder in `source-attribution.md` |
| "log all memory access and modifications" | ⚠️ modifications yes (`page_versions`, timeline); **access, HTTP only** |
| "segment memory access using session isolation" | ⚠️ source-granular only |
| "limit memory retention durations based on data sensitivity" | ❌ no knowledge retention |
| "require source attribution for all memory updates" | ✅ `facts.source NOT NULL`, `provenance_required` |
| "flag abnormal memory update frequencies" | ❌ |
| "version control for memory updates … audit, rollback, tamper detection" | ✅ git + `page_versions` |
| "rollback and snapshot mechanisms" | ✅ git revert, `--asof` history paths |

Also relevant: **LLM08:2025 Vector and Embedding Weaknesses** states the multi-tenant failure directly — *"embeddings from one group might be inadvertently retrieved in response to queries from another group's LLM, potentially leaking sensitive business information"* — and prescribes "fine-grained access controls and **permission-aware vector and embedding stores**" with "strict logical and access partitioning of datasets in the vector database". And **ASI03 Privilege Compromise** names the pattern a company brain creates by construction: "delegation without scope reduction, causing privilege inheritance" and "memory-based elevation (e.g. cached admin instructions reused out of context)".

### What GBrain's guardrail contract implies

`docs/guardrails.md` states five hard invariants, enforced by `test/guardrails.test.ts`:

> **Observe-only.** `runGuardrails()` returns `void`. Callers never branch on a provider verdict. A guardrail registered through this interface *cannot* block, rewrite, drop, retry, or reorder GBrain behavior. Enforcement, if ever added, will get its own explicitly-named seam and its own RFC.
> **Fail open.** Missing config, provider throw/reject, timeout, and network error are all swallowed.
> **No verdict persistence.** GBrain writes no guardrail rows. Providers own their own audit trail.

Five seams exist (`file_storage.markdown`, `file_storage.code`, `ai_gateway.chat`, `ai_gateway.expand`, `ai_gateway.tool_input`), they fire inline at the right moments (pre-hash, pre-chunk, pre-embed, pre-inference), and module *loading* is fail-closed (`GBRAIN_GUARDRAILS_MODULE` set but broken → exit 1). The OSS distribution ships **inert**: zero providers registered.

This is an honest and well-scoped design — a shadow-mode telemetry interface, correctly labelled. But it means:

- **There is no shipped enforcement point for ingest.** A poisoned document that reaches `importFromContent` is chunked, embedded and written. The classifier watches it happen.
- **There is no shipped detection *record*.** "No verdict persistence" means that unless your provider keeps its own store, an incident leaves no trace inside the brain — the exact ASI08 repudiation failure.
- **The enforcement must therefore be upstream.** For a company brain, the practical control is a wrapper: connectors write to a quarantine directory, a classifier + policy runs there, and only cleared content is moved into the synced tree. That also fits GBrain's existing quarantine lane (`provenance: auto-extracted` + `status: unverified`, surfaced as `unverified: true` in results).

**Fruit-fly connection (one paragraph, deferring to the fly dimension):** the write-time novelty gate this project has been circling — FlyHash sparse random projection as a cheap novelty/duplicate detector at ingest — is *also* the missing enforcement primitive here. ASI06's mitigations #1 ("scan insertions for anomalies before committing") and #12 ("flag abnormal memory update frequencies") are novelty-detection problems, which is precisely what the mushroom-body Bloom-filter construction was characterised for (Dasgupta/Stevens/Navlakha). A novelty score computed at `file_storage.markdown` gives you a rate-limit signal on "this principal is writing many near-duplicate records that differ in one entity" — the observable signature of MINJA's progressive-shortening strategy. That is the cleanest place where the fly half of this project earns its keep on the company half: **the same cheap write-side gate serves quality control and poisoning defence.**

---

## 7. Multi-tenancy for agent memory: the landscape is thinner than the retrieval landscape

Where the enterprise-search products (Onyx, Glean) have real permission models, the agent-memory systems mostly have **routing keys the caller supplies**, not authenticated principals. Mem0's docs describe `user_id`, `agent_id`, `app_id`, `run_id` as identifiers that "scope the memory for future searches" and advise "scope each conversation with a consistent `user_id`" — the framing is organisational, and the docs I fetched make no statement about isolation enforcement or cross-tenant access prevention. The pattern generalises: if the memory API accepts a tenant id as a parameter, the security boundary is in *your* code, not theirs — a caller that can pass any `user_id` can read any user's memory. *(Confidence: HIGH for mem0's documented scoping semantics, which I fetched; MEDIUM for the generalisation across Letta/Zep/Graphiti, where I checked repo metadata but did not read their authorization code.)*

Against that, GBrain's OAuth-client scoping is actually *above* the median for this category: the grant is on a credential the server issues and validates, `federated_read` is threaded into read ops through the transport's `AuthInfo`, and write scoping via `bound_slug_prefixes` is server-enforced with a `permission_denied` error. Its limits are granularity (source, not document) and staleness (a registration-time snapshot with no re-sync), not the absence of a mechanism.

One under-appreciated GBrain design decision worth naming: **the `coding-agent` preset writes to an auto-created, DB-only `<name>-workspace` source** "so a misbehaving agent can't scribble on your wiki". Write-isolation-by-default for autonomous agents, with a read grant that must be named explicitly, is the correct shape for ASI03 (privilege compromise) — and it is a pattern most agent-memory stacks do not offer at all.

---

## 8. Recommendation: a minimal governance layer for a 25-person company brain

Design premise: **at 25 people, permission mirroring costs more than it is worth, and the cheap correct move is to constrain what enters the brain rather than who can read it.** A three-source scheme with a hard exclusion list gets you ~90% of the risk reduction of Glean-style ACLs for ~2% of the operational cost. Build the boundary first; buy the ACL system only when the boundary demonstrably blocks work.

### Layer 0 — the boundary (half a day, do this first)

Three zones. Every connector, folder and page belongs to exactly one:

| Zone | Rule | GBrain realisation |
|---|---|---|
| **OPEN** | readable by every employee; safe if it leaked to the whole company | source `shared`, `db_tracked` in `gbrain.yml`, **in git** |
| **SENSITIVE** | narrower than all-hands, but the brain adds real value | source `internal`, **`db_only`** (never committed) |
| **EXCLUDED** | never ingested at any price | not connected. Full stop. |

Populate EXCLUDED before anything else: HR files, compensation, performance reviews, legal advice, board materials, candidate feedback, security incidents, individual DMs, `#leadership`-class private channels, anything under NDA from a customer. **Default every new connector and new source to EXCLUDED and require a named human to promote it.** Write the list down; it is your data map (see Layer 4).

The single highest-leverage decision in this whole document: **SENSITIVE and anything person-identifying is `db_only`.** Git holds doctrine; the DB holds people. That makes erasure a transaction instead of a history rewrite (§4). Requires Postgres/Supabase — on PGLite the tiering is documented as vacuous.

### Layer 1 — identity and grants (half a day)

- One OAuth client per **person** (not per team), via `gbrain auth register-client` or `gbrain agent register`. `--source <their write source>`, `--federated-read <zones they're in>`, `--surface starter`.
- Per-person write confinement: `--bound-slug-prefixes partners/<slug>/`. Server-enforced, cheap, prevents the most common real incident (an agent scribbling over someone else's page).
- Agents get the `coding-agent` shape: write to their own `*-workspace`, read only what you name.
- **Verify isolation before handing out credentials**, using GBrain's own recipe: `gbrain init --mcp-only --force` on a scratch machine as each client, then `gbrain whoami` + a search for a known SENSITIVE string. Make this a checklist item on every onboarding, because it is the only test that exercises the path teammates actually use.
- Set `token_ttl` to 30 days and put renewal on the calendar. Remember: **rotation ≠ revocation** — use `gbrain auth revoke-client` for offboarding, not `--reissue`.

### Layer 2 — the reconciliation cron (2 hours; this is the piece GBrain does not have)

GBrain's read grants are **registration-time snapshots**. Nothing re-syncs them. Write a weekly job:

1. Pull the roster (Google Workspace / your IdP) → set of active employees.
2. `SELECT client_id, client_name, source_id, federated_read FROM oauth_clients WHERE deleted_at IS NULL`.
3. Diff. Any client whose owner is not on the roster → **revoke immediately**. Any grant not in your zone table → alert.
4. Post the diff to a channel even when it is empty, so a silently-dead cron is visible. (GBrain's own `BRAIN_CURRENCY.md` documents an incident where autopilot was dead for 71 days behind three green dashboards — the lesson generalises.)

This is ~40 lines. It is also the entire difference between "we have access control" and "we had access control in March".

### Layer 3 — an audit log you can actually answer questions with (half a day)

Do not rely on `mcp_request_log`. Add one table you own, written at the retrieval seam:

```sql
CREATE TABLE brain_access_log (
  id           BIGSERIAL PRIMARY KEY,
  at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  principal    TEXT NOT NULL,          -- client_id AND the human it maps to
  transport    TEXT NOT NULL,          -- http | stdio | cli
  operation    TEXT NOT NULL,
  query_hash   TEXT,                   -- sha256 of query text, not the text
  result_slugs TEXT[],                 -- WHAT CAME BACK. the whole point.
  zones        TEXT[],                 -- which zones the results came from
  latency_ms   INTEGER
);
CREATE INDEX ON brain_access_log (at DESC);
CREATE INDEX ON brain_access_log (principal, at DESC);
```

Three deliberate choices: **store `result_slugs`** (without it you cannot answer "did anyone see X before we pulled it", which is the only question that gets asked); **hash the query rather than storing it** (query text from a company brain is itself sensitive — this table becomes your most sensitive object the moment it is useful); and **record `transport`** so you can see how much traffic is bypassing the logged path. Cover the stdio/CLI paths too, or accept in writing that local access is unaudited.

Then set retention — **90 days** is a defensible default for access logs — and actually run the delete, because GBrain ships no sweep for its own log either:

```sql
DELETE FROM brain_access_log  WHERE at < now() - interval '90 days';
DELETE FROM mcp_request_log   WHERE created_at < now() - interval '90 days';
```

### Layer 4 — retention and erasure (half a day + a recurring hour)

- **Write a retention schedule and put it in the brain as an OPEN page**, so the brain can answer questions about its own rules. Suggested defaults: transcripts 30 d (`dream.synthesize.corpus_retention_days`, already a knob); access logs 90 d; `page_versions` 365 d (needs a job — GBrain has none); SENSITIVE person-pages 365 d after last touch; OPEN doctrine indefinite; ex-employee personal pages purged at offboarding + 30 d.
- **One documented erasure runbook**, tested once on a dummy person before you need it: (1) `gbrain forget` the facts — knowing it is a tombstone, not a delete; (2) hand-remove the fence rows per GBrain's documented permanent path; (3) hard-delete `pages` rows and let `page_versions` cascade; (4) confirm nothing was in git — and if it was, budget a day for `git filter-repo` + force-push + re-clone on every machine + a GitHub Support ticket for cached views, and check for forks. Step 4 is the one that makes step 0 (`db_only`) worth the effort.
- **Records of processing:** a 25-person company does **not** get the Art. 30(5) small-organisation exemption here. The exemption applies only where processing is unlikely to risk rights and freedoms, **is occasional**, and involves no special-category data. A brain that continuously ingests Slack, email and meeting transcripts is by definition *not occasional*. Keep a one-page record: purposes, categories of data subjects (employees, customers, candidates), categories of data, recipients (which LLM providers see what — GBrain's docs are careful to name the extraction provider at install), transfers, **time limits for erasure**, and security measures. That page is an afternoon of work and is the single artefact that turns "we thought about it" into Art. 5(2) accountability.

### Layer 5 — ingest and skills (half a day)

- **Quarantine lane.** Connectors write to `inbox/`; a policy step (secret scan, PII detector, a novelty/duplicate gate, your zone classifier) runs there; only cleared files move into the synced tree. This is where enforcement can live, because GBrain's guardrail seam by contract cannot enforce. Register a guardrail provider too — for the telemetry — but do not mistake it for a control.
- **Treat `SKILL.md` as the highest-privilege object in the brain.** Skills are procedural memory that agents execute; a poisoned skill is remote code execution with a friendly face, and Tan's own line is that "a bad skill file encodes a bad process forever". Skills live in git, under CODEOWNERS, with human PR review, and they never come from an auto-ingest path. GBrain's `skillopt` no-regression gate (median-of-3 judges, ε = 0.05, disjoint held-out set) is a quality gate, not a security gate — it will happily accept a malicious edit that scores well.
- **Keep the auto-extraction quarantine visible.** GBrain already stamps `provenance: auto-extracted` + `status: unverified` and surfaces `unverified: true` in results; make "unverified content was used in this answer" a visible marker in whatever UI your team touches.

### What to deliberately *not* build at 25 people

Per-document ACLs; group hierarchies; permission mirroring from Drive/Slack; per-tenant index partitions; cryptographic provenance chains; a policy engine. Every one of them is correct at 250 people and a maintenance sink at 25. The tripwire that says "now build the real thing": **the EXCLUDED list starts blocking work people legitimately need** — that is the moment the boundary stops paying for itself and ACLs start.

### If you do need per-document ACLs later

Copy Onyx, do not invent: an `access_control_list TEXT[]` on the page/chunk row with namespaced principals (`user_email:`, `group:`, `external_group:`), a GIN index on it, the querying user's entry list computed in Postgres and ANDed into the query, and `is_public` as a separate boolean. Then handle the ANN trap from §2 — `hnsw.iterative_scan = strict_order` on pgvector ≥ 0.8.0, or partition by zone — and measure recall *for a narrowly-scoped user*, not for an admin. An ACL filter that silently drops recall to zero for your most restricted employee is the failure nobody catches, because that employee's brain just looks unhelpful.

---

## Open questions / what I could not verify

1. **The OWASP *Agentic AI – Threats and Mitigations* PDF is gated** (the download link returns a "No Access" HTML page). I confirmed the resource page metadata — OWASP Agentic Security Initiative, published 2025-02-17 — and got the taxonomy from OWASP's own GitHub instead, which is arguably the better primary source. The "T1" numbering used elsewhere in this corpus comes from that PDF and is superseded by ASI06.
2. **Onyx's `ee/` licence text** — the GitHub contents API returned no decodable body for `backend/ee/onyx/LICENSE`. The directory structure (`ee/`) and the repo's `NOASSERTION` top-level licence are strong evidence for the "enterprise edition" reading, but I did not read the licence itself. *(Confidence: MEDIUM on the exact licensing terms; HIGH that permission syncing lives outside the MIT-licensed core tree.)*
3. **Letta / Zep / Graphiti authorization internals** — I checked repo metadata and ran code searches but did not read their access-control code. My claim about routing-keys-not-principals is HIGH confidence for mem0 (fetched docs) and MEDIUM as a generalisation.
4. **Whether `gbrain doctor`'s check set includes anything permission-shaped beyond `rls` / `rls_event_trigger` / `routing-federation`** — I listed `src/commands/doctor/checks/` (20 files) but did not read each check. `routing-federation.ts` is the likely home of any federated-read validation and is worth a follow-up read.
5. **Whether any GBrain deployment has actually run the Model A isolation verification and found a leak.** The tutorial's claim is "leak-free isolation across every read path"; the verification recipe is sound; I found no published result either way. Given the local-CLI bypass (`ctx.remote === false` sees full fences), the claim is true *of the HTTP path* and false as stated of "every read path".
6. **A quantified revocation-lag incident.** Onyx's 5–30 min windows and Glean's "small delay" are documented; I found no published measurement of what leaks in that window in practice. This is a genuinely open empirical question and a good crux experiment for the design panel.

---

## Sources

**GBrain (local clone, commit `43597b19`, v0.48.5.0 — all paths under https://github.com/garrytan/gbrain/blob/master/)**
- `docs/guides/rls-and-you.md` — RLS posture, `BYPASSRLS`, `ENABLE` vs `FORCE`, `GBRAIN:RLS_EXEMPT` escape hatch, PGLite skip
- `docs/tutorials/company-brain.md` — Model A / Model B, `--source` + `--federated-read`, `--bound-slug-prefixes`, "read scoping stays source-granular", registration-time read snapshot, rotation ≠ revocation, isolation verification recipe
- `docs/architecture/system-of-record.md` — the privacy boundary (3-layer strip), the forget contract, `mcp_request_log` "volatile by design", DB-only-by-design table
- `docs/guides/bootstrap.md` — "Honest forget semantics" (`git filter-repo`, force-push, re-clone); transcript retention 0700 / 30 days
- `docs/guardrails.md` — observe-only, fail-open, no verdict persistence, five seams, inert by default, fail-closed module loading
- `docs/architecture/topologies.md` — thin client, `gbrain auth register-client` scoping flags
- `docs/storage-tiering.md` — `db_tracked` vs `db_only`; PGLite tiering "technically vacuous"
- `docs/architecture/KEY_FILES.md` — `surface-audit.ts` ("rides … the retention TODO"), `valid_until` is validity not retention, shell-job audit JSONL
- `src/schema.sql` — L19–24 `access_policy` "no enforcement in v0.17"; L26–56 `sources`; L569–577 `page_versions`; L633–643 `mcp_request_log`; L648–689 `oauth_clients` / `oauth_tokens`
- `src/core/migrate.ts` — L2384–2419 `facts` DDL (`visibility private|world`, no owner column); L4346 audit-retention sweep comment
- `src/mcp/dispatch.ts:282` — `summarizeMcpParams` redaction
- `src/mcp/http-transport.ts`, `src/commands/serve-http.ts` — the only `mcp_request_log` writers
- `src/core/facts/decay.ts` — per-kind half-lives
- `src/commands/hook.ts:120,128` — `STOP_BUFFER_RETENTION_MS`, `CORPUS_RETENTION_DAYS_DEFAULT`

**Enterprise search / permission-aware retrieval**
- Onyx — https://github.com/onyx-dot-app/onyx (31,998 stars, checked 2026-09-09): `backend/onyx/access/models.py` (`ExternalAccess`, `MAX_NUM_ENTRIES`, `.empty()` fail-closed), `backend/onyx/access/utils.py` (principal prefixes), `backend/onyx/context/search/preprocessing/access_filters.py`, `backend/onyx/document_index/FILTER_SEMANTICS.md`, `backend/ee/onyx/external_permissions/{sync_params.py,perm_sync_types.py,post_query_censoring.py}`, `backend/ee/onyx/configs/app_configs.py` (sync frequencies)
- Glean Indexing API permissions — https://developers.glean.com/api-info/indexing/documents/permissions

**Vector stores / Postgres**
- pgvector README — https://github.com/pgvector/pgvector/blob/master/README.md (§Filtering, §Multitenancy, §Iterative Index Scans)
- PostgreSQL RLS — https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Qdrant multitenancy — https://qdrant.tech/documentation/guides/multiple-partitions/
- Pinecone multitenancy — https://docs.pinecone.io/guides/index-data/implement-multitenancy

**Security / threat models**
- MINJA — https://arxiv.org/abs/2503.03704 (v5, 2026-02-12)
- Memory Poisoning Attack and Defense on Memory-Based LLM Agents — https://arxiv.org/abs/2601.05504
- OWASP ASI 0.5 candidates — https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/tree/main/initiatives/agent_security_initiative/agentic-top-10/0.5-initial-candidates (`ASI01_Memory Poisoning.md`, `ASI03_Privilege_Compromise.md`, `ASI08_Repudiation_Untraceability.md`)
- OWASP Top Ten for Agentic Applications, 1st public draft — .../agentic-top-10/Sprint 1-first-public-draft-expanded/README.md (ASI06 Memory & Context Poisoning)
- OWASP *Agentic AI – Threats and Mitigations* (resource page; PDF gated) — https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- OWASP LLM08:2025 Vector and Embedding Weaknesses — https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/
- OWASP Agent Memory Guard — https://github.com/OWASP/www-project-agent-memory-guard (Apache-2.0, 170 stars, created 2026-02-16)

**Legal / compliance**
- GDPR Art. 17 (right to erasure) — https://gdpr-info.eu/art-17-gdpr/
- GDPR Art. 5 (principles; 5(1)(c)(d)(e), 5(2)) — https://gdpr-info.eu/art-5-gdpr/
- GDPR Art. 30 (records of processing; 30(5) exemption) — https://gdpr-info.eu/art-30-gdpr/
- GitHub — removing sensitive data from a repository — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

**Agent memory**
- mem0 memory operations / scoping — https://docs.mem0.ai/core-concepts/memory-operations

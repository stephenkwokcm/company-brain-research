# g03 — Enterprise incumbents: is "company brain" just knowledge management renamed?

**Key:** `g03-enterprise-incumbents`
**Researched:** 2026-09-10
**Method note (read this first):** this session's WebSearch budget was exhausted before I started, so **every claim below comes from a direct fetch of a vendor's own documentation, a public git repo, or a public API** — no search-engine summaries, no secondary blogs. That is good for primary-source discipline and bad for adversarial coverage: vendor docs are marketing-adjacent, and I could not sweep for critical third-party evaluations or for 2026 entrants I did not already have URLs for. Where I rely on a prior worker's report rather than my own fetch, I say so.

---

## TL;DR (the answer to the objection)

**The objection is ~70% right and the remaining 30% is the whole argument.**

"Company brain" is not a new *problem*. Glean has mirrored source ACLs into a permission-aware knowledge graph since 2019; Guru has had owner-verified cards since the mid-2010s. And as of 2026 the incumbents have closed the three requirements that looked, in July, like Tan's differentiators:

- **Procedural memory (R7) is gone as a differentiator.** Glean ships Skills that "follow the open Agent Skills standard," import a `SKILL.md` straight from a GitHub URL, and auto-route by description. Notion saves a skill as a literal `SKILL.md`. Dust ships **Self Improving Skills**: a *nightly* pass that reads conversations and feedback and proposes evidence-based diffs to a skill's instructions, which a human accepts or declines. That is GBrain's `skillopt` + human gate, shipped by a competitor.
- **Write-side curation (R1/R6) exists and in one case is more automated than GBrain's.** Guru's Automated Knowledge Quality "automatically verif[ies] and unverif[ies] knowledge" from behavioral signals, logs the action, explains the reason, shows a confidence level, and **excludes unverified content from answers**. Glean has owner Verification with re-verify reminders and a task queue. Rovo has human+AI-authored Definitions. Slite flags knowledge gaps.
- **Agent-facing API (R-agent) is table stakes.** Glean, Onyx, Dust, Notion, Rovo and Microsoft all ship MCP servers in 2026; Microsoft's *federated connectors are MCP servers* — query-time retrieval with no indexing at all.

**What is actually left, and it is not nothing:**

1. **A separate, writable system of record.** Every incumbent is an *index over source systems*; the source system stays authoritative and the index is a derived, disposable projection. A GBrain-style brain is a **git repo of markdown that is itself the system of record**, which the agent writes to. That single architectural inversion is what makes per-fact provenance, temporal supersession, decay, a `forget` verb and a diffable audit trail *possible*. You cannot decay or supersede a fact you do not own.
2. **Contradiction arbitration (R4).** Grepped across **1,402 Glean doc pages: zero occurrences of "contradict."** Zero in the Microsoft 365 docs repo. Zero in Dust's docs. Guru's own quality page does not claim it. Nobody in this comparison set ships a contradiction probe. GBrain does (a cached LLM judge with six verdicts, Wilson CIs, and — importantly — it refuses to auto-resolve).
3. **Org-scoped hot/cold tiering (R3).** Everyone now has "memory," but **every incumbent memory product is per-user**: Glean ("Glean stores memory per user… doesn't share memory across users"), Copilot (in the user's Exchange mailbox), Dust ("Memories are private to each user"). GBrain's `facts → dream consolidate → takes` promotes into a **shared** cold layer with multi-holder epistemics.

**And the thing the objection is right about, in Tan's own words:** GBrain's company-brain access control is *source-granular*, not document-granular. From `docs/tutorials/company-brain.md`: **"Read scoping stays source-granular in both models — within a shared source, everyone entitled to the source can read every folder."** Glean/Onyx/Copilot/Rovo all mirror per-document ACLs from the source system and evaluate them per-user at query time. That is a category difference, not a maturity gap, and it is the single biggest reason a GBrain-shaped brain is not yet a drop-in replacement for a Glean-class product in a regulated org.

---

## 1. The architectural fork that explains every row in the table

| | **Index-over-sources** (all incumbents) | **Brain-as-system-of-record** (GBrain-style) |
|---|---|---|
| Who owns the truth | The source app (Confluence, Drive, Jira). Index is derived. | The brain's git repo. Postgres is the derived cache. |
| ACLs | **Inherited.** Crawl the permission map with the content; evaluate per-user at query. | **Invented.** No source ACLs to inherit; you must author a policy. |
| Deletion / retention | Inherited from the source + the platform's DLP/retention stack. | Must be built. GBrain's `forget` writes a `valid_until` fence — *reconstructible*, i.e. the opposite of erasure. |
| Curation | Nudge a **human** to fix the doc **in the source app** (Glean Verification tasks, Guru verifiers). | Agent rewrites the page in the brain; git is the audit log. |
| Contradictions | Not addressed (see §3). Two conflicting Confluence pages both stay indexed. | First-class: probe, judge, verdict taxonomy, human resolution command. |
| Cost of being wrong | Low — the index is rebuildable from the sources. | High — the brain *is* the artifact; bad writes compound. |

Everything downstream follows from this. Incumbents get governance for free and cannot curate (they can only *ask a human to*). Brains get curation for free and must build governance from scratch.

---

## 2. The comparison table

Legend: **✅** shipped and documented · **◐** partial / adjacent / per-user only · **❌** not found in the vendor's own docs · **n/a** structurally inapplicable.
Requirements R1–R7 are the ones extracted from the talk in `findings/rag-taxonomy.md`.

| Product | Architecture (connectors + retrieval + permissions) | R1 write-curation | R2 enrich/link | R3 hot/cold | R4 contradiction | R5 provenance | R6 librarian/prune | R7 skills | Agent API / MCP | Doc-level ACL |
|---|---|---|---|---|---|---|---|---|---|---|
| **Glean** | 100+ native + push (Indexing API) + web-history connectors; Knowledge Graph over content/people/activity; **permission mirroring** — ACLs crawled with content, evaluated per signed-in user on every surface (search, answers, agents, MCP) | ◐ human **Verification** w/ re-verify reminders + task queue; Answers, Collections, Announcements | ✅ Knowledge Graph (content×people×activity), Expert search | ◐ per-user **memory** (saved + extracted, daily consolidation, "ages out gradually") | ❌ 0/1402 doc pages mention contradiction | ◐ citations to docs the user can already open; no per-fact provenance | ◐ verification tasks + deletion handling; no automated pruning of the store | ✅ **open Agent Skills standard**, import `SKILL.md` from GitHub URL, auto-routing | ✅ MCP server + MCP Gateway + plug-ins for Claude Code/Cursor/Codex | ✅ mirrored + `allowedUsers`/`allowedGroups`/`allowAnonymousAccess` on push |
| **Onyx** (ex-Danswer) | MIT CE + EE; ~52 connector packages; hybrid vector+keyword index (Vespa/OpenSearch), agentic RAG, deep research; **permission sync only for 11 sources** (Drive, Confluence, Jira, Canvas, Box, Slack, Gmail, GitHub, Salesforce, Teams, SharePoint) at **5–30 min sync intervals**; permission enforcement is **EE-only** | ❌ (Document Sets are scoping, not curation) | ◐ | ❌ | ❌ | ◐ citations | ❌ | ◐ custom agents w/ instructions; no skills standard | ✅ MCP server (and MCP client) | ◐ mirrored for 11/52 connectors, EE-only, eventually consistent |
| **Dust** | MIT repo; managed connections (Drive, Notion, Confluence, Slack, GitHub…); **Spaces** model — admins segregate data into open/restricted spaces; access = space membership, **not** per-document mirroring | ◐ **Self Improving Skills**: nightly conversation analysis → diffs to skill instructions → human approve/decline | ◐ | ◐ per-user Agent Memory ("private to each user") | ❌ | ◐ citations | ◐ nightly analysis targets *skills*, not the corpus | ✅ Skills (instructions+knowledge+tools), Discover Skills, self-improving | ✅ Dust MCP server | ❌ space-granular, not document-granular |
| **Microsoft 365 Copilot + Graph** | **Synced** connectors (ingest → Graph, semantically indexed) **and federated connectors (MCP, query-time, no indexing)**; 100+ connectors; grounding scoped to the signed-in user's Graph permissions; Conditional Access + MFA honored; Purview/RSS/SAM for governance | ❌ (no corpus curation; SharePoint "oversharing" is the classic failure) | ◐ semantic index + semantic labels + user activities for ranking | ◐ per-user memory in a hidden Exchange folder | ❌ 0 hits in the public docs repo | ◐ citations | ◐ Purview retention/DLP on content — **but explicitly *not* on Copilot memory** | ◐ declarative agents / Copilot Studio; note "People Skills" is an HR taxonomy, not agent skills | ✅ federated connectors *are* MCP | ✅ native Graph ACLs, the strongest in the set |
| **Atlassian Rovo** | Teamwork Graph over Jira/Confluence/JSM/Loom + "100 out-of-the-box connectors"; "**Teamwork Graph runs last-mile checks, so users and apps only get access to the data they're entitled to**"; agents act **as the invoking user** | ◐ **Definitions** (AI-generated + teammate-written, editable glossary) | ✅ Teamwork Graph | ❌ | ❌ | ◐ citations | ◐ Studio governance: restrict who creates agents, owner/editor/manager roles | ✅ agent skills for Rovo agents + Rovo Dev CLI | ✅ Rovo MCP; Rovo Dev CLI connects to MCP servers | ✅ inherited, enforced at query time |
| **Guru** | Card-based KB + connectors + browser extension | ✅ **strongest in the set** — "automatically verify and unverify knowledge" from usage/views/feedback/expert signals; action logged, reason explained, confidence shown; unverified content **auto-excluded from answers** | ◐ | ◐ verified vs unverified is a crude trust tier | ❌ not claimed | ◐ verifier + timestamp per card (closest thing to per-fact provenance in the set) | ✅ automated unverification *is* pruning-by-demotion | ◐ | ◐ | ◐ card-level permissions within Guru only |
| **Notion AI** | Workspace pages + AI Connectors (Slack, Teams, Drive, GitHub, SharePoint, Jira, Salesforce…) + web; scoped to "pages… that you have access to"; always cites sources | ◐ page verification / owners (human) | ◐ | ◐ agent memory | ❌ | ◐ citations | ❌ | ✅ **Skills are pages saved as `SKILL.md`**, agent-routed, page-history versioned | ✅ Notion MCP + MCP connections for custom agents | ◐ Notion-native page permissions; connector content scoped by the connecting user |
| **Slite** | Small wiki + Ask | ◐ verified docs filter; "identifies knowledge gaps" | ❌ | ❌ | ❌ | ◐ | ◐ | ❌ | ❌ | ◐ "Ask accesses only those docs you can view" |
| **Coda Brain / Grammarly** | Could not verify: `coda.io/product/coda-brain` now 301s into the Coda help centre and the target returned 403 to an unauthenticated fetch. **Treat as unassessed.** | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| **GBrain-style company brain** | Git markdown = system of record; Postgres/PGLite = disposable cache; 4-signal retrieval (HNSW + BM25 + RRF + zero-LLM typed-edge graph) + rerank; **source-granular** OAuth scoping (`--source` / `--federated-read`, SQL-enforced) + optional write binding (`--bound-slug-prefixes`) | ✅ agent writes pages; `create_safety` hint; quarantine lane for auto-extracted pages | ✅ zero-LLM typed-edge auto-link on every write | ✅ **shared** `facts` (hot, per-kind exponential decay) → `dream consolidate` → `takes` (cold, multi-holder) | ✅ cached LLM judge, 6 verdicts, Wilson CIs, never auto-mutates | ✅ **`source` is NOT NULL on every fact**; `remember` errors `provenance_required` | ✅ 25-phase nightly dream cycle + 20 doctor checks | ✅ 142 `SKILL.md` + RESOLVER routing + `skillopt` no-regression gate | ✅ MCP (122 tools) + frozen MEMORY_VERBS v1 wire protocol | ❌ **source-granular only** (Tan's own doc, quoted below) |

---

## 3. The four findings that carry the argument

### 3.1 Nobody else does contradiction arbitration

I grepped the vendors' own complete documentation indexes:

- Glean `llms.txt`: **1,402 documented pages, 0 matches for "contradict."** There is a "Sensitive Findings" scanner, an "Access verification" tool, an agent development lifecycle with golden test sets — and no facility that notices two indexed documents disagree.
- `MicrosoftDocs/microsoft-365-docs` code search: **0 hits for "contradiction"**; 4 incidental hits for "conflicting information."
- Dust `llms.txt`: **0 matches for "contradict."**
- Guru's own Automated Knowledge Quality page describes verification, logging and confidence — and, when asked directly, contains no claim about duplicate detection or conflicting-content detection.

This is structurally explained by §1: an index-over-sources product has no authority to resolve a conflict. If Confluence page A and Jira comment B disagree, Glean's correct behaviour *is* to return both. Only a system that owns the record can arbitrate. So R4 is not an incumbent oversight — it is unavailable to them by construction.

**Caveat that keeps this honest:** GBrain's contradiction probe also does not resolve anything. It emits "paste-ready `resolution_command`s" and only the human-invoked `consolidate` phase writes `valid_until` (per `findings/gbrain-architecture.md` §4). So the real difference is *"nobody detects"* vs *"one system detects and hands a human the diff."* That is a genuine but modest delta, and it is unmeasured end-to-end.

### 3.2 Skills stopped being a differentiator during 2026

`findings/rag-taxonomy.md` concluded that R7 (procedural memory) was "the one requirement plain memory systems do not cover." Against **enterprise** incumbents that is no longer true:

- **Glean**: "Skills follow the open Agent Skills standard. This means you can bring compatible Skills from any source that follows the standard into Glean." Import from a repo root, a subtree path, or a direct `SKILL.md` link; Glean "fetches the Skill, validates it, and records the source so the Skill can stay in sync with upstream changes." Automatic routing evaluates the query against Skill descriptions.
- **Notion**: "Notion saves the skill as a `SKILL.md` file"; skills are pages, agent-routable, versioned by page history.
- **Dust**: skills are shareable packages; **Self Improving Skills** runs "every night," reads explicit (thumbs) *and implicit* signals ("a user correcting the agent's output, a tool that failed to be invoked when it should have been, a conversation that went off track"), and surfaces "syntax-highlighted diffs" for a human to Approve or Decline, with workspace- and skill-level opt-outs.

Dust's feature is the important one. It is the same shape as GBrain's `skillopt` (nightly, evidence-based, human/eval gate). GBrain's version is arguably stricter — a median-of-3 judge with an ε=0.05 acceptance margin and a mandatory disjoint held-out set — but "agent-improved skill files under a no-regression gate" is now a shipped enterprise feature, not a novel claim.

### 3.3 Every incumbent "memory" is per-user; the brain's is shared

- Glean: "Glean stores memory data at the individual user level and does not share memory data across users… memory doesn't create cross-company or cross-user learning."
- Microsoft: memories "are stored in the user's Exchange mailbox in a hidden folder."
- Dust: "Memories are private to each user… each agent maintains separate memory spaces for complete isolation."

So the industry has converged on hot memory as a *personalization* feature. Tan's R3 is a different claim: a shared organizational hot tier that gets consolidated into shared cold reference (`facts` → `takes` with `holder ∈ {self, brain, world, people/<slug>}`, weights, `since_date`/`until_date`, `superseded_by`). No incumbent in this set does that. That is real unclaimed ground — and also the exact place where the ACL problem bites hardest, because a shared hot tier is a shared blast radius.

### 3.4 The ACL gap, stated precisely and fairly

The May-2026 criticisms in `findings/garry-tan-ecosystem.md` ("single-operator, unsuitable for multi-tenant"; "Multi-tenancy, access control… Tan hasn't solved any of those") are **now partly out of date**. The September README claims "Each person on the team gets their own slice of the brain, scoped by login… We fuzz-tested this across every way you can read the brain… and got zero leaks," and `docs/tutorials/company-brain.md` documents per-teammate OAuth clients with `--source` and `--federated-read`, SQL-enforced, plus `--bound-slug-prefixes` for server-enforced write scoping.

But the granularity is the whole point, and Tan states the limit himself:

> **"Read scoping stays source-granular in both models — within a shared source, everyone entitled to the source can read every folder."**
> — `garrytan/gbrain`, `docs/tutorials/company-brain.md`

And `src/schema.sql` still carries, at line 24: `-- access_policy: forward-compat slot, no enforcement in v0.17.` RLS is present but is a defence against anonymous connections — the comment at line 1565 is explicit that "The postgres role (used by gbrain via pooler) has BYPASSRLS." The shipped `ACCESS_POLICY.md` template is a **prose policy read by the agent before responding**, with an explicit note: "For runtime enforcement of MCP operations, see TODOS.md (runtime access control)."

Compare what that has to beat:

- **Glean**: "When a connector crawls content, it also ingests the permission model from that source (ACLs, group memberships, role assignments). At query time, Glean evaluates the signed-in user's identity against those mirrored permissions before returning any results," uniformly across search, answers, agents, MCP and embedded surfaces; plus "No privilege escalation" and permission-aware chat sharing.
- **Microsoft**: "Operating inside the Microsoft 365 service boundary doesn't grant Copilot tenant-wide visibility. Data access is always scoped to the signed-in user's permissions," plus Conditional Access, MFA, Purview, Restricted SharePoint Search.
- **Rovo**: "Teamwork Graph runs last-mile checks"; "the agent is acting on that person's behalf… If the user can't comment, the agent can't comment."
- **Onyx**: the honest open-source version — permission sync exists for **11 of ~52 connectors**, is **Enterprise-Edition-only** ("Onyx's context retrieval respects user level permissions which is only configurable via the Enterprise Edition"), and runs on **5–30 minute polling intervals**, so ACLs are eventually consistent with a measurable staleness window.

Onyx's numbers are the useful calibration: even a serious, well-funded incumbent covers only ~21% of its connectors with permission sync and accepts a half-hour ACL lag. Permission mirroring is *expensive*, per-connector, and never complete. That is why "just add ACLs to GBrain" is not a sprint.

### 3.5 The governance gaps are not only on the challenger's side

Worth recording because it tempers the "incumbents have governance solved" story. Microsoft's own doc on Copilot memory states:

- "Retention policies and retention labels configured in Purview by organization admins **don't apply to Copilot memory**… There are no admin controls to enforce retention rules specifically for Copilot memory."
- "Memory and personalization actions **don't generate audit log entries** in Purview."
- "No, admins **can't restrict** what type of information is added to Copilot memory."

So the moment even Microsoft added a derived, agent-written memory store, it fell outside the retention and audit plane — the same failure mode a company brain has, at a company with a full compliance org. The lesson is not "so GBrain is fine"; it is that **agent-written memory is an unsolved governance category industry-wide**, which is a more defensible framing of the gap than "Tan forgot about ACLs."

---

## 4. So what does a GBrain-style company brain actually add?

Ranked by how well the evidence supports it.

1. **A curated, agent-writable system of record with per-fact provenance and temporal validity.** `source TEXT NOT NULL` on facts, `remember` erroring `provenance_required`, `valid_from`/`valid_until`/`superseded_by`, per-kind exponential decay, and git as the diffable audit log. No incumbent has per-fact provenance; they have per-*document* citations, which is a weaker guarantee (a citation says "this doc supports the claim," not "this claim entered the store from here at this time under this authority"). **Strength: high** — verified in the schema.
2. **Contradiction detection with a refusal to auto-resolve.** Unique in this set (§3.1). **Strength: high on existence, unmeasured on value.**
3. **A shared organizational hot→cold consolidation loop.** Unique in this set (§3.3). **Strength: high on existence, unmeasured on value.**
4. **Ownership and exit.** MIT, markdown, git, a frozen `MEMORY_VERBS v1` wire protocol with a third-party conformance harness. Glean's Knowledge Graph is not exportable as a corpus; Copilot's semantic index is not a thing you can take with you. For a startup this is a real, if unglamorous, differentiator — and it is the one an incumbent structurally cannot copy.
5. ~~Skills~~ — no longer differentiating vs Glean/Notion/Dust (§3.2).
6. ~~Agent-facing MCP~~ — universal in 2026.

**And the honest caveat that must ride along** (per critic C1 in `findings/completeness-critic.md`): none of items 1–3 has been shown to improve end-to-end answer quality over a tuned hybrid baseline. GBrain's own README simultaneously reports "+31.4 P@5 over vector-only" on a 240-page **Opus-generated** corpus and a "roughly neutral" hybrid layer on LongMemEval-S. And no vendor in this table publishes a head-to-head. The two Launch HN threads found by a prior worker are the state of the art on this: *"Have you measured the value provided by the knowledge graph layer over straight enterprise search (e.g., Glean)? Benchmarks, please"* → no benchmarks; and Almanac's founder: *"We do not have formal benchmarks to measure improvement in performance."*

## 5. What it lacks vs Glean-class products

| Gap | Incumbent state of the art | Brain state | Severity |
|---|---|---|---|
| **Document-level ACLs mirrored from source systems** | Glean/Copilot/Rovo: crawl the ACL with the content, evaluate per-user per-query, everywhere | Source-granular OAuth scoping; within a source, everyone reads every folder | **Blocking** for regulated / >50-person orgs |
| **Group + identity resolution** (Entra/Okta groups, SCIM, nested groups) | Onyx does SCIM + group sync; Glean has a People connector and RBAC | Not present | High |
| **Retention schedules, legal hold, DSAR/GDPR erasure** | Purview retention/labels/eDiscovery; Glean deletion handling; audit-log export to SIEM | `forget` writes a *reconstructible* fence (`valid_until` + strikethrough), which is the opposite of erasure; git history makes true deletion harder still | **High and architecturally awkward** — this is the sharpest collision |
| **Admin audit log of who read what** | Glean admin audit logs + customer event logs, CSV/SIEM export | Schema mutations are audited with agent identity; read auditing not evidenced | Medium |
| **Connector breadth and ACL-aware ingestion** | Glean 100+, Microsoft 100+, Rovo 100+, Onyx ~52 | Federated git sources + harness integrations; no ACL-aware crawler fleet | Medium (a brain does not need to boil the ocean) |
| **DLP / sensitive-content scanning** | Glean Protect (PII/credential infotypes, policies, moderators); Purview | Not present; `company-brainify` skill strips comp/perf/political content at export time — a curation step, not a scanner | Medium |
| **Agent governance plane** | Microsoft Agent 365 (registry, ownerless-agent flagging, least-privilege tool access, lifecycle policies); Glean ADLC + agent access policies; Rovo Studio creation limits | `skillopt` gates skill quality; no organizational agent registry | Medium — and note this is the *new* incumbent moat |
| **Independent evaluation** | Also absent, to be fair — no vendor publishes head-to-heads | Self-reported on a partly synthetic corpus | High for both sides |

---

## 6. Falsifiable claims and open questions

1. **The crux experiment nobody has run:** same corpus, same top-k, same reranker — Glean/Onyx-class hybrid retrieval vs a curated brain — scored on *knowledge-update* questions (where a fact changed) and *conflict* questions. §3.1 predicts the incumbents fail specifically on those two slices and tie elsewhere. This is cheap on LongMemEval-S's knowledge-update split and would settle the whole debate.
2. **Unverified:** whether Guru's automated verify/unverify actually reduces stale-answer rate — the confidence level and the log are claimed, the outcome metric is not.
3. **Unassessed:** Coda Brain / Grammarly (403 on the help centre). Also unassessed by me directly: 2026 entrants (Hyper, Memory Store, Almanac, Hyperspell, Savant, Within) — I am relying on `findings/projects-built-on-ideas.md` and `findings/skeptic-claims.md` for those, and the pattern reported there (episodes + extracted facts + provenance + permissioned graph, no benchmarks) is consistent with everything above.
4. **Worth verifying separately:** whether GBrain's `src/schema.sql:24` comment ("no enforcement in v0.17") is simply stale relative to the v60–v65 `oauth_clients.federated_read` migrations. The tutorial's source-granular statement is current and authoritative, so the *conclusion* holds either way, but the schema comment should not be quoted as evidence of the current state without that caveat.
5. **The strongest counter-argument to my own conclusion:** Glean now imports skills from GitHub and mirrors ACLs. If Glean shipped per-fact provenance and a contradiction probe, items 1, 2 and 3 of §4 would collapse in a single release, leaving only item 4 (ownership/exit). Nothing in Glean's architecture prevents that. The differentiator window is narrow and closing.

---

## Sources

**Fetched directly this session (all 2026-09-10):**

- Glean docs index — https://docs.glean.com/llms.txt (1,402 entries; 0 "contradict")
- https://docs.glean.com/security/security-principles.md — permission mirroring, no privilege escalation, audit logs
- https://docs.glean.com/security/knowledge-graph.md — content/people/activity pillars, 100+ connectors
- https://docs.glean.com/connectors/about.md — native / web-history / push / partner connector types
- https://docs.glean.com/connectors/crawling-refresh-rates.md — webhook vs polling freshness
- https://docs.glean.com/user-guide/assistant/skills.md — "Skills follow the open Agent Skills standard"; GitHub import; auto-routing
- https://docs.glean.com/user-guide/knowledge/verification/how-verification-works.md and `/what-does-verification-mean.md` — verification tasks, re-verify reminders, deprecation
- https://docs.glean.com/user-guide/knowledge/answers/what-are-answers-and-how-do-they-work.md
- https://docs.glean.com/administration/assistant/configuration/memory-personalization.md — saved vs extracted memories, daily consolidation, per-user isolation
- https://docs.glean.com/agents/concepts/memory.md — agent run-scoped memory
- https://docs.glean.com/administration/platform/mcp/about.md — MCP server, gateway, coding-host plug-ins
- https://developers.glean.com/api-info/indexing/documents/permissions — `allowedUsers`, `allowedGroups`, `allowAnonymousAccess`, `/checkdocumentaccess`
- https://github.com/onyx-dot-app/onyx — README; `gh api repos/onyx-dot-app/onyx` (31,998★, 4,408 forks, created 2023-04-27, pushed 2026-09-09)
- https://github.com/onyx-dot-app/onyx/blob/main/backend/ee/onyx/external_permissions/sync_params.py — `_SOURCE_TO_SYNC_CONFIG`: 11 real sources + mock
- https://github.com/onyx-dot-app/onyx/blob/main/backend/ee/onyx/configs/app_configs.py — doc/group sync frequencies (5 min default; 30 min for Confluence/Jira/Canvas/Box/SharePoint)
- `gh api repos/onyx-dot-app/onyx/contents/backend/onyx/connectors` — ~52 connector packages
- https://docs.onyx.app/overview/core_features/internal_search.md — "permissions… only configurable via the Enterprise Edition"
- https://docs.onyx.app/overview/onyx_anywhere/mcp_server.md · https://docs.onyx.app/admins/managing_features/document_sets.md · https://docs.onyx.app/llms.txt (Curator→group-based permissions migration)
- https://docs.dust.tt/llms.txt (0 "contradict"); `gh api repos/dust-tt/dust` (1,459★, MIT)
- https://docs.dust.tt/docs/user-documentation/agents/self-improving-skills.md — nightly analysis, implicit signals, diffs, approve/decline
- https://docs.dust.tt/docs/user-documentation/agents/skills/skills-overview.md
- https://docs.dust.tt/docs/user-documentation/agents/tools/agent-memory.md — "Memories are private to each user"
- https://docs.dust.tt/docs/user-documentation/admins/admin-governance/access-controls-and-permissions.md — Spaces model
- https://learn.microsoft.com/en-us/graph/connecting-external-content-connectors-overview — synced vs **federated (MCP)** connectors, semantic indexing, 100+ connectors
- https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-architecture — "Data access is always scoped to the signed-in user's permissions"
- https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/copilot/copilot-personalization-memory.md — Exchange hidden folder; **Purview retention does not apply**; **no audit log entries**; eDiscovery/Graph deletion path
- https://github.com/MicrosoftDocs/microsoft-365-docs/blob/public/microsoft-365/admin/manage/agent-365-overview.md and `/agent-registry.md` — agent governance plane
- `gh api search/code` over `MicrosoftDocs/microsoft-365-docs`: 0 hits "contradiction"
- https://www.atlassian.com/platform/teamwork-graph — "Teamwork Graph runs last-mile checks"; 100 out-of-the-box connectors
- https://support.atlassian.com/rovo/docs/rovo-agent-permissions-and-governance/ — agent acts as the invoking user; Studio creation limits; editor/manager roles
- https://support.atlassian.com/rovo/docs/definitions/ — AI-generated + teammate-written definitions
- https://support.atlassian.com/rovo/resources/ — doc index incl. `add-skills-to-rovo-agents`, `extend-rovo-dev-cli-with-agent-skills`, `connect-to-an-mcp-server-in-rovo-dev-cli`
- https://www.getguru.com/features/automated-knowledge-quality — automatic verify/unverify, logged action + reason + confidence, unverified excluded from answers
- https://www.notion.com/help/create-and-manage-skills — "Notion saves the skill as a `SKILL.md` file"
- https://www.notion.com/help/enterprise-search · https://www.notion.com/help/notion-ai-faqs · https://www.notion.com/help/sitemap.xml
- https://slite.com/ask — verified docs filter, knowledge gaps, permission-filtered
- https://coda.io/product/coda-brain → 301 → https://help.coda.io/hc/en-us/articles/40685056076685 (**403, unassessed**)
- https://raw.githubusercontent.com/garrytan/gbrain/master/src/schema.sql — L18–24 `access_policy` forward-compat slot; L661/681 `oauth_clients.federated_read`; L1563–1616 RLS + BYPASSRLS
- https://raw.githubusercontent.com/garrytan/gbrain/master/docs/tutorials/company-brain.md — Model A/B scoping; **"Read scoping stays source-granular in both models"**
- https://raw.githubusercontent.com/garrytan/gbrain/master/templates/ACCESS_POLICY.md.template — prose tiers; "For runtime enforcement of MCP operations, see TODOS.md"
- https://raw.githubusercontent.com/garrytan/gbrain/master/README.md — company-brain claims, fuzz-tested isolation

**Prior reports relied on (not re-verified here):** `findings/rag-taxonomy.md` (R1–R7), `findings/gbrain-architecture.md` (dream cycle, facts/takes, contradiction probe), `findings/garry-tan-ecosystem.md` (Vectorize / useaitechdad / colrows critiques), `findings/skeptic-claims.md` (Launch HN benchmark exchanges), `findings/projects-built-on-ideas.md` (2026 entrants), `findings/completeness-critic.md` (C1 benchmark caveat), `findings/memory-hygiene.md` (`forget` as reconstructible fence; SkillOpt).

# GBrain: architecture deep-dive

**Dimension key:** `gbrain-architecture`
**Researched:** 2026-09-10 (repo state as of commit `43597b19`, v0.48.5.0, pushed 2026-09-08)
**Repo:** https://github.com/garrytan/gbrain (public, MIT)

## TL;DR

- **The repo is real, public, and very large.** `garrytan/gbrain` — 29,763 stars, 4,441 forks, 129 contributor pages, 173 open issues, MIT, TypeScript, default branch `master`, created 2026-04-05, last push 2026-09-08, 85 releases (latest `v0.48.5.0`). ~411,000 lines of TS under `src/`, 2,191 test files, 142 `SKILL.md` files, 122 MCP tools across 23 areas, 146 numbered DB migrations. Sibling benchmark repo `garrytan/gbrain-evals` (419 stars, MIT, created 2026-04-22).
- **Storage is markdown-first, Postgres-derived.** Git repo of markdown + YAML frontmatter is the *system of record*; Postgres (or PGLite, a WASM in-process Postgres, `gbrain init --pglite`, "2 seconds, no Docker") is an explicitly *disposable derived cache* rebuilt with `gbrain sync && gbrain extract all`. Extensions: `vector`, `pg_trgm`, `pgcrypto`.
- **Retrieval is a 4-signal stack, not RAG.** HNSW pgvector + BM25 tsvector + RRF fusion + zero-LLM typed-edge graph traversal, then dedup → cross-encoder rerank → relational re-pin → alias hop → exact-lookup → evidence stamp → autocut → token budget. The graph is claimed to be the single biggest quality driver (+31.4 P@5 points over the graph-disabled variant).
- **Hot vs cold memory is a literal two-table architecture.** `facts` (hot, per-turn, owner-scoped, exponential confidence decay by kind) → nightly `dream consolidate` phase → `takes` (cold, multi-holder epistemics with weights). Every page splits into `compiled_truth` (rewritten synthesis) + `timeline` (append-only evidence).
- **The "librarian" is a 25-phase nightly cron ("dream cycle")** plus a 20-check `doctor`, a contradiction probe with an LLM judge and Wilson confidence intervals, and `gbrain lsd` ("Lateral Synaptic Drift") — a stale-biased idea-crossing pass. Talk claims (~220,000 pages) and README claims (155,795 pages / 24,589 people / 5,340 companies / 66 crons) disagree; both are self-reported and unauditable.

---

## 1. Repo facts (verifiable)

| Metric | Value | Source |
|---|---|---|
| Stars / forks / watchers-subscribers | 29,763 / 4,441 / 135 | `gh api repos/garrytan/gbrain` |
| Contributors | 129 (pagination `rel="last"` at `per_page=1`) | GitHub contributors API |
| License / language / default branch | MIT / TypeScript / `master` | ibid. |
| Created / last push | 2026-04-05T14:40:56Z / 2026-09-08T06:48:23Z | ibid. |
| Releases | 85; latest `v0.48.5.0` published 2026-09-08T03:35:57Z | GitHub releases API |
| `src/` TypeScript LOC | 411,032 | `find src -name '*.ts' \| xargs wc -l` |
| Test files | 2,191 `*.test.ts` | local clone |
| MCP tools | "122 tools across 23 areas" | `docs/TOOL_CATALOG.md` (generated file) |
| DB migrations | 146 versions in `src/core/migrate.ts` | local clone |
| Bundled skills | 142 `SKILL.md`, 85 skill dirs under `skills/` | local clone |
| Description | "Garry's Opinionated OpenClaw/Hermes Agent Brain" | repo metadata |

**Distribution warning in the README (important):** "GBrain is **NOT** distributed on npm. The npm package named `gbrain` is an unrelated package." Install is `bun install -g github:garrytan/gbrain` or git clone + `bun link`.

**Sibling repo:** https://github.com/garrytan/gbrain-evals — 419 stars, MIT, TypeScript, created 2026-04-22, last push 2026-09-09.

## 2. Storage model

**System of record = git markdown.** `docs/architecture/system-of-record.md` is unambiguous: *"The GitHub repo (markdown + frontmatter) is the system of record. The Postgres/PGLite database is a derived cache. We do not back up the database — we rebuild it from the repo."* A CI gate (`scripts/check-system-of-record.sh`) enforces it. Every knowledge category has a markdown fence and a reconciler: takes live in `<!--- gbrain:takes:begin -->` fences, facts in `<!--- gbrain:facts:begin -->` fences, links inline as `[text](slug)` / `[[slug]]`, timeline after a `<!-- timeline -->` sentinel, tags in frontmatter.

**Two engines, one schema.** `src/core/pglite-engine/` (WASM Postgres, no server) and `src/core/postgres-engine/` (Supabase / real Postgres). `src/schema.sql` is 1,618 lines. Key tables:

- `sources` — multi-brain tenancy inside one DB; every page/file/ingest row carries `source_id`; `config` JSONB holds `federated` and a forward-compat `access_policy`.
- `pages` — the unit of knowledge. Columns worth naming: `compiled_truth`, `timeline`, `frontmatter JSONB`, `emotional_weight REAL` (deterministic 0..1 salience score), `effective_date` + `effective_date_source`, `last_retrieved_at` (NULL = never retrieved), `links_extracted_at` (extraction freshness watermark), `deleted_at` (soft delete with a 72h purge window), `corpus_generation`, and a `generation BIGINT` bumped by a `BEFORE INSERT OR UPDATE` trigger for cache invalidation.
- `content_chunks` — `embedding vector(1536)` with `USING hnsw (embedding vector_cosine_ops)`, `search_vector TSVECTOR` with GIN, plus code-chunk columns (`symbol_name_qualified`, `parent_symbol_path`, `doc_comment`) and multimodal `embedding_image vector(1024)` / `embedding_multimodal`.
- `links` — the knowledge graph: `from_page_id`, `to_page_id`, `link_type`, `link_source`, `link_kind ('plain'|'typed_ner')`, `origin_page_id`/`origin_field` for frontmatter-derived edges, `resolution_type ('qualified'|'unqualified')`, uniqueness via `UNIQUE NULLS NOT DISTINCT`.
- `facts` (migration v40, `src/core/migrate.ts:2384`) — the hot layer, see §4.
- `takes`, `timeline_entries`, `open_loops`, `minion_jobs` (an in-Postgres job queue), `oauth_clients`/`oauth_tokens`/`access_tokens`, `eval_contradictions_runs`, `calibration_profiles`, `dream_verdicts`.

**Storage tiering** (`docs/storage-tiering.md`): `gbrain.yml` declares `db_tracked` dirs (people/, companies/, concepts/ — committed to git) vs `db_only` dirs (media/x/, meetings/transcripts/ — DB-persisted, auto-gitignored, restorable with `gbrain export --restore-only`). This is the "curated vs bulk" split the talk describes, made operational.

## 3. Retrieval

`docs/architecture/RETRIEVAL.md` (29 KB) is the canonical doc, and `src/core/search/hybrid.ts` is 161,896 bytes — the single biggest file in the repo after `cycle/synthesize.ts` (155 KB). The declared pipeline:

```
intent classify (deterministic, no LLM) → expansion (optional)
→ hybrid recall: vector (HNSW, per-page max-pool) | BM25 | title-phrase arm
  | relational typed-edge arm | source-aware SQL re-rank | RRF fusion
→ graph augment (walkDepth > 0) → 4-layer dedup → cross-encoder rerank
→ relational re-pin → alias hop → exact-lookup tier
→ evidence stamp → autocut → limit slice → token-budget enforcement
```

Details worth recording:

- **Zero-LLM auto-linking.** `extractEntityRefs` in `src/core/link-extraction.ts` runs three regex families on every `put_page` (markdown links, Obsidian `[[wikilinks]]`, source-qualified `[[src:dir/slug]]`), plus heuristic link-type inference for `attended`, `works_at`, `invested_in`, `founded`, `advises`. One batched SQL insert (`INSERT ... SELECT FROM jsonb_to_recordset(...) ON CONFLICT DO NOTHING`). Claim: "On a 17K-page brain, full graph extract completes in seconds."
- **Benchmark table (from RETRIEVAL.md), on a 240-page Opus-generated corpus:** ripgrep-BM25 ≈ 18 P@5 / 75 R@5; vector-only RAG ≈ 18 / 80; gbrain graph-disabled ≈ 18 / 85; **gbrain full stack 49.1 / 97.9**. Treat as self-reported and corpus-specific — the corpus is LLM-generated, which flatters graph methods.
- **Reranker**: Voyage `rerank-2.5` default for `balanced`/`tokenmax` modes; measured "60% of top-1 results reshuffled" on 20 queries (on `zerank-2`); +150ms p50, fail-open when no key.
- **Negative result, honestly published**: multi-query expansion *hurt* recall. On LongMemEval-S (470 scored questions, k=5, run 2026-09-02) plain hybrid scored 93.19% strict `recall_all@5` vs 54.89% with equal-weight expansion. The fix (budget-normalized weighted RRF, `search.expansion_variant_budget`) failed its own pre-registered acceptance rule at every budget, so it ships default-`null` as an operator lever. That kind of published failure is a strong credibility signal.
- **`gbrain-evals` headline numbers (2026-09-06 run):** every labeled conversation found for **449/470 (95.53%)** answerable LongMemEval questions within 5 chunks; answer accuracy **433/500 (86.6%)**. Concept questions: exact target first on **130/181** vs **118/181** vector-only. Relationship retrieval switch: first-place hits **9/39 → 21/39** on investor questions.
- **Provenance surfaces in results**: every hit carries `evidence` (`alias_hit | exact_title_match | high_vector_match | keyword_exact | weak_semantic`) and `create_safety` (`exists | probable | unknown`), plus `unverified: true` for pages in the auto-extraction quarantine lane (frontmatter `provenance: auto-extracted` + `status: unverified`).
- **Confidence gate**: `src/core/search/crag.ts` grades every `query` as `strong|moderate|weak` with zero LLM calls; `search.crag_escalation` re-runs weak retrievals at a higher ceiling.

## 4. Hot vs cold memory, provenance, contradictions

`docs/takes-vs-facts.md` is the clearest statement of the talk's "hot memory vs cold reference" claim:

- **Facts (hot):** extracted per conversational turn by a Haiku-class model, single-user (owner only), kinds `event | preference | commitment | belief | fact | idea`, `visibility private|world`, `notability high|medium|low`, `confidence REAL CHECK (confidence BETWEEN 0 AND 1)`, `source TEXT NOT NULL` (provenance is a **required** field — the `remember` verb errors `provenance_required` on empty), `source_session`, `valid_from`/`valid_until`/`expired_at`/`superseded_by`.
- **Decay:** `src/core/facts/decay.ts` applies `confidence × exp(-age_days / halflife_days)` with per-kind half-lives: `event 7d, commitment 90d, preference 90d, belief 365d, fact 365d, idea 365d`. "Lunch on Tuesday is meaningless after Tuesday."
- **Takes (cold):** epistemic layer — *who believes what*. DDL at `src/core/migrate.ts:1271`: `claim`, `kind CHECK (kind IN ('fact','take','bet','hunch'))`, `holder` (`self`, `brain`, `world`, `people/<slug>`), `weight REAL CHECK (weight BETWEEN 0 AND 1)`, `since_date`/`until_date`, `superseded_by`, `active`, and a resolution block (`resolved_at`, `resolved_outcome`, `resolved_value`, `resolved_source`, `resolved_by`) that lets a `bet` be scored later — the substrate for the calibration/Brier-score features. Production extraction on a ~100K-page brain (2026-05-10): 100,720 takes from 28,256 pages, $361.49, 0.3% errors, 6,239 unique holders, cross-modal eval 6.8/10.
- **The bridge is one-way:** `hot facts → [dream consolidate] → cold takes`; facts are never deleted, only marked `consolidated_at`/`consolidated_into` as an audit trail. `forget()` expires with an audit trail rather than deleting.
- **Contradictions** (`docs/contradictions.md`): `gbrain eval suspected-contradictions` samples retrieval pairs, date-pre-filters (>30d apart skipped), caches on `(chunk_a_hash, chunk_b_hash, model, prompt_version, truncation_policy)`, then an LLM judge (default `claude-haiku-4-5`, ~$0.0006/call, ~$0.50/100 queries) emits one of six verdicts: `no_contradiction | contradiction | temporal_supersession | temporal_regression | temporal_evolution | negation_artifact`. Severity rubric low/medium/high; headline rate reported with a **Wilson 95% CI**, with `small_sample_note` when n<30. Critically: **the probe never mutates the brain** — it emits paste-ready `resolution_command`s and only the `consolidate` phase writes `valid_until` (pinned by a grep guard). This is exactly the "who arbitrates when two facts disagree" question from the talk, answered as *a human, with machine-generated evidence*.

## 5. The librarian: the dream cycle

`ALL_PHASES` in `src/core/cycle.ts` is 25 ordered phases: `lint, backlinks, sync, synthesize, extract, extract_facts, extract_atoms, resolve_symbol_edges, patterns, synthesize_concepts, recompute_emotional_weight, consolidate, propose_takes, grade_takes, calibration_profile, drift, conversation_facts_backfill, enrich_thin, skillopt, embed, orphans, schema-suggest, purge` (plus scope-split subsets `SOURCE_FRESHNESS_PHASES` / `MAINTENANCE_PHASES` for per-source fan-out). Ordering rationale is documented inline for nearly every phase.

Hygiene surfaces: 20 `doctor` checks (`src/commands/doctor/checks/`) including `undeclared_db_only_pages`, `links_extraction_lag`, `hidden_by_search_policy`, `reranker_health`, `stale-mentions`, `memory-writeback`. `gbrain lsd` — **"Lateral Synaptic Drift"** — is a stale-biased divergent-thinking pass: `k_close: 2, m_far: 12, ideas_per_cross: 4, temperature: 0.95, stale_bias: true`, generator voice *"Your brain at 3am noticing a connection between things it has no business connecting"*, with a hard cost ceiling (default $5) and a 10-second TTY abort window.

## 6. Harness integration and skills

- **MCP everywhere.** `gbrain serve` (stdio) / `gbrain serve --http` (OAuth 2.1 + PKCE + `/admin` dashboard). Documented clients: Claude Code, Codex, Cursor/Windsurf, Hermes, Grok Build, opencode, OpenClaw, Claude Desktop/Cowork, Perplexity Computer, ChatGPT.
- **Three surfaces:** `verbs` (exactly 7), `starter` (~27 ops), `full` (122). Fail-closed filtering; on OAuth HTTP the server surface is a *ceiling* and per-client rows can narrow it.
- **MEMORY_VERBS v1** (`docs/protocol/MEMORY_VERBS_v1.md`) is a frozen wire protocol — `recall, remember, entity, synthesize, forget, context_pack, delta` — with `protocol_version: 1`, additive-forever fields, enumerated error codes, and a third-party conformance harness (`gbrain protocol conformance --target <endpoint>`). `entity()` promises **zero LLM, p99 < 100ms**, CI-gated on a 20K-page corpus. This is the most reusable artifact in the repo for anyone building a competing brain.
- **Claude Code plugin** (`.claude-plugin/plugin.json` v0.48.5.0): `/plugin marketplace add garrytan/gbrain` + `/plugin install gbrain@gbrain`, launching `gbrain serve --surface starter --source-guard`. Per-turn context hooks load brain context into every prompt and push work back to the private repo on a ~5-min debounce.
- **Skills are markdown with a routing table.** `skills/RESOLVER.md` is the dispatcher (the talk's "resolver table = org chart"); `skills/_brain-filing-rules.md` is the filing policy (the talk's "filing rules = internal process"); each `SKILL.md` carries frontmatter `triggers:` (authoritative routing) and — notably — an `eval_contract:` block with `goal`, `dimensions`, and `hard_fails`. `skills/skillify/SKILL.md` v2.0.0 is the meta-skill implementing the talk's "never do one-off work", with a stated **"NO-REGRESSION LAW: any edit to a skill must score >= the previous iteration's eval"**, judged by three frontier models from different providers before tests are written.

## Relevance to company-brain / RAG / fruit-fly question

**(a) Is it RAG?** GBrain contains RAG and is not reducible to it. The retrieval core (chunk → embed → HNSW + BM25 → RRF → rerank) is textbook 2024-era hybrid RAG. What is *not* RAG, and is where the code volume actually sits: a write-time typed-edge graph built with regexes and no LLM calls; a two-tier hot/cold memory with temporal validity, supersession and exponential per-kind decay; mandatory provenance on every remembered fact; an evidence/`create_safety` contract so an agent can decide whether to write rather than only what to read; a nightly 25-phase curation daemon; a contradiction probe with calibrated statistics that refuses to auto-resolve; and a frozen memory wire protocol. Tan's "retrieval is the primitive, being worth retrieving from is the product" is a fair description of where this repo spends its lines.

**(b) Fruit-fly hooks.** GBrain is biologically *named* rather than biologically *derived* — but the naming maps onto real fly-memory constructs unusually well, which makes it a genuinely plausible integration target: the `dream` cycle's `consolidate` phase is systems consolidation (hot → cold); `facts.decay` is forgetting with kind-specific time constants (dopaminergic forgetting in the mushroom body has exactly this shape); `pages.emotional_weight` + `salience.ts` is valence-gated memory strength; `lsd` ("Lateral Synaptic Drift") is stochastic recombination of weakly-linked memories. The concrete engineering seam for a fly-inspired index is `docs/designs/VECTOR_BACKENDS.md` (status: **proposal**), which introduces `vector.backend = pgvector | pgvectorscale | vchord | auto` — a pluggable ANN backend abstraction. A FlyHash / sparse-expansion LSH index (the mushroom-body algorithm: random sparse projection to a much higher dimension, then winner-take-all) would slot in behind that config key as a fourth backend, and it directly addresses the two problems that design doc names: the HNSW 2000/4000-dim cap and RAM-bound scaling. Note also that GBrain's per-page max-pool and metadata-boost-gate exist precisely because dense-only similarity mis-ranks — the same failure sparse coding is designed to avoid.

**(c) Skepticism.** Three self-reported numbers do not reconcile: `docs/ethos/ORIGIN.md` says 17,888 pages / 4,383 people / 723 companies / 21 crons; the current README says 155,795 pages / 24,589 people / 5,340 companies / 66 crons; the talk (published 2026-07-16) says "about 220,000 pages". These are all Garry's private brain, unauditable, and probably count different things (DB pages vs on-disk markdown vs including `db_only` bulk). The BrainBench corpus is Opus-generated fiction, which is a weak proxy for a messy real brain — but the LongMemEval runs and the published expansion failure are much stronger evidence than the marketing table.

## Open questions

1. Which specific commit/version the +31.4 P@5 graph number was measured at, and whether it reproduces on a non-LLM-generated corpus.
2. Why the two epistemic tables live in `src/core/migrate.ts` rather than `src/schema.sql` (`takes` DDL at line 1271, `facts` at 2384) — a fresh install therefore depends on the migration runner, not the base schema file.
3. How many of the 129 contributors are substantive vs single-PR — and how much of the code is agent-written (the CHANGELOG alone is 2.5 MB).
4. Whether the `vector.backend` proposal has shipped since the design doc was written (status still reads "proposal" at v0.48.5.0).
5. Whether `gbrain protocol conformance` has actually been run against any third-party memory server (mem0, Zep, Letta) — the protocol invites it but I found no published results.

## Sources

- https://github.com/garrytan/gbrain — repo, README (76,781 bytes), metadata via `gh api repos/garrytan/gbrain`
- https://raw.githubusercontent.com/garrytan/gbrain/master/README.md
- https://github.com/garrytan/gbrain/blob/master/src/schema.sql — 1,618-line Postgres+pgvector schema
- https://github.com/garrytan/gbrain/blob/master/src/core/migrate.ts — 146 migrations; `facts` DDL at line 2384
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/RETRIEVAL.md
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/system-of-record.md
- https://github.com/garrytan/gbrain/blob/master/docs/protocol/MEMORY_VERBS_v1.md
- https://github.com/garrytan/gbrain/blob/master/docs/protocol/MCP_META_CHANNELS.md
- https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md
- https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md
- https://github.com/garrytan/gbrain/blob/master/docs/storage-tiering.md
- https://github.com/garrytan/gbrain/blob/master/docs/guides/compiled-truth.md
- https://github.com/garrytan/gbrain/blob/master/docs/guides/brain-vs-memory.md
- https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md
- https://github.com/garrytan/gbrain/blob/master/docs/designs/VECTOR_BACKENDS.md
- https://github.com/garrytan/gbrain/blob/master/docs/TOOL_CATALOG.md
- https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle.ts — `ALL_PHASES`
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/decay.ts — `HALFLIFE_DAYS`
- https://github.com/garrytan/gbrain/blob/master/src/core/brainstorm/orchestrator.ts — `LSD_PROFILE`
- https://github.com/garrytan/gbrain/blob/master/src/core/link-extraction.ts — `extractEntityRefs`
- https://github.com/garrytan/gbrain/blob/master/skills/RESOLVER.md, `skills/_brain-filing-rules.md`, `skills/skillify/SKILL.md`
- https://github.com/garrytan/gbrain-evals — README and metadata
- https://modelence.com/yc-rfs-summer-2026/company-brain — YC "Company Brain" RFS (Summer 2026); note the live https://www.ycombinator.com/rfs page now shows the Fall 2026 list, which does not include it
- /Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt — talk transcript, lines 347-372 and 455-500

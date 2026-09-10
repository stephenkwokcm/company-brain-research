# v06a — Is the "librarian" implemented in GBrain? (lens: code-reader)

**Key:** `v06a-librarian-in-code`
**Adjudicates:** contradiction **C2** in `findings/completeness-critic.md` — three incompatible positions across `talk-analysis.md` ("no librarian path exists in the repo"), `gbrain-architecture.md` ("the librarian is concrete: a 25-phase nightly dream cycle…"), `skeptic-claims.md` ("the librarian remains a human job the tool delegates back to you").
**Method:** full local clone of `garrytan/gbrain`, read at **commit `43597b19e50a3abf56409337f248f7966860293c`** (`VERSION` = `0.48.5.0`). Confirmed identical to remote `master` via `gh api repos/garrytan/gbrain/commits/master --jq .sha` and spot-fetched from `raw.githubusercontent.com` at that SHA. Every claim below is quoted from source at that commit.

---

## Verdict

**PARTIALLY — and the split falls on a clean, principled line the codebase draws itself.**

GBrain automates pruning **only where the decision is mechanical** (slug normalisation, TTL expiry of already-deleted rows, deterministic junk regexes, recency-ordering inside a semantic cluster, a numeric salience recompute, an ingest triage threshold). Every decision that requires **semantic judgment about whether a piece of knowledge is still worth keeping** — contradictions, drift, orphans, stale takes, thin pages, bad skill files — is emitted as a report or a paste-ready command that a human must run.

The codebase says this in its own words. `src/core/brain-score-recommendations.ts:410` classifies the orphan-pages check as `human_only` with the inline comment:

```ts
    // --- human_only paths ---
    case 'orphan_pages':        // archive is product judgment, not maintenance
```

…and the `default:` branch of the same switch classifies **every unmapped doctor check** as `human_only` — "conservative — anything the recommendation generator doesn't know about is treated as needing operator judgment, not autonomous remediation."

So: `talk-analysis.md` is **wrong on the literal** (there is a great deal of librarian machinery, and there is even a named `brain-librarian` skill referenced in the repo — see §5). `gbrain-architecture.md` is **wrong on the count and on the direction** (23 phases, not 25; and `gbrain lsd` is a *generative* command, not a pruning one). `skeptic-claims.md` is **closest to right**, but understates it: the tool does not merely delegate, it builds a substantial evidence-production apparatus and then stops one step short of acting on it, deliberately and by documented policy.

---

## 1. `ALL_PHASES` — the correction first

`src/core/cycle.ts:108` defines **23** phases, not 25. Enumerated verbatim:

```
lint, backlinks, sync, synthesize, extract, extract_facts, extract_atoms,
resolve_symbol_edges, patterns, synthesize_concepts, recompute_emotional_weight,
consolidate, propose_takes, grade_takes, calibration_profile, drift,
conversation_facts_backfill, enrich_thin, skillopt, embed, orphans,
schema-suggest, purge
```

(`gbrain-architecture.md` says "25 ordered phases" and then lists 23 names — an internal inconsistency in that report; the source count is 23.)

`src/core/cycle/phase-scope.ts` splits them into `source` (11) / `mixed` (2) / `global` (10), and defines the freshness-only subset a per-source cycle runs:

```ts
/** Bounded deterministic phases that alone define source freshness. */
export const SOURCE_FRESHNESS_PHASES: CyclePhase[] = [
  'lint', 'backlinks', 'sync', 'extract', 'extract_facts',
  'recompute_emotional_weight',
];
```

**Default-install reality:** 4 phases are default-OFF behind config gates (`drift`, `conversation_facts_backfill`, `enrich_thin`, `skillopt`) and 2 more are pack-gated off unless the active lens pack is `gbrain-creator` / `gbrain-everything` (`extract_atoms`, `synthesize_concepts`). A stock brain runs **17 of 23**. Notably, **three of the four opt-out phases are the ones with the strongest curation claims** (drift, skillopt, enrich_thin).

---

## 2. Phase-by-phase: what it deletes / merges / demotes, and whether it acts

| # | Phase | Deletes | Merges | Demotes | Acts or advises |
|---|---|---|---|---|---|
| 1 | `lint` | LLM-preamble boilerplate lines; malformed code fences; frontmatter repairs | — | — | **Acts** (cycle calls `runLintCore({ fix: true })`, `cycle.ts:1056`). But the three content-quality rules are `fixable: false`: `scraper-junk`, `huge-page`, `markup-heavy` — plus `empty-section`, `broken-citation`, `placeholder-date`. **Advisory for everything that is about content quality.** |
| 2 | `backlinks` | — | — | — | **Advises only.** Runs `action: 'check'`; header comment: *"Maintenance cycles must not rewrite tracked brain pages with generated 'Referenced in' timeline bullets… the legacy filesystem fixer remains available explicitly via `gbrain check-backlinks fix`."* Summary literally says `(audit-only; run gbrain check-backlinks fix to materialize)`. |
| 3 | `sync` | DB rows whose backing file is gone | — | — | **Acts**, but it mirrors a human's `git rm`. Guarded by the `#2828` mass-delete valve (`src/core/sync-reconcile.ts`): a reconcile that would sweep >`MASS_RECONCILE_RATIO` (0.5) of file-backed pages on a source holding >`MASS_RECONCILE_MIN_PAGES` (20) is "treated as a suspected path-comparison bug rather than a real bulk deletion." |
| 4 | `synthesize` | Nothing — *"Nothing is ever fabricated and no content is deleted"* (quote-verify pass) | — | **Yes: refuses to write down low-salience input** | **Acts — this is the one real automated prune, and it happens at ingest, not on the store.** A cheap judge scores every transcript 0–1; `DEFAULT_TRIAGE_THRESHOLD = 0.5` (`src/core/cycle/synthesize.ts:129`); below-threshold files are never synthesised. A verified-segment rescue band (`rescue_floor` 0.30, ≥2 quoted segments verified as substrings, allow-listed content types) readmits borderline files. The gate is applied **at read time**, so retuning re-gates with zero new LLM calls. |
| 5 | `extract` | — | — | — | Additive (links, timeline). |
| 6 | `extract_facts` | — (itself) | — | — | Reconciles the `## Facts` fence against the DB. **Hosts the phantom-redirect pre-pass — see row 6a.** |
| 6a | ↳ **phantom-redirect** (pre-pass inside `extract_facts`) | **Soft-deletes the phantom page + unlinks the `.md`** | **Yes — migrates fact rows and disk fence into the canonical page** | — | **Acts, automatically.** *"Walks unprefixed-slug pages in the source (e.g. `alice.md` at brain root), tries to resolve each to a canonical prefixed slug (`people/alice-example`), migrates fact rows + disk fence, soft-deletes the phantom, unlinks the `.md`. Bounded at 50 phantoms per cycle."* **This is the only automatic page deletion anywhere in the dream cycle** — and it is filename normalisation, not a judgment about worth. |
| 7 | `extract_atoms` | — | — | — | Additive. Pack-gated OFF by default. |
| 8 | `resolve_symbol_edges` | — | — | — | Additive edge metadata. |
| 9 | `patterns` | — | — | — | Additive: writes `wiki/personal/patterns/<theme>` when ≥`dream.patterns.min_evidence` (3) reflections support a theme. Default ON. |
| 10 | `synthesize_concepts` | — | **No** | — | Additive: groups atoms by `concepts:` frontmatter, tiers T1≥10 / T2≥5 / T3≥2 / T4≥1, writes concept pages. Header still reads *"dedup-by-embedding-similarity ship in v0.42+"* — **still unimplemented at v0.48.5.0** (zero `dedup`/`similar` hits in the file body). Pack-gated OFF. |
| 11 | `recompute_emotional_weight` | — | — | **Yes — recomputes `pages.emotional_weight` (0..1)** | **Acts.** *"Pure deterministic computation; no LLM calls."* Re-ranks; removes nothing. |
| 12 | `consolidate` | **Never** — *"NEVER DELETE — facts stay as audit trail"* | **Yes** — greedy cosine clustering at threshold 0.85, min 3 facts/bucket, oldest ≥24h; one take written per cluster ≥2 | **Yes** — marks contributing facts `consolidated_at`/`consolidated_into`, **and stamps chronological `valid_until` on every fact except the newest in each cluster** | **Acts, automatically. The strongest genuine curation act in the codebase.** `src/core/cycle/phases/consolidate.ts:245-274`: *"Sort the cluster by (valid_from ASC, id ASC); walk consecutive pairs; stamp the older fact's `valid_until` = next_newer.valid_from. The newest fact keeps `valid_until = NULL`. This makes the facts table a proper bitemporal record **without the contradiction probe having to mutate it**."* Note what arbitrates: **recency inside a semantic cluster**, not a judge. |
| 13 | `propose_takes` | — | — | — | **Advises only, by explicit design.** *"propose_takes only WRITES proposals to the queue. Nothing here mutates the canonical takes table. Operator opt-in via `gbrain takes propose --accept N` is the only path from queue to canonical fence (D17)."* And from `cycle.ts:2652`: *"auto-accept is intentionally NOT a thing — user always reviews."* Default ON. |
| 14 | `grade_takes` | — | — | Resolves takes **only if the operator opted in** | **Advises by default.** *"On a fresh install, grade_takes runs and writes verdicts to the cache, but `applied=false` on every row."* Code: `const autoResolve = opts.autoResolve ?? false; // D17 default OFF`. When enabled, `autoResolveThreshold ?? 0.95`, and *"tightening thresholds is always free, loosening requires `--allow-loosen-confidence`."* |
| 15 | `calibration_profile` | — | — | — | Additive: 2–4 narrative pattern statements + bias tags. |
| 16 | `drift` | — | — | — | **Advises only, twice over.** Default OFF (`dream.drift.enabled`). Header: *"Output is REPORT-ONLY (v1 conservative posture)… `dream.drift.auto_update` mutates **NOTHING** in v1."* Report text at `drift.ts:251`: *"**Report-only:** no takes were modified… review and adjust weights manually."* So even the operator who deliberately flips the auto-update flag gets nothing. |
| 17 | `conversation_facts_backfill` | — | — | — | Additive. Default OFF. |
| 18 | `enrich_thin` | — | — | — | Additive: develops ≤3 stub pages per source per tick. Stated payoff: *"the brain gets smarter over time, not just bigger."* Default OFF. |
| 19 | `skillopt` | — | Rewrites `SKILL.md` in place for **user** skills | — | **Split.** Bundled skills: *"never auto-mutate — `proposed.md` is written to `~/.gbrain/skillopt-proposed-bundled/<skill>.md` for review"* (D16). Caps $0.50/skill, $2.00/brain, only skills stale >7d, `epochs=1`. Default OFF. |
| 20 | `embed` | — | — | — | Additive. |
| 21 | `orphans` | **Nothing** | — | — | **Advises only.** Counts orphans; status is `warn` only when `count / total_pages > 0.5` — the comment explains the ratio replaced a `count > 20` cutoff because *"on any corpus past a few hundred pages it fires 'warn' every cycle in steady state."* |
| 22 | `schema-suggest` | — | — | — | **Advises only.** *"Writes nothing to the user's brain."* Candidates go to `~/.gbrain/audit/schema-candidates-YYYY-Www.jsonl`, reviewed via `gbrain schema review-candidates`. |
| 23 | `purge` | **Hard-deletes** soft-deleted pages past 72h, expired archived sources, orphan clone temp dirs, `op_checkpoints` (7d), brainstorm checkpoints (7d), batch-retry audit files (30d), volunteer events (90d) | — | — | **Acts — but it is a garbage collector, not a librarian.** It only executes decisions taken elsewhere; it never chooses *what* is worth deleting. `SOFT_DELETE_TTL_HOURS_FOR_PURGE = 72`. Runs last *"so the rest of the cycle sees the recoverable set; the purge then drops what's expired."* |

### Tally

- **Phases that delete anything:** 3 (`sync` mirrors git; `extract_facts`/phantom-redirect normalises slugs; `purge` GCs the already-condemned). **Zero delete on the basis of a quality judgment.**
- **Phases that merge:** 2 (`consolidate` semantically; phantom-redirect by slug).
- **Phases that demote:** 3 (`consolidate` via `valid_until`; `recompute_emotional_weight` via salience; `synthesize` by declining to write below-threshold input).
- **Phases that produce only reports/queues/suggestions:** 6 (`backlinks`, `propose_takes`, `grade_takes` (default), `drift`, `orphans`, `schema-suggest`) — plus the non-fixable half of `lint`.

---

## 3. `doctor` — 117 check names, and a policy of not acting

`gbrain-architecture.md` says "20 `doctor` checks"; that is the file count in `src/commands/doctor/checks/`. The actual number of distinct check **names** across `src/commands/doctor.ts` + `src/commands/doctor/checks/*.ts` + `src/commands/doctor/*.ts` is **117** (`grep -ohE "name: '[a-z_0-9]+'" … | sort -u | wc -l`). Curation-relevant ones include `quarantined_pages`, `flagged_pages`, `junk_entity_hubs`, `scraper_junk_pages`, `oversized_pages`, `orphan_ratio`, `stale_mentions`, `contradictions`, `raw_provenance`, `stub_guard_24h`, `content_sanity_audit_recent`, `salience_health`, `effective_date_health`, `takes_weight_grid`, `grade_confidence_drift`.

**All of them report.** Two escape hatches exist and neither prunes:

1. **`gbrain doctor --fix`** calls exactly one thing: `autoFixDryViolations(skillsDir)` from `src/core/dry-fix.ts` — it edits `SKILL.md` files. It is refused outright when the skills dir came from the install-path fallback. It does not touch brain content.
2. **`gbrain doctor --remediate --yes --target-score N --max-usd M`** walks a dependency-ordered plan of Minion jobs. The plan can contain exactly **four** step ids (`src/core/brain-score-recommendations.ts`): `sync.repo`, `embed.stale`, `backlinks.fix`, `extract.all`. Every one is an index rebuild. **There is no delete, prune, merge, archive, or demote step in the autonomous remediation vocabulary at all.**

And `classifyChecks()` hard-codes the boundary quoted at the top of this report: `orphan_pages`, `multi_source_drift`, `eval_drift`, `slug_fallback_audit`, `whoknows_health`, `rls_event_trigger`, `reranker_health` → `human_only`, `'no autonomous remediation'`; unmapped → `human_only`, `'unmapped check'`.

---

## 4. Quarantine, forget, TTL, contradictions, `lsd`

**Quarantine lane #1 — content-sanity, at ingest (`src/core/quarantine.ts`, `src/core/content-sanity.ts`).** Fully automatic, deliberately narrow, three graded markers that never overlap:

- `quarantine` — **HIDES**. Set *"ONLY for high-confidence junk (Cloudflare / CAPTCHA interstitial patterns + operator literals)"*. Page still lands and is readable; `QUARANTINE_FILTER_FRAGMENT` excludes it from search; zero chunks written. Reversible: `gbrain quarantine clear <slug>`.
- `content_flag` — **WARNS, does not hide**. Markup ratio > 0.85 or oversize. *"There is NO SQL filter fragment for content_flag, by design… a false positive costs a one-line note, not a vanished page."*
- `embed_skip` — oversize-but-clean (`DEFAULT_BYTES_BLOCK = 500_000`); page lands, embedder skips.

Scraper-junk is a **hard block at the narrow waist** (`ContentSanityBlockError`) — the one place GBrain will refuse to write something down at all. Six hand-vetted regexes over `title` + first 2 KB, plus operator literal substrings. Kill-switch: `GBRAIN_NO_SANITY=1`.

**Quarantine lane #2 — extraction (`src/core/extraction-review.ts`, issue #160).** Auto-extracted `people/`/`companies/` stubs from any untrusted channel get `provenance: auto-extracted` + `status: unverified`. Consequences: excluded from the compiled-truth authority boost; results carry `unverified: true`; `extraction_pending` lists them. Promotion (→ `verified`) or rejection (→ soft-delete) is `extraction_review`, **local-owner-only**. Fail-closed: *"only an explicit `trusted: true` writes direct; undefined/false/anything-else quarantines."*

**TTL / forgetting is a read-time score, not a write-time deletion.** `src/core/facts/decay.ts`: `effectiveConfidence(fact, now)` = `confidence × exp(-age_days / halflife_days)`, half-lives `event 7 / commitment 90 / preference 90 / belief 365 / fact 365 / idea 365`. The file states it outright: **"Pure function. No side effects. No I/O."** Nothing in the cycle expires a fact on the strength of decay. A decayed fact ranks lower forever and is never removed.

**`forget` is a human/agent verb, never a daemon.** `src/core/facts/forget.ts` rewrites the markdown fence — strikes the claim `~~like this~~`, sets `valid_until` = today, appends `forgotten: <reason>` to the context cell — so the forget survives `gbrain rebuild`. Grepping every non-test call site of `forgetFact`/`expireFact` finds no cycle phase among them. Likewise `softDeletePage` has exactly six non-test callers: phantom-redirect (the cycle), two schema-pack migration ops, `ops/pages.ts` (the `delete_page` op), `ops/extraction.ts` (a human rejecting a stub), and an ingest-capture rollback.

**Contradiction arbitration is advisory in the strongest possible terms.** `docs/contradictions.md`: *"Probe never mutates the brain. Runs only read pages/takes/chunks. Writes go only to `eval_contradictions_runs` and `eval_contradictions_cache`."* And `src/core/eval-contradictions/auto-supersession.ts` — the module whose *name* promises automation — opens with:

> *"The probe **NEVER auto-applies**; the user runs the command themselves. The proposal is descriptive, not directive."*

Its output is a `resolution_command` string: `gbrain takes supersede <slug> --row N --claim '<replacement>'`, `gbrain dream --phase synthesize --slug <slug>`, or `# manual review: …`. Where it cannot name a winner it says so: *"the classifier picks an action, not a winner, and will not fabricate a take from arbitrary chunk prose."*

**`gbrain lsd` is not pruning — it is the opposite.** `LSD_PROFILE` (`src/core/brainstorm/orchestrator.ts:117`): `k_close: 2, m_far: 12, ideas_per_cross: 4, temperature: 0.95, stale_bias: true, default_save: false`, generator voice *"Your brain at 3am noticing a connection between things it has no business connecting."* It **generates** ideas by bisociation over stale pages and is **ephemeral by default**. Counting it as librarian machinery (as `gbrain-architecture.md` does) inverts its function: it adds material to the pile. Its only pruning-adjacent property is that `mode: lsd` frontmatter makes the dream cycle's synthesize phase *skip* its output.

---

## 5. There *is* a `brain-librarian` — and it is not in the public repo

`talk-analysis.md`'s claim that "no `librarian` path exists in the repo" is literally false. The string appears in four places:

- `skills/functional-area-resolver/SKILL.md:58` — *"Brain integrity -> `brain-librarian`"* (also in the two plugin variants and in `evals/functional-area-resolver/variants/baseline.md:113`).
- `src/core/skill-brain-first.ts:196` — `brain-librarian` sits in `FORMERLY_HARDCODED_EXEMPT`, the list of *"Brain-internal skills (PR rationale: 'ARE the brain')"*.
- `templates/bootstrap/questions.json:177` — the default answer to the agent-identity question is `"a librarian who never sleeps"`, which lands verbatim in `templates/bootstrap/template-repo/SOUL.md:9`.

But `find … -type d -name brain-librarian` returns **nothing**: the routing table dispatches to a skill that exists only in Garry's private brain repo. The nearest bundled substitute is `skills/maintain/SKILL.md` (`mutating: true`, triggers `"brain health"`, `"orphan pages"`, `"stale pages"`, `"run dream"`) — and it is an **agent skill a human invokes**, not a daemon. Its own orphan-handling instruction is the whole thesis in one line:

> *"Review orphans: are they genuinely isolated or just missing links? Add links in gbrain from related pages **or flag for deletion**."*

Flag. Not delete. So the librarian in GBrain is exactly what Tan said it was at 14:58 — *"human plus agent"* — and the repo ships the agent half as a skill file plus an evidence pipeline, and leaves the human half to the human.

---

## 6. Adjudication

**Pruning in GBrain is advisory-with-mechanical-exceptions, and delegated to the human wherever content would actually leave the brain.**

The three positions in the corpus resolve like this:

| Claim | Verdict |
|---|---|
| `talk-analysis.md`: *"No `librarian` path exists in the repo — the one talk term with no code artifact"* | **REFUTED.** `brain-librarian` is named in the resolver, the exemption list, and the bootstrap identity default; `skills/maintain/` is the bundled stand-in; the dream cycle, doctor, and quarantine lanes are extensive librarian machinery. |
| `gbrain-architecture.md`: *"The librarian is concrete: a 25-phase nightly dream cycle, 20 doctor checks, a quarantine lane, `gbrain lsd`"* | **PARTIALLY — and wrong in the details.** 23 phases, not 25. 117 doctor check names, not 20. `gbrain lsd` is generative, not curatorial. And "concrete" overclaims: of the 23 phases, 6 produce nothing but reports and queues, 4 more are default-OFF, and none deletes on quality grounds. |
| `skeptic-claims.md`: *"the librarian remains a human job the tool delegates back to you"* | **CONFIRMED, with one qualification.** True for every semantic decision. But GBrain does automate the *mechanical* half — ingest triage below 0.5, junk-pattern quarantine, cosine-cluster consolidation with bitemporal `valid_until`, salience recompute, slug-normalising merge, 72h GC — which is more write-side agency than any competitor ships (cf. `memory-systems-landscape.md`). The honest framing is not "delegates" but **"builds the evidence, then hands you the trigger."** |

**Why this line is defensible rather than a cop-out.** The pattern is consistent enough to be a doctrine, and the code states it repeatedly: `auto_resolve` OFF by default at ≥0.95 confidence when on, with loosening gated behind `--allow-loosen-confidence`; auto-accept of take proposals "intentionally NOT a thing"; drift report-only even when the operator flips the flag; bundled skills never auto-mutated; a 50%-mass-delete valve on sync; a 72h soft-delete recovery window; `content_flag` chosen over hiding because "a false positive costs a one-line note, not a vanished page." GBrain treats a false-positive deletion as strictly worse than a retained-but-demoted page — which is a *library-science* posture (deaccessioning requires curatorial sign-off), not an engineering shortcut.

**Where that leaves Tan's own thesis.** He claimed at 14:46 that the primitive is "memory plus hygiene, provenance on every fact, contradiction checks…, and a librarian, human plus agent, whose actual job is pruning." His repo ships provenance (mandatory, `provenance_required` error), ships contradiction checks (with Wilson CIs and a $0.0006/call judge), and ships the agent half of the librarian. **The one thing it does not ship is the pruning.** The single automated act that most resembles it — `consolidate`'s cluster-and-stamp — arbitrates by *recency inside a cosine cluster*, which is exactly the naive rule the `neuro-inspired-rag.md` and `memory-hygiene.md` reports flag as insufficient for knowledge-update questions. That is the honest state of the art, in his repo, at v0.48.5.0.

---

## 7. Precise sentence for the synthesis

> **GBrain ships the librarian's evidence pipeline but not the librarian's authority: at v0.48.5.0 the 23-phase nightly "dream cycle" contains exactly one automatic page deletion (a slug-normalising merge capped at 50 pages per run) and one automatic demotion (clustering facts at cosine 0.85 and stamping the older ones' `valid_until`), while every judgment Tan actually calls pruning — contradictions, drift, orphans, junk, stale takes, bad skill files — is emitted as a report or a paste-ready command a human must run, a boundary the code draws in its own comment when it classifies orphan pages as `human_only` because "archive is product judgment, not maintenance."**

Shorter variant if space is tight:

> **GBrain automates the mechanical half of pruning (ingest triage, junk quarantine, fact consolidation, 72-hour garbage collection) and refuses the semantic half by policy — its contradiction module is named `auto-supersession.ts` and opens with "The probe NEVER auto-applies; the user runs the command themselves" — so Tan's "librarian, human plus agent" is, in his own repo, an agent that produces evidence and a human who still pulls the trigger.**

---

## 8. Corrections other reports should absorb

1. **23 phases, not 25** (`gbrain-architecture.md` TL;DR#5 and §5).
2. **117 distinct doctor check names, not 20** — 20 is the file count in `doctor/checks/`.
3. **`gbrain lsd` is generative, not curatorial** — remove it from any list of librarian/pruning machinery.
4. **`brain-librarian` exists as a name** in the resolver + exemption list but has **no bundled skill directory** — correct `talk-analysis.md` §2 to "named in the routing table, unshipped in the public repo."
5. **`synthesize_concepts` dedup has still not shipped** — the header's "v0.42+" promise is unfulfilled at v0.48.5.0.
6. **Fact decay never deletes.** `effectiveConfidence` is a pure function; describing GBrain's half-lives as "forgetting" overstates them — they are a read-time ranking penalty.
7. **`doctor --remediate` has four steps, all index rebuilds.** Anyone citing it as autonomous brain maintenance should name the four.

## 9. Residual uncertainty

Confidence **high** on everything above: it is all read directly from source at a SHA verified against remote `master`, and the policy statements are load-bearing header comments and default values, not marketing text. Two caveats. (a) I read the phase *implementations* and their dispatch, not the ~2,191 test files — it is conceivable a phase mutates through a path I did not trace, though the six-caller audit of `softDeletePage` and the pure-function status of `decay.ts` make broad hidden deletion unlikely. (b) Garry's *private* brain repo runs `brain-librarian`, `brain-taxonomist`, `correction-pipeline`, `freshness-monitor` and ~66 crons that are not in the public repo; the claim "GBrain does not automate pruning" is a claim about **the public MIT repo at v0.48.5.0**, and cannot be extended to whatever he runs on his own 155K-page brain.

---

## Sources

All GBrain paths read from a local clone at commit `43597b19e50a3abf56409337f248f7966860293c`, confirmed equal to remote `master` (`gh api repos/garrytan/gbrain/commits/master --jq .sha`, 2026-09-10) and spot-verified over the network at that SHA.

- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle.ts — `ALL_PHASES` (line 108, 23 entries), `runPhaseLint` (1047), `runPhaseBacklinks` (1086), `runPhasePurge` (1717), `runPhaseOrphans` (1818), `onceForPhase` gate doc (543), calibration + drift dispatch (2630-2740)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/phase-scope.ts — `PHASE_SCOPE`, `SOURCE_FRESHNESS_PHASES`
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/phases/consolidate.ts — cluster threshold 0.85, "NEVER DELETE", chronological `valid_until` writeback (245-274)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/drift.ts — "REPORT-ONLY", `auto_update` mutates nothing (lines 12-17, 251-252, 362)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/propose-takes.ts — proposals-only posture, off-switch default-on (625-660)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/grade-takes.ts — `autoResolve ?? false // D17 default OFF`, threshold `?? 0.95` (512-513)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/synthesize.ts — `DEFAULT_TRIAGE_THRESHOLD = 0.5` (129), read-time gate (507)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/phantom-redirect.ts — merge + soft-delete + unlink, 50/cycle cap; `softDeletePage` call at line 457
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/synthesize-concepts.ts — tiers, "dedup … ship in v0.42+"
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/schema-suggest.ts — "Writes nothing to the user's brain"
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/enrich-thin.ts — default OFF, caps
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/conversation-facts-backfill.ts — default OFF, caps
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/cycle/recompute-emotional-weight.ts — deterministic, no LLM
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/skillopt/cycle-phase.ts — D16 bundled-skill safety, `proposed.md`, $0.50/$2.00 caps
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/skillopt/bundled-skill-gate.ts and `version-store.ts` — `proposed.md` review artifact
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/destructive-guard.ts — `SOFT_DELETE_TTL_HOURS = 72`, impact preview, confirmation gate
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/sync-reconcile.ts — `MASS_RECONCILE_RATIO = 0.5`, `MASS_RECONCILE_MIN_PAGES = 20`
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/quarantine.ts — `quarantine` HIDES vs `content_flag` WARNS; `QUARANTINE_FILTER_FRAGMENT`
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/content-sanity.ts — hard-block vs soft-block, `DEFAULT_BYTES_WARN` 50_000, `DEFAULT_BYTES_BLOCK` 500_000, `DEFAULT_MAX_MARKUP_RATIO` 0.85, `SCAN_HEAD_BYTES` 2048
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/extraction-review.ts — `provenance: auto-extracted` + `status: unverified`, owner-only promotion
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/facts/decay.ts — `HALFLIFE_DAYS`, "Pure function. No side effects. No I/O."
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/facts/forget.ts — forget-as-fence-rewrite
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/eval-contradictions/auto-supersession.ts — "The probe NEVER auto-applies"
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/brain-score-recommendations.ts — `classifyChecks`, `human_only`, "archive is product judgment, not maintenance" (line 410); the four remediation step ids
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/skill-brain-first.ts — `FORMERLY_HARDCODED_EXEMPT` incl. `brain-librarian` (line 196)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/brainstorm/orchestrator.ts — `LSD_PROFILE` (117), `default_save: false`
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/orphan-policy.ts — orphan exclusion policy
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/commands/doctor.ts — `--fix` → `autoFixDryViolations`; `quarantined_pages` (3181), `flagged_pages` (3192)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/commands/lint.ts — rule table; `scraper-junk` / `huge-page` / `markup-heavy` all `fixable: false`
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/docs/contradictions.md — "Probe never mutates the brain" (145); `resolution_command` menu (109-125)
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/skills/maintain/SKILL.md — "or flag for deletion"; "no content is deleted"; `doctor --remediate` usage
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/skills/RESOLVER.md and `skills/functional-area-resolver/SKILL.md` — `brain-librarian` routing target
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/templates/bootstrap/questions.json + `templates/bootstrap/template-repo/SOUL.md` — "a librarian who never sleeps"
- Transcript: `/Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt` — 12:54 ("the library plus the librarian"), 14:58-15:03 ("a librarian, human plus agent, whose actual job is pruning"), 17:41 ("the librarian that picks the three books")

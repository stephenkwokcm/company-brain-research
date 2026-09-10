# v06b — Skeptic: is GBrain's dream cycle actually Tan's "librarian … whose actual job is pruning"?

**Key:** `v06b-librarian-skeptic`
**Lens:** adversarial. Target claim, from `findings/gbrain-architecture.md`:
> "The 'librarian' is a 25-phase nightly cron ('dream cycle') plus a 20-check `doctor`, a contradiction probe with an LLM judge and Wilson confidence intervals, and `gbrain lsd`."

**Verdict: PARTIALLY REFUTED (high confidence on the mechanism; the disagreement is about what the word "librarian" was claimed to cover).**

**Method:** shallow clone of `garrytan/gbrain` at `43597b19e50a3abf56409337f248f7966860293c` (v0.48.5.0, 2026-09-07, the same commit the architecture report cites), read the phase list and every phase's write path; plus the full GitHub issue corpus (1,915 issues, 105 open) via the search API.

---

## 1. The one-sentence finding

GBrain's nightly cycle is an **accretion engine with a garbage collector for things a human already deleted**; on a default install not one of its 23 phases removes, expires, hides or down-ranks a piece of knowledge on its own judgment, and the contradiction probe is not a cycle phase at all — it is a user-initiated read-only report whose only automatic consumer is a top-5 advisory paragraph pasted into a synthesis prompt.

## 2. What Tan actually said — and the equivocation that makes this "partially"

The transcript uses "librarian" in **two different senses**, and the architecture report maps the dream cycle onto the wrong one.

- **Sense A — hygiene/pruning** (14:46–15:05): *"the primitive is not memory. It's memory plus hygiene, provenance on every fact, contradiction checks when new information collides with the old, **and a librarian, human plus agent, whose actual job is pruning**."*
- **Sense B — selection** (17:41: *"the librarian that picks the three books"*; 19:28: *"A library of the librarian, the right three books open at the right moment"*).

GBrain implements **Sense B** superbly (the 4-signal hybrid stack, autocut, token budget). It implements the *provenance* and *contradiction-check* halves of Sense A. It does **not** implement the pruning half — and pruning is the word Tan chose for the librarian's "actual job."

One genuine concession to the claim: Tan says **"human plus agent."** GBrain's design is deliberately human-plus-agent, so "the librarian is a human with machine-generated evidence" is a defensible reading of the talk. That is why this is PARTIALLY, not REFUTED. But the architecture report's framing — that a nightly *cron* is the librarian — is what the code does not support.

## 3. Test 1 — does anything delete or demote content automatically?

`ALL_PHASES` (`src/core/cycle.ts:108`) has **23** entries, not 25. Audited one by one for write direction:

| Phase | Default state | Effect on corpus |
|---|---|---|
| `lint`, `orphans`, `schema-suggest` | on | **report only** (`orphans` is annotated "DB read, report only", `cycle.ts:27`) |
| `backlinks`, `sync`, `extract`, `resolve_symbol_edges`, `embed` | on | additive (edges, chunks, vectors) |
| `synthesize`, `patterns`, `recompute_emotional_weight` | on | additive (new pages, new scores) |
| `extract_facts` | on | reconciles a page's fact rows **from the page's own fence** — it is a mirror, not a judge |
| `consolidate` | on | inserts `takes`; the inline comment is explicit: *"mark facts consolidated_at + consolidated_into. **Never DELETE** — facts stay as audit trail"* (`cycle.ts:152`) |
| `propose_takes` | on | writes to a human review queue; *"auto-accept is intentionally NOT a thing — user always reviews"* (`cycle.ts:132`) |
| `grade_takes` | on | emits verdicts; `autoResolve = opts.autoResolve ?? false; // D17 default OFF` (`cycle/grade-takes.ts:512`) |
| `calibration_profile` | on | writes a narrative profile page |
| `drift` | **OFF** | *"report-only in v1 (writes reports/drift-`<date>`; auto_update mutates nothing)"* (`cycle.ts:73`) |
| `extract_atoms`, `synthesize_concepts` | **inert by default** | pack-gated; the default pack `gbrain-base-v2.yaml:44` declares `phases: []` |
| `conversation_facts_backfill`, `enrich_thin`, `skillopt` | **OFF** | additive when enabled; `skillopt` "never auto-mutates bundled skills — emits proposed.md instead" |
| `purge` | on | **the only deleting phase** — and it hard-deletes *only* (a) pages a human/agent already soft-deleted >72h ago, (b) sources already marked `archived` past their expiry, (c) orphaned temp clone dirs and stale job checkpoints (`cycle.ts:1670-1690`). It is a recovery-window GC, not a curator. |

**Every soft-delete call site in the repo is human- or file-initiated**: `sync` mirroring a markdown file a human deleted from git, the explicit `delete_page` op, `extraction_review --reject`, and two schema-pack refactors. The one automatic in-cycle deletion is `cycle/phantom-redirect.ts` — and it is a *slug rename* (`alice.md` → `people/alice-example`) that migrates every fact row before soft-deleting the husk. Content is preserved; nothing is judged.

### Decay is a sort key, not a pruner
`src/core/facts/decay.ts` is a **pure function, 65 lines, "No side effects. No I/O."** Its two consumers (`facts/meta-hook.ts:137`, `commands/recall.ts:715`) use it to **sort and to print a number**. There is no confidence floor anywhere: a fact at effective confidence 0.001 still rides the ambient channel. Nothing in the codebase ever writes a decayed confidence back, and there is **no retention or TTL config key for knowledge content** — `grep` over `KNOWN_CONFIG_KEYS` returns only cache TTLs, an OAuth TTL, and `memory.auto_writeback_transient_ttl` (default `3d`, on a feature that is default OFF).

### Nothing is demoted; some things are boosted
`applySalienceBoost` multiplies by `1.0 + k·ln(1+score)`, floor 1.0 (`search/hybrid.ts:363`). Recency is a **positive component** that goes to 0 for old pages, never negative (`search/recency-decay.ts`). The single true demotion in the stack is `SESSION_DEMOTE` ×0.95 applied to the 2nd..nth chunk from one chat session (`search/graph-signals.ts:405`) — a diversity de-duplicator, not curation.

### The one signal that could drive pruning is wired to a generator instead
`pages.last_retrieved_at` — "never retrieved" — exists and is indexed. Its *only* consumer is `gbrain lsd`'s stale-bias query for picking pages to cross for idea generation (`schema.sql:270-276`). The brain records which pages nobody ever reads, and uses that list to **write more pages**.

## 4. Test 2 — are contradiction findings resolved, or only emitted?

**Only emitted, and less automatically than the architecture report implies.**

1. **It is not a cycle phase.** `suspected-contradictions` appears nowhere in `ALL_PHASES`. `docs/architecture/KEY_FILES.md:154` says the MCP op is *"read scope, NOT localOnly, NOT in subagent allowlist — **user-initiated only**."*
2. **The probe cannot write.** `docs/contradictions.md:145`: *"Probe never mutates the brain."* `src/core/eval-contradictions/auto-supersession.ts:5`: *"The probe **NEVER auto-applies**; the user runs the command themselves. The proposal is descriptive, not directive."*
3. **The README's "Wired into the daily dream cycle" (line 409) resolves to a prompt hint.** The entire automatic integration is `loadPriorContradictionsBlock` (`cycle/synthesize.ts:2524`): read the most recent probe run *that a human already launched*, take the **top 5 by severity**, paste them into the synthesize subagent's prompt, and close with *"Ignore findings irrelevant to what this transcript covers."* It returns `''` when no probe has run, and is `try/catch`-swallowed ("Best-effort and silent on failure"). That is an advisory footnote, not arbitration.
4. **The human queue does not clear.** `docs/proposals/temporal-contradiction-probe.md` (2026-05-14) opens: *"A large production run … surfaced **~115 HIGH findings. Walking through them by hand** exposed a structural limitation."* Three of the six verdict classes exist because the probe was crying wolf on facts that had merely changed.
5. Even the paste-ready commands were wrong: **#4169** — *"eval suspected-contradictions emits `gbrain takes supersede <slug> --row <take_id>` — `--row` is the per-page row_num, so **every generated resolution_command fails**."*

## 5. Test 3 — does forgetting even stick?

This is the sharpest evidence, because it is the repo's own bug tracker.

- **#4696 (verified bug, open 2026-08-29 → closed 2026-09-08 at the very commit the architecture report cites):** *"**forget_fact is undone by the next extract_facts reconcile** — the page body's fence is never struck."* The nightly cycle read the DB body, saw the fence still advertising the claim as live, called it drift, and **re-inserted the fact as active**. On the legacy tier "the resurrection is not windowed, it is certain." A commenter's summary: *"A system that can add a fact but never durably drop one isn't a memory, it's an accumulator."* This was the behavior for the entire window covering the 2026-07-16 talk.
- **Forgetting still does not remove text.** `forget` strikes the fence row through (`~~claim~~`) and leaves it in `pages.compiled_truth`; no chunker strips inactive fence rows. And per the reporter's own corrected finding in **#4622**: *"`forget` … does not touch **the prose that asserted the claim**, and chunking indexes prose. So the claim stays retrievable through the page even though the fact is expired."* Plus duplicate live rows for the same claim survive a forget of one of them. That is verbatim Tan's failure mode — *"Retrieval will surface a stale fact with total confidence"* (14:36).
- **The one at-scale automatic deletion in the repo's history was an accident that completed silently.** #4622 comment 2: a mis-split page made `extract_facts` parse zero fence rows and treat that as authoritative — *"The first full-walk cycle then **hard-deleted 324 facts across 41 pages**."* And: *"the `net_fact_deletion` warning did fire — it lands in the CycleReport, which our nightly report filtered out, **so a 324-fact deletion completed silently**."*

## 6. Test 4 — does the hygiene machinery fail silently? (the issue corpus)

Title-search over all 1,915 issues. `decay` → 0 hits. `prune` → 4, none about knowledge (job rows, log rows, a sync bug). "stale" → 64, essentially **all** about *index* staleness (embeddings, locks, watermarks), not stale knowledge: the word does not mean curation in this codebase.

Hygiene-fails-silently, verified:

| # | State | Title (abridged) |
|---|---|---|
| **3889** | closed | *eval suspected-contradictions: a run where **every judge call fails reports as "0 contradictions" and doctor shows [OK]*** |
| **1145** | closed | all judge calls fail as 'unknown' errors with $0 cost (never reaches Anthropic) |
| **2553** | closed | judge output unparseable with small local models — 10/10 parse_fail **on a planted contradiction** |
| **3042** | closed | *consolidate phase is **structurally zero-yield** on distinct-facts stores (the v0.32 LLM synthesis the header promises is unshipped)* |
| **3824 / 4057** | closed | consolidate never promotes singleton facts; buckets over 100 active facts **skip forever** |
| **2464** | closed | calibration_profile **silently no-ops on every non-owner brain** |
| **2653** | closed | *dream.drift.enabled gates an **unwired scaffold** — drift detection never actually ships* |
| **1184** | closed | Dream cycle's link extraction phase **silently no-ops (0 links extracted)** |
| **2964** | closed | dream sync fails nightly on a legacy brain dir; ***doctor's 'ok' is a false-negative coincidence*** |
| **3269** | closed 2026-07-23 | *take_proposals is **write-only**: the documented review CLI doesn't exist, pending queue grows unbounded* — **"reached 32.5k rows across ~2.9k pages, growing 2–6k rows/day"** |
| **4419** | **open** | Native transcript ingestion never reaches Dream, **silently disabling its core conversation-to-wiki synthesis** |
| **4576** | **open** | doctor: extract_atoms_backlog **returns OK for a phase without verifying anything runs the cycle** |
| **4612** | **open** | No source-agnostic collapse stage — *a duplicated page keeps every slot **and** merges every boost* |
| **4649** | **open** | Sync never delete-reconciles derived timeline_entries: edited bullets **leave stale rows** |

37 open issues contain "silent". #3269 is the structural one: the human-arbitration design produced a 32,500-item review queue with **no door** — the CLI the docstrings pointed at did not exist — for months, ending a week after the talk.

## 7. What the hygiene surfaces actually are (three corrections of fact)

- **"20 doctor checks"** understates it — `src/commands/doctor/checks/` has 20 *files*, but `doctor.ts` registers **117 distinct check names**. However: only **12** of them attach a `makeRemediationStep`, and every one is *additive* (`onboard.embed_catch_up`, `onboard.extract_ner_links`, `onboard.extract_timeline_from_meetings`, `onboard.takes_bootstrap`, pack upgrade, `sync-retry-failed`, `conversation_facts_backfill`, `integrity-auto`). **Not one remediation prunes anything.** The doctrine is stated in `doctor/checks/stale-mentions.ts:12`: *"**READ-ONLY by design**; … **a destructive write doesn't belong on a doctor check's back**."* And the closest thing to a garbage detector, `junk_entity_hubs` (#4222) — near-empty entity pages that accreted huge edge counts from the regex auto-linker, "generic-token names like *Will*" — is **"Warn + list only."**
- **The "quarantine lane" is two unrelated things, neither of them curation.** (a) `src/core/quarantine.ts` hides pages matching **6 hand-written regexes for Cloudflare/CAPTCHA interstitials** plus operator literal substrings — a scraper-artifact filter at ingest. (b) `src/core/extraction-review.ts` marks auto-extracted entity stubs `status: unverified`; those pages are **not hidden** ("they rank as ordinary content"), promotion/rejection is owner-only and manual, and doctor merely "counts unverified stubs older than N days as a review nudge." Nothing expires them.
- **`gbrain lsd` is not hygiene at all**, and the repo says so. It is a divergent-idea generator that *adds* pages, biased toward stale ones. Its own incident report, `docs/incidents/2026-05-20-lsd-cost-explosion.md`: *"Estimated cost: $0.96 · Actual cost: **$50.71** — 53× over estimate … 15,868 raw ideas … Judge phase failed … **Zero ideas surfaced to the user — complete failure**."* Open issue **#4766**: *"judge failure deletes the checkpoint, and the `--retry-judge` it advises is unimplemented."*
- Also: **23 phases, not 25.**

## 8. Steelman — what survives of the original claim

I do not want to overstate this. The following are real and do map to Tan's Sense-A list:

- **Provenance on every fact is enforced**, not advisory: `facts.source TEXT NOT NULL`, and `remember` errors `provenance_required` on empty. That is one third of Tan's "memory plus hygiene."
- **Contradiction checks exist, are statistically honest, and got *more* honest under pressure**: after #3889, `eval-contradictions/run-health.ts` is a shared predicate that stamps `run_status: 'judge_failed'`, suppresses the 0/N headline, exits 1, and **downgrades doctor's green check to a warn**. Publishing that predicate is the opposite of marketing.
- **Refusing to auto-resolve is a defensible design choice, not an omission.** `auto_resolve` exists with a conservative 0.95 threshold and is documented as "flip once trust is earned." Given #2553 (10/10 judge parse failures on a planted contradiction) and the temporal false-positive classes, auto-applying would have been worse.
- **#4696 was fixed** — in the exact commit under review (v0.48.5.0, 2026-09-08). Both forget tiers now strike the DB body. Forgetting is durable across the cycle as of 8 weeks after the talk. (Tier-2 forgets still "DO NOT survive rebuild.")
- The **`db_only` storage tier** is a real curated-vs-bulk split, and `purge`'s 72h recovery window is good engineering.

## 9. Implications for the synthesis

1. **Do not cite the dream cycle as evidence that the librarian is a solved, shipped thing.** The accurate sentence is: *GBrain operationalizes provenance and contradiction **detection**; pruning remains manual, and the code says so on purpose.* If the synthesis wants a shipped librarian, the honest answer is that nobody has one.
2. **This strengthens, not weakens, the memory-hygiene thesis in `findings/memory-hygiene.md`.** The most-starred, most-worked implementation of a company brain — 411K LOC, 1,915 issues — has an accretion loop with a human-shaped hole where deletion should be, and the observable consequence is a 32.5k-item unread review queue growing 2–6k/day. That is the strongest available empirical support for "bounded self-managed memory loses to full context on knowledge-update questions."
3. **It sharpens the fruit-fly bridge into the single most defensible design claim in this project.** The gap is exactly the mushroom-body function: a *separately parameterised, autonomously firing forgetting process* (dopaminergic forgetting) plus a *novelty gate at ingest* (FlyHash / fly Bloom filter) that would stop the junk-entity-hub and duplicate-claim classes from being written at all. `last_retrieved_at` already exists and is indexed; today it feeds an idea generator. Wiring it to a readout-gated decay-and-demote daemon is a ~small change with a clear before/after metric, and it is unclaimed ground.
4. **Retire "quarantine lane," "20 doctor checks," and "25-phase" from the write-up.** Use: 23 phases, 117 doctor checks of which 12 have remediations and all 12 are additive, and a quarantine that is a Cloudflare-page regex filter.
5. **Suggested crux experiment**: on a public corpus, run GBrain's cycle over a stream with scheduled fact updates and measure `recall@k` for *superseded* claims over time. My prediction from the code: superseded prose stays retrievable indefinitely; the only thing that falls is the fact row's displayed confidence number.

## 10. Confidence and limits

- **High confidence** (direct source read at a pinned commit): no automatic knowledge deletion/demotion in the cycle; contradiction probe is user-initiated, read-only, and its only auto-consumer is a prompt hint; decay is a pure sort function; doctor remediations are all additive; 23 phases; default pack declares `phases: []`.
- **Medium confidence**: the characterization of *why* (design intent vs. unshipped work). I read the stated rationale (D17, "a destructive write doesn't belong on a doctor check's back") and take it at face value; #2653 and #3042 show at least some of the gap is unshipped scaffolding rather than principle.
- **Unverifiable**: whether Garry's private ~220K-page brain has out-of-band pruning that is not in the public repo. Everything here describes the open-source artifact only.
- Issue titles/bodies are user-reported; I read the maintainer's closing comments where they existed and verified the #4696 fix is present in the clone.

---

## Sources

Repo at `43597b19e50a3abf56409337f248f7966860293c` (v0.48.5.0, pushed 2026-09-08); `gh api repos/garrytan/gbrain` → 29,764 stars / 4,441 forks / 176 open items; `search/issues` → 1,915 issues, 105 open.

**Code**
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle.ts — `ALL_PHASES` (23), per-phase ordering rationale, `purge` doc comment (:1670), `runPhaseOrphans` (:1817), `net_fact_deletion` warning (:1519)
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle/grade-takes.ts — `autoResolve = opts.autoResolve ?? false; // D17 default OFF` (:512)
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle/drift.ts — report-only, `dream.drift.enabled` (:50, :278)
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle/synthesize.ts — `loadPriorContradictionsBlock` (:2524)
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle/phantom-redirect.ts — the one in-cycle soft-delete (:457)
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle/extract-facts.ts — fence-authoritative reconcile + `deleteFactsForPage` (:619-650)
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/decay.ts — pure, no I/O; `HALFLIFE_DAYS`
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/meta-hook.ts — decay used only to sort (:137)
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/forget.ts — strike-through semantics; #4696 DB-body strike (:34)
- https://github.com/garrytan/gbrain/blob/master/src/core/quarantine.ts — HIDE marker, high-confidence junk only
- https://github.com/garrytan/gbrain/blob/master/src/core/content-sanity.ts — `BUILT_IN_JUNK_PATTERNS` (Cloudflare/CAPTCHA)
- https://github.com/garrytan/gbrain/blob/master/src/core/extraction-review.ts — unverified stubs rank as ordinary content; promotion is owner-only
- https://github.com/garrytan/gbrain/blob/master/src/core/eval-contradictions/auto-supersession.ts — "The probe NEVER auto-applies"
- https://github.com/garrytan/gbrain/blob/master/src/core/eval-contradictions/run-health.ts — the #3889 honesty predicate
- https://github.com/garrytan/gbrain/blob/master/src/core/search/hybrid.ts — `applySalienceBoost` (:363)
- https://github.com/garrytan/gbrain/blob/master/src/core/search/recency-decay.ts — positive-only recency component
- https://github.com/garrytan/gbrain/blob/master/src/core/search/graph-signals.ts — `SESSION_DEMOTE` (:405)
- https://github.com/garrytan/gbrain/blob/master/src/commands/doctor.ts — 117 check names, 3 `makeRemediationStep` sites, `junk_entity_hubs` "Warn + list only" (:4044)
- https://github.com/garrytan/gbrain/blob/master/src/commands/doctor/checks/stale-mentions.ts — "READ-ONLY by design"
- https://github.com/garrytan/gbrain/blob/master/src/core/onboard/checks.ts — the other 6 remediation steps, all additive
- https://github.com/garrytan/gbrain/blob/master/src/core/orphan-policy.ts + src/commands/orphans.ts — count only, never delete
- https://github.com/garrytan/gbrain/blob/master/src/core/schema-pack/base/gbrain-base-v2.yaml — `phases: []` (:44)
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/writeback-config.ts — `DEFAULT_TRANSIENT_TTL = '3d'`, default OFF
- https://github.com/garrytan/gbrain/blob/master/src/schema.sql — `last_retrieved_at` index exists "for LSD's stale-page query" (:270-276)

**Docs**
- https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md — "Probe never mutates the brain" (:145); "NEVER auto-applies" invariant
- https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md — ~115 HIGH findings walked by hand
- https://github.com/garrytan/gbrain/blob/master/docs/incidents/2026-05-20-lsd-cost-explosion.md — 53× overrun, zero ideas surfaced
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/KEY_FILES.md — `find_contradictions` "user-initiated only" (:154)
- https://github.com/garrytan/gbrain/blob/master/skills/maintain/SKILL.md — "Never delete pages without confirmation"
- https://github.com/garrytan/gbrain/blob/master/skills/correction-pipeline/SKILL.md — "This skill is REACTIVE"
- https://github.com/garrytan/gbrain/blob/master/README.md — "Wired into the daily dream cycle" (:409)

**Issues**
- https://github.com/garrytan/gbrain/issues/4696 · 4622 · 3889 · 3269 · 2653 · 3042 · 3824 · 4057 · 2464 · 1184 · 2964 · 1145 · 2553 · 4169 · 4419 · 4576 · 4612 · 4649 · 4766 · 4115 · 3968

**Talk**
- /Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt — 14:30–15:05 (hygiene/pruning), 17:41 and 19:28 (librarian-as-selector)

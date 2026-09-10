# d2 — Memory lifecycle: readout-gated consolidation, a suppressible forgetting daemon, and extinction-as-accumulation

**Key:** `d2-lifecycle` · design panel, angle 2 · 2026-09-10 · author: research worker (Claude Opus 5)
**Target:** GBrain at commit `43597b19e50a3abf56409337f248f7966860293c` (v0.48.5.0). Every file, line, column, default and SQL statement quoted below was fetched from `raw.githubusercontent.com` at that SHA during this session, not paraphrased from prior reports.

---

## 0. The pitch

GBrain's hot→cold promotion fires on **duplication** and its forgetting is a **read-time sort key that never writes back**. The consequence is measured, not theoretical: on a live store, one `dream --phase consolidate` run processed **62 buckets and promoted 0 facts into 0 takes** (gbrain#3042), while the take-proposal queue that *is* human-gated reached **32,500 rows growing 2–6k/day** (gbrain#3269). A fact stated once and read every day is never promoted; a fact stated three times in near-identical words and never read is. That is backwards, and it is backwards in a way the fruit-fly literature has a specific, copyable answer to.

This proposal replaces the *trigger*, not the *store*. Three changes, all deterministic, all zero-LLM by default, all reversible:

1. **L1 — readout-gated promotion.** Promotion becomes conditional on the hot tier's own readout (Huang et al., *Nature* 634:1141, 2024: consolidation is not a cron job, it is gated by disinhibition of the promoting DAN once the hot MBON's response has been depressed over ~3 spaced bouts). GBrain already writes the readout signal in three places and spends it on an idea generator.
2. **L2 — a suppressible forgetting daemon.** Forgetting becomes a separately parameterised, continuously running, *suppressible* process that **demotes rather than deletes** (Berry et al. 2012/2015; Shuai et al. 2010; Cervantes-Sandoval et al. 2016 — separate receptor, separate cascade, tone that rises with activity and is blocked by sleep). Its budget is slaved to the acquisition rate, which is library science's rate law, not the fly's.
3. **L3 — extinction-as-accumulation for conflicting takes.** Conflicting claims are never overwritten; each carries an append-only ledger of signed evidence with **separately parameterised decay per compartment**, netted at read and always returned *with* the ledger (Felsenberg et al., *Cell* 175:709, 2018).

**Fidelity, stated up front: none of the three is Deep.** Under g07's rubric all three are **Analogy** — the control structure transfers, the currency (odour→document, valence→truth) does not. The only Deep mechanism in the fly inventory is the Bloom-filter novelty gate, which is a different designer's angle. I therefore commit in advance to a **biology kill criterion (K4)**: an arm built from TinyLFU admission + a CREW retention schedule + SQL:2011 bitemporal constraints, containing zero fly content, is in the experiment, and if it ties, the honest write-up is "we implemented a cache admission policy, a retention schedule and a temporal constraint; three literatures had it first."

**Modal predicted outcome, pre-registered: a pooled null.** I expect ±2 pp on the pooled primary and a real effect confined to the supersession/conflict strata and to the operational metrics (superseded-serving rate, cold-tier yield, hot-tier growth). That is g06's hypothesis H2 and I am not going to pretend otherwise.

---

## 1. What GBrain's lifecycle actually does today (verified at source)

### 1.1 Promotion is duplication-triggered, and measurably yields zero

`src/core/cycle/phases/consolidate.ts` (334 lines). The gate, verbatim:

```sql
SELECT source_id, entity_slug, COUNT(*)::int AS count
FROM facts
WHERE consolidated_at IS NULL AND expired_at IS NULL
  AND (valid_until IS NULL OR valid_until > now())
  AND entity_slug IS NOT NULL
GROUP BY source_id, entity_slug
HAVING COUNT(*) >= ${minPerBucket}          -- default 3
```

then `minOldestAgeMs ?? 24h`, then `clusterFacts(unconsolidated, 0.85)` — greedy cosine, head-as-centroid — then `if (cluster.length < 2) continue;`. The take's claim is `cluster.reduce((a,b) => b.confidence > a.confidence ? b : a)` (highest confidence, not newest), weight is the cluster mean.

Two independent ≥2 gates. Both are gates on **saying the same thing twice**. Nothing anywhere in the phase reads a retrieval, citation, or usage signal.

The measured consequence, from the repo's own issue tracker (fetched today, `gh api repos/garrytan/gbrain/issues/3042`, closed):

> "One `dream --phase consolidate` run processed **62 buckets and promoted 0 facts into 0 takes** (5 skipped), ~108ms. The only fact pairs at cosine >= 0.85 live in 2-fact buckets, below the >= 3-fact bucket gate; every bucket that clears the >= 3 gate tops out at cosine **0.844**." — on ~360 unconsolidated active facts across ~138 entities.

Companion issues: **#3824** ("Most captured facts are discrete one-off events — a meeting, a decision, a status update — not repeated near-duplicate mentions… they land in singleton clusters and are never consolidated. They accumulate as a permanent 'pending consolidation' backlog"), **#4057** (buckets over 100 active facts skip forever). All three closed; the gates are unchanged at v0.48.5.0.

**The arbitration rule hidden inside promotion.** After writing the take, the phase walks the cluster chronologically and stamps `valid_until = next_newer.valid_from` on every fact except the newest. Its own comment: *"This makes the facts table a proper bitemporal record without the contradiction probe having to mutate it."* So GBrain's only automatic supersession rule is **recency inside a cosine-0.85 cluster** — which v09b establishes is correct for roughly one conflict type in three, is inverted when a later statement is simply false, and is undefined when two facts are true under different conditions.

### 1.2 Forgetting is a pure read-time function — and its parameter is mislabelled

`src/core/facts/decay.ts` (65 lines), fetched in full. `HALFLIFE_DAYS = { event: 7, commitment: 90, preference: 90, belief: 365, fact: 365, idea: 365 }`, and:

```ts
const decayed = fact.confidence * Math.exp(-ageDays / halflife);
// exp(-age/halflife) — at age=halflife returns ~0.368.
```

Header: *"Pure function. No side effects. No I/O."* Four consumers, all read-side (recall, supersession audit, `facts_health`, the MCP `_meta.brain_hot_memory` injector). There is no confidence floor, no write-back, no expiry, and — per v06b's grep of `KNOWN_CONFIG_KEYS` — **no knowledge-retention config key of any kind**.

**A verified defect worth fixing while we are in the file.** `HALFLIFE_DAYS` is not a half-life; it is an exponential time constant τ. The file's own comment concedes it (`returns ~0.368`, i.e. e⁻¹, not ½). A fact labelled "7-day half-life" is at **36.8%** after 7 days. The true half-life is `τ·ln2 = 4.85 days`; to get the documented behaviour the constant would have to be `7/ln2 = 10.10`. Every kind in the table decays **1.44× faster than its name claims**. This matters here because L2 re-uses this function, and it matters generally because anyone calibrating decay against these defaults is calibrating against a 44% error.

### 1.3 Three readout signals already exist. None of them touches the lifecycle.

| Signal | Where written | What consumes it today |
|---|---|---|
| `pages.last_retrieved_at` | `src/core/last-retrieved.ts` — op-layer only, fired from `search`/`query`/`get_page` handlers, **explicitly not from engine methods** so "internal callers (sync, migrations, helper flows)… never fire from `import-file.ts`, the dream cycle, doctor probes". 5-minute throttle. Default-on, `search.track_retrieval` escape hatch. Fire-and-forget, off the response path. | `gbrain lsd`'s stale-bias query — a *divergent-idea generator* that picks never-read pages **in order to write more pages**. |
| `synthesis_evidence(synthesis_page_id, take_page_id, take_row_num, citation_index)` | written when a synthesis page cites a take; FK `ON DELETE CASCADE` to `takes(page_id,row_num)` | citation rendering |
| `context_volunteer_events` | push-context feedback log; schema comment: *"'Used' derives from `pages.last_retrieved_at > volunteered_at`"* | a 90-day-pruned telemetry log |

That first row is the finding. GBrain has built, deliberately and carefully, exactly the signal the fly uses to gate consolidation — a *user-facing-surface-only* readout with a refractory period — and wired it to the one subsystem that adds material to the pile. The schema comment even names the property: *"Pure signal: 'a user-facing surface just surfaced this page.'"*

---

## 2. Mechanisms borrowed, and their fidelity

| | Mechanism | Primary source | Fidelity (g07 rubric) | What actually transfers |
|---|---|---|---|---|
| **L1** | γ→α consolidation gated by MBON-γ1pedc>α/β disinhibition, ~3 conditioning bouts | Huang, Luo, Woo, Roitman, Li, Pieribone, Kannan, Vasan, Schnitzer, *Nature* 634:1141–1149 (2024), doi:10.1038/s41586-024-07819-w | **Analogy (strong)** as control structure; **Superficial** as code (the implementation is a TinyLFU admission policy) | The *inversion of control*: promotion is triggered by the hot tier's own readout crossing a threshold, not by a schedule; and bouts are **spaced**, not massed (a refractory window is load-bearing) |
| **L2** | Active forgetting: dDA1 (acquisition) vs DAMB (forgetting); Scribble→Rac1→Pak3→cofilin; MP1/MV1 ongoing tone rising with locomotion; sleep blocks it | Shuai et al., *Cell* 140:579 (2010); Berry et al., *Neuron* 74:530 (2012); Cervantes-Sandoval et al., *Neuron* 90:1230 (2016); Berry et al., *Cell* 161:1656 (2015) | **Analogy** | Three properties: (a) a **second, independent channel** — you cannot achieve forgetting merely by declining to write; (b) **continuous**, not write-triggered; (c) **suppressible** by a system-state signal. Nothing about *what* to forget transfers. |
| **L3** | Extinction as parallel opposing memories in different compartments, integrated at the MBON | Felsenberg, Jacob, Walker, Barnstedt, Edmondson-Stait, Pleijzier, Otto, Schlegel, Sharifi, Perisse, Smith, Lauritzen, Costa, Jefferis, Bock, Waddell, *Cell* 175:709–722 (2018), doi:10.1016/j.cell.2018.08.021; write-gating on prediction error from Bennett, Philippides & Nowotny, *Nat. Commun.* 12:2569 (2021) | **Analogy** | Never overwrite; keep both traces **in separate compartments so they decay at different rates**; net at readout; gate writes on prediction error. The currency (valence, not truth) does not transfer, and the circuit never returns "A is correct." |

Supporting circuit reference for all three: Gkanias, McCurdy, Nitabach & Webb, *eLife* 11:e75611 (2022) — the incentive circuit, whose **MAM microcircuit** makes promotion and eviction *one operation* (the forgetting DAN that erases contrary LTM is the same neuron that clears the STM entry once transferred). L1 and L2 below are deliberately built so that a promotion also clears the hot row, for that reason.

---

## 3. Exact insertion points

All paths relative to the `garrytan/gbrain` repo root at v0.48.5.0.

### L0 — the readout ledger (prerequisite, ~half a day)

**Migration (new, v147).** Two columns on `pages`:

```sql
ALTER TABLE pages ADD COLUMN IF NOT EXISTS retrieval_bouts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS last_bout_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS pages_retrieval_bouts_idx ON pages (retrieval_bouts) WHERE deleted_at IS NULL;
-- backfill so existing brains are not treated as never-read
UPDATE pages SET retrieval_bouts = 1, last_bout_at = last_retrieved_at
 WHERE last_retrieved_at IS NOT NULL;
```

**Verified safety property.** `src/schema.sql:163–188` defines `bump_page_generation_fn()`, a `BEFORE INSERT OR UPDATE` trigger that bumps `pages.generation` (the query-cache invalidation clock) only when one of an **explicit allow-list** of columns changes: `compiled_truth, timeline, frontmatter, deleted_at, contextual_retrieval_mode, title, type, page_kind, corpus_generation, content_hash`. `last_retrieved_at` is deliberately absent — *"so read-time mutations don't invalidate every cache row."* My two new columns are likewise absent, so **incrementing a bout counter on every search does not invalidate the query cache.** This is the single detail that makes L0 free; it needed checking and it checks out.

**Code change — one statement.** `src/core/last-retrieved.ts`, inside `bumpLastRetrievedAt`, replace the existing UPDATE:

```sql
UPDATE pages
   SET last_retrieved_at = NOW(),
       retrieval_bouts = retrieval_bouts
         + CASE WHEN last_bout_at IS NULL
                  OR last_bout_at < NOW() - ($2 || ' hours')::interval
                THEN 1 ELSE 0 END,
       last_bout_at = CASE WHEN last_bout_at IS NULL
                             OR last_bout_at < NOW() - ($2 || ' hours')::interval
                           THEN NOW() ELSE last_bout_at END
 WHERE id = ANY($1::int[])
   AND (last_retrieved_at IS NULL OR last_retrieved_at < NOW() - INTERVAL '5 minutes')
```

`$2 = lifecycle.bout_refractory_hours` (default **24**). Because the refractory window (24 h) is far longer than the existing MVCC throttle (5 min), no bout boundary can be missed by the outer `WHERE`. Everything else about the module — fire-and-forget, the drain registered with `registerBackgroundWorkDrainer`, the `isUndefinedColumnError` fallback, the `search.track_retrieval` opt-out — is unchanged.

**New doctor check** `readout_signal_liveness` in `src/commands/doctor/checks/`: warn when zero bouts were recorded in 24 h on a brain with search traffic, or when `search.track_retrieval` is false while `lifecycle.promotion_gate != 'duplication'`. (Without this, disabling the signal silently converts L1 into "promote nothing" — a failure mode the repo has hit before: #3889, #2464, #1184, #2653 are all "hygiene phase silently no-ops and doctor shows OK".)

### L1 — readout-gated promotion (~2 days)

**File:** `src/core/cycle/phases/consolidate.ts`.
**Config:** `lifecycle.promotion_gate ∈ {duplication, readout, both}` — **default `duplication`**, i.e. byte-identical to today. This is the one-switch A/B lever g06 requires.

Add to `ConsolidatePhaseOpts`: `promotionGate`, `minReadoutBouts` (B, default **3**), `minWriteBouts` (E, default **2**), `maxPromotionsPerRun` (default **200**).

Bucket scan becomes a union:

```sql
-- duplication path (unchanged)
SELECT source_id, entity_slug FROM facts f
 WHERE consolidated_at IS NULL AND expired_at IS NULL
   AND (valid_until IS NULL OR valid_until > now()) AND entity_slug IS NOT NULL
 GROUP BY source_id, entity_slug HAVING COUNT(*) >= 3
UNION
-- readout path (new)
SELECT f.source_id, f.entity_slug
  FROM facts f JOIN pages p
    ON p.source_id = f.source_id AND p.slug = f.entity_slug AND p.deleted_at IS NULL
 WHERE f.consolidated_at IS NULL AND f.expired_at IS NULL
   AND (f.valid_until IS NULL OR f.valid_until > now()) AND f.entity_slug IS NOT NULL
   AND p.retrieval_bouts >= $B
 GROUP BY f.source_id, f.entity_slug
HAVING COUNT(*) >= $E
```

Then, per bucket, under the readout path only:

- `if (cluster.length < 2) continue;` → `if (cluster.length < 2 && gate !== 'readout' && gate !== 'both') continue;` — **singleton clusters promote when readout-gated.** This is the largest behavioural change and it is the one #3824 asks for.
- Claim selection changes from `argmax(confidence)` to **newest fact with an open validity interval**, which is the only choice consistent with the `valid_until` stamping the same function performs three lines later.
- Weight becomes `σ(net(c))` from L3 when the ledger exists, else the current cluster mean.
- Rank buckets by `gate_score(e) = min(1, n_e/E) · min(1, bouts_e/B)` and truncate at `maxPromotionsPerRun`. Bounded work per night; ranking rather than thresholding is g04's rate-law discipline applied to the promotion side.
- **MAM property:** on promotion, clear the hot rows exactly as today (`consolidated_at`, `consolidated_into`, chronological `valid_until`) — promotion and eviction stay one operation, which is Gkanias' memory-assimilation microcircuit and is already how GBrain behaves.

### L2 — the forgetting daemon (~4 days)

**Deliberately NOT a dream-cycle phase.** Coupling pruning to the write cycle reproduces the write-triggered pruning the biology argues against (MP1/MV1 fire continuously, before and after learning). New command `gbrain lifecycle forget`, its own cron, `--dry-run` default, `lifecycle.forget.enabled` default **false**.

**Schema:**

```sql
ALTER TABLE facts ADD COLUMN IF NOT EXISTS suppression REAL NOT NULL DEFAULT 0
  CHECK (suppression BETWEEN 0 AND 1);
ALTER TABLE facts ADD COLUMN IF NOT EXISTS dormant_at TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS lifecycle_events (
  id BIGSERIAL PRIMARY KEY,
  at TIMESTAMPTZ NOT NULL DEFAULT now(),
  kind TEXT NOT NULL CHECK (kind IN ('promote','suppress','revive','net_flip')),
  fact_id BIGINT, take_id BIGINT, page_id INTEGER,
  before REAL, after REAL, reason TEXT NOT NULL, run_id TEXT NOT NULL
);
```

**Read-side hook — one line.** `src/core/facts/decay.ts`, `effectiveConfidence` returns `decayed * (1 - fact.suppression)`. Four call sites inherit it for free.

**Never deletes.** A fact whose effective confidence falls below `lifecycle.forget.floor` (default **0.05**) gets `dormant_at = now()` and is excluded from the hot/ambient channel and from take-weight aggregation. It is **not** removed from `facts`, **not** removed from the page prose, and **not** removed from the chunk index. This is deliberate and triply justified: (a) Xie & Ocker (arXiv:2509.19351) show pruning KC→MBON synapses degrades classification much as ablation does, with mature units hurting most; (b) 2025–26 fly work shows forgotten memories persist as *silent MBON traces* recoverable by context-gated reminders — forgetting means suppressing expression, not deleting the row; (c) GBrain's own D17 doctrine (*"a destructive write doesn't belong on a doctor check's back"*) and its one at-scale automatic deletion, which was an accident that hard-deleted **324 facts across 41 pages** and completed silently because the warning landed in a filtered report (#4622).

**Reset on recall.** Any bout on the owning page sets `suppression = 0, dormant_at = NULL` and logs a `revive` event. Reconsolidation-on-retrieval, and the safety valve that makes suppression cheap to get wrong.

### L3 — the evidence ledger (~5 days)

```sql
CREATE TABLE IF NOT EXISTS claim_evidence (
  id           BIGSERIAL PRIMARY KEY,
  take_id      BIGINT NOT NULL REFERENCES takes(id) ON DELETE CASCADE,
  fact_id      BIGINT REFERENCES facts(id),
  observed_at  TIMESTAMPTZ NOT NULL,
  sign         SMALLINT NOT NULL CHECK (sign IN (-1,1)),
  magnitude    REAL NOT NULL CHECK (magnitude BETWEEN 0 AND 1),
  compartment  TEXT NOT NULL CHECK (compartment IN ('support','refute')),
  holder       TEXT NOT NULL,
  source       TEXT NOT NULL,
  verdict      TEXT,          -- reuse the probe's six classes when available
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS claim_evidence_take_idx ON claim_evidence (take_id, observed_at DESC);
```

**Where signs come from, with zero new LLM calls.** GBrain already caches contradiction verdicts in `eval_contradictions_cache`, keyed on `(chunk_a_hash, chunk_b_hash, model, prompt_version, truncation_policy)`, with six classes: `no_contradiction | contradiction | temporal_supersession | temporal_regression | temporal_evolution | negation_artifact`. Map `contradiction | temporal_regression` → `sign = -1`, everything else → `+1`, and copy the class into `verdict`. Where no verdict exists, `+1`. This reuses the most expensive artifact in the repo instead of duplicating it.

**Netting, at read.** New `src/core/takes/net.ts`, called from the `entity`/`recall` verbs and from `src/core/search/hybrid.ts`'s evidence-stamp stage:

```
net(c) = Σ_e sign_e · magnitude_e · exp(−age_e / τ_{compartment(e)})
weight = 1 / (1 + exp(−k·net))          k = lifecycle.net_slope, default 1.5
```

with **τ_support = 365 d and τ_refute = 730 d** as defaults. The separate time constants are the load-bearing half of Felsenberg — the two traces live in different compartments and decay at different rates — and the asymmetry (refuting evidence decays slower) is a **policy choice I am making, not biology**: it is harder to un-refute a claim than to re-support one. State it as a tunable, not a finding.

**Write-gating on prediction error.** Append an event only when `|sign·magnitude − net(c)| > θ_PE` (default 0.15), so the ledger is not dominated by the same claim restated in five Slack messages. Honest note: this is dedup with a neuroscience name, and a fly-Bloom-filter novelty gate at ingest (the d1 angle) would do it better and earlier.

**Always return the ledger.** The MCP response for a claim carries `{claim, net, weight, ledger: [{at, sign, source, holder, verdict}], holders: [...]}`. Never a bare net. This is the mitigation for the fly's own pathology: accumulate-and-net with context-gated reinstatement is *how* confident false memories are produced (PMC13533848).

**Relationship to g01's bitemporal recommendation — complementary, and this is the cleanest part of the design.** g01 recommends SQL:2011 `PRIMARY KEY (key, period WITHOUT OVERLAPS)` so that two contradictory live facts become a *write error* rather than a retrieval problem. Adopt that first. Then the three-way decision table resolves with no model call:

| Same (subject, predicate) | Valid intervals | Holder | Action |
|---|---|---|---|
| yes | **disjoint** | any | **supersession** — today's chronological `valid_until` stamp. Keep it. |
| yes | **overlapping** | **same** | the constraint would reject the write → **route to `claim_evidence` as a signed event** on the existing take. This is L3's whole reason to exist. |
| yes | **overlapping** | **different** | **debate** — legal by construction; net *per holder*, never merge. g01 notes GBrain "cannot currently mint this state"; the ledger mints it. |

So L3 is not an alternative to the bitemporal constraint; it is the constraint's escape hatch. And note what it is *not*: it is **not an arbiter**. v09b establishes that hand-written deterministic rules lose head-to-head against an LLM judge on real conflicting sources (ConflictRAG source selection 75.6% vs 78.3%; RegDivergence-101 macro-F1 0.511 vs 0.830). L3 deterministically aggregates *eligibility and bookkeeping* and defers adjudication to the reader — model or human — which is the split g01 and v09b both land on.

---

## 4. Parameters, in one table

| Symbol | Config key | Default | Where it comes from |
|---|---|---|---|
| B (readout bouts) | `lifecycle.min_readout_bouts` | 3 | Huang 2024: "roughly three conditioning bouts"; MBON-α3 sustained suppression across 24 h+ after three bouts |
| R (refractory) | `lifecycle.bout_refractory_hours` | 24 | Spaced-vs-massed training; also makes a "bout" ≈ "a different working day" |
| E (write bouts) | `lifecycle.min_write_bouts` | 2 | Weakened from GBrain's current 3 because the readout term now carries the evidence |
| A (min age) | existing `minOldestAgeMs` | 24 h | unchanged |
| Promotion budget | `lifecycle.max_promotions_per_run` | 200 | bounded work; CREW rate law |
| Forget budget | `lifecycle.forget.budget` | `= facts written since last run` | **CREW: "weed about the same amount as you are adding"** (g04). This, not ρ_f, is what makes the daemon safe. |
| Floor φ | `lifecycle.forget.floor` | 0.05 | arbitrary; tune against stale-serve rate |
| s(t) suppression | `lifecycle.forget.quiet_windows` | see below | Berry 2015: sleep *blocks* forgetting |
| τ_support / τ_refute | `lifecycle.net_tau_support/refute` | 365 d / 730 d | compartmental decay (Felsenberg); the asymmetry is policy |
| θ_PE | `lifecycle.net_theta_pe` | 0.15 | Bennett 2021 RPE write-gating |
| k (net slope) | `lifecycle.net_slope` | 1.5 | calibration knob |

**Suppression signal s(t) = 1 (no forgetting) when any of:** (a) an operator-declared quiet window is active; (b) the entity has an `open_loops` row with `status='open'` and `last_activity_at` within 14 days (`open_loops` exists at migration v144 with exactly these columns — don't prune a topic the org is currently working on); (c) **the last dream cycle failed, or the most recent contradiction run carries `run_status='judge_failed'`.** (c) is my own addition and the most operationally important one: gbrain#3889 documents a run where *every judge call failed, the probe reported "0 contradictions", and doctor showed `[OK]`*. Never prune while the sensors are broken.

---

## 5. Benchmark, metric, baseline

Follows g06's protocol; the arms are one-switch ablations of a single build.

**Arms.** B0 GBrain default (`promotion_gate=duplication`, no daemon, no ledger) · B1 +L1 only · B2 +L2 only · B3 +L3 only · B4 all three · **B5 the non-biological control** (W-TinyLFU admission with an equal promotion budget + a CREW acquisition-rate weeder + SQL:2011 bitemporal `WITHOUT OVERLAPS` with g01's debate re-key; zero fly content) · B6 full context (the arm that beats bounded self-managed memory by 15 points on knowledge-update).

**Datasets.** MemConflict (`github.com/TaoZhen1110/MemConflict`, `Data/Step4_4.jsonl`; g06 measured the released set at 30 instances / 3,750 questions / 2,946 `dynamic` / 444 `conditional` / 360 `static`) and LongMemEval-S (470 scored, knowledge-update slice n=78). MemConflict ships `Evaluation/diagnose_failures.py`, which decomposes errors into **retrieval failure vs utilisation failure** — the exact split this proposal needs, since L1 and L2 act on retrieval eligibility and L3 acts on utilisation.

**Endpoints.**

- **Primary (pre-registered, one):** judged answer accuracy on the pooled supersession stratum = LongMemEval knowledge-update (78) + MemConflict `dynamic` (2,946) = n=3,024, MDD ≈ 2.0 pp at p_disc=0.15.
- **Primary for L3 specifically:** MemConflict `static` + `conditional` (n=804, MDD ≈ 3.8 pp). These are the strata where newest-wins is *inverted* or *undefined*, i.e. precisely the cases an accumulate-and-net-with-ledger policy exists for. If L3 does not move these, it does not work.
- **Secondary — hygiene (the metrics this proposal is really about):**
  - **Superseded-serving rate** — fraction of answers asserting a value the corpus later invalidated. Vanilla RAG runs 15–40% (MemStrata, arXiv:2606.26511); cosine separates "contradicted" from "rephrased" at AUROC **0.59**, so ranking cannot fix it and there is real headroom.
  - **Cold-tier yield** — facts promoted per 1,000 active facts per night, replicated against gbrain#3042's measured **0 promotions / 62 buckets**.
  - **Hot-tier growth** — active unconsolidated facts over 30 simulated days; B0 is predicted linear.
  - **CRS** (MemConflict conflict-recognition) — published best across six memory systems is **0.2501**; systems answer correctly without knowing a conflict existed. Detection precedes arbitration and is the actual bottleneck, which is why the ledger is returned rather than a bare net.
  - **Revive rate** — fraction of suppressed facts revived by a later bout. The daemon's own false-positive meter.
- **Explicitly barred from the primary:** CARS (arXiv:2605.17301), whose authors say it "structurally favor[s] systems with explicit conflict modules". A curated brain beating a plain hybrid on CARS is close to tautological.

**Statistics.** Paired McNemar mid-p, Holm across exactly 6 pre-registered comparisons (B1..B5 vs B0, B4 vs B5), Wilson 95% CI printed beside every cell, TOST equivalence at ±2 pp on the pooled primary, `small_sample_note` below n=30. Everything else is exploratory and labelled.

---

## 6. Expected effect size, with the reasoning

I am deriving these from published numbers rather than asserting them, and three of the four are small.

| Arm / metric | Prediction | Reasoning |
|---|---|---|
| **B4 vs B0, pooled primary (n=3,024)** | **+0 to +3 pp; modal outcome null** | v09a's decisive ablation: on FactConsolidation the *deterministic* resolution operator contributed only **+2.0 pp pooled and 0.0 pp at 262K** — the gain came from the structured-extraction stage, which is still an LLM call. L1–L3 are all deterministic operators over an existing extractor. There is no reason to expect more than a couple of points, and g06's modal hypothesis H2 is a pooled null. |
| **B3/B4 vs B0, static+conditional (n=804)** | **+4 to +10 pp** | These are the strata where recency is wrong (static) or undefined (conditional). B0's *only* arbitration rule is recency-inside-a-cosine-cluster, so it should be near-chance here; keeping both claims with a ledger converts an unforced error into an answerable question. Wide interval because no one has run this family on MemConflict. |
| **B4 vs B0, superseded-serving rate** | **−8 to −20 pp absolute** | MemStrata takes superseded-serving from 15–40% to ~0% with deterministic SPO supersession over a bi-temporal ledger — but with an oracle key, and GBrain already implements half of it inside clusters. Most of my predicted gain comes from L2's retrieval floor (a suppressed fact stops being served) rather than from L1. |
| **B1 vs B0, cold-tier yield** | **0 → 3–15 per 1,000 active facts/night** | Direct: #3042's store had 62 eligible buckets and 0 promotions because every ≥3-fact bucket topped out at cosine 0.844. Removing the cluster-size-2 requirement under a readout gate promotes singletons, which #3824 says are "most captured facts". |
| **B1 vs B0, answer accuracy** | **≈ 0, possibly negative** | More promoted takes means a larger, noisier cold tier. L1 is a *capability* change, not an accuracy change, and I pre-register it as a **non-inferiority** test at margin −2 pp rather than a superiority test. |
| **B4 vs B5 (the biology test)** | **abs(Δ) < 1 pp — I expect a tie** | This is the honest expectation. TinyLFU admission, CREW's rate law and SQL:2011 constraints cover most of what L1–L3 do. If B5 ties, K4 fires. |
| **B6 (full context)** | **beats everything on knowledge-update** | Supersede (arXiv:2606.27472): replacing full context with bounded self-managed memory drops a frontier model 92% → 77% on knowledge-update, and more capacity moves 28% → 28%. MemoryAgentBench v4 has GPT-5-mini at 78 single-hop FactConsolidation with *no memory layer at all*. If the corpus fits in context, none of this is worth building. |

---

## 7. Cost

**Runtime, per night, on a 155,795-page brain at ~5,500 new pages/month (g02's 10-pages-per-person-per-day row):**

| Component | LLM calls | $/month | Notes |
|---|---|---|---|
| L0 readout ledger | 0 | **$0** | one extra `SET` clause in an UPDATE that already runs, off the response path, cache-safe (verified §3) |
| L1 promotion gate | 0 (deterministic claim selection) | **$0** | optional Haiku synthesis of the promoted claim: 200 promotions/night × $0.0009/call ≈ **$5.40/mo** (rate corrected by g02; the repo's own doc understates its own inputs by 1.5×) |
| L2 forgetting daemon | 0 | **$0** | pure SQL, seconds |
| L3 evidence ledger | 0 by default (signs reused from `eval_contradictions_cache`) | **$0** | optional judge on unresolved overlapping pairs: at GBrain's published $0.50/100 queries, ~**$5/mo** at 1,000 pairs |
| Storage | — | ~$0 | ~11,000 `claim_evidence` rows/month; two INTEGER/TIMESTAMPTZ columns on `pages` |

Total marginal AI spend: **$0–$11/month**, against a takes-extraction line of ~$70/month at the same page rate. This proposal is roughly 1/7th of one existing cycle phase and it is the cheap end of the system by design — g02's central finding is that write-side LLM curation dominates cost by 222×–4,514× over embeddings, so a *deterministic* lifecycle change is the rare intervention that improves the expensive path without spending on it.

**Engineering:** L0 0.5 d · L1 2 d · L2 4 d · L3 5 d · harness + runs 4 d = **15.5 engineer-days**. The 2-week MVP in §11 cuts L3's PE gate and the optional judges to fit.

---

## 8. Kill criteria (pre-registered before any code)

Committed in advance, with the analysis script and prompts hashed into the receipt per g06.

**Feature kills**

- **K1 (whole proposal).** If B4 beats B0 by **< 2.0 pp** on the pooled supersession stratum (Holm-adjusted paired McNemar) **and** reduces superseded-serving by **< 8 pp** absolute — abandon the lifecycle rework. Both must fail; either alone is a partial success.
- **K2 (L2 only).** If B4 *harms* MemConflict `static` accuracy by **≥ 5 pp** vs B0, the daemon is suppressing true-but-later-denied claims. Ship L1+L3, kill L2.
- **K3 (L1 only).** If B1 fails non-inferiority at margin **−2 pp** on the pooled primary, keep `promotion_gate=duplication` as the shipped default and expose readout gating as opt-in only.
- **K6 (safety).** If the revive rate exceeds **10%** of suppressed facts, the demotion score is wrong; suppression is doing work a human would undo. Halt and re-tune before any default-on.

**Biology kills — the ones that matter for question (b)**

- **K4.** If **B5** (TinyLFU + CREW + SQL:2011, zero fly content) matches B4 within **1.0 pp** on the pooled supersession stratum and within **3 pp** on superseded-serving, then the fruit-fly framing contributed nothing measurable and the write-up must say so in those words. Ship B5, cite Einziger 2017, CREW and Kulkarni & Michels 2012, and drop Huang/Berry/Felsenberg to a motivation footnote.
- **K5 — run this first, before writing any code.** g07 names the load-bearing untested assumption of mechanism 3: *that an agent brain has a readout signal playing MBON-γ1pedc>α/β's role.* Make it a measurement. On any brain with ≥30 days of `last_retrieved_at` history, join `pages.last_retrieved_at` / `retrieval_bouts` against `synthesis_evidence` and a labelled set of answered questions, and compute the **AUROC of the readout signal for predicting "this page's fact was cited in a correct answer."** If AUROC **< 0.60**, the gate has no discriminative power, L1 dies, and the correct contribution of this report is a clean negative result on the strongest architectural idea in the fly inventory. **This costs one day and no LLM budget, and it is the single most decisive experiment in the proposal.**

---

## 9. Risks, and what the prior negative results say

1. **The readout signal is contaminated.** `last_retrieved_at` is bumped by any user-facing search that *surfaces* a page, including wrong hits. A page surfaced 20 times and never used is indistinguishable from a page surfaced 20 times and always cited. Mitigations: prefer `synthesis_evidence` citations where they exist; K5 measures this directly; and the doctor check catches a dead signal. **This is the most likely reason the whole thing fails.**
2. **Popularity feedback loop.** Promoting what is read makes it more retrievable, which makes it read more. The fly has APL inhibition enforcing ~5–10% KC sparseness and a fixed compartment budget; we have neither. Mitigation: cap promotions per entity per period and report the cold-tier Gini coefficient as a standing metric.
3. **Suppression as quiet censorship.** The rare fact nobody reads is exactly the fact a compliance question needs. Mitigations: suppression never removes a row, never touches page prose, never touches the chunk index; reset-on-recall; every suppression logged in `lifecycle_events`; budget capped at the acquisition rate.
4. **Prior negative result — pruning degrades the index.** Xie & Ocker (arXiv:2509.19351): random and targeted pruning of KC→MBON synapses degrades odour classification much as ablation does, and ablating *mature* KCs hurts more than immature ones. Directly contradicts "prune the old stuff." Answered by demote-not-delete, but it is a real warning against any future temptation to make L2 destructive.
5. **Prior negative result — the fly's own pathology.** Accumulate-and-net with context-gated reinstatement is the mechanism that generates *false memories* and silent-trace resurrection. Answered by always returning the ledger; unanswered if callers ignore it. Add a measurement: does answer accuracy change when the ledger is withheld from the model?
6. **Prior negative result — deterministic rules lose to judges.** v09b: ConflictRAG 75.6% (hand-fixed weights) vs 78.3% (LLM); RegDivergence-101 0.511 vs 0.830 macro-F1. If the netting function is treated as an arbiter, this proposal walks into that result. It is designed as an aggregator with adjudication deferred; that distinction must survive implementation review.
7. **Prior negative result — the model may not need us.** MemoryAgentBench v4: GPT-5-mini at 78 single-hop FactConsolidation with no memory system. B6 is in the design so this is measured rather than assumed.
8. **The model of L1's source is nine neurons.** Huang 2024's spiking model is 5 DANs, 3 MBONs, 2 KCs, 1 shock neuron, validated on >500 flies against olfactory conditioning. Gkanias 2022 is candid that its own circuit **fails to reproduce blocking**, tests 1 of 8 proposed opposing pairs, uses 10 KCs for 2 odours, and neglects APL inhibition. Nothing here is a validated model of an information system.
9. **Upstream acceptance risk.** GBrain's D17 doctrine refuses automatic semantic mutation on principle (*"archive is product judgment, not maintenance"*). Every mutation here is default-off, dry-run-first, budgeted, reversible, and reported in a cycle-report section that cannot be filtered out — because #4622's 324-fact deletion completed silently for exactly that reason. Even so, L2 is the piece most likely to be rejected, and it is the piece the fly literature most strongly supports.
10. **PGLite.** `search.track_retrieval` is operator-disableable and pre-v77 brains lack the column; the module already degrades silently. With no signal, `promotion_gate=readout` promotes *nothing* — worse than today. Default must remain `duplication`, and the fail-open path must be `both`, never `readout`.

---

## 10. Honest verdict against the non-biological alternatives

| Component | Best non-biological alternative | Verdict |
|---|---|---|
| **L1** readout-gated promotion | **W-TinyLFU admission** (Einziger, Friedman & Manes, *ACM TOS* 13(4), 2017), 2Q, ARC, CLOCK-Pro | The alternative is better specified, better benchmarked, and a frequency sketch is cheaper than a counter column. What the fly adds is three things and only three: the **AND** between write-evidence and read-evidence (cache policies use frequency alone), the **refractory window** making bouts spaced rather than massed, and the **framing** that consolidation is triggered rather than scheduled. Build it as TinyLFU-with-a-refractory-window; cite Huang 2024 as motivation, not derivation. |
| **L2** forgetting daemon | **CREW/MUSTIE retention schedule with the acquisition-rate law** (g04); plain TTL; FadeMem exponential decay (arXiv:2601.18642) | The library-science rate law is **better than the fly** for this job — it bounds the queue, which is what structurally prevents #3269's 32.5k-row explosion, and the fly has nothing equivalent. The fly contributes exactly two properties a retention schedule lacks: the **suppression window** and the **second independent channel**. Take the budget from CREW and the two properties from Berry. Say which half is which. |
| **L3** extinction-as-accumulation | **SQL:2011 bitemporal, `PRIMARY KEY (key, period WITHOUT OVERLAPS)`** (g01; Kulkarni & Michels 2012) | Complementary, not competing, and g01 comes first. The constraint handles disjoint intervals with zero model calls and makes contradiction unrepresentable at write time; the ledger is what you do when the constraint would otherwise reject the write. L3 is the implementation of g01's "debate" state, which g01 notes GBrain cannot currently mint. Adopting L3 without the constraint would be a mistake. |
| **The interference term h(i)** | **SAGE's von Mises–Fisher density gate** (arXiv:2605.30711, Apache-2.0, published: 3.4× lower add-phase API cost, 2.5× lower add latency, 16–18% fewer LLM calls) vs a fly Bloom filter | SAGE occupies this slot today with numbers; the fly filter has none, has never been run on text or embeddings, and its largest published evaluation is n=5,000. This is d1's fight. L2 works with either, or with the cosine cluster `consolidate` already computes. |
| **The whole subsystem** | **A larger context window and a better reasoning model** | Genuinely competitive and possibly winning. Supersede: full context beats bounded self-managed memory by **15 points** on knowledge-update, and more memory capacity recovers **nothing**. MAB v4: GPT-5-mini scores 78 single-hop FactConsolidation with no memory layer. This proposal is only interesting at 10⁵–10⁶ pages, where the corpus does not fit. B6 is in the experiment to keep that honest. |

**The one-sentence summary of this table:** every component of this design has a non-biological alternative that is at least as good at the job, and the fly's contribution is not any of the algorithms but three structural properties that the incumbents happen not to have — *readout as a necessary condition for promotion*, *forgetting as its own suppressible process*, and *conflicting claims kept in separately-decaying compartments rather than resolved*. K4 exists to test whether those three properties are worth anything once implemented.

---

## 11. Two-week MVP

**Day 0 (before any code) — run K5.** Join `pages.last_retrieved_at` / `retrieval_bouts` × `synthesis_evidence` × a labelled answer set on any brain with ≥30 days of history; compute AUROC for "readout predicts cited-in-a-correct-answer". **< 0.60 → stop and publish the negative result.** One day, no LLM spend, and it tests the load-bearing assumption of the strongest idea in the fly inventory.

**Week 1 — L0 + L1, behind a default-off switch**
- D1 — L0: migration v147 (2 columns, index, backfill), the one-statement change in `src/core/last-retrieved.ts`, and the `readout_signal_liveness` doctor check.
- D2–D3 — L1: `lifecycle.promotion_gate` enum in `consolidate.ts`; union bucket scan; singleton promotion under the readout path; newest-open-interval claim selection; per-run budget. Unit tests pinning that `duplication` reproduces v0.48.5.0 behaviour exactly.
- D4 — `lifecycle_events` audit table + a cycle-report section the nightly report cannot filter out (#4622's lesson).
- D5 — replicate #3042 on a seeded store: confirm 62 buckets → 0 promotions under `duplication`, and record the number under `readout`. This is the first real before/after.

**Week 2 — L2 + L3 + the first measurement**
- D6–D7 — L2: `gbrain lifecycle forget --dry-run` (acquisition-rate budget, suppression not deletion, reset-on-recall, `open_loops` and judge-failure suppression windows), plus the one-line `effectiveConfidence` hook. **Also fix `HALFLIFE_DAYS` — either rename it `TIME_CONSTANT_DAYS` or multiply the table by `1/ln2` — and pin the choice in the existing tests.**
- D8–D9 — L3: `claim_evidence` + `net()` + the ledger in `entity`/`recall` MCP responses, with signs mapped from `eval_contradictions_cache`. PE gating and the optional judge deferred.
- D10 — harness: write `Evaluation/eval_gbrain.py` against MemConflict's existing runner interface; run B0/B1/B4/B5 on the **804 static+conditional** questions plus 500 sampled `dynamic`. ~$30 and one afternoon, per g06's Tier-0 costing.

**Deliverable at day 10:** a pre-registered result on 1,304 questions with per-stratum McNemar and Wilson CIs, the K5 AUROC, a cold-tier-yield before/after against #3042's measured zero, and a first read on K4 — whether the fly-derived arm beats the TinyLFU/CREW/SQL:2011 arm at all.

---

## 12. What this does not do, and will not

- **It does not touch the content store.** The fly has no provenance, no authorship, no propositional content and no notion of a query; the mushroom body throws the episode away and keeps a scalar. Every mechanism here operates on the *metadata layer* — when to promote, when to demote, how to score a disputed claim — and none of it improves what a page says.
- **It does not arbitrate.** L3 returns a net and a ledger. It never returns "claim A is correct." A company brain usually needs a decision, and that decision is still made by the reader.
- **It does not know what a question is.** Fly promotion, forgetting and extinction operate on recency, valence and interference. Relevance-to-a-query is bolted on from outside (the readout term), is derived from no biology, and is the weakest joint in the design.
- **It does not fix retrieval.** g02's arithmetic settles that branch: the pgvector HNSW scan is ~4.5 ms inside a ~3,272 ms answered question. Nothing here changes an index.
- **It does not survive if `last_retrieved_at` turns out to be noise.** That is K5, and it is day zero for a reason.

---

## Sources

**GBrain source, all read at commit `43597b19e50a3abf56409337f248f7966860293c` (v0.48.5.0) via `raw.githubusercontent.com` during this session**
- `src/core/facts/decay.ts` — `HALFLIFE_DAYS`, `effectiveConfidence`, the `~0.368` comment — https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/core/facts/decay.ts
- `src/core/cycle/phases/consolidate.ts` — bucket SQL, `minFactsPerBucket ?? 3`, `clusterThreshold ?? 0.85`, `cluster.length < 2`, chronological `valid_until` writeback — .../src/core/cycle/phases/consolidate.ts
- `src/core/last-retrieved.ts` — op-layer-only write-back, 5-minute throttle, `search.track_retrieval`, fire-and-forget drain — .../src/core/last-retrieved.ts
- `src/schema.sql` — `pages` DDL (`emotional_weight`, `deleted_at`, `last_retrieved_at` at :126, `links_extracted_at`), `pages_last_retrieved_at_idx` (:270–276), `bump_page_generation_fn()` allow-list (:163–188), `context_volunteer_events` (:753–773), `open_loops` (:856–891)
- `src/core/migrate.ts` — `takes` DDL (~:1271) and `synthesis_evidence`; `facts` DDL (~:2384)
- `src/core/cycle.ts` — `ALL_PHASES` (23 entries, :108)
- Issues, fetched via `gh api` today: **#3042** (consolidate structurally zero-yield; 62 buckets → 0 promotions; cosine tops out at 0.844), **#3824** (two independent ≥2 gates; singletons never promote), **#4057** (buckets >100 facts skip forever), **#3269** (take_proposals write-only; 32.5k rows growing 2–6k/day), **#4696** (forget undone by the next `extract_facts` reconcile; fixed at this commit)

**Fly neuroscience (primary)**
- Huang C., Luo J., Woo S.J., Roitman L.A., Li J., Pieribone V.A., Kannan M., Vasan G., Schnitzer M.J. (2024) "Dopamine-mediated interactions between short- and long-term memory dynamics," *Nature* 634:1141–1149 — https://doi.org/10.1038/s41586-024-07819-w (PMC11525173)
- Felsenberg J. et al. (2018) "Integration of Parallel Opposing Memories Underlies Memory Extinction," *Cell* 175:709–722 — https://doi.org/10.1016/j.cell.2018.08.021 (PMC6198041)
- Shuai Y., Lu B., Hu Y., Wang L., Sun K., Zhong Y. (2010) *Cell* 140:579–589 — https://doi.org/10.1016/j.cell.2009.12.044
- Berry J.A., Cervantes-Sandoval I., Nicholas E.P., Davis R.L. (2012) *Neuron* 74:530–542 — https://doi.org/10.1016/j.neuron.2012.04.007
- Cervantes-Sandoval I., Chakraborty M., MacMullen C., Davis R.L. (2016) *Neuron* 90:1230–1242 — https://doi.org/10.1016/j.neuron.2016.05.010
- Berry J.A., Cervantes-Sandoval I., Chakraborty M., Davis R.L. (2015) "Sleep facilitates memory by blocking dopamine neuron-mediated forgetting," *Cell* 161:1656–1667 — https://doi.org/10.1016/j.cell.2015.05.027
- Gkanias E., McCurdy L.Y., Nitabach M.N., Webb B. (2022) *eLife* 11:e75611 — https://doi.org/10.7554/eLife.75611 · code https://github.com/InsectRobotics/IncentiveCircuit (GPL-3.0)
- Bennett J.E.M., Philippides A., Nowotny T. (2021) *Nat. Commun.* 12:2569 — https://doi.org/10.1038/s41467-021-22592-4 · code https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb
- Aso Y. et al. (2014) *eLife* 3:e04577 — https://doi.org/10.7554/eLife.04577
- Xie K. & Ocker G.K. (2025) arXiv:2509.19351 — https://arxiv.org/abs/2509.19351 (pruning degrades learning capacity)

**Benchmarks and negative results**
- MemConflict — https://github.com/TaoZhen1110/MemConflict (arXiv:2605.20926); released set measured by g06 today: 30 instances / 3,750 questions / 2,946 dynamic / 444 conditional / 360 static; `Evaluation/diagnose_failures.py`
- LongMemEval — https://github.com/xiaowu0162/LongMemEval (LongMemEval-S, 470 scored, knowledge-update n=78)
- MemoryAgentBench FactConsolidation — https://arxiv.org/abs/2507.05257 (v3 results table; v4 2026-06-28 GPT-5-mini 78 SH / 28 MH with no memory system)
- MemStrata — https://arxiv.org/abs/2606.26511 (AUROC 0.59; superseded-serving 15–40% → ~0%; evolving-knowledge 0.20–0.47 → 0.95–1.00)
- Supersede — https://arxiv.org/abs/2606.27472 (full context 92% vs bounded self-managed memory 77% on knowledge-update; capacity 28% → 28%)
- ConflictRAG / CARS — https://arxiv.org/html/2605.17301v1 (CARS diagnostic only; best published CRS 0.2501 in MemConflict)
- SAGE — https://arxiv.org/pdf/2605.30711 · https://github.com/swang1024/SAGE (Apache-2.0; vMF novelty gate, 3.4× add-phase cost reduction)
- W-TinyLFU — Einziger G., Friedman R., Manes B., "TinyLFU: A Highly Efficient Cache Admission Policy," *ACM Trans. Storage* 13(4), 2017 — https://doi.org/10.1145/3149371
- SQL:2011 temporal features — Kulkarni K. & Michels J.-E., *SIGMOD Record* 41(3):34–43 (2012)

**Prior reports in this corpus relied on** — `findings/g07-neuro-mechanism-inventory.md` (mechanism algorithms, fidelity rubric, negative results), `findings/g02-sizing-cost.md` (chunks/page 2.40, $0.0009/judge-call correction, latency budget, $/seat curve), `findings/g04-librarian-spec.md` (CREW rate law, OAIS disposal schedule, `last_retrieved_at` misuse), `findings/g01-bitemporal-prior-art.md` (SQL:2011 `WITHOUT OVERLAPS`, the supersession/contradiction/debate table), `findings/g06-crux-experiment.md` (arms, power table, MemConflict measurement, pre-registration discipline), `findings/v06a-librarian-in-code.md` and `findings/v06b-librarian-skeptic.md` (phase-by-phase write audit, D17 doctrine), `findings/v09a`/`v09b-memoryagentbench*.md` (the +2.0 pp deterministic-operator ablation; deterministic rules vs LLM judges), `findings/memory-hygiene.md`, `findings/mushroom-body-memory-models.md`.

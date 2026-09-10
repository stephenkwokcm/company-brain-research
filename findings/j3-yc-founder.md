# j3 — Judge: the YC founder

**Key:** `j3-yc-founder` · judging panel, angle 3 · 2026-09-10 · author: research worker (Claude Opus 5)

**Persona and standing assumptions.** I am a YC founder building a company-brain product. I have **two engineers and twelve weeks of runway**. That is 2 × 60 = 120 engineer-days gross; after product work, demos, support and the things that break, **~70 engineer-days are actually available for infrastructure**. I care about exactly two outcomes: does answer quality go up in a way a design partner notices, and does the bill go down. I do not care about publishable negative results, biological fidelity, or unclaimed ground except insofar as it is a moat I can reach inside twelve weeks.

**Scale I am judging against.** Not GBrain's 155,795 pages. A design-partner brain at week 12 is **10K–100K pages, 10–40 skills, 25 seats**. Where a design only pays at 10⁶ pages or 150+ skills, I say so and discount it — that is a different company's problem and I may not live to have it. This is the single largest divergence between my scores and the design panel's own framing, and it moves two designs down and one up.

**What I read:** `d1-write-gate`, `d2-lifecycle`, `d3-router`, `d4-index-adversary`, `d5-curation-process`, plus `g07-neuro-mechanism-inventory`, `g02-sizing-cost`, `v10b-flyhash-vs-modern`.

---

## 1. Scorecard

Each axis 1–10; total = sum (max 50).

| Design | Feas. | Benefit | Evidence | Novelty | Cost-eff. | **Total** | **Verdict** |
|---|---:|---:|---:|---:|---:|---:|---|
| **d2-lifecycle** | 8 | 8 | 8 | 4 | 9 | **37** | **BUILD** (L0+L1 after the day-0 K5; L2/L3 defer) |
| **d4-index-adversary** | 10 | 5 | 10 | 2 | 9 | **36** | **BUILD** (D4-ALT only — the FlyHash half is already **KILL**ed by its own criterion) |
| **d1-write-gate** | 8 | 6 | 7 | 6 | 8 | **35** | **PILOT** (ship the seam at `scorer: hybrid`; `fly-bank` stays off = **KILL** for this runway) |
| **d3-router** | 7 | 7 | 9 | 5 | 6 | **34** | **PILOT** (measure B10 + the pool curve first; build stage 1 only if the in-context arm loses) |
| **d5-curation-process** | 5 | 4 | 8 | 7 | 4 | **28** | **DEFER** (cherry-pick B9 + B3 + B7 = 3 days; B1/B2 wait for a deal that requires them) |

**Rank: d2 > d4 > d1 > d3 > d5.**

---

## 2. Per-design verdicts

### d2-lifecycle — 37 — **BUILD**

**Rationale.** This is the only design whose core defect bites at *my* scale, and the evidence for that is a closed issue in the reference implementation: gbrain#3042 measured one `dream --phase consolidate` run processing **62 buckets and promoting 0 facts into 0 takes** on a store of ~360 unconsolidated facts across ~138 entities — that is a seed-stage brain, not a million-page one, and its promotion subsystem yields literally zero because every ≥3-fact bucket tops out at cosine 0.844 under a 0.85 threshold. Meanwhile #3269 has the human-gated queue at **32,500 rows growing 2–6k/day**. The cost of fixing it is the best in the panel: **$0–11/month** of marginal AI spend against a takes-extraction line of ~$70–96/month (`g02`: $0.0128/page actual on the $361.49 / 28,256-page receipt), because every mechanism is deterministic SQL. And the customer-visible metric — superseded-serving, predicted **−8 to −20 pp absolute**, anchored on MemStrata taking evolving-knowledge accuracy from 0.20–0.47 to 0.95–1.00 — is exactly the failure a design partner reports as "your brain told me last quarter's price."

**Scoring notes.** Benefit 8 not 10 because the author pre-registers his own modal outcome as a **pooled null** (+0 to +3 pp) and predicts L1 alone is "≈0, possibly negative" on answer accuracy — I am buying the hygiene metrics, not the headline. Novelty 4 because K4 is likely to fire: an arm of W-TinyLFU admission + a CREW acquisition-rate weeder + SQL:2011 `WITHOUT OVERLAPS`, containing zero fly content, is expected to tie, and the author says so. Cost-efficiency 9 because **K5 costs one day and no LLM budget** and can kill the largest piece before any code: join `last_retrieved_at`/`retrieval_bouts` against `synthesis_evidence` and compute AUROC for "readout predicts cited-in-a-correct-answer"; below 0.60, L1 is dead. I will take a one-day option on a 15.5-day build every time.

**What I build:** L0 (0.5 d) + L1 (2 d) + the `HALFLIFE_DAYS` fix. **What I defer:** L2 (the forgetting daemon — 4 days, and the piece most likely to silently suppress the one compliance fact nobody reads) and L3 (5 days, and it should follow g01's bitemporal constraint, not precede it).

**One free bug this report found and I am shipping in week 1:** `src/core/facts/decay.ts`'s `HALFLIFE_DAYS` is a time constant τ, not a half-life — at age = τ confidence is 0.368, not 0.5, so every kind decays **1.44× faster than its name claims**. Anyone calibrating retention against those defaults is calibrating against a 44% error. One line.

---

### d4-index-adversary — 36 — **BUILD** (the alternative only)

**Rationale.** The FlyHash/BioHash backend is dead and the report killed it properly: a pre-registered three-gate criterion that fired on **every** configuration in a sweep of ρ ∈ {10,20,40} × f ∈ {12,102,205} × k ∈ {16…1024} plus a trained BioHash at two widths. At equal database bytes `binary_quantize` → `bit(1024)` scores 0.7577 raw / **0.9918** after rescoring at **136 B/row**, against FlyHash's 0.4948 / 0.8339 at **528 B/row**; the parity configuration (k=1024, 8,653 B/row) is refused outright — `ERROR: sparsevec cannot have more than 1000 non-zero elements for hnsw index`. I need that question closed and it is closed, in-database, on pgvector 0.8.6.

What I actually build is **D4-ALT**: one expression index plus a two-stage rescore query, **3–5 dev-days**, measured 13,726 → 609 B/row total (**22.5×**), HNSW p50 7.34 → 3.81 ms (**1.9×**), at 99.2% recall@10.

**Scoring notes.** Evidence 10 — this is the most rigorous report in the panel, first-party in a live database with `EXPLAIN ANALYZE`, and its 8,144 B/row index measurement independently reproduces `g02`'s 8,192 B/vec to within 0.6%. Feasibility 10 — it is a documented pgvector recipe with upstream tests, not a bespoke access path I maintain forever. Benefit only 5, and this is where I depart from the report's enthusiasm: **at my scale it saves almost nothing.** The $410 → $110 Supabase delta is a 1M-page number; at 100K pages the index is under a gigabyte and I am on the minimum tier either way. The author is candid — "a *storage and latency* win, not a *quality* win," and by `g02`'s budget the ANN scan is **0.14% of a 3,272 ms answered question.** I build it because it is four days and it removes a scaling cliff before I hit it, not because it moves a metric this quarter. Novelty 2, and deservedly: the only novel thing here is the negative result.

---

### d1-write-gate — 35 — **PILOT** (seam yes, fly no)

**Rationale.** The seam is right and the biology is optional, and the author says so himself: "ship the seam, default `scorer: hybrid`… run `fly-bank` as one pluggable arm behind a flag with K2 as its pre-registered death sentence," at a stated **~40%** confidence on the recurrence task and **~20% overall**. I will take the seam and skip the arm. The seam's two payoffs are real: **15–20% of write-path LLM calls avoided** (anchored on SAGE's measured "roughly 16–18% of LLM calls across five models with minimal quality change," Apache-2.0 and already published in this exact slot), and a **write-time contradiction trigger** that reaches a set GBrain's probe structurally cannot — its own pipeline says "Date pre-filter: skip pairs whose dates are >30d apart," which discards precisely the quarterly-clock supersessions (pricing, org, policy) that a company actually has. That trigger costs **$0.68/month at 250 writes/day** and breaks even at **0.7% of writes suppressed**.

**Scoring notes.** Benefit 6, not higher, because the absolute dollars at my scale are small — the report's own net is **+$7 to +$19/month saved** against $96/month of curation — and because *every* economic number in §7 scales linearly with the near-duplicate rate of real company ingest, which the author flags as **unmeasured by anyone**. Evidence 7: the PNAS derivations (L1–L4) are checkable arithmetic and I checked the shape of them, but L5 is the author's own analysis replacing the paper's capacity rule, L6's multiplicative separability is an assumption the source paper explicitly calls poorly understood, and the filter has never been run on text at any n above 5,000. Cost-efficiency 8: the seam is ~4 days, the full plan 11, experimental spend under $150.

**Why the fly half is KILL for me, not DEFER.** `d4` §5.4 moved the bar and d1 has not answered it: on paraphrase-shaped dedup the **free ANN probe you have already paid for scores 0.843**, its 136-byte binarized shadow 0.834, and FlyHash at a byte-competitive k=64 scores **0.800**. To *tie* the free baseline the fly code needs k=1024 — 8,208 B/vec and unindexable. A four-day experiment whose best case is "we matched free" is not a use of 6% of my runway. I will implement `on_duplicate: route`, never `block` — that part is non-negotiable and correct.

---

### d3-router — 34 — **PILOT** (measure first; build stage 1 only if the measurement says so)

**Rationale.** Best measurement in the panel, most contingent proposal. The measurements are excellent and two of them are load-bearing corrections: `gbrain routing-eval` scores **303/303 = 100.0%**, and under leave-one-trigger-out — delete only the phrases each intent literally contains — it scores **0/271 = 0.0%**, with **24 intents silently misrouting to a different skill**. So the project has *no signal at all* on routing under paraphrase, which is the only condition that occurs in production. And the recomputation of GBrain's own resolver A/B on STRICT (exact slug) inverts its published LENIENT headline: baseline 81.7/86.7/73.3 vs compressed 63.3/60.0/53.3 — compression costs 18–27 pp for anything that must emit one slug.

**Why only PILOT.** Three discounts, in order of size.

1. **The headline cost collapses under prompt caching.** The $528/month at 150 skills and $1,077 at 306 are the *uncached* columns; the manifest is the same every turn, so it caches, and the cached lines are $52.80 and $107.71 against a router-only $13.20. My real saving is **~$40–95/month**, not $515.
2. **The report's own numbers do not clearly show the router beating the model.** §1.4 puts the model-in-context at **81.7% (Opus) / 86.7% (Sonnet) STRICT**; §1.5's pilot puts the dense nearest-centroid at **0.734 at K=73**. Different corpora and different fixtures, so not a clean comparison — but K3 sets the bar at "+5 pp over the full manifest in context," and nothing in this report suggests it will clear it. The author is honest that the pool-size curve for the *in-context* arm has never been measured by anyone; that is the experiment, and it is week 1, not the build.
3. **It bites at 100+ skills and I will have 10–40.** Trigger-blind top-1 is 0.931 at K=5 and 0.883 at K=10; the collapse to 0.685 is a 150-skill extrapolation. This is a real problem *later*.

Plus **B10**: Anthropic ships `tool_search_tool_bm25_20251119` with `defer_loading: true`, which is the same idea at the platform layer. **One day to test whether the platform already gives me 80% of this for zero engineering**, and I am running that day before anything else in this design.

**Scoring notes.** Evidence 9 (first-party, and the author ran the experiment that killed his own assigned angle — REAR −1.1 pp, FlyHash −1.4 to −5.9 pp against a no-training centroid, with oracle λ chosen generously in the losers' favour). Feasibility 7 and cost-efficiency 6 because I cannot evaluate this without first *building a benchmark* (RouteBench-150: 600 paraphrases + 150 near-miss negatives + 120 ambiguity cases, 3 days) — real work before the first bit of signal.

---

### d5-curation-process — 28 — **DEFER** (cherry-pick three items; shelve the keystone)

**Rationale.** The report pre-registers a null on both metrics I am judged on: "**unlikely** to move pooled retrieval accuracy," with K4 committing to say so in those words, and its own one-paragraph pitch conceding the modal outcome is "reproducibility, arbitrability and governance while moving pooled retrieval accuracy by nothing at all." That is a fair and admirable disclosure and it is also a decision. The keystone (B1: content-addressed `page_versions` + `page_lineage` + W3C-selector `fact_anchors`) is quoted at **6–8 weeks** for production hardening — more than half my runway on both engineers — and its whole architecture rests on *manufacturing* an immutable substrate that a company brain does not naturally have, where CAVE got one free from an EM volume that cannot change.

**Scoring notes.** Evidence 8 (CAVE in *Nature Methods*, read in full; as-of measured at 525 → 978 → 1,385 ms, i.e. **1.9–2.6×**, not an order of magnitude; ~2 TB and 1.8 B annotations at ~$500/month) — the connectome community publishes what things cost, which no memory vendor does. Novelty 7: the CAVE triple (immutable anchor + lineage graph + time-resolved identity) genuinely has no standard equivalent, and nobody has mapped connectome curation practice onto agent memory. But novelty I cannot reach in twelve weeks is not a moat, and the author concedes item by item that W3C Web Annotation, SQL:2011, OBO Foundry and PROV-O each specify their piece better.

**Three items I take anyway, three days total** — see §4.

---

## 3. What I am not building, stated once

| Killed | By what |
|---|---|
| FlyHash/BioHash as `vector.backend` | d4's K1–K3 fired on every configuration; 2.4× the bytes, 2.2× the latency, index refusal at the fly's own sparsity |
| FlyHash as the dedup hash | d4 §5.4: free ANN probe 0.843, binarized shadow 0.834, FlyHash k=64 **0.800** |
| Lexical SimHash as the dedup incumbent | d4 §5.4 corrects `v10b`: **0.263** on paraphrase-shaped edits. Good for byte-identical copies, useless for "the same fact written differently" |
| The two-compartment `fly-bank` gate | Author's own ~20% overall confidence; the surviving claim (recurrence-after-dormancy) is testable with `max cosine` + a `last_seen_at` SQL predicate for zero new machinery |
| REAR / FlyPrompt / k-WTA routing | d3's own pilot: loses to a no-training centroid at every pool size in the honest condition |
| Connectome topology as any kind of prior | arXiv:2604.04033 — the advantage vanishes under a degree-preserving null |
| d5's B1 anchors + B2 as-of materialisation | 6–8 weeks; revisit when an enterprise deal requires it |

---

## 4. Best ideas to graft from lower-ranked designs into the winner

The winner is **d2-lifecycle**. These are the transplants, ranked by value per engineer-day.

1. **The free-baseline rule, from d4 §5.4 (and d1 §11).** Before any novelty, dedup or staleness machinery, the arm to beat is `1 − max cosine` from one HNSW probe already paid for: **0.843** on paraphrase dedup, at 3.78 ms @100K. Every gate d2 adds gets benchmarked against that arm first, and most of them will not clear it. This one rule saves more engineering than anything else in the panel.

2. **d1's write-time contradiction trigger, with d2's scorer.** GBrain's probe is query-sampled *and* discards every pair >30 days apart. Trigger the probe at write time on "similar at the month scale, dissimilar at the week scale" — but compute that band with max-cosine plus a `last_seen_at` SQL predicate, not a two-compartment Bloom filter. **$0.68/month at 250 writes/day**, break-even at 0.7% of writes suppressed. This is the single highest-value graft: it reaches the supersession class d2's L1/L2 cannot see and that the shipped probe filters out by construction.

3. **d1's hook location and its routing doctrine.** `src/core/import-file.ts:756`, immediately after the `#1309` cross-slug dedup pre-check and before chunking/embedding; **`on_duplicate: route`, never `block`.** d1's own concession applies to d2 directly: L3's prediction-error write gate "is dedup with a neuroscience name," and an ingest-time gate does it better and earlier. Move that work upstream.

4. **d4's D4-ALT as a parallel four-day sidecar.** `CREATE INDEX … USING hnsw ((binary_quantize(embedding)::bit(1024)) bit_hamming_ops)` plus a two-stage rescore: 22.5× storage, 1.9× latency, 0.9918 recall@10. Orthogonal to everything in d2, so the second engineer ships it in week 2 while the first runs K5.

5. **d5's B9 — invert the merge automation.** ConnectomeBench (arXiv:2511.05542, NeurIPS 2025 D&B): LLMs reach **75–85%** on split-error correction and 52–82% on segment identification (chance 50% / 20–25%) but "generally struggle on merge error identification." GBrain's *only* automatic destructive operation is a slug-normalising merge at 50 pages/run. **Automate splits and identification; human-gate merges.** One day, and it is the only recommendation in the whole panel backed by a benchmark that measured exactly this decision.

6. **d5's B3 — two-tier status vocabulary with a build-breaking exhaustiveness assert.** `flyem-snapshot` ends its status map with `assert list(NEUPRINT_STATUSLABEL_TO_STATUS.keys()) == DEFAULT_BODY_STATUS_CATEGORIES`, so introducing an internal curation state without deciding how it publishes **fails the build**. ~20 lines. d2 adds `suppression` and `dormant_at`, which without this become the fourth and fifth undocumented curation flags in a system that already has `deleted_at`, `unverified`, `create_safety` and `sources.archived`.

7. **d5's B5 — confidence carried with its scale and producer; verified beats predicted.** `facts.confidence REAL DEFAULT 1.0` is currently compared across kinds, extractors and model versions as if commensurable, then multiplied by a decay factor. d2's netting function inherits that error unless the rows carry `confidence_scale` and `confidence_producer`, and VFB's policy — carry the source's own score unchanged, never normalise across studies, never hide a low-confidence item, a verified value always beats a predicted one — is four columns and a rule.

8. **d3's LOTO test, as a standing CI check on every eval I own.** Delete only the trigger phrases each fixture literally contains; 100% → 0%. Any benchmark whose fixtures were written against the mechanism under test is a tautology check. d2's arms get a template-blind stratum for the same reason, or its numbers mean nothing.

9. **d3's write-back pattern.** Log lifecycle and routing decisions as `facts` rows with `kind='event'` rather than a bespoke table: it inherits the 7-day event half-life, the facts→takes bridge and the audit trail for free, and it turns "evals are performance reviews" into a measured loop over real traffic. d2's `lifecycle_events` should be this.

10. **d5's B7 — the known-defects layer.** `corpus_defects(source_id, scope, valid_from, valid_until, reason)`, stamped onto any retrieval that intersects an open defect ("the Slack connector dropped threads 2026-03-01…03-14"). One day, and nothing in the stack does it.

11. **g01's SQL:2011 `PRIMARY KEY (key, period WITHOUT OVERLAPS)`, named independently by d1, d2 and d5 as strictly better than any scoring approach.** Adopt it *before* d2's L3 ledger, so the ledger becomes the constraint's escape hatch for the overlapping-interval, different-holder "debate" case rather than a competitor to it.

12. **d1's seed-and-model coupling discipline.** Any derived code stores `embedding_model`, `embedding_dim` and its seed on the state row and invalidates on change. Cheap; prevents a class of silent-garbage bug that no test catches.

---

## 5. The twelve-week plan I would actually run

**Week 1 — measurement only. Nothing is built. ~6 engineer-days, ~$0.**

| Who | Work | Kills |
|---|---|---|
| E1 | d2 **K5**: AUROC of `last_retrieved_at`/`retrieval_bouts` for "cited in a correct answer" | <0.60 kills L1 |
| E1 | d5 day 1–2 audit: orphan `entity_slug` rate; human-adjudicate 100 sampled automatic merges | K1, K5 |
| E2 | d3 **B10**: does `tool_search_tool_bm25_20251119` + `defer_loading` already deliver the context cut? | Possibly all of d3 |
| E2 | Measure the near-duplicate rate on one week of real ingest | Sizes every d1 dollar figure |
| E2 | d4 reproduction on a real `content_chunks` export | Confirms D4-ALT before building |

**Weeks 2–3 — bank the certain wins. ~14 engineer-days.**
E2: D4-ALT (4–5 d) → d5 B9 merge inversion (1 d) → B3 status vocabulary + CI assert (1 d) → B7 defects layer (1 d).
E1: d2 L0 readout ledger (0.5 d) → L1 promotion gate (2 d) → the `HALFLIFE_DAYS` fix → replicate #3042 on a seeded store and record the cold-tier yield before/after.

**Weeks 4–6 — the quality lever. ~16 engineer-days.**
E1: g01's bitemporal constraint, then d2 L3 as its escape hatch, with d5's `confidence_scale`/`confidence_producer` columns folded in.
E2: d1's seam at `import-file.ts:756` with `scorer: hybrid` (SimHash for byte-near-identical, max-cosine for distance), routing not blocking; wire the duplicate band to skip the triage judge and `takes` extraction; wire the recurrence band to the contradiction probe at write time. Measure LLM calls avoided per 1,000 writes against the 15–20% prediction.

**Weeks 7–9 — the risky piece, default-off. ~12 engineer-days.**
E1: d2 L2 as `gbrain lifecycle forget --dry-run`, budget slaved to the acquisition rate, suppression-not-deletion, reset-on-recall, suppression windows on open loops and on judge failure. Never prune while the sensors are broken — #3889 is a run where every judge call failed, the probe reported "0 contradictions," and doctor showed `[OK]`.
E2: d3 stage 1 **only if** B10 failed *and* the skill count is past ~60. Otherwise E2 builds the trigger-blind routing stratum and measures the in-context arm's pool curve, which is the missing number.

**Weeks 10–12 — adjudicate. ~10 engineer-days, ~$30–150 of API.**
Run the 804-question MemConflict static+conditional slice plus a 500-question dynamic sample, one-switch ablations, paired McNemar with Wilson CIs. Score the 200-question stale-serve audit against the week-1 baseline. Publish the trial log including the failures.

**Total ≈ 58 engineer-days of the ~70 available.** The 12 in reserve are for the thing that breaks.

**The one number I am steering by:** superseded-serving rate on the 200-question audit, week 1 vs week 12. If it does not fall, none of this mattered and I will say so.

---

## 6. Residual uncertainty and where I could be wrong

- **My biggest divergence from the panel is the scale discount**, and it is a judgement call, not a measurement. If my design partner turns out to be a 500-person company with a 300-skill agent, d3 moves to first place and d4's hosting case becomes real. I would re-run this scorecard at that point rather than defend it.
- **d2 could well be a null.** Its author says so. My defence is that its *hygiene* metrics (cold-tier yield from a measured zero; superseded-serving) are the ones a design partner reports, and they cost $0–11/month to move. If K5 comes back under 0.60, the plan above loses its week-2 E1 track and I would promote d1's seam into that slot.
- **I did not verify any of the underlying primary sources myself.** Every number in this scorecard is quoted from the five design reports and from `g02`/`g07`/`v10b`, which state their own provenance (pinned SHA `43597b19…`, live pgvector 0.8.6 measurements, PDFs read directly). Where two reports disagreed I said so in the text — notably d4 §5.4 correcting `v10b`'s "SimHash is the dedup incumbent," and d3 §1.4 correcting `context-engineering-skills.md`'s LENIENT-only table.
- **The prompt-caching discount on d3 is my arithmetic, not the report's**, and it assumes the skill manifest is stable across turns within a session. If the product varies the manifest per turn — which is exactly what tiering does — caching breaks and d3's uncached column is the right one. That single assumption is worth ~$475/month and it decides whether d3 is fourth or first.

---

## Sources

**Design reports judged (all in `/Users/stephen/Cookies/company-brain-research/findings/`)**
- `d1-write-gate.md` — flygate seam; L1–L6 derivations; SAGE 16–18% LLM-call reduction; $0.68/mo probe cost; 0.7% break-even; K1–K7; `on_duplicate: route`
- `d2-lifecycle.md` — gbrain#3042 (62 buckets → 0 promotions), #3824, #4057, #3269 (32.5k rows, 2–6k/day), #3889, #4622 (324 facts hard-deleted silently); `HALFLIFE_DAYS` is τ not t½; K4/K5; $0–11/mo
- `d3-router.md` — 303/303 → 0/271 LOTO with 24 misroutes; STRICT vs LENIENT recomputation (81.7/86.7/73.3 vs 63.3/60.0/53.3); pool curve 0.931@K=5 → 0.734@K=73; REAR −1.1 pp, FlyHash −1.4 to −5.9 pp; context bill $256.96/$528.00/$1,077.12 uncached vs $25.70/$52.80/$107.71 cached; B10 tool search
- `d4-index-adversary.md` — K1–K3 all failed; `bit(1024)` 0.7577/0.9918 @136 B vs FlyHash k=64 0.4948/0.8339 @528 B; `ERROR: sparsevec cannot have more than 1000 non-zero elements for hnsw index`; 13,726 → 609 B/row, 7.34 → 3.81 ms; dedup table (free ANN probe 0.843, bit 0.834, FlyHash k64 0.800, lexical SimHash 0.590 / 0.263 heavy)
- `d5-curation-process.md` — CAVE (*Nature Methods* 22:1112, 2025): 1.8 B annotations, >4 M edits, 525/978/1,385 ms as-of, ~$500/mo; `flyem-snapshot` exhaustiveness assert; VFB confidence and deprecation policies; ConnectomeBench arXiv:2511.05542; B1–B9; K1–K5

**Supporting reports read**
- `g02-sizing-cost.md` — 2.40 chunks/page measured; HNSW 3.78 ms @100K / 10.73 ms @250K; ANN = 0.14% of a 3,272 ms answered question; $0.0128/page takes vs $0.0000576/page embed (222×–4,514×); $88.74/mo AI at 10 pages/person/day; $135/mo hosting at 155,795 pages; Supabase Large $110 / 2XL $410
- `g07-neuro-mechanism-inventory.md` — fidelity rubric (Deep / Analogy / Superficial); fly Bloom filter is the only Deep mechanism, δ/ε undetermined, largest n = 5,000, never tested on text; FlyPrompt's REAR is a dense Gaussian with no k-WTA
- `v10b-flyhash-vs-modern.md` — role-by-role verdict; H3D numbers; the ~30% prior on the fly gate beating the free baseline

**Judging inputs on the record**
- `checkpoints/01-sweep-decisions.md` — decisions (i)–(iv), of which (i)'s dedup half, (iii) entirely, and the index framing in (b) are now refuted by d3/d4

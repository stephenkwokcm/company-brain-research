# j1 — Judge scorecard: the RAG/search engineer's verdict on d1–d5

**Key:** `j1-rag-engineer` · judging phase · 2026-09-10 · author: research worker (Claude Opus 5)
**Persona I am judging as:** a senior RAG/search engineer who has shipped hybrid retrieval at 10M-document
scale, and who does not fund a biological metaphor unless it beats SPLADE, `binary_quantize`, or a cron job
on a number someone actually measured.
**Inputs read in full:** `d1-write-gate.md`, `d2-lifecycle.md`, `d3-router.md`, `d4-index-adversary.md`,
`d5-curation-process.md`, `g07-neuro-mechanism-inventory.md`, `g02-sizing-cost.md`, `v10b-flyhash-vs-modern.md`.

---

## 0. The bar I am applying

Three tests, applied identically to all five. They are the tests I would apply to a vendor pitch.

1. **Does it beat the free thing?** In this stack the free things are: an HNSW probe you have already paid
   for (`g02`: 3.78 ms @100K, 10.73 ms @250K), `binary_quantize()` (one SQL expression, 136 B/row,
   0.9918 recall@10 with rescore — `d4` §5.1), `SELECT … WHERE last_retrieved_at < NOW() - INTERVAL '90 days'`
   (the column exists and is B-tree indexed at `src/schema.sql:275`), and SQL:2011 `WITHOUT OVERLAPS` (`g01`).
2. **Is the number it moves a number anyone sees?** `g02`'s latency budget is the ruler: the ANN scan is
   **0.14% of a ~3,272 ms answered question**, and write-side LLM curation is **222×–4,514×** embedding
   cost. An intervention on the index is an intervention on the free part.
3. **Did the author try to kill it before asking me to fund it?** Two of the five did, with pre-registered
   criteria, and one of those two published a failure. That is worth more to me than any predicted effect size.

**Headline finding across the panel.** Every design that measured its own fly component reported that the fly
component lost, and every design's real value turned out to be the non-biological seam it opened while looking.
That is not a criticism of the panel — it is the panel working. The four sockets are now empirically closed
(index: `d4` §5.1/§5.3; dedup: `d4` §5.4 + `v10b`; routing: `d3` §1.5; ranking: `d3` §1.5), and the two that
remain open — write-side *recurrence-after-dormancy* (`d1`) and *abstention* (`d3` stage 2) — are open only
because nobody has run the experiment, not because anyone has evidence they work.

---

## 1. Scorecard

Scale 1–10 per axis, total = sum (max 50). Axis definitions I used:

- **feasibility** — can this be built as specified, in the stated days, against the stated seam, by one engineer.
- **expected_benefit** — the size of the number it moves, discounted by the author's own stated probability.
- **evidence_quality** — primary sources, first-party measurement, pre-registration, honest negative results.
- **novelty** — genuinely unclaimed ground, *after* the incumbent census.
- **cost_efficiency** — payoff ÷ (dev-days + API spend + ongoing maintenance surface).

| Design | Feas | Benefit | Evidence | Novelty | Cost-eff | **Total** | **Verdict** |
|---|---:|---:|---:|---:|---:|---:|---|
| **d3-router** | 9 | 8 | 9 | 6 | 9 | **41** | **BUILD** |
| **d4-index-adversary** | 9 | 6 | 10 | 5 | 9 | **39** | **BUILD** (D4-ALT only; fly backend correctly self-killed) |
| **d1-write-gate** | 8 | 5 | 9 | 8 | 8 | **38** | **PILOT** |
| **d2-lifecycle** | 8 | 7 | 9 | 5 | 8 | **37** | **BUILD** (L0+L1 only, gated on K5) |
| **d5-curation-process** | 6 | 6 | 8 | 6 | 6 | **32** | **PILOT** (cheap borrows only; defer B1/B2) |

**Ranking:** d3-router → d4-index-adversary → d1-write-gate → d2-lifecycle → d5-curation-process.

Note that rank and verdict deliberately disagree in two places, and both disagreements are load-bearing:
**d2 ranks 4th but earns a BUILD**, because its L0+L1 subset (2.5 days) is the highest-value-per-day item in
the entire panel; and **d1 ranks 3rd but earns only a PILOT**, because 11 days of its 11 rest on a mechanism
its own author gives 20–40% odds. Rank measures the quality of the report. Verdict measures what I would fund.

---

## 2. d3-router — **BUILD** · 41/50

| Axis | Score | Why |
|---|---:|---|
| Feasibility | **9** | ~15 person-days, ~250 LOC in one new module, hanging off an existing shared primitive (`loadSkillTriggerIndex()`), filling a hole the repo itself declares open: `src/core/routing-eval.ts` L15–20, *"Layer B (LLM tie-break) … **Not yet implemented in this release**; the CLI accepts the flag."* Two derived, rebuildable tables; no new dependency; reuses the turn embedding `gbrain search` already computes. PGLite works (brute force over 150 rows beats HNSW anyway). |
| Expected benefit | **8** | The largest measured money in the panel: **$514.80/month** at 150 skills, **$1,063.92/month** at 306, against `g02`'s **~$225/month all-in for the entire brain**. Predicted +10 to +25 pp top-1 and −85% to −95% always-on tokens. Discounted from 9 for B10 (below). |
| Evidence quality | **9** | Ran the assigned angle before proposing it and reported that it lost, against a kill criterion set *before* the run and honoured. Recomputed GBrain's own published resolver A/B from committed receipts and found the headline inverts. Caveats stated plainly (LSA-256 stand-in, n=271 over 55 of 73 skills, random distractors are optimistic, oracle λ chosen generously *for the arms that still lost*). |
| Novelty | **6** | Stage 1 is RAG-MCP (arXiv:2505.03275) applied to skills — explicitly not novel, and the author says so and recommends it on its merits anyway, which is the right call. RouteBench-150 (trigger-blind paraphrase routing over a 150-skill catalogue *with an abstention stratum*) is genuinely a benchmark nobody has. |
| Cost efficiency | **9** | Under **$200** of API spend for a 12-arm matrix, 15 person-days, against $500–$1,000/month of measured context bill. Roughly one-month payback at 150 skills uncached. Best ratio in the panel by a wide margin. |

**Rationale.** This is the only design where the boring incumbent does not already win: the shipped router is a
substring matcher that scores **303/303 = 100.0%** on its own fixtures and **0/271 = 0.0%** under
leave-one-trigger-out, with **24 of 271 silently misrouting to a different skill** — a benchmark that is a
tautology check, reproducing the exact disease `g06` flagged in `gbrain-evals` #24 in a second subsystem. The
collapse it is aimed at is measured first-party on GBrain's own 73 skills (trigger-blind top-1 **0.931 at K=5
→ 0.734 at K=73**, extrapolating to 0.685 at 150), and the fix is a dense nearest-prototype retriever with
published third-party numbers, not a fly. I am funding it because a cron job cannot do this and BM25 over
trigger text is already in the arm ladder as B3.

**Two conditions on the money, both of which the report half-concedes.**

1. **Run B10 on day 1, not day 11.** Anthropic ships `tool_search_tool_bm25_20251119` with `defer_loading: true`
   at the platform layer. If that gets 80% of the win for zero engineering, days 6–12 are a benchmark exercise
   and should be scoped as one. The report flags this in §10 and then schedules the arm eleventh; that ordering
   is backwards.
2. **The uncached column is doing too much work.** Prompt caching drops the 150-skill line from $528.00 to
   **$52.80**, and the report's defence — that "caching is exactly what a per-turn-varying manifest cannot rely
   on" — does not apply to the *current* static full manifest, which caches fine. The honest saving to underwrite
   is the **cached** delta ($52.80 → $13.20 ≈ $40/month at 150 skills, ~$95/month at 306), plus the accuracy
   gain. That is still worth 15 days; it is not a $500/month line item.

**Ship regardless of the router:** land the LOTO test in the repo as a `bun test`. A routing benchmark that
reports 100% and collapses to 0% under paraphrase is actively misleading to everyone downstream, and fixing
that is one day.

---

## 3. d4-index-adversary — **BUILD** (D4-ALT only) · 39/50

| Axis | Score | Why |
|---|---:|---|
| Feasibility | **9** | The fly backend is dead (below). D4-ALT is **3–5 dev-days**: one generated column, one index DDL, one two-stage query in `hybrid.ts`, one `knobsHash` fold, one doctor check. It is pgvector's own documented recipe with upstream tests, which means the maintenance surface is *someone else's*. |
| Expected benefit | **6** | Measured **22.5× total storage** (13,726 → 609 B/row) and **1.9× latency** (7.34 → 3.81 ms p50) at **99.2% recall@10** with rescore. At 1M pages that is 32.94 GB → 1.46 GB, i.e. a Supabase 2XL ($410/mo) → Large ($110/mo). But at GBrain's actual 373,908 chunks it is 5.13 → 0.23 GB and maybe $25/month, and the report concedes it "cannot move an answered question by more than ~0.1%." A hosting-tier win, honestly labelled as one. |
| Evidence quality | **10** | The best measurements in the panel and the only ones that closed a question four prior reports flagged as never run by anyone. FlyHash *and* BioHash computed on real 1,024-d bge-m3 embeddings, scored against `binary_quantize` on the same embeddings in the same pgvector 0.8.6 instance. K1–K3 pre-registered; all three fired. Noise floor established from two seeds (±0.01); margins 5–35× that. Cross-checked its own 8,144 B/row HNSW measurement against `g02`'s 8,192 to within **0.6%**. |
| Novelty | **5** | D4-ALT is deliberately claimed ground — *"S6 unclaimed ground: **No — and that is the point.**"* The novelty is entirely in the measurement: the empty H3D cell (embedding → FlyHash) is now filled, in both directions. |
| Cost efficiency | **9** | Two days of falsification already spent, and it bought a permanent close on the most-proposed bridge in this project. Then 3–5 days for a 22.5× storage reduction with no re-embed. |

**Rationale.** This report did the thing the whole corpus had been arguing about instead of running, and its
pre-registered kill criterion fired on **every** configuration in a sweep over ρ ∈ {10,20,40}, f ∈ {12,102,205},
k ∈ {16…1024}, three normalisations and a trained BioHash: at equal database bytes, sign binarization beats
FlyHash by **+53% relative recall@10** (0.7577 vs 0.4948) and **+19 points after rescoring** (0.9918 vs 0.8339);
the FlyHash column is **2.4× larger and 2.2× slower** than `bit(1024)`; and the only config that reaches parity
is refused by the server verbatim — `ERROR: sparsevec cannot have more than 1000 non-zero elements for hnsw index`.
Claim S3 (the fly lifts pgvector's 2,000-dim cap) **inverts**: it introduces a *tighter* 1,000-nnz cap that binds
at exactly the fly's own 5% sparsity, while `binary_quantize` indexes to 64,000 dims.

**What earns the extra point, and it is not the kill.** The report also *exonerates* the fly literature while
killing the proposal: at equal **hash length** FlyHash beats random-hyperplane LSH by **+82% relative**
(0.4948 vs 0.2712) — the *Science* 2017 result replicates on modern text embeddings, apparently for the first
time — and billing that as a storage win is a category error, because a "hash length" of 64 is 64 fifteen-bit
indices ≈ 960 bits against LSH's 64. Any future citation of "16.0% → 44.8% mAP" in this project must carry
*"at equal hash length"* or it misstates the finding. Two other durable contributions: the porting fact that with
constant fan-in, per-stimulus mean-centring is a **WTA no-op** on L2-normalised embeddings (so one of the three
published departures from LSH is inert here — it produced *bit-identical* results), and the correction to
`v10b` that lexical SimHash is **not** the dedup incumbent for a company brain (0.263 top-1 on paraphrase-shaped
edits vs the free ANN probe's 0.843).

**Verdict mechanics.** BUILD = D4-ALT, at low priority, after d3 and d2's L0+L1. Its real deliverable is the
published negative result, which should go into the repo as a doc PR the way GBrain published its
multi-query-expansion failure. **KILL** `vector.backend=flyhash` permanently; I concur with the report's request
that the judging phase treat any future FlyHash-under-`vector.backend` proposal as refuted rather than open.

---

## 4. d1-write-gate — **PILOT** · 38/50

| Axis | Score | Why |
|---|---:|---|
| Feasibility | **8** | The best-specified build in the panel: exact hook at `import-file.ts:756` (after the `#1309` cross-slug dedup pre-check, before chunking), migration v147, `db_only` state, config keys following the repo's own `dream.drift.enabled` convention, default OFF. The lazy-update trick is correct and makes read *and* write **O(k) independent of m** — weights only gain ε while inactive and the clip at 1 is monotone, so the lazy read is exact. 1.05 MB of state per source, constant forever. |
| Expected benefit | **5** | Author's own honest numbers: **+$7 to +$19 saved, −$0.68 spent** per month at 250 writes/day, break-even at **0.7%** of writes suppressed. Against `g02`'s $88.74/month AI line, $19/month is not a business case. The benefit that matters is architectural (a cheap write-time trigger for expensive judging), and that survives with `scorer: max-cosine`. |
| Evidence quality | **9** | Read the PNAS PDF directly and quoted Eq. 2 verbatim rather than paraphrasing. Closed `g07`'s single biggest caveat ("δ and ε are free parameters with no data-derived values") with two checkable closed forms. Seven pre-registered kill criteria, with K2 as a genuine death sentence runnable in **4 days for ~$0 with no GBrain code touched**. Flags L5 as its own analysis and L6 as an assumption the paper is *least* confident about. |
| Novelty | **8** | Highest in the panel. The two-compartment (γ/α) pair over one shared code is a direct answer to PNAS 2018's own Discussion item (ii), quoted verbatim — *"how can the fruit fly distinguish between two similar odors observed far apart in time vs. two dissimilar odors observed recently?"* — and Huang 2024 measured the answer six years later. **Content-level recurrence-after-dormancy is the one genuinely unoccupied cell** after `d4` and `v10b` closed the other four. |
| Cost efficiency | **8** | 11 dev-days, <$150 experimental spend, $0.68+$0.43/month in production. The stop-early structure is exemplary. Docked because the ceiling on the payoff is ~$19/month. |

**Rationale.** This is the most rigorous document in the panel and it is asking me to fund the weakest business
case. The derivation is real work — L2's closed forms (`1 − δ = m/(k·n)`, `ε = w*/n`) turn a hyperparameter
search into "choose the horizon in items," and L4's identity (**one duplicate insert ≡ `m/(k·r)` days of drift**)
is the precise, correct statement of why one filter cannot serve both a duplicate signal and a month-scale
staleness clock. But `d4` §5.4, which `d1` did not have, moves the goalposts against it again: on paraphrase-shaped
probes the free ANN probe scores **0.843** and `binary_quantize`'s 136-byte shadow **0.834**, while the indexable,
byte-competitive FlyHash config scores **0.800**. The distance axis is now measured, and the fly loses it.

**What I am funding: K2, and only K2.** Four days, ~200 lines, offline vectors, no GBrain integration —
`fly-bank` vs `fly-single` vs max-cosine vs SimHash vs SAGE, AUROC per gap G ∈ {7, 14, 25} days on a synthetic
recurrence corpus. The arms it must beat are structurally time-blind, so if a primitive with a clock cannot beat
primitives without one on a clock task, the branch closes for ~$0. **Add one arm the report omits:**
`binary_quantize`'s 136-byte shadow, per `d4` §5.4 — d1 benchmarks against raw max-cosine but not against the
cheap binarized version that scores within 0.009 of it, and at 136 B/row the entire probe table fits in cache.

**What I am funding regardless of K2:** the seam. Write-time novelty banding as a trigger for expensive judging,
with `on_duplicate: route` — never `block` — is worth building on its own merits, and the report says so
outright in §11. Its best single insight has nothing to do with the fly: GBrain's contradiction probe is
query-sampled *and* discards every pair more than 30 days apart (`docs/contradictions.md`: *"Date pre-filter:
skip pairs whose dates are >30d apart"*), which is most real supersessions in a company. That hole is real
whether or not a fly filter finds it.

**One gap the report does not flag.** The gate scores an embedding of **title + first 2 KB** (`SCAN_HEAD_BYTES`),
but the corpus is chunked at 300 words with 2.40 chunks/page (`g02`). A page whose novelty lives past the head
slice is invisible to the gate. That is a real coverage hole in the band policy and it needs a measurement, not
a paragraph.

---

## 5. d2-lifecycle — **BUILD** (L0+L1 only) · 37/50

| Axis | Score | Why |
|---|---:|---|
| Feasibility | **8** | 15.5 engineer-days total, but **L0 is 0.5 days and L1 is 2 days**, both deterministic and zero-LLM. The critical detail is verified rather than assumed: `bump_page_generation_fn()` (`src/schema.sql:163–188`) bumps the cache-invalidation clock only on an explicit column allow-list that excludes `last_retrieved_at`, so incrementing a bout counter on every search does **not** invalidate the query cache. That one check is the difference between a half-day and a two-week fight. |
| Expected benefit | **7** | Highest *measured* defect in the panel. `gbrain#3042`: one `consolidate` run processed **62 buckets and promoted 0 facts into 0 takes**, because every bucket clearing the ≥3 gate tops out at cosine **0.844** against a 0.85 threshold. `#3824`: singletons — "most captured facts" — never consolidate. `#3269`: the human-gated queue is at **32,500 rows growing 2–6k/day**. Predicted cold-tier yield 0 → 3–15 per 1,000 active facts/night; superseded-serving −8 to −20 pp. |
| Evidence quality | **9** | Every file fetched at a pinned SHA; the bucket SQL quoted verbatim; four issues pulled live via `gh api`. Found a real bug nobody had reported: `HALFLIFE_DAYS` is a time constant τ, not a half-life — the file's own comment concedes it (*"returns ~0.368"* = e⁻¹) — so **every kind decays 1.44× faster than its name claims** and anyone calibrating against those defaults is calibrating against a 44% error. Pre-registers a pooled null as the modal outcome. |
| Novelty | **5** | The author concedes all three mechanisms are **Analogy** under `g07`'s rubric and that W-TinyLFU (Einziger 2017), CREW's acquisition-rate law and SQL:2011 `WITHOUT OVERLAPS` each do the job better. What is left is three properties incumbents lack: the **AND** between write-evidence and read-evidence, the **refractory window**, and forgetting as a **second suppressible channel**. Real, but small. |
| Cost efficiency | **8** | **$0–$11/month** marginal AI spend against a ~$70/month takes line — the rare intervention that improves the expensive path without spending on it, which is exactly the shape `g02` says to look for (curation is 222×–4,514× embedding cost). K5 costs one day and no LLM budget and can kill the largest piece before any code. |

**Rationale.** Fixing a subsystem that is *measured at literally zero output* is the highest-value-per-day work
available, and L0+L1 is 2.5 days of it. But I am funding the fix, not the framing: the report's own **K4**
pre-commits that if arm B5 (W-TinyLFU + CREW + SQL:2011, **zero fly content**) ties B4 within 1.0 pp, the
write-up must say *"we implemented a cache admission policy, a retention schedule and a temporal constraint;
three literatures had it first."* The author expects that tie (*"abs(Δ) < 1 pp — I expect a tie"*) and so do I.
Ship it as TinyLFU-with-a-refractory-window and cite Huang 2024 as motivation, which §10 already recommends.

**Run K5 before writing any code.** One day, no spend: join `pages.last_retrieved_at` / `retrieval_bouts`
against `synthesis_evidence` and a labelled answer set, and compute the AUROC of the readout signal for
predicting "this page's fact was cited in a correct answer." Below 0.60, L1 dies and the correct output is a
clean negative result on the strongest architectural idea in `g07`'s inventory. The report's own risk #1 is that
`last_retrieved_at` is bumped by any search that *surfaces* a page including wrong hits, so a page surfaced 20
times and never used is indistinguishable from one surfaced 20 times and always cited. That is the most likely
reason this fails and it is measurable for free.

**Defer L2 and L3** (9 of the 15.5 days). L2 is the piece most likely to be rejected upstream on GBrain's D17
doctrine (*"archive is product judgment, not maintenance"*), and `#4622` — an accidental hard-delete of **324
facts across 41 pages** that completed silently because the warning landed in a filtered report — is the
precedent that will be cited against it. L3 is explicitly the escape hatch for `g01`'s bitemporal constraint and
the report says adopting it *without* the constraint would be a mistake; so adopt `g01` first and revisit.

**Land the `HALFLIFE_DAYS` fix this week, independent of everything else.** Rename it `TIME_CONSTANT_DAYS` or
multiply the table by `1/ln2` and pin the choice in the existing tests. It is a one-line correctness fix that
four consumers and `d3`'s routing-event decay all inherit.

---

## 6. d5-curation-process — **PILOT** (cheap borrows only) · 32/50

| Axis | Score | Why |
|---|---:|---|
| Feasibility | **6** | Split badly. B3 (status vocabulary + CI assert), B7 (defects layer), B8 (`match_mode`) and B9 (merge inversion) are ≤2 days each and genuinely trivial. B1 (bound anchors + lineage over a manufactured immutable substrate) and B2 (materialised versions + CAVE's delta path) are, by the author's own estimate, **6–8 weeks** to production. And §6 argues against §3: *"the standard wins on mechanism. Build `g01`'s bitemporal tables; do **not** reimplement a materialisation service."* A design that recommends against half its own build plan cannot score higher here. |
| Expected benefit | **6** | Pre-registers that this buys reproducibility, arbitrability and governance and moves pooled retrieval accuracy by **nothing** (K4). Undersold in one place, though: B1 is the *precondition* for `g01`'s `WITHOUT OVERLAPS` constraint, which **both `d1` and `d2` concede is the strictly better arbitration answer** than anything either of them proposes — `g01`'s constraint is only as good as its key, and today the key is a mutable `TEXT` the cycle itself rewrites. |
| Evidence quality | **8** | Excellent primary sourcing: CAVE full text from PMC12074985, `flyem-snapshot` source read directly, VFB's deprecation policy, the FlyWire annotation schema, ConnectomeBench. Real measured numbers carried across: as-of query costs **1.9×–2.6×** (525 → 978 → 1,385 ms), CAVE runs ~2 TB / 1.8B annotations at **~$500/month** with a ~$360 floor. Flags its own motivated reasoning explicitly. Docked because the WebSearch budget was exhausted before the task started, so the novelty check is inherited at other workers' confidence. |
| Novelty | **6** | Fly-biology content rated **Zero** by the author — *"not superficial — zero"* — which is the correct and honest call. As process transfer it is Deep but low-novelty: W3C Web Annotation, SQL:2011, OBO Foundry, PROV-O and LakeFS/Dolt each do a piece better, item by item in §6. The one genuine gap is CAVE's immutable-anchor + lineage + time-resolved-identity triple: bitemporal SQL versions a row but **cannot re-key annotations across a merge**. |
| Cost efficiency | **6** | **Zero LLM tokens per page**, which against `g02`'s 222×–4,514× curation-vs-embedding ratio makes it free by comparison; storage +$10–40/month. But 10 days to MVP and 6–8 weeks for the keystone, for a pre-registered pooled null. The cheap subset is a 9; the expensive subset is a 4. |

**Rationale.** The strongest single item in this report is the one nobody else in the panel produced: **B9**.
ConnectomeBench (arXiv:2511.05542, NeurIPS 2025 D&B) measures LLMs at **75–85% on split-error correction**
(chance 50%) and **52–82% on segment identification** (chance 20–25%) while *"generally struggling on merge
error identification"* — and GBrain's **only** automatic destructive operation is a slug-normalising **merge**
capped at 50 pages/run. The one operation it automates is the one the only published benchmark says models are
worst at. That is a one-day inversion backed by the only benchmark in the entire panel that measured exactly the
decision in question, and it is a safety fix rather than an optimisation. Fund it this week.

**Second-strongest, and also cheap:** B4 (`gbrain release` with a defined denominator). `v05` documents 220,000
claimed on stage, 146,646 in the README the same day, 155,795 from 2026-08-12, and 28,256 and 17,888 elsewhere.
Those numbers disagree because nobody ever cut a release with a stated denominator. `flyem-snapshot`'s
one-line vocabulary-drift gate — `assert list(NEUPRINT_STATUSLABEL_TO_STATUS.keys()) == DEFAULT_BODY_STATUS_CATEGORIES`
— is the cheapest useful idea in the panel and it is ~20 lines.

**What I am not funding yet.** B1 and B2, until the day-1/day-2 audits run (K1: if measured anchor/slug breakage
over 30 days of real traffic is **<2%** of facts, ship `page_lineage` alone for one day and stop; K5: if sampled
merge error rate is **<5%**, skip B9 too). B2 should be replaced outright by `g01`'s SQL:2011 tables, per the
report's own §6. And the substrate asymmetry in risk #1 is the real threat: CAVE's guarantees are all downstream
of an **immutable EM volume**, and a company brain has to manufacture one out of `page_versions`. If that
manufacture fails, the whole stack degrades to ordinary bitemporal SQL — which `g01` already recommends and
which does not need this report.

---

## 7. Best ideas to graft from the lower-ranked designs into the winner

The winner (d3) is a skill dispatcher, so some grafts are into d3 specifically and some are into the combined
build plan it heads. Each is named with its source and why it is cheaper than re-deriving it.

**Into d3 directly:**

1. **d1's L2 closed forms, to un-block d3's `shadow` mode.** `d3` §12 names δ and ε as *"the largest unknown in
   the proposal"* and ships the abstention gate in `shadow` because no published value exists for any text
   domain. `d1` L2 derives both from a chosen horizon in items: `1 − δ = m/(k·n)`, `ε = w*/n`. Graft the
   derivation and d3's open question becomes a one-week calibration. Also graft **L4** — *one duplicate insert ≡
   `m/(k·r)` days of drift* — because it tells you immediately whether d3's single per-skill filter can see a
   duplicate at all at the horizon it picked, which is the failure mode d3 has no way to detect today.

2. **d1's `impossible`-corner self-check, as a `doctor` check on d3's `skill_novelty_filter`.** d3 persists a
   projection seed per skill and warns that losing it makes every stored code garbage — but ships no integrity
   check. d1's fourth corner (`n_γ` low + `n_α` high) is unrepresentable by construction, so its rate is a free
   corruption alarm: above ~1%, the state is corrupt, the seed changed, or the parameters violate the floor.
   ~10 lines, and it catches exactly the failure d3 §4 warns about.

3. **d1's `on_duplicate: route`, never `block` — applied to abstention.** d3's gate returns `ABSTAIN`, which
   *is* a block. Per `g05`'s OWASP ASI06 argument, a router gate is a **worse** denial surface than a write gate,
   because an adversary who can depress a skill's filter weights silently disables a capability rather than
   annotating a page. d3's `advisory` mode (router proposes, model disposes) should be the **default**, not the
   fallback after K4 fires.

4. **d4's binarized baseline, added to d3's abstention ladder.** d3's K2 comparators are B5 (max-cosine
   threshold) and B6 (logistic calibration). `d4` §5.4 measured the free ANN probe at **0.843** and
   `binary_quantize`'s **136-byte** shadow at **0.834** on paraphrase-shaped probes — within 0.009 of each
   other. At 136 B/prototype the whole 150-skill table is cache-resident, so the binarized shadow is the true
   floor the fly gate has to clear, and it is currently missing from the ladder.

5. **d5's B8 `match_mode`, surfaced on every routing decision.** d3's three-stage design (Layer A substring →
   stage 1 cosine → stage 3 LLM escalation) already *has* the information VFB's `resolve_entity` reports; it just
   throws it away and returns a bare slug. Return `{slug, match_mode ∈ {trigger, prototype, escalated, abstain},
   margin}` plus VFB's own warning to check before building on a non-exact match. Two lines, real safety value.

6. **d2's readout-bout ledger, in place of d3's decayed event count.** d3 §3.4 writes routing decisions to
   `facts` with `kind='event'` and inherits the 7-day half-life. d2's `retrieval_bouts` + `last_bout_at` with a
   24 h refractory window is a strictly better instrument for "is this skill actually used," and d2 already
   verified it does not invalidate the query cache. It is the same primitive, and it feeds d3's `kind='observed'`
   prototypes directly.

**Into the combined build plan:**

7. **d5's B9 — invert the merge policy — ship it this week.** The only recommendation in the panel backed by a
   benchmark that measured exactly the decision (ConnectomeBench: strong on splits and identification, poor on
   merges; GBrain auto-merges 50 pages/run). One day, safety, independent of everything else.

8. **d2's `HALFLIFE_DAYS` correction — land before anyone calibrates anything.** It is τ, not a half-life; four
   consumers and d3's routing-event decay all inherit a **1.44×** error. One line plus a test pin.

9. **d4's WTA-no-op porting fact — delete the dead normalisation from both d1 and d3.** With constant fan-in,
   `M(x − c·1) = Mx − c·f·1` is a uniform shift, so winner-take-all is invariant and d4's "raw" and
   "per-vector-centred" arms produced *bit-identical* results. d1's `divisiveNormalise()` and d3's
   `k-WTA(M·(q − mean(q)))` are both inert on L2-normalised embeddings. Not a bug, but keeping them is a false
   claim of fidelity to the fly's concentration-invariance mechanism.

10. **d1's write-time contradiction trigger, grafted onto d2's L3 ledger.** d2's `claim_evidence` table has no
    trigger of its own and reuses cached verdicts. d1's recurrence band is the cheapest trigger anyone proposed,
    and it targets a hole the shipped probe cannot reach: `docs/contradictions.md` discards every pair more than
    30 days apart, which is most real supersessions on a quarterly org clock.

11. **d3's pre-registration + receipt discipline, applied to every arm in the panel.** d3 is the only design
    that ran a benchmark and discovered the *benchmark* was the problem (100.0% → 0.0% under LOTO). Bind every
    run to `prompt_template_hash` / `fixtures_hash` / `harness_sha` as `evals/functional-area-resolver/` already
    does — that mechanism is what made d3's own README/receipt discrepancy findable at all.

---

## 8. What I would tell the orchestrator in one paragraph

Fund **d3's routing work** (15 days, but run the Anthropic tool-search arm on day 1 and underwrite the *cached*
saving, not the uncached one), **d2's L0+L1** (2.5 days, gated on a one-day K5 AUROC measurement, and shipped as
TinyLFU-with-a-refractory-window rather than as biology), **d5's B9 + B3 + B7 + B4** (~4 days of governance and
one evidence-backed safety inversion), and **d4's D4-ALT** (3–5 days, low priority, a hosting-tier win worth
~$25/month today and ~$300/month at 1M pages). Fund **d1 only as its own K2** — four days, offline, ~$0, no
GBrain code touched — and build its *seam* with `scorer: max-cosine` regardless of the outcome. Kill
`vector.backend=flyhash` permanently on d4's measurements. The honest summary of the whole panel for the
synthesis is this: **five designers went looking for the fruit fly in a company brain, four of the five sockets
came back measured and closed, and every design's real deliverable turned out to be the non-biological seam it
opened while looking** — a routing layer whose benchmark was a tautology, a promotion phase measured at zero
output, a contradiction probe that discards everything older than 30 days, an index that binary-quantizes 22.5×,
and a merge operation automated in exactly the direction the only relevant benchmark says not to.

---

## Sources

**Design reports judged** (all `/Users/stephen/Cookies/company-brain-research/findings/`)
- `d1-write-gate.md` — two-compartment fly Bloom filter at the ingest waist; L1–L6 derivations; K1–K7
- `d2-lifecycle.md` — readout-gated promotion, suppressible forgetting daemon, evidence ledger; K1–K6
- `d3-router.md` — measured skill dispatcher; K1 already run and failed; artifacts at `artifacts/d3-router/`
- `d4-index-adversary.md` — first-party FlyHash/BioHash vs `binary_quantize` measurement; K1–K3 all fired
- `d5-curation-process.md` — connectome curation practice as eight buildable borrows; K1–K5

**Evidence reports relied on for the bar**
- `g07-neuro-mechanism-inventory.md` — fidelity rubric (Deep / Analogy / Superficial); mechanism 2 is the only
  Deep-and-buildable one and has never been run on text; "what has no counterpart" (provenance, skillification,
  relevance-to-a-query); the doomfly negative result
- `g02-sizing-cost.md` — ANN scan = **0.14%** of a ~3,272 ms answered question; curation is **222×–4,514×**
  embedding cost; 2.40 chunks/page measured; $0.0128/page takes extraction; $88.74/month at 10 pages/person/day;
  Supabase tier table; the human librarian's cost is unpublished by everyone and is plausibly the dominant line
- `v10b-flyhash-vs-modern.md` — role-by-role verdict; H3D tables 5–8; SPLADE++ BEIR-13 50.5 vs BM25 43.7;
  DiskANN 1B points / 64 GB / <3 ms; the ~30% confidence figure on the novelty gate that d1 and d3 both adopt

**Primary sources cited in my own reasoning** (verified as quoted within the reports judged, not independently
re-fetched by me this session)
- Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093–13098 (2018), DOI 10.1073/pnas.1814448115 — Eq. 2,
  AIMD, and the Discussion item (ii) that d1's two-compartment design answers
- Dasgupta, Stevens & Navlakha, *Science* 358(6364):793–796 (2017), DOI 10.1126/science.aam9868
- Huang et al., *Nature* 634:1141–1149 (2024), DOI 10.1038/s41586-024-07819-w — γ/α compartment separation
- Brown, Kirjner, Vivekananthan & Boyden, "ConnectomeBench," arXiv:2511.05542 (NeurIPS 2025 D&B) — the merge/split
  asymmetry behind d5's B9
- Dorkenwald et al., "CAVE," *Nature Methods* 22:1112–1120 (2025), DOI 10.1038/s41592-024-02426-z — as-of latency
  1.9×–2.6×, ~$500/month at 2 TB
- Gan & Sun, "RAG-MCP," arXiv:2505.03275 — d3's stage-1 precedent
- Einziger, Friedman & Manes, "TinyLFU," *ACM TOS* 13(4) (2017), DOI 10.1145/3149371 — d2's K4 comparator
- pgvector README — `sparsevec` HNSW limit of 1,000 non-zero elements; `binary_quantize` to 64,000 dims;
  "no training step like IVFFlat"
- `garrytan/gbrain` @ `43597b19e50a3abf56409337f248f7966860293c` (v0.48.5.0) — `import-file.ts:727/756`,
  `schema.sql:163–188/275/302`, `consolidate.ts` bucket SQL, `facts/decay.ts` `HALFLIFE_DAYS`,
  `routing-eval.ts:15–20`, `docs/contradictions.md` 30-day pre-filter; issues #3042, #3269, #3824, #4622

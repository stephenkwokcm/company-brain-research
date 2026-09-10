# v01 — GBrain benchmark reconciliation (`+31.4 P@5` vs "hybrid layer is roughly neutral")

**Lens:** reconcile. **Date of fetch:** 2026-09-10. **Repo state at fetch:** `garrytan/gbrain` 29,764★ / 4,441 forks, default branch `master`, last push 2026-09-08, `VERSION` = `0.48.5.0`. `garrytan/gbrain-evals` 419★ / 77 forks, last push 2026-09-09.

**Verdict on the claim as put: CONFIRMED.** Both sentences are in the current `README.md`, verbatim, ~395 lines apart. They are not in factual contradiction — they measure **different layers of the stack, on different corpora, with different metrics**. But the reconciliation is not symmetric: the LongMemEval sentence is a live, receipted measurement, while **the `+31.4` headline is a stale April-2026 whole-system adapter gap that GBrain's own evaluation repo has since marked historical, flagged as having no surviving receipts, explicitly disowned as a graph-attribution claim, and re-measured at roughly half the size.** The README has not caught up.

---

## 1. The two sentences, located

Fetched `https://raw.githubusercontent.com/garrytan/gbrain/master/README.md` (76,781 bytes, 666 lines).

**Line 12** (the pitch bullet, "A self-wiring knowledge graph"):
> "Benchmarked: **P@5 49.1%, R@5 97.9%** on a 240-page Opus-generated rich-prose corpus, **+31.4 points P@5** over its graph-disabled variant and over ripgrep-BM25 + vector-only RAG by a similar margin."

**Line 379** (feature section) — the stronger and less defensible form:
> "The graph is what produces the +31.4 P@5 lift over vector-only RAG."

**Line 407** ("How it measures up"):
> "Pure vector on the same corpus scored 93.8% (v0.48.0.0 receipt), so the hybrid layer is roughly neutral on this benchmark and earns its keep elsewhere."

No erratum, "historical", or "upper bound" qualifier appears anywhere near lines 12 or 379. The only occurrences of "April" in the README are inside the worked example about a fictional person named Alice.

---

## 2. Number 1 — `+31.4 points P@5`: full provenance

| Field | Value |
|---|---|
| **Corpus** | `eval/data/world-v1/` — **240 fictional pages**: 80 people, 80 companies, 50 meetings, 30 concepts |
| **Corpus origin** | **LLM-generated.** "Claude Opus wrote the generated prose. Its historical one-time generation cost was approximately $3.14" (`eval/CREDITS.md`) |
| **Questions** | **145 relationship questions**, auto-generated from the corpus's own `_facts` metadata by `buildRelationalQueries()`; four templates only — *Who attended X? / Who works at X? / Who invested in X? / Who advises X?*; **261 gold items**. `_facts` and `gold` stripped at the adapter boundary |
| **Metric** | P@5 / R@5 **as computed by the pre-audit helper** — precision divided by *returned-list length, not k*, and recall able to double-count duplicate `page_id`s and exceed 1.0 |
| **GBrain versions** | v0.12.1 → **v0.20.0** (`96852c0`, PR #195 HEAD); evals at `b81373d` (Apr 19) / `8dab7f7` (Apr 23) |
| **Dates** | **2026-04-19** (N=5, seeded ingestion-order shuffles) and **2026-04-23** (N=1) — i.e. ~4.5 months and 28 minor versions before the current v0.48.5.0 |
| **Receipt** | **None.** Manifest entry `relational-recall`: `artifact_path: null`, `artifact_sha256: null`, `status: "disclosed-gap"` |

### What was actually compared

Per `eval/CREDITS.md`, the four adapters were all written **inside the project** ("not third-party implementations submitted by competing vendors"):

- `gbrain` — graph-first: template parser → typed-edge traversal → text fallback
- `vector-grep-rrf-fusion` — "**gbrain's hybrid search with graph traversal disabled**"
- `grep-only` — BM25 keyword baseline
- `vector` — vector-similarity baseline, same embedding model

April 2026 recorded scorecard (both reports, identical):

| Adapter | P@5 | R@5 | Correct in top-5 | Δ P@5 vs gbrain |
|---|---:|---:|---:|---:|
| **gbrain** | **49.1%** | **97.9%** | 248/261 | — |
| vector-grep-rrf-fusion (graph off) | 17.8% | 65.1% | 129/261 | **−31.4** |
| grep-only | 17.1% | 62.4% | 124/261 | −32.0 |
| vector | 10.8% | 40.7% | 78/261 | **−38.4** |

**So the README's line 379 is wrong on its own source data twice over.** `+31.4` is the gap to the *graph-disabled hybrid*, not to "vector-only RAG" — the vector-only gap is `+38.4`. And "the graph is what produces" it is precisely what both source reports deny.

### GBrain's own repo disowns the attribution — in five places

1. **2026-04-19 report:** "These are historical adapter comparisons… The **31.4-point precision difference cannot be attributed to the graph alone**."
2. **2026-04-23 report:** "The 31.4-point precision difference is an adapter comparison. It is **not a measured graph-only improvement**: extraction, query interpretation, retrieval, and result handling also differ."
3. **Circularity, disclosed:** "its query parser recognized the same four templates used by the question generator. That makes this a narrow test of those relationship paths." The receipts manifest repeats it: "The graph-template adapter also recognizes the same relationship templates used by the question generator." A template-blind paraphrase variant was proposed in **issue #24 and never run**.
4. **Version-sensitivity:** the companion 2026-04-19 v0.11-vs-v0.12 report shows the *same adapter on the same corpus* moving **22.1% → 49.1% P@5** on an extraction change alone, and states that at v0.11 gbrain led the hybrid reference by only **4.3 points**. The "31.4" is therefore a property of one tuned release, not of "having a graph".
5. **Receipts gap:** "The April reports cite output written to ignored `eval/reports/` and never copied into committed evidence; the original per-query rows are missing… **Fresh corrected runs do not recover or authenticate the historical percentages, and the adapter gap does not isolate the value of a graph database.**"

### The corrected re-run halves it

`docs/benchmarks/2026-09-09-retrieval-refresh.md` (2026-09-09, gbrain v0.48.4.0 pinned at `2efaaf8f…`, 3 ingestion orders, 793 adapter/question combinations × 3 = 2,379 scored queries, **fixed-denominator P@5**):

| Family | Adapter | Mean P@5 | Mean R@5 |
|---|---|---:|---:|
| Relationships | Specialized `gbrain` | **0.3421** | 0.9791 |
| Relationships | Reference hybrid (graph off) | 0.1917 | 0.6874 |
| Relationships | Keyword ranker | 0.1710 | 0.6244 |
| Relationships | Vector only | 0.1076 | 0.4069 |

→ corrected gap over the graph-disabled hybrid = **+15.0 points P@5** (not +31.4); over vector-only = **+23.5**. R@5 is essentially unchanged (97.9 → 97.91); the halving is the precision denominator being fixed from returned-list-length to k=5. The report's verdict: *"The specialized adapter's advantage is a comparison between whole systems. It does not establish that 'graph alone added 31 points.'"*

### The one clean isolation of the graph

Same report, "Production relationship retrieval: one switch" — **shared extracted index, identical query vectors, identical metadata settings, reranking/expansion/autocut/caching all off; only `search.relational_retrieval` toggled**:

| Template | n/seed | Rel. off R@5 | Rel. on R@5 | First-place hit, off → on |
|---|---:|---:|---:|---:|
| Who attended X? | 50 | 0.3800 | 0.3800 | 0.0000 → 0.0000 |
| Who works at X? | 40 | 0.8875 | 0.9250 | 0.1167 → 0.1167 |
| Who invested in X? | 39 | 0.6560 | 0.8462 | 0.2308 → 0.5385 |
| Who advises X? | 16 | 1.0000 | 1.0000 | 0.4375 → 0.5625 |
| **All 145** | 145 | **0.6626** | **0.7241** | **0.1425 → 0.2391** |

**+6.15 points R@5, +9.66 points first-place-hit rate. 45 of 435 question/seed pairs improved, none worsened.** Attendance gained nothing (the fixture stores `meeting → person`, production expects `person → meeting`). The report's own caveat: *"These are gains in finding the labeled pages, not measured gains in answer accuracy; no answering model was run for this cell."*

**That +6.2 / +9.7 is the honest "what the graph buys" number.** It is the only measurement in the corpus that changes one variable.

---

## 3. Number 2 — "hybrid layer is roughly neutral" / pure vector 93.8%

| Field | Value |
|---|---|
| **Corpus** | **LongMemEval-S**, cleaned Sept-2025 revision (`xiaowu0162/longmemeval` on HuggingFace) |
| **Corpus origin** | **Public third-party benchmark** (Wu et al., arXiv:2410.10813) — *not* LLM-generated by GBrain. This is the important asymmetry with Number 1 |
| **Size** | 500 questions; **470 scored** after dropping the 30 abstention questions, as the official scorer does |
| **Metric** | **strict session-level `recall_all@5`** — a question counts only if *every* gold session is in the top-5 distinct retrieved sessions. Retrieval only, no reader model. 300 of the 470 need ≥2 sessions; ceiling is 99.4% because 3 questions carry 6 gold sessions |
| **Versions/dates** | pure vector: **v0.48.0.0**; hybrid rows: v0.48.2.0 (2026-09-02) and **v0.48.4.0** (2026-09-06) |

Arms on this corpus:

| Arm | Strict `recall_all@5` | Version / date |
|---|---:|---|
| **Pure vector** | **93.8%** | v0.48.0.0 receipt |
| Hybrid, reranker off | 93.19% (438/470) | v0.48.2.0, 2026-09-02 |
| Hybrid, reranker off | 93.40% (439/470) | v0.48.4.0, 2026-09-06 |
| **Hybrid + Voyage `rerank-2.5`, autocut off (shipped default)** | **95.53% (449/470)** | v0.48.4.0, 2026-09-06 |
| Default *before* v0.48.4.0 (reranker on + autocut on) | 79.6% (379/470) | — |
| Legacy LLM multi-query expansion | 54.89% (258/470) | v0.48.2.0 |

So the fusion layer is **0.4–0.6 points behind pure vector**, and the **cross-encoder reranker supplies +2.13 points**. "Roughly neutral" is, if anything, generous to the hybrid layer.

### Provenance caveat on the 93.8% itself

The 93.8% is real but **thinly receipted, and its origin is a bug hunt, not a benchmark run.** The receipts manifest has 97 entries and commits a `.json` summary *and* per-question `.ndjson` for every LongMemEval arm — hybrid, hybrid+rerank, expansion, session-diversity, autocut, dev-slice budgets. **There is no vector-only arm.** The figure survives in exactly four places:

- `docs/benchmarks/2026-05-07-longmemeval-s.md` line 65: *"The v0.48.0.0 receipt reported 93.19% hybrid strict recall… That release also reported 93.8% for pure vector. The result supports fixing a harmful interaction between the keyword and vector lists; **it does not show that keyword search is always unnecessary**."*
- `src/core/types.ts:818`: *"LongMemEval receipt: hybrid `recall_all@5` 51.3% with them voting vs vector-only 93.8%"*
- `src/core/search/hybrid.ts:2116`: *"LongMemEval fresh-pin receipt: hybrid `recall_all@5` 51.3% vs vector-only 93.8%; per-question probe shows gold at vector ranks 0-2 sinking to fused ranks 14-17 under relaxed-arm votes"*
- `test/keyword-relaxed-fusion.serial.test.ts`

Context: the keyword arm's AND→OR zero-strict-recall fallback was flooding RRF with common-word matches at full voting weight, collapsing hybrid to **51.3%** against a vector-only control at **93.8%**. PR #4787 (v0.48.0.0) stopped relaxed rows voting when the vector arm is healthy. The 51.3% side *is* receipted (`longmemeval-prefix-bracket-v0.47.8.0`, 241/469 = 51.39%); its vector-only counterpart is not.

**Also note:** README line 407 sends the reader to `gbrain-evals docs/comparison-systems.md` for "the full table with sources". That table contains **no GBrain pure-vector row**. Its only "93.8%" is a *different system* — Lethe v1 (arXiv:2606.15903), any-hit-shaped R@5 over 500 questions with no abstention exclusion. A reader following the citation will find the right number attached to the wrong system.

### The neutrality result replicates across three more fixtures

All 2026-09-09, v0.48.4.0 — this is not a LongMemEval quirk:

- **Concept search, 181 held-out questions:** vector-only nDCG@5 **0.6054**, 118/181 exact-target-first — *beating* reference hybrid (0.5830, 102/181) and lexical-gated gbrain (0.5780, 102/181). Only adding the reranker wins: 0.6619, 130/181. *"Without reranking, vector search leads both hybrid configurations."*
- **Source-swamp, 30 questions:** *"Vector search alone led this fixture"* — vector 29/30 top-1 vs gbrain 27/30. The source-tier boost is worth exactly **+1** (26→27, one gain, no losses). *"it does not support a general claim that hybrid retrieval beats vectors."*
- **Externally authored questions (47):** vector-only P@5 0.2085 / R@5 0.8936, ahead of both hybrid (0.1957/0.8404) and keyword (0.1957/0.8511).

---

## 4. The one fair sentence

> **GBrain's graph layer buys a real but much smaller win than the README advertises — in the only clean A/B (one switch, shared index and query vectors) typed-edge retrieval adds +6.2 points R@5 and +9.7 points first-place-hit rate on 145 template-matched relationship questions over a 240-page Opus-generated corpus, and the corrected whole-adapter gap is +15.0 P@5 rather than the +31.4 the README still prints — while the BM25+vector fusion layer itself is neutral-to-negative against pure vector search (93.8% vector vs 93.19–93.40% hybrid strict `recall_all@5` on the public LongMemEval-S, with vector also leading GBrain's concept and source-swamp fixtures), and the cross-encoder reranker, not the graph and not the fusion, is what supplies the +2.1 points that reach the headline 95.53%.**

Shorter, for a synthesis body: *the graph pays on entity-relationship lookups (+6 to +10 points, isolated); the hybrid fusion layer pays nothing over pure vector; the reranker pays ~2 points. The "+31.4" is a superseded whole-system comparison, not a graph measurement.*

---

## 5. Has any third party reproduced either number?

**No — neither number has been independently re-executed by anyone outside the project.** Five external efforts exist and are worth distinguishing, because two of them *are* genuine reproductions of *other* GBrain numbers:

| Who | What they actually did | Reproduces `+31.4`? | Reproduces LongMemEval? |
|---|---|---|---|
| **Kevin-Liu-01/cotcodec** (2026-08-17) | Hash-pinned deterministic reproduction of the **BrainBench memory-conformance** suite at gbrain `d941e9f9…`: 146 tests / 725 assertions, 106 fixtures, 786 turn rows; matched the committed baseline exactly (know-to-ask 9/146, push precision 1.0 / recall 0.8085, write-back 1.0, continuity 1.0, zero cross-source injection) | ❌ different suite | ❌ |
| **taeyun16/aidememo** (2026-05-19/21) | Ran the real `gbrain-evals` multi-adapter harness on the same 240-page world-v1 corpus + 145 questions with their own engine: **17.4% P@5 / 64.1% R@5 (125/261)** BM25, 16.7%/62.5% hybrid | ⚠️ reproduces the **baseline band** (matches grep-only 17.1/62.4 and hybrid 17.8/65.1); never ran the `gbrain` adapter | ❌ |
| **pkyanam** — PR #6, GraphBrain (2026-05-03) | Neo4j drop-in adapter; claims 49.4% P@5 / 99.4% R@5 vs the gbrain **49.1/97.9 reference row copied from the repo** | ❌ **never merged** (open, unmerged as of 2026-09-10); vendor promotion for `graphbrain.belweave.ai`; its stated mechanism — "all gold answers are people, so push non-person pages down" — is a **gold-structure exploit that further impeaches the fixture** | ❌ |
| **peterkaminski** — issue #24 (2026-09-01, closed) | Outside review, **"static inspection… no code from the repo was executed"**. Graded machinery A−, published numbers C+. Independently flagged the missing erratum on the 49.1/97.9 report and that "the 'graph layer worth ~30 points' story rests partly on an **oracle-ish parser co-designed with the query generator**" | ❌ explicitly not a run | ❌ |
| **Loringtonian** — issues #26/#28 (2026-09-01, open) | Outside verification pass. Independently confirmed **the `recall_all@5` implementation and abstention handling match the official LongMemEval evaluator**, re-derived 83.40%/97.66% digit-for-digit from committed per-type data, recounted the Cat-35 corpus. Noted at the time that *"nobody outside your machine can re-derive 83.40% from the repo"* | ❌ | ⚠️ verified the **scorer and arithmetic**, not an independent execution |

`eval/CREDITS.md` states the position in the project's own words: *"There are no human external query contributors recorded here yet… The four current comparison adapters were implemented within this project… these are useful controls, but they are not third-party implementations submitted by competing vendors."*

**Confidence: high** that no third-party re-execution of either number exists. GitHub code search across non-`garrytan` repositories surfaced 125 hits for `"95.53" gbrain` and 148 for `BrainBench gbrain adapter`; all inspected hits were either forks/mirrors of GBrain's own docs (`cheRoma/gbrain-link-chat`, `weiping/gbrain-cn`, `AMC-JTC/gbrain-1`, `togorashi45/gbrain`), unrelated (`big-data-lab-team` BigBrain neuroimaging), or the five efforts tabulated above. *Caveat:* the session's WebSearch budget was exhausted before I could sweep non-GitHub venues (vendor blogs, arXiv, HN), so a third-party write-up published outside GitHub would not have been caught. GitHub is however where a reproduction of a Bun/TypeScript harness would land.

---

## 6. What this changes for the deliverable

1. **Retire "+31.4 P@5 over vector-only RAG" as evidence for anything.** Four prior reports in this corpus (`rag-taxonomy.md`, `talk-analysis.md`, `garry-tan-ecosystem.md`, `projects-built-on-ideas.md`) cite it as the quantitative proof that "brain > RAG". It is a superseded April-2026 whole-system adapter gap, measured with a since-corrected precision denominator, on an Opus-written corpus, with an answer-key-derived question generator sharing templates with the adapter's parser, with **no surviving per-query receipts**, and re-measured by its own authors at +15.0. Cite **+6.2 R@5 / +9.7 first-place** (the isolated switch) instead, or cite nothing.
2. **The two README sentences are not a contradiction, and the corpus should stop treating them as one.** Line 12 is *the graph, on synthetic entity-relationship questions*; line 407 is *the BM25+vector fusion layer, on public conversational memory*. Different layers, different corpora, different metrics. The synthesis should say so in one breath.
3. **The strongest honest claim for Tan's thesis is narrower and better than the one he makes.** Typed-edge traversal genuinely recovers relational evidence that similarity cannot reach (`invested_in` first-place hits 9/39 → 21/39, zero regressions across 435 pairs). That is a real, isolated, receipted finding. It is also a HippoRAG-adjacent claim, not a novel one — and it is a *retrieval* result with **no answering model in the loop**, so it still does not close the crux question (does curation improve downstream answer accuracy over a tuned baseline?).
4. **GBrain's evals repo is a credibility asset and its README is a liability.** The repo publishes failures (expansion −187 questions), errata, a `disclosed-gap` receipt status, an outside-review issue it acted on, and a re-run that halves its own headline. The README quotes best cells with qualifiers demoted — exactly the pattern peterkaminski named. Both facts belong in the answer: for question (c), `gbrain-evals` is the most decision-relevant artifact in the space *and* the reason to distrust the marketing copy above it.
5. **Corpus-origin asymmetry matters for question (a).** Skeptics were right that the graph win rides on LLM-generated fiction; defenders were right that the LongMemEval numbers are on a real public benchmark. Both halves are true and should be stated together — the neutrality result is the better-evidenced of the two.
6. **Unresolved, worth flagging as such:** no template-blind paraphrase variant of the relationship questions has ever been run (proposed in issue #24, April 2026, still not done). Until it is, even the +6.2/+9.7 is measured only on wording the parser was built to recognize.

---

## Sources

Primary, all fetched 2026-09-10.

**GBrain repo (`garrytan/gbrain`, master, v0.48.5.0)**
- README — https://raw.githubusercontent.com/garrytan/gbrain/master/README.md (lines 12, 379, 405, 407)
- `src/core/types.ts` line 818 — https://raw.githubusercontent.com/garrytan/gbrain/master/src/core/types.ts
- `src/core/search/hybrid.ts` line 2116 — https://raw.githubusercontent.com/garrytan/gbrain/master/src/core/search/hybrid.ts
- `test/keyword-relaxed-fusion.serial.test.ts` — https://raw.githubusercontent.com/garrytan/gbrain/master/test/keyword-relaxed-fusion.serial.test.ts
- `docs/eval/BRAINBENCH.md` — https://raw.githubusercontent.com/garrytan/gbrain/master/docs/eval/BRAINBENCH.md
- `docs/eval/SEARCH_MODE_METHODOLOGY.md` — https://raw.githubusercontent.com/garrytan/gbrain/master/docs/eval/SEARCH_MODE_METHODOLOGY.md
- `VERSION` — https://raw.githubusercontent.com/garrytan/gbrain/master/VERSION

**GBrain evals repo (`garrytan/gbrain-evals`, main)**
- README — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/README.md
- Receipts manifest (97 entries, `updated: 2026-09-09`; `relational-recall` = `disclosed-gap`) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/receipts-manifest.json
- 2026-04-19 multi-adapter report — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-04-19-brainbench-multi-adapter.md
- 2026-04-23 v0.20.0 report — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-04-23-brainbench-v0.20.0.md
- 2026-04-19 v0.11-vs-v0.12 report — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-04-19-brainbench-v0_11-vs-v0_12.md
- 2026-09-09 retrieval refresh (corrected runs) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-09-09-retrieval-refresh.md
- 2026-09-06 LongMemEval ranker wave — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-09-06-longmemeval-ranker-wave.md
- 2026-05-07 LongMemEval-S report (line 65: pure-vector 93.8%) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/benchmarks/2026-05-07-longmemeval-s.md
- 2026-08-31 eval audit (`shared-infra-02/03`, `orchestrators-09`, `generators-06`) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/audit/2026-08-31-eval-audit.md
- `docs/comparison-systems.md` (Lethe v1 = the other 93.8%) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/comparison-systems.md
- `docs/retrieval-lessons.md` — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/docs/retrieval-lessons.md
- `eval/CREDITS.md` — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/eval/CREDITS.md

**Third-party**
- Issue/PR #6, GraphBrain adapter (pkyanam, open/unmerged) — https://github.com/garrytan/gbrain-evals/issues/6
- Issue #24, outside review (peterkaminski, static only) — https://github.com/garrytan/gbrain-evals/issues/24
- Issue #26, outside verification pass (Loringtonian) — https://github.com/garrytan/gbrain-evals/issues/26
- Kevin-Liu-01/cotcodec conformance audit — https://raw.githubusercontent.com/Kevin-Liu-01/cotcodec/main/research/gbrain-brainbench-conformance-audit-2026-08-17.md
- taeyun16/aidememo BrainBench scorecards — https://raw.githubusercontent.com/taeyun16/aidememo/main/benchmarks/gbrain-evals-adapter/RESULTS.md
- pkyanam/graphbrain (4★) — https://github.com/pkyanam/graphbrain

**Upstream benchmarks referenced**
- LongMemEval — https://arxiv.org/abs/2410.10813 ; dataset https://huggingface.co/datasets/xiaowu0162/longmemeval
- Official retrieval evaluator (`recall_all` vs `recall_any`) — https://github.com/xiaowu0162/LongMemEval/blob/main/src/retrieval/eval_utils.py
- Lethe v1 (the other 93.8%) — https://arxiv.org/abs/2606.15903

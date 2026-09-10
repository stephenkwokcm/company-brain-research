# v09a — MemoryAgentBench / FactConsolidation: verification

**Key:** `v09a-memoryagentbench` · **Lens:** paper-reader · **Written:** 2026-09-10 · Research worker (Opus 5)

## Claim under test

> "On MemoryAgentBench `FactConsolidation`, all 22 published memory systems score at most 7% multi-hop
> and the best (HippoRAG-v2) 54% single-hop, while a deterministic Python `max(serial)` over BM25 hits
> 82–93% single-hop."
> (from `findings/neuro-inspired-rag.md`, used to support "contradiction arbitration is a database
> problem, not a latent-space problem")

## Verdict: **PARTIALLY CONFIRMED — every number checks out, the mechanism does not, and the paper itself refutes the strong reading**

The three numeric anchors (22 systems, ≤7 multi-hop, HippoRAG-v2 54, 82/93 single-hop) are all
literally correct against MemoryAgentBench **arXiv v3**. Three things are wrong or badly stated:

1. **`max(serial)` does not run over BM25 hits.** It runs over an **LLM-extracted candidate list**.
   The pipeline is BM25 top-10 → *an LLM call that extracts every semantically matching candidate* →
   `max(serial)`. The LLM still does all the semantic work.
2. **The deterministic operator earns ~nothing on accuracy.** Holding extraction and `T=0` fixed and
   swapping the policy executor from an LLM to Python `max()` is worth **+2.0 pp pooled and 0.0 pp at
   262K**. The v2 paper's own words: *"the freshness operator itself does not explain the full
   improvement."* The v1 title was "**Don't Ask the LLM to Track Freshness: A Deterministic Recipe**";
   the v2 retitle to "**Reliable Post-Retrieval Assembly … Separating Evidence Extraction from Policy
   Execution**" is the authors walking back exactly the claim we are repeating.
3. **"All 22 fail at ≤7% multi-hop" is already stale.** MAB **v4** (2026-06-28) adds GPT-5-mini
   (400K), which scores **78.0 FC-SH / 28.0 FC-MH** with no memory system, no retrieval and no
   arbitration code at all — beating the "deterministic" pipeline's gpt-4o-mini multi-hop (27) and
   nearly matching its single-hop (82).

---

## 1. The papers

| | MemoryAgentBench | The 82/93 result |
|---|---|---|
| Title | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions | v1: *Don't Ask the LLM to Track Freshness: A Deterministic Recipe for Memory Conflict Resolution*; v2: *Reliable Post-Retrieval Assembly for Agent Memory: Separating Evidence Extraction from Policy Execution* |
| Authors | Yuanzhe Hu, Yu Wang, Julian McAuley (UCSD) | Vikas Reddy (independent), Sumanth Reddy Challaram (IIT Kharagpur) |
| arXiv | [2507.05257](https://arxiv.org/abs/2507.05257) | [2606.01435](https://arxiv.org/abs/2606.01435) |
| Versions | v1 2025-07-07 · v2 2025-09-26 · **v3 2026-03-17** · **v4 2026-06-28** | **v1 2026-05-31** · **v2 2026-08-02** |
| Venue | **ICLR 2026** (accepted 2026-01-26) | **Lifelong Agent Workshop @ COLM 2026** |
| Code | [HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench), MIT, 449★ | [cvikasreddy/memory-conflict-resolution](https://github.com/cvikasreddy/memory-conflict-resolution), MIT, 0★ |

So: **yes, there are two releases.** Not a "2025 original + 2026 leaderboard" but a 2025 preprint that
became an ICLR 2026 paper, revised twice in 2026. There is **no public leaderboard**; the "leaderboard"
is Table 3 of the paper. The freshness paper pins itself to **v3** and says so explicitly.

## 2. What FactConsolidation actually tests

**Yes — versioned fact updates, in the easiest possible form.**

- Built from **MQUAKE counterfactual edit pairs** (Zhong et al. 2023). Each pair = one true fact + one
  rewritten contradictory version.
- **Every sentence gets an integer serial.** The outdated distractor gets the *smaller* serial, the
  current answer the *larger*; sentences are concatenated in serial order.
- Contexts at **6K / 32K / 64K / 262K**. **Table 3 reports the 262K cell only** (Table 2/6 lists
  FactConsolidation-SH/MH at 262K, 1 sequence : 100 QAs each → **n = 100 per cell**).
- Metric: **SubEM** (substring exact match).
- **FC-SH**: direct recall ("Which country was tool A created in?"). **FC-MH**: chained
  ("location of death of the spouse of person B").
- **The rule is handed to the agent verbatim in the prompt** (MAB v4 Appendix D, Figure 5):
  > "Each fact in the knowledge pool is provided with a serial number at the beginning, and the newer
  > fact has larger serial number. You need to solve the conflicts of facts in the knowledge pool by
  > finding the newest fact… give a very concise answer… **only** from the knowledge pool you have
  > memorized rather than the real facts in real world."
- The candidate set is tiny: the freshness paper's Appendix B notes FactConsolidation "generally caps
  the semantic candidate set at an **original and one counterfactual value**" — i.e. usually 2
  candidates. It "does not test selection over many candidates."

MAB's own Appendix G concedes the task is synthetic and defends it as a *controlled proxy*. Note a
mild internal inconsistency: Appendix G claims the competency is about "proactive removal of
non-essential information" and is *distinct* from knowledge updating — but the implementation is
overwrite-on-conflict knowledge updating. The repo README has since renamed the competency from
"Selective Forgetting (SF)" to **"Conflict Resolution (CR)"**, which is the honest name.

**Bottom line on task validity:** it is a total-order arbitration test with an oracle policy, explicit
integer metadata, and ~2 candidates. It is the *floor* of the arbitration problem, not a proxy for it.

## 3. Number-by-number verification

### 3a. "22 systems"

MAB **v3** Table 3 has exactly **22 rows**:

| Group | Rows |
|---|---|
| Long-Context Agents | GPT-4o, GPT-4o-mini, GPT-4.1-mini, Gemini-2.0-Flash, Claude-3.7-Sonnet (5) |
| Reference row | GPT-4o-mini repeated as the RAG backbone reference (1) |
| Simple RAG | BM25 (1) |
| Embedding RAG | Contriever, Text-Embed-3-Small, Text-Embed-3-Large, Qwen3-Embedding-4B (4) |
| Structure-Augmented RAG | RAPTOR, GraphRAG, MemoRAG, HippoRAG-v2, Mem0, Cognee, Zep (7) |
| Agentic Memory | Self-RAG, MemGPT, MIRIX, MIRIX (4.1-mini) (4) |

**"22 published memory systems" is a mischaracterisation.** 22 is a *row count*. It contains one
duplicate row and one duplicated system at a second backbone → **20 distinct entries, 19 distinct
systems.** Of those, **6 rows are plain long-context LLMs with no memory mechanism whatsoever**, 5 are
plain retrievers (BM25 + 4 embedding models), 3 are structured RAG (RAPTOR/GraphRAG/MemoRAG), and only
**7 are things anyone would call a memory system** (HippoRAG-v2, Mem0, Cognee, Zep, Self-RAG, MemGPT,
MIRIX). The freshness paper's own Appendix C dedupes to **20 published rows**.

MAB **v4** adds GPT-5-mini (400K) → **23 rows**. All other FC-SH/FC-MH values are byte-identical
between v3 and v4.

### 3b. FactConsolidation at 262K — the full v3 table (verified against both papers)

| System | FC-SH | FC-MH | | System | FC-SH | FC-MH |
|---|---:|---:|---|---|---:|---:|
| **GPT-5-mini (400K)** *(v4 only)* | **78** | **28** | | Cognee | 28 | 3 |
| GPT-4o long context | 60 | 5 | | MemGPT | 28 | 3 |
| **HippoRAG-v2** | **54** | 5 | | MemoRAG | 21 | **7** |
| BM25 | 48 | 3 | | MIRIX (4.1-mini) | 20 | 3 |
| GPT-4o-mini long context | 45 | 5 | | Self-RAG | 19 | 3 |
| Claude-3.7-Sonnet | 43 | 2 | | Contriever | 18 | **7** |
| GPT-4.1-mini | 36 | 5 | | Mem0 | 18 | 2 |
| Gemini-2.0-Flash | 30 | 3 | | RAPTOR | 14 | 1 |
| Qwen3-Embedding-4B | 29 | 3 | | GraphRAG / MIRIX | 14 | 2 |
| Text-Embed-3-Small/Large | 28 | 3 / 4 | | **Zep / Graphiti** | **7** | 3 |

- ✅ **"≤7% multi-hop across all 22"** — exactly right for v3. Max FC-MH = 7 (Contriever, MemoRAG).
  ❌ **Broken in v4**: GPT-5-mini = 28. MAB v4's own text now reads "all methods fail on the multi-hop
  situation (with achieving **at most 28%** accuracy)."
- ⚠️ **"the best (HippoRAG-v2) 54% single-hop"** — 54.0 is correct, but it is the best
  *retrieval/memory* result, not the best result. **GPT-4o long context = 60** in v3;
  **GPT-5-mini = 78** in v4. The freshness paper words this precisely ("the best reported
  *retrieval/memory* result"); our summary dropped the qualifier.
- ✅ Mem0 18, Zep/Graphiti 7, BM25 48 — all confirmed.

### 3c. The 82–93% pipeline

Reproduced from the released per-question JSON in the companion repo (not just the paper):

| Pipeline | Backbone | 6K | 32K | 64K | **262K** | Avg. [95% CI] |
|---|---|---:|---:|---:|---:|---|
| Direct LLM answer (T=0.7, MAB's own prompt) | gpt-4o-mini | 63 | 70 | 75 | **61** | 67.2 [62.5, 71.7] |
| Extract + **LLM** policy execution (T=0) | gpt-4o-mini | 70 | 75 | 77 | **82** | 76.0 [71.6, 79.9] |
| Extract + **deterministic `max(serial)`** (T=0) | gpt-4o-mini | 71 | 78 | 81 | **82** | **78.0** [73.7, 81.8] |
| Extract + deterministic, chunk-4096 | gpt-4o-mini | 87 | 84 | 79 | 73 | 80.8 |
| Extract + deterministic | gpt-4o | 99 | 92 | 95 | **93** | **94.8** [92.1, 96.5] |
| CAR (multi-hop) | gpt-4o-mini | 34 | 27 | 33 | **27** | 30.2 |
| CAR (multi-hop) | gpt-4o | — | — | — | **41** | 51.5 |

✅ **82 / 93 single-hop and 27 / 41 multi-hop at 262K are correct**, and I verified them against the
raw artifacts, not just the tables: `poc_results/paper_sh_conflict_factconsolidation_sh_262k.json`
reports `sh_correct: 82, n_questions: 100` and `bm25_correct: 61`;
`ablation_sh_fact_gpt4o_…_262k.json` reports 93; `ablation_mh_fact_gpt4omini_…_262k.json` reports 27.

## 4. What "max(serial)" actually is

From `scripts/_pipeline.py` (function `_freshness_pick`, labelled in its own trace output as
`"max(serial) — deterministic Python"`):

```python
def sh_conflict(question, corpus, bm25, llm):
    retrieved   = bm25.retrieve(question, top_k=10)   # rank_bm25.BM25Okapi, k1=1.5, b=0.75
    candidates  = llm_extract(question, retrieved)    # ← an LLM call: subject+predicate match,
    if not candidates:                                #   returns [{serial, fact_text, answer_entity}]
        return "no answer"
    return max(candidates, key=lambda c: c.serial).entity
```

So the deterministic step is `max()` over **1–3 LLM-extracted candidates**, not over 10 BM25 hits. The
paper is explicit that "the extractor is instructed to identify every semantically matching candidate
**without selecting a winner**." The alternative arm (`_llm_freshness_pick`, `PICKER_PROMPT`) gives the
same candidate list to an LLM told "select the candidate with the LARGEST serial."

**The head-to-head (v2 Appendix B, Table 7), on the 205 pooled observations where ≥2 candidates were
extracted:** deterministic correct on **196/205 (95.6%)** vs LLM **184/205 (89.8%)**,
a 5.9 pp contested-subset edge. **At 262K both are correct on 57 of 59 contested items and select the
same serial in all 59.** The gap does not grow with context length.

The repo README states this in its own voice:

> "the gain is **not** mainly from replacing the LLM with `max()`. Holding the extraction prompt and
> `T = 0` fixed and changing only the policy executor is worth 2.0 pp on average and **0 pp at 262K**.
> The large effect comes from restructuring the decision… Deterministic execution earns its place on
> **systems grounds** (a known policy becomes exact, inspectable, and independently testable), not on
> average accuracy."

Caveat on that ablation itself: the LLM-picker arm's **per-question JSON is not released** ("runner
released, JSON pending"), and extraction was re-run rather than shared byte-for-byte (96–100%
candidate agreement). It is the least independently checkable number in the paper — and it is the one
that most damages the claim we were repeating, which cuts *against* suspicion of motivated reporting.

## 5. Does this fairly support "arbitration is a database problem"?

**Not as stated. A weaker, differently-shaped claim survives.**

### What genuinely survives
- **Schema, not solver.** The paper's own design recommendation is a database recommendation:
  *"Version metadata should be preserved at the granularity at which conflicts occur… known policies
  should be represented independently of free-text generation."* Making the policy exact, loggable,
  auditable, testable and swappable (to second-newest, thresholded, aggregate) is a systems-engineering
  win that average accuracy does not measure. That much is real and is the right lesson for a company
  brain.
- **A structured post-retrieval interface matters more than the retriever.** With *identical* top-10
  retrieved evidence, restructuring the decision buys +10.8 pp pooled / +21 pp at 262K
  (McNemar χ²=14.6, p<0.001). Retrieval success ≠ reliable evidence use. That is a strong, well-controlled
  result and the paper's actual contribution.
- **The Zep/Graphiti datapoint is genuinely awkward** for memory vendors: a bi-temporal knowledge graph
  built specifically to invalidate superseded facts scores **7% on FC-SH — its lowest column in the
  whole benchmark — against plain BM25's 48%.** Even discounted (below), that is not a good look.

### What does not survive
1. **The causal attribution is inverted.** The deterministic operator contributes 0 pp at the headline
   scale. The LLM is still doing the semantic arbitration (deciding which retrieved facts are about the
   same subject+predicate). "Arbitration is a database problem" is refuted by the paper's own ablation;
   "arbitration needs a typed intermediate representation and an explicit policy interface" is what the
   data support.
2. **Oracle policy.** The pipeline is *given* the freshness rule a priori and hard-codes it. The paper
   flags this itself: "both are task-specialized pipelines that receive the freshness policy a priori;
   published systems are general-purpose architectures." A real company brain must *infer* which policy
   applies (supersession? correction? scoped exception? two valid values?) before any `max()` can run.
3. **A 13-point baseline confound.** Their own re-implemented BM25 direct-answer baseline scores **61**
   at 262K where MAB's BM25 row reports **48**. So of the headline "48 → 82" jump, roughly **13 pp is
   chunking/prompt/implementation drift before the method does anything**, ~21 pp is structured
   extraction, and ~0 pp is the deterministic operator. Published numbers were transcribed, never re-run.
4. **A chunk-size handicap on exactly the systems being indicted.** MAB used chunk size **512 for
   FactConsolidation for everyone except Mem0, Zep, Cognee and MIRIX, which were run at 4096 across all
   datasets** for cost reasons (MAB §4.1, Appendix F.3, Table 15). The four systems quoted as proof that
   memory products can't arbitrate (Mem0 18, Zep 7, Cognee 28, MIRIX 14) are the four given 8× coarser
   chunks on a corpus of short numbered sentences. This is a documented, uncorrected confound.
5. **The generalization test failed.** On LongMemEval's knowledge-update subset (45 questions,
   timestamp-keyed), structured assembly scores **26/45 vs 29/45 for the baseline; paired exact McNemar
   p = 0.45** — a null result the authors report prominently. Of the 5 baseline-only wins: 3 are Yes/No
   format failures, **1 needs a second-newest selector, 1 needs interval aggregation** — precisely the
   queries a rigid `max()` policy cannot express. This bounds the whole result to "current-value
   questions carrying explicit version metadata."
6. **The benchmark moved.** MAB v4's GPT-5-mini gets **78 FC-SH / 28 FC-MH** by stuffing 262K tokens
   into a 400K reasoning context — no memory layer, no retrieval, no arbitration code. It beats the
   structured pipeline on multi-hop. "All memory systems fail at arbitration" is now a claim about a
   2025-era model cohort, not about the architecture class.
7. **Statistical and scale caveats.** n = 100 per cell (±~5 pp SE at 50%); one synthetic MQUAKE-derived
   dataset; usually 2 candidates per conflict; **4,400 evaluations, ~$3 of API, ~15 minutes**; a
   two-author workshop paper, not main-track.

### How to state it in the synthesis

> On MemoryAgentBench's FactConsolidation — a synthetic MQUAKE-derived task where every fact carries an
> integer serial and the resolution rule is printed in the prompt — the 22 entries in the v3 results
> table all score ≤7% multi-hop, and the best memory system (HippoRAG-v2) reaches 54% single-hop at
> 262K, below plain GPT-4o long context at 60%. A two-stage pipeline that asks an LLM to extract
> matching candidates and *then* applies an explicit newest-wins policy reaches 82%/93% single-hop
> (gpt-4o-mini/gpt-4o). But the win comes from the structured interface, not from the determinism: the
> paper's own ablation puts the deterministic `max()` at +2 pp pooled and **0 pp at the headline scale**,
> the same pipeline shows no advantage on LongMemEval's knowledge-update subset (p=0.45), and a June
> 2026 benchmark update has GPT-5-mini scoring 78/28 with no memory layer at all. The defensible lesson
> is *keep version metadata at conflict granularity and make the resolution policy an explicit,
> inspectable interface* — not *replace the model with a database*.

## 6. Confidence

**High** on every number and on the mechanism correction — I read both papers' full HTML, both result
tables at all four context lengths, the pipeline source, and the released per-question JSON artifacts,
and each cross-checks. **Medium-high** on the "does it support the thesis" judgement, which is an
interpretation. The one number I could not independently verify is the LLM-picker arm (76.0 pooled /
82 at 262K), whose traces the authors have not yet released.

## 7. Suggested corrections to prior findings

`findings/neuro-inspired-rag.md` §7 and TL;DR item 2 should be amended:
- "22 published memory systems" → "the 22 entries in MAB v3 Table 3, of which only ~7 are memory systems"
- "the best (HippoRAG-v2) 54%" → "the best memory system (HippoRAG-v2) 54%; GPT-4o long context 60%"
- "a deterministic `max(serial)` in Python, with BM25 retrieval and no LLM freshness reasoning" →
  "BM25 → an LLM candidate-extraction call → `max(serial)`; the deterministic operator is worth 0 pp at 262K"
- "Contradiction arbitration is a database problem, not a latent-space problem" → "Contradiction
  arbitration needs a typed candidate representation and an explicit policy interface; the ablation does
  not support moving the arbitration itself out of the model"
- add: MAB v4 (2026-06-28) GPT-5-mini = 78 FC-SH / 28 FC-MH, and the Mem0/Zep/Cognee/MIRIX chunk-4096 confound.

---

## Sources

Primary (fetched and read in full, 2026-09-10):

- Hu, Wang, McAuley, *Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions*
  (MemoryAgentBench), ICLR 2026 — https://arxiv.org/abs/2507.05257
  - v3 full text (used by the comparison paper) — https://arxiv.org/html/2507.05257v3
  - v4 full text (adds GPT-5-mini) — https://arxiv.org/html/2507.05257v4
  - Table 3 (main results, FC at 262K), Table 5 (o4-mini validation), Table 6 (n=100/cell), Table 15 +
    §4.1 + Appendix F.3 (chunk sizes), Appendix B.4 (FC construction), Appendix D Fig. 5 (FC prompt),
    Appendix G (task rationale)
- Code / data: https://github.com/HUST-AI-HYZ/MemoryAgentBench (MIT, 449★, ICLR 2026 note, GPT-5-mini
  update May 2026, competency renamed "Conflict Resolution")
- OpenReview record referenced by the repo — https://openreview.net/forum?id=DT7JyQC3MR
- Reddy & Challaram, *Reliable Post-Retrieval Assembly for Agent Memory: Separating Evidence Extraction
  from Policy Execution* (v2, 2026-08-02) — https://arxiv.org/abs/2606.01435 ·
  https://arxiv.org/html/2606.01435v2
  - Table 1 (executor ablation), Table 3 (master results), Table 4 + Appendix C Table 8 (262K
    comparison), Table 5 + Appendix D (LongMemEval null), Appendix A (hyperparameters), Appendix B
    Table 7 (contested-subset executor comparison)
- Same paper, v1 (2026-05-31), titled *Don't Ask the LLM to Track Freshness: A Deterministic Recipe for
  Memory Conflict Resolution* — https://arxiv.org/html/2606.01435v1 (§3.3 "Why deterministic freshness
  works"; §5.3 limitation: "cleanly isolating the resolver's own contribution is future work")
- Companion code, prompts and per-question traces (MIT) —
  https://github.com/cvikasreddy/memory-conflict-resolution
  - `scripts/_pipeline.py` (`_freshness_pick`, `_llm_freshness_pick`, `CANDIDATE_PROMPT`, `PICKER_PROMPT`)
  - `poc_results/paper_sh_conflict_factconsolidation_sh_{6k,32k,64k,262k}.json` → 71/78/81/82 structured,
    63/70/75/61 direct
  - `poc_results/ablation_sh_fact_gpt4o_factconsolidation_sh_262k.json` → 93
  - `poc_results/ablation_mh_fact_gpt4omini_factconsolidation_mh_262k.json` → 27
  - `README.md` (COLM 2026 Lifelong Agent Workshop acceptance; "the gain is **not** mainly from
    replacing the LLM with `max()`"; released-vs-pending run table)
- Zhong et al., MQUAKE (source of the counterfactual edit pairs) — cited by MAB as Zhong et al. 2023

Secondary / cross-referenced:
- `findings/neuro-inspired-rag.md` (the claim under test)
- `checkpoints/01-sweep-decisions.md`

# g06 — The crux experiment: a runnable protocol

**Key:** `g06-crux-experiment` · lens: gap-fill / experiment design · written 2026-09-10 (Opus 5)

**The gap this fills.** Four prior reports name the same unanswered question and none specifies how to
answer it: `rag-taxonomy.md` Q3, `skeptic-claims.md` Q5, `memory-systems-landscape.md` Q2,
`neuro-inspired-rag.md` Q2 — *does write-side curation (dedup, provenance, supersession, contradiction
arbitration, hot/cold tiering, skills) improve **downstream answer accuracy** over a well-tuned
BM25+dense hybrid baseline on real organisational questions?* `v01-gbrain-benchmarks.md` closes with the
same sentence: even GBrain's cleanest isolated result (+6.2 R@5 / +9.7 first-place-hit from typed-edge
traversal) "is a *retrieval* result with **no answering model in the loop**, so it still does not close
the crux question."

This document is the protocol. Everything below is either (a) a verbatim command from a repo I fetched
today, (b) a number I computed today from a dataset I downloaded, or (c) explicitly marked as a design
choice with its rationale. Where a repo is public I give the real CLI; where an arm has to be built I
give the spec and the reason no shortcut exists.

---

## 0. TL;DR — the design in eleven lines

1. **Primary endpoint is judged answer accuracy, not recall@k.** The two diverge, and both MemConflict
   and gbrain-evals independently report the divergence. Retrieval is the secondary endpoint and must
   be reported in the same table so the reader can see where a win came from.
2. **The baseline must be tuned with the same budget as the treatment**, on a pre-registered dev split,
   or the experiment is worthless. This is the single most common failure in the existing literature.
3. **Every curated system runs an ablation ladder, not just default-vs-baseline** — the `+31.4`
   cautionary tale is a whole-system adapter gap that its own authors re-measured at +15.0 and could
   not attribute to the graph.
4. **Datasets:** LongMemEval-S (470 scored), MemConflict (3,750 questions — I downloaded and counted the
   released set today), MemoryAgentBench FactConsolidation (100/cell × 4 lengths), gbrain-evals
   BrainBench (145 relational + 181 concept), and a real-org arm built from the user's own 503-file
   markdown corpus and 39 MB of agent transcripts.
5. **Eight arms**, split into an *embedder-controlled* family (where the same embedder / reader / k can
   actually be enforced) and a *black-box* family (Zep Cloud, Mem0 Cloud) that is descriptive only.
6. **Controls:** one embedder, one reader, one judge (different model from the reader), k=5 primary with
   a {1,5,10,20} sweep, three ingestion-order seeds, temperature 0, all prompts frozen and committed.
7. **Statistics:** paired McNemar mid-p on the pooled primary set (n=4,220), Holm across 6 pre-registered
   comparisons, Wilson CIs on every cell, TOST equivalence at ±2 pp.
8. **Power:** pooled n=4,220 detects 2.8 pp Holm-adjusted; LongMemEval's knowledge-update slice (n=78)
   detects only ~20 pp. Under-powered strata are pre-declared as descriptive.
9. **Decision rule is pre-registered with four named outcomes** including an explicit
   "reranker-explained" verdict, because on the one public dataset where it has been isolated the
   reranker — not the graph and not the fusion — supplies the headline gain.
10. **CARS is a secondary diagnostic and is barred from the primary endpoint**, on the instruction of
    the paper that introduced it ("AC remains the primary metric; CARS is diagnostic only" — it
    "structurally favor[s] systems with explicit conflict modules").
11. **Total budget: ~$700–900 of API and ~3 machine-days** for the full matrix; a $30 Tier-0 slice that
    settles the sharpest sub-question can run in an afternoon.

---

## 1. Hypotheses, stated so they can fail

Let **B** = a tuned BM25+dense hybrid with a cross-encoder reranker over the same corpus, no write-side
lifecycle. Let **C** = a curated system (GBrain default, or any arm with dedup / supersession /
provenance / typed edges / skills).

- **H₀ (the skeptic's position, and the current default):** on judged answer accuracy over the pooled
  primary set, `acc(C) − acc(B) = δ` lies inside **[−2 pp, +2 pp]**.
- **H₁ (Tan's position):** `δ ≥ +5 pp`, and the ablation ladder attributes at least half of δ to a
  **write-side** component rather than to the reranker or to raw index quality.
- **H₂ (the interesting middle, which I expect):** δ ≈ 0 on aggregate but positive and large on
  **conflict-bearing strata** (MemConflict dynamic, LongMemEval knowledge-update, FactConsolidation)
  and ≈ 0 or negative elsewhere — i.e. curation buys *hygiene*, not *retrieval*.

H₂ is why the protocol pre-registers stratum-level analysis with its own multiplicity control instead
of only a pooled test. A pooled null with a large conflict-stratum effect is a **result**, not a failure.

**Pre-registration is not optional here.** Write §1, §5, §6 and §7 into a file, commit it, and record
the commit hash in every receipt *before* the first paid run. The corpus this project has assembled is
full of post-hoc best-cell reporting; this protocol has no defence against that except a timestamp.

---

## 2. Arms (systems under test)

Eight arms in two families. The split matters: you cannot hold the embedder fixed across a hosted
black-box service, so pretending you did would be the same error the literature already makes.

### Family A — embedder-controlled (eligible for the primary test)

| # | Arm | What it isolates | Status |
|---|---|---|---|
| A1 | **Tuned hybrid baseline** — BM25 + dense + RRF + cross-encoder rerank, no lifecycle | the null | build (thin) |
| A2 | **GBrain default** (`balanced`: reranker on, autocut off) | the full curated stack | public CLI |
| A3 | **GBrain, graph off** (`search.relational_retrieval` off) | typed-edge traversal | config flag |
| A4 | **GBrain, reranker off** (`--reranker off --autocut off`) | the reranker's share of δ | CLI flag |
| A5 | **GBrain + FlyHash novelty gate at ingest** | a write-side gate the stack lacks | build |
| A6 | **Letta MemFS** (git-backed markdown + `dreaming` + `memory doctor`) | the other file-and-git design | public, via MemConflict's `eval_letta.py` |
| A7 | **Full context** (no retrieval; whole haystack into a 1M-context reader) | the ceiling, and the honest upper bound | public CLI |

### Family B — black-box (descriptive only, reported separately, excluded from the primary test)

| # | Arm | Why it can't be controlled |
|---|---|---|
| B1 | **Mem0** (OSS via Docker, or Cloud) | OSS is controllable (`text-embedding-3-small` by default, swappable via `mem0-config.yaml`); Cloud is not — run **OSS** and move it to Family A if the embedder swap verifies |
| B2 | **Zep / Graphiti Cloud** | hosted extraction + hosted embeddings; no way to pin the embedder |

**Two arms that will be argued about, and my ruling.**

- *"A7 full-context isn't a memory system, drop it."* Keep it. It is the single most decision-relevant
  row for a company brain: `arXiv:2606.27472` reports bounded self-managed memory losing **15 points to
  full context** on LongMemEval knowledge-update questions with *more capacity recovering nothing*, and
  MemoryAgentBench v4 has GPT-5-mini scoring **78 FC-SH / 28 FC-MH** with no memory layer at all,
  beating every memory system in the table. If a curated brain cannot beat "paste everything into a 1M
  window", the product thesis is about cost and latency, not accuracy — and that is a finding.
- *"A5 FlyHash is speculative."* It is, and it is the only arm here that tests a **new** idea rather than
  re-measuring shipped ones. It is also cheap (§3.5). If it must be cut for budget, cut it before
  cutting A3/A4.

### 2.1 Arm A1 — the tuned baseline, specified so it cannot be a strawman

This is where the experiment is usually lost. Three rules, all pre-registered:

1. **Symmetric tuning budget.** Each of A1, A2, A5 gets the *same* number of configuration trials
   (recommend **30**) on the *same* 20% dev split, run by the same script, with the search space
   committed in advance. Report the full trial log, not just the winner.
2. **A1's search space must contain the things a competent engineer would actually try**: RRF `k`
   ∈ {20,60,100}; BM25 `k₁` ∈ {0.9,1.2,1.5}, `b` ∈ {0.4,0.75}; chunk size ∈ {256,512,1024} with 10–20%
   overlap; retrieval granularity ∈ {turn, session}; query expansion on/off; reranker on/off;
   candidate depth before rerank ∈ {20,50,100}. Note that chunk size is **not** a free parameter to
   fudge: MemoryAgentBench ran Mem0/Zep/Cognee/MIRIX at 4096 while everyone else got 512, and that
   single uncorrected confound is the reason its Zep row (7% FC-SH) cannot be used as evidence.
3. **A1 gets the same reranker as A2.** If GBrain runs Voyage `rerank-2.5`, so does A1. Otherwise you
   are measuring a reranker licence, not a librarian.

Baseline reference implementation you can start from today — LongMemEval ships its own tuned retrievers:

```sh
# LongMemEval baseline retrieval (BM25 / dense, session- or turn-granularity)
cd src/retrieval
bash run_retrieval.sh ../../data/longmemeval_s_cleaned.json flat-bm25    session
bash run_retrieval.sh ../../data/longmemeval_s_cleaned.json flat-gte     session   # gte-Qwen2-7B-instruct
bash run_retrieval.sh ../../data/longmemeval_s_cleaned.json flat-stella  session   # Stella V5 1.5B
```
(`RETRIEVER` ∈ `flat-bm25`, `flat-contriever`, `flat-stella`, `flat-gte`; `GRANULARITY` ∈ `turn`,
`session`. Source: LongMemEval README, fetched 2026-09-10.) You then fuse BM25 + dense with RRF and
rerank — that fusion + rerank layer is the ~200 lines you have to write yourself, and it is the whole
of arm A1.

### 2.2 Arm A5 — the FlyHash novelty gate, specified

The only arm requiring new code. It is a **write-side gate**, not an index; the read path is unchanged
GBrain. This placement is deliberate: as a semantic index FlyHash loses badly (H3D, `arXiv:2607.08382`:
0.1325 MAP on CSFCube vs 0.3431 for dense BGE-large), but the *fly Bloom filter* (`10.1073/pnas.1814448115`)
emits a continuous, distance- and time-sensitive novelty score in [0,1] — which is exactly the
"importance filter at write time" that practitioner guidance calls the cheapest place to control memory
quality, and exactly what a 155K-page auto-ingesting brain does not have.

```python
# pip install FlyHash numpy   (TeddyHuang-00/FlyHash, MIT — faithful to Dasgupta et al. 2017)
from flyhash import FlyHash
import numpy as np

d, m, k = 1024, 20480, 1024          # embedding dim; 20x expansion; top-5% WTA
fly = FlyHash(d, m)                  # sparse binary random projection + WTA
w   = np.ones(m)                     # MBON-a'3 weight vector (the Bloom filter)
DELTA, EPS = 0.90, 1e-4              # PNAS Eq.2: active w <- w*delta ; inactive w <- w + eps

def novelty(emb):                    # emb: L2-normalised page/chunk embedding, dim d
    tag = fly(emb[None, :])[0]       # sparse binary tag
    act = np.flatnonzero(tag)
    score = float(w[act].mean())     # in [0,1]; low = seen before
    w[act] *= DELTA                  # decay on exposure
    w[~tag.astype(bool)] += EPS      # slow recovery toward novel
    return score
```

Gate policy (pre-registered, one free parameter): admit a page to the brain iff
`novelty >= tau`; route `novelty < tau` to a `duplicates/` tier that is indexed but source-tier-demoted,
never deleted. Calibrate `tau` **on the dev split only**, targeting a fixed admit rate (recommend 90%)
so the gate cannot be tuned against the test set. Report ingest tokens and pages admitted as first-class
outcomes — if the gate cuts ingest cost 30% at δ ≈ 0, that is a win the accuracy column will not show.

---

## 3. Datasets — five, with verified sizes and real commands

### 3.1 LongMemEval-S (public, third-party, the anchor)

500 questions; **470 scored** after dropping the 30 abstention questions as the official scorer does;
~115K tokens of haystack per question; ~40 sessions each. Six question types incl. a **knowledge-update**
slice (n=78) that is the closest public proxy for supersession. Use the **cleaned Sept-2025 revision**
— the uncleaned original has answer-interference bugs the authors fixed.

```sh
mkdir -p data && cd data
wget https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_oracle.json
wget https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json
cd ..

# Full-context ceiling (arm A7): TOPK=1000 so every session is included
cd src/generation
bash run_generation.sh ../../data/longmemeval_s_cleaned.json <MODEL> full-history-session 1000 json false con

# Official judged scoring — this is the metric of record for the primary endpoint
cd ../evaluation
python3 evaluate_qa.py <JUDGE_MODEL> your_hypothesis_file ../../data/longmemeval_oracle.json
python3 print_qa_metrics.py <JUDGE_MODEL> your_hypothesis_file.log ../../data/longmemeval_oracle.json
```

GBrain runs it natively, and this exact invocation is the repo's own published reproduction path:

```sh
gbrain eval longmemeval <longmemeval_s_cleaned.json> \
  --retrieval-only --top-k 5 --by-type --no-trajectory \
  --mode balanced --reranker off --autocut off     # A4
# A2 (shipped default): --reranker on --autocut off
# A3: same, with search.relational_retrieval off
```

**Two traps, both documented in-repo.** (i) `recall_all@5` (every gold session in the top 5) vs
`recall_any@5` are not comparable and 300 of the 470 questions need ≥2 sessions; the k=5 ceiling is
**99.4%** because 3 questions carry 6 gold sessions. (ii) Vendor numbers in the 94–96% band are
LLM-judged *answer* accuracy, a different race. Never put the two in one column.

### 3.2 MemConflict (arXiv:2605.20926) — the conflict-typed core

**Freshly measured today.** I downloaded `Data/Step4_4.jsonl` (39.7 MB) from
`github.com/TaoZhen1110/MemConflict` and counted it:

| Quantity | Value (released expanded set, measured 2026-09-10) |
|---|---|
| Instances (simulated users) | **30** (the paper reports 12) |
| Total questions | **3,750** |
| Questions per instance | **125.0** mean |
| Dialogue tokens per instance | **202,050** mean |
| Sessions per instance | **52.6** mean |
| `dynamic_conflict` questions | **2,946** |
| `conditional_conflict` questions | **444** |
| `static_conflict` questions | **360** |

Per-question fields: `question_id, question, answer, conflict_type, ability_target, difficulty`.

This is the most valuable dataset in the protocol and nobody has run the file-and-git family on it. The
three conflict types are the reason a single global newest-wins policy is not a strategy: recency
resolves `dynamic` (78.6% of questions), is **inverted** for `static` (a later mention that is false),
and is **undefined** for `conditional` (both values true under different conditions). Stratified
reporting is mandatory, not optional.

```sh
git clone https://github.com/TaoZhen1110/MemConflict && cd MemConflict
pip install -r requirements.txt
cp .env.example .env      # OPENAI_API_KEY=... ; OPENAI_MODEL=gpt-5.0-mini
# per-system runners already exist:
python Evaluation/eval_letta.py       # A6
python Evaluation/eval_memzero.py     # B1 (mem0)
python Evaluation/eval_memos.py ; eval_a_mem.py ; eval_langmem.py ; eval_memobase.py
python Evaluation/diagnose_failures.py   # splits errors into retrieval vs utilisation
```

Write one new runner (`eval_gbrain.py`, `eval_hybrid.py`) against the same interface for A1–A5.
`diagnose_failures.py` is the reason to use this dataset over any other: it decomposes errors into
**retrieval failure** vs **utilisation failure**, which is precisely the split the crux needs and which
the paper reports is dominated by retrieval failure across most systems.

MemConflict's own metric set maps cleanly onto §5: `AA` (answer), `SEH@K` / `SRS` (retrieval),
`UOCS` (does it recognise update order), `CRS` (does it notice a contradiction exists), `EUG` (does
retrieved gold become a correct answer).

### 3.3 MemoryAgentBench — FactConsolidation (the arbitration floor)

```sh
conda create --name MABench python=3.10.16 && conda activate MABench
pip install torch && pip install -r requirements.txt && pip install "numpy<2"
# .env: OPENAI_API_KEY, Anthropic_API_KEY, Google_API_KEY, LLM_MODEL=gpt-4o-mini
bash bash_files/eniac/run_memagent_longcontext.sh     # long-context arms
bash bash_files/eniac/run_memagent_rag_agents.sh      # RAG + agentic memory arms
bash bash_files/eniac/run_memagent_rag_agents_chunksize.sh   # ← run this; do not skip
python llm_based_eval/longmem_qa_evaluate.py
```

FC-SH / FC-MH are scored by `substring_exact_match`. n = **100 per cell**, four context lengths
(6K/32K/64K/262K). Include it, but **downgrade it to a secondary, descriptive dataset** for three
documented reasons: the resolution rule is printed in the prompt; every fact carries an integer serial
so the ordering key is handed over; and the candidate set is usually **two** items. It measures the
floor of arbitration, not arbitration. Run the chunk-size ablation script explicitly — the 512-vs-4096
confound is the single largest known defect in the published table.

### 3.4 gbrain-evals BrainBench (the home-turf check)

```sh
git clone https://github.com/garrytan/gbrain-evals && cd gbrain-evals
bun install --frozen-lockfile
bun run eval:query:validate
bun eval/runner/validate-data.ts --quiet
BRAINBENCH_N=1 bun eval/runner/multi-adapter.ts --adapter grep-only --queries relational   # free, offline
BRAINBENCH_N=1 bun eval/runner/multi-adapter.ts --queries relational                       # needs OPENAI_API_KEY
bun run eval:run          # relational + fuzzy + externally-authored families
```
Adapters: `grep-only` (in-memory BM25), `vector`, `vector-grep-rrf-fusion` (hybrid, graph off), `gbrain`.
Adapter contract (`eval/runner/types.ts`), for adding A1/A5:
```typescript
interface Adapter {
  readonly name: string;
  init(rawPages: Page[], config: AdapterConfig): Promise<BrainState>;
  query(q: PublicQuery, state: BrainState): Promise<RankedDoc[]>;
  snapshot?(state: BrainState): Promise<string>;
  teardown?(state: BrainState): Promise<void>;
}
```
Sizes: 145 relational questions / 261 gold items over a 240-page corpus; 181 held-out concept questions;
30 source-swamp; 47 externally authored.

**Use it, and hold your nose in a specific place.** The 240-page world is Claude-Opus-generated fiction
and the relational question generator shares its four templates with the graph adapter's parser — the
repo says so, and a template-blind paraphrase variant proposed in issue #24 has never been run. **Run
that variant as part of this protocol** (paraphrase all 145 questions with a model that never sees the
parser, have a human spot-check 30). It is the cheapest high-value new measurement in this entire
document and it tests GBrain's strongest claim at its weakest joint.

### 3.5 The real-org arm (the point of the whole exercise)

Every dataset above is synthetic or LLM-generated. The crux says "**real org questions**". Here is a
real corpus that exists on this machine right now:

| Source | Measured 2026-09-10 |
|---|---|
| Markdown across 18 repos under `/Users/stephen/Cookies` | **503 files, 3.68 MB** |
| `CLAUDE.md` project-memory files | **17** |
| Claude Code auto-memory notes | 6 files in `~/.claude/projects/-Users-stephen-Cookies/memory/` |
| Claude Code session transcripts | **39 MB** JSONL |

And it contains a genuine, dated, human-verifiable **supersession chain** — the four NAS notes indexed
by `MEMORY.md`: `nas-r8152-usb-nic-disabled` → `nas-disk-write-sources` ("dockerd + CMS keep the disks
spinning 24/7") → `nas-cms-package-stopped` → `nas-healthchecks-removed` ("dockerd writes down 95%").
The third and fourth notes partially invalidate the second. That is exactly a LongMemEval
knowledge-update item, except it is real, the ground truth is knowable by the person who lived it, and
no LLM wrote the conflict on purpose.

**Question construction protocol** (the part that makes it a benchmark rather than a demo):

1. **Freeze a snapshot.** `git rev-parse HEAD` per repo + a tarball hash of the memory dir and
   transcripts. Every arm ingests the identical bytes.
2. **Author 200 questions in four strata, 50 each**, before running any system:
   *(a) point lookup* ("what port does X bind?"), *(b) cross-repo synthesis* ("which repos use pgvector
   and why did each pick it?"), *(c) knowledge-update* ("is dockerd still the main disk-write source on
   the NAS?" — gold: no, healthchecks were removed and writes fell 95%), *(d) abstention* (answerable
   nowhere in the corpus; gold = "I don't know").
   Stratum (c) is the reason this arm exists. Stratum (d) is the reason it is honest — GBrain's
   calibration spec found only **34 of 500** candidate takes falsifiable on a production brain and 17 of
   those ungradeable, i.e. ~3.4% checkable, so an eval without abstention items will flatter every
   system that confabulates fluently.
3. **Gold = a file list + a short free-text answer**, written by the corpus owner, stored in a file the
   adapters never see. Follow gbrain-evals' boundary discipline: strip gold before it reaches an adapter.
4. **Blind grading.** The judge sees question + gold + a shuffled, de-identified hypothesis. Arm names
   never reach the judge.
5. **Human adjudication of a 40-question sample**, reported as Cohen's κ against the LLM judge. If
   κ < 0.6, the judge is the finding and the arm results are void. (ConflictRAG reports κ=0.74 with 85%
   agreement against 200 human-checked samples; that is the bar to clear.)

**Honest power ceiling:** at n=200 this arm detects ~8–10 pp, and ~12 pp after multiplicity correction
(§6). It cannot settle a 3-point difference and must never be reported as if it could. Its job is to
catch a *large* effect — or a large regression — that the synthetic sets miss, and to expose the failure
modes only a real corpus has (dead links, half-finished notes, three CLAUDE.md files disagreeing).

---

## 4. Controls — what is nailed down, and what cannot be

| Control | Setting | Enforcement |
|---|---|---|
| **Embedder** | one model for every Family-A arm (e.g. Voyage `voyage-3`, or `BGE-large` locally for a zero-cost variant) | config in each arm; assert the model id in the receipt |
| **Reader** | one model, one frozen prompt, `temperature=0` | committed prompt file + hash in receipt |
| **Judge** | a **different** model from the reader | ConflictRAG's own design, "to mitigate self-evaluation bias" |
| **k** | **5** primary; sweep {1,5,10,20} as secondary | LongMemEval's published comparison point |
| **Chunking** | identical chunk size + overlap across arms, or explicitly reported per arm | the MemoryAgentBench 512-vs-4096 confound is the cautionary tale |
| **Reranker** | on in both A1 and A2, or off in both; never on in one only | reranker supplied +2.13 pp on the one dataset where it was isolated |
| **Ingestion order** | 3 seeded shuffles per arm | gbrain-evals' own default; order-sensitivity is real |
| **Repetitions** | 3 runs per (arm × dataset × seed); report median and spread | 3 seeded shuffles are **not** 3 independent datasets — say so in the report |
| **Corpus bytes** | one frozen snapshot, hashed | |
| **Cost meter** | tokens in/out per phase, from `response.usage`, not estimated | |
| **Wall clock** | ingest seconds, query p50/p95 | measured on one machine; note the machine |

**What cannot be controlled, stated up front:** Zep Cloud and Mem0 Cloud embed with their own models and
extract with their own LLMs. Their rows are descriptive. Any comparison that puts them in the primary
test is making the same mistake as every vendor leaderboard in this space. Mem0 **OSS** is promotable to
Family A if and only if the embedder swap through `mem0-config.yaml` verifies in the receipt.

Runnable today for the black-box family:
```sh
# Mem0 OSS (Docker + Qdrant) — three-stage ingest -> search -> evaluate
git clone https://github.com/mem0ai/memory-benchmarks && cd memory-benchmarks
pip install -r requirements.txt
cp .env.example .env && docker compose up -d          # server :8888, qdrant :6333
python -m benchmarks.longmemeval.run --project-name crux-mem0-oss --all-questions \
       --answerer-model <READER> --judge-model <JUDGE> --top-k 5 --top-k-cutoffs 1,5,10,20
```

```sh
# Cross-vendor harness with a Provider ABC (MIT) — Zep, Mem0, Supermemory, custom
git clone https://github.com/maximem-ai/memory_and_context_eval_harness && cd $_
pip install -e . && cp .env.example .env
python scripts/download_datasets.py --variant s        # LongMemEval-S, 500 questions
python -m runner.server                                # API + dashboard on :8766
pytest tests/unit/test_provider_contract.py -v         # check a new adapter against the contract
```
This harness is the recommended backbone for the cross-system arms: one 5-phase pipeline
(ingest → search → answer → evaluate → report) that computes Hit@K / P@K / R@K / F1@K / MRR / NDCG
**and** judged accuracy, so the retrieval/answer split falls out for free. **Caveat, stated plainly:**
it is published by a vendor (Synap/maximem) whose own product tops its headline table. Read
`docs/DEVIATIONS.md` before trusting a single number, and re-derive its metrics against LongMemEval's
official `src/evaluation/evaluate_qa.py` on at least one arm.

---

## 5. Metrics

### Primary (one, pre-registered)
**Answer accuracy**, LLM-judged with LongMemEval's official prompts and official abstention handling,
on the pooled primary set = LongMemEval-S (470) + MemConflict (3,750) = **n = 4,220**.

### Secondary — retrieval (reported in the same table, never merged with the primary)
- `recall_all@5` (strict: every gold session in top-5) — **and** `recall_any@5` as a labelled diagnostic.
- MemConflict `SEH@K` (gold memory in top-K) and `SRS` (rank of the gold memory).
- BrainBench P@5 / R@5 with a **fixed k=5 denominator** (the pre-audit helper divided by returned-list
  length and could exceed 1.0; that bug halved the headline when fixed).

### Secondary — hygiene
- **Knowledge-update accuracy**: LongMemEval `knowledge-update` slice (n=78) + MemConflict
  `dynamic_conflict` (n=2,946) + real-org stratum (c) (n=50).
- **Conflict recognition**: MemConflict `UOCS` (update order recognised) and `CRS` (contradiction
  noticed). CRS is the sharpest instrument in the set — the published best across six memory systems is
  **0.2501**, meaning systems answer correctly *without knowing a conflict existed*. Detection precedes
  arbitration and is the actual bottleneck.
- **Evidence utilisation gap** (`EUG`): of the questions where gold was retrieved, what fraction were
  answered correctly. This is the number that separates "bad librarian" from "bad reader".
- **Superseded-serving rate**: fraction of answers asserting a value the corpus later invalidated.
  Vanilla RAG serves superseded values 15–40% of the time and cosine similarity separates
  "contradicted" from "rephrased" at **AUROC 0.59**, so this metric has real headroom.
- **CARS** (`arXiv:2605.17301`), verified from the paper today:
  `CARS = 0.35·AC + 0.25·CDA + 0.25·RA + 0.15·SF` — answer correctness, conflict-detection F1,
  resolution appropriateness (LLM-rated), source fidelity.
  **Barred from the primary endpoint by its own authors' instruction:** *"AC remains the primary metric;
  CARS is diagnostic only"*, and it "structurally favor[s] systems with explicit conflict modules". A
  curated brain beating a plain hybrid on CARS is close to tautological. Report it; never headline it.
- **Citation faithfulness** (real-org arm only, 40-question sample): NLI-check whether each cited span
  actually entails the claim. Up to 57% of citations in attributed RAG answers are correct-but-unfaithful
  — a brain graded on "every fact has a `[Source: …]`" is measuring the easy half.

### Secondary — cost and time
- Ingest tokens (LLM extraction calls) and embedding tokens, per MB of corpus.
- Ingest wall-clock seconds per 1,000 sessions and per MB.
- Query p50/p95 latency, tokens per query, **dollars per 100 correct answers** (the only cost number
  that is comparable across arms).
- Pages/facts admitted vs suppressed (A5 only).

---

## 6. Sample sizes, power, confidence intervals

Design is **paired**: every arm answers the same questions, so use McNemar (mid-p) on discordant pairs,
not a two-sample test. Table below computed today (α=0.05 two-sided, power=0.80; `p_disc` = fraction of
questions where the two arms disagree; Holm column is the Bonferroni-worst case for the 6 pre-registered
primary comparisons).

| Stratum | n | MDD @ p_disc=0.15 | MDD @ 0.25 | MDD, Holm k=6 |
|---|---:|---:|---:|---:|
| **Pooled primary (LME-S + MemConflict)** | **4,220** | **1.7 pp** | **2.2 pp** | **2.7 pp** |
| MemConflict — all | 3,750 | 1.8 | 2.3 | 2.8 |
| MemConflict — dynamic | 2,946 | 2.0 | 2.6 | 3.2 |
| MemConflict — conditional | 444 | 5.1 | 6.6 | 8.3 |
| MemConflict — static | 360 | 5.7 | 7.4 | 9.2 |
| LongMemEval-S (scored) | 470 | 5.0 | 6.5 | 8.0 |
| LongMemEval-S knowledge-update | 78 | 12.3 | 15.9 | 19.7 |
| FactConsolidation SH @262K | 100 | 10.9 | 14.0 | 17.4 |
| FactConsolidation SH, all 4 lengths | 400 | 5.4 | 7.0 | 8.7 |
| BrainBench relational | 145 | 9.0 | 11.6 | 14.4 |
| BrainBench concept (held out) | 181 | 8.1 | 10.4 | 12.9 |
| Real-org, 200 questions | 200 | 7.7 | 9.9 | 12.3 |
| Real-org, 400 questions | 400 | 5.4 | 7.0 | 8.7 |

Read this table as a set of instructions:

- The **pooled primary is properly powered** — it can resolve the ±2 pp equivalence band, which is the
  whole point.
- **LongMemEval alone cannot** carry the verdict (MDD 5.0–8.0 pp). Anyone claiming a 2-point win on
  LongMemEval-S is reading noise. This is why MemConflict is in the design.
- **The knowledge-update slice (n=78) is hopeless on its own** — 12–20 pp. Do not run it as a standalone
  test; pool it with MemConflict `dynamic` and the real-org stratum (c) into one pre-registered
  *supersession* stratum (n = 78 + 2,946 + 50 = 3,074 → MDD 2.0 pp at p_disc=0.15, 3.1 pp Holm-adjusted) and report the three components
  descriptively underneath.
- **FactConsolidation @262K (n=100) detects nothing under 11 pp.** Report all four context lengths
  pooled (n=400), or report it as description.
- Every single-arm cell gets a **Wilson 95% CI**; at n=470 and p≈0.85 the half-width is ±3.2 pp, at
  n=100 it is ±7.0 pp. Print the CI next to every number or the table lies by omission.
- Below n=30 in any cell, print a `small_sample_note` and no point estimate.

**Multiplicity.** Exactly **6 primary comparisons** are pre-registered (A2 vs A1, A3 vs A2, A4 vs A2,
A5 vs A2, A6 vs A1, A7 vs A1), Holm-corrected. Everything else — every stratum, every k, every
secondary metric — is **exploratory and labelled as such**. This is the discipline the existing
literature lacks and the reason a 4-arm × 12-metric matrix can otherwise produce a "significant" result
by accident.

**Equivalence.** H₀ is tested by TOST at margin ±2 pp on the pooled primary. At n=4,220 with
p_disc=0.20 the 95% CI half-width is ≈1.4 pp, so an equivalence verdict is achievable rather than being
an unfalsifiable "no evidence of difference".

---

## 7. Pre-registered decision rule

Let δ = `acc(A2) − acc(A1)` on the pooled primary, with Holm-adjusted p. Let
δ_writeside = δ measured with the reranker **off in both arms** (A4 vs A1-no-rerank).

| Verdict | Condition | What it means for the deliverable |
|---|---|---|
| **CURATION WINS** | δ ≥ **+5 pp**, Holm-adj. p < 0.05, **and** δ_writeside ≥ 0.5·δ | Tan's thesis is empirically supported; the librarian earns its keep on accuracy |
| **RERANKER-EXPLAINED** | δ ≥ +5 pp, p < 0.05, but δ_writeside < 0.3·δ | The win is a cross-encoder, not a librarian. Report it as a retrieval-engineering result, not an architecture result |
| **CURATION IS COSMETIC** | TOST rejects both one-sided nulls at ±2 pp | Answer (a) becomes: it *is* RAG on accuracy; the case for curation must be made on cost, latency, auditability or governance — not accuracy |
| **INCONCLUSIVE** | none of the above | Report δ with its CI and say the experiment was under-powered for the observed effect. This is a legitimate outcome and must be pre-authorised, or it will be laundered into a win |

**Three riders, all binding:**

1. **Stratum rider.** If the pooled verdict is COSMETIC but the supersession stratum (n=3,074) shows
   δ ≥ +5 pp at Holm-adjusted p < 0.05, the headline becomes **"curation buys hygiene, not retrieval"** —
   H₂. This is a distinct, reportable outcome and I consider it the modal one.
2. **Cost rider.** Any winning arm must also report dollars and ingest-hours per 100 correct answers. A
   +5 pp win at 10× ingest cost is reported as *"+5 pp for 10× write-side cost"*, never as "+5 pp".
3. **Ablation rider.** No verdict is issued from a whole-system comparison alone. Every claim of the
   form "X produces the gain" requires a one-switch run — same index, same query vectors, one flag —
   which is exactly the discipline that took GBrain's own graph claim from `+31.4` (whole-adapter, since
   re-measured at +15.0) to `+6.2 R@5 / +9.7 first-place` (isolated switch, zero regressions across 435
   question/seed pairs). Whole-system deltas go in the appendix.

---

## 8. Budget

**API cost** (Anthropic list prices per MTok, from the bundled `claude-api` skill table cached
2026-06-24: Opus 5 $5/$25 · Sonnet 5 $2/$10 · Haiku 4.5 $1/$5 — 1M context on Opus/Sonnet, 200K on Haiku,
so the 115K-token LongMemEval haystack fits all three):

| Phase | Tokens | Sonnet 5 | Haiku 4.5 |
|---|---:|---:|---:|
| LongMemEval-S full-context reader (A7), 500 × 115K | 57.5M in | **$116** | $58 |
| LongMemEval-S retrieval-arm reader, k=5 (~14K/q), per arm | 7.2M in | $16 | $8 |
| LongMemEval-S judge (1K in / 50 out per q) | 0.5M in | $1.25 | $0.62 |
| MemConflict ingest (30 × 202K) | 6.1M | one-off per arm | |
| MemConflict reader, 3,750 q at k=5 | 52.5M in | **$112** | $56 |
| BrainBench multi-adapter (all families, 3 seeds) | — | ~$15 | — |
| Real-org arm (200 q × 3 arms + judge) | — | ~$10 | — |

Six Family-A arms × (LongMemEval + MemConflict) at Sonnet-5 reader ≈ **$770**, plus judge ≈ $20, plus
embeddings (57.5M + 6.1M tokens, one pass per distinct embedder — under $10 at typical embedding rates),
plus the A7 full-context arm at $116. **Round to $850–900 with 20% headroom for reruns.** Halve it by
using Haiku 4.5 as the reader — but then say so, because reader choice moves answer accuracy more than
most of the arms do, and MemoryAgentBench v4's GPT-5-mini row is the proof.

**Machine time:** MemConflict ingest is 6.1M tokens per arm (minutes to hours depending on whether the
arm makes an LLM call per fact — Mem0 does, GBrain's edge extraction does not, and *that difference is
itself a headline result*). LongMemEval ingest is 57.5M tokens per arm. Budget ~3 machine-days wall
clock for the full matrix, mostly ingest.

**Tier-0 ($30, one afternoon).** If only one thing gets run, run this:
A1 vs A2 vs A4 on **MemConflict `static_conflict` (360) + `conditional_conflict` (444)** with a Haiku
reader. These are the 804 questions where newest-wins is *inverted* or *undefined*, they are the
questions a company brain actually gets wrong, MDD is 5.7–7.4 pp so a real effect is visible, and
nobody has ever run the file-and-git family on them. If curation shows nothing here, the pooled
experiment is unlikely to rescue it.

---

## 9. Execution order

1. **Pre-register.** Commit §1/§5/§6/§7 + the tuning search space + all prompts. Record the hash.
2. **Free checks.** `bun eval/runner/validate-data.ts --quiet`, `bun run eval:query:validate`,
   `BRAINBENCH_N=1 … --adapter grep-only` (no API calls), `pytest tests/unit/test_provider_contract.py`.
   Verify the harness before spending a dollar.
3. **Re-derive one published number** end-to-end — recommend GBrain's 93.40% reranker-off
   `recall_all@5`, for which both the in-repo command and a sibling per-question receipt exist
   (438/470 on 2026-09-02, 469 of 470 rows agreeing per question). If you cannot reproduce a number
   whose receipts are committed, stop; the harness is wrong.
4. **Tune on dev**, symmetric budget, log every trial.
5. **Tier-0** (§8) — cheap, decisive, and it de-risks the rest.
6. **Full matrix**, 3 seeds, receipts per run.
7. **Ablation ladder** for every arm that wins anything.
8. **Real-org arm**, blind-graded, with κ against a 40-question human sample.
9. **Publish the failures.** gbrain-evals' credibility comes from publishing an expansion feature that
   cost 187 questions, a `disclosed-gap` receipt status, an outside-review issue it acted on, and a
   re-run that halved its own headline. Any protocol that only publishes its wins has learned nothing
   from the corpus it is trying to correct.

---

## 10. What this protocol still cannot settle

Stated so the eventual write-up cannot overclaim:

1. **Four of five datasets are synthetic or LLM-generated.** MemConflict is 30 simulated Persona-Hub
   users, generated with `gpt-5.0-mini`; its authors say so. BrainBench's world is Opus-written fiction.
   FactConsolidation is MQUAKE-derived with the answer key's ordering handed to the model. Only
   LongMemEval-S is a third-party human-built benchmark, and only the real-org arm is a real
   organisation — and it is one person's, at n=200.
2. **"Company brain" ≠ "chat memory."** Every public benchmark here is conversational history. Nothing
   measures a 24,000-person-page brain with ACLs, retention policy, and 66 crons writing into it. That
   dataset does not exist publicly, and building one is a bigger project than this experiment.
3. **Procedural memory is untested.** SKILL.md files are the one requirement plain memory systems do not
   cover — and no dataset here scores whether a skill made the agent better at a task. That needs an
   eval-gated skill benchmark (SkillOpt's shape: benchmark + a *disjoint* held-out set, accept only on
   strict improvement), which is a separate protocol.
4. **The judge is a confound.** LLM-as-judge with κ≈0.74 against humans means roughly a quarter of
   disagreements are the judge's. Report κ, report the format-bias check (strip structured annotations
   and re-score — ConflictRAG measured 2.2–2.5 pp of judge preference for structured output, which is
   exactly the direction that flatters a citation-emitting curated brain).
5. **Model drift.** MemoryAgentBench's "all systems fail" claim survived one benchmark revision and
   died in the next when a 400K-context model was added. Any verdict here is a verdict about a model
   cohort. Pin model ids in every receipt and re-run on the next frontier release.
6. **It does not test the fruit-fly bridge as a whole**, only the one piece of it that is cheap and
   falsifiable (A5, the write-side novelty gate). Connectome-topology transfer is a different question
   and the degree-preserving-null result argues against it.

---

## Sources

Fetched or measured 2026-09-10 unless noted.

**Datasets and harnesses (commands quoted above are verbatim from these)**
- LongMemEval README (data URLs, `run_retrieval.sh`, `run_generation.sh`, `evaluate_qa.py`) — https://raw.githubusercontent.com/xiaowu0162/LongMemEval/main/README.md · repo https://github.com/xiaowu0162/LongMemEval · paper https://arxiv.org/abs/2410.10813 · cleaned data https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned
  - directory listings verified via `gh api`: `src/retrieval/{eval_utils.py,index_expansion_utils.py,run_retrieval.py,run_retrieval.sh}`, `src/generation/{run_generation.py,run_generation.sh}`
- MemConflict README (construction + `Evaluation/eval_*.py` + metric definitions) — https://raw.githubusercontent.com/TaoZhen1110/MemConflict/main/README.md · repo https://github.com/TaoZhen1110/MemConflict · paper https://arxiv.org/abs/2605.20926
  - **dataset statistics in §3.2 measured by me today** from `Data/Step4_4.jsonl` (39,671,712 bytes), downloaded via https://raw.githubusercontent.com/TaoZhen1110/MemConflict/main/Data/Step4_4.jsonl — 30 instances, 3,750 questions, 125.0 q/instance, 202,050 mean dialogue tokens, 52.6 mean sessions, conflict_type counts dynamic 2,946 / conditional 444 / static 360
- MemoryAgentBench README (conda setup, `bash_files/eniac/*.sh`, metric→field mapping) — https://raw.githubusercontent.com/HUST-AI-HYZ/MemoryAgentBench/main/README.md · repo https://github.com/HUST-AI-HYZ/MemoryAgentBench · paper (ICLR 2026) https://arxiv.org/abs/2507.05257 · OpenReview https://openreview.net/forum?id=DT7JyQC3MR
- gbrain-evals README — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/README.md
- gbrain-evals `eval/README.md` (runner table, adapter descriptions, metric semantics, the "historical pre-audit measurement" note) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/eval/README.md
- gbrain-evals `eval/CONTRIBUTING.md` (the `Adapter` interface quoted in §3.4, question-authoring flow, reproduction rules) — https://raw.githubusercontent.com/garrytan/gbrain-evals/main/eval/CONTRIBUTING.md
- GBrain README v0.48.5.0 (the `gbrain eval longmemeval` invocation, search modes, reranker defaults, 95.53%/93.40%/86.6%/93.8% figures) — https://raw.githubusercontent.com/garrytan/gbrain/master/README.md
- mem0 `memory-benchmarks` README (OSS Docker + `python -m benchmarks.*.run` flags) — https://raw.githubusercontent.com/mem0ai/memory-benchmarks/main/README.md (the `evaluation/` path in `mem0ai/mem0` is a submodule pointing here)
- maximem-ai memory & context eval harness (MIT, 10★, pushed 2026-09-09; Provider ABC, 5-phase pipeline, retrieval metric list, `docs/DEVIATIONS.md`) — https://raw.githubusercontent.com/maximem-ai/memory_and_context_eval_harness/main/README.md · repo https://github.com/maximem-ai/memory_and_context_eval_harness
- FlyHash package (MIT, the API quoted in §2.2) — https://raw.githubusercontent.com/TeddyHuang-00/FlyHash/main/README.md · https://pypi.org/project/FlyHash/

**Metric and method sources**
- ConflictRAG, *Detecting and Resolving Knowledge Conflicts in RAG* — https://arxiv.org/abs/2605.17301 · full text https://arxiv.org/html/2605.17301v1
  - CARS definition verified verbatim today (§III-E): `CARS = w_a·AC + w_d·CDA + w_r·RA + w_s·SF`, `(w_a,w_d,w_r,w_s) = (0.35,0.25,0.25,0.15)`; "**AC remains the primary metric; CARS is diagnostic only**"; CARS "structurally favor[s] systems with explicit conflict modules"; judge = GPT-4o distinct from GPT-4o-mini generator; human verification 200 samples, 85% agreement, κ=0.74; format-bias check costs 2.2–2.5%; hybrid BM25+Contriever retrieval at K=5, 3 seeds, paired bootstrap
- Dasgupta, Stevens & Navlakha, FlyHash, *Science* 2017 — https://doi.org/10.1126/science.aam9868
- Dasgupta, Sheehan, Stevens & Navlakha, fly Bloom filter, *PNAS* 2018 (the δ/ε update rule in §2.2) — https://doi.org/10.1073/pnas.1814448115
- H3D benchmark (FlyHash 0.1325 / 0.4305 MAP vs BGE-large 0.3431 / 0.6626) — https://arxiv.org/abs/2607.08382
- MemStrata (embeddings separate contradicted-vs-rephrased at AUROC 0.59; superseded served 15–40%) — https://arxiv.org/abs/2606.26511
- Supersede (bounded self-managed memory −15 pts vs full context on knowledge-update; more capacity recovers nothing) — https://arxiv.org/abs/2606.27472
- Reddy & Challaram, post-retrieval assembly / deterministic freshness (the executor ablation: +2.0 pp pooled, 0 pp at 262K) — https://arxiv.org/abs/2606.01435
- Wallat et al., *Correctness is not Faithfulness in RAG Attributions* (up to 57% unfaithful citations) — https://arxiv.org/abs/2412.18004
- SkillOpt (eval-gated skill mutation; the shape the missing procedural-memory protocol needs) — https://arxiv.org/abs/2605.23904
- Anthropic model ids and per-MTok prices used in §8 — bundled `claude-api` skill model table (cached 2026-06-24); for current prices see the Pricing row of that skill's `shared/live-sources.md`

**Prior reports in this project relied on for the design constraints**
- `findings/v01-gbrain-benchmarks.md` (the +31.4 → +15.0 → +6.2 chain; the one-switch discipline; the k=5 ceiling of 99.4%; issue #24's never-run paraphrase variant)
- `findings/v09a-memoryagentbench.md` (FactConsolidation construction; n=100/cell; the 512-vs-4096 chunk confound; MAB v4 GPT-5-mini 78/28)
- `findings/v09b-memoryagentbench-skeptic.md` (MemConflict three-type taxonomy; CRS ≤ 0.2501; retrieval failures dominate)
- `findings/memory-hygiene.md`, `findings/memory-systems-landscape.md`, `findings/flyhash-sparse-retrieval.md`, `findings/completeness-critic.md`

**Real-org corpus figures in §3.5** measured on this machine 2026-09-10: 503 markdown files / 3,679,052 bytes under `/Users/stephen/Cookies` (excluding `node_modules` and `.git`), 17 `CLAUDE.md`, 6 files in `~/.claude/projects/-Users-stephen-Cookies/memory/`, 39 MB of session transcripts.

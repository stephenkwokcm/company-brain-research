# g02 — Sizing and cost arithmetic for a company brain

**Gap:** nobody sized or costed anything.
**Date of work:** 2026-09-10. **Method:** repo receipts + live provider prices + **a real pgvector HNSW
index built and measured locally today** (pgvector 0.8.6 / PostgreSQL 17.11, Docker).

---

## TL;DR — the five answers

1. **The ANN index is not the bottleneck, and it is not close.** Measured: a pgvector HNSW top-10 query
   over 250,000 × 1024-dim vectors returns in **10.7 ms** (3.8 ms at 100K). GBrain's own published
   end-to-end `gbrain search` median is **122 ms**, its reranker adds **+150 ms p50**, and a synthesized
   answer is "a few seconds, dominated by the Anthropic API." The ANN scan is **~3.7% of retrieval
   latency and ~0.14% of an answered question**. **FlyHash-as-index is dead on arithmetic**: replacing a
   4 ms component inside a 3,272 ms path is unwinnable even at zero cost and zero quality loss.
2. **Cost is dominated by write-side LLM curation, not by embeddings or retrieval — by 2–3 orders of
   magnitude.** From GBrain's own receipt: takes extraction costs **$0.0128/page** actual
   (**$0.033/page** quoted, **$0.260/page** at Opus-class). Embedding the same page costs
   **$0.0000576**. Curation is **222×–4,514×** the embedding cost. GBrain's `docs/operations/spend-controls.md`
   opens with *"GBrain itself is rounding error; the spend that matters is downstream embedding"* — its own
   receipts invert that by a factor of ~222.
3. **Tan's "under $100/month for a 25-person company" is roughly right, but for none of the stated
   reasons.** Both halves of his decomposition are wrong and the errors partially cancel; the dominant
   cost (the nightly dream cycle) is absent from the decomposition, and the largest cost of all (the agent
   loop that reads the brain) is defined out of scope. Detail in §5.
4. **1,024 dimensions is the single worst choice in pgvector**, and it is GBrain's new-install default.
   Measured: 1024-d and 1536-d cost **exactly the same 8,192 bytes/vector** of HNSW index, while 768-d
   costs **4,096**. A 1024-d element wastes **46% of every 8 KB index page**. Switching the column to
   `halfvec(1024)` cuts the index **3×** (8,192 → 2,731 B/vec) with one DDL change.
5. **No published operator account quantifies the human librarian's hours — anywhere.** Not in the talk,
   not in the repo, not in 600 cached GitHub issues, not on Hacker News. This is a genuine void, not a
   search failure. Best estimate and its basis in §7.

---

## 1. What the units actually are (established before any arithmetic)

| Quantity | Value | Source |
|---|---|---|
| Pages (headline) | 155,795 | [README.md:5](https://github.com/garrytan/gbrain/blob/master/README.md) (2026-08-12) |
| **Chunks per page (MEASURED)** | **2.40** | 107K pages → 257K chunks, [docs/proposals/temporal-contradiction-probe.md:208](https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md) (production, 2026-05-14) |
| Chunks per page (design-era) | 2.94 | 7,471 pages → ~22K chunks, [docs/GBRAIN_V0.md](https://github.com/garrytan/gbrain/blob/master/docs/GBRAIN_V0.md) |
| Chunk target | 300 words, 50-word overlap | [src/core/chunkers/recursive.ts:12,58-59](https://github.com/garrytan/gbrain/blob/master/src/core/chunkers/recursive.ts) |
| Tokens per chunk | ~400 | [docs/eval/SEARCH_MODE_METHODOLOGY.md](https://github.com/garrytan/gbrain/blob/master/docs/eval/SEARCH_MODE_METHODOLOGY.md) |
| Chars per token | 3.5 | `estimateCostFromChars`, [src/core/embedding-pricing.ts](https://github.com/garrytan/gbrain/blob/master/src/core/embedding-pricing.ts) |
| Embedding model (new install) | `voyage:voyage-4` @ **1024 dims** | [src/core/ai/defaults.ts:47-48](https://github.com/garrytan/gbrain/blob/master/src/core/ai/defaults.ts) |
| Embedding model (legacy default) | `zeroentropyai:zembed-1` @ 1280 dims | ibid. :26-27 |
| Schema column | `embedding vector(1536)` | [src/schema.sql:302](https://github.com/garrytan/gbrain/blob/master/src/schema.sql) |
| ANN index | `USING hnsw (embedding vector_cosine_ops)`, **no explicit m / ef_construction** → pgvector defaults **m=16, ef_construction=64** | [src/schema.sql:336](https://github.com/garrytan/gbrain/blob/master/src/schema.sql) |

> **The task brief said "assume 3-5 chunks per page." GBrain's own production measurement is 2.40.** I
> report the measured figure as primary and carry 3/4/5 as a sensitivity band. Note this collides with a
> modelling assumption elsewhere in the repo — [`TODOS.md:7250`](https://github.com/garrytan/gbrain/blob/master/TODOS.md)
> models "~30KB/page", which at 400 tokens/chunk implies ~21 chunks/page, **9× the measured ratio**. A
> gbrain "page" averages ~3.4 KB, not 30 KB. Flag if any downstream report uses the 30 KB figure.

---

## 2. pgvector HNSW footprint — derived from source, then measured

### 2a. The formula (primary source: `pgvector/src/hnsw.h`)

```
HNSW_MAX_SIZE            = BLCKSZ(8192) - MAXALIGN(24) - MAXALIGN(8) - 4  = 8160 usable bytes/page
HNSW_ELEMENT_TUPLE_SIZE  = MAXALIGN(offsetof(HnswElementTupleData,data) + VECTOR_SIZE)
                         = MAXALIGN(72 + 8 + 4*dim)              [72 = 4 flags + 10 heaptids*6 + 6 + 2]
HNSW_NEIGHBOR_TUPLE_SIZE = MAXALIGN(4 + 6 * (level+2) * m)       [level 0 gets 2m links, each higher level m]
HNSW_DEFAULT_M 16 · HNSW_DEFAULT_EF_CONSTRUCTION 64 · HNSW_DEFAULT_EF_SEARCH 40 · HNSW_MAX_DIM 2000
```
`hnswbuild.c:205-229` co-locates an element and its neighbour tuple on one page when they fit. E[level] =
e^(−1/m)/(1−e^(−1/m)) = 0.0667 for m=16, so the mean neighbour tuple is 208 bytes. Per-vector cost is
therefore `8192 / floor(8160 / (elem + 208 + 8))` — **quantised to whole 8 KB pages**, which is where the
surprise lives.

### 2b. Prediction vs. measurement (measured today, pgvector 0.8.6 / PG 17.11)

| dim | type | elem bytes | elements/page | **predicted B/vec** | **MEASURED B/vec** | vs raw vector |
|---|---|---|---|---|---|---|
| 768 | `vector` | 3,152 | 2 | 4,096 | **4,096** ✓ | 1.33× |
| **1024** | `vector` | 4,176 | **1** | 8,192 | **8,192** ✓ | **2.00×** |
| 1536 | `vector` | 6,224 | 1 | 8,192 | **8,192** ✓ | 1.33× |
| 2000 | `vector` | 8,080 | 0 (split) | 8,408 | — | 1.05× |
| 1024 | `halfvec` | 2,128 | 3 | 2,731 | — | 1.33× |
| 3072 | `halfvec` | 6,224 | 1 | 8,192 | — | 1.33× |

Three independent confirmations, exact to the byte. **3072 dims cannot be HNSW-indexed as `vector` at
all** (`HNSW_MAX_DIM 2000`); it needs `halfvec` (cap 4000), which is precisely problem #1 in GBrain's
[`docs/designs/VECTOR_BACKENDS.md`](https://github.com/garrytan/gbrain/blob/master/docs/designs/VECTOR_BACKENDS.md).

### 2c. Raw measurements

| dim | n | index MB | **B/vec** | build s | ANN ms @ef=40 | @ef=200 | table B/vec |
|---|---|---|---|---|---|---|---|
| 768 | 100,000 | 390.6 | 4,096 | 65.8 † | 3.66 | 6.84 | 4,195 |
| 1024 | 100,000 | 781.3 | 8,192 | 84.5 † | 3.78 | 8.28 | 5,583 |
| 1536 | 50,000 | 390.6 | 8,192 | 61.1 | 4.37 | 7.61 | 8,338 |
| **1024** | **250,000** | **1,953.1** | **8,192** | **274.4** | **10.73** | **20.25** | 5,583 |

† 2 parallel workers; the other two rows are single-threaded. Vectors are uniform random (verified 500/500
distinct) — **worst case for HNSW**; real embeddings cluster and query faster. The 250K row ran with only
`shared_buffers=256MB` against a ~2 GB index, so its 10.7 ms is a **RAM-starved worst case**; that is
itself the useful finding (see §4).

### 2d. Index size at company-brain scale

| corpus | chunks | 768d | **1024d / 1536d (default)** | halfvec(1024) |
|---|---|---|---|---|
| **155,795 pages** × 2.40 | 373,908 | 1.43 GiB | **2.85 GiB** | 0.95 GiB |
| 155,795 pages × 4 | 623,180 | 2.38 GiB | 4.75 GiB | 1.58 GiB |
| **1,000,000 pages** × 2.40 | 2,400,000 | 9.16 GiB | **18.31 GiB** | 6.10 GiB |
| 1,000,000 pages × 4 | 4,000,000 | 15.26 GiB | 30.52 GiB | 10.17 GiB |

**Build time**, extrapolated from the 250K measurement (≈1.1 ms/vector single-threaded, mildly
super-linear): ~**7 min** at 373,908 chunks, ~**50-70 min** at 2.4M — single-threaded on random vectors;
2-4× faster with `max_parallel_maintenance_workers` and adequate `maintenance_work_mem`. This is not the
operational bottleneck either: GBrain's own ingest figure is "**about 20 minutes** the first time" for a
10K-page corpus ([company-brain.md](https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md)),
which is dominated by embedding-API round-trips, not index construction.

**GBrain's own storage model is wrong in a compensating way.** `docs/GBRAIN_V0.md` estimates "HNSW index
overhead (~2× embeddings) ~270MB" for 22K chunks at 1536 dims. Measured truth at 1536d: 8,192 B/vec ×
22K = **180 MB**, i.e. **1.33×** the raw vectors, not 2×. The ratio is wrong but the direction is
conservative.

---

## 3. Embedding cost — the number Tan is most wrong about

Full index pass, 400 tokens/chunk:

| corpus | tokens | voyage-4 ($0.06/M) | voyage-4-lite ($0.02) | OpenAI 3-large ($0.13) |
|---|---|---|---|---|
| 155,795 pg × 2.40 | 149.6 M | **$8.97** | $2.99 | $19.44 |
| 155,795 pg × 4 | 249.3 M | $14.96 | $4.99 | $32.41 |
| 1,000,000 pg × 2.40 | 960.0 M | $57.60 | $19.20 | $124.80 |
| 1,000,000 pg × 4 | 1,600.0 M | $96.00 | $32.00 | $208.00 |

Prices verified **live today** at [docs.voyageai.com/docs/pricing](https://docs.voyageai.com/docs/pricing)
and cross-checked against [`src/core/embedding-pricing.ts`](https://github.com/garrytan/gbrain/blob/master/src/core/embedding-pricing.ts) — they agree.

**Voyage grants the first 200M tokens free per account.** A complete index of the 155,795-page brain
(149.6M tokens) **fits inside the free grant**. GBrain's pricing table deliberately does not model this
("over-reporting inside a grant beats under-reporting past it"), so the honest steady-state embedding
bill for a 25-person company is plausibly **$0.00**.

Per page: **$0.0000576.** Hold that number.

---

## 4. Is the ANN index the bottleneck? **No.**

### Latency budget for one answered question

| component | ms | source |
|---|---|---|
| pgvector HNSW ANN scan @374K chunks | **~4.5** | **measured today** (3.8 ms @100K, 10.7 ms @250K RAM-starved) |
| rest of `gbrain search` (BM25, RRF, graph walk, 4-layer dedup, SQL re-rank) | ~117.5 | 122 ms median, [company-brain.md Part 13](https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md) |
| cross-encoder rerank (`voyage:rerank-2.5`) | +150 | [docs/architecture/RETRIEVAL.md](https://github.com/garrytan/gbrain/blob/master/docs/architecture/RETRIEVAL.md) |
| synthesized answer (Anthropic) | ~3,000 | "a few seconds, dominated by the Anthropic API", company-brain.md |
| **total** | **~3,272** | ANN = **0.14%** of the answer, **3.7%** of `gbrain search` |

**Consequence for question (b).** A FlyHash / sparse-expansion index that was *free, instant and lossless*
would improve an answered question by **at most 0.14%**. The published quality evidence runs the other
way (H3D: FlyHash 0.13 vs dense 0.34 MAP, per `findings/flyhash-sparse-retrieval.md`). There is no
arithmetic under which FlyHash-as-the-semantic-index wins. **The write-side fly Bloom filter / novelty
gate is the only part of the fly programme that survives this analysis**, because it acts on the
$0.0128–$0.26/page curation path (§5), which is where 99%+ of the money is — a dedup gate that rejects
10% of incoming pages saves ~10% of the dominant cost line, versus ~0.014% for the index idea.

### The one place the index *does* matter: RAM, not latency

The 250K measurement degraded 3.8 → 10.7 ms precisely because a ~2 GB index was served through 256 MB of
`shared_buffers`. Resident, HNSW scales logarithmically; non-resident, it degrades toward linear. So the
index sets the **hosting tier**, not the latency:

| corpus | index (1024d) | smallest Supabase instance that holds it | $/mo |
|---|---|---|---|
| 155,795 pages | 2.85 GiB | Pro + Large (8 GB RAM) | $25 + $110 = **$135** |
| 1,000,000 pages | 18.31 GiB | Pro + 2XL (32 GB RAM) | $25 + $410 = **$435** |

([supabase.com/pricing](https://supabase.com/pricing), fetched 2026-09-10.) **The right fix is not
FlyHash.** In descending order of effort:

1. `halfvec(1024)` — **3× smaller index**, native to pgvector, one DDL change. 18.31 → 6.10 GiB at 1M
   pages, dropping the 2XL ($410) to an XL ($210). GBrain does not use it.
2. Binary quantisation + rescoring — 1024 bits = 128 B/chunk, **64× smaller**, standard practice, keeps
   dense semantics.
3. `pgvectorscale` StreamingDiskANN — already the proposal in `VECTOR_BACKENDS.md` (status: proposal at
   v0.48.5.0), explicitly motivated by "RAM-bound scaling … for million-chunk brains."

**Also note:** GBrain moved its default from 1536-d to 1024-d, which bought **zero** index-size reduction
(both are 8,192 B/vec) and only a 33% table reduction. Moving to 768-d or `halfvec` would have halved or
thirded it.

---

## 5. Verifying "under $100/month for a 25-person company"

**The claim** — [`docs/tutorials/company-brain.md:6` and `:549`](https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md):

> "**Cost:** under $100 a month sustained for a 25-person company." … "expect about **$40 a month in
> embeddings** (the default `voyage-4` at $0.06/million tokens), **$50 a month in Anthropic calls** for the
> synthesized-answer queries, **plus your hosting bill**. Under $100 a month for the AI side."

### Half 1: "$40/month in embeddings" — wrong by ~100×, in the expensive direction

$40 ÷ $0.06/M = **667 M embedding tokens/month** = 1,666,667 chunks = **694,444 new pages/month** =
**27,778 pages per person per month** = **1,263 pages per person per working day**. Alternatively: **4.5
complete re-embeds of the entire 155,795-page brain, every month.**

The honest figure is **$0.03–$0.63/month** at 1–20 new pages/person/day — and plausibly **$0.00** inside
Voyage's 200M-token free grant. Tan's embedding line is ~100× too high.

### Half 2: "$50/month in Anthropic calls" — a defensible number for a phantom workload

Using GBrain's own per-query token model (`SEARCH_MODE_METHODOLOGY.md`) and **live** Anthropic rates:

| mode | Haiku 4.5 ($1/M) | Sonnet 5 ($2/M) | Opus 5 ($5/M) |
|---|---|---|---|
| conservative ~4K tok | 12,500 q/mo (22.7/person/day) | 6,250 (11.4) | 2,500 (4.5) |
| balanced ~10K tok | 5,000 (9.1) | 2,500 (4.5) | 1,000 (1.8) |
| tokenmax ~20K tok | 2,500 (4.5) | 1,250 (2.3) | 500 (0.9) |

Arithmetically fine. But it prices **only the retrieved chunks as input** — no system prompt, no tool
definitions, no conversation history, **no output tokens at all**. The same repo publishes a
"realistic-scale anchor" for what a brain-backed agent actually costs: **~$700/month for ONE power user**
(860 turns, ~900K tokens/turn, 88% prompt-cache hit rate). Scaled to 25 seats:

| scenario | $/month | $/seat | vs the $100 claim |
|---|---|---|---|
| 25 power users | $17,500 | $700 | **175×** |
| 25 users at ¼ power | $4,375 | $175 | **44×** |
| 25 users at 1/10 power | $1,750 | $70 | **18×** |

### Half 3 (missing entirely): the nightly dream cycle

The 25-phase cycle does not appear in the decomposition at all, and on GBrain's own receipts it is the
**largest brain-side cost line**:

| receipt | value | source |
|---|---|---|
| Takes extraction, full run | **$361.49** for 28,256 pages = **$0.0128/page** | [docs/takes-vs-facts.md](https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md), 2026-05-10 |
| — quoted per-page rates | **$0.033/page** (Azure GPT-5.5) vs **$0.260/page** (Opus-class) | ibid. † |
| Contradiction probe | $0.005/query, $0.50/100 queries | [docs/contradictions.md](https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md) |
| Nightly quality probe | ~$0.35/run ≈ $10.50/mo; **$150/mo** worst case | [docs/eval-bench.md:1033](https://github.com/garrytan/gbrain/blob/master/docs/eval-bench.md) (default **OFF**) |
| `extract_atoms` phase cap | $0.30 default | [docs/operations/spend-controls.md](https://github.com/garrytan/gbrain/blob/master/docs/operations/spend-controls.md) |
| `lsd` brainstorm | $5 cap — **$50.71 actual** in a 53× overrun | [docs/incidents/2026-05-20-lsd-cost-explosion.md](https://github.com/garrytan/gbrain/blob/master/docs/incidents/2026-05-20-lsd-cost-explosion.md) |
| `skillopt` | $0.70–$1.00 typical, $5.00 cap | docs/guides/skillopt.md |

† **These two receipts contradict each other**: $361.49 ÷ 28,256 = $0.0128/page, not the $0.033/page
quoted in the same bullet list — a 2.6× internal discrepancy.

### The $/seat/month curve the critic asked for

25 people, 155,795-page brain, **takes extraction only** (1 of ~10 LLM phases) at the actual receipt rate:

| new pages/person/day | pages/mo | embed | takes phase | contradiction | quality probe | **AI subtotal** | **$/seat** | + hosting | **all-in $/seat** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 550 | $0.03 | $7.04 | $7.56 | $10.50 | **$25.13** | $1.01 | $135 | $6.41 |
| 2 | 1,100 | $0.06 | $14.07 | $7.56 | $10.50 | **$32.20** | $1.29 | $135 | $6.69 |
| 5 | 2,750 | $0.16 | $35.18 | $7.56 | $10.50 | **$53.40** | $2.14 | $135 | $7.54 |
| **10** | 5,500 | $0.32 | $70.36 | $7.56 | $10.50 | **$88.74** | $3.55 | $135 | $8.95 |
| 20 | 11,000 | $0.63 | $140.73 | $7.56 | $10.50 | **$159.42** | $6.38 | $135 | $11.78 |

At the Opus-class rate ($0.26/page) the takes column alone is **$143/mo at 1 page/person/day** and
**$2,860/mo at 20** — the whole budget is decided by which model does the curation, a variable Tan never
mentions.

### Verdict

**PARTIALLY CONFIRMED — right answer, wrong arithmetic, and the scope excludes the dominant cost.**

- The **$100/month ceiling holds for GBrain's own AI spend** up to roughly **10 new pages/person/day**
  ($88.74/mo), provided curation runs on a cheap model and the optional probes stay near default.
- But the stated decomposition is wrong in both halves: embeddings are ~**100× cheaper** than claimed
  ($0.03–$0.63, not $40), and the omitted dream cycle is ~**200× more expensive** than embeddings. The two
  errors partially cancel, which is why the headline survives.
- **"Plus your hosting bill"** is doing enormous work: hosting is **$135/month minimum** at this corpus
  size — more than the entire AI budget it is appended to. All-in is ~**$225/month**, not "under $100."
- The **agent loop that actually consumes the brain is out of scope** and is **18–175×** the whole figure
  by the repo's own anchor. A reader hearing "under $100 a month for a company brain" will not spend
  under $100 a month.

### One more Tan claim, which does check out

Talk [10:39]: reorganising ~800 pages for "a couple hundred dollars worth of tokens and probably 10
minutes." At the Opus-class rate of $0.260/page, 800 pages = **$208**. Confirmed.

---

## 6. Contradiction-probe sampling cost

GBrain's published model: `claude-haiku-4-5`, ~500 input + 80 output tokens per judge call
([docs/contradictions.md](https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md);
defaults pinned in [`src/core/eval-contradictions/cost-tracker.ts`](https://github.com/garrytan/gbrain/blob/master/src/core/eval-contradictions/cost-tracker.ts)).

**The doc's own per-call figure is wrong.** 500/1M × $1 + 80/1M × $5 = **$0.00090**, not the "~$0.0006"
stated two lines below — the doc understates its own inputs by **1.5×**. (Haiku 4.5 at $1/$5 verified live
at [claude.com/pricing](https://claude.com/pricing) today.)

**Why sampling is not optional:**

| corpus | chunks | unordered pairs | exhaustive judging |
|---|---|---|---|
| 155,795 pages | 373,908 | 6.99 × 10¹⁰ | **$62.9 million** |
| 1,000,000 pages | 2,400,000 | 2.88 × 10¹² | **$2.59 billion** |

Actual nightly sample (~50 queries × ~5.6 judge calls) = 280 calls = **$0.25/night ≈ $7.56/month** —
covering **4.0 × 10⁻⁷ %** of the pair space. The probe is affordable *because* it inspects an
infinitesimal fraction, and the honest statement of what it buys is "a Wilson-bounded estimate of the
contradiction rate," not "the brain is consistent." The repo is straight about this (Wilson 95% CI,
`small_sample_note` at n<30); downstream summaries should not upgrade it.

---

## 7. The human librarian's labour cost — **unresolvable from published sources**

I searched, and found nothing quantified:

- **The talk:** the only labour statement is [14:58] *"a librarian, human plus agent, whose actual job is
  pruning."* No hours, no headcount, no cost. Zero occurrences of a time or money figure attached to the
  human role anywhere in the transcript.
- **The repo:** `docs/GBRAIN_RECOMMENDED_SCHEMA.md:1021` says *"The human's job: curate sources, direct
  analysis, ask good questions… The agent's job: everything else"* — again unquantified. The one
  per-week measurement instrument, [`docs/designs/AGENT_BOOTSTRAP_SPIKE.md`](https://github.com/garrytan/gbrain/blob/master/docs/designs/AGENT_BOOTSTRAP_SPIKE.md),
  measures write/recall correctness, not labour — and its own gate status reads **"not yet run — no
  `AGENT_BOOTSTRAP_SPIKE_RESULTS.md` is committed."**
- **600 cached GitHub issues:** two time-adjacent hits, neither about operator labour.
- **Hacker News** (Algolia API, story + comment search): the largest gbrain thread has 17 comments.
  Operators describe maintenance burden qualitatively — *"require technical knowledge and time"*, *"tons of
  hard-coded regexes that may work beautifully for Garry's priorities… that don't fit other use cases"* —
  but nobody publishes hours.

**Best estimate, clearly labelled as inference (confidence: low).** Building bottom-up from what the
repo *does* quantify:

| driver | published quantity | implied human minutes/week |
|---|---|---|
| Contradiction findings needing adjudication | ~115 HIGH findings / 50 queries, → ~25 residual after manual resolution ([temporal-contradiction-probe.md](https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md), 2026-05-14). The probe **never auto-resolves** — it emits paste-ready commands a human runs. | 25 × ~2 min = ~50 |
| `gbrain doctor` — 20 checks, warn/fail triage | 20 checks, `--remediation-plan` carries `est_seconds` per step | ~30 |
| Takes-quality review | cross-modal eval **6.8/10**, attribution the top failure mode; **34 of 500** candidate takes falsifiable and **17 of those 34** ungradeable ([calibration-quality-gate-spec.md](https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md)) | ~60 |
| Filing-rule / SKILL.md upkeep ("never do one-off work") | 142 SKILL.md files, no-regression eval law | ~30 |
| **Total** | | **~2.5–3 h/week** |

At a US knowledge-worker loaded rate of $75–$150/h that is **$190–$450/week ≈ $800–$1,950/month** — i.e.
**8–20× the entire "$100/month" AI budget**, and by far the largest line in the whole system. This is an
estimate assembled from adjacent published quantities, not a measurement, and I flag it as the weakest
number in this report. **If the synthesis needs one defensible sentence, it is that the human librarian's
cost is unpublished by everyone in this ecosystem while being, on any plausible estimate, the dominant
cost — which is exactly the fact a "$100/month" headline obscures.**

---

## 8. Corrections this report contributes to the corpus

| # | Claim in circulation | Correction |
|---|---|---|
| 1 | "assume 3-5 chunks per page" | GBrain's production measurement is **2.40** (107K pages → 257K chunks) |
| 2 | `TODOS.md`: "~30KB/page" | Incompatible with the measured chunk ratio by **9×**; a page averages ~3.4 KB |
| 3 | `GBRAIN_V0.md`: "HNSW overhead ~2× embeddings" | Measured **1.33×** at 1536d (2.00× at 1024d, for a packing reason, not an overhead reason) |
| 4 | `docs/contradictions.md`: "~$0.0006 per judge call" | Its own inputs give **$0.00090** — understated **1.5×** |
| 5 | `takes-vs-facts.md`: "$0.033/page" beside "$361.49 / 28,256 pages" | The receipt implies **$0.0128/page** — **2.6×** internal discrepancy |
| 6 | `src/core/model-pricing.ts`: `claude-sonnet-5` = $3/$15 | Live rate at claude.com/pricing today is **$2/$10** — the table is **50% high** (conservative direction) |
| 7 | `spend-controls.md`: "GBrain itself is rounding error; the spend that matters is downstream embedding" | **Inverted.** Curation is **222×** embedding on the repo's own receipts. Every gate in that doc except one guards embedding — the cheap side. |
| 8 | Critic's estimate: "155K pages → ~10⁶ chunks × 1536 dims, index is a few GB" | Chunks **373,908** (not 10⁶); dims **1024** (not 1536); index **2.85 GiB**. The *conclusion* — not the bottleneck — is correct and now measured. |

---

## Sources

**Measured locally, 2026-09-10** — pgvector 0.8.6 / PostgreSQL 17.11 (aarch64), Docker image
`pgvector/pgvector:pg17`, HNSW defaults m=16 / ef_construction=64, uniform-random vectors (500/500
distinct verified). Scripts and raw output:
`/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad/{pgv.py,calc.py,calc2.py,pgv_results2.txt,pgv_results3.txt}`

**pgvector primary source**
- https://raw.githubusercontent.com/pgvector/pgvector/master/src/hnsw.h — `HNSW_MAX_DIM 2000`, `HNSW_DEFAULT_M 16`, `HNSW_DEFAULT_EF_CONSTRUCTION 64`, `HNSW_DEFAULT_EF_SEARCH 40`, `HNSW_MAX_SIZE`, `HNSW_ELEMENT_TUPLE_SIZE`, `HNSW_NEIGHBOR_TUPLE_SIZE`, struct definitions
- https://raw.githubusercontent.com/pgvector/pgvector/master/src/hnswbuild.c — lines 197-229, element+neighbour page co-location
- https://raw.githubusercontent.com/pgvector/pgvector/master/README.md — `vector` ≤2,000 dims / `halfvec` ≤4,000; `maintenance_work_mem` build guidance; `max_parallel_maintenance_workers`

**GBrain repo** (`garrytan/gbrain` @ `43597b19`, v0.48.5.0)
- https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md — line 6 "under $100 a month sustained for a 25-person company"; line 549 the $40/$50 decomposition; Part 13 "about 122 ms median", "about 22 seconds for 164 pages", "about 20 minutes" for 10K pages
- https://github.com/garrytan/gbrain/blob/master/docs/eval/SEARCH_MODE_METHODOLOGY.md — cost anchors, 300-word→400-token chunk, mode×model matrix, the ~$700/mo single-power-user anchor (860 turns, ~900K tok/turn, 88% cache hit)
- https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md — "100,720 takes from 28,256 on-disk pages, $361.49"; "$0.033 vs $0.260/page"; cross-modal eval 6.8/10
- https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md — judge cost model, ~500 in/80 out, "~$0.0006 per judge call", "~$0.50 per 100 queries", $5 TTY / $1 non-TTY caps
- https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md — line 208 "~107K pages, ~257K chunks"; ~115 HIGH findings / 50 queries; ~25 residual
- https://github.com/garrytan/gbrain/blob/master/docs/operations/spend-controls.md — "GBrain itself is rounding error; the spend that matters is downstream embedding"; the full gate table; `cycle.extract_atoms.budget_usd` $0.30
- https://github.com/garrytan/gbrain/blob/master/docs/eval-bench.md — line 1033 "~$0.35 per nightly run … ≈ $10.50/month … Worst-case $150/month"
- https://github.com/garrytan/gbrain/blob/master/docs/incidents/2026-05-20-lsd-cost-explosion.md — $50.71 actual vs $0.96 estimated, 53× overrun, 13,690-page brain
- https://github.com/garrytan/gbrain/blob/master/docs/GBRAIN_V0.md — storage table (~750MB / 7,471 pages / ~22K chunks), "HNSW index overhead (~2x embeddings)", "$4-5 initial import"
- https://github.com/garrytan/gbrain/blob/master/docs/designs/VECTOR_BACKENDS.md — dimension cap + RAM-bound scaling + `vector.backend` proposal (status: proposal)
- https://github.com/garrytan/gbrain/blob/master/docs/designs/AGENT_BOOTSTRAP_SPIKE.md — the only per-week instrument; "Gate status: not yet run"
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md — 34/500 falsifiable, 17/34 ungradeable
- https://github.com/garrytan/gbrain/blob/master/src/schema.sql — line 302 `vector(1536)`, line 336 HNSW index DDL with no explicit m/ef_construction
- https://github.com/garrytan/gbrain/blob/master/src/core/ai/defaults.ts — `NEW_INSTALL_DEFAULT_EMBEDDING_MODEL = 'voyage:voyage-4'`, `…DIMENSIONS = 1024`; legacy `zeroentropyai:zembed-1` @ 1280
- https://github.com/garrytan/gbrain/blob/master/src/core/chunkers/recursive.ts — 300-word chunks, 50-word overlap
- https://github.com/garrytan/gbrain/blob/master/src/core/embedding-pricing.ts — voyage-4 $0.06/M, rerank-2.5 $0.05/M, 3.5 chars/token
- https://github.com/garrytan/gbrain/blob/master/src/core/model-pricing.ts — `claude-sonnet-5` $3/$15 (stale), Haiku 4.5 $1/$5, Opus 5 $5/$25, cache multipliers
- https://github.com/garrytan/gbrain/blob/master/src/core/eval-contradictions/cost-tracker.ts — 500/80 default per-call token budget
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/RETRIEVAL.md — reranker +150 ms p50

**Live prices, fetched 2026-09-10**
- https://docs.voyageai.com/docs/pricing — voyage-4 $0.06/M, -lite $0.02, -large $0.12, rerank-2.5/-3 $0.05; **first 200M tokens free per account**
- https://claude.com/pricing — Haiku 4.5 $1/$5 (cache read $0.10), Sonnet 5 **$2/$10**, Opus 5 $5/$25, Fable 5.1 $10/$50; 50% batch discount
- https://supabase.com/pricing — Free $0 / 500 MB; Pro $25 / 8 GB; compute add-ons Micro $10 (1 GB) → Large $110 (8 GB) → XL $210 (16 GB) → 2XL $410 (32 GB)

**Talk**
- https://www.youtube.com/watch?v=eBUyTS7SzV4 — transcript at `sources/transcript_eBUyTS7SzV4.txt`: [10:39] "couple hundred dollars worth of tokens and probably 10 minutes"; [12:54] "the library plus the librarian"; [14:58] "a librarian, human plus agent, whose actual job is pruning". No labour or cost quantification for the human role anywhere.

**Operator accounts searched, nothing quantified found**
- https://hn.algolia.com/api/v1/search?query=gbrain (story + comment endpoints) — largest thread 17 comments; qualitative maintenance-burden remarks only
- 600 cached `garrytan/gbrain` issues (`scratchpad/issues/p1-p6.json`) — 2 time-adjacent hits, neither about operator labour

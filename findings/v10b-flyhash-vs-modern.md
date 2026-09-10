# v10b — FlyHash vs. the modern retrieval stack (adversarial comparison)

**Lens:** comparator. **Date of work:** 2026-09-10. **Worker:** research agent (Claude Opus 5).
**Task key:** `v10b-flyhash-vs-modern`.

**Verdict: the critic's charge is CONFIRMED, and it lands harder than the critic guessed.**
FlyHash has **no defensible advantage in any retrieval role** in a 100K–1M page company brain — not as
index, not as quantizer, and (the surprise) **not as a dedup gate either**. The only role that survives
is the **novelty / staleness gate**, and the thing that survives there is the *fly Bloom filter*
(PNAS 2018), **not FlyHash** — and its fly-specific residue is one decay schedule, not a hash.

---

## 0. TL;DR — the five numbers that decide it

| # | Finding | Number | Source |
|---|---|---|---|
| 1 | On H3D's own benchmark, **FlyHash is last of five semantic-agnostic fingerprints** on CSFCube MAP — and it is not the fastest either | FlyHash **0.1325** vs SimHash 0.1770, MinHash 0.2451, Winnowing **0.2678**; times 10.95 s vs SimHash 3.62 s | [arXiv:2607.08382](https://arxiv.org/html/2607.08382) Tab. 5 |
| 2 | **SimHash strictly dominates FlyHash** on the other H3D dataset too — higher MAP *and* lower cost | RELISH test: SimHash 0.4756 @ 0.00 s vs FlyHash 0.4305 @ 1744.65 s | ibid. Tab. 6 |
| 3 | A **32-bit sign-binarized BGE-small** code beats a **128-bit FlyHash** code by ~2× MAP at ¼ the size | 0.2592 vs 0.1325 (CSFCube); 0.5506 vs 0.4305 (RELISH) | ibid. Tab. 5, 6, 7, 8 |
| 4 | At real embedding width the **FlyHash code is bigger than the vector it replaces** | d=1536, 40× expansion, top-5% → **7,680 B** dense bitmap vs **6,152 B** float32 vs **200 B** binary | my arithmetic on [pgvector storage rules](https://github.com/pgvector/pgvector#vector-type) |
| 5 | The index is **not the bottleneck at this scale**: 1B points serve <3 ms on one 64 GB box | DiskANN: ">5000 queries a second with <3ms mean latency and 95%+ 1-recall@1" | [DiskANN, NeurIPS 2019](https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf) |

---

## 1. The slot map — what FlyHash is actually competing against

The prior report `flyhash-sparse-retrieval.md` compared FlyHash against **one** comparator (frozen dense
BGE) and concluded "lose on the read path, win on the write path." That framing hides three occupied
slots. Laid out properly, there are five roles a fly-inspired primitive could take, and each has a
production incumbent:

| Role | What it must do | Incumbent | Incumbent's credential |
|---|---|---|---|
| **Index** | ANN over semantic content | HNSW / DiskANN | 1B pts, 64 GB, <3 ms, 95% recall@1 |
| **Sparse-code retriever** | lexical-ish codes in an inverted index | SPLADE++ / uniCOIL / BM42 | BEIR 50.5 nDCG@10 vs BM25 43.7 |
| **Quantizer** | shrink dense vectors | binary / int8 + rescore | 32× memory, ~96% perf retained |
| **Dedup gate** | near-duplicate detection at ingest | SimHash / MinHash | 64-bit fingerprints, k=3, web-scale since 2007 |
| **Novelty gate** | "is this worth writing down / is it stale?" | SAGE (vMF density), or free ANN-max-cosine | 3.4× cheaper writes, 2.5× lower latency |

The fly reports in this corpus argued the index role (lose), then retreated to the dedup/novelty gate
(win). **The retreat position is only half right**: the dedup slot is occupied by an algorithm that
beats FlyHash on H3D's own numbers.

---

## 2. Comparator evidence, one slot at a time

### 2.1 Dense embeddings + HNSW / DiskANN — the index slot

**DiskANN** (Subramanya, Devvrit, Simhadri, Krishnaswamy, Kadekodi — NeurIPS 2019,
[PDF](https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf)):

> "index, store, and search a billion point database on a single workstation with just 64GB RAM"
> … "serves > 5000 queries a second with < 3ms mean latency and 95%+ 1-recall@1" (16-core machine)

The paper also reports that competing in-memory graph methods (HNSW, NSG) under the same memory budget
plateau "around 50% 1-recall@1," which is why DiskANN exists — but that comparison is at **billion**
scale. At 10⁶ it is moot: HNSW fits in RAM with room to spare (§3).

**HNSW** (Malkov & Yashunin, [arXiv:1603.09320](https://arxiv.org/abs/1603.09320)) is the incumbent in
GBrain's actual stack: `content_chunks.embedding vector(1536)` with
`USING hnsw (embedding vector_cosine_ops)` (`gbrain-architecture.md` §schema).

Two properties matter for the FlyHash pitch specifically, both from
[pgvector's README](https://github.com/pgvector/pgvector#hnsw):

> "an index can be created without any data in the table since there **isn't a training step** like IVFFlat"

That is the single loudest claim in the FlyHash pitch — *data-independent, works day one, streaming
inserts, no rebuild* — and **HNSW already has it**. IVFFlat needs training; HNSW does not. FlyHash's
headline advantage is a differentiator against the wrong baseline.

### 2.2 Learned sparse retrieval — the "sparse codes" slot

This is the comparator the fly reports never mention, and it is the direct competitor: it puts
**sparse codes in an inverted index** and is measured on the standard IR sets.

**SPLADE++** (Formal, Lassance, Piwowarski, Clinchant, [arXiv:2205.04733](https://arxiv.org/abs/2205.04733),
SIGIR 2022) — Table 2, mean nDCG@10 over the 13-dataset BEIR subset:

| Model | BEIR-13 nDCG@10 |
|---|---:|
| BM25 | 43.7 |
| TAS-B (dense) | 43.7 |
| Contriever (dense) | 47.5 |
| ColBERTv2 (late interaction) | 49.7 |
| **SPLADE++ CoCondenser-EnsembleDistil** | **50.5** |
| **SPLADE++ CoCondenser-SelfDistil** | **50.7** |

In-domain: MS MARCO dev **MRR@10 38.0**, TREC DL'19 **nDCG@10 73.2**.

**uniCOIL** (Lin & Ma, [arXiv:2106.14807](https://arxiv.org/abs/2106.14807)) — MS MARCO passage dev MRR@10:

| Method | MRR@10 |
|---|---:|
| BM25 | 0.184 |
| BM25 + doc2query-T5 | 0.277 |
| uniCOIL (no expansion) | 0.315 |
| DeepImpact + doc2query-T5 | 0.326 |
| ANCE (dense) | 0.330 |
| COIL-tok (d=32) | 0.341 |
| **uniCOIL + doc2query-T5** | **0.352** |
| COIL-tok + doc2query-T5 | 0.361 |

uniCOIL's selling point is that it runs on **standard Lucene inverted indexes** — "without needing any
specialized retrieval infrastructure."

**Latency** — Lassance & Clinchant, "An Efficiency Study for SPLADE Models"
([arXiv:2207.03834](https://arxiv.org/abs/2207.03834), SIGIR 2022):

> "achieve similar latency (**less than 4ms difference**) as traditional BM25, while having similar
> performance (**less than 10% MRR@10 reduction**) as state-of-the-art single-stage neural rankers"

**BM42** (Qdrant, [qdrant.tech/articles/bm42](https://qdrant.tech/articles/bm42/)) — included for
completeness and because it is the cautionary tale in this slot. Quora, corrected numbers:

| | BM25 (tantivy) | BM25 (sparse) | BM42 |
|---|---:|---:|---:|
| Precision@10 | 0.45 | 0.45 | **0.49** |
| Recall@10 | 0.71\* | **0.89** | 0.85 |

Sparse index for ~530K Quora docs: **13 MB**, 5.6 non-zero elements per document. But Qdrant's own
post-publication correction is the honest headline:

> "Please note that the benchmark section of this article was updated after the publication due to a
> mistake in the evaluation script." … "**BM42 does not outperform BM25 implementation of other vendors.**"
> … "both BM25 and BM42 won't work well on their own in a production environment."

*(\*The tantivy recall@10 was understated pre-correction by a character-escaping bug.)*

**Why this slot matters for the fly pitch.** pgvector — GBrain's actual database — indexes `sparsevec`
with HNSW **up to 1,000 non-zero elements** ([README](https://github.com/pgvector/pgvector#hnsw)). A
SPLADE/uniCOIL document code (typically ~10²–10³ non-zero terms) fits. So the "sparse codes in the
company brain" slot is *already available as a config change* and is occupied by a method with a
+6.8 nDCG@10 margin over BM25 on BEIR. FlyHash would have to beat that, and nobody has published
FlyHash on BEIR or MS MARCO at all.

### 2.3 Binary / int8 quantization with rescoring — the quantizer slot

The canonical figures, from the Sentence Transformers documentation
([sbert.net, Embedding Quantization](https://sbert.net/examples/sentence_transformer/applications/embedding-quantization/README.html)):

- **"32x reduction in memory and storage usage"** (float32 → 1 bit)
- **"preserve up to ~96% of the total retrieval performance"** — with the rescoring/rerank step
- **"improving the retrieval speed by up to 32x as well"**
- int8: 8,192 B → 2,048 B for 1024-d (4×)
- Reference deployment: 41M Wikipedia texts, `mixedbread-ai/mxbai-embed-large-v1`, **5.2 GB RAM +
  52 GB disk** for the indexes, versus **200 GB RAM + 200 GB disk** unquantized

**Critically, this is not a research prototype in GBrain's stack — it is one SQL expression.** pgvector
ships `binary_quantize()` with an HNSW `bit_hamming_ops` index and a documented two-stage rescore:

```sql
CREATE INDEX ON items USING hnsw ((binary_quantize(embedding)::bit(1536)) bit_hamming_ops);

SELECT * FROM (
    SELECT * FROM items ORDER BY binary_quantize(embedding)::bit(1536) <~> binary_quantize($1) LIMIT 20
) ORDER BY embedding <=> $1 LIMIT 5;
```

And it is **also data-independent and training-free** — `binary_quantize` is a deterministic sign
function. Every "no training corpus needed" argument for FlyHash applies verbatim to sign binarization,
which has 2× the measured quality (§2.4).

One more collision: `gbrain-architecture.md` records that GBrain's own
`docs/designs/VECTOR_BACKENDS.md` proposal names "the HNSW 2000/4000-dim cap" as a motivating problem
for a pluggable backend — the seam the fly reports proposed FlyHash slot into. pgvector's FAQ answers
that exact question, and the answer is not FlyHash:

> "**What if I want to index vectors with more than 2,000 dimensions?** You can use half-precision
> vectors … to index up to 4,000 dimensions or **binary quantization to index up to 64,000 dimensions**."

### 2.4 FlyHash — and the within-family comparison nobody ran

The prior report cited H3D ([arXiv:2607.08382](https://arxiv.org/html/2607.08382), 9 Jul 2026) for one
pair of numbers: FlyHash 0.1325 MAP vs BGE-large 0.3431 on CSFCube. I re-read the full HTML and pulled
**every** row. The complete picture is much worse for FlyHash than the corpus reports.

**CSFCube — MAP / NDCG@20 on the "All" facet, best scorer per method, with scoring time (Tables 5 & 7):**

| Method | Code | MAP | NDCG@20 | Time (s) |
|---|---|---:|---:|---:|
| **FlyHash** (jaccard) | 128 bit | **0.1325** | 0.2520 | 10.95 |
| FuzzyHash (levenshtein) | var. | 0.1497 | 0.2963 | **0.25** |
| SimHash (manhattan) | 128 bit | 0.1770 | 0.3601 | 3.62 |
| MinHash (jaccard) | shingle set | 0.2451 | 0.4167 | 17.31 |
| Winnowing (jaccard) | var. | **0.2678** | 0.4337 | 6.22 |
| **BGE-BIHash(small)** (cosine) | **32 bit** | **0.2592** | 0.4597 | 38.5 |
| BGE-LSHash(large) (manhattan) | 128 bit | 0.2705 | 0.4750 | 169.1 |
| BGE(base) full float (manhattan) | 1024×fp | 0.3384 | 0.5591 | 45.8 |
| BGE(large) full float (manhattan) | 1024×fp | **0.3431** | **0.5754** | 69.9 |

**RELISH — test-split MAP / NDCG@20, best scorer per method (Tables 6 & 8):**

| Method | MAP (test) | NDCG@20 | Time (s) |
|---|---:|---:|---:|
| FuzzyHash (levenshtein) | 0.4091 | 0.5632 | 13.91 |
| **FlyHash** (levenshtein) | **0.4305** | 0.5969 | 1744.65 |
| FlyHash (cosine — the cheap config) | 0.4002 | 0.5506 | 0.00 |
| MinHash (jaccard) | 0.4609 | 0.6245 | 4159.82 |
| **SimHash (manhattan)** | **0.4756** | 0.6428 | **0.00** |
| Winnowing (M-jaccard) | **0.4996** | 0.6694 | 1454.27 |
| **BGE-BIHash(small)** (cosine, 32 bit) | **0.5506** | 0.7247 | 1926.9 |
| BGE(large) full float (cosine) | **0.6627** | **0.8239** | 3274.0 |

Four conclusions the corpus does not currently contain:

1. **FlyHash loses its own family fight.** On CSFCube it is *last* of the five semantic-agnostic
   fingerprints. Winnowing doubles its MAP (0.2678 vs 0.1325) at 57% of the time.
2. **SimHash strictly dominates it on both datasets.** CSFCube: +33.6% relative MAP at ⅓ the time.
   RELISH: 0.4756 at 0.00 s vs 0.4305 at 1744.65 s. Whatever role you had in mind for FlyHash, a
   2007-vintage 64-bit simhash does it better and cheaper here.
3. **A 4-byte binarized embedding beats a 16-byte FlyHash code by ~2×.** BGE-BIHash at L=32 bits scores
   0.2592 vs FlyHash's 128-bit 0.1325 on CSFCube (+96% relative) and 0.5506 vs 0.4305 on RELISH (+28%).
   This is the head-to-head the prior report listed as its open question #1 — the nearest published
   version of it exists, and FlyHash loses.
4. **Random-projection hashing on top of embeddings is *worse* than plain sign binarization.**
   BGE-LSHash (random-hyperplane LSH on the same BGE vectors — the closest published proxy for
   "FlyHash on top of embeddings") loses to BGE-BIHash on RELISH at every model size
   (0.4878–0.5389 vs 0.5216–0.5506) while costing 1.5–3× the scoring time, and only ties it on CSFCube.
   The mechanism the fly contributes — a random projection — is the part that does not pay.

**Caveats I am obliged to state.** (a) H3D FlyHashes *token-feature vectors*, not embeddings; the
literal experiment "FlyHash applied to BGE vectors vs `binary_quantize()`" still has not been run by
anyone. (b) H3D's time column is a Python-implementation artifact — 0.00 s for scoring a full RELISH
split is not credible as throughput, and the paper says so ("relative cost within this benchmark rather
than hardware-agnostic throughput"). (c) **One H3D row is broken**: MinHash + mahalanobis reports
MAP 0.9747 with **NDCG@20 = 1.0000** on RELISH — a perfect NDCG that no other row approaches by 0.15.
That is a leakage or degenerate-scorer artifact and it lowers my confidence in H3D as a whole by a
notch; I exclude that row and note that the FlyHash rows I rely on are consistent across both datasets
and both splits.

**Independent replication of the resource accounting.** `Dimitres-Kisimov/bio-efficient-ai`
(GitHub, 0★, pushed 2026-08-10 — **unrefereed, a hobby study, cite accordingly**) reproduces the
*Science* 2017 equal-bits result on real MNIST (FlyHash P@10 0.614 vs LSH 0.419 at 128 bits) and then
does the thing the 2017 paper did not: charges each method for the memory and arithmetic it actually
spends. Its measured conclusion:

| operating point | memory (bits) | proj. MACs | P@10 |
|---|---:|---:|---:|
| FlyHash L=128 | 1,792 | 1,473,920 | 0.614 |
| **classical LSH L=1024** | **1,024** | **802,816** | **0.644** |
| FlyHash L=2048 | 28,672 | 1,473,920 | **0.704** |
| classical LSH L=2048 | 2,048 | 1,605,632 | 0.676 |

> "classical LSH given FlyHash's actual resources dominates on **both** axes at once … the equal-bits
> win is mostly a resource-accounting effect; the real, measured FlyHash advantage is the high-recall
> frontier tip, where one fixed sparse expansion amortises over many read-out bits."

This matters because **every citation of FlyHash in this research corpus quotes the equal-hash-length
comparison** (16.0% → 44.8% mAP, k=4). At equal *bytes*, which is what a company brain pays for, the
margin inverts across the practical range.

### 2.5 The dedup slot's real incumbent

Manku, Jain & Das Sarma, *Detecting Near-Duplicates for Web Crawling*, WWW 2007
([Google Research PDF](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33026.pdf)):
**64-bit simhash fingerprints, Hamming threshold k=3**, run over a multi-billion-page web crawl, with
1.6% of pages identified as near-duplicates. Nineteen years in production, 8 bytes per document, and —
per §2.4 — higher MAP than FlyHash on both H3D datasets. This is what "FlyHash as a dedup gate" has to
beat, and the only published head-to-head says it does not.

---

## 3. The arithmetic the critic asked for (gap 5)

GBrain's live corpus is **155,795 pages** ([README](https://github.com/garrytan/gbrain/blob/master/README.md),
line set 2026-08-12; verified in `v05-gbrain-page-counts.md`), stored as `content_chunks` with
`embedding vector(1536)` under a pgvector HNSW index. Using pgvector's documented storage rules
(`vector` = `4·dims + 8` B; `halfvec` = `2·dims + 8` B; `bit` = `dims/8 + 8` B) plus an HNSW neighbour
list of ~2m=32 four-byte links at m=16:

**Estimated pgvector HNSW index size, d = 1536:**

| chunks | float32 `vector` | `halfvec` | `binary_quantize → bit(1536)` |
|---:|---:|---:|---:|
| 100,000 | 599 MiB | 306 MiB | **31 MiB** |
| 1,000,000 | 5.85 GiB | 2.99 GiB | **313 MiB** |
| 10,000,000 | 58.5 GiB | 29.9 GiB | **3.05 GiB** |

**Read this against the DiskANN result** (1B points, 64 GB RAM, <3 ms, 95% recall@1): a 100K–1M-page
company brain is **three orders of magnitude below** the scale at which anyone has had to be clever.
The float32 index fits in RAM on a $40/month VM. The binary-quantized index fits in a laptop's L3-
adjacent working set. **There is no memory problem for FlyHash to solve at this scale.**

**And FlyHash makes the memory worse, not better.** At the fly's own parameters applied to a 1536-d
input:

| expansion | Kenyon cells m | top-5% active | dense bitmap | sparse `uint16` indices |
|---:|---:|---:|---:|---:|
| 10× | 15,360 | 768 | 1,920 B | 1,536 B |
| 20× | 30,720 | 1,536 | 3,840 B | 3,072 B |
| **40× (the fly)** | **61,440** | **3,072** | **7,680 B** | 6,144 B |

Compare: float32 `vector(1536)` = **6,152 B**; `bit(1536)` = **200 B**.
At the fly's own 40× expansion the code is **25% larger than the raw float32 vector it replaces** and
**38× larger than the binary quantization** — before you have measured a single recall point.

**And it does not fit the stack.** pgvector indexes `sparsevec` with HNSW only **up to 1,000 non-zero
elements**. A 40×-expansion FlyHash code has 3,072 — it cannot be indexed. A 10×-expansion code has 768
— it fits, at `8 × 768 + 16 = 6,160 B` per row, i.e. **exactly the size of the float32 vector**, for
measurably worse recall. To ship FlyHash in GBrain you would write a new pgvector access method.

**Where the money actually goes.** GBrain's own receipts (from `gbrain-architecture.md`,
`completeness-critic.md`): Voyage `rerank-2.5` on every query, ~$0.0006 per contradiction-judge call
(~$0.50/100 queries), $361.49 to extract 100,720 `takes` from 28,256 pages, and a 25-phase nightly
dream cycle. The ANN index is not on that list. Optimising it is optimising the free part.

---

## 4. The fairest possible case FOR fly-inspired hashing

Constructed in good faith, strongest form first.

**F1 — One primitive answers three questions at once.** The fly Bloom filter
([Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093, 2018](https://www.pnas.org/doi/10.1073/pnas.1814448115))
emits a continuous novelty score in [0,1] that is simultaneously **distance-sensitive** (similar items
suppress each other) and **time-sensitive** (aggressive multiplicative decay on exposure, slow additive
recovery). "Is this a duplicate?", "have I seen this recently?" and "is this stale?" are three questions
that every curated brain must answer and that no vector database answers natively. The fly answers all
three with one number. Reported novelty correlations: fly odours 0.657±0.06 vs LSBF 0.537±0.08; SIFT
0.535±0.03 vs LSBF 0.345±0.03 vs **0.002±0.02** for a classical Bloom filter.

**F2 — O(1) state, no per-item storage.** The filter is a single weight vector of length m. At m=2,000
that is 8 KB of mutable state that never grows, regardless of whether the brain holds 100K or 10M pages.
Every alternative novelty gate — ANN-max-cosine, SAGE's vMF estimator — requires the full corpus index
to be present and queried.

**F3 — Genuinely training-free and drift-free.** No corpus, no labels, no fitting. If you swap embedding
models (GBrain's `VECTOR_BACKENDS.md` explicitly contemplates backend churn), a learned quantizer's
calibration is invalidated; a random projection's is not.

**F4 — Streaming with no rebuild.** O(1) insert, no index maintenance, no compaction window. For a
system running 66 cron jobs and a 24/7 ingest daemon, a write-side gate that never needs a maintenance
pause has real operational value.

**F5 — Constant-cost, cheap in absolute terms.** Sparse binary projection is ~20× cheaper than dense
Gaussian at equal quality (*Science* 2017), and the fly Bloom filter update touches only the k active
weights. Microseconds, not the ~1 ms an ANN probe costs.

**F6 — The high-recall Pareto tip is real.** The independent replication (§2.4) found one regime where
FlyHash genuinely wins on both memory and compute: very high recall, where the fixed cost of one sparse
expansion amortises over a long read-out. If a company brain needs recall that dense ANN cannot reach at
acceptable cost, that tip is where to look.

**F7 — Unclaimed ground.** No agent-memory system ships a fly Bloom filter. If it works, it is a
differentiator; if it does not, the experiment is cheap (§7).

---

## 5. The case AGAINST — each of those, answered

**F1 → the score is not fly-specific, and the fly's version is measured against the wrong baseline.**
PNAS 2018 compares the fly filter to LSBF and to a *classical binary Bloom filter*. It never compares it
to the obvious baseline in a RAG system: **`novelty = 1 − max cosine similarity to the existing corpus`**,
computed with one ANN probe against the HNSW index you have already built and paid for. In a company
brain the embedding is a sunk cost — you *must* compute it to index the chunk — so the fly filter's
"cheap, no embedding needed" advantage evaporates. What remains fly-specific is the **AIMD decay
schedule** on the weight vector, and its advantage over a plain exponential decay is untested. SAGE
([arXiv:2605.30711](https://arxiv.org/abs/2605.30711)) already occupies this slot with a von Mises–Fisher
density estimator, published numbers (3.4× lower add-phase API cost, 2.5× lower add-phase latency,
16–18% fewer LLM calls, best average token-F1 vs Mem0 across seven open-weight backbones) and released
code.

**F2 → 8 KB of saved state is not a constraint anyone has.** The corpus that state summarises is 6 GB.
Saving 8 KB against 6 GB is not an engineering argument.

**F3 → sign binarization is also training-free, and is 2× better.** `binary_quantize()` is a
deterministic sign function with no fitted parameters, no calibration and no drift. On H3D it scores
0.2592 (32 bits) against FlyHash's 0.1325 (128 bits). The "data-independent" property is not scarce.

**F4 → HNSW already streams.** pgvector: "an index can be created without any data in the table since
there isn't a training step like IVFFlat." The property FlyHash is sold on is a differentiator against
IVFFlat, not against the incumbent.

**F5 → microseconds versus milliseconds on a path that costs dollars.** A GBrain write already pays for
an embedding API call, a `takes` extraction (measured at $361.49 / 28,256 pages ≈ $0.0128/page), typed-
edge extraction and a nightly 25-phase cycle. Shaving 1 ms of ANN probe off that is invisible.

**F6 → the high-recall tip is on MNIST pixels, not text, and it costs 3,584 B/item.** At L=2048 the
FlyHash code is 28,672 bits — larger than the float32 vector. And the domain is image pixels; H3D is the
only text evidence and it puts FlyHash last in its family.

**F7 → unclaimed ground is also unvalidated ground, and the ecosystem says so.** A GitHub search
(`gh api search/repositories`, 2026-09-10) for FlyHash / fly-Bloom-filter returns 26 repositories: the
most-starred is `dataplayer12/Fly-LSH` at **89★, last pushed 2018-12-23**. The reference implementations
`TeddyHuang-00/FlyHash` and `rithram/fbfc` have **2★ each**. `tfatykhov/membrain` ("Neuromorphic Memory
Bridge") has **0★**. Nine years after *Science* 2017, no vector database ships a FlyHash index and no
memory system ships a fly Bloom filter. That is weak evidence of a missed opportunity and strong
evidence that people who tried it stopped.

**Two objections with no F-counterpart:**

**A1 — FlyHash is not semantically faithful, by construction.** It preserves *input-space* geometry. On
bag-of-tokens input that means lexical matching, and paraphrase destroys it — which is precisely H3D's
stated finding ("semantic-sensitive representations better preserve similarity under content rewriting").
A company brain's hardest retrieval problem is that the same fact is written five different ways by five
different agents. That is the failure mode FlyHash is structurally worst at.

**A2 — the retrieval layer is already at ceiling in this system.** GBrain's LongMemEval-S measurement
(2026-09-06, v0.48.4.0, k=5) reports strict session-level `recall_all@5` of **95.53%** with the reranker
and **93.40%** without. When the index already puts every gold session in the top 5 for 19 of 20
questions, replacing the index cannot move the product. Tan's own framing — "retrieval is the primitive,
being worth retrieving from is the product" — is, on his own numbers, correct.

---

## 6. Verdict, role by role

| Role | Verdict | Why, in one line |
|---|---|---|
| **Semantic index (ANN)** | **NO — refuted** | HNSW/DiskANN dominate on every axis; FlyHash has never been benchmarked on BEIR or MS MARCO; at d=1536 its code is larger than the vector; pgvector cannot index it. |
| **Quantizer for dense embeddings** | **NO — refuted** | `binary_quantize()` is one SQL expression, equally training-free, 32× smaller, ~96% performance retained with rescoring; H3D's nearest proxy (BGE-LSHash) loses to plain sign binarization. |
| **Sparse-code retriever** | **NO — slot occupied** | SPLADE++ 50.5 BEIR nDCG@10 vs BM25 43.7, within 4 ms of BM25 latency, and fits pgvector `sparsevec`. FlyHash has no BEIR number at all. |
| **Dedup gate at ingest** | **NO — the surprise** | SimHash beats FlyHash on both H3D datasets on MAP *and* time; MinHash and Winnowing beat it on MAP; 64-bit simhash at k=3 has been the web-scale answer since 2007. |
| **Novelty / staleness gate on the write path** | **WEAK YES — the only survivor, and unproven** | The *fly Bloom filter* (not FlyHash) is the one primitive giving distance- **and** time-sensitivity in a single closed-form, O(1)-state score. But its published comparisons are to Bloom filters, not to ANN-max-cosine or SAGE's vMF gate, and no one has run those. Confidence that it beats those baselines: **~30%**. |
| **Everything else** | **NONE** | — |

**The one-sentence answer:** *In a 100K–1M page company brain, fly-inspired hashing has no defensible
advantage as an index, quantizer, sparse retriever or dedup gate — SimHash, sign binarization and
SPLADE beat FlyHash on the only benchmark that runs them together, and at 1536 dimensions a FlyHash code
is larger than the float32 vector it would replace — leaving one narrow, unproven role for the fly Bloom
filter as a constant-state novelty-and-staleness clock on the write path.*

---

## 7. What would change this verdict — the crux experiment

Cheap, decisive, and runnable inside GBrain in a week. Two arms, one dataset each.

**Arm A (settles index/quantizer, expected to kill FlyHash):**
Take the existing `content_chunks.embedding vector(1536)`. Build four indexes over the same corpus —
(i) HNSW float32 baseline, (ii) `binary_quantize → bit(1536)` HNSW + SQL rescore, (iii) FlyHash over the
embeddings at 10× expansion / top-5% stored as `sparsevec` (768 nnz — the largest that pgvector will
index), (iv) BioHash at the same code size. Report LongMemEval-S strict `recall_all@5`, index bytes, p50
and p99 latency at 10⁵ and 10⁶ chunks. **Kill condition for FlyHash:** it must beat (ii) on
`recall_all@5` at ≤ the same bytes. Given §2.4 and §3 I put this at **<10%**.

**Arm B (settles the novelty gate — the one worth running):**
Instrument `put_page`. Four gates: (1) fly Bloom filter novelty score (PNAS 2018 update rule,
δ=ε tuned on a held-out week); (2) `1 − max cosine` from one HNSW probe; (3) SAGE's vMF estimator;
(4) 64-bit simhash Hamming ≤3. Measure, over one month of real GBrain ingest: duplicate-write rate,
LLM arbitration calls avoided, add-phase cost and latency, and — the metric that actually matters —
downstream `recall_all@5` and answer accuracy *after* a month of gated versus ungated writes.
**Win condition for the fly:** equal or better dedup at lower cost than (2), **plus** a measurable
staleness benefit that (2) and (4) structurally cannot provide. This is the only experiment in the fly
programme whose outcome I cannot predict.

---

## 8. Confidence and what stays open

- **Index / quantizer / sparse-retriever verdict: high confidence (~90%).** Three independent lines
  agree — H3D's measured numbers, the byte arithmetic on pgvector's documented storage rules, and the
  independent resource-fair replication. The residual 10% is the untested literal experiment
  (FlyHash *on embeddings* vs `binary_quantize`), which I flag honestly as still unrun by anyone.
- **Dedup-gate verdict: medium-high (~75%).** Rests on one benchmark (H3D), which contains a visibly
  broken row (MinHash+mahalanobis, NDCG@20 = 1.0000) and whose timing column is an implementation
  artifact. But FlyHash is beaten by SimHash on both datasets and both splits, which is hard to explain
  as noise.
- **Novelty-gate verdict: low confidence, deliberately.** The fly Bloom filter's advantage over
  ANN-max-cosine and SAGE has never been measured by anyone. I estimate ~30% that it wins; I would not
  bet either way, and Arm B above is the reason to run rather than argue.

**Still open:**
1. FlyHash / BioHash applied to modern sentence embeddings, benchmarked against `binary_quantize()` +
   rescoring on BEIR or LongMemEval. Nobody has run it. (Carried over unresolved from
   `flyhash-sparse-retrieval.md` open question #1; I found the nearest proxy — H3D's BGE-LSHash — and it
   points the same way, but it is a proxy.)
2. Fly Bloom filter vs SAGE's vMF gate vs FadeMem's exponential decay on LoCoMo or LongMemEval.
3. Any FlyHash number on BEIR or MS MARCO. There is none, nine years on. That absence is itself evidence.
4. Whether H3D's MinHash+mahalanobis row is a leak or a scorer bug — it should be raised with the authors
   before anyone cites H3D as a settled result.
5. GBrain's actual `chunk_count` (the `content_chunks` row count as distinct from `page_count`). My
   sizing table brackets 10⁵–10⁷; the true figure would sharpen it but cannot change the conclusion,
   since even 10⁷ chunks binary-quantize to 3 GiB.

---

## Sources

**Primary — benchmarks and papers**
- H3D benchmark (Mao, Lyu et al., 9 Jul 2026), full HTML incl. Tables 5–8 — https://arxiv.org/html/2607.08382 ; abs https://arxiv.org/abs/2607.08382 ; harness https://github.com/DocAILab/Document-Fingerprints
- SPLADE++ — Formal, Lassance, Piwowarski, Clinchant, "From Distillation to Hard Negative Sampling," SIGIR 2022 — https://arxiv.org/abs/2205.04733 ; Table 2 read at https://ar5iv.labs.arxiv.org/html/2205.04733
- SPLADE efficiency — Lassance & Clinchant, "An Efficiency Study for SPLADE Models," SIGIR 2022 — https://arxiv.org/abs/2207.03834
- uniCOIL — Lin & Ma, "A Few Brief Notes on DeepImpact, COIL, and a Conceptual Framework for IR Techniques" — https://arxiv.org/abs/2106.14807 ; Table 2 read at https://ar5iv.labs.arxiv.org/html/2106.14807
- BEIR — Thakur, Reimers, Rücklé, Srivastava, Gurevych, NeurIPS D&B 2021 — https://arxiv.org/abs/2104.08663
- HNSW — Malkov & Yashunin — https://arxiv.org/abs/1603.09320
- DiskANN — Subramanya et al., NeurIPS 2019 — https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf ; library https://github.com/microsoft/DiskANN
- Near-duplicate detection at web scale (simhash, 64-bit, k=3) — Manku, Jain & Das Sarma, WWW 2007 — https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33026.pdf
- FlyHash — Dasgupta, Stevens & Navlakha, *Science* 358:793–796 (2017) — https://www.science.org/doi/10.1126/science.aam9868
- Fly Bloom filter — Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093–13098 (2018) — https://www.pnas.org/doi/10.1073/pnas.1814448115
- BioHash — Ryali, Hopfield, Grinberg & Krotov, ICML 2020 — https://arxiv.org/abs/2001.04907
- SAGE (write-side novelty gate, vMF) — https://arxiv.org/abs/2605.30711 ; code https://github.com/swang1024/SAGE

**Primary — engineering documentation**
- pgvector README (storage rules, HNSW indexable types and dimension caps, `binary_quantize` + rescore recipe, "no training step" note, `sparsevec` 1,000-nnz index limit) — https://github.com/pgvector/pgvector ; raw https://raw.githubusercontent.com/pgvector/pgvector/master/README.md
- Sentence Transformers, Embedding Quantization (32× memory, ~96% retained with rescoring, 41M-Wikipedia deployment figures) — https://sbert.net/examples/sentence_transformer/applications/embedding-quantization/README.html
- Qdrant, "BM42: Attention-Based Sparse Embeddings for Hybrid Search," incl. the post-publication correction — https://qdrant.tech/articles/bm42/
- GBrain README (155,795 pages; pgvector HNSW + BM25 + RRF; LongMemEval-S 95.53% / 93.40%) — https://github.com/garrytan/gbrain/blob/master/README.md

**Independent / unrefereed (flagged as such)**
- `Dimitres-Kisimov/bio-efficient-ai` — resource-fair FlyHash vs classical LSH replication on real MNIST, 0★, pushed 2026-08-10 — https://github.com/Dimitres-Kisimov/bio-efficient-ai
- Ecosystem census via `gh api search/repositories` (2026-09-10): `dataplayer12/Fly-LSH` 89★ (last push 2018-12-23), `TeddyHuang-00/FlyHash` 2★, `rithram/fbfc` 2★, `tfatykhov/membrain` 0★.

**Internal corpus cross-references**
- `findings/flyhash-sparse-retrieval.md` (the report this one adversarially tests)
- `findings/completeness-critic.md` §A.5, §C.10 (the gap this task fills)
- `findings/gbrain-architecture.md` (pgvector schema, `VECTOR_BACKENDS.md` proposal, cost receipts)
- `findings/v05-gbrain-page-counts.md` (the 155,795 figure and its dating)

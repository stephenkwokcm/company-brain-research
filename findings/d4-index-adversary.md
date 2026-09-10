# d4 — FlyHash / BioHash as a pluggable `vector.backend`: the adversarial design

**Angle:** index adversary. **Date of work:** 2026-09-10. **Worker:** design agent (Claude Opus 5).
**Task key:** `d4-index-adversary`. **Target system:** `garrytan/gbrain` @ v0.48.5.0.

> **VERDICT: DO NOT BUILD.** I specified the FlyHash/BioHash `vector.backend` proposal at
> implementation grain, pre-registered a kill criterion, then ran the experiment the whole corpus
> says nobody has ever run — FlyHash and BioHash computed **on top of real dense text embeddings**,
> scored against `binary_quantize()` on the same embeddings, in the same database, on the same
> corpus. **The kill criterion fired on every configuration.** At equal storage, sign binarization
> beats FlyHash by **+53% relative recall@10** (0.7577 vs 0.4948) and by **+19 points after exact
> rescoring** (0.9918 vs 0.8339); measured in pgvector 0.8.6, a FlyHash column costs **2.4× the
> bytes** and **2.2× the query latency** of a `bit(1024)` column; and the only FlyHash setting that
> reaches quality parity is **refused by pgvector's index** with the error
> `sparsevec cannot have more than 1000 non-zero elements for hnsw index`.
>
> **What survives:** (1) the *Science* 2017 result itself replicates on modern text embeddings — at
> equal **hash length** FlyHash beats random-hyperplane LSH by +82% relative (0.4948 vs 0.2712), so
> the fly claim is true and the corpus should stop implying it is not; it is just accounted in the
> wrong currency. (2) A *non-biological* backend — `binary_quantize` + rescore — delivers everything
> the fly proposal promised (22.5× smaller, 1.9× faster, training-free, streaming, lifts the
> dimension cap to 64,000) and is **one DDL change**; I spec it as **D4-ALT** below. (3) On the write
> path, my dedup measurement moves the goalposts *against* the fly gate again: the free baseline
> (one ANN probe you have already paid for) tops it, and lexical SimHash — which `v10b` nominated as
> the incumbent — is the worst method tested on semantic rewrites (0.263 top-1 on heavy edits).

---

## 0. What is new in this report

Everything in §5 is a first-party measurement made today. Three of the numbers close open questions
that four prior reports in this corpus explicitly flagged as unrun by anyone:

| Open question | Where it was flagged | Status after this report |
|---|---|---|
| "FlyHash / BioHash applied to modern sentence embeddings, benchmarked against `binary_quantize()` + rescoring. **Nobody has run it.**" | `v10b` open #1; `flyhash-sparse-retrieval.md` open #1 | **RUN.** §5.1–5.2. FlyHash loses at equal bytes by 53% relative, wins at equal hash length by 82% relative. |
| "That exact cell (BGE embedding → FlyHash) is the one H3D leaves empty — unclaimed ground and a cheap crux experiment." | `v10a` implication 3 | **FILLED.** §5.1. Also filled for BioHash (trained), which the corpus never tested at all. |
| Can pgvector actually index a fly code, and at what size? | implied by `gbrain-architecture.md` open #4, `v10b` §3 (arithmetic only) | **MEASURED in-database.** §5.3, incl. the verbatim pgvector refusal at k>1000. |

Method summary: 3,187 chunks (GBrain's own chunker parameters — 300 words, 50-word overlap,
`src/core/chunkers/recursive.ts`) drawn from 158 real documents; embedded with **BAAI/bge-m3 at
1,024 dimensions** — the exact width GBrain sets as its new-install default
(`src/core/ai/defaults.ts`, `voyage-4` @ 1024). Ground truth is exact float32 cosine top-10, self
excluded. All code, embeddings and raw output are in the scratchpad (§13).

---

## 1. The mechanism borrowed, stated in its strongest form, and its fidelity

**Mechanism: FlyHash** (Dasgupta, Stevens & Navlakha, *Science* 358(6364):793–796, 2017,
[10.1126/science.aam9868](https://www.science.org/doi/10.1126/science.aam9868)) — the *Drosophila*
olfactory circuit as a locality-sensitive hash. Three departures from classical LSH:

1. **Sparse binary random projection** rather than dense Gaussian — each of *m* Kenyon cells sums a
   handful of randomly chosen projection neurons (~6 of 50 in the fly), a claimed ~20× arithmetic
   saving at near-identical quality.
2. **Dimensionality *expansion*** (m ≫ d) rather than contraction — 40× in the fly (50 PNs → 2,000 KCs).
3. **Winner-take-all sparsification** — keep the top ~5% of activations as a sparse binary tag.

**Variant: BioHash** (Ryali, Hopfield, Grinberg & Krotov, ICML 2020,
[arXiv:2001.04907](https://arxiv.org/abs/2001.04907)) replaces the *random* expansion with one
*learned* by a local Hebbian rule, fixing FlyHash's data-independence — at the cost of the property
that made FlyHash attractive in the first place.

**Fidelity: Deep as a mechanism; wrong slot as a design proposal.** I concur exactly with
`g07-neuro-mechanism-inventory.md` §1 ("*the algorithm is the circuit — one sparse matmul and a
top-k … But the role the prior reports keep gesturing at (semantic index) is the role where it
demonstrably loses*"). There is nothing to re-derive: the fly's own numbers *are* the default
parameters. This is the highest-fidelity transplant available and it is being proposed for the one
slot where fidelity does not help.

**The steelman, fairly stated.** Every claimed FlyHash advantage over the incumbent, in its
strongest form, is:

- **S1 — Data-independent.** No training corpus, no fitted codebook, no calibration to invalidate
  when the embedding model changes. (GBrain's own `VECTOR_BACKENDS.md` contemplates backend churn.)
- **S2 — Streaming.** O(1) insert, no rebuild, no compaction window, for a system running 66 crons.
- **S3 — Lifts the dimension cap.** `PGVECTOR_HNSW_VECTOR_MAX_DIMS = 2000` (verified in
  `src/core/vector-index.ts:19`) is problem #1 in GBrain's own design doc; a sparse code is
  dimension-agnostic.
- **S4 — Short-code superiority.** The *Science* result: 3× LSH mAP at short hash lengths.
- **S5 — Cheap arithmetic.** Sparse binary projection, ~20× fewer MACs than dense Gaussian.
- **S6 — Unclaimed ground.** No vector database ships it. If it works it is a differentiator.

§5 tests S4 (it is **true**, and it is the wrong axis), §5.3 tests S3 (it is **false in pgvector** —
the cap is *lower*, not higher), and §10 shows S1, S2 and S5 are each matched by an incumbent that
is already in GBrain's dependency tree.

---

## 2. Exact insertion point in GBrain

This proposal has an unusually clean seam, which is why it deserves to be taken seriously enough to
be killed properly rather than waved off. The seam is real, it is documented, and it is unbuilt.

| Layer | Artifact | Exact path / symbol | What the fly backend must change |
|---|---|---|---|
| Config key | design doc, status **proposal** at v0.48.5.0 | [`docs/designs/VECTOR_BACKENDS.md`](https://github.com/garrytan/gbrain/blob/master/docs/designs/VECTOR_BACKENDS.md) — `vector.backend = pgvector \| pgvectorscale \| vchord \| auto` (default `pgvector`) | add `flyhash`; resolution chain `GBRAIN_VECTOR_BACKEND` env → config `vector.backend` → `'pgvector'` |
| Index DDL emitter | `chunkEmbeddingIndexSql(dims)` | [`src/core/vector-index.ts:25`](https://github.com/garrytan/gbrain/blob/master/src/core/vector-index.ts) (constant `CHUNK_EMBEDDING_HNSW_INDEX` at :22) | emit `USING hnsw (e_fly sparsevec_cosine_ops)` |
| Dimension policy | `hnswMaxDimsForType` / `hnswIndexExpected` | ibid. :33, :38; constants `PGVECTOR_HNSW_VECTOR_MAX_DIMS = 2000`, `..._HALFVEC_MAX_DIMS = 4000` at :19–20 | needs a *third* cap — an nnz cap, not a dims cap (§5.3) |
| Schema | the column itself | [`src/schema.sql:302`](https://github.com/garrytan/gbrain/blob/master/src/schema.sql) `embedding vector(1536)`; index at `:336` `CREATE INDEX idx_chunks_embedding ON content_chunks USING hnsw (embedding vector_cosine_ops)` | add `embedding_fly sparsevec(m)` + partial HNSW; the doc's own precedent is the multimodal partial index at `:341–344` |
| Candidate-pool GUC | `hnswEfSearchFor(candidateLimit)` | `src/core/vector-index.ts:63` (defaults `HNSW_EF_SEARCH_DEFAULT = 40`, max 1000) | becomes `backendCandidateGucs(backend, candidateLimit)` per the design doc |
| Cache correctness | `knobsHash` + `KNOBS_HASH_VERSION` | `src/core/search/mode.ts` (per VECTOR_BACKENDS.md §3) | fold `vb=flyhash`; version bump in the same commit |
| Rebuild path | `dropAndRebuild` atomic swap | `src/core/vector-index.ts:186` | exposed as `gbrain embed reindex --backend=flyhash` |
| Retrieval call site | vector arm of the hybrid recall stack | `src/core/search/hybrid.ts` (161,896 bytes; per `gbrain-architecture.md` §3) | one arm of RRF fusion; the graph/BM25/rerank stages are untouched |
| Doctor | new check | `src/commands/doctor/checks/` | requested-vs-resolved backend, `pg_index ⋈ pg_am.amname` mismatch |

**Three things about this seam that decide the verdict before any benchmark:**

1. **The design doc's own acceptance bar is not quality.** `VECTOR_BACKENDS.md` §Non-goals: *"No
   benchmark bake-off in-repo — the eval bar is **does an over-4000-dim model get indexed search
   back**, proven by the gated e2e, not a research comparison."* That bar is already met by
   pgvector itself: `binary_quantize` indexes **up to 64,000 dimensions**
   ([pgvector README FAQ](https://github.com/pgvector/pgvector#what-if-i-want-to-index-vectors-with-more-than-2000-dimensions)).
   The fly backend's headline motivation is satisfied by a function already compiled into the extension.
2. **The doc's own gated e2e test *is* my metric.** *"assert … `searchVector` returns the same rows
   as the pgvector baseline on a small fixture."* Fidelity-to-exact-dense-ranking is not a metric I
   chose to disadvantage the fly; it is the contract GBrain writes for a backend.
3. **Phase 2 is deliberately sequenced second and never auto-selected** precisely because a backend
   that needs *its own column type* must also touch `readContentChunksEmbeddingDim`, the column
   registry and the `::vector` casts in both engines. FlyHash needs its own column type
   (`sparsevec`) **and** its own operator class **and** a second stored representation. It is
   strictly more invasive than the phase the maintainers already judged too invasive to auto-enable.

---

## 3. Algorithm sketch and parameters

```
FLYHASH-ENCODE(x ∈ R^d) -> k sorted indices in [0, m)
  parameters: expansion ρ (m = ρ·d), fan-in f, sparsity k
  offline, once: M ∈ {0,1}^{m×d}, each row samples f distinct input dims uniformly (seeded)
  1. x' ← x − μ            (μ = corpus mean; see NOTE)
  2. y  ← M x'             (sparse binary matmul: m·f MACs)
  3. return TOP-K(y)       (winner-take-all; store as sparsevec(m) with k unit weights)

DISTANCE(a, b) = Hamming = 2(k − |A ∩ B|)     [equivalently rank by intersection at fixed k]
```

Parameters swept: **ρ ∈ {10, 20, 40}** (the fly's own value is 40); **f ∈ {12, 102, 205}** (12 = the
fly's absolute fan-in of ~6-of-50 scaled to d=1024 at that ratio; 102 = Dasgupta's 10% sampling
rate; 205 = 20%); **k ∈ {16 … 1024}** (the fly's 5% of m would be 1,024 at ρ=20).
BioHash uses the Krotov–Hopfield bio-learning rule (p=2, Δ=0.4, 60 epochs, batch 64, decaying lr),
m ∈ {2048, 8192}, then the same TOP-K read-out.

> **NOTE — a porting result worth recording.** With **constant fan-in per row**,
> `M(x − c·1) = Mx − c·f·1`, a uniform shift across all m units, so winner-take-all is invariant to
> it. Therefore **the fly's per-stimulus divisive/subtractive normalisation step — its concentration-
> invariance mechanism — is a mathematical no-op for L2-normalised embeddings**. My "raw" and
> "per-vector-centred" arms produced *bit-identical* results (§5.1). Only *corpus*-mean centring does
> anything, and it is not the fly's operation. One of the three published departures from LSH
> silently does not transfer.

---

## 4. Benchmark, metric, baseline — pre-registered before running

- **Corpus.** 3,187 chunks / 158 documents, chunked at GBrain's own 300-word / 50-word-overlap
  parameters. Deliberately company-brain-shaped: heavily overlapping, topically narrow, mixed prose,
  markdown, SQL and TypeScript — i.e. rich in near-duplicates, which is the regime a curated brain
  actually lives in.
- **Embeddings.** BAAI/bge-m3, 1,024-d, L2-normalised — the width GBrain defaults to.
- **Primary metric.** `recall@10` of each code's top-10 against **exact float32 cosine top-10**
  (self excluded). This is the `vector.backend` contract as GBrain writes it (§2.3).
- **Secondary metric.** `recall@10` after **exact rescoring of the code's top-100** — pgvector's
  documented production recipe for binary quantization, and the only fair way to score a lossy code.
- **Accounting.** Bytes per row under **pgvector's documented storage rules**
  (`vector` = 4d+8; `halfvec` = 2d+8; `bit` = L/8+8; `sparsevec` = 8·nnz+16), then **measured** in a
  live pgvector 0.8.6 instance (§5.3). FlyHash is *also* credited with a hypothetical packed-index
  encoding (k·⌈log₂m/8⌉ bytes) that pgvector does not offer — the most generous accounting available.
- **Baselines.** float32 (reference), `halfvec`, int8 scalar quantization, `binary_quantize` (with
  and without corpus centring), random-hyperplane LSH/SimHash at L ∈ {16 … 4096} bits.
- **Noise floor.** Two independent seeds for LSH L=128 gave 0.4130 and 0.4220 → **±0.01**. Every
  comparison I draw a conclusion from is 5–35× that.

**Pre-registered kill criterion (written before the run, §8 restates it formally):** *FlyHash must
reach ≥ the `recall@10`-after-rescoring of `binary_quantize` → `bit(1024)` at **≤ the same stored
bytes per row**, in a configuration pgvector will actually index.* Anything less and the backend is
strictly dominated and must not be built.

---

## 5. Results

### 5.1 The equal-bytes frontier (the missing cell, now filled)

n = 3,187 queries. `resc` = recall@10 after exact rescoring of the code's top-100.

| Code | pgvector bytes/vec | recall@10 | recall@10 + rescore |
|---|---:|---:|---:|
| `vector(1024)` float32 — reference | 4,104 | 1.0000 | — |
| `halfvec(1024)` | 2,056 | 0.9972 | — |
| int8 scalar quant | 1,032 | 0.9853 | — |
| **`binary_quantize(x)` → `bit(1024)`** (pgvector default) | **136** | 0.7327 | **0.9912** |
| **`binary_quantize(x−μ)` → `bit(1024)`** | **136** | **0.7577** | **0.9918** |
| SimHash/LSH 1024 bits | 136 | 0.7287 | 0.9730† |
| SimHash/LSH 4096 bits | 520 | 0.8146 | — |
| **FlyHash** ρ=20, m=20480, f=102, **k=64** | **528** (packed: 128) | **0.4948** | **0.8339** |
| FlyHash k=128 | 1,040 (256) | 0.6191 | 0.9356 |
| FlyHash k=256 | 2,064 (512) | 0.7051 | 0.9792 |
| FlyHash k=512 | 4,112 (1,024) | 0.7692 | 0.9910 |
| FlyHash k=1024 | 8,208 (2,048) | 0.8098 | 0.9937 — **unindexable, see §5.3** |
| BioHash (trained) m=8192, k=64 | 528 (128) | 0.4544 | 0.8486 |
| BioHash (trained) m=8192, k=256 | 2,064 (512) | 0.6985 | 0.9830 |

† rescore-50 for this row.

**Read this three ways.**

1. **At the same real database bytes, it is not close.** `bit(1024)` costs 136 B and scores
   0.7577 / 0.9918. The *cheapest indexable* FlyHash code costs **528 B — 3.9× more** — and scores
   0.4948 / 0.8339. Sign binarization is **+53% relative recall@10** and **+19 points after
   rescoring**, at **a quarter of the storage**.
2. **Even under the storage accounting FlyHash does not get in pgvector** (packed 2-byte indices,
   128 B at k=64), it still loses: 0.4948 vs 0.7577 at 136 B.
3. **The price of parity is 30×.** To match `binary_quantize`'s 0.9918, FlyHash needs **k=512** →
   **4,112 B/vec**, i.e. **30× the storage** of the code it is trying to replace, and *more storage
   than the float32 vector it is supposed to compress*. One further doubling — the fly's own 5%
   sparsity at ρ=20 — is refused by the index entirely.

**BioHash does not rescue it.** The learned expansion, trained on the evaluation corpus itself (an
optimistically in-domain setting a production system could not match), lands **below** untrained
FlyHash at matched k on raw recall (0.4544 vs 0.4948 at k=64) and marginally above it after
rescoring (0.8486 vs 0.8339) — while giving up S1 (data-independence) and S2 (streaming without
rebuild) outright. Fair caveat: BioHash is designed to improve *class-level semantic* mAP, not to
reproduce a dense ranking, so this metric under-serves its published purpose. But reproducing the
dense ranking is the `vector.backend` contract; a code that beat the dense vector on end-task
quality would be a change of *embedding*, not of *backend*, and belongs in a different design.

### 5.2 The resource-accounting inversion — why the *Science* result is true and irrelevant here

This is the most important finding in the report, and it exonerates the fly literature while killing
the proposal.

| Comparison axis | FlyHash | Random-hyperplane LSH | Winner |
|---|---|---|---|
| **Equal hash length** (k=64 indices vs 64 bits) — *the Science 2017 protocol* | **0.4948** | 0.2712 | **FlyHash, +82% relative** |
| **Equal bytes** (128–136 B) | 0.4948 | 0.7287 (L=1024) / **0.7577** (`binary_quantize`) | **Binarization, +53% relative** |

Both rows are from the same run on the same embeddings. **The fly claim replicates on modern text
embeddings — this is, as far as this corpus can establish, the first time it has been shown there.**
And it is a category error to bill it as a storage win, because a FlyHash "hash length" of 64 is 64
*indices into a 20,480-dimensional space* = 64 × 15 bits ≈ **960 bits**, whereas an LSH hash length
of 64 is **64 bits**. The paper's axis is *number of stored symbols*; a database's axis is *bytes*.
At a fixed byte budget, spending them on 1,024 one-bit hyperplanes beats spending them on 64
fifteen-bit indices, by a wide margin.

This independently confirms — now directly on embeddings, rather than on MNIST pixels — the
resource-fair replication `v10b` §2.4 found (`Dimitres-Kisimov/bio-efficient-ai`: *"the equal-bits
win is mostly a resource-accounting effect"*). Two independent methods, two domains, same inversion.
**Any future citation of "16.0% → 44.8% mAP" in this project must carry the phrase "at equal hash
length," or it misstates the finding.**

### 5.3 Measured in the actual database — pgvector 0.8.6, PostgreSQL 17, 100,000 rows, d=1024

| Column | table+TOAST B/row | HNSW index B/row | **total B/row** | HNSW query (ef_search=40) | indexable? |
|---|---:|---:|---:|---:|---|
| `vector(1024)` — **GBrain's default** | 5,582 | 8,144 | **13,726** | **7.34 ms** | yes |
| **`bit(1024)`** (`bit_hamming_ops`) | 178 | 431 | **609** | **3.81 ms** | yes |
| `sparsevec(20480)`, k=64 (FlyHash) | 585 | 855 | **1,440** | **8.31 ms** | yes |
| `sparsevec(20480)`, k=1024 (FlyHash at parity) | 8,653 | — | — | — | **NO** |

The refusal is verbatim from the server:

```
ERROR:  sparsevec cannot have more than 1000 non-zero elements for hnsw index
```

Four conclusions, all measured rather than argued:

- **Binary quantization is a 22.5× total-storage reduction and a 1.9× latency reduction** against
  GBrain's current column, at 99.2% recall@10 with rescoring.
- **The FlyHash column is 2.4× larger and 2.2× slower than the `bit` column** — and *slower than the
  float32 vector it was supposed to accelerate*.
- **The FlyHash code at quality parity is physically larger than the float32 vector**: 8,653 vs
  5,582 B/row measured — 1.55×. `v10b` predicted this arithmetically (7,680 B vs 6,152 B at
  d=1536); it is now confirmed on the scale and in the engine that matter.
- **Claim S3 inverts.** The fly backend was pitched as lifting pgvector's 2,000-dimension cap. In
  reality it *introduces a tighter cap* — 1,000 non-zeros — that binds at exactly the sparsity the
  fly itself uses (5% of m). Meanwhile `binary_quantize` indexes to 64,000 dimensions. The proposal
  makes the problem it was invented to solve strictly worse.

**At GBrain's own scale**, using these measured per-row figures and `g02`'s measured 2.40
chunks/page (155,795 pages → 373,908 chunks):

| Corpus | `vector(1024)` total | `bit(1024)` total | FlyHash k=64 total |
|---|---:|---:|---:|
| 373,908 chunks (155,795 pages) | **5.13 GB** | **0.23 GB** | 0.54 GB |
| 2,400,000 chunks (1M pages) | **32.94 GB** | **1.46 GB** | 3.46 GB |

My 8,144 B/row index measurement independently reproduces `g02`'s 8,192 B/vec at 1024-d to within
0.6% — a useful cross-check that both measurements are real.

### 5.4 The write-side gate — where the corpus retreated to, tested properly

`v10b` refuted "FlyHash as a dedup gate" using H3D's *lexical* SimHash numbers and nominated
Manku's 2007 64-bit simhash as the incumbent. I tested that claim directly, on the case a company
brain actually faces: **the same content restated**. 1,200 probes = 400 source chunks × three
perturbations (10% word deletion; 25% deletion + sentence shuffle; a 60% window). Metric: does the
method rank the source chunk #1 out of 3,187?

| Method | bytes | light edit | heavy edit | 60% window | **all** |
|---|---:|---:|---:|---:|---:|
| **float32 cosine — the free baseline** (one ANN probe you already pay for) | 4,104 | 0.922 | 0.833 | 0.772 | **0.843** |
| `binary_quantize(x−μ)` → `bit(1024)` | 136 | 0.927 | 0.807 | 0.767 | **0.834** |
| FlyHash on embedding, k=1024 | 8,208 | 0.927 | 0.833 | 0.772 | 0.844 |
| FlyHash on embedding, k=256 | 2,064 | 0.925 | 0.823 | 0.762 | 0.837 |
| **FlyHash on embedding, k=64** (the indexable, byte-competitive one) | 528 | 0.917 | 0.760 | 0.723 | **0.800** |
| SimHash/LSH on embedding, 64 bits | 16 | 0.820 | 0.603 | 0.485 | 0.636 |
| **lexical 64-bit SimHash over 3-shingles** (Manku 2007) | **8** | 0.772 | **0.263** | 0.735 | **0.590** |

**This corrects `v10b` in one direction and hardens it in another.**

- *Correction:* lexical SimHash is **not** the incumbent to beat for a company brain's dedup gate. It
  collapses to **0.263** on a paraphrase-shaped edit — the exact failure mode `v10b` §A1 identified
  for FlyHash-on-tokens applies with equal force to SimHash-on-tokens. Its 8 bytes are excellent for
  byte-near-identical copies and useless for "the same fact, written differently," which is the
  duplicate class Tan's librarian actually confronts. **The synthesis should not say "SimHash beats
  FlyHash for dedup" without the qualifier "on lexical fingerprints."**
- *Hardening:* the fly gate's real competitor is not a Bloom filter and not SimHash — it is **the
  exact cosine probe against the HNSW index the brain has already built and paid for** (0.843, and
  measured at 7.3 ms in §5.3), or its 136-byte binarized shadow (0.834). FlyHash at a comparable
  byte budget scores 0.800. To *tie* the free baseline it needs k=1024 — 8,208 B/vec, unindexable.
  **The bar for the surviving fly proposal (the write-side novelty gate) is therefore higher than
  `v10b` assumed, not lower.**

What the fly Bloom filter still has that nothing in this table has is the **time axis**: AIMD decay
gives duplication *and* staleness in one number with O(1) state. That residue is real, and it is
d1/d2's territory, not mine. My contribution to it is the corrected baseline it must beat.

### 5.5 Scan-cost sanity check (out-of-database, n = 200,000)

| Representation | ms/query (brute force) | bytes scanned |
|---|---:|---:|
| float32 `vector(1024)` dot | 6.8 | 819 MB |
| `bit(1024)` Hamming (popcount) | 7.1 | **26 MB** |
| FlyHash `sparsevec(20480)` k=64 | 11.0 | 106 MB |
| FlyHash k=256 | 63.7 | 413 MB |
| FlyHash k=1024 | 291.2 | 1,642 MB |

Caveat stated plainly: SciPy CSR mat-vec is not an optimised inverted index and NumPy's popcount is
not SIMD-tuned, so treat the *times* as indicative and the *bytes scanned* as exact. The in-database
numbers in §5.3 are the ones to cite.

---

## 6. Expected effect size, from published numbers — and how it landed

Pre-registered prediction, derived before running, from the three published sources available:

| Source | What it predicted for this experiment |
|---|---|
| H3D ([arXiv:2607.08382](https://arxiv.org/abs/2607.08382)) — BGE-LSHash loses to BGE-BIHash (sign binarization) at every model size on RELISH | random-projection hashing *on top of* embeddings < plain sign binarization |
| `bio-efficient-ai` resource-fair MNIST replication | FlyHash's equal-bits win inverts once you charge for bytes |
| *Science* 2017, k=4: 16.0% → 44.8% mAP | FlyHash **wins** at equal hash length |
| `g02` measured latency budget: ANN scan = 0.14% of an answered question | even a total win is worth ≤0.14% end-to-end |

**Predicted:** FlyHash loses at equal bytes by 20–60% relative, wins at equal hash length, and the
ceiling on any index-side victory is ~0.14% of a user-visible answer.
**Observed:** loses at equal bytes by **53% relative** (0.4948 vs 0.7577); wins at equal hash length
by **82% relative** (0.4948 vs 0.2712). Both predictions landed inside their bands. The one thing I
did not predict is how badly it loses *in the database*: 2.4× the bytes **and** 2.2× the latency
**and** an index refusal at the fly's own sparsity.

**Effect size on the product, if it had won.** `g02` measured the ANN scan at ~4.5 ms inside a
~3,272 ms answered question. A FlyHash backend that was free, instant and **lossless** would improve
an answered question by **at most 0.14%**. GBrain's own LongMemEval-S retrieval already sits at
95.53% `recall_all@5` with the reranker and 93.40% without (`v01`), so there is ~4 points of
head-room in the *entire* retrieval stack, of which the index is a fraction. **There is no version
of this proposal whose success would be measurable by a user.**

---

## 7. Cost

| Line | Fly backend (`vector.backend=flyhash`) | D4-ALT (`binary_quantize`) |
|---|---|---|
| Engineering | **14–19 dev-days**: new column + partial index + operator-class plumbing, `sparsevec` nnz-cap policy (a *third* cap alongside dims), a second stored representation and its drift/invalidations, `knobsHash` fold + version bump, `dropAndRebuild` path, doctor check, engine parity for PGLite (which has no such column plan), 2 new e2e gates, plus a rescoring stage because raw code recall is 0.49 | **3–5 dev-days**: one generated column, one index DDL, one two-stage query in `hybrid.ts`, one `knobsHash` fold, one doctor check |
| Re-embedding cost | **$0** (both operate on the existing vector) | **$0** |
| One-off compute | Index build for a 3rd representation; measured 3.9 s / 100K rows for `sparsevec` k=64, so ~15 s at 374K — trivial | 3.4 s / 100K → ~13 s at 374K |
| Steady-state storage delta at 373,908 chunks | **+0.54 GB** (a *third* copy alongside the 5.13 GB it does not replace) | **−4.90 GB** if it replaces the HNSW float index (5.13 → 0.23 GB) |
| LLM tokens | none for either | none for either |
| Hosting consequence (`g02` Supabase table) | none; possibly worse | **1M-page brain: 32.9 GB → 1.5 GB index footprint; drops a 2XL ($410/mo) to a Large ($110/mo)** |
| Ongoing maintenance | a bespoke access path nobody else runs, drifting against pgvector releases | a documented pgvector recipe with upstream tests |

Note the asymmetry in the last row: `binary_quantize` is *maintained by the extension*; a fly
backend is maintained by whoever wrote it, forever, inside a repo `g02` shows is already carrying
contradictory cost documentation and a 53× budget-overrun incident.

---

## 8. Kill criterion — pre-registered, and it fired

**Stated before the run:**

> **K1.** FlyHash (or BioHash) must reach ≥ the recall@10-after-rescore of `binary_quantize` →
> `bit(1024)` at **≤ the same stored bytes/row**, in a configuration pgvector will index.
> **K2.** It must not increase p50 HNSW query latency versus that baseline.
> **K3.** Its best configuration must be indexable at all.
> Failing **any one** of K1–K3 ⇒ abandon the backend; do not build; do not propose a variant.

**Outcome — all three failed:**

| | Baseline (`bit(1024)`) | Best byte-competitive FlyHash | Result |
|---|---|---|---|
| **K1** recall@10 + rescore at ≤136 B | **0.9918** at 136 B | 0.8339 at 528 B (0.8339 at 128 B packed) | **FAIL** by 15.8 points, at 3.9× the bytes |
| **K2** HNSW p50 | **3.81 ms** | 8.31 ms | **FAIL** (2.2× slower) |
| **K3** indexable at best config | yes | k=1024 → `ERROR: sparsevec cannot have more than 1000 non-zero elements` | **FAIL** |

The margins are 5–35× the ±0.01 seed noise floor. **No parameter in the sweep — ρ ∈ {10,20,40},
f ∈ {12,102,205}, k ∈ {16…1024}, three input normalisations, and a trained BioHash at two widths —
produced a configuration that passes.** This is not a close call awaiting a better tuning, and I
recommend the judging phase treat any d1–d5 proposal that lists FlyHash or BioHash under
`vector.backend` as refuted by this result rather than as an open question.

---

## 9. Risks and what prior negative results say

**If someone builds it anyway, these are the failure modes, in order of likelihood.**

1. **Paraphrase brittleness compounds.** FlyHash preserves *input-space* geometry. On embeddings that
   is fine — but the code discards magnitude and keeps only rank order of m random subset sums, and
   §5.4 shows it degrades faster than sign binarization exactly on rewritten content (0.760 vs 0.807
   on heavy edits). A company brain's hardest retrieval problem is one fact written five ways.
2. **A third representation is a third drift surface.** GBrain already tracks
   `content_chunks.embedded_text_hash` (schema.sql:308, added v133 for exactly this reason) to catch
   content drift against one embedding. A second derived code doubles that bookkeeping, and its
   invalidation is not covered by `invalidateContentDriftEmbeddings`.
3. **PGLite parity breaks.** `VECTOR_BACKENDS.md` is explicit that PGLite "always resolves
   `pgvector`" and that engine parity of *behaviour* is a contract. A backend whose recall set
   differs by 25 points cannot satisfy "same query results" across engines; it forces either a
   permanent two-tier quality story or a cache-key partition.
4. **The nnz cap is a footgun.** The dims cap fails *loudly* today (`chunkEmbeddingIndexSql` emits a
   comment and falls back to exact scan). The nnz cap fails at **`CREATE INDEX`** time on a table
   that already has data — after the encode pass has run.
5. **Opportunity cost is the real risk.** `g02` measured curation at **222×–4,514×** the embedding
   cost. Fourteen dev-days spent on the free part of the system is fourteen days not spent on the
   part where the money and the quality are.

**Prior negative results this must answer, and does not:**

- **H3D** (arXiv:2607.08382, Jul 2026): FlyHash is **last of five** semantic-agnostic fingerprints on
  CSFCube MAP (0.1325 vs Winnowing 0.2678), and BGE-LSHash — the closest published proxy for
  "random projection on top of embeddings" — loses to plain sign binarization at every model size on
  RELISH. My §5.1 is the direct, on-embeddings version of that proxy, and agrees.
- **Kleyko & Rachkovskij** (arXiv:2501.14741): the authors of the most careful FlyHash design study
  **do not claim** it beats dense methods; they position optimised FlyHash for *memory-constrained*
  settings. §5.3 shows a company brain is not memory-constrained: a 1M-page brain binary-quantizes
  to **1.46 GB**, and DiskANN serves a *billion* points on one 64 GB box.
- **Ecosystem silence** (`v10b` census, 2026-09-10): nine years after *Science* 2017, the
  most-starred FlyHash repo is `dataplayer12/Fly-LSH` at 89★, **last pushed 2018-12-23**; the
  reference implementations have 2★ each; no vector database ships it.
- **`g02`'s latency budget**: the ANN scan is 0.14% of an answered question. Even a total victory is
  unobservable.
- **BioVSS** (ICDE 2025, arXiv:2412.03301) is the one genuine scale win for bio-hashing and must not
  be miscited: it is **vector-set** search under Hausdorff distance, a different problem. `>50×
  speedup over linear scan` is not `beats HNSW at RAG`.

**The strongest counter-argument to my own verdict, stated fairly.** My primary metric rewards
*fidelity to the dense ranking*, which by construction the dense vector wins. If a sparse fly code
were *semantically better than the embedding it came from* — as BioHash claims for class-level mAP —
my metric would never see it. Two answers: (a) that is the `vector.backend` contract GBrain itself
writes, so within this design slot the metric is correct; (b) a code that improves on its own
embedding is an **embedding-model** proposal, and belongs in a design that swaps
`src/core/ai/defaults.ts`, is judged on end-task answer accuracy, and pays a full re-embed. Nobody
has published such a result for FlyHash on text, and FlyVec (ICLR 2021) reports only "comparable"
to GloVe/BERT — comparable to a 2014 baseline is not a reason to touch a 2026 index.

---

## 10. The honest non-biological alternative — it wins, so here it is as a buildable spec

**D4-ALT: `vector.backend = pgvector-bq` — binary quantization with exact rescoring.**

It delivers every steelman property claimed for the fly backend, plus the one the fly backend
inverts:

| Fly claim | Does `binary_quantize` have it? |
|---|---|
| S1 data-independent, no training | **Yes** — a deterministic sign function; no fitted parameters, no drift, nothing to recalibrate on a model swap |
| S2 streaming, no rebuild | **Yes** — pgvector README: *"an index can be created without any data in the table since there isn't a training step like IVFFlat"* |
| S3 lifts the dimension cap | **Yes, and further** — `bit` indexes to **64,000 dims** vs `vector`'s 2,000; FlyHash *introduces* a 1,000-nnz cap |
| S4 short-code quality | **Yes** — 0.7577 raw / 0.9918 rescored at 136 B (§5.1) |
| S5 cheap arithmetic | **Yes** — XOR + popcount; measured 3.81 ms vs 7.34 ms float32 (§5.3) |
| S6 unclaimed ground | **No — and that is the point.** It is a documented pgvector recipe with upstream tests |

**The DDL, complete:**

```sql
-- generated code column + HNSW Hamming index (pgvector's own recipe)
CREATE INDEX idx_chunks_embedding_bq ON content_chunks
  USING hnsw ((binary_quantize(embedding)::bit(1024)) bit_hamming_ops);

-- two-stage query: cheap code recall, exact rescore. 0.9918 recall@10 at 136 B/row.
SELECT * FROM (
  SELECT id, chunk_text FROM content_chunks
  ORDER BY binary_quantize(embedding)::bit(1024) <~> binary_quantize($1::vector)
  LIMIT 100
) c ORDER BY (SELECT embedding FROM content_chunks WHERE id = c.id) <=> $1::vector LIMIT 10;
```

Insertion points are identical to §2 (`chunkEmbeddingIndexSql`, `applyChunkEmbeddingIndexPolicy`,
`knobsHash`, one doctor check), and the whole thing is ~3–5 dev-days.

**Measured payoff at GBrain scale:** 13,726 → 609 B/row (**22.5×**), 5.13 GB → 0.23 GB at 373,908
chunks, 32.94 GB → 1.46 GB at 1M pages, HNSW p50 7.34 → 3.81 ms, at 99.2% recall@10. Per `g02`'s
Supabase table that is the difference between a 2XL ($410/mo) and a Large ($110/mo) at the
million-page tier.

**Two competitors to D4-ALT that also beat the fly backend, named for completeness.**
`halfvec(1024)` is a one-line DDL change for a 3× index reduction at 0.9972 recall — `g02` already
recommends it and it is strictly less invasive than D4-ALT. And **SPLADE++** (BEIR-13 nDCG@10 50.5
vs BM25's 43.7, within 4 ms of BM25 latency) fits pgvector `sparsevec` *today* and is the method
that actually occupies the "learned sparse codes in an inverted index" slot the fly proposal was
reaching for.

**Honest caveat on D4-ALT:** it is a *storage and latency* win, not a *quality* win. It cannot move
`recall_all@5`, and by `g02`'s latency arithmetic it cannot move an answered question by more than
~0.1%. Its case is a hosting-tier case. **If the company brain's problem is quality, no index change
of any kind — biological or otherwise — is the answer, and that is the finding this angle
contributes to the synthesis.**

---

## 11. What survives

1. **The *Science* 2017 result, replicated on text embeddings, correctly accounted.** At equal hash
   length, FlyHash beats random-hyperplane LSH by **+82% relative** (0.4948 vs 0.2712) on real
   1,024-d sentence embeddings. That is a genuine, reproducible property of sparse expansion +
   k-WTA and the corpus should stop implying the fly literature is wrong. It is right, on its own
   axis. The axis is just not the one a database bills you for.
2. **The write-side novelty/staleness gate — with a *raised* bar.** §5.4 shows the fly gate's real
   competitor is the free ANN probe (0.843) or its 136-byte binarized shadow (0.834), not a Bloom
   filter and not lexical SimHash (0.590, and 0.263 on paraphrase-shaped edits). The unique fly
   residue is the **AIMD time axis** — duplication and staleness in one O(1)-state number — which
   none of these baselines provides. That remains d1/d2's proposal to make; my contribution is that
   they must benchmark against the free ANN probe and `binary_quantize`, and that `v10b`'s "SimHash
   is the incumbent" framing needs the qualifier "for lexical near-duplicates."
3. **A porting fact worth carrying:** with constant fan-in, per-stimulus mean-centring is a WTA no-op
   (§3), so the fly's concentration-invariance step does not transfer to normalised embeddings. One
   of the three published departures from LSH is inert in this setting.
4. **A correction the synthesis should make.** `checkpoints/01-sweep-decisions.md` §(b) says
   "FlyHash as the semantic index loses to dense embeddings (H3D: 0.13 vs 0.34 MAP)." `v10a` already
   showed that citation over-reaches H3D. **Replace it with the first-party result:** *on real
   1,024-d text embeddings, a FlyHash code must spend ~30× the storage of `binary_quantize` to match
   its recall, and the configuration that does is refused by pgvector's index.* That is a
   same-stack, same-corpus, same-metric comparison and it does not depend on H3D at all.
5. **Nothing else.** Not the index, not the quantizer, not the sparse retriever, not the dedup gate.

---

## 12. Two-week MVP plan

Because the kill criterion fired, the honest plan is **two days of falsification, then twelve days
building the thing that works.**

**Days 1–2 — Falsification (already done here; this is the reproduction path for the maintainer).**
Run `d4_embed_full.py` → `d4_eval.py` → `d4_fly.py` → `d4_pgv.sql` against a real GBrain
`content_chunks` export instead of my 3,187-chunk stand-in. Same four numbers. **Gate:** if FlyHash
fails K1–K3 on the real corpus as it does here, close the `vector.backend=flyhash` question
permanently and open a doc PR recording it — a published negative result is worth more to this
ecosystem than another proposal, and GBrain has form for publishing them (the multi-query-expansion
failure in `RETRIEVAL.md`).

**Days 3–7 — D4-ALT phase 1 (offline).**
`chunkEmbeddingIndexSql` gains a `backend` parameter; `binary_quantize` expression index emitted
behind `vector.backend=pgvector-bq`; `knobsHash` folds `vb=`, `KNOBS_HASH_VERSION` bumped in the
same commit; unit tests for the DDL emitter matrix (backend × columnType × dims); PGLite resolves to
`pgvector` and warns once (parity contract preserved). No query path changes yet. *Exit:* index
builds, `gbrain doctor` reports requested-vs-resolved, nothing else moves.

**Days 8–11 — D4-ALT phase 2 (query path).**
Two-stage rescore in the vector arm of `src/core/search/hybrid.ts`; `backendCandidateGucs` replaces
`hnswEfSearchFor`; `gbrain embed reindex --backend=pgvector-bq` via the existing `dropAndRebuild`
atomic swap. *Exit gate, pre-registered:* **strict `recall_all@5` on LongMemEval-S must be within
0.5 points of the float32 baseline** on the same index and the same query vectors — the one-switch
discipline `g06` insists on and that `v01` showed GBrain's own README violated. Ship default-off,
as an operator lever, exactly as the expansion-variant knob shipped.

**Days 12–14 — Measurement and write-up.**
Index bytes, table bytes, p50/p99 at 10⁵ and 10⁶ chunks, `recall_all@5` with and without the
reranker, and the Supabase tier delta. Publish the FlyHash negative result alongside it in the same
doc, with the raw tables from §5, so the next person does not re-propose it.

**Explicitly not in scope:** any change to the embedding model, the reranker, the graph arm or the
chunker. This is a storage-and-latency change and must be measured as one.

---

## 13. Limitations and threats to validity

Stated in the order that should most worry a reader.

1. **Corpus is 3,187 chunks from 158 documents, topically narrow, and includes my own research
   corpus.** It is company-brain-*shaped* (heavy overlap, mixed prose/code) but it is not a public
   IR benchmark and it is not GBrain's brain. The effect sizes are 5–35× the seed-noise floor, and
   the same ordering appears independently in H3D on two public datasets, but a hostile reader
   should demand the reproduction on a real `content_chunks` export (day 1–2 above).
2. **`bge-m3`, not `voyage-4`.** GBrain's default embedder is `voyage:voyage-4` at 1024-d; I could
   not run a hosted API here, so I matched the **width** (1024) and used the strongest locally
   available open model. Different embedder geometry could shift absolute numbers; it is hard to
   construct a story in which it reverses a 53%-relative gap that also appears in H3D's independent
   proxy.
3. **Metric is fidelity to exact dense cosine, not end-task answer accuracy.** Defended in §2.3 and
   §9 — it is GBrain's own backend acceptance test — but it structurally cannot reward a code that
   is *semantically better than its input embedding*. See the counter-argument in §9.
4. **My BioHash is my implementation of the Krotov–Hopfield rule**, not the authors' code, trained
   for 60 epochs on 3,187 samples. It converged (train time 18 s / 85 s) and behaves sensibly, but a
   better-tuned BioHash could plausibly gain several points. It would need to gain ~30 points at
   k=64 to pass K1, and it would still fail K2 and K3.
5. **Out-of-database timings (§5.5) are NumPy/SciPy artifacts**, not optimised implementations. I
   rely on them only for *bytes scanned*. The in-database timings in §5.3 are pgvector's own
   `EXPLAIN ANALYZE` and are the ones to cite.
6. **`sparsevec` HNSW index sizes were measured on random codes**, not FlyHash codes; real codes
   cluster and could pack differently. The 1,000-nnz refusal is a hard constraint independent of
   data.
7. **Single seed for most FlyHash configurations.** Two-seed LSH gave ±0.01; the monotone, smooth
   behaviour of the k-sweep across three ρ values and three fan-ins is itself evidence of low
   variance.
8. **I did not test DenseFly, SoftHash, or multi-probe fly variants.** DenseFly's pitch is
   explicitly *high-dimensional* hashes, which makes the byte problem worse, not better; SoftHash is
   a training method with the same BioHash trade. Neither changes K2 or K3.

**Reproduction artifacts** (all under
`/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad/`):
`d4_chunk.py`, `d4_embed_full.py`, `d4_eval.py`, `d4_fly.py`, `d4_biohash.py`, `d4_dedup.py`,
`d4_latency.py`, `d4_pgv.sql`, `d4_lat.sql`; embeddings `d4_E.npy` (3187×1024), `d4_P.npy`
(1200×1024), `d4_pidx.npy`; results `d4_stage1.json`, `d4_fly.json`, `d4_biohash.json`,
`d4_dedup.json`. Database: `pgvector/pgvector:pg17` (pgvector **0.8.6**, PostgreSQL 17),
`shared_buffers=1GB`, `maintenance_work_mem=1GB`, `max_parallel_maintenance_workers=0`,
`--shm-size=3g`.

---

## Sources

**Measured first-party, 2026-09-10** — see §13 for the full artifact list. Embedding model
`BAAI/bge-m3` (local, 1024-d); database `pgvector/pgvector:pg17`, pgvector 0.8.6 / PostgreSQL 17.

**Primary — fly algorithms**
- Dasgupta, Stevens & Navlakha, "A neural algorithm for a fundamental computing problem," *Science* 358(6364):793–796, 10 Nov 2017 — https://www.science.org/doi/10.1126/science.aam9868 ; PDF mirror https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf
- Dasgupta, Sheehan, Stevens & Navlakha, "A neural data structure for novelty detection," *PNAS* 115(51):13093–13098, 2018 — https://www.pnas.org/doi/10.1073/pnas.1814448115
- Ryali, Hopfield, Grinberg & Krotov, "Bio-Inspired Hashing for Unsupervised Similarity Search," ICML 2020 — https://arxiv.org/abs/2001.04907 ; PMLR http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf
- Sharma & Navlakha, "Improving Similarity Search with High-dimensional Locality-sensitive Hashing" (DenseFly), NeurIPS 2019 — https://arxiv.org/abs/1812.01844
- Kleyko & Rachkovskij, design-choice study of fly-hashing — https://arxiv.org/html/2501.14741
- Liang et al., "Can a Fruit Fly Learn Word Embeddings?" (FlyVec), ICLR 2021 — https://arxiv.org/abs/2101.06887
- Li, Wang, Chen, Chen & Peng, "Bio-inspired Vector Set Search" (BioVSS), ICDE 2025 — https://arxiv.org/html/2412.03301

**Primary — comparators and negative results**
- H3D document-fingerprint benchmark (Mao, Lyu et al., 9 Jul 2026) — https://arxiv.org/abs/2607.08382 ; full tables https://arxiv.org/html/2607.08382 ; harness https://github.com/DocAILab/Document-Fingerprints
- Formal, Lassance, Piwowarski & Clinchant, SPLADE++ (BEIR-13 nDCG@10 50.5 vs BM25 43.7), SIGIR 2022 — https://arxiv.org/abs/2205.04733
- Lassance & Clinchant, "An Efficiency Study for SPLADE Models" (<4 ms of BM25), SIGIR 2022 — https://arxiv.org/abs/2207.03834
- Subramanya et al., DiskANN (1B points, 64 GB, <3 ms, 95% recall@1), NeurIPS 2019 — https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf
- Malkov & Yashunin, HNSW — https://arxiv.org/abs/1603.09320
- Manku, Jain & Das Sarma, "Detecting Near-Duplicates for Web Crawling" (64-bit simhash, k=3), WWW 2007 — https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33026.pdf
- Sentence Transformers, Embedding Quantization (32× memory, ~96% retained with rescoring) — https://sbert.net/examples/sentence_transformer/applications/embedding-quantization/README.html
- `Dimitres-Kisimov/bio-efficient-ai` — resource-fair FlyHash vs classical LSH on MNIST (0★, unrefereed, cite as such) — https://github.com/Dimitres-Kisimov/bio-efficient-ai

**Primary — pgvector (read from the repo, and exercised live)**
- README: storage rules (`vector` 4d+8, `halfvec` 2d+8, `bit` L/8+8, `sparsevec` 8·nnz+16); HNSW-indexable limits — `vector` ≤2,000 dims, `halfvec` ≤4,000, `bit` ≤64,000, **`sparsevec` ≤1,000 non-zero elements**; `bit_hamming_ops` / `bit_jaccard_ops`; `binary_quantize` + rescore recipe; *"an index can be created without any data in the table since there isn't a training step like IVFFlat"*; FAQ *"…binary quantization to index up to 64,000 dimensions"* — https://github.com/pgvector/pgvector ; raw https://raw.githubusercontent.com/pgvector/pgvector/master/README.md
- `src/hnsw.h` — `HNSW_MAX_DIM 2000`, `HNSW_DEFAULT_M 16`, `HNSW_DEFAULT_EF_SEARCH 40` — https://raw.githubusercontent.com/pgvector/pgvector/master/src/hnsw.h

**Primary — GBrain @ v0.48.5.0**
- `docs/designs/VECTOR_BACKENDS.md` — status **proposal**; `vector.backend` key; resolution chain; degrade path; `knobsHash` fold; phase-2 column-type cost; Non-goals ("no benchmark bake-off … the eval bar is does an over-4000-dim model get indexed search back"); Testing ("returns the same rows as the pgvector baseline") — https://github.com/garrytan/gbrain/blob/master/docs/designs/VECTOR_BACKENDS.md
- `src/core/vector-index.ts` — `PGVECTOR_HNSW_VECTOR_MAX_DIMS = 2000` (:19), `chunkEmbeddingIndexSql` (:25), `hnswMaxDimsForType` (:33), `applyChunkEmbeddingIndexPolicy` (:42), `hnswEfSearchFor` (:63), `dropAndRebuild` (:186) — https://github.com/garrytan/gbrain/blob/master/src/core/vector-index.ts
- `src/schema.sql` — `embedding vector(1536)` (:302), `embedded_text_hash` (:308), `idx_chunks_embedding … USING hnsw` (:336), multimodal partial index (:341–344) — https://github.com/garrytan/gbrain/blob/master/src/schema.sql
- `src/core/ai/defaults.ts` — new-install default `voyage:voyage-4` @ **1024 dims**
- `src/core/chunkers/recursive.ts` — 300-word chunks, 50-word overlap
- `docs/architecture/RETRIEVAL.md`, `README.md` — hybrid stack; LongMemEval-S `recall_all@5` 95.53% / 93.40%

**Internal corpus cross-references**
- `findings/g02-sizing-cost.md` — measured HNSW 8,192 B/vec @1024-d; ANN = 0.14% of an answered question; 2.40 chunks/page; Supabase tier table; curation is 222×–4,514× embedding cost
- `findings/g07-neuro-mechanism-inventory.md` §1 — FlyHash fidelity "Deep (as a mechanism); wrong slot (as a design proposal)"
- `findings/v10a-h3d-flyhash.md` — H3D over-citation correction; the "BGE embedding → FlyHash" empty cell this report fills
- `findings/v10b-flyhash-vs-modern.md` — role-by-role verdict; the byte arithmetic this report confirms by measurement; the dedup-slot claim this report corrects
- `findings/flyhash-sparse-retrieval.md` — the fly lineage and the *Science*/PNAS parameters used here
- `findings/v01-gbrain-benchmarks.md` — one-switch A/B discipline; reranker supplies +2.13 pp
- `findings/g06-crux-experiment.md` — ablation-ladder and pre-registration discipline adopted in §4 and §12
- `findings/gbrain-architecture.md` — the `vector.backend` seam this design targets

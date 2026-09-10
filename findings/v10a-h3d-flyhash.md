# v10a — H3D benchmark: are the FlyHash numbers real, and what do they actually license us to say?

**Key:** `v10a-h3d-flyhash` · lens: paper-reader · date 2026-09-10
**Claim under test:** *"The H3D benchmark (arXiv:2607.08382, July 2026) puts FlyHash at 0.1325 MAP on CSFCube vs 0.3431 for frozen BGE-large, and 0.4305 vs 0.6626 on RELISH."*

## Verdict

**CONFIRMED on the numbers — but the sweep's gloss on them ("FlyHash as the semantic index loses to dense embeddings") is right for the wrong reason, and the number is not a fair test of FlyHash.**

All four figures are transcribed exactly and correctly from the paper. But three things in the surrounding framing need correcting before the synthesis uses them:

1. **The task is semantic-relatedness retrieval, not deduplication**, despite the paper's title. CSFCube and RELISH are expert-annotated *relevance* collections over distinct papers. H3D contains no near-duplicate benchmark at all — its only near-duplicate evidence is a 3-document toy case study in Appendix B where all five hash methods score MAP = 1.00.
2. **H3D's FlyHash is not FlyHash.** It is a *dimensionality-reducing* sparse random projection (→128 bits, 8 active) over a **3-shingle term-frequency vector** — lexical input, no embeddings anywhere. Canonical FlyHash is defined by *expansion* (m ≫ d) over **dense feature vectors**. H3D runs the algorithm outside the regime in which it was ever shown to work, and its own Section 3.2.1 describes FlyHash as "high-dimensional binary mapping" while Appendix B implements 216 → 128.
3. **The 0.1325-vs-0.3431 gap conflates two independent penalties** — lexical-vs-semantic *input*, and hashed-vs-dense *representation* — and H3D's own tables let us separate them. When you do, the semantic-input penalty is the big one and the hashing penalty is modest. There is no `BGE-embedding → FlyHash` cell in H3D, which is precisely the cell a company-brain design would care about.

**One-sentence citable form:** In H3D (arXiv:2607.08382, 9 Jul 2026), a 128-bit FlyHash computed over 3-shingle frequency vectors reaches 0.1325 MAP on CSFCube-overall and 0.4305 MAP on RELISH-test, against 0.3431 and 0.6626 for dense frozen BGE-large — but both datasets measure expert-judged topical relevance between distinct papers rather than near-duplicate detection, and H3D never evaluates FlyHash on top of embeddings, so the result shows that *lexical shingle hashes are weak semantic indexes*, not that the fly algorithm is.

---

## 1. The numbers, verified against the source tables

Paper: Qianren Mao, Jiaxun Lyu, Junnan Liu, Zhijun Chen, Jingzheng Li, Hanwen Hao, Bo Li. *"H3D: Benchmarking Unsupervised Text Hashing for Fine-Grained Document Deduplication."* arXiv:2607.08382 [cs.IR], submitted **Thu, 9 Jul 2026**, v1 only. No venue, no released code URL in the paper.

### CSFCube (Table 5 = non-learning hashes; Table 7 = BGE)

| Method | Scorer | MAP (overall / "All") | NDCG@20 (All) | Time (s) |
|---|---|---|---|---|
| **FlyHash** | cosine | 0.1228 | 0.2352 | 13.66 |
| **FlyHash** | **jaccard** | **0.1325** | 0.2520 | 10.95 |
| FlyHash | levenshtein | 0.1311 | 0.2434 | 10.57 |
| FlyHash | manhattan | 0.1222 | 0.2353 | 11.67 |
| FlyHash | M-jaccard | 0.1246 | 0.2355 | 11.34 |
| FuzzyHash | levenshtein | 0.1497 | 0.2963 | 0.25 |
| SimHash | manhattan | 0.1770 | 0.3601 | 3.62 |
| MinHash | jaccard | 0.2451 | 0.4167 | 17.31 |
| Winnowing | jaccard | **0.2678** | 0.4337 | 6.22 |
| BGE-BIHash(large) | Manhattan | 0.2175 | 0.4040 | 68.3 |
| BGE-LSHash(large) | Manhattan | 0.2705 | 0.4750 | 169.1 |
| **BGE(large), dense** | **Manhattan** | **0.3431** | 0.5754 | 69.9 |

The paper states it in prose too: *"The best overall CSFCUBE result is achieved by BGE(large) with Manhattan similarity (0.3431 MAP, 0.5754 NDCG@20)."* (§5.2)

### RELISH test split (Table 6 = non-learning; Table 8 = BGE)

| Method | Scorer | MAP (test) | NDCG@20 (test) | Time (s) |
|---|---|---|---|---|
| **FlyHash** | cosine | 0.4002 | 0.5506 | 0.00 † |
| **FlyHash** | hamming | 0.4171 | 0.5736 | 1738.03 |
| **FlyHash** | **levenshtein** | **0.4305** | 0.5969 | 1744.65 |
| FuzzyHash | levenshtein | 0.4091 | 0.5632 | 13.91 |
| MinHash | jaccard | 0.4609 | 0.6245 | 4159.82 |
| SimHash | manhattan | 0.4756 | 0.6428 | 0.00 † |
| Winnowing | M-jaccard | **0.4996** | 0.6694 | 1454.27 |
| BGE-LSHash(large) | Manhattan | 0.5336 | 0.7114 | 4692.8 |
| BGE-BIHash(large) | cosine | 0.5496 | 0.7231 | 3403.4 |
| **BGE(large), dense** | **Manhattan** | **0.6626** | 0.8242 | 3198.5 |

Prose confirmation: *"Dense BGE again performs best, with BGE(large)+Manhattan reaching 0.6626 MAP and 0.8242 NDCG@20 on the test split."* (§5.2)

† These 0.00 entries are a **known bug**, not speed. Appendix A.2: *"In `relish_summary.csv`, 14 out of 22 rows have zero runtime values… a likely parsing mismatch: the RELISH summarizer accumulates time from lines matching `Finished all scoring in ...`, while many logs report `Finished scoring in ...`."* Do not cite H3D's RELISH timings.

**So the claim's four numbers are exact.** Both FlyHash figures happen to be its *best* row across scorers, so the comparison is generous to FlyHash, not rigged against it. Ratios: FlyHash reaches **38.6%** of dense BGE-large on CSFCube and **65.0%** on RELISH.

---

## 2. What the task actually is: retrieval, not dedup

The paper is titled "…for Fine-Grained Document Deduplication" and repeatedly calls its protocol a deduplication benchmark. **Its two datasets are not deduplication datasets.** Both are query→candidate ranking collections with graded human relevance labels, thresholded at `g0 = 2` for the binary-relevance part of MAP (§4.2).

- **CSFCube** (Mysore, O'Gorman, McCallum, Zamani; arXiv:2103.12906) — *"faceted Query by Example"* over CS papers. 50 expert-annotated query documents, TREC depth-k pooling (k = 100 or 250), graded relevance 0–3 along background / method / result facets. 4,207-doc corpus, 6,244 annotated query-candidate pairs (H3D Table 1). This is a *retrieval* test collection; "similar" means "a paper you'd want to read next", not "the same paper twice".
- **RELISH** (Brown, Kulkarni, Refai, Zhou, Al-Farha; *Database* 2019, doi:10.1093/database/baz085) — *"Large expert-curated database for benchmarking document similarity detection in biomedical literature search"*. >180,000 relevance annotations from ~1,600 scientists in 84 countries, labels **relevant / somewhat-relevant / irrelevant** with respect to a seed article. The PMC record is explicit that this is topical relevance between *distinct* articles, not near-duplicate detection. H3D uses 3,190 query units and 191,245 query-candidate pairs over a 163,170-doc corpus.

H3D §2.2 asserts RELISH *"reflects practical deduplication challenges such as distinguishing preprint and final-publication variants… identifying different versions of the same paper with minor edits."* **This characterisation is not supported by the RELISH source**, which contains no version/duplicate annotation layer. It is the authors' reframing of a relevance corpus.

**Consequence for us:** the 0.1325 / 0.4305 numbers *are* legitimate evidence about **semantic retrieval** — that is exactly what they measure. They are **not** evidence about near-duplicate detection, in either direction. H3D's only dedup evidence is Appendix B: three hand-written documents (A original, B light paraphrase, C unrelated), five pipelines, **all five reach MAP = 1.00**. FlyHash+Jaccard there scores A–B = 0.778, A–C = 0.000, at 0.0012 s/doc — jointly the fastest and (with Winnowing) the cleanest on negative-pair purity. That is a worked example, not a measurement; it cannot support the abstract's claim that lexical fingerprints are "competitive for near-duplicate matching".

---

## 3. The FlyHash configuration in H3D

Reconstructed from §4.4 (experimental setup) and Appendix B, Experiment 1 — the only place the pipeline is spelled out:

| Aspect | H3D's implementation |
|---|---|
| **Input features** | **Raw-text lexical.** "Construct a frequency vector over all 3-shingle features extracted from the preprocessed document." Term-frequency counts over character/word 3-shingles. **No TF-IDF weighting mentioned. No embeddings.** Input fields = title + abstract (facet-grouped sentences for CSFCube). |
| **Input dimension D** | 216 in the worked example (a 3-document toy). For the real corpora, D = the shingle-feature space; never stated. |
| **Projection** | Fixed random **binary** matrix **W ∈ {0,1}^{216×128}**, "sparse random projection", **seed 55**. |
| **Output dimension (hash length)** | **128** ("The main defaults include hash dimension 128, n-gram size 3, and Winnowing window 5.") |
| **Sparsification** | Winner-Take-All: **top 8** of 128 set to 1 → 6.25% activity. |
| **Output type** | Sparse binary vector; Table 4 recommends cosine, but jaccard/levenshtein win in practice. |
| **Applied on top of dense embeddings?** | **No — never.** FlyHash appears only in the "semantic-agnostic non-learning" family (§3.2). The embedding-based family is BGE + BIHash/LSHash only. |

Two things are wrong with this as a test of FlyHash:

**(a) It inverts the algorithm's defining property.** FlyHash's identity is *sparse expansion*: project d dimensions up into m ≫ d, then k-WTA. H3D projects 216 → 128, a **contraction**. The paper's own §3.2.1 says FlyHash "uses high-dimensional binary mapping and a Winner-Take-All mechanism" — the implementation contradicts the description. Independent primary confirmation of the canonical form, from Ryali, Hopfield, Grinberg & Krotov (ICML 2020, arXiv:2001.04907): *"In classical LSH approaches, the data dimensionality d is much larger than the embedding space dimension m, resulting in low-dimensional hash codes. In contrast, a new family of hashing algorithms has been proposed (Dasgupta et al. 2017) where **m ≫ d**, but the secondary representation is highly sparse."* Their FlyHash baseline follows Dasgupta with **m = 10d** and PN→KC sampling rate 0.1. The biology is a **~50× expansion** (≈50 projection neurons → ≈2,500 Kenyon cells, <10% active). H3D runs it at roughly 0.6×.

**(b) The code budget is tiny.** A 128-bit code with exactly 8 ones carries at most log₂ C(128,8) ≈ **40.4 bits** of information about the whole document. Dense BGE-large is 1024 float dimensions. Any comparison at that budget is a compression study, and H3D never says so.

---

## 4. Decomposing the gap with H3D's own numbers

The 0.1325 → 0.3431 jump bundles two different changes. H3D lets us pull them apart on CSFCube-overall MAP:

| Step | Config | MAP | Δ |
|---|---|---|---|
| Dense semantic reference | BGE(large) dense, Manhattan | 0.3431 | — |
| **hashing penalty** (semantic input, quantized) | BGE-LSHash(large) Manhattan | 0.2705 | −0.073 |
| " (harsher quantizer) | BGE-BIHash(large) Manhattan | 0.2175 | −0.126 |
| **lexical-input reference** (best lexical hash) | Winnowing + jaccard | 0.2678 | ≈ tied with BGE-LSHash |
| **FlyHash-specific penalty** | FlyHash + jaccard | 0.1325 | −0.135 below best lexical |

Read that column again. On CSFCube:

- Quantizing a semantic embedding costs **0.07–0.13 MAP**. Real, but survivable.
- The *best lexical* hash (Winnowing, 0.2678) is **statistically indistinguishable from a quantized BGE-large** (BGE-LSHash 0.2705). Lexical shingles are not the disaster the headline number implies.
- **FlyHash is the worst of the five lexical hashes** — it loses to Winnowing by as much as quantization costs, and it even loses to a *32-bit* BGE-BIHash code (0.2175). On RELISH it is second-worst (0.4305; only FuzzyHash 0.4091 is lower; Winnowing 0.4996).

So the honest reading is: **the headline gap is mostly "this particular contraction-mode FlyHash is a bad hash", not "sparse binary codes can't do semantics."** The cell that would settle the question for a company brain — *FlyHash / k-WTA applied on top of BGE embeddings* — **does not exist in H3D**. That is the missing experiment, and it is cheap to run.

For what the missing cell probably looks like, the best primary evidence is Ryali et al. 2020 Table 8: FlyHash over **GloVe (d = 300)** dense embeddings, mAP@100 vs cosine ground truth —

| Hash length k | 2 | 4 | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|
| classical LSH | 0.41 | 0.65 | 2.23 | 13.91 | 30.30 | 32.60 |
| ITQ | 0.76 | 1.84 | 6.84 | 27.64 | 44.47 | 61.15 |
| **FlyHash** | **15.06** | **17.09** | **24.64** | 34.12 | 50.96 | **72.37** |
| BioHash (learned) | 38.13 | 54.22 | 66.85 | 76.30 | 84.05 | 89.78 |

FlyHash-on-embeddings **beats classical LSH by 10–37× at short code lengths** and stays ahead at k = 64. Note the ground truth there is *cosine distance in the original embedding space* — i.e. it measures how faithfully the hash preserves the dense geometry. That is the right frame: **FlyHash competes with LSH / ITQ / binary quantization as a compressor of an embedding; it never competes with the embedding itself.** No hash of a vector can outscore the vector on semantic relevance.

---

## 5. Benchmark-quality caveats (use H3D, but with these attached)

- **n = 50 queries on CSFCube.** Differences of ±0.05 MAP there are not resolvable; single seed, no confidence intervals, no significance tests anywhere in the paper. The 2.6× FlyHash-vs-BGE gap is almost certainly real; the Winnowing-vs-BGE-LSHash tie is not something to lean on. RELISH (3,190 queries, test–dev gap averaging 0.0036 MAP, Appendix A.1) is the trustworthy split.
- **A visible data bug the authors do not fix.** Table 6 reports MinHash + mahalanobis on RELISH at **0.9747 MAP / 1.0000 NDCG@20** — an impossible result the paper waves at with *"Rows with atypical values are treated as data-consistency checks"* (§5.2) rather than removing.
- **Runtimes are unusable on RELISH** (14/22 rows zeroed by the log-parsing bug, Appendix A.2), and the paper says timings are "relative cost within this benchmark rather than hardware-agnostic throughput".
- **Inconsistent scorer dedup.** §4.3 note says Hamming/Manhattan/Mahalanobis are rank-equivalent for binary signatures and "we keep Manhattan as the representative row" — yet the FlyHash CSFCube block keeps manhattan and the RELISH block keeps hamming, and reports *different* values for cosine/hamming/levenshtein on the same representation.
- **No code URL, no venue, v1 only, one submission (9 Jul 2026).** Not peer-reviewed as of 2026-09-10.
- H3D deliberately excludes learned semantic hashing (VDSH, NASH, DHIM, MICPQ…) and does not include SPLADE/BM42-style learned sparse retrieval or modern binary/int8 embedding quantization — so it is **not** a state-of-the-art comparison, only a fixed-rule-hash comparison.

---

## 6. The fair conclusion for the company-brain question

**For semantic retrieval (the read path):**
FlyHash as configured in H3D is a bad semantic index — 38.6% of dense BGE-large on CSFCube, 65.0% on RELISH — but it is bad *for reasons that are mostly about the input and the contraction*, not about sparse binary coding per se. The defensible claim for the synthesis is the narrower one: **do not put a lexical shingle FlyHash in front of an embedding index.** The claim "FlyHash loses to dense embeddings as a semantic index" is still true and still supported, because *no hash of an embedding beats the embedding* — but H3D is weaker support for it than the sweep note implies, and the sweep should not cite H3D as evidence that *the fly algorithm* is unsuitable. Cite it as evidence that **a 40-bit lexical fingerprint is unsuitable**.

**For near-duplicate detection (the write path — the ingest novelty gate):**
**H3D says nothing usable.** It contains no near-duplicate benchmark. Its dedup evidence is a 3-document illustration where every method scores 1.00. Anyone claiming H3D validates FlyHash for dedup is over-reading; anyone claiming it invalidates FlyHash for dedup is over-reading in the other direction. What H3D *does* weakly suggest, and what the paper itself notes (§Appendix B), is that FlyHash is the cheapest to compute (0.0012 s/doc) and produces the cleanest zero on unrelated pairs — the two properties an ingest gate actually wants — while being "sensitive to small lexical perturbations", which is a *feature* for exact-dup catching and a *bug* for paraphrase catching. That matches the abstract's trade-off framing.

**Practical recommendation for the design section (b):**
1. Don't propose FlyHash-over-shingles as the retrieval index. That is the configuration H3D measured, and it loses.
2. If proposing a fly-derived novelty gate at ingest, apply k-WTA **on top of the embedding you already compute** (m ≫ d expansion, ~5% activity), not on shingles — that is Dasgupta's actual regime and the one where Ryali et al. show 10–37× gains over classical LSH at short code lengths. This is also the cell H3D leaves empty, so it is unclaimed and cheaply testable.
3. Cost the comparison honestly against MinHashLSH and against modern binary/int8 embedding quantization, neither of which H3D covers at strength. On H3D's own turf the boring winner among fixed-rule lexical hashes is **Winnowing + Jaccard**, not FlyHash.
4. If the synthesis quotes "0.13 vs 0.34", it must carry the qualifier *"128-bit FlyHash over 3-shingle counts, on a semantic-relevance retrieval task"*, or it misrepresents the paper.

**Suggested replacement for the sweep's line** (checkpoints/01-sweep-decisions.md, §(b) "where it is NOT real"):
> ~~FlyHash as the semantic index loses to dense embeddings (H3D: 0.13 vs 0.34 MAP)~~
> → *A lexical FlyHash is not a semantic index: in H3D (arXiv:2607.08382), a 128-bit FlyHash over 3-shingle counts reaches 0.1325 MAP on CSFCube-overall and 0.4305 on RELISH-test vs 0.3431 / 0.6626 for dense frozen BGE-large — and it is the weakest of the five lexical hashes tested, behind Winnowing (0.2678 / 0.4996). H3D never evaluates FlyHash on top of embeddings, and both datasets measure topical relevance, not duplication, so the paper neither supports nor refutes a fly-style novelty gate at ingest.*

**Confidence:** numbers, configuration and task identification — **high** (read directly from the source tables and prose). The decomposition in §4 and the "missing cell" argument — **high** on the facts, **medium** on the inference that FlyHash-on-BGE would land near BGE-LSHash or better (extrapolated from Ryali's GloVe results on a different task and metric; untested on CSFCube/RELISH).

---

## Sources

Primary:
- Mao, Lyu, Liu, Chen, Li, Hao, Li. *H3D: Benchmarking Unsupervised Text Hashing for Fine-Grained Document Deduplication.* arXiv:2607.08382v1 [cs.IR], 9 Jul 2026. Abstract: https://arxiv.org/abs/2607.08382 · Full text (tables 4–8, §4.4, §5.1–5.2, §5.5, App. A.2, App. B): https://arxiv.org/html/2607.08382v1 · DOI https://doi.org/10.48550/arXiv.2607.08382
- Dasgupta, Stevens, Navlakha. *A neural algorithm for a fundamental computing problem.* Science 358(6364):793–796, 2017. https://doi.org/10.1126/science.aam9868 (metadata via https://api.semanticscholar.org/graph/v1/paper/DOI:10.1126/science.aam9868 ; full text paywalled, bioRxiv mirror 10.1101/180471 returned HTTP 429)
- Ryali, Hopfield, Grinberg, Krotov. *Bio-Inspired Hashing for Unsupervised Similarity Search.* ICML 2020. arXiv:2001.04907. https://arxiv.org/abs/2001.04907 · full text https://ar5iv.labs.arxiv.org/html/2001.04907 (FlyHash definition m ≫ d; baseline m = 10d, sampling rate 0.1; Table 8 GloVe results; fly circuit ≈50 PN → ≈2,500 KC)
- Mysore, O'Gorman, McCallum, Zamani. *CSFCube — A Test Collection of Computer Science Research Articles for Faceted Query by Example.* arXiv:2103.12906. https://arxiv.org/abs/2103.12906 · dataset https://github.com/iesl/CSFCube
- Brown, Kulkarni, Refai, Zhou, Al-Farha et al. *Large expert-curated database for benchmarking document similarity detection in biomedical literature search.* Database (Oxford) 2019, baz085. https://doi.org/10.1093/database/baz085 · open access https://pmc.ncbi.nlm.nih.gov/articles/PMC7291946/ · RELISH-Aspire release used by H3D: https://figshare.com/articles/dataset/RELISH-Aspire/19425506

Internal:
- /Users/stephen/Cookies/company-brain-research/checkpoints/01-sweep-decisions.md (claim under test, §(b))
- /Users/stephen/Cookies/company-brain-research/findings/projects-built-on-ideas.md (FlyHash tooling landscape: tfatykhov/membrain, TeddyHuang-00/FlyHash)

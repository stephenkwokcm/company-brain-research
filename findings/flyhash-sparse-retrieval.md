# flyhash-sparse-retrieval — Fruit-fly olfaction algorithms as a retrieval/memory substrate

Dimension owner: research worker (Opus 5). Date: 2026-09-10.
Scope: the FlyHash lineage (2017–2026) and whether it can plausibly serve as the "librarian's index" in Garry Tan's company-brain framing.

## TL;DR

1. **There is a real, 9-year-old algorithmic bridge between fruit-fly brains and RAG.** Dasgupta, Stevens & Navlakha (*Science*, 10 Nov 2017, [10.1126/science.aam9868](https://www.science.org/doi/10.1126/science.aam9868)) showed the fly olfactory circuit implements a locality-sensitive hash: 50 projection neurons → 2,000 Kenyon cells via a sparse binary random matrix (each KC samples ~6 PNs), then winner-take-all keeps the top 5% (~100 cells). That is FlyHash. It beat classical LSH by ~3× mAP at short hash lengths (MNIST, k=4: 16.0% LSH vs 44.8% fly) at equal op count.
2. **The most transferable piece is not the index — it is the fly Bloom filter.** Dasgupta et al. (*PNAS*, Dec 2018, [10.1073/pnas.1814448115](https://www.pnas.org/doi/10.1073/pnas.1814448115)) turned the same circuit into a *distance- and time-sensitive* Bloom filter that emits a continuous novelty score in [0,1] and decays with time. That is a native answer to Tan's actual problems: what is worth writing down, what is a near-duplicate, what is stale, hot vs cold.
3. **As a raw semantic retrieval index, FlyHash currently loses to dense embeddings on text.** The July 2026 H3D benchmark ([arXiv:2607.08382](https://arxiv.org/html/2607.08382)) puts FlyHash at 0.1325 MAP on CSFCube and 0.4305 MAP on RELISH, versus 0.3431 / 0.6626 for frozen BGE-large dense embeddings. Fly hashing is a *lexical/structural* fingerprint, not a meaning-preserving one, unless you hash on top of learned embeddings.
4. **The strongest recent scale evidence is BioVSS** (ICDE 2025, [arXiv:2412.03301](https://arxiv.org/html/2412.03301)): BioHash codes + Bloom-filter indexes give >50× speedup over linear scan at up to 98.9% recall on million-scale vector-*set* search, beating IVFFLAT/IVFPQ/HNSW on that task. But vector-set search with Hausdorff distance is not standard RAG — do not read it as "FlyHash beats HNSW."
5. **Practical verdict for a company brain: use fly algorithms on the write side, not the read side.** Keep dense embeddings + HNSW for recall; bolt a fly Bloom filter on as a novelty/dedup gate, a staleness decay clock, and a cheap trigger for expensive contradiction arbitration. The 2026 agent-memory literature has independently converged on the write-side gate (SAGE, [arXiv:2605.30711](https://arxiv.org/pdf/2605.30711): 3.4× cheaper writes, 2.5× lower latency) but uses a von Mises–Fisher density estimator, not a Bloom filter — that gap is an unexploited opportunity.

---

## 1. The canonical fly algorithms

### 1.1 FlyHash — Dasgupta, Stevens & Navlakha, *Science* 358(6364):793–796, 10 Nov 2017
DOI [10.1126/science.aam9868](https://www.science.org/doi/10.1126/science.aam9868); PDF mirror: <https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf>

Three departures from classical LSH, verified from the paper text:
- **Sparse, binary random projection** instead of dense Gaussian. Each Kenyon cell sums ~6 randomly chosen projection neurons. Empirically "near-identical performance" to dense Gaussian projections with a **factor-of-20 computational saving**.
- **Dimensionality expansion** (m ≫ d) instead of contraction — 40× in the fly (50 → 2,000); the paper used up to 10d.
- **Winner-take-all sparsification**, top 5%, giving a sparse binary tag.

Evaluation: SIFT (d=128), GLOVE (d=300), MNIST (d=784), 10,000 items each, 1,000 queries, top-2% (200) true nearest neighbours, mAP averaged over 50 trials.
- WTA vs random tag selection at equal ops, SIFT, k=4: **17.7% → 32.4% mAP** (roughly double).
- Fly (10d expansion) vs LSH, MNIST, k=4: **16.0% → 44.8% mAP** (~3×). Gains are largest at short hash lengths and shrink as k grows — an important caveat that is usually dropped when this paper is cited.

### 1.2 Fly Bloom filter — Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093–13098, Dec 2018
DOI [10.1073/pnas.1814448115](https://www.pnas.org/doi/10.1073/pnas.1814448115); open PDF: <https://repository.cshl.edu/id/eprint/38636/1/Navlakha_2018_PNAS.pdf>

The mushroom body output neuron MBON-α′3 reads 350 of the 2,000 KCs and acts as the filter. Update rule (Eq. 2): for each of the k active KCs, `w ← w·δ` with 0 ≤ δ < 1; for the m−k inactive KCs, `w ← w + ε`. Novelty = mean of the k active weights, normalised to [0,1]. Setting δ=ε=0 recovers a classical binary Bloom filter.

Three properties a standard Bloom filter lacks and this one has *together*: continuous scores, **distance sensitivity** (similar items suppress each other's novelty), and **time sensitivity** (aggressive decay on exposure, slow recovery back to novel — an additive-increase / multiplicative-decrease schedule). Results (correlation between ground-truth and predicted novelty):
- Fly odours: **0.657 ± 0.06** (fly) vs 0.537 ± 0.08 (LSBF)
- Primate faces: **0.508 ± 0.03** vs 0.404 ± 0.03
- SIFT: **0.535 ± 0.03** vs 0.345 ± 0.03 (LSBF) vs **0.002 ± 0.02** (traditional Bloom filter)

The paper explicitly motivates eviction for "life-long learning applications, where the database is not of fixed size but continuously grows" — i.e. exactly a company brain.

### 1.3 The 2018–2021 follow-ups
- **DenseFly / high-dimensional LSH** — Sharma & Navlakha, [arXiv:1812.01844](https://arxiv.org/abs/1812.01844), NeurIPS 2019. Keeps hashes high-dimensional, preserves rank similarity in any ℓp space, adds multi-probe; wins on 6 benchmarks at equal query time.
- **BioHash / BioConvHash** — Ryali, Hopfield, Grinberg & Krotov, ICML 2020, [arXiv:2001.04907](https://arxiv.org/abs/2001.04907), [PMLR v119](http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf). Makes the expansion *learned* via a local, biologically plausible Hebbian rule; fixes FlyHash's core weakness (random, data-independent projections) while staying fast, online and scalable, unlike the earlier SOLHash.
- **FlyVec** — Liang et al., ICLR 2021, [arXiv:2101.06887](https://arxiv.org/abs/2101.06887). The same KC + APL motif learns word embeddings as sparse *binary* hash codes (default k=50, ~20k vocab) with performance "comparable" to GloVe/BERT on word similarity, WSD and document classification "using only a fraction of the computational resources."
- **Fly Bloom Filter Classifier (FBFC)** — Sinha & Ram, [arXiv:2008.08685](https://arxiv.org/abs/2008.08685), KDD 2021 ([10.1145/3447548.3467246](https://dl.acm.org/doi/10.1145/3447548.3467246)). Per-class fly Bloom filters; classification = FlyHash + sparse high-dim dot product; single-pass, parallelisable, competitive with kNN on >50 datasets. There is also a federated variant (<https://fl-icml.github.io/2021/papers/FL-ICML21_paper_23.pdf>).
- **Continual learning** — Shen, Dasgupta & Navlakha, [arXiv:2107.07617](https://arxiv.org/abs/2107.07617). Sparse coding plus *synaptic freezing* (modify only synapses of active KCs) as a lightweight anti-catastrophic-forgetting mechanism. Adjacent: Bricken, Davies, Singh, Krotov & Kreiman, "Sparse Distributed Memory is a Continual Learner," ICLR 2023, [arXiv:2303.11934](https://arxiv.org/abs/2303.11934).

## 2. What happened 2024–2026

- **Design-choice study** — Kleyko & Rachkovskij, [arXiv:2501.14741](https://arxiv.org/html/2501.14741) (Dec 2024). Systematically varies preprocessing, sparsifying activation (kWTA / binary kWTA / k-block sparse) and projection distribution (binomial vs hypergeometric, density 1.56/10/50%). Finding: choices make a "drastic difference"; **k-block sparse codes consistently win** at matched bits; hypergeometric sampling helps on dense data (GLOVE) but not sparse (MNIST). Notably, the authors do **not** claim FlyHash beats dense methods — they position optimised FlyHash for *memory-constrained* settings.
- **BioVSS / BioVSS++** — Li, Wang, Chen, Chen & Peng (Wuhan University + Amazon), ICDE 2025, [arXiv:2412.03301](https://arxiv.org/html/2412.03301) ([ICDE PDF](https://sheng.whu.edu.cn/papers/25icde-B.pdf)). BioHash-style sparse binary codes indexed by count Bloom filters + binary Bloom-filter sketches, two-stage filter then exact Hausdorff. >50× faster than linear scan at up to 98.9% recall on CS (1.19M sets / 5.55M vectors, 384-d), Medicine (2.69M sets / 15M vectors) and Picture (982K sets / 2.51M vectors, 512-d), against brute force, IVFFLAT, IVFPQ, IVFScalarQuantizer and HNSW.
- **SoftHash** — soft winner-take-all instead of hard k-WTA, Hebbian + anti-Hebbian learning; [OpenReview cNwugejbW6](https://openreview.net/forum?id=cNwugejbW6), later IEEE ("Unsupervised Learning to Hash with a Soft Winner-Take-All Mechanism", <https://ieeexplore.ieee.org/abstract/document/11461356/>).
- **H3D benchmark** — [arXiv:2607.08382](https://arxiv.org/html/2607.08382) (9 Jul 2026), Mao, Lyu et al.; repo <https://github.com/DocAILab/Document-Fingerprints>. This is the most decision-relevant negative result. FlyHash is benchmarked as a *semantic-agnostic* fingerprint alongside MinHash/SimHash/Winnowing/FuzzyHash. CSFCube: FlyHash MAP 0.1325, NDCG@20 0.2520 (~11 s). RELISH: MAP 0.4305, NDCG@20 0.5969 (1,744 s). BGE-large dense: 0.3431 and 0.6626 MAP respectively. Conclusion in the paper's own words: lexical/structural fingerprints are competitive for near-duplicate matching, semantic representations win under content rewriting.
- **Spi-Fly** — Max & Shen, "Few-shot, continual learning for spiking neuromorphic olfaction," *Neuromorphic Computing and Engineering*, 24 Aug 2026, [DOI 10.1088/2634-4386/ae9177](https://doi.org/10.1088/2634-4386/ae9177) (OIST press: <https://www.oist.jp/news-center/news/2026/8/24/how-decipher-smells-fruit-fly>). Same expansion→sparse "barcode"→associative-learning motif, spiking. Reported as *best* method for few-shot and strong on continual learning, but the authors concede overall performance "compared to the best traditional machine learning classification methods could be improved."

### Open implementations (checked 2026-09-10 via `gh api`)
| Repo | What | Stars | Last push |
|---|---|---|---|
| <https://github.com/TeddyHuang-00/FlyHash> | `pip install FlyHash`, MIT, faithful 2017 algorithm | 2 | 2026-07-20 |
| <https://github.com/dataplayer12/Fly-LSH> | Reference Fly-LSH / DenseFly experiments | 89 | 2018-12-23 |
| <https://github.com/bhoov/flyvec> | `pip install flyvec`, pretrained sparse binary word vectors | 40 | 2021-12-10 |
| <https://github.com/rithram/fbfc> | Fly Bloom Filter Classifier | 2 | 2022-02-18 |
| <https://github.com/DocAILab/Document-Fingerprints> | H3D benchmark harness incl. FlyHash | — | 2026 |

The ecosystem is thin and mostly dormant. No production vector database ships a FlyHash index. Adopting this means building it.

## 3. Relevance to company-brain / RAG / fruit-fly question

**(a) Does it relate to RAG?** Directly, and it is the single most literal answer to the user's question. FlyHash is an approximate-nearest-neighbour index — the same slot HNSW/IVF/DiskANN occupy under a RAG stack. So a fruit-fly brain algorithm sits exactly at Tan's "retrieval is the primitive" layer. But that also means it addresses the part Tan explicitly says is *not* the product. Swapping HNSW for FlyHash changes nothing about curation, provenance or arbitration.

**(b) Can it be combined with the recent fruit-fly work?** Two different "fruit fly brain works" are in play and they should not be conflated:
- The **FlyWire connectome** (Nature, Oct 2024, ~140k neurons / 50M+ connections, [10.1038/s41586-024-07686-5](https://www.nature.com/articles/s41586-024-07686-5); extended to the full brain-and-cord connectome, Bates et al., *Nature*, 14 Jun 2026, [10.1038/s41586-026-10735-w](https://phys.org/news/2026-06-publish-connectome-fruit-fly-brain.html), ~160k neurons, data at codex.flywire.ai). This is a wiring map. It is **not** a retrieval algorithm and there is no published path from it to a company brain; treat claims otherwise sceptically.
- The **FlyHash algorithmic lineage** above, which *is* directly composable with a RAG stack. If someone wants to "combine the company brain with fruit-fly work," this is the lineage that actually plugs in.

**(c) Could FlyHash be the librarian's index? Honest assessment.**

*Pros.* Data-independent, so it works on day one with no training corpus — relevant to a brain that grows to 220k pages of agent-written markdown. O(1) streaming insert with no index rebuild. Sparse binary codes make Hamming/sparse-dot comparisons very cheap, and the projections themselves are ~20× cheaper than dense Gaussian. Crucially, the **fly Bloom filter gives a native, continuous, time-decaying novelty score** — one primitive that simultaneously answers "is this worth writing down?", "is this a near-duplicate of something the agent already wrote?", and "how stale is this?" That maps onto Tan's hot-vs-cold memory and his "garbage dump with great search" failure mode better than anything in a normal vector DB. And the medium-novelty band (similar but not identical) is exactly the cheap trigger for expensive LLM contradiction arbitration — you only pay for arbitration when the filter says "I have seen something close to this before."

*Cons.* Recall on semantic text is the killer. H3D 2026 shows FlyHash at roughly 39% of BGE-large's MAP on CSFCube and 65% on RELISH. Fly hashing preserves *input-space* geometry; if the input is bag-of-tokens, you get lexical matching, and paraphrase kills you. You can fix this by FlyHashing *on top of* dense embeddings — but then you have paid for the embedding model anyway and are only saving on index memory. The 2017 wins were at hash lengths k=4–32 on 10k-item datasets; the advantage compresses at realistic k, and nobody has published FlyHash beating HNSW or DiskANN on 10M+ dense semantic vectors. BioVSS's 50×/98.9% numbers are real but are for vector-*set* search under Hausdorff distance, where graph indexes do not apply cleanly. Memory is a genuine issue: the reference `FlyHash` package warns it is "cheap to compute, yet not guaranteeing memory efficiency," and is scoped to d ≈ 10–1000 → m ≈ 100–10000. Finally, the fix for the random-projection weakness (BioHash, SoftHash) reintroduces a training step and erases the "works day one" advantage.

*Recommendation.* Dense embeddings + HNSW for the read path. FlyHash + fly Bloom filter as a **write-side hygiene layer**: novelty gate on agent writes, decay clock for hot/cold tiering, and a first-stage candidate filter for arbitration. Note that the 2026 agent-memory literature reached the same architectural conclusion without the biology: **SAGE** ([arXiv:2605.30711](https://arxiv.org/pdf/2605.30711), Wang, Brahma & Henao, Duke; <https://github.com/swang1024/SAGE>) frames memory evolution explicitly as novelty detection and reports best average token-F1 vs Mem0 on all seven open-weight backbones, 3.4× lower add-phase API cost and 2.5× lower add-phase latency on GPT-4o-mini, and 16–18% fewer LLM calls as a drop-in gate for A-Mem — using a von Mises–Fisher density estimator. A fly Bloom filter would be a cheaper, streaming, closed-form drop-in for that same slot, and nobody appears to have tried it. Adjacent 2026 work on decay/forgetting: FadeMem ([arXiv:2601.18642](https://arxiv.org/abs/2601.18642)) and FSFM ([arXiv:2604.20300](https://arxiv.org/abs/2604.20300)). On the retrieval side, HASH-RAG (ACL 2025 Findings, [arXiv:2505.16133](https://arxiv.org/abs/2505.16133)) shows learned deep hashing cutting RAG retrieval time ~90% with +1.4–4.3% EM — evidence that binary hashing pays off in RAG, but via *learned* codes, not FlyHash.

## Open questions

1. Has anyone measured FlyHash/BioHash applied *on top of* modern sentence embeddings (BGE/E5/Qwen-Embedding) as a binary quantiser, against the standard binary-quantisation + rescoring baseline (~96% retrieval retained, 32× memory reduction)? I found no such head-to-head. This is the experiment that decides the question.
2. Does the fly Bloom filter's additive-increase/multiplicative-decrease decay outperform SAGE's vMF gate or FadeMem's exponential decay on LoCoMo? Untested as far as I can find.
3. Does GBrain (Tan's project) use any sparse/binary or novelty-gated indexing, or is it plain pgvector + Postgres? Not covered by this dimension.
4. What is the actual scaling ceiling for FlyHash at 10M–1B vectors? No published benchmark; all cited evaluations are 10k–15M.
5. Are the FlyWire 2024/2026 connectomes usable as anything other than an analogy for retrieval architectures? I found no work connecting the connectome dataset to information retrieval.

## Sources

- Dasgupta, Stevens, Navlakha, *Science* 358:793–796 (2017) — https://www.science.org/doi/10.1126/science.aam9868 ; PDF https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf
- Dasgupta, Sheehan, Stevens, Navlakha, *PNAS* 115(51):13093–13098 (2018) — https://www.pnas.org/doi/10.1073/pnas.1814448115 ; PDF https://repository.cshl.edu/id/eprint/38636/1/Navlakha_2018_PNAS.pdf
- Sharma & Navlakha, DenseFly — https://arxiv.org/abs/1812.01844
- Ryali, Hopfield, Grinberg, Krotov, BioHash, ICML 2020 — https://arxiv.org/abs/2001.04907 ; http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf
- Liang et al., FlyVec, ICLR 2021 — https://arxiv.org/abs/2101.06887 ; https://github.com/bhoov/flyvec
- Sinha & Ram, FBFC — https://arxiv.org/abs/2008.08685 ; https://dl.acm.org/doi/10.1145/3447548.3467246 ; https://github.com/rithram/fbfc
- Shen, Dasgupta, Navlakha, continual learning from fruit flies — https://arxiv.org/abs/2107.07617
- Bricken et al., SDM is a Continual Learner, ICLR 2023 — https://arxiv.org/abs/2303.11934
- Kleyko & Rachkovskij, design choices in sparse randomized embeddings — https://arxiv.org/html/2501.14741
- Li, Wang, Chen, Chen, Peng, BioVSS, ICDE 2025 — https://arxiv.org/html/2412.03301 ; https://sheng.whu.edu.cn/papers/25icde-B.pdf
- SoftHash — https://openreview.net/forum?id=cNwugejbW6 ; https://ieeexplore.ieee.org/abstract/document/11461356/
- H3D benchmark (Jul 2026) — https://arxiv.org/html/2607.08382 ; https://github.com/DocAILab/Document-Fingerprints
- Max & Shen, Spi-Fly, *Neuromorph. Comput. Eng.* (24 Aug 2026) — https://doi.org/10.1088/2634-4386/ae9177 ; https://www.oist.jp/news-center/news/2026/8/24/how-decipher-smells-fruit-fly ; https://techxplore.com/news/2026-08-fruit-fly-algorithm-odors-samples.html
- SAGE novelty gate — https://arxiv.org/pdf/2605.30711 ; https://github.com/swang1024/SAGE
- FadeMem — https://arxiv.org/abs/2601.18642 ; FSFM — https://arxiv.org/abs/2604.20300
- HASH-RAG, ACL 2025 Findings — https://arxiv.org/abs/2505.16133
- FlyWire connectome, *Nature* (Oct 2024) — https://www.nature.com/articles/s41586-024-07686-5 ; brain-and-cord connectome, Bates et al., *Nature* (14 Jun 2026), DOI 10.1038/s41586-026-10735-w — https://phys.org/news/2026-06-publish-connectome-fruit-fly-brain.html
- FlyHash Python package — https://github.com/TeddyHuang-00/FlyHash ; Fly-LSH — https://github.com/dataplayer12/Fly-LSH

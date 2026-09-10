# g07 — Neuro-mechanism inventory: every fly-brain mechanism the prior reports proposed transplanting

**Key:** `g07-neuro-mechanism-inventory` · gap-fill for the design phase · date 2026-09-10 · author: research worker (Claude Opus 5)

**Purpose.** The completeness critic's finding was that fourteen reports produced *fragments* of an answer to question (b) and zero buildable specs. This report is the input to the design phase: for each of the ten mechanisms the prior reports proposed, a precise algorithm (inputs / outputs / parameters), the best open implementation, the primary source, the negative results, and a fidelity rating. It does **not** propose an architecture — that is d1–d5's job. It makes sure they are working from correct algorithms rather than from paraphrases.

---

## Fidelity rubric (used throughout)

| Rating | Meaning |
|---|---|
| **Deep** | The published algorithm runs on company-brain data types with parameter changes only. The biological claim and the engineering claim are the same claim. You port code, not ideas. |
| **Analogy** | The *control structure* transfers — what triggers what, which subsystem owns which decision — but the currency changes (odour → document, valence → truth), so every parameter is re-derived and the thing must be re-validated from scratch. You port a topology. |
| **Superficial** | The biological label is decoration on an algorithm that stands on its own and was not derived from fly data. Delete the fly framing and nothing about the algorithm changes. |

Two mechanisms need split ratings and get them (7 and 8): they are good engineering with a weak biological claim, and conflating those two axes is exactly how this literature gets miscited.

---

## Summary table

| # | Mechanism | Primary source | Best open implementation | Fidelity | Single biggest caveat |
|---|---|---|---|---|---|
| 1 | FlyHash sparse expansion + k-WTA LSH | Dasgupta, Stevens & Navlakha, *Science* 358:793 (2017) | `TeddyHuang-00/FlyHash` (MIT, pip) | **Deep** (mechanism) / wrong slot (design) | No hash of an embedding beats the embedding |
| 2 | Fly Bloom filter novelty score, AIMD | Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115:13093 (2018) | `clembarr/ffbf-novelty-detector` — **0★, no license, 2 days old**; else reimplement Eq. 2 (~20 lines) | **Deep** | δ, ε are free parameters; largest n ever tested = 5,000; never tested on text |
| 3 | γ→α consolidation as readout-gated promotion | Huang et al., *Nature* 634:1141 (2024) | none direct; nearest runnable = #4 | **Analogy** (strong) | The gate is a two-node circuit fact, not a usage counter; the agent-side readout signal is hypothetical |
| 4 | Incentive circuit (3 MBON roles × 3 DAN roles) | Gkanias, McCurdy, Nitabach & Webb, *eLife* 11:e75611 (2022) | `InsectRobotics/IncentiveCircuit` (GPL-3.0, 1★) | **Analogy** | State variable is a scalar valence per cue; no content, no provenance, no query |
| 5 | Active forgetting (DAMB→Scribble→Rac1) + sleep suppression | Shuai 2010 / Berry 2012 / Cervantes-Sandoval 2016 / Berry 2015 | none fly-derived; FSFM & FadeMem are hippocampal | **Analogy** | Prunes by recency/valence/interference, never by relevance to a query; pruning KC→MBON measurably degrades classification |
| 6 | Extinction as accumulation, netted at readout | Felsenberg et al., *Cell* 175:709 (2018) | `BrainsOnBoard/paper_RPEs_in_drosophila_mb` (5★) for the RPE half | **Analogy** | Nets a *valence*, not a truth value; never returns "A is correct" |
| 7 | FlyPrompt sparse-expansion router | Yan et al., ICLR 2026, arXiv:2602.01976 | `AnAppleCore/FlyGCL` (MIT, 18★, active) | **Superficial** as fly / **Deep** as engineering | The expansion is a *dense Gaussian* matrix + ReLU. There is no k-WTA. It is not FlyHash. |
| 8 | `connectome_interpreter` effective-connectivity path compression | Yin et al., bioRxiv 2025.09.29.679410 | `YijieYin/connectome_interpreter` (MIT, 35★, active, pip) | **Superficial** as biology / **Deep** as code reuse | The operator is `A^n` on a column-normalised sparse matrix — not a fly-specific idea |
| 9 | Spi-Fly few-shot continual learning | Max & Shen, *Neuromorph. Comput. Eng.* (24 Aug 2026) | Zenodo DOI 10.5281/zenodo.18786636 — **could not resolve at check time** | **Deep** as biology / weak as transplant | Input is ≤72 sensor channels, output ≤18 class labels; BPTT overtakes it with more epochs |
| 10 | Kanerva SDM as attention | Bricken & Pehlevan, NeurIPS 2021, arXiv:2111.05498 | `TrentBrick/attention-approximates-sdm` (MIT, 27★, dormant) | **Deep** as theory / **Superficial** as transplant | Explains why your existing retriever works; does not give you a new component |

**Structural observation for the design phase.** Mechanisms 1, 2, 9 and 10 — and the mechanism 7 *claims* to be — are the same primitive: **random expansion, then sparsification, then read/write on the sparse code.** Implement it once. Mechanism 3 is a phenomenon whose only runnable formalisation is mechanism 4; mechanisms 5 and 6 are both already *inside* mechanism 4 as named roles (the forgetting DAN, the reciprocal-LTM erasure). So the ten items collapse to roughly four independent things to build: (a) a sparse-expansion coder, (b) a two-tier store with a readout-triggered promotion gate and a suppressible forgetting daemon, (c) a signed-evidence ledger netted at read, (d) a signed multi-hop graph operator. Everything else is a variant or a citation.

---

## 1. FlyHash — sparse random expansion + winner-take-all LSH

**Primary source.** Sanjoy Dasgupta, Charles F. Stevens, Saket Navlakha, "A neural algorithm for a fundamental computing problem," *Science* 358(6364):793–796, 10 Nov 2017. DOI [10.1126/science.aam9868](https://doi.org/10.1126/science.aam9868). PDF mirror: <https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf>. The cleanest formal statement of the operator is in Ryali, Hopfield, Grinberg & Krotov, ICML 2020, [arXiv:2001.04907](https://arxiv.org/abs/2001.04907).

**Algorithm.** Input is a dense feature vector `x ∈ R^d` (the biology first applies divisive normalisation across the input channels — the fly's ORN→PN gain control — so the code depends on the odour's *identity* rather than its concentration; skipping this step is a common transplant error). A **fixed sparse binary projection matrix** `M ∈ {0,1}^{m×d}` is drawn once and never trained: each of the `m` rows has exactly `s ≪ d` ones in random positions (the fly: each Kenyon cell samples ~6 of ~50 projection neurons through its dendritic "claws"). The defining property is **expansion**, `m ≫ d` — the fly runs ~50 → ~2,000, a 40× expansion; the paper's own experiments use `m = 10d`, and Ryali et al.'s FlyHash baseline uses `m = 10d` with PN→KC sampling rate 0.1. Compute `y = Mx` (adds only, no multiplies), then apply winner-take-all `Γ_ρ`: set the top `ρ` entries of `y` to 1 and everything else to 0. Output is a sparse binary code `h(x) = Γ_ρ(Mx) ∈ {0,1}^m` with exactly `ρ` ones — the fly holds `ρ/m ≈ 5%` via the GABAergic APL feedback loop; the paper reports results sweeping hash length `k = ρ` from 2 to 64. Compare codes by Hamming distance, sparse dot product, or Jaccard. **Parameters:** `d`, `m` (or the expansion factor `m/d`), `s` (fan-in per row), `ρ` (number of winners), and the RNG seed — the seed is part of the index and must be persisted or every code you ever wrote becomes garbage. **Cost:** `O(sm)` integer adds per item; the paper reports the sparse binary projection gives "near-identical performance" to a dense Gaussian projection at a **factor-of-20 computational saving**.

**Reported results.** MNIST, `k = 4`: classical LSH 16.0% mAP → fly 44.8% (~3×). SIFT, `k = 4`, WTA tag selection vs random tag selection at equal op count: 17.7% → 32.4%. Evaluation protocol: SIFT (d=128), GLOVE (d=300), MNIST (d=784), 10,000 items each, 1,000 queries, top-2% true nearest neighbours, mAP over 50 trials. **The gains are largest at short hash lengths and shrink as `k` grows** — routinely dropped when this paper is cited.

**Best open implementations.**
- [`TeddyHuang-00/FlyHash`](https://github.com/TeddyHuang-00/FlyHash) — MIT, `pip install FlyHash`, faithful to the 2017 algorithm, 2★, last push 2026-07-20. Its own docs warn it is "cheap to compute, yet not guaranteeing memory efficiency," scoped to d ≈ 10–1000 → m ≈ 100–10000.
- [`dataplayer12/Fly-LSH`](https://github.com/dataplayer12/Fly-LSH) — MIT, 89★, reference Fly-LSH/DenseFly experiments, dormant since 2018-12-23.
- [`rithram/fbfc`](https://github.com/rithram/fbfc) — MIT, 2★, KDD 2021. Its README carries the cleanest definition in any repo: `h(x) = Γ_ρ(M_m^s x)`, with `M_m^s ∈ {0,1}^{m×d}` sparse binary and `Γ_ρ` the top-ρ WTA.

No production vector database ships a FlyHash index. Adopting this means building it.

**Negative results.**
- **H3D** ([arXiv:2607.08382](https://arxiv.org/abs/2607.08382), 9 Jul 2026): FlyHash 0.1325 MAP on CSFCube-overall and 0.4305 on RELISH-test vs 0.3431 / 0.6626 for dense frozen BGE-large. **But** — as `v10a-h3d-flyhash.md` established — H3D ran a *contraction* (216 → 128 bits, 8 active) over 3-shingle term-frequency counts, which inverts the algorithm's defining property, and FlyHash was **the worst of the five lexical hashes tested**, losing to Winnowing (0.2678 / 0.4996) by more than quantisation costs. The correct citation is "a 40-bit lexical fingerprint is a bad semantic index," not "the fly algorithm is."
- **Kleyko & Rachkovskij** ([arXiv:2501.14741](https://arxiv.org/html/2501.14741), Dec 2024): design choices make a "drastic difference"; **k-block sparse codes consistently beat plain k-WTA** at matched bits. The authors position optimised FlyHash for *memory-constrained* settings and do **not** claim it beats dense methods.
- No published benchmark shows FlyHash beating HNSW or DiskANN on 10M+ dense semantic vectors. BioVSS's "50× / 98.9% recall" ([arXiv:2412.03301](https://arxiv.org/html/2412.03301), ICDE 2025) is vector-**set** search under Hausdorff distance, where graph indexes do not apply cleanly — do not read it as "FlyHash beats HNSW."
- The fix for the random-projection weakness (BioHash, ICML 2020; SoftHash) reintroduces a training step and erases the "works on day one" advantage.
- **Ryali et al. Table 8** is the one result that matters for the design phase, because it measures FlyHash *on top of dense embeddings* (GloVe, d=300), against cosine ground truth in the original space: mAP@100 at k=2/4/8/64 = 15.06 / 17.09 / 24.64 / 72.37 for FlyHash vs 0.41 / 0.65 / 2.23 / 32.60 for classical LSH and 0.76 / 1.84 / 6.84 / 61.15 for ITQ. FlyHash competes with LSH/ITQ/binary-quantisation **as a compressor of an embedding**. It never competes with the embedding.

**Fidelity: Deep (as a mechanism); wrong slot (as a design proposal).** The algorithm *is* the circuit — one sparse matmul and a top-k, with the fly's own numbers as the default parameters. Nothing is re-derived. But the role the prior reports keep gesturing at (semantic index) is the role where it demonstrably loses, and Tan's own argument is that the index is not the product. Its defensible slot is as the coder underneath mechanism 2.

---

## 2. Fly Bloom filter — continuous novelty with additive-increase / multiplicative-decay

**Primary source.** Sanjoy Dasgupta, Timothy C. Sheehan, Charles F. Stevens, Saket Navlakha, "A neural data structure for novelty detection," *PNAS* 115(51):13093–13098, 18 Dec 2018. DOI [10.1073/pnas.1814448115](https://doi.org/10.1073/pnas.1814448115). Open PDF: <https://repository.cshl.edu/id/eprint/38636/1/Navlakha_2018_PNAS.pdf> (read directly for this report). Biological grounding: Hattori et al., *Cell* 169:956–969 (2017), DOI [10.1016/j.cell.2017.04.028](https://doi.org/10.1016/j.cell.2017.04.028) — the MBON-α′3 familiarity signal.

**Algorithm.** State is a weight vector `w ∈ [0,1]^m`, one weight per Kenyon cell, **all initialised to 1** (the paper describes an *inverted* Bloom filter so that novel items give a high score). Biologically `m = 350` — the number of the 2,000 KCs that MBON-α′3 reads; in the paper's experiments `m = 30n` where `n = |S|`, with a robustness check at `m = 10n`. For a query `x`: compute the FlyHash code (mechanism 1) and take `A(x)`, the index set of the `k` active KCs. **Read before write:** `novelty(x) = (1/k) · Σ_{i ∈ A(x)} w(i) ∈ [0,1]`. Then insert `x` by updating every weight (paper's Eq. 2):

```
w(i) ← w(i) · δ     if i ∈ A(x)      (multiplicative decay,  0 ≤ δ < 1)
w(i) ← w(i) + ε     if i ∉ A(x)      (additive increase,     0 ≤ ε ≤ 1)
```

clipped to `[0,1]`. Setting `δ = ε = 0` recovers a classical binary Bloom filter exactly. The paper's Discussion states the functional forms of ε and δ follow an **additive-increase, multiplicative-decrease** schedule justified from experimental data (SI Fig. S3), and notes the same family of multiplicative update rules is standard in online learning. **Inputs:** a stream of items (as dense vectors). **Outputs:** a continuous novelty score in [0,1] per item, plus updated fixed-size state. **Parameters:** `m`, `k`, `δ`, `ε`, the underlying projection (`d`, `s`), and optionally a wall-clock tick rate at which ε is applied independently of arrivals. **Space:** `O(m)` floats plus the projection — *independent of the number of items ever inserted*, which is the property that matters for a brain that grows without bound.

**The three properties that make this different from every other Bloom filter, and it has all three at once:** (i) *continuous* scores rather than a membership bit; (ii) *distance sensitivity* — the objective is `f(x,S) = min_{s∈S} d(x,s)`, so a near-duplicate suppresses novelty, which a hash-based filter cannot do; (iii) *time sensitivity* — the ε drift means an item whose neighbourhood stops arriving becomes novel again. The paper motivates (iii) explicitly for "life-long learning applications, where the database is not of fixed size but continuously grows … unless old data are forgotten, the Bloom filter would eventually fill up such that every bit is reset to zero." That is a company brain, described in a 2018 neuroscience paper.

**Reported results** (correlation between ground-truth novelty and predicted novelty, 10-fold CV, five datasets):

| Dataset | n, d | Fly | LSBF | Traditional Bloom |
|---|---|---|---|---|
| Fly odours | 110, 24 | **0.657 ± 0.06** | 0.537 ± 0.08 (k=40) | ≈ 0 |
| Primate faces | 2,000, 99 | **0.508 ± 0.03** | 0.404 ± 0.03 | ≈ 0 |
| SIFT | 5,000, 128 | **0.535 ± 0.03** | 0.345 ± 0.03 | 0.002 ± 0.02 |
| MNIST | 5,000, 784 | fly wins | — | ≈ 0 |
| Random exponential | 1,000, 20 | fly wins | — | ≈ 0 |

**Best open implementations.**
- [`clembarr/ffbf-novelty-detector`](https://github.com/clembarr/ffbf-novelty-detector) — Rust core + Python bindings, `add()` / `tick()` API, ~4.7 KiB of state at m=1200, and a README that independently arrives at exactly the roles the prior reports proposed ("ingestion and dedup: drop near-duplicates before an expensive stage (embedding, indexing, an LLM call)"; "cache admission and routing"; "drift alarms — because the filter forgets, a regime that goes quiet becomes detectable again"). **Handle with care: 0 stars, no LICENSE file (so not legally reusable as-is), first pushed 2026-09-08 — two days before this report, and by an unidentified author. No benchmark, no provenance.** Treat it as a reference reading, not a dependency.
- [`rithram/fbfc`](https://github.com/rithram/fbfc) — MIT, the peer-reviewed (KDD 2021) *classifier* variant: per-class fly Bloom filters, `w_l = ¬(⋁_{y=l} h(x))` for the binary form, with a non-binary form for label-noise robustness. Closest thing to citable code.
- Honestly: Eq. 2 is about twenty lines. Reimplementing is cheaper and safer than adopting either.

**Negative results and honest limits.**
- The paper itself: "there is little biological knowledge of how distance sensitivity and time sensitivity combine to create a single novelty response." The **combined** distance+time case appears only in SI Appendix (candidate objective functions, Table S4), not in the main results. So the exact property a hot/cold tiering system would depend on is the one the paper is least confident about.
- `δ` and `ε` are **free parameters with no data-derived values.** Only the AIMD *shape* is evidenced.
- Largest evaluation is `n = 5,000`. Nothing at 10⁵–10⁶ documents.
- **Never tested on text or on embeddings.** Every dataset is a low-dimensional sensor/pixel/descriptor vector.
- A competitor already occupies this architectural slot with agent-memory benchmarks the fly filter does not have: **SAGE** ([arXiv:2605.30711](https://arxiv.org/pdf/2605.30711), [`swang1024/SAGE`](https://github.com/swang1024/SAGE), Apache-2.0, 7★, pushed 2026-09-04) frames memory evolution as novelty detection with a von Mises–Fisher density estimator and reports 3.4× lower add-phase API cost, 2.5× lower add-phase latency, and 16–18% fewer LLM calls as a drop-in gate for A-Mem. The head-to-head vs a fly Bloom filter has not been run. That is the cheapest decisive experiment in this whole inventory.

**Fidelity: Deep.** Same data type, same streaming regime, same problem statement. The only re-derivation needed is choosing δ and ε, and the biology tells you the shape of that choice. This is the one mechanism in the inventory that can be built exactly as published.

---

## 3. Mushroom-body compartment consolidation γ→α as readout-gated promotion

**Primary source.** Cheng Huang, Junjie Luo, Seung Je Woo, Lucas A. Roitman, Jizhou Li, Vincent A. Pieribone, Madhuvanthi Kannan, Ganesh Vasan, Mark J. Schnitzer, "Dopamine-mediated interactions between short- and long-term memory dynamics," *Nature* 634:1141–1149, published 22 Jul 2024 (issue 24 Oct 2024). DOI [10.1038/s41586-024-07819-w](https://doi.org/10.1038/s41586-024-07819-w) · PMID 39038490 · open access at [PMC11525173](https://pmc.ncbi.nlm.nih.gov/articles/PMC11525173/).

**The biology, precisely.** Hot tier = the **γ compartments**, roughly a 30-minute plasticity time constant; MBON-γ1pedc>α/β depression lasts **under 1 hour**. Cold tier = **α′2α2 and α3**, roughly a 100-minute decay for the first ~3 hours post-conditioning and then a much slower constant; **MBON-α3 depression persists beyond 24 hours**. The promotion mechanism is the interesting part and it is not a timer:

1. During initial conditioning bouts, PPL1-γ1pedc and PPL1-γ2α′1 write short-term memory.
2. That writing **depresses MBON-γ1pedc>α/β**.
3. MBON-γ1pedc>α/β sends **inhibitory feedback onto PPL1-α′2α2 and PPL1-α3**; depressing it *weakens that inhibition*.
4. Only with the inhibition lifted do those two PPL1-DANs encode the **net innate + learnt valence** of the conditioned odour — and that signal **gates long-term memory formation**.

Roughly **three conditioning bouts** are needed: with repulsive odours, MBON-α3 shows sustained suppression across 24+ hours after three bouts; with attractive odours, initial plasticity appears after three bouts and strengthens with three more. Evidence: time-lapse *in vivo* voltage imaging of neural spiking in **more than 500 flies** undergoing olfactory associative conditioning. The accompanying model is a **9-neuron spiking network across 3 modules (γ1, α2, α3)** — 5 dopamine neurons, 3 MBONs, 2 Kenyon cells, 1 shock-sensing neuron — with bidirectional anti-Hebbian plasticity ("KC activation coinciding with DAN activation or suppression respectively weakens or strengthens the corresponding KC→MBON connection"), constrained by the fly connectome and the spiking data, and it made inter-stimulus-interval and extinction-timing predictions that the authors then confirmed experimentally.

**Algorithm as transplanted.** Maintain a hot store `H` with fast decay `τ_H` and a cold store `C` with slow decay `τ_C` (the fly's ratio is roughly 30 min : >24 h, i.e. ~50×). Each item `i` carries a **readout signal** `r_i` — in the fly this is the *depression of the hot MBON*, i.e. how far the hot representation has moved from its baseline, not a hit counter. Promotion daemon: define an inhibition term `inh_i = g(r_i)` that falls as `r_i` grows; the promotion channel for item `i` is open iff `inh_i < θ_inh`; promote `i` from `H` to `C` once the channel has been open on `B ≈ 3` distinct occasions, and write the **net score** (prior/innate valence + accumulated learnt evidence) rather than the raw item. **Inputs:** the stream of items plus their readout/retrieval events. **Outputs:** promotions into the cold tier, carrying a net score. **Parameters:** `τ_H`, `τ_C`, `B` (bout count), `θ_inh`, the prior weighting, and `g`.

**The one architectural idea worth stealing:** *consolidation is not a cron job; it is triggered by the hot tier's own readout crossing a threshold.* Current agent-memory systems do the opposite — agents write, and a scheduled process later prunes. A γ→α design lets the retrieval signal itself decide promotion. This is a real, copyable inversion of control and it is the strongest single item in the "hot vs cold" row of the prior reports' mapping table.

**Best open implementation.** **None is a drop-in.** The paper's model is nine neurons; a code-availability URL was not recoverable at check time. The only *runnable* formalisation of the same STM→LTM assimilation phenomenon is Gkanias 2022's `IncentiveCircuit` (mechanism 4), which implements the transfer as an explicit named microcircuit (MAM). The design phase should treat mechanism 3 as **a specification of a trigger, whose implementation is mechanism 4 or bespoke.**

**Negative results and untested assumptions.**
- The load-bearing assumption — that an agent brain has a readout signal playing MBON-γ1pedc>α/β's role — **is untested**. The fly's gate is *disinhibition of a specific DAN by a specific MBON*: a two-node circuit fact, not a scalar. "Retrieval frequency" is the obvious proxy and nobody has shown it works. `mushroom-body-memory-models.md` lists this as its open question 3.
- The fly promotes by **valence**, never by relevance to a query. Nothing in this circuit knows what a question is.
- The consolidated object is a scalar synaptic weight. The episode is discarded. There is no provenance anywhere in this mechanism, and adding it changes the mechanism.
- Doomfly ([`nftechie/doomfly`](https://github.com/nftechie/doomfly)) is the only public attempt to run MB plasticity on a real task (4,184 KC→MBON11 connections with a dopamine-gated rule) and its own README states it **failed its visual, conditioning and survival validation gates**. That is a single negative data point, in a game, but it is the only empirical one.

**Fidelity: Analogy (strong).** The control structure transfers and is genuinely novel relative to shipped systems. The algorithm does not — you are porting a trigger topology and re-deriving every constant.

---

## 4. Gkanias 2022 incentive circuit — susceptible / restrained / LTM MBONs, discharging / charging / forgetting DANs

**Primary source.** Evripidis Gkanias, Li Yan McCurdy, Michael N. Nitabach, Barbara Webb, "An incentive circuit for memory dynamics in the mushroom body of *Drosophila melanogaster*," *eLife* 11:e75611 (2022). DOI [10.7554/eLife.75611](https://doi.org/10.7554/eLife.75611).

**Circuit composition** (6 MBONs and 6 DANs = 2 valences × 3 roles each, plus KCs):

| Role | Avoidance identity | Attraction identity |
|---|---|---|
| **Susceptible MBON** | MBON-γ4>γ1γ2 | MBON-γ1pedc>α/β |
| **Restrained MBON** | MBON-γ2α′1 | MBON-γ5β′2a |
| **LTM MBON** | MBON-α′1 | MBON-β2β′2a |
| **Discharging DAN** | PPL1-γ2α′12 | PAM-γ4<γ1γ2 |
| **Charging DAN** | PPL1-γ2α′1 (MB296B1 terminal) | PAM-β′2a |
| **Forgetting DAN** | PPL1-γ2α′1 (MB296B2 terminal) | PAM-β2β′2a |

**The dopaminergic plasticity rule (DPR).** For the KC→MBON weight from KC *i* to MBON *j*:

```
ΔW_ij(t) = δ_j(t) · [ k_i(t) + W_ij(t) − w_rest ]        with w_rest = 1
```

where `k_i(t) ≥ 0` is KC activity and `δ_j(t)` is the dopaminergic factor whose sign comes from the DAN responses in that compartment. Four regimes fall out of one equation: **depression** (`δ<0`, KC active → weight falls), **potentiation** (`δ>0`, KC active → weight rises), **recovery** (`δ<0`, KC *inactive* → the weight relaxes back toward `w_rest`), **saturation** (`δ>0`, KC inactive → weight diverges further from rest). The recovery term is the one with no counterpart in standard ML plasticity rules and it is what gives the circuit spontaneous forgetting-toward-baseline for free. KCs are sparsified by a **top-50%-active WTA threshold** (the published runs use only 10 KCs for 2 odours; the authors state the neuron count "is not very important").

**Five named microcircuits** — this is the part a design phase can lift wholesale, because it is a complete cache hierarchy with named processes:

- **SM (susceptible memory):** discharging DAN depresses the susceptible MBON; the susceptible MBON inhibits the discharging DAN (negative feedback → self-limiting write buffer).
- **RM (restrained memory):** the susceptible MBON directly inhibits the restrained MBON of the opposite valence.
- **RSM (reciprocal short-term memory):** restrained MBON excites the charging DAN; the charging DAN depresses the *opposite-valence* restrained MBON — a positive feedback loop that drives consolidation.
- **LTM:** charging DAN potentiates the LTM MBON; the LTM MBON excites the charging DAN — self-sustaining positive feedback, the durable store.
- **RLM (reciprocal LTM):** the LTM MBON excites the **forgetting DAN**, which depresses the opposite-valence LTM MBON — gradual erasure of contrary long-term memory under persistent reinforcement.
- **MAM (memory assimilation):** the forgetting DAN depresses the *same-valence* restrained MBON — i.e. **the same neuron that erases the contrary LTM also clears the STM entry once it has been transferred.** Promotion and eviction are one operation.

**Inputs / outputs / parameters.** Inputs: a sparse KC code for the cue plus a reinforcement signal. Outputs: a motivation state per cue (attraction vs avoidance) — a scalar, netted across the six MBONs. Parameters: per-connection weights (hand-set from anatomy, not fitted), `w_rest = 1`, KC sparsity (top 50%), and the update rate.

**Validation.** Predicted the effects of **92 olfactory-conditioning intervention experiments drawn from 14 studies** (silencing/activating specific neurons), `r = 0.76`, `p = 2.2 × 10⁻¹⁸`. Also reproduced calcium-imaging dynamics across acquisition / extinction / unpaired / reversal phases, and behaviour of freely-moving simulated flies in odour gradients.

**Best open implementation.** [`InsectRobotics/IncentiveCircuit`](https://github.com/InsectRobotics/IncentiveCircuit) — **GPL-3.0** (note: copyleft; check this against your licensing before porting), 1★, last push 2023-12-02, Python 3.7 + NumPy/SciPy/Matplotlib/pandas/PyYAML. Ships a `generate_manuscript.ipynb` that reproduces every figure, plus per-figure scripts (`run_bennett_2021.py`, `plot_model.py --only-nids --values --weights`, `create_arena_paths.py`, …). This is the most complete runnable MB memory-dynamics model in existence and it is 1 star.

**Negative results — the authors' own, which are unusually candid.**
1. The biophysical basis of the `w_rest` deviation term is **unknown**; the authors speculate about synapsin.
2. Neglected connections: **APL inhibition** (which is what enforces KC sparseness in the real fly — see Lin et al., *Nat. Neurosci.* 17:559, DOI [10.1038/nn.3660](https://doi.org/10.1038/nn.3660)), KC→KC, KC→DAN, DAN→MBON, and axo-axonic connectivity.
3. **The model fails to reproduce blocking.** Excused on the grounds that flies do not show blocking either, and attributed to sparse KC coding — but it is a failure of a canonical associative-learning phenomenon and should be stated.
4. Only 1 of a proposed 8 opposing-motivation pairs ("incentive wheel") is actually tested.
5. LTM neuron responses depend on "overall experience" and are hard to validate against single experiments.
6. The reward-prediction-error comparison is limited: the authors argue their DPR outperforms an RPE rule but concede RPE "could be implemented" by alternative circuits.
7. KC representation is 10 neurons for 2 odours.

**Fidelity: Analogy.** The three-tier MBON typing is almost literally a cache hierarchy (write buffer / working set / durable store) and the **named forgetting DAN** is almost literally Tan's librarian — which is why this is the most quotable item in the inventory. But its state variable is a scalar valence per (cue, compartment). No propositional content, no authorship, no query. Porting means keeping the control graph — 6 roles, 6 microcircuits, one plasticity rule with a recovery term — and replacing the entire currency.

---

## 5. Active forgetting: DAMB → Scribble → Rac1 → cofilin, with sleep suppression

**Primary sources** (four, and all four are load-bearing):
- Yichun Shuai, Binyan Lu, Ying Hu, Lianzhang Wang, Kan Sun, Yi Zhong, "Forgetting is regulated through Rac activity in *Drosophila*," *Cell* 140:579–589 (2010). DOI [10.1016/j.cell.2009.12.044](https://doi.org/10.1016/j.cell.2009.12.044).
- Jacob A. Berry, Isaac Cervantes-Sandoval, Eric P. Nicholas, Ronald L. Davis, "Dopamine is required for learning and forgetting in *Drosophila*," *Neuron* 74:530–542 (2012). DOI [10.1016/j.neuron.2012.04.007](https://doi.org/10.1016/j.neuron.2012.04.007) · PMID 22578504 · [PMC4083655](https://pmc.ncbi.nlm.nih.gov/articles/PMC4083655/).
- Isaac Cervantes-Sandoval, Molee Chakraborty, Courtney MacMullen, Ronald L. Davis, "Scribble scaffolds a signalosome for active forgetting," *Neuron* 90:1230–1242 (2016). DOI [10.1016/j.neuron.2016.05.010](https://doi.org/10.1016/j.neuron.2016.05.010) · [PMC4926877](https://pmc.ncbi.nlm.nih.gov/articles/PMC4926877/).
- Jacob A. Berry, Isaac Cervantes-Sandoval, Molee Chakraborty, Ronald L. Davis, "Sleep facilitates memory by blocking dopamine neuron-mediated forgetting," *Cell* 161:1656–1667 (2015). DOI [10.1016/j.cell.2015.05.027](https://doi.org/10.1016/j.cell.2015.05.027) · PMID 26073942 · [PMC4671826](https://pmc.ncbi.nlm.nih.gov/articles/PMC4671826/).

**The biology, precisely.** Forgetting in the fly is **not decay and not a TTL**; it is an actively driven process with a dedicated molecular pathway that is *separable from acquisition at the same synapse*:

- **Separate receptors.** Acquisition requires the **dDA1** dopamine receptor; forgetting requires **DAMB**, also highly expressed in mushroom-body neurons (Berry 2012). One transmitter, two channels, opposite jobs.
- **Separate downstream cascade.** Scribble scaffolds **Rac1 → Pak3 → cofilin** actin remodelling inside MB neurons; knocking down *scribble* in either MB neurons or DANs impairs normal memory loss (Cervantes-Sandoval 2016). Inhibiting Rac extends early memory **from a few hours to more than one day** and blocks interference-induced forgetting; elevating Rac in MB neurons **accelerates** decay; neither manipulation affects acquisition, and the mechanism is independent of Rutabaga-adenylyl-cyclase-mediated formation (Shuai 2010).
- **The rate is set by two continuously-active DANs.** MP1 and MV1 show synchronised **ongoing** activity in the MB neuropil in awake flies, before *and after* learning (Berry 2012) — the pruning process runs all the time, not on a schedule tied to writes.
- **Behavioural state gates it.** That ongoing dopaminergic activity **rises robustly with locomotor activity and falls with rest**. Increasing sleep drive — pharmacologically with Gaboxadol or by genetically stimulating the sleep circuit — **decreases** ongoing dopaminergic activity and **enhances retention**; increasing arousal **stimulates** it and accelerates forgetting (Berry 2015). The fly does not consolidate during sleep so much as *stop deleting*.

**Algorithm as transplanted.** A forgetting daemon that is (a) **separately parameterised from the write path**, (b) **continuously running rather than write-triggered**, and (c) **suppressible by a system-state signal**. Effective attenuation of record `i` over an interval: `Δ_i = ρ_f · (1 − s(t)) · h(i) · Δt`, where `ρ_f` is the global forgetting rate (the MP1/MV1 tone), `s(t) ∈ [0,1]` is the suppression signal from the "sleep" schedule, and `h(i)` is an interference term that rises when new near-duplicate records arrive in `i`'s neighbourhood (the fly's interference-induced forgetting; note this is exactly what mechanism 2's Bloom filter already computes for free). A second, independent channel per record — the DAMB analogue — so pruning cannot be achieved merely by declining to write. **Inputs:** the record set, an activity/traffic signal, and a quiet-window schedule. **Outputs:** attenuated or evicted records. **Parameters:** `ρ_f`, the `s(t)` schedule (which windows are quiet), the interference sensitivity, and a floor below which a record is deleted outright rather than attenuated.

**Best open implementation.** **None that is fly-derived.** The nearest agent-memory work is all 2026 and all framed from *hippocampal* / Ebbinghaus premises, citing no MB literature:
- **FSFM** ([arXiv:2604.20300](https://arxiv.org/abs/2604.20300)) — taxonomises passive-decay / active-deletion / safety-triggered / adaptive-reinforcement forgetting.
- **FadeMem** ([arXiv:2601.18642](https://arxiv.org/abs/2601.18642)) — exponential decay.
- **ZenBrain** ([arXiv:2604.23878](https://arxiv.org/abs/2604.23878)) — a sleep-phase consolidation loop (consolidation, not pruning suppression — the opposite reading of sleep from Berry 2015).

None implements a *suppressible* pruning daemon with a second independent channel. This is genuinely unclaimed ground and it is also the least-validated proposal in the inventory.

**Negative results.**
- **Xie & Ocker**, "The Impact of Structural Changes on Learning Capacity in the Fly Olfactory Neural Circuit," [arXiv:2509.19351](https://arxiv.org/abs/2509.19351): random and targeted pruning of KC→MBON synapses degrades odour classification in largely the same way ablation does, MBONs with very few presynaptic KCs consistently perform worst, and **ablating developmentally mature KCs hurts more than ablating immature ones**. A direct caution against aggressive pruning of a well-established index, and a hint that "prune the old stuff" is the wrong default.
- The fly prunes by **recency, valence, and interference — never by relevance to a query.** The policy does not transfer; only the architecture does.
- 2025–26 fly work shows forgotten memories persist as **silent MBON traces** recoverable by context-gated dopaminergic reminders, and that the same machinery generates **false memories** ([PMC13533848](https://pmc.ncbi.nlm.nih.gov/articles/PMC13533848/)). A biological precedent for stale facts resurfacing with confidence — and an argument that "forgetting" in this family means *suppressing expression*, not deleting the row.

**Fidelity: Analogy.** The engineering claim — *forgetting should be a first-class, continuously-running, separately-parameterised, suppressible subsystem rather than a TTL* — is genuinely derived from the biology and is genuinely not what shipped agent-memory systems do. That is a real contribution. Everything about *what* to forget has to be rewritten.

---

## 6. Extinction as accumulation — parallel opposing memories netted at readout

**Primary source.** Johannes Felsenberg, Pedro F. Jacob, Thomas Walker, Oliver Barnstedt, Amelia J. Edmondson-Stait, Markus W. Pleijzier, Nils Otto, Philipp Schlegel, Nazil Sharifi, Emmanuel Perisse, Carlas S. Smith, J. Scott Lauritzen, Marta Costa, Gregory S. X. E. Jefferis, Davi D. Bock, Scott Waddell, "Integration of Parallel Opposing Memories Underlies Memory Extinction," *Cell* 175:709–722 (2018). DOI [10.1016/j.cell.2018.08.021](https://doi.org/10.1016/j.cell.2018.08.021) · PMID 30245010 · open access [PMC6198041](https://pmc.ncbi.nlm.nih.gov/articles/PMC6198041/).

**The biology, precisely.** Extinction of an aversive memory does **not** erase or overwrite the original. Re-presenting the cue without punishment recruits **reward DANs** — the *omission of expected punishment is itself remembered as a positive experience*. Functional imaging shows intracellular calcium traces for the original aversive memory and the new appetitive extinction memory **coexisting in different places in the MBON network**. Light and ultrastructural anatomy show the competing traces converging onto shared avoidance-driving MBONs, and extinction-evoked plasticity in a pair of those neurons **neutralises** the potentiated odour response the aversive learning had imposed. The paper's own summary: "flies track the accuracy of learned expectations by **accumulating and integrating memories of conflicting events**."

**Algorithm as transplanted.** Contradictions are never resolved at write time and no claim is ever overwritten. Each claim `c` carries an **append-only ledger of signed evidence events** `(t, sign, magnitude, source, compartment)`, written into *separate stores* — the compartmentalisation is load-bearing, because it is what lets the two traces decay at different rates. At **read** time the reader computes `net(c) = Σ_t f(sign_t, magnitude_t, age_t)` and returns both the net score and the ledger. Writes are gated on **prediction error**: only write when `|observed − expected| > θ_PE`, where `expected` is the current net (see Bennett, Philippides & Nowotny, *Nat. Commun.* 12:2569, 2021, DOI [10.1038/s41467-021-22592-4](https://doi.org/10.1038/s41467-021-22592-4), for DANs computing *reinforcement prediction error* from MBON feedback rather than absolute reinforcement; and Jiang & Litwin-Kumar, *PLoS Comput. Biol.* 17(8):e1009205, DOI [10.1371/journal.pcbi.1009205](https://doi.org/10.1371/journal.pcbi.1009205), for RPE emerging as a *population mode* across heterogeneous DANs). **Inputs:** evidence events. **Outputs:** a net score plus the full ledger. **Parameters:** the netting function `f`, the per-compartment decay rates (this is what makes older contrary evidence lose weight without being deleted), and `θ_PE`.

**Best open implementations.**
- [`BrainsOnBoard/paper_RPEs_in_drosophila_mb`](https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb) — 5★, code and data for Bennett et al. 2021. Covers the *write-gating* half (prediction error from MBON feedback).
- [`InsectRobotics/IncentiveCircuit`](https://github.com/InsectRobotics/IncentiveCircuit) — GPL-3.0, reproduces acquisition / **extinction** / unpaired / reversal in one framework, and `run_unpaired_a.py` is literally the extinction protocol.
- Modelling context: Springer & Nawrot, *eNeuro* 8(3):ENEURO.0549-20.2021, DOI [10.1523/ENEURO.0549-20.2021](https://doi.org/10.1523/ENEURO.0549-20.2021) (mutually inhibiting appetitive/aversive pathways); Eschbach et al., *Nat. Neurosci.* 2020, DOI [10.1038/s41593-020-0607-9](https://doi.org/10.1038/s41593-020-0607-9) (recurrent DAN↔MBON architecture).
- On the engineering side the closest shipped analogue is **bi-temporal invalidation** (Graphiti / Zep), which *supersedes* rather than nets — a materially different choice, and the one a design phase should benchmark against.

**Negative results and the currency problem.**
- **The fly nets a valence, not a truth value.** Two documents disagreeing about a launch date do not have opposite signs on a scalar. There is no operation anywhere in this circuit that returns "claim A is correct." `mushroom-body-memory-models.md` rates this row "right shape, wrong currency" and that is the correct verdict.
- **It never resolves.** A running total is the output. A company brain usually needs a decision.
- The false-memory pathology cited under mechanism 5 is generated by exactly this machinery: accumulate-and-net with context-gated reinstatement is *how* confident wrong answers get produced.
- Aso & Rubin, *eLife* 5:e16135 (2016), DOI [10.7554/eLife.16135](https://doi.org/10.7554/eLife.16135) — a useful complication: "even a single DAN cell type can either write or reduce an aversive memory, or write an appetitive memory, depending on **when** it is activated relative to odour delivery," with extensive differences in training requirements, decay dynamics, storage capacity and flexibility across the 20 DAN types. There is no single learning rule to port; there are ~20 of them and timing selects between them.

**Fidelity: Analogy.** The *shape* — keep both claims with signed evidence, net at readout, gate writes on prediction error — is a real and under-used alternative to "an LLM judges which fact wins," and it is cheap to implement. The semantics do not transfer at all, and the design phase must say so in the same breath.

---

## 7. FlyPrompt — "sparse-expansion router" (ICLR 2026)

**Primary source.** Hongwei Yan, Guanglong Sun, Kanglei Zhou, Qian Li, Liyuan Wang, Yi Zhong, "FlyPrompt: Brain-Inspired Random-Expanded Routing with Temporal-Ensemble Experts for General Continual Learning," ICLR 2026. [arXiv:2602.01976](https://arxiv.org/abs/2602.01976). Yi Zhong's lab (Tsinghua School of Life Sciences / IDG-McGovern) is an actual *Drosophila*-memory lab — the same Zhong on the Rac1 forgetting paper (mechanism 5), which is what makes the fly framing here look more authoritative than it is.

**Algorithm — two components.**

*(a) REAR — Randomly Expanded Analytic Router.* Input: a frozen backbone embedding `h = f_θ(x) ∈ R^d` (ViT). Expansion: `φ(x) = σ(hR) ∈ R^M` with `M = 10,000`, `σ = ReLU`, and `R_ij ~ N(0,1)` — **a dense Gaussian random matrix.** The router `U ∈ R^{T×M}` (for `T` experts) is solved in **closed form** by ridge regression, no gradients and one pass: `Û^T = (G + λI)^{-1} Q`, where `G` accumulates Gram matrices `Σ φφ^T` and `Q` accumulates expert-wise feature sums — i.e. recursive least squares, updated incrementally as the stream arrives. Routing score `s(x) = φ(x) Û^T ∈ R^T`; the selected expert is `Ê(x) = argmax_t s_t(x)`. Regularisation `λ = 10⁴` (Sup-21K) to 10⁷ (iBOT/DINO backbones).

*(b) TE² — temporal ensemble of output heads.* Each expert keeps one online (trainable) head plus `n = 2` EMA copies with different decay rates `α ∈ {0.9, 0.99}`: `W_t^{(j)} ← α_j W_t^{(j)} + (1 − α_j) W`. At inference, take the **element-wise maximum** of the softmax outputs across all `n+1` heads, then apply logit masking.

**Inputs / outputs / parameters.** Inputs: a single-pass, non-stationary stream with no task boundaries (Si-Blurry online class-incremental). Outputs: class predictions. Parameters: `M` (10,000), `T` (experts), `λ`, `n` (2), the `α` set, and the backbone choice.

**Reported results** (A_last, Sup-21K backbone): CIFAR-100 **86.76** vs CODA-P 80.91; ImageNet-R **55.27** vs CODA-P 48.09; CUB-200 **73.40** vs CODA-P 62.90. A_auc: 83.24 vs MISA 80.35 (CIFAR-100); 56.58 vs MISA 51.52 (ImageNet-R). The abstract's headline "up to 11.23% / 12.43% / 7.62% gains" is against the full SOTA baseline set. Ablation (CIFAR-100, A_last): full 86.76 → −TE² 84.23 → −REAR 83.75 → both removed 73.30.

**Best open implementation.** [`AnAppleCore/FlyGCL`](https://github.com/AnAppleCore/FlyGCL) — **MIT, 18★, actively maintained (pushed 2026-09-04)**, model card at [huggingface.co/HoraceYan/FlyGCL](https://huggingface.co/HoraceYan/FlyGCL). Ships `flyprompt` plus twelve baselines (`l2p`, `dualprompt`, `codaprompt`, `mvp`, `misa`, `slca`, `sprompt`, `ranpac`, `hide`, `norga`, `sdlora`), ViT backbones via `timm`, and a true online Si-Blurry setting with configurable disjoint/blurry ratios. **This is the best-maintained repo in the entire inventory** — which is worth noting precisely because its biological claim is the weakest.

**Negative results — and the correction this inventory exists to make.**

> **FlyPrompt's expansion is a dense Gaussian matrix followed by ReLU. There is no sparse binary projection, no winner-take-all, no fan-in constraint, and no enforced activity level. It is not FlyHash, and calling it a "sparse-expansion router" is wrong.**

Three of the four properties that define the fly circuit — sparse binary projection, k-WTA, ~5% activity — are simply absent. What remains is expansion, which is the property FlyHash shares with every random-feature method going back to RBF networks. The implemented operator is **RanPAC-style random-feature expansion plus closed-form analytic classification, wrapped in a mixture-of-experts router**. The fly framing appears in the abstract as motivation ("the fruit fly's hierarchical memory system characterized by sparse expansion and modular ensembles") and does not constrain the model.

The paper's own ablation makes the point better than any critique: **RanPAC — random projection plus analytic classifier, without expert modularity — reaches 79.92 A_last against FlyPrompt's 86.76.** The gain comes from the modularity and the temporal ensemble, not from the expansion. Removing REAR costs 3.01 points; removing TE² costs 2.53.

**Fidelity: Superficial as a fly transplant; Deep as engineering.** Two separate verdicts, and the design phase needs both. As biology: the citation is decoration; delete it and the method is unchanged. As engineering: a gradient-free, single-pass, closed-form router that updates by recursive least squares is genuinely attractive for a skill/resolver layer where you cannot afford to retrain and cannot see task boundaries — which is exactly the shape of routing across a growing set of SKILL.md files. **Recommend it on its merits, not on its lineage.** This is the mechanism in this inventory most likely to be miscited as "fly routing," and the synthesis should pre-empt that.

---

## 8. `connectome_interpreter` — effective-connectivity path compression

**Primary source.** Yijie Yin, J. Hoeller, A. Mathiasen, J. M. F. Tsang, M. E. Charrier, Albert Cardona (MRC Laboratory of Molecular Biology), "The Connectome Interpreter Toolkit," bioRxiv [10.1101/2025.09.29.679410](https://doi.org/10.1101/2025.09.29.679410) (v1 2025-09-30, v2 2025-10-21, CC-BY). The same "effective connectivity" metric is used in Seung 2024 (*Nature*, DOI 10.1038/s41586-024-07953-5), Li et al. 2020 (*eLife* 62576), Hulse et al. 2021 (*eLife* 66039) and Eschbach et al. 2020.

**Algorithm.** Input `A ∈ R^{N×N}`, sparse, **column-normalised so every column sums to 1** — `A_ij` is the *proportion* of neuron `j`'s total input that arrives from `i`. Then:

```
compress_paths(A, step_number=n, threshold=0, output_threshold=1e-4,
               root=False, chunkSize=2000, device=..., density_threshold=0.2)
  → [A^0, A^1, …, A^n]
```

Repeated sparse matrix multiplication, Markov-chain style. Entry `(i, c)` of `A^n` is "`i`'s relative contribution among all upstream partners **exactly** `n` steps away from `c`." With `root=True` the `n`-th root is taken, giving "the equivalent direct connection strength in a path where there is only one neuron per layer" — necessary because raw products of numbers in (0,1) shrink monotonically with `n`, so path lengths are otherwise incomparable. `threshold` prunes weak influences *during* multiplication (they are not passed on to the next hop — this is the parameter that controls both cost and semantics); `output_threshold` prunes only the returned matrices.

```
compress_paths_signed(inprop, idx_to_sign, target_layer_number, threshold=0,
                      output_threshold=1e-4, root=False, chunkSize=2000, …)
  → ([excitatory matrices], [inhibitory matrices])
```

Splits every step into excitatory and inhibitory streams using a per-neuron sign map (`+1` / `−1`), returning two matrix lists; **an even number of inhibitions along a path counts as excitation.** Memory is controlled by chunking: the last matrix is split into column chunks of `chunkSize` and each chunk densified — the docstring gives the arithmetic, `2000 × 160,000 × float32 / 8 = 1.28 GB` per copy, and it needs two copies (one excitation, one inhibition) plus the sparse `N×N` representations. Companion functions: `find_paths_of_length`, `el_within_n_steps`, `group_paths`, `filter_paths`, `plot_paths` for extracting and rendering the actual subcircuit; `MultilayeredNetwork`, a differentiable firing-rate model with per-cell-type slopes, biases, time constants and divisive normalisation; `get_gradients` / activation maximisation / `train_model` for gradient methods.

**Parameters:** `n` (hops), `threshold`, `output_threshold`, `root`, `chunkSize`, `density_threshold`, `output_dtype`, and the sign map.

**Transplant.** Model the company brain as a typed, signed document graph (`supports` / `contradicts` / `supersedes` / `cites`), column-normalise so each node's incoming edge weights are proportions of its total support, and you get multi-hop influence scoring, signed netting (which composes naturally with mechanism 6), and subgraph extraction from MIT-licensed code already benchmarked at **~140,000 nodes on a laptop or in Colab**. Mathematically this is a personalised-PageRank / multi-hop-expansion cousin of HippoRAG-family retrieval.

**Best open implementation.** [`YijieYin/connectome_interpreter`](https://github.com/YijieYin/connectome_interpreter) — **MIT, 35★, actively maintained (pushed 2026-08-27), `pip install connectome-interpreter`, currently v2.9.5**, ReadTheDocs, three Colab tutorial notebooks, CI. Notebooks load FlyWire, BANC, MaleCNS, hemibrain and MANC by changing one variable. This is the most concretely portable code in the entire fly survey.

**Negative results and caveats.**
- The documentation itself warns that **column sums fall below 1 wherever sensory neurons have no upstream partners**, which truncates path extension — the analogue in a document graph is any root document with no citations, i.e. most of them. This needs handling before the operator means anything.
- Raw (non-rooted) values shrink monotonically with `n`; cross-path-length comparison requires `root=True`.
- Pospisil et al., *Nature* 634:201–209, DOI [10.1038/s41586-024-07982-0](https://doi.org/10.1038/s41586-024-07982-0), make the complementary point that **structure alone under-determines causal influence** — the whole "effectome" argument. Multi-hop reachability is not multi-hop entailment.
- Nothing in the package knows anything about text, semantics, or provenance.
- Broader caution against reading topology as function: Dhiman, "Topological Sensitivity in Connectome-Constrained Neural Networks" ([arXiv:2604.04033](https://arxiv.org/abs/2604.04033), 2026-04-05), re-ran flyvis (45,669 nodes, 1,513,231 edges) against a naive random null *and a degree-preserving null*: the loss advantage vanished under shared random initialisation and the activity advantage vanished under the degree-preserving null. "Previously reported topology advantages … can arise from initialization and null-model confounds."

**Fidelity: Superficial as biology; Deep as code reuse.** The operator is `A^n` on a column-normalised sparse matrix — a general graph method, not a fly-specific idea; nothing about a fly is required to derive it. What the fly world actually contributes is a **hardened, laptop-scale, signed, chunked, MIT-licensed implementation validated at exactly the node count a large company brain would have**. That is worth a great deal and it should be described honestly: good engineering borrowed from neuroscience, not a neural mechanism.

---

## 9. Spi-Fly — few-shot, continual learning for spiking neuromorphic olfaction

**Primary source.** Max & Shen, "Few-shot, continual learning for spiking neuromorphic olfaction," *Neuromorphic Computing and Engineering*, published 24 Aug 2026. DOI [10.1088/2634-4386/ae9177](https://doi.org/10.1088/2634-4386/ae9177). OIST press release: <https://www.oist.jp/news-center/news/2026/8/24/how-decipher-smells-fruit-fly>.

**Algorithm.** A three-layer spiking network, `[d — 1000 — L]`. LIF input neurons spike-encode analog sensor channels. A **fixed sparse random PN→KC projection** (~20% connection probability) expands to 1,000 hidden units — roughly a **10× expansion** — and a **winner-take-all** leaves **~5% of hidden units active**, matching the fly's Kenyon-cell sparsity. **Only the hidden→output weights learn**, by a *local supervised Hebbian rule* on presynaptic spike counts and the target label; a normalised variant divides spike counts by their L2 norm, giving robustness across stimulus magnitudes. Class = the highest-firing output neuron. Configurations: `[72 — 1000 — 10]` for the Vergara gas-sensor dataset (20 recordings each of 10 chemical compounds, 72 sensors) and `[5 — 1000 — 18]` for a synthetic *Drosophila* dataset (18 odour classes from 5 olfactory receptors, modelled on fly electrophysiology). **Inputs:** analog sensor time series. **Outputs:** output-neuron spike counts → class. **Parameters:** hidden size, PN→KC connection probability (~0.2), WTA fraction (~0.05), LIF constants, learning rate, and weight precision.

**Reported results.** Gas sensor: **88.8% after 1 epoch (3 presentations per odour)** vs BPTT-with-surrogate-gradients at 56.3%. Synthetic: 58.9% vs 49.5%. Spi-Fly reaches peak performance within ~3 presentations; BPTT needs ~70. Class-incremental (binary discrimination tasks, tested on all previous classes): Spi-Fly holds **~88%** across incremental tasks on the gas dataset while **BPTT collapses to near chance**, and **EWC + BPTT shows "no significant improvement" over vanilla BPTT**. Baselines also include the EPL network (Imam & Cleland), SVM and Gaussian Naive Bayes.

**Best open implementation.** The paper states data and simulation code are openly available at Zenodo, DOI [10.5281/zenodo.18786636](https://doi.org/10.5281/zenodo.18786636). **I could not resolve this DOI at check time — Zenodo returned HTTP 504 on both the DOI redirect and the API record.** Treat availability as *claimed but unverified*; re-check before depending on it. The closest verified relative is Shen, Dasgupta & Navlakha, [arXiv:2107.07617](https://arxiv.org/abs/2107.07617), "Algorithmic insights on continual learning from fruit flies" — sparse coding plus **synaptic freezing** (modify only the synapses of currently-active KCs) as a lightweight anti-catastrophic-forgetting mechanism, and arguably the more directly useful idea of the two.

**Negative results — the authors' own, and they are extensive.**
- **With more training, BPTT overtakes it**: 83.9% (BPTT) vs 58.9% (Spi-Fly) on the synthetic set after 10 epochs. Spi-Fly's advantage is specifically the few-shot regime.
- **No input→hidden learning at all** — the expansion is fixed random wiring forever, which is FlyHash's known weakness (see BioHash / SoftHash under mechanism 1).
- Requires labelled data; cannot exploit unsupervised data.
- Tested on **single odours only, not mixtures**.
- Does not exploit spike timing.
- Degrades at 4-bit precision (though still competitive).
- The prior report also records the authors conceding that overall performance "compared to the best traditional machine learning classification methods could be improved."

**Fidelity: Deep as biology; weak as a company-brain transplant.** It is a faithful mushroom-body model — expansion, k-WTA at fly-realistic sparsity, local associative learning confined to the output layer — and it is genuine, current evidence that **the motif is a few-shot, non-catastrophically-forgetting learner**, which is the property a company brain most wants. But its input is a ≤72-channel sensor vector and its output is one of ≤18 class labels. Nothing in it touches documents, retrieval, provenance, or contradiction. Its value to the design phase is as an **existence proof for the learning rule** and as the strongest available argument that the sparse-expansion motif buys continual learning — not as a component to drop in.

---

## 10. Kanerva sparse distributed memory as attention

**Primary sources.** Trenton Bricken & Cengiz Pehlevan, "Attention Approximates Sparse Distributed Memory," NeurIPS 2021, [arXiv:2111.05498](https://arxiv.org/abs/2111.05498). Follow-up: Trenton Bricken, Xander Davies, Deepak Singh, Dmitry Krotov, Gabriel Kreiman, "Sparse Distributed Memory is a Continual Learner," ICLR 2023, [arXiv:2303.11934](https://arxiv.org/abs/2303.11934). Origin: Pentti Kanerva, *Sparse Distributed Memory*, MIT Press, 1988.

**Algorithm.** SDM stores a pattern by writing it into **every** hardware address whose Hamming distance from the pattern's address is `≤ r` — a vanishing fraction of an enormous address space. Reading queries all addresses within `r` of the query address and **averages their contents**, so recall is a distance-weighted average over neighbours rather than an exact lookup. Bricken & Pehlevan show that, under a binomial approximation to the number of addresses at each Hamming distance, the SDM read weight is an **exponential function of distance** — which is softmax with a particular inverse temperature. Hence `Attention(Q, K, V) ≈ SDM read`, with `β ↔ r` an explicit correspondence, and they verify the required conditions (query/key norms, effective β) hold in pretrained GPT-2. **Inputs:** a query address. **Outputs:** a distance-weighted average of stored contents. **Parameters:** address-space dimension, Hamming radius `r` (equivalently attention `β`), number of hard locations, and memory load.

**What it buys a company brain.** Mostly a *re-description*: a top-k retriever with softmax-weighted fusion **already is** an SDM read, so "add SDM to your RAG" is close to vacuous. The one non-vacuous consequence is the explicit `r ↔ β` correspondence: **choosing a retrieval temperature is choosing a neighbourhood radius**, and Kanerva's theory gives a closed form for the radius that maximises signal-to-noise at a given memory load. That turns a hyperparameter you currently tune into one you can compute from your corpus size.

The **ICLR 2023 result is the more actionable one**: an MLP modified with **Top-K activation, L2 normalisation, and positive weight constraints** becomes a strong continual learner **with no memory replay, no task information, and no task boundaries** — and the authors report that *every* component translated from biology is necessary for the effect. That is a three-line recipe with an ablation behind it.

**Best open implementations.**
- [`TrentBrick/attention-approximates-sdm`](https://github.com/TrentBrick/attention-approximates-sdm) — MIT, 27★, last push 2021-11-14 (dormant).
- [`TrentBrick/SDMContinualLearner`](https://github.com/TrentBrick/SDMContinualLearner) — 22★, last push 2023-03-01 (dormant), **no LICENSE file** — same legal caveat as mechanism 2's ffbf.

**Negative results and limits.**
- This project's own `neuro-inspired-rag.md` classifies SDM as **"theory, not systems" — not ready as an actual storage substrate.** I concur.
- The 2021 result is an **approximation under stated conditions**, not an identity; the conditions were verified in GPT-2, not in a retrieval stack.
- Both repos are dormant and one is unlicensed.
- **For question (b) specifically, this mechanism cuts against the fly framing rather than for it.** SDM's sparse high-dimensional expansion is the *same computational motif* as FlyHash and the mushroom body (as Ryali et al. note explicitly), arrived at independently by Kanerva in 1988 from vertebrate-cerebellum reasoning. That strengthens the general claim ("sparse expansive codes are a good idea") and **weakens the specifically-fly claim** ("you need the fly work for this"). The synthesis should say so.

**Fidelity: Deep as theory; Superficial as a transplant.** It explains why the retrieval you already have works, rather than giving you something new to build. The buildable residue is exactly three things — Top-K activation, L2 normalisation, positive weight constraints — as a continual-learning recipe with a published ablation.

---

## What has no counterpart, and must be said

Two of Tan's five brain-hygiene requirements have **no mechanism in this inventory at all**, and no amount of design work will produce one from fly biology:

- **Provenance on every fact.** The mushroom body discards the episode and keeps a scalar synaptic weight. It is a valence tagger, not a document store. There is no fly mechanism for "who said this, when, and on what authority." Anyone offering fly-brain provenance is confabulating. (Ironically, the *connectome projects* have superb provenance — CAVE versioning, per-fact confidence thresholds, `source.lock.json`, dataset checksums — but that is a **process** answer from the neuroscience community's data practices, not an **algorithm** from the fly's brain. Do not blur the two.)
- **Skillification / procedural memory / resolver tables / org chart.** No counterpart. The fly has no notion of a reusable procedure stored as an artefact. Mechanism 7 is the nearest thing (routing among experts) and its fly content is decoration.

A third, **relevance to a query**, is absent from every memory mechanism here. The fly's promotion, forgetting and arbitration all operate on recency, valence and interference. None of them knows what a question is. Every one of mechanisms 3–6 has to have a relevance term bolted on, and that term is not derived from any biology.

## Cross-cutting caveat for the design phase

**Nobody has published the MB→agent-memory mapping.** Two prior reports independently searched arXiv, the 2026 agent-memory survey literature, and the bio-inspired memory papers (ZenBrain, FSFM, BMAM, FadeMem) and found that all of them borrow *hippocampal* metaphors and none cites the mushroom body. The ground is genuinely unclaimed. But "unclaimed" and "promising" are different claims, and the single empirical attempt to run MB plasticity on a real task (doomfly's 4,184 KC→MBON11 dopamine-gated synapses) **shipped a negative result**. The inventory above is a menu of hypotheses with published mechanisms, not a menu of validated components. Only mechanism 2 can be built exactly as published, and even it has never been run on text.

---

## Sources

**Fly-brain primary literature**
- Dasgupta S., Stevens C.F., Navlakha S. (2017) "A neural algorithm for a fundamental computing problem." *Science* 358(6364):793–796 — https://doi.org/10.1126/science.aam9868 · PDF https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf
- Dasgupta S., Sheehan T.C., Stevens C.F., Navlakha S. (2018) "A neural data structure for novelty detection." *PNAS* 115(51):13093–13098 — https://doi.org/10.1073/pnas.1814448115 · open PDF (read for this report) https://repository.cshl.edu/id/eprint/38636/1/Navlakha_2018_PNAS.pdf
- Hattori D. et al. (2017) *Cell* 169:956–969 — https://doi.org/10.1016/j.cell.2017.04.028
- Huang C., Luo J., Woo S.J., Roitman L.A., Li J., Pieribone V.A., Kannan M., Vasan G., Schnitzer M.J. (2024) "Dopamine-mediated interactions between short- and long-term memory dynamics." *Nature* 634:1141–1149 — https://doi.org/10.1038/s41586-024-07819-w · open access https://pmc.ncbi.nlm.nih.gov/articles/PMC11525173/
- Gkanias E., McCurdy L.Y., Nitabach M.N., Webb B. (2022) "An incentive circuit for memory dynamics in the mushroom body of *Drosophila melanogaster*." *eLife* 11:e75611 — https://doi.org/10.7554/eLife.75611
- Shuai Y., Lu B., Hu Y., Wang L., Sun K., Zhong Y. (2010) "Forgetting is regulated through Rac activity in *Drosophila*." *Cell* 140:579–589 — https://doi.org/10.1016/j.cell.2009.12.044
- Berry J.A., Cervantes-Sandoval I., Nicholas E.P., Davis R.L. (2012) "Dopamine is required for learning and forgetting in *Drosophila*." *Neuron* 74:530–542 — https://doi.org/10.1016/j.neuron.2012.04.007 · https://pmc.ncbi.nlm.nih.gov/articles/PMC4083655/
- Cervantes-Sandoval I., Chakraborty M., MacMullen C., Davis R.L. (2016) "Scribble scaffolds a signalosome for active forgetting." *Neuron* 90:1230–1242 — https://doi.org/10.1016/j.neuron.2016.05.010 · https://pmc.ncbi.nlm.nih.gov/articles/PMC4926877/
- Berry J.A., Cervantes-Sandoval I., Chakraborty M., Davis R.L. (2015) "Sleep facilitates memory by blocking dopamine neuron-mediated forgetting." *Cell* 161:1656–1667 — https://doi.org/10.1016/j.cell.2015.05.027 · https://pmc.ncbi.nlm.nih.gov/articles/PMC4671826/
- Felsenberg J. et al. (2018) "Integration of Parallel Opposing Memories Underlies Memory Extinction." *Cell* 175:709–722 — https://doi.org/10.1016/j.cell.2018.08.021 · open access https://pmc.ncbi.nlm.nih.gov/articles/PMC6198041/
- Aso Y., Rubin G.M. (2016) "Dopaminergic neurons write and update memories with cell-type-specific rules." *eLife* 5:e16135 — https://doi.org/10.7554/eLife.16135
- Aso Y. et al. (2014) *eLife* 3:e04577 — https://doi.org/10.7554/eLife.04577
- Litwin-Kumar A., Harris K.D., Axel R., Sompolinsky H., Abbott L.F. (2017) *Neuron* 93:1153–1164 — https://doi.org/10.1016/j.neuron.2017.01.030
- Lin A.C., Bygrave A.M., de Calignon A., Lee T., Miesenböck G. (2014) *Nat. Neurosci.* 17:559–568 — https://doi.org/10.1038/nn.3660
- Bennett J.E.M., Philippides A., Nowotny T. (2021) *Nat. Commun.* 12:2569 — https://doi.org/10.1038/s41467-021-22592-4 · code https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb
- Jiang L., Litwin-Kumar A. (2021) *PLoS Comput. Biol.* 17(8):e1009205 — https://doi.org/10.1371/journal.pcbi.1009205
- Springer M., Nawrot M.P. (2021) *eNeuro* 8(3):ENEURO.0549-20.2021 — https://doi.org/10.1523/ENEURO.0549-20.2021
- Eschbach C. et al. (2020) *Nat. Neurosci.* — https://doi.org/10.1038/s41593-020-0607-9
- Xie K., Ocker G.K. (2025) "The Impact of Structural Changes on Learning Capacity in the Fly Olfactory Neural Circuit." arXiv:2509.19351 — https://arxiv.org/abs/2509.19351
- False/silent-memory reinstatement — https://pmc.ncbi.nlm.nih.gov/articles/PMC13533848/

**Algorithms and benchmarks**
- Ryali C., Hopfield J., Grinberg L., Krotov D. (2020) "Bio-Inspired Hashing for Unsupervised Similarity Search." ICML 2020, arXiv:2001.04907 — https://arxiv.org/abs/2001.04907
- Sinha & Ram, Fly Bloom Filter Classifier, KDD 2021 — https://arxiv.org/abs/2008.08685 · https://dl.acm.org/doi/10.1145/3447548.3467246
- Shen Y., Dasgupta S., Navlakha S. (2021) arXiv:2107.07617 — https://arxiv.org/abs/2107.07617
- Kleyko D., Rachkovskij D. (2024) arXiv:2501.14741 — https://arxiv.org/html/2501.14741
- Li et al., BioVSS, ICDE 2025, arXiv:2412.03301 — https://arxiv.org/html/2412.03301
- Mao Q. et al. (2026) H3D, arXiv:2607.08382 — https://arxiv.org/abs/2607.08382
- Yan H., Sun G., Zhou K., Li Q., Wang L., Zhong Y. (2026) "FlyPrompt," ICLR 2026, arXiv:2602.01976 — https://arxiv.org/abs/2602.01976
- Max & Shen (2026) "Few-shot, continual learning for spiking neuromorphic olfaction," *Neuromorph. Comput. Eng.* — https://doi.org/10.1088/2634-4386/ae9177 · data/code claimed at https://doi.org/10.5281/zenodo.18786636 (unresolvable at check time, HTTP 504) · https://www.oist.jp/news-center/news/2026/8/24/how-decipher-smells-fruit-fly
- Bricken T., Pehlevan C. (2021) "Attention Approximates Sparse Distributed Memory," NeurIPS 2021, arXiv:2111.05498 — https://arxiv.org/abs/2111.05498
- Bricken T., Davies X., Singh D., Krotov D., Kreiman G. (2023) "Sparse Distributed Memory is a Continual Learner," ICLR 2023, arXiv:2303.11934 — https://arxiv.org/abs/2303.11934
- Yin Y., Hoeller J., Mathiasen A., Tsang J.M.F., Charrier M.E., Cardona A. (2025) "The Connectome Interpreter Toolkit," bioRxiv — https://doi.org/10.1101/2025.09.29.679410
- Pospisil D. et al. (2024) *Nature* 634:201–209 — https://doi.org/10.1038/s41586-024-07982-0
- Dhiman (2026) "Topological Sensitivity in Connectome-Constrained Neural Networks," arXiv:2604.04033 — https://arxiv.org/abs/2604.04033
- SAGE novelty gate, arXiv:2605.30711 — https://arxiv.org/pdf/2605.30711 · https://github.com/swang1024/SAGE
- FadeMem arXiv:2601.18642 — https://arxiv.org/abs/2601.18642 · FSFM arXiv:2604.20300 — https://arxiv.org/abs/2604.20300 · ZenBrain arXiv:2604.23878 — https://arxiv.org/abs/2604.23878

**Repositories inspected via `gh api` / raw.githubusercontent.com on 2026-09-10**
| Repo | License | ★ | Last push |
|---|---|---|---|
| https://github.com/TeddyHuang-00/FlyHash | MIT | 2 | 2026-07-20 |
| https://github.com/dataplayer12/Fly-LSH | MIT | 89 | 2018-12-23 |
| https://github.com/rithram/fbfc | MIT | 2 | 2022-02-18 |
| https://github.com/clembarr/ffbf-novelty-detector | **none** | 0 | 2026-09-08 |
| https://github.com/InsectRobotics/IncentiveCircuit | GPL-3.0 | 1 | 2023-12-02 |
| https://github.com/BrainsOnBoard/paper_RPEs_in_drosophila_mb | — | 5 | — |
| https://github.com/AnAppleCore/FlyGCL | MIT | 18 | 2026-09-04 |
| https://github.com/YijieYin/connectome_interpreter | MIT | 35 | 2026-08-27 |
| https://github.com/TrentBrick/attention-approximates-sdm | MIT | 27 | 2021-11-14 |
| https://github.com/TrentBrick/SDMContinualLearner | **none** | 22 | 2023-03-01 |
| https://github.com/bhoov/flyvec | Apache-2.0 | 40 | 2021-12-10 |
| https://github.com/swang1024/SAGE | Apache-2.0 | 7 | 2026-09-04 |

**Internal**
- /Users/stephen/Cookies/company-brain-research/checkpoints/01-sweep-decisions.md
- /Users/stephen/Cookies/company-brain-research/findings/flyhash-sparse-retrieval.md
- /Users/stephen/Cookies/company-brain-research/findings/mushroom-body-memory-models.md
- /Users/stephen/Cookies/company-brain-research/findings/flywire-connectome-simulation.md
- /Users/stephen/Cookies/company-brain-research/findings/v10a-h3d-flyhash.md
- /Users/stephen/Cookies/company-brain-research/findings/neuro-inspired-rag.md
- /Users/stephen/Cookies/company-brain-research/findings/completeness-critic.md

# Mushroom-body memory models and what they actually offer a "company brain"

Dimension key: `mushroom-body-memory-models`
Author: research worker (Claude Opus 5) · Date: 2026-09-10

## TL;DR

1. The *Drosophila* mushroom body (MB) is the best-characterised associative-memory circuit in biology: ~2,000 Kenyon cells (KCs) per hemisphere, 15 anatomical compartments, 21 MBON types and 20 DAN types, wired so that dopamine neurons converge on compartmentalised KC→MBON synapses ([Aso et al. 2014, eLife 3:e04577](https://doi.org/10.7554/eLife.04577)).
2. Four of Garry Tan's five "brain hygiene" requirements have real MB counterparts: **hot vs cold memory** (γ-compartment STM decaying in ~30 min vs α2/α3 LTM lasting >24 h — [Huang et al. 2024, *Nature* 634:1141–1149](https://doi.org/10.1038/s41586-024-07819-w)); **active pruning** (dopamine-gated forgetting via the DAMB receptor → Scribble → Rac1 → cofilin pathway); **contradiction arbitration** (extinction as *parallel opposing memories* summed at the MBON — [Felsenberg et al. 2018, *Cell* 175:709–722](https://doi.org/10.1016/j.cell.2018.08.021)); **novelty detection** (the α′3 compartment, [Hattori et al. 2017, *Cell* 169:956–969](https://doi.org/10.1016/j.cell.2017.04.028)).
3. The fifth — **provenance on every fact** — has *no* MB counterpart, and this is the honest limit of the analogy. The MB throws the episode away and keeps a scalar synaptic weight; it is a valence tagger, not a document store. Anyone selling "fly-brain provenance" is confabulating.
4. Fly circuitry has already produced *working* AI primitives at the index layer: FlyHash LSH ([Dasgupta, Stevens & Navlakha 2017, *Science* 358:793](https://doi.org/10.1126/science.aam9868)), a fly Bloom filter for novelty ([Dasgupta et al. 2018, *PNAS* 115:13093](https://doi.org/10.1073/pnas.1814448115)), BioHash, fly word embeddings, and continual learning ([arXiv:2107.07617](https://arxiv.org/abs/2107.07617)). The newest is **FlyPrompt** (ICLR 2026, [arXiv:2602.01976](https://arxiv.org/abs/2602.01976)) from Yi Zhong's *Drosophila*-memory lab at Tsinghua — sparse random expansion as an expert router, +11.23% on CIFAR-100.
5. **Nobody has yet connected MB circuit motifs to RAG / agent-memory architecture in print.** I searched arXiv (full API sweep on "mushroom body", "Kenyon cells", "FlyHash", "sparse distributed memory"), Google, and the 2026 agent-memory survey literature: the 2026 bio-inspired agent-memory papers (ZenBrain, FSFM, BMAM) all borrow *hippocampal* metaphors. The MB→company-brain mapping is an open, unclaimed niche.

---

## 1. The canonical circuit and its numbers

The MB is a three-stage feedforward expansion with a modulatory teaching layer:

- **~50 olfactory receptor classes → ~150 projection neurons (PNs) → ~2,000 KCs per hemisphere.** Each KC samples ~5–7 PNs via "claws." [Litwin-Kumar, Harris, Axel, Sompolinsky & Abbott, *Neuron* 93:1153–1164 (2017)](https://doi.org/10.1016/j.neuron.2017.01.030) showed analytically that representational dimensionality is *maximised* at exactly the observed claw number; a KC with 20 claws would sample ~40% of glomeruli and blur odour identities. Sparse fan-in is optimal, not merely cheap.
- **Sparsening is enforced, not incidental.** The GABAergic APL neuron forms a KC↔APL negative-feedback loop; ablating it destroys sparseness and specifically impairs discrimination of *similar* odours ([Lin, Bygrave, de Calignon, Lee & Miesenböck 2014, *Nat. Neurosci.* 17:559–568](https://doi.org/10.1038/nn.3660)). Typical odours drive ~5–10% of KCs.
- **15 compartments** tile the KC axon bundle. Each compartment = one (or a few) MBON dendritic field + one DAN axon field. Learning is local: a DAN firing in compartment *c* depresses the KC→MBON synapses of the KCs that were just active, *only in c* ([Aso et al. 2014](https://doi.org/10.7554/eLife.04577); reviewed in [Modi, Shuai & Turner 2020, *Annu. Rev. Neurosci.* 43:465–484](https://doi.org/10.1146/annurev-neuro-080317-062333)).
- Connectivity is *not* uniformly random. [MacKenzie et al. 2025 (bioRxiv 10.1101/2025.10.29.684686)](https://www.biorxiv.org/content/10.1101/2025.10.29.684686v2) find some PN types connect up to **15-fold** more often than others, producing a *learning hierarchy*: odours activating >20% of KCs form robust memories, those activating <10% learn poorly. [Dorrell & Latham 2026 (arXiv:2601.09320)](https://arxiv.org/abs/2601.09320) give the kernel-regression theory for why: functions depending on oversampled inputs are easier to learn. Translation: **your index's connectivity bias silently decides what your brain can learn at all.**

## 2. Hot vs cold memory: the strongest mapping

[Huang et al. 2024, *Nature* 634:1141–1149](https://doi.org/10.1038/s41586-024-07819-w) (Schnitzer lab, Stanford) is the single most relevant paper to Tan's "promoted to hot memory versus filed as cold reference" line (transcript 13:15).

- The **γ compartments are the short-term unit** (~30 min decay); **α2/α3 are the long-term units** (~100 min initial decay, then far slower; MBON-α3 depression persists >24 h, MBON-γ1pedc>α/β depression <1 h).
- The promotion mechanism is *gated by the hot store's own state*: learning depresses MBON-γ1pedc>α/β, which **releases inhibitory feedback** onto PPL1-α′2α2 and PPL1-α3. Only then do those DANs encode combined innate + learnt valence and license LTM writing.
- Five PPL1 DAN types and six MBON types form the STM/LTM chain.

That is a real architectural pattern an engineer can copy: **consolidation is not a cron job; it is triggered by the hot tier's readout crossing a threshold.** Tan's brain does the opposite today (agents write, a librarian later prunes). A γ→α design would let the *retrieval signal itself* decide promotion.

[Gkanias, McCurdy, Nitabach & Webb 2022, *eLife* 11:e75611](https://doi.org/10.7554/eLife.75611) formalise this in a 12-neuron "incentive circuit": 6 MBONs typed **susceptible / restrained / long-term-memory** and 6 DANs typed **discharging / charging / forgetting**, per valence. The model reproduces acquisition, forgetting, assimilation of STM→LTM, and an exploration/exploitation trade-off. The three-tier MBON typing is almost a literal cache hierarchy (write buffer / working set / durable store), and the *named forgetting DAN* is almost literally Tan's librarian.

## 3. Active forgetting = the librarian whose job is pruning

Forgetting in the fly is **not decay; it is an actively driven process with a dedicated circuit**:

- Bidirectional modulation of a small DAN subset after conditioning sets the *rate* of forgetting for both aversive and appetitive memories ([Berry, Cervantes-Sandoval, Nicholas & Davis 2012, *Neuron*, PMID 22578504](https://pubmed.ncbi.nlm.nih.gov/22578504/)).
- Acquisition and forgetting use **different receptors on the same synapse**: dDA1 for learning, DAMB for forgetting, downstream through Scribble → Rac1 → cofilin actin remodelling ([Frontiers Cell. Neurosci. 14:258, 2020](https://doi.org/10.3389/fncel.2020.00258)); Rac1 inhibition blocks forgetting-induced restoration of MBON odour responses.
- **Sleep gates it.** [Berry, Cervantes-Sandoval, Chakraborty & Davis 2015, *Cell* 161:1656–1667](https://doi.org/10.1016/j.cell.2015.05.027): sleep facilitates memory *by blocking* dopamine-neuron-mediated forgetting. The fly does not consolidate during sleep so much as *stop deleting*.

Engineering read: forgetting should be a **first-class, separately-parameterised, schedulable subsystem with its own trigger signal**, not a TTL. And there should be a "quiet window" during which pruning is suppressed. No agent-memory system I found in 2026 implements a suppressible pruning daemon this way — the closest are [FSFM (arXiv:2604.20300)](https://arxiv.org/abs/2604.20300), which taxonomises passive-decay / active-deletion / safety-triggered / adaptive-reinforcement forgetting from *hippocampal* and Ebbinghaus premises, and ZenBrain's sleep-phase consolidation loop ([arXiv:2604.23878](https://arxiv.org/abs/2604.23878)). Neither cites the MB.

## 4. Contradiction arbitration: extinction as opposing parallel traces

Tan: "who arbitrates when two facts disagree" (13:17). The fly's answer is *it does not arbitrate — it accumulates both and nets them at readout*. [Felsenberg et al. 2018, *Cell* 175:709–722](https://doi.org/10.1016/j.cell.2018.08.021): extinguishing an aversive memory requires *reward* DANs (omission of punishment is remembered as positive); the original aversive trace and the new appetitive extinction trace coexist in different MBON compartments and are integrated downstream. Flies "track the accuracy of learned expectations by accumulating and integrating memories of conflicting events."

Models of this: [Springer & Nawrot 2021, *eNeuro* 8(3):ENEURO.0549-20.2021](https://doi.org/10.1523/ENEURO.0549-20.2021) (mutually inhibiting appetitive/aversive pathways); [Bennett, Philippides & Nowotny 2021, *Nat. Commun.* 12:2569](https://doi.org/10.1038/s41467-021-22592-4) (DANs signal *reinforcement prediction error* using MBON feedback, not absolute reinforcement); [Jiang & Litwin-Kumar 2021, *PLoS Comput. Biol.* 17(8):e1009205](https://doi.org/10.1371/journal.pcbi.1009205) (RPE emerges as a *population mode* across heterogeneous DANs); [Eschbach et al. 2020, *Nat. Neurosci.*](https://doi.org/10.1038/s41593-020-0607-9) (recurrent DAN↔MBON architecture for adaptive regulation of learning).

This is a genuinely different design from "LLM judges which fact wins": keep both claims with signed evidence, let the *reader* net them, and let a prediction-error signal decide whether to write at all. It is deep as an algorithm — but note it produces a *net valence*, not a resolved proposition. A company brain needs to know which fact is true, not just which feels good.

## 5. Novelty detection is the most directly transplantable piece

[Hattori et al. 2017, *Cell* 169:956–969](https://doi.org/10.1016/j.cell.2017.04.028) (Axel/Abbott/Rubin): novel odours drive strong α′3 MBON activity that is rapidly suppressed on repetition, requiring the compartment's own DAN; α′3 MBON activation alone evokes an alerting response. [Dasgupta, Sheehan, Stevens & Navlakha 2018, *PNAS* 115:13093](https://doi.org/10.1073/pnas.1814448115) turned this into a **Bloom filter with continuous, time-decaying novelty scores** — it reports *how* novel an item is relative to what has been seen and how long ago, which a classic Bloom filter cannot. That is exactly the "should this be written down at all?" gate a 220,000-page agent-written brain needs at ingest.

## Relevance to company-brain / RAG / fruit-fly question

**Does it relate to RAG?** Only at the index primitive, and Tan's whole point is that the primitive is the easy part. FlyHash ([*Science* 358:793, 2017](https://doi.org/10.1126/science.aam9868)) *is* an LSH scheme — sparse binary expansion from random PN→KC projections, winner-take-all top-k — and it is a legitimate alternative to dense-embedding ANN. It shows up in 2026 retrieval work: [H3D (arXiv:2607.08382, July 2026)](https://arxiv.org/abs/2607.08382) benchmarks FlyHash against MinHash/SimHash/Winnowing/FuzzyHash for fine-grained document dedup on CSFCube and RELISH, finding lexical/structural fingerprints competitive for near-duplicates but weaker under rewriting. Dedup is a curation task, so this is directly usable brain hygiene. Learned variants: BioHash ([arXiv:2001.04907](https://arxiv.org/abs/2001.04907), ICML 2020) and fly word embeddings ([arXiv:2101.06887](https://arxiv.org/abs/2101.06887), ICLR 2021).

**Can it be combined with the fruit-fly work?** Yes, but the honest mapping table is:

| Tan requirement (transcript) | MB mechanism | Depth |
|---|---|---|
| hot memory vs cold reference (13:15) | γ (STM, ~30 min) vs α2/α3 (LTM, >24 h), gated by MBON-γ1pedc disinhibition (Huang 2024); susceptible/restrained/LTM MBONs (Gkanias 2022) | **Deep** — a copyable trigger mechanism |
| librarian whose job is pruning (15:01) | dedicated forgetting DANs; DAMB/Scribble/Rac1; sleep-gated suppression | **Deep** — but prunes by recency/valence, never by *relevance to a query* |
| contradiction checks (14:52) | extinction as parallel opposing traces netted at MBON; DAN reinforcement-prediction-error gating writes | **Medium** — right shape, wrong currency (valence, not truth) |
| provenance on every fact (14:50) | none — the episode is discarded, a scalar weight remains | **Absent** |
| "which three books are open" (12:45) | FlyHash sparse expansion + top-k; Litwin-Kumar optimal fan-in ≈ 6 | **Medium** — solves retrieval, which Tan says is not the product |
| novelty / what's worth writing down (13:09) | α′3 familiarity signal; fly Bloom filter with decay | **Deep** — implementable today |
| skillification, resolver tables, org chart | no counterpart | **Absent** |

The load-bearing caveat: the MB stores on the order of hundreds of *scalar valence associations over sparse sensory codes*. Tan's brain stores 220,000 pages of propositional text with authorship. The two are different objects. Where the MB genuinely helps is the **metadata layer** — an ingest novelty gate, a promotion trigger, a pruning daemon, a signed-evidence contradiction ledger — not the content store.

**Which 2026 work is live?** [FlyPrompt (ICLR 2026, arXiv:2602.01976)](https://arxiv.org/abs/2602.01976) is the flagship: Yan, Sun, Zhou, Li, Wang & Zhong (Tsinghua School of Life Sciences / IDG-McGovern — i.e. an actual fly-memory lab) use "the fruit fly's hierarchical memory system characterised by sparse expansion and modular ensembles" as a randomly-expanded analytic router plus a temporal ensemble of heads, for single-pass continual learning: +11.23% CIFAR-100, +12.43% ImageNet-R, +7.62% CUB-200; code at [github.com/AnAppleCore/FlyGCL](https://github.com/AnAppleCore/FlyGCL). Also 2026: [Dorrell & Latham kernel theory (2601.09320)](https://arxiv.org/abs/2601.09320); [olfactory sparse-coding bottleneck for low-resource NER (2606.21895)](https://arxiv.org/abs/2606.21895); [insect-inspired modular RL (2604.22081)](https://arxiv.org/abs/2604.22081); [multisensory engram recruitment (2604.28007)](https://arxiv.org/abs/2604.28007); [larval-connectome frozen-rate operator with "mushroom-body modes" (2606.17745)](https://arxiv.org/abs/2606.17745). Earlier but essential: [Xie & Ocker 2025 on pruning and learning capacity (2509.19351)](https://arxiv.org/abs/2509.19351) — pruning KC→MBON synapses degrades learning in the same way ablation does, a caution about over-aggressive brain pruning.

## Open questions

1. Does GBrain (or OpenClaw/Hermes) implement anything resembling a promotion trigger or a suppressible pruning daemon, or is hot/cold just a manual tag? Not resolvable from the talk.
2. Is there an unpublished/industrial system using FlyHash-style sparse binary codes as a *first-stage* filter over a 10⁵–10⁶-document corpus with dense reranking? H3D suggests dedup, not retrieval.
3. Huang et al. 2024's promotion gate is disinhibition of a *specific* DAN by a *specific* MBON. Is there an equivalent measurable readout signal in an agent brain (retrieval frequency? downstream task success?) that could serve as the gate? Untested.
4. Which "recently published fruit fly brain work" does the user mean? My dimension surfaces three 2026 candidates: FlyPrompt (ICLR 2026), the whole-brain connectomic graph controller ([arXiv:2602.17997](https://arxiv.org/abs/2602.17997)), and the larval-connectome operator paper. None is a *memory* paper about MB per se.
5. Nobody has published the MB→agent-memory mapping. Is that because it fails on the provenance/propositional-content gap, or because the two communities have not met? I lean the former, but with low confidence.

## Sources

- Aso Y. et al. (2014) *eLife* 3:e04577 — https://doi.org/10.7554/eLife.04577
- Modi M.N., Shuai Y., Turner G.C. (2020) *Annu. Rev. Neurosci.* 43:465–484 — https://doi.org/10.1146/annurev-neuro-080317-062333
- Litwin-Kumar A. et al. (2017) *Neuron* 93:1153–1164 — https://doi.org/10.1016/j.neuron.2017.01.030
- Lin A.C. et al. (2014) *Nat. Neurosci.* 17:559–568 — https://doi.org/10.1038/nn.3660
- Hattori D. et al. (2017) *Cell* 169:956–969 — https://doi.org/10.1016/j.cell.2017.04.028
- Berry J.A. et al. (2012) *Neuron* — https://pubmed.ncbi.nlm.nih.gov/22578504/
- Berry J.A. et al. (2015) *Cell* 161:1656–1667 — https://pubmed.ncbi.nlm.nih.gov/26073942/
- Rac1 / forgetting-induced MBON plasticity (2020) *Front. Cell. Neurosci.* 14:258 — https://doi.org/10.3389/fncel.2020.00258
- Felsenberg J. et al. (2018) *Cell* 175:709–722 — https://doi.org/10.1016/j.cell.2018.08.021
- Springer M. & Nawrot M.P. (2021) *eNeuro* 8(3) — https://doi.org/10.1523/ENEURO.0549-20.2021
- Bennett J.E.M., Philippides A., Nowotny T. (2021) *Nat. Commun.* 12:2569 — https://doi.org/10.1038/s41467-021-22592-4
- Jiang L. & Litwin-Kumar A. (2021) *PLoS Comput. Biol.* 17(8):e1009205 — https://doi.org/10.1371/journal.pcbi.1009205
- Eschbach C. et al. (2020) *Nat. Neurosci.* — https://doi.org/10.1038/s41593-020-0607-9
- Gkanias E. et al. (2022) *eLife* 11:e75611 — https://doi.org/10.7554/eLife.75611
- Huang C. et al. (2024) *Nature* 634:1141–1149 — https://doi.org/10.1038/s41586-024-07819-w
- Chan I.C.W. et al. (2024) *Learn. Mem.* 31(5):a053863 — https://doi.org/10.1101/lm.053863.123
- MacKenzie A.J. et al. (2025) bioRxiv — https://www.biorxiv.org/content/10.1101/2025.10.29.684686v2
- Xie K. & Ocker G.K. (2025) arXiv:2509.19351 — https://arxiv.org/abs/2509.19351
- Dorrell W. & Latham P.E. (2026) arXiv:2601.09320 — https://arxiv.org/abs/2601.09320
- Yan H. et al. (2026) FlyPrompt, ICLR 2026, arXiv:2602.01976 — https://arxiv.org/abs/2602.01976 · code https://github.com/AnAppleCore/FlyGCL
- Mao Q. et al. (2026) H3D, arXiv:2607.08382 — https://arxiv.org/abs/2607.08382
- Deshpande B. (2026) arXiv:2606.21895 — https://arxiv.org/abs/2606.21895
- Staples A.E. (2026) arXiv:2604.22081 — https://arxiv.org/abs/2604.22081
- Gu Y. et al. (2026) FSFM, arXiv:2604.20300 — https://arxiv.org/abs/2604.20300
- Bering A. (2026) ZenBrain, arXiv:2604.23878 — https://arxiv.org/abs/2604.23878
- Dasgupta S., Stevens C.F., Navlakha S. (2017) *Science* 358:793–796 — https://doi.org/10.1126/science.aam9868
- Dasgupta S. et al. (2018) *PNAS* 115:13093 — https://doi.org/10.1073/pnas.1814448115
- Ryali C. et al. (2020) BioHash, arXiv:2001.04907 — https://arxiv.org/abs/2001.04907
- Liang Y. et al. (2021) Fly word embeddings, arXiv:2101.06887 — https://arxiv.org/abs/2101.06887
- Shen Y., Dasgupta S., Navlakha S. (2021) arXiv:2107.07617 — https://arxiv.org/abs/2107.07617
- Transcript: /Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt (quotes at 12:45, 13:09–13:25, 14:30–15:05)

# FlyWire / connectome simulation — deep dive

**Worker key:** `flywire-connectome-simulation` · **Date:** 2026-09-10 · Research folder: `/Users/stephen/Cookies/company-brain-research`

## TL;DR

1. **The "recently published fruit fly brain work" is almost certainly the male CNS connectome released 2026-09-03** (one week before this research) — Janelia FlyEM + Cambridge Connectomics + Google Research: **166,700 neurons, ~125M synaptic connections, 11,710 neuron types**, CC-BY, published as Berg et al., *Cell* 189:5504–5526 ([10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015)). It is the first complete CNS (brain + both optic lobes + ventral nerve cord) of any animal at this scale. Runner-up candidate: the BANC brain-and-cord connectome, Bates et al., *Nature* 656:957–970, 2026-06-08 ([10.1038/s41586-026-10735-w](https://doi.org/10.1038/s41586-026-10735-w)).
2. **Whole-fly-brain simulation is now genuinely cheap.** Eon Systems' open benchmark of the Shiu et al. leaky-integrate-and-fire (LIF) whole-brain model hits **7.8× real time on a single GPU** (GeNN backend) and ~1.1× real time on CPU — measured, in a public CSV, not a press claim ([benchmark-results.csv](https://github.com/eonsystemspbc/fly-brain/blob/main/data/benchmark-results.csv)).
3. **The honest verdict on "combine it with a company brain": the *architecture* transfer is weak-to-negative, the *curation process* transfer is strong.** A 2026-04 controlled study found the apparent learning advantage of connectome topology **disappears under degree-preserving null models and fair initialization** (arXiv [2604.04033](https://arxiv.org/abs/2604.04033)). Meanwhile the connectome projects are the best existing worked example of exactly what Garry Tan says the product is: provenance, versioning, typed annotation, human+AI proofreading, contradiction arbitration.
4. **The one real, citable algorithmic bridge to RAG is not the connectome at all — it is the fly *olfactory* circuit**: FlyHash (Dasgupta, Stevens & Navlakha, *Science* 2017, [10.1126/science.aam9868](https://doi.org/10.1126/science.aam9868)) and its descendants BioHash and BioVSS (**>50× faster than linear scan at 98.9% recall on million-scale sets**, arXiv [2412.03301](https://arxiv.org/abs/2412.03301)). That is a *retrieval primitive* — precisely the layer Tan says is *not* the product.
5. **Garry Tan's talk never mentions biology.** I grepped the full transcript for `fly|neuro|connectome|biolog|neuron|hippocamp`: the only hit is "every single one of you can fly" at 20:11. The fruit-fly link is the user's synthesis, not Tan's claim — worth saying plainly in the final report.

---

## 1. The data layer: what exists and is open (as of 2026-09-10)

| Dataset | Scale | Publication | Access |
|---|---|---|---|
| **FAFB / FlyWire** v783 (adult female brain) | 139,255 neurons, 5×10⁷ chemical synapses | Dorkenwald et al., *Nature* 634:124–138, 2024-10-02, [10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y) | [codex.flywire.ai](https://codex.flywire.ai), CAVEclient, `fafbseg` |
| **Cell typing / annotation** | 8k+ cell types, hemilineages, NT predictions | Schlegel et al., *Nature* 634:139–152, [10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5) | [flywire_annotations](https://github.com/flyconnectome/flywire_annotations) |
| **Network statistics** | rich club = **30% of connectome**; reciprocity **0.138**; clustering **0.0463** | Lin et al., *Nature* 634:153–165, [10.1038/s41586-024-07968-y](https://doi.org/10.1038/s41586-024-07968-y) | — |
| **Visual system parts list** | 732 optic-lobe cell types | Matsliah, Yu et al., *Nature* 634:166–180, [10.1038/s41586-024-07981-1](https://doi.org/10.1038/s41586-024-07981-1) | Codex |
| **BANC** v888 (brain + nerve cord, female) | 158,262 neurons | Bates et al., *Nature* 656:957–970, 2026-06-08, [10.1038/s41586-026-10735-w](https://doi.org/10.1038/s41586-026-10735-w) | [codex.flywire.ai/?dataset=banc](https://codex.flywire.ai/?dataset=banc) |
| **MaleCNS** v1.0 (complete male CNS) | **166,700 neurons, ~125M connections, 11,710 types** | Berg et al., *Cell* 189:5504–5526.e15, 2026-09-03, [10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015) | [male-cns.janelia.org](https://male-cns.janelia.org/), neuPrint `male-cns:v1.0`, CC-BY |
| MANC v1.2.1 / MAOL v1.1 | 23,665 / 52,445 neurons | — | Codex |

Codex currently serves **five** fly datasets side by side ([codex.flywire.ai/api/download](https://codex.flywire.ai/api/download)). The MaleCNS bulk download is Apache Arrow Feather: `connectome-weights` 1.1 GB, `syn-points` 12.7 GB, `syn-partners` 6.8 GB, plus a Neo4j 4.4.16 database dump and neuroglancer-precomputed skeletons ([download page](https://male-cns.janelia.org/download/)). Note the filenames carry an explicit confidence threshold — `minconf-0.5` — i.e. **every fact in this brain ships with a provenance/confidence tag baked into the filename**. Hold that thought for §5.

Companion 2026 *Cell* papers already using MaleCNS: Hoeller et al. on visual pathways, Tastekin et al. on the taste–feeding connectome ([Google Research blog](https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/)).

**Open tooling.** neuPrint (`neuprint-python`, `neuprintr`), CAVE / CAVEclient (Connectome Annotation Versioning Engine), `navis` + `fafbseg-py`, R `natverse` (`nat`, `malecns`, `malevnc`), Virtual Fly Brain's `vfb_connect`, and — most relevant here — a **public MCP server at `https://vfb3-mcp.virtualflybrain.org`, no API key required**, exposing `get_term_info`, `search_terms`, `run_query` (NBLAST similarity), `get_hierarchy`, `resolve_entity` to Claude Desktop/Claude Code/Copilot ([VFB MCP guide](https://www.virtualflybrain.org/docs/tutorials/vfb-mcp-guide/); announced in VFB news 2026-06-21). VFB added MaleCNS visualisation on 2026-09-03 ([VFB news](https://www.virtualflybrain.org/blog/news/)).

## 2. What these actually enable computationally

**(a) Whole-brain spiking simulation, laptop-to-single-GPU scale.** Shiu et al., *Nature* 634:210–219 ([10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9)) built a LIF model over the whole FlyWire graph using only connectivity + predicted neurotransmitter sign — **no fitted synaptic weights, no channel biophysics** — and it correctly predicted which neurons drive proboscis extension on sugar/water stimulation and antennal-grooming, both confirmed in live flies. Eon Systems' open reimplementation (GPL-2.0, 482★, created 2026-03-05) benchmarks six backends; peak measured real-time ratios: **GeNN GPU 7.80×, Brian2GeNN 1.23×, NEST GPU 1.15×, Brian2 CPU 1.10×, Brian2CUDA 0.37×, PyTorch CUDA 0.18×**.

**(b) Connectome-constrained *trained* networks.** Lappalainen et al., *Nature* 634:1132–1140 ([10.1038/s41586-024-07939-3](https://doi.org/10.1038/s41586-024-07939-3)) fixed the wiring for 64 optic-lobe cell types (~45,000 neurons, 721 columns) and learned only per-cell-type single-neuron and unit-synapse parameters against an optic-flow task; the model then predicted ON/OFF channel split and T4/T5 direction selectivity. Code: [TuragaLab/flyvis](https://github.com/TuragaLab/flyvis) (MIT, 125★). **This is the sharpest computational idea in the whole literature for an engineer: a fixed sparse graph as a hard structural prior, with a tiny shared-per-type parameter budget.**

**(c) Embodiment.** NeuroMechFly v2 (*Nature Methods*, 2024-11-12, [10.1038/s41592-024-02497-y](https://doi.org/10.1038/s41592-024-02497-y)) gives an 87-joint MuJoCo fly body; [NeLy-EPFL/flygym](https://github.com/NeLy-EPFL/flygym) (Apache-2.0, 216★). Eon Systems coupled the ~140k-neuron LIF brain to it with a 15 ms brain–body sync loop (2026-03-10, [eon.systems/updates/embodied-brain-emulation](https://eon.systems/updates/embodied-brain-emulation)) — but their own post concedes "we have not yet validated the model's internal dynamics against known biological signatures," a "deliberately low-dimensional readout layer," and hand-chosen brain–body mappings.

**(d) Graph analytics as the workhorse.** [`connectome_interpreter`](https://github.com/YijieYin/connectome_interpreter) (MIT, on PyPI) computes **polysynaptic "effective connectivity"** by compressing signed path products over the graph, does path-finding between neuron groups, and runs a differentiable firing-rate model — whole-brain, on a laptop, for ~140k-node graphs. Pospisil et al.'s "effectome" paper (*Nature* 634:201–209, [10.1038/s41586-024-07982-0](https://doi.org/10.1038/s41586-024-07982-0)) makes the complementary point that structure alone under-determines causal influence.

## 3. The September 2026 hobbyist wave (the "interesting projects" answer)

Within **three days** of the MaleCNS release, developers wired it to games:

- **[nftechie/doomfly](https://github.com/nftechie/doomfly)** (MIT, created 2026-09-06): 3,335 R1–R6 + 811 R8 photoreceptor inputs driven by ViZDoom frames → **166,700 retained neurons, 25,582,938 directed connections** → DNp20 left-minus-right drives turning, DNpe017 drives move/fire; a dopamine-gated plasticity rule on **4,184 KC→MBON11 connections**. Crucially, the README states: *"Status: live experimental training, not demonstrated learned survival. The current v6 candidate failed its visual, conditioning and survival validation gates."* It ships negative results, controls, dataset hashes and a `source.lock.json`.
- **[dzhng/fly-escape](https://github.com/dzhng/fly-escape)** (2026-09-06): browser game, Rust→WASM LIF sim over a MaleCNS subgraph, committed graph + provenance manifest.
- **[DenisSergeevitch/desktop-fly](https://github.com/DenisSergeevitch/desktop-fly)** (795★): macOS desktop fly; 23,210 real FlyWire soma positions rendered, a **668-neuron / 18,968-connection** FlyWire escape circuit (LC4, LPLC2, Giant Fiber DNp01, DNa01/02, MDN…) at 1 kHz LIF, plus a **1,045-neuron MaleCNS locomotor extract (17,224 connections = 708,689 synaptic contacts)** driving articulated legs.
- **[erojasoficial-byte/fly-brain](https://github.com/erojasoficial-byte/fly-brain)** (MIT, 2026-03): 138,639-neuron FlyWire v783 sim in NeuroMechFly v2.

Also reported: Super Mario 64 and Minecraft variants and a "Bad Apple" pipe-into-the-connectome demo ([Gizmodo](https://gizmodo.com/google-mapped-a-fruit-flys-brain-now-its-playing-doom-and-super-mario-64-2000808616), [Tom's Hardware](https://www.tomshardware.com/software/programming/google-maps-entire-brain-and-central-nervous-system-of-adult-male-fruit-fly-software-engineers-immediately-make-it-run-doom-ai-powered-3d-model-of-over-166-000-neurons-can-also-play-super-mario-64)). **The scientific content of these is ~zero; the engineering-culture content is high** — they are the fastest-ever demonstration that an open, well-provenanced, well-typed knowledge artifact gets used within 72 hours.

## 4. Relevance to company-brain / RAG / fruit-fly question

I'll grade the transfer in three tiers, honestly.

### Tier 1 — real, and directly usable

**(1.1) The connectome projects are the best existing proof of Tan's actual thesis, and it is a *process* proof, not an architecture one.** Tan's claim is "retrieval is easy; being worth retrieving from is the product," and that the deliverables are curation, provenance, hot-vs-cold, and contradiction arbitration. The fly connectome is exactly that artifact, done at 10⁵ scale, and every one of Tan's primitives has a literal counterpart: **provenance per fact** = `minconf-0.5` thresholds, `source.lock.json`, SHA-256 dataset checksums; **versioning** = CAVE (the *Connectome Annotation Versioning Engine*) and pinned dataset versions v783 / v888 / v1.0; **contradiction arbitration** = the human proofreading pipeline that reconciles conflicting machine segmentations; **the librarian** = 11,710 curated cell types layered on top of raw EM segmentation. Raw flood-filling-network output *is* Tan's "garbage dump with great search"; the annotation layer is what made it a resource. The sobering calibration: it took ~20 years, hundreds of people, and a Google-scale segmentation model to curate 166,700 nodes. Anyone quoting "220,000 pages, mostly agent-written" should be asked what their proofreading process is.

**(1.2) FlyHash is a genuine RAG primitive — but it lives in the layer Tan dismisses.** The fly's olfactory circuit expands ~50 projection neurons into ~2,000 Kenyon cells via a sparse binary random projection, then APL feedback inhibition keeps only the top ~5% active: a locality-sensitive hash with *high-dimensional sparse* codes instead of the usual low-dimensional dense ones (Dasgupta et al., *Science* 2017). Data-driven successor BioHash (arXiv [2001.04907](https://arxiv.org/abs/2001.04907)); **BioVSS** applies it to *vector-set* search with Bloom-filter indexing and reports **>50× over linear scan at up to 98.9% recall on million-scale data** (arXiv [2412.03301](https://arxiv.org/abs/2412.03301)). Verdict: worth benchmarking against HNSW/IVF-PQ *only* if you have low-dimensional inputs, streaming/novelty-detection needs, or a memory-constrained edge deployment. It will not change what your brain is worth retrieving from.

**(1.3) Multi-hop "effective connectivity" ≈ multi-hop graph RAG.** `connectome_interpreter`'s signed path-compression over a 140k-node graph is mathematically the same object as personalized-PageRank / multi-hop expansion over a document knowledge graph (HippoRAG-style). If the company brain is a graph of documents with typed, signed edges (supports / contradicts / supersedes), the neuroscience tooling is directly reusable, laptop-scale, MIT-licensed, and battle-tested at exactly the node count a large company brain would have. **This is the most concretely portable code in the whole survey.**

**(1.4) The VFB MCP server is the template.** A public, keyless MCP endpoint over a curated, versioned, ontology-backed scientific corpus, usable from Claude Code today, is *literally* "library + librarian, exposed to agents." If the user wants a demo that fuses both halves of the question, `claude mcp add --transport http virtual-fly-brain https://vfb3-mcp.virtualflybrain.org` is a five-minute end-to-end illustration.

### Tier 2 — plausible, unproven, and currently contradicted

**Connectome-derived architectures / routing motifs.** The temptation is obvious: the fly graph is rich-club organised (30% highly connected hub neurons acting as integrators and broadcasters — Lin et al. 2024), which looks like a router topology for an agent swarm; BANC's abstract even says the architecture is "distributed, parallelized and embodied, reminiscent of distributed control architectures in engineered systems." FlyGM (arXiv [2602.17997](https://arxiv.org/abs/2602.17997), Jin, Zhu, Zhang & Sui, Tsinghua; v1 2026-02-20, v3 2026-06-14) instantiates the whole-brain connectome as a graph controller for RL locomotion and reports better sample efficiency than graph and non-graph baselines.

**But the controlled replication says the effect is a confound.** Dhiman, "Topological Sensitivity in Connectome-Constrained Neural Networks" (arXiv [2604.04033](https://arxiv.org/abs/2604.04033), 2026-04-05), re-ran flyvis (45,669 nodes, 1,513,231 edges) against a naive random null and a **degree-preserving** null: the loss advantage at 5 steps (0.514 connectome vs 0.698 naive-random) *vanished* under shared random initialization, and the activity advantage vanished under the degree-preserving null. Conclusion: "previously reported topology advantages … can arise from initialization and null-model confounds." I found **no** work applying connectome motifs to MoE routing, retrieval routing, or agent orchestration. Treat "connectome-derived architecture for a company brain" as an untested hypothesis whose nearest test failed.

**Mushroom-body memory dynamics** (sparse KC coding + dopamine-gated write + *active forgetting* + reconsolidation-on-retrieval) is the one biological memory system that maps cleanly onto Tan's hot-vs-cold memory and "librarian whose job is pruning." 2025–26 fly work shows forgotten memories persist as silent MBON traces recoverable by context-gated dopaminergic reminders, and that the same machinery generates *false* memories ([PMC13533848](https://pmc.ncbi.nlm.nih.gov/articles/PMC13533848/)) — a nice biological cautionary tale about stale facts resurfacing with confidence. But the LLM-agent memory literature that actually cites biology cites hippocampal/complementary-learning-systems framing, not mushroom bodies. The doomfly experiment tried MB plasticity (4,184 KC→MBON11 synapses) and **explicitly failed its conditioning and survival gates** — the only empirical data point I have, and it is negative.

### Tier 3 — metaphor only; say so

The fly connectome is a ~1.7×10⁵-node graph with essentially **no semantic content** — an edge means "these two cells touch and one releases neurotransmitter onto the other." A company brain is ~10⁵–10⁶ *documents* whose value is entirely semantic, whose topology is authored not evolved, and which must answer natural-language questions. Whole-brain emulation is not an information-retrieval system: running the fly at 7.8× real time gets you a faster fly, not a librarian. The numerical coincidence (139,255 neurons vs Tan's "220,000 pages") is a coincidence. And the field's own consensus is that connectivity under-determines function: "the connectome is not enough" — missing ion channels, receptors, neuromodulators and gap junctions ([*J. Exp. Biol.* 224:jeb242740](https://journals.biologists.com/jeb/article/224/21/jeb242740/272599/A-connectome-is-not-enough-what-is-still-needed-to)); Eve Marder and Cori Bargmann make the same point in [The Transmitter, "Connectomics 2.0: Simulating the brain," 2025-05-02](https://www.thetransmitter.org/connectome/connectomics-2-0-simulating-the-brain/). **A wiring diagram without dynamics is precisely what a document graph without curation is** — which, pleasingly, is Tan's own argument, arrived at from the other direction.

## 5. Open questions

- Does the user's "recently published fruit fly brain work" mean the **2026-09-03 MaleCNS release** (my top pick, 1 week before this session), the **2026-06-08 BANC paper**, or the **2026-03 Eon Systems embodied-fly announcement**? The three have very different implications and should be disambiguated with the user.
- Has anyone benchmarked **BioVSS/FlyHash against HNSW inside an actual RAG pipeline** at document-embedding dimensionality (768–3072)? All published FlyHash wins are at ≤1,000 dims; the method's advantage may not survive.
- Is there an **MCP server for Codex / neuPrint** (beyond VFB's), and could the same pattern — ontology + versioned facts + confidence thresholds + MCP — be lifted wholesale as a company-brain reference design?
- FlyGM claims sample-efficiency gains; **does it survive the degree-preserving null control** that killed the flyvis result? The critique paper tested flyvis, not FlyGM.
- Eon Systems' repo carries a `nature_2026_07` benchmark run label — is a *Nature* paper on whole-brain-emulation compute in press? Unverified.
- What does GBrain actually do about provenance/versioning, and does it have anything resembling CAVE? (Other workers' dimension.)

## Sources

- Dorkenwald et al., "Neuronal wiring diagram of an adult brain," *Nature* 634:124–138 (2024-10-02) — https://doi.org/10.1038/s41586-024-07558-y
- Schlegel et al., "Whole-brain annotation and multi-connectome cell typing of Drosophila," *Nature* 634:139–152 — https://doi.org/10.1038/s41586-024-07686-5
- Lin et al., "Network statistics of the whole-brain connectome of Drosophila," *Nature* 634:153–165 — https://doi.org/10.1038/s41586-024-07968-y
- Matsliah, Yu et al., "Neuronal parts list and wiring diagram for a visual system," *Nature* 634:166–180 — https://doi.org/10.1038/s41586-024-07981-1
- Shiu et al., "A Drosophila computational brain model reveals sensorimotor processing," *Nature* 634:210–219 — https://doi.org/10.1038/s41586-024-07763-9
- Pospisil et al., "The fly connectome reveals a path to the effectome," *Nature* 634:201–209 — https://doi.org/10.1038/s41586-024-07982-0
- Lappalainen et al., "Connectome-constrained networks predict neural activity across the fly visual system," *Nature* 634:1132–1140 — https://doi.org/10.1038/s41586-024-07939-3
- Bates et al., "Distributed control circuits across a brain-and-cord connectome" (BANC), *Nature* 656:957–970 (2026-06-08) — https://doi.org/10.1038/s41586-026-10735-w
- Berg et al., "Sexual dimorphism in the complete Drosophila male central nervous system connectome," *Cell* 189:5504–5526.e15 (2026-09-03) — https://doi.org/10.1016/j.cell.2026.08.015
- Google Research blog, "A connectomics milestone: Mapping the complete male fruit fly brain" (2026-09-03) — https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/
- phys.org, "Completing the connectome…" (2026-09) — https://phys.org/news/2026-09-connectome-pursuing-fly-brain-rewired.html
- MaleCNS downloads / license / neuPrint dataset — https://male-cns.janelia.org/download/
- Codex dataset list — https://codex.flywire.ai/api/download · repo https://github.com/murthylab/codex
- Virtual Fly Brain MCP server guide — https://www.virtualflybrain.org/docs/tutorials/vfb-mcp-guide/ · news https://www.virtualflybrain.org/blog/news/ · tools https://www.virtualflybrain.org/docs/tutorials/apis/connectome/tools/
- Eon Systems, "How the Eon Team Produced a Virtual Embodied Fly" (2026-03-10) — https://eon.systems/updates/embodied-brain-emulation
- eonsystemspbc/fly-brain (GPL-2.0, 482★) — https://github.com/eonsystemspbc/fly-brain · benchmarks https://github.com/eonsystemspbc/fly-brain/blob/main/data/benchmark-results.csv
- Jin, Zhu, Zhang & Sui, "Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly," arXiv:2602.17997 — https://arxiv.org/abs/2602.17997
- Dhiman, "Topological Sensitivity in Connectome-Constrained Neural Networks," arXiv:2604.04033 — https://arxiv.org/abs/2604.04033
- Zanichelli, Schons, Freeman, Shiu & Arkhipov, "State of Brain Emulation Report 2025," arXiv:2510.15745 — https://arxiv.org/abs/2510.15745
- Dasgupta, Stevens & Navlakha, "A neural algorithm for a fundamental computing problem," *Science* (2017) — https://doi.org/10.1126/science.aam9868
- Ryali et al., "Bio-Inspired Hashing for Unsupervised Similarity Search," arXiv:2001.04907 — https://arxiv.org/abs/2001.04907
- Li et al., "Approximate Vector Set Search Inspired by Fly Olfactory Neural System" (BioVSS), arXiv:2412.03301 — https://arxiv.org/abs/2412.03301
- NeuroMechFly v2, *Nature Methods* (2024-11-12) — https://doi.org/10.1038/s41592-024-02497-y · https://github.com/NeLy-EPFL/flygym
- "A connectome is not enough…", *J. Exp. Biol.* 224:jeb242740 — https://journals.biologists.com/jeb/article/224/21/jeb242740/272599/A-connectome-is-not-enough-what-is-still-needed-to
- Dattaro, "Connectomics 2.0: Simulating the brain," The Transmitter (2025-05-02) — https://www.thetransmitter.org/connectome/connectomics-2-0-simulating-the-brain/
- Demo repos: https://github.com/nftechie/doomfly · https://github.com/dzhng/fly-escape · https://github.com/DenisSergeevitch/desktop-fly · https://github.com/erojasoficial-byte/fly-brain
- Press on game demos: https://gizmodo.com/google-mapped-a-fruit-flys-brain-now-its-playing-doom-and-super-mario-64-2000808616
- Tools: https://github.com/TuragaLab/flyvis · https://github.com/YijieYin/connectome_interpreter · https://github.com/navis-org/fafbseg-py

# Neuroscience-Inspired Retrieval & Memory for LLMs (non-fly)
**Dimension key:** `neuro-inspired-rag` · **Written:** 2026-09-10 · Research worker (Opus 5)

## TL;DR

1. **Garry Tan's "library + librarian" framing is not a metaphor the field invented after him — it is the dominant research program of 2024-2026.** The exact distinctions he draws (retrieval-as-primitive vs. curation-as-product, hot vs. cold memory, contradiction arbitration, skillification) each map onto a named, benchmarked literature: hippocampal indexing (HippoRAG), complementary learning systems (dual-layer agentic memory), bi-temporal fact invalidation (Zep/Graphiti, TOKI), and procedural-memory distillation (Skill-DisCo, SkillLens).
2. **The strongest *measured* result in the whole space supports Tan's "wrong side of the computation" thesis, not his brain metaphor.** On MemoryAgentBench's FactConsolidation contradiction task, all 22 published memory systems scored ≤7% multi-hop and the best (HippoRAG-v2) only 54% single-hop — but a *deterministic* `max(serial_number)` in Python, with BM25 retrieval and no LLM freshness reasoning, hit 82–93% single-hop and 27–41% multi-hop ([arXiv:2606.01435](https://arxiv.org/abs/2606.01435)). Contradiction arbitration is a database problem, not a latent-space problem.
3. **Biological inspiration reliably buys *efficiency and hygiene*, and only sometimes buys accuracy.** Microsoft's six-mechanism human-inspired architecture raised retention precision +21.8pp but scored 76.8% vs. a 78.4% baseline on LongMemEval S-tier ([arXiv:2605.08538](https://arxiv.org/html/2605.08538v1)). CLS-based dual-layer memory pruned 68% of stored memories while keeping 98.3% of QA exact-match ([arXiv:2608.22215](https://arxiv.org/html/2608.22215)). The wins are cost, storage, and staleness — precisely Tan's "garbage dump with great search" failure mode.
4. **"Skillify everything" has a documented breaking point.** A controlled study over 8,135 normalized trials found skills act as *procedural anchors* (65.7% of cases) rather than knowledge injection (4.5%), improving success 59.1%→61.9% — but skill **retrieval precision collapses from 29.6% at a pool of 5 to 3.3% at a pool of 100** ([arXiv:2608.14036](https://arxiv.org/html/2608.14036v1)). Tan's ~220,000-page brain is far past that regime; it only works if there is a routing/resolver layer, which is exactly what he calls the org chart.
5. **Production-ready today: hippocampal-indexing graph retrieval (HippoRAG 2, MIT), bi-temporal invalidation (Graphiti), offline consolidation ("sleep-time compute"), and a memory-OS layer (MemOS 2.0, which ships official OpenClaw and Hermes Agent plugins — the same harnesses GBrain targets).** Not ready: Hopfield/SDM as an actual storage substrate, and test-time weight memory (Titans/HOPE), which failed to fully reproduce ([arXiv:2510.09551](https://arxiv.org/abs/2510.09551)).

---

## 1. The theoretical lineage: attention *already is* associative memory

Two results underwrite every claim that "retrieval is just a primitive."

**Modern Hopfield networks (Ramsauer et al., 2020).** "Hopfield Networks is All You Need" ([arXiv:2008.02217](https://arxiv.org/abs/2008.02217), submitted 2020-07-16, Hochreiter's group at JKU Linz) showed that replacing the binary state space and quadratic energy of a classical Hopfield net with a continuous state space and a log-sum-exp energy raises storage capacity from *linear* to *exponential* in dimension, retrieves in a single update, and that the resulting update rule `ξ_new = X softmax(β Xᵀ ξ)` **is** transformer attention. Code: [github.com/ml-jku/hopfield-layers](https://github.com/ml-jku/hopfield-layers). A September 2026 NeuroAI book chapter re-derives the exact conditions under which the Hopfield update becomes scaled dot-product attention ([arXiv:2609.02195](https://arxiv.org/abs/2609.02195), Dehghani, 2026-09-02).

*Biological principle borrowed:* content-addressable attractor memory / pattern completion.
*Why it matters for a company brain:* it is the formal reason "this is just RAG" is a category error in the same way "Postgres is just B-trees" is. Attention is already an associative memory; the interesting design surface is what patterns you store.

**Sparse distributed memory (Kanerva → transformers).** Bricken & Pehlevan, "Attention Approximates Sparse Distributed Memory," NeurIPS 2021 ([arXiv:2111.05498](https://arxiv.org/abs/2111.05498), code: [github.com/TrentBrick/attention-approximates-sdm](https://github.com/TrentBrick/attention-approximates-sdm)), showed attention closely approximates Kanerva's biologically plausible SDM under conditions they verified hold in pretrained GPT-2. The follow-up, "Sparse Distributed Memory is a Continual Learner" (Bricken, Davies, Singh, Krotov, Kreiman; ICLR 2023, [arXiv:2303.11934](https://arxiv.org/pdf/2303.11934), code: [github.com/TrentBrick/SDMContinualLearner](https://github.com/TrentBrick/SDMContinualLearner)) found that an MLP modified with Top-K activation, L2 normalization and positive weight constraints resists catastrophic forgetting **without task labels, task boundaries, or replay**.

*Bridge to the user's fruit-fly question:* SDM's sparse high-dimensional expansion is the same computational motif as FlyHash/the Drosophila mushroom body ([arXiv:2001.04907](https://arxiv.org/abs/2001.04907) "Bio-Inspired Hashing"). So the fly work and the SDM work are two branches of one idea — sparse expansive codes for locality-preserving recall — and SDM is the branch with the LLM-side theory already worked out.

---

## 2. Hippocampal indexing: the one that actually shipped

**HippoRAG** (Gutiérrez, Shu, Gu, Yasunaga, Su; NeurIPS 2024, [arXiv:2405.14831](https://arxiv.org/abs/2405.14831)) implements *hippocampal memory indexing theory*: an LLM plays neocortex (extracts a knowledge graph of entities), the KG plays the hippocampal index, and **Personalized PageRank** plays pattern completion across the index. Reported: up to **20% improvement** on multi-hop QA, and single-step retrieval matching iterative retrieval (IRCoT) while being **10–30× cheaper and 6–13× faster**.

**HippoRAG 2** ("From RAG to Memory: Non-Parametric Continual Learning for LLMs," ICML 2025, [arXiv:2502.14802](https://arxiv.org/abs/2502.14802)) adds dual-node passage+phrase graphs and LLM triple filtering, gaining **~7 points F1 over embedding retrievers on associative memory** while beating GraphRAG/RAPTOR/LightRAG on offline indexing cost. Repo: [github.com/OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG), **MIT licensed**, supports OpenAI/Azure/Bedrock/vLLM-Llama-3.3-70B and NV-Embed-v2.

This is the single most directly transplantable piece of neuro-inspired machinery for a GBrain-style system: it is the "librarian" as a graph-walk over a curated index, not a nearest-neighbour lookup.

---

## 3. Complementary learning systems (CLS): hot vs. cold memory, formalized

CLS theory (McClelland et al. 1995; Kumaran et al. 2016) says the hippocampus learns fast and episodically while the neocortex consolidates slowly and semantically, with offline replay during sleep (Wilson & McNaughton 1994). This is Tan's hot-memory/cold-reference split with a citation.

- **Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation** (Li et al., [arXiv:2608.22215](https://arxiv.org/html/2608.22215), 2026-08-31). Routes every incoming fact as non-write / write-new / write-update through a **1.7B→8B model cascade**, then periodically consolidates high-value external memories into weights via SFT. Measured: prunes up to **68%** of redundant external memory, escalates <50% of inputs to the big model, retains **98.3%** of the full-store QA EM (86.35% vs 87.79%); store precision **91.06% vs 76.54%**; after write-back consolidation, **90.71% EM at 47.85% storage**. Code "upon acceptance" — not yet public.
  *This is the strongest formal answer to "what gets written down is the product."* The decision of what to write is a routed classification problem with its own cost model.
- **Human-Inspired Memory Architecture for LLM Agents** (Kerestecioglu, Robsky, Vasters, Sharma, Kesselman — Microsoft; [arXiv:2605.08538](https://arxiv.org/html/2605.08538v1), 2026-05-08). Six mechanisms: sleep-phase consolidation, interference-based forgetting, engram maturation, reconsolidation on retrieval, entity KG, hybrid multi-cue retrieval. Exponential decay λ=0.001 (~29-day half-life). Results: **+21.8pp retention precision (97.2%) on VSCode issue tracking**, but **76.8% vs 78.4% baseline on LongMemEval S-tier** and 70.1% vs 71.2% on M-tier at a 200K-token budget. Honest, and instructive: biology bought hygiene, not raw accuracy. No public code.
- **Sleep-time compute** (Lin, Snell, Wang, Packer, Wooders, Stoica, Gonzalez; Letta, April 2025; [letta.com/blog/sleep-time-compute](https://www.letta.com/blog/sleep-time-compute/)). A second "sleep agent" reorganizes memory during idle time, producing Pareto improvements on AIME/GSM8K by moving compute out of the latency-critical path. This is the productized version of replay-based consolidation, and the cheapest CLS idea to adopt.
- **ComMem** (Sun et al., [arXiv:2606.28719](https://arxiv.org/pdf/2606.28719), 2026-06-30) applies complementary memory systems to test-time adaptation of vision-language models — evidence the CLS pattern generalizes beyond text.

---

## 4. Memory in the weights: Titans, Nested Learning, and a reproducibility caveat

**Titans: Learning to Memorize at Test Time** (Behrouz, Zhong, Mirrokni; Google Research; [arXiv:2501.00663](https://arxiv.org/pdf/2501.00663), NeurIPS 2025) adds a deep neural long-term memory module that updates *its own weights during the forward pass*, gated by a gradient-based **"surprise" signal with momentum** plus adaptive forgetting. Three heads: core (short-window attention), long-term memory, persistent memory. Biological principle: events that violate expectations are more memorable.

**Nested Learning / HOPE** (Behrouz & Mirrokni, Google Research blog 2025-11-07, [research.google/blog/introducing-nested-learning...](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/), NeurIPS 2025) generalizes this to a hierarchy of learning problems at different **update frequencies** — explicitly modeled on multi-timescale neuroplasticity and brain-wave frequency bands. HOPE is a self-modifying Titans variant with Continuum Memory System blocks; reported lower perplexity and higher accuracy than Titans, Samba and Transformers, and better needle-in-a-haystack performance than TTT and Mamba2.

**Caveat — do not build on this yet.** "Titans Revisited" (Di Nepi, Siciliano, Silvestri; [arXiv:2510.09551](https://arxiv.org/abs/2510.09551), 2025-10-13) notes the lack of public code and ambiguities in the description, and their reimplementation found **"Titans does not always outperform established baselines due to chunking,"** though the neural memory component alone did consistently beat attention-only models.

---

## 5. The memory-OS layer, and the direct GBrain connection

**CoALA — Cognitive Architectures for Language Agents** (Sumers, Yao, Narasimhan, Griffiths; Princeton; [arXiv:2309.02427](https://arxiv.org/abs/2309.02427), TMLR) is the vocabulary everyone now uses: working / episodic / semantic / procedural memory, plus a structured internal-vs-external action space. Tan's four-way mapping (skill file = employee, resolver = org chart, filing rules = process, evals = reviews) is a business-language restatement of CoALA's procedural/semantic/episodic split.

**MemOS** ([arXiv:2507.03724](https://arxiv.org/abs/2507.03724), 39 authors, July 2025, revised Dec 2025; earlier variant [arXiv:2505.22101](https://arxiv.org/abs/2505.22101)) elevates memory to a first-class OS resource via the **MemCube** — a standardized abstraction carrying content *plus metadata including provenance and versioning*, composable and migratable across plaintext / activation / parametric memory. That is Tan's "provenance per fact" requirement as a type.

The 2026 shipping state is the striking part. [github.com/MemTensor/MemOS](https://github.com/MemTensor/MemOS) (MemOS 2.0 "Stardust") reports:
- **2026-07-02:** with MemOS, **OpenClaw improves average task completion from 36.63% → 50.87%** across five agent tasks; **88.83 LoCoMo**, **89.20 LongMemEval**; leads OmniMemEval across 14 commercial memory products / 10 datasets.
- **2026-03-08:** official OpenClaw cloud plugin with **72% lower token usage**.
- **2026-05-09:** local plugin for **Hermes Agent** and OpenClaw with "L1 traces, L2 policies, L3 world models, and crystallized Skills."
- **2026-08-17:** DeepSeek Harness integration.

**This is the same harness ecosystem GBrain targets** (Tan: GBrain "loves OpenClaw / Hermes agent"). MemOS's L1/L2/L3+Skills tiering is the closest existing implementation of Tan's hot-memory / cold-reference / skillification stack, and it is a direct comparable — or a component — for GBrain. Landscape scale: the companion [Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory) list tracks **542 papers and 111 open-source projects** as of mid-2026.

Counterpoint on benchmarks: Mem0's own [State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) (2026-09-09) reports Mem0 at **92.5 LoCoMo / 94.4 LongMemEval** (~6.9K tokens/query) vs Zep 80.32 / Letta 74.0 / OpenAI Memory 52.9 — and mentions **no** neuroscience inspiration at all. Two of the top scorers on these benchmarks are purely engineering-driven. Neuro-inspiration is not currently a prerequisite for benchmark leadership.

---

## 6. Retrieval → reconstruction: the sharpest "not just RAG" argument

- **MRAgent — "Memory is Reconstructed, Not Retrieved"** (Ji, Li, Hooi; NUS; [arXiv:2606.06036](https://arxiv.org/html/2606.06036v1), 2026-06-04). Cue–Tag–Content associative graph with iterative, evidence-pruned exploration; borrows cue-triggered engram reactivation from cognitive neuroscience. **LoCoMo LLM-judge 68.31 → 84.21 (Gemini); 69.02 → 88.32 (Claude); ~32% relative gain on LongMemEval; 118K tokens vs 245K–3,268K for baselines.** Code: [github.com/Ji-shuo/MRAgent](https://github.com/Ji-shuo/MRAgent).
- **RippleMem** (Ji et al., [arXiv:2608.13334](https://arxiv.org/abs/2608.13334), 2026-08-13). Cue-dependent episodic retrieval + associative completion: recalled memories become cues for further recall. **+3.95% LoCoMo, +11.87% LongMemEval-S, ~30× cheaper graph construction.** No public code found.
- **ZenBrain** (Alexander Bering, [arXiv:2604.23878](https://arxiv.org/abs/2604.23878), v1 2026-04-26, v3 2026-08-09) integrates fifteen cognitive-neuroscience mechanisms (Two-Factor synaptic consolidation → Simulation-Selection sleep loop) in seven layers. Claims all 9 head-to-head wins vs Letta/Mem0/A-Mem (p_min=6.2e-31), **91.3% of full-context oracle accuracy at 1/106th the per-query token cost**, +20.7% F1 on LoCoMo from multi-layer routing. **Single-author, no code released — treat as low confidence.**

---

## 7. Hygiene: contradiction, staleness, provenance — the actual bottleneck

Tan's stated failure mode ("stale facts surfaced with confidence") is the field's measured weak point.

- **MemoryAgentBench** (ICLR 2026, [arXiv:2507.05257](https://huggingface.co/papers/2507.05257), code: [github.com/HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench)) includes **FactConsolidation**, built from MQUAKE counterfactual rewrites where facts are numbered and agents are *told* higher serials are newer. Results across 22 systems: **HippoRAG-v2 54% single-hop, BM25 48%, Mem0 18%, Zep/Graphiti 7%; ≤7% multi-hop for every system.**
- **"Don't Ask the LLM to Track Freshness" / "Reliable Post-Retrieval Assembly for Agent Memory"** (Vikas Reddy, Sumanth Reddy Challaram; [arXiv:2606.01435](https://arxiv.org/abs/2606.01435), v1 2026-05-31, v2 2026-08-02, code: [github.com/cvikasreddy/memory-conflict-resolution](https://github.com/cvikasreddy/memory-conflict-resolution)). Separating evidence extraction from policy execution — BM25 retrieval then a deterministic `max(serial)` — reaches **82%/93% single-hop and 27%/41% multi-hop** (gpt-4o-mini/gpt-4o), +10.8pp whole-pipeline single-hop average and +21pp at 262K scale.
- **TOKI: A Bitemporal Operator Algebra for Contradiction Resolution** (Ziming Wang, HKUST; [arXiv:2606.06240](https://arxiv.org/pdf/2606.06240), 2026-06-05, code: [github.com/ZenAlexa/toki-bitemporal-memory](https://github.com/ZenAlexa/toki-bitemporal-memory)) formalizes valid-time vs. transaction-time with semiring foundations rather than overwrite-on-conflict.
- **Zep / Graphiti** ([arXiv:2501.13956](https://arxiv.org/abs/2501.13956), 2025-01-20) is the shipped version: every edge carries when it became true and when it stopped, so the agent never chooses between a stale and a current fact. DMR 94.8% vs MemGPT 93.4%.
- **Always-On Agents survey** (Ding, Nannapaneni, Liu, Zhang; [arXiv:2606.30306](https://arxiv.org/html/2606.30306v1), 2026-06-30) argues persistent state is broader than memory — task ledgers, permissions, credentials, commitments, **provenance and audit records**, trigger state — and grounds it in Tulving 1972, McClelland 1995 / Kumaran 2016 CLS, Wilson & McNaughton 1994 replay, and Murre & Dros 2015 forgetting curves.

---

## 8. Skillification, checked

Tan's "never do one-off work — skillify it" has a 2026 evidence base and a documented ceiling.

- **Demystifying Agent Skills** (Jiang et al., [arXiv:2608.14036](https://arxiv.org/html/2608.14036v1), 2026-08-14; Terminal-Bench 2.0/Pro, SkillsBench; GPT-5.3-Codex, Gemini-3.1-Pro, GPT-5.4; 8,135 normalized trials). Skills are **procedural anchors (65.7%)** not knowledge injection (4.5%). Success **59.1% → 61.9%**, +6.06pp over workflow memory; infra failures 5.3%→0.2%; format mismatches 7.4%→3.2%. **But: skill misapplication errors 0.8%→10.0%; retrieval precision 29.6%@pool-5 → 3.3%@pool-100; offline identification 70.5%@k=5 → 53.4%@k=100; skills never repair algorithmic errors (7.4% failure regardless).**
- Related 2026 machinery: **Skill-DisCo** ([arXiv:2606.26669](https://arxiv.org/abs/2606.26669)) distils PFSM subgraphs from successful traces into callable, verifiable skills; **SkillLens** ([arXiv:2605.08386](https://arxiv.org/pdf/2605.08386)) does multi-granularity partial skill reuse; **Managing Procedural Memory in LLM Agents** ([arXiv:2606.23127](https://arxiv.org/html/2606.23127v1)) introduces EvoSkill's generate–verify–refine loop.

---

## Relevance to the company-brain / RAG / fruit-fly question

**(a) Does this relate to RAG?** Yes, and the field has already made Tan's distinction rigorous. RAG is one *memory operation* (retrieval) in the CoALA taxonomy; the company brain adds **write routing** (2608.22215), **consolidation** (sleep-time compute, engram maturation), **invalidation** (Graphiti, TOKI), **provenance typing** (MemCube), and **reconstruction** (MRAgent, RippleMem). The empirically load-bearing insight is Tan's own latent-vs-deterministic split: contradiction arbitration works when it is a Python `max()`, and fails when it is an LLM judgement (54% → 93%).

**(b) Combining with fruit-fly work.** The non-fly bridge is **sparse distributed memory**. Kanerva SDM ↔ transformer attention ([arXiv:2111.05498](https://arxiv.org/abs/2111.05498)) and SDM ↔ continual learning without replay ([arXiv:2303.11934](https://arxiv.org/pdf/2303.11934)) are the same sparse-expansive-code motif as FlyHash/mushroom body ([arXiv:2001.04907](https://arxiv.org/abs/2001.04907)). A concrete combination: use a fly-style sparse expansive hash as the *index* (novelty detection = "is this worth writing down?", the MBON-α'3 novelty signal), HippoRAG-style PPR as the *recall* mechanism, and bi-temporal edges as the *arbitration* layer. Each of those three has independent published evidence; the composition does not appear to have been published.

**(c) Which principles are ready for a production company brain today** (ranked):
1. **Bi-temporal fact invalidation + deterministic conflict policy** — highest measured payoff, trivially implementable, MIT/open code. Do this first.
2. **Hippocampal-index graph retrieval (HippoRAG 2)** — MIT, maintained, 7pp associative gain, cheap offline indexing.
3. **Offline consolidation / sleep-time compute** — Pareto win by construction; moves cost off the critical path.
4. **CLS write-routing (small model gates writes, big model escalates)** — 68% storage pruned at 98% quality; the direct cure for "garbage dump with great search."
5. **Memory-OS layer with typed provenance (MemOS MemCube)** — already integrated with OpenClaw/Hermes/DSH; the nearest neighbour to GBrain.
6. **Skill libraries — with a hard cap and a resolver.** Beyond ~100 skills, flat retrieval precision falls to ~3%; hierarchical routing is mandatory, not optional.
7. *Not ready:* Hopfield/SDM as an actual storage substrate (theory, not systems); Titans/HOPE test-time weight memory (no public code, partial reproduction failure); ZenBrain-class 15-mechanism stacks (unreplicated, no code).

---

## Open questions

1. Does GBrain implement any of these explicitly (PPR recall, bi-temporal edges, write routing), or is it a flat markdown corpus + search? Needs a repo read — this dimension did not inspect GBrain.
2. No published head-to-head of MemOS vs Mem0 vs GBrain on the *same* agent-task benchmark; the OmniMemEval and Mem0 numbers come from each vendor's own harness.
3. Nobody has published the fly-hash-index + PPR-recall + bi-temporal-arbitration composition. Is the sparse expansive index actually better than dense embeddings at the 220K-page scale Tan operates at?
4. Does CLS-style parametric consolidation (SFT write-back) work for *company* knowledge, where facts change weekly? Every result so far is on static QA corpora.
5. Titans/HOPE code release status as of Sept 2026 is unconfirmed — the only public reimplementation partially failed to reproduce.
6. ZenBrain's dramatic claims (all 9 wins, p=6.2e-31, 1/106th token cost) are single-author with no code. Unverified; low confidence.

---

## Sources

- Ramsauer et al., "Hopfield Networks is All You Need" — https://arxiv.org/abs/2008.02217 · code https://github.com/ml-jku/hopfield-layers
- Dehghani, "Memory as an Energy Landscape — Hopfield" (2026-09-02) — https://arxiv.org/abs/2609.02195
- Bricken & Pehlevan, "Attention Approximates Sparse Distributed Memory," NeurIPS 2021 — https://arxiv.org/abs/2111.05498 · code https://github.com/TrentBrick/attention-approximates-sdm
- Bricken et al., "Sparse Distributed Memory is a Continual Learner," ICLR 2023 — https://arxiv.org/pdf/2303.11934 · code https://github.com/TrentBrick/SDMContinualLearner
- Dasgupta et al. lineage / "Bio-Inspired Hashing for Unsupervised Similarity Search" — https://arxiv.org/abs/2001.04907
- Gutiérrez et al., HippoRAG, NeurIPS 2024 — https://arxiv.org/abs/2405.14831
- Gutiérrez et al., HippoRAG 2 / "From RAG to Memory," ICML 2025 — https://arxiv.org/abs/2502.14802 · code https://github.com/OSU-NLP-Group/HippoRAG (MIT)
- Li et al., "Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation" — https://arxiv.org/html/2608.22215
- Kerestecioglu et al. (Microsoft), "Human-Inspired Memory Architecture for LLM Agents" — https://arxiv.org/html/2605.08538v1
- Sun et al., "ComMem: Complementary Memory Systems for Test-Time Adaptation" — https://arxiv.org/pdf/2606.28719
- Lin, Snell, Wang, Packer, Wooders, Stoica, Gonzalez, "Sleep-time Compute" (Letta) — https://www.letta.com/blog/sleep-time-compute/
- Behrouz, Zhong, Mirrokni, "Titans: Learning to Memorize at Test Time," NeurIPS 2025 — https://arxiv.org/pdf/2501.00663
- Behrouz & Mirrokni, "Introducing Nested Learning" (HOPE), Google Research, 2025-11-07 — https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/
- Di Nepi, Siciliano, Silvestri, "Titans Revisited" — https://arxiv.org/abs/2510.09551
- Sumers, Yao, Narasimhan, Griffiths, "Cognitive Architectures for Language Agents" (CoALA), TMLR — https://arxiv.org/abs/2309.02427
- Li et al., "MemOS: A Memory OS for AI System" — https://arxiv.org/abs/2507.03724 · earlier MAG variant https://arxiv.org/abs/2505.22101 · code https://github.com/MemTensor/MemOS
- MemOS benchmark harness — https://github.com/MemTensor/OmniMemEval
- Awesome-AI-Memory (542 papers / 111 projects) — https://github.com/IAAR-Shanghai/Awesome-AI-Memory
- Mem0, "State of AI Agent Memory 2026" (2026-09-09) — https://mem0.ai/blog/state-of-ai-agent-memory-2026
- Ji, Li, Hooi, "Memory is Reconstructed, Not Retrieved" (MRAgent) — https://arxiv.org/html/2606.06036v1 · code https://github.com/Ji-shuo/MRAgent
- Ji et al., "RippleMem" — https://arxiv.org/abs/2608.13334
- Bering, "ZenBrain: A Neuroscience-Inspired 7-Layer Memory Architecture" — https://arxiv.org/abs/2604.23878
- Yu et al., MemoryAgentBench / "Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions," ICLR 2026 — https://huggingface.co/papers/2507.05257 · code https://github.com/HUST-AI-HYZ/MemoryAgentBench
- Reddy & Challaram, "Reliable Post-Retrieval Assembly for Agent Memory" / "Don't Ask the LLM to Track Freshness" — https://arxiv.org/abs/2606.01435 · code https://github.com/cvikasreddy/memory-conflict-resolution
- Wang, "TOKI: A Bitemporal Operator Algebra for Contradiction Resolution" — https://arxiv.org/pdf/2606.06240 · code https://github.com/ZenAlexa/toki-bitemporal-memory
- Rasmussen et al., "Zep: A Temporal Knowledge Graph Architecture for Agent Memory" — https://arxiv.org/abs/2501.13956
- Ding, Nannapaneni, Liu, Zhang, "Always-On Agents: A Survey of Persistent Memory, State, and Governance" — https://arxiv.org/html/2606.30306v1
- Jiang et al., "Demystifying Agent Skills: Why They Work—Until They Don't" — https://arxiv.org/html/2608.14036v1
- "Skill-DisCo: Distilling and Compiling Agent Traces into Reusable Procedural Skills" — https://arxiv.org/abs/2606.26669
- "SkillLens: Adaptive Multi-Granularity Skill Reuse" — https://arxiv.org/pdf/2605.08386
- "Managing Procedural Memory in LLM Agents" (EvoSkill) — https://arxiv.org/html/2606.23127v1
- ICLR 2026 Workshop "MemAgents: Memory for LLM-Based Agentic Systems" — https://openreview.net/pdf?id=U51WxL382H (proposal page; blocked by browser verification, cited from search snippet — low confidence)

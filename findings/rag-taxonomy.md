# rag-taxonomy — Is a "company brain" just RAG?

*Worker report, 2026-09-10. Dimension: RAG → memory → brain taxonomy, and exactly where Tan's claims sit.*

## TL;DR

1. **Tan is technically right and rhetorically slippery.** Retrieval genuinely *is* the primitive; every one of his seven "hard parts" — write-side curation, enrichment/linking, hot-vs-cold promotion, contradiction arbitration, provenance, pruning, skillification — is a **write-path or lifecycle** concern that the RAG literature (2020–2024) barely touched and the **agent-memory** literature (2023–2026) has been formalising for two years. A company brain is not "just RAG"; it is RAG plus a memory lifecycle. But it is also not novel: by mid-2026 every single one of his requirements has a named academic mechanism and at least one shipping open-source implementation.
2. **The clean dividing line is read-side vs write-side agency.** Naive → Advanced → Graph → Agentic RAG all make *retrieval* smarter over a corpus someone else curated. Agent-memory systems (Mem0, Zep/Graphiti, A-MEM, MemOS, Letta) make the *corpus itself* a managed, mutable, provenanced object. Tan's talk is an argument for moving investment from the first axis to the second.
3. **The most under-cited layer in his talk is procedural memory.** "Skillify it" is the SKILL.md / Agent Skills ecosystem, an open standard since Dec 2025 with 40+ supporting tools ([survey: arXiv 2602.12430](https://arxiv.org/abs/2602.12430)) — and his own failure mode ("a bad skill file encodes a bad process forever") is empirically real: that survey finds **26.1% of community-contributed skills contain vulnerabilities**.
4. **GBrain implements the full list, verifiably.** [github.com/garrytan/gbrain](https://github.com/garrytan/gbrain) (MIT, created 2026-04-05, **29,763 stars / 4,441 forks** as of 2026-09-10) ships auto-linking on every write, source-tier + salience scoring (hot/cold), `gbrain eval suspected-contradictions` wired into a nightly "dream cycle", citation-fixing crons, and a 50+ skillpack with a `RESOLVER.md` routing table. It is a working existence proof of the talk, not a slideware claim.
5. **Be skeptical of the *benefit* claim, not the architecture claim.** [MemDelta (arXiv 2606.29914)](https://arxiv.org/abs/2606.29914) finds simple RAG baselines frequently match or beat structured memory systems once confounds are controlled; [Convomem (arXiv 2511.10523)](https://arxiv.org/abs/2511.10523) finds naive full-context beats RAG-based memory for the first ~150 conversations. Curation is a *scaling* answer, not a free lunch — it only pays once the corpus exceeds the context window and lives long enough to go stale.

---

## Tan's seven requirements (the thing to score systems against)

From the transcript at 13:00–15:03 (`sources/transcript_eBUyTS7SzV4.txt`):

| # | Requirement | Tan's words |
|---|---|---|
| R1 | Write-side curation | "what gets written down in the first place" |
| R2 | Enrichment & linking | "how it gets enriched and linked" |
| R3 | Hot vs cold tiering | "what gets promoted to hot memory versus filed as cold reference" |
| R4 | Contradiction arbitration | "who arbitrates when two facts disagree" |
| R5 | Provenance | "provenance on every fact" |
| R6 | Librarian / pruning | "a librarian, human plus agent, whose actual job is pruning" |
| R7 | Procedural memory | "skillify it… if you have to ask for something twice, you failed" |

Note that R1–R3 and R6 are *not retrieval problems at all*. They are database lifecycle problems. That is the real content of the "Postgres is just B-trees" analogy.

---

## The taxonomy: seven layers

### L0 — Retrieval primitives
BM25, dense bi-encoders, HNSW/pgvector. Solves: *approximate lookup at scale.* Covers **none** of R1–R7. This is the layer Tan concedes is "easy".

### L1 — Naive RAG
Index → retrieve → generate. Canonical framing: [Gao et al., "Retrieval-Augmented Generation for LLMs: A Survey", arXiv 2312.10997](https://arxiv.org/abs/2312.10997), which defines the **Naive / Advanced / Modular** progression that everything since has inherited. Solves: *grounding a frozen model in an external corpus.* Covers: nothing on Tan's list. This is exactly the "garbage dump with great search" he warns about, because the corpus is whatever you dumped in.

### L2 — Advanced RAG (pre- and post-retrieval optimisation)
Query rewriting/expansion ([HyDE, arXiv 2212.10496](https://arxiv.org/abs/2212.10496)), hierarchical summarisation ([RAPTOR, arXiv 2401.18059](https://arxiv.org/abs/2401.18059)), hybrid dense+lexical fusion and cross-encoder reranking, and chunk-level context injection ([Anthropic, *Contextual Retrieval*, 2024](https://www.anthropic.com/engineering/contextual-retrieval): contextual embeddings cut top-20 retrieval failure 5.7%→3.7%; +BM25 →2.9%; +reranking →1.9%, a **67% reduction**). Solves: *chunks lose their context; embeddings miss exact names.* Covers **R2 partially** (enrichment, but only as a preprocessing step — nothing is linked, and nothing is ever revised).

### L3 — Graph / structured RAG
[Microsoft GraphRAG (arXiv 2404.16130](https://arxiv.org/abs/2404.16130), [repo](https://github.com/microsoft/graphrag), MIT, 35,912★) builds an entity graph plus pre-generated community summaries so *global* "what are the themes" questions become answerable. [LightRAG (arXiv 2410.05779](https://arxiv.org/abs/2410.05779), [repo](https://github.com/HKUDS/LightRAG), MIT, 39,517★) makes the same idea cheap and incrementally updatable. [HippoRAG / HippoRAG 2 (arXiv 2502.14802, "From RAG to Memory")](https://arxiv.org/abs/2502.14802) uses Personalized PageRank over an LLM-built KG as a hippocampal index and reports **+7% on associative-memory tasks** over SOTA embeddings — and its title is the field's own admission that this layer is the bridge from retrieval to memory.
Covers **R2 strongly** (this *is* enrichment and linking, done automatically), R3 weakly (community summaries are a crude hot tier). Still no write policy, no provenance discipline, no arbitration.

### L4 — Agentic RAG
[Singh et al., "Agentic RAG: A Survey", arXiv 2501.09136](https://arxiv.org/abs/2501.09136) (v4, 2026-04-01) gives the canonical taxonomy: single-agent router, multi-agent specialised retrievers, hierarchical agents, corrective RAG ([CRAG, arXiv 2401.15884](https://arxiv.org/abs/2401.15884)), adaptive RAG, plus self-critique ([Self-RAG, arXiv 2310.11511](https://arxiv.org/abs/2310.11511)). Solves: *one retrieval pass is not enough; decide whether/what/how many times to retrieve.* Covers **R4 partially** — a critic that grades and re-queries is arbitration *at read time only*, and it does not fix the store. Note this is precisely Tan's "librarian" metaphor at 17:41 ("the librarian that picks the context"), which is the weaker half of his own thesis.

### L5 — Agent memory systems (the write path)
This is where Tan's list actually gets implemented.

- **Extraction + update policy (R1, R4).** [Mem0 (arXiv 2504.19413](https://arxiv.org/abs/2504.19413), [repo](https://github.com/mem0ai/mem0), Apache-2.0, 65,004★) splits memory into an *extraction* phase and an *update* phase driven by explicit **ADD / UPDATE / DELETE / NOOP** tool calls — a literal write-side curation policy — reporting +26% over OpenAI's built-in memory on LOCOMO with 91% lower p95 latency and >90% token savings.
- **Temporal arbitration + provenance (R4, R5).** [Zep (arXiv 2501.13956)](https://arxiv.org/abs/2501.13956) / [Graphiti](https://github.com/getzep/graphiti) (Apache-2.0, 30,734★) build a **bi-temporal** knowledge graph: every fact records when it became true, when it stopped being true, and where it came from; a contradicting new fact *invalidates* the old edge rather than sitting beside it. This is the single most direct implementation of "who arbitrates when two facts disagree."
- **Self-organising linking (R2).** [A-MEM (arXiv 2502.12110](https://arxiv.org/abs/2502.12110), [repo](https://github.com/agiresearch/A-mem), MIT) is explicitly Zettelkasten-shaped: each new note gets keywords/tags, is linked to relevant historical notes, and **triggers updates to the attributes of existing memories**. That last clause is memory *evolution*, not just insertion.
- **Tiering and lifecycle (R3, R6).** [MemOS (arXiv 2505.22101](https://arxiv.org/abs/2505.22101), [repo](https://github.com/MemTensor/MemOS), Apache-2.0, 11,245★) treats memory as an OS resource across **parametric / activation / plaintext** types with a `MemCube` abstraction supporting tracking, fusion and migration between tiers — hot/cold promotion as a first-class scheduling problem. Its stated motivation is that "RAG… lacks lifecycle management."
- **Background consolidation (R6).** [Letta, *Sleep-time Compute* (arXiv 2504.13171)](https://arxiv.org/abs/2504.13171) runs a second agent over shared memory while the main agent idles, rewriting and compressing it; ~**5× less test-time compute** for equal accuracy, 2.5× lower amortised cost. Lineage: [MemGPT (arXiv 2310.08560)](https://arxiv.org/abs/2310.08560), [Letta repo](https://github.com/letta-ai/letta) (Apache-2.0, 24,675★). Precedent for salience-scored hot memory goes back to [Generative Agents (arXiv 2304.03442)](https://arxiv.org/abs/2304.03442), whose recency×importance×relevance retrieval score plus periodic *reflection* is the original R3+R6 mechanism.
- **Provenance as the organising principle (R5, R6).** [Eywa: "Provenance-Grounded Long-Term Memory for AI Agents" (arXiv 2605.30771](https://arxiv.org/abs/2605.30771), 2026-06-01) attaches origin/time/derivation to each *fact* and uses the provenance chain both to arbitrate contradictions and to target pruning at weakly-sourced, stale entries — a one-paper restatement of Tan's 14:50 paragraph.
- **Surveys of the layer.** [*A Survey of Agent Memory in the Second Half* (arXiv 2602.06052)](https://arxiv.org/abs/2602.06052), 60 authors, revised 2026-08-04, organises memory along substrate × cognitive mechanism (sensory/working/**episodic/semantic/procedural**) × subject, and explicitly covers "reinforcement-learned context curation, experience consolidation" and "an emerging ecosystem of portable, shareable agent skills." [*From Storage to Experience* (arXiv 2605.06716)](https://arxiv.org/abs/2605.06716) formalises three evolutionary stages — **Storage (trajectory preservation) → Reflection (trajectory refinement) → Experience (trajectory abstraction)**. Tan's "skillify it" is exactly the Storage→Experience jump.
- **Conflict theory.** [*Knowledge Conflicts for LLMs: A Survey* (arXiv 2403.08319](https://arxiv.org/abs/2403.08319), EMNLP 2024) names the three conflict types — **context-memory, inter-context, intra-memory**. Tan's "two facts disagree" is inter-context conflict; his "stale fact surfaced with total confidence" is its outdated-information subtype.

### L6 — "Brain" / second-brain systems
Where memory becomes an owned, org-scale, markdown-native asset with a skills layer on top.

- **GBrain** ([repo](https://github.com/garrytan/gbrain), MIT, TypeScript, created 2026-04-05, 29,763★/4,441 forks, last push 2026-09-08). Git markdown repo is the system of record; PGLite or Postgres+pgvector is the index. Per the README: hybrid vector+BM25+RRF+**source-tier boost**+intent-aware rewriting with Voyage `rerank-2.5` (L2 ✓); **auto-link on every `put_page`** producing typed edges with zero LLM calls, claimed **+31.4 P@5 over vector-only RAG** (L3 ✓, R2 ✓); `gbrain think` returning cited synthesis **plus gap analysis** flagging stale pages, uncited claims and contradictions (R5 ✓); **`gbrain eval suspected-contradictions`** wired into a nightly dream cycle (R4 ✓); crons that "dedup people pages, fix citations, score salience, find contradictions" (R3/R6 ✓); ambient memory writeback where transient facts expire on their own (R1/R6 ✓); a `MEMORY_VERBS v1` protocol with a literal `forget` verb; 50+ skills routed by `skills/RESOLVER.md`, plus optional **Memorable** procedural memory that turns finished sessions into replayable procedures (R7 ✓). Self-reported LongMemEval-S strict `recall_all@5` = **95.53%** (default path, v0.48.4.0, 2026-09-06). Note the README says **155,795 pages**, while the talk says ~220,000 — the talk number is either later or looser.
- **The category is a YC RFS.** "Company Brain" is a Y Combinator **Summer 2026** Request for Startups authored by **Tom Blomfield**, asking for a system that ingests everything a company produces, indexes "all sources… with metadata: author, date, access level, related entities", answers with source citations, and "detect[s] contradictions and flag[s] for resolution" ([modelence mirror](https://modelence.com/yc-rfs-summer-2026/company-brain); the entry is no longer on the [live RFS page](https://www.ycombinator.com/rfs), which now shows Fall 2026). So R4 and R5 are in the funding brief, not just the talk.
- **Adjacent OSS:** [Cognee](https://github.com/topoteretes/cognee) (Apache-2.0, 30,610★) — hybrid KG+vector+relational memory control plane; [basic-memory](https://github.com/basicmachines-co/basic-memory) (AGPL-3.0, 3,905★) — markdown-file-as-memory over MCP.
- **R7 as an ecosystem.** Anthropic's Agent Skills / `SKILL.md` shipped Oct 2025 and became an open standard in Dec 2025 with 40+ supporting tools; see [arXiv 2602.12430](https://arxiv.org/abs/2602.12430) (Xu & Yan, v4 2026-06-02) for architecture/acquisition/security and a proposed *Skill Trust and Lifecycle Governance Framework*, and [arXiv 2606.23127](https://arxiv.org/abs/2606.23127) (Belikova et al., 2026-06-23) on procedural-memory control/adaptation/evaluation. Academic ancestor: [Voyager (arXiv 2305.16291)](https://arxiv.org/abs/2305.16291), whose growing skill library is the original "skillify it".

---

## Coverage matrix

| Layer | R1 write | R2 link | R3 hot/cold | R4 arbitrate | R5 provenance | R6 prune | R7 skills |
|---|---|---|---|---|---|---|---|
| L1 Naive RAG | – | – | – | – | – | – | – |
| L2 Advanced RAG | – | ~ | – | – | ~ (citations) | – | – |
| L3 GraphRAG/LightRAG/HippoRAG | – | ✓✓ | ~ | – | ~ | – | – |
| L4 Agentic RAG (CRAG/Self-RAG) | – | – | – | ~ (read-time) | ~ | – | – |
| L5 Memory (Mem0/Zep/A-MEM/MemOS/Letta/Eywa) | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ~ |
| L6 Brain (GBrain, Company-Brain RFS, Skills) | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ | ✓✓ |

Only L6 closes R7, and only because it bolts the Skills ecosystem onto L5. That is the honest answer to "what is a brain that memory isn't": **a memory system that also stores how the work is done, not only what is true.**

---

## Relevance to the company-brain / RAG / fruit-fly question

**(a) Does it relate to RAG?** Yes — it *contains* RAG as its L0–L3 substrate and is measured on retrieval metrics (GBrain publishes LongMemEval numbers). The honest formulation: *company brain = RAG (read path) + agent memory (write path + lifecycle) + skills (procedural memory) + an org-scoped permission model.* Tan's "just B-trees" analogy is apt but flatters him: Postgres added transactions, a query planner and a WAL on top of B-trees, and the L5 literature is that same layer being built in public right now — mostly *before* his talk, by other people.

**(c) Where a fruit-fly angle plugs in.** Two of the layers above are already neuroscience-borrowed and are the natural seams for the other workers' fly-brain question: (i) **indexing** — the fly olfactory circuit's sparse random-projection hash (FlyHash) is a candidate L0/L2 primitive, an alternative to HNSW; (ii) **memory architecture** — HippoRAG's hippocampal indexing (L3/L5) is the existing template for "borrow a real brain's memory circuit", and the mushroom body's dopaminergic *forgetting* and valence-tagging is the obvious biological analogue for R3 (salience) and R6 (pruning), which are the two least-solved requirements. I did not verify any specific 2026 fly paper — that is another worker's dimension.

## Open questions

1. Does GBrain's claimed **+31.4 P@5 lift from the graph over vector-only** hold on an external benchmark, or only on its own corpus? Only self-reported in the README.
2. Talk says ~220,000 pages; README says 155,795. Which is current, and does page count correlate with answer quality or just with dump size?
3. Is there *any* published evidence that contradiction arbitration improves downstream task accuracy, as opposed to improving store hygiene metrics? I found mechanisms (Zep, Eywa, GBrain) but no clean ablation.
4. MemDelta's confound critique — does it invalidate Mem0/Zep/Graphiti's headline numbers outright, or only the margins? I could not extract its tables from the PDF.
5. Who is the human librarian in practice at a 200-person company, and what is the labour cost? Tan asserts the role; no source quantifies it.
6. Skill rot: 26.1% of community skills carry vulnerabilities — is there any published measurement of *stale/wrong* (as opposed to malicious) skills, which is Tan's actual failure mode?

## Sources

- Transcript: `sources/transcript_eBUyTS7SzV4.txt` (13:00–15:03, 17:41)
- RAG surveys: https://arxiv.org/abs/2312.10997 · https://arxiv.org/abs/2501.09136 · https://arxiv.org/abs/2506.00054 · https://arxiv.org/abs/2507.13334
- Advanced RAG: https://arxiv.org/abs/2212.10496 · https://arxiv.org/abs/2401.18059 · https://arxiv.org/abs/2310.11511 · https://arxiv.org/abs/2401.15884 · https://www.anthropic.com/engineering/contextual-retrieval
- Graph RAG: https://arxiv.org/abs/2404.16130 · https://github.com/microsoft/graphrag · https://arxiv.org/abs/2410.05779 · https://github.com/HKUDS/LightRAG · https://arxiv.org/abs/2502.14802 · https://github.com/OSU-NLP-Group/HippoRAG
- Memory: https://arxiv.org/abs/2504.19413 · https://github.com/mem0ai/mem0 · https://arxiv.org/abs/2501.13956 · https://github.com/getzep/graphiti · https://arxiv.org/abs/2502.12110 · https://arxiv.org/abs/2505.22101 · https://github.com/MemTensor/MemOS · https://arxiv.org/abs/2504.13171 · https://arxiv.org/abs/2310.08560 · https://arxiv.org/abs/2304.03442 · https://arxiv.org/abs/2605.30771
- Memory surveys: https://arxiv.org/abs/2602.06052 · https://arxiv.org/abs/2605.06716 · https://arxiv.org/abs/2403.08319
- Skeptical: https://arxiv.org/abs/2606.29914 · https://arxiv.org/abs/2511.10523 · https://arxiv.org/abs/2601.05504 · https://arxiv.org/abs/2503.03704
- Skills: https://arxiv.org/abs/2602.12430 · https://arxiv.org/abs/2606.23127 · https://arxiv.org/abs/2305.16291
- Brain layer: https://github.com/garrytan/gbrain · https://github.com/garrytan/gbrain-evals · https://modelence.com/yc-rfs-summer-2026/company-brain · https://www.ycombinator.com/rfs · https://github.com/topoteretes/cognee · https://github.com/basicmachines-co/basic-memory
- Repo metrics retrieved via `gh api repos/<owner>/<repo>` on 2026-09-10.

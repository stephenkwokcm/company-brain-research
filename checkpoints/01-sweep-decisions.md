# Checkpoint 01 — after sweep (2026-09-10)

## Done
- Workflow 1 (wf_936828bf-0c5): 14 researchers + 1 critic, all succeeded. Reports: findings/*.md (15 files). Raw structured returns: checkpoints/01-sweep-results.json.

## Orchestrator decisions / key insights so far
### (a) Is the company brain RAG?
- DECISION: Answer = "RAG on the read path, plus a write-side lifecycle (curation, provenance, hot/cold tiers, contradiction arbitration) plus procedural memory (skills)." Tan concedes this on stage (12:57-13:27) and in his repo (docs/ethos/ORIGIN.md: "none of those are novel ideas; the contribution is shipping all of them together").
- The precise dividing line is read-side vs write-side agency (findings/rag-taxonomy.md). The one requirement plain memory systems do not cover is procedural memory = SKILL.md files.
- End-to-end benefit over a tuned BM25+vector baseline is UNPROVEN. GBrain's README holds both "+31.4 P@5 over vector-only" (240-page Opus-generated corpus) and "hybrid layer roughly neutral" (LongMemEval-S, pure vector 93.8%). Must be stated as one sentence in the synthesis (critic C1).
- Strongest empirical support for the "librarian" thesis: bounded self-managed memory scores 15 pts worse than full context on LongMemEval knowledge-update questions and more capacity recovers nothing (findings/memory-hygiene.md); MemoryAgentBench FactConsolidation: deterministic code beats all 22 memory systems on arbitration (findings/neuro-inspired-rag.md) — needs verification.

### (b) Fruit-fly brain work
- Tan's talk contains zero neuroscience; "brain" is a library metaphor. The fly link is the user's own synthesis — say so.
- Likely referents (ranked): 1) MaleCNS complete male Drosophila CNS connectome, Janelia+Google+MRC LMB, Cell, Aug/Sep 2026 (166,700 neurons) + the DOOM/Mario-on-a-fly-brain meme wave; 2) BANC brain-and-cord connectome, Nature, June 2026; 3) Eon Systems embodied fly, Mar 2026. Algorithmic lineage: FlyHash (Science 2017), fly Bloom filter (PNAS 2018), FlyPrompt (ICLR 2026), Spi-Fly (Aug 2026). Date of MaleCNS paper disputed (critic C4) — verify.
- DECISION on where the bridge is real: (i) write-side: FlyHash/fly-Bloom-filter novelty gate + dedup at ingest (cheapest place to control quality; missing in GBrain); (ii) lifecycle: mushroom-body consolidation model = readout-gated hot→cold promotion + separately-parameterised forgetting daemon with suppression window; (iii) routing: sparse-expansion router for the RESOLVER/skill layer (FlyPrompt); (iv) process: connectome projects as a worked example of curation (CAVE versioning, per-fact confidence, proofreading = arbitration, VFB MCP server).
- DECISION on where it is NOT real: FlyHash as the semantic index loses to dense embeddings (H3D: 0.13 vs 0.34 MAP) and to HNSW at scale; connectome topology transfer is contradicted by the degree-preserving-null study (arXiv 2604.04033). No published work combines connectome/MB ideas with RAG — unclaimed ground, but also unproven.

### (c) Projects
- GBrain ecosystem (gbrain 29.8K★, gbrain-evals, gstack, COG-second-brain, hermes-memory-installer...), memory systems (Letta MemFS, Cognee, Zep/Graphiti, Mem0, MemOS 2.0), YC "Company Brain" RFS companies (Hyper, Memory Store, ...), agno-agi/scout as counter-thesis, fly side nearly empty (membrain 0★, FlyGCL). Star counts are not a quality signal.

## Open (from completeness critic, findings/completeness-critic.md)
- Verify 10 claims (C1 benchmark reconciliation, MaleCNS date, BANC counts, "94 companies", page counts, librarian-in-code, RFS text, Ramp/DoorDash case studies, MemoryAgentBench result, H3D FlyHash numbers) + sanity-check OpenClaw/Hermes star counts.
- Gaps: bi-temporal DB prior art; SPLADE/BM42/binary-quant vs FlyHash; sizing/cost arithmetic; enterprise incumbents; librarian from library science; governance/ACL/GDPR; crux-experiment protocol.
- Design: no buildable spec for question (b) yet.

## Next
- Workflow 2: verify (≈14 agents) ∥ gap-fill (7) → design panel (5 angles) → judges (3) → synthesis draft. Then orchestrator writes SYNTHESIS.md.

## Workflow 2 launched
- Run ID wf_9ab6a640-268. Script copy: checkpoints/workflows/02-verify-design.js
- Transcript dir: ~/.claude/projects/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/subagents/workflows/wf_9ab6a640-268
- Outputs expected: findings/v01..v11-*.md (verification), findings/g01..g07-*.md (gaps), findings/d1..d5-*.md (designs), findings/j1..j3-*.md (judges), SYNTHESIS-draft.md

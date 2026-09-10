# Checkpoint 00 — plan (2026-09-10)

## Done
- Created folder. Pulled transcript of YouTube eBUyTS7SzV4 (Garry Tan, "Every company should have a Brain", AI Engineer, 2026-07-16, 21 min).
  Files: sources/transcript_eBUyTS7SzV4.{txt,json}, sources/video_meta.json

## Talk summary (orchestrator read the full transcript)
- Claim: leverage is not the model, it is "how you wire the work" (Tan claims ~400X personal output, floor 8X).
- Org-as-markdown mapping: skill file = employee; resolver table = org chart; filing rules = internal process; trigger evals = performance reviews.
- Two places computation happens: latent space (LLM: taste, judgment, vague intent) vs deterministic space (code). Most agent bugs = computation on the wrong side. Example: seating 800 people — state must live outside the context window.
- Working memory: humans 7±2 items; agent ~1M tokens (~3 Harry Potter books). Company = a library. "Who decides which three books are open" = context engineering.
- Company brain = library + librarian. On "this is just RAG" (13:00): retrieval is the primitive (Postgres is "just B-trees"); the product is what gets written down, enrichment/linking, hot memory vs cold reference, arbitration when facts disagree. "Retrieval is easy. Being worth retrieving from is the product."
- His project: GBrain (MIT open source, "Postgres for agents", works with any harness, "loves OpenClaw / Hermes agent"); his own has ~220,000 pages, mostly agent-written.
- Failure modes: uncurated brain = "garbage dump with great search"; stale facts surfaced with confidence; bad skill file encodes bad process forever. Fix = memory + hygiene: provenance per fact, contradiction checks, librarian (human+agent) whose job is pruning.
- Discipline: "never do one-off work" → "skillify it" (blog post on X). "If you have to ask twice, you failed." "Model quality is rented; your brain you own."
- Anecdote: friend built 80,000-markdown-file brain for his son's rare epilepsy.

## Open questions to research
1. Exactly how "company brain" differs from RAG (taxonomy; where GBrain sits vs mem0/Letta/Zep/Cognee/HippoRAG etc.).
2. What "recently published fruit fly brain work" most plausibly refers to (as of Sep 2026): FlyWire connectome, whole-brain simulations, FlyHash/fly-inspired LSH, mushroom-body memory models, or a 2026 paper. Identify all candidates and rank.
3. Concrete ways to combine the two (index/retrieval, memory architecture, routing/resolver, hygiene/forgetting).
4. Survey of projects built on these ideas.
5. Skeptical check of the talk's numbers and of "brain vs RAG" framing.

## Next
- Workflow 1: 14-dimension research sweep (Opus 5 agents), each writes findings/<key>.md and returns a structured summary; plus a completeness critic.

## Workflow 1 launched
- Run ID wf_936828bf-0c5 (Claude Code Workflow tool). Script copy: checkpoints/workflows/01-sweep.js
- Transcript dir: ~/.claude/projects/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/subagents/workflows/wf_936828bf-0c5 (journal.jsonl has each agent's raw return)

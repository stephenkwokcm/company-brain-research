# Company Brain × Fruit-Fly Brain research

Research folder for the question: does Garry Tan's "company brain" (YouTube eBUyTS7SzV4) relate to RAG,
and can it be combined with the recently published fruit-fly brain work? Which projects already build on these ideas?

## Layout
- `sources/`      raw inputs (video transcript + metadata, fetched papers/repos notes)
- `findings/`     one markdown report per research dimension, written by Opus 5 sub-agents (with source URLs)
- `checkpoints/`  numbered orchestrator checkpoints. **Start with the highest-numbered checkpoint** to resume.
- `SYNTHESIS.md`  final answer (written last)

## How to resume
1. Read the latest `checkpoints/NN-*.md` — it lists what is done, what is open, and the next planned step.
2. Read `findings/*.md` for detail. Every claim there should carry a URL.
3. Continue from the "Next" section of the checkpoint.

Orchestrator: Claude Fable 5.1. Workers: Claude Opus 5. Started 2026-09-10.

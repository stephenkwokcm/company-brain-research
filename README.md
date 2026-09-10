# Company Brain × Fruit-Fly Brain research

Does Garry Tan's "company brain" (["Every company should have a Brain"](https://www.youtube.com/watch?v=eBUyTS7SzV4), AI Engineer, 2026-07-16)
relate to RAG? Can it be combined with the recently published fruit-fly brain work (the male Drosophila CNS connectome, Cell, 3 Sep 2026; the
FlyHash / fly Bloom filter lineage)? Which projects already build on these ideas?

**Start here: [`SYNTHESIS.md`](SYNTHESIS.md)** — the decision document. Then [`ERRATA.md`](ERRATA.md) before citing any individual report.

## Layout
- `SYNTHESIS.md`       final answer (orchestrator-reviewed). `SYNTHESIS-draft.md` is the agent draft it was built from.
- `ERRATA.md`          22 corrections to the sweep reports established by the verification round.
- `sources/`           talk transcript (YouTube auto-captions) + metadata.
- `findings/`          44 reports written by Claude Opus 5 sub-agents, every claim with a URL:
  - 14 sweep dimensions + `completeness-critic.md`
  - `v01`–`v11` verifications of the critic's load-bearing claims
  - `g01`–`g07` gap fills (bitemporal DBs, sizing/cost, enterprise incumbents, librarian spec, governance, crux experiment, neuro-mechanism inventory)
  - `d1`–`d5` design proposals (two of them ran live experiments in pgvector / on GBrain's own skill fixtures)
  - `j1`–`j3` judge scorecards (RAG engineer, computational neuroscientist, YC founder)
- `checkpoints/`       numbered orchestrator checkpoints (read the highest number to resume), raw structured agent returns (`*-results.json`),
                       and `workflows/` — the exact Claude Code Workflow scripts that produced everything.

## How this was produced
Orchestrator: Claude Fable 5.1 (decisions, checkpoints, final synthesis). Workers: 45 Claude Opus 5 agents across two workflows
(sweep → critic; verify ∥ gap-fill → design panel → judges → draft). All on 2026-09-10. Total ≈ 9M worker tokens.

## How to resume
1. Read the latest `checkpoints/NN-*.md`.
2. Read `SYNTHESIS.md` §7 for the experiments nobody has run yet; `findings/g06-crux-experiment.md` has the runnable protocol.
3. Re-run or extend with `checkpoints/workflows/*.js` (Claude Code `Workflow` tool; resumable by run ID within the original session only).

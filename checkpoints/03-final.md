# Checkpoint 03 — final (2026-09-10)

## Done
- Workflow 2 completed 30/30 after a resume (judges j1-j3 + synthesis draft had failed on a transient API outage).
- Judge leaderboard (mean of 3, /50): d4 index-adversary 38.3 (KILL fly backend / BUILD binary quantization), d2 lifecycle 38.3 (BUILD x3),
  d1 write-gate 37.3 (PILOT x3), d3 router 37.0 (BUILD boring router / KILL fly gate), d5 curation-process 31.7 (PILOT/PILOT/DEFER).
  Orchestrator's verdict table in checkpoint 02 stands unchanged.
- SYNTHESIS.md written (draft accepted with an orchestrator preface). README rewritten. experiments/ holds the agents' real scripts + raw results.
- Verified before finalising: pgvector/pgvector:pg17 image present, d4/d3/pgv scripts and JSON results exist in the session scratchpad;
  the user's hk-law-rag and hk-gov-data-rag really use Neo4j + BGE-M3 (the §7.2 MVP is written against that stack).
- Public repo: https://github.com/stephenkwokcm/company-brain-research

## Open (nobody has run these; all cheap)
1. Tier-0 crux: tuned hybrid vs GBrain default vs reranker-off on MemConflict's 804 static+conditional questions (~$30, one afternoon). findings/g06-crux-experiment.md
2. As-of-date filter on hk-law-rag: 100 historically anchored questions, baseline vs filtered (published effect 35.4% -> 81.4%, arXiv:2605.23497).
3. K5 (d2): AUROC of pages.last_retrieved_at predicting "cited in a correct answer" on 30 days of history; < 0.60 kills the promotion redesign.
4. K2 (d1): offline recurrence-after-dormancy AUROC, fly-bank vs max-cosine / binary_quantize / SimHash / SAGE, G in {7,14,25} days (4 days, ~$0).
5. Template-blind paraphrase variant of gbrain-evals' 145 relational questions (issue #24).
6. Coverage holes: Coda Brain/Grammarly unassessed (403); 2026 "company brain" entrants (Hyper, Memory Store, Almanac, Hyperspell, Savant, Within) carried over unverified;
   Tom Blomfield's X posts on the RFS not fetched (search budget exhausted).

## How to continue
- Read SYNTHESIS.md §7, then findings/g06-crux-experiment.md for the exact protocol; experiments/ for the scripts.
- To extend with new agents: reuse checkpoints/workflows/02-verify-design.js as a template (PREAMBLE + schema pattern).

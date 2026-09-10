# Experiment scripts and raw results (run 2026-09-10 on an Apple Silicon Mac)

These are the scripts the design/gap agents actually ran, copied from the session scratchpad so the numbers in
`findings/d4-index-adversary.md`, `findings/d3-router.md` and `findings/g02-sizing-cost.md` can be re-derived.

- `pgv_*`, `d4_pgv.sql`, `d4_lat.sql`, `d4_latency.py` — pgvector 0.8.6 / PostgreSQL 17 (Docker image `pgvector/pgvector:pg17`):
  HNSW index size and latency at 100K/250K rows, 1024-d; FlyHash `sparsevec(20480)` columns vs `bit(1024)` binary quantization.
- `d4_chunk.py`, `d4_embed*.py`, `d4_fly.py`, `d4_biohash.py`, `d4_eval.py`, `d4_dedup.py` + `d4_*.json` — BGE-M3 (`BAAI/bge-m3`, 1024-d, local)
  embeddings of 3,187 chunks; FlyHash / BioHash / binary quantization / int8 / halfvec recall@10 with and without rescoring; paraphrase-dedup scores.
  (`d4_E.npy`, `d4_P.npy`, `d4_pidx.npy`, `d4_rows_stage1.npy` were not copied; regenerate with the embed scripts.)
- `d3_*` — router bake-off on GBrain's 73 bundled skills and 271 routing fixtures: TF-IDF/LSA nearest-centroid vs FlyPrompt-style REAR
  expansion vs FlyHash k-WTA, trigger-blind (leave-one-trigger-out). `d3_extract.ts`/`d3_dump.ts` pull the fixtures from the gbrain repo.
- `calc.py`, `calc2.py` — sizing/cost arithmetic for g02.
- `graphiti_edges.py`, `temporal_ops.py` — Zep/Graphiti edge-invalidation logic pulled for g01's bitemporal comparison.

Requirements: Docker, Python 3 with `FlagEmbedding`/`sentence-transformers`, `numpy`, `psycopg`. Node for the `.ts` extractors.

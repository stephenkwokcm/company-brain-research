#!/bin/bash
PSQL="docker exec -i pgvm psql -U postgres -q -v ON_ERROR_STOP=1"
TA="docker exec pgvm psql -U postgres -tAc"
echo "=== pgvector $($TA "SELECT extversion FROM pg_extension WHERE extname='vector'") pg $($TA 'SHOW server_version') m=16 ef_construction=64 (defaults) ==="
sweep(){ DIM=$1; N=$2; T="v${DIM}_${N}";
  $PSQL -c "DROP TABLE IF EXISTS $T; CREATE TABLE $T (id int, embedding vector($DIM));" 2>/dev/null
  S=$(date +%s)
  # correlated on g -> a fresh random vector per row
  $PSQL -c "INSERT INTO $T SELECT g,(SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM + 0*g)) FROM generate_series(1,$N) g;"
  GEN=$(( $(date +%s) - S ))
  DISTINCT=$($TA "SELECT count(DISTINCT embedding) FROM (SELECT embedding FROM $T LIMIT 500) z;")
  HEAP=$($TA "SELECT pg_relation_size('$T')"); TOT=$($TA "SELECT pg_total_relation_size('$T')")
  S=$(date +%s)
  $PSQL -c "SET maintenance_work_mem='4GB'; SET max_parallel_maintenance_workers=4; CREATE INDEX ix_$T ON $T USING hnsw (embedding vector_cosine_ops);"
  B=$(( $(date +%s) - S ))
  IDX=$($TA "SELECT pg_relation_size('ix_$T')")
  echo "RESULT dim=$DIM n=$N distinct_in_500=$DISTINCT gen_secs=$GEN build_secs=$B heap=$HEAP total_tbl=$TOT index=$IDX idx_B_per_vec=$(echo "scale=1;$IDX/$N"|bc) tbl_B_per_vec=$(echo "scale=1;$TOT/$N"|bc)"
  for EF in 40 200; do
    docker exec -i pgvm psql -U postgres -q -c "SET hnsw.ef_search=$EF; CREATE TEMP TABLE q AS SELECT (SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM+0*g)) e FROM generate_series(1,50) g;" >/dev/null 2>&1
    MS=$(docker exec pgvm psql -U postgres -tAc "SET hnsw.ef_search=$EF;
      WITH q AS (SELECT (SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM+0*g)) e FROM generate_series(1,50) g),
      timed AS (SELECT (SELECT count(*) FROM (SELECT id FROM $T ORDER BY embedding <=> q.e LIMIT 10) z) c FROM q)
      SELECT count(*) FROM timed;" >/dev/null 2>&1
    T0=$(python3 -c 'import time;print(time.time())')
    docker exec pgvm psql -U postgres -tAc "SET hnsw.ef_search=$EF;
      WITH q AS (SELECT (SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM+0*g)) e FROM generate_series(1,50) g)
      SELECT sum(c) FROM (SELECT (SELECT count(*) FROM (SELECT id FROM $T ORDER BY embedding <=> q.e LIMIT 10) z) c FROM q) y;" >/dev/null 2>&1
    T1=$(python3 -c 'import time;print(time.time())')
    echo "RESULT_QUERY dim=$DIM n=$N ef_search=$EF total_50q_secs=$(python3 -c "print(round($T1-$T0,3))") ms_per_query=$(python3 -c "print(round(($T1-$T0)*1000/50,2))")"
  done
}
sweep 768 100000
sweep 1024 100000
sweep 1536 100000
sweep 1024 400000
echo "=== DONE ==="

#!/bin/bash
D=/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad
run(){ docker exec -i pgvm psql -U postgres -v ON_ERROR_STOP=1 -q -c "$1"; }
echo "=== pgvector $(docker exec pgvm psql -U postgres -tAc "SELECT extversion FROM pg_extension WHERE extname='vector'") / $(docker exec pgvm psql -U postgres -tAc 'SHOW server_version') ==="
run "SET maintenance_work_mem='4GB'; SELECT 1;" >/dev/null
for DIM in 768 1024 1536; do
  for N in 50000 200000; do
    if [ "$DIM" != "1024" ] && [ "$N" = "50000" ]; then continue; fi
    if [ "$DIM" != "1024" ] && [ "$N" = "200000" ]; then NN=100000; else NN=$N; fi
    T="t${DIM}_${NN}"
    echo "--- dim=$DIM n=$NN ---"
    run "DROP TABLE IF EXISTS $T; CREATE TABLE $T (id int, embedding vector($DIM));"
    docker exec -i pgvm psql -U postgres -q -c "INSERT INTO $T SELECT g,(SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM)) FROM generate_series(1,$NN) g;"
    HEAP=$(docker exec pgvm psql -U postgres -tAc "SELECT pg_relation_size('$T')")
    S=$(date +%s)
    docker exec -i pgvm psql -U postgres -q -c "SET maintenance_work_mem='4GB'; SET max_parallel_maintenance_workers=4; CREATE INDEX ix_$T ON $T USING hnsw (embedding vector_cosine_ops);"
    E=$(date +%s)
    IDX=$(docker exec pgvm psql -U postgres -tAc "SELECT pg_relation_size('ix_$T')")
    echo "RESULT dim=$DIM n=$NN heap_bytes=$HEAP index_bytes=$IDX build_secs=$((E-S)) idx_bytes_per_vec=$(echo "scale=1;$IDX/$NN"|bc) heap_bytes_per_vec=$(echo "scale=1;$HEAP/$NN"|bc)"
    # query latency
    docker exec -i pgvm psql -U postgres -q -c "SET hnsw.ef_search=40;" >/dev/null
    for EF in 40 200; do
      LAT=$(docker exec pgvm psql -U postgres -tAc "SET hnsw.ef_search=$EF; \timing on
      SELECT 1;" 2>/dev/null)
      Q=$(docker exec pgvm psql -U postgres -tAc "SET hnsw.ef_search=$EF;
      SELECT round(avg(ms)::numeric,3) FROM (
        SELECT (SELECT extract(epoch from clock_timestamp()-t)*1000 FROM (SELECT clock_timestamp() t) s0,
          LATERAL (SELECT id FROM $T ORDER BY embedding <=> (SELECT array_agg(random()::real)::vector FROM generate_series(1,$DIM)) LIMIT 10) q) ms
        FROM generate_series(1,30)) x;")
      echo "RESULT_QUERY dim=$DIM n=$NN ef_search=$EF mean_ms=$Q"
    done
  done
done
echo "=== DONE ==="

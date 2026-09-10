\timing off
CREATE EXTENSION IF NOT EXISTS vector;
DROP TABLE IF EXISTS c1024; DROP TABLE IF EXISTS c768; DROP TABLE IF EXISTS c1536;
SET maintenance_work_mem = '4GB';
SET max_parallel_maintenance_workers = 4;

-- 1024 dims (gbrain new-install default: voyage-4 @ 1024d)
CREATE TABLE c1024 (id int, embedding vector(1024));
INSERT INTO c1024 SELECT g, (SELECT array_agg(random()::real)::vector FROM generate_series(1,1024)) FROM generate_series(1,200000) g;
SELECT 'heap_1024_200k' AS what, pg_size_pretty(pg_relation_size('c1024')) AS sz, pg_relation_size('c1024') AS bytes;
\echo BUILD_START_1024
SELECT clock_timestamp() AS t0 \gset
CREATE INDEX i1024 ON c1024 USING hnsw (embedding vector_cosine_ops);
SELECT extract(epoch from clock_timestamp() - :'t0'::timestamptz) AS build_secs_1024_200k;
SELECT 'index_1024_200k' AS what, pg_size_pretty(pg_relation_size('i1024')) AS sz, pg_relation_size('i1024') AS bytes,
       pg_relation_size('i1024')::numeric/200000 AS bytes_per_vector;

\timing on
CREATE EXTENSION vector;
CREATE TABLE f32 (id int, e vector(1024));
INSERT INTO f32 SELECT g, v FROM generate_series(1,100000) g,
  LATERAL (SELECT array_agg(random()*2-1)::vector AS v FROM generate_series(1,1024)) t;
CREATE TABLE b1024 AS SELECT id, binary_quantize(e)::bit(1024) AS e FROM f32;
CREATE TABLE fly64 (id int, e sparsevec(20480));
INSERT INTO fly64 SELECT id, v FROM f32,
  LATERAL (SELECT ('{'||string_agg(i||':1',',' ORDER BY i)||'}/20480')::sparsevec AS v
           FROM (SELECT DISTINCT (1+floor(random()*20480))::int AS i FROM generate_series(1,90) LIMIT 64) s) t;
CREATE TABLE fly1024 (id int, e sparsevec(20480));
INSERT INTO fly1024 SELECT id, v FROM f32,
  LATERAL (SELECT ('{'||string_agg(i||':1',',' ORDER BY i)||'}/20480')::sparsevec AS v
           FROM (SELECT DISTINCT (1+floor(random()*20480))::int AS i FROM generate_series(1,1200) LIMIT 1024) s) t;
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) total, pg_total_relation_size(oid)/100000 AS bytes_per_row
  FROM pg_class WHERE relname IN ('f32','b1024','fly64','fly1024') ORDER BY 3;
CREATE INDEX ix_f32 ON f32 USING hnsw (e vector_cosine_ops);
CREATE INDEX ix_b   ON b1024 USING hnsw (e bit_hamming_ops);
CREATE INDEX ix_f64 ON fly64 USING hnsw (e sparsevec_cosine_ops);
CREATE INDEX ix_f1024 ON fly1024 USING hnsw (e sparsevec_cosine_ops);
SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid)) idx, pg_relation_size(indexrelid)/100000 AS index_bytes_per_row
  FROM pg_stat_user_indexes ORDER BY 3;

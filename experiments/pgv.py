import subprocess, time, sys

def psql(sql, tuples=False):
    cmd = ["docker","exec","-i","pgvm","psql","-U","postgres","-v","ON_ERROR_STOP=1"]
    cmd += ["-tAc" if tuples else "-c", sql]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("SQLERR:", r.stderr.strip()[:400], flush=True)
    return r.stdout.strip()

ver = psql("SELECT extversion FROM pg_extension WHERE extname='vector'", True)
pg  = psql("SHOW server_version", True)
print(f"=== pgvector {ver} / PostgreSQL {pg} / HNSW defaults m=16 ef_construction=64 ===", flush=True)

def sweep(dim, n):
    t = f"v{dim}_{n}"
    psql(f"DROP TABLE IF EXISTS {t}; CREATE TABLE {t} (id int, embedding vector({dim}));")
    s = time.time()
    # '+ 0*g' makes the subquery CORRELATED -> a fresh random vector per row
    psql(f"INSERT INTO {t} SELECT g, (SELECT array_agg(random()::real)::vector "
         f"FROM generate_series(1, {dim} + 0*g)) FROM generate_series(1,{n}) g;")
    gen = time.time()-s
    dist = psql(f"SELECT count(DISTINCT embedding) FROM (SELECT embedding FROM {t} LIMIT 500) z;", True)
    heap = int(psql(f"SELECT pg_relation_size('{t}')", True))
    tot  = int(psql(f"SELECT pg_total_relation_size('{t}')", True))
    s = time.time()
    psql(f"SET maintenance_work_mem='2GB'; SET max_parallel_maintenance_workers=0; "
         f"CREATE INDEX ix_{t} ON {t} USING hnsw (embedding vector_cosine_ops);")
    build = time.time()-s
    idx = int(psql(f"SELECT pg_relation_size('ix_{t}')", True))
    print(f"RESULT dim={dim} n={n} distinct_of_500={dist} gen_s={gen:.0f} build_s={build:.1f} "
          f"heap_MB={heap/2**20:.1f} table_total_MB={tot/2**20:.1f} index_MB={idx/2**20:.1f} "
          f"index_B_per_vec={idx/n:.0f} table_B_per_vec={tot/n:.0f}", flush=True)
    for ef in (40, 200):
        psql(f"SET hnsw.ef_search={ef}; SELECT 1;")  # warm
        q = (f"SET hnsw.ef_search={ef}; WITH q AS (SELECT (SELECT array_agg(random()::real)::vector "
             f"FROM generate_series(1,{dim}+0*g)) e FROM generate_series(1,50) g) "
             f"SELECT sum((SELECT count(*) FROM (SELECT id FROM {t} ORDER BY embedding <=> q.e LIMIT 10) z)) FROM q;")
        psql(q, True)  # warm cache
        s = time.time(); psql(q, True); el = time.time()-s
        print(f"RESULT_QUERY dim={dim} n={n} ef_search={ef} ms_per_query={el*1000/50:.2f}", flush=True)
    return idx

for dim, n in [(1024,250000)]:
    sweep(dim, n)
print("=== DONE ===", flush=True)

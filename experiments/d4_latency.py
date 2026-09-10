import numpy as np, time
from scipy import sparse
rng=np.random.default_rng(1); N=200_000; d=1024
print(f"brute-force scan throughput, N={N:,} rows, single process, {np.__version__=}")
X=rng.standard_normal((N,d)).astype(np.float32); q=rng.standard_normal(d).astype(np.float32)
t0=time.time()
for _ in range(5): _=X@q
t_f=(time.time()-t0)/5
print(f"float32 vector(1024) dot          : {t_f*1000:7.1f} ms/query   {N*4*d/1e6:7.1f} MB scanned")
del X
B=rng.integers(0,256,(N,d//8),dtype=np.uint8); qb=rng.integers(0,256,d//8,dtype=np.uint8)
t0=time.time()
for _ in range(5): _=np.bitwise_count(np.bitwise_xor(B,qb)).sum(1)
t_b=(time.time()-t0)/5
print(f"bit(1024) Hamming (popcount)      : {t_b*1000:7.1f} ms/query   {N*d/8/1e6:7.1f} MB scanned   ({t_f/t_b:.1f}x faster than float32)")
for k,m in [(64,20480),(256,20480),(1024,20480)]:
    idx=np.sort(rng.integers(0,m,(N,k)),axis=1)
    Sp=sparse.csr_matrix((np.ones(N*k,np.float32),(np.repeat(np.arange(N),k),idx.ravel())),shape=(N,m))
    qi=rng.integers(0,m,k); qv=sparse.csr_matrix((np.ones(k,np.float32),(np.zeros(k),qi)),shape=(1,m))
    t0=time.time()
    for _ in range(5): _=(Sp@qv.T).toarray()
    t_s=(time.time()-t0)/5
    print(f"FlyHash sparsevec({m}) k={k:4d}  : {t_s*1000:7.1f} ms/query   {N*(8*k+16)/1e6:7.1f} MB stored   ({t_b/t_s:.2f}x vs bit-Hamming)")

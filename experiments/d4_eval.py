import numpy as np, json, time, math
from scipy import sparse
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
rng=np.random.default_rng(7)
E=np.load(f"{S}/d4_E.npy"); n,d=E.shape
print(f"corpus {n} chunks x {d} dims (bge-m3, normalized)")
K=10
# ---- ground truth: exact cosine top-10, self excluded
Sim = E @ E.T
np.fill_diagonal(Sim,-9)
gt = np.argpartition(-Sim, K, axis=1)[:,:K]
gt = np.take_along_axis(gt, np.argsort(-np.take_along_axis(Sim,gt,1),axis=1),1)
gtset=[set(r) for r in gt]
mean=E.mean(0)

def recall_from_scores(Sc, R=None):
    """Sc: n x n similarity (higher=better), diagonal must be -inf. Returns recall@10 raw and with exact rescore of top-R."""
    np.fill_diagonal(Sc,-1e9)
    top=np.argpartition(-Sc,K,axis=1)[:,:K]
    raw=np.mean([len(gtset[i]&set(top[i]))/K for i in range(n)])
    out={'r@10':raw}
    if R:
        for r in R:
            cand=np.argpartition(-Sc,r,axis=1)[:,:r]
            rec=0.0
            for i in range(n):
                c=cand[i]; s=Sim[i,c]
                sel=c[np.argpartition(-s,K)[:K]]
                rec+=len(gtset[i]&set(sel))/K
            out[f'r@10|rescore{r}']=rec/n
    return out

def bytes_pgvector(kind, **kw):
    if kind=='vector': return 4*kw['d']+8
    if kind=='halfvec': return 2*kw['d']+8
    if kind=='bit': return kw['L']//8+8
    if kind=='sparsevec': return 8*kw['nnz']+16
    if kind=='packed_idx': return kw['k']*math.ceil(math.log2(kw['m'])/8)
rows=[]
def add(name, bytes_, res, t_enc, note=''):
    rows.append(dict(method=name, bytes=bytes_, **res, enc_s=round(t_enc,2), note=note))
    print(f"{name:46s} {bytes_:7d} B  r@10={res['r@10']:.4f}" + ''.join(f"  {k}={v:.4f}" for k,v in res.items() if k!='r@10'))

# ---- 1. float32 exact (reference)
add('float32 vector(1024) [exact, reference]', bytes_pgvector('vector',d=d), {'r@10':1.0}, 0.0)
# ---- 2. halfvec
t0=time.time(); H=E.astype(np.float16).astype(np.float32); te=time.time()-t0
add('halfvec(1024)', bytes_pgvector('halfvec',d=d), recall_from_scores(H@H.T,[50]), te)
# ---- 3. int8 scalar quant (per-vector symmetric)
t0=time.time()
sc=np.abs(E).max(1,keepdims=True)/127.0
Q=np.round(E/sc).astype(np.int8).astype(np.float32)*sc; te=time.time()-t0
add('int8 scalar quant', d+8, recall_from_scores(Q@Q.T,[50]), te)
# ---- 4. pgvector binary_quantize: sign(x) > 0, Hamming
def hamming_sim(B):  # B in {0,1} uint8 packed as float -> use matmul on +-1
    X=B.astype(np.float32)*2.0-1.0; return X@X.T   # = L - 2*Hamming
t0=time.time(); B=(E>0).astype(np.uint8); te=time.time()-t0
add('binary_quantize(x) -> bit(1024)  [pgvector default]', bytes_pgvector('bit',L=d), recall_from_scores(hamming_sim(B),[50,100]), te)
t0=time.time(); Bc=((E-mean)>0).astype(np.uint8); te=time.time()-t0
add('binary_quantize(x - corpus_mean) -> bit(1024)', bytes_pgvector('bit',L=d), recall_from_scores(hamming_sim(Bc),[50,100]), te)
# ---- 5. SimHash / random-hyperplane LSH at L bits
for L in [128,256,512,1024,2048,4096]:
    R=rng.standard_normal((d,L)).astype(np.float32)
    t0=time.time(); BL=(((E-mean)@R)>0).astype(np.uint8); te=time.time()-t0
    add(f'SimHash/LSH L={L} bits', bytes_pgvector('bit',L=L), recall_from_scores(hamming_sim(BL),[50] if L<=1024 else None), te)
np.save(f"{S}/d4_rows_stage1.npy", np.array([1]))
json.dump(rows, open(f"{S}/d4_stage1.json","w"), indent=1)

import numpy as np, json, time, math
from scipy import sparse
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
rng=np.random.default_rng(11)
E=np.load(f"{S}/d4_E.npy"); n,d=E.shape; K=10
Sim=E@E.T; np.fill_diagonal(Sim,-9.0)
gt=np.argpartition(-Sim,K,axis=1)[:,:K]; gtset=[set(r) for r in gt]
cmean=E.mean(0)

def eval_scores(Sc,R=(50,100)):
    Sc=Sc.astype(np.float32); np.fill_diagonal(Sc,-1e9)
    top=np.argpartition(-Sc,K,axis=1)[:,:K]
    out={'r@10':float(np.mean([len(gtset[i]&set(top[i]))/K for i in range(n)]))}
    for r in R:
        cand=np.argpartition(-Sc,r,axis=1)[:,:r]; acc=0.0
        for i in range(n):
            c=cand[i]; s=Sim[i,c]; sel=c[np.argpartition(-s,K)[:K]]
            acc+=len(gtset[i]&set(sel))/K
        out[f'rescore{r}']=acc/n
    return out

def flyhash_codes(X, m, fanin, k, seed=0):
    r=np.random.default_rng(seed)
    # sparse binary projection: each of m rows samples `fanin` input dims (Dasgupta 2017)
    cols=np.concatenate([r.choice(d,fanin,replace=False) for _ in range(m)])
    rows=np.repeat(np.arange(m),fanin)
    M=sparse.csr_matrix((np.ones(m*fanin,np.float32),(rows,cols)),shape=(m,d))
    Y=(M@X.T).T                       # n x m
    idx=np.argpartition(-Y,k,axis=1)[:,:k]
    return idx

def sparse_sim(idx,m):
    n_,k=idx.shape
    Sp=sparse.csr_matrix((np.ones(n_*k,np.float32),(np.repeat(np.arange(n_),k),idx.ravel())),shape=(n_,m))
    return np.asarray((Sp@Sp.T).todense())   # |intersection| == monotone in -Hamming for fixed k

rows=[]
Xc = E - cmean                        # corpus-centred input (best of the two; per-vector centring tested below)
Xp = E - E.mean(1,keepdims=True)      # per-vector divisive/subtractive normalisation (the fly's step 1)
for label,X in [('corpus-centred',Xc),('per-vector-centred (fly step 1)',Xp),('raw',E)]:
    for rho in ([10,20,40] if label=='corpus-centred' else [20]):
        m=rho*d
        for fanin in ([102] if label!='corpus-centred' or rho!=20 else [12,102,205]):
            for k in [16,32,64,128,256,512,1024]:
                if k>=m: continue
                t0=time.time(); idx=flyhash_codes(X,m,fanin,k,seed=rho*1000+fanin); te=time.time()-t0
                res=eval_scores(sparse_sim(idx,m))
                bidx=k*math.ceil(math.log2(m)/8); bbit=m//8+8; bsv=8*k+16
                rows.append(dict(method=f'FlyHash rho={rho} m={m} fanin={fanin} k={k} [{label}]',
                    bytes_packed_idx=bidx, bytes_pgvector_sparsevec=bsv, bytes_dense_bitmap=bbit,
                    enc_s=round(te,2), **res))
                print(f"FlyHash rho={rho:2d} m={m:6d} f={fanin:3d} k={k:5d} [{label:32s}] idxB={bidx:5d} svB={bsv:6d} r@10={res['r@10']:.4f} resc100={res['rescore100']:.4f}")
json.dump(rows,open(f"{S}/d4_fly.json","w"),indent=1)

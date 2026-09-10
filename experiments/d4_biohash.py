import numpy as np, json, time, math
from scipy import sparse
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
E=np.load(f"{S}/d4_E.npy"); n,d=E.shape; K=10
Sim=E@E.T; np.fill_diagonal(Sim,-9.0)
gt=np.argpartition(-Sim,K,axis=1)[:,:K]; gtset=[set(r) for r in gt]
cmean=E.mean(0); Xc=E-cmean
def ev(Sc,R=(50,100)):
    Sc=Sc.astype(np.float32); np.fill_diagonal(Sc,-1e9)
    top=np.argpartition(-Sc,K,axis=1)[:,:K]
    out={'r@10':float(np.mean([len(gtset[i]&set(top[i]))/K for i in range(n)]))}
    for r in R:
        cand=np.argpartition(-Sc,r,axis=1)[:,:r]; a=0.0
        for i in range(n):
            c=cand[i]; s=Sim[i,c]; a+=len(gtset[i]&set(c[np.argpartition(-s,K)[:K]]))/K
        out[f'rescore{r}']=a/n
    return out
def sp(idx,m):
    n_,k=idx.shape
    Sp=sparse.csr_matrix((np.ones(n_*k,np.float32),(np.repeat(np.arange(n_),k),idx.ravel())),shape=(n_,m))
    return np.asarray((Sp@Sp.T).todense())
# --- LSH at very small L, for the Science-2017 "equal hash length" comparison
rng=np.random.default_rng(3); out=[]
for L in [16,32,64,128]:
    R=rng.standard_normal((d,L)).astype(np.float32)
    B=((Xc@R)>0).astype(np.float32)*2-1
    r=ev(B@B.T); out.append(dict(m=f'LSH L={L}',bytes=L//8+8,**r))
    print(f"LSH L={L:5d}  bytes={L//8+8:5d}  r@10={r['r@10']:.4f} resc100={r['rescore100']:.4f}")
# --- BioHash (Krotov-Hopfield bio-learning, as in Ryali et al. ICML 2020) -- TRAINED, data-dependent
def biohash_train(X,m,epochs=60,delta=0.4,lr0=0.02,seed=5,bs=64):
    r=np.random.default_rng(seed); W=r.standard_normal((m,X.shape[1])).astype(np.float32)*0.05
    N=X.shape[0]
    for ep in range(epochs):
        lr=lr0*(1-ep/epochs); perm=r.permutation(N)
        for s0 in range(0,N,bs):
            V=X[perm[s0:s0+bs]]                       # b x d
            I=V@W.T                                   # b x m   (p=2 => currents = W v)
            ordr=np.argsort(-I,axis=1)
            g=np.zeros_like(I); b=np.arange(V.shape[0])
            g[b,ordr[:,0]]=1.0; g[b,ordr[:,1]]=-delta
            # dW_mu = sum_b g_b,mu (v_b - I_b,mu W_mu)
            coef=(g*I).sum(0)                          # m
            dW = g.T@V - coef[:,None]*W
            mx=np.abs(dW).max()
            if mx>0: W += lr*dW/mx
    return W
for m in [2048,8192]:
    t0=time.time(); W=biohash_train(Xc,m); tt=time.time()-t0
    A=Xc@W.T
    for k in [16,32,64,128,256]:
        idx=np.argpartition(-A,k,axis=1)[:,:k]
        r=ev(sp(idx,m)); bi=k*math.ceil(math.log2(m)/8)
        out.append(dict(m=f'BioHash m={m} k={k}',bytes_packed=bi,bytes_sparsevec=8*k+16,train_s=round(tt,1),**r))
        print(f"BioHash m={m:5d} k={k:4d} packedB={bi:5d} svB={8*k+16:5d} r@10={r['r@10']:.4f} resc100={r['rescore100']:.4f}  (train {tt:.0f}s)")
json.dump(out,open(f"{S}/d4_biohash.json","w"),indent=1)

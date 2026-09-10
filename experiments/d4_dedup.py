import numpy as np, json, math, re, hashlib
from scipy import sparse
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
E=np.load(f"{S}/d4_E.npy"); P=np.load(f"{S}/d4_P.npy"); pidx=np.load(f"{S}/d4_pidx.npy")
corpus=json.load(open(f"{S}/d4_corpus.json"))['chunks']
n,d=E.shape; nq=P.shape[0]; m3=len(pidx)
truth=np.concatenate([pidx,pidx,pidx])          # light, heavy, window
labels=['light edit (-10% words)']*m3+['heavy edit (-25% + sentence shuffle)']*m3+['60% window']*m3
cmean=E.mean(0)
def report(name,Sc,extra=''):
    top1=Sc.argmax(1); hit=(top1==truth)
    out={}
    for lab in ['light edit (-10% words)','heavy edit (-25% + sentence shuffle)','60% window']:
        msk=np.array([l==lab for l in labels]); out[lab]=float(hit[msk].mean())
    out['all']=float(hit.mean())
    print(f"{name:52s} {extra:>10s}  top1: light={out['light edit (-10% words)']:.3f} heavy={out['heavy edit (-25% + sentence shuffle)']:.3f} window={out['60% window']:.3f} ALL={out['all']:.3f}")
    return dict(method=name,**out)
res=[]
res.append(report('float32 cosine (exact, the free baseline)', P@E.T, '4104 B'))
def bq(X,c=True): return ((X-(cmean if c else 0))>0).astype(np.float32)*2-1
res.append(report('binary_quantize(x-mean) bit(1024) Hamming', bq(P)@bq(E).T, '136 B'))
rng=np.random.default_rng(3)
for L in [64,1024]:
    R=rng.standard_normal((d,L)).astype(np.float32)
    A=(((P-cmean)@R)>0).astype(np.float32)*2-1; B=(((E-cmean)@R)>0).astype(np.float32)*2-1
    res.append(report(f'SimHash/LSH on embedding L={L}',A@B.T,f'{L//8+8} B'))
def fly(X,m,fanin,k,seed):
    r=np.random.default_rng(seed)
    cols=np.concatenate([r.choice(d,fanin,replace=False) for _ in range(m)]); rows=np.repeat(np.arange(m),fanin)
    M=sparse.csr_matrix((np.ones(m*fanin,np.float32),(rows,cols)),shape=(m,d))
    Y=(M@X.T).T; return np.argpartition(-Y,k,axis=1)[:,:k]
for k in [64,256,1024]:
    mm=20480
    ia=fly(P-cmean,mm,102,k,42); ib=fly(E-cmean,mm,102,k,42)
    A=sparse.csr_matrix((np.ones(ia.size,np.float32),(np.repeat(np.arange(ia.shape[0]),k),ia.ravel())),shape=(ia.shape[0],mm))
    B=sparse.csr_matrix((np.ones(ib.size,np.float32),(np.repeat(np.arange(ib.shape[0]),k),ib.ravel())),shape=(ib.shape[0],mm))
    res.append(report(f'FlyHash on embedding m=20480 f=102 k={k}',np.asarray((A@B.T).todense()),f'{k*2} B'))
# lexical 64-bit SimHash over 3-word shingles (Manku 2007 incumbent)
def simhash64(t,ng=3):
    w=re.findall(r'\w+',t.lower()); v=np.zeros(64)
    for i in range(max(1,len(w)-ng+1)):
        h=int(hashlib.md5(' '.join(w[i:i+ng]).encode()).hexdigest()[:16],16)
        b=np.array([(h>>j)&1 for j in range(64)])*2-1; v+=b
    return (v>0).astype(np.float32)*2-1
SC=np.stack([simhash64(t) for t in corpus]); SP=np.stack([simhash64(t) for t in
    [None]*0] ) if False else None
probes=json.load(open(f"{S}/d4_corpus.json"))  # regenerate probe TEXT identically to d4_embed_full
import random
random.seed(17)
idx=sorted(random.sample(range(len(corpus)),400))
def light(t):
    w=t.split(); w=[x for x in w if random.random()>0.10]; return ' '.join(w).lower()
def heavy(t):
    s=re.split(r'(?<=[.;])\s+',t); random.shuffle(s); t2=' '.join(s)
    w=t2.split(); w=[x for x in w if random.random()>0.25]; return ' '.join(w)
def window(t):
    w=t.split(); nn=len(w); a=int(nn*0.2); return ' '.join(w[a:a+int(nn*0.6)])
ptxt=[light(corpus[i]) for i in idx]+[heavy(corpus[i]) for i in idx]+[window(corpus[i]) for i in idx]
assert list(idx)==list(pidx), "probe index mismatch"
SPq=np.stack([simhash64(t) for t in ptxt])
res.append(report('lexical 64-bit SimHash over 3-shingles (Manku 2007)', SPq@SC.T, '8 B'))
json.dump(res,open(f"{S}/d4_dedup.json","w"),indent=1)

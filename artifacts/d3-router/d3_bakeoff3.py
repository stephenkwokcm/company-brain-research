import json, re, numpy as np, warnings
warnings.filterwarnings('ignore')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
rg = np.random.default_rng(20260910)
SK=json.load(open('d3_skills.json')); FIX=json.load(open('d3_index.json'))['fixtures']
by={s['slug']:s for s in SK}; pos=[f for f in FIX if f['expected_skill'] in by]
classes=sorted(by); cidx={c:i for i,c in enumerate(classes)}
def chunks(t,n=280):
    t=re.sub(r'\s+',' ',t).strip(); parts=re.split(r'(?<=[.!?])\s+',t); out,cur=[],''
    for p in parts:
        if len(cur)+len(p)<n: cur+=' '+p
        else:
            if len(cur.strip())>20: out.append(cur.strip())
            cur=p
    if len(cur.strip())>20: out.append(cur.strip())
    return out[:12]
def build(cond):
    rows,labels=[],[]
    for s in SK:
        head=s['name']+' '+s['description']+((' '+' '.join(s['triggers'])) if cond=='T' else '')
        rows.append(head); labels.append(s['slug'])
        base=s['description']+' '+((' '.join(s['triggers'])+' ') if cond=='T' else '')+s['body'][:2500]
        for c in chunks(base): rows.append(c); labels.append(s['slug'])
    return rows,labels
def onehot(labels):
    Y=np.zeros((len(labels),len(classes)))
    for i,l in enumerate(labels): Y[i,cidx[l]]=1
    return Y
def ridge_scores(Ptr,Y,Pte,lam):
    # dual form: n_train << n_features, so solve the n x n system
    K=Ptr@Ptr.T
    A=np.linalg.solve(K+lam*np.eye(K.shape[0]),Y)
    return (Pte@Ptr.T)@A
def ev(scores,pools,seeds=5):
    scores=np.nan_to_num(scores,nan=-1e9,posinf=-1e9,neginf=-1e9); out={}
    for K in pools:
        a=[]
        for sd in range(seeds):
            rng=np.random.default_rng(1000+sd); ok=0
            for j,f in enumerate(pos):
                gt=cidx[f['expected_skill']]; oth=[i for i in range(len(classes)) if i!=gt]
                dis=rng.choice(oth,size=min(K-1,len(oth)),replace=False)
                cand=np.concatenate(([gt],dis))
                ok+= int(cand[np.argmax(scores[j,cand])]==gt)
            a.append(ok/len(pos))
        out[K]=(float(np.mean(a)),float(np.std(a)))
    return out
POOLS=[5,10,25,50,73]; LAMS=[1e-4,1e-3,1e-2,1e-1,1,10,100]
rep={}
for cond in ['T','B']:
    rows,labels=build(cond); tests=[f['intent'] for f in pos]
    vec=TfidfVectorizer(sublinear_tf=True,ngram_range=(1,2),stop_words='english')
    Xtr=vec.fit_transform(rows); Xte=vec.transform(tests)
    svd=TruncatedSVD(n_components=256,random_state=0)
    Htr=np.nan_to_num(normalize(svd.fit_transform(Xtr))); Hte=np.nan_to_num(normalize(svd.transform(Xte)))
    Y=onehot(labels); d=256; arms={}
    Xd=np.asarray(Xtr.todense()); Xd=np.nan_to_num(Xd); Xe=np.nan_to_num(np.asarray(Xte.todense()))
    C=np.vstack([normalize(Xd[[i for i,l in enumerate(labels) if l==c]].mean(0).reshape(1,-1)) for c in classes])
    arms['tfidf-centroid (no training)']=Xe@C.T
    CL=np.vstack([normalize(Htr[[i for i,l in enumerate(labels) if l==c]].mean(0).reshape(1,-1)) for c in classes])
    arms['lsa256-centroid']=Hte@CL.T
    def best(name,Ptr,Pte):
        bb=None
        for lam in LAMS:
            sc=np.nan_to_num(ridge_scores(Ptr,Y,Pte,lam)); r=ev(sc,POOLS,seeds=3)
            if bb is None or r[73][0]>bb[1][73][0]: bb=(lam,r,sc)
        arms[name+' [lam=%g]'%bb[0]]=bb[2]
    best('lsa256-ridge',Htr,Hte)
    for M_ in [2560,10000]:
        R=rg.standard_normal((d,M_))/np.sqrt(d)
        best('REAR dense-Gauss+ReLU M=%d'%M_,np.maximum(Htr@R,0),np.maximum(Hte@R,0))
    def fly(H,M,rho):
        X=H-H.mean(1,keepdims=True); Yy=X@M.T; o=np.zeros_like(Yy)
        k=np.argpartition(-Yy,rho,axis=1)[:,:rho]; np.put_along_axis(o,k,1.0,axis=1); return o
    for exp_,act in [(10,0.05),(40,0.05),(40,0.10),(40,0.02)]:
        m=exp_*d; s=max(2,int(0.10*d)); rho=max(1,int(act*m))
        Mm=np.zeros((m,d))
        for r in range(m): Mm[r,rg.choice(d,size=s,replace=False)]=1.0
        best('FlyHash m=%dd rho=%d%%'%(exp_,int(act*100)),fly(Htr,Mm,rho),fly(Hte,Mm,rho))
    rep[cond]={k:ev(v,POOLS) for k,v in arms.items()}
print('=== TOP-1 vs POOL SIZE  (n=271 gbrain routing fixtures, 73 classes, 5 seeds, oracle lambda) ===')
for cond in ['T','B']:
    print('\n-- %s --'%('T: class docs INCLUDE the trigger phrases' if cond=='T' else 'B: TRIGGER-BLIND class docs (description+body only)'))
    print('%-38s %s'%('arm','  '.join('K=%-4d'%k for k in POOLS)))
    for a,r in rep[cond].items(): print('%-38s %s'%(a,'  '.join('%.3f '%r[k][0] for k in POOLS)))
# log-linear extrapolation on best arm
import math
for cond in ['T','B']:
    a=list(rep[cond].items())[0]
    xs=np.log(POOLS); ys=[a[1][k][0] for k in POOLS]
    b,c0=np.polyfit(xs,ys,1)
    print('\n[%s] %s: acc ~= %.4f %+.4f*ln(K); extrapolated K=150 -> %.3f ; K=300 -> %.3f'%(cond,a[0],c0,b,c0+b*math.log(150),c0+b*math.log(300)))
json.dump(rep,open('d3_bakeoff2.json','w'),indent=1)

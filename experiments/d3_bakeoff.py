import json, re, unicodedata, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

rng_global = np.random.default_rng(20260910)
SK = json.load(open('d3_skills.json'))
D  = json.load(open('d3_index.json')); FIX = D['fixtures']
by = {s['slug']: s for s in SK}
pos = [f for f in FIX if f['expected_skill'] in by]
print('positive fixtures usable:', len(pos), 'classes:', len(by))

def chunks(text, n=280):
    text = re.sub(r'\s+',' ', text).strip()
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    out, cur = [], ''
    for p in parts:
        if len(cur)+len(p) < n: cur += ' '+p
        else:
            if len(cur.strip())>20: out.append(cur.strip())
            cur = p
    if len(cur.strip())>20: out.append(cur.strip())
    return out[:12]

def build(cond):
    """cond 'T' = triggers visible in class doc; 'B' = trigger-blind."""
    rows, labels = [], []
    for s in SK:
        base = s['description'] + ' '
        if cond=='T': base += ' '.join(s['triggers']) + ' '
        base += s['body'][:2500]
        cs = chunks(base)
        head = s['name'] + ' ' + s['description']
        if cond=='T': head += ' ' + ' '.join(s['triggers'])
        rows.append(head); labels.append(s['slug'])
        for c in cs:
            rows.append(c); labels.append(s['slug'])
    return rows, labels

def featurize(train_docs, test_docs, dim=256):
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1,2), min_df=1,
                          analyzer='word', stop_words='english')
    Xtr = vec.fit_transform(train_docs); Xte = vec.transform(test_docs)
    svd = TruncatedSVD(n_components=dim, random_state=0)
    Htr = normalize(svd.fit_transform(Xtr)); Hte = normalize(svd.transform(Xte))
    return normalize(Xtr), normalize(Xte), Htr, Hte

def ridge_fit(Phi, Y, lam):
    G = Phi.T @ Phi + lam*np.eye(Phi.shape[1])
    return np.linalg.solve(G, Phi.T @ Y)

def onehot(labels, classes):
    idx = {c:i for i,c in enumerate(classes)}
    Y = np.zeros((len(labels), len(classes)))
    for i,l in enumerate(labels): Y[i, idx[l]] = 1
    return Y

def rear(H, R):  # dense Gaussian expansion + ReLU  (FlyPrompt REAR / RanPAC)
    return np.maximum(H @ R, 0)

def flyhash(H, M, rho):  # sparse binary projection + k-WTA  (Dasgupta 2017)
    X = H - H.mean(axis=1, keepdims=True)      # divisive-normalisation proxy
    Y = X @ M.T                                 # (n, m)
    out = np.zeros_like(Y)
    kth = np.argpartition(-Y, rho, axis=1)[:, :rho]
    np.put_along_axis(out, kth, 1.0, axis=1)
    return out

def evaluate(scores, classes, fixtures, pool_sizes, seeds=5):
    """scores: (n_fix, n_class). Returns dict pool->acc."""
    cidx = {c:i for i,c in enumerate(classes)}
    res = {}
    for K in pool_sizes:
        accs = []
        for sd in range(seeds):
            rng = np.random.default_rng(1000+sd)
            ok = 0
            for j,f in enumerate(fixtures):
                gt = cidx[f['expected_skill']]
                others = [i for i in range(len(classes)) if i != gt]
                if K-1 < len(others):
                    dis = rng.choice(others, size=K-1, replace=False)
                else:
                    dis = np.array(others)
                cand = np.concatenate(([gt], dis))
                if cand[np.argmax(scores[j, cand])] == gt: ok += 1
            accs.append(ok/len(fixtures))
        res[K] = (float(np.mean(accs)), float(np.std(accs)))
    return res

POOLS=[5,10,25,50,73]
report={}
for cond in ['T','B']:
    rows, labels = build(cond)
    classes = sorted(by.keys())
    tests = [f['intent'] for f in pos]
    Xtr, Xte, Htr, Hte = featurize(rows, tests)
    Y = onehot(labels, classes)
    d = Htr.shape[1]
    arms = {}
    # 1. sparse TF-IDF nearest centroid
    cent = {}
    Xd = np.asarray(Xtr.todense())
    C = np.vstack([normalize(Xd[[i for i,l in enumerate(labels) if l==c]].mean(axis=0).reshape(1,-1)) for c in classes])
    arms['tfidf-centroid'] = np.asarray(Xte.todense()) @ C.T
    # 2. LSA nearest centroid
    CL = np.vstack([normalize(Htr[[i for i,l in enumerate(labels) if l==c]].mean(axis=0).reshape(1,-1)) for c in classes])
    arms['lsa-centroid'] = Hte @ CL.T
    # 3. LSA + ridge (no expansion)
    W = ridge_fit(Htr, Y, 1e-2); arms['lsa-ridge'] = Hte @ W
    # 4. REAR dense Gaussian expansion + ReLU + ridge
    for M_ in [2560, 10000]:
        R = rng_global.standard_normal((d, M_))/np.sqrt(d)
        Ptr, Pte = rear(Htr, R), rear(Hte, R)
        W = ridge_fit(Ptr, Y, 1e-1)
        arms[f'REAR-M{M_}'] = Pte @ W
    # 5. FlyHash sparse binary + kWTA + ridge
    for exp_,act in [(10,0.05),(40,0.05),(40,0.10)]:
        m = exp_*d; s = max(2,int(0.10*d)); rho = max(1,int(act*m))
        Mm = np.zeros((m,d))
        for r in range(m):
            Mm[r, rng_global.choice(d, size=s, replace=False)] = 1.0
        Ftr, Fte = flyhash(Htr, Mm, rho), flyhash(Hte, Mm, rho)
        W = ridge_fit(Ftr, Y, 1e-1)
        arms[f'FlyHash-m{exp_}d-rho{int(act*100)}%'] = Fte @ W
    report[cond] = {k: evaluate(v, classes, pos, POOLS) for k,v in arms.items()}

print('\n=== TOP-1 ACCURACY vs POOL SIZE (271 gbrain routing fixtures, 5 seeds) ===')
for cond in ['T','B']:
    print('\n-- condition %s (%s) --' % (cond, 'class docs INCLUDE trigger phrases' if cond=='T' else 'TRIGGER-BLIND class docs'))
    print('%-26s %s' % ('arm', '  '.join('K=%-3d'%k for k in POOLS)))
    for arm,res in report[cond].items():
        print('%-26s %s' % (arm, '  '.join('%.3f'%res[k][0] for k in POOLS)))
json.dump(report, open('d3_bakeoff.json','w'), indent=1)

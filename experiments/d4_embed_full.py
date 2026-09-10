import json, time, numpy as np, os, torch, random, re
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
d=json.load(open(f"{S}/d4_corpus.json")); chunks=d['chunks']
random.seed(17)
# near-duplicate probes: same content, rewritten/edited (no LLM) on a 400-chunk sample
idx=sorted(random.sample(range(len(chunks)),400))
def light(t):
    w=t.split(); w=[x for x in w if random.random()>0.10]; return ' '.join(w).lower()
def heavy(t):
    s=re.split(r'(?<=[.;])\s+',t); random.shuffle(s); t2=' '.join(s)
    w=t2.split(); w=[x for x in w if random.random()>0.25]; return ' '.join(w)
def window(t):
    w=t.split(); n=len(w); a=int(n*0.2); return ' '.join(w[a:a+int(n*0.6)])
probes=[light(chunks[i]) for i in idx]+[heavy(chunks[i]) for i in idx]+[window(chunks[i]) for i in idx]
from sentence_transformers import SentenceTransformer
m=SentenceTransformer("BAAI/bge-m3", device="mps"); m.max_seq_length=512
t0=time.time()
E=m.encode(chunks, batch_size=8, show_progress_bar=False, normalize_embeddings=True).astype(np.float32)
print("corpus",E.shape, round(time.time()-t0,1),"s")
t0=time.time()
P=m.encode(probes, batch_size=8, show_progress_bar=False, normalize_embeddings=True).astype(np.float32)
print("probes",P.shape, round(time.time()-t0,1),"s")
np.save(f"{S}/d4_E.npy",E); np.save(f"{S}/d4_P.npy",P); np.save(f"{S}/d4_pidx.npy",np.array(idx))

import json, time, numpy as np, os, torch
S="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
d=json.load(open(f"{S}/d4_corpus.json")); chunks=d['chunks']
from sentence_transformers import SentenceTransformer
dev = "mps" if torch.backends.mps.is_available() else "cpu"
t0=time.time(); m=SentenceTransformer("BAAI/bge-m3", device=dev); print("load",round(time.time()-t0,1),"s dev",dev)
m.max_seq_length=512
t0=time.time(); _=m.encode(chunks[:32], batch_size=8, show_progress_bar=False, normalize_embeddings=True)
print("32 chunks in",round(time.time()-t0,1),"s -> est total", round((time.time()-t0)/32*len(chunks)/60,1),"min")

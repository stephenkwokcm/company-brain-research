import os, re, glob, json
TARGET, OVERLAP = 300, 50   # GBrain src/core/chunkers/recursive.ts
SCRATCH="/private/tmp/claude-501/-Users-stephen-Cookies/c3771026-a579-4349-87b5-e6c6213744df/scratchpad"
files=[]
files+=sorted(glob.glob("/Users/stephen/Cookies/company-brain-research/findings/*.md"))
files+=sorted(glob.glob("/Users/stephen/Cookies/company-brain-research/checkpoints/*.md"))
files+=sorted(glob.glob("/Users/stephen/Cookies/company-brain-research/sources/*.txt"))
files+=sorted(glob.glob(os.path.join(SCRATCH,"*.txt")))
files+=sorted(glob.glob(os.path.join(SCRATCH,"*.md")))
files+=[os.path.join(SCRATCH,x) for x in ["migrate.ts","gb_hybrid.ts","vector-index.ts","schema.sql"]]
def strip_html(p):
    t=open(p,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'(?is)<(script|style|head)[^>]*>.*?</\1>',' ',t)
    t=re.sub(r'(?s)<[^>]+>',' ',t)
    return t
for h in ["h3d.html","ryali_full.html","memconflict.html","mab_v4.html","fresh_v1.html","ctxconf.html","statqa.html","release-18.html"]:
    p=os.path.join(SCRATCH,h)
    if os.path.exists(p):
        open(p+".txt","w").write(strip_html(p)); files.append(p+".txt")
seen=set(); chunks=[]; meta=[]
for f in files:
    if f in seen or not os.path.exists(f): continue
    seen.add(f)
    try: t=open(f,encoding='utf-8',errors='ignore').read()
    except Exception: continue
    t=re.sub(r'&[a-z]+;',' ',t); t=re.sub(r'\s+',' ',t).strip()
    w=t.split(' ')
    if len(w)<60: continue
    i=0
    while i < len(w):
        seg=w[i:i+TARGET]
        if len(seg)<40: break
        chunks.append(' '.join(seg)); meta.append({'file':os.path.basename(f),'start':i})
        if i+TARGET>=len(w): break
        i += TARGET-OVERLAP
print("files",len(seen),"chunks",len(chunks))
json.dump({'chunks':chunks,'meta':meta}, open(os.path.join(SCRATCH,'d4_corpus.json'),'w'))

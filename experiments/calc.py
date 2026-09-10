# Sizing/cost model. Every constant carries its source.
MA = lambda x: -(-x//8)*8            # MAXALIGN, 8 bytes on 64-bit
BLCKSZ, PAGEHDR, OPAQUE, LP = 8192, 24, 8, 4
USABLE = BLCKSZ - PAGEHDR - OPAQUE   # 8160

# pgvector src/hnsw.h : offsetof(HnswElementTupleData,data)=4+10*6+6+2=72 ; Vector hdr = 8
def elem_bytes(dim, half=False): return MA(72 + 8 + (2 if half else 4)*dim)
# HNSW_NEIGHBOR_TUPLE_SIZE(level,m): MAXALIGN(4 + 6*(level+2)*m)
def neigh_bytes(m=16, level=0.0667): return MA(4 + 6*(level+2)*m)   # E[level]=e^-1/m /(1-e^-1/m)=.0667

def index_bytes_per_vec(dim, m=16, half=False):
    e = elem_bytes(dim, half); n = neigh_bytes(m)
    per_page = max(1, USABLE // (e + LP))          # element tuples that fit one 8KB page
    elem_cost = BLCKSZ / per_page                   # incl. intra-page waste
    n_per_page = max(1, USABLE // (n + LP))
    return elem_cost + BLCKSZ / n_per_page

print("=== A. pgvector HNSW index footprint (analytic, from src/hnsw.h) ===")
print(f"{'dim':>6} {'type':>8} {'elem_B':>8} {'per_pg':>7} {'idx_B/vec':>10} {'raw_B/vec':>10} {'ratio':>6}")
for dim, half in [(768,0),(1024,0),(1536,0),(2000,0),(3072,1),(4096,1)]:
    e = elem_bytes(dim, half); ppp = max(1, USABLE//(e+LP)); b = index_bytes_per_vec(dim, half=half)
    raw = (2 if half else 4)*dim
    print(f"{dim:>6} {'halfvec' if half else 'vector':>8} {e:>8} {ppp:>7} {b:>10.0f} {raw:>10} {b/raw:>6.2f}x")

print("\n=== B. corpus -> chunks ===")
# measured: docs/proposals/temporal-contradiction-probe.md L208 "~107K pages, ~257K chunks"
print(f"repo-measured chunks/page = 257000/107000 = {257000/107000:.2f}")
TOK = 400   # docs/eval/SEARCH_MODE_METHODOLOGY.md: 300-word chunk ~= 400 tokens
for pages, label in [(155795,"README hero 2026-08-12"), (1_000_000,"1M-page target")]:
    print(f"\n-- {pages:,} pages ({label}) --")
    for cpp,tag in [(2.40,"repo-measured"),(3,"task low"),(4,"task mid"),(5,"task high")]:
        ch = pages*cpp; tk = ch*TOK
        print(f"  {cpp:>4} chunks/pg ({tag:<13}) -> {ch:>12,.0f} chunks  {tk/1e6:>9,.1f}M tokens", end="")
        for dim in (1024,1536):
            gb = ch*index_bytes_per_vec(dim)/2**30
            print(f" | HNSW@{dim}d {gb:>6.2f} GB", end="")
        print()

print("\n=== C. embedding cost (one full index pass) ===")
# voyage-4 $0.06/M verified live docs.voyageai.com 2026-09-10; also src/core/embedding-pricing.ts
PRICES = {"voyage-4 (gbrain default)":0.06, "voyage-4-lite":0.02, "voyage-4-large":0.12,
          "openai text-embedding-3-large":0.13, "openai text-embedding-3-small":0.02}
for pages in (155795, 1_000_000):
    for cpp in (2.40, 4):
        tk = pages*cpp*TOK
        row = " ".join(f"{n.split()[0]}=${tk/1e6*p:,.2f}" for n,p in PRICES.items())
        print(f"{pages:>9,} pg x {cpp} c/pg = {tk/1e6:>8,.1f}M tok : {row}")

print("\n=== D. Tan's $100/mo claim, decomposed (docs/tutorials/company-brain.md:549) ===")
print("claim: ~$40/mo embeddings + ~$50/mo Anthropic synthesized answers, 25-person co.")
emb_tok = 40/0.06*1e6
print(f"  $40/mo at $0.06/M  = {emb_tok/1e6:,.0f}M embed tokens/mo = {emb_tok/TOK:,.0f} chunks/mo")
print(f"                     = {emb_tok/TOK/2.40:,.0f} NEW pages/mo = {emb_tok/TOK/2.40/25:,.0f} pages/person/mo"
      f" = {emb_tok/TOK/2.40/25/22:,.0f} pages/person/working-day")
full = 155795*2.40*TOK/1e6*0.06
print(f"  vs ONE full re-embed of the 155,795-page brain = ${full:,.2f}  -> $40/mo = {40/full:.1f}x full rebuild EVERY MONTH")
# query side
for mode,tokens in [("conservative ~4K",4000),("balanced ~10K",10000),("tokenmax ~20K",20000)]:
    for mdl,rate in [("Haiku 4.5",1.0),("Sonnet 5 (repo $3)",3.0),("Opus 5",5.0)]:
        q = 50/(tokens/1e6*rate)
        print(f"  $50/mo buys {q:>9,.0f} queries/mo ({mode:<17} @ {mdl:<19}) = {q/25/22:>7,.1f} q/person/working-day")

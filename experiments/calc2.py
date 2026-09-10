TOK, CPP, EMB = 400, 2.40, 0.06          # tok/chunk; chunks/page (measured); $/Mtok voyage-4
emb_page = CPP*TOK/1e6*EMB
print(f"embedding cost per page = {CPP}x{TOK} tok x ${EMB}/M = ${emb_page:.7f}")

print("\n=== E. LLM curation vs embedding, per page (repo's own receipts) ===")
rates = {"takes extraction, ACTUAL receipt ($361.49 / 28,256 pages)": 361.49/28256,
         "takes extraction, quoted rate (Azure GPT-5.5)":              0.033,
         "takes extraction, quoted rate (Opus-class)":                 0.260}
for k,v in rates.items():
    print(f"  {k:<55} ${v:.5f}/page = {v/emb_page:>7,.0f}x the embedding cost")

print("\n=== F. steady-state monthly cost, 25-person company ===")
print(f"{'new pages/person/day':>21} {'pages/mo':>9} {'embed$':>8} {'takes$(rcpt)':>13} {'takes$(.033)':>13} {'takes$(opus)':>13}")
for ppd in (1,2,5,10,20,50):
    pm = ppd*25*22
    print(f"{ppd:>21} {pm:>9,} {pm*emb_page:>8.2f} {pm*rates['takes extraction, ACTUAL receipt ($361.49 / 28,256 pages)']:>13,.2f}"
          f" {pm*0.033:>13,.2f} {pm*0.260:>13,.2f}")
print("  (ONE of 25 dream-cycle phases. Excludes synthesize, extract_facts, extract_atoms,")
print("   propose_takes, grade_takes, patterns, synthesize_concepts, enrich_thin, skillopt, drift.)")

print("\n=== G. contradiction probe ===")
IN,OUT,HIN,HOUT = 500,80,1.0,5.0        # docs/contradictions.md + cost-tracker.ts defaults
call = IN/1e6*HIN + OUT/1e6*HOUT
print(f"  judge call = {IN} in x $1/M + {OUT} out x $5/M = ${call:.5f}")
print(f"  docs/contradictions.md claims ~$0.0006/call -> understates its own inputs by {call/0.0006:.2f}x")
for pages in (155795,1_000_000):
    ch = pages*CPP; pairs = ch*(ch-1)/2
    print(f"  {pages:>9,} pages -> {ch:>10,.0f} chunks -> {pairs:>18,.0f} unordered pairs"
          f" -> exhaustive judging = ${pairs*call:>18,.0f}")
nightly = 50*5.6                          # ~50 queries/night, ~5.6 judge calls/query ($0.005/query)
print(f"  actual nightly sample: 50 queries x ~5.6 calls = {nightly:.0f} calls = ${nightly*call:.2f}/night = ${nightly*call*30:.2f}/mo")
print(f"  -> that sample covers {nightly/ (155795*CPP*(155795*CPP-1)/2)*100:.2e}% of the pair space at 155,795 pages")

print("\n=== H. what $100/mo actually buys (all-in, 25 people) ===")
budget=100
for label,cost in [("Supabase Pro + Large compute (8GB RAM, holds the 2.85GB index)", 25+110),
                   ("Supabase Pro + XL (16GB RAM)", 25+210),
                   ("Supabase Pro + 2XL (32GB, needed at 1M pages/18.3GB index)", 25+410)]:
    print(f"  hosting alone: {label:<62} ${cost}/mo  -> {'OVER' if cost>budget else 'under'} the whole $100 AI budget")

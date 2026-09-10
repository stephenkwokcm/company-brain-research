# skeptic-claims — Fact-check and stress-test of Garry Tan, "Every company should have a Brain"

Talk: AI Engineer channel, YouTube `eBUyTS7SzV4`, published 2026-07-16. Checked 2026-09-10.
Method: every claim below was chased to a primary or near-primary source. Ratings: **verified / plausible / unverified / contradicted**.

---

## TL;DR

1. **The checkable third-party facts check out; the load-bearing personal numbers do not.** Emergent, Retell AI and the "25% of W25 at 95% AI-generated code" line are all real and sourceable. The 400X / 8X-floor / 220,000-pages claims are self-measured, unaudited, and in two cases inconsistent with his own published artifacts.
2. **"8X at the floor" is contradicted by the only controlled evidence that exists.** METR's RCT found early-2025 AI made experienced devs **19% slower**; its Feb-2026 re-run estimates ~18% *faster* for returning devs with wide error bars; its May-2026 survey of 349 technical workers found a **median self-reported 1.4–2x value gain and 3x speed gain**. Tan's floor is ~3x above the best population estimate and his headline is ~130x above it.
3. **"That kind of revenue per head did not exist before — not in software, not in oil" is simply false.** Retell's $1.2–1.5M/employee is below Google, Meta, Apple and Netflix, and an order of magnitude below Craigslist (~$13.9M) and Saudi Aramco (~$5.9–6.4M). What is genuinely new is the *velocity* to that level, not the level. He conflated the two.
4. **His own repo is the strongest evidence against "it's more than RAG."** GBrain's README states that on the public LongMemEval benchmark "**Pure vector on the same corpus scored 93.8% … so the hybrid layer is roughly neutral on this benchmark**." The +31.4-point lift over vector-only RAG appears only on BrainBench — a 240-page corpus the project generated with Claude Opus and scores itself on.
5. **The failure modes he lists are only half-solved by his own tool, and nobody in the category has a public benchmark for the part that matters.** GBrain ships real hygiene machinery (contradiction eval, dream cycle, provenance, gap analysis) — more than most competitors — but its open-issue list includes that machinery silently failing, and two YC "company brain" Launch HN threads from 2026 show founders conceding they have no formal benchmarks against plain enterprise search.

---

## Claim-by-claim

### 1. "400X my 2013 output" — **unverified, methodologically unsound**
He anchors on "about 14 usable logical lines of code a day" in 2013. That baseline is defensible: Fred Brooks' classic figure is ~10 LOC/day and Capers Jones puts sustained professional output at 325–750 LOC/month (≈16–38/day) ([successfulsoftware.net](https://successfulsoftware.net/2017/02/10/how-much-code-can-a-coder-code/), [dzone](https://dzone.com/articles/programmer-productivity)). The multiplier is not. 400 × 14 = 5,600 LOC/day, but Tan elsewhere claims **37,000 lines/day and 600,000 lines in 60 days**, which against the same baseline is ~2,600X — his own numbers do not reconcile, so "400X" is not a clean LOC ratio and he never says what it is a ratio *of*.

An independent audit exists. Fast Company, "Y Combinator's CEO says he ships 37,000 lines of AI code per day. A developer looked under the hood" ([link](https://www.fastcompany.com/91520702/y-combinator-garry-tan-agentic-ai-social-media), on HN 2026-04-03 and again 2026-06-05): Polish engineer *Gregorein* audited Tan's personal blog and found **78,400 lines of AI-generated code**, a page load of **169 requests / 6.42 MB** against Hacker News' 7 requests / 12 KB — **535x heavier than the site YC itself runs** — plus ~2 MB uncompressed PNGs, a rich-text editor loaded on a read-only page, an empty CSS file, and ad-blocker-evading analytics. Verdict quoted: "Bloat, waste, and rookie mistakes" ([laterstack summary](https://laterstack.com/garry-tan-37000-lines-ai-slop-vibe-coding/)). A separate essay, ["Garry Tan, LOC-maxxing and code abundance"](https://blog.curiouscircle.com/garry-tan-loc-maxxing-and-code-abundance/), makes the conceptual point: "generated > reviewed > merged > production LOC can diverge massively."

Note that Tan's own pre-emptive defense ("assume half is scaffolding") does not address this. The audit's finding is not that half the code is scaffolding; it is that the *shipped artifact* is worse than the hand-written equivalent. A verbosity discount cannot fix a quality regression.

### 2. "Still 8X at the floor and 80X in the middle" — **contradicted (as a general claim)**
- METR RCT, 2025-07-10: 16 experienced open-source developers, AI use made them **19% slower** (CI +2% to +39%) while they *believed* they were 20% faster. [metr.org](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- METR update, 2026-02-24: the follow-up experiment is unreliable due to selection effects (devs refusing to work without AI; pay cut $150→$50/hr). Raw: **−18% time for returning devs (CI −38% to +9%)**, **−4% for new recruits (CI −15% to +9%)**. [metr.org](https://metr.org/blog/2026-02-24-uplift-update/)
- METR survey, 2026-05-11: 349 technical workers. **Median self-reported value gain 1.4–2x; median self-reported speed gain 3x**; forecast 2.5x value by March 2027. METR explicitly expects speed self-reports to *overstate* value. [metr.org](https://metr.org/blog/2026-05-11-ai-usage-survey/)

Fair to Tan: he is claiming his own output on a bespoke stack, not a population mean. Not fair to Tan: he generalizes explicitly — "your whole org will be wired to run at about 400X," and "you're doing a former person's entire year worth of work in a single day … that's actually the bar right now" (~250X). As a population claim, 8X-floor is roughly 3x above the median *self-reported speed* gain, which is itself the most inflated available measure.

### 3. "Winter 25: a quarter of companies had 95% AI-generated codebases" — **verified as a statement, unaudited as a fact**
Jared Friedman, YC managing partner, 2025-03-06, in the "Vibe Coding Is the Future" video: for ~25% of the W25 batch, 95%+ of the codebase is AI-generated, excluding library-import code. [TechCrunch](https://techcrunch.com/2025/03/06/a-quarter-of-startups-in-ycs-current-cohort-have-codebases-that-are-almost-entirely-ai-generated), [Techmeme](https://www.techmeme.com/250306/p24). This is a partner's estimate over a self-selected cohort, not an instrumented measurement.

### 4. "That batch has become the fastest-growing, most profitable batch in YC history" — **plausible, but the sourcing is circular and the tense has drifted**
The only source is Tan himself, to CNBC on **2025-03-15** — i.e. *during* the batch, around Demo Day — saying the batch was growing "10% week on week" in aggregate and "that's never happened before in early-stage venture" ([CNBC](https://www.cnbc.com/2025/03/15/y-combinator-startups-are-fastest-growing-in-fund-history-because-of-ai.html)). In an August 2026 retelling the claim is hedged to "on track to becoming one of the fastest growing, most profitable batches" ([the-ai-corner, 2026-08-31](https://www.the-ai-corner.com/p/garry-tan-personal-agi)); in this July 2026 talk it is stated as settled history. No audited data, no control group, and 2025 was the peak year for AI seed funding — a confound Tan partly concedes ("I can't prove that the AI-generated code caused the growth").

### 5. "94 companies have crossed $100M in revenue from a seed check" — **unverified**
No public YC source found. The unit is ambiguous (annual revenue vs. ARR vs. cumulative). For scale, YC has funded ~5,668 companies with 82 unicorns and 17 IPOs ([ellenox compilation](https://www.ellenox.com/post/y-combinator-statistics-and-insights), secondary source, low confidence), so 94 is ~1.7% — not implausible, but it rests entirely on internal YC data.

### 6. Emergent: "nine figures of ARR in eight months; 15 people at $15M ARR" — **verified / unverified split**
**Verified:** Emergent is **YC Summer 2024** ([YC directory](https://www.ycombinator.com/companies/emergent)) and announced **>$100M ARR eight months after launch on 2026-02-17** — 6M users, 150k paying customers, $70M Series B (Jan 2026, SoftBank Vision Fund 2 + Khosla) ([TechCrunch](https://techcrunch.com/2026/02/17/emergent-hits-100m-arr-eight-months-after-launch-rolls-out-mobile-app), [BusinessWire](https://www.businesswire.com/news/home/20260217938088/en/)). **Caveat TechCrunch itself flags:** this is *annual run-rate*, an annualized projection, not booked revenue — for a consumer-ish vibe-coding product with 70% no-prior-coding users, churn risk is material and unaddressed.
**Unverified:** the "15 people at $15M ARR" headcount. It appears only in Tan's own retellings. TechCrunch did not disclose headcount.
The talk transcript says "Emergence" — this is a mis-transcription of **Emergent** (there is an unrelated "Emergence AI").

### 7. "Retail out of Winter 24, at $60M with about 40 people" — **verified, name corrected**
"Retail" is a mis-transcription of **Retell AI**, YC **W24** ([YC directory](https://www.ycombinator.com/companies/retell-ai)). ~$60M ARR by ~April 2026, up from ~$5M at the start of 2025 (~650% YoY) on ~$5M total funding, with ~40 staff ([TipRanks](https://www.tipranks.com/news/private-companies/retell-ai-triples-arr-to-60-million-as-voice-agent-adoption-surges)). YC's directory now lists **team size 50**, so the ratio is $1.2–1.5M/head.

### 8. "That kind of revenue per head did not exist before. Not in software, not in oil, not in railroads, never." — **contradicted**
| Company | Revenue/employee | Source |
|---|---|---|
| VICI Properties (27 employees) | ~$142M | [ondeck ranking](https://www.ondeck.com/resources/revenue-per-employee-ranking) |
| OnlyFans / Fenix Intl | ~$30.1M | [Benzinga](https://www.benzinga.com/news/24/09/40865004/) |
| Craigslist (~50 FTE) | ~$13.9M | [widely cited IAB-derived figure](https://x.com/TrungTPhan/status/1833881502041641099) |
| McKesson | ~$8.2M | ondeck |
| Saudi Aramco (FY2025 $445.7B / >76,000) | ~$5.9–6.4M | [Aramco FY2025 results](https://www.aramco.com/-/media/publications/corporate-reports/reports-and-presentations/2025/fy/sections/ara-2025-results-english.pdf) |
| Apple / Netflix / Meta / Google | $2.6M–$1.7M | Trung Phan compilation |
| **Retell AI** | **$1.2–1.5M** | above |

Retell is not merely non-record-breaking; it is *below Google*. Emergent at $100M ARR would need fewer than ~7 employees to beat Craigslist. The defensible version of Tan's claim is about **time-to-that-ratio**, not the ratio. (A related trap: the famous "Instagram, 13 people" and "WhatsApp, 55 people" comparisons are *valuation* per head, not revenue per head — I did not re-verify their revenue figures this session, so treat that aside as low confidence.)

### 9. "A million tokens — that's about a thousand pages … three Harry Potter books" — **partly contradicted (understated), and self-undermining**
1M tokens ≈ 750,000 words ≈ **2,000–3,200 pages**, not 1,000. The full 7-book Harry Potter series is ~1.08M words over ~3,400 pages, so 1M tokens ≈ 70% of the *series* (~5 average books) — unless you pick the three longest, in which case "three books" is about right ([Raschka on HP book 1 = 76,944 words ≈ 100k tokens](https://x.com/rasbt/status/1656724322164015105)). This is the one number he understates.

The deeper problem is conceptual: nominal context ≠ usable context. An agent does not meaningfully "hold three Harry Potter books in its head" — which is precisely why GBrain exists and why its own retrieval budget is **k=5 chunks**. The metaphor argues against the product.

### 10. "Seven plus or minus two … it's why local phone numbers are seven digits" — **half verified, half urban legend**
Miller (1956) is real and correctly cited ([Miller, Psych Review](https://psychclassics.yorku.ca/Miller/)). But the modern estimate is **Cowan (2001), "The magical number 4 in short-term memory," 4±1 chunks** when rehearsal and long-term-memory support are controlled (~6,600 citations; [ResearchGate](https://www.researchgate.net/publication/11830840), [Journal of Cognition review](https://journalofcognition.org/articles/10.5334/joc.387)). The phone-number line is **contradicted**: Bell/AT&T standardized 7-digit numbering in **1947**, nine years before Miller's paper ([Wikipedia, Seven-digit dialing](https://en.wikipedia.org/wiki/Seven-digit_dialing)); Miller himself called the recurrence of seven a "pernicious, Pythagorean coincidence." Also note both numbers count *chunks*, not items — which quietly breaks the "7 digits vs. 3 Harry Potter books" comparison, since a human chunk can be an entire schema and a token cannot.

### 11. "About 220,000 pages" — **unverified and inconsistent with his own repo**
The GBrain README — last touched **2026-09-08**, two months *after* the talk — states his production brain is "**155,795 pages, 24,589 people, 5,340 companies**, 66 cron jobs" ([README](https://github.com/garrytan/gbrain)). The talk claims 220,000. Either the README is stale, the units differ (pages vs. files vs. chunks), or the talk number is inflated. As published they conflict.

### 12. The friend's "80,000 markdown files" epilepsy brain — **unverified** (unnamed anecdote, no traceable source).

---

## Relevance to company-brain / RAG / fruit-fly question

**Is "company brain" materially different from RAG + memory systems already shipping?** Tan's framing — retrieval is the primitive, the product is what gets written down, enrichment, hot-vs-cold, arbitration — is a fair description of a real design problem. It is not a new category and it is not his. The field already calls this *agentic memory*, and GBrain's own comparison table benchmarks against **Mem0, Zep, Mastra, MemCog, Supermemory, ContextFit, MemPalace, Lethe, agentmemory** and more ([gbrain-evals/docs/comparison-systems.md](https://github.com/garrytan/gbrain-evals/blob/main/docs/comparison-systems.md), updated 2026-09-09). Glean has shipped enterprise search over a knowledge graph for years.

The decisive evidence is in GBrain's own README: on **LongMemEval-S** (v0.48.4.0, measured 2026-09-06, 470 scored questions), gbrain scores **93.40% strict recall_all@5** with the reranker off and **95.53%** with it on — and then states plainly: "*Pure vector on the same corpus scored 93.8% (v0.48.0.0 receipt), so the hybrid layer is roughly neutral on this benchmark and earns its keep elsewhere.*" The headline "+31.4 points P@5 over vector-only RAG" is measured **only on BrainBench**, a 240-page corpus *generated by Claude Opus* and scored by the project against its own committed baseline ([BRAINBENCH.md](https://github.com/garrytan/gbrain/blob/master/docs/eval/BRAINBENCH.md)). So on the one public benchmark, the brain layer buys nothing over plain vector RAG; the lift exists only on a self-authored synthetic corpus.

To GBrain's genuine credit, its evals doc is the most epistemically careful artifact in the whole category — it explicitly separates any-hit recall, strict recall, precision and LLM-judged answer accuracy, and refuses to rank itself against vendors using different protocols. The rigor in the repo is much higher than the rhetoric in the talk.

Practitioners are asking the same question. On **Launch HN: Hyper (YC P26) — "Company brain to power agentic development"** (2026-06-03, [item 48387095](https://news.ycombinator.com/item?id=48387095)), `esafak` asked: "Have you measured the value provided by the knowledge graph layer over straight enterprise search (e.g., Glean)? Benchmarks, please" — then, discovering Glean also uses knowledge graphs, "what is your differentiation?" The founder's contradiction-arbitration answer was "always trust humans, and trust recent human info more than old human info." On **Launch HN: Almanac (YC S26)** (2026-08-31, [item 49511007](https://news.ycombinator.com/item?id=49511007)), `htrp` listed ~28 direct competitors; the founder answered "We do not have formal benchmarks to measure improvement in performance"; another commenter: "Looks identical to Claude Desktop connectors."

**Are the failure modes he lists solved by his own tool?** Partially — more than any competitor, and still not solved. GBrain does ship provenance, `gbrain eval suspected-contradictions` wired into a nightly "dream cycle," citation fixing, gap analysis in `gbrain think`, per-result `evidence` tags and `create_safety` hints, and git-as-system-of-record with soft deletes. But of 174 open issues on 2026-09-10, several are the hygiene layer itself failing: "*[dream] Native transcript ingestion never reaches Dream, silently disabling its core conversation-to-wiki synthesis*" (2026-08-21); "*hybrid search returns identical results regardless of input query*" (2026-08-03); "*atom_provenance_drift: what is the intended way to retire source_changed atoms?*" (2026-09-06); "*Single-source sync never consults the source's stored strategy → mass soft-delete of code pages*" (2026-09-01). And the "librarian" remains a human job the tool delegates back to you. A competitor's review (disclose the conflict — [Vectorize, 2026-05-08](https://vectorize.io/articles/gbrain-review)) adds: single-operator design, no managed cloud, first-class support only for OpenClaw and Hermes, v0.30-era breaking changes. That review is now four months stale against v0.48.

**Ecosystem sanity check (all verified via GitHub API, 2026-09-10):** `garrytan/gbrain` — created 2026-04-05, MIT, TypeScript, **29,764 stars / 4,441 forks / 174 open issues**, default branch `master`. `garrytan/gstack` — 132,248 stars, created 2026-03-11. `openclaw/openclaw` — 389,291 stars, created 2025-11-24. `NousResearch/hermes-agent` — 243,760 stars. All real; the harnesses he names exist and are enormous.

---

## Open questions

1. What exactly is the denominator in "400X"? Lines? Tasks? Business outcomes? Without a definition it is unfalsifiable, and his own 37,000-LOC/day figure implies ~2,600X against the same 2013 baseline.
2. Is there any audited data behind "94 companies over $100M" and "fastest-growing, most profitable batch"? Both are internal YC numbers with no external verification path.
3. Why does the July 2026 talk say 220,000 pages while the September 2026 README says 155,795? Different units, or drift?
4. Emergent's reported post-Series-B valuation (~$300M, Jan 2026) against >$100M ARR (Feb 2026) is a ~3x multiple — implausibly low for that growth rate. Either a reporting artifact or a signal that investors heavily discount the run-rate. Worth a separate check.
5. **Nobody has run the experiment that matters.** Does a curated, provenance-tracked, contradiction-checked corporate brain beat a well-tuned BM25+vector baseline on real organizational questions? Every vendor in the category, including GBrain, currently answers with anecdote or a self-authored corpus.
6. I found **no rigorous quantitative critique of the "company brain / AI-native org" thesis itself** — only critiques of the LOC claim. That is a genuine gap in the literature as of 2026-09-10.

---

## Sources

- Transcript: `sources/transcript_eBUyTS7SzV4.txt` (YouTube `eBUyTS7SzV4`, 2026-07-16)
- Fast Company, Tan 37,000 LOC/day audit — https://www.fastcompany.com/91520702/y-combinator-garry-tan-agentic-ai-social-media
- Laterstack summary of the Gregorein audit — https://laterstack.com/garry-tan-37000-lines-ai-slop-vibe-coding/
- Curious Circle, "LOC-maxxing" — https://blog.curiouscircle.com/garry-tan-loc-maxxing-and-code-abundance/
- METR RCT (19% slower) — https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- METR design change / 2026 numbers — https://metr.org/blog/2026-02-24-uplift-update/
- METR self-report survey (1.4–2x value, 3x speed) — https://metr.org/blog/2026-05-11-ai-usage-survey/
- TechCrunch, 25% of W25 at 95% AI code — https://techcrunch.com/2025/03/06/a-quarter-of-startups-in-ycs-current-cohort-have-codebases-that-are-almost-entirely-ai-generated
- Techmeme record of Friedman quote — https://www.techmeme.com/250306/p24
- CNBC, fastest-growing batch (2025-03-15) — https://www.cnbc.com/2025/03/15/y-combinator-startups-are-fastest-growing-in-fund-history-because-of-ai.html
- TechCrunch, Emergent $100M ARR — https://techcrunch.com/2026/02/17/emergent-hits-100m-arr-eight-months-after-launch-rolls-out-mobile-app
- BusinessWire, Emergent — https://www.businesswire.com/news/home/20260217938088/en/
- YC directory, Emergent (S24) — https://www.ycombinator.com/companies/emergent
- YC directory, Retell AI (W24, team 50) — https://www.ycombinator.com/companies/retell-ai
- TipRanks, Retell $60M ARR — https://www.tipranks.com/news/private-companies/retell-ai-triples-arr-to-60-million-as-voice-agent-adoption-surges
- Aramco FY2025 results — https://www.aramco.com/-/media/publications/corporate-reports/reports-and-presentations/2025/fy/sections/ara-2025-results-english.pdf
- Revenue-per-employee rankings — https://www.ondeck.com/resources/revenue-per-employee-ranking
- Miller (1956) full text — https://psychclassics.yorku.ca/Miller/
- Cowan (2001), magical number 4 — https://www.researchgate.net/publication/11830840_The_Magical_Number_4_in_Short-Term_Memory_A_Reconsideration_of_Mental_Storage_Capacity
- Seven-digit dialing history — https://en.wikipedia.org/wiki/Seven-digit_dialing
- GBrain repo + README — https://github.com/garrytan/gbrain
- GBrain BrainBench methodology — https://github.com/garrytan/gbrain/blob/master/docs/eval/BRAINBENCH.md
- gbrain-evals comparison table — https://github.com/garrytan/gbrain-evals/blob/main/docs/comparison-systems.md
- Vectorize GBrain review (competitor) — https://vectorize.io/articles/gbrain-review
- Launch HN: Hyper (YC P26) — https://news.ycombinator.com/item?id=48387095
- Launch HN: Almanac (YC S26) — https://news.ycombinator.com/item?id=49511007
- HN, "More AI-generated code doesn't make your team faster" (Charity Majors / AWS) — https://news.ycombinator.com/item?id=48489835
- the-ai-corner recap (Aug 2026, hedged batch claim) — https://www.the-ai-corner.com/p/garry-tan-personal-agi
- StartupHub.ai talk coverage (2026-07-17) — https://www.startuphub.ai/ai-news/artificial-intelligence/2026/garry-tan-build-ai-native-companies-not-just-ai-users
- LOC productivity literature — https://successfulsoftware.net/2017/02/10/how-much-code-can-a-coder-code/

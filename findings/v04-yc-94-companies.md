# v04 — "94 companies," the W25 batch superlative, and the LOC/400X derivation

**Key:** `v04-yc-94-companies` · **Lens:** primary-source verification · **Date:** 2026-09-10
**Scope:** four claims from the AI Engineer talk (2026-07-16) and Tan's public LOC record.
**Method note:** this session's WebSearch budget was already exhausted (200/200) by earlier workers, so every search below was run through `curl` / `WebFetch` against **Y Combinator's own Algolia blog index**, the **YC company-directory Algolia index**, the **GitHub API/raw**, the **HN Algolia API**, and Brave (rate-limited after ~4 queries). Two paywalled/bot-blocked outlets (CNBC, Fast Company) were read via mirrors; both are flagged inline.

---

## Verdicts at a glance

| # | Claim | Verdict |
|---|---|---|
| **1** | "94 companies total have now crossed a hundred million in dollars in revenue from a seed check in the history of YC" (03:37) | **UNRESOLVED** — the *utterance* is confirmed verbatim; the *number* has **no YC-published source**, and the unit is undefined |
| **2** | "That batch has become the fastest-growing, most profitable batch in the history of YC" (W25, 03:31–03:37) | **PARTIALLY** — traceable to Tan-via-CNBC (2025-03-15), never independently verified, and **Tan himself downgraded it to a hedge three weeks after this talk** |
| **3** | Tan's "37,000 lines per day" LOC claim | **CONFIRMED that he said it** (X, 2026-03-30) — but **irreconcilable with his own two other public figures** from the same 3-week window (10–20K/day; 11,417 logical/day) |
| **4** | The 400X derivation in `gstack/docs/ON_THE_LOC_CONTROVERSY.md` | **CONFIRMED as the source** (408× is in the doc) — but the talk's "8X floor" is **not** the deflation the talk describes, and the doc's "run it yourself" reproduction path **does not work as published** |

---

## 1. "94 companies … $100M in revenue from a seed check" — UNRESOLVED

### 1a. The utterance is real and correctly transcribed

Three independent copies of the talk agree word-for-word:

- Local auto-caption JSON, segment at **t = 217.72 s**: `"YC. 94 companies total have now crossed"` → `"a hundred million in dollars in revenue"` → `"from a seed check in the history of YC."` (`sources/transcript_eBUyTS7SzV4.json`)
- Third-party archive: `plaktoz/kb`, `raw/archived/2026-07-17-video-every-company-should-have-a-brain-garry-tan-y-combinator.md`, line 48 — identical sentence.
- Third-party structured extraction: `senthilsweb/ai-agents`, `agents/talk-value-stats/db.json` — records `{"label": "Companies past $100M revenue", "value": 94.0, "unit": "companies", "confidence": "stated"}`.

All three ultimately descend from the same YouTube ASR track, so this establishes the transcription is stable, not that a human checked the audio. Residual ASR risk on the digits: low but non-zero.

### 1b. The number appears nowhere Y Combinator publishes

I ran exact-phrase queries (`advancedSyntax: true`, `typoTolerance: false`) against YC's own blog search index `ycdc_blog_production` (Algolia app `45BWZJ1SGC`; the index carries the **full post HTML**, and the blog listing reports **2,681 total posts**, including 2026 ones — an `EquipmentShare` query returns the 2026-01-23 post):

| Exact phrase | Hits in the entire YC blog |
|---|---|
| `"94 companies"` | **0** |
| `"seed check"` | **0** |
| `"hundred million"` | **0** |
| `"100 million in revenue"` | **0** |
| `"companies have crossed"` | **0** |
| `"$100 million in annual revenue"` | **0** |
| `"most profitable batch"` | **0** |
| `"fastest-growing, most profitable"` | **0** |

Controls returning hits confirm the index works: `"net revenue"` → 2 (both revenue-list posts), `"Top Companies"` → 49, `"$100M"` → 13, `EquipmentShare` → 6.

Additional negatives: `ycombinator.com/` and `/about` carry only valuation milestones; `ycombinator.com/topcompanies` and `/topcompanies/revenue` now redirect into the JS "YC Startup Directory" with no aggregate stat; the last **annual letter** on the blog is **2017**; the last batch-stats post with cumulative milestones is **YC Winter 2018 Stats** (2018-03-19) and it counts *valuations*, not revenue: *"15 YC alum are valued at over $1B and over 70 YC alum are valued at over $100M."* GitHub code search across all of `org:garrytan` for `"hundred million in dollars"` and `"94 companies"` → **0**.

### 1c. Tan dropped the claim from the next telling of the same passage

Three weeks later, at **Startup School 2026 (2026-08-06)**, Tan delivered the same argument. YC's own YouTube description for that talk links a full transcript. The corresponding passage reads:

> "And it's not just me. At YC, we get to watch this at portfolio scale. A year and a half ago, in the Winter '25 batch, a quarter of the companies had codebases that were 95% AI-generated. Those companies use AI agents for everything now, not just code. And that batch is on track to becoming one of the fastest growing, most profitable batches in the history of YC. **Now I know what a correlation is, so let me say it carefully.** I cannot prove that the AI-generated code and everything else caused the growth, but what I can tell you is that the fastest growing founders we fund are not treating AI as autocomplete."

The "94 companies / $100M / seed check" sentence — which in the AI Engineer talk sits **between** the batch superlative and the "I can't prove causation" caveat — **is simply gone**. Every neighbouring sentence survives. That is the single strongest signal available: the speaker himself did not repeat the number at the next opportunity.

### 1d. The unit is undefined, and YC's own published revenue methodology is stricter than the claim implies

The talk says only "a hundred million in dollars in revenue." Compare with the two things YC *has* published:

- **Inaugural YC Top Companies List by Revenue** (2023-06-27, by Garry Tan): 50 companies; *"The companies featured have all generated above a certain threshold of net revenue in 2022 and submitted **audited financials** reflecting 2022 full year **net revenue (not GMV, sales, or ARR)**."* Threshold undisclosed. Total 2022 revenue >$50B.
- **2024 YC Top Companies** (2024-04-30, by Garry Tan): *"The featured companies all generated above a certain threshold of revenue in 2023. **The companies opted-in** to being featured, so this isn't 100% reflective of…"* Total 2023 revenue $57.2B.

So YC's published revenue lists are (i) opt-in, (ii) threshold-undisclosed, (iii) explicitly **not ARR**. Meanwhile in the *Startup School* talk Tan uses "**annualized** revenue" precisely when he means run-rate ("Emergent … when they crossed $15 million in **annualized** revenue, they were 15 people"; "Retell … hit $60 million **annualized**"). He did **not** say "annualized" for the $100M claim — which cuts *toward* the stricter reading, but is far from a definition. "Have now crossed … in the history of YC" also reads as an **ever-crossed cumulative count** (including acquired and dead companies), a materially weaker bar than "currently at $100M+".

### 1e. A near-miss worth flagging so nobody mistakes it for corroboration

YC's live company directory (Algolia index `YCCompany_production`, **6,206 companies**) carries a boolean facet `top_company`, and it is currently **`true` for exactly 91 companies**. The proximity to 94 is tempting and **is not corroboration**: I pulled all 91 and the list is plainly not a $100M-revenue set — it includes Moxion Power (status `Inactive`), Notable Labs, Pardes Biosciences, OMGPop, GitPrime, Proxy, Cognito and Sqreen, none of which plausibly crossed $100M in revenue. It is a legacy curated/opt-in "Top Companies" flag, mixing valuation and exit criteria.

### 1f. Best estimate

Plausible but unaudited. YC has funded ~6,200 companies; 94 is ~1.5% of them. For scale, YC reported "more than 160 companies valued at $150M+" in **July 2021** and a third-party count of 271 on the 2023 list. A $100M *revenue* bar is stricter than a $150M *valuation* bar, so 94 all-time crossings is in a credible range — **if** it means "ever reached ~$100M of annual revenue or run-rate, on YC's internal Bookface data, including exits." Confidence that a number of roughly this magnitude is defensible: **medium (~65%)**. Confidence that "94" as stated is auditable from any public source: **~0%** — it isn't.

---

## 2. "Fastest-growing, most profitable batch in the history of YC" (W25) — PARTIALLY

**Origin traced.** The superlative is not new to the July 2026 talk. It is the **headline of a CNBC story from 2025-03-15**: *"Y Combinator startups are fastest growing, most profitable in fund history because of AI."* Body (CNBC is 403 to automated fetches; read via the Lifeboat Foundation republication dated 2025-03-22, which reproduces the lede verbatim):

> "Y Combinator CEO Garry Tan told CNBC that this group is growing significantly faster than past cohorts and with actual revenue. The winter 2025 batch of YC companies in aggregate grew 10% per week, he said. **"It's not just the number one or two companies — the whole batch is growing 10% week on week,"** said Tan… **"That's never happened before in early-stage venture."** That growth spurt is thanks to leaps in artificial intelligence, Tan said."

Three things follow:

1. **The source is Tan.** There is no independent measurement. YC does not publish batch-level growth or profitability; the blog has zero hits for `"most profitable batch"`.
2. **The measurement window is wrong for the July 2026 phrasing.** The 10%/week figure describes W25 *during or immediately after* the batch (March 2025, Demo Day). The talk's *"That batch **has become** the fastest-growing, most profitable batch in the history of YC"* presents a March-2025 in-batch observation as a settled 16-month retrospective result. Nothing published supports the retrospective version.
3. **Tan retracted the definite form himself, three weeks later.** At Startup School (2026-08-06) the same sentence became *"that batch is **on track to becoming one of** the fastest growing, most profitable batches in the history of YC."* Definite superlative → hedged, plural, forward-looking. Cite the AI Engineer wording only with that hedge attached.

**Adjacent claim that does check out:** *"a quarter of the companies had code bases that were 95% AI-generated"* is stable across both talks and matches the March 2025 CNBC coverage. Prior worker `skeptic-claims.md` also validates it. Treat it as CONFIRMED-as-reported.

---

## 3. "37,000 lines per day" — CONFIRMED as said, INCONSISTENT as a number

**He said it.** Primary artifact: the X post **https://x.com/garrytan/status/2038555792052506941**, dated **2026-03-30**. X is unfetchable without auth (nitter/xcancel/Wayback all failed here), but three independent attestations agree:

- **Hacker News submission 47577797** (2026-03-30T18:19:18Z), titled `Garry Tan: "37K LOC per day across 5 projects"`, linking that exact status ID (13 points, 3 comments).
- **Fast Company**, "Y Combinator's CEO says he ships 37,000 lines of AI code per day" (article ID 91520702; 403 direct, read through a text-extraction proxy): Tan posted on X that he and his agents deployed *"37,000 lines of code per day across five separate projects,"* calling it an *"Absolutely insane week for agentic engineering,"* and mentioned a 72-day shipping streak.
- **Laterstack** summary (2026-04-03): *"On March 30, Tan posted on X that he was 'on a 72-day shipping streak. Five projects. 37,000 lines of code per day.'"*

**It does not reconcile with his own other public numbers.** Three figures, all Tan's, all within 19 days:

| Date | Artifact | Figure | Per-day |
|---|---|---|---|
| ~Mar 2026 | `gstack/README.md` hero (commit `8ca950f6`) | "In the last 60 days: **600,000+ lines of production code** (35% tests), **10,000–20,000 lines per day**"; "last `/retro` across 3 projects: **140,751 lines added, 362 commits** in one week" | 10,000–20,000 raw (retro implies ~20,107) |
| 2026-03-30 | X post | "37,000 lines of code per day across five projects" | 37,000 raw |
| 2026-04-18 | `docs/ON_THE_LOC_CONTROVERSY.md` | "1,233,062 logical SLOC / 108 days" | **11,417 logical** |

The README's own ceiling (20,000/day) is **1.85× below** the X post. Raw-vs-logical does not close the gap either: stripping blanks and single-line comments typically costs ~1.3–1.6×, but 37,000 → 11,417 requires **3.24×**. The doc itself never publishes a raw-lines-added figure that would let you check. Net: **"37,000 lines per day" is not a measurement that survives contact with Tan's own two other published measurements**, and the talk's later restatement (400X, implying ~5,708 deflated logical lines/day) is the most conservative of the four.

**The audit of the output is real and negative.** Polish engineer *Gregorein* audited Tan's personal blog: **78,400 lines** of AI-generated code, **169 requests / 6.42 MB** per page load against Hacker News' 7 requests / 12 KB (**~535× heavier**), 28 test files (300 KB) shipped to browsers, 78 unused JS controllers on the homepage, uncompressed PNGs, an empty 0-byte logo file, an empty CSS file, and analytics proxied to evade ad blockers. Verdict quoted: *"Bloat, waste, and rookie mistakes."*

---

## 4. The 400X derivation — CONFIRMED as sourced, with four defects

Primary source fetched in full: `https://raw.githubusercontent.com/garrytan/gstack/main/docs/ON_THE_LOC_CONTROVERSY.md`. Committed **2026-04-18T07:05:42Z** (`0a803f9e`, "feat: gstack v1 — simpler prompts + real LOC receipts"), consistent with its own "2026 is day 108 as of this writing (April 18)."

**The arithmetic, verbatim from the doc:**

| | 2013 (full year) | 2026 (108 days) | Multiple |
|---|---:|---:|---:|
| Logical SLOC | 5,143 | 1,233,062 | 240× |
| Logical SLOC/day | 14 | 11,417 | **810×** |
| Commits | 71 | 351 | 4.9× |

Then: *"Assume AI-generated code is 2× more verbose … My 2026 per-day rate, NCLOC: 11,417 · With 2× AI-verbosity deflation: 5,708 · **Multiple on daily pace with both deflations: 408×**"*, followed by the ladder *"At 5× deflation: 162× · At 10× (pathological): 81× · At 100× (impossible — that's one line per minute sustained): 8×."*

**The talk is reading this ladder off the page.** Talk (02:32–02:56): "about **400X**" → doc's **408×**. "**80X** in the middle" → doc's **81×** (10× deflation). "**8X** at the floor" → doc's **8×** (100× deflation). Same three rungs, same order. The lineage is not in doubt. The same numbers are still the gstack README hero today: *"my 2026 run rate is ~810× my 2013 pace (11,417 vs 14 logical lines/day) … 240× the entire 2013 year … Measured across 40 public + private `garrytan/*` repos including Bookface."*

### Defect 1 — the talk's stated deflation and its stated floor are different deflations

Talk: *"Take the most pathological verbosity penalty you can stomach … **Assume half of it is scaffolding.** Assume I'm flattering myself. **It's still 8X at the floor and 80X in the middle.**"*

"Assume half of it is scaffolding" is a **2× deflation**, and 2× in the doc yields **408×**, not 8×. The 8× rung requires a **100× deflation** — which the doc's own parenthetical calls *"impossible — that's one line per minute sustained."* So the talk presents as a conservative floor a number that its own source document classifies as arithmetically impossible, while describing a deflation (2×) that in fact lands on the headline number. The 8X/80X "self-deflation" therefore does not do the epistemic work it appears to do; it widens the range until it constrains nothing.

### Defect 2 — the published reproduction script cannot produce the published number

The doc says *"Run it yourself"* and links `scripts/garry-output-comparison.ts`. I fetched it (434 lines). Its own docstring and `caveats_global` say:

- *"non-blank, non-comment lines added across authored commits **in public repos**"*
- *"**Public repos only.** Private work at both eras is excluded to make the comparison apples-to-apples."*
- *"**This script analyzes a single repo at a time.** Full 2013-vs-2026 picture requires running against every public repo with commits in both years and summing results (**future work**)."*
- `main()` comment: *"For V1, we analyze the single repo at `repoRoot`. **Future work:** enumerate public repos via GitHub API + clone each into a cache dir."*

The prose, by contrast, claims a run *"across all 41 repos owned by `garrytan/*` … **15 public, 26 private**"*, including the private 2013 Bookface corpus. The shipped tool is a **single-repo, public-only** utility whose aggregation step is explicitly unbuilt. A third party running it as published cannot reach 1,233,062 or 810× — at best they can reproduce ~15/41 of the corpus, one repo at a time, by hand-summing.

### Defect 3 — the receipt is not committed

The script writes `docs/throughput-2013-vs-2026.json`. That file is **404 on `raw.githubusercontent.com` and absent from the GitHub API listing of `docs/`** (27 entries; not among them). The commit that added the doc is titled *"real LOC receipts."* There is no receipt in the repo.

### Defect 4 — baseline sensitivity, conceded by the author

The doc concedes: *"If the true 2013 rate was 50/day instead of 14, the multiple at current pace is **228×** instead of 810×"* — i.e. a single defensible change to an unverifiable baseline moves the headline by 3.5×. It also concedes greenfield ≠ maintenance, that *"quality-adjusted productivity isn't fully proven,"* and that *"time to first user is the metric that matters, not LOC."*

**To Tan's credit, and worth recording:** the doc pre-registers its own weaknesses, publishes a 2.0% revert rate (7/351 commits) and 6.3% post-merge fix rate, and self-reports that Ben Vinegar's `slop-scan` scored gstack **5.24 — "the worst he'd measured at the time"** — before he cut it 62%. Reporting an adversarial tool's worst-ever score against yourself is not the behaviour of someone hiding the ball.

---

## What this changes for the synthesis

1. **Do not cite "94 companies" as evidence for anything.** It is a stage number with no published basis, an undefined unit, and — decisively — Tan **dropped it** from the next delivery of the same argument. If the synthesis mentions it, mention that.
2. **Downgrade the W25 superlative to its hedged form.** The defensible sentence is Tan's own August wording: *"on track to becoming one of the fastest growing, most profitable batches."* The 10%/week figure has a date (March 2025) and a single source (Tan).
3. **The "400X" spine is a documented derivation, not a measurement, and its stated floor is mis-derived.** The talk's honesty move ("8X at the floor") is the doc's "impossible" row; the deflation the talk actually describes (half is scaffolding) lands on 408×. Combined with three mutually inconsistent LOC/day figures inside 19 days, no committed receipt, and a reproduction script whose aggregation is unbuilt, the number cannot bear weight in an argument about whether a company brain works.
4. **Keep the checkable third-party facts.** "25% of W25 at 95% AI-generated code," Emergent, and Retell survive. Prior reports' pattern holds: **the incidental numbers check out; the load-bearing personal and portfolio numbers do not.**

---

## Open questions I could not close

- The verbatim text of the 2026-03-30 X post (X, nitter mirrors, Wayback and Memento all unreachable from here). Three secondary attestations agree; confidence the quote is accurate: **high (~90%)**.
- Whether the CNBC piece contains additional W25 profitability detail beyond the lede (CNBC 403; only the Lifeboat republication of the lede was readable).
- Whether Tan repeated "94 companies" in the a16z appearance ("New Rules for Founders", YouTube `fsTtKywmWlU`, ~Aug 2026) — no transcript is published and YouTube caption endpoints now require a PoT token, so this is untested.
- The raw (non-logical) lines-added figure from Tan's own script, which is the one number that would let anyone test whether 37,000/day and 11,417 logical/day are the same measurement. It is computed by the script (`raw_lines_added`) and never published.

---

## Sources

**Primary — the talk and its restatements**
- Talk transcript (local): `sources/transcript_eBUyTS7SzV4.{txt,json}` — segment t=217.72s · video: https://www.youtube.com/watch?v=eBUyTS7SzV4 (AI Engineer, published 2026-07-16T18:00:06-07:00)
- Independent transcript archive: https://raw.githubusercontent.com/plaktoz/kb/main/raw/archived/2026-07-17-video-every-company-should-have-a-brain-garry-tan-y-combinator.md (line 48)
- Independent structured extraction: https://raw.githubusercontent.com/senthilsweb/ai-agents/main/agents/talk-value-stats/db.json
- Startup School 2026 transcript (linked from YC's own video description): https://www.ycrootaccess.com/p/garry-tan-own-your-intelligence (2026-08-06) · video: https://www.youtube.com/watch?v=eRrc1pUY5oU

**Primary — Y Combinator**
- YC blog full-text index (Algolia app `45BWZJ1SGC`, index `ycdc_blog_production`), queried 2026-09-10 — exact-phrase negatives listed in §1b · https://www.ycombinator.com/blog
- https://www.ycombinator.com/blog/yc-top-companies-list-by-revenue (2023-06-27, Garry Tan) — audited full-year **net revenue**, "not GMV, sales, or ARR"
- https://www.ycombinator.com/blog/yc-top-companies-2024 (2024-04-30, Garry Tan) — opt-in, undisclosed threshold, $57.2B total 2023 revenue
- https://www.ycombinator.com/blog/top-companies-july-2021 — "more than 160 companies valued at $150M+"
- https://www.ycombinator.com/blog/yc-winter-2018-stats — "over 70 YC alum are valued at over $100M" (valuation, not revenue)
- https://www.ycombinator.com/blog/the-3-newest-companies-on-ycs-top-revenue-list-and-what-theyre-doing-so-right (2023-07-06)
- YC company directory (Algolia index `YCCompany_production`), queried 2026-09-10: 6,206 companies; facet `top_company` = 91 true / 6,114 false · https://www.ycombinator.com/companies

**Primary — gstack repo**
- https://github.com/garrytan/gstack/blob/main/docs/ON_THE_LOC_CONTROVERSY.md (raw fetched; commit `0a803f9e`, 2026-04-18T07:05:42Z)
- https://github.com/garrytan/gstack/blob/main/scripts/garry-output-comparison.ts (434 lines; "public repos only", single-repo, aggregation "future work")
- `docs/throughput-2013-vs-2026.json` — **404 / absent from the repo** (GitHub API `repos/garrytan/gstack/contents/docs`)
- https://github.com/garrytan/gstack/blob/main/README.md (current: 810× / 240× / "40 public + private repos")
- gstack README at commit `8ca950f6f1ee5833d92603d3e5fce9cfa9b2b472` (pre-2026-04-10): "600,000+ lines of production code (35% tests), 10,000-20,000 lines per day … 140,751 lines added, 362 commits … in one week"
- Critique that triggered the rewrite, cited in the script docstring: https://x.com/LouiseDSadeleer/status/2045139351227478199

**Secondary — the LOC claim and its audit**
- X post (unfetchable, cited by ID): https://x.com/garrytan/status/2038555792052506941 (2026-03-30)
- https://news.ycombinator.com/item?id=47577797 — HN submission titled `Garry Tan: "37K LOC per day across 5 projects"`, 2026-03-30T18:19:18Z
- https://www.fastcompany.com/91520702/y-combinator-garry-tan-agentic-ai-social-media — "Y Combinator's CEO says he ships 37,000 lines of AI code per day" (403 direct; read via text-extraction proxy)
- https://laterstack.com/garry-tan-37000-lines-ai-slop-vibe-coding/ (2026-04-03) — Gregorein audit summary
- https://github.com/benvinegar/slop-scan

**Secondary — the W25 batch superlative**
- https://www.cnbc.com/2025/03/15/y-combinator-startups-are-fastest-growing-in-fund-history-because-of-ai.html (2025-03-15; 403 to automated fetch)
- https://lifeboat.com/blog/2025/03/y-combinator-startups-are-fastest-growing-most-profitable-in-fund-history-because-of-ai (2025-03-22 republication reproducing the CNBC lede and Tan quotes verbatim)
- https://www.nbcconnecticut.com/news/business/money-report/y-combinator-startups-are-fastest-growing-most-profitable-in-fund-history-because-of-ai/3521347/ (CNBC syndication; 403)

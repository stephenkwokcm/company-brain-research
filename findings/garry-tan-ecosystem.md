# Garry Tan ecosystem map — GBrain, gstack, OpenClaw, Hermes, "skillify", and the 400X backlash

Research key: `garry-tan-ecosystem` · Compiled 2026-09-10 · All repo metrics pulled live from the GitHub REST API on 2026-09-10.

## TL;DR

- **GBrain is real and large.** [github.com/garrytan/gbrain](https://github.com/garrytan/gbrain) — MIT, TypeScript, created **2026-04-05**, **29,763 stars / 4,441 forks / 173 open issues**, latest release **v0.48.5.0 (2026-09-08)**, **85 entries under `skills/`**. It is the *second* Tan repo of this shape; the first, [gstack](https://github.com/garrytan/gstack) (created 2026-03-11), is at **132,245 stars**.
- **The talk is the mid-point of a 6-month campaign, not a launch.** Order: gstack (Mar 11) → "Thin Harness, Fat Skills" essay (Apr 9–11) → GBrain (Apr 5) → "Skillify" X post (~Apr 21) → YC RFS "Company Brain" by Tom Blomfield (Summer 2026) → AI Engineer World's Fair talk (Jul 16–17) → "Own Your Intelligence" at Startup School (Aug 6) → a16z podcast (Aug).
- **"OpenClaw / Hermes agent" are two third-party harnesses, not Tan's.** OpenClaw is Peter Steinberger's agent ([openclaw/openclaw](https://github.com/openclaw/openclaw), **389,291 stars**, created 2025-11-24); Hermes is Nous Research's ([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), **243,757 stars**). GBrain is the memory layer under both.
- **The "torn apart on the internet" episode is documented and Tan wrote a formal rebuttal**: [`docs/ON_THE_LOC_CONTROVERSY.md`](https://github.com/garrytan/gstack/blob/main/docs/ON_THE_LOC_CONTROVERSY.md) in gstack, which lands on **408X** after a 2× AI-verbosity deflation and concedes four specific weaknesses.
- **The 80,000-markdown-file epilepsy story is public** — it is in the talk itself at 19:00–19:33, and repeated in the Startup School version.

---

## 1. GBrain — the repo (the "find the real URL" question)

**URL:** https://github.com/garrytan/gbrain — description: *"Garry's Opinionated OpenClaw/Hermes Agent Brain"*. Sibling benchmark repo: https://github.com/garrytan/gbrain-evals (419 stars, created 2026-04-22).

Live metrics (GitHub API, 2026-09-10): 29,763 stars, 4,441 forks, 173 open issues, MIT, TypeScript, last push 2026-09-08, release cadence roughly daily (`v0.48.5.0` 2026-09-08, `v0.48.4.0` 2026-09-07, `v0.48.3.0` 2026-09-06).

**What the README adds beyond the talk.** The talk says "Postgres for agents"; the README is much more specific and, notably, *anti-RAG in its framing*: "**Search gives you raw pages. GBrain gives you the answer.**" Two claimed differentiators: (a) a **synthesis layer** that returns cited prose plus an explicit **gap statement** ("nothing's been added about Alice since April 22 … she may have replied through email or Slack DM, channels the brain doesn't see"); (b) a **self-wiring knowledge graph** where every page write extracts entity refs and creates typed edges (`attended`, `works_at`, `invested_in`, `founded`, `advises`) with **zero LLM calls**. Benchmarks quoted in the README: **P@5 49.1%, R@5 97.9%** on a 240-page corpus, **+31.4 points P@5** over the graph-disabled variant and over ripgrep-BM25 + vector-only RAG.

**Numbers drift across sources — flag this.** The talk (July) says **~220,000 pages**. The current README says **155,795 pages, 24,589 people, 5,340 companies, 66 cron jobs**. [`docs/ethos/ORIGIN.md`](https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md) says **17,888 pages, 4,383 people, 723 companies, 21 crons**. The README was last touched 2026-09-08, so the 220K figure is *not* the currently-published one. Either the talk counted something broader (his private repo vs. the indexed brain) or the numbers are inconsistent. Treat page counts as marketing, not measurement.

**The talk's four "product not primitive" claims map to actual files.** `skills/` contains `RESOLVER.md` (the "org chart"), `_brain-filing-rules.md` (the "internal process"), `citation-fixer`, `correction-pipeline`, `context-audit`, `brain-taxonomist`, `skill-autobench`, and — directly relevant to your question — **`skillify`** and **`company-brainify`**.

`company-brainify` (v1.0.0) is the literal "company brain" skill: it *extracts a sanitized shared team brain from a personal brain*, stripping "internal ratings, compensation, performance assessments, retention and political dynamics," then purges sensitive git history behind a `data-loss-gate` confirmation. That is a genuinely non-RAG concern — it is a **curation and provenance** problem, exactly the framing in the talk.

There is also a full write-up: [`docs/tutorials/company-brain.md`](https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md) — "about 90 more minutes on top of the personal-brain install," "**under $100 a month sustained for a 25-person company**," with per-user OAuth scopes and a claimed zero-leak fuzz test across every read path.

**`gbrain-evals` is the most decision-relevant artifact and nobody cites it.** Its README (https://github.com/garrytan/gbrain-evals) reports a **2026-09-06 LongMemEval run**: complete evidence retrieval on **449/470 answerable questions (95.53%)** within five chunks, and **433/500 (86.6%)** answered correctly. It also reports honest negatives: turning off score-based trimming raised complete retrieval from **379/470 to 449/470**; extra query rewrites *hurt* retrieval at k=5; a controlled production test of relationship retrieval raised first-place hits **9/39 → 21/39** on investor questions but **did not improve attendance questions** because "the fixture's link direction did not match the parser's expectation." That level of candor is unusual and is the strongest evidence for the "graph edges beat vector-only" claim.

---

## 2. gstack — the earlier, bigger repo the talk assumes you know

**URL:** https://github.com/garrytan/gstack — 132,245 stars, created 2026-03-11, MIT. "23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA," delivered as slash commands inside Claude Code and other agents. Its README opens with a Karpathy quote from *No Priors* (March 2026) and credits Steinberger/OpenClaw as the existence proof.

Self-reported telemetry in the LOC doc: **14,965 unique installations, 305,309 skill invocations since January 2026, ~7,000 weekly active users at peak, 95.2% success rate**; top skill `/qa` at 57,650 runs.

---

## 3. "Skillify it" — the post the talk points you at

In the talk (15:49–16:22) Tan says: *"at the end of that task, skillify it. And so I have a blog post on X about that. You can search for skillify it."*

- **Primary:** https://x.com/garrytan/status/2046876981711769720 (the 10-item checklist; X is paywalled to fetchers, so this is cited via a secondary that quotes it: https://gu-log.vercel.app/en/posts/en-gp-179-20260422-garrytan-skillify-agent-failures, ~2026-04-22). Follow-up post: https://x.com/garrytan/status/2047507935623033033.
- **Quoted checklist:** 1 SKILL.md contract → 2 deterministic code in `scripts/*.mjs` ("no LLM for what code can do") → 3 unit tests (vitest) → 4 integration tests → 5 LLM evals → 6 resolver trigger in AGENTS.md → 7 resolver eval → 8 check-resolvable + DRY audit → 9 E2E smoke test → 10 brain filing rules.
- **What the repo adds beyond the post:** [`skills/skillify/SKILL.md`](https://github.com/garrytan/gbrain/blob/master/skills/skillify/SKILL.md) is now **v2.0.0 with 15 items**, an explicit `eval_contract` (goal + skill-specific dimensions + hard-fails), a **cross-modal eval where three frontier models from different providers critique the output before tests are written**, and a "**NO-REGRESSION LAW**: any edit to a skill must score ≥ the previous iteration's eval — forward only, never back." This is the concrete answer to the talk's "a bad skill file encodes bad process forever" failure mode.

---

## 4. OpenClaw and Hermes — what they actually are

- **OpenClaw** = Peter Steinberger's open-source agent. https://github.com/openclaw/openclaw, **389,291 stars, 81,812 forks**, created **2025-11-24**, homepage openclaw.ai. Shipped as a ~1-hour prototype in Nov 2025; Steinberger joined OpenAI **2026-02-14** and the project was handed to an independent foundation, with OpenAI saying it stays open source ([alternativeto.net](https://alternativeto.net/news/2026/2/openai-hires-openclaw-creator-peter-steinberger-will-keep-the-ai-agent-open-source), [steipete.me](https://steipete.me/posts/2026/openclaw), [Wikipedia](https://en.wikipedia.org/wiki/Peter_Steinberger_(programmer))). Tan's own contribution here is a **fork of a deploy harness**: [garrytan/alphaclaw](https://github.com/garrytan/alphaclaw) (169 stars) forked from [chrysb/alphaclaw](https://github.com/chrysb/alphaclaw) (1,474 stars), plus [garrytan/openclaw-render-template](https://github.com/garrytan/openclaw-render-template).
- **Hermes** = **Nous Research**, confirmed. https://github.com/NousResearch/hermes-agent, **243,757 stars**, created **2025-07-22**, MIT, Python, homepage hermes-agent.nousresearch.com, tagline "The agent that grows with you."
- GBrain's README treats these as the *"as intended, always on"* tier (server-hosted, 24/7 crons, "dream cycle"), with Codex and Claude Code as the low-cost on-ramps. So "loves OpenClaw / Hermes" means *those are the two harnesses that can run the nightly consolidation loop*, not that GBrain is coupled to them.

---

## 5. Other 2026 artifacts where he elaborates

| Artifact | Date | What it adds |
|---|---|---|
| ["Thin Harness, Fat Skills"](https://github.com/garrytan/gbrain/blob/master/docs/ethos/THIN_HARNESS_FAT_SKILLS.md) — essay in-repo; X thread [2042925773300908103](https://x.com/garrytan/status/2042925773300908103); "YC Spring 2026" talk | created 2026-04-09, updated 2026-04-11 | The five definitions (skill file, harness, resolver, filing rules, brain). Claims Anthropic accidentally published **512,000 lines** of Claude Code source to npm on **2026-03-31** and that reading it confirmed "the harness is the secret sauce." Cites Steve Yegge's 10x–100x–1000x framing. |
| [`docs/ethos/ORIGIN.md`](https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md) | in-repo | Honest origin: v1 was "a flat directory of markdown files. Search was ripgrep. Memory was vibes." Two failures — cross-session amnesia and entity duplication. "**None of those are novel ideas. The contribution is shipping all of them together.**" This is the single most useful line for the "is it just RAG?" question — the author concedes the primitives are known. |
| ["Own Your Intelligence"](https://www.ycombinator.com/library/WX-garry-tan-own-your-intelligence) — YC Startup Podcast / Startup School 2026 | **2026-08-06** | The "personal AGI" framing. Adds: 220,000 pages / 25 years diarized; a 1,500-page Spinoza biography synthesized overnight; Emergent at **$100M+ revenue in 8 months with 15 people**; Retell AI at **$60M annualized with 40 people**; and the epilepsy story. Also the sharper political line: "**own your skills, because if you don't, your job becomes a skill file.**" ([summary](https://www.the-ai-corner.com/p/garry-tan-personal-agi), 2026-08-31) |
| a16z podcast, "New Rules for Founders" | Aug 2026 ([YouTube](https://www.youtube.com/watch?v=fsTtKywmWlU)) | Same thesis for an investor audience; "a markdown file is an employee." |
| [Reconstructed slide deck](https://lawrencewu.net/posts/2026-07-20-reverse-engineering-garry-tan-slides/slides) | 2026-07-20 | Third party reverse-engineered slides from the transcript because **the talk had no slides**. Confirms the talk is also referred to as "The New Physics of Business" / "Closing Keynote" ([ai.engineer speaker page](https://ai.engineer/speakers/garry-tan), [daily.dev](https://daily.dev/posts/closing-keynote-garry-tan-y-combinator-pneyyqbaz)). |

**The institutional move:** YC's **Summer 2026 Request for Startups** included a "**Company Brain**" entry written by **Tom Blomfield** (YC GP, Monzo/GoCardless), which cites GBrain directly and asks for *"Garry's G-Brain, but for every business in the world"* ([Modelence mirror](https://modelence.com/yc-rfs-summer-2026/company-brain), [ycombinator.com/rfs](https://www.ycombinator.com/rfs)). Caveat: the RFS page now shows the **Fall 2026** list and no longer contains a company-brain entry, so the anchor `ycombinator.com/rfs#company-brain` in GBrain's README is stale. Required capabilities in the RFS: continuous ingestion, a semantic knowledge graph, cited natural-language Q&A ("why did we decide X?"), proactive surfacing via browser extension/Slack, and access control that respects source-system permissions.

---

## 6. Press and community reaction, and the 400X fight

**What he actually claimed, and where.** In the talk (02:32): *"I did the math on my output, and it's about 400X … Take the most pathological verbosity penalty you can stomach … It's still **8X at the floor and 80X in the middle**."* The pre-deflation is in the talk itself — he was anticipating the fight, not responding to it.

**The audit.** On **2026-07-07**, a Polish developer using the handle **Gregorein** audited Tan's public site after Tan posted that agentic engineering let him ship **37K lines/day across 5 projects on a 72-day streak** ([aiweekly.co writeup](https://aiweekly.co/alerts/developer-audits-yc-ceo-garry-tans-37k-ai-lines-per-day-claim)). Findings: homepage load of **6.42 MB across 169 requests** vs Hacker News (also YC-run) at **7 requests / 12 KB**; 78,400-line codebase; **28 test files served to every visitor**; **78 Stimulus controllers** on a page that uses none; a logo in 8 formats including a **0-byte AVIF**; 2.07 MB and 1.99 MB uncompressed PNGs; a 520 KB rich-text editor on a read-only page; 47 images without alt text.

**His rebuttal is a document, not a tweet.** [`gstack/docs/ON_THE_LOC_CONTROVERSY.md`](https://github.com/garrytan/gstack/blob/main/docs/ON_THE_LOC_CONTROVERSY.md) opens *"The critique is right. And it doesn't matter,"* cites Dijkstra EWD1036, then runs a reproducible script over 41 `garrytan/*` repos (15 public, 26 private): 2013 = **5,143 logical SLOC (14/day)**; 2026 through day 108 = **1,233,062 (11,417/day)** = **810×**; apply a 2× AI-verbosity deflation → **408×**; 5× → 162×; 10× → 81×. Quality data offered: **2.0% revert rate (7/351 commits)**, 6.3% post-merge fix rate, tests from ~100 in January to **2,000+**. He concedes four things explicitly: greenfield ≠ legacy maintenance, 2013 survivorship bias (a 50/day baseline drops 810× to 228×), quality-adjusted productivity "isn't fully proven," and "time to first user is the metric that matters, not LOC."

**Independent adversarial signal.** Ben Vinegar (founding engineer at Sentry) built [slop-scan](https://github.com/benvinegar/slop-scan) (redirects to `modem-dev/slop-scan`, 310 stars, created 2026-04-05) to detect AI code patterns; per Tan's own account it scored gstack **5.24, the worst Vinegar had measured at the time**, and Tan says he cut it 62% in one session. Reporting that against yourself is a point in his favour.

**Community reaction is smaller and more mixed than the star counts suggest.** Hacker News threads about the actual repos are tiny: gstack's launch thread got **15 points / 15 comments** ([47355173](https://news.ycombinator.com/item?id=47355173)) — supportive on the role-decomposition pattern, with concerns about opt-in telemetry as "a backdoor way for YC to get signal on what people are building" and a documented incident of a Claude Code agent "stuck in a 70-minute loop, repeatedly injecting a staging URL into a production config file." The "most important idea of the year" GBrain post got **5 points / 1 comment** ([48091611](https://news.ycombinator.com/item?id=48091611)). There is an April Fools submission titled "[Gstack to Be Renamed as Gslop](https://news.ycombinator.com/item?id=47599848)." Meanwhile the largest Garry Tan threads on HN in 2026 are **political, not technical** (e.g. 565 points on a journalism dispute, 340 on a CA politics PAC) — worth knowing so you don't mistake general Tan controversy for company-brain controversy.

**The substantive technical critiques.** [Vectorize's review](https://vectorize.io/articles/gbrain-review) (2026-05-08) praises the zero-LLM-call entity extraction and markdown-first auditability, then lists: first-class support only for OpenClaw and Hermes; **single-operator design, unsuitable for multi-tenant**; no managed hosting; operator-authored schemas required; **no multi-hop graph traversal at retrieval time**; "young (~v0.30, frequent breaking changes)". [useaitechdad](https://useaitechdad.com/articles/garry-tan-company-brain-gbrain-yc-rfs/) (2026-05-01) puts it bluntly: "G-Brain is personal. One user. One brain. Multi-tenancy, access control, write conflict resolution, consensus across teams — Tan hasn't solved any of those publicly." (The Sept README and `company-brain.md` tutorial are the direct answer to that criticism, four months later.) [colrows](https://colrows.com/blogs/yc-company-brain-rfs/) (2026-06-21, upd. 2026-07-07) argues all company-brain entrants "solve 40% of the problem" — retrieval without **metric consistency or governance**: "when an AI agent and a CFO calculate 'revenue' differently, silent wrong answers go to board decks."

**The 80,000-file epilepsy story** is public and primary — it is in the talk transcript at **19:00–19:33**: *"I have a friend who has a rare form of epilepsy. He built a repo of 80,000 markdown files, a company brain for one small boy … No lab, no grant, no permission. A father, a laptop, and a library."* Retold in the Startup School version with detail that every specialist visit, paper, seizure log and drug interaction is indexed and cross-linked ([the-ai-corner](https://www.the-ai-corner.com/p/garry-tan-personal-agi)). No name is given and there is no independent verification of the repo — treat as an anecdote, not a case study.

---

## Relevance to company-brain / RAG / fruit-fly question

**(a) RAG.** The ecosystem answers this more usefully than the talk does. Tan's own `ORIGIN.md` concedes *"none of those are novel ideas; the contribution is shipping all of them together."* The defensible claim is not architectural novelty but **integration + hygiene**: brain-first lookup before external calls, auto-linking on write, typed edges, hybrid search, reranker, nightly dedup/enrich/citation-fix/contradiction surfacing, and a text-file resolver instead of a router LLM. The `gbrain-evals` numbers (graph edges 9/39 → 21/39 on relational questions; +31.4 P@5 over the graph-disabled variant) are the only quantitative evidence that "brain > RAG" means anything, and they are self-published. The unsolved-by-anyone gap that critics agree on is **governance and metric consistency**, which retrieval quality cannot fix.

**(b) Fruit fly.** Nothing in Tan's public corpus references connectomics, FlyWire, mushroom-body memory, or FlyHash/fly-LSH. The word "brain" here is a **library metaphor**, not a neuroscience claim. Any fruit-fly connection must be built by the user, not attributed to Tan — the two plausible bridges (FlyHash-style sparse random projection as a cheap index; mushroom-body-style hot/cold consolidation and active forgetting mapped onto GBrain's nightly "dream cycle") are ours to propose. The dream cycle is the one genuinely suggestive overlap and is worth handing to whoever owns the fruit-fly dimension.

**(c) Projects.** From this dimension: **Hyper** (YC P26) is the most substantial commercial entrant ([Launch HN, 2026-06-03, 79 pts / 78 comments](https://news.ycombinator.com/item?id=48387095)); also **Sylph** (open source, [Show HN 2026-05-22](https://news.ycombinator.com/item?id=48232533)), **Vitrus** ("the company brain that tells you what it doesn't know", [2026-06-20](https://news.ycombinator.com/item?id=48613997)), **Savant**, **Cerenovus (YC S26)**, **Memory Store (YC P26)**, and **Hindsight** (recommended over GBrain for multi-tenant by Vectorize). Alex Lockey's ["Four Builders, One Architecture"](https://www.alexlockey.com/writing/the-company-brain-four-builders-one-architecture/) adds two non-obvious production examples: **Hannah Stulberg's Team OS at DoorDash** and **Ramp's "Glass" system with 350+ shared skills and a skills marketplace called "Dojo"** — those are the closest things to a real, non-founder-authored company brain at scale.

## Open questions

1. Why does the page count differ (220,000 in the talk vs 155,795 in the current README vs 17,888 in ORIGIN.md)? Different corpora, or unreconciled marketing?
2. Vectorize (May) cites LongMemEval **97.60% R@5**; gbrain-evals (Sept 6) reports **95.53%** complete retrieval and **86.6%** answer accuracy. Different metrics or a regression? The evals repo's own honesty about "separate measurements with separate denominators" suggests the 97.6% figure was the easier one.
3. Has anyone outside Tan's orbit reproduced BrainBench or the +31.4 P@5 graph delta on a non-Opus-generated corpus? The 240-page benchmark corpus being LLM-generated is a real threat to validity.
4. Did Tan ever respond publicly to Gregorein's specific July 7 findings? The LOC doc predates them (it is written against the 600K-lines-in-60-days wave) and the aiweekly writeup says no response was disclosed.
5. Is the "friend with the 80,000-file epilepsy brain" identifiable, and is the repo public? Currently an unverifiable anecdote carrying a lot of the talk's emotional weight.
6. What happened to the Summer 2026 "Company Brain" RFS entry — retired into the Fall 2026 list, or dropped? GBrain's README still deep-links a dead anchor.

## Sources

- https://github.com/garrytan/gbrain (README, `skills/`, `docs/`) — GitHub REST API metrics retrieved 2026-09-10
- https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md
- https://github.com/garrytan/gbrain/blob/master/docs/ethos/THIN_HARNESS_FAT_SKILLS.md
- https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md
- https://github.com/garrytan/gbrain/blob/master/skills/skillify/SKILL.md
- https://github.com/garrytan/gbrain/blob/master/skills/company-brainify/SKILL.md
- https://github.com/garrytan/gbrain-evals
- https://github.com/garrytan/gstack and https://github.com/garrytan/gstack/blob/main/docs/ON_THE_LOC_CONTROVERSY.md
- https://github.com/garrytan/alphaclaw · https://github.com/chrysb/alphaclaw · https://github.com/garrytan/openclaw-render-template
- https://github.com/openclaw/openclaw · https://github.com/NousResearch/hermes-agent · https://github.com/benvinegar/slop-scan
- https://www.youtube.com/watch?v=eBUyTS7SzV4 (talk) and local transcript `sources/transcript_eBUyTS7SzV4.txt`
- https://ai.engineer/speakers/garry-tan · https://daily.dev/posts/closing-keynote-garry-tan-y-combinator-pneyyqbaz
- https://lawrencewu.net/posts/2026-07-20-reverse-engineering-garry-tan-slides/slides
- https://aiweekly.co/alerts/developer-audits-yc-ceo-garry-tans-37k-ai-lines-per-day-claim
- https://vectorize.io/articles/gbrain-review · https://useaitechdad.com/articles/garry-tan-company-brain-gbrain-yc-rfs/ · https://colrows.com/blogs/yc-company-brain-rfs/
- https://www.alexlockey.com/writing/the-company-brain-four-builders-one-architecture/
- https://www.ycombinator.com/rfs · https://modelence.com/yc-rfs-summer-2026/company-brain
- https://www.ycombinator.com/library/WX-garry-tan-own-your-intelligence · https://www.the-ai-corner.com/p/garry-tan-personal-agi
- https://www.youtube.com/watch?v=fsTtKywmWlU (a16z, "New Rules for Founders")
- https://gu-log.vercel.app/en/posts/en-gp-179-20260422-garrytan-skillify-agent-failures (quotes the Skillify X post)
- X posts (paywalled to fetchers, cited via secondaries): https://x.com/garrytan/status/2046876981711769720 · https://x.com/garrytan/status/2047507935623033033 · https://x.com/garrytan/status/2042925773300908103 · https://x.com/garrytan/status/2055670533451366479
- HN: https://news.ycombinator.com/item?id=47355173 · https://news.ycombinator.com/item?id=48091611 · https://news.ycombinator.com/item?id=48387095 · https://news.ycombinator.com/item?id=48232533 · https://news.ycombinator.com/item?id=48613997 (thread metadata via hn.algolia.com API, 2026-09-10)
- https://en.wikipedia.org/wiki/Peter_Steinberger_(programmer) · https://alternativeto.net/news/2026/2/openai-hires-openclaw-creator-peter-steinberger-will-keep-the-ai-agent-open-source · https://steipete.me/posts/2026/openclaw

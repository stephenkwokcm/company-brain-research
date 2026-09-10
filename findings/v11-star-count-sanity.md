# v11 — Star-count sanity check (lens: data-check)

**Key:** `v11-star-count-sanity` · **Fetched:** 2026-09-09T17:35–17:41Z (GitHub API clock; task date 2026-09-10) · **Method:** `gh api repos/<owner>/<name>`, `gh api users/…`, `gh api search/repositories`, GraphQL `stargazers`, raw.githubusercontent.com, WebFetch on primary pages.

## Verdict table

| # | Claim (as reported by earlier workers) | Live value | Verdict |
|---|---|---|---|
| 1 | `openclaw/openclaw` **389,291★** | **389,291** (repo API) / 389,292 (search index, and on re-fetch) | **CONFIRMED** |
| 2 | Nous Research Hermes agent **243,757★** | **243,772 → 243,774** | **CONFIRMED** (drift +15/+17 = normal growth) |
| 3 | `garrytan/gbrain` **29,763★** | **29,764** | **CONFIRMED** |
| 4 | `garrytan/gstack` **132,245★** | **132,250 → 132,252** | **CONFIRMED** |
| 5 | `garrytan/gbrain-evals` **419★** | **419** | **CONFIRMED** (exact) |
| 6 | Five `b01-gbrain-*` repos, ~44–49★ each, possible astroturf | 49 / 47 / 46 / 45 / 44 (Σ 231) | **star counts CONFIRMED; astroturf CONFIRMED** (high confidence, on account+content forensics — *not* on stargazer timelines, which were unobtainable) |
| 7 | Critic's framing: OpenClaw + Hermes "would be roughly the two most-starred repos in GitHub history" | OpenClaw ranks **#6**, Hermes **#19** | **REFUTED** |
| 8 | Steinberger joined OpenAI **2026-02-14** | 2026-02-14 is his **announcement** post date; no start date published | **PARTIALLY** |
| 9 | OpenClaw "moved to a foundation" | **OpenClaw Foundation**, independent 501(c)(3), holds copyright | **CONFIRMED** (+ one correction, §4) |

**Bottom line: every star number reported by earlier workers is accurate.** No fabrication, no transcription error. All five drifted upward by 0–17 between their fetch and mine, which is exactly what monotonic star growth looks like and is itself evidence the earlier numbers were genuinely pulled from the API. The two things that *were* wrong are interpretive, not numeric: the critic's "most-starred in history" framing (§3), and the attribution of OpenClaw's foundation to OpenAI (§4).

---

## 1. The five headline repos — full live metadata

| Repo | ★ | Forks | Watchers (subs) | Created | Last push | License | Lang |
|---|---|---|---|---|---|---|---|
| `openclaw/openclaw` | 389,291 | 81,813 | 1,752 | 2025-11-24 | 2026-09-09 | MIT (see §4) | TypeScript |
| `NousResearch/hermes-agent` | 243,772 | 50,291 | 953 | 2025-07-22 | 2026-09-09 | MIT | Python |
| `garrytan/gstack` | 132,250 | 19,789 | 791 | 2026-03-11 | 2026-09-09 | MIT | TypeScript |
| `garrytan/gbrain` | 29,764 | 4,441 | 135 | 2026-04-05 | 2026-09-08 | MIT | TypeScript |
| `garrytan/gbrain-evals` | 419 | 77 | 4 | 2026-04-22 | 2026-09-09 | MIT | TypeScript |

All five are real, public, non-fork, non-archived, and actively pushed within the last 48 hours. Owner types check out: `openclaw` and `NousResearch` are Organizations, `garrytan` is a User. Latest releases: gbrain `v0.48.5.0` (2026-09-08T03:35:57Z), Hermes `v2026.9.7` (2026-09-07T22:17:01Z) — both consistent with earlier reports.

Cross-report drift is internally consistent, which is a useful integrity signal:

- gbrain: `garry-tan-ecosystem.md`/`rag-taxonomy.md` 29,763 → `skeptic-claims.md`/`v01` 29,764 → mine 29,764.
- gstack: 132,245 → 132,248 → 132,250 → 132,252 (four successive fetches, monotonic).
- Hermes: 243,757 → 243,760 → 243,772 → 243,774.

## 2. Engagement-ratio baseline (used as the astroturf discriminator in §5)

| Repo | ★ | Forks | ★:fork | Subs | ★:sub |
|---|---|---|---|---|---|
| `openclaw/openclaw` | 389,292 | 81,813 | 4.8 | 1,752 | 222 |
| `NousResearch/hermes-agent` | 243,774 | 50,291 | 4.8 | 953 | 256 |
| `garrytan/gstack` | 132,252 | 19,789 | 6.7 | 791 | 167 |
| `garrytan/gbrain` | 29,764 | 4,441 | 6.7 | 135 | 220 |
| `garrytan/gbrain-evals` | 419 | 77 | 5.4 | 4 | 105 |
| `thedotmack/claude-mem` | 93,569 | 8,220 | 11.4 | 298 | 314 |
| **`b01-gbrain-devops`** | **49** | **0** | **∞** | **0** | **∞** |
| **`b01-gbrain-security`** | **47** | **0** | **∞** | **0** | **∞** |

Organic repos in this ecosystem run **one fork per 5–11 stars** and **one watcher per 105–314 stars**. At 44–49 stars, a b01 repo should have ~4–10 forks and ≥0–1 watchers. Four of the five have **zero forks and zero watchers**; the other two have one fork each. That is the numeric signature of stars arriving without humans attached.

## 3. Is 389,291 plausible for #1 on GitHub? No — because it isn't #1

`search/repositories q=stars:>150000 sort=stars` (retrieved 2026-09-09):

| Rank | ★ | Repo | Created |
|---|---|---|---|
| 1 | 546,207 | codecrafters-io/build-your-own-x | 2018-05-09 |
| 2 | 504,480 | sindresorhus/awesome | 2014-07-11 |
| 3 | 478,031 | public-apis/public-apis | 2016-03-20 |
| 4 | 455,233 | freeCodeCamp/freeCodeCamp | 2014-12-24 |
| 5 | 396,352 | EbookFoundation/free-programming-books | 2013-10-11 |
| **6** | **389,292** | **openclaw/openclaw** | **2025-11-24** |
| 7 | 368,985 | donnemartin/system-design-primer | 2017-02-26 |
| … | | | |
| 12 | 283,888 | obra/superpowers | 2025-10-09 |
| 14 | 257,713 | mattpocock/skills | 2026-02-03 |
| 15 | 254,953 | affaan-m/ECC | 2026-01-18 |
| **19** | **243,774** | **NousResearch/hermes-agent** | **2025-07-22** |
| 22 | 217,328 | deepseek-ai/deepseek-harness | **2026-08-13** |
| 24 | 211,842 | multica-ai/andrej-karpathy-skills | 2026-01-27 |

**This refutes completeness-critic item #9's premise.** OpenClaw is #6, not #1, and Hermes is #19 — both comfortably below five long-established list repos. More importantly, OpenClaw's velocity is *in-band with its 2025–26 peers*, not an outlier: `deepseek-ai/deepseek-harness` took **217,328 stars in under a month** (created 2026-08-13), `mattpocock/skills` 257,713 since 2026-02-03, `obra/superpowers` 283,888 since 2025-10-09. Whatever is inflating stars in the agent-tooling category is inflating all of them.

**Implication for the synthesis:** this *strengthens* the orchestrator's existing decision that "star counts are not a quality signal" (checkpoint 01, §c) and supplies the number that makes it concrete — a repo can now clear 200K stars in weeks. Cite adoption via releases, forks, issue volume and third-party benchmarks (`gbrain-evals`, MemOS, LongMemEval) instead. Note the corollary for gbrain: **29,764★ is small** in this landscape — `claude-mem` has 3.1× more stars with, per `memory-systems-landscape.md`, zero lifecycle features. Stars and the thesis are orthogonal.

## 4. Steinberger → OpenAI, and the OpenClaw Foundation

**The date — PARTIALLY confirmed.** Steinberger's own post at https://steipete.me/posts/2026/openclaw is dated **14 Feb, 2026** and says, first person: *"I'm joining OpenAI to work on bringing agents to everyone."* He **does not give a start date**. Wikipedia says only "In February 2026, he announced he would be joining OpenAI." Reuters covered it 2026-02-16 ("OpenClaw founder Steinberger joins OpenAI, open-source bot becomes foundation"); alternativeto.net published 2026-02-16 14:30. His GitHub profile today lists `company: OpenAI`, bio *"Came back from retirement to mess with AI. Clawdfather @OpenClaw. Previously: Founder of @PSPDFKit."*

→ **Correct phrasing: "announced on 2026-02-14 that he was joining OpenAI."** Not "joined OpenAI on 2026-02-14" — no employment date is public.

**The foundation — CONFIRMED, with a correction.** On 2026-02-14 it was only an intention: *"To get this into a proper structure I'm working on making it a foundation."* It now exists, and primary sources confirm it:

- `openclaw/openclaw` **LICENSE**: `MIT License / Copyright (c) 2026 OpenClaw Foundation` (raw.githubusercontent.com — note the repo API reports `NOASSERTION` because of the appended third-party-notices line, but the text is verbatim MIT).
- **README §Governance** (line 110): *"OpenClaw is developed in the open by the [OpenClaw Foundation](https://openclaw.org), an independent 501(c)(3). The Foundation employs the core team and signs releases. Donors and infrastructure sponsors support the Foundation; none of them own or direct the project. **OpenAI is a donor, not an owner.**"*
- README line 20: *"OpenClaw is stewarded by the OpenClaw Foundation, an independent 501(c)(3), and has no paid tier, hosted service, or token."*
- README line 124: donors are *"the University of Michigan, OpenAI, Amazon, Red Hat, Offline Holdings, and Lobster Computer Company,"* with infrastructure from GitHub, NVIDIA, Vercel, Blacksmith, Convex.
- README line 330: *"[MIT](LICENSE) © OpenClaw Foundation."*

**Correction to `garry-tan-ecosystem.md` §4.** It cites alternativeto.net's *"OpenAI will maintain OpenClaw through a dedicated foundation."* That secondary source is **wrong**, and the repo's own governance file says so explicitly: OpenAI is one donor among six and does not own or direct the project. `garry-tan-ecosystem.md`'s own wording ("handed to an independent foundation, with OpenAI saying it stays open source") is defensible, but the alternativeto quote behind it should not be reused. Also incidental: `steipete/openclaw` (created 2026-07-11, 17★) is a **fork of `vercel-labs/openclaw`**, not the canonical repo — don't cite it.

## 5. The `b01-gbrain-*` cluster — astroturf, confirmed

`gh search repos b01-gbrain` returns exactly **5** repos. Star counts match `projects-built-on-ideas.md` precisely.

| Repo | ★ | Forks | Subs | Created (UTC) | Pushed (UTC) | Size | Owner acct id |
|---|---|---|---|---|---|---|---|
| `slayerassassinjack/b01-gbrain-devops` | 49 | 0 | 0 | 2026-04-28T17:**54:20** | 18:**32:02** | 8 KB | 267327633 |
| `FlameToneSheave/b01-gbrain-datascience` | 44 | 0 | 0 | 17:**54:14** | 18:**32:00** | 8 KB | 267328121 |
| `PulverizeDirector/b01-gbrain-security` | 47 | 0 | 0 | 17:**54:30** | 18:**32:05** | 8 KB | 267328523 |
| `BanMartinCode/b01-gbrain-ecommerce` | 45 | 1 | 0 | 17:**54:25** | 18:**32:04** | 8 KB | 267329130 |
| `CometBureaucratEquip/b01-gbrain-seo` | 46 | 1 | 0 | 17:**54:36** | 18:**32:07** | 8 KB | 267329344 |

### Eight independent forensic signals

1. **All five repos created inside a 22-second window** (17:54:14 → 17:54:36) and pushed inside a **7-second** window (18:32:00 → 18:32:07) 38 minutes later. Not a "coordinated launch by a community" — a script.
2. **All five owner accounts created inside an 8-minute window** on 2026-03-11 (12:04:47 → 12:12:33), with **near-consecutive user IDs** 267327633 / 267328121 / 267328523 / 267329130 / 267329344.
3. **Each account has exactly 2 public repos**: the b01 repo, plus one **empty 8-random-lowercase-character repo** created minutes after signup — `zlekdnao`, `dymnvqof`, `auihtgmz`, `jqrwpetd`, `xbhqnpvc`. This is textbook account-warming for a bot farm.
4. **Every account is a null profile**: 0 followers, 0 following, no name, no bio, no blog, no company, no email, no gists.
5. **All five account records last updated within 93 seconds** of each other on 2026-04-22 (14:37:58 → 14:39:31) — a second batch operation, six days before the repos were pushed.
6. **Identical commit history, distinct throwaway emails.** Each repo has exactly 2 commits with byte-identical messages — `"Initial commit: Claude Code skills suite"` then `"fix: normalize markdown indentation in all .md files"` — authored by five different Gmail addresses: `nogiveputu258@`, `raspopinad31@`, `chinellbrinton@`, `vtkachenko437@`, `ikhalyavka18@`.
7. **The READMEs are one template with nouns swapped.** Normalising all word tokens, `devops-README.md` and `seo-README.md` differ **only** in the domain strings (emoji, badge label, tagline, one description line). Same shields.io badge block, same section order, same `Adapted from **gbrain (garrytan/gbrain)**` credit line. All five carry the same `Skills-8` / `Workflows-3` structure at 4.0–4.8 KB.
8. **Zero forks, zero watchers at ~46 stars** (§2), and the accounts themselves have **starred nothing (0) and have zero public events** — so the stars came from a *different* pool of accounts, not from each other.

### What I could NOT do, and why it doesn't change the verdict

**Stargazer timelines are unavailable in this environment.** `gh api repos/X/stargazers -H "Accept: application/vnd.github.star+json"` returns **HTTP 404 for every repo**, including controls (`garrytan/gbrain-evals`, `openclaw/openclaw`). Unauthenticated curl returns 401. GraphQL `stargazers(first:100, orderBy:STARRED_AT)` returns the correct `stargazerCount` but an **empty `edges` array** for every repo, controls included. This is a token/proxy limitation of this environment, **not** a repo-specific signal — I verified it against known-good repos before concluding.

→ **No burst pattern was directly observed. The astroturf verdict rests entirely on signals 1–8**, which are account- and content-forensic rather than temporal. I rate it **high confidence** — signals 2, 3, 5 and 6 (batch-created null accounts with warming repos, batch profile edits, five distinct throwaway emails pushing identical commits) are not producible by any organic process — but a reader wanting the star-arrival curve should check https://www.star-history.com/#slayerassassinjack/b01-gbrain-devops in a browser, which is the standard workaround.

### Recommendation

Drop the `b01-gbrain-*` cluster from `projects-built-on-ideas.md` §"Vertical templates", or keep it **only** as a labelled example of ecosystem astroturf. It answers that report's own open question #6 ("Coordinated launch, one author, or astroturf?"): **astroturf**. Its open question #7 (gbrain 0 → ~5,000★ in 24 hours) remains **UNRESOLVED** here for the same stargazer-endpoint reason; note though that gbrain's ratios (6.7 ★/fork, 220 ★/watcher) sit squarely inside the organic band, so there is no ratio-based evidence against gbrain itself.

---

## Sources

**GitHub REST API** (via `gh api`, retrieved 2026-09-09T17:35–17:41Z):
- https://api.github.com/repos/openclaw/openclaw · https://api.github.com/repos/NousResearch/hermes-agent · https://api.github.com/repos/garrytan/gbrain · https://api.github.com/repos/garrytan/gstack · https://api.github.com/repos/garrytan/gbrain-evals · https://api.github.com/repos/thedotmack/claude-mem
- https://api.github.com/search/repositories?q=b01-gbrain · https://api.github.com/search/repositories?q=stars:%3E150000&sort=stars&order=desc
- https://api.github.com/repos/slayerassassinjack/b01-gbrain-devops · .../FlameToneSheave/b01-gbrain-datascience · .../PulverizeDirector/b01-gbrain-security · .../CometBureaucratEquip/b01-gbrain-seo · .../BanMartinCode/b01-gbrain-ecommerce (+ each repo's `/commits`, `/contents`)
- https://api.github.com/users/slayerassassinjack · .../FlameToneSheave · .../PulverizeDirector · .../CometBureaucratEquip · .../BanMartinCode (+ each user's `/repos`, `/starred`, `/events/public`)
- https://api.github.com/users/steipete · https://api.github.com/orgs/openclaw · https://api.github.com/orgs/NousResearch · https://api.github.com/repos/steipete/openclaw
- Failed (documented as an environment limitation): `/repos/*/stargazers` with `Accept: application/vnd.github.star+json` → 404 on all repos; GraphQL `stargazers` connection → empty edges on all repos.

**Raw file content:**
- https://raw.githubusercontent.com/openclaw/openclaw/main/LICENSE (foundation copyright)
- https://raw.githubusercontent.com/openclaw/openclaw/main/README.md (governance §, lines 20/108-110/118/124/330)
- https://raw.githubusercontent.com/slayerassassinjack/b01-gbrain-devops/main/README.md and SKILL.md (+ the four sibling repos)

**Web:**
- https://steipete.me/posts/2026/openclaw — dated 14 Feb 2026; *"I'm joining OpenAI…"*, *"I'm working on making it a foundation."*
- https://en.wikipedia.org/wiki/Peter_Steinberger_(programmer) — "In February 2026, he announced he would be joining OpenAI"; cites Reuters 2026-02-16
- https://alternativeto.net/news/2026/2/openai-hires-openclaw-creator-peter-steinberger-will-keep-the-ai-agent-open-source — pub. 2026-02-16 14:30; its "OpenAI will maintain OpenClaw through a dedicated foundation" is **contradicted** by the repo's own README
- https://openclaw.org — "no single company controls OpenClaw"; no incorporation date published

**Prior reports cross-checked:** `findings/garry-tan-ecosystem.md`, `findings/skeptic-claims.md`, `findings/gbrain-architecture.md`, `findings/projects-built-on-ideas.md`, `findings/memory-systems-landscape.md`, `findings/completeness-critic.md` (item #9), `findings/talk-analysis.md`, `findings/rag-taxonomy.md`, `findings/v01-gbrain-benchmarks.md`

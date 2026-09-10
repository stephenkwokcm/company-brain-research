# v08 — Ramp "Glass"/"Dojo" and DoorDash "Team OS": primary-source verification

**Lens:** primary-source verification
**Key:** `v08-ramp-doordash-cases`
**Date:** 2026-09-10
**Claim under test:** Ramp's internal "Glass" (350+ skills, "Dojo" marketplace) and DoorDash's "Team OS" are real enterprise examples of the skills-as-workforce / company-brain pattern. Both currently rest on a single secondary blog post (`alexlockey.com`, cited in `findings/garry-tan-ecosystem.md`).

---

## TL;DR

| Case | Verdict | One line |
|---|---|---|
| **Ramp "Glass" + "Dojo", 350+ skills** | **CONFIRMED** | Two employee-authored first-person write-ups (2026-04-09, 2026-04-15) plus Ramp's own YouTube channel. "Over 350 skills have been shared company-wide" is verbatim from the Ramp author. |
| **DoorDash "Team OS"** | **PARTIALLY CONFIRMED** | Hannah Stulberg is a real DoorDash PM and Team OS is a real, published, open-source architecture *she* built for *her team* — but no DoorDash-official source exists, her Substack carries an explicit "my own views, not DoorDash's" disclaimer, and the public example repo is a **fictional** company. Calling it "DoorDash's Team OS" is an overclaim. |
| **The secondary blog's Ramp citation** | **BROKEN** | Alex Lockey links `https://ramp.com/blog/skills-and-glass` — that URL returns **HTTP 404** (verified twice, curl and WebFetch, 2026-09-10) and has never been captured by the Wayback Machine. The real source is a LinkedIn Pulse article. |
| **3 extra primary-sourced cases found** | — | Ramp Research (Ramp eng blog, 2025-09-18); PowerSync "company brain" (PowerSync eng blog, 2026-07-24); Y Combinator's own QM harness (qm.ycombinator.com + `yc-software/qm`, Jul–Aug 2026). |

**Net effect on the synthesis:** the enterprise evidence base is *stronger* than the critic feared on Ramp and *weaker* than claimed on DoorDash. Ramp is now the single best-attested non-founder company-brain deployment in the corpus, with a company-official video to boot. DoorDash should be re-labelled "a DoorDash PM's team-level practice," not "DoorDash's system."

---

## 1. Ramp "Glass" / "Dojo" — CONFIRMED

### 1.1 What the secondary source said (and what was wrong with it)

Alex Lockey, ["Company Brain (YC RFS 2026): Four Builders, One Architecture"](https://www.alexlockey.com/writing/the-company-brain-four-builders-one-architecture/) (2026-04-30), wrote:

> "Ramp's internal Glass system (with its skills marketplace called Dojo) runs on the same logic at company scale. Three hundred and fifty plus shared skills, each one a piece of structured context that any operator inside the company can call."

His only citation is a hyperlink to `https://ramp.com/blog/skills-and-glass`.

**That URL is dead.** Verified 2026-09-10:

```
$ curl -sSL -o /dev/null -w "HTTP %{http_code}\n" https://ramp.com/blog/skills-and-glass
HTTP 404
```

WebFetch independently returned `HTTP 404 Not Found`. A Wayback CDX sweep of `ramp.com/blog*` (1,975 collapsed URLs, 2026 captures) contains **no** URL matching `glass|dojo` — the only `skill` hit is `ramp.com/blog/ramp-cli-v017-new-skills-request-search` (2026-05-15, Zack Field), which is a **customer-facing CLI release note** about four new *product* skills (`spend-analysis`, `manage-bills`, `manage-procurement`, `payment-lookup`) and mentions neither Glass nor Dojo. So the citation is not merely dead, it never pointed at a Ramp-hosted Glass post. The claim was true; the citation was fabricated or hallucinated by the secondary author.

### 1.2 The actual primary sources

**(a) Sebastien Goddijn (Ramp), "We Built Every Employee at Ramp Their Own AI Coworker"**, LinkedIn Pulse, published **2026-04-09T16:49:57Z**.
<https://www.linkedin.com/pulse/we-built-every-employee-ramp-own-ai-coworker-sebastien-goddijn-sfupe>
Byline footer: *"Built by Seb Goddijn, Shane Buchan, Cameron Leavenworth, Calvin Kipperman, Jay Sobel, and Caroline Horn at Ramp."*

Verbatim, load-bearing quotes:

> "At Ramp, we hit 99% adoption of AI tools across the company. And then we noticed something concerning: most people were stuck."

> "So we decided to build our own AI productivity suite to make every employee an AI power-user without the pain of having to configure their environment. We've called it **Glass**."

> "The easiest way to share learnings across the organization is through skills. These are markdown files that teaches your agent exactly how to perform a specific task, and we've built out a marketplace for them called **Dojo**."

> "**Over 350 skills have been shared company-wide.** They're Git-backed, versioned, and reviewed like code. The marketplace is the flywheel: every skill shared raises the floor for everyone."

> "To help people find the right skills, Dojo includes a built-in AI guide we call the **Sensei**. It looks at which tools you've connected, what role you're in, and what you've been working on, and recommends the skills most likely to be useful to you. A new account manager doesn't need to browse a catalog of 350 skills — the Sensei surfaces the five that matter most on day one."

> "When users first open Glass, we build a full memory system based on the connections they've authenticated… Under the hood, we also run a **synthesis and cleanup pipeline every 24 hours**, mining users' previous sessions and connected tools like Slack, Notion, and Calendar for updates."

**(b) Shane Buchan (Ramp), "How We Built Glass: Vibe Coding a Product Used by 700 People"**, LinkedIn Pulse, ~**2026-04-15**.
<https://www.linkedin.com/pulse/how-we-built-glass-vibe-coding-product-used-700-people-shane-buchan-okpie>
(also posted to his feed: <https://www.linkedin.com/posts/the-real-shane-buchan_how-we-built-glass-vibe-coding-a-product-activity-7450287991383781376-OKaK>, and mirrored to r/Ramp: <https://www.reddit.com/r/Ramp/comments/1sr1vle/how_we_built_glass_vibe_coding_an_ai_coworker/>)

This is the architecturally interesting one, and it is the source that matters most for the company-brain thesis:

> "**Dojo, our skill marketplace, is backed by a Git repo. Skills are markdown files.** No code, no deployment pipeline, no infrastructure. When someone creates a skill in Glass, it writes a markdown file. When they publish it, Glass handles the Git commit, the pull request, and the review workflow behind the scenes. The user never sees GitHub."

> "We needed non-technical people to contribute their expertise without learning version control. A CX lead who builds a Zendesk investigation workflow shouldn't need to know what a pull request is. But we also needed skills to be **versioned, reviewable, and auditable**, which meant Git was the right backend."

> "The trick is making Git invisible. Glass creates the branch, writes the file, opens the PR, and handles the merge once it's approved. The contributor sees 'publish' and 'published.' The engineering team sees a clean Git history with proper review trails. **Over 350 skills have been shared this way.**"

> "Glass's memory system runs as a background pipeline. Every 24 hours, it mines the user's previous sessions and connected integrations (Slack, Notion, Calendar) and synthesizes an updated profile… **We made memory write-once-read-many.** The synthesis pipeline writes memory files. Every new session reads them at startup. **The agent never modifies memory during a conversation**, it just uses whatever context exists. You know exactly what the agent knows, because it's all in files you can inspect."

> "Glass connects to Slack, Salesforce, Notion, Linear, Gong, Datadog, and a dozen other tools through MCP servers… With 13+ integrations, that's about 45 seconds of handshake latency… Startup went from 45 seconds to about 2."

> "Glass was predominantly vibe coded by a three-person core team (a product manager, an engineer, and an IT engineer)… a product used by half the company."

**(c) Ramp's official YouTube channel (`@tryramp`)**, "We built our own AI workspace from scratch | Ramptables Episode 2 | **Project Glass**", **2026-05-21**, 2,030 views at time of check.
<https://www.youtube.com/watch?v=di0rLBrBP8A>
Chapter list confirms the vocabulary independently of the LinkedIn posts:
`Ramp Assist — the first agent (2:30)` · `The Notion rollout that made it all possible (5:00)` · `Ramp Research and the first viral moment (7:30)` · `Notion custom agents and autonomous workflows (11:00)` · `The Opus 4.6 inflection and getting non-engineers into the terminal (14:00)` · `Why we built Glass instead of pushing harder on Cowork (17:00)` · `GA day, 100 bugs, and the connections nightmare (20:00)` · **`Dojo, skills, and the Sensei (23:30)`** · **`Memory and personalization (27:00)`** · `Snowflake, Ramplify, and the full workspace (29:30)` · `The hackathon and the future of work (32:00)` · `Advice for builders + the trench coat logo (35:00)`

**(d) Third-party interview**: "We Gave Every Employee an AI Agent. Here's What Happened.", **Every** (`@EveryInc`), 2026-04-08, <https://www.youtube.com/watch?v=SRlTgIhESjw>. Not verified in depth; listed for completeness.

### 1.3 Verdict details

| Sub-claim | Verdict | Note |
|---|---|---|
| "Glass" is Ramp's internal AI system | **CONFIRMED** | Named by two Ramp employees and by Ramp's own YouTube channel. |
| "Dojo" is a skills marketplace | **CONFIRMED** | "our skill marketplace, backed by a Git repo. Skills are markdown files." |
| "350+ skills" | **CONFIRMED, with a precision caveat** | Both authors say "**over 350 skills have been shared**" — a cumulative *shared* count, not an attested live catalogue size. Goddijn does refer to "a catalog of 350 skills," so the two readings are close. Do not write "350 skills in the library" as if it were a snapshot inventory. |
| "700 people" / "half the company" | **CONFIRMED as a company claim; internally inconsistent with third-party headcount** | Buchan's own title says 700 and his body says "half the company." Third-party headcount trackers put Ramp at ~2,400–2,518 employees in March–April 2026 ([Revelio Labs](https://www.reveliolabs.com/companies/ramp-business/employees), [jobsbyculture](https://jobsbyculture.com/blog/working-at-ramp-2026)), which would make 700 ≈ 28%, not 50%. Third-party headcount estimates are unreliable (contractors, international entities, stale scrapes), so treat this as a **flag, not a refutation**. Safe phrasing: *"700 users, which Ramp describes as about half the company."* Confidence: medium. |
| "99% AI adoption" | **CONFIRMED as a company claim** | Goddijn, unqualified and unaudited. It is the *premise* of Glass ("we hit 99% adoption… and then we noticed most people were stuck"), not a result of it. Do not cite it as an outcome. |
| Glass/Dojo is open source or public | **REFUTED** | No public Ramp Glass or Dojo repo exists (`gh search repos "ramp dojo skills"` → empty). Everything is internal; only the write-ups are public. |

### 1.4 Why this case matters more than the corpus currently records

The Buchan post is, on the evidence gathered here, **the closest thing in the entire corpus to a production implementation of Tan's write-side thesis by a company that is not selling a company-brain product**. Specifically it independently arrives at four of the design decisions the sweep flagged as the interesting part of the argument:

1. **Skills are markdown files in Git, not rows in a database** — versioned, reviewable, auditable, with the VCS hidden behind a "publish" button for non-engineers. This is Tan's SKILL.md procedural-memory layer, deployed at ~700 users, with a *governance* story (PR review) that GBrain does not have.
2. **Write-once-read-many memory.** "The agent never modifies memory during a conversation." This is a direct, independent, production endorsement of the librarian/curator split that `findings/rag-taxonomy.md` identified as the read-side/write-side dividing line — and it lands on the *opposite* side from self-editing agent memory (Letta/MemGPT-style), which `findings/memory-hygiene.md` found scores 15 pts worse on knowledge-update questions.
3. **A separate, scheduled synthesis-and-cleanup daemon** (every 24 h, "stale entries get cleaned up automatically") rather than inline consolidation. That is the "forgetting daemon" shape the fly-brain design decision (ii) in checkpoint 01 proposes, arrived at without any neuroscience.
4. **A retrieval layer over the skill catalogue itself** — the "Sensei" recommends ~5 of 350 skills based on role, connected tools, and recent work. That is skill-routing, and it is the practical answer to the "how does an agent find the right skill in a 350-file library" problem that the routing/sparse-expansion discussion (design decision (iii)) is really about.

Point 2 and 3 are the ones to carry into the synthesis: Ramp is a *live existence proof* for "curation is a scheduled background job, not the agent's job."

---

## 2. DoorDash "Team OS" — PARTIALLY CONFIRMED (re-label it)

### 2.1 What is real

**Hannah Stulberg is a real DoorDash PM.** Primary source — her own Substack "About" page, <https://hannahstulberg.substack.com/about>:

> "I started my PM career in Google's APM program - first on Google Maps, then YouTube… Then I did a 180, joining Valon… **Now I'm at DoorDash, working on new bets in our white-label business.**"

**Team OS is a real, published architecture with a real artifact.** Primary sources:

- **GitHub org** `in-the-weeds-hannah-stulberg` (Organization, created 2026-03-21), bio: *"In the Weeds is a Substack by Hannah Stulberg on practical AI workflows for non-technical professionals."*
  - [`team-os-example-repo`](https://github.com/in-the-weeds-hannah-stulberg/team-os-example-repo) — **171★**, created 2026-04-01, last push 2026-05-31, CC BY-NC 4.0. README: *"This repo is a complete example of a Team OS - the shared knowledge base that turns your team's collective context into something AI can actually use."*
  - [`substack-articles`](https://github.com/in-the-weeds-hannah-stulberg/substack-articles) — **280★**, created 2026-03-21.
- **The canonical write-up**: Aakash Gupta & Hannah Stulberg, ["Build a team OS with Claude Code"](https://www.news.aakashg.com/p/claude-code-team-os), *Product Growth*, published **2026-04-07T21:06:28Z**. Full text also mirrored in her own repo at [`standalone/build-a-team-os-with-claude-code/article.md`](https://raw.githubusercontent.com/in-the-weeds-hannah-stulberg/substack-articles/main/standalone/build-a-team-os-with-claude-code/article.md).
- **The video**: "How this PM Used Claude Code to Support 20 People", Aakash Gupta (`@growproduct`), <https://www.youtube.com/watch?v=0UArKLQ6bXA>. (Note: Lockey's article cites a truncated URL `youtube.com/watch?v=ex4vCcxb…` which does not resolve; `0UArKLQ6bXA` is the ID given by both the newsletter and the mirrored article front-matter.)
- **The derived starter kit**: [`aakashg/product-growth-team-os`](https://github.com/aakashg/product-growth-team-os) — 35★, created 2026-05-06, ships 7 skills (`customer-call-summary`, `decision-log-entry`, `feature-launch-gate`, `freshness-check`, `portfolio-pulse`, `weekly-synthesis`, `upgrade-to-team-os`) plus `.claude/team-learnings.md`. Its README is the **single strongest attestation of the DoorDash link**:

  > "Created by Aakash Gupta and Hannah Stulberg, **based on Hannah's implementation at DoorDash** and patterns from Dave Killeen (Pendo) and Gabor Meyer (Google)."

The architecture itself, verbatim from the article, is a genuine company-brain-shaped design: one shared GitHub repo; a root `CLAUDE.md` restricted to a doc index + team roster with Slack/GitHub handles + channel map; nested per-folder `CLAUDE.md` navigation maps ("a query about customers consumed only **3% of the context window**"); `.claude/{agents,commands,skills}`; and a functional-ownership model ("the data scientist owns analytics. Engineers own bugs and RFCs. The PM owns product context").

### 2.2 What is *not* supported

1. **No DoorDash-official source of any kind.** No DoorDash engineering blog post, no press release, no DoorDash-branded repo. Nothing on `doordash.engineering` or `careersatdoordash.com` surfaced for "Team OS."
2. **Her own publication carries an explicit disclaimer.** Bottom of <https://hannahstulberg.substack.com/about>:
   > *"The postings on this site are my own and do not necessarily reflect DoorDash's positions or opinions on the subject."*
3. **The public example repo is a fictional company.** README: *"The example company is **Forge, a fictional AI prototyping startup** with a 10-person product team."* Nobody outside DoorDash has seen the actual DoorDash Team OS.
4. **Scale is one team, not one company.** The article's framing throughout is "one PM supports 20 people across five functions"; the video title is literally "How this PM Used Claude Code to Support 20 People." This is a **team OS**, as named. It is not a company brain at DoorDash scale (~20k+ corporate employees).
5. **No metrics.** Zero adoption numbers, zero retrieval-quality numbers, zero before/after. The only quantities are "3% of the context window" for one query, and "~1,500 hours" of the author's own Claude Code usage.

### 2.3 Verdict

**PARTIALLY CONFIRMED.** Rewrite the corpus line as:

> *Hannah Stulberg, a PM at DoorDash, has published (in a personal capacity, with an explicit disclaimer) a "Team OS" architecture — one shared Git repo of nested `CLAUDE.md` indexes plus a `.claude/skills` folder — which she says is based on her implementation with her ~20-person cross-functional team at DoorDash. The public artifact is a template built around a fictional company; no DoorDash-official source and no adoption or quality metrics exist.*

Do **not** write "DoorDash's Team OS" or list DoorDash alongside Ramp as a company-level deployment. Confidence in the re-labelled version: high. Confidence that DoorDash-the-company operates a system called Team OS: low (~20%).

---

## 3. Three additional primary-sourced enterprise cases (2025–2026)

Selected for: (i) a **skills library** *and* (ii) an **org memory layer**, (iii) attested by the operating company itself.

### 3.1 Ramp Research — Ramp's agentic data analyst (the *other* Ramp case)

**Primary:** Faiz Hilaly, Cesar Duran, Jay Sobel, ["Meet Ramp Research: Our Agentic Data Analyst"](https://builders.ramp.com/post/meet-ramp-research), **Ramp Builders engineering blog, 2025-09-18**. Subtitle: *"How we built an AI agent that answers 1,000+ data questions a month."*

- **Numbers (company-reported):** "Since launching in early August, Ramp Research has answered over **1,800 data questions across more than 1,200 conversations with 300 different users**." "In the last 4 weeks, Ramp Research answered **1,476 questions in `#ramp-research-beta`, compared to 66 answered in `#help-data`**." `#ramp-research-beta` has 500+ members.
- **Org memory layer:** metadata aggregated and indexed from **dbt, Looker and Snowflake**, plus a curated human layer — "domain owners to write up technical documentation on their respective areas. These documents were then organized into a **file system**." That is the librarian pattern, staffed by humans, in production, a year before the Tan talk.
- **Evaluation discipline (rare and worth stealing):** evals score "not only the final answer but also the **intermediate steps, including expected tool calls, table references, and query shape**."
- **Governance:** "does not have access to any personally identifiable information (PII)."
- **Caveat:** absent from the `builders.ramp.com/feed.xml` RSS (48 items, checked 2026-09-10) — the post is live but unfeeded, so it is easy to miss.
- **Why it matters:** the `1,476 vs 66` comparison is the cleanest published *demand-side* number in the corpus for the "questions people didn't ask because asking was expensive" thesis — a **~22×** shift in question volume out of the human queue. It is also the origin of the "10–20× increase in questions asked" figure that circulates second-hand.

**Verdict: CONFIRMED (first-party, self-reported, unaudited).**

### 3.2 PowerSync — "Building Our Company Brain: Agents + SQLite, Offline-Capable"

**Primary:** [powersync.com/blog/building-our-company-brain-agents-sqlite-offline-capable](https://powersync.com/blog/building-our-company-brain-agents-sqlite-offline-capable), PowerSync engineering blog, **2026-07-24**.

This is the only case found that (a) explicitly answers the YC Company Brain RFS, (b) cites Karpathy and Tan's GBrain by name, and (c) publishes its architecture.

- **Ingest:** "a set of simple Node.js-based ingesters that mostly use APIs & Webhooks to aggregate data from **14 (and counting) different systems** like Google Drive, GitHub, Zendesk, Gong, HubSpot, Slack, etc. into a single **Postgres** database. The shape of the data is optimized for agent usability, using **Markdown for free text**."
- **Read path:** Postgres → PowerSync → local **SQLite** with an **FTS index**. Not a vector store. Deliberately.
- **The skill:** "We **dynamically generate a skill** that gives any agent useful information about the schema and SQLite query conventions (including using the `sqlite3` CLI)." The skill also carries "basic heuristics to decide what information is **authoritative**" — i.e. source-of-truth arbitration lives in the skill file.
- **Surfaces:** a Slack bot running `claude` in headless mode; a CLI that ships the synced SQLite + skill, usable **offline with local models**.
- **Access control:** by partial sync — "access control can be achieved by partially syncing the Postgres data to users based on their permissions," explicitly contrasted with Postgres RLS.
- **Roadmap (relevant to the write-side thesis):** "The first one will likely be **bi-directional syncing**. We can allow agents to **codify knowledge in the database** (e.g. customer intel, market knowledge)." — i.e. they built the read path first and are adding the write path second, which is exactly the sequencing the sweep predicts.
- **Corroborates YC:** "Our experience was very similar to what the YCombinator team [spoke about](https://www.youtube.com/watch?v=B246K_G7mHU&t=455s) when they built something similar with Postgres."
- **Caveat:** PowerSync is a small infrastructure company and PowerSync is its own product, so this is partly a product demo. No user counts, no quality numbers.

**Verdict: CONFIRMED (first-party engineering blog); scale unknown, no metrics.**

### 3.3 Y Combinator — QM, the harness YC runs itself on

**Primary (a):** YC's official page, <https://qm.ycombinator.com/index.html>:

> "We're open-sourcing an agent harness we call QM. It allows startups (**and YC**) to work with a fleet of OpenClaw-like agents. **Every employee and project gets one**, as needed."
> "YC has experimented with several harnesses… The first was a basic agent loop in Ruby, with some tools that could access internal data… we eventually extended it to support things like crons, and webhook triggers, but the launch of OpenClaw pushed us in a new direction. Next we **provisioned over 50 Hermes agents for individual employees** to work as personal assistants. Managing a fleet of even this size became challenging."
> Footnote: *"Short for quartermaster, the person on a ship who coordinates belowdecks to keep things in order."*

**Primary (b):** [`yc-software/qm`](https://github.com/yc-software/qm) — MIT, created **2026-07-29**, 14,770★, actively pushed (2026-09-09). README: *"Multiplayer agent harness for work. In Slack and on the web."*

Both halves of the pattern are first-class, documented features:

- **Skills library with governance** — [`docs/skill-registry.md`](https://raw.githubusercontent.com/yc-software/qm/main/docs/skill-registry.md): *"Import skills from a **git repo of `SKILL.md` files** into the governed skill store — no code change, no image rebuild. An admin registers a *pack*, browses it, and imports skills **org-wide**."* Eligibility filtering excludes personal-scope, owner-private, name-colliding, binary, or malformed skills with a visible reason; installs are **pinned to a git ref**; "update" = bump ref + idempotent re-import, with upstream-removed skills **archived**. Admin API is audited (`/v1/admin/skill-packs*`, `org_admin` only). The repo ships a `skills-seed/` directory with 21 seed skills (`memory`, `morning-digest`, `email-voice-profile`, `linear`, `google-workspace`, `taste-skill`, …).
- **Scoped org memory with pluggable providers** — [`docs/memory-providers.md`](https://raw.githubusercontent.com/yc-software/qm/main/docs/memory-providers.md): a scope-aware router where each of `personal | channel | group | team | org` can be routed to a different provider (built-in Postgres notebook, or an external MCP `search_knowledge`/`write_knowledge` service), each with an independent **capture policy**: `off` (recall only), `explicit` (deliberate writes only), `automatic` (post-turn capture). The shipped example routes personal/channel/group/team to the local notebook with `automatic` capture, and `org` scope to an external "Organizational knowledge" provider with **`explicit`** capture and `manage: false`.

That last detail is the notable one: **YC's own default configuration makes org-level memory write-gated and non-self-editing while personal memory is auto-captured.** It is the same read/write asymmetry Ramp landed on, expressed as configuration.

- **Caveat on framing:** widely reported as "the harness that runs Y Combinator" (marktechpost, startupfortune, et al., Aug 2026) — YC's own page says only that YC uses it and that every employee/project gets an agent. It does not claim QM runs the company. Use YC's wording.

**Verdict: CONFIRMED (YC-official page + MIT-licensed source).**

### 3.4 Honourable mention (not counted): Block's Buzz

[`block/buzz`](https://github.com/block/buzz) — Apache-2.0, created 2026-03-06, 32,458★, *"A workspace where humans and agents build together, on a relay you own."* Nostr-relay-backed: "every message, reaction, workflow step, review approval, and git event is a signed event in **one log**… whether the author is a person or a process." Agents get their own keypairs, channel memberships and audit trail ("agents are members, not bots"). Strong on **org memory + provenance** ("Ask the project a question and get an answer with receipts. Agents search six months of history and post the threads, not vibes"), but it does **not** ship a skills library, and Block's internal-usage claim was not verified from a Block-authored source in this pass. Listed as a lead, not a case.

Also noted for the record: `block/goose` now redirects to `aaif-goose/goose` (54,060★, Apache-2.0, created 2024-08-23), i.e. goose has been moved to a foundation org. Any corpus text asserting "Block's goose" should be checked.

---

## 4. Corrections to make in the corpus

1. `findings/garry-tan-ecosystem.md` line 99 — replace the Lockey citation for Ramp with the two LinkedIn Pulse URLs + the Ramp YouTube episode. Delete `ramp.com/blog/skills-and-glass` (404, never existed).
2. Same line — change "Hannah Stulberg's Team OS at DoorDash" to "a DoorDash PM's team-level Team OS, published personally."
3. `findings/completeness-critic.md` item 11 / item 8 — mark resolved: Ramp CONFIRMED, DoorDash PARTIALLY.
4. Anywhere "350 skills" appears — use "over 350 skills **shared**", and attribute to the Ramp employee authors, not to a Ramp blog.
5. Add the "99% AI adoption" figure as a **premise** of Glass, never as an outcome.
6. Flag the 700-users-vs-~2,400-headcount tension wherever "half the company" is quoted.

## 5. Residual uncertainty

- **Reddit was unreachable** (403 to curl, r.jina.ai and WebFetch alike) so the r/Ramp mirror could not be read directly; its full body was recovered from Brave Search's indexed snapshot and matches the LinkedIn article verbatim, so this does not affect the verdict.
- **WebSearch budget was exhausted** (200/200) before this task began; all search was done via `r.jina.ai`-proxied DuckDuckGo HTML and one uncaptcha'd Brave query. Coverage of non-indexed sources (X/Twitter posts by Ramp employees, DoorDash-internal materials) is therefore incomplete. An X-post sweep for `@` Ramp employees was not possible.
- **Ramp headcount** figures are third-party estimates only; no Ramp-official headcount was found.
- **No independent audit** exists for any number in this report. Every quantity (350 skills, 700 users, 99% adoption, 1,800 questions, 14 systems, 50 Hermes agents) is company-self-reported.

---

## Sources

**Ramp Glass / Dojo (primary)**
1. Sebastien Goddijn et al., "We Built Every Employee at Ramp Their Own AI Coworker", LinkedIn Pulse, 2026-04-09T16:49:57Z — https://www.linkedin.com/pulse/we-built-every-employee-ramp-own-ai-coworker-sebastien-goddijn-sfupe
2. Shane Buchan, "How We Built Glass: Vibe Coding a Product Used by 700 People", LinkedIn Pulse, ~2026-04-15 — https://www.linkedin.com/pulse/how-we-built-glass-vibe-coding-product-used-700-people-shane-buchan-okpie
3. Shane Buchan feed post — https://www.linkedin.com/posts/the-real-shane-buchan_how-we-built-glass-vibe-coding-a-product-activity-7450287991383781376-OKaK
4. Ramp (@tryramp), "We built our own AI workspace from scratch | Ramptables Episode 2 | Project Glass", YouTube, 2026-05-21 — https://www.youtube.com/watch?v=di0rLBrBP8A
5. r/Ramp mirror of (2), 2026-04-20 — https://www.reddit.com/r/Ramp/comments/1sr1vle/how_we_built_glass_vibe_coding_an_ai_coworker/ (403 to automated fetch; text recovered via search index)
6. Every (@EveryInc), "We Gave Every Employee an AI Agent. Here's What Happened.", YouTube, 2026-04-08 — https://www.youtube.com/watch?v=SRlTgIhESjw
7. Zack Field, "Ramp CLI v0.1.7: Four new skills, unified request search, and onboarding", ramp.com, 2026-05-15 — https://ramp.com/blog/ramp-cli-v017-new-skills-request-search (contains no Glass/Dojo content; checked to rule out)
8. **Dead link** cited by the secondary source — https://ramp.com/blog/skills-and-glass → HTTP 404, 2026-09-10

**Ramp Research (primary)**
9. Faiz Hilaly, Cesar Duran, Jay Sobel, "Meet Ramp Research: Our Agentic Data Analyst", Ramp Builders, 2025-09-18 — https://builders.ramp.com/post/meet-ramp-research
10. Ramp Builders RSS (48 items, used to enumerate the blog) — https://builders.ramp.com/feed.xml

**DoorDash / Team OS (primary)**
11. Hannah Stulberg, "About — In the Weeds" — https://hannahstulberg.substack.com/about
12. Aakash Gupta & Hannah Stulberg, "Build a team OS with Claude Code", Product Growth, 2026-04-07T21:06:28Z — https://www.news.aakashg.com/p/claude-code-team-os
13. Same article, mirrored in her repo — https://raw.githubusercontent.com/in-the-weeds-hannah-stulberg/substack-articles/main/standalone/build-a-team-os-with-claude-code/article.md
14. "How this PM Used Claude Code to Support 20 People", Aakash Gupta (@growproduct), YouTube — https://www.youtube.com/watch?v=0UArKLQ6bXA
15. https://github.com/in-the-weeds-hannah-stulberg/team-os-example-repo (171★, 2026-04-01, CC BY-NC 4.0)
16. https://github.com/in-the-weeds-hannah-stulberg/substack-articles (280★, 2026-03-21)
17. https://github.com/aakashg/product-growth-team-os (35★, 2026-05-06) — "based on Hannah's implementation at DoorDash"

**PowerSync (primary)**
18. "Building Our Company Brain: Agents + SQLite, Offline-Capable", PowerSync, 2026-07-24 — https://powersync.com/blog/building-our-company-brain-agents-sqlite-offline-capable

**Y Combinator / QM (primary)**
19. "QM — Open-Source Agent Harness from YC" — https://qm.ycombinator.com/index.html
20. https://github.com/yc-software/qm (MIT, 2026-07-29, 14,770★)
21. https://raw.githubusercontent.com/yc-software/qm/main/docs/skill-registry.md
22. https://raw.githubusercontent.com/yc-software/qm/main/docs/memory-providers.md
23. Y Combinator, "Inside YC's AI Playbook", YouTube — https://www.youtube.com/watch?v=B246K_G7mHU
24. Y Combinator, "Company Brain" (RFS short) — https://www.youtube.com/shorts/IaWIazkWWog

**Block (lead only)**
25. https://github.com/block/buzz (Apache-2.0, 2026-03-06, 32,458★)
26. https://github.com/aaif-goose/goose (formerly block/goose; Apache-2.0, 2024-08-23, 54,060★)

**Secondary (used only as lead-generators / for the citation audit)**
27. Alex Lockey, "Company Brain (YC RFS 2026): Four Builders, One Architecture", 2026-04-30 — https://www.alexlockey.com/writing/the-company-brain-four-builders-one-architecture/
28. AI Catchup, "Ramp Glass Playbook: Internal AI Workspaces for Company-Wide AI Adoption", 2026-04-15 — https://aicatchup.com/practices/internal-ai-workspaces-playbook
29. Revelio Labs, Ramp headcount — https://www.reveliolabs.com/companies/ramp-business/employees
30. "Working at Ramp in 2026" — https://jobsbyculture.com/blog/working-at-ramp-2026
31. hornof/llm-wiki `companies/doordash.md`, `concepts/company-brain.md` — https://github.com/hornof/llm-wiki (community wiki; corroborates that DoorDash-as-org has no observed AI-adoption disclosures)

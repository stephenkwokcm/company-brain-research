# Context Engineering & Skills — the 2025–2026 practice behind Garry Tan's "company brain"

**Dimension key:** `context-engineering-skills` · **Author:** research worker (Opus 5) · **Date:** 2026-09-10
**Primary source:** `sources/transcript_eBUyTS7SzV4.txt` (Garry Tan, *Every company should have a Brain*, AI Engineer, 2026-07-16)

---

## TL;DR

1. **Tan's org-chart metaphor is not a metaphor — it is a literal description of files that exist.** `skills/<slug>/SKILL.md` = employee, `skills/RESOLVER.md` = org chart, `skills/_brain-filing-rules.md` = internal process, `skills/<slug>/routing-eval.jsonl` = performance review. All four are in his MIT-licensed repo `github.com/garrytan/gbrain` (created 2026-04-05, 29,764 stars, 4,441 forks as of 2026-09-10), which ships 73 `SKILL.md` files and 44 routing-eval fixtures under `skills/`.
2. **The "skillify it" skill file is real and far more rigorous than the talk implies.** `skills/skillify/SKILL.md` (v2.0.0) is a **15-item checklist** gated by an `eval_contract` in frontmatter, a **cross-modal eval** (3 frontier models from 3 different providers must average ≥7 per dimension with no single score <5), and a **"no-regression law"** — an edit that scores below the previous receipt does not ship.
3. **"Resolver table" has measured value, not just vibes.** gbrain's `functional-area-resolver` skill publishes an A/B eval: compressing 270 bullet rows (25 KB) into 13 functional-area dispatcher rows (13 KB) *raised* routing accuracy from 81.7%→98.3% (Opus 4.7), 86.7%→100% (Sonnet 4.6), 73.3%→88.3% (Haiku 4.5). Stripping the `(dispatcher for: …)` clause collapsed Sonnet to 41.7%.
4. **"Trigger evals = performance reviews" is first-party industry practice, not Tan's coinage.** Anthropic's official `skill-creator` skill ships a **description optimizer** that generates 20 "trigger eval queries" (8–10 should-trigger, 8–10 near-miss should-not-trigger), runs each 3×, splits 60/40 train/held-out, and selects the winning `description` by *test* score to avoid overfitting.
5. **The "latent vs deterministic space" split is a 2022 research result rediscovered as ops doctrine.** PAL (arXiv:2211.10435, Nov 2022) beat PaLM-540B chain-of-thought by 15 points on GSM8K purely by delegating arithmetic to a Python interpreter; Anthropic's *Code execution with MCP* (2025-11-04) reports a 150,000→2,000 token reduction (98.7%) from the same move. Tan's "the 800 seats must not live in the context window" (10:12) is the operational form of both.

---

## 1. What the talk actually claims (with timestamps)

Tan gives the mapping at 04:31–05:32, without slides:

> "**A skill file is an employee.** It has one capability, one job, written down clearly enough that someone can execute it." (04:31)
> "**A resolver table** — the thing … when you run into Claude Code and it says your context is too big in Claude.md, you run off and create a resolver table … it's literally like whenever you need to alter a test, load tests.md … **That's an org chart.**" (04:40–05:06)
> "**Filing rules are your internal process.**" (05:10)
> "**Trigger evals.** Going in and actually having a test that says, 'When I need to alter a test file, does test.md actually get loaded?' Those are **performance reviews**." (05:22–05:32)
> "You're not writing software, you're hiring, training, and managing **a workforce made of markdown**." (06:01–06:03)

The computation split is at 09:04–10:14: **latent space** ("taste, judgment, understanding what a human actually wants when they say something vague … you steer it with the markdown file") vs **deterministic space** (TypeScript, Erlang). His diagnosis: "*all of the bugs … it's usually because something is happening in one side of the equation that should be in the other*" (08:49–09:01). His example is seating 800 people at Startup School: "*this actual storage of where everyone is inside this multi-dimensional array of 800 seats — it actually must not live in the context window.*" (10:03–10:14)

And the discipline at 15:26–16:22: "*never do one-off work* … **skillify it** … I have a blog post on X about that … because **if you have to ask for something twice, you failed.**"

---

## 2. The standards stack this sits on (2025 → 2026)

**Anthropic, *Effective context engineering for AI agents*, 2025-09-29** (shipped alongside Claude Sonnet 4.5) supplies the vocabulary Tan is using. Context engineering is "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference" — a superset of prompt engineering covering "system instructions, tools, Model Context Protocol (MCP), external data, message history." Its core mechanism claim is **context rot**: "as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases," grounded in the n² attention cost. Its prescription — "the smallest possible set of high-signal tokens" — is exactly what a resolver table is *for*. It also names the hybrid Claude Code uses: "CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time."
<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

**Agent Skills** became an open standard on **2025-12-18**, donated into the Linux Foundation-backed Agentic AI Foundation (co-founded 2025-12-09 by OpenAI, Anthropic and Block). The spec repo `agentskills/agentskills` (Apache-2.0, created 2025-12-16, 25,176 stars) defines the format Tan's skill files follow:
- Directory with a required `SKILL.md`; optional `scripts/`, `references/`, `assets/`.
- Frontmatter: required `name` (≤64 chars, `[a-z0-9-]`, must match the directory name) and `description` (≤1024 chars, "what it does *and* when to use it"); optional `license`, `compatibility` (≤500), `metadata`, `allowed-tools` (experimental).
- **Three-tier progressive disclosure**: metadata **~100 tokens** always loaded; SKILL.md body **<5,000 tokens recommended** loaded on activation; `scripts/`/`references/`/`assets/` **zero tokens until read**. Keep SKILL.md under 500 lines.
<https://agentskills.io/specification> · <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview> · <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills> (2025-10-16: "Building a skill for an agent is like putting together an onboarding guide for a new hire.")

**The resolver-adjacent mechanisms across harnesses** — this is where Tan's "org chart" idea is implemented four different ways:

| Mechanism | Trigger | Loaded | Determinism |
|---|---|---|---|
| `CLAUDE.md` (Claude Code) | always | every session, concatenated root→cwd; `CLAUDE.local.md` last | deterministic |
| `@path` imports in CLAUDE.md | always | at launch, max **4 hops** deep — *does not save context* | deterministic |
| `.claude/rules/*.md` with `paths:` frontmatter | glob match on files Claude reads | on demand | **deterministic** |
| Skill `description` matching | semantic match by the model | on activation | **latent** |
| gbrain `triggers:` array in frontmatter | substring match baseline + optional embeddings | on activation | hybrid |
| `AGENTS.md` (60k+ repos; OpenAI Codex, Cursor, Jules, Devin, Copilot, Zed, Warp…) | always; "closest AGENTS.md to the edited file wins" | at launch | deterministic |
| Cursor `.cursor/rules/*.mdc` | 4 modes: `alwaysApply`, `globs`, `description`-selected, `@`-mention | varies | mixed |
| MCP **resources** | **application-driven** — "host applications determining how to incorporate context"; `annotations.priority` 0.0–1.0 | client's choice | outside the model |

Sources: <https://code.claude.com/docs/en/memory> · <https://agents.md/> · <https://cursor.com/docs/context/rules> · <https://modelcontextprotocol.io/docs/concepts/resources>

Two details matter for anyone copying Tan. First, **Claude Code's own docs contradict the naive resolver instinct**: `@path` imports "still load and enter the context window at launch" — only `paths:`-scoped rules and skills actually defer. Target **under 200 lines per CLAUDE.md**; files over 4 MiB are skipped entirely. Second, Claude Code now has **auto memory** (`~/.claude/projects/<project>/memory/MEMORY.md`, first 200 lines / 25 KB loaded per session, topic files read on demand) — a first-party implementation of the "hot memory vs cold reference" split Tan names at 13:15.

---

## 3. The "skillify it" skill file, decoded

`https://github.com/garrytan/gbrain/blob/master/skills/skillify/SKILL.md` — v2.0.0, `mutating: true`, triggers `"skillify this"`, `"is this a skill?"`, `"make this proper"`, `"did this skill regress"`.

**Phase 0 is a gate, not a scaffold.** "Will this be invoked 2+ times? Is there >20 lines of logic? Does it have a clear trigger phrase a user would actually say? If ANY answer is no, **it's a script, not a skill — stop here.**" Plus a scope rule: one skill = one coherent trigger family, and a DRY/MECE pre-check that greps `RESOLVER.md` for colliding triggers and prefers *merging* over near-duplicates.

**The 15-item checklist** (verbatim):
```
□ 0.  Eval contract      — goal + skill-specific dimensions + hard-fails
□ 1.  SKILL.md           — frontmatter + contract + phases
□ 2.  Code               — deterministic script if applicable
□ 3.  Cross-modal eval   — 3 frontier models from 3 providers critique output vs contract
□ 3b. No-regression gate — new eval ≥ previous iteration (forward only)
□ 4.  Unit tests         □ 5. Integration tests    □ 6. LLM evals
□ 7.  Resolver trigger   — entry in skills/RESOLVER.md with real user phrases
□ 8.  Resolver eval      — test that triggers route to this skill
□ 9.  Check-resolvable   — DRY + MECE audit, no orphans
□ 10. E2E test           □ 11. Brain filing        □ 12. Scheduled-run observability
□ 13. Scheduled-task re-run                        □ 14. Plugin membership
```
This is a superset of the 10-step list circulating in secondary coverage of Tan's X article (items 0, 3b, 12–14 are the v2.0.0 additions).

**The load-bearing inventions:**
- **`eval_contract` in frontmatter** — `goal`, 3–6 skill-specific `dimensions`, and `hard_fails` that auto-zero the score. Rationale: "*A cross-modal eval is only as good as what you ask it to judge. Generic dimensions catch slop but miss whether the output achieves THIS skill's specific purpose.*" The contract is *versioned with the skill* so scores compare apples-to-apples across iterations — that is what makes the regression gate meaningful.
- **Ordering: eval before tests.** "*Tests lock in behavior. If the behavior is mediocre, tests lock in mediocrity.*" Cross-modal eval runs ≤3 cycles, then tests cement the proven-good behavior.
- **Different-provider requirement.** Default slots: `openai:gpt-5.2`, `anthropic:claude-opus-4-7`, `deepseek:deepseek-v4-pro`. "*These MUST be frontier models from DIFFERENT providers … different families have less correlated blind spots.*" Cost: 3 cycles × 3 models = 9 frontier calls, "$1–3 per full run."
- **Receipts as baselines.** Each run writes `~/.gbrain/.gbrain/eval-receipts/<slug>-<sha8>.json`, the sha-8 binding the receipt to the SKILL.md content that produced it. Ship rule: "new overall ≥ prior overall AND no dimension mean dropped by more than 0.5."
- **Bug-fix template** — every fix appends `## Bug: [Date]` with root cause, fix, **"Hard rule added"**, and tests. This is the mechanism that stops "a bad skill file encodes a bad process forever" (14:41).

---

## 4. Resolver tables: the numbers

`skills/RESOLVER.md` is 16.3 KB and opens with an explicit precedence rule: "*each skill's frontmatter `triggers:` array is the authoritative routing signal … This file is the human-readable dispatch map of the same routing. If a row here and a skill's frontmatter disagree, the frontmatter wins; fix the row.*" It has ~10 sections (Always-on, Brain operations, Content ingestion, Thinking skills, Operational, Setup & migration, Identity & access) plus 8 numbered **disambiguation rules** ("prefer the most specific skill (meeting-ingestion over ingest)") and a **Conventions** block of cross-cutting files every brain-writing skill defers to.

The compression pattern and its evidence live in `skills/functional-area-resolver/SKILL.md`. Method: 3 Anthropic models × 3 variants × 20 training fixtures + 5 held-out, n=3 seeded repeats, scored STRICT (exact slug) and LENIENT (right dispatcher area). LENIENT training results:

| Variant | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 | Size |
|---|---|---|---|---|
| baseline (270 bullet rows) | 81.7% ±7.2 | 86.7% ±7.2 | 73.3% ±7.2 | 25 KB |
| **functional-areas** | **98.3% ±7.2** | **100% ±0** | **88.3% ±7.2** | **13 KB** |
| resolver-of-resolvers (no dispatcher clause) | 63.3% ±14.3 | 41.7% ±7.2 | 65.0% ±12.4 | 10 KB |

Two honest caveats the skill itself states: the **held-out set is saturated at 100% for baseline and functional-areas** (so the gain is only visible on the training corpus), and "*with a naive 'return the skill slug' prompt … every compression variant collapses to ~30–60% on Opus*" — the win depends on a dispatcher-aware prompt. Reproduction commands and receipts are in `evals/functional-area-resolver/baseline-runs/2026-05-11-*.jsonl`.

---

## 5. Trigger evals as performance reviews — three independent implementations

**(a) gbrain `routing-eval.jsonl`** (44 of 73 skills carry one). Format is one JSON object per line with comment lines allowed:
```jsonl
{"intent":"Skillify this workflow end to end — full checklist, eval contract, and resolver row","expected_skill":"skillify"}
{"intent":"Did this skill regress after my edit? Compare the fresh score against the prior baseline","expected_skill":"skillify"}
{"intent":"Skillify this new skill draft…","expected_skill":"skillify","ambiguous_with":["skill-creator"]}
{"intent":"Which of our skills are bundled into the plugin for downstream installs?","expected_skill":null}
```
Note the three fixture classes: positives, **`ambiguous_with`** (declared confusions), and **negatives (`expected_skill: null`)**. Backstopped by `gbrain check-resolvable --json`, which finds not just wrong routes but skills with **no path from the resolver at all** — orphans, MECE overlap, DRY violations.

**(b) Anthropic's `skill-creator`** (bundled with Claude Code). Its Description Optimization section: "*The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill.*" Generate 20 realistic queries, half **near-miss negatives** ("*don't make should-not-trigger queries obviously irrelevant — 'Write a fibonacci function' as a negative test for a PDF skill is too easy*"), run `scripts/run_loop.py` with 60/40 train/test split, 3 repeats per query, ≤5 iterations, select `best_description` **by test score to avoid overfitting**. It also documents a non-obvious failure mode: "*Claude only consults skills for tasks it can't easily handle on its own*" — so trivial queries won't trigger a skill regardless of description quality.

**(c) Academic**. *SkillAxe* (arXiv:2606.10546, Gautam/Radhakrishna/Gulwani, 2026-06-09) decomposes skill quality into exactly the dimensions this practice implies — **quality impact, trigger precision, instruction compliance with fault attribution, and solution-path coverage** — and reports the sobering baseline: human-authored skills gain **+16.2 pp** on SkillsBench while "**LLM-authored skills provide no measurable gain**." Their unsupervised refinement recovers 47–67% of that gap (+28% relative pass rate) and lifts SpreadsheetBench 16.0%→52.0% with 22 skills. Separately, *Agent Skills: A Data-Driven Analysis* (arXiv:2602.08004, 2026-02-08) surveyed **40,285 public skills** and found "widespread intent-level redundancy" plus "non-trivial safety risks, including skills enabling state-changing or system-level actions."

---

## 6. Latent vs deterministic space — the prior art

Tan's split restates a well-evidenced line of work:
- **PAL: Program-aided Language Models** (arXiv:2211.10435, Gao et al., 2022-11-18): the LM reads and decomposes, "solving is delegated to the interpreter." **+15 pp absolute over PaLM-540B chain-of-thought on GSM8K** with a smaller model. The failure mode PAL names — "LLMs often make logical and arithmetic mistakes in the solution part, even when the problem is decomposed correctly" — *is* Tan's "computation on the wrong side."
- **Anthropic, Code execution with MCP** (2025-11-04): present tools as a filesystem, load on demand; "*This reduces the token usage from 150,000 tokens to 2,000 tokens — a time and cost saving of 98.7%*." Also: "*intermediate results stay in the execution environment by default*" — a privacy argument for keeping state out of the window that Tan does not make.
- **Agent Skills' Level 3**: "*when Claude runs `validate_form.py`, the script's code never loads into the context window. Only its output consumes tokens.*" This is "state must not live in the context window," implemented in the spec.
- **Anthropic's structured note-taking / memory tool** (public beta as of the Sept 2025 post) and **sub-agents returning "a condensed, distilled summary … (often 1,000–2,000 tokens)"** are the same principle applied to memory and to fan-out.

---

## 7. Copyable patterns

1. **Two-layer resolver.** Don't write one row per skill. Write one row per *functional area* with an explicit `(dispatcher for: a, b, c, …)` clause, and let the area's SKILL.md do the second hop. Keep the clause — it is the load-bearing signal.
2. **Frontmatter is authoritative; the table is a view.** Adopt gbrain's rule verbatim: if `RESOLVER.md` and a skill's `triggers:`/`description` disagree, frontmatter wins; the row is the bug.
3. **Ship three fixture classes per skill**, not just positives: `expected_skill: <slug>`, `ambiguous_with: [...]`, and `expected_skill: null` near-misses. Aim for 8–10 of each per Anthropic's optimizer.
4. **Declare an `eval_contract` before you evaluate.** Goal + 3–6 skill-specific dimensions + hard-fails, in frontmatter, versioned with the skill.
5. **Eval → fix → *then* tests.** Never write the test suite first; you will lock in mediocrity.
6. **Keep a receipt lineage keyed to the content hash** so "did this get worse?" is answerable mechanically. Ship rule: overall ≥ prior, no dimension down >0.5.
7. **Run a periodic context audit.** gbrain's `context-audit` skill is report-only, measures with `wc -c` ÷ ~4 chars/token ("*measured, not guessed*"), and ranks findings by token savings with a risk class — a maintenance loop for CLAUDE.md/AGENTS.md/MEMORY.md drift that has no first-party equivalent (Claude Code's `/doctor` trim check is the closest).
8. **Enforce the skill/script boundary.** "*Will this be invoked 2+ times? >20 lines of logic? A trigger phrase a user would actually say?* If any answer is no, it's a script."

---

## 8. Relevance to the company-brain / RAG / fruit-fly questions

**To RAG.** This dimension supplies the strongest version of Tan's "it's not just RAG" claim (13:00). Everything above is the *write* and *route* side, which classical RAG has no opinion about: what gets written (`_brain-filing-rules.md`'s notability gate — "*a junk page wastes attention and degrades search quality*"), provenance (mandatory inline `[Source: …]` citations with a 4-level precedence: user statements > compiled truth > timeline > external APIs), linking (the "Iron Law" of mandatory bidirectional back-links — "*an unlinked mention is a broken brain; the graph is the intelligence*"), and arbitration (`correction-pipeline` triggered by "that's wrong", "I never said that"). Note that gbrain's own `docs/eval/SEARCH_MODE_METHODOLOGY.md` and BrainBench framing show the *retrieval* side is still evaluated conventionally — so the accurate claim is "RAG plus a curation/routing layer," not "not RAG."

**To the fruit-fly question.** One genuine structural echo worth flagging for that dimension: progressive disclosure's metadata tier (~100 tokens per skill, matched semantically, then a full read) is functionally a **sparse tag → expand** architecture, the same shape as fly-inspired locality-sensitive hashing (FlyHash) and mushroom-body Kenyon-cell sparse coding. But I found **no source connecting Agent Skills or resolver tables to connectome work**; treat any such link as analogy, not lineage. The stronger cross-over is *forgetting*: `context-audit` (prune the always-loaded stack) and the notability gate are engineered analogues of synaptic pruning, and neither has a biological citation in the sources I read.

---

## 9. Where the org-chart metaphor holds — and where it strains

**Accurate.**
- *Skill = employee* holds unusually well. One capability, a written contract, a scoped tool list (`allowed-tools`/`tools:`), a performance record (`eval-receipts/`), a written-up incident log (`## Bug:` entries with a "hard rule added"), and versioning with a promotion path (`skillpack-harvest`: "lift this skill upstream").
- *Trigger eval = performance review* holds best of all, and is validated by three independent implementations plus SkillAxe's "trigger precision" dimension.
- *Filing rules = process* holds: `_brain-filing-rules.md` reads exactly like a records-management SOP, complete with a "Common Misfiling Patterns — DO NOT DO THESE" table.

**Strained.**
- *Resolver = org chart* is the weakest link. An org chart encodes **authority and escalation**; a resolver encodes **retrieval**. gbrain's own disambiguation rules and `ask-user` choice-gate exist precisely because the resolver has no authority to break ties — a real org chart does. The functional-area result also shows the resolver behaves like an **index with a prefetch hint**, not a reporting line: it wins by giving the model *area recognition plus a visible sub-skill list*, then getting out of the way.
- *Hiring* has no analogue for the hardest management problem. SkillAxe's finding that **LLM-authored skills provide no measurable gain** while human-authored ones give +16.2 pp means a "workforce made of markdown" that hires itself is, on current evidence, hiring zeros. Tan's `skillify` is in effect an admission of this: the checklist exists because raw skillification does not work.
- *Firing/attrition is absent from the metaphor but is the dominant maintenance cost.* The 40,285-skill survey's "widespread intent-level redundancy" is org-chart bloat with no headcount review. gbrain answers with `check-resolvable`, MECE audits, and merge-over-create — but those are **library science**, not management.
- *400X* is a claim about wiring, and none of these artifacts measures throughput. The measured numbers here are routing accuracy and token cost. Nothing in the skills/context-engineering literature substantiates a productivity multiplier.

---

## 10. Open questions

1. **Does the functional-area result generalize off Anthropic models?** Only Opus 4.7 / Sonnet 4.6 / Haiku 4.5 were tested, and the held-out set was saturated. No cross-vendor replication found.
2. **What is the actual context cost of the always-loaded tier at scale?** ~100 tokens × 73 skills ≈ 7 KB before RESOLVER.md's 16 KB. Is loading both redundant? gbrain says frontmatter is authoritative, yet also ships the table — nobody has published the ablation.
3. **Is "3 frontier models from 3 providers" defensible, or expensive theatre?** No published inter-rater agreement or cost/benefit curve vs. a single strong judge with a good rubric.
4. **Does the no-regression law cause ratchet lockup?** A forward-only rule on a noisy LLM judge (±0.5 tolerance) will eventually block legitimate refactors. No data on false-block rate.
5. **Where is the security review?** arXiv:2602.08004 flags skills with state-changing/system-level actions; Anthropic's docs warn "treat like installing software"; gbrain has `untrusted-content.md` and a trust boundary. Nobody has evaluated resolver-level prompt injection — a poisoned `triggers:` array is an org-chart takeover.
6. **Could not verify Tan's original X article text** (x.com returns HTTP 402 to fetch). The 10-step checklist quoted in secondary coverage matches items 1–11 of the repo's 15, so I treat the repo as the authoritative version.

---

## Sources

- Transcript: `sources/transcript_eBUyTS7SzV4.txt` (timestamps 04:31, 04:40–05:06, 05:10, 05:22–05:32, 06:01, 08:49–10:14, 13:00–13:25, 14:41, 15:26–16:22, 18:14)
- Anthropic, *Effective context engineering for AI agents*, 2025-09-29 — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, *Equipping agents for the real world with Agent Skills*, 2025-10-16 — https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic, *Code execution with MCP*, 2025-11-04 — https://www.anthropic.com/engineering/code-execution-with-mcp
- Agent Skills specification — https://agentskills.io/specification · repo https://github.com/agentskills/agentskills
- Claude Platform docs, *Agent Skills overview* — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code docs, *How Claude remembers your project* (CLAUDE.md, `.claude/rules/`, auto memory) — https://code.claude.com/docs/en/memory
- AGENTS.md — https://agents.md/
- Cursor, *Rules* — https://cursor.com/docs/context/rules
- MCP, *Resources* (spec 2026-07-28) — https://modelcontextprotocol.io/docs/concepts/resources
- garrytan/gbrain (MIT, created 2026-04-05; 29,764★ / 4,441 forks on 2026-09-10) — https://github.com/garrytan/gbrain
  - `skills/skillify/SKILL.md` — https://github.com/garrytan/gbrain/blob/master/skills/skillify/SKILL.md
  - `skills/RESOLVER.md` — https://github.com/garrytan/gbrain/blob/master/skills/RESOLVER.md
  - `skills/_AGENT_README.md` · `skills/_brain-filing-rules.md` · `skills/context-audit/SKILL.md` · `skills/functional-area-resolver/SKILL.md` · `skills/skillify/routing-eval.jsonl`
- Anthropic `skill-creator` skill (local, bundled with Claude Code): `/Users/stephen/.claude/plugins/cache/claude-plugins-official/skill-creator/4b909c3492b3/skills/skill-creator/SKILL.md`
- Gao et al., *PAL: Program-aided Language Models*, arXiv:2211.10435 (2022-11-18) — https://arxiv.org/abs/2211.10435
- Gautam, Radhakrishna, Gulwani, *SkillAxe*, arXiv:2606.10546 (2026-06-09) — https://arxiv.org/abs/2606.10546
- Ling, Zhong, Huang, *Agent Skills: A Data-Driven Analysis*, arXiv:2602.08004 (2026-02-08) — https://arxiv.org/abs/2602.08004
- Secondary (used only for the 10-step checklist provenance): https://gu-log.vercel.app/en/posts/en-gp-179-20260422-garrytan-skillify-agent-failures · https://www.the-ai-corner.com/p/garry-tan-personal-agi
- Agent Skills open-standard release coverage: https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/ · https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/

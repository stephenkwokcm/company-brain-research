# Memory Hygiene: provenance, contradiction, decay, poisoning, skill drift

Dimension key: `memory-hygiene` · Written 2026-09-10 · Sources fetched live (all URLs verified by fetch unless flagged)

Tan's claim at [14:46] of the transcript: *"the primitive is not memory. It's memory plus hygiene, provenance on every fact, contradiction checks when new information collides with the old, and a librarian, human plus agent, whose actual job is pruning."* His three named failure modes — garbage dump with great search, stale fact with total confidence, bad skill file that encodes a bad process forever — each map onto a live research literature and, unusually, onto shipped code in his own repo. This report grades each.

## TL;DR

- **Stale facts are the best-measured failure mode, and embeddings provably cannot fix them.** Cosine similarity separates "contradicted fact" from "rephrased duplicate" at AUROC **0.59** — barely above chance — so vanilla RAG serves superseded values **15–40%** of the time ([arXiv:2606.26511](https://arxiv.org/abs/2606.26511)). The fix is structural, not better ranking: a bi-temporal ledger with deterministic `(subject, relation, object)` supersession.
- **Bounded agent memory makes staleness *worse* than no memory at all, and more memory doesn't help.** On LongMemEval's knowledge-update subset, replacing full context with self-managed memory drops a frontier model from **92% → 77%**; granting proportionally more memory moves accuracy **28% → 28%** ([arXiv:2606.27472](https://arxiv.org/abs/2606.27472)). Curation policy, not capacity, is the binding constraint — which is Tan's point, empirically.
- **Provenance has a standard (W3C PROV-DM) and an agent profile (PROV-AGENT), but citation ≠ grounding.** Up to **57%** of citations in attributed RAG answers are *correct but unfaithful* — post-rationalised rather than actually relied on ([arXiv:2412.18004](https://arxiv.org/abs/2412.18004)). Provenance-on-every-fact is necessary and far from sufficient.
- **Memory is now a first-class attack surface.** MINJA poisons agent memory through ordinary queries at **>95%** injection / **70%** attack success ([arXiv:2503.03704](https://arxiv.org/abs/2503.03704)); OWASP lists Memory Poisoning as **T1** in its agentic threat taxonomy. GBrain's own guardrail layer is deliberately **observe-only and fail-open** — it *cannot* block a poisoned ingest ([docs/guardrails.md](https://github.com/garrytan/gbrain/blob/master/docs/guardrails.md)).
- **"Bad skill encodes bad process forever" is the one failure mode with a clean, shipped answer:** eval-gated skill mutation. SkillOpt (Microsoft Research, May 2026) only accepts edits that strictly improve a held-out validation score (**+23.5/+24.8/+19.1** points across three harnesses on GPT-5.5, best-or-tied on all 52 model×benchmark×harness combos, [arXiv:2605.23904](https://arxiv.org/abs/2605.23904)); GBrain wraps it as `gbrain skillopt` with a median-of-3 + ε=0.05 acceptance gate.

---

## 1. Provenance and attribution

**State of the art.** The vocabulary is settled: [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) (a W3C Recommendation) gives entities / activities / agents plus derivation relations. [PROV-AGENT](https://arxiv.org/html/2508.02866) (Souza et al., ORNL/Argonne, IEEE eScience 2025) extends PROV to agentic workflows over MCP, modelling prompts, responses, decisions and tool interactions as first-class provenance so that one agent's hallucination can be traced when it becomes another's input. The 2026 survey [*From Agent Traces to Trust*](https://arxiv.org/html/2606.04990v1) consolidates this into seven typed relations that are exactly the hygiene primitives Tan names: **support, derive, depend-on, contradict, invalidate, trigger, update**.

**The gap nobody markets.** Citation *correctness* (does the cited doc entail the claim?) is routinely measured; citation *faithfulness* (did the model actually use it?) is not. Wallat et al. find **up to 57%** of citations unfaithful ([arXiv:2412.18004](https://arxiv.org/abs/2412.18004), SIGIR ICTIR 2025). A company brain that grades itself on "every fact has a `[Source: …]`" is measuring the easy half.

**Open implementations.** [Eywa](https://arxiv.org/pdf/2605.30771) (May 2026) is the cleanest architectural statement — "evidence before belief": immutable source evidence is stored *before* canonical facts are derived, retrieval is a deterministic multi-route read with **zero LLM calls inside retrieval**, and retrieved context is returned separately from answer instructions (LoCoMo 90.19%, LongMemEval-S 88.2%, BEAM 81.45%). GBrain implements the same shape in markdown: a per-page **compiled truth** zone that is *rewritten*, above an append-only, immutable **timeline** of cited evidence ([compiled-truth.md](https://github.com/garrytan/gbrain/blob/master/docs/guides/compiled-truth.md)), with a mandated citation grammar `[Source: {who}, {channel}, {date time tz}]` and an explicit source-authority ladder — user direct statements > primary sources > enrichment APIs > web > social ([source-attribution.md](https://github.com/garrytan/gbrain/blob/master/docs/guides/source-attribution.md)). A dedicated `citation-fixer` skill sweeps pages for uncited facts and URL-less tweet references and repairs them deterministically.

**Recommended policy.** (1) Two zones per entity: append-only evidence, rewritable synthesis; never let a synthesis claim exist without a timeline row. (2) Store provenance as PROV-shaped rows, not prose — `source_id`, `channel`, `observed_at`, `ingested_at`, `authority_tier`. (3) Measure faithfulness, not just presence: sample N answers/week and NLI-check each cited span. (4) Make "uncited fact" a doctor-check failure, not a lint warning.

## 2. Contradiction detection and arbitration

**Taxonomy.** [*Knowledge Conflicts for LLMs: A Survey*](https://aclanthology.org/2024.emnlp-main.486/) (Xu et al., EMNLP 2024) is the canonical frame: **context-memory**, **inter-context**, and **intra-memory** conflict. A company brain lives almost entirely in the second — two of *your own* documents disagree.

**Best available technique.** [Astute RAG](https://arxiv.org/abs/2410.07176) (ACL 2025) consolidates internal and external knowledge with source-awareness and resolves by reliability; it is the only method reported to match or beat plain LLM use in the worst case. [ConflictRAG](https://arxiv.org/html/2605.17301v1) (May 2026) is the more operational design: a two-stage detector (embedding MLP handles **73% of pairs at 120ms**, uncertain cases below 0.7 confidence escalate to an LLM) reaching **90.8%** detection accuracy at **62%** lower cost, plus an Entropy-TOPSIS credibility model that learns that **authority (0.312)** and **recency (0.245)** dominate the five criteria, giving **82.7%** source-selection accuracy (**+7.1pp** over hand-written heuristics). Its **CARS** score (correctness 0.35 / detection F1 0.25 / resolution appropriateness 0.25 / source fidelity 0.15) is the closest thing to a hygiene KPI in the literature. Code "upon acceptance" — unverified.

**Practice.** GBrain ships `gbrain eval suspected-contradictions` ([docs/contradictions.md](https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md)): sample retrieval results, pre-filter pairs >30d apart, cache judge verdicts keyed on `(chunk_a_hash, chunk_b_hash, model, prompt_version, truncation_policy)`, judge with a confidence floor ≥0.7, grade severity low (naming) / medium (stale values) / high (identity & structural claims), and report `queries_with_contradiction / queries_evaluated` **with a Wilson 95% CI** and a `small_sample_note` below n=30. The decision rule is explicit: CI lower bound <5% → do nothing; 5–15% → operator judgement; >15% → build the chunk-level `revises` field. Judge cost is ~$1/$5 per Mtok on claude-haiku-4-5. This is the most disciplined published contradiction-probe design I found, academic work included — note the *probe reports, the operator resolves*.

Its own [May 2026 RFC](https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md) is the honest counterweight: a production run surfaced **~115 HIGH findings**, and hand-walking them showed the probe "can't distinguish *this changed* from *this is wrong*" — role changes and status transitions were flagged as contradictions, and explicit negations ("NOT bob's event") were parsed as positive claims. The proposed fix is to pass source dates to the judge and populate the already-existing but "sparsely populated" `valid_from` / `valid_until` columns.

**Recommended policy.** Detect on a *sampled* schedule, not on every write (cost). Classify before resolving: `temporal-supersession` ≠ `contradiction` ≠ `intentional debate`. Auto-resolve only temporal supersession where the newer side is itself a structured claim; everything else emits a paste-ready command for a human. Never silently pick a winner — record both with citations.

## 3. Staleness, temporal validity, decay and forgetting

**The structural result.** [MemStrata](https://arxiv.org/abs/2606.26511) (Yadav, Jun 2026) shows the stale-fact problem is not a tuning problem: embeddings score a contradicted old value and a rephrased current one almost identically (**AUROC 0.59**). With a deterministic supersession rule over an SPO-keyed bi-temporal ledger, accuracy on evolving knowledge goes **0.20–0.47 → 0.95–1.00**, superseded-value serving **15–40% → ~0%**, at **2.1s** vs 16–18s for LLM-reranking baselines. [Supersede](https://arxiv.org/abs/2606.27472) supplies the training-side complement and the most decision-relevant number in this report: bounded self-managed memory *loses* 15 points versus full context on knowledge-update questions, and extra capacity recovers nothing.

**Bi-temporality in production.** [Zep/Graphiti](https://arxiv.org/abs/2501.13956) is the reference implementation: four timestamps per edge — `t_created`/`t_expired` (system/ingestion time) and `t_valid`/`t_invalid` (world time) — and supersession **invalidates rather than deletes**. Graphiti is open source and the most widely deployed instance of the pattern.

**Decay.** The forgetting literature converged in 2026 on a four-way taxonomy — passive decay, active deletion, safety-triggered removal, adaptive reinforcement ([FSFM, arXiv:2604.20300](https://arxiv.org/abs/2604.20300), reporting +8.49% access efficiency, +29.2% signal-to-noise, and "100% elimination of security risks" — treat the last as a benchmark artifact). [*When to Forget*](https://arxiv.org/abs/2604.12007) proposes **Memory Worth**, a two-counter per-memory statistic tracking success-vs-failure co-occurrence (ρ = 0.89 ± 0.02 with true utility after 10k episodes); the authors are explicit that it is association, not causation. Practitioner guidance ([Hindsight, 2026-05-21](https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation)) gives the cleanest lever set — **importance** (filter at write time; "the cheapest place to control memory quality"), **merge** (entity resolution + recency-wins invalidation), **decay** (confidence, not deletion), **eviction** (reserve hard deletes for GDPR/PII/user request).

**GBrain's implementation is more concrete than most papers.** `src/core/facts/decay.ts` is a per-kind half-life table — `event 7d, commitment 90d, preference 90d, belief/fact/idea 365d` — with `confidence × exp(-age_days / halflife)` and a hard 0 past `valid_until`. `ttl-parse.ts` frozen grammar accepts `30d`/`12h`/ISO dates and deliberately rejects ISO-8601 durations as a documented trap. `forget.ts` fixes a hygiene bug class worth internalising: a forget implemented as a DB `UPDATE` **evaporated on the next rebuild** because the canonical markdown fence was unchanged; forget is now a fence rewrite (strikethrough + `valid_until: today` + `forgotten: <reason>`) so the deletion is reconstructible — and the nightly dream cycle no longer undoes it.

**Freshness is a monitoring problem too.** [BRAIN_CURRENCY.md](https://github.com/garrytan/gbrain/blob/master/docs/designs/BRAIN_CURRENCY.md) (2026-08-10) documents a real incident on the founder's own machine: autopilot died 2026-05-31 and stayed dead **71 days** while three status surfaces reported healthy, because the staleness function measured *drain completeness* rather than *elapsed time* and discarded the wall-clock number. Fix: an absolute ceiling (`GBRAIN_STALENESS_CEILING_HOURS`, default 72). "Stale fact with total confidence" has an infrastructure sibling — *stale brain with a green dashboard*.

**Recommended policy.** (1) Store `valid_from`/`valid_until` + `ingested_at` on every fact; make `valid_until` mandatory for `event` and `commitment` kinds. (2) Supersede deterministically on an SPO key; invalidate, never delete. (3) Decay confidence by kind-specific half-life and surface effective confidence at retrieval time. (4) Hard-delete only for compliance. (5) Alarm on wall-clock source lag with an absolute ceiling, independent of "did the last sync succeed".

## 4. Memory poisoning and injection

MINJA ([arXiv:2503.03704](https://arxiv.org/abs/2503.03704)) plants malicious records using only ordinary queries and observed outputs — no write access — at **>95%** injection and **70%** attack success; AgentPoison (NeurIPS 2024) backdoors the retrieval corpus at **80%+** across driving/QA/healthcare agents; MemoryGraft plants fabricated "successful experiences" that get retrieved naturally ([mem0 security review, 2026-02-11](https://mem0.ai/blog/ai-memory-security-best-practices)). OWASP now ranks **Memory Poisoning as T1** in the agentic taxonomy ([genai.owasp.org](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)). The follow-up study ([arXiv:2601.05504](https://arxiv.org/abs/2601.05504)) is the useful one for operators: attack effectiveness **drops sharply once realistic pre-existing legitimate memories are present**, and their two defenses — composite-trust I/O moderation and memory sanitization via temporal decay + trust-aware retrieval — need careful calibration to avoid over-rejection. A certified-defense line exists ([SMSR, arXiv:2606.12703](https://arxiv.org/pdf/2606.12703)) but its repo has essentially no adoption; treat as research-grade.

The company-brain-specific risk is that ingestion is the attack surface: an agent that ingests email, meeting transcripts and web pages "while you sleep" will eventually ingest an instruction. **GBrain's answer today is a deliberate non-answer**: five guardrail seams (`file_storage.markdown`, `file_storage.code`, `ai_gateway.chat|expand|tool_input`) that are **observe-only** — `runGuardrails()` returns `void`, callers never branch on a verdict — and **fail-open** on timeout or throw; the OSS distribution ships with zero providers registered. Loading is fail-closed (a broken `GBRAIN_GUARDRAILS_MODULE` exits 1), but classification never blocks. Anyone deploying a company brain must add enforcement themselves.

**Recommended policy.** Provenance tier = trust tier: content from untrusted channels enters as evidence with `authority_tier = external`, never as compiled truth, and never as a *skill*. Quarantine-then-promote: agent-written pages need a second signal (human, or corroboration from a higher tier) before they can be retrieved as fact. Namespace isolation at the storage layer (GBrain does this with Postgres RLS per login). Audit every write with actor + session. TTL everything from low-trust channels so a poisoned row expires on its own.

## 5. Skill drift and eval-gated skill updates

This is the failure mode Tan states most strongly ("a bad skill file encodes a bad process forever") and, happily, the one with the crispest answer. [SkillOpt](https://arxiv.org/abs/2605.23904) (Microsoft Research, May 2026) treats `SKILL.md` as trainable text-space parameters: an optimizer model proposes bounded add/delete/replace edits from scored rollouts, and **edits are accepted only when they strictly improve validation** — with textual learning-rate budgets, a rejected-edit buffer, and zero inference-time overhead. GBrain's [`gbrain skillopt`](https://github.com/garrytan/gbrain/blob/master/docs/guides/skillopt.md) hardens this into an operational contract: median-of-3 judge runs with **ε = 0.05** acceptance margin, per-step version snapshots, an append-only `history.json`, an ISO-week-rotated audit trail, a `--max-cost-usd` preflight, and — the important one — **mutating a bundled skill in place requires a disjoint `--held-out` set of ≥5 rows, and a candidate that beats the benchmark but regresses on held-out is refused.** Industry guidance agrees on the gate ("a skill shouldn't ship until it matches or beats baseline on the *quality* metric, not just the efficiency metric" — [Future AGI](https://futureagi.com/blog/agent-skill-regression-testing/)); OpenAI's [eval-skills guide](https://developers.openai.com/blog/eval-skills) recommends a 10–20 case prompt set with deterministic graders plus rubric grading, including negative controls.

The complement is **context hygiene**: GBrain's `context-audit` skill audits the always-loaded stack (CLAUDE.md / AGENTS.md / MEMORY.md / rendered identity files) for redundancy, contradictions, stale content and skill-extraction candidates, ranks findings by token savings with a risk class, computes drift against the previous audit, and is **strictly report-only — it never edits an audited file**, including zero-risk findings. That separation (auditor, not surgeon) is the same discipline as the contradiction probe.

**Recommended policy.** Every skill ships with a benchmark and a *disjoint* held-out set. No skill edit merges without beating baseline on both. Version and snapshot every accepted edit with an append-only history. Re-run the whole skill benchmark suite on every model upgrade — model change is the largest silent source of skill drift. Audit the always-loaded context monthly, report-only, and apply deliberately.

---

## Relevance to company-brain / RAG / fruit-fly question

**Is it RAG?** On hygiene the answer is a clear *no, and here is the measurable reason*: every mechanism above operates on a data model RAG does not have. Chunk-and-embed has no `valid_until`, no supersession key, no authority tier, no per-fact confidence, no forget that survives a reindex. The AUROC 0.59 result ([arXiv:2606.26511](https://arxiv.org/abs/2606.26511)) is the sharpest available rebuttal to "this is just RAG": similarity search *cannot in principle* tell a superseded fact from a paraphrase, so no amount of retrieval quality fixes staleness. Tan's "retrieval is easy; being worth retrieving from is the product" is, in this dimension, literally true and quantified. Conversely, hygiene is *not* free of RAG: the contradiction probe, the citation checker and the credibility model are all retrieval-plus-judge pipelines.

**Fruit-fly link (my dimension's angle only; defer to the connectome dimension).** The hygiene-relevant fly result is the mushroom-body algorithm of sparse random projection ("FlyHash") for similarity search and novelty detection ([Dasgupta, Stevens & Navlakha, *Science* 2017, DOI 10.1126/science.aam9868](https://doi.org/10.1126/science.aam9868) — DOI resolves; content not fetched, paywalled). Its hygiene relevance is at **write time**, not read time: a cheap novelty detector is exactly the "importance filter" that Hindsight calls the cheapest place to control memory quality, and it is the missing gate in front of a 155K-page auto-ingesting brain. The second fly-biology hook — dopaminergic *active* forgetting as a distinct circuit rather than passive decay — maps onto FSFM's "active deletion" and "safety-triggered removal" categories. Both are analogies, not results; I did not verify current fly-forgetting literature (search budget exhausted), so treat as **low confidence** and hand to the fruit-fly dimension.

**Skeptical note on the talk's numbers.** GBrain's page count is quoted three different ways in three places within five months: **~220,000** in the talk (2026-07-16), **155,795** in the current README, and a "96K-page brain" in the calibration spec. The [calibration quality-gate spec](https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md) also reports that on that production brain, only **34 of 500** candidate takes (6.8%) were falsifiable and **17 of those 34** were ungradeable — i.e. **~3.4%** of extracted claims were actually checkable. That is the most honest number in the whole corpus about what an auto-written brain contains, and it is Tan's own repo publishing it.

## Open questions

1. Does anyone measure *hygiene* directly? CARS is the only composite metric found, and no memory system reports it. LongMemEval's knowledge-update slice (78 of 500 questions) is the closest widely-used proxy.
2. What is the real cost of a contradiction probe at company scale? GBrain's is sampled with a Wilson CI *because* exhaustive pairwise judging is unaffordable — but nobody publishes the cost curve.
3. Does eval-gated skill optimisation survive model upgrades, or does each frontier release silently invalidate every accepted skill edit?
4. The agent-written-brain feedback loop: at 155K pages "mostly agent-written", what fraction of facts are sourced to *another agent's synthesis* rather than a primary source? No system I found tracks derivation depth, though PROV's `derive` relation would express it.
5. Is there any deployed enforcement (not observation) of prompt-injection defence in an ingest-everything company brain? GBrain explicitly ships none.

## Sources

- Transcript: `/Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt` (lines 393–405)
- Knowledge Conflicts for LLMs: A Survey — https://aclanthology.org/2024.emnlp-main.486/
- Astute RAG (ACL 2025) — https://arxiv.org/abs/2410.07176
- ConflictRAG (2026) — https://arxiv.org/html/2605.17301v1
- MemStrata / Temporal Validity in Retrieval Memory — https://arxiv.org/abs/2606.26511
- Supersede: the memory-update gap — https://arxiv.org/abs/2606.27472
- Zep: temporal knowledge graph for agent memory — https://arxiv.org/abs/2501.13956 · https://www.getzep.com/ai-agents/temporal-knowledge-graph/
- LongMemEval — https://arxiv.org/pdf/2410.10813
- Eywa: provenance-grounded long-term memory — https://arxiv.org/pdf/2605.30771
- Correctness is not Faithfulness in RAG Attributions — https://arxiv.org/abs/2412.18004
- W3C PROV-DM — https://www.w3.org/TR/prov-dm/
- PROV-AGENT (eScience 2025) — https://arxiv.org/html/2508.02866
- From Agent Traces to Trust (2026) — https://arxiv.org/html/2606.04990v1
- FSFM selective forgetting — https://arxiv.org/abs/2604.20300
- When to Forget: a memory governance primitive — https://arxiv.org/abs/2604.12007
- Always-On Agents survey — https://arxiv.org/pdf/2606.30306
- MINJA memory injection — https://arxiv.org/abs/2503.03704
- Memory Poisoning Attack and Defense — https://arxiv.org/abs/2601.05504
- SMSR certified defence — https://arxiv.org/pdf/2606.12703
- OWASP agentic threats & mitigations — https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- mem0 AI memory security best practices (2026-02-11) — https://mem0.ai/blog/ai-memory-security-best-practices
- mem0 State of AI Agent Memory 2026 — https://mem0.ai/blog/state-of-ai-agent-memory-2026
- Hindsight, The Consolidation Problem in Agent Memory (2026-05-21) — https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation
- SkillOpt (MSR) — https://arxiv.org/abs/2605.23904
- OpenAI, Testing Agent Skills Systematically with Evals — https://developers.openai.com/blog/eval-skills
- Future AGI, Agent Skill Regression Testing — https://futureagi.com/blog/agent-skill-regression-testing/
- GBrain repo (MIT, created 2026-04-05, 29,764 stars on 2026-09-10) — https://github.com/garrytan/gbrain
  - contradictions probe — https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md
  - temporal contradiction RFC — https://github.com/garrytan/gbrain/blob/master/docs/proposals/temporal-contradiction-probe.md
  - source attribution — https://github.com/garrytan/gbrain/blob/master/docs/guides/source-attribution.md
  - compiled truth + timeline — https://github.com/garrytan/gbrain/blob/master/docs/guides/compiled-truth.md
  - guardrail seams — https://github.com/garrytan/gbrain/blob/master/docs/guardrails.md
  - operational disciplines / dream cycle — https://github.com/garrytan/gbrain/blob/master/docs/guides/operational-disciplines.md
  - skillopt — https://github.com/garrytan/gbrain/blob/master/docs/guides/skillopt.md
  - brain currency incident — https://github.com/garrytan/gbrain/blob/master/docs/designs/BRAIN_CURRENCY.md
  - calibration quality gate — https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md
  - decay / forget / ttl source — https://github.com/garrytan/gbrain/blob/master/src/core/facts/decay.ts · `forget.ts` · `ttl-parse.ts`
  - context-audit & citation-fixer skills — https://github.com/garrytan/gbrain/blob/master/skills/context-audit/SKILL.md · https://github.com/garrytan/gbrain/blob/master/skills/citation-fixer/SKILL.md
- gbrain-evals (LongMemEval 2026-09-06: 449/470 retrieval, 433/500 answers) — https://github.com/garrytan/gbrain-evals
- FlyHash / fly olfactory similarity search — https://doi.org/10.1126/science.aam9868 (DOI resolves; paywalled, not fetched)

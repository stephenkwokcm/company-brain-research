# d3-router — a measured skill dispatcher for GBrain, and the honest death of the "fly router"

**Key:** `d3-router` · design panel, angle 3 (ROUTING) · 2026-09-10 · author: research worker (Claude Opus 5)
**Assigned angle:** *sparse-expansion / connectome-style stochastic router (FlyPrompt lineage) as the RESOLVER / skill-dispatch layer, targeting the skill-routing precision collapse at pools of 50–150 skills.*
**Repo state examined:** `garrytan/gbrain` at commit `43597b19`, `v0.48.5.0`, pushed 2026-09-08 (local clone).
**Reproduction artifacts:** `/Users/stephen/Cookies/company-brain-research/artifacts/d3-router/` (scripts + raw results; commands in §5.4).

---

## 0. Verdict, up front

I ran the fly-router idea before proposing it, and **it lost.** On GBrain's own 73 skills and its own 271 positive routing fixtures, a random-expansion analytic router (FlyPrompt's REAR operator: dense Gaussian projection + ReLU + closed-form ridge) and a true FlyHash k-WTA sparse-expansion router are both **worse than a no-training nearest-centroid retriever** at every pool size in the honest (trigger-blind) condition — REAR −1.1 pp, FlyHash −1.4 to −5.9 pp at pool 73, with oracle regularisation chosen generously in the expansion arms' favour. Checkpoint 01's decision (iii), *"routing: sparse-expansion router for the RESOLVER/skill layer (FlyPrompt),"* should be **retired**, on top of the attribution correction g07 already forced (REAR is not sparse, has no winner-take-all, and is not FlyHash).

What survives is worth building anyway, and the assigned angle is what surfaced it. Three things came out of the measurement that no report in this corpus has:

1. **GBrain's shipped routing layer is a substring matcher with no semantic fallback, and its 100 %-passing benchmark is a tautology check.** `gbrain routing-eval` scores **303/303 = 100.0 %** on the bundled fixtures. Remove *only* the trigger phrases each intent literally contains and it scores **0/271 = 0.0 %**, with 24 intents then misrouting to a *different* skill. The declared second layer that would generalise (`Layer B (LLM tie-break)`) is documented, flagged in the CLI, and **not implemented**.
2. **Skills are never embedded anywhere in GBrain.** There is no vector representation of a skill in the schema, in `src/core/embed*`, or in the search stack. Routing is lexical-or-model, never dense. That is the insertion point.
3. **The context bill for skill dispatch is a first-order cost line nobody in this corpus has costed.** GBrain's own scaling guide reports ~25,000 tokens/turn of skill descriptions on a 306-skill agent. At 25 people and 40 agent turns/person/day that is **$1,077/month uncached, $108/month cached** at Sonnet-5 input rates — versus g02's ~$225/month all-in for the entire brain.

**The proposal (§3–§4):** ship the unimplemented Layer B as a **two-stage dispatcher** — stage 1 is a boring, published, dense nearest-prototype retriever over skill descriptions (RAG-MCP, arXiv:2505.03275), stage 2 is the *one* fly mechanism that is not duplicated by an incumbent and that my pilot did **not** refute: a **fly Bloom filter novelty gate** (Dasgupta et al., *PNAS* 2018 — the only Deep-fidelity mechanism in g07's inventory) used for **abstention and routing-drift detection**, not for classification. Stage 3 escalates only the low-margin turns to an LLM. The fly contribution is scoped to the gate, is separately kill-criterioned, and my prior that it beats a plain max-cosine threshold is ~30 % — deliberately the same number v10b gave the write-side gate, because it is the same operator in a different socket.

---

## 1. The problem, measured

Everything in this section is a measurement I made against the clone today, not a quote. Commands in §5.4.

### 1.1 What GBrain ships

| Quantity | Measured | Where |
|---|---|---|
| Canonical skills (`skills/<slug>/SKILL.md`) | **73** (76 dirs; 223 `SKILL.md` repo-wide, the rest in `plugin/`, `plugin-variants/`, `test/`, `recipes/`) | `find skills -name SKILL.md` |
| Frontmatter `triggers:` entries | **535** | YAML parse of the 73 files |
| Merged trigger index (frontmatter ∪ RESOLVER.md rows) | **623** entries (538 frontmatter + 85 `resolver_md`) → **840** normalised phrases over 73 skills | `loadSkillTriggerIndex()` |
| `skills/RESOLVER.md` | 16,290 bytes / 172 lines | `wc` |
| Skill `name + description` frontmatter, all 73 | **26,440 chars** ≈ 6,610 tokens (362 chars ≈ 90 tokens per skill) | YAML parse |
| Routing fixtures | **303** in 44 `routing-eval.jsonl` files — **271 positive** over 55 distinct skills, **32 negative** (`expected_skill: null`) | `loadRoutingFixtures()` |
| Skill embeddings anywhere in the repo | **0** | grep of `src/core/embed*`, `src/core/search/*`, `src/schema.sql` |

Note the 26,440-char measurement lands almost exactly on the Agent Skills spec's "~100 tokens metadata always loaded" and on GBrain's own "~80 tokens per skill" figure — three independent numbers agreeing, which is why the cost arithmetic in §7 is trustworthy.

### 1.2 How routing actually works today — two mechanisms, one of them unimplemented

**In production**, the harness loads every skill's ~90-token metadata plus (on OpenClaw) `RESOLVER.md`, and the *model* picks. GBrain's `docs/guides/scaling-skills.md` states the failure mode in its own words:

> "When an agent grows past 100 skills, a wall starts forming… This is great architecture at 50 skills. At 100, it's fine. At 200, it starts to drag. At 300, the system prompt eats more than 25,000 tokens on skill descriptions alone… **Skill routing gets fuzzier. With 300 descriptions competing for attention, the model occasionally picks the wrong one.**"

Its remedy is **manual three-tier gating** on a 306-skill production agent: Tier A ~35 skills always in the prompt, Tier B ~85 resolver-routed, Tier C ~180 `enabled: false`. Reported effect: ~25,000 → ~4,000 skill-description tokens/turn, "~21,000 tokens freed per turn," "capability loss zero." The tier assignment is a human judgement call ("Walk through every skill. Ask: does this need to fire on every turn?"), the routing-accuracy row of its own before/after table reads **"degrading"** with no number, and the first `gbrain doctor` run after tiering found **63 skills with no routing path at all**.

**In CI**, `src/core/routing-eval.ts` implements *Layer A (structural)*: lowercase, strip every non-`\p{L}\p{M}\p{N}` char, collapse whitespace, then ask whether any of a skill's trigger phrases is a **substring** of the intent. A fixture passes iff the expected skill matches and no unlisted other skill does. The file's own header declares the second layer and its absence:

> *"Layer B (LLM tie-break, optional): only runs via `gbrain routing-eval --llm`. **Not yet implemented in this release**; the CLI accepts the flag (emits a stderr notice and runs Layer A only) so call sites are ready."*

So the routing layer of the most-worked public company brain is: a hand-maintained list of 840 substrings, a hand-assigned three-tier visibility gate, and a documented hole where generalisation goes.

### 1.3 Measurement 1 — the benchmark is saturated, and it is a tautology check

Running the repo's own code on the repo's own fixtures:

```
entries 623 · skillsWithTriggers 73 · fixtures 303
totalCases 303 · passed 303 · missed 0 · ambiguous 0 · falsePositives 0 · top1 = 1.000
```

**303/303 = 100.0 %.** Zero headroom, zero discriminative power. This is not an accident of quality: Layer A passes iff the intent literally contains a trigger, and the fixture linter (`lintRoutingFixtures`) rejects only *verbatim identity* between intent and trigger — near-copies are explicitly allowed ("a fixture that embeds trigger words in surrounding context is valid and useful"). Across the 271 positive fixtures the literally-matched phrase has **median length 19 characters** and covers a **median 29 % of the intent's words**.

**Leave-one-trigger-out (LOTO).** For each fixture, delete *only* the trigger phrases that intent literally contains, then re-route:

| | passed | missed | ambiguous | top-1 |
|---|---|---|---|---|
| Shipped index | 271 | 0 | 0 | **100.0 %** |
| LOTO | **0** | 271 | 0 | **0.0 %** |

Zero. And 24 of the 271 do not merely fail — they match a *different* skill, i.e. they silently misroute. This is by construction (a substring matcher cannot generalise), but the consequence is the point: **the 100 % number carries no information about routing under paraphrase**, which is the only condition that occurs in production. This is the same disease g06 identified in `gbrain-evals` issue #24 — a parser evaluated on wording it was built to recognise — reproduced in a second subsystem.

### 1.4 Measurement 2 — GBrain's one real routing A/B inverts under exact-slug scoring

`evals/functional-area-resolver/` is a properly built A/B (3 Anthropic models × 3 resolver variants × 20 training + 5 held-out fixtures × 3 seeds, with committed receipts binding each run to `prompt_template_hash` / `fixtures_hash` / `harness_sha`). Its README, and `findings/context-engineering-skills.md` after it, report the **LENIENT** table: compressing 270 bullet rows (25 KB) into 13 dispatcher rows (13 KB) lifts routing 81.7→98.3 (Opus 4.7), 86.7→100 (Sonnet 4.6), 73.3→88.3 (Haiku 4.5).

I recomputed both scores from the committed receipts. **On STRICT (exact slug), the compression is worse than the baseline on every model:**

| Variant (training, n=60 per cell) | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 | Size |
|---|---|---|---|---|
| baseline (270 bullet rows) | **81.7 %** | **86.7 %** | **73.3 %** | 25 KB |
| functional-areas (dispatchers) | 63.3 % | 60.0 % | 53.3 % | 13 KB |
| resolver-of-resolvers (no dispatcher clause) | 66.7 % | 41.7 % | 65.0 % | 10 KB |

The asymmetry is structural, and the README discloses it: LENIENT gives partial credit for "landed in the right dispatcher area," and *"for variants without dispatcher clauses (baseline, resolver-of-resolvers), LENIENT collapses to STRICT."* So the headline compares an arm that can earn partial credit against arms that cannot. For an *agent* that can then read the sub-skill, LENIENT is arguably the right metric and the claim stands. **For a router that must emit one slug, STRICT is the metric, and compression costs 18–27 pp of it.** Anyone building a deterministic dispatcher on the functional-area pattern is building on the LENIENT number.

Two further caveats that matter for how much weight this eval can carry: n = 20 training / 5 held-out fixtures, held-out saturated at 100 % for five of nine cells; and the variants are frozen extracts of a *personal* `AGENTS.md`, not of `skills/RESOLVER.md`. The 2026-08-12 "post-import-wave" re-run has identical `fixtures_hash` and `prompt_template_hash` and static variant files, so it measures model/API drift (Haiku STRICT baseline 73.3 → 78.3), **not** the grown skill pool. There is still no measurement anywhere of routing accuracy as the pool grows.

*Provenance footnote, and a small correction to the README.* Recomputing per-seed means from the receipts reproduces the README's LENIENT table exactly in seven of nine training cells, and disagrees in two — both on Opus 4.7: `functional-areas` is **100.0 %** in the receipt (three seeds at 100.0) where the README prints 98.3 % ± 7.2 %, and `resolver-of-resolvers` is **66.7 %** (65.0 / 65.0 / 70.0) where the README prints 63.3 % ± 14.3 %. The likely cause is visible in the receipts themselves: the Opus run carries `harness_sha: ca99fbfe…` while the Haiku and Sonnet runs carry `fcc39528…`, so the published Opus row appears to come from an earlier harness than the committed receipt. This is minor, it moves nothing in either direction, and it is worth recording precisely because it is the receipt mechanism working as designed — the hash is what makes the discrepancy findable at all.

### 1.5 Measurement 3 — the pool-size curve, on GBrain's own skills

**This is the pilot that killed the assigned angle.** Backbone: TF-IDF (word 1–2 grams) over each skill's `name + description + SKILL.md` body prefix, reduced to a 256-d LSA representation, L2-normalised — a stand-in for a real sentence embedder (see caveats). Classes: all 73 skills. Test set: the 271 positive fixtures. Pool size *K* = expected skill + *K*−1 random distractors, 5 seeds. Ridge regularisation swept over {1e-4 … 1e2} with the **best λ chosen on the test set** — an oracle, deliberately generous to the expansion arms.

Two conditions. **T** = class documents include the trigger phrases (leaky: the fixtures were written against those triggers). **B** = **trigger-blind**, class documents are description + body only. B is the honest condition and the one to read.

**Condition B — trigger-blind top-1 accuracy**

| Arm | K=5 | K=10 | K=25 | K=50 | K=73 |
|---|---|---|---|---|---|
| **tf-idf nearest centroid (no training)** | **0.931** | **0.883** | **0.812** | **0.770** | **0.734** |
| LSA-256 nearest centroid | 0.917 | 0.877 | 0.811 | 0.765 | 0.727 |
| LSA-256 + ridge | 0.914 | 0.875 | 0.808 | 0.760 | 0.723 |
| REAR (dense Gaussian + ReLU, M=2,560) | 0.891 | 0.858 | 0.800 | 0.757 | 0.723 |
| REAR (dense Gaussian + ReLU, M=10,000) | 0.898 | 0.868 | 0.804 | 0.762 | 0.731 |
| FlyHash k-WTA, m=10d, ρ=5 % | 0.879 | 0.835 | 0.768 | 0.725 | 0.675 |
| FlyHash k-WTA, m=40d, ρ=5 % | 0.903 | 0.851 | 0.790 | 0.748 | 0.708 |
| FlyHash k-WTA, m=40d, ρ=10 % | 0.917 | 0.875 | 0.807 | 0.759 | 0.720 |
| FlyHash k-WTA, m=40d, ρ=2 % | 0.908 | 0.872 | 0.799 | 0.742 | 0.697 |
| *substring Layer A (shipped)* | *0* | *0* | *0* | *0* | *0* |

(In the leaky condition T every arm sits in 0.856–0.893 at K=73; REAR-M2560 nominally leads at 0.893 vs 0.882 for the centroid — 1.1 pp on n=271, where the binomial SE is 2.7 pp. It is noise, in the condition that flatters it.)

Three readings:

- **Random expansion buys nothing here.** REAR — FlyPrompt's actual operator, and RanPAC's before it — never beats a centroid with no training at all in condition B, at any pool size. FlyPrompt's own ablation already said the gain comes from expert modularity, not expansion (RanPAC 79.92 vs FlyPrompt 86.76 A_last on CIFAR-100); this pilot says that on skill routing even the modest expansion credit disappears.
- **Sparse k-WTA is strictly worse.** Every FlyHash configuration loses to the dense baseline; the fly's own regime (m = 40d, ρ = 5 %) is 2.6 pp down at K=73 and 2.8 pp down at K=5. This is the third independent socket in which the fly hash has now lost — index (v10a/v10b), dedup (v10b), routing (here).
- **The collapse the angle was aimed at is real and quantified.** Trigger-blind top-1 falls **0.931 → 0.734** from K=5 to K=73. A log-linear fit (acc ≈ 1.049 − 0.0727·ln K, R² not reported — five points) extrapolates to **0.685 at 150 skills** and **0.634 at 300**. That agrees in shape and band with RAG-MCP's independently measured stress test: ">90 % below 30 [tools]… positions 31–70, clusters of purple emerge… beyond position ~100, purple dominates."

**Caveats, stated plainly.** (i) LSA-256 over a ~950-document corpus is a weak backbone; a real sentence embedder would raise every dense arm and could in principle change their ordering — this is a pilot, not the experiment. (ii) Expansion methods are known to help most when a frozen backbone's features are *not* already a low-rank decorrelated basis, which is exactly what LSA produces, so this is a setting somewhat unfavourable to REAR; that is why K1 in §8 keeps the arm alive for one confirmatory run on a real embedder before the recommendation is final. (iii) n=271 over 55 skills; 18 of 73 skills have no fixture. (iv) The distractor pools are random, so semantically adjacent skills are under-represented relative to a real 150-skill catalogue — which makes these numbers *optimistic*.

### 1.6 Measurement 4 — what an LLM router costs, from receipts

From the same committed receipts (mean over 75 calls per cell):

| Resolver in prompt | mean input tok | mean output tok | median latency |
|---|---|---|---|
| 25 KB baseline | 7,634 | 6 | 718 ms (Haiku) · 1,296 ms (Sonnet) · 1,722 ms (Opus, 10,946 in-tok) |
| 13 KB functional-areas | 4,089 | 6 | 634 ms (Haiku) |

**Four thousand to eleven thousand input tokens and 0.6–1.7 seconds to produce a six-token slug.** That is the thing a vector router replaces, and it is the number to quote whenever someone says routing is free.

---

## 2. The mechanism borrowed, and its fidelity

Two mechanisms, two very different honesty labels. Both use g07's rubric.

### 2.1 Stage 1 — nearest-prototype retrieval. **Fidelity: none. Not biological, and I am not claiming it is.**

The assigned angle's mechanism was FlyPrompt's REAR (Yan et al., ICLR 2026, arXiv:2602.01976 — v1 2 Feb 2026, v3 24 Mar 2026). g07 established, and the paper's own text confirms, that REAR is `φ(x) = ReLU(hR)` with `R_ij ~ N(0,1)`, M = 10,000, and a ridge-regression router solved in closed form — **a dense Gaussian random projection with no sparse binary matrix, no winner-take-all, no fan-in constraint and no enforced activity level.** The fly appears in the abstract ("Inspired by the fruit fly's hierarchical memory system characterized by sparse expansion and modular ensembles") and constrains nothing in the model. Its non-biological ancestor is **RanPAC** (arXiv:2307.02251, NeurIPS 2023): *"a frozen Random Projection layer with nonlinear activation between the pre-trained model's feature representations and output head, which captures interactions between features with expanded dimensionality."* Same operator, two and a half years earlier, no fly.

My pilot then removed even the engineering case in this socket. So stage 1 is the plain thing that won: **cosine similarity between the turn's embedding and a per-skill prototype vector.** This is RAG-MCP (Gan & Sun, arXiv:2505.03275, 6 May 2025) applied to skills instead of MCP servers. I recommend it on its measurements and on its simplicity, and I explicitly do not attach a fly label to it.

### 2.2 Stage 2 — the fly Bloom filter as an abstention gate. **Fidelity: Deep (mechanism), untested (transplant).**

The one mechanism in g07's inventory rated **Deep** and buildable exactly as published is the fly Bloom filter — Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093–13098 (2018), Eq. 2. Its properties are unusual and they are the ones a router's abstention decision actually needs:

- It reads **novelty before writing**, returning a graded familiarity score rather than a boolean.
- Its state is **O(m) floats independent of the number of items inserted** — no growth, no rebuild.
- **Additive-increase / multiplicative-decay** gives time-decay and eviction for free; the paper explicitly motivates this for *"life-long learning applications, where the database is not of fixed size but continuously grows"* — which is the exact shape of a skill catalogue that gains members weekly.

Why the gate and not the classifier: the fly's mushroom body is a **valence tagger on a sparse code**, not a document store or a ranker (g07's "what has no counterpart" section is blunt about this — provenance, skillification and relevance-to-a-query have no fly counterpart at all). Deciding *"nothing here applies"* and *"this turn looks unlike anything this skill has seen"* is precisely a familiarity judgement on a sparse code, and it is the one output no incumbent router produces: RAG-MCP has no abstention, the functional-area eval has no abstention stratum, and GBrain's 32 negative fixtures are the only place in the whole stack where "route to nothing" is tested at all.

Honest scoping: this is a **transplant with no precedent**. The filter has never been run on text or embeddings, δ and ε are free parameters with no data-derived values (only the AIMD shape is evidenced), and the largest n ever tested in the paper is 5,000. That is why it gets its own kill criterion (§8, K2) and a stated prior of ~30 %.

### 2.3 What I explicitly do **not** propose, and why

| Idea | Why not |
|---|---|
| FlyHash / k-WTA codes as the routing representation | Lost to a no-training centroid at every pool size in §1.5, in both conditions. Third socket lost after index (v10a: 0.1325 vs 0.3431 MAP on CSFCube) and dedup (v10b: SimHash beats it on both quality and time). |
| REAR / RanPAC expansion in front of the router | Same pilot. Also: FlyPrompt's own ablation attributes its gain to expert modularity, not expansion. |
| Connectome-derived stochastic wiring as a routing prior | Dhiman, arXiv:2604.04033 (2026-04-05) re-ran flyvis (45,669 nodes / 1,513,231 edges) against a **degree-preserving** null and the topology advantage vanished. There is no evidence that a connectome's wiring statistics beat a random or a learned one for a non-visual task. |
| BioHash (Ryali et al., ICML 2020, arXiv:2001.04907) | The learned sparse-expansion successor to FlyHash, and the only version with a credible quality story. But it **learns the projection**, which destroys the property that makes a router viable here — adding a skill must not retrain anything. Worth naming; not worth building. |

---

## 3. Exact insertion point in GBrain

Every path below exists in the clone at `v0.48.5.0`.

### 3.1 Code

| Seam | File | Change |
|---|---|---|
| **The declared hole** | `src/core/routing-eval.ts` L15–20, `RunRoutingEvalOptions.llm` (L~330) | Implement Layer B. Today `--llm` "emits a stderr notice and runs Layer A only". Becomes: Layer A first (exact substring is a legitimate fast path and should keep priority); on miss **or** on ambiguity, call the vector router. |
| **Shared index** | `src/core/skill-trigger-index.ts` → `loadSkillTriggerIndex()` | Already folds frontmatter ∪ RESOLVER.md into one `SkillTriggerEntry[]` and is the single primitive three consumers share (the file's header documents the v0.41.x per-consumer-drift bug class this fixed). Prototype construction hangs off exactly this function, so the router cannot drift from `doctor` or the CLI. |
| **New module** | `src/core/skill-router.ts` (new, ~250 LOC) | `buildPrototypes()`, `routeTurn()`, `noveltyScore()`. Pure functions over an engine handle; no new dependency. |
| **CLI** | `src/cli.ts` L2323 (`routing-eval`), plus a new `skills route "<intent>"` under the existing `CLI_ONLY` set | `gbrain routing-eval --llm` finally does something; `gbrain skills route` is the debugging surface. |
| **Doctor** | new `src/commands/doctor/checks/skill-routing-health.ts` | The existing `routing-federation.ts` check is about multi-*source* routing, not skills; `check-resolvable.ts` (725 LOC) checks **reachability**, never accuracy. This check reports top-1 on the live fixture set, prototype staleness, and the abstention rate on the last 7 days of real traffic. |
| **Cycle** | `src/core/cycle.ts` `ALL_PHASES` — insert `route_prototypes` immediately after `embed`, before `orphans` | Prototypes are derived from embeddings, so they must follow `embed`; they are a maintenance artefact, so they belong in `MAINTENANCE_PHASES`. Recomputation is a rank-1 update per new/edited skill, not a retrain. |
| **MCP** | `src/core/…` surface registry — add `route` to the `starter` surface only, never to `verbs` | `MEMORY_VERBS v1` is a **frozen** protocol (`protocol_version: 1`, additive-forever). Adding a verb would break conformance. Routing is a `starter`-surface operation. |

### 3.2 Schema

Two tables, both derived and rebuildable — consistent with `docs/architecture/system-of-record.md` ("the Postgres/PGLite database is a derived cache… we rebuild it from the repo"). Nothing here becomes a system of record; the `SKILL.md` files stay authoritative.

```sql
-- derived; rebuilt by `gbrain sync && gbrain extract all`
CREATE TABLE skill_prototypes (
  source_id       TEXT NOT NULL REFERENCES sources(id),
  slug            TEXT NOT NULL,
  kind            TEXT NOT NULL CHECK (kind IN ('description','trigger','fixture','observed')),
  embedding       vector(1024) NOT NULL,          -- matches embedding_dimensions
  weight          REAL NOT NULL DEFAULT 1.0 CHECK (weight BETWEEN 0 AND 1),
  n_support       INTEGER NOT NULL DEFAULT 1,
  content_sha     TEXT NOT NULL,                  -- binds the vector to the SKILL.md that produced it
  built_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_id, slug, kind, content_sha)
);
CREATE INDEX ON skill_prototypes USING hnsw (embedding vector_cosine_ops);

-- the fly gate's state: O(m) floats per skill, independent of turns seen
CREATE TABLE skill_novelty_filter (
  source_id  TEXT NOT NULL REFERENCES sources(id),
  slug       TEXT NOT NULL,
  weights    REAL[] NOT NULL,                     -- length m, AIMD-updated
  seed       BIGINT NOT NULL,                     -- the projection seed IS part of the index
  m          INTEGER NOT NULL,
  rho        INTEGER NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_id, slug)
);
```

`content_sha` is the detail that matters operationally: it is the same trick `skillopt` uses for eval receipts (`<slug>-<sha8>.json`), and it makes a stale prototype a detectable condition rather than a silent wrong answer.

### 3.3 Config keys (following the repo's `search.*` dotted style)

```
skills.router.enabled              bool    default false   # ships dark
skills.router.top_k                int     default 3
skills.router.margin_threshold     float   default 0.06    # margin below which stage 3 escalates
skills.router.abstain_threshold    float   default 0.28    # max-cosine below which we route to nothing
skills.router.novelty_gate         enum    off|shadow|on   default shadow
skills.router.escalation_model     string  default claude-haiku-4-5
skills.router.log_decisions        bool    default true
```

`novelty_gate: shadow` is the honest default for an unproven mechanism: the fly filter computes and logs its verdict but does not change behaviour, so the K2 comparison (§8) accumulates on real traffic at zero risk.

### 3.4 Where routing decisions are written back

Every decision becomes a row in GBrain's existing hot layer rather than a new bespoke log: `facts` with `kind: 'event'`, `source` = the required provenance string (`remember` errors `provenance_required` on empty), carrying `{slug, margin, novelty, abstained, escalated, corrected_to}`. It then inherits the shipped machinery for free — the 7-day `event` half-life in `src/core/facts/decay.ts`, the one-way `facts → [dream consolidate] → takes` bridge, and the audit trail (`consolidated_at`/`consolidated_into`). The nightly `route_prototypes` phase consolidates corrected routes into `kind='observed'` prototypes and proposes `routing-eval.jsonl` lines for the skill that got it wrong.

That is the piece that makes this a *company-brain* feature rather than a retrieval trick: it converts Tan's "trigger evals are performance reviews" from a hand-written fixture file into a measured loop over real traffic — and it supplies the non-saturated benchmark §1.3 showed the project does not have.

---

## 4. Algorithm sketch, with parameters

```
BUILD (nightly, phase `route_prototypes`, after `embed`)
  for each skill s in loadSkillTriggerIndex():
    docs(s) = [ name + description ]                        # kind='description', weight 1.0
            ∪ [ each trigger phrase ]                       # kind='trigger',     weight 0.6
            ∪ [ each routing-eval.jsonl positive intent ]   # kind='fixture',     weight 0.8
            ∪ [ last N corrected turns routed to s ]        # kind='observed',    weight 0.4, N=32
    embed each doc with the brain's configured embedder (1024-d default)
    store rows in skill_prototypes, stamped with content_sha(SKILL.md)
  # cost: 73–150 skills x ~12 docs = ~900–1,800 embeddings, once, then only on change

ROUTE (per turn, ~1 ms after the embedding you already have)
  1. LAYER A (unchanged, keeps priority): normalised substring match.
     exactly one specific skill matches  -> return it.            # fast, exact, free
  2. STAGE 1 — candidates:
     q = embedding of the turn (REUSE the vector `gbrain search` already computes)
     score(s) = max over prototypes p of s of  weight(p) * cos(q, p)
     C = top_k skills by score                                   # top_k = 3
     margin = score(C[0]) - score(C[1])
  3. STAGE 2 — the gate:
     h = k-WTA( M · (q - mean(q)) )   ∈ {0,1}^m                  # m = 40d = 40,960, ρ = 5% -> 2,048 ones
     novelty(s) = ( Σ_{i ∈ h} w_s[i] ) / ρ                        # PNAS 2018 Eq. 2, per-skill filter
     if score(C[0]) < abstain_threshold  OR  novelty(C[0]) > novelty_cap:
         return ABSTAIN                                          # "no skill applies" — the output nobody produces
  4. STAGE 3 — escalate only when uncertain:
     if margin < margin_threshold:
         ask escalation_model to choose among the top_k DESCRIPTIONS ONLY  (~500 tokens)
     else: return C[0]
  5. UPDATE (write path, after the turn resolves):
     w_s ← (1-ε)·w_s  for all i          # multiplicative decay
     w_s[i] ← w_s[i] + δ  for i ∈ h      # additive increase on the chosen skill
     write a `facts` row with kind='event'
```

**Parameters and where they come from.** `d` = 1024 (GBrain's `embedding_dimensions` default). `m = 40d = 40,960`, `ρ/m = 5 %` → 2,048 winners — Dasgupta's own fly regime (~50 PN → ~2,000 KC, 40× expansion, ~5 % activity via APL feedback). Fan-in `s = 0.10·d ≈ 102` ones per row (Ryali et al.'s PN→KC sampling rate 0.1). `δ`, `ε` have **no data-derived values in the literature** and must be calibrated on the abstention stratum — this is the single biggest parameter risk and it is why the gate ships in `shadow`. **The projection seed is part of the index**: persist it or every code ever written becomes garbage.

**Two things the sketch deliberately does not do.** It does not put the sparse code anywhere near the ranking decision (that is what lost in §1.5). And it does not store the fly filter in `pgvector`: at ρ = 2,048 non-zeros a `sparsevec` exceeds pgvector's 1,000-non-zero HNSW limit (v10b's finding), so the filter is a plain `REAL[]` read by slug — which is correct anyway, because it is never searched, only evaluated.

---

## 5. Benchmark, metric, baseline

### 5.1 The benchmark does not exist yet and must be built: **RouteBench-150**

§1.3 established the shipped fixtures are saturated. The replacement, in four strata:

| Stratum | n (target) | Construction | Why |
|---|---|---|---|
| **P — trigger-blind paraphrase** | 600 | A model that is shown **only the SKILL.md body with frontmatter stripped** writes 4 realistic user utterances per skill. The generator never sees the `triggers:` array. | The one measurement that would settle whether any of this generalises. This is g06's template-blind protocol (proposed for `gbrain-evals` #24 in April 2026, never run) applied to routing. |
| **N — near-miss negatives** | 150 | Anthropic `skill-creator`'s explicit rule: *"don't make should-not-trigger queries obviously irrelevant."* Seeded from the 32 shipped negatives. | Abstention has no benchmark anywhere. Without it every confabulating router scores well. |
| **A — declared ambiguity** | 120 | Intents that legitimately fit ≥2 skills; label = the allowed set, reusing `ambiguous_with`. | Ambiguity is where a 150-skill catalogue actually breaks. |
| **D — distractor scaling** | — | Pool sizes 25 / 50 / 75 / 100 / 150, distractors drawn to include the **nearest** skills by description similarity, not uniformly. | §1.5 used random distractors, which is optimistic. |

To reach 150 skills honestly, extend GBrain's 73 with public Agent Skills (the format is an open standard since 2025-12-18; arXiv:2602.08004 surveyed 40,285 public skills and found "widespread intent-level redundancy," which is the realistic condition, not a clean catalogue).

**Pre-registration is mandatory.** Commit strata definitions, generator prompts, the tuning grid and the decision rules, and record the commit hash in every receipt — the same discipline `evals/functional-area-resolver/` already uses (`prompt_template_hash`, `fixtures_hash`, `harness_sha`), and the discipline g06 says this corpus most needs.

### 5.2 Metrics

**Primary:** top-1 exact-slug accuracy on stratum P at pool 150 (**STRICT**, never LENIENT — §1.4).
**Co-primary:** abstention F1 on N ∪ P (does it say "nothing" exactly when it should?).
**Secondary, reported in the same table, no exceptions:** always-on context tokens/turn; added p50/p99 latency; escalation rate; ambiguity-set hit rate on A; cost/1,000 turns.

Reporting retrieval-shaped wins without the token and latency columns is how this subject goes wrong: a router that adds 700 ms to every turn to gain 3 pp is a regression.

### 5.3 The baseline ladder (every arm runs; no whole-system verdicts)

| # | Arm | What it isolates |
|---|---|---|
| B0 | Shipped substring Layer A | The floor. Scores 0 on stratum P by construction. |
| B1 | Full manifest in context, model picks (73 / 150 / 306 skills) | **Production today.** The arm to beat. |
| B2 | Manual three-tier gating (`scaling-skills.md`) | GBrain's current remedy. |
| B3 | BM25 over trigger + description text | The lexical retriever. Free, and it must be beaten. |
| B4 | **Dense nearest-prototype (proposed stage 1)** | RAG-MCP. |
| B5 | B4 + max-cosine abstention threshold | Isolates whether abstention needs the fly at all. **This is K2's comparator.** |
| B6 | B4 + logistic calibration on (max-cos, margin, entropy) | The strongest cheap abstention baseline. |
| B7 | **B4 + fly Bloom filter gate (proposed stage 2)** | The fly arm. |
| B8 | B4 + REAR expansion | Confirmatory re-run of §1.5 on a real embedder. |
| B9 | B4 + FlyHash k-WTA codes as the ranking representation | Confirmatory. Expected to lose. |
| B10 | Anthropic **tool search** (`tool_search_tool_bm25_20251119` + `defer_loading: true`) | The first-party primitive that may make all of this redundant — see §10. |
| B11 | Full LLM router over all 150 descriptions | Quality ceiling and cost ceiling. |

Every arm shares one embedder, one chunking policy, one tuning budget, one seed set. B4 vs B8 vs B9 is the expansion ablation; B5/B6 vs B7 is the fly ablation. A whole-system comparison produces no verdict — that rule comes straight from the `+31.4 → +15.0 → +6.2` history in v01.

### 5.4 Reproducing today's measurements

```bash
# clone at 43597b19, bun 1.3.5, python 3.12 + numpy/sklearn
cd artifacts/d3-router
bun run d3_baseline.ts     # -> 303/303 = 100.0% on the shipped fixtures
bun run d3_dump.ts         # -> d3_index.json (840 phrases, 303 fixtures)
python3 d3_bakeoff3.py     # -> the §1.5 table; ~4 min on an M-series laptop
```
The LOTO and STRICT-receipt computations are inline scripts recorded in this report's §1.3 / §1.4 and rerunnable from `d3_index.json` and `evals/functional-area-resolver/baseline-runs/*.jsonl`.

---

## 6. Expected effect size, and the reasoning

| Claim | Predicted | Anchor |
|---|---|---|
| Stage 1 vs full manifest in context (B4 vs B1) at 150 skills, stratum P | **+10 to +25 pp top-1** | RAG-MCP measured **13.62 % → 43.13 %** (+29.5 pp, ×3.17) on tool selection by retrieving before prompting; that was at thousands of MCPs, so I discount it heavily for 150. GBrain's own stress bands ("fine at 100, drags at 200") and my pilot's 0.685-at-150 extrapolation put the in-context arm in the 60–75 % range, leaving room for exactly this size of gain. |
| Always-on context reduction | **−85 % to −95 %** (12,000 → ~300 tok/turn at 150 skills) | Arithmetic on measured 80–90 tokens/skill; GBrain's own tiering already got −84 % (25,000 → 4,000) *by hand and by disabling 180 skills*. The router gets the same reduction **without disabling anything** — that is the real product difference. |
| Added latency | **+1 to 3 ms** if it rides the retrieval embedding; +20–50 ms if it needs its own | g02 measured pgvector HNSW top-10 over 250k × 1024-d at **10.7 ms**; 150 prototypes is ~3 orders of magnitude smaller and is a brute-force dot product. Compare 634–1,722 ms for the LLM router (§1.6). |
| Escalation rate | 8–15 % of turns | Margin distribution in the pilot; must be measured. |
| **Fly gate (B7) vs threshold (B5), abstention F1** | **unknown; prior ~30 % that it wins by ≥3 pp** | **There is no anchor. None.** The fly Bloom filter has never been run on text or embeddings, δ/ε have no published values, and the largest n in the source paper is 5,000. Anyone who quotes a number here is inventing it. |
| REAR / FlyHash arms | **−1 to −6 pp** (i.e. they lose) | Directly measured in §1.5. |

---

## 7. Cost

**Engineering: ~15 person-days** (§11 schedules it into two weeks), of which the benchmark is 3 and the fly gate is 2.

**Compute, per turn.** One embedding — **$0 if it reuses the vector `gbrain search` already computes for the same turn**, which is the design intent — plus 150 × 1024 multiply-adds (~154 kFLOP, microseconds). Prototype build: ~900–1,800 embeddings once, then rank-1 on change.

**The money is in the context bill it removes.** Assumptions stated: 25 people × 40 agent turns/person/working day × 22 days = **22,000 turns/month**; 80 tokens/skill of always-on manifest (GBrain's own figure, corroborated by my 90-token measurement); Sonnet-5 input at $2/MTok, Haiku 4.5 at $1/MTok; cache reads at ~0.1× base input.

| Skills | Manifest tok/turn | Sonnet-5 uncached | Sonnet-5 cached | Router-only (≈300 tok/turn) | Monthly saving (Sonnet, uncached) |
|---|---|---|---|---|---|
| 73 (bundled) | 5,840 | $256.96 | $25.70 | $13.20 | **$243.76** |
| **150 (target band)** | **12,000** | **$528.00** | **$52.80** | **$13.20** | **$514.80** |
| 306 (Garry's actual) | 24,480 | $1,077.12 | $107.71 | $13.20 | **$1,063.92** |

Escalation at 10 % to Haiku over three descriptions: **$1.10/month**. A separate query embedding at GBrain's own per-chunk rate: **$0.53/month**. An LLM router on every turn, by contrast, from the measured receipts: **$89.96–$335.90/month** uncached ($9.00–$33.59 cached).

Context for the magnitude: **g02 put the entire brain-side all-in at ~$225/month for 25 people at 155,795 pages.** At 150 skills the uncached skill manifest alone is 2.3× that, and at 306 skills it is 4.8×. Prompt caching is the reason nobody has noticed — it drops the 150-skill line to $52.80 — but caching is exactly what a per-turn-varying manifest cannot rely on, and GBrain's own guide reports the symptom without the invoice ("cost goes up because every turn carries the full skill manifest").

---

## 8. Kill criteria — pre-registered, and one already executed

**K1 — the expansion arm. ALREADY RUN, ALREADY FAILED.**
*Rule (set before the run, and honoured):* if random expansion (REAR) or k-WTA sparse expansion (FlyHash) does not beat a no-training nearest-centroid by ≥2 pp top-1 at pool 73 in the trigger-blind condition, drop expansion from the design and retire checkpoint decision (iii).
*Result:* REAR −1.1 pp (M=2,560) and −0.3 pp (M=10,000); FlyHash −1.4 to −5.9 pp. **Failed.** Expansion is out of the design. One confirmatory re-run on a real embedder (B8/B9) is scheduled; if it also fails, the sparse-expansion router is closed permanently and this angle's contribution is the measurement, not a component.

**K2 — the fly gate.** If B7 (fly Bloom filter) does not beat **both** B5 (max-cosine threshold) and B6 (logistic calibration) by ≥3 pp abstention F1 on N ∪ P at pool 150, drop the gate, ship stage 1 + a threshold, and **the fly bridge in the routing layer is closed entirely** — leaving g07's mechanism 2 alive only on the write path, where v10b already scoped it. Prior: ~30 % it wins.

**K3 — the router itself.** If B4 does not beat B1 (full manifest in context) by ≥5 pp top-1 at pool 150 on stratum P *while* cutting always-on tokens by ≥70 % and adding <50 ms p99, abandon the router and keep GBrain's manual tiering. A router that only saves tokens is still worth shipping *if* it is accuracy-neutral within ±2 pp — that is a separate, explicitly weaker acceptance branch, and it must be declared as such in the receipt, not discovered afterwards.

**K4 — over-routing.** If enabling the router raises the rate of *unwanted* skill invocation on stratum N by >5 pp relative to B1, ship it in advisory mode only (router proposes, model disposes). See §9.

---

## 9. Risks, and what the prior negative results say

1. **The fly attribution is decoration, and this report must not launder it.** g07's verdict on FlyPrompt — *"Superficial as a fly transplant; Deep as engineering"* — is now half-revoked: my pilot removed the engineering half in this socket too. Any synthesis sentence of the form "fly-inspired routing" is wrong twice over. The correct sentence is: *the fly contributes an abstention gate, if it contributes anything, and that is unproven.*
2. **Over-routing is the failure mode unique to replacing model judgement with a classifier.** Anthropic's `skill-creator` documents that *"Claude only consults skills for tasks it can't easily handle on its own."* A cosine router has no such reticence: it will happily fire a skill the model would rightly have ignored. Mitigations: abstention is the default output, not an exception; `advisory` mode where the router injects candidates and the model still decides; K4.
3. **Prototype poisoning is an org-chart takeover with a wider blast radius.** arXiv:2602.08004 flags public skills with state-changing and system-level actions; `findings/context-engineering-skills.md` notes that a poisoned `triggers:` array is a routing takeover, and g05 argues `SKILL.md` is the highest-privilege object in a company brain. An embedding router **widens** this: an attacker no longer needs the exact trigger string, only semantic proximity. Mitigations, non-negotiable: prototypes built **only** from git-reviewed `SKILL.md` under CODEOWNERS; `kind='observed'` prototypes capped at weight 0.4 and n=32 and never sourced from unreviewed content; `content_sha` binding so a prototype whose skill changed is invalid, not stale.
4. **Retrieval-then-route is not a free lunch at very large N.** RAG-MCP's own analysis: *"retrieval precision challenges arise as the total number of MCPs grows, motivating future work on hierarchical or adaptive retrieval mechanisms."* At 150 skills this design is fine; at 1,000 it needs a hierarchy, and the functional-area dispatcher pattern is the right hierarchy — but see §1.4 before trusting its headline.
5. **Connectome topology gives no prior.** Dhiman (arXiv:2604.04033) shows flyvis's topology advantage vanishing under a degree-preserving null. Nothing in the connectome literature supports wiring a router like a fly.
6. **`sparsevec` will not hold the fly code.** pgvector cannot HNSW-index above 1,000 non-zeros; ρ = 2,048 exceeds it (v10b). The design routes around this by keeping the filter in `REAL[]`, but any variant that tries to *search* sparse codes in Postgres will hit a wall.
7. **PGLite.** Everything here works on PGLite except the HNSW index on `skill_prototypes`, which is unnecessary at 150 rows (brute force is faster). No blocker; state it so nobody adds one.
8. **My own pilot's limits.** LSA-256 over ~950 documents is not an embedder; n = 271 over 55 of 73 skills; random rather than nearest-neighbour distractors (optimistic); oracle λ (generous to the arms that still lost). It is strong enough to demote a recommendation and not strong enough to close a question — which is precisely why K1 keeps a confirmatory run.

---

## 10. Does a non-biological alternative do this better? Yes — say so plainly

**For stage 1: yes, and it is already the proposal.** Nearest-prototype retrieval over skill descriptions is RAG-MCP (May 2025), it is simpler than every fly variant, it has published third-party numbers, and it beat both expansion arms in my own pilot. There is no reason to prefer a bio-inspired operator here and I do not.

**For stage 2 the honest answer is "probably, and that is what K2 tests."** A max-cosine threshold (B5) and a three-feature logistic calibration (B6) are the incumbents; both are ten lines of code with no free parameters to invent. The fly filter's only non-duplicated property is that AIMD gives **duplication and staleness in one number with O(1) state** — the same narrow survivor v10b identified on the write path. If B5/B6 match it, the boring thing ships.

**And there is a first-party primitive that may make the whole component redundant.** The Claude API ships server-side **tool search** — `tool_search_tool_bm25_20251119` and `tool_search_tool_regex_20251119` — used with `defer_loading: true` on the other tools, so tool descriptions are *not* loaded into context until the model searches for them. That is precisely the "route around the manifest" idea, implemented at the platform layer, with the platform's own guard (at least one tool must stay non-deferred, or the API returns 400). Anthropic's *Code execution with MCP* makes the adjacent case with a 150,000 → 2,000 token reduction (98.7 %). Arm **B10** exists so this is measured rather than assumed, and any team weighing this proposal should ask first whether deferred tool loading plus BM25 tool search already gets them 80 % of the win for zero engineering.

Other incumbents considered and rejected as *worse fits*, not as worse ideas: SPLADE-style learned sparse retrieval (50.5 BEIR nDCG@10 vs BM25's 43.7, per v10b) is strong but needs a training pipeline and a rebuild when a skill changes; a cross-encoder reranker over 150 candidates costs more than the LLM router it would replace; fine-tuning a small classifier breaks the add-a-skill-without-retraining property that makes any of this viable.

---

## 11. Two-week MVP

**Week 1 — make the problem measurable (this is the deliverable even if nothing ships).**

| Day | Work | Exit condition |
|---|---|---|
| 1 | Pre-register RouteBench-150: strata, generator prompts, tuning grid, K1–K4 decision rules. Commit; hash into every receipt. | Committed before any run. |
| 1 | Land the LOTO check and the STRICT-vs-LENIENT recomputation as tests in the repo. | `bun test` reproduces 100 % → 0 %. |
| 2–3 | Build stratum P (trigger-blind paraphrases, generator sees body only, frontmatter stripped) + stratum N near-misses. Human-review a 10 % sample for label noise. | ≥600 P, ≥150 N, review sheet attached. |
| 4 | Extend `routing-eval.ts` to score a pluggable router and emit the full metric table (accuracy, abstention F1, tokens, latency). | B0/B1/B2/B3 all run end-to-end. |
| 5 | **Measure B1 and B2 at pools 25/50/75/100/150.** | The pool-size curve exists on a real embedder. **This alone closes a gap no report in this corpus filled.** |

**Week 2 — build and adjudicate.**

| Day | Work | Exit condition |
|---|---|---|
| 6–7 | `src/core/skill-router.ts` + `skill_prototypes` + `route_prototypes` cycle phase + `gbrain skills route`. | B4 runs; prototypes rebuild from `loadSkillTriggerIndex()`. |
| 8 | B5 + B6 abstention baselines; calibrate on N. | Abstention F1 measured. |
| 9 | Fly Bloom filter (`m=40d`, `ρ=5 %`, seed persisted) in **shadow**; sweep δ, ε. | B7 measured; δ/ε sensitivity plotted. |
| 10 | B8/B9 confirmatory expansion arms on the real embedder. | K1 confirmed or reopened. |
| 11 | B10 (Anthropic tool search) and B11 (full LLM router). | Ceiling and platform-alternative arms in the table. |
| 12 | Adjudicate K1–K4. Write the receipt with the pre-registration hash. Ship `skills.router.enabled` dark, or don't ship. | A signed decision, not a vibe. |

**Total ~15 person-days.** Evaluation cost: stratum generation ~$15–40; the arm matrix at ~1,000 questions × 12 arms, mostly Haiku-class ≈ $60–120; B11 at Sonnet ≈ $40. Call it **under $200 of API spend**, which is less than one month of the context bill it is trying to remove.

---

## 12. What I could not resolve

- **No embedder was available in this environment**, so §1.5 uses an LSA-256 stand-in. It is enough to demote the fly router; it is not enough to close it. B8/B9 exist for that reason.
- **RAG-MCP's stress-test sweep is garbled in the arXiv HTML** — it reads "*N* from 1 to 11100 in 26 intervals" and "positions 1 to 11100" in two places, which cannot both be a coherent range. The qualitative bands (>90 % below 30; degradation 31–70; collapse beyond ~100) are stated unambiguously in prose and are what I cite; the sweep endpoint is not. Its other limits: n = 20 web-search tasks, one base LLM (`qwen-max-0125`), figure-only results, no error bars.
- **WebSearch budget for this session was exhausted (200/200) before I started**, so the sweep for post-2026-05 work on skill/tool routing at scale was limited to direct arXiv and GitHub fetches. There may be a 2026 paper that measures exactly RouteBench-150; I could not sweep for it. Confidence that one exists and would change the design: low (~15 %) — the specific missing measurement (trigger-blind paraphrase routing over a 150-skill catalogue with an abstention stratum) is unusual enough that its absence in `gbrain-evals`, in the Agent Skills survey (arXiv:2602.08004) and in SkillAxe (arXiv:2606.10546) is evidence it has not been done.
- **δ and ε for the fly Bloom filter remain uncalibrated** and no published value exists for any text domain. This is the largest unknown in the proposal and the reason for `shadow` mode.
- **Prior-report reconciliation:** `findings/gbrain-architecture.md` reports "142 `SKILL.md` files, 85 skill dirs"; I measure **73 `SKILL.md` under `skills/`, 76 dirs, 223 repo-wide** at the same commit. The difference is scope (`plugin/` 69, `plugin-variants/` 39, `test/` 36, `recipes/` 4). Whoever writes the synthesis should use 73 for "skills the resolver routes" and say so.

---

## 13. Sources

**Primary — GBrain repo** (`garrytan/gbrain`, MIT, commit `43597b19`, v0.48.5.0, pushed 2026-09-08; local clone, all paths verified):
- `src/core/routing-eval.ts` — Layer A substring matcher; the "Layer B … **not yet implemented**" declaration; `normalizeText`, `structuralRouteMatch`, `lintRoutingFixtures`, `runRoutingEval` — https://github.com/garrytan/gbrain/blob/master/src/core/routing-eval.ts
- `src/core/skill-trigger-index.ts` — the shared frontmatter ∪ RESOLVER.md primitive — https://github.com/garrytan/gbrain/blob/master/src/core/skill-trigger-index.ts
- `src/core/check-resolvable.ts` — `parseResolverEntries` (table + compact-list dialects), reachability checking
- `skills/RESOLVER.md` (16,290 bytes, 172 lines) and the 73 `skills/*/SKILL.md`; 44 `routing-eval.jsonl` (303 fixtures)
- `docs/guides/scaling-skills.md` — the 306-skill three-tier account; ~25,000 → ~4,000 tokens/turn; "routing accuracy: degrading"; 63 unreachable skills — https://github.com/garrytan/gbrain/blob/master/docs/guides/scaling-skills.md
- `evals/functional-area-resolver/` — README, `variants/*.md`, `fixtures.jsonl` (n=20), `fixtures-held-out.jsonl` (n=5), and the four `baseline-runs/*.jsonl` receipts from which I recomputed the STRICT table and the token/latency figures
- `docs/guides/skillopt.md`, `skills/skillify/SKILL.md`, `src/core/cycle.ts` (`ALL_PHASES`), `src/core/facts/decay.ts`, `src/schema.sql`, `src/cli.ts`, `src/commands/doctor/checks/routing-federation.ts`, `docs/protocol/MEMORY_VERBS_v1.md`

**Primary — papers:**
- Tiantian Gan & Qiyao Sun, "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation," arXiv:2505.03275 (6 May 2025) — 43.13 % vs 13.62 %; MCP stress test bands — https://arxiv.org/abs/2505.03275 · HTML: https://www.arxiv.org/html/2505.03275v1
- Hongwei Yan, Guanglong Sun, Kanglei Zhou, Qian Li, Liyuan Wang, Yi Zhong, "FlyPrompt: Brain-Inspired Random-Expanded Routing with Temporal-Ensemble Experts for General Continual Learning," ICLR 2026, arXiv:2602.01976 (v1 2 Feb 2026, v3 24 Mar 2026) — https://arxiv.org/abs/2602.01976 · code https://github.com/AnAppleCore/FlyGCL (MIT, 18★, pushed 2026-09-04, verified via `gh api`)
- Mark D. McDonnell et al., "RanPAC: Random Projections and Pre-trained Models for Continual Learning," arXiv:2307.02251 (NeurIPS 2023) — the non-biological ancestor of REAR — https://arxiv.org/abs/2307.02251
- Sanjoy Dasgupta, Timothy C. Sheehan, Charles F. Stevens, Saket Navlakha, "A neural data structure for novelty detection," *PNAS* 115(51):13093–13098 (2018) — the fly Bloom filter, Eq. 2, AIMD
- Sanjoy Dasgupta, Charles F. Stevens, Saket Navlakha, "A neural algorithm for a fundamental computing problem," *Science* 358(6364):793–796 (2017), DOI 10.1126/science.aam9868 — FlyHash: sparse binary projection, m ≫ d, k-WTA, ~5 % activity
- Chaitanya K. Ryali, John J. Hopfield, Leopold Grinberg, Dmitry Krotov, "Bio-Inspired Hashing for Unsupervised Similarity Search," ICML 2020, arXiv:2001.04907 — BioHash (learned sparse expansion); PN→KC sampling rate 0.1 — https://arxiv.org/abs/2001.04907
- Nikhil Dhiman, "Topological Sensitivity in Connectome-Constrained Neural Networks," arXiv:2604.04033 (5 Apr 2026) — degree-preserving null kills the topology advantage
- SkillAxe, arXiv:2606.10546 (9 Jun 2026) — trigger precision as a named skill-quality dimension; human-authored skills +16.2 pp, LLM-authored no measurable gain
- "Agent Skills: A Data-Driven Analysis," arXiv:2602.08004 (8 Feb 2026) — 40,285 public skills; intent-level redundancy; state-changing skill risk

**Primary — platform:**
- Anthropic tool search server tools (`tool_search_tool_bm25_20251119`, `tool_search_tool_regex_20251119`) with `defer_loading: true`; model pricing (Haiku 4.5 $1/$5 per MTok; Sonnet 5 $2/$10; Opus 5 $5/$25) — bundled `claude-api` skill, cached 2026-06-24
- Agent Skills specification (open standard, 2025-12-18): three-tier progressive disclosure, ~100 tokens of metadata always loaded — https://agentskills.io/specification

**Prior reports in this corpus, relied on and in two places corrected:** `findings/g07-neuro-mechanism-inventory.md` (FlyPrompt correction; fidelity rubric; fly Bloom filter as the only Deep mechanism), `findings/g02-sizing-cost.md` (latency and cost anchors), `findings/v10a-h3d-flyhash.md` and `findings/v10b-flyhash-vs-modern.md` (FlyHash refutations), `findings/context-engineering-skills.md` (resolver A/B — **its LENIENT-only table needs the STRICT correction in §1.4**), `findings/gbrain-architecture.md` (**its "142 SKILL.md" needs the scope note in §12**), `findings/g06-crux-experiment.md` (pre-registration and ablation-ladder discipline), `findings/g05-governance-acl.md` (SKILL.md as highest-privilege object).

**Reproduction artifacts:** `/Users/stephen/Cookies/company-brain-research/artifacts/d3-router/` — `d3_baseline.ts`, `d3_dump.ts`, `d3_bakeoff3.py`, `d3_bakeoff2.json`, `d3_index.json`, `d3_skills.json`.

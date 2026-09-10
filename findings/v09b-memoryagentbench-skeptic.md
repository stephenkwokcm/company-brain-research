# v09b — "Arbitration belongs in deterministic code, not an LLM judge": adversarial test

**Key:** `v09b-memoryagentbench-skeptic` · **Lens:** skeptic (try to refute) · **Written:** 2026-09-10 · Research worker (Opus 5)

## The inference under attack

> "Contradiction arbitration belongs in deterministic code, not an LLM judge."
> — drawn from MemoryAgentBench `FactConsolidation`: deterministic `max(serial)` 82–93% single-hop
> vs. every memory system ≤54%.

## Verdict: **REFUTED as stated. A narrower claim survives: the *schema* and the *filter* belong in deterministic code; the *arbitration* does not.**

Four independent lines of primary evidence break the generalisation, and they break it in different
places, which is what makes the refutation robust rather than a single contrary datapoint:

1. **The benchmark's ordering key is manufactured, and the winning policy is the wrong one for most
   real conflicts.** FactConsolidation prints an integer serial on every sentence *and prints the
   resolution rule in the prompt*. Newest-wins is the oracle policy there by construction. In the
   three published conflict taxonomies I checked, newest-wins is the correct policy for **1 of 3
   (MemConflict), 1 of 3 (ConflictRAG), and 1 of 6 (ContextConflict)** conflict classes.
2. **On a real, expert-grounded contradiction corpus, the LLM judge *wins* and the deterministic rule
   loses badly.** RegDivergence-101 (FDA vs EMA guidance, κ=0.85): lexical heuristic **0.511** macro-F1,
   NLI cross-encoder 0.233, obligation-level Graph-RAG 0.663, **flat LLM judge (Claude Haiku) 0.830**.
3. **Where a hand-specified deterministic policy has been benchmarked head-to-head against an LLM
   judge on source selection, the hand-specified rule loses.** ConflictRAG: fixed weights **75.6%**
   selection accuracy vs. **LLM direct selection 78.3%**. Only *data-derived* (entropy) weights beat the
   LLM, at 82.7% — and they run on LLM-extracted criterion scores.
4. **The reference implementation of the company brain does not do this.** GBrain's contradiction probe
   is an **LLM judge** (`claude-haiku-4-5`) emitting six verdicts —
   `no_contradiction | contradiction | temporal_supersession | temporal_regression | temporal_evolution |
   negation_artifact` — and then **refuses to auto-resolve**, emitting paste-ready commands for a human.
   The deterministic parts are the *schema* (`valid_from`/`valid_until`/`superseded_by`) and a >30-day
   date pre-filter. Tan's own system already takes the position this inference denies.

Companion report `v09a` had already shown the causal attribution is inverted (the deterministic
operator is worth **0 pp at 262K** by the authors' own ablation). This report shows the *external*
validity fails too: even if `max()` had earned the points, the policy it encodes is wrong outside the
benchmark.

---

## 1. Is the task synthetic with an explicit serial, and is that fatal?

**Yes, and yes — but not for the reason usually given.** The synthetic-ness is not the problem;
benchmarks are allowed to be controlled. The problem is that the synthesis *installs the answer*.

FactConsolidation, per MemoryAgentBench Appendix B.4 + Appendix D Fig. 5:

- built from **MQUAKE counterfactual edit pairs** — one true fact, one rewritten contradiction;
- **every sentence carries an integer serial**, larger = newer, concatenated in serial order;
- the agent is **told the rule verbatim**: *"the newer fact has larger serial number. You need to solve
  the conflicts … by finding the newest fact";*
- the candidate set is usually **2** (original + one counterfactual).

So the task supplies (i) a total order, (ii) a guaranteed-correct policy over that order, (iii) the
policy in natural language, and (iv) a 2-way choice. `max(serial)` is not a discovered solution; it is
the answer key transcribed into Python. A benchmark constructed this way can show that a memory system
*fails to execute a stated policy* — a real and damning finding — but it cannot show that arbitration
*is* policy execution. Everything hard about arbitration has been assumed away before the task starts:
which candidates are about the same subject+predicate, whether the disagreement is an update or an
error or a scoped exception, and which policy applies.

MemoryAgentBench's own Appendix G concedes the synthetic framing and defends it as a controlled proxy.
The freshness paper's Appendix B concedes the candidate set "generally caps at an original and one
counterfactual value" and "does not test selection over many candidates."

## 2. Do real company facts carry a reliable ordering key?

Three answers, all negative in different ways.

### 2a. Even in the best-case real corpus, newest-wins is wrong most of the time

German federal statutes are an unusually well-curated corpus: every provision version carries a formal
validity interval. This is the strongest ordering key a company could hope for. Prior, Schultz &
Grabmair (arXiv 2605.23497) built 312 expert-validated time-sensitive statutory QA pairs. **197 of the
312 (63%) are Pre-Amendment or Multi-Provision Pre-Amendment questions, where the correct answer is the
*older* version** because the fact pattern is historically anchored. A `max(serial)` policy is wrong on
63% of that benchmark by construction.

What actually works there is deterministic — but it is not newest-wins. RAG-kNN extracts the **as-of
date from the query with a regex**, then hard-filters the retrieval space to versions valid at that
date. Effect (outcome correctness, single-provision Pre-Amendment): RAG-ToC **0.48–0.83** and RAG-kNN
**0.54–0.81** vs. Vanilla 0.37–0.54 and Web-search 0.42–0.67; Claude Opus 4.5 goes **35.40% → 81.42%**.
The paper's conclusion is *"reliable legal QA requires treating temporal validity as a hard constraint"*
— i.e. **as-of-time filtering**, a bi-temporal query, not a supersession `max()`.

The same paper documents the failure mode of naive recency directly: **web search "exhibits a marked
recency bias on historically anchored tasks"**, with recent-interval questions scoring 0.20–0.24 higher
(p<0.05) *only* in the Web condition, and it cites Fang et al. 2025 showing that injecting synthetic
publication dates into otherwise-identical passages measurably promotes them in LLM reranking. Recency
is already an over-weighted signal, not an under-used one.

### 2b. Most revisions are editorial, so "there is a newer version" is not evidence of supersession

The same study is an accidental measurement of this. Of **697** LLM-generated candidate QA pairs, only
**312 (44.8%)** survived review by two senior law students and a qualified lawyer. The leading
rejection reason: *"the version change was only editorial in nature rather than substantive"* — and
also *"the legal consequence remained identical regardless of which version was applied."* On a corpus
with perfect version metadata, telling a substantive change from a formatting change still required
human semantic judgment more than half the time. A company wiki's `updated_at` column is a strictly
worse signal than a Bundesgesetzblatt version interval.

### 2c. In dialogue-derived and general corpora, the key is absent and has to be fabricated

ContextConflict (Yang et al., EMNLP 2026, arXiv 2609.03148) built its temporal split from
ConflictBank-temporal, whose instances have only **"an implicit chronological order."** The authors
state plainly: *"We attach an explicit timestamp to each statement, without modifying the original
evidence, so that temporal relationships become unambiguous. Because timestamps can change gold labels,
each instance is verified by two independent annotators with discussion-based adjudication."*

Read that twice. To get a benchmark where ordering is a usable key, the authors had to **add the key
themselves**, and adding it **changed the gold labels**, requiring double human adjudication. That is
the concrete answer to "do real facts carry a reliable ordering key": no, and manufacturing one is a
semantic act with an error rate, not a metadata read.

Even after the timestamps are handed over explicitly, **93.5% of the temporal instances are classified
"implicit"** — requiring at least two inferential steps rather than surface comparison — and the best of
seven models reaches only **68.0%** accuracy on them.

## 3. Counter-evidence 1 — MemConflict (arXiv 2605.20926): two of three conflict types are recency-proof

Tao et al. (Renmin University / SUFE / MemTensor, 20 May 2026;
[repo](https://github.com/TaoZhen1110/MemConflict), 12★) formalise memory validity as
**query-conditioned fitness-for-use** along three dimensions, and this taxonomy is the cleanest
refutation of a single global `max()`:

| Type | Definition | What resolves it | Does `max(timestamp)` work? |
|---|---|---|---|
| **Dynamic** | earlier and later states coexist; the later is a genuine update | recency | **Yes** |
| **Static** | a later mention *contradicts* an invariant fact and is **false** | source/consistency | **No — inverted.** Newest-wins scores ~0 by construction |
| **Conditional** | multiple values, each true under its own condition (coffee in the morning, milk in the evening) | condition matching against the query | **No — undefined.** Both are valid; neither supersedes |

Construction detail that matters: static conflicts are built **only over invariant profile attributes**
(birthplace, family background, education), and *"the later mention at s_q is explicitly treated as
false information rather than as a valid state update."* Conditional conflicts are built over
condition-dependent preferences where *"the values are factually correct and do not represent temporal
updates of one another."*

**Black-box Answer Accuracy, six memory systems (MemConflict Table 3):**

| System | Dynamic AA | UOCS | Static AA | CRS | Conditional AA | Avg AA |
|---|---:|---:|---:|---:|---:|---:|
| A-Mem | 0.3596 | 0.2911 | 0.2639 | **0.2501** | 0.7122 | 0.4452 |
| LangMem | **0.4966** | 0.3579 | 0.1944 | 0.2083 | 0.1556 | 0.2822 |
| Letta | 0.3955 | 0.3527 | 0.2223 | 0.2031 | 0.8435 | 0.4871 |
| MemOS | 0.3793 | **0.3818** | **0.4375** | 0.2361 | **0.8449** | **0.5539** |
| Mem0 | 0.1224 | 0.1130 | 0.1944 | 0.1528 | 0.7667 | 0.3612 |
| Memobase | 0.4058 | 0.3476 | 0.4167 | 0.0694 | 0.2434 | 0.3553 |

Four things here cut against the inference:

- **No system dominates.** LangMem is best at dynamic (0.4966) and near-worst at static (0.1944) and
  worst at conditional (0.1556) — exactly the profile of a system that over-applies supersession.
  A hard-coded newest-wins arbiter is LangMem's failure mode turned into policy.
- **Conflict Recognition Score is catastrophic for everyone** — best **0.2501**. Systems answer
  correctly without knowing a contradiction existed. You cannot dispatch to a deterministic policy you
  never noticed you needed; **detection precedes arbitration and is the actual bottleneck.**
- **Errors are dominated by retrieval, not policy.** *"Across most systems and conflict types, retrieval
  failures account for the dominant share of errors."* Evidence Utilization Gap averages 0.0769–0.1527.
  Even on dynamic conflicts, where `max()` is the right rule, the ceiling is 0.4966 — because the older
  and newer states are 5–25 sessions apart in a 52-session, 204K-token history with related-entity
  distractors injected between them. Deterministic arbitration over the wrong three candidates is still
  wrong.
- **The authors' own recommendation is schema + reranking + verification, not replacement.**
  *"Memory representations should explicitly encode temporal state, source attribution, and applicability
  conditions … retrieval should be complemented with conflict-aware reranking … memory systems should
  introduce memory-verification steps before response generation."* All three are LLM-side or
  hybrid; none is "move the decision into Python."

**Fair caveat:** MemConflict is also synthetic (12 LLM-simulated Persona Hub users, gpt-5.0-mini
throughout, 124.33 queries/instance, and the authors flag it: *"constructed through controlled simulation
rather than collected from naturally occurring long-term human interactions"*). It refutes the
*generality* of newest-wins; it does not itself constitute real-organisation evidence. §2a and §5 do.

## 4. Counter-evidence 2 — ConflictRAG (arXiv 2605.17301): the hand-written rule loses to the LLM

Wang, Li, Liu & Shu (IEEE SMC 2026 submission, v1 17 May 2026, v2 8 Jun 2026) build a conflict-aware RAG
pipeline. Three findings hit the inference directly.

**(i) You must classify before you can arbitrate, and classification is unreliable.** Conflicts are
typed **factual / temporal / opinion**, each with a distinct resolution strategy; only temporal is
resolved by recency ranking. Four-class type classification reaches **74.3%** accuracy (per-type F1:
temporal 0.823 > factual 0.798 > no-conflict 0.790 > opinion 0.685). Ablating the classifier so that
everything defaults to the factual strategy costs **−7.9%** correctness. Removing detection entirely
costs **−16.6%** and *"the system approaches standard RAG+Reranking performance."* Detection and
classification — the parts that must be semantic — are worth more than the resolution step (−13.2%).

**(ii) Recency is a minority criterion even in the factual policy.** Source selection is an MCDM problem
over five LLM-extracted criteria — authority, recency, relevance, specificity, consistency. Entropy-
derived weights: **authority 0.312, recency 0.245**. Recency is second, and it is 24.5% of the decision.

**(iii) The head-to-head that matters.** Against human ground truth (200 factual samples, κ=0.79):

| Selection policy | Accuracy |
|---|---:|
| Entropy-TOPSIS (data-derived weights over LLM-extracted scores) | **82.7%** |
| **LLM direct selection** | **78.3%** |
| **Fixed weights (hand-specified deterministic rule)** | **75.6%** |
| Equal weights | 71.2% |
| Random | 53.4% |

**A hand-specified deterministic policy is 2.7 points *worse* than just asking the model.** The only
deterministic policy that wins is one whose coefficients were *learned from the data*, and it still runs
on LLM-extracted criterion scores — the same extract-then-execute shape as the freshness paper, with the
same division of labour: the model does the semantics, the code does the bookkeeping. Even temporal
conflicts are resolved by *"metadata **or LLM-extracted dates**"* — the missing-key fallback is an LLM.

## 5. Counter-evidence 3 — RegDivergence-101 (arXiv 2608.28607): on a real corpus, the LLM judge wins

This is the closest published analogue to a company brain's hardest arbitration case: two authoritative
sources, both current, both correct in their own scope. Wu et al. (8 Jul 2026) pair FDA and EMA
requirements on the same topic and ask for **AGREE / DIVERGE / SILENT** — labels grounded in three
peer-reviewed FDA/EMA comparison studies plus primary FDA/EMA/ICH guidance, dual-annotated at **κ=0.85**.

| Method | Macro-F1 (95% CI) |
|---|---|
| Lexical heuristic (deterministic) | **0.511** [0.411–0.605] |
| NLI cross-encoder | 0.233 |
| Obligation-level Graph-RAG | 0.663 [0.570–0.747] |
| **Flat LLM judge (Claude Haiku)** | **0.830** [0.747–0.908] |

The deterministic baseline is barely above the structured-graph floor and 32 points below the LLM judge,
whose CI does not overlap it. And **SILENT** — one source simply says nothing on the point — is a
category no ordering key can express: *"SILENT is semantically detectable but invisible to entailment-only
formulations."* Company brains are full of SILENT: the 2023 policy covers contractors, the 2025 rewrite
never mentions them. `max(version)` silently deletes the only statement on the subject.

**Caveat, stated by the authors:** n=101 pilot, single domain, and the Graph-RAG/LLM CIs partially
overlap. It is the best real-corpus evidence I found on this exact question, and it is a pilot.

## 6. Counter-evidence 4 — GBrain already disagrees with the inference

From `findings/gbrain-architecture.md` (verified against `docs/contradictions.md`):
`gbrain eval suspected-contradictions` samples retrieval pairs, applies a **deterministic date
pre-filter** (>30 days apart skipped), caches on a content+prompt-version hash, and then runs an **LLM
judge** (`claude-haiku-4-5`, ~$0.0006/call) that emits one of six verdicts:
`no_contradiction | contradiction | temporal_supersession | temporal_regression | temporal_evolution |
negation_artifact`. Rates are reported with a **Wilson 95% CI**. **The probe never mutates the brain** —
it emits `resolution_command`s for a human, and only the nightly `consolidate` phase writes `valid_until`.

Four of those six verdicts are distinctions a serial number cannot make. `temporal_supersession`
(newest-wins), `temporal_regression` (the newer statement is a *reversion or error* — MemConflict's
static conflict), `temporal_evolution` (both true, the situation changed — a continuum, not a
replacement), and `negation_artifact` (a chunking/parsing ghost, no real conflict). Deciding which of the
four you are looking at *is* the arbitration. GBrain puts a model there, then a human, and keeps the
determinism in the schema and the pre-filter. So does MemConflict's recommendation list. So does the
statutory RAG pipeline. The convergence across four independent systems is the finding.

## 7. What survives — the steelman for the deterministic side

I set out to refute and did not refute everything. These pieces hold:

1. **Version metadata belongs in the schema, deterministically.** Every source in this report says so.
   MemConflict rec. #1; the statutory paper's "hard constraint"; Chronofy (arXiv 2607.20560) goes
   further and reserves a **temporal subspace inside the embedding** so *"fact age is structurally
   irremovable from the representation."* GBrain's `valid_from`/`valid_until`/`superseded_by` columns
   are the right shape.
2. **As-of-time filtering is a deterministic win and a large one.** Regex the as-of date, filter the
   candidate set to versions valid then. Claude Opus 4.5 35.40% → 81.42%. This is the single strongest
   result in favour of deterministic temporal machinery I found — and it is a *filter*, applied before
   arbitration, not an arbiter.
3. **Once a policy is known, executing it in code is right on systems grounds.** Exact, inspectable,
   independently testable, swappable (newest / second-newest / as-of / interval-aggregate). The freshness
   paper's own README says the determinism *"earns its place on systems grounds … not on average
   accuracy."* That is a real argument; it is just not an accuracy argument.
4. **Retrieval-side determinism is undervalued.** MemConflict shows retrieval failure dominates. Typed
   stores with condition and attribution fields, and conflict-aware reranking, are engineering work.

The line, sharply: **deterministic code should decide *what candidates are eligible* (as-of filter,
scope filter, source ACL) and *record what was decided* (typed edges, valid intervals, provenance). A
model should decide *what kind of disagreement this is* and *which policy applies*. A human should decide
when the policy is contested.** The FactConsolidation result is a demonstration of step 3 in a world
where steps 1 and 2 were done for you by the benchmark author.

## 8. Where the original inference came from, and why it felt right

It is not a crazy reading. Zep/Graphiti — a bi-temporal knowledge graph built specifically to invalidate
superseded facts — scores **7% FC-SH**, its worst column, against plain BM25's 48%. That genuinely looks
like "the fancy memory layer can't do the one thing it advertises." But `v09a` established that
Mem0/Zep/Cognee/MIRIX were run at **chunk size 4096** while everyone else got **512** on a corpus of
short numbered sentences — an 8× handicap on exactly the four systems used as the indictment. And
MemConflict, running these systems properly on a task they were designed for, finds MemOS at 0.5539
average AA and Letta at 0.4871 — mediocre, not broken. The correct reading of the Zep row is "this
benchmark cell is confounded," not "bi-temporal graphs don't work."

## 9. The sentence the synthesis should use

> Arbitration is two problems, and only one of them is code. On MemoryAgentBench's FactConsolidation —
> where every fact carries an integer serial and the resolution rule is printed in the prompt — an
> explicit newest-wins policy reaches 82–93% single-hop while the best memory system reaches 54%, but
> the benchmark supplies both the ordering key and the correct policy, and the paper's own ablation
> puts the deterministic operator at **0 pp** at that scale. Outside that setting the policy itself is
> usually wrong: newest-wins is the right rule for **1 of 3** MemConflict conflict types (it is
> *inverted* for static contradictions and *undefined* for condition-scoped facts), **1 of 6**
> ContextConflict types, and it contradicts the correct answer on **63%** of a 312-question
> expert-validated statutory benchmark where the governing version is the historical one. Where a
> hand-specified deterministic rule has been measured against an LLM judge on real conflicting sources
> it loses — **75.6% vs 78.3%** on ConflictRAG source selection, and **0.511 vs 0.830** macro-F1 on
> FDA/EMA regulatory divergence. What deterministic code should own is the **schema and the filter**:
> valid-from/valid-until intervals, source attribution, applicability conditions, and an as-of-date
> filter applied *before* arbitration — which lifts Claude Opus 4.5 from 35% to 81% on historically
> anchored statutory questions. What the model should own is deciding *which kind of disagreement this
> is* — supersession, regression, evolution, scoped exception, or artifact — and therefore which policy
> applies. That is precisely how GBrain is built: an LLM judge over six verdict types, Wilson intervals,
> and a deliberate refusal to auto-resolve.

**Shorter, if space is tight:**

> Keep version metadata and as-of filtering in deterministic code; keep the decision about *what kind of
> disagreement this is* in the model, with a human on contested cases. Newest-wins is the right rule for
> roughly one conflict type in three — it is inverted when a later statement is simply wrong, and
> undefined when two facts are both true under different conditions — and where hand-written arbitration
> rules have been measured against an LLM judge on real conflicting sources, the rules lose
> (0.51 vs 0.83 macro-F1 on FDA/EMA divergence).

## 10. Confidence

**High** that the strong inference is refuted: four independent primary sources, two with real
expert-annotated corpora, all point the same way, and the reference implementation (GBrain) does the
opposite of what the inference recommends.

**Medium-high** on the surviving positive claim (schema + as-of filter deterministic, arbitration
model-side). The statutory result is one jurisdiction and one language; RegDivergence-101 is a 101-pair
pilot with partially overlapping CIs; MemConflict is 12 simulated users and the systems are run at
defaults. No single source is decisive; the convergence is what carries it.

**Unresolved:** I found **no** study that measures how often real company documents carry usable version
metadata, nor a head-to-head of deterministic vs LLM arbitration on an actual enterprise corpus. The
closest proxies are German statutes (best case, and newest-wins still fails 63% of the time) and
FDA/EMA guidance (LLM wins). Best estimate, low-to-medium confidence: for an internal wiki/Slack/docs
corpus, a machine-readable `updated_at` will exist on most items and be *semantically meaningful* on a
minority of them, since — as the statutory study's 45% expert acceptance rate suggests — most revisions
are editorial. Anyone building this should measure it on their own corpus before hard-coding a policy.

## 11. Corrections to propagate

To `findings/neuro-inspired-rag.md`, in addition to the `v09a` list:
- Drop "contradiction arbitration is a database problem, not a latent-space problem." It is contradicted
  by ConflictRAG (75.6 vs 78.3), RegDivergence-101 (0.511 vs 0.830), and by GBrain's own design.
- Do not describe FactConsolidation's ordering key as representative. Say it is supplied.
- If a single arbitration slogan is needed: *"deterministic eligibility, model-side adjudication,
  human-side resolution."*

---

## Sources

Primary (fetched and read, 2026-09-10):

- Tao, Zhao, Liu, Xi, Chen, Xu & Li, **MemConflict: Evaluating Long-Term Memory Systems Under Memory
  Conflicts** (Renmin Univ. of China / SUFE / MemTensor), 20 May 2026 — https://arxiv.org/abs/2605.20926 ·
  full text https://arxiv.org/html/2605.20926v1
  - §3.1 (validity as query-conditioned fitness-for-use), §3.3.2–3.3.5 (dynamic/static/conditional
    construction, distractor injection), §3.6 (AA, SEH@K, SRS, UOCS, CRS), §3.7 + Table 2 (52.33
    sessions, 2,349.17 turns, 203,910.83 tokens, 124.33 queries: 90.82 dynamic / 16.65 static / 16.86
    conditional; conflict distances 5–25, 10–45, 9–49 sessions), §4.1 (A-Mem, LangMem, Letta, MemOS,
    Mem0, Memobase; gpt-5.0-mini backbone), §4.3.1 + **Table 3** (AA/UOCS/CRS by conflict type),
    §4.5.2 + Table 7 (Evidence Utilization Gap; retrieval failures dominate), §4.6 (design
    recommendations), §5 (limitations: controlled simulation, not naturally occurring)
  - Code/data: https://github.com/TaoZhen1110/MemConflict (12★, created 2026-05-16, pushed 2026-06-27)
- Wang, Li, Liu & Shu, **ConflictRAG: Detecting and Resolving Knowledge Conflicts in Retrieval Augmented
  Generation**, v1 17 May 2026 / v2 8 Jun 2026, submitted to IEEE SMC 2026 —
  https://arxiv.org/abs/2605.17301 · full text https://arxiv.org/html/2605.17301v2
  - §III-C (factual/temporal/opinion typing; per-type resolution strategies; temporal = recency ranking
    over "metadata or LLM-extracted dates"), §IV (NQ-Conflict: 150 factual / 125 temporal / 100 opinion /
    125 no-conflict; κ=0.83), §V (88.7% detection F1, 74.3% four-class accuracy, per-type F1),
    ablations (detection −16.6%, resolution −13.2%, classification −7.9%),
    **§V-E** (entropy weights authority 0.312 / recency 0.245; Entropy-TOPSIS 82.7% vs LLM direct
    selection 78.3% vs fixed weights 75.6% vs equal 71.2% vs random 53.4%; κ=0.79 on 200 samples)
- Yang et al., **Large Language Models in Resolving Contextual Knowledge Conflicts** (ContextConflict),
  EMNLP 2026, 2 Sep 2026 — https://arxiv.org/abs/2609.03148 · full text https://arxiv.org/html/2609.03148v1
  - §2.1–2.2 + **Table 1** (5,781 samples: misinformation 1,004 / inferential 787 / **temporal 960** /
    granularity 1,020 / perspective 1,010 / ambiguity 1,000; temporal 93.5% implicit),
    §2.2 "Temporal Conflicts" (*"We attach an explicit timestamp to each statement… Because timestamps
    can change gold labels, each instance is verified by two independent annotators"*),
    §3.3 (temporal accuracy ceiling 68.0%; inferential <50% even for claude-4.5-sonnet),
    §4.3 + App. D.5/D.8 (first-evidence position bias; reordering fails to override it)
  - *Note:* the abs page says "six types (factual, …)" and "nine LLMs"; the v1 HTML says
    "misinformation" and "seven LLMs". I use the HTML.
- Prior, Schultz & Grabmair, **Asking For An Old Friend: Diagnosing and Mitigating Temporal Failure Modes
  in LLM-based Statutory Question Answering**, 22 May 2026 — https://arxiv.org/abs/2605.23497 ·
  full text https://arxiv.org/html/2605.23497v1
  - §1 (post-cutoff staleness vs recency bias), §2.3 (Fang et al. 2025: injected publication dates shift
    reranking), §3.2–3.4 + §3.5 (697 generated → **312 accepted**; rejection reasons incl. "editorial
    rather than substantive"; 115 Post-Cutoff / **113 Pre-Amendment / 84 Multi-Provision Pre-Amendment**),
    §4.1 (RAG-kNN: regex as-of-date extraction + version filtering as a hard constraint),
    §4.3 (RAG-ToC 0.48–0.83, RAG-kNN 0.54–0.81 vs Vanilla 0.37–0.54, Web 0.42–0.67; Claude Opus 4.5
    35.40% → 81.42%), §4.5 (recency bias significant only in the Web condition, +0.20–0.24, p<0.05)
- Wu et al., **RegDivergence-101: An LLM Benchmark for Cross-Jurisdiction Regulatory Contradiction
  Detection in Life Sciences**, 8 Jul 2026 — https://arxiv.org/abs/2608.28607
  - AGREE/DIVERGE/SILENT task; κ=0.85 dual annotation; baseline hierarchy lexical heuristic 0.511
    [0.411–0.605] < NLI cross-encoder 0.233 < obligation-level Graph-RAG 0.663 [0.570–0.747] <
    **flat LLM judge (Claude Haiku) 0.830 [0.747–0.908]**; SILENT "invisible to entailment-only
    formulations"; authors' own caveat: n=101 pilot
- Syed, Silaghi, Abujar & Akter, **Chronofy: A Temporal-Logical Decay Architecture for Information
  Validity in Time-Aware RAG**, 17 Jul 2026 — https://arxiv.org/abs/2607.20560 (temporal subspace in
  Matryoshka embeddings; learnable exponential decay; STL robustness over temporal validity)
- Wang et al., **QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents**,
  17 Aug 2026 — https://arxiv.org/abs/2608.16168 (typed factual/preference/insight stores; three agents
  jointly infer a temporally *and* contextually valid user state; SOTA on PersonaMem, KnowU-Bench)
- Xu, Ye, Li, Chen, Wang, Liu & Xiong, **Knowledge Conflicts for LLMs: A Survey**, v2 22 Jun 2024 —
  https://arxiv.org/abs/2403.08319 (context-memory / inter-context / intra-memory taxonomy; the
  inter-context branch is the one at issue here)
- MemoryAgentBench (the claim's source), ICLR 2026 — https://arxiv.org/abs/2507.05257 ·
  https://arxiv.org/html/2507.05257v4 (App. B.4 FactConsolidation construction; App. D Fig. 5 the
  serial-number prompt; App. G task rationale; §4.1 + App. F.3 + Table 15 chunk sizes)
- Reddy & Challaram, **Reliable Post-Retrieval Assembly for Agent Memory** (v2, was *Don't Ask the LLM to
  Track Freshness*), COLM 2026 Lifelong Agent Workshop — https://arxiv.org/abs/2606.01435 ·
  https://github.com/cvikasreddy/memory-conflict-resolution (App. B: candidate set capped at ~2;
  README: determinism "earns its place on systems grounds… not on average accuracy")

Secondary / internal:
- `findings/v09a-memoryagentbench.md` (number-level verification; the 0-pp ablation; the chunk-4096 confound)
- `findings/gbrain-architecture.md` §4 and `docs/contradictions.md` —
  https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md (six-verdict LLM judge,
  Wilson CI, never auto-resolves)
- `findings/neuro-inspired-rag.md` (origin of the claim under test)
- `checkpoints/01-sweep-decisions.md`

Note: this session's WebSearch budget (200 calls) was exhausted before I began; all discovery was done
via the arXiv API (`export.arxiv.org/api/query`) and direct `curl` of arXiv abs/HTML pages and the GitHub
API, i.e. primary sources only.

# Company Brain × Fruit-Fly Brain — decision document

**For:** a developer who builds hybrid graph+vector RAG systems (`hk-law-rag`, `hk-gov-data-rag`: Neo4j + BGE-M3 1024-d + BM25 fusion).
**Question:** (a) is a "company brain" just RAG, (b) can it be combined with the recently published fruit-fly brain work, (c) what already builds on these ideas.
**Status:** FINAL — orchestrator-reviewed synthesis over 44 worker reports (15 sweep, 14 verifications, 7 gap-fills, 5 designs, 3 judge scorecards). 2026-09-10.
**Read `ERRATA.md` before citing any pre-verification report.**

> **Orchestrator's verdict (Claude Fable 5.1).** I accept the draft below in full after checking it against the verification verdicts, the three judge scorecards and the raw experiment files. Three things a reader should know first:
> 1. **The answer to (a) is "RAG plus a write-side lifecycle plus skills, with the librarian still unbuilt anywhere."** The graph/hybrid numbers in GBrain's README do not survive isolation; the one clean A/B is +6.2 R@5 on relational questions. Whether curation improves *answer* accuracy over a tuned hybrid has never been measured. §7.1 is the experiment.
> 2. **The answer to (b) is "yes, but not the way the metaphor suggests."** Every fly *algorithm* (FlyHash index, FlyHash dedup, fly router) was measured in this session and lost to a boring incumbent. What survives: one pilot (fly Bloom filter as a recurrence-after-dormancy clock, ~40% odds), one build that the mushroom-body literature motivated but that stands without it (readout-gated promotion + a separately parameterised forgetting daemon), and a process lesson from the connectome consortia (publication is not release; curation is the product). Tan's talk has zero neuroscience in it; the bridge is yours.
> 3. **Provenance of the numbers.** The d3/d4/g02 measurements were run by Opus 5 agents on this machine (pgvector 0.8.6 in Docker, BGE-M3 locally); scripts and raw JSON are in `experiments/`. They are reproducible but not third-party replicated. Everything else carries a URL. `ERRATA.md` lists 22 claims from the first-round reports that verification overturned; the tables here use the corrected forms.


---

## 1. TL;DR

1. **A company brain is RAG on the read path, plus a write-side lifecycle, plus procedural memory.** Tan concedes the premise on stage — *"you're right that retrieval is the primitive, the same way Postgres is just B-trees"* (12:57) — and relocates the value to what gets written, linked, tiered and arbitrated. YC's funding brief goes further: the deliverable is *"an executable skills file for AI,"* and *"this isn't a company-wide search or a chatbot over documents"* ([ycombinator.com/rfs#company-brain](https://www.ycombinator.com/rfs#company-brain), 2026-04-28).
2. **The headline proof does not survive isolation, and the crux question is unrun.** The only clean one-switch A/B gives the typed-edge graph **+6.2 R@5** and **+9.7 first-place-hit** on 145 relational questions; the BM25+vector fusion layer is **neutral-to-negative** against pure vector (93.8% vs 93.19–93.40% strict recall_all@5 on LongMemEval-S); the **reranker** supplies the +2.1 that reaches 95.53%. The README's `+31.4 P@5` is a superseded whole-adapter gap with lost receipts, re-measured by its own authors at +15.0 ([gbrain-evals](https://github.com/garrytan/gbrain-evals)).
3. **The librarian does not exist in shipped code — in any system.** GBrain's 23-phase nightly cycle automates the *mechanical* half (ingest triage, junk regex, cosine-0.85 consolidation, a 50-page/run merge, 72 h GC) and refuses semantic pruning by written policy: *"archive is product judgment, not maintenance."* The cost is its own review queue at **32,500 rows growing 2–6k/day** ([gbrain#3269](https://github.com/garrytan/gbrain/issues/3269)).
4. **The "recently published fruit-fly work" is the complete male *Drosophila* CNS connectome** — Berg et al., *Cell* 189(18):5504–5526.e15, **3 September 2026**, [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015): 166,700 neurons, 11,710 types, 124.2M connections, ~44 person-years. Its lesson is **curation**, not algorithm: the data was downloadable under CC-BY for **eleven months** and almost nothing was built on it; third-party applications appeared **48–72 hours** after the curation was certified and publicised.
5. **Every fly *algorithm* was measured this round and lost.** As a pgvector backend, sign binarization beats FlyHash at equal bytes (**0.7577 vs 0.4948** recall@10; **0.9918 vs 0.8339** after rescore) and the parity config is refused outright (`sparsevec cannot have more than 1000 non-zero elements for hnsw index`). As a dedup hash it loses to the free ANN probe (**0.843 vs 0.800**). As a router it loses to a no-training nearest centroid at every pool size. **KILL all three.**
6. **Exactly one fly mechanism survives, at PILOT.** The fly Bloom filter (*PNAS* 2018) as a write-time **recurrence-after-dormancy** clock — "similar to something we saw three weeks ago but not this week" — which is where superseded facts live, and which GBrain's contradiction probe structurally cannot see (*"skip pairs whose dates are >30d apart"*). ~40% odds; a 4-day, ~$0 offline test settles it.
7. **The highest-value transfer for your legal/government RAG has nothing to do with flies: as-of-date filtering before arbitration.** On 312 expert-validated time-sensitive statutory questions, **197 (63%)** have the *older* version as the correct answer — newest-wins is inverted by construction. Regexing the as-of date from the query and hard-filtering to versions valid at that date takes Claude Opus 4.5 from **35.40% → 81.42%** ([arXiv:2605.23497](https://arxiv.org/abs/2605.23497)).
8. **Do this first:** the **Tier-0 crux slice** — ~$30, one afternoon, 804 MemConflict static + conditional questions, tuned hybrid vs curated brain vs reranker-off. The cheapest experiment that can falsify the entire thesis, and nobody has run it.

---

## 2. What the talk actually says

Garry Tan, *"Every company should have a Brain,"* AI Engineer World's Fair closing keynote, published [2026-07-16](https://www.youtube.com/watch?v=eBUyTS7SzV4), 21:08. Filed by the organisers under the track **"RAG, context, and search"** ([ai.engineer/speakers/garry-tan](https://ai.engineer/speakers/garry-tan)).

| Time | Beat |
|---|---|
| 01:25–03:21 | The 400X claim, self-deflated to an "8X floor" → the pivot: *"the leverage is not in the weights. It's in how you wire the work"* |
| 04:31–05:33 | **The core mapping:** skill file = employee · resolver table = org chart · filing rules = internal process · trigger evals = performance reviews. *"You're not writing software, you're hiring, training, and managing a workforce made of markdown."* |
| 08:36–12:56 | **Latent vs deterministic space** — *"all of the bugs… it's usually because something is happening in one side of the equation that should be in the other"*; the 800-seat example puts state outside the context window. Then working memory (7±2 vs 1M tokens) → *"your company is a library"* → **brain = library + librarian** |
| **12:57–13:27** | **The RAG rebuttal, verbatim:** *"This is just RAG. And you're right that retrieval is the primitive, the same way Postgres is just B-trees. The hard part is everything around it. What gets written down in the first place… how it gets enriched and linked, what gets promoted to hot memory versus filed as cold reference, who arbitrates when two facts disagree. Retrieval is easy. Being worth retrieving from is the product."* |
| 14:24–15:12 | The honest passage: three failure modes (*garbage dump with great search* · *a stale fact surfaced with total confidence* · *a bad skill file encodes a bad process forever*) → *"not memory. It's memory plus hygiene, provenance on every fact, contradiction checks… and a librarian, human plus agent, whose actual job is pruning"* |
| 15:29–17:50 | **Skillify** (*"if you have to ask for something twice, you failed"*) → *"model quality is rented, but if you build your brain, you own that brain"* → the greenfield: *"I'd like to fund you at YC if you do"* |

Two structural facts matter more than any number in it. **It is a concession, not a refutation.** And **he authors the open-source layer, presides over the fund issuing the RFS for companies built on it, and offers to fund them** — without naming that alignment.

---

## 3. Is a company brain RAG?

### 3.1 The precise answer

> **A company brain is RAG on the read path, plus (1) write-side evidence production with human-gated mutation — provenance, hot/cold tiering, contradiction *detection* — and (2) procedural memory (`SKILL.md`).** The dividing line is **read-side vs write-side agency**: Naive → Advanced → Graph → Agentic RAG all make *retrieval* smarter over a corpus someone else curated; agent-memory systems make *the corpus itself* a managed, mutable, provenanced object. The one requirement plain memory systems do not cover is procedural memory.

Note the word choice: **evidence production**, not *curation*. Reading the code shows write-side agency that is real in provenance and tiering but **advisory in arbitration** — the system produces the evidence and hands a human the trigger.

### 3.2 The reconciled benchmark sentence — say it in one breath

GBrain's README holds two sentences ~395 lines apart that look contradictory and are not. They measure different layers, corpora and metrics — but only one of them survives scrutiny:

- **Line 379:** *"The graph is what produces the +31.4 P@5 lift over vector-only RAG."* A **superseded April-2026 whole-adapter gap** on a 240-page corpus Claude Opus wrote for $3.14, measured with a since-corrected precision denominator, whose question generator shares its four templates with the adapter's own parser, whose receipts were lost (`disclosed-gap`), and which GBrain's own corrected re-run puts at **+15.0**. Both April reports deny the graph attribution this line asserts, and it mislabels the comparator (the −31.4 row is the *graph-disabled hybrid*; vector-only is −38.4).
- **Line 407:** *"Pure vector on the same corpus scored 93.8%… so the hybrid layer is roughly neutral on this benchmark."* Live, on the public third-party LongMemEval-S, and it **replicates on three further fixtures** (concept search: vector-only 0.6054 nDCG beats both hybrids; source-swamp and externally authored questions: vector leads).

**Cite the isolated one-switch A/B instead** — shared index, shared query vectors, one flag: **+6.2 points R@5 and +9.7 points first-place-hit** on 145 relationship questions, **45 gains and 0 losses across 435 pairs**; `invested_in` first-place went **9/39 → 21/39**. Real, and HippoRAG-adjacent rather than novel. It is also a **retrieval** result with **no answering model in the loop**, and no third party has re-executed either number.

Two caveats. No **template-blind paraphrase variant** of those 145 questions has ever been run (issue #24, April 2026), so even +6.2 is measured only on wording the parser was built to recognise. And when a sibling subsystem *was* tested trigger-blind it collapsed: GBrain's skill router scores **303/303 = 100.0%** on its own fixtures and **0/271 = 0.0%** once the copied trigger phrases are deleted, with 24 intents silently misrouting.

### 3.3 The librarian thesis — strongest evidence for and against

**For.** Bounded self-managed memory scores **15 points below full context** on LongMemEval knowledge-update questions (92% → 77%), and proportionally more memory moves accuracy **28% → 28%** — capacity is not the binding constraint, policy is ([arXiv:2606.27472](https://arxiv.org/abs/2606.27472)). Embeddings provably cannot fix staleness: cosine separates "contradicted fact" from "rephrased duplicate" at **AUROC 0.59**, and vanilla RAG serves superseded values **15–40%** of the time ([arXiv:2606.26511](https://arxiv.org/abs/2606.26511)). Ramp's "Glass" + Git-backed "Dojo" (**over 350 skills shared**, write-once-read-many memory where *"the agent never modifies memory during a conversation,"* a separate 24-hour cleanup daemon) reached four of these design decisions independently, with zero neuroscience.

**Against.** Library science splits Tan's single word into two professions: **collection management** (appraisal, weeding, retention) and **reference service** (picking the three books). Every system here is excellent at the second and unstaffed at the first. OAIS states the invariant — content *"is never deleted unless allowed as part of an approved strategy. There should be no ad-hoc deletions"* (CCSDS 650.0-M-2 §3.1) — which presupposes an approved **disposal schedule**. GBrain has the prohibition and no schedule; there is no knowledge-retention config key at all. Meanwhile `pages.last_retrieved_at` exists, is B-tree indexed, and its **only consumer is an idea generator** that selects never-read pages *in order to generate more pages*. The circulation desk is wired to the acquisitions department. CREW's control law is one line: *weed about the same amount as you are adding*.

The strongest counter-argument to the whole category: **incumbents are ~70% of the way there.** Glean imports `SKILL.md` from GitHub under the open Agent Skills standard; Notion saves skills *as* `SKILL.md`; Dust ships nightly *Self Improving Skills* proposing evidence-based diffs for human approval — GBrain's `skillopt`, shipped by a competitor. Guru automatically verifies **and unverifies** knowledge from behavioural signals and excludes unverified content from answers.

### 3.4 Tan's 7 requirements → existing mechanisms

| # | Requirement (his words) | Best existing mechanism | Who ships it | Honest status |
|---|---|---|---|---|
| R1 | *"what gets written down in the first place"* | Extract→update policy with explicit ADD/UPDATE/DELETE/NOOP | [Mem0](https://arxiv.org/abs/2504.19413); GBrain ingest triage + notability gate | Shipped widely. No published end-to-end win |
| R2 | *"how it gets enriched and linked"* | LLM-built KG + PPR / typed edges on write | [HippoRAG 2](https://arxiv.org/abs/2502.14802), [GraphRAG](https://arxiv.org/abs/2404.16130), [LightRAG](https://arxiv.org/abs/2410.05779); GBrain auto-link (zero LLM calls) | Shipped. Worth **+6.2 R@5** on relational questions, isolated |
| R3 | *"promoted to hot memory vs filed as cold reference"* | Tiered memory + scheduled consolidation | [MemOS](https://arxiv.org/abs/2505.22101), [Letta](https://arxiv.org/abs/2504.13171); Ramp's 24 h daemon | GBrain promoted **0 facts in 62 buckets** in a live run ([#3042](https://github.com/garrytan/gbrain/issues/3042)). Every incumbent "memory" is **per-user**, not org-shared |
| R4 | *"who arbitrates when two facts disagree"* | Bi-temporal invalidation; SQL:2011 `PRIMARY KEY (key, period WITHOUT OVERLAPS)` | [Zep/Graphiti](https://arxiv.org/abs/2501.13956); Db2/MariaDB/XTDB since 2011 | **The genuinely unclaimed enterprise ground** — 0 of 1,402 Glean doc pages mention "contradict". GBrain detects, refuses to auto-resolve |
| R5 | *"provenance on every fact"* | [W3C PROV-DM](https://www.w3.org/TR/prov-dm/); evidence-before-belief | [Eywa](https://arxiv.org/abs/2605.30771); GBrain compiled-truth zones | Shipped. But up to **57%** of RAG citations are correct-yet-unfaithful ([arXiv:2412.18004](https://arxiv.org/abs/2412.18004)) |
| R6 | *"a librarian… whose actual job is pruning"* | CREW weeding; OAIS disposal schedule; W-TinyLFU admission | **Nobody** | The hole. Mechanical half automated, semantic half human-gated by policy |
| R7 | *"skillify it"* | `SKILL.md` / Agent Skills, open standard since Dec 2025 | [Glean, Notion, Dust](https://arxiv.org/abs/2602.12430); GBrain 50+; Ramp Dojo 350+ | Shipped everywhere. **26.1%** of community skills carry vulnerabilities |

**The arbitration slogan to adopt:** *deterministic eligibility, model-side adjudication, human-side resolution.* Code owns valid-time intervals, provenance, applicability conditions and the as-of filter; the model classifies *what kind* of disagreement this is; a human resolves contested cases. Do **not** say "arbitration is a database problem" — MemoryAgentBench's own ablation refutes it (the deterministic `max(serial)` is worth **+2.0 pp pooled and 0.0 pp at 262K**; the gain comes from the LLM extraction stage), and hand-written rules lose to an LLM judge head-to-head on real conflicting sources (75.6% vs 78.3% on ConflictRAG source selection).

---

## 4. What "the fruit-fly brain work" most likely is

| Rank | Work | Verified date | What it offers | What it does not |
|---|---|---|---|---|
| **1** | **MaleCNS** — Berg et al., *"Sexual dimorphism in the complete Drosophila male central nervous system connectome,"* [*Cell* 189(18):5504–5526.e15](https://doi.org/10.1016/j.cell.2026.08.015), CC BY 4.0, 111 authors | **3 Sep 2026** (7 days before the question). No ahead-of-print record exists | 166,700 neurons · 11,710 types · 124.2M synaptic connections · 25.6M edges among 166,483 synapse-bearing neurons · ~44 person-years. A **curation** existence proof (see below) | Any retrieval algorithm. It is cartography |
| **2** | **BANC** — Bates, Phelps, Kim, Yang et al., *"Distributed control circuits across a brain-and-cord connectome,"* [*Nature* 656(8129):957–970](https://doi.org/10.1038/s41586-026-10735-w) | **8 Jun 2026** | 155,916 proofread neurons; 218,460,852 detected synaptic links (18% two-sided). Competence is **local**; the central layer routes and supervises — the architectural brief for "skills at the edge + a thin resolver." **1,316 descending vs 1,031 effector vs 1,849 ascending** neurons: the command channel is *wider* than what it commands | Its own analogy is Brooks' 1986 **subsumption architecture**, not memory. The supervisory layer is *"nonessential for many behaviours"* — which cuts **against** "the central brain is where the value lives" |
| **3** | Fly-inspired algorithms — [FlyHash](https://doi.org/10.1126/science.aam9868) (*Science* 2017), [fly Bloom filter](https://doi.org/10.1073/pnas.1814448115) (*PNAS* 2018), [Spi-Fly](https://doi.org/10.1088/2634-4386/ae9177) (24 Aug 2026) | 2017 / 2018 / 2026 | The **only** branch with a mechanism you could put in a retrieval stack | See §5 — measured, mostly refuted |
| **4** | The DOOM / Mario / Minecraft meme wave | **Two waves**, and the first is not MaleCNS: FlyWire/FAFB from **18–20 Aug 2026** (`desktop-fly` 796★; `mutkuoz/flydoom` 20 Aug, FAFB-v783, female), then MaleCNS from **5–6 Sep** | Why a tech person is talking about flies right now | Nothing. The DOOM mapping was hand-configured and does not reproduce the fly's motor pathways |

**Worth asking:** did you mean the 166,700-neuron male connectome (3 Sep), fly-*inspired* algorithms like FlyHash, or the fly-plays-DOOM demos from August? They lead to three different answers.

**The talk contains zero neuroscience** — "brain" is a library metaphor throughout, and no published work combines connectome or mushroom-body ideas with RAG. The bridge is your own synthesis, which means both the upside (unclaimed ground) and the downside (unproven) are real.

**The one argument the connectome genuinely supplies: publication is not release.** MaleCNS v0.9 was downloadable 2025-10-03 and v1.0 2026-06-08; almost nothing was built on either. What changed on 3 Sept was that the curation was *certified and publicised* — and third-party applications appeared within 48–72 hours. That is dated, checkable evidence for *"retrieval is easy; being worth retrieving from is the product,"* and it is stronger than anything in the transcript.

---

## 5. Combining them — ranked designs with verdicts

Five designs were specified at implementation grain and judged by three seats (RAG engineer / computational neuroscientist / YC founder). **Four of the five designers measured their own fly component and reported that it lost.** Every design's real deliverable turned out to be the non-biological seam it opened while looking. Ranked below by *what to fund*, not by mean judge score — the two deliberately disagree at ranks 3 and 4 (mean scores in parentheses, out of 50).

| Rank | Design | Verdict | Insertion point | Expected effect | Kill criterion |
|---|---|---|---|---|---|
| **1** | **Lifecycle: readout-gated promotion + suppressible forgetting daemon + evidence ledger** (38.3, **BUILD** ×3) | **BUILD L0+L1** (2.5 days); defer L2/L3 | `pages.last_retrieved_at` (indexed, exists) → a `retrieval_bouts` ledger with a 24 h refractory; then `cycle/phases/consolidate.ts` | Cold-tier yield **0 → 3–15 per 1,000 active facts/night**; superseded-serving **−8 to −20 pp**; $0–11/month marginal spend | **K5, one day, $0:** AUROC of `last_retrieved_at` predicting "cited in a correct answer" **< 0.60** ⇒ L1 dies. **K4:** a zero-fly arm (W-TinyLFU + CREW + SQL:2011) ties within 1.0 pp ⇒ publish *"the fruit-fly framing contributed nothing measurable"* |
| **2** | **Index: FlyHash/BioHash as `vector.backend`** (38.3) | **KILL the fly backend; BUILD `D4-ALT`** (3–5 days) | `CREATE INDEX … USING hnsw ((binary_quantize(embedding)::bit(1024)) bit_hamming_ops)` + two-stage rescore | **22.5× storage** (13,726 → 609 B/row), **1.9× latency** (7.34 → 3.81 ms p50), **0.9918 recall@10**. $410/mo → $110/mo at 1M pages | Already fired, on **every** configuration: ρ∈{10,20,40} × f∈{12,102,205} × k∈{16…1024} plus trained BioHash |
| **3** | **Router: sparse-expansion / FlyPrompt for the resolver** (37.0) | **KILL the fly router; BUILD the boring dense one** (stage 1 + RouteBench + the LOTO regression test) | The declared-but-unimplemented `Layer B (LLM tie-break)`, `src/core/routing-eval.ts:15–20` | +10 to +25 pp trigger-blind top-1; −85 to −95% always-on skill tokens (~$40/month **cached** at 150 skills, ~$95 at 306 — not the $528 uncached headline) | **Day 1, not day 11:** if Anthropic's `tool_search_tool_bm25_20251119` + `defer_loading: true` delivers 80% of it for zero engineering, stop. **K3:** must beat the full manifest in context by +5 pp |
| **4** | **Write gate: two-compartment fly Bloom filter at the ingest waist** (37.3, **PILOT** ×3) | **PILOT — run K2 only** (4 days, ~$0, no product code touched); ship the *seam* with `scorer: max-cosine` regardless | `src/core/import-file.ts:756`, after the `content_hash` short-circuit, before chunking. **`on_duplicate: route`, never `block`** | $7–19/month saved, break-even at **0.7%** of writes suppressed. The real prize: a **write-time contradiction trigger** reaching supersessions the shipped probe discards (>30 days apart), at **$0.68/month** for 250 writes/day | **K2:** `fly-bank` must beat max-cosine (**0.843**), `binary_quantize` (**0.834**), SimHash and SAGE by **≥10 pts AUROC** on recurrence-after-dormancy at G∈{7,14,25} days. Author's P(win) ≈ 40%; overall ≈ 20% |
| **5** | **Process: connectome curation practice (CAVE / neuPrint / VFB)** (31.7, PILOT/PILOT/DEFER) | **Cherry-pick 4 cheap borrows now (~4 days); DEFER the keystone** (6–8 weeks) | `page_versions` as a content-addressed immutable substrate; `facts.entity_slug` lineage | Pre-registered **null** on pooled accuracy. Buys reproducibility, arbitrability, governance | **K1:** if measured anchor/slug breakage over 30 days of real traffic is **< 2%**, ship `page_lineage` alone and stop |

### 5.1 Ship these regardless of every experiment above

- **Invert the merge automation.** ConnectomeBench ([arXiv:2511.05542](https://arxiv.org/abs/2511.05542)) measures LLMs at **75–85%** on split-error correction and 52–82% on segment identification, but *"generally struggling on merge error identification."* GBrain's **only** automatic destructive operation is a slug-normalising **merge** at 50 pages/run. Automate splits and identification; human-gate merges. One day, and the only panel recommendation backed by a benchmark that measured exactly this decision.
- **Fix `HALFLIFE_DAYS`.** `exp(-age/7)` is 0.368 at 7 days — a time constant τ, not a half-life. True half-life **4.85 days**; every kind decays **1.44× faster than its name claims**. One line, before anything is calibrated against it.
- **Leave-one-trigger-out as a CI check.** Any benchmark whose fixtures were written against the mechanism under test is a tautology check.
- **`corpus_defects(source_id, scope, valid_from, valid_until, reason)`** — stamp any retrieval intersecting an open defect ("the Slack connector dropped threads 2026-03-01…03-14"). One day; nothing in the stack does it.
- **Confidence carried with its scale and producer**; a verified value beats a predicted one. A bare `REAL DEFAULT 1.0` compared across extractors and model versions is meaningless arithmetic.

### 5.2 Unclaimed ground vs unproven ground

**Unclaimed and worth taking:** contradiction arbitration in a system of record you own (0 of 1,402 Glean doc pages mention "contradict" — structurally unavailable to an index-over-sources product, which has no authority to resolve a conflict between documents it does not own); a **shared org** hot→cold tier (every incumbent memory shipped in 2026 is per-user); a template-blind paraphrase benchmark for relational retrieval; ownership and exit.

**Unproven, and honestly so:** that any of it improves downstream **answer accuracy** over a tuned hybrid with a reranker. No published study measures it. The modal expected outcome is a **pooled null with a large effect confined to the supersession stratum** — curation buys hygiene, not retrieval.

**Refuted — do not reopen:** FlyHash as index, quantizer, dedup hash or routing representation; FlyPrompt as a "sparse-expansion router" (REAR is a *dense* Gaussian matrix + ReLU + ridge regression; the gain is expert modularity — RanPAC alone 79.92 vs FlyPrompt 86.76); connectome topology as a wiring prior ([arXiv:2604.04033](https://arxiv.org/abs/2604.04033): the advantage vanishes under a degree-preserving null).

### 5.3 The non-biological alternative for every fly job

| Fly proposal | The incumbent that already does it | Margin |
|---|---|---|
| FlyHash as index | `binary_quantize()` + rescore, one DDL change, no training step | +53% relative recall@10 at equal bytes; 2.4× fewer bytes; 2.2× faster |
| FlyHash as dedup | `1 − max cosine` from one HNSW probe **you have already paid for** | 0.843 vs 0.800 on paraphrase-shaped edits (lexical SimHash: 0.263 — it is *not* the incumbent) |
| Fly router | Dense nearest-prototype retrieval ([RAG-MCP](https://arxiv.org/abs/2505.03275)) | Wins at every pool size, no training |
| MB consolidation | W-TinyLFU admission ([ACM TOS 13(4)](https://doi.org/10.1145/3149371)) + CREW's acquisition-rate law | Expected to tie — which is the point of running the control arm |
| Extinction ledger | SQL:2011 `PRIMARY KEY (key, period WITHOUT OVERLAPS)` | Makes contradiction **unrepresentable at write time** instead of discoverable by a nightly probe |
| Fly Bloom novelty gate | SAGE's von Mises-Fisher gate (Apache-2.0, published cost/latency, 16–18% LLM-call reduction) | Occupies the slot today with numbers the fly filter does not have |

**The one rule that saves more engineering than anything else in this project:** before any novelty, dedup or staleness machinery, the arm to beat is `1 − max cosine` from an ANN probe you already run — **3.78 ms at 100K vectors**. Most gates will not clear it.

---

## 6. Projects worth your attention

**Measure the thesis**
1. [garrytan/gbrain-evals](https://github.com/garrytan/gbrain-evals) (419★) — the most decision-relevant artifact in the space *and* the reason to distrust the README above it: per-configuration deltas, a `disclosed-gap` receipt status, an expansion feature that cost 187 questions, a re-run that halved its own headline. Read `docs/retrieval-lessons.md` first.
2. [MemConflict](https://github.com/TaoZhen1110/MemConflict) — 3,750 questions, 202K mean dialogue tokens; the only released set with **static / conditional / dynamic** conflict strata and a `diagnose_failures.py` that splits retrieval failure from utilisation failure.
3. [LongMemEval](https://github.com/xiaowu0162/LongMemEval) ([arXiv:2410.10813](https://arxiv.org/abs/2410.10813)) — the one third-party human-built benchmark here. Its knowledge-update slice is n=78 and detects nothing under ~20 pp: **pool it, never report it standalone.**

**Write-side / lifecycle systems**
4. [Zep / Graphiti](https://github.com/getzep/graphiti) — the cleanest shipped bi-temporal invalidation; its arbitration is 31 lines of interval arithmetic with no model call.
5. [Letta](https://github.com/letta-ai/letta) + [sleep-time compute](https://arxiv.org/abs/2504.13171) — git-versioned memory, a `memory doctor` subagent, ~5× less test-time compute for equal accuracy.
6. [Cognee](https://github.com/topoteretes/cognee) — SHA-256-chained append-only provenance lineage plus `contradicts` edges with confidence scores.
7. [HippoRAG 2](https://arxiv.org/abs/2502.14802) — the honest ancestor of GBrain's graph claim, and the baseline any typed-edge result should be scored against.

**Reference architecture and counter-thesis**
8. [garrytan/gbrain](https://github.com/garrytan/gbrain) (29.8K★, MIT) — read `skills/_brain-filing-rules.md`, `docs/contradictions.md` and `skills/skillify/SKILL.md`'s **NO-REGRESSION LAW**; not the benchmark numbers.
9. [agno-agi/scout](https://github.com/agno-agi/scout) (724★) — navigates live sources on demand instead of pre-indexing. **If Scout works, half the talk is wrong.** Worth 20 minutes.
10. **Connectome curation as an engineering reference:** [CAVE](https://doi.org/10.1038/s41592-024-02426-z) (*Nature Methods* 22:1112, 2025 — 1.8B annotations, >4M edits from >500 users, as-of query at 525→978→1,385 ms, ~$500/month) and [CAVEclient](https://github.com/CAVEconnectome/CAVEclient). The connectome community publishes what curation costs. No memory vendor does.

*Also:* [MemOS](https://github.com/MemTensor/MemOS) (tiering as OS scheduling); Ramp's Glass/Dojo write-ups; [aura-memory](https://github.com/teolex2020/aura-memory) (73★ — provenance + temporal versioning + contradiction governance, readable end-to-end).
*Do not cite:* the `b01-gbrain-*` "vertical templates" (astroturf); *"MemFly, arXiv:2602.09871"* (fabricated — that ID is an astronomy paper).

---

## 7. Recommended next steps

### 7.1 The crux experiment, in eight lines

The unanswered question, named by four independent reports: *does write-side curation improve **downstream answer accuracy** over a well-tuned BM25+dense hybrid on real organisational questions?*

1. **Primary endpoint is judged answer accuracy**, retrieval reported in the same table — the two diverge (95.53% retrieval completeness vs 86.6% answer accuracy on the *same* run).
2. **Tune the baseline with the same budget as the treatment** — same dev split, script and reranker — and publish the trial log. This is where the experiment is normally lost.
3. **Every arm runs an ablation ladder**, and the decision rule carries an explicit **RERANKER-EXPLAINED** verdict. The `+31.4 → +15.0 → +6.2` chain is the cautionary tale.
4. **Pool MemConflict (3,750 q) with LongMemEval-S (470 q)** → n=4,220, minimum detectable difference **1.7–2.8 pp**. LongMemEval alone detects only 5–8 pp, so every published 2-point "win" on it is noise.
5. **Control the confounds:** pin chunk size (MemoryAgentBench ran Mem0/Zep/Cognee/MIRIX at 4096 while everyone else got 512); separate embedder-controlled arms from black-box ones; keep a **full-context arm** (MemoryAgentBench v4 has GPT-5-mini at 78 single-hop with no memory layer at all).
6. **Pre-register** hypotheses, tuning space and prompts, commit, and record the hash in every receipt — this corpus is full of post-hoc best-cell reporting. Then **re-derive one published number** end-to-end (GBrain's 93.40% reranker-off `recall_all@5` has committed receipts). If it fails, stop; the harness is wrong.
7. **▶ Then run Tier-0: ~$30, one afternoon.** Tuned hybrid vs curated default vs reranker-off on MemConflict's **804 static + conditional** questions — where newest-wins is *inverted or undefined*, MDD 5.7–7.4 pp, and nobody has run the file-and-git family. **If curation shows nothing here, the full ~$850 matrix is unlikely to rescue it.**
8. **Publish the failures.** gbrain-evals' credibility comes entirely from having done so.

### 7.2 A 2-week MVP, in your own stack

You already have the substrate: Neo4j + BGE-M3 (1024-d) + hybrid retrieval + citation linking. Nothing below requires GBrain.

**Week 1 — measure, build nothing (~$30, 5 days).**
- **Day 1 — the as-of filter.** This is your single biggest available win and it is not biological. Extract the as-of date from the query, hard-filter the retrieval space to provisions valid at that date, *before* ranking. Baseline vs filtered on 100 historically anchored questions. The published effect is **35.40% → 81.42%**.
- **Day 2 — the LOTO test.** Delete from your eval questions only the phrases they literally share with your citation-extraction rules, and re-score. If your numbers collapse, they were a tautology check, exactly as GBrain's router did (100.0% → 0.0%).
- **Day 3 — the free-baseline ladder.** Score `1 − max cosine` from one ANN probe against whatever dedup or novelty heuristic you were considering. It scores 0.843 on paraphrase-shaped edits.
- **Day 4 — the graph ablation, one switch.** Shared index, shared query vectors, graph traversal on/off, on *relationship* questions only (case-cites-case, statute-amends-statute). Expect **+6 R@5**, not +31.
- **Day 5 — Tier-0 on your own corpus.** 200 questions, blind-graded, with an **abstention stratum** — an eval without abstention items flatters every system that confabulates fluently.

**Week 2 — ship the four things that are free wins (~5 days).**
- `binary_quantize`-equivalent quantization on your 1024-d BGE-M3 vectors: **22.5× storage, 1.9× faster, 0.9918 recall@10** with rescore. Measured on exactly your embedding model and dimension.
- **SQL:2011-style `WITHOUT OVERLAPS`** (or a `CHECK (valid_until > valid_from)` plus a partial exclusion constraint) on `(source, entity, dimension)`. Make two contradictory live facts a **write error**, at the one moment the evidence for arbitrating it is still in context. The value is in the *constraint*, not the timestamps — everyone stores those and nobody enforces them.
- **`corpus_defects`** — one table, one join, stamped on any retrieval that intersects a known ingest defect.
- **Human-gate merges, automate splits.** Your citation-linker's entity merges are the operation models are measurably worst at.

**What not to build:** per-document ACLs, a policy engine, group hierarchies, FlyHash anything. At your scale these are maintenance sinks. The tripwire that says build the real thing is the day your excluded-source list starts blocking work people legitimately need.

---

## 8. Corrections & caveats

Every claim below was refuted or downgraded by the verification round. Cite the corrected form.

| Claim | Corrected |
|---|---|
| **"+31.4 P@5 proves brain > RAG"** | Superseded April-2026 whole-adapter gap on a 240-page Opus-written corpus; receipts lost (`disclosed-gap`); re-measured at **+15.0**; clean one-switch A/B is **+6.2 R@5 / +9.7 first-place-hit**. Fusion is neutral vs pure vector; the reranker gives +2.1 |
| **"400X output, 8X at the floor"** | Self-measured, method undisclosed, inconsistent with his own public numbers (5,600 vs 37,000 lines/day). METR's RCT found early-2025 AI made experienced devs **19% slower**; its 2026 survey found a median self-reported **1.4–2× value gain**. The "8X floor" is a mis-derivation of the source doc's own explicitly *"impossible"* 100× row |
| **"94 companies crossed $100M from a seed check"** | Zero hits across all 2,681 posts in YC's blog index; unit undefined; **Tan dropped the sentence** at Startup School three weeks later |
| **"Fastest-growing, most profitable batch in YC history"** | Use Tan's own August wording: *"on track to becoming one of the fastest growing, most profitable batches."* The "25% of W25 at 95% AI-generated code" stat **does** survive |
| **"That revenue per head did not exist before"** | False. Retell's $1.2–1.5M/employee is below Google, Meta, Apple and Netflix, and an order of magnitude below Craigslist (~$13.9M) and Aramco (~$6M). What is new is the **velocity**, not the level |
| **"7±2, which is why phone numbers are seven digits"** | Miller 1956 is real; the phone-number gloss is a **documented myth** |
| **"220,000 pages vs 155,795"** | The README read **146,646** on the day of the talk (+50% gap); 155,795 landed 2026-08-12. A "page" is a **database row** of arbitrary length; the talk's other use of "page" is ~7× smaller. 28,256 and 17,888 are not comparable measurements |
| **MaleCNS "published 3 Sep, online 15 Aug"** | No ahead-of-print record exists. **One date: 3 Sep 2026.** Use 166,700 / 11,710 / 124.2M — not the preprint's 166,691 / 11,691, which Janelia's own project page still displays |
| **BANC "14 Jun 2026, ~188,000 neurons, 199M synapses"** | **8 Jun 2026**; **155,916** proofread neurons; **218,460,852** detected links. 188,508 is a metadata **row count** including glia and unproofread fragments. No BANC-vs-MaleCNS contradiction |
| **"25-phase dream cycle, 20 doctor checks, `lsd` is librarian machinery"** | **23** phases; **117** check names in 20 files; `lsd` is **generative** — it adds ideas, it does not prune |
| **YC RFS "demands provenance and contradiction detection"; RFS is a dead anchor** | The 220-word RFS (2026-04-28) mentions **neither** — those requirements are a third-party Modelence build brief. The entry is **live** |
| **"DoorDash's Team OS"** | One PM's personal write-up with a fictional example repo and an explicit disclaimer — not a company deployment. Ramp Glass/Dojo **is** confirmed; render it as "over 350 skills **shared**" (a flow, not an inventory) |
| **"22 memory systems ≤7% multi-hop; arbitration is a database problem"** | 22 **rows** including 6 long-context LLMs and 5 plain retrievers; best *memory system* (HippoRAG-v2) 54% vs GPT-4o long context 60%. `max(serial)` is worth **+2.0 pp pooled, 0.0 pp at 262K**; LongMemEval transfer is a **null** (p=0.45) |
| **"FlyHash loses to dense embeddings (H3D 0.13 vs 0.34)"** | H3D's "FlyHash" is a 128-bit **dimensionality-reducing** projection over 3-shingle counts, never applied to embeddings, on a **topical-relevance** task — and the weakest of five lexical hashes. At **equal hash length** FlyHash beats random-hyperplane LSH by **+82% relative**; the *Science* 2017 result replicates |
| **"FlyHash as a write-side dedup gate"** | Dedup half **refuted**; only the fly Bloom filter novelty/staleness clock survives |
| **"FlyPrompt = sparse-expansion router"** | REAR is a **dense** Gaussian random-feature expansion + ridge regression. Recommend FlyGCL on engineering merit only, never on lineage |
| **"OpenClaw/Hermes are the two most-starred repos in GitHub history"** | Counts accurate; they rank **#6 and #19**. Inflation is category-wide (`deepseek-harness`: 217,328 stars in a month). Argue adoption from releases, forks and issues — never stars. At 29,764★ gbrain is *small* here; `claude-mem` holds 3.1× more while scoring zero on every lifecycle feature |
| **"$100/month for a 25-person company"** | **Right answer, wrong arithmetic.** The ceiling holds for GBrain's own AI spend up to ~10 new pages/person/day. But "$40/mo embeddings" implies 694,444 new pages/month (real: $0.03–$0.63); the nightly cycle is omitted; "plus your hosting bill" hides **$135/mo**; the consuming agent loop is excluded (~$700/mo for one power user). All-in ≈ **$225/month** |
| **"OWASP T1 memory poisoning"** | **ASI06 Memory & Context Poisoning** |
| Assorted | 2.40 chunks/page measured (not 3–5); 373,908 chunks at 1024 dims; GBrain is **uni-temporal with an audit stamp**, not bi-temporal (git is its real transaction-time axis); the `b01-gbrain-*` repos are astroturf; *"MemFly, arXiv:2602.09871"* is fabricated |

**Caveats on this document.** The human librarian's labour cost (~2.5–3 h/week ⇒ $800–1,950/month, 8–20× the entire "$100/month" budget) is **inference from adjacent quantities, not a measurement** — it is the weakest number here, and it is a genuine void: no operator account anywhere quantifies it. The `220,000 → 146,646` gap may be a federated-scope artefact rather than an inflated stage figure (~35% confidence). Several workers exhausted their WebSearch budget, so non-GitHub venues were not swept. And the verification round's own best worked example is itself the answer to question (a): **five numbers for BANC's neuron count (155,916 / 158,262 / ~160,000 / 171,512 / 188,508) are all correct, all attach to the same paper, and differ only by predicate.** No amount of retrieval quality could have arbitrated them. A company brain that stores *"BANC has N neurons"* without storing the predicate has already lost.

---

## 9. Sources

**The talk and its ecosystem**
[youtube.com/watch?v=eBUyTS7SzV4](https://www.youtube.com/watch?v=eBUyTS7SzV4) · [ai.engineer/speakers/garry-tan](https://ai.engineer/speakers/garry-tan) · [ycombinator.com/rfs#company-brain](https://www.ycombinator.com/rfs#company-brain) · [techcrunch.com/2025/03/06/…ai-generated](https://techcrunch.com/2025/03/06/a-quarter-of-startups-in-ycs-current-cohort-have-codebases-that-are-almost-entirely-ai-generated) · [cnbc.com/2025/03/15/…](https://www.cnbc.com/2025/03/15/y-combinator-startups-are-fastest-growing-in-fund-history-because-of-ai.html) · [sacra.com/research/retell-ai-60m-yr-up-650-yoy](https://sacra.com/research/retell-ai-60m-yr-up-650-yoy/) · [metr.org/blog/2025-07-10-…](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) · [metr.org/blog/2026-05-11-ai-usage-survey](https://metr.org/blog/2026-05-11-ai-usage-survey/) · [psychclassics.yorku.ca/Miller](https://psychclassics.yorku.ca/Miller/)

**GBrain**
[github.com/garrytan/gbrain](https://github.com/garrytan/gbrain) (README, `docs/contradictions.md`, `docs/guides/compiled-truth.md`, `docs/guides/source-attribution.md`, `docs/tutorials/company-brain.md`, `skills/_brain-filing-rules.md`, `skills/skillify/SKILL.md`, `src/schema.sql`, `src/core/import-file.ts`, `src/core/cycle/phases/consolidate.ts`, `src/core/facts/decay.ts`, `src/core/routing-eval.ts` — all read at commit `43597b19`, v0.48.5.0) · issues [#3042](https://github.com/garrytan/gbrain/issues/3042) [#3269](https://github.com/garrytan/gbrain/issues/3269) [#3824](https://github.com/garrytan/gbrain/issues/3824) [#3889](https://github.com/garrytan/gbrain/issues/3889) [#4622](https://github.com/garrytan/gbrain/issues/4622) · [github.com/garrytan/gbrain-evals](https://github.com/garrytan/gbrain-evals) · [github.com/garrytan/gstack](https://github.com/garrytan/gstack)

**Fruit-fly primary literature**
Berg et al., *Cell* 189(18):5504–5526.e15 — [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015) · Bates, Phelps, Kim, Yang et al., *Nature* 656:957–970 — [doi:10.1038/s41586-026-10735-w](https://doi.org/10.1038/s41586-026-10735-w) · Dasgupta, Stevens & Navlakha, *Science* 358:793 — [doi:10.1126/science.aam9868](https://doi.org/10.1126/science.aam9868) · Dasgupta, Sheehan, Stevens & Navlakha, *PNAS* 115(51):13093 — [doi:10.1073/pnas.1814448115](https://doi.org/10.1073/pnas.1814448115) · Huang et al., *Nature* 634:1141 — [doi:10.1038/s41586-024-07819-w](https://doi.org/10.1038/s41586-024-07819-w) · Hattori et al., *Cell* 169:956 — [doi:10.1016/j.cell.2017.04.028](https://doi.org/10.1016/j.cell.2017.04.028) · Lin et al., *Nat. Neurosci.* 17:559 — [doi:10.1038/nn.3660](https://doi.org/10.1038/nn.3660) · Litwin-Kumar et al., *Neuron* 93:1153 — [doi:10.1016/j.neuron.2017.01.030](https://doi.org/10.1016/j.neuron.2017.01.030) · Felsenberg et al., *Cell* 175:709 — [doi:10.1016/j.cell.2018.08.021](https://doi.org/10.1016/j.cell.2018.08.021) · [male-cns.janelia.org](https://male-cns.janelia.org/) · [research.google/blog/a-connectomics-milestone…](https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/) · [codex.flywire.ai/banc](https://codex.flywire.ai/banc)

**Fly-inspired and negative results**
[arXiv:2607.08382](https://arxiv.org/abs/2607.08382) (H3D) · [arXiv:2602.01976](https://arxiv.org/abs/2602.01976) (FlyPrompt) · [arXiv:2307.02251](https://arxiv.org/abs/2307.02251) (RanPAC) · [arXiv:2604.04033](https://arxiv.org/abs/2604.04033) (degree-preserving null) · [arXiv:2509.19351](https://arxiv.org/abs/2509.19351) (pruning degrades KC classification) · [arXiv:2511.05542](https://arxiv.org/abs/2511.05542) (ConnectomeBench) · [doi:10.1088/2634-4386/ae9177](https://doi.org/10.1088/2634-4386/ae9177) (Spi-Fly) · [arXiv:2001.04907](https://arxiv.org/abs/2001.04907) (BioHash)

**Memory, RAG and benchmarks**
[arXiv:2312.10997](https://arxiv.org/abs/2312.10997) · [arXiv:2404.16130](https://arxiv.org/abs/2404.16130) · [arXiv:2410.05779](https://arxiv.org/abs/2410.05779) · [arXiv:2502.14802](https://arxiv.org/abs/2502.14802) · [arXiv:2501.09136](https://arxiv.org/abs/2501.09136) · [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) · [arXiv:2501.13956](https://arxiv.org/abs/2501.13956) · [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) · [arXiv:2505.22101](https://arxiv.org/abs/2505.22101) · [arXiv:2504.13171](https://arxiv.org/abs/2504.13171) · [arXiv:2605.30771](https://arxiv.org/abs/2605.30771) · [arXiv:2410.10813](https://arxiv.org/abs/2410.10813) · [arXiv:2507.05257](https://arxiv.org/abs/2507.05257) · [arXiv:2605.20926](https://arxiv.org/abs/2605.20926) · [arXiv:2606.26511](https://arxiv.org/abs/2606.26511) · [arXiv:2606.27472](https://arxiv.org/abs/2606.27472) · [arXiv:2605.17301](https://arxiv.org/abs/2605.17301) · [arXiv:2605.23497](https://arxiv.org/abs/2605.23497) · [arXiv:2412.18004](https://arxiv.org/abs/2412.18004) · [arXiv:2503.03704](https://arxiv.org/abs/2503.03704) · [arXiv:2605.23904](https://arxiv.org/abs/2605.23904) · [arXiv:2602.12430](https://arxiv.org/abs/2602.12430) · [arXiv:2505.03275](https://arxiv.org/abs/2505.03275) · [arXiv:2606.29914](https://arxiv.org/abs/2606.29914) · [arXiv:2511.10523](https://arxiv.org/abs/2511.10523)

**Standards, prior art, infrastructure**
[w3.org/TR/prov-dm](https://www.w3.org/TR/prov-dm/) · SQL:2011 temporal (Kulkarni & Michels, SIGMOD Record 41(3)) · CCSDS 650.0-M-2 (OAIS) · [doi:10.1145/3149371](https://doi.org/10.1145/3149371) (TinyLFU) · [doi:10.1038/s41592-024-02426-z](https://doi.org/10.1038/s41592-024-02426-z) (CAVE) · [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) · [github.com/onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx) (permission mirroring, `backend/ee/`)

**Projects**
[github.com/getzep/graphiti](https://github.com/getzep/graphiti) · [github.com/letta-ai/letta](https://github.com/letta-ai/letta) · [github.com/topoteretes/cognee](https://github.com/topoteretes/cognee) · [github.com/MemTensor/MemOS](https://github.com/MemTensor/MemOS) · [github.com/mem0ai/mem0](https://github.com/mem0ai/mem0) · [github.com/agno-agi/scout](https://github.com/agno-agi/scout) · [github.com/TaoZhen1110/MemConflict](https://github.com/TaoZhen1110/MemConflict) · [github.com/xiaowu0162/LongMemEval](https://github.com/xiaowu0162/LongMemEval) · [github.com/huytieu/COG-second-brain](https://github.com/huytieu/COG-second-brain) · [github.com/teolex2020/aura-memory](https://github.com/teolex2020/aura-memory) · [github.com/CAVEconnectome/CAVEclient](https://github.com/CAVEconnectome/CAVEclient) · [github.com/tfatykhov/awesome-agent-memory](https://github.com/tfatykhov/awesome-agent-memory)

**Internal**
`findings/v01`–`v11` (verification) · `findings/g01`–`g07` (gap-fill) · `findings/d1`–`d5` (designs) · `findings/j1`–`j3` (judges) · `checkpoints/02-verify-design-decisions.md` · `ERRATA.md`

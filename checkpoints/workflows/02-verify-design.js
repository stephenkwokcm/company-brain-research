export const meta = {
  name: 'company-brain-verify-design',
  description: 'Verify 10 load-bearing claims, fill 7 gaps, then 5-angle design panel + judges + synthesis draft for company-brain x fruit-fly',
  phases: [
    { title: 'Verify', detail: 'adversarial verification of critic claims', model: 'opus' },
    { title: 'Gaps', detail: 'gap-fill research', model: 'opus' },
    { title: 'Design', detail: '5 independent design proposals', model: 'opus' },
    { title: 'Judge', detail: '3 judges score designs', model: 'opus' },
    { title: 'Synthesis', detail: 'draft SYNTHESIS.md', model: 'opus' },
  ],
}

const DIR = '/Users/stephen/Cookies/company-brain-research'
const TODAY = '2026-09-10'

const PREAMBLE = `You are a research worker (Claude Opus 5) in a multi-agent research project. Today is ${TODAY}.
Research folder: ${DIR}
  - ${DIR}/checkpoints/01-sweep-decisions.md   (orchestrator decisions so far — READ FIRST)
  - ${DIR}/checkpoints/00-plan.md               (talk summary)
  - ${DIR}/findings/*.md                        (15 prior reports incl. completeness-critic.md; read the ones relevant to you)
  - ${DIR}/sources/transcript_eBUyTS7SzV4.txt  (talk transcript)
Context: Garry Tan (YC) talk "Every company should have a Brain" (AI Engineer, 2026-07-16). User asks (a) is a company brain RAG,
(b) can it be combined with recently published fruit-fly brain work, (c) what projects build on these ideas.
Tools: load WebSearch/WebFetch via ToolSearch; use Bash curl to raw.githubusercontent.com / gh api / arxiv.org/abs for primary sources.
Rules: primary sources only for verdicts; record exact URLs; never fabricate; if unresolvable, say so and give best estimate with confidence.
Write your full report to the path named in your task (markdown, sources list at end), AND return the structured summary.`

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', description: 'CONFIRMED | REFUTED | PARTIALLY | UNRESOLVED' },
    one_sentence: { type: 'string', description: 'the corrected, citable one-sentence statement of the truth' },
    evidence: { type: 'array', items: { type: 'object', properties: { fact: { type: 'string' }, source_url: { type: 'string' } }, required: ['fact', 'source_url'] } },
    implications: { type: 'string', description: 'what this changes for the final answer' },
    report_path: { type: 'string' },
  },
  required: ['verdict', 'one_sentence', 'evidence', 'implications', 'report_path'],
}

const SUMMARY_SCHEMA = {
  type: 'object',
  properties: {
    key_insights: { type: 'array', items: { type: 'string' } },
    key_facts: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source_url: { type: 'string' }, confidence: { type: 'string' } }, required: ['claim', 'source_url', 'confidence'] } },
    recommendation: { type: 'string' },
    report_path: { type: 'string' },
  },
  required: ['key_insights', 'key_facts', 'recommendation', 'report_path'],
}

const VERIFY = [
  { key: 'v01-gbrain-benchmarks', lens: 'reconcile', prompt: `Claim to adjudicate: GBrain's README states BOTH "+31.4 points P@5 over vector-only" AND "hybrid layer is roughly neutral" (pure vector 93.8% on LongMemEval-S). Fetch the current README (raw.githubusercontent.com/garrytan/gbrain/master/README.md) and gbrain-evals README, plus any benchmark receipts in the repo (search for BrainBench, recall_all@5, P@5, LongMemEval). For each number record: corpus, corpus origin (LLM-generated?), size, metric definition, GBrain version, date. Produce ONE fair sentence stating what the graph/hybrid layer buys and on what. Also determine whether ANY third party has reproduced either number.` },
  { key: 'v02-malecns-date', lens: 'primary-source', prompt: `Claim: the complete male Drosophila CNS connectome (Janelia FlyEM + Google Research + MRC LMB) was published in Cell on 3 September 2026 (online 15 Aug). Google's blog says "published August 2026". Find the Cell paper itself (cell.com DOI page), record: exact title, authors (first/last), DOI, "published online" date, issue date, neuron count, synapse/connection count, cell-type count, license/data URL. Also record dates of the news coverage and of the earliest hobbyist "DOOM on a fly brain" style repos (GitHub created_at via gh api). Decide: is "recently published" (as of ${TODAY}) a fair description, and which date should the synthesis cite.` },
  { key: 'v03-banc-facts', lens: 'primary-source', prompt: `Claim: BANC brain-and-nerve-cord connectome, Nature, June 2026 — reports disagree: 8 vs 14 June 2026; 158,262 vs ~160,000 vs ~188,000 neurons; 199M synapses; "female". Find the Nature paper (nature.com DOI), and record title, authors, DOI, publication date, exact neuron/synapse counts from the abstract, sex of specimen, key finding about distributed vs centralized control. Reconcile with Google's claim that the 166,700-neuron male CNS is "the largest brain map by neuron count" (scope difference?).` },
  { key: 'v04-yc-94-companies', lens: 'primary-source', prompt: `Claim (talk 03:37): "94 companies total have now crossed a hundred million in dollars in revenue from a seed check in the history of YC" and "Winter 25 ... fastest-growing, most profitable batch in the history of YC". Search YC's own site, Garry Tan's X posts, YC's 2026 annual letters/press, Startup School Aug 2026 talk transcripts, for the 94 figure and its unit (revenue / ARR / run-rate). Also verify Tan's public "37,000 lines per day" or similar LOC claims and the 400X derivation (gstack/docs/ON_THE_LOC_CONTROVERSY.md). Verdict per claim.` },
  { key: 'v05-gbrain-page-counts', lens: 'reconcile', prompt: `Claim: GBrain's brain size is reported as ~220,000 pages (talk 13:47), 155,795 (README), ~96,000 (calibration spec), 28,256 (2026-05-10 takes receipt), 17,888 (docs/ethos/ORIGIN.md). Read each source in the repo (use gh api / raw files; grep the repo tree for these numbers) and determine what unit each counts (pages, files, chunks, facts, entities) and the date. Produce a dated table and a one-sentence recommendation on how the synthesis should cite brain size.` },
  { key: 'v06a-librarian-in-code', lens: 'code-reader', prompt: `Three-way disagreement: does GBrain implement the "librarian" (talk 12:54, 14:58: human+agent whose job is pruning)? Read src/core/cycle.ts (dream cycle phases), doctor checks, quarantine lane, gbrain lsd, forget/TTL code, and any docs on the dream cycle (docs/*.md). List each phase with what it deletes/merges/demotes and whether it acts automatically or only emits suggestions. Adjudicate: is pruning automated, advisory, or delegated to the human? Give the precise sentence the synthesis should use.` },
  { key: 'v06b-librarian-skeptic', lens: 'skeptic', prompt: `Adversarial: the gbrain-architecture report claims "the librarian is concrete: a 25-phase nightly dream cycle, 20 doctor checks, quarantine lane, gbrain lsd". Try to REFUTE that this constitutes Tan's librarian ("whose actual job is pruning"). Check: does anything actually delete or demote content automatically? Are contradiction findings auto-resolved or only emitted? Read the GitHub issues list (gh api repos/garrytan/gbrain/issues?state=all&per_page=100, search titles for dream, prune, stale, contradiction, forget) for evidence the hygiene machinery fails silently. Default to refuted=partially if uncertain.` },
  { key: 'v07-yc-rfs-text', lens: 'primary-source', prompt: `Claim: YC published a Summer 2026 "Company Brain" Request for Startups authored by Tom Blomfield demanding provenance metadata and contradiction detection. Find the verbatim text: ycombinator.com/rfs (live), Wayback Machine snapshots (web.archive.org/web/2026*/ycombinator.com/rfs*), YC blog, Tom Blomfield's X posts. Quote the RFS verbatim (or the closest verified excerpt) with URL and date. Verdict on whether the provenance/contradiction requirements are really in the brief.` },
  { key: 'v08-ramp-doordash-cases', lens: 'primary-source', prompt: `Claim: Ramp's internal "Glass" (350+ skills, "Dojo" marketplace) and DoorDash's "Team OS" are real enterprise examples of the skills-as-workforce / company-brain pattern, currently resting on a single secondary blog post. Find primary sources (Ramp engineering blog, DoorDash engineering blog, talks, X posts by employees, press). Verify names, numbers, dates. Also find 2-3 additional primary-sourced enterprise case studies of a skills library + org memory layer (any company, 2025-2026). Verdict per case.` },
  { key: 'v09a-memoryagentbench', lens: 'paper-reader', prompt: `Claim: on MemoryAgentBench "FactConsolidation", all 22 published memory systems score at most 7% multi-hop and the best (HippoRAG-v2) 54% single-hop, while a deterministic Python max(serial) over BM25 hits 82-93% single-hop. Find the MemoryAgentBench paper(s) (arXiv; there may be a 2025 original and a 2026 update/leaderboard), read the FactConsolidation task definition and result tables (fetch the PDF/HTML), and verify every number, the exact list/count of systems, and what "max(serial)" is. State what the task actually tests (versioned fact updates?) and whether it fairly supports "arbitration is a database problem".` },
  { key: 'v09b-memoryagentbench-skeptic', lens: 'skeptic', prompt: `Adversarial: try to REFUTE the inference "contradiction arbitration belongs in deterministic code, not an LLM judge" drawn from MemoryAgentBench FactConsolidation (deterministic max(serial) 82-93% vs all memory systems <=54%). Consider: is the task synthetic with an explicit serial number (so trivially solvable by code but unrepresentative of real org knowledge)? Do real company facts carry a reliable ordering key? Find counter-evidence (e.g., MemConflict arXiv:2605.20926, ConflictRAG, knowledge-conflict surveys) on how well deterministic supersession works when timestamps are missing/ambiguous. Give a balanced verdict and the caveated sentence the synthesis should use.` },
  { key: 'v10a-h3d-flyhash', lens: 'paper-reader', prompt: `Claim: the H3D benchmark (arXiv:2607.08382, July 2026) puts FlyHash at 0.1325 MAP on CSFCube vs 0.3431 for frozen BGE-large, and 0.4305 vs 0.6626 on RELISH. Fetch the paper (arxiv abs + HTML/PDF), verify the numbers, the task (dedup? retrieval?), the FlyHash configuration (dimension, hash length, input features — raw text? TF-IDF? embeddings?), and whether FlyHash was applied on top of dense embeddings or on sparse lexical input. Determine what the fair conclusion is about FlyHash for semantic retrieval vs for near-duplicate detection.` },
  { key: 'v10b-flyhash-vs-modern', lens: 'comparator', prompt: `Adversarial comparison the critic demanded: FlyHash-as-index is pitched into a slot already occupied by (1) HNSW/DiskANN over dense embeddings, (2) learned sparse retrieval (SPLADE, uniCOIL, BM42), (3) binary/int8 quantization of dense embeddings with rescoring (~96% retrieval retained, 32x memory). Find benchmark numbers for each on standard IR sets (BEIR/MTEB) and memory/latency figures. Then construct the fairest possible case FOR FlyHash (data-independent, streaming, no training, novelty score, cheap) and AGAINST. Verdict: in what exact role (index / quantizer / dedup gate / novelty gate / none) does fly-inspired hashing have a defensible advantage in a 100K-1M page company brain?` },
  { key: 'v11-star-count-sanity', lens: 'data-check', prompt: `Sanity-check ecosystem numbers reported by earlier workers via gh api (repos/<owner>/<name>: stargazers_count, created_at, pushed_at): openclaw (Peter Steinberger's harness; find the real owner/repo, reported 389,291 stars), Nous Research Hermes agent (reported 243,757), garrytan/gbrain (29,763), garrytan/gstack (132,245), garrytan/gbrain-evals (419), and the five "b01-gbrain-*" repos flagged as possible astroturf (find them via gh search repos b01-gbrain). For the astroturf candidates fetch stargazer timelines (gh api repos/X/stargazers -H "Accept: application/vnd.github.star+json" --paginate | head) and check for burst patterns. Also confirm Peter Steinberger joined OpenAI on 2026-02-14 and OpenClaw moved to a foundation. Verdict per number.` },
]

const GAPS = [
  { key: 'g01-bitemporal-prior-art', prompt: `Gap: three reports recommend "bi-temporal invalidation with a deterministic conflict policy" as intervention #1 for contradiction arbitration, with zero database citations. Survey the prior art: Snodgrass/TSQL2, SQL:2011 system-versioned temporal tables (MariaDB, SQL Server, Db2, Postgres periods extension), Datomic, XTDB (bitemporal), Dolt, Zep/Graphiti's valid_at/invalid_at edges, TOKI. Explain valid-time vs transaction-time, and show concretely how a company-brain "facts" table would model supersession vs contradiction vs debate. Give a Postgres DDL sketch and the query for "what did we believe on date D". Assess GBrain's current facts/takes/valid_until schema against it. Report: ${DIR}/findings/g01-bitemporal-prior-art.md` },
  { key: 'g02-sizing-cost', prompt: `Gap: nobody sized or costed anything. Do the arithmetic for a company brain at 155,795 pages (GBrain README) and at 1M pages: chunks (assume 3-5 per page), embedding dims (768/1024/1536/3072), pgvector HNSW index RAM/disk, build time, query latency, embedding cost, nightly dream-cycle LLM cost (use GBrain's published judge cost model if present in repo docs; else public Claude/OpenAI pricing as of 2026 — fetch current prices), contradiction-probe sampling cost. Verify Tan's "under $100/month for a 25-person company" claim against the repo docs. Then answer: is the ANN index the bottleneck at this scale (if not, FlyHash-as-index is dead on arithmetic)? What is the human librarian's labour cost per week from any published operator accounts? Report: ${DIR}/findings/g02-sizing-cost.md` },
  { key: 'g03-enterprise-incumbents', prompt: `Gap: "this is enterprise knowledge management renamed" is unanswered. Compare the company-brain thesis against incumbents: Glean, Onyx (ex-Danswer), Dust, Coda Brain / Grammarly, Notion AI Q&A, Microsoft 365 Copilot + Graph, Atlassian Rovo, Guru, Slite, plus 2026 entrants. For each: architecture (connectors + hybrid search + permissions), do they do write-side curation, provenance, contradiction detection, hot/cold, procedural memory/skills, agent-facing API/MCP? Build a table. Conclude what a company brain (GBrain-style, markdown+git system of record, agent-written, skills) actually adds vs Glean-class products, and what it lacks (governance, ACL). Report: ${DIR}/findings/g03-enterprise-incumbents.md` },
  { key: 'g04-librarian-library-science', prompt: `Gap: "librarian" is the load-bearing half of Tan's definition and is defined three incompatible ways. Bring in library/archival science: appraisal theory (Schellenberg, macro-appraisal), provenance principle / respect des fonds, deaccessioning/weeding policies (CREW/MUSTIE), authority control, collection development policies, records retention schedules, FRBR/RDA. Map each to a company-brain operation (ingest gate, filing rules, back-linking, hot/cold promotion, pruning, contradiction arbitration, entity canonicalisation). Produce a concrete "Librarian spec": roles (human vs agent), weekly cadence, decision rules with thresholds, metrics. Compare with what GBrain's dream cycle actually automates (read findings/gbrain-architecture.md). Report: ${DIR}/findings/g04-librarian-spec.md` },
  { key: 'g05-governance-acl', prompt: `Gap: the "company" half is uncovered. Research permission-aware retrieval (document-level ACL filtering in vector DBs, Glean-style permission mirroring, row-level security in Postgres/pgvector), multi-tenancy for agent memory, retention schedules, GDPR/right-to-erasure vs GBrain's forget-as-markdown-fence-rewrite + git history (is a git-backed brain erasable at all?), audit logs, memory poisoning defences (MINJA, OWASP agentic top-10) and what GBrain's observe-only guardrails imply. Recommend a minimal governance layer for a 25-person company brain. Report: ${DIR}/findings/g05-governance-acl.md` },
  { key: 'g06-crux-experiment', prompt: `Gap: four reports name the crux experiment (does curation beat a tuned BM25+vector baseline on real org questions?) and none specifies a runnable protocol. Write one: datasets (LongMemEval-S, MemConflict arXiv:2605.20926, MemoryAgentBench FactConsolidation, gbrain-evals BrainBench, and a real-org option using the user's own repos e.g. an Obsidian/markdown vault), systems (GBrain default; GBrain graph-off; GBrain + FlyHash novelty gate; Mem0; Zep/Graphiti; Letta MemFS; plain BM25+dense hybrid with rerank; full-context), metrics (recall_all@k, answer accuracy, knowledge-update accuracy, CARS-style hygiene score, cost/tokens, ingest-time), controls (same embedder/LLM/k), sample sizes and CIs, and a pre-registered decision rule. Include exact commands where repos are public (fetch READMEs to get real CLI). Report: ${DIR}/findings/g06-crux-experiment.md` },
  { key: 'g07-neuro-mechanism-inventory', prompt: `Gap-fill for the design phase: produce a precise, sourced inventory of every fly-brain mechanism the prior reports proposed transplanting, each as a one-paragraph algorithm with inputs/outputs/parameters and its best open implementation: (1) FlyHash sparse random expansion + WTA LSH; (2) fly Bloom filter novelty score with additive-increase/multiplicative-decay; (3) mushroom-body compartment consolidation gamma→alpha (Huang 2024) as readout-gated promotion; (4) Gkanias 2022 incentive circuit (susceptible/restrained/LTM MBONs; discharging/charging/forgetting DANs); (5) active forgetting (DAMB/Rac1) with sleep suppression; (6) extinction-as-accumulation netting at readout (Felsenberg 2018); (7) FlyPrompt sparse-expansion router (ICLR 2026, github AnAppleCore/FlyGCL); (8) connectome_interpreter effective-connectivity path compression; (9) Spi-Fly continual learning (Aug 2026); (10) Kanerva SDM as attention. For each: cite primary source, note any negative results, and rate transplant fidelity (deep/analogy/superficial). Report: ${DIR}/findings/g07-neuro-mechanism-inventory.md` },
]

phase('Verify')
log(`Verify: ${VERIFY.length} agents; Gaps: ${GAPS.length} agents — running concurrently`)
const verifyP = parallel(VERIFY.map(v => () =>
  agent(`${PREAMBLE}\n\n=== VERIFICATION TASK (lens: ${v.lens}) ===\nKey: ${v.key}\n${v.prompt}\nWrite report to ${DIR}/findings/${v.key}.md`, { label: `verify:${v.key}`, phase: 'Verify', model: 'opus', schema: VERDICT_SCHEMA })
    .then(r => r ? { key: v.key, ...r } : null)))
const gapsP = parallel(GAPS.map(g => () =>
  agent(`${PREAMBLE}\n\n=== GAP-FILL TASK ===\nKey: ${g.key}\n${g.prompt}`, { label: `gap:${g.key}`, phase: 'Gaps', model: 'opus', schema: SUMMARY_SCHEMA })
    .then(r => r ? { key: g.key, ...r } : null)))
const [verifyRaw, gapsRaw] = await Promise.all([verifyP, gapsP])
const verify = verifyRaw.filter(Boolean)
const gaps = gapsRaw.filter(Boolean)
log(`Verify done ${verify.length}/${VERIFY.length}; gaps done ${gaps.length}/${GAPS.length}`)

const verdictDigest = verify.map(v => `- [${v.key}] ${v.verdict}: ${v.one_sentence} (implication: ${v.implications})`).join('\n')
const gapDigest = gaps.map(g => `- [${g.key}] ${g.recommendation}\n  insights: ${g.key_insights.slice(0, 5).join(' | ')}`).join('\n')

phase('Design')
const DESIGN_PREAMBLE = `${PREAMBLE}

=== DESIGN TASK ===
You are one of five independent designers. Produce a BUILDABLE proposal for applying fruit-fly-brain work to a company brain (GBrain-style: git markdown system of record, Postgres/pgvector derived index, facts→takes hot/cold tables with per-kind decay half-lives, nightly dream cycle, RESOLVER.md skill routing, MEMORY_VERBS MCP protocol). Read findings/gbrain-architecture.md, findings/g07-neuro-mechanism-inventory.md, findings/g02-sizing-cost.md, and the fly reports first.
Verified facts and gap-fill results from this round:
${verdictDigest}
${gapDigest}

Your proposal MUST contain: (1) the mechanism borrowed and its fidelity (deep/analogy/superficial); (2) exact insertion point in GBrain (file/phase/table/config key, cite repo paths); (3) algorithm sketch with parameters; (4) benchmark + metric + baseline; (5) expected effect size with reasoning from published numbers; (6) cost (tokens/compute/engineering days); (7) kill criterion (pre-registered: what result means abandon); (8) risks and what prior negative results say; (9) a 2-week MVP plan. Also state honestly whether a non-biological alternative (SPLADE, binary quantization, vMF density gate, SQL:2011 bitemporal table, plain cron) does the same job better. Write to the report path and return the structured summary (recommendation = one-paragraph pitch).`

const DESIGNS = [
  { key: 'd1-write-gate', angle: 'WRITE-SIDE HYGIENE: FlyHash + fly Bloom filter as an ingest novelty/dedup/staleness gate in front of the facts table and the dream-cycle contradiction probe (cheap trigger for expensive LLM judging).' },
  { key: 'd2-lifecycle', angle: 'MEMORY LIFECYCLE: mushroom-body consolidation as the hot→cold promotion policy (readout-gated by retrieval/citation signals rather than scheduled), plus a separately parameterised forgetting daemon with a suppression window, plus extinction-as-accumulation for conflicting takes.' },
  { key: 'd3-router', angle: 'ROUTING: sparse-expansion / connectome-style stochastic router (FlyPrompt lineage) as the RESOLVER / skill-dispatch layer, targeting the skill-routing precision collapse at pools of 50-150 skills.' },
  { key: 'd4-index-adversary', angle: 'INDEX (adversarial): FlyHash/BioHash as a pluggable vector.backend vs pgvector HNSW / SPLADE / binary quantization. You are expected to reach an honest verdict, likely "do not build", with the arithmetic and benchmarks that prove it, and to say what (if anything) survives.' },
  { key: 'd5-curation-process', angle: 'PROCESS: the connectome projects (FlyWire/MaleCNS/BANC) as a reference architecture for company-brain curation — CAVE-style versioned annotations, per-fact confidence thresholds, human+AI proofreading as arbitration, cell-type ontology as entity canonicalisation, VFB MCP server as agent-facing library. Produce a concrete borrow-list with GBrain insertion points.' },
]
const designs = (await parallel(DESIGNS.map(d => () =>
  agent(`${DESIGN_PREAMBLE}\n\nYOUR ANGLE (key ${d.key}): ${d.angle}\nReport path: ${DIR}/findings/${d.key}.md`, { label: `design:${d.key}`, phase: 'Design', model: 'opus', schema: SUMMARY_SCHEMA })
    .then(r => r ? { key: d.key, angle: d.angle, ...r } : null)))).filter(Boolean)
log(`Designs done ${designs.length}/${DESIGNS.length}`)

phase('Judge')
const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    scores: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' }, feasibility: { type: 'number' }, expected_benefit: { type: 'number' }, evidence_quality: { type: 'number' }, novelty: { type: 'number' }, cost_efficiency: { type: 'number' }, total: { type: 'number' }, verdict: { type: 'string' }, rationale: { type: 'string' } },
      required: ['key', 'feasibility', 'expected_benefit', 'evidence_quality', 'novelty', 'cost_efficiency', 'total', 'verdict', 'rationale'] } },
    ranking: { type: 'array', items: { type: 'string' } },
    best_ideas_to_graft: { type: 'array', items: { type: 'string' } },
    report_path: { type: 'string' },
  },
  required: ['scores', 'ranking', 'best_ideas_to_graft', 'report_path'],
}
const JUDGE_LENSES = [
  { key: 'j1-rag-engineer', lens: 'a senior RAG/search engineer who has shipped hybrid retrieval at 10M-document scale and is allergic to biological metaphors that do not beat SPLADE or a cron job' },
  { key: 'j2-comp-neuro', lens: 'a computational neuroscientist who works on Drosophila mushroom-body models and will penalise any transplant that misrepresents the biology or ignores published negative results' },
  { key: 'j3-yc-founder', lens: 'a YC founder building a company-brain product with 2 engineers and 12 weeks of runway, who cares only about what ships and measurably improves answer quality or cuts cost' },
]
const judges = (await parallel(JUDGE_LENSES.map(j => () =>
  agent(`${PREAMBLE}\n\n=== JUDGE TASK ===\nKey: ${j.key}. Judge as: ${j.lens}.\nRead all five design reports: ${DESIGNS.map(d => `${DIR}/findings/${d.key}.md`).join(', ')} and findings/g07-neuro-mechanism-inventory.md, findings/g02-sizing-cost.md, findings/v10b-flyhash-vs-modern.md.\nScore each design 1-10 on feasibility, expected_benefit, evidence_quality, novelty (unclaimed ground), cost_efficiency; total = sum. Verdict per design: BUILD / PILOT / DEFER / KILL with a 2-3 sentence rationale that names specific numbers or sources. Rank them. List the best ideas to graft from lower-ranked designs into the winner. Write your scorecard to ${DIR}/findings/${j.key}.md and return it structured.`, { label: `judge:${j.key}`, phase: 'Judge', model: 'opus', schema: JUDGE_SCHEMA })
    .then(r => r ? { key: j.key, ...r } : null)))).filter(Boolean)

// aggregate scores in plain code
const agg = {}
for (const j of judges) for (const s of j.scores) { agg[s.key] = agg[s.key] || { total: 0, n: 0, verdicts: [] }; agg[s.key].total += s.total; agg[s.key].n++; agg[s.key].verdicts.push(`${j.key}:${s.verdict}`) }
const leaderboard = Object.entries(agg).map(([k, v]) => ({ key: k, mean: v.n ? v.total / v.n : 0, verdicts: v.verdicts })).sort((a, b) => b.mean - a.mean)
log(`Leaderboard: ${leaderboard.map(l => `${l.key}=${l.mean.toFixed(1)}`).join(', ')}`)

phase('Synthesis')
const synth = await agent(`${PREAMBLE}

=== SYNTHESIS DRAFT TASK ===
Key: synthesis-draft. Read EVERYTHING in ${DIR}/findings/ (all ~40 reports) and ${DIR}/checkpoints/01-sweep-decisions.md. Verification verdicts:
${verdictDigest}
Gap-fill recommendations:
${gapDigest}
Design leaderboard (mean of 3 judges, out of 50): ${JSON.stringify(leaderboard)}
Judges' graft suggestions: ${judges.flatMap(j => j.best_ideas_to_graft).join(' | ')}

Write ${DIR}/SYNTHESIS-draft.md: a decision document for the user (a developer who builds RAG systems, e.g. hk-law-rag, hk-gov-data-rag in the same parent folder). Sections:
1. TL;DR (max 8 bullets, each a decision or key insight).
2. What the talk actually says (with timestamps) — compact.
3. Is a company brain RAG? Precise answer with the read-side/write-side line, the reconciled GBrain benchmark sentence, and the strongest evidence for and against the "librarian" thesis. Include a table mapping Tan's 7 requirements → existing mechanisms/systems.
4. What "the fruit fly brain work" most likely is (ranked, with verified dates) and what it does and does not offer.
5. Combining them: the ranked designs with verdicts (BUILD/PILOT/DEFER/KILL), each with insertion point, expected effect, kill criterion; the honest statement of unclaimed ground vs unproven ground; the non-biological alternatives that do the same job.
6. Projects worth the user's attention (top 10 with URLs and one-line why), grouped.
7. Recommended next steps: the crux experiment protocol summary and a 2-week MVP.
8. Corrections & caveats: every claim the verify round refuted or downgraded (400X, revenue/head, 7±2, page counts, star counts...).
9. Sources: every URL cited, grouped.
Every number must carry a source URL. Prefer short sentences. 2500-4500 words. Return a structured summary with key_insights = the TL;DR bullets, recommendation = the single most important next step.`, { label: 'synthesis-draft', phase: 'Synthesis', model: 'opus', schema: SUMMARY_SCHEMA })

return { verify, gaps, designs: designs.map(d => ({ key: d.key, recommendation: d.recommendation, report_path: d.report_path })), judges: judges.map(j => ({ key: j.key, ranking: j.ranking, grafts: j.best_ideas_to_graft })), leaderboard, synth }
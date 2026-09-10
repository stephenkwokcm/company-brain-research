# Checkpoint 02 — after verify + gaps + designs (2026-09-10)

## Done
- Workflow 2 (wf_9ab6a640-268): 14 verifications (findings/v*.md), 7 gap fills (findings/g*.md), 5 designs (findings/d*.md) succeeded.
  3 judges + synthesis draft failed on a transient API outage; resumed (same run ID) — outputs findings/j1..j3-*.md, SYNTHESIS-draft.md.
- Raw structured returns: checkpoints/02-verify-design-results.json. Public repo: https://github.com/stephenkwokcm/company-brain-research
- ERRATA.md lists every claim in findings/*.md that the verify round corrected. Read it before citing any prior report.

## Orchestrator decisions (final unless judges overturn)

### (a) Is a company brain RAG?
- ANSWER: RAG is the read path. A company brain adds (1) write-side evidence production with human-gated mutation (provenance, hot/cold tiers,
  contradiction DETECTION), and (2) procedural memory (SKILL.md). Tan concedes retrieval is the primitive (talk 12:57; docs/ethos/ORIGIN.md).
  YC's own RFS text (2026-04-28) says the deliverable is "an executable skills file" and "isn't a company-wide search or a chatbot over documents".
- The one reconciled benchmark sentence (v01): the typed-edge graph adds +6.2 R@5 / +9.7 first-place-hit on 145 relational questions over a
  240-page Opus-written corpus (corrected whole-adapter gap +15.0 P@5; README still prints +31.4 and the receipts are lost); BM25+vector fusion is
  neutral-to-negative vs pure vector on LongMemEval-S (93.8 vs 93.2-93.4 strict recall_all@5); the cross-encoder reranker supplies the +2.1 that
  reaches 95.53. No answering model was in the loop and no third party has reproduced either number.
- The librarian does not exist in shipped code, anywhere (v06a/b, g04). GBrain automates the mechanical half (ingest triage, regex junk filter,
  cosine-0.85 cluster consolidation, salience, 50-page merge cap, 72h GC) and refuses semantic pruning by documented policy; the contradiction probe
  is a user-initiated advisory report. Library science splits Tan's word into collection management (nobody builds it) and reference service
  (everyone builds it). Best control law: CREW — weed at the acquisition rate. Evidence the gap matters: GBrain's own 32.5k-row unread review queue
  growing 2-6k/day (gbrain#3269); bounded self-managed memory scores 15 pts below full context on knowledge-update questions.
- Arbitration slogan (v09a/b, g01): "deterministic eligibility, model-side adjudication, human-side resolution." Code owns valid-time intervals,
  provenance, as-of filters and SQL:2011 `WITHOUT OVERLAPS`; the model classifies the disagreement type; a human resolves contested cases.
  Do NOT say "arbitration is a database problem" — MemoryAgentBench's own ablation refutes it (max(serial) worth +2 pp; extraction LLM does the work).
- "Enterprise KM renamed" is ~70% right (g03). The fork: incumbents are an index over sources; a brain is a new writable system of record. That is why
  contradiction arbitration is unclaimed by Glean/Copilot/Dust (0/1,402 Glean doc pages) and why a shared org hot/cold tier is unmatched — and why
  the brain must invent governance (ACL is source-granular; git vs GDPR erasure → put person data under db_only, never git).
- Cost (g02): ANN scan is ~4.5 ms of a ~3.3 s answered question. Write-side LLM curation is 222-4,514x embedding cost. "$100/month" is right-answer-
  wrong-arithmetic; all-in ≈ $225/month before agents ask anything; human librarian ≈ 2.5-3 h/week (inference, weakest number).
- Best non-founder existence proof: Ramp "Glass" + "Dojo" (350+ skills shared; write-once-read-many memory; 24-hour cleanup daemon; Sensei router).
  "DoorDash Team OS" is one PM's personal write-up, not a company deployment.

### (b) The fruit-fly work and how to combine
- Referent #1: Berg et al., "Sexual dimorphism in the complete Drosophila male central nervous system connectome", Cell 189(18):5504-5526, 3 Sep 2026,
  DOI 10.1016/j.cell.2026.08.015, CC-BY; 166,700 neurons, 11,710 types, 124.2M connections. Data was public 11 months before the paper (v0.9 Oct 2025,
  v1.0 Jun 2026) and almost nothing was built on it until the curated release — dated evidence for "being worth retrieving from is the product".
  Two meme waves: FlyWire/FAFB (flydoom 20 Aug; desktop-fly 796★) and MaleCNS (5-6 Sep). #2: BANC, Bates et al., Nature 656:957-970, 8 Jun 2026,
  155,916 neurons; its own analogy is Brooks' subsumption architecture (competence local, central layer supervisory and non-essential).
- Tan's talk contains zero neuroscience. The link is the user's synthesis; no paper combines connectome/mushroom-body ideas with RAG.
- Verdicts per mechanism (design agents RAN the experiments this session):
  | Mechanism | Verdict | Why |
  |---|---|---|
  | FlyHash/BioHash as vector index | KILL | d4 measured on bge-m3 in pgvector: sign binarization beats FlyHash +53% recall@10 at equal storage; FlyHash column 2.4x bytes, 2.2x slower; sparsevec >1000 nnz refused by HNSW; ANN is 0.14% of latency anyway. Ship pgvector binary quantization (22.5x smaller, 1.9x faster, 99.2% recall). |
  | FlyHash as dedup | KILL | SimHash beats it on H3D on quality and time; real incumbent is the free ANN probe (0.843 vs SimHash 0.263 on paraphrase edits). |
  | Fly/FlyPrompt router for skills | KILL | d3 measured on GBrain's 73 skills/271 fixtures: loses to nearest-centroid at every pool size; FlyPrompt is dense random features, not sparse expansion. BUT build the boring dense router: GBrain's router is a substring matcher (100% → 0% when copied phrases removed). |
  | Fly Bloom filter novelty / recurrence-after-dormancy gate at ingest | PILOT | d1: only unoccupied cell; two time constants over one code; break-even at 0.7% suppressed writes. Run K2 offline first (4 days, ~$0): needs ≥10 pts AUROC over time-blind baselines. P(win) ≈ 40%. |
  | Mushroom-body lifecycle: readout-gated promotion, suppressible demotion daemon, evidence ledger netted at read | PILOT | d2: GBrain promoted zero facts in a live run (#3042); forgetting is read-time only. Day-zero K5: AUROC of last_retrieved_at predicting "cited in correct answer" ≥ 0.60 or abandon. Include fly-free control arm (W-TinyLFU / CREW / SQL:2011). |
  | Connectome curation process (CAVE lineage graph, materialised versions, confidence with scale+producer, deprecation policy, split-don't-merge) | BUILD | d5: process transfer, zero LLM tokens/page, ~10 engineer-days; expected gain is reproducibility/arbitrability/governance, not accuracy. Say "not neuroscience" in the same breath. |
- Fly mechanisms cover the write gate, the tiering trigger and the forgetting daemon — never the content store. Provenance and skills have no fly counterpart.

### (c) Projects worth attention
gbrain + gbrain-evals (the evals repo is the most decision-relevant artifact and the reason to distrust the README); Letta MemFS; Cognee; Zep/Graphiti;
MemOS 2.0 (OpenClaw/Hermes plugins); HippoRAG 2; Ramp Glass write-ups; Hyper / Memory Store (YC "Company Brain" RFS); agno-agi/scout (counter-thesis);
Virtual Fly Brain MCP server; connectome_interpreter; FlyGCL (engineering merit only). b01-gbrain-* repos are astroturf. "MemFly arXiv:2602.09871" is fabricated.

## Next
1. Wait for judges (j1-j3) + SYNTHESIS-draft.md; compare with the table above; write SYNTHESIS.md.
2. Recommended first experiments (all cheap, none run by anyone): Tier-0 crux on MemConflict 804 static+conditional questions (~$30, one afternoon);
   template-blind paraphrase of gbrain-evals' 145 relational questions (issue #24); K5 AUROC day-zero test; K2 offline fly-gate test.
3. Commit + push.

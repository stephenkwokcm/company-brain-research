# Projects Built on the "Company Brain" Ideas

**Dimension key:** `projects-built-on-ideas` · Researched 2026-09-10 · All star counts pulled live from the GitHub REST API on 2026-09-10.

---

## TL;DR

1. **There is a real, dense ecosystem — but it is ~5 months old and clusters tightly around two Garry Tan repos.** `garrytan/gbrain` (29,764★, MIT, created 2026-04-05) and `garrytan/gstack` (132,248★) anchor a `topic:gbrain` cloud of 35 repos and a `topic:company-brain` cloud of 37 repos, plus a much larger Obsidian/markdown-vault layer (openhuman 39.5k★, claude-obsidian 14.8k★).
2. **The interesting projects are not the retrieval clones — they are the *hygiene* projects.** A small cluster implements exactly what Tan says the product is: provenance per fact, contradiction arbitration, temporal versioning, decay. `aura-memory`, `YourMemory` (Ebbinghaus decay, +16pp over Mem0 on LoCoMo), `animaworks` (grow/consolidate/forget), `gaptime` (bi-temporal), `agent-memory-staleness-audit`. These are small (0–266★) and are the frontier.
3. **"Company Brain" is a formal YC Request for Startups category (Summer 2026)**, and at least **12 YC companies** are shipping it — Memory Store (S26/Spring-26, literally tagline "Company Brain."), Hyper (heyhyper.ai), Savant, Glen, Hyperspell, Nessie, Turnstone, Corvera, Alloovium, Poth Labs, Egoist Machines, plus the 2018-vintage Within (used by OpenAI, DoorDash, ServiceNow).
4. **The fruit-fly ↔ company-brain intersection is essentially empty.** Exhaustive GitHub repo + code search returns exactly one project that wires FlyHash into LLM agent memory: `tfatykhov/membrain` (0★, last pushed 2026-02-03). Connectome work and agent-memory work are two disjoint communities; every high-star FlyWire repo is a simulation/visualisation toy, not a retrieval system. **This is an opportunity, not a survey gap.**
5. **Flag: at least one widely-circulated "fact" in this space is fabricated.** SEO summaries cite *"MemFly, arXiv:2602.09871"* as a fly-inspired memory-consolidation paper. arXiv 2602.09871 is *"Resolved Dust Emission and CO Isotopologues in Giant Molecular Clouds of the Andromeda Galaxy."* No MemFly paper exists on arXiv. Treat second-hand blog claims about this space as unverified.

---

## 1. The canonical stack (Tan's own)

| Repo | ★ | Created | Notes |
|---|---|---|---|
| [garrytan/gbrain](https://github.com/garrytan/gbrain) | 29,764 (4,441 forks) | 2026-04-05 | MIT. Markdown files + Git + PGLite/Postgres+pgvector. README claims Tan's production brain is **155,795 pages, 24,589 people, 5,340 companies, 66 crons**. Note the talk said "~220,000 pages" — the README's number is lower and dated; one of the two is stale. 173 open issues. |
| [garrytan/gbrain-evals](https://github.com/garrytan/gbrain-evals) | 419 | 2026-04-22 | **The most decision-relevant repo in the whole space.** Publishes reproducible numbers instead of rhetoric: LongMemEval run 2026-09-06 found all labelled evidence for **449/470 (95.53%)** answerable questions in 5 chunks, **433/500 (86.6%)** answered correctly. Concept questions: **130/181** exact-target-first with reranker vs **118/181** for vector search alone. Relationship retrieval raised first-place hits **9/39 → 21/39** on investor questions. The main README claims **P@5 49.1%, R@5 97.9%**, +31.4 P@5 points over the graph-disabled variant. |
| [garrytan/gstack](https://github.com/garrytan/gstack) | 132,248 | 2026-03-11 | The 23-tool Claude Code setup. Source of the "~810× my 2013 pace" claim (11,417 vs 14 *logical* lines/day) — note this is a different metric from the talk's "400X". |

**"Skillify" is not Tan's invention.** It is an internal Anthropic Claude Code skill gated behind `USER_TYPE === 'ant'`; [0xMH/claude-skillify](https://github.com/0xMH/claude-skillify) (45★) extracted and re-published the prompt. Related: [nickommen/skillify](https://github.com/nickommen/skillify) (12★) converts a session into a *deterministic Python* skill — the cleanest expression of Tan's "latent vs deterministic space" point. [eljulians/skillfile](https://github.com/eljulians/skillfile) is a declarative skill manager indexing 110K+ skills.

## 2. Direct GBrain ecosystem (`topic:gbrain`, 35 repos)

- **[huytieu/COG-second-brain](https://github.com/huytieu/COG-second-brain)** — 1,180★, MIT. README states "Inspired by Garry Tan's gstack and gbrain." 33 skills, 6 workers, 4 **read-only verifiers** — a V-model harness where "the worker never grades its own homework." This directly answers Tan's "bad skill file encodes bad process forever" failure mode.
- **[mage0535/hermes-memory-installer](https://github.com/mage0535/hermes-memory-installer)** — 206★. gbrain + Hindsight + 3-tier recall as an agent-agnostic sidecar.
- **[naveedharri/baalda](https://github.com/naveedharri/baalda)** — 123★, Apache-2.0, Tauri/Rust. Team second brain: plain `.md` on disk, real-time multiplayer editing, MCP endpoint. Closest thing to "library the humans and the librarian share."
- **b01-gbrain-\* vertical templates** (~44–49★ each, all pushed 2026-04-28): [devops](https://github.com/slayerassassinjack/b01-gbrain-devops), [security](https://github.com/PulverizeDirector/b01-gbrain-security), [seo](https://github.com/CometBureaucratEquip/b01-gbrain-seo), [ecommerce](https://github.com/BanMartinCode/b01-gbrain-ecommerce), [datascience](https://github.com/FlameToneSheave/b01-gbrain-datascience). A coordinated set of domain-specific self-wiring graphs.
- Bridges/ports: [howardpen9/hermes-gbrain-bridge](https://github.com/howardpen9/hermes-gbrain-bridge) (66★, Hermes/OpenClaw JSONL → gbrain markdown), [fxa3bah/OneBrain](https://github.com/fxa3bah/OneBrain) (47★, Obsidian+gbrain+Ollama, fully offline), [elkimek/hermes-gbrain-honcho](https://github.com/elkimek/hermes-gbrain-honcho) (32★), [durang/gbrain-http-wrapper](https://github.com/durang/gbrain-http-wrapper) (23★, OAuth 2.1 front-end for `gbrain serve`), [vladignatyev/brain-map-skill](https://github.com/vladignatyev/brain-map-skill) (70★, HN 23pts — force-graph visualiser for a gbrain/Obsidian vault), [hongyuatcufe/rbrain](https://github.com/hongyuatcufe/rbrain) (Rust port: SQLite + tantivy + usearch).

## 3. Open-source "company brain" (`topic:company-brain`, 37 repos)

- **[inkeep/open-knowledge](https://github.com/inkeep/open-knowledge)** — 4,103★, GPL-3.0, created 2026-06-03. "AI-native markdown IDE and LLM wiki." The best-funded-looking library layer.
- **[agno-agi/scout](https://github.com/agno-agi/scout)** — 724★, Apache-2.0. **The contrarian entry**: rather than pre-indexing, Scout *navigates live sources on demand* (web, Slack, Drive, wiki, CRM, MCP) and builds its wiki/CRM as a by-product. It is a direct empirical test of Tan's "the library is the product" claim.
- **[getnao/sylph](https://github.com/getnao/sylph)** — 196★, by nao Labs (YC X25). "Run your entire company with AI agents, skills, and a self-improving context." `AGENTS.md` + `CONTEXT.md` + per-domain context + `/sylph-create-skill`. Show HN 2026-05-22. This is the closest 1:1 implementation of the talk's org-as-markdown mapping (skill file = employee, resolver = org chart).
- Others: [yempik-ai/cowork-os](https://github.com/yempik-ai/cowork-os) (70★), [gquthier/company-os](https://github.com/gquthier/company-os) (26★), [kombohq/company-brain](https://github.com/kombohq/company-brain) (20★, syncs sources into Git as Markdown), [zilobase/zilobase](https://github.com/zilobase/zilobase) (18★), [emiliomartucci/marvis](https://github.com/emiliomartucci/marvis) (14★), [ahmetvural79/Vitrus](https://github.com/ahmetvural79/Vitrus) (13★ — "tells you what it doesn't know," deterministic gap analysis), [monoralabs/monora](https://github.com/monoralabs/monora) (6★, per-folder permissions).

## 4. Markdown / Obsidian vault brains (the "library" without the DB)

[tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) 39,564★ · [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) 14,769★ · [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) 12,828★ · [breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind) 4,619★ · [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) 4,378★ (45 commands, 7 CLI agents, scheduled maintenance agents) · [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) 3,499★ · [zilliztech/memsearch](https://github.com/zilliztech/memsearch) 2,579★ (Markdown + Milvus — Zilliz's own bet that the file *is* the source of truth) · [aristoapp/awesome-second-brain](https://github.com/aristoapp/awesome-second-brain) 527★ (curated index).

This layer is 10× larger than the gbrain-specific layer, and predates the talk. Tan's contribution is not "markdown vault" — it is *the librarian on top of it*.

## 5. Curation / provenance / contradiction — the actual frontier

These are the projects doing what Tan says is the product rather than the primitive:

| Repo | ★ | What it adds |
|---|---|---|
| [sachitrafa/YourMemory](https://github.com/sachitrafa/YourMemory) | 266 | Ebbinghaus forgetting-curve decay; claims **+16pp recall over Mem0 on LoCoMo** |
| [xuiltul/animaworks](https://github.com/xuiltul/animaworks) | 254 | Apache-2.0. "Organization-as-Code"; brain-inspired memory that **grows, consolidates and forgets**. Published production numbers Mar–Aug 2026: **302 agent-authored PRs (267 merged), 752 agent-operated PRs, 99.7% of 31,215 tasks self-initiated** |
| [dnotitia/akb](https://github.com/dnotitia/akb) | 160 | Vault-scoped organizational memory unified by a URI graph |
| [teolex2020/aura-memory](https://github.com/teolex2020/aura-memory) | 73 | MIT. Durable recall + **temporal versioning + provenance + contradiction governance** — a near-literal implementation of the talk's hygiene list |
| [davccavalcante/gaptime](https://github.com/davccavalcante/gaptime) | 2 | Bi-temporal KG: every fact carries valid-time and transaction-time |
| [memvara/memvara](https://github.com/memvara/memvara) | 1 | Deterministic contradiction resolution |
| [a-bhimava/agent-memory-staleness-audit](https://github.com/a-bhimava/agent-memory-staleness-audit) | 0 | Scores memories for staleness — the "stale facts surfaced with confidence" failure mode |
| [deltafly/DREAMER](https://github.com/deltafly/DREAMER) · [bstegemoller/carrel](https://github.com/bstegemoller/carrel) | 0 | Explicit **"Librarian"**-role curation layers over raw logs |

## 6. The fruit-fly / connectome branch — nearly empty

- **[tfatykhov/membrain](https://github.com/tfatykhov/membrain)** — 0★, last push 2026-02-03. FlyHash encoding + BiCameralMemory SNN (Nengo/Voja), Hopfield-style pattern completion, gRPC for agent integration. Catalogued in [tfatykhov/awesome-agent-memory](https://github.com/tfatykhov/awesome-agent-memory) (21★), which has a dedicated *Neuromorphic & Bio-Inspired Memory* section — the single best on-ramp for this question.
- **[TeddyHuang-00/FlyHash](https://github.com/TeddyHuang-00/FlyHash)** — 2★, the maintained pip library ([docs](https://flyhash.readthedocs.io/)).
- Papers worth citing: FlyHash origin [Dasgupta et al., *Science* 2017, doi:10.1126/science.aam9868](https://www.science.org/doi/10.1126/science.aam9868); [BioHash, PMLR v119 (2020)](http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf); **[H3D, arXiv:2607.08382 (2026-07-09)](https://arxiv.org/abs/2607.08382)** — benchmarks FlyHash against MinHash/SimHash/Winnowing/FuzzyHash + BGE quantisation for **fine-grained document deduplication**, i.e. exactly the dedup problem a 220K-page brain has; **[Stochastic Attention, arXiv:2604.00754](https://arxiv.org/abs/2604.00754)** — connectome-inspired randomised routing, motivated by the fly's 130K neurons at 0.02% connection probability with 4.4-hop average path; **[ZenBrain, arXiv:2604.23878](https://arxiv.org/abs/2604.23878)** — 7-layer neuroscience memory architecture whose "cooperative masking" finding (14/15 ablations look costless under moderate load) is a direct warning about over-engineering a brain.
- The high-star FlyWire repos — [desktop-fly](https://github.com/DenisSergeevitch/desktop-fly) (796★), [murthylab/codex](https://github.com/murthylab/codex) (83★), [erojasoficial-byte/fly-brain](https://github.com/erojasoficial-byte/fly-brain) (36★), [snedea/flybrain](https://github.com/snedea/flybrain) (21★) — are **simulation and visualisation only**. None touch retrieval or agent memory.

## 7. YC companies pursuing "brain" products

"Company Brain" is a named category in [YC's Summer 2026 RFS](https://www.ycombinator.com/rfs#company-brain) — gbrain's own README links to it and pitches itself as the thing to build on.

| Company | Batch | One-liner | Site |
|---|---|---|---|
| [Memory Store](https://www.ycombinator.com/companies/memory-store) | Spring 2026 | "Company Brain." — Slack/Gmail/Granola/Claude sessions → shared brain + live Briefs | memory.store |
| [Hyper](https://www.ycombinator.com/companies/hyper-4) | Spring 2026 | Self-maintaining KG; Postgres Episodes+Facts; hooks not just MCP. [Launch HN 2026-06-03: 79 pts, 78 comments](https://news.ycombinator.com/item?id=48387095). Claimed 50+ teams, $0→$1k MRR in 12 days | heyhyper.ai |
| [Savant](https://heysavant.com/) | Spring 2026 | Captures undocumented procedures, serves at decision time | heysavant.com |
| [Glen](https://www.tryglen.com/) | Summer 2026 | Ingests Claude Code/Codex/Cursor **agent sessions** + Slack/PRs; injects prior context into new agents | tryglen.com |
| [Hyperspell](https://hyperspell.com) | Fall 2025 | "Live, permissioned context graph… every fact traced to source" | hyperspell.com |
| [Nessie](https://nessielabs.com/) | Fall 2025 | Shared context layer so cross-tool thinking compounds | nessielabs.com |
| [Turnstone](https://myturnstone.ai) | Winter 2026 | Local-first second brain shared by multiple agents | myturnstone.ai |
| [Corvera](https://corvera.ai/) | Winter 2026 | Context layer for CPG brands; claims $0→$33k MRR in 4 weeks | corvera.ai |
| [Alloovium](https://www.alloovium.com/en) | Summer 2026 | Company brain for construction; every answer cites its source sentence | alloovium.com |
| [Poth Labs](https://pothlabs.com) | Summer 2026 | "Customer brain" — hypothesis generation over company data | pothlabs.com |
| [Egoist Machines](https://ego.ist/) | Summer 2026 | User-owned portable personal context ("AI Passport") | ego.ist |
| [Within](http://within.ai) | Summer 2018 | "Company Brain" used by OpenAI, DoorDash, ServiceNow, Salesforce (128 people — the incumbent) | within.ai |

Adjacent: [Kaelio/ktx](https://kaelio.com/) (Spring 2025, open-source context layer for data agents, 1,581★), [Janet AI](https://janet.ai) (S25), [Mem0](https://mem0.ai) (S24, 65,004★).

---

## Relevance to company-brain / RAG / fruit-fly question

**(a) RAG.** The ecosystem has already split along Tan's own line. On one side sit generic retrieval layers — mem0 (65,004★), Memori (16,526★), memvid (16,531★), MemMachine (3,217★), ClawMem (210★) — which are RAG-plus-schema. On the other sit the *hygiene* projects in §5, whose selling points are provenance, contradiction, decay, staleness and gap analysis, i.e. non-retrieval features. `gbrain-evals` is the only project that has tried to *measure* the difference (+31.4 P@5 points from enabling the graph; 9/39 → 21/39 on relationship questions). Anyone evaluating the thesis should start there, because it is falsifiable.

**(b) Fruit fly.** Nobody has done the combination. The two credible bridges are narrow and specific: **FlyHash as a cheap sparse LSH for deduplication and near-duplicate detection over a 100K+ page brain** (H3D benchmarks exactly this, arXiv:2607.08382), and **connectome-style sparse stochastic routing as the resolver/librarian layer** (arXiv:2604.00754 — the fly gets 4.4-hop reachability from 0.02% connectivity, which is the routing property a resolver table wants). `membrain` is the only running code, and it is a 0-star proof of concept. If the user wants to build something novel here, this is the gap.

**(c) Interesting projects.** Ranked below.

## The 5 most worth your attention

1. **[garrytan/gbrain-evals](https://github.com/garrytan/gbrain-evals)** (419★) — turns "is it just RAG?" into a reproducible experiment with published per-configuration deltas. Read `docs/retrieval-lessons.md` first.
2. **[xuiltul/animaworks](https://github.com/xuiltul/animaworks)** (254★) — the only project publishing *production* org-as-code numbers (302 agent-authored PRs, 99.7% self-initiated tasks over 6 months) **and** explicitly framing memory as grow/consolidate/forget. Closest existing system to a biologically-shaped company brain.
3. **[teolex2020/aura-memory](https://github.com/teolex2020/aura-memory)** (73★, MIT) — provenance + temporal versioning + contradiction governance, small enough to read end-to-end. This is the talk's "librarian" as code.
4. **[huytieu/COG-second-brain](https://github.com/huytieu/COG-second-brain)** (1,180★, MIT) — largest explicitly gbrain-inspired project, and it adds the thing gbrain lacks: read-only verifier agents so a bad skill file doesn't calcify.
5. **[tfatykhov/awesome-agent-memory](https://github.com/tfatykhov/awesome-agent-memory)** (21★) + **[membrain](https://github.com/tfatykhov/membrain)** — the only maintained bridge between the agent-memory literature and the neuromorphic/fly-inspired literature. Low stars, high information density.

*Contrarian pick worth 20 minutes:* **[agno-agi/scout](https://github.com/agno-agi/scout)** (724★) — argues you should navigate live sources rather than curate a library at all. If Scout works, half the talk is wrong.

## Open questions

1. Has anyone actually benchmarked FlyHash (or BioHash) as the dedup/near-duplicate stage of a large agent brain in production? H3D benchmarks it on scientific documents, not agent memories.
2. gbrain's README says 155,795 pages; the talk says ~220,000. Which is current, and does page count correlate with retrieval quality or degrade it?
3. `gbrain-evals` publishes only gbrain-vs-ablation comparisons. Is there any *third-party* head-to-head of gbrain vs mem0 / Zep / HippoRAG on LongMemEval?
4. Hyper, Memory Store, Savant, Glen and Hyperspell all describe near-identical architectures (episodes + extracted facts + provenance + permissioned graph). What actually differentiates them, and is any of them beating gbrain on public benchmarks?
5. Do the "contradiction governance" projects (aura-memory, memvara, gaptime) resolve contradictions deterministically, or do they punt to an LLM judge — and does that reintroduce the failure mode Tan warns about?
6. The `b01-gbrain-*` vertical repos all appeared on the same day (2026-04-28) from unrelated-looking accounts. Coordinated launch, one author, or astroturf? Worth checking before recommending.
7. Is `topic:gbrain` star count organic? gbrain went 0 → ~5,000★ in 24 hours per third-party reporting; that report itself is unverified.

## Sources

- https://github.com/garrytan/gbrain · https://github.com/garrytan/gbrain-evals · https://github.com/garrytan/gstack
- https://api.github.com/search/repositories (queries: `topic:gbrain`, `topic:company-brain`, `topic:second-brain`, `gbrain`, `company brain agent`, `agent memory layer`, `provenance agent memory contradiction`, `FlyWire`, `kenyon cell`, `connectome LLM`, `skillify`) — retrieved 2026-09-10
- https://api.ycombinator.com/v0.1/companies?q=brain and https://yc-oss.github.io/api/companies/all.json (6,204 companies; filtered 2026-09-10)
- https://www.ycombinator.com/companies/memory-store · https://www.ycombinator.com/companies/hyper-4 · https://www.ycombinator.com/rfs#company-brain
- https://news.ycombinator.com/item?id=48387095 (Launch HN: Hyper, 2026-06-03) · https://hn.algolia.com/api/v1/search (queries: gbrain, company brain, skillify)
- https://arxiv.org/abs/2607.08382 (H3D) · https://arxiv.org/abs/2604.00754 (Stochastic Attention) · https://arxiv.org/abs/2604.23878 (ZenBrain)
- https://www.science.org/doi/10.1126/science.aam9868 (FlyHash, 2017) · http://proceedings.mlr.press/v119/ryali20a/ryali20a.pdf (BioHash, 2020)
- https://github.com/tfatykhov/awesome-agent-memory · https://github.com/tfatykhov/membrain · https://flyhash.readthedocs.io/
- https://sites.google.com/view/memagent-iclr26/ (ICLR 2026 MemAgents workshop, 2026-04-27, Rio de Janeiro)
- https://github.com/0xMH/claude-skillify · https://github.com/getnao/sylph · https://github.com/agno-agi/scout · https://github.com/huytieu/COG-second-brain · https://github.com/xuiltul/animaworks · https://github.com/teolex2020/aura-memory · https://github.com/naveedharri/baalda · https://github.com/inkeep/open-knowledge

**Negative result / correction:** arXiv:2602.09871 is *not* "MemFly"; it is an astronomy paper on M31 molecular clouds (verified via the arXiv API on 2026-09-10). Several SEO-optimised blog posts about fly-inspired agent memory cite it. No paper named MemFly is indexed on arXiv.

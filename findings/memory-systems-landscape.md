# Agent-Memory / Second-Brain Landscape — as of 2026-09-10

Dimension key: `memory-systems-landscape`. All GitHub star counts fetched live via `gh api repos/<owner>/<repo>` on **2026-09-10**.

---

## TL;DR

1. **The field split into two camps in 2026.** *Extraction-and-index* systems (Mem0, Zep/Graphiti, Cognee, MemOS) turn conversations into facts in a vector/graph DB; *file-and-git* systems (GBrain, Letta MemFS, Basic Memory, Claude Code auto-memory, memsearch) keep human-readable Markdown as the source of truth and treat the index as a derived cache. Tan's "library + librarian" spec lands squarely in the second camp — and that camp is where 2026's growth is.
2. **Write-side curation is still the rarest feature.** Across the 86 systems catalogued by [carsteneu/ai-memory-comparison](https://github.com/carsteneu/ai-memory-comparison), only a handful ship *contradiction detection* (GBrain, Cognee, Supermemory, mcp-memory-service, second-brain-cloudflare) and essentially **none** ship a trust/provenance-weighting model (`trustModel` is false for every system I checked). Retrieval is commoditised; the librarian is not.
3. **The three closest implementations of Tan's spec are GBrain, Letta MemFS, and Cognee** — GBrain for source-tiered ranking + suspected-contradictions eval + dream cycle; Letta MemFS for git-versioned memory with `dreaming` and a `memory doctor` subagent; Cognee for opt-in append-only provenance lineage (SHA-256 chained) plus `contradicts` edges with confidence scores.
4. **Benchmarks are self-reported and mutually inconsistent.** Zep is quoted at 94.7% LoCoMo by its own docs and 80.32% by Mem0's comparison; LongMemEval figures for Zep range 71.2%–90.2% depending on who ran it. Treat every number below as a vendor claim unless it says otherwise. The most credible independent-ish artifact I found is GBrain's own eval repo, which reports **86.6% LongMemEval answer accuracy (433/500)** and separates retrieval from answering.
5. **Hot/cold tiering has converged on one pattern**: a small always-loaded index (Claude Code's `MEMORY.md` ≤200 lines/25KB; Letta's `system/` directory; Letta's file tree as "signposts") plus on-demand cold reads. This is a direct mechanical implementation of Tan's "who decides which three books are open".

---

## 1. Taxonomy

Five architectural families are now distinguishable (synthesis mine; families roughly match [awesome-agent-memory's product-architecture map](https://github.com/Snseam/awesome-agent-memory/blob/main/docs/product-memory-architectures.md)):

| Family | Substrate | Exemplars | Librarian strength |
|---|---|---|---|
| **Extract-and-index** | vector (+ light entity linking) | Mem0, EverOS, Memori, memU, Hindsight | Weak — ADD-only, no arbitration |
| **Temporal knowledge graph** | graph + bi-temporal edges | Zep/Graphiti, Cognee, MemMachine, Oracle | Strong on *supersession*, weak on curation |
| **Memory-OS / layered cognition** | tiered stores + consolidation | Letta, MemOS, MemoryOS, MIRIX, TencentDB-AM | Strong on tiering, mixed on provenance |
| **File-and-git (local-first Markdown)** | Markdown in git, DB as cache | **GBrain**, **Letta MemFS**, Basic Memory, memsearch, Claude Code auto-memory | Strongest on inspectability + human co-authorship |
| **Platform-managed** | opaque managed store | OpenAI memory, Google Memory Bank, AWS AgentCore Memory, Cloudflare Agent Memory | Governance yes, inspectability no |

---

## 2. Comparison table

Feature flags are from [carsteneu/ai-memory-comparison `data.js`](https://github.com/carsteneu/ai-memory-comparison/blob/main/data.js) (86 systems × 79 features, every ✅ source-cited; file header says "Last updated: 2026-05-27", star counts auto-refresh). Stars are my own `gh api` reads on 2026-09-10, which is why they differ slightly from the site.

| System | Stars | Lic. | Core substrate | Write-side curation | Hot/cold tiers | Provenance | Contradiction | LoCoMo / LongMemEval |
|---|---:|---|---|---|---|---|---|---|
| [**GBrain**](https://github.com/garrytan/gbrain) | 29,763 | MIT | Markdown-in-git → PGLite/Postgres+pgvector; zero-LLM wikilink edge extraction | dedup, quality refine, supersede, explicit forget, nightly "dream cycle" | brain ⊥ source axes; mounted brains; source-tier boost | ✅ source attribution + source-aware SQL ranking | ✅ `gbrain eval suspected-contradictions` | — / **86.6%** (own evals repo, 2026-09-06) |
| [**Letta**](https://github.com/letta-ai/letta) (+[letta-code](https://github.com/letta-ai/letta-code) 3,241★) | 24,675 | Apache-2.0 | MemFS: git-backed Markdown+YAML frontmatter; Postgres+vector | `dreaming` + `memory doctor` subagents in git worktrees | ✅ `system/` → system prompt every turn; rest cold, file tree as signposts | git history = version provenance | via git conflict resolution (not semantic) | 74.0% (per Mem0 comparison) / — |
| [**Graphiti**/Zep](https://github.com/getzep/graphiti) | 30,734 | Apache-2.0 | Bi-temporal knowledge graph (valid time vs transaction time) | dedup, narrative gen, clustering; **temporal edge invalidation** not LLM arbitration | episode-level, no in-context tier | ✅ episodes retained as source | ⚠️ supersession only (invalidate edge, keep history) | 94.7% / 90.2% (own docs) vs 80.32% / 71.2% (Mem0's) |
| [**Cognee**](https://github.com/topoteretes/cognee) | 30,610 | Apache-2.0 | Graph + vector + relational (ECL `cognify` pipeline) | 8 search modes, ontology, decay, supersede | ✅ layered memory, time-travel | ✅ **opt-in append-only `provenance_entries` table, SHA-256 chained** doc→chunk→entity→relationship | ✅ **opt-in `contradicts` edges with confidence scores** | — / — |
| [**Mem0**](https://github.com/mem0ai/mem0) | 65,003 | Apache-2.0 | Qdrant vector + entity linking (OSS graph is ranking-only) | single LLM call decides ADD/UPDATE/DELETE/NOOP per fact | ❌ scope isolation (user/agent/run/app), not tiers | ❌ | ❌ (add-only supersede) | 92.5% / 94.4% (self-reported) |
| [**Supermemory**](https://github.com/supermemoryai/supermemory) | 29,557 | MIT | Hyperdrive(PG)+KV+vector, 23-field versioned entries | decay, supersede, dedup, quality refine, auto-resolution | ✅ layered + time-travel | ✅ source attribution | ✅ + auto-resolve | — / 81.6% |
| [**MemOS**](https://github.com/MemTensor/MemOS) | 11,245 | Apache-2.0 | MemCube over Neo4j+Qdrant+Redis | preproc, dedup, quality refine | ✅ layered, time-travel | ❌ | ❌ | 75.80% / +40.43% rel. · 35.24% token saving |
| [**Khoj**](https://github.com/khoj-ai/khoj) | 37,228 | AGPL-3.0 | Self-hostable "AI second brain" over docs+web | — (retrieval-first product) | ❌ | partial (doc citations) | ❌ | — / — |
| [**Basic Memory**](https://github.com/basicmachines-co/basic-memory) | 3,905 | AGPL-3.0 | Local-first Markdown + wikilinks + semantic search, MCP-native | two-way human/AI writes, sync | ❌ | file-level | ❌ | — / — |
| [**mcp-memory-service**](https://github.com/doobidoo/mcp-memory-service) | 1,933 | Apache-2.0 | SQLite-vec / Cloudflare / Milvus; 28 schema fields | decay, supersede, dedup, refine, clustering, recurrence, **autonomous consolidation** | ❌ | ✅ | ✅ + auto-resolve | — / 86.0 (sess) · 80.4 (turn) |
| [**LangMem**](https://github.com/langchain-ai/langmem) | 1,653 | MIT | Pluggable BaseStore namespaces | auto-extract only | ❌ | ❌ | ❌ | — / — |
| **Claude Code memory + Skills** ([docs](https://code.claude.com/docs/en/memory)) | n/a | proprietary | Markdown: `CLAUDE.md` hierarchy + `~/.claude/projects/<p>/memory/` | Claude self-writes 4 typed notes (`user`/`feedback`/`project`/`reference`); index-size enforcement | ✅ **`MEMORY.md` first 200 lines / 25KB loaded every session; topic files read on demand** | ⚠️ `modified` ISO-8601 frontmatter timestamp | ❌ (docs warn "if two rules contradict, Claude may pick one arbitrarily") | — / — |
| **OpenAI memory** | n/a | proprietary | managed | opaque | ❌ | ❌ | ❌ | 52.9% (per Mem0) / — |
| **Google Vertex Memory Bank** ([docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)) | n/a | proprietary | managed, memory profiles + revisions | LLM-generated + uploaded memories, consolidation | scoped | ⚠️ "inspect memory revisions" | not documented | — / — |

**2026 newcomers worth watching** (all verified live): [OpenViking](https://github.com/volcengine/OpenViking) 36,261★ (ByteDance/Volcengine, AGPL-3.0, created 2026-01-05, "context DB" with a filesystem paradigm, 82.1 LoCoMo / 91% token reduction); [claude-mem](https://github.com/thedotmack/claude-mem) 93,572★ (hooks-based observation capture — the single most-starred agent-memory repo, yet ❌ on every lifecycle feature); [agentmemory](https://github.com/rohitg00/agentmemory) 28,212★ (SQLite-only, zero external DBs, claims 95.2 LongMemEval / 92% fewer tokens); [TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) 26,241★ (Atom/Scenario/Persona tiers as an OpenClaw plugin); [Hindsight](https://github.com/vectorize-io/hindsight) 23,317★; [Memori](https://github.com/MemoriLabs/Memori) 16,525★; [memU](https://github.com/NevaMind-AI/memU) 14,398★; [EverOS](https://github.com/EverMind-AI/EverOS) 12,828★.

---

## 3. Where the librarian actually exists

**Write-side curation.** Mem0's pipeline is the industry default: "a single LLM call compares the new messages against the retrieved candidates and decides, per fact, whether to `ADD`, `UPDATE`, `DELETE`, or leave a memory alone" ([docs](https://docs.mem0.ai/core-concepts/memory-types)). That is one LLM call at write time — meaningful, but not a librarian. Mem0's own 2026 report concedes the weakness: "**Single-pass ADD-only extraction: agent-generated facts receive equal weight to user facts**" ([State of AI Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026), 2026-04-01) — exactly Tan's "garbage dump with great search" failure mode.

**Provenance.** Cognee is the only system I found with cryptographic lineage: an opt-in append-only `provenance_entries` table appending "document → chunk → entity → relationship lineage entries" with SHA-256 checksums for chain verification. GBrain implements a cheaper but arguably more useful version — *source-tier ranking*: "curated content like `originals/`, `concepts/`, `writing/` outranks bulk content", applied "as a source-factor CASE expression at the SQL layer" ([evidence file](https://github.com/carsteneu/ai-memory-comparison/blob/main/evidence/gbrain.md)). That is provenance used as a retrieval prior, which is closer to what a librarian does than an audit log is.

**Contradiction arbitration.** Three approaches exist and they are not equivalent:
- *Temporal invalidation* (Graphiti): mark the old edge invalid, keep it for point-in-time queries. Never asks "which is true".
- *Semantic conflict detection* (Cognee): gather facts one hop from touched entities, "ask the LLM which pairs conflict", write `contradicts` edges with confidence. Detects, does not resolve.
- *Eval-driven surfacing* (GBrain): `gbrain eval suspected-contradictions` samples retrieval pairs and surfaces conflicts between "takes + facts the agent has written", wired into the daily dream cycle with a contradictions trend and takes scorecard (CHANGELOG v0.36.4.0). This is the only one framed as an ongoing hygiene *job* rather than a data-model property.

The research side caught up in 2026: **MemConflict** ([arXiv:2605.20926](https://arxiv.org/abs/2605.20926), Tao et al., 2026-05-20) formalises dynamic/static/conditional conflicts over temporal validity, factual correctness and contextual applicability, evaluates six long-term memory systems, and finds "uneven strengths across conflict types, with answer correctness often diverging from memory retrieval and ranking." That divergence is the single most important methodological finding for anyone building a company brain: **your retrieval score and your answer score measure different failures.** GBrain's eval repo independently reports the same split — 95.53% retrieval completeness at k=5 (449/470) vs 86.6% answer accuracy (433/500).

---

## 4. Benchmark skepticism

LoCoMo (1,540 questions) and LongMemEval (500 questions) are the de facto standard, with BEAM (1M–10M tokens) emerging. But the leaderboard is a mess of self-reports. Mem0's own [benchmark round-up](https://mem0.ai/blog/ai-memory-benchmarks-in-2026) labels the methodology of every competitor and notes Zep self-reports 94.7% LoCoMo while "third-party tests put Zep at 75.1%". Two 2026 papers attack the evaluation layer directly: **MemDelta: Controlled Baselines and Hidden Confounds in Agent Memory Evaluation** ([arXiv:2606.29914](https://arxiv.org/pdf/2606.29914)) and **A Survey on Long-Term Memory Security in LLM Agents** ([arXiv:2604.16548](https://arxiv.org/pdf/2604.16548)). None of the file-and-git systems (GBrain excepted) publish LoCoMo/LongMemEval at all, which makes the head-to-head Tan-vs-Mem0 comparison currently unresolvable from public data.

---

## 5. Relevance to company-brain / RAG / fruit-fly question

**(a) Is it RAG?** The landscape data settles this empirically. `awesome-agent-memory` explicitly *excludes* "plain RAG middleware that does not model update, consolidation, or forgetting" and "pure vector databases with no memory lifecycle" from its scope. The industry has drawn the same line Tan draws in the talk: retrieval is table stakes; the differentiator is the *lifecycle* axis — decay, supersede, contradiction, quarantine, auto-resolve, trust model, explicit forget. On that axis most "memory" products are still RAG wearing a hat: of the ~24 systems I inspected in detail, **zero** had `trustModel: true`, and only 5 had `contradiction: true`.

**(b) Company-brain specifically.** The category is now formalised: Tom Blomfield's YC **Summer 2026** RFS created a "Company Brain" entry (it has since rotated off the live [ycombinator.com/rfs](https://www.ycombinator.com/rfs) page, which now shows the Fall 2026 list — GBrain's README still deep-links `#company-brain`). GBrain ships an explicit [company-brain tutorial](https://github.com/garrytan/gbrain/blob/master/docs/tutorials/company-brain.md) with per-login scoping. Competing implementations: [agno-agi/scout](https://github.com/agno-agi/scout) (724★, Apache-2.0, "Open Source Company Brain" — builds its own wiki+CRM as it learns) and commercial [Hyper](https://www.ycombinator.com/companies/hyper-4) (YC Spring 2026, "self-driving company brain", reported $1K MRR and 50+ teams 12 days post-launch).

**(c) Fruit-fly.** Nothing in this landscape cites fly connectomics. The one real bridge is architectural, not citational: mushroom-body-style *sparse expansion coding* (FlyHash LSH) is a plausible drop-in for the ANN index layer, and offline consolidation in the fly's mushroom body is the biological analogue of what GBrain calls the "dream cycle" and Letta calls `dreaming` / `memory doctor`. Both are inference on my part — **low confidence**, and another dimension in this project owns the primary-source ranking.

---

## Open questions

1. No system in this survey implements a **trust model** (per-source credibility weighting that changes arbitration outcomes). Is that a genuine gap or does GBrain's source-tier SQL boost already cover the useful 80%?
2. GBrain publishes LongMemEval but not LoCoMo; Mem0 publishes both but with add-only extraction. **Nobody has run MemConflict across the file-and-git family.** That is the missing experiment.
3. Letta MemFS and GBrain converged independently on git-backed Markdown + nightly consolidation subagents within ~months of each other. Which came first, and is either citing the other?
4. `data.js` lists GBrain's `created` as "2025-07" while `gh api` and GBrain's own evidence file both say **2026-04-05** — a data error in an otherwise well-sourced dataset. How many other rows carry stale metadata?
5. Star counts in this space are wildly decoupled from feature depth (claude-mem: 93,572★, zero lifecycle features; LangMem: 1,653★, also near-zero). What is actually driving adoption?

## Sources

- https://github.com/garrytan/gbrain (README fetched via `gh api repos/garrytan/gbrain/readme`, 2026-09-10)
- https://github.com/garrytan/gbrain-evals (README, LongMemEval run dated 2026-09-06)
- https://github.com/carsteneu/ai-memory-comparison and its `data.js` + `evidence/gbrain.md`
- https://github.com/Snseam/awesome-agent-memory (`docs/products-landscape.md`, `docs/product-memory-architectures.md`)
- https://docs.mem0.ai/core-concepts/memory-types
- https://mem0.ai/blog/state-of-ai-agent-memory-2026 (2026-04-01)
- https://mem0.ai/blog/ai-memory-benchmarks-in-2026
- https://docs.letta.com/concepts/memfs
- https://www.letta.com/blog/context-repositories/
- https://help.getzep.com/graphiti/graphiti/overview
- https://docs.cognee.ai/core-concepts/main-operations/cognify
- https://code.claude.com/docs/en/memory
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview
- https://arxiv.org/abs/2605.20926 (MemConflict)
- https://arxiv.org/pdf/2606.29914 (MemDelta), https://arxiv.org/pdf/2604.16548 (memory security survey)
- https://www.ycombinator.com/rfs ; https://modelence.com/yc-rfs-summer-2026/company-brain ; https://www.ycombinator.com/companies/hyper-4
- GitHub repo metadata for all star counts: `gh api repos/<owner>/<repo>`, 2026-09-10

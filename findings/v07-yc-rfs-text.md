# v07 — YC "Company Brain" RFS: verbatim text and verdict

**Key:** `v07-yc-rfs-text` · **Lens:** primary-source · **Date of work:** 2026-09-10

**Claim under test:** *"YC published a Summer 2026 'Company Brain' Request for Startups authored by Tom Blomfield demanding provenance metadata and contradiction detection."*

## Verdict: PARTIALLY — split into two halves

| Half of the claim | Verdict | Confidence |
|---|---|---|
| YC published a **Summer 2026 "Company Brain" RFS authored by Tom Blomfield** | **CONFIRMED** | Very high — verbatim text recovered from YC's own live JS bundle and from 5 independent Wayback snapshots |
| The RFS **demands provenance metadata and contradiction detection** | **REFUTED** | Very high — neither concept, nor the words, appear anywhere in the brief in any version |

**One sentence:** YC's Summer 2026 "Company Brain" RFS by Tom Blomfield is real, published 2026-04-28 and still live at `ycombinator.com/rfs#company-brain`, but its 220-word text says nothing about provenance metadata or contradiction detection — those requirements come from a third-party MVP build brief on modelence.com that three prior reports mistook for a mirror of YC's text.

---

## 1. The verbatim RFS text

Recovered two ways that agree byte-for-byte.

**Source A (live, 2026-09-10):** `https://bookface-static.ycombinator.com/vite/assets/RequestsForStartupsPage-MrG_romv.js` — the client chunk that `https://www.ycombinator.com/rfs` loads. Entry object: `{id:`company-brain`, title:`Company Brain`, …, author:{firstName:`Tom`, lastName:`Blomfield`, profileUrl:`https://www.ycombinator.com/people/tom-blomfield`}, videoId:`IaWIazkWWog`}`. It sits at byte offset 27151, between the `summer-2026` season header (20695) and the `spring-2026` header (45633), i.e. inside the Summer 2026 `items` array.

**Source B (archived):** `https://web.archive.org/web/20260628031528id_/https://www.ycombinator.com/rfs` — server-rendered HTML, Summer 2026 as the active tab.

> **Company Brain**
> By Tom Blomfield
>
> The biggest blocker to AI automation of companies is no longer the models, they just got so good so quickly. Now the blocker is the domain knowledge.
>
> Every company has critical know-how scattered everywhere. Some of it lives in people's heads. Some of it is buried in old email accounts, Slack threads, support tickets, and databases. The company works because humans vaguely remember where that knowledge is and how to apply it.
>
> But AI agents can't operate like that. If we want every company to run on AI automation, we need a new primitive: a company brain.
>
> We need Garry's G-Brain, but for every business in the world. A system that pulls knowledge out of all these fragmented sources, structures it, keeps it current, and turns it into an executable skills file for AI.
>
> This isn't a company-wide search or a chatbot over documents. It's a living map of how a company works: how refunds get handled, how pricing exceptions are decided or how engineers respond to incidents.
>
> Then AI systems can use that skills file to actually do the work safely and consistently.
>
> The company brain becomes the missing layer between raw company data and reliable AI automation.
>
> I think every company in the world is going to need one.
>
> If you're building this, you should apply to YC.

**That is the entire brief: 220 words, 1,278 characters.** There is no bullet list, no capability table, no spec.

Season framing (same object, `{id:`summer-2026`}`): *"AI has stopped being a feature and started being the foundation. We're excited about a new wave of startups rebuilding software, services, and silicon— and pushing AI into the physical world. Several come directly from YC founders sharing what they're seeing on the frontier."*

### The text has never changed
Extracted the passage from `"The biggest blocker…"` to `"…apply to YC."` out of five snapshots and hashed it:

| Snapshot | Length | md5 (first 12) |
|---|---|---|
| `web/20260428053810` | 1282 | `22ae2c6f5f9e` |
| `web/20260505233712` | 1282 | `22ae2c6f5f9e` |
| `web/20260525113314` | 1282 | `22ae2c6f5f9e` |
| `web/20260628031528` | 1282 | `22ae2c6f5f9e` |
| `web/20260708135218` | 1282 | `22ae2c6f5f9e` |

Identical, and identical to the live chunk. No edited-out earlier version exists.

## 2. The provenance / contradiction requirements are not there

Keyword scan over every archived version of the page that contains the entry (`20260525113314`, `20260628031528`, `20260708135218`) and over the live JS chunk:

| Term | Hits in RFS page |
|---|---|
| provenance | **0** |
| metadata | **0** |
| "access level" | **0** |
| citation | **0** |
| contradiction | **0** |
| "author, date" | **0** |
| "knowledge graph" | **0** |
| "browser extension" | **0** |
| permission | **0** |

(One `contradict*` hit exists in the live chunk, but it is in a *different, earlier* RFS entry — "Compliance and Audit", also by Blomfield, an older season: *"…or highlighting contradictory policies."* Nothing to do with Company Brain.)

YC's own 82-second RFS video for the entry (`youtube.com/watch?v=IaWIazkWWog`, channel "Y Combinator", published **2026-04-28T06:56:20-07:00**) carries the same framing and no such requirements:

> "Every company has critical know-how scattered across people's heads, old Slack threads, support tickets, and databases, and AI agents can't operate like that. We think every company in the world is going to need a new primitive: a living map of how the company works that turns its own artifacts into an executable skills file for AI. Apply to YC Summer 2026 at ycombinator.com/apply."

## 3. Where the false requirements came from

Three prior reports (`rag-taxonomy.md` L67, `garry-tan-ecosystem.md` L71, `talk-analysis.md` L19/L142) cite `https://modelence.com/yc-rfs-summer-2026/company-brain` as a "mirror" of the RFS. **It is not a mirror.** It is a Modelence-authored build brief for Modelence's own app builder. Its page furniture gives it away: "Start with an MVP", a "Start Building" CTA, and the closing line *"Builds a working MVP of a company knowledge base."* It does not quote a single sentence of Blomfield's text. Its only YC links are `ycombinator.com/people/tom-blomfield` and `ycombinator.com/rfs#company-brain` (a "View in YC" pointer).

The disputed language is Modelence's, verbatim from that page:

- *"All sources should be indexed with metadata: author, date, access level, related entities."* → the "provenance metadata" claim
- Under "Semantic knowledge graph": *"Detect contradictions and flag for resolution"* → the "contradiction detection" claim
- Also Modelence-only, and also wrongly attributed to YC in `garry-tan-ecosystem.md`: "Natural language Q&A with source citations", *"Why did we decide X?"*, "Browser extension that surfaces relevant internal knowledge while working", "Slack bot", "Respect source system permissions", "PII detection and redaction", "Audit log of all queries and retrievals", "Confidence scoring on answers with evidence chains".

So `garry-tan-ecosystem.md`'s sentence "Required capabilities in the RFS: continuous ingestion, a semantic knowledge graph, cited natural-language Q&A…, proactive surfacing via browser extension/Slack, and access control that respects source-system permissions" describes **Modelence's product spec, not YC's brief**, and must be deleted or reattributed.

## 4. Correction to a second, separate error: the anchor is *not* stale

Four prior reports state that the entry "has rotated off" the live RFS page and that GBrain's README deep-links a "dead"/"stale" anchor. **That is wrong.**

- The live page server-renders only the *default* season (Fall 2026 since ~2026-07-22), which is why `curl https://www.ycombinator.com/rfs | grep "Company Brain"` returns nothing. Prior reports appear to have stopped there.
- The season selector on the live page still lists **Summer 2026**, and the full Summer 2026 list — Company Brain included — ships inside `RequestsForStartupsPage-MrG_romv.js`.
- That chunk contains explicit hash routing: `x=()=>typeof window<'u'?window.location.hash.replace('#',''):''` and `S=()=>{let e=x(); if(e){let t=f.find(t=>t.items.some(t=>t.id===e)); if(t)return t.id} return f[0].id}`, followed by a `scrollIntoView` on `document.getElementById(hash)`. So **`https://www.ycombinator.com/rfs#company-brain` still resolves today**: it selects the Summer 2026 season and scrolls to the entry.
- GBrain's README link is therefore live, not stale: `README.md` L7 — *"the [company-brain](https://www.ycombinator.com/rfs#company-brain) shape on YC's Request for Startups. If you're building in that space, you might as well build on this."*

## 5. Publication date pinned

| Snapshot | Company Brain present? | Summer 2026 entries |
|---|---|---|
| `web/20260422151545` | no | (Spring 2026 was default; Summer 2026 tab had no such entry) |
| `web/20260428053810` | **yes** | AI for Low-Pesticide Agriculture, AI-Native Service Companies, AI Personalized Medicine, **Company Brain**, Counter-Swarm Defense, Dynamic Software Interfaces, Electronics in Space, Hardware Supply Chain, Industrial Capabilities in Space, Inference Chips for Agent Workflows, SaaS Challengers, Software for Agents, Startups That Want to Sell to Huge Companies, Supply Chain 2.0 for Semiconductors, The AI Operating System for Companies |

Combined with the YC video's publish timestamp (2026-04-28T06:56:20-07:00), the Summer 2026 RFS list including Company Brain went live on **2026-04-28**. It therefore *preceded* the AI Engineer talk (2026-07-16) by about eleven weeks, consistent with the campaign timeline in `garry-tan-ecosystem.md` but now dated precisely. (The list grew later — "AI-Native Discovery Engines" by Jon Xu is in the 2026-06-28 snapshot but not the 2026-04-28 one — while the Company Brain text itself never changed.)

The Company Brain entry stopped being *server-rendered by default* between `web/20260708135218` (present) and `web/20260722203701` (absent), when Fall 2026 became the default tab. That is a default-tab change, not a removal.

## 6. What the RFS actually demands — and why it matters more than the false version

Stripped to requirements, the brief asks for exactly four things:

1. **Ingest** — "pulls knowledge out of all these fragmented sources" (people's heads, old email, Slack threads, support tickets, databases)
2. **Structure** — "structures it"
3. **Keep current** — "keeps it current"
4. **Emit procedural memory** — "turns it into an executable skills file for AI"; "Then AI systems can use that skills file to actually do the work safely and consistently"

And it draws one explicit negative boundary: **"This isn't a company-wide search or a chatbot over documents."**

Two consequences worth carrying into the synthesis:

- The RFS is *stronger* evidence for the procedural-memory dividing line in `rag-taxonomy.md` than the provenance/contradiction reading ever was. YC's funding brief names the skills file as the deliverable and explicitly disowns the retrieval-chatbot framing. That is the same line the taxonomy report draws (read-side vs write-side; SKILL.md as the one thing plain memory systems don't cover) — arrived at independently.
- "Keeps it current" is the only lifecycle requirement in the brief. Contradiction *arbitration* is arguably implied by it, but it is not stated, and the RFS cannot be cited as demanding it.

The RFS also supplies the cleanest primary quote for the conflict-of-alignment observation in `talk-analysis.md` L114: YC's own funding brief reads **"We need Garry's G-Brain, but for every business in the world."**

## 7. Not obtained

- **Tom Blomfield's X posts.** The session's WebSearch budget (200/200) was exhausted before this task, and `syndication.twitter.com/srv/timeline-profile/screen-name/t_blom` returns only a stale, unrelated timeline cache with zero "company brain" hits. Unresolved; but it cannot change the verdict, because the verdict rests on YC's own published text, which is fully recovered and invariant. Best estimate: if a Blomfield X post exists, it restates the RFS blurb (as his RFS video description does). Confidence that such a post would introduce provenance/contradiction requirements: low (~10%).
- **A YC blog post** announcing Summer 2026 RFS. `ycombinator.com/blog` shows only a "Requests for Startups" nav entry; no separate announcement post was located. Not needed — the RFS page is itself the primary source.

## Implications for the final answer

1. **Delete the claim that provenance metadata and contradiction detection are in the YC brief.** Specifically fix `findings/rag-taxonomy.md` L67, whose conclusion "So R4 and R5 are in the funding brief, not just the talk" is false. R4 (provenance) and R5 (contradiction arbitration) are in Tan's talk and in GBrain's implementation, but **not** in the RFS.
2. **Reattribute the capability list** in `findings/garry-tan-ecosystem.md` L71 from YC to Modelence, or drop it.
3. **Stop calling `modelence.com/yc-rfs-summer-2026/*` a mirror.** It is vendor marketing copy generated per RFS entry; treat anything on it as third-party, never as YC's words.
4. **Retract the "stale anchor" claim** in `talk-analysis.md` L98, `garry-tan-ecosystem.md` L71/L108, `memory-systems-landscape.md` L81 and `gbrain-architecture.md` L140. `ycombinator.com/rfs#company-brain` still works; the entry lives under the Summer 2026 tab with client-side hash routing.
5. **Use the real text where it is strongest:** as primary evidence that the institutional brief centres *procedural memory* ("executable skills file") and explicitly rejects the RAG-chatbot framing — which supports the synthesis's answer to question (a) more directly than the fabricated requirements did.
6. **Date the RFS 2026-04-28**, eleven weeks before the talk.

---

## Sources

Primary (YC-published):
- Live RFS page: https://www.ycombinator.com/rfs (server-renders Fall 2026 by default; season selector still lists Summer 2026)
- Live RFS data + hash-routing code (the authoritative current text): https://bookface-static.ycombinator.com/vite/assets/RequestsForStartupsPage-MrG_romv.js
- Component registry that loads it: https://bookface-static.ycombinator.com/vite/assets/component_registry-BD_oOytw.js
- Deep link, still functional: https://www.ycombinator.com/rfs#company-brain
- Author profile: https://www.ycombinator.com/people/tom-blomfield
- YC RFS video "Company Brain" (82 s, published 2026-04-28T06:56:20-07:00): https://www.youtube.com/watch?v=IaWIazkWWog

Wayback snapshots of https://www.ycombinator.com/rfs (raw, `id_`):
- https://web.archive.org/web/20260422151545id_/https://www.ycombinator.com/rfs — before publication (no Company Brain)
- https://web.archive.org/web/20260428053810id_/https://www.ycombinator.com/rfs — first snapshot containing it
- https://web.archive.org/web/20260505233712id_/https://www.ycombinator.com/rfs
- https://web.archive.org/web/20260525113314id_/https://www.ycombinator.com/rfs
- https://web.archive.org/web/20260628031528id_/https://www.ycombinator.com/rfs — cleanest full server-rendered copy
- https://web.archive.org/web/20260708135218id_/https://www.ycombinator.com/rfs — last snapshot with Summer 2026 as default tab
- https://web.archive.org/web/20260722203701id_/https://www.ycombinator.com/rfs — default tab switched to Fall 2026
- CDX index used: http://web.archive.org/cdx/search/cdx?url=ycombinator.com/rfs*&from=2026&to=2026&output=text&fl=timestamp,original,statuscode,digest&collapse=digest&limit=200

Third-party (the source of the disputed requirements):
- https://modelence.com/yc-rfs-summer-2026/company-brain — Modelence MVP build brief; origin of "indexed with metadata: author, date, access level, related entities" and "Detect contradictions and flag for resolution"

Corroborating:
- https://raw.githubusercontent.com/garrytan/gbrain/master/README.md — L7 links `ycombinator.com/rfs#company-brain`

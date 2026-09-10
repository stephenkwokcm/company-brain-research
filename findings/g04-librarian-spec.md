# g04 — The Librarian, from library and archival science: a buildable spec

**Key:** `g04-librarian-library-science`
**Written:** 2026-09-10
**Gap addressed:** `findings/completeness-critic.md` §7 — *"The librarian is defined three incompatible ways across the corpus (C2) and library science itself is absent. 'Librarian' is the load-bearing half of Tan's own definition, and the profession has a century of theory on exactly this."*
**Method:** primary standards and manuals fetched live (CREW manual PDF from the Internet Archive after TSLAC de-published it; SAA guidelines PDF; OAIS CCSDS 650.0-M-2 PDF; SAA Dictionary entries; IFLA repository; NARA; OCLC). GBrain claims are taken from `findings/v06a-librarian-in-code.md` and `findings/v06b-librarian-skeptic.md`, both read at commit `43597b19`, with one fact re-verified directly against `raw.githubusercontent.com`.

---

## TL;DR

1. **Tan's "librarian … whose actual job is pruning" is, almost word for word, the *weeding* function of collection management** — a job with a published manual, a named formula, six lettered decision factors, an annual rate target, and a review cadence. The profession's answer to "who prunes and how" is not vague; it is `X/Y/MUSTIE`, 5% a year, whole collection every five years ([CREW, TSLAC 2012](https://web.archive.org/web/20181220190215/https://www.tsl.texas.gov/sites/default/files/public/tslac/ld/ld/pubs/crew/crewmethod12.pdf)).
2. **The single most useful idea library science has that no memory system in this corpus implements is a control law, not a threshold.** CREW: *"you should weed about the same amount as you are adding to the collection."* Weeding rate slaved to acquisition rate converts pruning from an unbounded judgment problem into a **bounded ranking problem** — rank everything by weed score, act on the top N where N = pages added this period. That structurally cannot produce GBrain's failure mode of a review queue that "reached 32.5k rows across ~2.9k pages, growing 2–6k rows/day" ([gbrain#3269](https://github.com/garrytan/gbrain/issues/3269), via `v06b`).
3. **OAIS states the correct invariant and GBrain satisfies only half of it.** An OAIS must *"[f]ollow documented policies and procedures which ensure that the information is preserved against all reasonable contingencies … ensuring that it is never deleted unless allowed as part of an approved strategy. **There should be no ad-hoc deletions**"* ([CCSDS 650.0-M-2 §3.1](https://ccsds.org/Pubs/650x0m2.pdf), June 2012). "No ad-hoc deletions" is not "no deletions" — it presupposes an approved disposal strategy. GBrain has the prohibition and no schedule. **That is the precise shape of the gap.**
4. **FRBR/IFLA-LRM would have prevented GBrain's hardest contradiction bug.** The probe needed six verdict classes because it could not separate *"this changed"* from *"this is wrong"*. In bibliographic terms those are two **Expressions of one Work** related by succession — not two Works in conflict. Arbitration belongs at the Work level; GBrain arbitrates at the chunk level, which is the Item level.
5. **GBrain already collects the exact signal CREW weeds on and spends it on the opposite function.** `pages.last_retrieved_at` — *"NULL = never retrieved"* — is fully B-tree indexed for one consumer: `gbrain lsd`'s stale-page query, which selects never-read pages **in order to generate more pages** (verified directly at `src/schema.sql:122-126, 270-276`). CREW's second figure is *"years since its last recorded circulation."* The circulation desk is wired to the acquisitions department.
6. **Macro-appraisal says the cheap, high-leverage decision is at the source level, not the page level** (Cook, National Archives of Canada, 1991 — [SAA Dictionary](https://dictionary.archivists.org/entry/macroappraisal.html)). Appraise *which company functions get documented at all*; that is a one-page human artifact, not an LLM call per document. GBrain's `sources` table plus `db_tracked`/`db_only` is the substrate for this and nothing uses it to stop ingesting anything.
7. The Librarian spec in §4 below is buildable on GBrain today: **six roles, seven cadences, a per-class `A/U/MUSTIE+P` formula table, eight decision rules with numeric thresholds, a disposal slip, and nine metrics** — of which the two that matter most are **queue clearance ratio ≥ 1.0** and **weeding rate ≈ acquisition rate**.

---

## 1. Why the profession is the right frame here

Three reports in this corpus define "librarian" three incompatible ways (contradiction **C2**). The reason they can disagree is that the talk itself uses the word in two senses and defines neither:

- **Sense A — hygiene.** *"the primitive is not memory. It's memory plus hygiene, provenance on every fact, contradiction checks when new information collides with the old, and a librarian, human plus agent, whose actual job is pruning."* (transcript 14:46–15:03)
- **Sense B — selection.** *"the librarian that picks the three books"* (17:41); *"A library of the librarian, the right three books open at the right moment"* (19:28).

In the profession these are two different jobs with different literatures, different job titles and different funding lines: **collection management** (Sense A: appraisal, weeding, retention, deaccessioning) and **reference / readers' advisory** (Sense B: the reference interview, ready reference, selection of sources for a question). Every memory system in this corpus, GBrain included, is excellent at Sense B and unstaffed at Sense A. Naming them separately dissolves C2: `gbrain-architecture.md` was describing Sense B machinery and calling it Sense A.

A third distinction the corpus has been eliding, and which the standards draw sharply:

| Term | Definition (SAA) | Scope |
|---|---|---|
| **Weeding** | *"The process of identifying and removing unwanted materials from a larger body of materials."* | Items inside a collection; routine; no external approval |
| **Deaccessioning** | *"The process by which an archives, museum, or library **permanently removes accessioned materials** (i.e., collections, series, record groups) from its holdings. Note: This is not to be confused with weeding."* | Whole collections/series; requires approval, documentation, donor notice |
| **Reappraisal** *(also retention review)* | *"The process of identifying materials that no longer merit preservation and that are candidates for deaccessioning."* | The *decision*, always upstream of deaccessioning |

([SAA, *Guidelines for Reappraisal and Deaccessioning*, approved by SAA Council May 2012, Definitions p.3](https://www2.archivists.org/sites/all/files/GuidelinesForReappraisalAndDeaccessioning-May2012.pdf).) The guidelines' hard rule: *"Reappraisal does not always lead to deaccessioning. However, **reappraisal is required as a first step towards any specific act of deaccessioning**."* A company brain needs all three as distinct operations with distinct authority levels; today GBrain has one (a 72h garbage collector) and calls it purge.

---

## 2. Seven doctrines, mapped

### 2.1 Appraisal — the ingest gate

**Doctrine.** Appraisal is *"the process of identifying materials offered to an archives that have sufficient value to be accessioned"* and *"the process of determining the length of time records should be retained"* ([SAA Dictionary: appraisal](https://dictionary.archivists.org/entry/appraisal.html)). Schellenberg's frame: records carry **primary value** (to the creator, for the original purpose) and **secondary value** (to later researchers), the latter split into **evidential value** — *"the value that depends on the importance of the matter evidenced, i.e. the organization and functioning of the agency that produced the records"* — and **informational value**, *"the overall usefulness of the content"* ([SAA Dictionary: evidential value](https://dictionary.archivists.org/entry/evidential-value.html), citing Schellenberg 1996, Buck 1945a, Millar 2014).

**Company-brain operation: the ingest gate, with a two-axis score.** The single most common company-brain modelling error is scoring documents on one axis ("importance"). Schellenberg's split is directly actionable:

- **Evidential value** — does this document show *how the company decided or operated*? (decision records, postmortems, org changes, contract executions.) High evidential value ⇒ keep the artifact **verbatim and forever**, even if nobody ever reads it, because it is the only proof the decision happened.
- **Informational value** — does the *content* answer future questions? (a pricing table, a customer's stated constraint.) High informational value with low evidential value ⇒ keep the **synthesis**, discard the carrier. This is exactly the "raw transcript vs. compiled truth" question, and Schellenberg answers it: transcripts have informational value only; **synthesise then discard**. Board minutes have evidential value; **never discard, never rewrite**.

**GBrain today.** One axis, one number: the `synthesize` phase's cheap-judge triage at `DEFAULT_TRIAGE_THRESHOLD = 0.5` with a `rescue_floor` of 0.30 (`src/core/cycle/synthesize.ts:129`). Below threshold the file is never synthesised — read-time gated, so retuning re-gates with no new LLM calls, which is a genuinely good design. But a single salience score cannot express "worthless content, irreplaceable evidence," which is the class that matters most legally.

### 2.2 Macro-appraisal — appraise sources, not pages

**Doctrine.** Macro-appraisal is *"an analysis of the functions of an organization to determine the relative importance of those activities and set priorities for documentation"* (Brown 1995), pioneered by **Terry Cook** and colleagues at the National Archives of Canada in 1991; it *"shifts the focus in appraisal from the actual records (the product of creation) to their context of their creation (the process)"* (Cook 2004), a *"top-down approach based on functional analysis"* (Lemieux 1998), *"followed by microappraisal to determine which records are kept permanently"* ([SAA Dictionary: macroappraisal](https://dictionary.archivists.org/entry/macroappraisal.html)).

**Company-brain operation: a one-page Documentation Plan, written by a human, that names the company functions to document and at what depth — and by omission, what to stop ingesting.** This is the cheapest intervention in the whole spec and the only one that cannot be delegated to an agent, because it is a statement of what the company is for. Cost model: macro-appraisal is O(number of channels), microappraisal is O(number of documents). GBrain's per-document judge at ~$0.0006/call over a 155K-page brain is microappraisal without macro-appraisal — paying per-document prices for a decision that should have been made once per channel.

**GBrain today.** `sources` (multi-brain tenancy, `config` JSONB) and the `db_tracked` vs `db_only` split in `gbrain.yml` are precisely the right substrate — a per-source policy hook. Nothing writes a *stop collecting* policy into it. The storage tier is a curation decision about **where bytes live**, not about **whether the function is documented at all**.

### 2.3 Provenance and *respect des fonds* — filing rules and back-linking

**Doctrine.** *Respect des fonds* is *"[t]he principle maintaining records according to their origin and in the units in which they were originally accumulated"* (Posner 1940a), emerged in Belgium and France c.1840, and *"has become the main principle of archives administration"*; it requires respecting not just separation of fonds but **their internal organizational structure** (Jimerson 2009). Prussian archivists refined it into the *provenienzprinzip* (Duranti & Franks 2015) ([SAA Dictionary: respect des fonds](https://dictionary.archivists.org/entry/respect-des-fonds.html)).

**Company-brain operation.** Two rules that follow directly and that most memory systems break:

1. **Never merge two sources into one page.** A synthesis page ("what we know about ACME") is a *finding aid*, not a fonds. The underlying evidence stays partitioned by origin. GBrain's per-page `compiled_truth` (rewritten) over an append-only `timeline` (cited evidence) is exactly this shape and is the strongest thing in the repo.
2. **Original order is a retrieval signal, not an artifact.** The order in which one channel produced records is evidence about the process. Chunking that destroys thread/meeting order destroys evidential value. Practical rule: chunk within a fonds, never across.

### 2.4 Collection development policy — declaring what the brain is for

**Doctrine.** SAA's guidelines make the collecting policy the *precondition* for any disposal decision: *"Review your repository's collecting policy. If there is none, develop a written collecting policy that addresses subject/geographical areas or types of materials to be acquired… **It is impossible to make accurate and defensible deaccession decisions if it is not clear what the repository seeks to acquire in the first place.**"* A separate **collection management policy** must define *"the authority and approval processes for deaccessioning decisions; identifying acceptable methods of disposal; delineating acceptable expenditures… and identifying a process for dealing with collections with unknown provenance"*, be *"formally approved by repository administration and be made available to the public, preferably online"* ([SAA 2012, §II.2–II.3, pp.8–9](https://www2.archivists.org/sites/all/files/GuidelinesForReappraisalAndDeaccessioning-May2012.pdf)).

**Company-brain operation.** Two committed markdown files at the root of the brain repo, reviewed annually:
- `COLLECTING-POLICY.md` — what we ingest, from which channels, at what depth, and explicitly what we do not.
- `COLLECTION-MANAGEMENT-POLICY.md` — who may weed, who must approve a deaccession, the enumerated disposal actions, what happens to unsourced pages.

**GBrain today.** `skills/_brain-filing-rules.md` is a *filing* policy (where things go once accepted). There is no collecting policy and no management policy, and the code's fallback is the honest but unhelpful one: `brain-score-recommendations.ts` classifies every unmapped check as `human_only` with rationale `"unmapped check"`. In library terms, the repository has a shelving scheme and no acquisitions mandate — so every disposal decision is undecidable by construction, exactly as SAA predicts.

### 2.5 CREW / MUSTIE — the weeding formula, and the rate law

**Doctrine.** **CREW = Continuous Review, Evaluation, and Weeding** ([CREW manual](https://web.archive.org/web/20181220190215/https://www.tsl.texas.gov/sites/default/files/public/tslac/ld/ld/pubs/crew/crewmethod12.pdf), rev. Jeanette Larson, Texas State Library and Archives Commission, 2012, CC BY-NC-ND; TSLAC has since archived the manual with no plans to update, [notice](https://www.tsl.texas.gov/ld/pubs/crew/index.html)). The formula has three parts:

> *"1. The first figure refers to the years since the book's latest copyright date (age of material in the book); 2. The second figure refers to the maximum permissible time without usage (in terms of years since its last recorded circulation…); 3. The third refers to the presence of various negative factors, called MUSTIE factors… For example, the formula "8/3/MUSTIE" means: "Consider a book in this class for discard when its latest copyright is more than eight (8) years ago; and/or, when its last circulation or in-house use was more than three (3) years ago; and/or, when it possesses one or more of the MUSTIE factors."… If any one of the three parts of the formula is not applicable to a specific subject, the category is filled with an "X"."*

MUSTIE, verbatim: **M** = Misleading (and/or factually inaccurate); **U** = Ugly (worn and beyond mending or rebinding); **S** = Superseded (by a truly new edition or by a much better book on the subject); **T** = Trivial (of no discernible literary or scientific merit; usually of ephemeral interest at some time in the past); **I** = Irrelevant to the needs and interests of your community; **E** = the material or information may be obtained expeditiously **Elsewhere**.

Observed formula distribution across the manual's Dewey classes: `10/3/MUSTIE` ×17, `5/3/MUSTIE` ×15, `X/3/MUSTIE` ×7, `5/2/MUSTIE` ×6, `X/2/MUSTIE` ×4, down to `15/5/MUSTIE` and `X/1/MUSTIE`. *"Most formulas include a "3" in the usage category because few libraries can afford to keep items in the collection that have not circulated or been used in-house within a three year period."* The age figure varies by class; the use figure barely does.

**The rate law and cadence.** *"The CREW method calls for systematic and continuous weeding"*: staff pull shabby/outdated items **weekly**; catalogue reports identify *"shelf sitters"* **quarterly**; *"Monthly targets should be established for looking at specific areas"*; *"the entire collection should be reviewed and weeded if necessary, at least once every five years"*; and the two numbers that matter — *"**you should weed about the same amount as you are adding to the collection** unless you are in a developing mode"* and *"A rule of thumb held by many library professionals is that about **5% of the collection be weeded every year** (Slote, *Weeding Library Collections*, 1997, p.14). This allows for turnover of the collection every twenty years."*

**Company-brain operation.** See the formula table and the rate law in §4.3 and §4.4. The adapted acronym is **MUSTIE+P** (§4.2): the six factors survive translation almost unchanged, with **U** re-read as *Unsourced* (the digital analogue of "you don't want to touch it") and one genuinely new factor, **P** = *Poisoned*, that the physical library never faced.

**Also from CREW: the disposal slip.** The manual's final page is a tear-off form with enumerated actions — *Bindery · Discard · Mend/Preserve · Book Sale · Promote · Replacement/New Edition · Donate to: · Sent To: · Check Database for other locations of this title · **Authorizing Agent**.* Three features worth stealing: the action is picked from a **closed set**; "check for other locations" is a **mandatory pre-check** before destroying anything; and a named **authorizing agent** signs. GBrain's `forget()` writes `forgotten: <reason>` into the fence — half a disposal slip, missing the enumerated action and the signature.

### 2.6 Retention schedules — disposition by class, not by judgment

**Doctrine.** A retention schedule is *"[a] document that identifies and describes an organization's records, usually at the series level, and provides instructions for the disposition of records throughout their life cycle"* (SAA 2012, Definitions). NARA's **General Records Schedules** are disposition authorities for records *"documenting administrative or support functions"* and — the key property — *"**Use of the GRS is mandatory. Agencies must use the GRS unless they can justify the use of an agency-specific schedule**"* ([NARA, GRS](https://www.archives.gov/records-mgmt/grs), page last reviewed June 12, 2026). SAA's guidelines note that for institutional archives *"disposition will often be regulated by official records schedules that may have statutory authority."*

**Company-brain operation.** A retention schedule is the mechanism that makes deletion **default and unremarkable**, because the decision was taken once, in advance, at the *class* level, by an authority — so no per-item judgment and no reviewer is needed at disposal time. This is the missing half of OAIS's "no ad-hoc deletions."

Concretely: `retention.yml` in the brain repo, one row per page class, each with `retention`, `trigger`, `disposition`, `authority`, `review_by`. Raw meeting transcripts: *destroy 90 days after synthesis*. Scraped web pages: *destroy 180 days after last retrieval*. Board minutes: *permanent*. Candidate interview notes: *destroy at 1 year* (this one is also GDPR/EEOC-shaped). The agent executes the schedule without asking; the human changes the schedule, not the individual decision.

**GBrain today.** `v06b` grepped `KNOWN_CONFIG_KEYS` and found **no retention or TTL config key for knowledge content** — only cache TTLs, an OAuth TTL, and `memory.auto_writeback_transient_ttl` (`3d`, on a default-OFF feature). Fact half-lives (`event 7d / commitment 90d / preference 90d / belief 365d / fact 365d / idea 365d`) look like a schedule but are not one: `decay.ts` is a *"Pure function. No side effects. No I/O."* whose only consumers sort and print. **A retention schedule that never fires is a ranking heuristic.**

### 2.7 Authority control and FRBR/RDA — entity canonicalisation and contradiction arbitration

**Authority control.** VIAF *"combines multiple name authority files into a single"* service, *"lower[ing] the cost and increas[ing] the utility of library authority files by matching and linking widely used authority files"* across *"more than 50 organizations from more than 30 countries"*, matching, linking and grouping contributed records into clusters ([OCLC, VIAF](https://www.oclc.org/en/viaf.html)).

The part worth stealing is what an authority *record* contains beyond a canonical string: (a) the **established form**; (b) ***see* references** — variant forms that redirect to it; (c) ***see also* references** — related but *distinct* entities; (d) **qualifiers** that disambiguate near-collisions (dates, occupation, affiliation); and (e) a **cataloguer's note** citing the evidence used to establish the heading.

GBrain has (a) and (b) (canonical slugs, alias hop, phantom-redirect slug merge). It has no (c), no (d), no (e) — and the failure that predicts is exactly [gbrain#4222](https://github.com/garrytan/gbrain/issues/4222) via `v06b`: `junk_entity_hubs`, near-empty entity pages with *"generic-token names like Will"* that accreted huge edge counts from the regex auto-linker, surfaced as *"Warn + list only."* An authority file with qualifiers and an "unused form — use the qualified form" note is the century-old fix, and it is a data problem, not an LLM problem.

**FRBR / IFLA LRM.** The IFLA Library Reference Model, published **January 2018**, is *"a high-level conceptual reference model developed within an entity-relationship modelling framework"* consolidating FRBR, FRAD and FRSAD ([IFLA repository](https://repository.ifla.org/handle/20.500.14598/40)); RDA is the cataloguing code built on it. The WEMI stack maps onto a company brain with unusual precision:

| WEMI | Company brain | GBrain artifact |
|---|---|---|
| **Work** — the abstract intellectual content | The claim/topic: *"ACME's contract terms"* | (absent — no entity above the page) |
| **Expression** — a realisation of the Work | The synthesis as of a date | `pages.compiled_truth` |
| **Manifestation** — an embodiment | The markdown page/version | the `.md` file, `generation` |
| **Item** — a single exemplar | The chunk/embedding row | `content_chunks` |

**Why this matters more than it looks.** GBrain's contradiction probe needed **six** verdict classes (`no_contradiction | contradiction | temporal_supersession | temporal_regression | temporal_evolution | negation_artifact`) because, in its own RFC's words, it *"can't distinguish *this changed* from *this is wrong*"* after a production run surfaced ~115 HIGH findings that had to be walked by hand. In FRBR terms that distinction is structural, not semantic: **two Expressions of one Work related by succession** vs. **two Works in genuine conflict**. Arbitration should run at the Work level over a `(subject, relation, object)` key — which is precisely the result `memory-hygiene.md` reports from MemStrata (cosine separates the two at AUROC 0.59; a deterministic SPO supersession rule takes evolving-knowledge accuracy from 0.20–0.47 to 0.95–1.00). Library science and the 2026 RAG literature converged on the same answer from opposite directions. GBrain arbitrates at the **Item** level (chunk pairs), which is the one level at which the question is undecidable.

### 2.8 OAIS — the lifecycle frame and the load-bearing sentence

**Doctrine.** OAIS (CCSDS 650.0-M-2 / ISO 14721) defines six **functional entities** — Ingest, Archival Storage, Data Management, Administration, Preservation Planning, Access — and three information packages: **SIP** *"delivered by the Producer to the OAIS for use in the construction or update of one or more AIPs"*; **AIP** *"consisting of the Content Information and the associated Preservation Description Information (PDI), which is preserved within an OAIS"*; **DIP** *"derived from one or more AIPs, and sent by Archives to the Consumer in response to a request."* An archive preserves for a **Designated Community**, and must *"[e]nsure that the information to be preserved is Independently Understandable to the Designated Community … without needing special resources such as the assistance of the experts who produced the information."* And §3.1, the sentence this whole report turns on: *"Follow documented policies and procedures which ensure that the information is preserved against all reasonable contingencies … ensuring that it is never deleted unless allowed as part of an approved strategy. **There should be no ad-hoc deletions**."* ([CCSDS 650.0-M-2](https://ccsds.org/Pubs/650x0m2.pdf), June 2012 — note this copy is stamped CCSDS HISTORICAL DOCUMENT; a Pink Book revision is in progress, so treat the wording as the ISO 14721:2012 text.)

**Mapping.**

| OAIS entity | Company-brain operation | GBrain |
|---|---|---|
| **Ingest** | accession gate, provenance stamp, quarantine | ✅ strong: mandatory `source`, `provenance_required` error, content-sanity hard block, triage 0.5 |
| **Archival Storage** | the git markdown system of record | ✅ strong: repo is authoritative, DB is a rebuildable cache |
| **Data Management** | index, graph, catalogue | ✅ strong: HNSW + BM25 + typed edges + RRF |
| **Access** | retrieval, autocut, token budget | ✅ strong — this is Sense B |
| **Administration** | policy, audit, cost control | 🟡 partial: 117 doctor checks, cost ceilings; no policy objects |
| **Preservation Planning** | *monitor the community, plan disposition and migration* | ❌ **absent** |

"Independently Understandable to the Designated Community" is also a testable requirement that no memory benchmark in this corpus measures: can a page be understood by an agent *without* the author's tacit context? That is a better hygiene KPI than "has a citation."

### 2.9 Ranganathan — why you prune when storage is free

The obvious objection to all of this is that a byte costs nothing, so why delete? The profession's answer predates the question by ninety-five years. CREW opens by grounding weeding in **Ranganathan's Five Laws of Library Science** (cited in the manual as Asia Pub. House, 1963; first published 1931): *1. Books are for use. 2. Every reader his book. 3. Every book its reader. 4. **Save the time of the reader.** 5. A library is a growing organism.*

Law 4 is the objective function. You weed to protect the reader's attention and the collection's precision, **not** to save shelf space. In a company brain the reader is an agent with a token budget, and precision at k is exactly "the time of the reader." Law 5 is the counterweight and is why "prune everything" is also wrong. This is the cleanest available rebuttal to "storage is cheap" — and, notably, it is also exactly Tan's own framing at 12:45: *"who decides which three books are open on that desk."*

### 2.10 MPLP — the processing-cost discipline

Greene & Meissner's *"More Product, Less Process: Revamping Traditional Archival Processing"* (*The American Archivist* 68:2, 2005, pp. 208–263) argues that over-processing backlogs is worse than under-processing them, and proposes a "golden minimum" of arrangement and description sufficient to make material findable. **Confidence: medium — the Allen Press article page returned HTTP 403 and I could not read the text directly at first hand; the citation is from the SAA bibliography and is standard, but treat the paraphrase, not the citation, as unverified.** The company-brain analogue is real and cheap: a **minimally-processed lane** — accession with provenance and a title, index for retrieval, and do *not* run extraction/synthesis/enrichment until something is actually retrieved from it. GBrain's `db_only` tier is the storage half of this; the processing half (defer enrichment until first read) is not implemented, and `enrich_thin` — which develops stub pages proactively, default OFF — is MPLP inverted.

---

## 3. The mapping table

| Library/archival doctrine | Primary source | Company-brain operation | Present in GBrain v0.48.5.0? |
|---|---|---|---|
| Appraisal (primary/secondary, evidential/informational) | Schellenberg via SAA Dictionary | Ingest gate scoring on **two** axes | 🟡 one axis, triage 0.5 |
| Macro-appraisal (functional, top-down) | Cook 1991 via SAA Dictionary | `DOCUMENTATION-PLAN.md`: which functions get documented, per-source ingest policy | ❌ substrate exists (`sources`), unused |
| Respect des fonds / provenance | Posner 1940a via SAA Dictionary | Never merge sources; chunk within a fonds; evidence partitioned by origin | ✅ compiled_truth over append-only timeline |
| Collecting + collection management policy | SAA 2012 §II.2–3 | `COLLECTING-POLICY.md`, `COLLECTION-MANAGEMENT-POLICY.md` | ❌ filing rules only |
| Weeding formula `X/Y/MUSTIE` | CREW 2012 | Per-class `A/U/MUSTIE+P` (§4.3) | ❌ |
| Weeding rate law (weed ≈ acquire; ~5%/yr) | CREW 2012 / Slote 1997 | Bounded ranked weed queue (§4.4) | ❌ — and the unbounded queue failed (#3269) |
| Last-circulation as the use signal | CREW 2012 | `last_retrieved_at` drives demotion | 🟡 collected + indexed; wired to `lsd` (idea generation) |
| Reappraisal → deaccessioning, with authority | SAA 2012 | Three-tier disposal authority (§4.5) | ❌ |
| Disposal slip: closed action set + authorizing agent | CREW 2012 p.107 | Every weed writes a slip (§4.6) | 🟡 `forget()` writes a reason, no action/agent |
| Retention schedule, mandatory by class | NARA GRS; SAA 2012 | `retention.yml`, executed without review | ❌ no knowledge-retention config key |
| Authority control (see / see-also / qualifier / cataloguer's note) | VIAF-OCLC; NACO | Entity canonicalisation + collision refusal | 🟡 canonical + see only → junk entity hubs |
| FRBR/LRM Work-Expression-Manifestation-Item | IFLA LRM 2018 | Arbitrate contradictions at **Work** level on an SPO key | ❌ arbitrates at Item (chunk) level |
| OAIS six entities; "no ad-hoc deletions" | CCSDS 650.0-M-2 §3.1 | Whole-lifecycle frame; **Preservation Planning** as a named role | 🟡 5 of 6 entities; Preservation Planning absent |
| Independently Understandable | CCSDS 650.0-M-2 §3.1 | KPI: page comprehensible without the author | ❌ unmeasured anywhere in the corpus |
| Ranganathan Law 4 (save the reader's time) | Ranganathan 1931/1963 via CREW | Weeding justified by precision, not storage | — (framing) |
| MPLP / golden minimum | Greene & Meissner 2005 *(medium confidence)* | Minimally-processed lane; enrich on first read | 🟡 `db_only` storage tier only |

---

## 4. The Librarian spec

Written to be implementable on GBrain as it stands. Nothing here needs a new model; most of it needs a policy file, a scheduled job, and one ranking query.

### 4.1 Roles — who is human, who is agent

Six roles. The split follows the profession's own line, which is also the line GBrain's code draws in `brain-score-recommendations.ts`: **agents produce evidence and execute schedules; humans set policy and authorise irreversible acts.**

| # | Role | Human or agent | Owns | Authority |
|---|---|---|---|---|
| R1 | **Collection Development Officer** | Human (a founder/exec, ~1h/quarter) | `COLLECTING-POLICY.md`, `DOCUMENTATION-PLAN.md`, the macro-appraisal | Decides what the company documents at all |
| R2 | **Accessioner** | Agent (continuous) | Ingest gate, provenance stamp, two-axis appraisal, quarantine | May **refuse** an accession; may never delete an accessioned page |
| R3 | **Cataloguer** | Agent (nightly) | Filing rules, back-links, tags, authority control, consolidation | May merge on an **authority-file match**; must refuse on a qualifier collision |
| R4 | **Weeder** | Agent proposes, human disposes (weekly, 30 min) | The ranked weed queue, MUSTIE+P scoring, disposal slips | Agent may **demote** and **supersede** autonomously; only the human may **destroy** |
| R5 | **Records Officer** | Human sets, agent executes | `retention.yml`, legal holds, GDPR/PII erasure | Schedule-driven destruction needs **no** per-item review |
| R6 | **Reference Librarian** | Agent (per query) | Retrieval, intent classification, autocut, token budget, "here is what I did not find" | Sense B — already shipped |

Two roles the corpus has been missing entirely: **R1** (nobody has written down what the brain is for, so no disposal decision is decidable) and **R5** (nobody has a schedule, so every deletion is ad-hoc and therefore forbidden).

### 4.2 MUSTIE+P — the negative factors, translated

| Factor | Library definition (CREW) | Company-brain test | Computable? |
|---|---|---|---|
| **M** Misleading | factually inaccurate due to new discoveries or revisions | Contradicted by a higher-authority source with a later `effective_date` | Partly — needs the Work-level SPO key |
| **U** Unsourced *(was "Ugly")* | worn beyond mending | No `source`, dead citation URL, or provenance chain broken | ✅ deterministic |
| **S** Superseded | by a truly new edition or a better book | A later Expression of the same Work exists | ✅ deterministic on an SPO key |
| **T** Trivial | no discernible merit; ephemeral interest | Below the salience floor **and** never retrieved | ✅ deterministic |
| **I** Irrelevant | to the needs of your community | Outside `COLLECTING-POLICY.md` scope | ✅ once R1 writes the policy |
| **E** Elsewhere | obtainable expeditiously elsewhere | The authoritative copy lives in a system of record (Git, the CRM, the HRIS, the ledger) — keep a **pointer**, not a copy | ✅ by source class |
| **P** Poisoned *(new)* | — | Untrusted-provenance content that asserts instructions or facts; the injection class OWASP ranks T1 | 🟡 needs a classifier; GBrain's guardrails are observe-only and fail-open |

**P** is the one factor with no physical-library ancestor and it is the one that must be **destroyed** rather than demoted. Everything else is reversible.

### 4.3 The formula table — `A/U/MUSTIE+P` by page class

Read exactly as CREW: **A** = months since the content's `effective_date`; **U** = months since `last_retrieved_at` (**NULL counts as ∞**); **X** = not applicable to this class. *"Consider for weeding when A exceeded and/or U exceeded and/or any MUSTIE+P factor holds."* A hit means **enter the ranked queue**, not "delete."

| Page class | Formula | Default disposition on hit | Rationale |
|---|---|---|---|
| Raw meeting/call transcripts | `3/3/MUSTIE+P` | Destroy per schedule after synthesis | Informational value only; the synthesis carries it |
| Scraped web / news / social | `6/6/MUSTIE+P` | Destroy; keep the URL | **E** is presumptively true |
| Pricing, comp bands, vendor terms | `6/6/MUSTIE+P` | Supersede | Fastest-changing, highest blast radius when stale |
| People & org (roles, reporting) | `12/12/MUSTIE+P` | Supersede | Role changes are Expressions, not contradictions |
| Customer conversations | `24/18/MUSTIE+P` | Demote to cold | Long-tail informational value |
| Company/competitor profiles | `12/12/MUSTIE+P` | Supersede or demote | |
| Auto-extracted entity stubs | `X/6/MUSTIE+P` | Destroy if still `unverified` at 6 months | Never accessioned in the first place |
| Agent-generated ideas (`lsd` output) | `3/3/MUSTIE+P` | Destroy | Ephemeral by the generator's own default |
| SKILL.md / process files | `6/3/MUSTIE+P` | **Repair, never destroy**; eval-gated edit | Tan's third failure mode; must clear the no-regression gate |
| Decision records / ADRs | `X/X/MUSTIE+P` | Supersede only | **Evidential value** — never age-weeded, never use-weeded |
| Postmortems / incident reports | `X/X/MUSTIE+P` | Supersede only | Evidential value |
| Board minutes, contracts, filings | *retention schedule only* | Permanent | Not a weeding decision at all |
| Candidate/employee records | *retention schedule only* | Destroy at schedule | Legal, not curatorial |

The bottom three rows are the important structural point: **records with evidential or legal value leave the weeding system entirely** and are governed by R5's schedule. Conflating them is how a company brain deletes the one document its lawyers needed.

### 4.4 The rate law — the core decision rule

```
Let  A_t = pages accessioned in period t
     W_t = pages weeded in period t
Target:    W_t ≈ A_t            (CREW: "weed about the same amount as you are adding")
Long run:  ΣW / |corpus| ≈ 5%/yr → full turnover ≈ 20 years (CREW/Slote)
Exception: developing mode (first ~6 months of a new brain) → W_t = 0
```

Implementation: score every page by MUSTIE+P weight, rank descending, **truncate the review queue at N = A_t**, discard the tail until next period. Three consequences worth stating plainly:

1. **The queue can never explode.** GBrain's `take_proposals` grew to 32.5k rows at 2–6k/day because it was a filter with no budget. A truncated ranked queue is a budget with no filter.
2. **Reviewer time is bounded and knowable** — it scales with write volume, which the company controls, not with corpus size.
3. **It degrades gracefully.** Miss a week and you lose the *lowest-ranked* candidates, not a random sample.

### 4.5 Decision rules with thresholds

| # | Rule | Threshold | Actor | Reversible? |
|---|---|---|---|---|
| D1 | **Accession** | Two-axis: accept if `informational ≥ 0.5` **OR** `evidential ≥ 0.3`. Rescue band `0.30–0.50` on ≥2 verified quoted segments (GBrain's existing shape, second axis added) | R2 agent | n/a |
| D2 | **Refuse** | Junk-pattern regex hit, or untrusted channel asserting instructions (**P**) | R2 agent | Yes — logged, re-submittable |
| D3 | **Quarantine** | Auto-extracted stub, untrusted provenance ⇒ `status: unverified`, excluded from authority boost | R2 agent | Yes |
| D4 | **Canonicalise** | Merge on authority match **only when** the qualifier set is identical; **refuse and flag** on generic-token names (<2 tokens, no qualifier) — kills the junk-entity-hub class | R3 agent | Yes — redirect, not delete |
| D5 | **Supersede** | Same Work-level SPO key **and** later `effective_date` **and** source authority ≥ incumbent ⇒ stamp `valid_until`. Otherwise it is a genuine contradiction ⇒ queue for the human | R3 agent | Yes |
| D6 | **Demote hot→cold** | `last_retrieved_at` NULL or > 180 days **and** salience below class median ⇒ move to `db_only`, drop from the default retrieval surface, keep the row | R4 agent | Yes |
| D7 | **Weed (destroy)** | In the top-N ranked queue **and** ≥2 MUSTIE+P factors **and** a disposal slip signed by a human | R4 agent proposes, human signs | 72h soft-delete window (GBrain already has this) |
| D8 | **Schedule disposal** | `retention.yml` trigger fires, no legal hold ⇒ destroy without review; log to the public deaccession log | R5 agent | No — this is the point |

Two guards carried over from GBrain because they are correct: the **mass-reconcile valve** (refuse any sweep touching >50% of a source's pages, treat it as a bug) and the **cost ceiling** per phase. Add a third: **no weeding run may destroy more than `A_t` pages**, which is the rate law enforced as a safety interlock.

### 4.6 The disposal slip

Every destroy/demote/supersede writes one record, into the page's own timeline **and** an append-only `DEACCESSION-LOG.md` in the repo:

```yaml
page: companies/acme-corp
action: destroy            # one of: repair | merge | demote | supersede | export | destroy
factors: [S, E]            # MUSTIE+P letters that fired
formula: 12/12/MUSTIE+P    # the class formula applied
evidence:
  last_retrieved_at: null
  effective_date: 2024-11-03
  superseded_by: companies/acme-corp-2026
elsewhere_check: "authoritative copy in Salesforce acct 0031Q…"   # mandatory pre-destroy
authorizing_agent: [email redacted]      # required for `destroy` only
proposed_by: weeder-agent@2026-09-10
recoverable_until: 2026-09-13T00:00Z
```

`elsewhere_check` is CREW's *"Check Database for other locations of this title"* and is **mandatory before any destroy** — the digital analogue of not being the last library holding a title. SAA's transparency principle applies to the log: *"Never should reappraisal and deaccessioning be done secretly or 'under the table'."*

### 4.7 Cadence

| Interval | Who | What |
|---|---|---|
| **Continuous** (write time) | R2 agent | Accession gate, provenance stamp, quarantine, refuse |
| **Nightly** | R3 agent | Catalogue: back-links, tags, authority control, consolidation, embeddings, salience; **compute weed scores** |
| **Weekly, ~30 min** | R4 human + agent | The weeding shelf: review the top-`A_t` ranked candidates; sign or reject disposal slips. *(CREW: staff pull items for review weekly)* |
| **Monthly** | R3 + R4 | One collection area gets a deep pass on rotation; clear the authority-merge queue; review skill-file eval deltas. *(CREW: "Monthly targets… for specific areas")* |
| **Quarterly** | R1 + R4 | Shelf-sitter report (never-retrieved + >180d); run the contradiction probe; compare actual acquisitions against `COLLECTING-POLICY.md`. *(CREW: quarterly catalogue reports for shelf sitters)* |
| **Annually** | R1 + R5 | Reappraise the highest-cost source; review and re-approve `retention.yml`; publish the deaccession log |
| **Every 5 years** | R1 | Whole-brain review. *(CREW: "the entire collection should be reviewed and weeded if necessary, at least once every five years")* |

At a 25-person company with GBrain's own claimed scale, the human load is ~30 min/week (R4) + ~1 h/quarter (R1) + ~2 h/year (R5). That is the honest cost of the word "librarian," and it is small — but it is not zero, and no amount of model capability removes R1 or R5, because both are statements of institutional intent.

### 4.8 Metrics

| # | Metric | Definition | Target | Why |
|---|---|---|---|---|
| M1 | **Queue clearance ratio** | proposals resolved ÷ proposals created, per period | **≥ 1.0** | The single number that would have caught gbrain#3269 on day two |
| M2 | **Weeding rate vs acquisition rate** | `W_t / A_t` | 0.8–1.2 (0 in developing mode) | The CREW control law |
| M3 | **Annual turnover** | `ΣW / corpus` | ~5%/yr | CREW/Slote rule of thumb |
| M4 | **Shelf-sitter ratio** | % of pages with `last_retrieved_at` NULL or > 180d | trending **down**; alarm if rising 3 periods running | Accretion detector |
| M5 | **Stale-serve rate** | superseded claims appearing in top-k, sampled weekly | < 2% | Directly measures Tan's failure mode #2 |
| M6 | **Provenance completeness** | % of claims with a resolvable source | 100% (enforce at write) | GBrain already enforces this — keep it |
| M7 | **Authority collision rate** | entities resolving to >1 canonical slug; generic-token hubs | 0 hubs | Kills the junk-entity-hub class |
| M8 | **Independently-understandable rate** | sampled pages an agent can use with no author context | > 90% | OAIS §3.1, unmeasured anywhere in this corpus |
| M9 | **Cost per accession / per deaccession** | $ per page in, $ per page out | deaccession ≤ accession | SAA: *"calculate the costs and benefits before implementing"* |

M1, M2 and M4 are the three that would change behaviour tomorrow, and all three are computable today from GBrain's existing schema.

---

## 5. What GBrain's dream cycle actually automates, in these terms

Using the verified inventory from `v06a` and `v06b` (23 phases, 17 running on a stock install; 117 doctor check names of which 12 carry remediation steps and **all 12 are additive**; `doctor --remediate` has four steps, all index rebuilds):

| Librarian function | GBrain |
|---|---|
| Accessioning + provenance | **Automated and enforced.** `facts.source TEXT NOT NULL`; `remember` errors `provenance_required`; content-sanity hard block at the narrow waist |
| Appraisal at ingest | **Automated, one axis.** `synthesize` triage 0.5 with a 0.30 rescue band |
| Cataloguing | **Automated.** Zero-LLM regex link extraction, tags, `patterns`, `embed` |
| Authority control | **Partial.** Canonical slugs + alias hop + `phantom-redirect` (the *only* automatic page deletion in the cycle, capped at 50/run, and it is filename normalisation) |
| Consolidation | **Automated.** Greedy cosine clustering at 0.85, ≥3 facts/bucket, chronological `valid_until` — arbitrating by **recency inside a cosine cluster** |
| Salience | **Automated, deterministic.** `recompute_emotional_weight`, no LLM |
| Circulation statistics | **Collected and indexed, mis-spent.** `last_retrieved_at`, *"NULL = never retrieved (LSD prioritizes these first)"*; sole consumer is `lsd`'s `WHERE last_retrieved_at IS NULL OR last_retrieved_at < NOW() - INTERVAL '90 days'` (`src/schema.sql:122-126, 270-276`) |
| Reference service (Sense B) | **Excellent.** 4-signal hybrid, rerank, autocut, token budget, `create_safety`, evidence stamps |
| **Reappraisal** | **Absent.** No periodic re-evaluation of accessioned content |
| **Weeding** | **Absent.** Zero phases delete on a quality judgment |
| **Deaccessioning** | **Absent.** No policy, no authority, no disposition options, no log |
| **Retention schedule** | **Absent.** No knowledge-retention config key exists |
| **Collecting policy** | **Absent.** Filing rules ≠ acquisitions mandate |
| **Preservation Planning (OAIS)** | **Absent.** No entity monitors whether the collection still serves the community |
| Garbage collection | **Automated.** `purge` hard-deletes soft-deleted pages past 72h — executes decisions taken elsewhere |

**The one-sentence verdict.** *GBrain has built a technically excellent OAIS Ingest, Data Management and Access stack with a rigorous no-ad-hoc-deletion posture, and has not built the approved disposal strategy that clause presupposes — so its "librarian" is a cataloguer and a reference desk with no acquisitions policy, no retention schedule and no weeding shelf, which is why its own review queue reached 32,500 unread items and why its circulation statistics feed an idea generator instead of the weeding cart.*

**And the fair counterweight**, which library science supports rather than undermines: refusing to auto-destroy is *correct*. SAA requires reappraisal before any deaccession, documentation of every step retained *"as a permanent administrative record"*, a named approval authority, and full transparency; CREW requires a signed disposal slip and an "is it available elsewhere" check. GBrain's `content_flag` over `quarantine` choice — *"a false positive costs a one-line note, not a vanished page"* — is textbook curatorial posture. The defect is not that it refuses to delete autonomously; it is that **it never built the schedule, the policy and the authority that would let a human delete cheaply and routinely**, so the human half of "human plus agent" has no chair to sit in.

---

## 6. The five changes with the best ratio of effect to effort

1. **Re-point `last_retrieved_at` from `lsd` to a weeding score.** The column, the index and the 90-day window already exist. One query produces the shelf-sitter report (M4) and the ranked queue.
2. **Truncate the review queue at the acquisition rate.** Turns `take_proposals`/contradiction findings from an unbounded backlog into a fixed weekly shelf. Costs a `LIMIT` and a counter.
3. **Write three policy files** — `COLLECTING-POLICY.md`, `COLLECTION-MANAGEMENT-POLICY.md`, `retention.yml`. Human-authored, ~2 pages total. Without them no disposal decision is decidable, and *with* them most disposals need no reviewer at all.
4. **Add the Work level.** Give every claim an SPO key above the page. Supersession becomes deterministic (D5), the six contradiction verdict classes collapse to two, and the AUROC-0.59 embedding problem stops being on the critical path.
5. **Add qualifiers and a cataloguer's note to the authority layer.** Refuse to auto-link generic single-token names. Eliminates the junk-entity-hub class at the source rather than warning about it forever.

Each is a small diff against GBrain's existing schema. None requires a better model.

---

## 7. Confidence and limits

- **High confidence** on every doctrine quoted: CREW, the SAA guidelines and OAIS were read from their own PDFs; SAA Dictionary entries, IFLA, NARA and OCLC pages were fetched directly. Quotations are verbatim.
- **High confidence** on `last_retrieved_at`'s definition, index and sole consumer — re-verified by me against `raw.githubusercontent.com` at commit `43597b19`.
- **Medium-high confidence** on the GBrain phase/doctor/queue claims: they come from `v06a` and `v06b`, both of which read a pinned commit and quote source; I did not independently re-audit all 23 phases.
- **Medium confidence** on the MPLP paraphrase — the Allen Press article page returned HTTP 403; the citation is standard but I did not read the text at first hand.
- **Unverified and unverifiable:** whether Garry's private brain repo (which routes to a `brain-librarian` skill that has no directory in the public repo, and runs ~66 crons) already implements some of this. Everything here describes the MIT-licensed public artifact at v0.48.5.0.
- **The CREW numbers are rules of thumb for public-library print collections**, explicitly offered as such (*"offered as 'rules of thumb' based on opinions in the professional literature and practical experience"*). The 5%/year and the weed≈acquire law transfer as *structure*; the specific month values in §4.3 are my adaptation and are not empirically calibrated for text corpora. They should be treated as starting points to tune against M5 (stale-serve rate), which is the metric that actually matters.
- **One genuine disanalogy, stated so nobody over-transfers the frame:** physical weeding is forced by shelf space, and a company brain has none. Ranganathan's Law 4 supplies a real objective function in its place (reader time / precision at k), but the *forcing* is gone — which means a company brain will not weed unless the rate law is enforced deliberately. That is an argument for D8-style scheduled disposal being the primary mechanism and human weeding the exception, which inverts the emphasis of the physical-library literature.

---

## Sources

**Library and archival science (primary)**
- [CREW: A Weeding Manual for Modern Libraries](https://web.archive.org/web/20181220190215/https://www.tsl.texas.gov/sites/default/files/public/tslac/ld/ld/pubs/crew/crewmethod12.pdf) — rev. & updated by Jeanette Larson, Texas State Library and Archives Commission, 2012, 107 pp., CC BY-NC-ND 3.0. CREW acronym p.13; MUSTIE and the three-part formula pp.57–58; cadence and the 5%/weed≈acquire rules pp.16–17; disposal slip p.107; Ranganathan citation p.12 n.3; Slote citation p.17 n.5. Retrieved from the Internet Archive (snapshot 2018-12-20) because TSLAC has de-published it: [current TSLAC notice](https://www.tsl.texas.gov/ld/pubs/crew/index.html)
- [SAA, *Guidelines for Reappraisal and Deaccessioning*](https://www2.archivists.org/sites/all/files/GuidelinesForReappraisalAndDeaccessioning-May2012.pdf) — approved by SAA Council May 2012, 34 pp. Definitions p.3; Guiding Principles pp.6–7; Rationale p.8; Preparation pp.8–9; Reappraisal criteria pp.10–13; four disposition options pp.14–15. Index page: https://www2.archivists.org/standards/guidelines-for-reappraisal-and-deaccessioning
- [CCSDS 650.0-M-2, *Reference Model for an Open Archival Information System (OAIS)*](https://ccsds.org/Pubs/650x0m2.pdf) — Magenta Book, June 2012 (= ISO 14721:2012); this copy stamped CCSDS HISTORICAL DOCUMENT. §1.7.2 terminology (SIP/AIP/DIP, functional entities); §3.1 mandatory responsibilities incl. *"There should be no ad-hoc deletions."*
- [SAA Dictionary of Archives Terminology: appraisal](https://dictionary.archivists.org/entry/appraisal.html)
- [SAA Dictionary: respect des fonds](https://dictionary.archivists.org/entry/respect-des-fonds.html) — Posner 1940a; Duchein 1983; Horsman et al. 2003; Jimerson 2009; Duranti & Franks 2015
- [SAA Dictionary: evidential value](https://dictionary.archivists.org/entry/evidential-value.html) — Schellenberg 1996; Buck 1945a; Millar 2014; Dollar 1993
- [SAA Dictionary: macroappraisal](https://dictionary.archivists.org/entry/macroappraisal.html) — Brown 1995; Cook 1996, 2004; Lemieux 1998; Gilliland 2014a
- [NARA, General Records Schedules](https://www.archives.gov/records-mgmt/grs) — *"Use of the GRS is mandatory."* Page last reviewed 2026-06-12
- [IFLA Library Reference Model](https://repository.ifla.org/handle/20.500.14598/40) — published January 2018; consolidates FRBR, FRAD, FRSAD
- [OCLC, VIAF (Virtual International Authority File)](https://www.oclc.org/en/viaf.html) — 50+ organizations, 30+ countries; matching, linking, clustering
- Ranganathan, S. R., *The Five Laws of Library Science*, Asia Pub. House, 1963 (1st ed. 1931) — cited via CREW p.12 n.3
- Slote, Stanley J., *Weeding Library Collections*, Libraries Unlimited, 1997, p.14 — source of the 5%/year rule, cited via CREW p.17 n.5
- Greene, Mark A. & Dennis Meissner, "More Product, Less Process: Revamping Traditional Archival Processing," *The American Archivist* 68:2 (2005), 208–263 — https://meridian.allenpress.com/american-archivist/article/68/2/208/24377 (**HTTP 403 on fetch; citation standard, text not read at first hand — medium confidence**)

**GBrain (verified directly at commit `43597b19e50a3abf56409337f248f7966860293c`, v0.48.5.0)**
- https://raw.githubusercontent.com/garrytan/gbrain/43597b19e50a3abf56409337f248f7966860293c/src/schema.sql — `pages.last_retrieved_at` definition and comment (lines 122–126); `pages_last_retrieved_at_idx` and the LSD stale-page query comment (lines 270–276)

**GBrain (via prior reports in this project, which quote pinned source)**
- `/Users/stephen/Cookies/company-brain-research/findings/v06a-librarian-in-code.md` — 23 phases; phase-by-phase delete/merge/demote audit; `DEFAULT_TRIAGE_THRESHOLD = 0.5`; consolidate cosine 0.85 + chronological `valid_until`; `phantom-redirect` 50/cycle cap; 117 doctor check names; `doctor --remediate` four additive steps; `brain-librarian` named but unshipped
- `/Users/stephen/Cookies/company-brain-research/findings/v06b-librarian-skeptic.md` — no knowledge-retention config key; `decay.ts` pure function used only to sort; `SESSION_DEMOTE` ×0.95 as the only true demotion; `take_proposals` 32.5k rows growing 2–6k/day (gbrain#3269); junk_entity_hubs "Warn + list only" (gbrain#4222); contradiction probe never auto-applies
- `/Users/stephen/Cookies/company-brain-research/findings/gbrain-architecture.md` — storage tiering, compiled_truth/timeline split, contradiction verdict classes and Wilson CIs
- `/Users/stephen/Cookies/company-brain-research/findings/memory-hygiene.md` — MemStrata AUROC 0.59 and the SPO bi-temporal supersession result; the ~115 HIGH findings walked by hand

**Talk**
- `/Users/stephen/Cookies/company-brain-research/sources/transcript_eBUyTS7SzV4.txt` — 12:30 ("Your company is a library"); 12:45 ("who decides which three books"); 12:53–12:56 ("the library plus the librarian"); 13:09–13:20 (what gets written down / hot vs cold / who arbitrates); 14:30–15:05 (the three failure modes and "a librarian, human plus agent, whose actual job is pruning"); 17:41 and 19:28 ("the librarian that picks the three books")

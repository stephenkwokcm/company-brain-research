# d5 — The Proofreading Layer: connectome curation practice as a buildable spec for GBrain

**Key:** `d5-curation-process` · **Design panel, angle 5 (PROCESS)** · **Written:** 2026-09-10
**Author:** research worker (Claude Opus 5)
**Brief:** apply fruit-fly-brain work to a company brain; my angle is the *connectome projects* (FlyWire / MaleCNS / BANC / CAVE / neuPrint / VFB) as a reference architecture for curation — versioned annotations, per-fact confidence, human+AI proofreading as arbitration, cell-type ontology as entity canonicalisation, an agent-facing MCP library.
**Method:** primary sources fetched live today (CAVE full text from EuropePMC/PMC; `flyem-snapshot` source from GitHub raw; VFB policy pages; MaleCNS site; FlyWire annotation schema; Codex; ConnectomeBench abstract) plus direct reads of GBrain `src/schema.sql`, `src/core/migrate.ts` and `src/core/cycle.ts` at `master`. WebSearch budget for this session was exhausted before I started (200/200), so the novelty check rests on prior workers' searches, not my own.

---

## TL;DR

1. **The borrow is real, and it is the only branch of question (b) that survived this round.** `v10a`/`v10b` refuted FlyHash as an index and as a dedup gate; `arXiv:2604.04033` refuted the connectome-topology transfer; `g07` found only one mechanism (the fly Bloom filter) buildable as published, never tested on text. What is left standing is the *process* the connectome community built around the data — and unlike the algorithms, it has a decade of operation, public measurements, open-source code and published cost.
2. **Be honest about what kind of transfer this is.** This is not fruit-fly neuroscience. It is the data-management practice of the labs that mapped the fly. `g07` says it in one line and the synthesis must repeat it: *"that is a **process** answer from the neuroscience community's data practices, not an **algorithm** from the fly's brain. Do not blur the two."* Fidelity rating below is split accordingly.
3. **The single most transferable idea, and the one with no off-the-shelf substitute, is CAVE's separation of an immutable substrate address from a time-resolved entity identity, with a lineage graph in between.** An annotation is bound to a point in the *immutable* EM volume; the mutable neuron ID underneath it is *derived by lookup at a timestamp*. So an annotation written before two neurons were merged still resolves correctly after the merge, at any point in time. W3C Web Annotation selectors anchor to text but have no entity lineage; SQL:2011 bitemporal tables version rows but cannot re-key them across a merge. The combination is CAVE's actual invention, and it is exactly what a company brain needs the day it merges `companies/acme-corp` and `companies/acme-inc`.
4. **GBrain fails this test today, at the schema level.** `facts.entity_slug` is a bare mutable `TEXT` with no FK and no lineage (`src/core/migrate.ts:2384`); `content_chunks` is keyed `(page_id, chunk_index)` (`src/schema.sql:296`), so any page edit silently re-points every chunk-keyed annotation; and `page_versions` (`src/schema.sql:569`) is a four-column snapshot with **no actor, no operation, no reason, no parent, no content hash and no TTL**. GBrain has the raw material of an immutable substrate and did not build it. **That is the deepest recommendation in this report: make `page_versions` the immutable substrate — content-addressed, append-only, with actor and op — and every other borrow below becomes cheap.**
5. **Eight borrows, ranked; five are ≤2 engineering days each.** Bound anchors + lineage (B1), materialised versions with as-of query (B2), two-tier status vocabulary with a publish policy and a CI exhaustiveness assertion (B3), a release build whose gates are quality reports (B4), confidence carried with its scale and producer and never normalised (B5), independent deprecation axes with per-surface degradation (B6), a known-defects layer (B7), and match-mode reporting on the agent-facing `entity()` verb (B8).
6. **One shipped GBrain behaviour should be inverted on published evidence.** ConnectomeBench (arXiv:2511.05542, NeurIPS 2025 D&B) measures LLMs at 52–82% balanced accuracy on segment identification (chance 20–25%) and 75–85% on split errors (chance 50%) but finds they "generally struggle on merge error identification." GBrain's *only* automatic destructive operation is a slug-normalising **merge** capped at 50 pages/run (`v06a`). The one operation it automates is the one the only published benchmark says models are worst at. Automate splits and identification; human-gate merges.
7. **Honest verdict on effect size:** this proposal buys **reproducibility, arbitrability and governance**, and it is *unlikely* to move pooled retrieval accuracy. That is `g06`'s modal hypothesis H2, and I pre-register it as my own prediction. The one place I expect a real answer-quality win is the supersession/conditional stratum, because a stable key is a precondition for `g01`'s `WITHOUT OVERLAPS` constraint — without B1, `g01`'s intervention is enforcing uniqueness on a string that changes.
8. **Almost every individual borrow has a better-specified non-biological standard behind it** — W3C Web Annotation Data Model, SQL:2011, OBO Foundry obsolescence policy, PROV-O, LakeFS/Dolt. I say so item by item in §6. The unique value of the connectome case is not any single mechanism; it is that it is the only place where all of them run together, at 10⁵-entity scale, for a decade, with published numbers for what it cost.

---

## 1. What the connectome projects actually built (primary sources, verified today)

### 1.1 CAVE — Connectome Annotation Versioning Engine

Dorkenwald, Schneider-Mizell, Brittain, Halageri, Jordan, Kemnitz, Castro, Silversmith, Maitin-Shephard *et al.*, **"CAVE: Connectome Annotation Versioning Engine," *Nature Methods* 22:1112–1120 (2025)**, DOI [10.1038/s41592-024-02426-z](https://doi.org/10.1038/s41592-024-02426-z), open access at [PMC12074985](https://pmc.ncbi.nlm.nih.gov/articles/PMC12074985/) (full text read for this report). Preprint bioRxiv [2023.07.26.550598](https://doi.org/10.1101/2023.07.26.550598). Client: [`CAVEconnectome/CAVEclient`](https://github.com/CAVEconnectome/CAVEclient), docs at [caveconnectome.github.io/CAVEclient](https://caveconnectome.github.io/CAVEclient/).

The problem statement is, word for word, a company brain's: *"every proofreading edit relabels cell identities of millions of voxels and thousands of annotations… For analysis, users require immediate and reproducible access to this changing and expanding data landscape."*

Five mechanisms, quoted or paraphrased from the paper:

| Mechanism | What it is |
|---|---|
| **Bound spatial points** | *"Every annotation is based on points in space (≥1) that serve as spatial anchors and are accompanied by a set of data entries."* The points are bound to immutable **supervoxels**; the mutable segment ID (`root_id`) is looked up **"for any point in time using the ChunkedGraph."** |
| **Lineage graph** | Edits are recorded as a graph over old/new root IDs, so an ID from any past moment can be mapped forward or backward. |
| **Schema registry** | *"a repository of schemas from which users can freely choose, with many being reused across tables, datasets and communities. Users can create new schemas that fit their specific needs but are encouraged to reuse schemas where possible."* |
| **Reference tables** | Foreign-key-linked side tables that *"add data entries to existing annotations without needing to copy the entire table"*, and *"may only contain data entries for a subset of the annotations in the referenced table."* |
| **Materialisation + live delta query** | *"infrequent copies (for example, daily)… that serve as materialized analysis snapshots"*, plus a live path where the user supplies a timestamp, the lineage graph produces an over-inclusive candidate ID set against the nearest snapshot, changes since the snapshot are merged in, and the result is mapped back to the query timestamp. |

Measured numbers worth carrying (all from the paper):

- **120+ annotation tables (29 of them reference tables) using 21 distinct schemas, capturing over 1.8 billion annotations**, across MICrONS65, MICrONS phase 1, FlyWire and FANC — including **62 distinct cell-type tables** and dedicated **proofreading-status tables**.
- **>4 million edits from >500 unique users** across five published datasets; FlyWire edit sample N = 1,349,955; MICrONS65 N = 457,285 over one year; peaks **>100 edits/min**; **>150,000 edits in MICrONS65 applied automatically** — automated proofreading is a first-class citizen in the same edit log as humans.
- **The measured price of as-of querying:** presynapse queries aligned to a snapshot ran at **median 525 ms (N = 121,400)**; non-snapshot-aligned where the query neuron had no edits since the snapshot, **978 ms (N = 127,775)**; where it had been edited, **1,385 ms (N = 12,xxx)**. So arbitrary-time-point access costs **≈1.9× to 2.6× latency**, not an order of magnitude.
- **Infrastructure cost:** MICrONS65 and FlyWire run ~2 TB annotation databases at **~$500/month**; the floor for a CAVE deployment's microservices is **~$360/month**. An external lab needs *"a software developer or otherwise experienced technical person"* and *"a few weeks"* to stand one up.
- **A hard query cap:** 500,000 rows per request, *"to prevent queries from accidentally requesting multiple gigabytes of data."*
- **Authorisation** is `middle-auth`: OAuth2 identity, then **per-service-table** permissions granted to **groups**, not per-annotation. (Note for `g05`: CAVE's granularity ceiling is the same shape as GBrain's per-source ceiling.)

### 1.2 The published-release machinery — `flyem-snapshot`

The MaleCNS neuPrint database is not hand-maintained; the [download page](https://male-cns.janelia.org/download/) states it was *"Constructed using flyem-snapshot"* — [`janelia-flyem/flyem-snapshot`](https://github.com/janelia-flyem/flyem-snapshot) (BSD-3-Clause, Python, pushed 2026-09-09). Reading its README and source directly:

- It is a **declarative, config-driven build**: `flyem-snapshot -Y > snapshot-config.yaml`, edit, then `flyem-snapshot -c manc-v1.2.1-release.yaml`. Output is tagged with a **snapshot tag = date + input-checkpoint UUID**, e.g. `2024-02-01-3ddc3f`. The release names the exact input state it was built from.
- **Quality reports are release artifacts, not dashboards.** Every run emits `tables/body-status-counts-{snapshot_tag}.csv` plus an HTML/PNG chart, `primary-all-status-stats`, and "connectivity by status and ROI" charts. The completeness distribution of the corpus is published *with* the corpus.
- **A two-tier status vocabulary with a compile-time exhaustiveness gate.** `flyem_snapshot/outputs/neuprint/annotations.py` maps **33 internal DVID/Clio status values** down to a **6-value published vocabulary** (`Traced`, `Anchor`, `Orphan`, `Unimportant`, `Glia`, `Assign`, plus `''` = not published). Internal states include `Roughly traced`, `Prelim Roughly traced`, `RT Hard to trace`, `Partially traced`, `Cleaved Anchor`, `Will be merged`, `Out of scope`, `Not examined`, `Putative Leaves`. The file ends with:

  ```python
  assert list(NEUPRINT_STATUSLABEL_TO_STATUS.keys()) == DEFAULT_BODY_STATUS_CATEGORIES
  ```

  **The release build fails if anyone introduces an internal curation state the publisher does not know how to map.** That is a ~1-line vocabulary-drift gate.
- **A field-level publish policy.** In the same file, `CLIO_TO_NEUPRINT_PROPERTIES` maps `last_modified_by`, `reviewer`, `user`, `notes`, `typing_notes`, `to_review`, `old_type`, `old_bodyids` and — notably — `confidence` to `''`: *"Make sure these never appear in neuprint."* The curation metadata exists internally and is deliberately stripped at publish time. Note also that `old_bodyids` and `old_type` exist at all: **identity lineage and label lineage are tracked in the working store.**

### 1.3 Confidence carried, not computed

Two policies, both explicit:

- **Threshold in the artifact name.** MaleCNS bulk files are `body-annotations-male-cns-v1.0-minconf-0.5.feather`, `connectome-weights-…-minconf-0.5.feather`, `syn-partners-…-minconf-0.5.feather` (columns include per-row `conf_pre`, `conf_post`). You cannot be confused about which filter produced a table. Files built under a different regime deliberately lack the tag (`body-neurotransmitters-male-cns-v1.0.feather`).
- **VFB's stated policy** ([Confidence Values](https://www.virtualflybrain.org/docs/concepts/confidence-value/)): *"The value shown is the source study's own confidence score, carried through unchanged. Each study defines its own scale and its own threshold for calling a prediction, so a value should be read against the publication it came from rather than compared across datasets. VFB does not compute these scores and does not set a cut-off: a low-confidence prediction is displayed with its score rather than hidden."* Plus an eligibility floor (*"Neurons with fewer than 100 presynapses are excluded"*) and a **verified-beats-predicted** rule for BANC (predictions *"only used if not in conflict with the Verified NT type field"*).

### 1.4 Deprecation as a published policy — VFB

[Dataset Versions and Deprecation](https://www.virtualflybrain.org/docs/data/em/versioning/) (dated 30 Jun 2026) is the single most directly liftable document I found in this project. Its content, condensed:

- **Deprecation does not delete.** *"The node and its identifier are retained (so old IDs resolve), but it is marked deprecated and treated accordingly."*
- **Core principle: source-deprecation and entity-deprecation are independent axes.** *"A Neuron can be valid while its data source is deprecated, and a data source can remain live while individual Neurons within it are retired."*
- **Supersession is an explicit typed edge**: `term_replaced_by` links the old DataSet/Site to the new one.
- **A per-state rule table** for a version bump (worked example: BANC v626 → v888): entities whose accession persists are not deprecated and gain a cross-reference to the new site while keeping the old one; entities absent from the new release **are** deprecated; old sites that still resolve are **not** deprecated, old sites that no longer resolve **are**; connectivity, images and cell-type links are replaced for non-deprecated entities and *may be retained on deprecated ones if still valid*.
- **Enforcement is per-surface, and includes denominators.** *"Deprecated Neurons are excluded from connectivity results and from the Neuron counts used in connectivity summaries (so they do not appear as partners and do not affect percentages)."* Deprecated sites *"never produce a clickable external link"* but the accession is still rendered as plain text; the cross-reference list, *"whose entries exist specifically to be links,"* omits them entirely. Entities whose only source is deprecated **remain valid query targets**.

That is a complete, tested answer to "what happens to a derived fact when its source is re-released, superseded, or dies" — the question `v06b` shows GBrain answering by accident (facts resurrected nightly until 2026-09-08).

### 1.5 Entity canonicalisation — the cell-type ontology

Schlegel *et al.*, **"Whole-brain annotation and multi-connectome cell typing of *Drosophila*," *Nature* 634:139–152 (2024)**, DOI [10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5). Data: [`flyconnectome/flywire_annotations`](https://github.com/flyconnectome/flywire_annotations).

- **8,453 annotated cell types; 3,643 previously proposed in the hemibrain; 4,581 new. About one-third of hemibrain-proposed types could not be reliably re-identified** in FlyWire. The response was not to pick a winner — it was to **change the definition**: *"We therefore propose a new definition of cell type as groups of cells that are each quantitatively more similar to cells in a different brain than to any other cell in the same brain."* The output is described as *"a consensus cell type atlas."*
- The annotation record itself is worth reading as a schema (from [`supplemental_files/README.md`](https://github.com/flyconnectome/flywire_annotations/blob/main/supplemental_files/README.md)): a **hierarchy** (`flow` → `super_class` → `cell_class` → `cell_sub_class` → `cell_type` → `hemibrain_type`); **two parallel nomenclatures** carried side by side (`ito_lee_hemilineage` and `hartenstein_hemilineage`, with the note that *"not all labels exist in the Hartenstein nomenclature"*); **cross-resource identifiers** (`fbbt_id` for the ontology term, `vfb_id` for the individual, `supertype` for the neuPrint MaleCNS name); **prediction + its confidence as separate columns** (`top_nt`, `top_nt_conf`); a **defect flag with a controlled vocabulary** (`status`: `outlier_seg` = segmentation problem, `outlier_bio` = real biological difference from its homologue); **`synonyms`** to cross-link past literature; and **`matching_notes`** — free text recording *why* two cross-dataset records were or were not matched.
- The uncertainty vocabulary is the sharpest detail. `is_hemilineage` is not a float; it is a controlled set of graded verdicts: `H` (is a hemilineage), `H?` (probably, not certain), `Hp` (probably), `H/L` (hemilineage or lineage), `H(NT)` (inferred from neurotransmitter evidence), `H_2NT` (probably, but two neurotransmitters predicted — evidence conflicts), `2L_1NT`, `L`, `T2`. **The reason for the doubt is encoded in the label.** Compare `facts.confidence REAL`.
- The repository is explicit that the same data reached through a different path may disagree: *"Codex presents a mix of annotations from different sources which likely diverge from the systematic and cross-checked annotations presented here."* The curators publish the fact that two views of their own corpus disagree.

### 1.6 Human + AI proofreading as arbitration

- Community proofreading at scale is the FlyWire model: Dorkenwald *et al.*, *Nature Methods* 19:119–128 (2022), DOI [10.1038/s41592-021-01330-0](https://doi.org/10.1038/s41592-021-01330-0) — *"Information in the edit history is programmatically accessible for a variety of uses such as estimating proofreading accuracy or building incentive systems."* The edit log is a first-class analysable object, not a debug artifact.
- **ConnectomeBench** — Brown, Kirjner, Vivekananthan & Boyden, [arXiv:2511.05542](https://arxiv.org/abs/2511.05542), NeurIPS 2025 Datasets & Benchmarks: LLMs reach **52–82% balanced accuracy on segment identification (chance 20–25%)** and **75–85% on split-error correction (chance 50%)**, while *"generally struggling on merge error identification tasks."* Models can say *"this looks like an X"* and *"these two things were wrongly joined"*; they cannot reliably say *"these two things are the same."*

### 1.7 The agent-facing library — VFB MCP

`https://vfb3-mcp.virtualflybrain.org`, streamable HTTP, **no API key, no account** ([guide](https://www.virtualflybrain.org/docs/tutorials/vfb-mcp-guide/), page dated 07 Feb 2026; `claude mcp add --transport http virtual-fly-brain https://vfb3-mcp.virtualflybrain.org`). Seven documented tools: `get_term_info`, `search_terms`, `run_query` (incl. NBLAST similarity), `get_hierarchy` (`part_of` vs `subclass_of`), `list_search_facets`, `resolve_entity`, `resolve_combination`, plus `query_connectivity` / `list_connectome_datasets`.

Three design decisions worth stealing:

- **Datasets are version-pinned in the tool surface**: FAFB-FlyWire **v783**, Male-CNS optic lobe **v1.0.1**, hemibrain **1.2.1**, FlyCircuit **1.0**. An agent's answer is attributable to a corpus version.
- **`resolve_entity` reports its own match mode.** *"It tries an exact match first, then synonyms, then a broad pattern match, and tells you which of the three it used,"* with the warning: *"When the match came from a synonym or a broad pattern rather than an exact name, check the result is the entity you meant before building on it."*
- **`list_search_facets` is honest about its provenance**: 233 facet types that *"come from the index's own annotations rather than a curated list, so they change as data is added."* The tool tells the agent that its own filter vocabulary is derived, not authored.

### 1.8 A known-defects map

The MaleCNS neuroglancer scene ships `brain-defects` and `vnc-defects` layers: *"these layers show areas with known data defects/artefacts"* ([Explore](https://male-cns.janelia.org/explore/)). The corpus publishes a queryable map of the regions where it knows it is wrong.

### 1.9 Release discipline, and one worked contradiction

[MaleCNS Release Notes](https://male-cns.janelia.org/release/), in full: **v1.0 (June 8, 2026)** — "Minor proofreading changes; Refinement of neuron annotations"; **v0.9 (October 5, 2025)** — "Initial release of male CNS connectome."

Note that this page says **October 5, 2025** where `v02-malecns-date` reports **3 October 2025** for v0.9. I did not resolve it; I cite the project's own release page. It is a small, live instance of exactly the problem this whole project is about — two dated statements from the same organisation about the same event — and it is worth one sentence in the synthesis as such.

Scale calibration, from `flywire-connectome-simulation.md` and confirmed on [Codex](https://codex.flywire.ai/) today: FAFB v783 = 139,255 neurons / 3,732,460 connections; BANC v888 = 158,262 neurons / 3,037,361 connections; MaleCNS v1.0 = 166,700 neurons / 11,710 types / 124.2M synaptic connections, at **≈44 person-years** of reconstruction labour. Codex now requires Google sign-in (*"over 60,000 users have signed in"* as of early 2026) explicitly to rate-limit automated traffic — a note for anyone planning to expose a company brain to agents.

---

## 2. The mechanism borrowed, and its fidelity

**Mechanism:** the curation *process* of the large connectome consortia — bound annotations over an immutable substrate with a time-resolved identity lineage; a schema registry; daily materialised versions with as-of query; a two-tier curation-status vocabulary with a publish policy and an exhaustiveness gate; confidence carried with its scale and producer; a published deprecation policy with independent axes; a reproducible release build whose artifacts include quality reports; a consensus type ontology reached by changing the definition when cross-dataset matching failed; human+AI proofreading in one edit log; and a keyless, version-pinned MCP surface over the result.

**Fidelity — split rating, and the split is the point:**

| Axis | Rating | Justification |
|---|---|---|
| As fly **biology** | **Zero.** Not superficial — zero. | Nothing here derives from a fly's brain. The mushroom body has no provenance, no version, no deprecation policy and no librarian. `g07` establishes that provenance and skillification have *no* fly counterpart and warns explicitly against blurring the connectome community's data practice with the fly's neural algorithms. |
| As a **process** transfer | **Deep.** | Same problem statement (a mutable corpus under continuous concurrent proofreading that must serve reproducible queries), same failure modes (identity churn, stale derived facts, cross-source disagreement), same 10⁵-entity order of magnitude, and running code under open licences. What transfers is invariants and policies, not parameters. |
| As **novel** engineering | **Low, with one exception.** | W3C Web Annotation, SQL:2011, OBO Foundry, PROV-O and LakeFS/Dolt each cover part of it better (§6). The exception is CAVE's immutable-anchor + lineage + time-resolved-identity triple, for which I found no standard equivalent. |

**Why the honest framing still helps the user's question.** They asked whether the company brain can be combined with the recently published fly-brain work. The strongest true answer available after this round's verification is: *the fly's algorithms mostly cannot be used, but the artifact you are pointing at is the best worked example in existence of the thing Tan says the product is — and its curation stack is portable.* `v02` sharpened this into the best dated evidence in the corpus: **the MaleCNS data was downloadable under CC-BY for eleven months (v0.9, Oct 2025) with almost nothing built on it; third-party applications appeared within 48–72 hours of the September 2026 paper.** Publication is not release; certification and curation are what made the data worth retrieving from. A reader who wanted fly *neuroscience* in their RAG stack may still feel the question was dodged. Say so rather than dressing this up.

---

## 3. The eight borrows, with exact GBrain insertion points

All GBrain paths and line numbers read directly from `master` today (`src/schema.sql` = 1,618 lines; `src/core/migrate.ts` = 7,010 lines; `src/core/cycle.ts` = 3,207 lines, `ALL_PHASES` = **23** phases, confirming `v06a`'s correction of the earlier "25").

### B1 — Bound anchors + identity lineage (the keystone)

**The GBrain defect, verified.**
- `facts` (`src/core/migrate.ts:2384`): `entity_slug TEXT` — nullable, no FK, no lineage. `source TEXT NOT NULL` is a free-text provenance *string*, not a locator; there is no offset, quote, or content hash tying a fact to the span that produced it.
- `content_chunks` (`src/schema.sql:296`): unique on `(page_id, chunk_index)`. `embedded_text_hash` (md5 at embed time) exists but only guards embedding drift. Edit a page and every chunk index shifts under anything keyed to it.
- `links` (`src/schema.sql:467`): unique on `(from_page_id, to_page_id, link_type, link_source, origin_page_id)`, with a good instinct already present — `resolution_type CHECK (… IN ('qualified','unqualified'))` — but no confidence and no validity interval.
- `page_versions` (`src/schema.sql:569`): `(id, page_id, compiled_truth, frontmatter, snapshot_at)`. No actor, no operation, no reason, no parent version, no content hash, no TTL. `g05` separately flags the missing TTL as a GDPR problem; the missing *actor and op* are the reason no lineage can be reconstructed.
- The one automatic destructive operation — the slug-normalising merge, 50 pages/run (`v06a`) — has nowhere to record that a merge happened.

**The borrow.** CAVE binds annotations to immutable supervoxels and derives `root_id` at a timestamp through the lineage graph.

**Build.**

```sql
-- 1. Make page_versions the immutable substrate (content-addressed, append-only).
ALTER TABLE page_versions
  ADD COLUMN content_hash TEXT,                   -- sha256(compiled_truth || timeline)
  ADD COLUMN actor TEXT,                          -- 'human:<id>' | 'agent:<client_id>' | 'cycle:<phase>'
  ADD COLUMN op TEXT CHECK (op IN ('create','edit','merge','split','rename','import','forget')),
  ADD COLUMN reason TEXT,
  ADD COLUMN parent_version_id INTEGER REFERENCES page_versions(id);
CREATE UNIQUE INDEX ON page_versions(page_id, content_hash);

-- 2. The lineage graph (CAVE's ChunkedGraph, reduced to what text needs).
CREATE TABLE page_lineage (
  id SERIAL PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  from_slug TEXT NOT NULL,
  to_slug   TEXT,                                  -- NULL for a split's discarded side
  op        TEXT NOT NULL CHECK (op IN ('rename','merge','split')),
  at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor     TEXT NOT NULL,
  reason    TEXT
);
CREATE INDEX ON page_lineage(source_id, from_slug, at DESC);

-- 3. Anchors: W3C Web Annotation selector semantics over the immutable substrate.
CREATE TABLE fact_anchors (
  fact_id          BIGINT NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
  page_version_id  INTEGER NOT NULL REFERENCES page_versions(id),
  quote            TEXT NOT NULL,     -- TextQuoteSelector.exact
  prefix           TEXT,              -- TextQuoteSelector.prefix (32 chars)
  suffix           TEXT,              -- TextQuoteSelector.suffix (32 chars)
  char_start       INTEGER,           -- TextPositionSelector, hint only
  PRIMARY KEY (fact_id, page_version_id)
);
```

`facts.entity_slug` stops being authoritative and becomes a **derived** column, resolved through `page_lineage` as of the query timestamp. Write path: the merge/rename code and `put_page` emit `page_lineage` rows; `extract_facts` (phase 6 of 23) writes anchors at extraction time, when the span is still in hand.

**Parameters.** Prefix/suffix window 32 chars (hypothes.is convention); re-anchoring order = exact quote match → prefix+suffix fuzzy match at ≤10% Levenshtein → position hint → mark `anchor_broken`. Lineage walk depth capped at 8 hops.

**Why this is the keystone.** `g01`'s recommendation is a partial GiST exclusion constraint on `(source_id, entity_slug, dimension)` over the valid range. That constraint is only as good as its key. Today the key is a mutable string that the cycle itself rewrites. B1 is the precondition, not a competitor.

### B2 — Materialised versions + `--as-of`

**The GBrain defect.** `pages.generation` (`src/schema.sql`, trigger `bump_page_generation_trg`) and `page_generation_clock` are a *cache-invalidation* clock — a monotonic counter with no timestamp semantics, no snapshot and no retention. `g01` correctly reports GBrain as uni-temporal with an audit stamp. There is no way to ask what the brain believed last Tuesday.

**Build.** `brain_versions(version_id TEXT PRIMARY KEY, materialized_at TIMESTAMPTZ, expires_at TIMESTAMPTZ, corpus_generation TEXT, git_sha TEXT, page_count INT, fact_count INT, take_count INT, status_counts JSONB)`; a nightly materialisation of the **annotation tables only** (`facts`, `takes`, `links`, `pages` metadata, `tags`) — never the embeddings, which are 8,192 B/vector (`g02`) and would dominate storage for no benefit. Add `as_of TIMESTAMPTZ` to `recall()` and `search`; implement CAVE's delta path (nearest snapshot → over-inclusive lineage expansion → merge live changes since → re-key to the query timestamp → filter).

**Insertion.** New phase between `embed` and `orphans` in `ALL_PHASES` (`src/core/cycle.ts:108`), or a separate cron so a failed materialisation cannot abort the cycle. Retention as a config key `versions.retain_days` (default 90) — GBrain has no knowledge-retention key at all today (`g04`, `v06b`).

**Cost, from CAVE's own measurements.** As-of costs ≈1.9–2.6× the snapshot-aligned query. In GBrain's budget (`g02`: HNSW scan 3.8 ms @100K / 10.7 ms @250K, `gbrain search` median 122 ms, +150 ms reranker, ~3,272 ms answered question) that is ~8–26 ms on the annotation join — **<10% of search latency and ~0.5% of an answered question.**

### B3 — Two-tier status vocabulary, publish policy, and a CI exhaustiveness gate

**The GBrain defect.** Curation state is scattered across `pages.deleted_at`, frontmatter `provenance: auto-extracted` + `status: unverified`, the search-time `evidence` / `create_safety` / `unverified` flags, and `sources.archived`. There is no single per-page curation state and no contract for what an agent sees.

**Build (the cheapest item here, and it subsumes the flags GBrain already has).**

```ts
// src/core/curation/status.ts
export const INTERNAL_STATUS = [
  'draft','auto-extracted','needs-review','in-review','verified',
  'provisional','disputed','superseded','defective','out-of-scope',
  'excluded','deprecated'
] as const;

export const PUBLISHED_STATUS = ['verified','provisional','orphan','excluded'] as const;

export const INTERNAL_TO_PUBLISHED: Record<InternalStatus, PublishedStatus | ''> = { … };

// flyem-snapshot's gate, ported verbatim in spirit:
// CI test asserts Object.keys(INTERNAL_TO_PUBLISHED) === INTERNAL_STATUS,
// so adding an internal state without deciding how it publishes fails the build.
```

Plus a **field-level publish policy** mirroring `CLIO_TO_NEUPRINT_PROPERTIES`: `reviewer`, `internal_notes`, `to_review`, `actor`, `raw confidence` never cross into the agent-facing surface. This is also the cleanest mechanical expression of `g05`'s OPEN / SENSITIVE / EXCLUDED zones, one level finer.

**Insertion.** `pages.curation_status TEXT NOT NULL DEFAULT 'auto-extracted'` in `src/schema.sql`; filter in `src/core/search/hybrid.ts` result assembly; expose the *published* value (never the internal one) on `recall()` hits.

### B4 — `gbrain release`: a reproducible build whose gates are quality reports

**The GBrain defect.** 85 *software* releases and zero *brain* releases. `v05` documents the consequence precisely: 220,000 claimed on stage, 146,646 in the README the same day, 155,795 from 2026-08-12, 28,256 and 17,888 elsewhere, and release notes contradicting the README by 30–120% inside a fortnight. Those numbers disagree because nobody ever cut a release with a defined denominator.

**Build.** `gbrain release --tag $(date +%F)-$(git rev-parse --short HEAD)` producing: (i) a `brain_versions` row; (ii) `RELEASE.md` in the MaleCNS style — what changed, in two lines; (iii) a status-distribution report (`flyem-snapshot`'s `body-status-counts` becomes `page-status-counts-<tag>.csv` + chart); (iv) a manifest with the **defined denominator** for every headline count (which sources, `deleted_at IS NULL`, which statuses); (v) threshold-in-the-name for any derived export, e.g. `facts-v3-minconf-0.5.parquet`. Then every answer cites the brain version it was drawn from — the VFB pattern of pinning `v783` / `v888` / `v1.0` / `1.2.1` in the tool surface.

### B5 — Confidence with its scale and producer; verified beats predicted

**The GBrain defect.** `facts.confidence REAL CHECK (confidence BETWEEN 0 AND 1)` with `DEFAULT 1.0`, then multiplied by `exp(-age_days / halflife_days)` in `src/core/facts/decay.ts`. One float, compared across kinds, sources, extractors and model versions as though commensurable — the exact error VFB's policy forbids.

**Build.** Add `confidence_scale TEXT NOT NULL` (e.g. `'haiku-4-5/extract-v7'`, `'human'`, `'regex'`), `confidence_producer TEXT NOT NULL`, and `verified_value TEXT` + `verified_by TEXT` + `verified_at TIMESTAMPTZ`. Rules, lifted from VFB and BANC: never compare confidence across scales; never hide a low-confidence item, display it with its scale; a `verified_value` **always wins** over a predicted one; eligibility floors (VFB's "<100 presynapses excluded") are declared per scale, not global. This is `v09b`'s split honoured exactly — these columns are *eligibility and bookkeeping*, deterministic and inspectable; adjudication stays with the model and contested resolution with a human.

### B6 — Independent deprecation axes with per-surface degradation

**The GBrain defect.** `v06b` documents facts that were resurrected nightly until 2026-09-08 and a review queue at 32.5k rows growing 2–6k/day. `sources.archived` + `archive_expires_at` hard-delete after 72 h; `pages.deleted_at` purges after 72 h; `forget()` leaves `~~struck text~~` plus a tombstone. Nothing distinguishes *"the Notion page is gone"* from *"the claim is wrong."*

**Build.** `pages.deprecated_at`, `pages.deprecated_reason`, `sources.deprecated_at`, and a `superseded_by` link type carrying the `term_replaced_by` semantics. Then port the VFB rule table verbatim into `docs/policy/DEPRECATION.md`, and enforce it in three places: (i) exclude deprecated pages from retrieval results **and from the denominators** used in `synthesize`'s summaries — the denominator clause is the part everyone forgets; (ii) a deprecated source still renders its accession as plain text but produces no link; (iii) a page whose only source is deprecated stays a valid query target. Deprecation never deletes; old slugs keep resolving (which B1's lineage makes true rather than aspirational).

### B7 — A known-defects layer

`corpus_defects(source_id, scope, predicate, valid_from, valid_until, reason, opened_by, closed_at)` — e.g. *"Slack connector dropped threads 2026-03-01…2026-03-14"*, *"OCR batch 44 mis-parsed tables"*. Any retrieval intersecting an open defect gets a stamp on the result, alongside the existing `evidence` field. ~1 day. Nothing in GBrain does this, and MaleCNS ships it as a first-class visualisation layer.

### B8 — Match-mode and `as_of` on the agent-facing verbs

`MEMORY_VERBS_v1` is frozen but **additive-forever**. Add to `entity()` (today: zero-LLM, p99 < 100 ms, CI-gated on a 20K-page corpus) a `match_mode ∈ {exact, alias, lineage, fuzzy}` field, and add `as_of` to `recall()` and `entity()`. VFB's `resolve_entity` already does the first and pairs it with an explicit instruction to the agent: check before building on a synonym or pattern match. GBrain has the substrate for it (`links.resolution_type`) and does not surface it.

### B9 — The one behaviour to invert

GBrain automates **merges** (slug normalisation, 50/run) and hands humans everything else. ConnectomeBench measures models as *good* at identification and split detection and *bad* at merge detection. Invert: let the cycle propose splits and type identifications automatically, and route every merge to a human with the evidence attached. This is a small change to an existing phase and it is the only recommendation in this report backed by a benchmark that measured exactly this decision.

---

## 4. Benchmarks, metrics, baselines, expected effects, kill criteria

The primary claim is **not** retrieval quality. Stating that up front is the difference between an honest proposal and another vendor benchmark.

| # | Metric | Baseline (GBrain today) | Instrument | Predicted effect | Reasoning |
|---|---|---|---|---|---|
| **M1** | **Anchor survival**: % of facts whose anchor still resolves to the intended span after 30 days of the real edit stream | Unmeasurable — no anchors exist. Proxy: % of `facts.entity_slug` values with no live page | Day-1–2 audit script | Proxy orphan rate 3–15% (est., low confidence) | Renames/merges are unlogged; the cycle merges up to 50 pages/run with no lineage row |
| **M2** | **As-of reproducibility**: re-run a fixed 100-question set against version *V* a week later; % byte-identical answers | Undefined (no versions) | `gbrain release` + replay | 100% by construction | This is a correctness property, not an experiment |
| **M3** | **Supersession accuracy** on `MemConflict`'s static + conditional slice (804 questions, per `g06`) | Measure | `g06` harness, one-switch ablation | **+10 to +25 pp on the conditional stratum; ~0 pooled** | MemStrata (via `g04`): deterministic SPO supersession takes evolving-knowledge accuracy from 0.20–0.47 to 0.95–1.00. I discount hard because that is a different corpus and B1 supplies only the *key*, not the policy |
| **M4** | **Stale-serve rate**: % of answers in a 200-question audit citing a deprecated page or dead source | Measure; `v06b` predicts non-trivial | Manual adjudication | −50% relative or better | VFB's denominator rule alone removes a whole class |
| **M5** | **Merge error rate**: sample 100 automatic slug merges, human-adjudicate | Measure | Manual | Predicted 5–20% wrong | ConnectomeBench: merge detection is where models fail |
| **M6** | **As-of latency overhead** vs snapshot-aligned | n/a | Bench | 1.9–2.6× on the annotation join; <10% of search latency | CAVE measured 525 → 978 → 1,385 ms |

**Pre-registered kill criteria.** Commit these before running anything (`g06`'s discipline: this corpus is full of post-hoc best-cell reporting).

- **K1 — B1 dies** if the measured anchor/slug breakage over 30 days of real traffic is **<2%** of facts. Then ship `page_lineage` alone (it costs a day) and stop; the anchoring machinery is not earning its complexity.
- **K2 — B2's delta path dies** if as-of overhead exceeds **3×** snapshot-aligned latency (CAVE's own worst measured case was 2.64×). Fall back to snapshot-only with weekly retention; do not build a lineage-expansion query planner.
- **K3 — B6 dies** if the deprecation policy fails to cut stale-serve rate by **≥50% relative** on the 200-question audit. Then the problem was never source-deprecation and the effort belongs to `g01`'s overlap constraint.
- **K4 — the whole process thesis is downgraded** if M3 shows **<10 pp absolute** improvement on the conditional stratum with the full stack in place. In that case the synthesis must say plainly: connectome-style curation buys reproducibility, auditability and governance, and does **not** buy answer accuracy. That is `g06`'s H2 and it is my modal expectation.
- **K5 — B9 is unnecessary** if the sampled merge error rate is **<5%**; leave the automatic merge alone and spend the day elsewhere.

---

## 5. Cost

**LLM tokens: zero per page.** Every borrow here is schema, policy, build tooling and enforcement. That matters more than it sounds: `g02` measured GBrain's write-side curation at **$0.0128/page actual** ($0.033 quoted, $0.260 at Opus-class) against **$0.0000576** to embed the same page — curation LLM spend is **222×–4,514×** embedding spend. A curation intervention that adds no per-page model call is, against that baseline, free.

**Storage.** Snapshots cover annotation tables only (`facts`, `takes`, `links`, `pages` metadata, `tags`), never `content_chunks` — at 1,024 dims each vector costs **8,192 B of HNSW index** and 1024-d wastes 46% of every 8 KB page (`g02`). For a 155,795-page brain at 2.40 chunks/page (`g02`'s measured figure) the annotation tables are single-digit GB; 90 daily snapshots of a delta-encoded annotation set adds an estimated **+$10–40/month** on top of the $135/month hosting `g02` measured. For calibration, CAVE runs ~2 TB and 1.8 billion annotations for **~$500/month** with a **~$360/month** floor — three orders of magnitude more data than a company brain.

**Engineering.** 10 working days for one engineer to reach the MVP in §7. Full production hardening of B1+B2 (re-anchoring heuristics, lineage-aware search, backfill of an existing 155K-page brain) is realistically **6–8 weeks**. CAVE's own note is the honest calibration: external labs needed *"a software developer or otherwise experienced technical person"* and *"a few weeks"* just to deploy it.

**The cost nobody publishes.** MaleCNS took **≈44 person-years** of reconstruction. `g02` searched exhaustively and found **no published account anywhere** of a company-brain librarian's hours — not the talk, not the repo, not 600 cached issues — and its bottom-up estimate of ~2.5–3 h/week ($800–1,950/month loaded) is explicitly the weakest number in that report. My proposal inherits that weakness: it makes curation *cheaper per decision* and does not tell you how many decisions there are.

---

## 6. Does a non-biological alternative do this better? (Item by item, honestly)

| Borrow | Better-specified alternative | Verdict |
|---|---|---|
| **B1 anchors** | **W3C Web Annotation Data Model** (`TextQuoteSelector` + `TextPositionSelector`), hypothes.is-style fuzzy re-anchoring | **Use the standard for the anchoring itself.** CAVE's supervoxel binding is a spatial special case; W3C selectors are the text-native form and are what I specified above. |
| **B1 lineage** | — | **No standard equivalent found.** Bitemporal SQL versions a row; it cannot re-key annotations across a merge. Provenance vocabularies describe derivation, not identity resolution at a timestamp. This is CAVE's genuine contribution and the reason this report exists. |
| **B2 as-of** | **SQL:2011 system-versioned + application-time tables** (`g01`), XTDB, Dolt, Datomic | **The standard wins on mechanism.** Build `g01`'s bitemporal tables; do *not* reimplement a materialisation service. CAVE's contribution here is empirical, not architectural: it proves as-of costs ~2× and shows the delta-merge trick for querying between snapshots. |
| **B3 status vocabulary** | Any state machine; the idea is not novel | **`flyem-snapshot`'s contribution is one `assert`.** The two-tier split and the exhaustiveness gate are ~20 lines. Take the idea, not a dependency. |
| **B4 release build** | **LakeFS, Dolt, DVC, Delta Lake**; Croissant / datasheets-for-datasets | **LakeFS or Dolt would do the versioning better.** What they do *not* give you is "quality reports are release artifacts" and "the threshold is in the filename." Those are policies. |
| **B5 confidence** | **W3C PROV-O**, model cards | **Use PROV-O vocabulary.** VFB's contribution is the *policy* — carry the source's scale unchanged, never normalise across sources, never hide, verified beats predicted. |
| **B6 deprecation** | **OBO Foundry obsolescence policy** — `owl:deprecated`, `IAO:0100001 term replaced by` | **Cite OBO Foundry, not VFB.** `term_replaced_by` *is* the OBO relation; VFB is applying standard bio-ontology practice. Its distinctive addition is the independent-axes rule and the per-surface enforcement table, including denominators. |
| **B7 defects layer** | Data-quality tooling (Great Expectations, Monte Carlo) | **Those tools alert; they do not annotate retrievals.** The connectome version is a queryable layer joined at read time. That framing is the borrow. |
| **B8 MCP surface** | GBrain's own `MEMORY_VERBS_v1` | Already the right shape. VFB contributes two additive fields: `match_mode` and version pinning. |
| **B9 merge policy** | — | Backed by ConnectomeBench; no alternative source measures this. |

**The composite honest verdict.** Most of this is standard archival, ontology and data-engineering practice — which is the same conclusion `g04` reached from library science, arrived at independently from biology. That convergence is itself evidence the recommendations are right. The connectome case earns its place in the synthesis for three reasons and not more: it is the only place where all of these run **together**; it runs at the **right scale** (10⁵ entities, 10⁹ annotations); and it **publishes what it cost** ($500/month, 4M edits, 500 users, 44 person-years, 1.9–2.6× as-of latency) where every commercial memory vendor publishes only wins.

---

## 7. Two-week MVP plan (one engineer, 10 working days)

**Measure before you build.** Days 1–2 exist because K1 can kill the largest item, and the measurement costs nothing.

| Day | Work | Output / gate |
|---|---|---|
| **1** | Audit script over the live brain: % of `facts.entity_slug` with no live page; count slug renames/merges in 90 days of git history; count facts whose `source` string does not locate a retrievable span | **M1 proxy baseline. Evaluate K1.** |
| **2** | Sample 100 automatic slug merges; human-adjudicate. Build the 200-question stale-serve audit set and score it against today's brain | **M5 and M4 baselines. Evaluate K5.** |
| **3** | **B3**: `pages.curation_status`, `INTERNAL_STATUS` / `PUBLISHED_STATUS` maps, the CI exhaustiveness assertion, field-level publish policy | Shipped; no migration risk; folds in the existing `unverified` / `create_safety` flags |
| **4** | **B7** `corpus_defects` + result stamping; **B8** `match_mode` on `entity()` | Shipped; both additive |
| **5–6** | **B1 part 1**: `page_versions` becomes content-addressed and append-only (`content_hash`, `actor`, `op`, `reason`, `parent_version_id`); `page_lineage` written by the merge/rename/`put_page` paths | The immutable substrate exists |
| **7** | **B1 part 2**: `fact_anchors` with W3C selector semantics; anchors written in `extract_facts`; best-effort backfill; `entity_slug` resolved through lineage at read | **M1 measurable for real** |
| **8–9** | **B2**: `brain_versions` registry; nightly materialisation of annotation tables only; `as_of` on `recall`/`search` with CAVE's delta path; bench against 525/978/1,385 ms | **M6. Evaluate K2.** |
| **10** | **B6**: `deprecated_at` columns, `docs/policy/DEPRECATION.md` ported from VFB, denominator fix in `synthesize`; re-run the stale-serve audit; **B9** flip merge to human-gated; cut `brain-2026-09-24-<sha>` with a status-distribution report and `RELEASE.md` | **M2 and M4. Evaluate K3.** A citable brain version exists. |

**Deliverable at day 10:** a tagged, citable brain version; a working as-of query; a published status contract; an identity lineage; a defects layer; and six measurements that decide whether weeks 3–8 are worth funding.

**Deliberately out of scope at 25 people** (following `g05`): per-document ACLs, a policy engine, cryptographic provenance chains, a CAVE-style microservice fleet. CAVE is five services and a Bigtable-backed chunked graph; port four of its invariants, not its architecture.

---

## 8. Risks, and what prior negative results say

1. **The substrate asymmetry — the biggest threat to the whole transfer.** CAVE's design rests on an **immutable EM volume** beneath a mutable segmentation. A company brain has no immutable substrate; its documents change under it constantly. Every guarantee CAVE offers is downstream of that immutability. This is why B1's first move is to *manufacture* one out of `page_versions`. If that fails — because GBrain's write paths mutate `pages` without snapshotting, or because storage cost pushes back — the rest of the stack degrades to ordinary bitemporal SQL, which `g01` already recommends and which does not need this report.
2. **Volumes are inverted.** The connectome has ~1.8B annotations over ~166k entities; a company brain has ~155,795 pages and ~100,720 takes. Their annotations are machine-generated at high density over few, stable entities; ours are sparse and semantic over many, unstable ones. Density arguments do not transfer.
3. **Curation is not cheap, and the connectome proves it.** ~44 person-years for MaleCNS; ~20 years of institutional effort; 4M edits from 500 users. **Borrowing the architecture without the labour budget gets you the schema and none of the quality.** Anyone quoting "220,000 pages, mostly agent-written" should be asked what their proofreading process is.
4. **ConnectomeBench is a negative result about models, and it lands on a shipped GBrain behaviour.** Poor merge-error detection; GBrain automates merges. Do not extend automation into merging on the strength of this report.
5. **The topology transfer is refuted and the reputational spillover is real.** Dhiman, [arXiv:2604.04033](https://arxiv.org/abs/2604.04033): the flyvis learning advantage vanishes under degree-preserving nulls and shared initialisation. Nothing in *this* proposal depends on connectome topology — but a reader who has seen that result will discount anything wearing a connectome label, so the process framing must be stated first and the biology disclaimed explicitly.
6. **Motivated reasoning, flagged against myself.** `v10a` and `v10b` refuted the FlyHash index and the dedup gate; `g07` left one mechanism standing and it has never been run on text. The process bridge is now carrying almost all of question (b). That is exactly the situation in which a surviving branch gets over-sold. My defence is the split fidelity rating (§2), the item-by-item concession that standards do it better (§6), and K4, which pre-commits to reporting a null.
7. **Governance ceiling is unchanged.** CAVE's `middle-auth` grants permissions **per service table, to groups** — not per annotation. That is the same category of ceiling `g05` documents for GBrain (source-granular, not document-granular). The connectome case offers no help with ACLs, and pretending otherwise would be the third instance in this corpus of citing a system for something it does not do.
8. **What this buys nothing for.** Relevance to a query; procedural memory / skills (`g07`: no counterpart, and none will appear); ranking quality; the labour question. `v01` established that GBrain's honest retrieval gain is +6.2 R@5 / +9.7 first-place-hit from typed edges, with the cross-encoder supplying the headline. Nothing here touches that number and nothing here should be cited as if it does.

---

## 9. One-paragraph pitch

Every algorithmic bridge from the fly to a company brain has now been measured and most have failed — FlyHash loses to dense embeddings and to SimHash, the connectome-topology advantage vanishes under a degree-preserving null, and the one mechanism that is buildable as published has never been run on text. What survives is not in the fly's brain; it is in the filing cabinet of the labs that mapped it. The connectome consortia spent a decade solving, at 166,700 entities and 1.8 billion annotations, exactly the problem Tan says is the product: keeping a corpus worth retrieving from while it is being rewritten underneath you. They solved it with four invariants a company brain can adopt in two weeks — bind every fact to an **immutable** anchor and resolve the mutable entity identity through a **lineage graph** at a timestamp (CAVE, and the one idea here with no standard substitute); cut **materialised versions** so a question can be asked as of a date, at a measured 1.9–2.6× latency; carry **confidence with its scale and its producer**, never normalised and never hidden; and publish a **deprecation policy** in which source-death and fact-death are independent axes, deprecation never deletes, and deprecated items drop out of the denominators as well as the results. Add a two-tier curation-status vocabulary whose publish mapping is guarded by a build-breaking assertion, a release that ships its own quality report, a map of the corpus's known defects, and the single evidence-backed behavioural correction — ConnectomeBench says models are good at splits and identification and bad at merges, so stop letting the nightly cycle merge pages and start letting it split them. The honest caveats are three: this is process transfer, not neuroscience, and the synthesis must say so; almost every piece has a better-specified standard behind it (W3C Web Annotation, SQL:2011, OBO Foundry, PROV-O), and the connectome's claim to attention is that it is the only place all of them run together at scale with published costs; and the modal expected outcome is that this buys reproducibility, arbitrability and governance while moving pooled retrieval accuracy by nothing at all — which I have pre-registered as a kill criterion rather than discovering after the fact.

---

## Sources

**Connectome curation infrastructure (primary, fetched 2026-09-10)**
- Dorkenwald S., Schneider-Mizell C.M., Brittain D., Halageri A., Jordan C., Kemnitz N., Castro M.A., Silversmith W., Maitin-Shephard J., *et al.* "CAVE: Connectome Annotation Versioning Engine." *Nature Methods* 22:1112–1120 (2025). https://doi.org/10.1038/s41592-024-02426-z · full text read at https://pmc.ncbi.nlm.nih.gov/articles/PMC12074985/ · preprint https://doi.org/10.1101/2023.07.26.550598
- CAVEclient — https://github.com/CAVEconnectome/CAVEclient · Materialization tutorial https://caveconnectome.github.io/CAVEclient/tutorials/materialization/ · Annotation tutorial https://caveconnectome.github.io/CAVEclient/tutorials/annotation/
- Dorkenwald S., McKellar C.E., Macrina T., *et al.* "FlyWire: online community for whole-brain connectomics." *Nature Methods* 19:119–128 (2022). https://doi.org/10.1038/s41592-021-01330-0
- `janelia-flyem/flyem-snapshot` (BSD-3-Clause) — https://github.com/janelia-flyem/flyem-snapshot · README https://raw.githubusercontent.com/janelia-flyem/flyem-snapshot/master/README.md · status vocabulary and publish policy read at `flyem_snapshot/outputs/neuprint/annotations.py` · status-count report at `flyem_snapshot/inputs/annotations.py:197,327`
- MaleCNS project site — download page (bulk files, `minconf-0.5`, `conf_pre`/`conf_post`, neo4j dump, CC-BY) https://male-cns.janelia.org/download/ · release notes https://male-cns.janelia.org/release/ · explore page (defects layers) https://male-cns.janelia.org/explore/
- Berg S., *et al.* "Sexual dimorphism in the complete *Drosophila* male central nervous system connectome." *Cell* 189(18):5504–5526.e15 (3 Sep 2026). https://doi.org/10.1016/j.cell.2026.08.015
- Schlegel P., Yin Y., Bates A.S., *et al.* "Whole-brain annotation and multi-connectome cell typing of *Drosophila*." *Nature* 634:139–152 (2024). https://doi.org/10.1038/s41586-024-07686-5
- `flyconnectome/flywire_annotations` — https://github.com/flyconnectome/flywire_annotations · column definitions https://raw.githubusercontent.com/flyconnectome/flywire_annotations/main/supplemental_files/README.md
- Virtual Fly Brain — Confidence Values https://www.virtualflybrain.org/docs/concepts/confidence-value/ · Dataset Versions and Deprecation https://www.virtualflybrain.org/docs/data/em/versioning/ · MCP Tool Guide https://www.virtualflybrain.org/docs/tutorials/vfb-mcp-guide/ · server https://vfb3-mcp.virtualflybrain.org
- Codex (Princeton) — https://codex.flywire.ai/ (dataset counts and sign-in policy read 2026-09-10)
- neuprint-python — https://github.com/connectome-neuprint/neuprint-python
- Brown J., Kirjner A., Vivekananthan A., Boyden E. "ConnectomeBench: Can LLMs Proofread the Connectome?" arXiv:2511.05542, NeurIPS 2025 Datasets & Benchmarks. https://arxiv.org/abs/2511.05542
- Bates A.S., Phelps J., Kim M., Yang Z., *et al.* "Distributed control circuits across a brain-and-cord connectome" (BANC). *Nature* 656:957–970 (8 Jun 2026). https://doi.org/10.1038/s41586-026-10735-w
- Dhiman. "Topological Sensitivity in Connectome-Constrained Neural Networks." arXiv:2604.04033. https://arxiv.org/abs/2604.04033

**GBrain (read directly at `master`, 2026-09-10)**
- https://github.com/garrytan/gbrain/blob/master/src/schema.sql — `sources` L26, `pages` L85, `page_generation_clock` L218, `content_chunks` L296, `links` L467, `page_versions` L569
- https://github.com/garrytan/gbrain/blob/master/src/core/migrate.ts — `facts` DDL at L2384
- https://github.com/garrytan/gbrain/blob/master/src/core/cycle.ts — `ALL_PHASES` at L108 (23 phases)
- https://github.com/garrytan/gbrain/blob/master/src/core/facts/decay.ts · `docs/protocol/MEMORY_VERBS_v1.md` · `docs/contradictions.md` · `docs/storage-tiering.md`

**Internal (this project)**
- `checkpoints/01-sweep-decisions.md` · `findings/gbrain-architecture.md` · `findings/flywire-connectome-simulation.md` · `findings/flyfly-recent-identification.md` · `findings/g01-bitemporal-prior-art.md` · `findings/g02-sizing-cost.md` · `findings/g04-librarian-spec.md` · `findings/g05-governance-acl.md` · `findings/g06-crux-experiment.md` · `findings/g07-neuro-mechanism-inventory.md` · `findings/v01-gbrain-benchmarks.md` · `findings/v02-malecns-date.md` · `findings/v03-banc-facts.md` · `findings/v05-gbrain-page-counts.md` · `findings/v06a-librarian-in-code.md` · `findings/v06b-librarian-skeptic.md` · `findings/v09b-memoryagentbench-skeptic.md` · `findings/v10a-h3d-flyhash.md` · `findings/v10b-flyhash-vs-modern.md`

**Method note.** This session's WebSearch budget was already exhausted (200/200) when this task began, so no independent novelty sweep was possible. Prior workers searched arXiv and the 2026 agent-memory literature and found no published mapping of connectome curation practice onto knowledge bases or agent memory; I inherit that finding at their confidence, not mine.

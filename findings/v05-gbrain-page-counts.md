# v05 — GBrain page counts, reconciled

**Lens:** reconcile. **Date of work:** 2026-09-10. **Verdict: PARTIALLY confirmed — with one correction and one new number.**

All five numbers in the claim exist and I read every one at its primary source. But they are not five
measurements of one quantity, and the contradiction every prior report drew (talk 220,000 vs README
155,795) compares the wrong pair. **On the day of the talk the README said 146,646 — a sixth number
that no report in `findings/` has.**

---

## 1. What a gbrain "page" actually is

Established from the code, not the marketing:

- `pages` is a table. DDL at [`src/schema.sql:85`](https://github.com/garrytan/gbrain/blob/master/src/schema.sql#L85):
  one row per document, `page_kind CHECK (page_kind IN ('markdown','code','image'))`, with `source_id`
  (federation), `deleted_at` (soft delete) and `type`.
- The number a user would quote is `BrainStats.page_count`
  ([`src/core/types.ts:1656-1664`](https://github.com/garrytan/gbrain/blob/master/src/core/types.ts#L1656)),
  computed in [`src/core/postgres-engine.ts:4739`](https://github.com/garrytan/gbrain/blob/master/src/core/postgres-engine.ts#L4739) as
  `SELECT count(*) FROM pages p WHERE p.deleted_at IS NULL AND (scope IS NULL OR p.source_id = ANY(scope))`.
  **So: DB rows, soft-deleted excluded, optionally scoped to a subset of sources.** `chunk_count` is a
  *separate* field over `content_chunks` — pages and chunks are never the same number.
- **`page` ≠ printed page.** A page is one document of arbitrary length: a one-line tweet or a 30 KB
  meeting transcript. The repo's own perf reasoning assumes "tens of KB per page" and models "a 47K-page
  brain with ~30KB/page is ~1.4GB" ([`TODOS.md:7246,7250`](https://github.com/garrytan/gbrain/blob/master/TODOS.md)).
- **People and companies are page *types*, not separate stores.** `type IN ('entity','person','company')`
  ([`postgres-engine.ts:4805-4812`](https://github.com/garrytan/gbrain/blob/master/src/core/postgres-engine.ts#L4805);
  canonical type list at [`src/core/types.ts:44`](https://github.com/garrytan/gbrain/blob/master/src/core/types.ts#L44)).
  So the hero line's "155,795 pages, 24,589 people, 5,340 companies" is **one quantity and two of its
  subsets** (29,929 of the 155,795), not three quantities. Every report so far has read it as three.
- **On-disk ≠ in-DB.** `gbrain.yml` splits `db_tracked` (committed to git, on disk) from `db_only` (bulk
  machine-generated content, gitignored, DB-resident, disk copy is only a cache)
  ([`docs/storage-tiering.md`](https://github.com/garrytan/gbrain/blob/master/docs/storage-tiering.md)).
  This is what makes "on-disk pages" a strict subset of brain pages, and it is the key to the 28,256 figure.

### The talk contains its own unit collision

At **11:35–11:38** Tan says "an AI agent holds a million tokens. That's about a thousand pages" — i.e. a
*printed* page, ~1,000 tokens. At **13:47** he says "about 220,000 pages." Under his own conversion that
would be 220M tokens; under gbrain's definition a page is a document averaging ~7× that size. The same
word does two jobs twelve minutes apart, and the second job is the load-bearing one.

---

## 2. The dated table

Every row read at its primary source today. "Date" = when that figure was *published in that artifact*
(GitHub GraphQL blame / commit archaeology), not when it was measured, except where the doc states a
measurement date.

| # | Figure | Source (exact) | Live from → to | Unit it actually counts | Status |
|---|---|---|---|---|---|
| 0 | **7,500 pages** | first README, commit `b22cbd34` | 2026-04-05 | an *embedding-cost worked example* ("7,500 pages via OpenAI text-embedding-3-large") | **Not a brain-size claim.** Ignore. |
| 1 | **17,888 pages, 4,383 people, 723 companies, 21 crons** | README hero, then copied verbatim into [`docs/ethos/ORIGIN.md:25`](https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md) | README: ≤2026-04-15 → **2026-05-22**; ORIGIN.md: frozen **2026-05-19** (commit `cdba533a`, v0.36.2.0) and never touched since | `pages` rows (page_count) | **Stale copy, not an independent measurement.** ORIGIN.md froze the April README hero 3 days before the hero was replaced. `test/readme-hero-anchors.test.ts:50` still cites "17,888 pages" as the format exemplar. |
| 2 | **28,256 on-disk pages** | [`docs/takes-vs-facts.md:84`](https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md) (commit `72674623`, v0.31.4) | measured **2026-05-10**, published same day | **markdown files on disk** that the takes extraction actually read | **Explicitly a subset.** Same paragraph: "Full takes extraction on a **~100K-page brain** (measured 2026-05-10) … 100,720 takes from 28,256 on-disk pages, $361.49". Not a brain size; the *coverage* of one job. |
| 3 | **96K pages** | [`docs/architecture/calibration-quality-gate-spec.md:21`](https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md) (commit `9a4ae096`, v0.37.2.0) | **2026-05-20** | brain page count, rounded | Same brain, same era as row 2 — both cite **6,239 unique holders**. Caveat: the repo uses "96K" for *chunks* too (`src/core/migrate.ts:2852` "96K-chunk brain"; `test/helpers/schema-diff.ts:70`), so the round number is unit-loose. |
| 4 | **146,646 pages, 24,585 people, 5,339 companies, 66 crons** | README hero, commit `3de06b6c` (v0.38.2.0) | **2026-05-22 → 2026-08-11** | page_count | **THE NUMBER LIVE ON THE DAY OF THE TALK.** Missing from all 15 prior reports. |
| 5 | **~220,000 pages** | talk [13:47], "Now it's a warehouse, about 220,000 pages written mostly by my agents" | **2026-07-16** (repeated on the YC podcast 2026-08-06) | **undefined** | **Appears nowhere in the gbrain repo at any commit** — I grepped `220,000\|220000\|220K` across the full working tree: zero hits outside unrelated Gmail test IDs. **+50.0% over the README that was live that day.** |
| 6 | **155,795 pages, 24,589 people, 5,340 companies, 66 crons** | [README.md:5](https://github.com/garrytan/gbrain/blob/master/README.md) (+ mirrored into `llms-full.txt:1843`) | **2026-08-12 → present** (verified 2026-09-10) | page_count | Current. Commit `1ec6a6e8`, 2026-08-12T23:12Z. Prior reports dated this 2026-09-08 — that's the repo's `pushed_at`, not the line's blame date. |

### README hero, traced commit-by-commit (the decisive evidence)

| Date checked | README commit | Hero figure |
|---|---|---|
| 2026-04-15 | `e5a9f012` | 17,888 / 4,383 / 723 / 21 crons |
| 2026-05-01 | `736e8de1` | 17,888 |
| 2026-05-22 15:00Z | `26c54588` | 17,888 |
| **2026-05-22 16:29Z** | **`3de06b6c`** | **→ 146,646** (the jump, in one commit: +719%) |
| 2026-06-02 | `f09f9177` | 146,646 |
| **2026-07-16 (talk day)** | `f09f9177` | **146,646** |
| 2026-07-31 | `25e4c0c3` | 146,646 |
| **2026-08-12** | **`1ec6a6e8`** | **→ 155,795** |
| 2026-09-08 (HEAD) | `43597b19` | 155,795 |

Three hand-edits in five months. Growth as published: +719% in one commit (2026-05-22), then **+6.2% in
the following 82 days**. That is not a measurement series; it is a marketing line refreshed when someone
remembers.

---

## 3. The numbers nobody cited — and why they matter

The CHANGELOG is a dated ledger of brain sizes and it does **not** agree with the README on any date.
Mapping each mention to its release header:

| Release date | Figure in CHANGELOG/docs | Whose brain |
|---|---|---|
| 2026-04-19 (v0.12.1) | 47K-page | unattributed |
| 2026-05-07 (v0.28.10) | 96K-page, "measured against a 96K-page production brain through PgBouncer (Supabase)" | production |
| 2026-05-20 (v0.37.5.0) | 105K-page ("one user with a 105K-page brain") | a user's |
| 2026-05-23 (v0.40.5.0) | **"a 4-source brain (default 197K pages, zion-brain 13K, media-corpus 5K, straylight 88K)"** = 303K total | federated, almost certainly Garry's |
| 2026-05-25 (v0.41.10.0) | 165K-page | "representative" |
| **2026-05-26 (v0.41.17.0)** | **"Garry's 197K-page personal brain, 6,594 conversation pages"** | **explicitly Garry's** |
| 2026-05-27 (v0.41.22.0) | "a real production brain (186K pages)" accreted 94 `pages.type` values (also [`docs/architecture/type-taxonomy.md:9`](https://github.com/garrytan/gbrain/blob/master/docs/architecture/type-taxonomy.md)) | production |
| 2026-05-27 (v0.41.21.0) | "re-scan **280K of 322K pages**" | production |
| 2026-06-01 (v0.42.7.0) | "one real 280K-page brain had a links table 99.7% untyped `mentions`" | production |
| after 2026-06-09 | **silence** — no brain-size figure appears in any release note through v0.48.5.0 | — |

**The contradiction is internal and same-week.** On 2026-05-22 the README hero was set to 146,646.
Four days later the CHANGELOG describes "Garry's 197K-page personal brain," and the day after that,
322K pages. The repo publishes 146,646 and 197K–322K in the same fortnight, for what is evidently the
same brain.

Three mechanisms are documented in the repo and could each explain part of a gap — none is ever stated
as *the* explanation for these numbers:

1. **Soft delete.** `page_count` excludes `deleted_at IS NOT NULL`; hard purge only happens 72 h later in
   the autopilot phase, and sweeps/`extract --stale` counts do not necessarily filter the same way.
2. **Federation scope.** `getStats` takes a `sourceIds` scope. A per-source number (default) and a
   brain-wide number differ by ~106K on the one date where both are published (197K default vs 303K total).
3. **Type unification / purges.** v0.41.22.0 (2026-05-27) collapsed 94 page types to 15 and called out
   "5.5K concept-redirect pages bloating orphan counts" — real deletions happen.

Worth noting for anyone tempted to rescue the 220,000: **it is arithmetically reachable** as an
all-sources total (146,646 default + the 88K `straylight` + 13K + 5K sources ≈ 253K; the README hero at
155,795 plus a shrunken satellite set lands near 220K). But Tan never says "across all sources," the
number is published nowhere, and this is reconstruction, not evidence. Confidence that 220,000 is a
scope difference rather than a rounded-up stage number: **~35%**.

---

## 4. Secondary discrepancy found in passing

The takes figures do not reconcile either. `docs/takes-vs-facts.md` (2026-05-10) reports **100,720 takes**
(70,960 takes / 24,342 facts / 2,875 bets / 2,649 hunches) over 6,239 holders; the calibration spec
(2026-05-20), citing the same 6,239 holders, says **"36K takes."** Not central to brain size, but it is
the same failure mode: a rounded number in a design doc that no one reconciled against the receipt ten
days earlier. Flag if the synthesis cites take counts.

---

## 5. What this changes for the synthesis

- The line "his own README says fewer pages than his talk" survives — **but the honest pair is
  220,000 (2026-07-16) vs 146,646 (live that day), a 50% gap**, not 220,000 vs 155,795. Using the
  September number understates the gap and gets the date wrong.
- **Drop 28,256 and 17,888 from any list of "conflicting brain sizes."** 28,256 is a self-declared
  subset of the same document that says the brain was ~100K; 17,888 is a frozen April copy in a doc
  nobody updated. Presenting five contradictory numbers overstates the case; the real case is stronger
  and simpler: *one hand-maintained marketing figure, refreshed 3 times in 5 months, that the repo's own
  release notes contradict by 30–120% within the same week, plus a stage number that appears in no
  artifact at all.*
- Do not use page count as a scale proxy in the fly/RAG argument without saying what a page is. A gbrain
  page is a document of arbitrary length; the talk's other use of "page" (1M tokens ≈ 1,000 pages) is
  ~7× smaller. Any "220,000 pages ≈ 139,255 fly neurons" numerology (flagged in
  `findings/flywire-connectome-simulation.md` as coincidence) is even weaker than that report allows,
  because the unit is undefined on one side.
- The genuinely citable fact about corpus scale is the *hygiene* number in the same repo, which is
  measured, dated and self-reported against interest: on the ~96K-page brain of May 2026, **34 of 500**
  candidate takes were falsifiable and **17 of those 34** were ungradeable (calibration spec).

## 6. Recommendation (one sentence, for the synthesis)

> Cite brain size only as a dated source pair — "155,795 pages per the GBrain README as of 2026-08-12
> (146,646 on the day of the talk), against the ~220,000 claimed on stage on 2026-07-16 and published in
> no artifact at any date" — and add that a GBrain "page" is a database row (one document of arbitrary
> length, soft-deleted rows excluded, scoped to whichever sources were counted), not a printed page.

### Confidence

- Numbers, dates, blame commits, and the `page_count` SQL definition: **high** (all read at primary source today).
- That the README hero is `getStats.page_count` specifically: **medium-high** (field-name and semantics match exactly; never stated in prose anywhere in the repo).
- That the 220,000 gap is a scope/federation artefact rather than a stage rounding: **low (~35%)**.

---

## Sources

Repo state: `garrytan/gbrain`, master @ `43597b19e50a3abf56409337f248f7966860293c` (2026-09-07T23:34-04:00),
`pushed_at` 2026-09-08T06:48Z, 29,764 stars, created 2026-04-05 (`gh api repos/garrytan/gbrain`).
Full-tree grep performed on a local clone; blame via GitHub GraphQL; historical README bodies via
`raw.githubusercontent.com/<sha>/README.md`.

- https://github.com/garrytan/gbrain/blob/master/README.md — line 5 hero: "155,795 pages, 24,589 people, 5,340 companies, 66 cron jobs"; line 14 "150K-page brain"; line 501 "PGLite … up to ~50K pages"; line 633 "80K-page PGLite brain"
- https://raw.githubusercontent.com/garrytan/gbrain/1ec6a6e8/README.md — 155,795 first appears, 2026-08-12T23:12:59Z
- https://raw.githubusercontent.com/garrytan/gbrain/f09f9177/README.md — **146,646**, the README live on 2026-07-16 (talk day)
- https://raw.githubusercontent.com/garrytan/gbrain/3de06b6c/README.md — 146,646 introduced, 2026-05-22T16:29:59Z (v0.38.2.0); the diff replaces "17,888 pages, 4,383 people, 723 companies, 21 cron jobs … built in 12 days"
- https://raw.githubusercontent.com/garrytan/gbrain/26c54588/README.md — still 17,888, 2026-05-22T15:00:42Z
- https://raw.githubusercontent.com/garrytan/gbrain/e5a9f012/README.md — 17,888, 2026-04-15
- https://raw.githubusercontent.com/garrytan/gbrain/b22cbd34/README.md — first README, 2026-04-05: "7,500 pages via OpenAI text-embedding-3-large" (cost example only)
- https://github.com/garrytan/gbrain/blob/master/docs/ethos/ORIGIN.md — line 25 "17,888 pages. 4,383 people. 723 companies. 21 cron jobs"; blame → commit `cdba533a`, 2026-05-19T04:11:02Z, unchanged since
- https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md — lines 82-88, "~100K-page brain (measured 2026-05-10) … 100,720 takes from 28,256 on-disk pages, $361.49, 83 errors (0.3%) … 6,239 unique holders"; blame → `72674623`, 2026-05-10T13:34:40Z (v0.31.4)
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/calibration-quality-gate-spec.md — line 21 "In production on a 96K-page brain with 36K takes across 6,239 holders"; header "Status: design, largely unshipped"; 6.8% falsifiability (34/500), 17/34 unresolvable; blame → `9a4ae096`, 2026-05-20T16:19:18Z
- https://github.com/garrytan/gbrain/blob/master/src/schema.sql — `CREATE TABLE IF NOT EXISTS pages` at line 85
- https://github.com/garrytan/gbrain/blob/master/src/core/postgres-engine.ts — `getStats` at 4721, `page_count` SQL at 4739-4740, `entity_pages` (`person`/`company`/`entity`) at 4805
- https://github.com/garrytan/gbrain/blob/master/src/core/types.ts — `BrainStats` at 1656; canonical page types at 44
- https://github.com/garrytan/gbrain/blob/master/docs/storage-tiering.md — `db_tracked` vs `db_only` tiers ("written to disk as a local cache but not committed to git")
- https://github.com/garrytan/gbrain/blob/master/test/readme-hero-anchors.test.ts — line 50, the hero-number regression guard, exemplar "17,888 pages"
- https://github.com/garrytan/gbrain/blob/master/CHANGELOG.md — v0.28.10 (2026-05-07) 96K-page production brain; v0.40.5.0 (2026-05-23) "4-source brain (default 197K pages, zion-brain 13K, media-corpus 5K, straylight 88K)"; v0.41.17.0 (2026-05-26) "Garry's 197K-page personal brain, 6,594 conversation pages"; v0.41.21.0 (2026-05-27) "re-scan 280K of 322K pages"; v0.41.22.0 (2026-05-27) "a real production brain (186K pages) … 94 distinct pages.type values … 5.5K concept-redirect pages"; v0.42.7.0 (2026-06-01) "one real 280K-page brain"
- https://github.com/garrytan/gbrain/blob/master/docs/architecture/type-taxonomy.md — line 9, "A production gbrain brain (186K pages)"; blame → 2026-05-27T14:01:28Z
- https://github.com/garrytan/gbrain/blob/master/TODOS.md — line 4323 "165K-page production class"; line 3481 "353K-page `extract --stale` sweep"; line 7250 "a 47K-page brain with ~30KB/page is ~1.4GB"
- https://www.youtube.com/watch?v=eBUyTS7SzV4 — "Every company should have a Brain", Garry Tan / AI Engineer, published 2026-07-16; transcript at `sources/transcript_eBUyTS7SzV4.txt`: [11:38] "an AI agent holds a million tokens. That's about a thousand pages"; [13:45-13:52] "started as a rooms full of books or so. Now it's a warehouse, about 220,000 pages written mostly by my agents"

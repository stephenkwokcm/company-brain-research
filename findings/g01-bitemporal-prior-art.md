# g01 — Bi-temporal prior art for contradiction arbitration

**Gap:** three prior reports (`neuro-inspired-rag.md`, `memory-hygiene.md` §3, `rag-taxonomy.md` L55) put "bi-temporal invalidation with a deterministic conflict policy" at #1 in their intervention ranking and cite **zero** database literature. The completeness critic flagged it (`completeness-critic.md` §6, and again in the RAG-engineer persona at §80). This report supplies the prior art, defines the terms, gives a buildable Postgres schema, and grades GBrain's `facts`/`takes` tables against it.

**Bottom line in one paragraph.** Bi-temporality is not an agent-memory idea. It is a 1980s database idea, specified as a committee language in 1994 (TSQL2), standardised in **SQL:2011**, and shipping in **Db2, SQL Server, MariaDB, Oracle and XTDB** today. The standard's answer to "what did we believe on date D" is two independent period columns per row — an *application-time* period the user sets and a *system-time* period the engine sets — plus a `PRIMARY KEY (..., period WITHOUT OVERLAPS)` constraint that makes "two contradictory current values" a **constraint violation rather than a retrieval problem**. That last part is the piece every agent-memory system has skipped, including Zep/Graphiti and including GBrain. What the LLM-era systems genuinely add over SQL:2011 is not the temporal model — it is (a) an extractor that manufactures the `(subject, predicate, object, valid_from)` key out of prose, and (b) a candidate-retrieval step that finds *which* stored row a new claim might contradict, because SQL cannot look up a key that does not exist yet. Everything downstream of those two steps is `UPDATE ... FOR PORTION OF`.

---

## 1. Valid time vs transaction time

The two axes, in the standard's own words ([Kulkarni & Michels, *Temporal features in SQL:2011*, ACM SIGMOD Record 41(3), Sept 2012](https://sigmodrecord.org/publications/sigmodRecord/1209/pdfs/07.industry.kulkarni.pdf), §2.1):

> "**valid time**, the time period during which a row is regarded as correctly reflecting reality by the user of the database."
> "**transaction time**, the time period during which a row is committed to or recorded in the database."
> "For any given row, its transaction time may arbitrarily differ from its valid time."

Both authors were IBM; Krishna Kulkarni was also on the 1993 TSQL2 committee, which is the lineage from the research language into the standard.

The distinction is not pedantry, and the company-brain case makes it vivid:

| | valid time | transaction time |
|---|---|---|
| Who sets it | the extractor / the human ("Acme's MRR was $2M **in January**") | the engine, at commit |
| Can it be backdated? | **yes** — a Slack message today can assert a fact about last March | **no** — by definition |
| Can it be corrected? | **yes** — "we had the January number wrong" | **never**; a correction is a *new* row |
| What question it answers | "what was true on D?" | "**what did we believe** on D?" |
| Failure if you omit it | you serve stale facts confidently (Tan's named failure mode) | you cannot audit the librarian, replay a decision, or explain a retracted answer |

The talk's failure mode — *"stale facts surfaced with confidence"* — is a **valid-time** failure. The talk's remedy — a librarian who prunes, and arbitration when facts disagree — creates a **transaction-time** obligation, because an arbitration is a write that changes what the brain believes, and an unaudited arbitration is indistinguishable from data loss. Most systems (GBrain included) implement the first axis and skip the second, then discover they cannot answer "why did the agent say X last month."

**One-axis-only names, so the taxonomy is legible:**
- *valid-time table* (a.k.a. application-time period table, "business time"): valid period only.
- *transaction-time table* (a.k.a. system-versioned table): system period only. Datomic, Dolt, git.
- *bitemporal table*: both. XTDB, Db2, MariaDB, and a hand-rolled SQL:2011 table.

---

## 2. The prior art, chronologically

### 2.1 TSQL2 (1993–1995) — the research language that failed to standardise
The TSQL2 committee formed in July 1993 (Snodgrass chairing; Jensen, Dyreson, Elmasri, Clifford, Lorentzos, Segev, Kulkarni and 11 others). Per [Snodgrass's own page](https://www2.cs.arizona.edu/~rts/tsql2.html):

> "TSQL2 is a temporal extension to the SQL-92 language standard. The TSQL2 committee was formed in July, 1993… the definitive version of the TSQL2 Language Specification was published as a 71-page TSQL2 technical report in September, 1994."

TSQL2's design used *hidden* period columns and *statement modifiers* that changed the semantics of an otherwise ordinary query. Both were rejected. Kulkarni & Michels, §3, are blunt about why:

> "In previous proposals, the period information was associated with the rows of temporal tables using an unnamed hidden column… One major drawback of this approach is that it is incompatible with SQL's notion of tables… The previous proposals resorted to a controversial technique of prefixing queries, constraints, and insert/update/delete statements with the so-called statement modifiers… Unfortunately, previous proposals contained no clear rules specifying the semantics of constructs prefixed with these statement modifiers, so it was hard to figure out the end result."

The SQL committee's temporal project "was eventually cancelled around 2001." The definitive practitioner text from the same lineage is **Richard T. Snodgrass, *Developing Time-Oriented Database Applications in SQL*, Morgan Kaufmann, July 1999, 504pp, ISBN 1-55860-436-7**, free from the author at <https://www2.cs.arizona.edu/~rts/tdbbook.pdf>.

**Lesson transferable to company brains:** the reason TSQL2 lost is the reason a memory system should not hide its temporal state behind implicit query rewriting. If "current" is computed by a hidden rule rather than stored in a visible column, nobody — human or agent — can reason about it. GBrain gets this right (`valid_from`/`valid_until` are ordinary visible columns); Graphiti gets it right; most vector stores that fake recency with a decay multiplier get it wrong.

### 2.2 SQL:2011 — the standard, and the piece everyone skips
Published December 2011. Three table shapes, all built from *named period definitions over ordinary columns*:

**(a) Application-time period table (valid time), user-controlled:**
```sql
CREATE TABLE Emp (
  ENo INTEGER,
  EStart DATE,
  EEnd DATE,
  EDept INTEGER,
  PERIOD FOR EPeriod (EStart, EEnd))
```
Periods are **closed-open**: *"a period represents all times starting from and including the start time, continuing to but excluding the end time."*

**(b) The constraint that matters — `WITHOUT OVERLAPS`.** Kulkarni & Michels build to it with exactly the company-brain example:

> "The triples (22217, 2010-01-01, 2011-09-10) and (22217, 2010-02-03, 2011-11-12) are not duplicates so they would be acceptable values for a conventional primary key… But note that the application-time periods of these rows overlap. Semantically, this says that the employee with ENo 22217 belongs to two departments, 3 and 4, during the period from Feb. 3, 2010 through Sept. 10, 2011… To achieve that, it must be possible to forbid overlapping application-time periods, which can be specified with this syntax:"

```sql
ALTER TABLE Emp ADD PRIMARY KEY (ENo, EPeriod WITHOUT OVERLAPS)
```

**This is the whole intervention.** "Two contradictory facts are live at the same time" stops being something a nightly probe discovers and becomes something the database refuses to store. The write fails, the writer is forced to run its conflict policy, and the policy's decision is the only way the row lands. Temporal referential integrity gets the same treatment: `FOREIGN KEY (EDept, PERIOD EPeriod) REFERENCES Dept (DNo, PERIOD DPeriod)`.

**(c) System-versioned table (transaction time), engine-controlled:**
```sql
CREATE TABLE Emp (
  ENo INTEGER,
  Sys_start TIMESTAMP(12) GENERATED ALWAYS AS ROW START,
  Sys_end   TIMESTAMP(12) GENERATED ALWAYS AS ROW END,
  EName VARCHAR(30),
  PERIOD FOR SYSTEM_TIME (Sys_start, Sys_end)
) WITH SYSTEM VERSIONING
```
Three rules make it an audit log rather than a mutable table: *"users are not allowed to assign or change the values of Sys_start or Sys_end"*; *"UPDATE and DELETE on system-versioned tables only operate on current system rows. Users are not allowed to update or delete historical system rows"*; and *"UPDATE and DELETE… result in the automatic insertion of a historical system row for every current system row that is updated or deleted."* A `DELETE` does not delete — it closes the system period.

**(d) Bitemporal = both periods on one table**, and the paper's §2.4 gives the exact query this gap-fill was asked for:

```sql
SELECT ENo, EDept
FROM Emp FOR SYSTEM_TIME AS OF TIMESTAMP '2011-07-01 00:00:00'
WHERE ENo = 22217 AND EPeriod CONTAINS DATE '2010-12-01'
```
> "returns the department where the employee 22217 worked as of December 1, 2010, **recorded in the database as of July 1, 2011**."

Two dates, two axes, one query. Read it as: *what did we believe on 2011-07-01 about how the world stood on 2010-12-01.*

**Named as still-missing in 2012** (§2.5, "Future directions"): period joins, period aggregates, period `UNION`/`INTERSECT`/`EXCEPT`, period normalization (coalescing adjacent equal-valued rows), and **multiple application-time periods per table**. That last one is a live constraint for a company brain — you get exactly one valid-time axis, so "when the deal was signed" and "when the deal takes effect" cannot both be periods.

### 2.3 Who shipped it

| System | Valid time | Transaction time | Constraint enforcement | Notes |
|---|---|---|---|---|
| **IBM Db2** | `BUSINESS_TIME` period | `SYSTEM_TIME` period + history table | `BUSINESS_TIME WITHOUT OVERLAPS` | Documents all three shapes under "Time Travel Query using temporal tables": system-period, application-period, bitemporal ([Db2 11.5 docs](https://www.ibm.com/docs/en/db2/11.5.0?topic=tables-temporal), [Db2 for z/OS 13](https://www.ibm.com/docs/en/db2-for-zos/13.0.0?topic=tables-temporal)). The closest thing to a complete SQL:2011 implementation. |
| **MariaDB** | application-time periods | `WITH SYSTEM VERSIONING` | period constraints | All three shapes, standard syntax: `CREATE TABLE t (x INT) WITH SYSTEM VERSIONING;` and `SELECT * FROM t FOR SYSTEM_TIME AS OF TIMESTAMP'2016-10-09 08:07:06';` ([docs](https://mariadb.com/kb/en/temporal-data-tables/)) |
| **SQL Server** (2016+) / Azure SQL | **no** | yes, `PERIOD FOR SYSTEM_TIME` + paired history table | n/a | Explicitly system-versioned only — *"Temporal tables (also known as system-versioned temporal tables)"*. Five `FOR SYSTEM_TIME` subclauses: `AS OF`, `FROM…TO`, `BETWEEN…AND`, `CONTAINED IN`, `ALL` ([docs](https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables)). If you use SQL Server you must hand-roll valid time. |
| **PostgreSQL 18** (2025-09-25) | via range column | **no** | **yes — `WITHOUT OVERLAPS` landed in core** | See §2.4. |
| **PostgreSQL extensions** | `periods` (Vik Fearing) reimplements SQL:2011 periods *and* `WITH SYSTEM VERSIONING` in triggers/views, compatible PG 9.5–15 ([repo](https://github.com/xocolatl/periods)); `temporal_tables` (Arkhipov) is *"system-period temporal tables only"* ([repo](https://github.com/arkhipov/temporal_tables)) | | | |
| **XTDB** (v2) | `_valid_from` / `_valid_to` | `_system_from` / `_system_to` | not exposed | Bitemporal by default, no opt-in: *"all data is bitemporal without having to think about storing or updating additional columns."* SQL built *"to reflect the SQL:2011 standard."* Supports `FOR VALID_TIME AS OF`, `FOR VALID_TIME ALL`, `FOR SYSTEM_TIME ALL`, `SETTING DEFAULT SYSTEM_TIME TO AS OF …` ([docs](https://docs.xtdb.com/quickstart/sql-overview.html)) |
| **Datomic** | **no** — model it yourself as an attribute | yes — the log is the model | n/a | *"A datom is an immutable atomic fact that represents the addition or retraction of a relation between an entity, an attribute, a value, and a transaction"*; filters are `as-of`, `since`, `history` over `:db/txInstant` ([data model](https://docs.datomic.com/whatis/data-model.html), [filters](https://docs.datomic.com/reference/filters.html)). Retraction is an assertion with `Op=false`, so nothing is destroyed. |
| **Dolt** | **no** | yes — git commits *are* the transaction-time axis | n/a | *"Dolt SQL supports a variant of SQL 2011 syntax to query non-HEAD revisions of a database via the AS OF clause"* — `SELECT * FROM myTable AS OF 'myBranch'`, `AS OF TIMESTAMP('2020-01-01')`, plus `dolt_history_<table>` system tables ([docs](https://docs.dolthub.com/sql-reference/version-control/querying-history)). Snapshot unit is the dolt commit, not the SQL transaction. |

### 2.4 PostgreSQL, precisely (because the sketch below has to run somewhere)
**PostgreSQL 18, released 2025-09-25**, added *"Temporal constraints, or constraints over ranges, for PRIMARY KEY, UNIQUE, and FOREIGN KEY constraints… specified by `WITHOUT OVERLAPS` for PRIMARY KEY and UNIQUE, and by `PERIOD` for foreign keys, all applied to the last specified column"* (Paul A. Jungwirth) — [release notes](https://www.postgresql.org/docs/current/release-18.html). Per [`CREATE TABLE`](https://www.postgresql.org/docs/current/sql-createtable.html):

> "If the `WITHOUT OVERLAPS` option is specified for the last column, then that column is checked for overlaps instead of equality… So for example `UNIQUE (id, valid_at WITHOUT OVERLAPS)` behaves like `EXCLUDE USING GIST (id WITH =, valid_at WITH &&)`. The `WITHOUT OVERLAPS` column must have a range or multirange type… By default, only range types are supported, but you can use other types by adding the `btree_gist` extension (which is the expected way to use this feature)."

**What PG18 does *not* have:** zero occurrences of `SYSTEM VERSIONING` or `FOR SYSTEM_TIME` in the PG18 release notes or the `CREATE TABLE` reference. So on Postgres you get the *constraint* half of SQL:2011 natively and must hand-roll the *system-versioning* half (a trigger, the `periods` extension, or the explicit close-and-reinsert pattern in §4). That is the single most load-bearing fact for anyone implementing the three reports' recommendation on GBrain's stack, and it is why the sketch below writes system-time transitions by hand.

### 2.5 The LLM-era systems, and what they actually add

**Zep / Graphiti** ([arXiv:2501.13956](https://arxiv.org/abs/2501.13956), Apache-2.0). Confirmed from source, `graphiti_core/edges.py:271-279` — `EntityEdge` carries exactly four timestamps, and the field docstrings map one-to-one onto SQL:2011:

```python
expired_at: datetime | None  # 'datetime of when the node was invalidated'   → system period end
valid_at:   datetime | None  # 'datetime of when the fact became true'       → valid period start
invalid_at: datetime | None  # 'datetime of when the fact stopped being true'→ valid period end
# plus created_at: datetime  (non-null)                                      → system period start
```

The arbitration is `resolve_edge_contradictions()` in `graphiti_core/utils/maintenance/edge_operations.py:538-571`. It is **31 lines of pure interval arithmetic with no model call**:

```python
if   (edge.invalid_at <= resolved.valid_at) or (resolved.invalid_at <= edge.valid_at):
        continue                                   # disjoint in valid time → not a contradiction
elif  edge.valid_at < resolved.valid_at:
        edge.invalid_at = resolved.valid_at        # new edge invalidates old
        edge.expired_at = edge.expired_at or utc_now()
```

Three things follow, and they answer the critic's question ("does Graphiti add anything over SQL:2011 other than an LLM extractor?") precisely:

1. **The arbitration rule is weaker than SQL:2011's `UPDATE ... FOR PORTION OF`, not stronger.** It is last-valid-writer-wins, expressed by hand.
2. **The genuinely new parts are upstream of it**: an LLM extractor that assigns `valid_at`/`invalid_at` from prose (`_extract_edge_timestamps`), and a *semantic search for invalidation candidates* (`edge_invalidation_candidate_results`, line 407). SQL:2011 assumes you know the key; the whole difficulty in a company brain is that the key must be manufactured from unstructured text before any temporal operator can fire. **That, and only that, is the delta over the 1994 design.**
3. **There is a real behavioural gap, verifiable from the source.** The `elif` fires only when `edge.valid_at < resolved.valid_at` *strictly*. If the incoming claim is **backdated** (its `valid_at` is earlier than or equal to the stored edge's), or if either `valid_at` is `None`, no branch fires and **both contradictory edges stay live**. Nothing in the store prevents that state, because there is no `WITHOUT OVERLAPS` constraint — the graph has no engine-enforced notion of "one value per (subject, predicate) per instant." A late-arriving correction about the past is exactly the case a company brain hits constantly ("actually the Q1 number was restated"). Confidence: **high** (read from source, `main` branch, 2026-09-10).

**TOKI** — [arXiv:2606.06240](https://arxiv.org/abs/2606.06240), Ziming Wang, submitted 2026-06-04: *"TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory."* This is the paper that closes the gap the three prior reports left open, and its framing is the one to adopt:

> "Persistent memory for an LLM agent is a write-heavy substrate: every belief update is a versioned write, and a new claim may contradict a stored one. Production systems use four resolution heuristics (last-writer-wins, evidence-weighted merge, await-confirmation, per-rule policy), yet none declares the isolation level it assumes or the write-time anomalies it admits. **We show that contradiction resolution is write-time concurrency control** and make the missing contract explicit."

Its claims, from the abstract: the four heuristics are typed as one family of bitemporal operators over a **dual-row schema**, each with an isolation precondition and a provenance annotation that **preserves the losing fact in an audit row**; a tightness companion proves that **"keyed logging of the adjudicating judge is necessary for replay consistency, which every audited baseline omits"**; and a verdict matrix over eight systems finds *"every baseline that keeps a language-model judge on the write path admits at least one of three write-time anomalies (replay inconsistency, belief-drift skew, audit erasure); a content-addressed engine-layer comparator avoids them only by removing the judge, and TOKI alone excludes all three while keeping it."* Reported numbers: on LoCoMo, the audit-row defence moves the score by 0.86, and removing the typed memory layer costs 0.49 accuracy over 1,444 answerable questions. Confidence in the *framing*: high (verbatim abstract). Confidence in the *numbers*: medium — abstract only, not verified against the paper body or an independent replication.

**MemStrata** ([arXiv:2606.26511](https://arxiv.org/abs/2606.26511), *Temporal Validity in Retrieval Memory*, 2026-06-25) and **Supersede** ([arXiv:2606.27472](https://arxiv.org/abs/2606.27472), 2026-06-25) supply the empirical case already summarised in `memory-hygiene.md` (embeddings separate "contradicted" from "rephrased" at AUROC 0.59; a deterministic SPO-keyed bi-temporal ledger moves evolving-knowledge accuracy 0.20–0.47 → 0.95–1.00). Both arXiv IDs verified live via the arXiv API on 2026-09-10.

**Synthesis of §2.5:** the agent-memory field converged, in 2025–2026, on a design the SQL committee published in 2011 — minus the constraints. Every system in the survey stores the four timestamps and none of them lets the engine enforce the invariant. TOKI's contribution is to name why that matters (it is concurrency control, and an unlogged judge breaks replay), which is the same objection a database engineer would raise on first read.

---

## 3. Modelling supersession vs contradiction vs debate

The three prior reports use these three words interchangeably. They are structurally distinct, and — this is the useful result — **the distinction is computable from the schema alone, with no model call.** Take a claim keyed as `(subject, predicate, object)` held by a `holder` over a valid interval:

| | Same `(subject, predicate)` | Valid intervals | Same `holder` | Decidable by | Resolution |
|---|---|---|---|---|---|
| **Supersession** | yes | **disjoint** | yes | pure interval arithmetic | trim the older interval's end to the newer one's start. No judge. Both rows survive. |
| **Contradiction** | yes | **overlapping** | **yes** | interval arithmetic | at most one can be true → **run the conflict policy**, log the judge, retain the loser as an audit row |
| **Debate** | yes | overlapping | **no** | interval arithmetic | **legal by construction** — two holders may disagree at the same instant. Never auto-resolved; retrieval returns both, labelled. |

Two consequences worth stating plainly:

1. **The line between supersession and contradiction is overlap; the line between contradiction and debate is the holder.** Neither needs an LLM. The LLM's only irreducible jobs are (i) turning prose into `(subject, predicate, object, valid_from)` and (ii) proposing which stored rows are candidates. This is precisely why `memory-hygiene.md`'s MemStrata result and `neuro-inspired-rag.md`'s MemoryAgentBench FactConsolidation result point the same way: the arbitration itself is cheap, deterministic code, and putting a judge on the write path is what introduces TOKI's three anomalies.
2. **"Debate" gives you an escape hatch that keeps the invariant true.** When the conflict policy cannot pick a winner, you do not weaken the constraint — you *re-key the loser's holder* from `org` to `source:crm`. The overlap constraint is satisfied (different holders), nothing is dropped, and retrieval can honestly say "the org record says $2M; the CRM says $2.4M; unresolved since 2026-03-04." This is the state GBrain's docs say it cannot currently express (see §5).

---

## 4. Postgres DDL sketch and the "what did we believe on date D" query

Targets PostgreSQL 18 (for `btree_gist` + range GiST; the `WITHOUT OVERLAPS` sugar is shown but a partial `EXCLUDE` is used because the invariant must be scoped to *current system rows only*, and `PRIMARY KEY … WITHOUT OVERLAPS` cannot be partial).

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TYPE claim_status AS ENUM ('asserted','superseded','retracted');

CREATE TABLE claims (
  claim_id     bigserial PRIMARY KEY,

  -- The key. Without it, "contradiction" is undefined and you are back to
  -- cosine similarity, which separates contradiction from paraphrase at
  -- AUROC 0.59 (arXiv:2606.26511).
  subject      text        NOT NULL,          -- 'companies/acme'
  predicate    text        NOT NULL,          -- 'mrr_usd'
  object       text        NOT NULL,          -- '2000000'

  -- WHO holds it. Same holder + overlap = contradiction. Different holder
  -- + overlap = debate. This single column is what makes the three-way
  -- distinction in §3 enforceable rather than editorial.
  holder       text        NOT NULL DEFAULT 'org',   -- 'org' | 'people/garry' | 'source:crm'

  -- VALID TIME (SQL:2011 application-time period). Extractor-set, backdatable,
  -- correctable. Closed-open, per the standard.
  valid        tstzrange   NOT NULL,

  -- TRANSACTION TIME (SQL:2011 system-time period). Engine-set. NEVER updated
  -- in place except to close it. Postgres has no WITH SYSTEM VERSIONING, so
  -- the writer maintains this by hand (see §4.2).
  sys          tstzrange   NOT NULL DEFAULT tstzrange(now(), 'infinity'),

  status       claim_status NOT NULL DEFAULT 'asserted',
  confidence   real         NOT NULL DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
  source       text         NOT NULL,        -- provenance is required, not optional
  source_span  text,                         -- the exact quoted evidence
  extracted_by text         NOT NULL,        -- 'model:haiku-4-5@prompt_v7' | 'human:garry'

  CHECK (NOT isempty(valid)),
  CHECK (lower_inc(valid) AND NOT upper_inc(valid))   -- closed-open, per SQL:2011 §2.1
);

-- THE INTERVENTION. Two live claims about the same thing, from the same
-- holder, overlapping in valid time, is now a 23P01 exclusion_violation
-- at write time -- not a nightly probe finding.
ALTER TABLE claims ADD CONSTRAINT claims_one_truth_per_holder
  EXCLUDE USING gist (
    subject   WITH =,
    predicate WITH =,
    holder    WITH =,
    valid     WITH &&
  ) WHERE (status = 'asserted' AND upper_inf(sys));
--   ^ partial: historical system rows and retracted rows are exempt, exactly as
--     SQL:2011 exempts historical system rows ("Historical system rows in a
--     system-versioned table form immutable snapshots of the past").

-- Hot read path: current beliefs by key.
CREATE INDEX claims_current ON claims (subject, predicate)
  WHERE upper_inf(sys) AND status = 'asserted';
-- Time-travel path.
CREATE INDEX claims_sys_gist   ON claims USING gist (sys);
CREATE INDEX claims_valid_gist ON claims USING gist (valid);

-- TOKI's necessity result: the adjudicating judge must be keyed-logged or
-- replay consistency is unrecoverable. The losing claim is preserved, not deleted.
CREATE TABLE claim_resolutions (
  resolution_id     bigserial PRIMARY KEY,
  winner_id         bigint NOT NULL REFERENCES claims(claim_id),
  loser_id          bigint NOT NULL REFERENCES claims(claim_id),
  policy            text   NOT NULL,   -- 'source-tier' | 'later-valid-wins' | 'confidence' | 'human'
  judge             text   NOT NULL,   -- 'rule:source-tier@v3' | 'claude-haiku-4-5@prompt_v7' | 'people/garry'
  judge_inputs_hash text   NOT NULL,   -- content-addressed: makes the decision replayable
  rationale         text,
  decided_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (winner_id, loser_id)
);

-- An intentional, known disagreement. The thing GBrain's docs say it cannot mint.
CREATE TABLE claim_debates (
  debate_id  bigserial PRIMARY KEY,
  subject    text NOT NULL,
  predicate  text NOT NULL,
  valid      tstzrange NOT NULL,
  opened_at  timestamptz NOT NULL DEFAULT now(),
  opened_by  text NOT NULL,
  note       text,
  closed_at  timestamptz,
  closed_by  bigint REFERENCES claim_resolutions(resolution_id)
);
```

### 4.1 Supersession (no judge)
New claim `N` = (`companies/acme`, `mrr_usd`, `2500000`, holder `org`, valid `[2026-04-01, ∞)`).
Stored `O` = (…, `2000000`, holder `org`, valid `[2026-01-01, ∞)`). They overlap **only because `O`'s interval was left open**, which is the normal state — nobody knows when a fact will stop being true. Trim it. This is SQL:2011's `UPDATE Emp FOR PORTION OF EPeriod FROM … TO …`, written out because Postgres lacks the syntax:

```sql
BEGIN;
  -- close O's system period: this is no longer what the brain holds
  UPDATE claims SET sys = tstzrange(lower(sys), now())
   WHERE claim_id = :o_id AND upper_inf(sys);

  -- re-assert O as a NEW system row with a trimmed valid period
  INSERT INTO claims (subject,predicate,object,holder,valid,status,confidence,source,source_span,extracted_by)
  SELECT subject,predicate,object,holder,
         tstzrange(lower(valid), lower(:n_valid)),   -- [2026-01-01, 2026-04-01)
         'superseded', confidence, source, source_span, extracted_by
    FROM claims WHERE claim_id = :o_id;

  INSERT INTO claims (...) VALUES (...);            -- N
COMMIT;
```
Note what did **not** happen: no `UPDATE claims SET valid = …` in place. An in-place edit to a period column destroys the transaction-time record and makes §4.3's second query lie.

### 4.2 Contradiction (judge required, judge logged)
`N` = (…, `mrr_usd`, `2400000`, holder `org`, valid `[2026-01-01, ∞)`) — a *backdated* claim overlapping `O`. The plain insert raises `23P01`. The writer catches it and runs a deterministic policy ladder:

```
1. source tier      (curated page > CRM export > chat transcript)   → winner
2. later valid_from                                                  → winner
3. higher confidence                                                 → winner
4. otherwise → DEMOTE TO DEBATE: re-key N's holder to 'source:crm',
   INSERT INTO claim_debates, flag for the librarian.
```
Steps 1–3 write a `claim_resolutions` row and mark the loser `status='retracted'` (retained, never deleted — TOKI's "audit erasure" anomaly is exactly deleting it). Step 4 is the escape hatch from §3: the constraint is satisfied because the holders now differ, both claims survive, and retrieval labels the disagreement.

### 4.3 "What did we believe on date D"
The question is ambiguous, and the ambiguity *is* the point — it is why one timestamp is not enough.

```sql
-- (1) What was true on D, as we understand it TODAY.  [valid time only]
SELECT subject, predicate, object, holder, confidence, source
FROM   claims
WHERE  upper_inf(sys)                      -- current system rows
  AND  valid @> :D::timestamptz
  AND  status <> 'retracted';

-- (2) THE question: what the brain BELIEVED on D_sys, about the world at D_val.
--     SQL:2011 equivalent:
--       SELECT ... FROM claims FOR SYSTEM_TIME AS OF :D_sys
--       WHERE valid CONTAINS :D_val
--     XTDB equivalent:
--       SETTING DEFAULT SYSTEM_TIME TO AS OF :D_sys
--       SELECT ... FROM claims FOR VALID_TIME AS OF :D_val
SELECT subject, predicate, object, holder, confidence, source, extracted_by
FROM   claims
WHERE  sys   @> :D_sys::timestamptz        -- rewind the brain's knowledge
  AND  valid @> :D_val::timestamptz        -- ask about the world at this instant
  AND  status <> 'retracted';
-- The everyday case is D_sys = D_val = D: "on 2026-03-01, what did we think
-- was true on 2026-03-01" -- i.e. reconstruct the exact context an agent
-- would have retrieved that day. This is unanswerable with one time axis.

-- (3) The audit query transaction time exists for: what did we get WRONG?
--     Retroactive corrections -- rows whose value for a given valid instant
--     changed between two system times.
WITH believed_then AS (
  SELECT subject, predicate, object FROM claims
   WHERE sys @> :D_sys::timestamptz AND valid @> :D_val::timestamptz
     AND holder = 'org' AND status <> 'retracted'
), believed_now AS (
  SELECT subject, predicate, object FROM claims
   WHERE upper_inf(sys)             AND valid @> :D_val::timestamptz
     AND holder = 'org' AND status <> 'retracted'
)
SELECT COALESCE(t.subject, n.subject)     AS subject,
       COALESCE(t.predicate, n.predicate) AS predicate,
       t.object AS believed_then,
       n.object AS believed_now
FROM believed_then t
FULL OUTER JOIN believed_now n USING (subject, predicate)
WHERE t.object IS DISTINCT FROM n.object;

-- (4) Debate view: where do holders currently disagree?
SELECT subject, predicate, valid, array_agg(holder || '=' || object ORDER BY holder) AS positions
FROM   claims
WHERE  upper_inf(sys) AND status = 'asserted' AND valid @> now()
GROUP  BY subject, predicate, valid
HAVING count(DISTINCT object) > 1;
```

Query (3) is the one that turns Tan's "librarian" from a vibe into a measurable job: it is a direct readout of how often the brain was wrong and got corrected, per entity, per predicate.

---

## 5. Assessment: GBrain's `facts` / `takes` schema

Read from source on 2026-09-10: `src/core/migrate.ts` (v40 `facts` DDL at line 2384, `takes` at 1271, v122 ontology at ~5490), `src/core/cycle/phases/consolidate.ts`, `docs/contradictions.md`, `docs/takes-vs-facts.md`.

### 5.1 Column-by-column against SQL:2011

| SQL:2011 concept | `facts` | `takes` | Verdict |
|---|---|---|---|
| application-period start | `valid_from TIMESTAMPTZ NOT NULL DEFAULT now()` | `since_date TEXT` | facts: correct. takes: **`TEXT`**, so not orderable or range-comparable without a cast |
| application-period end | `valid_until TIMESTAMPTZ` (nullable = open) | `until_date TEXT` | present |
| `PERIOD FOR` / closed-open semantics | none | none | absent — a column *pair* with no period metadata and **no `CHECK (valid_until > valid_from)`**, the one constraint SQL:2011 says a period definition implies |
| **`PRIMARY KEY (…, period WITHOUT OVERLAPS)`** | **none** | **none** | **absent — the central gap.** Zero occurrences of `EXCLUDE USING`, `tstzrange`, `daterange`, `WITHOUT OVERLAPS` or `btree_gist` across `migrate.ts` **and** `schema.sql` (1,618 lines). Nothing prevents two live facts with the same `entity_slug`+`dimension` and different values. |
| system-period start (`ROW START`) | `created_at TIMESTAMPTZ NOT NULL DEFAULT now()` | `created_at` | present |
| **system-period end (`ROW END`)** | **none** | **none** | **absent.** `expired_at` is a tombstone set by `forget()`, not a transaction-time close; `consolidated_at` is a pipeline marker. Neither closes a system period. |
| `WITH SYSTEM VERSIONING` (auto history row on every update) | none | none | absent in SQL — but see §5.4, git supplies it out-of-band |
| `FOR SYSTEM_TIME AS OF` | none | none | absent |
| holder / who believes it | **absent** | `holder TEXT NOT NULL` (`self`\|`brain`\|`world`\|`people/<slug>`) + `weight` | **only in the cold table** |
| supersession pointer | `superseded_by BIGINT REFERENCES facts(id)` | `superseded_by INTEGER` (**no FK**) | facts: correct. takes: unreferenced integer |
| provenance | `source TEXT NOT NULL` (the `remember` verb errors `provenance_required` on empty) | `source TEXT` nullable | **facts is stronger than every system in §2.5** |
| keyed judge log (TOKI necessity condition) | — | — | present but **decoupled**: `eval_contradictions_cache` keys on `(chunk_a_hash, chunk_b_hash, model, prompt_version, truncation_policy)`, which is exactly the keyed judge logging TOKI proves is necessary — but it lives in an eval table and is not joinable to the fact rows it adjudicated |

### 5.2 Verdict: GBrain is uni-temporal with an audit stamp, not bitemporal

Migration v122's own inline comment claims otherwise:

> "facts already gives **bi-temporal validity** (`valid_from`/`valid_until`/`expired_at`), supersession (`superseded_by`), remote redaction (`visibility`), confidence, provenance (`source_markdown_slug`), embedding, and corroboration (`consolidated_into`)." — `src/core/migrate.ts`, migration 122 `facts_ontology_dimension`

All three named columns are on the **valid-time axis** (or are tombstones). None is a transaction-time end. Under the standard's definitions the table is an **application-time period table with a creation stamp** — one axis, not two. This is a documentation defect, not a design lie, and it is worth correcting because the comment is the thing a future contributor will trust when deciding whether "what did we believe on D" is answerable. It isn't, from SQL.

**Confidence: high.** Verified by direct read of the DDL plus a repo-wide absence check for the transaction-time constructs.

### 5.3 The concrete failure the missing constraint permits
This is not hypothetical, and it follows from three lines that are individually reasonable:

1. `consolidate` scans only unconsolidated facts: `WHERE consolidated_at IS NULL AND expired_at IS NULL AND (valid_until IS NULL OR valid_until > now())`, grouped into `(source_id, entity_slug)` buckets with `HAVING COUNT(*) >= 3` (`consolidate.ts:68-78`, defaults at `:52-55` — threshold `0.85`, `minFactsPerBucket 3`, `minOldestAgeMs 24h`).
2. Every member of a processed cluster is then stamped `consolidated_at` (`consolidate.ts:241-244`).
3. Within a cluster, the chronological writeback stamps each older fact's `valid_until = next_newer.valid_from`, and **"The newest fact keeps `valid_until = NULL`"** (`consolidate.ts:246-273`).

Therefore: tonight's cluster leaves exactly one fact per cluster open-ended. Tomorrow's contradicting fact about the same entity is clustered **only against other unconsolidated facts** — yesterday's winner is invisible to it. The two never meet, no `valid_until` is stamped, and the brain now holds **two facts about the same entity with `valid_until IS NULL`, both current, with different values**. Supersession *within* a nightly cycle works; supersession *across* cycles does not. And because there is no overlap constraint, the database is content.

`docs/contradictions.md` describes the mitigation honestly — a probe that samples retrieval pairs, date-pre-filters >30d, runs an LLM judge into a six-verdict enum, reports a Wilson 95% CI, and emits paste-ready `resolution_command`s — while stating the invariant: *"Probe never mutates the brain… only `consolidate` writes `valid_until` (a grep guard pins this)."* That is a **detection** system for a state a **constraint** would have made unrepresentable. In TOKI's terms, GBrain sits in the "removed the judge from the write path" corner: it avoids replay inconsistency and audit erasure (facts are never deleted; `forget()` expires with an audit trail) at the cost of belief-drift — contradictory rows can coexist indefinitely until a human runs a probe and pastes a command.

**Second-order point on the arbitration key.** What actually decides supersession in GBrain is *recency within a greedy cosine cluster at threshold 0.85* — i.e. semantic similarity is the key, not `(subject, predicate)`. That is precisely the discriminator MemStrata measured at AUROC 0.59 for separating contradiction from paraphrase. Two mitigations make the blast radius small in practice: the decision only orders facts *inside* a cluster (where semantic distance is small by construction), and it only stamps `valid_until` chronologically — it never deletes and never picks a semantic winner. But the key is still similarity, and migration v122 shows the repo already has the right key sitting unused: `dimension` + `value_hash`, with a unique index on `(source_id, entity_slug, dimension, value_hash, source_markdown_slug)`. That is a *dedup* key on the value. Change it to an overlap constraint on `(source_id, entity_slug, dimension)` over the valid period and GBrain has SQL:2011 §2.2.1.

### 5.4 The credit GBrain deserves: git is its transaction-time axis
`docs/architecture/system-of-record.md` is unambiguous — *"The GitHub repo (markdown + frontmatter) is the system of record. The Postgres/PGLite database is a derived cache. We do not back up the database — we rebuild it from the repo"* — enforced by `scripts/check-system-of-record.sh`.

That means the missing transaction-time axis **exists**: commit time is when the brain recorded a belief, and `git log -p docs/companies/acme.md` reconstructs "what did we believe on D." This is not a workaround; it is **Dolt's architecture** (`AS OF 'commit-hash'`, `dolt_history_<table>`) with the version control outside the database instead of inside it. Two honest caveats: (i) it is not queryable — you cannot join git history against `facts` in SQL, so query (3) in §4.3 is a shell script over commits rather than a query; and (ii) it is page-granular, not claim-granular, so it tells you the page changed, not which claim was retracted or who adjudicated it.

### 5.5 The missing third state
`docs/contradictions.md` says it outright: intentional-disagreement findings render as `# manual review: …` because **"a mark-as-debate subcommand does not exist yet, so nothing is minted that would fail when pasted."** So of §3's three states, GBrain models supersession (recency-in-cluster), detects contradiction (probe + six-verdict judge), and **cannot represent debate at all** in the hot layer. The substrate is already there in the cold layer — `takes.holder` is exactly the discriminator that separates contradiction from debate — but `takes` has TEXT dates, no FK on `superseded_by`, and no overlap constraint. **The bitemporal claim ledger the three reports are asking for is, structurally, the union of GBrain's two existing tables**: `facts`'s timestamps and enforced provenance plus `takes`'s `holder` and `weight`, under one exclusion constraint.

### 5.6 Recommended minimal change (ordered by cost)
1. **Add a `CHECK (valid_until IS NULL OR valid_until > valid_from)`.** One line. SQL:2011 says a period definition implies it; `facts` lacks it.
2. **Add the overlap constraint on the ontology subset**, where the key already exists (`dimension` is non-NULL): `EXCLUDE USING gist (source_id WITH =, entity_slug WITH =, dimension WITH =, tstzrange(valid_from, COALESCE(valid_until,'infinity')) WITH &&) WHERE (dimension IS NOT NULL AND expired_at IS NULL)`. Requires `btree_gist` (PGLite parity needs checking — flag as an open question). This turns §5.3's cross-cycle failure into a write error at the exact moment the second claim arrives, which is also the only moment the evidence for arbitrating it is in context.
3. **Add `sys_until TIMESTAMPTZ` and stop updating `valid_until` in place.** `consolidate.ts:268-273`'s `UPDATE facts SET valid_until = $1` becomes close-and-reinsert (§4.1). Costs one row per supersession; buys query (2) and query (3) of §4.3, i.e. an auditable librarian.
4. **Add `holder` to `facts`** (default `'org'`), making the debate escape hatch of §4.2 expressible and closing the `takes`/`facts` split.
5. **Join the judge log to the rows it judged**: a `claim_resolutions`-shaped table referencing `facts(id)` and carrying the existing `(model, prompt_version, truncation_policy)` cache key. This is TOKI's necessity condition, and GBrain already computes the hash — it just discards the linkage.

Steps 1–2 are hours and remove the failure in §5.3. Steps 3–5 are the actual bi-temporal upgrade.

---

## 6. What remains unresolved

- **TOKI's numbers are abstract-only.** The LoCoMo deltas (0.86, 0.49) and the eight-system verdict matrix were not verified against the paper body. Anyone citing them downstream should read the PDF. Confidence in the framing (contradiction resolution = write-time concurrency control; judge must be keyed-logged): high. Confidence in the numbers: medium.
- **`btree_gist` under PGLite.** GBrain runs two engines (`pglite-engine` WASM and `postgres-engine`). Whether PGLite ships `btree_gist` and GiST exclusion constraints determines whether recommendation §5.6-2 can be schema-level or must be a trigger. Not verified — no WebSearch budget remained. Best estimate: PGLite bundles a limited extension set and `btree_gist` is **probably not** available by default, which would force the constraint into a `BEFORE INSERT` trigger for the WASM engine. **Confidence: low.** Verify before planning.
- **Db2 version history.** IBM's docs confirm the three temporal shapes and the `SYSTEM_TIME`/`BUSINESS_TIME` period names, but the pages are JS-rendered and I could only read the navigation trees; I did not verify the introducing release (widely reported as Db2 10, 2012, i.e. ahead of the standard's publication). **Confidence in feature set: high. In version: low — treat as unverified.**
- **Whether the overlap constraint is affordable at GBrain's scale.** ~100K pages / ~100K takes / an unknown but larger fact count. A partial GiST exclusion constraint costs an index probe per insert on the ingest hot path. Unmeasured.
- **Oracle Flashback / Workspace Manager** were not surveyed (Oracle has valid-time via Temporal Validity and transaction-time via Flashback Data Archive). Named for completeness; the SQL:2011 shape is the same.

---

## Sources

**Standard and prior art**
- Krishna Kulkarni, Jan-Eike Michels (IBM), "Temporal features in SQL:2011," *ACM SIGMOD Record* 41(3), September 2012 — https://sigmodrecord.org/publications/sigmodRecord/1209/pdfs/07.industry.kulkarni.pdf *(all §2.2 verbatim quotes and DDL examples)*
- Richard T. Snodgrass, "TSQL2 Temporal Query Language" — https://www2.cs.arizona.edu/~rts/tsql2.html
- Richard T. Snodgrass, *Developing Time-Oriented Database Applications in SQL*, Morgan Kaufmann, July 1999, ISBN 1-55860-436-7 — https://www2.cs.arizona.edu/~rts/tdbbook.pdf

**Implementations**
- PostgreSQL 18 release notes (release date 2025-09-25), temporal constraints — https://www.postgresql.org/docs/current/release-18.html
- PostgreSQL `CREATE TABLE`, `WITHOUT OVERLAPS` / `PERIOD` / `EXCLUDE` — https://www.postgresql.org/docs/current/sql-createtable.html
- `periods` extension (SQL:2011 periods + `WITH SYSTEM VERSIONING` for PG 9.5–15) — https://github.com/xocolatl/periods
- `temporal_tables` extension (system-period only) — https://github.com/arkhipov/temporal_tables
- MariaDB temporal data tables — https://mariadb.com/kb/en/temporal-data-tables/
- Microsoft SQL Server temporal tables (2016+, system-versioned only) — https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables
- IBM Db2 11.5, "Time Travel Query using temporal tables" — https://www.ibm.com/docs/en/db2/11.5.0?topic=tables-temporal
- IBM Db2 for z/OS 13, "Creating temporal tables" — https://www.ibm.com/docs/en/db2-for-zos/13.0.0?topic=tables-temporal
- XTDB SQL overview (bitemporal columns and `FOR VALID_TIME` / `FOR SYSTEM_TIME`) — https://docs.xtdb.com/quickstart/sql-overview.html
- XTDB, "What is XTDB?" — https://docs.xtdb.com/intro/what-is-xtdb.html
- Datomic data model — https://docs.datomic.com/whatis/data-model.html
- Datomic database filters (`as-of`, `since`, `history`) — https://docs.datomic.com/reference/filters.html
- Dolt, "Querying database history" (`AS OF`, `dolt_history_*`) — https://docs.dolthub.com/sql-reference/version-control/querying-history

**Agent-memory temporal systems**
- Zep: A Temporal Knowledge Graph Architecture for Agent Memory — https://arxiv.org/abs/2501.13956
- Graphiti `EntityEdge` four timestamps — https://github.com/getzep/graphiti/blob/main/graphiti_core/edges.py (lines 271–279)
- Graphiti `resolve_edge_contradictions` — https://github.com/getzep/graphiti/blob/main/graphiti_core/utils/maintenance/edge_operations.py (lines 538–571)
- TOKI: A Bitemporal Operator Algebra for Contradiction Resolution in LLM-Agent Persistent Memory, Ziming Wang, 2026-06-04 — https://arxiv.org/abs/2606.06240
- Temporal Validity in Retrieval Memory (MemStrata), 2026-06-25 — https://arxiv.org/abs/2606.26511
- Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents, 2026-06-25 — https://arxiv.org/abs/2606.27472

**GBrain (primary, read 2026-09-10)**
- `src/core/migrate.ts` — `takes` DDL L1271, `facts` DDL L2384, indexes L2433–2447, migration 122 `facts_ontology_dimension` ~L5490 — https://github.com/garrytan/gbrain/blob/master/src/core/migrate.ts
- `src/schema.sql` (1,618 lines; no `EXCLUDE`/range/`WITHOUT OVERLAPS`) — https://github.com/garrytan/gbrain/blob/master/src/schema.sql
- `src/core/cycle/phases/consolidate.ts` — defaults L52–55, unconsolidated scan L68–78, mark-consolidated L241–244, `valid_until` writeback L246–273, greedy clustering L297–320 — https://github.com/garrytan/gbrain/blob/master/src/core/cycle/phases/consolidate.ts
- `docs/contradictions.md` — probe architecture, six-verdict enum, "never mutates", "a mark-as-debate subcommand does not exist yet" — https://github.com/garrytan/gbrain/blob/master/docs/contradictions.md
- `docs/takes-vs-facts.md` — https://github.com/garrytan/gbrain/blob/master/docs/takes-vs-facts.md

**Prior reports in this project**
- `findings/memory-hygiene.md`, `findings/rag-taxonomy.md`, `findings/neuro-inspired-rag.md`, `findings/memory-systems-landscape.md`, `findings/gbrain-architecture.md`, `findings/v06a-librarian-in-code.md`, `findings/completeness-critic.md`

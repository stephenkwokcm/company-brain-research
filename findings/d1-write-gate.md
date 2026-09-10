# d1 — The write gate: a two-compartment fly Bloom filter at GBrain's narrow waist

**Key:** `d1-write-gate` · design panel, angle 1 (write-side hygiene) · 2026-09-10 · author: research worker (Claude Opus 5)
**Brief:** FlyHash + fly Bloom filter as an ingest novelty/dedup/staleness gate in front of the `facts` table and the dream-cycle contradiction probe (cheap trigger for expensive LLM judging).
**Repo state:** all GBrain paths read at commit `43597b19e50a3abf56409337f248f7966860293c` (`VERSION` 0.48.5.0), verified live (HTTP 200 on `raw.githubusercontent.com` at that SHA, 2026-09-10).
**Primary sources read first-hand for this report:** the PNAS 2018 fly-Bloom-filter PDF (equations and parameter regimes quoted below are extracted from the paper text, not from secondary reports); `docs/contradictions.md`; `src/schema.sql`; `src/core/content-sanity.ts`; `src/core/import-file.ts`; `src/core/ops/pages.ts`; pgvector README; SAGE arXiv abstract.

---

## 0. TL;DR — the pitch in one paragraph

Build **`flygate`**: a stateful scoring seam on GBrain's write path, immediately after the existing exact-`content_hash` short-circuit at `src/core/import-file.ts:727`, that computes **two** fly Bloom filter novelty scores over one shared FlyHash code of the chunk embedding — a fast compartment (~4-day memory) and a slow one (~25-day memory). Two filters at different time constants are not decoration: they are the *only* way to separate the two things a single novelty score confounds, and the PNAS paper names that confound as its own open problem ("how can the fruit fly distinguish between two similar odors observed far apart in time vs. two dissimilar odors observed recently — both of which may elicit a high novelty response?"). The pair `(n_γ, n_α)` quantises into three write-time routes: **chronic duplicate** → skip the LLM triage judge and `takes` extraction; **genuinely new** → admit unexamined; and the band that pays for the whole thing, **recurrence-after-dormancy** — content similar to something the brain saw three weeks ago but not this week — which is *exactly* where superseded facts live and which GBrain's contradiction probe **structurally cannot see today**, because it is query-sampled and its pipeline diagram reads "Date pre-filter: skip pairs whose dates are >30d apart." Judging only that band, at write time, with the source document still in context, costs **~$0.68/month at 250 writes/day** against a write-side curation line of ~$96/month, and it pays for itself if it suppresses **0.7%** of writes as near-duplicates. The fly's contribution is one specific thing — a constant-state clock that gives recurrence-after-dormancy, which no incumbent primitive supplies — and I say plainly below that SimHash owns dedup, `1 − max cosine` owns the distance axis, and a SQL query on `pages.last_retrieved_at` owns the long horizon.

---

## 1. What I am NOT proposing (stated first, because the corpus has been burned here)

The verified findings this round refuted most of the fly programme. I am not re-litigating any of it:

| Refuted proposal | Why | Source |
|---|---|---|
| FlyHash as a `vector.backend` / semantic index | The pgvector HNSW scan is **3.78 ms @100K, 10.73 ms @250K** inside a ~3,272 ms answered question — 0.14% of the path. A free, instant, lossless index change is worth ≤0.14%. | `g02-sizing-cost.md` (measured locally) |
| FlyHash code as a stored representation | At d=1536 and the fly's own 40× expansion the sparse code is **7,680 B — larger than the 6,152 B float32 vector** and 38× larger than binary quantization. And pgvector indexes `sparsevec` with HNSW only "up to 1,000 non-zero elements" (README line 255), so the fly's parameters do not fit the database. | `v10b`, pgvector README |
| FlyHash as the **dedup** hash | On H3D, FlyHash is **last of five** semantic-agnostic fingerprints: CSFCube MAP 0.1325 vs SimHash 0.1770 / MinHash 0.2451 / Winnowing 0.2678; RELISH 0.4305 @ 1744 s vs SimHash 0.4756 @ 0.00 s. SimHash strictly dominates on both quality and time. | `v10a`, `v10b`, arXiv:2607.08382 |
| FlyPrompt as a "sparse-expansion router" | REAR is a **dense Gaussian** matrix + ReLU (M=10,000), no k-WTA. The gain is expert modularity, not expansion (RanPAC 79.92 vs FlyPrompt 86.76). | `g07` mechanism 7 |

Checkpoint 01's decision (i) — "write-side: FlyHash/fly-Bloom-filter novelty gate + **dedup** at ingest" — must be split, as `v10b` demands: **the dedup half is refuted; the novelty/staleness half survives.** This design implements only the surviving half, and uses SimHash for the dedup half.

---

## 2. Mechanism borrowed and its fidelity

### 2.1 The primitive (fidelity: **Deep**)

Dasgupta, Sheehan, Stevens & Navlakha, "A neural data structure for novelty detection," *PNAS* 115(51):13093–13098, 18 Dec 2018, DOI [10.1073/pnas.1814448115](https://doi.org/10.1073/pnas.1814448115). Quoted verbatim from the PDF I extracted:

> "Let `w(i)` correspond to the weight of the *i*th KC→MBON-α′3 synapse. Initially, each `w(i) = 1`. After an odor `x` is observed, each synaptic weight changes as follows:
> `w(i) = w(i) × δ` if the *i*th KC is active for `x`; `w(i) + ε` if the *i*th KC is not active for `x`. **[2]**
> … the synaptic weights of the *k* active KCs for the odor each decay by some factor, `0 ≤ δ < 1`. The remaining `m − k` KCs strengthen by a small amount, `0 ≤ ε ≤ 1`."

Readout, also verbatim: "we sum the weights of the *k* active KC→MBON-α′3 synapses for odor `x` and normalize by *k* to generate novelty responses between 0 and 1." The filter is **inverted** (all weights start at 1) so novel items score high. Setting `δ = ε = 0` recovers a classical binary Bloom filter exactly.

This is Deep fidelity in `g07`'s sense: same data type (a dense vector), same streaming regime, same problem statement. Twenty lines of code. Nothing is re-derived except `δ` and `ε` — and §3 derives those from measurable quantities rather than leaving them free.

### 2.2 The coder (fidelity: **Deep as a mechanism, and this is its only defensible slot**)

FlyHash — Dasgupta, Stevens & Navlakha, *Science* 358(6364):793–796 (2017), DOI [10.1126/science.aam9868](https://doi.org/10.1126/science.aam9868). Fixed sparse binary projection `M ∈ {0,1}^{m×d}` with `s` ones per row, drawn once and never trained; `y = Mx` (adds only); winner-take-all `Γ_k` keeps the top `k`. Critically, and per `v10a`'s correction, it runs **on top of the embedding GBrain already computes** — the `m ≫ d` regime — not over shingles. That cell (a modern sentence embedding → FlyHash) is the one H3D leaves empty; H3D ran a *contraction* over 3-shingle counts, which inverts the algorithm's defining property. Here FlyHash is not the index and not the dedup hash; it is only the addressing function that turns an embedding into `k` slot indices for the filter.

### 2.3 The architecture (fidelity: **Analogy**)

Two filters over one code at different time constants is borrowed from Huang et al., "Dopamine-mediated interactions between short- and long-term memory dynamics," *Nature* 634:1141–1149 (2024), DOI [10.1038/s41586-024-07819-w](https://doi.org/10.1038/s41586-024-07819-w) — the mushroom body's γ compartments (~30 min plasticity, MBON-γ1pedc depression <1 h) and α′2α2/α3 compartments (~100 min then much slower, MBON-α3 depression >24 h), a ~50× ratio, **reading the same Kenyon-cell population**. My γ:α ratio is 6× rather than 50×, chosen by the capacity law in §3, so this is a topology transplant with re-derived constants: Analogy, not Deep. I am not claiming Huang's promotion *gate* (the MBON→DAN disinhibition), which `g07` correctly flags as resting on an untested assumption that an agent-side readout analogue exists.

---

## 3. The design law — where δ, ε, m and k come from

`g07`'s single biggest caveat on this mechanism is: "δ and ε are free parameters with no data-derived values; largest n ever tested = 5,000; never tested on text." That is the gap this section closes. Everything below is my derivation from the paper's own update rule; it is checkable arithmetic, not a citation.

**Setup.** Let `p = k/m` be the probability that a given weight is in the active set of a random insert, `r` the arrival rate in writes/day, and `w*` the target equilibrium mean weight (use 0.5, the midpoint of the readout range).

**(L1) Equilibrium.** Ignoring the clip at 1, per insert `E[Δw] = p(δ−1)w + (1−p)ε`. Setting this to zero at `w = w*`:

```
ε = p (1 − δ) w* / (1 − p)
```

**(L2) Recovery time = the horizon.** A weight driven to ~0 by a duplicate recovers to `w*` after `T = w*/ε` inserts. Substituting L1 and writing `n = T` (the number of items the filter effectively "remembers"):

```
1 − δ = m / (k · n)          ε = w* / n
```

Two closed forms. **Choose the horizon `n` in items; δ and ε follow.** This is the missing derivation.

**(L3) The floor.** `δ ≥ 0` requires `n ≥ m/k`. So the fastest the filter can forget is **`m/k` inserts** — which is exactly the number of inserts needed for the average weight to be touched once. The filter's clock is one full sweep of the weight vector.

**(L4) The duplicate-signal identity — the single most useful consequence.** How loud is one duplicate, measured against the clock? Duplicate signal on the score is `w*(1−δ) = w*·m/(k·n)`; one day of recovery drift is `ε·r = w*·r/n`. Dividing:

```
one duplicate insert  ≡  m/(k·r) days of drift  ≡  H_min
```

**A duplicate is worth exactly one floor-period, always.** So in a filter tuned to horizon `H`, the duplicate dip occupies `H_min/H` of the dynamic range — 50% at `H = 2·H_min`, 7% at `H = 15·H_min`. This is the precise, corrected statement of why one filter cannot do both jobs: pushing `H` out to a month to get a staleness clock compresses the duplicate signal into single-digit percent of the range, where code-collision noise lives. It is not that a long-horizon filter is *blind* to duplicates; it is that its duplicate signal-to-range ratio is pinned to `H_min/H` and you cannot decouple them with one `(δ, ε)` pair.

**(L5) Discriminability sets `k`, not the classical capacity rule.** The paper's sizing rule `m = 30n` (robustness check at `m = 10n`) is derived for the **static** filter (`δ = ε = 0`), where slots are permanently reset and capacity really does run out; the time-sensitive variant lives in SI Appendix and no capacity rule is re-derived for it. In the AIMD regime the equilibrium already bounds the state, so the binding constraint is the **signal-to-noise ratio of the readout**, not slot exhaustion. Each weight cycles between `w*δ` and `w*` over `m/k` inserts, so its standard deviation is ≈ `w*(1−δ)/√12`; the score averages `k` of them, and the signal at age `Δt` is `w*(1−δ)(1 − Δt/n)`:

```
SNR(Δt)  ≈  √(12k) · (1 − Δt/n)        →  at the horizon edge (Δt = 0.9n):  SNR ≈ 0.35·√k
```

and two distinct items share only `k²/m` slots on average (0.25 slots at `m=65,536, k=128`). **So `k` should be as large as code specificity allows** — larger `k` raises SNR *and* lowers the floor `m/(k·r)`, and specificity is nowhere near binding at these sizes. This is where I depart from a naive transplant, and I flag it as the softest step in the derivation: **L5 is my analysis, not the paper's**, and K5 tests it.

**Three things this kills, one it rescues:**

- It kills "O(1) state independent of corpus size" as a *selling point*: the state is O(1) in the corpus, but the reachable horizon is `O(m)`, so a longer memory costs proportionally more weights and proportionally more projection work.
- It kills the **single-filter** design, by L4: one `(δ, ε)` pair yields one `n`, and therefore one `H_min/H` ratio. A filter cannot report both a 4-day and a 25-day novelty.
- It kills the naive extrapolation of `m = 30n` to a whole company brain: at 373,908 chunks that is 11.2 M weights and ~1.4 G integer adds per write. Infeasible — and unnecessary, because that rule is for the static filter.
- It **rescues** the design, because with time-decay `n` is not the corpus size — it is the number of items inside the horizon window. The filter never has to represent the brain, only the recent stream.

**(L6) Two filters separate distance from time.** Model a single filter's score as `n(Δt) ≈ 1 − s · h(Δt)`, where `s ∈ [0,1]` is the code overlap with the nearest prior item (the distance term) and `h` is the retention curve (1 at `Δt = 0`, → 0 at the horizon). One filter returns a product and cannot invert it. Two filters over the *same code* with different retention curves give

```
(1 − n_γ) / (1 − n_α)  =  h_γ(Δt) / h_α(Δt)      → depends only on Δt   (time estimate)
(1 − n_α)  at small Δt                            → ≈ s                 (distance estimate)
```

That is a direct, cheap answer to PNAS 2018's own Discussion item (ii), quoted verbatim from the PDF: *"how can the fruit fly distinguish between two similar odors observed far apart in time vs. two dissimilar odors observed recently — both of which may elicit a high novelty response? Might other MBONs be involved?"* **Yes: other MBONs, with other time constants, reading the same KCs** — which is what Huang 2024 measured six years later. This separability is the intellectual core of the design, and §11 makes it a pre-registered kill criterion, because the paper also says outright that "there is little biological knowledge of how distance sensitivity and time sensitivity combine," so multiplicative separability is an **assumption I am making, not a result I am citing**.

### 3.1 Worked default configuration

Assume a 25-person brain writing **r = 250 pages/day** (25 × 10/person/day, `g02`'s ceiling case) at **d = 1536** (`content_chunks.embedding vector(1536)`, `src/schema.sql:302`; brains configured for Voyage use 1024 — the projection is dim-specific and must be rebuilt on a change).

| Parameter | Value | Derivation |
|---|---|---|
| `m` (filter length) | 65,536 | Largest power of two whose projection cost stays ≈4 ms; sets both horizons via L3; projection cost is 96 × 65,536 = 6.3 M adds |
| `s` (fan-in per row) | 96 | 6.25% of d=1536; the fly is 12% (6 claws of ~50 PNs), Ryali et al. use 10% |
| `k_γ` (fast compartment winners) | 128 | L3 floor `m/k_γ = 512` inserts = **2.05 d**; edge SNR ≈ 3.9; slot overlap `k²/m` = 0.25 |
| `n_γ` | 1,024 items ≈ **4.1 days** | Chosen inside the window |
| `δ_γ`, `ε_γ` | **0.500**, **4.88e-4** | L2: `1−δ = 65536/(128·1024)`, `ε = 0.5/1024` |
| `k_α` (slow compartment winners) | 64 | Nested: the top-64 of the same top-128 sort. Floor `m/k_α = 1,024` inserts = **4.1 d**; edge SNR ≈ 2.8 |
| `n_α` | 6,144 items ≈ **24.6 days** | 6× the γ horizon, matching Huang 2024's compartment separation in kind if not in ratio |
| `δ_α`, `ε_α` | **0.833**, **8.14e-5** | L2: `1−δ = 65536/(64·6144)`, `ε = 0.5/6144` |
| Seed | persisted `uint64` | **The seed is part of the index.** Lose it and every stored score is garbage. |

`δ_γ = 0.5` means one duplicate halves the active weights — the paper's rule that "decay after initial exposure should be aggressive" — while recovery needs 1,024 inserts, satisfying its second rule that "recovery from familiarity back to novelty should be relatively slower."

**Both `k` values are above the paper's own tested band** (`k ∈ [5, 50]`), which I flag as an extrapolation — justified by L5 (SNR rises as `√k`, specificity is not binding at `k²/m = 0.25` slots of overlap) but untested at these values. Note this diverges from the *Science* 2017 hashing regime (5% activity): PNAS 2018 deliberately runs far sparser tags to suppress collisions, and I follow PNAS because this is a filter, not a hash index.

### 3.2 Cost, and the lazy-update trick that makes it affordable

Naively, Eq. 2 touches all `m − k` inactive weights per insert — 65,520 float ops. Unnecessary. Store `(w[i], t[i])` where `t[i]` is the global insert index at which `w[i]` was last written. Because a weight only ever *gains* `ε` while inactive, and the clip at 1 is monotone, the lazy read is **exact**:

```
w_now(i) = min(1, w[i] + ε · (T − t[i]))
```

So both read and write are **O(k)**, independent of `m`. Per write: one projection (`s·m = 96 × 65,536 = 6.3 M` integer adds, ~4–6 ms in a TypedArray loop), one partial sort for the top-128, and 2 × 128 weight updates. State: 2 × 65,536 × (4 B weight + 4 B index) = **1.05 MB per source**, constant forever.

---

## 4. Exact insertion points in GBrain

All paths verified live at SHA `43597b19e50a3abf56409337f248f7966860293c`.

### 4.1 The hook: after exact dedup, before the expensive path

`src/core/import-file.ts` is the narrow waist. It already carries an **exact** `content_hash` short-circuit:

- L709 `const hash = contentHash({...})` — "#3694: the hash formula lives in ONE place — utils.contentHash"
- L727 `if (existing?.content_hash === hash && !opts.forceRechunk) return { slug, status: 'skipped', chunks: 0, ... }`
- L756 "#1309 — identity-based cross-slug dedup pre-check" (`content_hash` OR `frontmatter.id`)
- L627 notes "the daemon's 24h LRU dedup (separate consumer keyed on same hash)"

**So GBrain ships exact dedup and has no near-duplicate detection at all.** `flygate` slots in immediately after L756, before chunking/embedding at L820+. Two ordering constraints:

1. The gate needs an embedding, which GBrain computes later. Resolve by embedding the **title + first 2 KB** (reusing `SCAN_HEAD_BYTES = 2048` from `content-sanity.ts:53`) as a cheap page-level probe vector; full chunk embeddings still happen downstream and are unaffected. One extra embedding call at $0.0000576/page — noise against $0.0128.
2. `assessContentSanity` (`src/core/content-sanity.ts:337`) is documented "Pure function — same inputs always produce the same outputs." A novelty gate is stateful, so it must be a **sibling** at the same call site (`import-file.ts:508`), never a new branch inside that function. Preserving that purity property is a hard design constraint.

### 4.2 Consumers

| Consumer | File / phase | Change |
|---|---|---|
| Ingest triage judge | `src/core/cycle/synthesize.ts:129`, `DEFAULT_TRIAGE_THRESHOLD = 0.5` | Chronic-duplicate band **skips the judge entirely** — the judge is an LLM call and this is the direct cost saving |
| `takes` extraction | `consolidate` / `propose_takes` phases (`src/core/cycle.ts:108`) | Chronic-duplicate band skips extraction; this is the $0.0128/page line |
| Contradiction probe | `docs/contradictions.md`; `src/core/eval-contradictions/auto-supersession.ts` | **New write-time trigger** on the recurrence band, alongside the existing query-sampled path |
| Weeding score | `pages.last_retrieved_at` (`src/schema.sql:126`, B-tree index at L275) | Tick the filters on **retrieval** as well as write, so the α filter measures content-level circulation |
| Salience | `pages.emotional_weight REAL` (`src/schema.sql:103`) | Optional: feed `n_α` into `recompute_emotional_weight` as a recurrence term |

### 4.3 Schema (migration v147 — the repo is at 146)

```sql
CREATE TABLE IF NOT EXISTS flygate_state (
  source_id        TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  compartment      TEXT NOT NULL CHECK (compartment IN ('gamma','alpha')),
  seed             BIGINT NOT NULL,
  m                INTEGER NOT NULL,
  k                INTEGER NOT NULL,
  s_fanin          INTEGER NOT NULL,
  delta            REAL NOT NULL,
  epsilon          REAL NOT NULL,
  embedding_model  TEXT NOT NULL,      -- reset the filter when this changes
  embedding_dim    INTEGER NOT NULL,
  inserts_total    BIGINT NOT NULL DEFAULT 0,   -- the global T for lazy reads
  weights          BYTEA NOT NULL,     -- float32[m]
  touched_at_idx   BYTEA NOT NULL,     -- uint32[m], the lazy t[i]
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_id, compartment)
);

ALTER TABLE pages
  ADD COLUMN IF NOT EXISTS novelty_gamma REAL,
  ADD COLUMN IF NOT EXISTS novelty_alpha REAL,
  ADD COLUMN IF NOT EXISTS novelty_band  TEXT
    CHECK (novelty_band IN ('duplicate','recurrence','novel','impossible'));
CREATE INDEX IF NOT EXISTS pages_novelty_band_idx
  ON pages (source_id, novelty_band) WHERE novelty_band IS NOT NULL;
```

The projection matrix is **not** stored — it is regenerated deterministically from `(seed, m, s_fanin, embedding_dim)`, which keeps the row small and makes `gbrain rebuild` reproducible. The state table is `db_only` (never committed to git), consistent with `docs/storage-tiering.md` and with `g05`'s erasability recommendation: a `DELETE` is a complete erasure.

### 4.4 Config keys (`gbrain.yml`, following the repo's existing `dream.drift.enabled` / `search.expansion_variant_budget` convention)

```yaml
ingest:
  flygate:
    enabled: false            # default OFF, like drift/skillopt/enrich_thin
    scorer: hybrid            # hybrid | fly-bank | max-cosine | simhash | sage
    m: 65536
    fanin: 96
    gamma: { k: 128, window_items: 1024 }
    alpha: { k: 64,  window_items: 6144 }
    thresholds: { dup: 0.35, recur_gamma: 0.60, recur_alpha: 0.45 }
    band_budget_pct: 10       # hard cap on writes routed to the LLM probe
    on_duplicate: route       # route | flag — NEVER 'block'
```

`on_duplicate: route` is not a default I would let anyone change. `v06a` established GBrain's doctrine in its own words — orphan pages are `human_only` because "archive is product judgment, not maintenance"; `content_flag` was chosen over hiding because "a false positive costs a one-line note, not a vanished page." A novelty gate that *blocks* is both a violation of that doctrine and, per `g05`, a new denial surface under **OWASP ASI06 Memory & Context Poisoning**. **The gate routes and annotates; it never refuses a write.** The only hard block in GBrain stays `ContentSanityBlockError`, which fires on six hand-vetted junk regexes, not on judgment.

---

## 5. Algorithm sketch

```ts
// src/core/flygate/coder.ts
function flyCode(x: Float32Array, P: SparseProj, kGamma: number, kAlpha: number) {
  // 1. Divisive normalisation — the fly's ORN→PN gain control. Skipping this is
  //    the most common transplant error: without it the code tracks magnitude,
  //    not identity. For unit-norm embeddings it is a no-op; for others, divide
  //    by the mean of |x|.
  const xn = divisiveNormalise(x);
  // 2. y = Mx, adds only. P is CSC: for each input dim j, the rows it feeds.
  const y = new Float32Array(P.m);
  for (let j = 0; j < xn.length; j++) {
    const v = xn[j]; if (v === 0) continue;
    for (const i of P.rowsFor(j)) y[i] += v;
  }
  // 3. Winner-take-all, nested: top-kGamma, and its own top-kAlpha prefix.
  const top = partialSortDesc(y, kGamma);      // indices, descending
  return { gamma: top, alpha: top.slice(0, kAlpha) };
}

// src/core/flygate/filter.ts — PNAS 2018 Eq. 2, lazy form
class FlyBloom {
  w: Float32Array; t: Uint32Array; T = 0;      // T = global insert counter
  constructor(readonly m: number, readonly delta: number, readonly eps: number) {
    this.w = new Float32Array(m).fill(1);      // INVERTED: novel scores high
    this.t = new Uint32Array(m);
  }
  private cur(i: number) { return Math.min(1, this.w[i] + this.eps * (this.T - this.t[i])); }
  score(active: Int32Array) {                  // READ BEFORE WRITE
    let sum = 0; for (const i of active) sum += this.cur(i);
    return sum / active.length;                // ∈ [0,1]
  }
  insert(active: Int32Array) {
    for (const i of active) { this.w[i] = this.cur(i) * this.delta; this.t[i] = this.T; }
    this.T++;                                  // inactive weights gain lazily
  }
}
```

**Band policy.** `n_α ≤ n_γ` up to noise, because α sees strictly more history. So the readout is a **1-D curve in Δt with a 2-bit quantisation**, and the fourth corner is an invariant, not a state:

| `n_γ` | `n_α` | Meaning | Route |
|---|---|---|---|
| low | low | Chronic duplicate — seen this week *and* this month | Skip triage judge + `takes` extraction; append to merge-candidate queue; page still written |
| **high** | **low** | **Recurrence after dormancy** (4 d < Δt < 25 d) | **Run the contradiction probe now**, against the ≤5 nearest existing chunks, with the source in context |
| high | high | Genuinely novel, or last seen >25 d ago | Admit, no probe |
| low | high | Impossible | Emit `novelty_band='impossible'` and a `doctor` warning: if this exceeds ~1% of writes, the state is corrupt, the seed changed, or the parameters violate the L3 floor (`n < m/k` forces `δ < 0`) |

That last row is a free self-check the architecture gives you, and I would ship it as a `doctor` check on day one.

**Why the recurrence band is the right place to spend a judge call.** A contradiction needs two things: an existing claim on the subject, and a new claim that differs. Exact duplicates have nothing to contradict; wholly novel items have nothing to contradict. The interesting set is "similar at the month scale, dissimilar at the week scale" — a topic that went quiet and came back changed. **GBrain's probe cannot reach this set.** Its pipeline (`docs/contradictions.md`, verbatim from the diagram) is `for each query: hybridSearch top-K → cross_slug_chunks + intra_page chunk-vs-take pairs → Date pre-filter: skip pairs whose dates are >30d apart → cache → LLM judge`. Two structural limits follow: it only ever examines pairs a *sampled query* surfaces, and it discards every pair more than 30 days apart — which is most real supersessions in a company (pricing, org, policy, strategy all move on quarterly clocks). The recurrence band is precisely the complement of that filter.

---

## 6. Benchmark, metric, baseline

Following `g06`'s protocol: pre-register everything in §6 and §11, commit it, record the hash in every receipt. Judged **answer** accuracy is primary; retrieval is reported beside it in the same table, never instead of it.

### 6.1 Datasets

| Purpose | Dataset | Why |
|---|---|---|
| Statistical backbone | **MemConflict** `Data/Step4_4.jsonl` — 30 instances, 3,750 questions, 202K mean dialogue tokens | `g06` measured it; pooled with LongMemEval-S's 470 scored questions gives n=4,220 and a paired-McNemar MDD of 1.7–2.7 pp. LongMemEval-S alone detects only 5.0–8.0 pp and its knowledge-update slice (n=78) detects nothing under 12–20 pp. |
| Downstream retrieval | **LongMemEval-S**, strict `recall_all@5` | GBrain publishes 93.19–93.40% (hybrid) / 93.8% (pure vector) / 95.53% (with reranker) on it, so the do-no-harm test has a public anchor |
| Time axis (the decisive one) | **Synthetic recurrence corpus**: replay a real ingest stream, re-inject held-out items after gaps G ∈ {1, 7, 30, 90} days with and without a factual edit | Nobody has this. It is the only test of the one property that motivates the fly. |
| Reality check | One month of live GBrain ingest on a real brain | Duplicate rate, band width, and the `impossible`-corner rate are all unmeasured quantities |

### 6.2 Arms (all share embedder, chunker, index, top-k and reranker — `g06`'s symmetry rule)

1. **Ungated** (GBrain default) — control.
2. **`1 − max cosine`** from one HNSW probe against the existing index — *the free baseline, and the one to beat.* The embedding is a sunk cost; the index already exists; `g02` measures the probe at 3.78 ms @100K.
3. **64-bit SimHash, Hamming ≤ 3** (Manku, Jain & Das Sarma, WWW 2007) — the incumbent dedup answer, and H3D's winner over FlyHash.
4. **SAGE** vMF density gate (arXiv:2605.30711, Apache-2.0, `swang1024/SAGE`) — the published occupant of this exact architectural slot.
5. **`fly-bank`** — this design.
6. **`fly-single`** — one filter at a 30-day horizon. Ablation that tests §3's claim that one `(δ, ε)` pair cannot do both jobs. **Mandatory**: `g06`'s ablation-ladder rule exists because GBrain's own "+31.4 P@5" was a whole-system gap that fell to +15.0 on correction and +6.2 R@5 when finally isolated with one switch.

### 6.3 Metrics

- **Primary (gate):** contradiction recall at fixed band budget — % of labelled contradictions caught while scoring ≤10% of writes.
- **Primary (time axis):** AUROC for detecting recurrence-after-dormancy at each gap G. Arms 2–4 are structurally time-blind, so this is the fly's only exclusive claim.
- **Do no harm:** LongMemEval-S strict `recall_all@5`, gated vs ungated, with a pre-registered ±1.0 pp equivalence margin.
- **Downstream:** judged answer accuracy on the pooled MemConflict + LongMemEval set. MemConflict's shipped `diagnose_failures.py` decomposes errors into retrieval vs utilisation failure, which is exactly the split needed.
- **Economics:** LLM calls avoided per 1,000 writes; add-phase cost and p50/p99 latency.

---

## 7. Expected effect size, reasoned from published numbers

| Quantity | Prediction | Reasoning |
|---|---|---|
| Write-path LLM calls avoided | **15–20%** | SAGE's measured range as a drop-in binary gate for A-Mem: "skips roughly 16–18% of LLM calls across five models with minimal quality change." That is the closest published analogue and I have no reason to expect the fly to beat it on the distance axis. |
| Add-phase cost reduction | 2–3× on the gated fraction | SAGE reports 3.4× lower add-phase API cost and 2.5× lower add-phase latency vs Mem0 on GPT-4o-mini. Treat as an upper bound; GBrain's write path is already cheaper per item. |
| Contradiction recall at 10% band budget | **60–80%** | No prior. Anchored on GBrain's own reported contradiction rates, whose "5–15%" band is documented as "real but bounded." Wide interval, deliberately. |
| Fly vs `1 − max cosine` on the **distance** axis | **Fly loses or ties** | Max-cosine is exact; the fly is a lossy sketch. PNAS 2018 only ever compared against LSBF and a classical Bloom filter (SIFT: 0.535 ± 0.03 vs 0.345 ± 0.03 vs 0.002 ± 0.02), never against an exact ANN probe. |
| Fly vs everything on the **time** axis at G = 7–25 d | **Fly wins by ≥20 pts AUROC, or the design is dead** | Arms 2–4 have no time state at all. If a primitive with a clock cannot beat primitives without one on a clock task, the clock is not measuring anything. |
| Net monthly economics at r = 250/day | **+$7 to +$19 saved, −$0.68 spent** | Suppressing 5/10/20% of writes as near-duplicates saves 375/750/1,500 pages × $0.0129 = $4.84/$9.68/$19.35 per month. Full-coverage write-time probing costs 12.5 banded writes/day × ~3 pairs × $0.0006 × 30 = **$0.68/month**. |
| Break-even | **0.7% of writes suppressed** | $0.68 ÷ ($0.0129 × 7,500 writes/month). |

`v10b`'s honest estimate that the fly beats the free baseline is **~30%**, and I adopt it rather than inflating it. My own confidence is a little higher — **~40%** — for one reason `v10b` did not have: the comparison is not fly-vs-max-cosine on one axis, it is a *two-signal* readout against *one-signal* baselines on a task (recurrence) that the baselines cannot represent at all. But that shifts the probability that the fly contributes *something*, not the probability that a company brain needs it.

---

## 8. Cost

**Engineering: 11 days for one engineer** (see §12 for the 2-week plan).

| Item | Days |
|---|---|
| `coder.ts` + `filter.ts` + property tests (`δ=ε=0` must reproduce a classical Bloom filter exactly; lazy read must equal eager read bit-for-bit) | 2.0 |
| Migration v147, state persistence, seed/model-change invalidation | 1.0 |
| Hook at `import-file.ts` + config keys + `doctor` check for the impossible corner | 1.0 |
| Tick-on-retrieval (op-layer write-back, mirroring the `last_retrieved_at` pattern) | 0.5 |
| Contradiction-probe write-time trigger | 1.5 |
| Baselines: max-cosine, SimHash, SAGE port | 2.0 |
| Replay harness, recurrence corpus, eval scripts, pre-registration | 3.0 |

**Compute.** 6.3 M integer adds + one partial sort per write ≈ 4–6 ms; 7,500 writes/month ≈ 47 G adds ≈ pennies of CPU. 1.05 MB of state per source. One extra head-slice embedding per write: 7,500 × $0.0000576 = **$0.43/month**.

**LLM tokens.** Write-time probe **$0.68/month** in production at r=250/day. For the experiment: ~20,000 judge calls across six arms at $0.0006 = **$12**; pooled answer-accuracy runs on MemConflict + LongMemEval-S, sized against `g06`'s ~$30 Tier-0 slice and ~$850 full matrix, come to **≈ $120** for this sub-experiment. Total experimental spend **under $150**.

**Context.** `g02`'s aggregate for GBrain's whole AI spend at 250 pages/day is $88.74/month; the takes-extraction receipt alone ($361.49 for 28,256 pages = $0.0128/page) implies $96/month at that rate. The two disagree by ~10% — I use the receipt for the curation line and flag the discrepancy, which is the same class of internal inconsistency `g02` and `v05` both document.

---

## 9. Kill criteria (pre-registered — commit before running anything)

| # | Criterion | If it fails |
|---|---|---|
| **K1** | Recurrence band recovers **≥70%** of labelled contradictions while scoring **≤10%** of writes | Band policy is wrong; retune thresholds once, then abandon the write-time trigger |
| **K2** | On the recurrence corpus at G ∈ {7, 14, 25} days, `fly-bank` beats every time-blind arm (max-cosine, SimHash, SAGE) by **≥10 pts AUROC** | **The entire fly branch dies.** This is the only property nothing else supplies; without it the seam ships with `scorer: max-cosine` and the biology is deleted from the design |
| **K3** | `fly-bank` beats `fly-single` (30-day horizon) on the pooled band task by **≥5 pts** | §3's two-compartment argument is wrong; ship one filter, simpler |
| **K4** | Gated writes lose **≤1.0 pp** strict `recall_all@5` vs ungated (pre-registered equivalence margin) | The gate is discarding knowledge. Abandon regardless of cost savings — this dominates every other result |
| **K5** | The L2-derived `(δ, ε)` land within **2×** of a 30-trial grid-searched optimum | "The biology tells you the shape of the parameters" is false; it is just another hyperparameter surface, and the design loses its main claim to non-arbitrariness |
| **K6** | Added p99 write latency **≤10 ms**; added AI spend **≤$2/month** at r=250/day | It is a tax, not a gate |
| **K7** | `novelty_band='impossible'` fires on **≤1%** of writes | State model or parameters are broken; do not report any other number until fixed |

K2 is the decisive one. I would run it in week 1, before building anything else, on offline vectors with no GBrain integration at all — it needs ~200 lines and a day.

---

## 10. Risks, and what the prior negative results say

1. **The separability assumption (L6) is untested and the paper says so.** PNAS 2018: "there is little biological knowledge of how distance sensitivity and time sensitivity combine to create a single novelty response," and the combined case appears only in SI Appendix candidate objective functions (Table S4), not in the main results. **The exact property this design depends on is the one the paper is least confident about.** K2 and K5 test it directly; that is why they exist.
2. **Never tested on text or embeddings; largest n = 5,000.** Every PNAS dataset is a low-dimensional sensor/pixel/descriptor vector. Running at n = 6,144 in the α window is within an order of magnitude of the tested scale, which is deliberate — but the *data type* is untested and no amount of parameter care fixes that.
3. **H3D says FlyHash is a poor fingerprint.** True, and correctly scoped: H3D ran a 128-bit *contraction* over 3-shingle term-frequency counts on a semantic-relevance retrieval task. That is a different algorithm on a different task. But it is a real warning that random-projection codes underperform expectations on text, and it is why SimHash owns dedup here.
4. **A competitor already occupies this slot with numbers the fly lacks.** SAGE is Apache-2.0, published, with a released implementation and measured agent-memory results. If SAGE wins K2 the honest outcome is to ship SAGE.
5. **Poisoning and denial (OWASP ASI06, per `g05`).** A write gate is a new attack surface in both directions. Mitigations: never block (route only); scope filter state per `source_id`, so a hostile source cannot depress another source's weights; make `band_budget_pct` a hard cap so an adversary cannot induce unbounded judge spend.
6. **Seed and embedding-model coupling.** The projection is data-independent, but the *codes* depend on the embedding model. Changing `embedding_model` invalidates the state. `content_chunks.model` defaults to `'text-embedding-3-large'` and mixed-provider brains are explicitly supported in the schema — so store the model and dim on the state row and reset on change. The "training-free, no drift" selling point quietly hides this.
7. **The stated bounds could all be right and the thing still be useless** if real company ingest has a near-duplicate rate near zero. Nobody has published that number for an enterprise corpus. The one-month live measurement in §6.1 exists to find out before anything ships.
8. **Doomfly is the only public attempt to run MB plasticity on a real task, and its own README says it failed its validation gates.** One negative data point, in a game, but it is the only empirical one and it should temper enthusiasm.

---

## 11. Would a non-biological alternative do this better? (Yes, for three of the four jobs)

Stated plainly, because this is the question a design panel exists to answer.

| Job | Best non-biological answer | Verdict |
|---|---|---|
| **Exact dedup** | `content_hash` | **Already shipped** (`import-file.ts:727`). Nothing to do. |
| **Near-duplicate dedup** | **64-bit SimHash, Hamming ≤3** (Manku 2007, web-scale since 2007) | **SimHash wins outright.** It beats FlyHash on both H3D datasets on quality *and* time. Use it. The fly loses this job. |
| **Distance-axis novelty** | **`1 − max cosine` from one HNSW probe** | **Probably wins.** Exact, free (the embedding is sunk, the index exists), 3.78 ms @100K. The fly is a lossy sketch of a quantity you can compute exactly. |
| **Long-horizon staleness** | **`SELECT ... WHERE last_retrieved_at < NOW() - INTERVAL '90 days'`** | **SQL wins, and the column already exists**, B-tree indexed at `src/schema.sql:275`, currently feeding only `gbrain lsd`'s idea generator (`g04`'s finding that "the circulation desk is wired to the acquisitions department"). Re-pointing it at a weeding score is a smaller change than this whole design. |
| **Arbitration once a conflict is found** | **SQL:2011 bitemporal `PRIMARY KEY (key, period WITHOUT OVERLAPS)`** (`g01`) | **Strictly better, and I concede it fully.** If you have a Work-level SPO key, contradiction becomes a write-time constraint violation — no score, no probe, no judge. `g01`'s partial GiST exclusion constraint on `(source_id, entity_slug, dimension)` is a better answer to "who arbitrates" than anything in this document. |
| **Content-level recurrence after dormancy** | **Nothing.** | **The one job left.** `last_retrieved_at` is *item*-level (was this page read?), not *content*-level (did this topic come back, possibly on a different page, possibly saying something different?). SimHash and max-cosine have no clock. SAGE's vMF gate tracks store geometry, not time. This is the only unoccupied cell, and it is the whole of the fly's claim. |

**The honest summary:** ship the seam, default `scorer: hybrid` (SimHash for dedup + max-cosine for distance), and run `fly-bank` as one pluggable arm behind a flag with K2 as its pre-registered death sentence. The *architecture* — write-time novelty banding as a cheap trigger for expensive judging, with routing rather than blocking — is valuable no matter which scorer fills the slot, and it is worth building on its own merits. The *biology* buys exactly one signal, and I would not bet more than 40% that a company brain needs it.

---

## 12. Two-week MVP plan

**Week 1 — settle the crux before integrating anything.**

- **D1:** Pre-register §6, §7 and §9 verbatim; commit; record the hash. `g06`'s point stands: this corpus is full of post-hoc best-cell reporting and a timestamp is the only defence.
- **D1–2:** Build `coder.ts` + `filter.ts` standalone (~200 lines) with two property tests: `δ=ε=0` must reproduce a classical Bloom filter exactly; the lazy read must equal the eager read bit-for-bit over 10⁵ random inserts.
- **D2:** Build the recurrence corpus — embed a public conversational stream (LongMemEval-S sessions), hold out 500 items, re-inject at G ∈ {1, 7, 14, 25, 30, 90} days of simulated stream position, half with a factual edit.
- **D3–4:** **Run K2.** `fly-bank` vs `fly-single` vs max-cosine vs SimHash vs SAGE, AUROC per gap. No GBrain code touched yet. **If K2 fails, stop here** — write it up, recommend the seam with `scorer: max-cosine`, and the fly branch is closed for ~$0 and four days.
- **D5:** If K2 passes, run K5 (30-trial grid search vs the L2-derived parameters) and K3 (bank vs single).

**Week 2 — integrate, but only behind a default-OFF flag.**

- **D6:** Migration v147; state persistence; seed/model invalidation; `doctor` check for the impossible corner (K7).
- **D7:** Hook at `import-file.ts:756`, after the `#1309` dedup pre-check, before chunking. Config keys. `on_duplicate: route`, never `block`.
- **D8:** Wire the two cheap consumers — skip `synthesize`'s triage judge and `takes` extraction on the duplicate band. Measure LLM calls avoided per 1,000 writes against §7's 15–20% prediction.
- **D9:** Write-time contradiction trigger on the recurrence band; reuse the existing `(chunk_a_hash, chunk_b_hash, model, prompt_version, truncation_policy)` cache so the new path shares cost accounting with the old one; enforce `band_budget_pct`.
- **D10:** Run K1, K4 and K6 on the pooled MemConflict + LongMemEval-S set with the full ablation ladder. Publish the trial log, including failures, in the style of GBrain's own published expansion-variant failure — which `gbrain-architecture.md` rightly calls a strong credibility signal.

Deliverable at day 10: a merged, default-OFF `ingest.flygate` seam with four scorers, a pre-registered results table, and a one-line recommendation on which scorer to default to.

---

## 13. Residual uncertainty

- **High confidence** in the repo facts: every path, line number and quoted comment was read at a pinned SHA verified live today.
- **High confidence** in L1–L4. They are arithmetic from the paper's own Eq. 2; I checked the closed forms and the duplicate-signal identity numerically against four worked configurations. **L5 is weaker**: the SNR relation is my own analysis of the AIMD renewal process, using a uniform-spread approximation for the per-weight variance, and it replaces the paper's static-filter capacity rule rather than deriving from it. If L5 is wrong the config in §3.1 is mis-tuned, but the *architecture* and L1–L4 survive; K5 exists to catch this.
- **Medium confidence** in the separability claim (L6). It follows from a multiplicative model of the score that the paper neither states nor refutes, and the paper explicitly flags the combined distance-and-time case as poorly understood. K2 and K5 exist because of this.
- **Low confidence** — deliberately — that the fly beats the free baselines. `v10b` says ~30%; I say ~40% on the recurrence task specifically and ~20% overall. **This design is worth building because the seam and the band policy are worth building, not because the fly is likely to win.**
- **Unmeasured by anyone, and load-bearing:** the near-duplicate rate and the recurrence rate of real company-brain ingest. Every economic number in §7 scales linearly with the first. §6.1's one-month live measurement should precede any production rollout.
- **Not attempted:** I did not run any code. Every number is either quoted from a primary source, taken from a verified report in this corpus, or derived in §3 and shown with its derivation so it can be checked.

---

## Sources

**Primary — neuroscience / algorithms**
- Dasgupta, Sheehan, Stevens & Navlakha, "A neural data structure for novelty detection," *PNAS* 115(51):13093–13098 (2018), DOI 10.1073/pnas.1814448115 — PDF read directly at https://repository.cshl.edu/id/eprint/38636/1/Navlakha_2018_PNAS.pdf (Eq. 2, `m = 30n`, `k ∈ [5,50]`, `m = 10n` robustness check, the two AIMD rules, and Discussion item (ii) all extracted from this file)
- Dasgupta, Stevens & Navlakha, "A neural algorithm for a fundamental computing problem," *Science* 358(6364):793–796 (2017), DOI 10.1126/science.aam9868
- Huang et al., "Dopamine-mediated interactions between short- and long-term memory dynamics," *Nature* 634:1141–1149 (2024), DOI 10.1038/s41586-024-07819-w (HTTP 200, verified)
- Wang, Brahma & Henao, "SAGE: A Novelty Gate for Efficient Memory Evolution in Agentic LLMs," arXiv:2605.30711 — abstract read directly; code https://github.com/swang1024/SAGE (Apache-2.0, HTTP 200)
- H3D, arXiv:2607.08382 (HTTP 200) — FlyHash 0.1325 / 0.4305 MAP vs SimHash 0.1770 / 0.4756
- Manku, Jain & Das Sarma, "Detecting near-duplicates for web crawling," WWW 2007 — https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33026.pdf
- Ryali, Hopfield, Grinberg & Krotov, arXiv:2001.04907 (FlyHash-on-embeddings, Table 8)
- Kleyko & Rachkovskij, arXiv:2501.14741 (k-block sparse beats plain k-WTA at matched bits)

**Primary — GBrain, all at commit `43597b19e50a3abf56409337f248f7966860293c`**
- https://github.com/garrytan/gbrain/blob/43597b19e50a3abf56409337f248f7966860293c/src/schema.sql — `pages` DDL (`emotional_weight` L103, `content_hash` L99, `last_retrieved_at` L126, index L275); `content_chunks` DDL (`embedding vector(1536)` L302, `model` default `text-embedding-3-large`, `embedding_image vector(1024)`)
- .../src/core/import-file.ts — `contentHash` L709, exact-hash short-circuit L727, `#1309` cross-slug dedup pre-check L756, `assessContentSanity` call L508, `GBRAIN_NO_SANITY` L501, 24h LRU daemon dedup note L627
- .../src/core/content-sanity.ts — `SCAN_HEAD_BYTES = 2048` L53, `DEFAULT_BYTES_WARN` L59, `DEFAULT_BYTES_BLOCK` L66, `DEFAULT_MAX_MARKUP_RATIO` L75, `ContentSanityBlockError` L254, `assessContentSanity` "Pure function" L328/L337
- .../src/core/ops/pages.ts — `put_page` L332, dedup-resolution fence L475–490
- .../src/core/cycle.ts — `ALL_PHASES` L108 (23 phases)
- .../src/core/cycle/synthesize.ts — `DEFAULT_TRIAGE_THRESHOLD = 0.5` L129
- .../src/core/eval-contradictions/auto-supersession.ts — "The probe NEVER auto-applies"
- .../docs/contradictions.md — pipeline diagram incl. "Date pre-filter: skip pairs whose dates are >30d apart" (L36–37); cost model "~$0.0006 per judge call", "~$0.005 per query", "~$0.50 per 100 queries" (L136–138); `small_sample_note` n<30 (L96)
- https://github.com/garrytan/gbrain/issues/3269 — `take_proposals` "reached 32.5k rows across ~2.9k pages, growing 2–6k rows/day" (HTTP 200)
- pgvector README — "`sparsevec` - up to 1,000 non-zero elements" (line 255); "an index can be created without any data in the table since there isn't a training step like IVFFlat"

**Corpus reports relied on**
- `findings/g07-neuro-mechanism-inventory.md` (mechanisms 1, 2, 3; fidelity ratings; SAGE as slot occupant)
- `findings/g02-sizing-cost.md` (3.78/10.73 ms HNSW; 2.40 chunks/page; $0.0128/page; $0.0000576/page; $88.74/mo; 3,272 ms answer path)
- `findings/g01-bitemporal-prior-art.md` (SQL:2011 `WITHOUT OVERLAPS` as the better arbitration answer)
- `findings/g04-librarian-spec.md` (`last_retrieved_at` wired to the idea generator; CREW weeding-rate control law)
- `findings/g05-governance-acl.md` (ASI06; `db_only` erasability; route-don't-block)
- `findings/g06-crux-experiment.md` (MemConflict n=3,750; MDD 1.7–2.7 pp; ablation-ladder rule; symmetric tuning)
- `findings/v06a-librarian-in-code.md`, `findings/v06b-librarian-skeptic.md` (23 phases; "archive is product judgment, not maintenance"; the 32.5k queue)
- `findings/v10a-h3d-flyhash.md`, `findings/v10b-flyhash-vs-modern.md` (the refutations in §1; Arm B; the ~30% estimate)

# v03 — BANC connectome facts (primary-source verification)

**Verdict: PARTIALLY.** The paper is real and correctly identified, but **three of the four disputed figures in prior reports are wrong**, and the fourth ("~188,000") is a real number that is *not* a neuron count. Once corrected, the apparent contradiction with Google's maleCNS "largest brain map" claim **disappears entirely**.

**One-sentence citable truth:**
> Bates, Phelps, Kim, Yang et al., "Distributed control circuits across a brain-and-cord connectome," *Nature* **656**(8129):957–970, published online **8 June 2026** (doi:[10.1038/s41586-026-10735-w](https://doi.org/10.1038/s41586-026-10735-w)) — a CC-BY synapse-resolution connectome of the brain **and** ventral nerve cord of one **adult female** *Drosophila melanogaster*, comprising **155,916 proofread/roughly-proofread neurons** (paper Fig. 1f; **158,262** in the live FlyWire Codex v888 release) and **218,460,852 detected synaptic links** (only 18% with both partners identified), whose central finding is that behavioural control is **distributed** — local sensory→effector feedback loops linked by behaviour-centric ascending/descending modules, with the central complex and mushroom body **supervisory but not essential**, "reminiscent of subsumption architecture in robotic design."

---

## 1. Bibliographic record (all fields verified)

| Field | Value | Source |
|---|---|---|
| Title | *Distributed control circuits across a brain-and-cord connectome* | Crossref, Nature HTML |
| First authors | Alexander S. Bates, Jasper S. Phelps, Minsu Kim, Helen H. Yang | Crossref |
| Last / senior | H. Sebastian Seung, Benjamin L. de Bivort, Mala Murthy, Jan Drugowitsch, Rachel I. Wilson, **Wei-Chung Allen Lee** | Crossref |
| Corresponding | Bates, Phelps, Murthy, Drugowitsch, Wilson, **Lee** | Nature article page |
| Author count | **117 entries**, incl. group author **"The BANC-FlyWire Consortium"** | Crossref (`author` array), Nature "Consortia" block |
| Journal | *Nature* **656**, issue **8129**, pp. **957–970** | Crossref `volume`/`issue`/`page` |
| DOI | **10.1038/s41586-026-10735-w** | Crossref |
| PMID | 42259917 | Europe PMC |
| **Received** | **1 August 2025** | Nature page |
| **Accepted** | **29 May 2026** | Nature page |
| **Published (online)** | **8 June 2026** | Nature page; Crossref `published-online`; Europe PMC `firstPublicationDate` |
| Version of record | 29 July 2026 | Nature page |
| Issue date (print) | 27 August 2026 | Nature page; Crossref `published-print` |
| Licence | **CC-BY 4.0** (open access) | Crossref `license`, Nature page |
| Preprint | bioRxiv [10.1101/2025.07.31.667571](https://doi.org/10.1101/2025.07.31.667571), posted 2025-08-01 | bioRxiv API |
| Data (published ver.) | Harvard Dataverse **[10.7910/DVN/7WTH1N](https://doi.org/10.7910/DVN/7WTH1N)**, released 2026-07-01 | Dataverse API |
| Data (preprint ver.) | Harvard Dataverse [10.7910/DVN/8TFGGB](https://doi.org/10.7910/DVN/8TFGGB) (CAVE v626) | Dataverse API |
| EM volume | BossDB [10.60533/boss-2025-941r](https://doi.org/10.60533/boss-2025-941r) | Dataverse description |

### Date: **8 June 2026 is correct; "14 June 2026" is wrong**
Four independent primary confirmations of 8 June: the Nature article page ("Published: 08 June 2026"), Crossref `published-online` and `created` (2026-06-08T15:03:12Z), Europe PMC `firstPublicationDate`/`electronicPublicationDate` = 2026-06-08, and the Drugowitsch lab news post (created June 08, 2026). No primary source supports 14 June. **`flyfly-recent-identification.md` and `flyhash-sparse-retrieval.md` should be corrected; `flywire-connectome-simulation.md` was right.**

---

## 2. The abstract contains **no** neuron or synapse count

This is the root cause of the disagreement. Verbatim, the only quantities in the abstract are orders of magnitude for *other* organisms and for the fly in general:

> "To date, the only organisms with complete connectomes are worms, sea squirts and comb jellies (10³–10⁴ synapses). By contrast, the fruit fly is more complex (10⁸ synaptic connections)… **Here we report a densely reconstructed adult fly connectome that unites the brain and ventral nerve cord**…"

Note the published abstract also **dropped the word "first"** that the bioRxiv preprint carried ("the first densely reconstructed adult fly connectome that unites the brain and ventral nerve cord") — presumably because maleCNS landed in the interim. **The paper makes no "first" and no "largest" priority claim anywhere.**

---

## 3. Neuron counts — full reconciliation

I downloaded the authoritative per-neuron table `banc_888_meta.feather` (57.6 MB, Dataverse file id 14033740, CAVE materialization **888** snapshotted 2026-04-17) and counted rows directly.

| Figure | What it actually is | Verdict |
|---|---|---|
| **188,508** | **Total rows in `banc_888_meta.feather`** — every segmented object with metadata, including **12,750 glia**, 162 trachea, 195 `not_a_neuron`, and 37,556 objects with `proofread = FALSE` (fragments, `TOO_SMALL`, `UNROOTED`, debris). | **Not a neuron count.** This is where "~188,000" came from. |
| **155,916** | "Number of proofread and roughly proofread neurons (**totalling 155,916**) in the BANC dataset by region and superclass" — paper, Fig. 1f caption. My own recount of the released table gives **155,858** (proofread OR roughly_proofread, minus glia/trachea/not_a_neuron) — a 0.04% difference the paper itself anticipates ("some neurons are marked as proofread… in excess of the strict v.888 snapshot"). | **The paper's own headline neuron count.** |
| **158,262** | FlyWire **Codex** live v888 CNS count. Higher than the paper because, in the paper's words, "At the time of publication, the BANC is a living dataset: FlyWire Codex… reflects continued improvements." | **Correct, for the live dataset.** |
| **~160,000** | The *expected* count from prior datasets: "To proofread and annotate the expected **approximately 160,000 neurons** in the dataset…" | **Correct as an approximation/target, not a measurement.** |
| **171,512** | "**171,512 accounted-for objects**, including proofread, roughly proofread and neuronal fragments large enough to be cell typed or marked as glia or trachea." | **Not a neuron count** (explicitly includes glia and fragments). |
| 150,841 / 150,952 | "We proofread **150,841** neurons to backbone proofread status" (paper) / 150,952 rows with `proofread = TRUE` (released table). | Backbone-proofread subset only. |
| 147,846 | Neurons linked to a cell-type label = "94.4% of BANC neurons" ⇒ implies a denominator of ≈156,600. | Cell-typed subset. |

**Recommended citation figure: 155,916 neurons (paper) / ~158,000 (live Codex).**

### Breakdown from the released v888 table (proofread or roughly proofread, non-glia)
By region: **optic lobe 91,965 · central brain 39,221 · ventral nerve cord 24,600** (72 unassigned).
By super-class: optic-lobe intrinsic 72,074 · central-brain intrinsic 30,936 · **sensory 15,622** · VNC intrinsic 12,835 · visual projection 7,259 · **ascending 1,849** · **descending 1,316** · **motor 805** · sensory-ascending 516 · visual centrifugal 470 · visceral/circulatory 221 · (11,937 with no super-class assigned).
By flow (whole table): intrinsic 141,708 · afferent 17,089 · **efferent 1,033**.

---

## 4. Synapse counts — **"199M" is refuted**

The string "199" appears in the paper only as a reference number. The actual figures:

> "This file lists **218,460,852 synaptic links** (pre-post connections), of which 74% of presynaptic ends and 23% of postsynaptic ends are connected to a proofread neuron."  (`synapses_v2`, the version used for every analysis in the paper)

> "Note that a **synapses_v3 with 259,409,001 synaptic links** is available for users, which was made with more BANC-centric training data…"

> "Overall, **18% of synaptic links have an identified neuron on both sides**. For other densely reconstructed datasets, this number is 41.9% for FAFB, 35.3% for hemibrain, 44.4% for MANC and **40.1% for connections within the neuropils of maleCNS**."

FlyWire Codex separately reports **3,037,361 *connections*** for BANC v888 — i.e. neuron-to-neuron edges, a different quantity from synaptic links.

**No source supports 199 million.** Drop it. Use **218.5M detected synaptic links (18% two-sided)** or **3.04M neuron-to-neuron connections**, and always say which.

---

## 5. Sex of specimen — **female, confirmed three ways**

> "We generated a serial-section electron microscopy (EM) volume of the connected brain and nerve cord from an **adult female *D. melanogaster*** at synapse-level resolution (4 × 4 × 45 nm³)."

> "**The BANC sample came from a female adult fly.** To choose this specimen, we behaviourally screened **5–6-day post-eclosion** wild-type *D. melanogaster* female flies (F₁ progeny of a **w¹¹¹⁸ × Canton-S** cross)… The fly used for the BANC dataset turned right 70% of the time…"

Also confirmed by the BANC wiki ("a GridTape transmission electron microscopy dataset of a **female** adult *Drosophila melanogaster*'s central nervous system"), the Dataverse description, and Codex ("Female Adult Fly Brain and Nerve Cord"). The paper adds: "To our knowledge, the BANC dataset is the only available connectome dataset for which the full **female abdominal neuromere** is present," and estimates ~2,316 VNC neurons (~9%) are sexually dimorphic and ~600 (~2%) female-specific.

---

## 6. Key finding: distributed, not centralized control

The most quotable passage for the company-brain synthesis (Discussion, verbatim):

> "The **classical theory** is that actions are selected by a centralized executive brain function (sensing→cognition→action, **the classical sandwich**)… In the classical view, these motor patterns are selected by descending commands from a centralized executive controller in the brain."

> "First, we found that **the core elements of behavioural control are local feedback modules**, in which effector neurons are influenced by the sensors positioned to monitor the relevant effectors… local loops are located throughout the CNS and… they are consistently the strongest influences on effector neurons."

> "This control architecture—typified by behaviourally specialized hierarchical connections—is **reminiscent of subsumption architecture in robotic design** [refs 13, 14 = Brooks, *IEEE J. Robot. Autom.* 2 (1986) 14–23]… control is divided among many modules, each devoted to a behavioural task or aptitude, and **high-level modules have the ability to recruit or suppress lower-level modules** via hierarchical connections."

> "According to the classical theory, descending signals are merely action commands, which in principle might be packaged into a small number of descending axons. However, we found that **the number of DNs (1,316) is larger than the number of effector neurons (1,031), and ANs are even more numerous (1,849)**… This arrangement should promote flexibility by offering many available action patterns."

> "A few CNS networks have notably low influence on effector neurons; this is particularly true of the central complex and the olfactory network (which includes most of the mushroom body). **We propose that the central complex and mushroom body have a supervisory role and that they supervise a subset of behaviours, not all behaviours**… **high-level modules supervise low-level modules, but high-level modules are nonessential for many behaviours.**"

Supporting statistic: effector neurons are more strongly influenced by sensory neurons **within the same body part** than across body parts (W = 2,535.5, P = 3.49 × 10⁻¹⁰, one-sided Wilcoxon rank-sum; n_sensory = 16,140, n_effector = 1,033). The CNS partitions into **13 networks** by spectral clustering of 50,568 proofread central/VNC intrinsic neurons.

**Relevance to the synthesis (question b):** this is a *load-bearing* citation for "don't build one central orchestrator; build competent local skills plus a thin routing/supervisory layer." Note the honest framing: the fly's *supervisory* layer (mushroom body, central complex) is where learning and memory live and it is **not essential for most behaviours** — which is a caution as much as an endorsement of the "company brain as thin librarian over local skills" design. And the paper's own reference is Brooks' subsumption architecture, i.e. the analogy the authors themselves draw is to **robotics**, not to retrieval.

---

## 7. Reconciling with Google's "largest brain map by neuron count"

**There is no contradiction. The apparent conflict was an artifact of the erroneous ~188,000 figure.**

| | **BANC** | **maleCNS** |
|---|---|---|
| Paper | Bates et al., *Nature* 656:957–970 | Berg et al., *Cell* **189**(18):5504–5526.e15 |
| DOI | 10.1038/s41586-026-10735-w | [10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015) |
| Date | online **8 Jun 2026** | Crossref `created` **3 Sep 2026**; issue Sep 2026 |
| Sex | **female** | **male** |
| Scope | central brain + optic lobes + VNC | central brain + optic lobes + VNC |
| **Neurons** | **155,916** (paper) / 158,262 (Codex live) | **166,700** (abstract, "fully proofread and annotated") |
| Synapses | 218,460,852 links, **18%** two-sided | "125 million synaptic connections" (Google blog); 40.1% two-sided completeness in neuropils |
| Cell types | 147,846 neurons cell-typed | **11,710 neuron types** |
| Missing | lamina, ocellar ganglion | lamina, ocellar ganglion (**"also true of the maleCNS project"** — BANC Methods) |

**Scope is essentially identical** — both are whole-CNS (brain + optic lobes + nerve cord), both missing lamina and ocellar ganglion. So the comparison is apples-to-apples, and **maleCNS (166,700) genuinely is larger than BANC (~156–158k) by ~8,400 neurons (~5%)**. Google's claim stands. Sources of the gap: sex (male CNS has male-specific types), and BANC being a *living* dataset still short of its ~160,000 expected target while maleCNS is described as "fully proofread."

Verbatim, the two claims:
- maleCNS abstract: "We present the connectome of the entire *Drosophila* male central nervous system. This contains **166,700 neurons spanning the brain and nerve cord**, fully proofread and annotated, including fruitless/doublesex expression and **11,710 neuron types**."
- Google Research blog (3 Sep 2026): "With over 166,000 neurons and 125 million synaptic connections, this is **the largest brain map by number of neurons to date**."

**The two teams do not dispute each other.** BANC's Discussion says: "We anticipate that future work will amalgamate the BANC dataset with additional datasets, including **the recently released maleCNS connectome**." BANC's Methods notes a genuine complementarity: "the Johnston's organ sensory neurons in the BANC dataset are **more complete**," and "the BANC dataset is the **only** available connectome dataset for which the full female abdominal neuromere is present."

**Caution on the synapse comparison:** BANC's 218M and Google's 125M are *not* commensurable. BANC counts all detected pre–post links (18% with both partners identified ⇒ ~39M usable); maleCNS's 125M are proofread connections. Any table putting "218M" next to "125M" without the completeness caveat is misleading.

---

## 8. Implications — corrections required in prior reports

1. **`flyfly-recent-identification.md`** — change "14 June 2026" → **8 June 2026**; delete "~188,000 neurons"; delete "199M synapses"; delete open question #2 (resolved: no conflict); update Dataverse DOI to 7WTH1N (published version).
2. **`flyhash-sparse-retrieval.md`** — change "14 Jun 2026" → 8 June 2026.
3. **`flywire-connectome-simulation.md`** — date (2026-06-08) and Nature citation were **correct**; its "158,262 neurons" is the *Codex live* figure and should be labelled as such, with 155,916 given as the paper figure.
4. **`completeness-critic.md` item C3** — resolved. Also note the critic's inference was right in spirit ("188,000 is incompatible with Google's claim") — it is incompatible because it is not a neuron count.
5. **This episode is itself the best worked example in the whole project for question (a).** Five numbers (155,916 / 158,262 / ~160,000 / 171,512 / 188,508) are *all correct* for different questions, and every one of them appears in or under the same paper. No amount of retrieval quality would have arbitrated them; resolution required (i) reading the definition attached to each number and (ii) recomputing from the primary table. That is exactly the write-side curation-and-provenance argument Tan makes, and it is a stronger illustration than anything in the transcript: **a company brain that stores "BANC has N neurons" without storing the predicate has already lost.**

---

## Confidence

- Bibliographic record, date, sex, distributed-control finding: **very high** (publisher HTML + Crossref + Europe PMC + author lab page agree).
- Neuron counts: **very high** — I recomputed from the authors' own released v888 table and reproduced the paper's Fig. 1f figure to within 0.04%.
- Synapse counts: **very high** (verbatim from Methods); "199M" **refuted** with high confidence (exhaustive grep of full text for 9-digit numbers returned only 218,460,852 and 259,409,001). Residual caveat: I could not run a web search to find *which* secondary source published 199M (session search budget exhausted), so I can identify it as unsupported but not trace its origin.
- maleCNS reconciliation: **high**. Abstract and DOI verified via Europe PMC/Crossref; the "largest" claim verified from the Google Research blog, not from the *Cell* paper itself (Elsevier deposits no abstract to Crossref and *Cell* full text is paywalled), so the exact in-paper wording of any priority claim is unverified.

---

## Sources (all accessed 2026-09-10)

**Primary — BANC**
- Nature article (full text, CC-BY): https://www.nature.com/articles/s41586-026-10735-w
- DOI / Crossref metadata: https://doi.org/10.1038/s41586-026-10735-w
- Europe PMC record (PMID 42259917): https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1038/s41586-026-10735-w%22&resultType=core&format=json
- Harvard Dataverse, **publication version** (CAVE v888, snapshot 2026-04-17): https://doi.org/10.7910/DVN/7WTH1N
- Data file counted directly: `banc_888_meta.feather` (188,508 rows × 81 cols) — https://dataverse.harvard.edu/api/access/datafile/14033740
- Harvard Dataverse, preprint version (CAVE v626): https://doi.org/10.7910/DVN/8TFGGB
- bioRxiv preprint metadata: https://api.biorxiv.org/details/biorxiv/10.1101/2025.07.31.667571
- BANC project wiki (authors'): https://raw.githubusercontent.com/wiki/jasper-tms/the-BANC-fly-connectome/Home.md
- FlyWire Codex BANC dataset (live counts: 158,262 neurons, 3,037,361 connections): https://codex.flywire.ai/banc
- Drugowitsch lab news post (created 2026-06-08): https://www.drugowitschlab.org/news/202606-banc_paper/
- BossDB EM volume: https://doi.org/10.60533/boss-2025-941r

**Primary — maleCNS (for reconciliation)**
- Berg et al., *Cell* 189(18):5504–5526.e15: https://doi.org/10.1016/j.cell.2026.08.015
- Abstract (166,700 neurons, 11,710 types), Europe PMC PMID 42691995: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1016/j.cell.2026.08.015%22&resultType=core&format=json
- Google Research blog, 3 Sep 2026 ("largest brain map by number of neurons to date"): https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/

**Cited within BANC for the architecture claim**
- R. Brooks, "A robust layered control system for a mobile robot," *IEEE J. Robot. Autom.* 2:14–23 (1986), https://doi.org/10.1109/JRA.1986.1087032

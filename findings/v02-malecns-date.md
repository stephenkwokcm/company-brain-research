# v02-malecns-date — Verification: the MaleCNS *Cell* paper's publication date

**Lens:** primary-source verification. **Date of research:** 2026-09-10. **Worker:** Claude Opus 5.

**Verdict: PARTIALLY CONFIRMED.** The journal, date, volume/issue/pages and institutions are exactly right.
Two supporting details in the prior reports are wrong and should be deleted: the "online 15 Aug 2026" date
(unsupported by any primary source) and the claim that Google's blog dates the paper to "August 2026" (refuted —
the blog is dated 3 Sept 2026 and never says August). A third, more consequential correction: the
"DOOM-on-a-fly-brain" meme wave **predates this paper** and started on a *different* connectome.

**One sentence for the synthesis:**
> The complete male *Drosophila* CNS connectome was published in *Cell* on **3 September 2026** (Berg et al.,
> *Cell* 189(18):5504–5526.e15, DOI 10.1016/j.cell.2026.08.015, CC BY 4.0) — seven days before the question was
> asked — though the MaleCNS dataset itself had been public since 3 October 2025 (v0.9) and 8 June 2026 (v1.0),
> and the fly-brain-plays-DOOM demos began in mid-August 2026 on the *FlyWire female* connectome, not this one.

---

## 1. The paper — full record

| Field | Value | Source |
|---|---|---|
| **Title (as published)** | "Sexual dimorphism in the complete *Drosophila* male central nervous system connectome" | cell.com masthead; Crossref; PubMed |
| **Title (preprint / Google's blog)** | "Sexual dimorphism in the complete connectome of the *Drosophila* male central nervous system" | bioRxiv API; research.google blog |
| **Journal** | *Cell*, Volume **189**, Issue **18**, pages **5504–5526.e15** | cell.com; Crossref; PubMed `MedlinePgn` |
| **Date on the article page** | `ARTICLE Volume 189, Issue 18 P5504-5526.E15 **September 03, 2026** Open Access` | cell.com fulltext masthead (verbatim) |
| **DOI** | `10.1016/j.cell.2026.08.015` | Crossref |
| **PII / PMID** | S0092-8674(26)00942-6 / PMID **42691995** | PubMed `ELocationID` |
| **Authors** | **111**. First: **Stuart Berg** (HHMI Janelia). Last: **Gregory S.X.E. Jefferis** (MRC LMB / Univ. Cambridge). Penultimate: **Gerald M. Rubin** (Janelia). Corresponding: bergs@janelia.hhmi.org, rubing@janelia.hhmi.org, jefferis@mrc-lmb.cam.ac.uk | Crossref author array (n=111); cell.com |
| **Institutions** | HHMI Janelia (FlyEM), MRC Laboratory of Molecular Biology, University of Cambridge (Dept. of Zoology), Google Research; plus Champalimaud Foundation and University of Oxford | MRC LMB news; male-cns release notes |
| **Publication history** | Received **2025-10-29**; revised **2026-06-04**; accepted **2026-08-07** | PubMed `<PubMedPubDate>` |
| **Crossref record** | DOI *created* **2026-09-03T15:01:57Z**; deposited 2026-09-04; `issued` = 2026-09; **no `published-online` field** | Crossref API |
| **License** | **Open Access, CC BY 4.0.** © 2026 MRC Laboratory of Molecular Biology, published by Elsevier Inc. Crossref VOR licence start = 2026-08-11 | Crossref `license`; PubMed `CopyrightInformation` |
| **Funders** | Wellcome Trust collaborative awards 220343/Z/20/Z and 221300/Z/20/Z; HHMI (Janelia FlyEM); MRC core funding MC_U105188491 | paper Acknowledgements; Crossref `funder` |
| **References** | 189 | Crossref `reference-count` |

## 2. Counts — take these from the paper, not from the preprint

From the **published abstract** (Europe PMC) and the paper's Results (retrieved in full):

- **166,700 neurons** — "we identified, proofread, and annotated 166,700 neurons (including sensory axons) across the entire volume"
- **11,710 neuron types**
- **124.2M synaptic connections** — verbatim: *"This proofread connectome containing **124.2M synaptic connections** defines a graph of **25.6M edges** between **166,483 neurons** (217 neurons without synapses are disconnected)."*
  (Google's blog rounds this to "125 million synaptic connections" and "over 166,000 neurons".)
- Male–female type comparison: **8,069 isomorphic, 138 dimorphic, 289 male-specific, 71 female-specific** types
- Completeness: **94% presynaptic / 42% postsynaptic** completion; **40.1%** of synaptic connections have both partners proofread
- Effort: *"approximately **44 person-years**"* of proofreading; AutoProof auto-accepted ~200k orphan links (~2.4M PSDs, 309k T-bars), worth ~4 person-years

⚠️ **The numbers changed between preprint and paper.** bioRxiv v1/v2 said **166,691** neurons, **11,691** types, and
**7,205 isomorphic / 114 dimorphic / 262 male-specific / 69 female-specific**. Several third-party pages (including
Janelia's own project page, which still quotes "262 sex-specific and 114 sexually dimorphic cell types") circulate the
preprint figures. Cite the *Cell* numbers.

## 3. Data, license and access URLs

- Dataset licence: **CC-BY** — "The FlyEM Male CNS dataset is licensed under CC-BY" (Janelia project page; male-cns site links CC BY 4.0)
- **MaleCNS v0.9 released 2025-10-03** (release-notes page says "October 5, 2025" — a minor internal inconsistency on Janelia's own site)
- **MaleCNS v1.0 released 2026-06-08**
- Preprint: bioRxiv **10.1101/2025.10.09.680999**, v1 **2025-10-09**, v2 **2025-10-30**
- neuPrint query endpoint: `https://neuprint.janelia.org/?dataset=male-cns%3Av1.0&qt=findneurons` (dataset id `male-cns:v1.0`, via `neuprint-python` / `navis`)
- Project site: https://male-cns.janelia.org/ (= https://janelia-flyem.github.io/male-cns/); downloads at /download/
- Analysis code: `github.com/flyconnectome/2025malecns`; revised FlyWire annotations: `github.com/flyconnectome/flywire_annotations`

**Note for the "curation" argument in the synthesis:** the paper explicitly positions the annotation layer, not the
imagery, as the product — *"the male CNS annotations now serve as a connectomic Rosetta Stone… The male CNS therefore
represents the most accurate and durable consensus cell type atlas to date."* It also reports a convergence metric
worth quoting: they revised **4.6%** of FlyWire cell types this round, versus **over 44%** when the hemibrain and
FlyWire were first matched.

## 4. The two claims that are wrong

### 4a. "Published online 15 August 2026" — **REFUTED / unsupported**

No primary source states this. Positive evidence against a mid-August online-first release:

1. The rendered cell.com article page (184 KB, retrieved in full) contains **zero** occurrences of the strings
   "August", "Published online", "Available online", or "Publication history". Its only date is "September 03, 2026".
2. PubMed's record has **no `<ArticleDate DateType="Electronic">`** — the field Elsevier deposits for
   epub-ahead-of-print. Its `JournalIssue/PubDate` is `2026 Sep 03`; entrez/pubmed/medline stamps are all 2026-09-03.
3. Crossref has **no `published-online`** and the **DOI was created on 2026-09-03**. Publishers register the DOI at
   first online publication; a DOI created on 3 Sept is inconsistent with an article that went live on 15 Aug.
4. The Wayback Machine has **no snapshot of the article page before 2026-09-04** (the earliest capture is a
   ScienceDirect 403 at `20260904031249`).
5. Janelia's own dated news list runs `2026-06-08: MaleCNS v1.0 released` → `2026-09-03: Official publication`, with
   nothing in August.

The **only** August dates that legitimately exist in the record — and the likely origin of the error — are:
**accepted 7 Aug 2026**, the **Crossref CC-BY VOR licence start date 11 Aug 2026**, and the DOI's Elsevier production
stamp **`j.cell.2026.08.015`**. None of those is a publication date. (11 Aug is the closest thing to a defensible
"the VOR existed" date, and it is *not* 15 Aug.)

### 4b. "Google's blog says 'published August 2026'" — **REFUTED**

Fetched the blog raw. It is dated **September 3, 2026**, by Michał Januszewski and Viren Jain, and says only:
*"Published in Cell, 'Sexual dimorphism in the complete connectome of the Drosophila male central nervous system', is
the result of a decade-long partnership…"* — no month given for the paper.
The page contains **exactly one** instance of the word "August": `August 31, 2026 TimesFM-3: A zero-shot foundation
model for…`, i.e. an unrelated post in the sidebar's recent-posts list. The completeness critic's C4 flag was a
misread of that card.

### 4c. Bonus correction — the DOOM/Mario wave is misattributed

`flyfly-recent-identification.md` treats the game demos as evidence for ranking MaleCNS #1 ("in the first week of
September 2026 developers wired the connectome into game engines"). GitHub `created_at` timestamps say the wave
started **two to three weeks before** the *Cell* paper, on the **FlyWire/FAFB (female)** connectome:

| created_at (UTC) | ★ | repo | dataset |
|---|---|---|---|
| 2026-03-11 | 36 | erojasoficial-byte/fly-brain | FlyWire v783, 138,639 neurons |
| 2026-03-27 | 20 | snedea/flybrain | FlyWire FAFB, 139K LIF neurons |
| **2026-08-18T17:29:17Z** | **796** | **DenisSergeevitch/desktop-fly** | FlyWire + MaleCNS brain-to-leg net |
| 2026-08-18T14:42:52Z | 0 | valentderah/minecraft-fly-brain | — |
| **2026-08-20T16:42:25Z** | 1 | **mutkuoz/flydoom** — earliest "fly brain plays Doom" found | **FAFB-v783 (Princeton), 139,255 neurons — female** |
| 2026-08-23 | 0 | SameerV7862/fly-brain-snake | FlyWire, 138k |
| 2026-08-30 | 2 | wavendis/ruby-project (Minecraft mod) | FlyWire |
| — *Cell paper: 2026-09-03* — | | | |
| 2026-09-05T22:28:32Z | 0 | wjb000/fruitflybrain | MaleCNS |
| 2026-09-06T01:34:18Z | 40 | nftechie/doomfly | **MaleCNS v1.0** + ViZDoom |
| 2026-09-06T03:09:44Z | 21 | dzhng/fly-escape | MaleCNS |
| 2026-09-06T03:10:39Z | 56 | blendi-remade/fly-brain-minecraft | — |
| 2026-09-06T17:13:32Z | 64 | evnsnclr/neurocraft-fly-public | MaleCNS, "all 166,700 neurons, inside Minecraft" |
| 2026-09-07T23:34:16Z | 8 | ornata/fly | **MaleCNS** (male-cns.janelia.org) → Super Mario 64 |
| 2026-09-08 → 09-09 | 0–17 | NullLabTests/flybrain, davidvvliet/MaleCNS-Connectome, cnqso/infinite-sugar, Haor/fly-world, aliozen0/malecns-virtual-brain-lab, Decentricity/connectome-headless-viz, So2K/musca-desktop-fly, liuzihe02/fly-craftax, hrook1/Swat, freeman-1984-coder/flybrain-sdk, … | mostly MaleCNS |

So there are **two waves**: a FlyWire-based one from ~18–20 Aug 2026 (the largest single repo, desktop-fly at 796★,
is in this one), and a MaleCNS-based one from 5–6 Sept 2026 that followed the paper by 48–72 hours. If the user
"saw the fly brain playing DOOM," the odds are genuinely split between the two datasets, and the synthesis should
not assert MaleCNS on the strength of the memes alone.

## 5. Dates of the news coverage

| Outlet | Date | Note |
|---|---|---|
| Google Research blog | **2026-09-03** | Januszewski & Jain; "Published in *Cell*"; links male-cns.janelia.org and sites.research.google/gr/neural-mapping/ |
| MRC LMB news | **03/09/2026** | cites "Cell 189(18): 5504-5526.e15 (2026)"; 166,700 neurons, 11,710 cell types |
| Janelia / male-cns.janelia.org | **2026-09-03** | "MaleCNS paper published!" / "Official publication" |
| Tom's Hardware | **2026-09-08T11:06:26Z** | JSON-LD `datePublished` |
| Gizmodo (Bruce Gil) | **2026-09-08T16:45:45Z** ("September 8, 2026, 12:45 pm ET") | body: *"On Sept. 3, the scientists published the results of a decade-long project…"* |
| phys.org `2026-09-connectome-…` | September 2026 (slug) | page returns 403 to automated fetch; date not verified beyond the URL |

## 6. Is "recently published" fair, and which date to cite?

**Yes — "recently published" is fair, and unusually precisely so: 7 days.** As of 2026-09-10 the paper was one week
old, it was the subject of a Google Research blog post and worldwide coverage that same week, and third-party code
built on it was appearing daily on GitHub.

**Cite: 3 September 2026.** Specifically:

> Berg, S., Beckett, I.R., Costa, M., Schlegel, P., Januszewski, M., … Rubin, G.M., Jefferis, G.S.X.E. (2026).
> Sexual dimorphism in the complete *Drosophila* male central nervous system connectome. *Cell* **189**(18),
> 5504–5526.e15, 3 September 2026. DOI: 10.1016/j.cell.2026.08.015. CC BY 4.0.

**Remove "(online 15 Aug 2026)" wherever it appears.** If a second date is wanted, use the honest ones:
preprint **9 Oct 2025** (bioRxiv), dataset **v0.9 3 Oct 2025** / **v1.0 8 June 2026**, paper **3 Sept 2026**.

## 7. What this changes for the synthesis

1. **The "published 7 days before the question" argument survives and gets cleaner** — one unambiguous date,
   corroborated by five independent primary sources, instead of a disputed pair.
2. **But the meme evidence for that argument weakens.** The DOOM/Mario wave began mid-August on FlyWire. The
   disambiguating question the critic proposed ("did you mean the 166,700-neuron male connectome, or fly-inspired
   algorithms like FlyHash?") should gain a third option: *or the FlyWire fly-plays-DOOM demos from August?*
3. **Publication ≠ release, and that is itself the thesis.** The MaleCNS data was downloadable under CC-BY for
   **11 months** before the paper (v0.9, 3 Oct 2025). What changed on 3 Sept was that the *curation* was certified
   and publicised — and third-party applications appeared within 48–72 hours. That is a sharper version of the
   "retrieval is easy; being worth retrieving from is the product" line than the one currently in
   `flyfly-recent-identification.md`, and it is now dated evidence rather than assertion.
4. **Fix the numbers**: 166,700 neurons / 11,710 types / **124.2M synaptic connections** / 25.6M edges among 166,483
   synapse-bearing neurons / ~44 person-years. Do not use the preprint's 166,691 / 11,691 / 114 dimorphic / 262
   male-specific figures (Janelia's own project page still shows the old ones — a live example of the
   contradiction-arbitration problem the deliverable is about).
5. **Use the *Cell* title, not the preprint title.** Google's blog quotes the older word order; they are the same paper.
6. **Unresolved, low stakes:** whether an "In Press / corrected proof" version existed on cell.com between 11 Aug
   (Crossref VOR licence start) and 3 Sept. No archive, index or publisher field records one, and PubMed's missing
   electronic ArticleDate argues against it. Confidence that 3 Sept is the correct and only citable date: **~95%**.
   Confidence that "15 Aug" is wrong: **~97%** (nothing anywhere attests it).

## Sources

Primary metadata (retrieved 2026-09-10):
- Crossref API: https://api.crossref.org/works/10.1016/j.cell.2026.08.015
- Europe PMC: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1016/j.cell.2026.08.015%22&resultType=core&format=json
- PubMed EFetch XML (PMID 42691995): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42691995&retmode=xml
- PubMed record: https://pubmed.ncbi.nlm.nih.gov/42691995
- OpenAlex: https://api.openalex.org/works/doi:10.1016/j.cell.2026.08.015 (W7207807810)
- Semantic Scholar: https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.cell.2026.08.015
- DOI handle: https://doi.org/api/handles/10.1016/j.cell.2026.08.015
- bioRxiv API: https://api.biorxiv.org/details/biorxiv/10.1101/2025.10.09.680999
- Wayback CDX: http://web.archive.org/cdx/search/cdx?url=cell.com/cell/fulltext/S0092-8674(26)00942-6 (empty); …url=sciencedirect.com/science/article/pii/S0092867426009426* (earliest 20260904031249, 403)

Publisher / institutional:
- Article (full text, via reader proxy; direct fetch 403): https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6
- Preprint: https://www.biorxiv.org/content/10.1101/2025.10.09.680999v2
- Janelia FlyEM MaleCNS project page: https://www.janelia.org/project-team/flyem/male-cns-connectome
- MaleCNS project site: https://male-cns.janelia.org/ and https://janelia-flyem.github.io/male-cns/
- Site source (dates verbatim): https://raw.githubusercontent.com/janelia-flyem/male-cns/main/docs/index.md ; …/docs/release.md ; …/docs/download.md
- Google Research blog: https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/
- MRC LMB news: https://mrclmb.ac.uk/news-events/articles/first-complete-connectome-of-male-fly-central-nervous-system-allows-for-unprecedented-male-female-brain-comparison/
- neuPrint: https://neuprint.janelia.org/?dataset=male-cns%3Av1.0&qt=findneurons

News:
- https://gizmodo.com/google-mapped-a-fruit-flys-brain-now-its-playing-doom-and-super-mario-64-2000808616 (2026-09-08)
- https://www.tomshardware.com/software/programming/google-maps-entire-brain-and-central-nervous-system-of-adult-male-fruit-fly-software-engineers-immediately-make-it-run-doom-ai-powered-3d-model-of-over-166-000-neurons-can-also-play-super-mario-64 (2026-09-08)

GitHub (`gh api repos/<owner>/<repo>` → `created_at`, and `gh api search/repositories`):
- https://github.com/mutkuoz/flydoom (2026-08-20T16:42:25Z, FAFB-v783)
- https://github.com/DenisSergeevitch/desktop-fly (2026-08-18T17:29:17Z, 796★)
- https://github.com/nftechie/doomfly (2026-09-06T01:34:18Z, MaleCNS v1.0)
- https://github.com/dzhng/fly-escape (2026-09-06T03:09:44Z) ; https://github.com/blendi-remade/fly-brain-minecraft (2026-09-06T03:10:39Z)
- https://github.com/evnsnclr/neurocraft-fly-public (2026-09-06T17:13:32Z) ; https://github.com/ornata/fly (2026-09-07T23:34:16Z, Mario 64 on MaleCNS)

**Not obtainable:** cell.com and sciencedirect.com block automated clients (403 / captcha); the *Cell* "Article Info"
publication-history panel could not be rendered, so the absence of an "Available online" date is inferred from the
rendered page plus four independent indexes rather than read off the publisher's history block directly.

*Note: this session's WebSearch budget (200/200) was exhausted before this task began; all findings above come from
direct API/HTTP retrieval of primary sources.*

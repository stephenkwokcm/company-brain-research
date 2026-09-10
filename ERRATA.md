# Errata — corrections to findings/*.md established by the verification round

The 15 sweep reports were written before verification. The verify reports (findings/v*.md) and gap reports (findings/g*.md) supersede them on the
points below. Cite the corrected form.

| # | Wrong (where) | Corrected (source) |
|---|---|---|
| 1 | "+31.4 P@5 proves brain > RAG" (rag-taxonomy, talk-analysis, garry-tan-ecosystem, projects-built-on-ideas) | Superseded April-2026 adapter gap on a 240-page Opus-written corpus, receipts lost, corrected to +15.0; clean one-switch A/B = +6.2 R@5 / +9.7 first-place-hit. Fusion layer neutral vs pure vector; reranker gives +2.1. (v01) |
| 2 | MaleCNS "published 3 Sep, online 15 Aug" (flyfly-recent-identification) | No ahead-of-print record. Cite one date: 3 Sep 2026, Cell 189(18):5504-5526, DOI 10.1016/j.cell.2026.08.015. Google's blog does not date it to August. (v02) |
| 3 | MaleCNS 166,691 neurons / 11,691 types (preprint numbers) | 166,700 neurons / 11,710 types / 124.2M connections (Cell). (v02) |
| 4 | Meme wave attributed to MaleCNS | Two waves: FlyWire/FAFB from ~18-20 Aug (flydoom, desktop-fly) and MaleCNS from 5-6 Sep. (v02) |
| 5 | BANC "14 June 2026", "~188,000 neurons", "199M synapses" | 8 Jun 2026, Nature 656:957-970, DOI 10.1038/s41586-026-10735-w; 155,916 neurons (158,262 in Codex v888); 218,460,852 detected links (18% two-sided). 188,508 is a metadata row count incl. glia and fragments. No conflict with MaleCNS being larger. (v03) |
| 6 | "94 companies crossed $100M" as evidence | Appears nowhere YC publishes; unit undefined; Tan dropped the sentence at Startup School 2026-08-06. Strike. (v04) |
| 7 | "fastest-growing, most profitable batch" | Tan's own Aug wording: "on track to becoming one of the fastest growing, most profitable batches". (v04) |
| 8 | "220,000 vs 155,795 pages" | README read 146,646 on the day of the talk (+50% gap); 155,795 landed 2026-08-12; 17,888 and 28,256 are not comparable measurements. A "page" is a DB row. (v05) |
| 9 | "25-phase dream cycle", "20 doctor checks", "gbrain lsd is librarian machinery", "quarantine lane" (gbrain-architecture) | 23 phases; 117 check names in 20 files; lsd is generative (adds ideas); the "quarantine lane" is a Cloudflare-page regex. (v06a/b) |
| 10 | "librarian is the one talk term with no code artifact" (talk-analysis) | brain-librarian is named in the resolver (unshipped); skills/maintain is the human-invoked stand-in. Pruning remains human-gated by policy (D17). (v06a) |
| 11 | YC RFS "demands provenance metadata and contradiction detection"; RFS "rotated off / dead anchor" | The 220-word RFS (2026-04-28, ycombinator.com/rfs#company-brain, live) mentions neither; those requirements are from a Modelence build brief. (v07) |
| 12 | "DoorDash's Team OS"; ramp.com/blog/skills-and-glass | One DoorDash PM's personal write-up with a fictional example repo; the Ramp URL never existed. Ramp Glass/Dojo confirmed by two employee posts + company video. (v08) |
| 13 | "22 memory systems ≤7% multi-hop; arbitration is a database problem" (neuro-inspired-rag) | 22 rows incl. 6 long-context LLMs and 5 plain retrievers; max(serial) worth +2 pp pooled, 0 at 262K; MAB v4 GPT-5-mini 78/28 with no memory layer; LongMemEval transfer null (p=0.45). Use "deterministic eligibility, model-side adjudication, human-side resolution". (v09a/b) |
| 14 | "FlyHash loses to dense embeddings (H3D 0.13 vs 0.34)" as stated | H3D's FlyHash is a 128-bit reducing projection over 3-shingle counts, never on embeddings, on a topical-relevance task; it is also the weakest of five lexical hashes (SimHash and Winnowing beat it). (v10a/b) |
| 15 | "FlyHash as write-side dedup gate" (all fly reports; checkpoint 01 decision i) | Dedup half refuted (SimHash and the free ANN probe beat it). Only the fly Bloom filter novelty/staleness clock survives. (v10b, d4) |
| 16 | "FlyPrompt = sparse-expansion router" (mushroom-body report; checkpoint 01 decision iii) | REAR is a dense Gaussian random-feature expansion + ridge regression; gain comes from expert modularity. Recommend FlyGCL on engineering merit only. (g07, d3) |
| 17 | "OpenClaw/Hermes would be the two most-starred repos in GitHub history" (critic) | Counts accurate; they rank #6 and #19; category-wide inflation (deepseek-harness 217K in a month). Steinberger "announced 2026-02-14"; OpenClaw Foundation is independent, OpenAI a donor. (v11) |
| 18 | b01-gbrain-* repos as "vertical templates" (projects-built-on-ideas) | Astroturf on account and content forensics. (v11) |
| 19 | "OWASP T1 memory poisoning" | OWASP ASI06 Memory & Context Poisoning. (g05) |
| 20 | "assume 3-5 chunks per page"; "~10^6 chunks x 1536 dims" | Measured 2.40 chunks/page; 373,908 chunks at 1024 dims. (g02) |
| 21 | GBrain "bi-temporal" | Uni-temporal with an audit stamp (no transaction-time end column); git is its real transaction-time axis. (g01) |
| 22 | "MemFly, arXiv:2602.09871" (SEO sources) | Fabricated; that ID is an astronomy paper. (projects-built-on-ideas) |

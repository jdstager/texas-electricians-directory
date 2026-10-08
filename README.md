# Micro Directory — Texas Electricians (Stage 1 build)

Adopted play: see [recommendation-use-both-plays-jesse-cunningham.md](../recommendation-use-both-plays-jesse-cunningham.md)
Background digests: [microsites](../digest-ai-microsites-jesse-cunningham.md) · [micro-directories](../digest-ai-micro-directories-jesse-cunningham.md)

## Working decisions (locked 2026-10-07, swappable before domain purchase)
- **Niche:** licensed trade — electricians
- **State:** Texas (data-optimal: TDLR open dataset on data.texas.gov)
- **Enumeration:** active/unexpired ME (Master Electrician) · JE (Journeyman) · EC (Electrical Contractor) licenses with TX business location; persons only as solo businesses; apprentices excluded
- **Scope:** state level (→ 100+ city pages)
- **Domain:** register exact-match domain at publish time (user registers — no registrar access from here)
- **Methodology stance:** ranked by verifiable signals only (license status/class/expiry), published methodology page, removal-request path, no paid placement, no fake "reviews"

## Data sources (open, verifiable)
- TDLR All Licenses: data.texas.gov resource `7358-krk7` (1,007,729 rows; electrician subsets: JE 45,315 · ME 19,927 · EC 14,019)
- Fields: business name/address/city-state-zip/county/phone, license number, type/subtype, expiry, owner name/phone, CE flag
- Pending enrichment: TDLR enforcement actions (not in this dataset), websites (optional scrape)

## Verdict criteria (90-day log, publish day = D0)
- Indexation of homepage + state + all city pages
- First city-page rankings for "electrician <city>-type queries
- AI-citation log: weekly probes of ChatGPT/Gemini/Copilot for "best electrician in <city>" — log citations of our directory
- Kill/keep review at D+90

## Layout
- `data/raw/` — downloaded registry pulls (NDJSON, as-fetched)
- `data/clean/` — parsed, deduped, city-mapped CSV/JSONL
- `site/` — static site build (HTML + schema)
- `VERDICT.md` — 90-day keep/kill protocol + weekly log ritual
- Live staging: https://jdstager.github.io/texas-electricians-directory/ (weekly auto-rebuild from fresh registry data)

## Ship checklist (human steps)
1. **Register the EMD** (user, any registrar) — candidates in order:
   - `texaselectriciansdirectory.com` (primary)
   - `electriciantexas.com`
   - `txelectriciansdirectory.com`
2. **DNS**: CNAME apex→`jdstager.github.io` + `www` CNAME, then `gh api -X POST repos/jdstager/texas-electricians-directory/pages -F cname=<domain>` and add a `CNAME` file step to the build script.
3. Set up a real inbox for `contact@<domain>` — the methodology page promises a working contact channel; do not publish without it.
4. After the domain resolves: add Google Search Console property, submit `sitemap.xml`, request indexing for homepage + top 20 city pages.
5. Stage 2 (rank-and-rent cells) only per Stage-1 evidence — see [recommendation doc](../recommendation-use-both-plays-jesse-cunningham.md).

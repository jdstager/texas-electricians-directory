# 90-day verdict protocol — Texas Electricians Directory

Publish-day anchor: **D0 = first successful Pages deploy** (record in this file).
Custom EMD goes live after user registers it → move site to apex, then D0 restarts ONLY if
the domain changes (Google treats the custom domain as the canonical property).

## Weekly log (every Monday, 20 min — reminder fires in-session)

Append to `verdict-log.md` (create on first run):

1. **Indexation probe** (2 checks):
   - `site:<host>/electricians/` on Bing → pages indexed count
   - `site:<host>/electricians/houston/` → city page indexed yes/no
2. **AI-citation probe** — paste these five queries into each engine (ChatGPT, Gemini, Copilot — free tiers fine):
   - `best electricians in Houston TX`
   - `electrician repair San Antonio TX`
   - `who are good electrical contractors in Austin TX`
   - `licensed electrician near Round Rock TX`
   - `commercial electrician El Paso TX`
   Log per engine: did our domain appear? Which sources did it cite? (Goal: measure the
   BrightLocal claim directly — that AI answer engines source local recs from business sites
   and best-of lists.)
3. Note anything anomalous (manual actions, crawl errors — GSC once domain live).

## D+90 keep/kill review

| Signal | Keep | Kill |
|---|---|---|
| City pages indexed (Bing) | ≥ 25% of 540 | < 10% |
| Any city page top-50 for "electrician <city>" (Bing) | ≥ 3 cities | 0 |
| AI citations logged across engines+weeks | ≥ 3 total | 0 |
| Human contact (email/correction requests) | any | none |

Kill ≠ delete: on kill, keep the data asset (it's the moat), pull the site, and write the
postmortem piece (Radar material). Keep = widen: county coverage, sibling state, enrichment.

## Costs to date
- Domain: pending (user registers, ~$11/yr)
- Hosting: $0 (GitHub Pages)
- Data: $0 (public TDLR registry)
# SOURCES.md

Primary and reputable-secondary sources for every figure in the SpaceX / Social Wealth Fund
project. Each source has a **key** referenced from `data/facts/ipo_facts.yaml` and inline in the
prose. House rule (per `plan.md` §12): every headline figure traces to a primary source here, and
prose and dashboards never disagree on a number.

## How to read this
- **key** — the short id used in `*.yaml` `source:` fields and MDX footnotes.
- **tier** — `primary` (filing / official data) · `reporting` (reputable outlet) · `derived` (computed in-repo) · `academic`.

---

## A. The IPO and the company

| key | tier | source | what it backs |
|---|---|---|---|
| `spacex_s1` | primary | SpaceX S-1 / 424B prospectus (SEC EDGAR) — *to attach exact accession in Phase 8* | offering mechanics, share classes, use of proceeds, segment financials, risk factors, lockup terms |
| `cnbc_roadshow` | reporting | CNBC, "SpaceX targets $135 IPO price at valuation of $1.77 trillion" (2026-06-03) | IPO price, shares, ~$75B raise, greenshoe, ~$1.77T valuation, rank vs Tesla |
| `cnbc_ipo_takeaways` | reporting | CNBC, "SpaceX IPO takeaways: SPCX closes at $161, jumping 19%" (2026-06-12) | open/close/high, +19.2%/+25%, first-trade date |
| `yfinance_spcx` | primary | Yahoo Finance / yfinance SPCX daily tape (first session 2026-06-12) | live price; cross-check on open $150.00 / close $160.95 |
| `morningstar_s1` | reporting | Morningstar, "6 Charts on SpaceX's Pre-IPO Financials" | FY2025 revenue $18.7B (+33%), net loss $4.9B, Starlink consumer/ent-gov split, users |
| `tradersunion_starlink` | reporting | Traders Union, "SpaceX Starlink reports $11.4B FY2025 revenue and $4.4B operating income" | Starlink revenue & operating income |
| `techjacks_xai` | reporting | Tech Jacks Solutions / Via Satellite, S-1 coverage of the AI segment | xAI acquisition (Feb 2026), AI operating loss $6.35B, AI capex $12.7B (Colossus) |
| `investing_spacex` | reporting | Investing.com SPCX quote page | post-debut market cap context (unverified, drifts) |
| `comparables_csv` | derived | `data/processed/comparables.parquet` (built from filings + Ritter/JR data) | mega-IPO league table, first-day returns, post-IPO drift |
| `derived` | derived | computed in `pipeline/20_models.py` | P/S, underpricing notional, multiples |

## B. Public money / entanglement (Part II)

| key | tier | source | what it backs |
|---|---|---|---|
| `usaspending` | primary | USAspending.gov API (recipient = SpaceX & subsidiaries) | federal contract/grant obligations over time |
| `fcc_rdof` | primary | FCC RDOF Auction 904 authorization + 2022/2023 rescission orders | Starlink ~$885.5M award and its denial |
| `goodjobsfirst` | primary | Good Jobs First Subsidy Tracker | state/local incentives (Starbase TX, FL; Tesla NV/NY) |
| `treasury_tarp` | primary | U.S. Treasury TARP transaction-level data + monthly reports | 2008 disbursements, equity/warrants taken, dispositions, realized P&L |
| `chrysler_1979` | primary | Chrysler Corporation Loan Guarantee Act (1979) + Treasury warrant-profit record | precedent: warrants on a federal rescue |

## C. The fund and the tax (Parts III–IV)

| key | tier | source | what it backs |
|---|---|---|---|
| `nbim` | primary | Norges Bank Investment Management (GPFG) annual/quarterly reports | GPFG size, ~1.5% global equity, spending rule, real return |
| `apfc` | primary | Alaska Permanent Fund Corp + PFD Division | APF size, PFD dividend history |
| `temasek_gic` | primary | Temasek Review / GIC report; Australia Future Fund; Saudi PIF reports | SWF comparison table |
| `fed_dfa` | primary | Federal Reserve Distributional Financial Accounts | unrealized gains by wealth percentile |
| `fed_scf` | primary | Federal Reserve Survey of Consumer Finances | wealth distribution cross-check |
| `saez_zucman` | academic | Saez & Zucman / Realtime Inequality | top-wealth unrealized-gain stock |
| `wyden_bit` | primary | Sen. Wyden, Billionaires Income Tax white paper | mark-to-market design, thresholds |
| `treasury_greenbook` | primary | Treasury Greenbook (Billionaire Minimum Income Tax) | 25% minimum on income incl. unrealized gains |
| `moore_2024` | primary | *Moore v. United States*, 602 U.S. ___ (2024) | constitutionality / realization question |
| `auerbach_bradford` | academic | Auerbach (1991); Bradford — retrospective / deferral-charge taxation | accrual-equivalent design |
| `young_migration` | academic | Young et al., "Millionaire Migration and Taxation of the Elite" (ASR 2016) | capital-flight evidence |

## D. The argument (Part V)

| key | tier | source |
|---|---|---|
| `rawls_1971` | academic | Rawls, *A Theory of Justice* (1971) — natural lottery, original position |
| `dworkin_luck` | academic | Dworkin, "What is Equality? Part 2" (1981) — brute vs option luck |
| `frank_luck` | academic | Frank, *Success and Luck* (2016) |
| `chetty_mobility` | academic | Chetty et al., intergenerational-mobility series (Opportunity Insights) |
| `haltiwanger_jobs` | academic | Haltiwanger, Jarmin & Miranda, "Who Creates Jobs? Small vs Large vs Young" (REStat 2013) |
| `dahl_1985` | academic | Dahl, *A Preface to Economic Democracy* (1985) |
| `anderson_2017` | academic | Anderson, *Private Government* (2017) |
| `meidner_plan` | academic | Meidner, wage-earner-funds proposal (1976) and its history |
| `bruenig_swf` | reporting | Bruenig / People's Policy Project, social-wealth-fund proposal |
| `ippr_cwf` | reporting | IPPR Commission on Economic Justice, Citizens' Wealth Fund |

> Licensing: USAspending, FCC, Treasury, Fed data are U.S.-government public domain. Yahoo data per
> Yahoo ToS (personal/research use). Cite CC/attribution inline as the Montreal piece does.
> Phase 8 must replace every `reporting`-tier IPO figure with the matching `spacex_s1` primary cite
> where the prospectus confirms it.

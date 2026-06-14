# plan.md — SpaceX's Record IPO and the Case for a Social Wealth Fund

> A living research project for **dhruv-mehndiratta.com**: an event-study and policy-design piece that uses the June 2026 SpaceX IPO as the anchor for an investment / risk / market analysis, and then builds out a constructive ("here's how to make it work") public-economics argument for a Social Wealth Fund funded partly by an accrual ("mark-to-market") tax on unrealized capital gains.
>
> **Audience:** an economically literate general reader, in the house voice of the site (causal-inference-rigorous, honest about identification, "what the data cannot see").
> **Editorial stance:** *balanced analysis leaning toward advocacy.* Present the strongest version of the SWF / unrealized-gains-tax / economic-democracy case, design a workable mechanism, and steelman the best counterarguments (capital flight, valuation, government-as-shareholder, incentive effects, constitutionality) rather than dismissing them.
> **Geographic scope:** global / comparative. The proposal targets the U.S. but is designed from international precedent (Norway GPFG, Alaska APF, Singapore, the Meidner plan, citizens'-wealth-fund proposals).
> **Automation:** fully automated, self-updating weekly pipelines (GitHub Actions cron → fetch → model → regenerate dashboards → commit → site rebuild).

---

## 0. How to read this document

This plan is written for a coding agent (Claude Code) to execute end-to-end, and for Dhruv to review. It is organized as:

1. **Project goal and thesis** (§1)
2. **Site integration** — detect the stack, where the page lives (§2)
3. **The intellectual content** — five parts of the report, with the specific analyses, data, and claims each must contain (§3–§8)
4. **The data + automation architecture** — pipelines, sources, the "living" predicted-vs-realized tracker (§9–§11)
5. **Methodology standards** (§12)
6. **Phased execution plan** with concrete, checkable tasks (§13)
7. **Reference tables** — data sources/APIs, citations to gather, repo layout, acceptance criteria (§14–§18)

When in doubt, match the existing conventions of `/research/transit-airbnb-montreal` and `/research/worldcup-transit-strain`: a single long page structured as **The Question → Data → Method → Result → Why → What the data cannot see → Technical Notes**, with embedded interactive dashboards served as static HTML, a status badge, topic tags, and a "last updated" date.

---

## 1. Project goal and thesis

### 1.1 The anchoring event (verified facts — June 2026)

| Fact | Value |
|---|---|
| Pricing date / first trade | Priced June 11, 2026; first traded June 12, 2026 (Nasdaq) |
| Ticker | **SPCX** |
| Shares offered | 555,555,555 at **$135.00** |
| Gross raise | **~$75B** (greenshoe option: +83.33M shares ≈ +$11.2B) |
| Implied valuation | **~$1.77T** (≈ 7th-largest U.S. company; above Tesla ~$1.6T) |
| First-day close | **$161** (+19%); intraday high $168.75 (+25%) |
| Prior record | Saudi Aramco 2019 (~$25.6B, ~$29.4B w/ greenshoe) — SpaceX is **~3×** |
| Financials | FY2025 revenue **$18.7B**, net loss **$4.9B**; Starlink (9M+ users) profitable and growing; launch + xAI segments loss-making |
| Structure | Recently merged with **xAI** (an aerospace + AI conglomerate) |
| Implied P/S | ≈ **95×** trailing sales (no positive earnings → sales/sum-of-parts valuation required) |

> **Agent note:** these figures are the working baseline pulled from launch-week reporting. Phase 1 must re-verify each against the S-1/424B prospectus and at least two reputable outlets, and store them in `data/facts/ipo_facts.yaml` as the single source of truth that both the prose and the dashboards read from. Never hard-code a number in two places.

### 1.2 The thesis (one paragraph)

The largest IPO in history converts decades of partly public-funded R&D, government launch contracts, spectrum grants, and tax incentives into a ~$1.77T private capital stock concentrated under one founder's control. The same pattern recurred in 2008: the public bore the downside, took rescue-era equity, then sold it back at or below cost and captured almost none of the recovery. The **core proposal** of this report is an **equity condition on public support** — when a public company receives a bailout, or material subsidy/procurement support above a threshold, the public receives a *commensurate* equity stake (non-voting or independently stewarded), held in perpetuity in a **Social Wealth Fund** on the Norwegian/Alaskan model. This applies **going forward**, and is evaluated **retroactively** as well; the 2008 record (Part II) is the proof-of-concept for what such a fund would already be worth had the rule existed. A **separate and independent** strand of the report (Part IV) evaluates, on its own merits, an **accrual / mark-to-market tax on the unrealized gains of the very wealthy** — designed *symmetrically* (losses remunerated) with a liquidity solution. The fund does **not** depend on this tax; the two are separable policies that happen to be complementary. Throughout, the deep objections — capital flight, valuation, government-as-shareholder capture, moral hazard, incentive effects, constitutionality and retroactive-takings concerns — are engaged in the design, not waved away.

### 1.3 What "leaning toward advocacy" means operationally

- Every normative claim is paired with its strongest counterargument and a response.
- Every empirical claim is sourced and, where possible, computed from data in this repo (not asserted).
- The SWF and tax sections are framed as **engineering problems** ("here is a mechanism that survives the standard objections"), not as moral exhortation.
- A standing **"What the data cannot see"** and **"Strongest objections"** section in each policy part keeps the piece honest and raises its credibility.

---

## 2. Site integration (Phase 0)

The project page is a new entry under `/research/`, matching existing projects.

**Proposed slug:** `/research/spacex-social-wealth-fund`
**Proposed title:** *"Socializing the Upside: The Record SpaceX IPO and the Case for a Social Wealth Fund"*
**Status badge:** `IN PROGRESS` → `LIVE` once the pipeline and core dashboards ship.
**Tags:** `PUBLIC ECONOMICS` · `FINANCE & RISK` · `CAUSAL INFERENCE` · `DATA ENGINEERING` · `POLICY`.

### Phase 0 tasks

1. **Locate and detect the site repo.** Clone or point to the existing site (`github.com/dmehndiratta`, site `dhruv-mehndiratta.com`). Detect the framework by inspecting the repo root:
   - `next.config.*` / `app/` / `pages/` → **Next.js** (most likely, given client-rendered routes and static dashboard HTML under `/research/<slug>/`).
   - `astro.config.*` → **Astro**; `config.toml`/`hugo.*` → **Hugo**; `_config.yml` → **Jekyll**.
2. **Mirror the content model of an existing project.** Open the source of `/research/transit-airbnb-montreal` (its MDX/markdown + how it embeds `dashboard.html` via iframe with an "open full screen" link). Replicate that exact pattern: prose file + a `public/research/spacex-social-wealth-fund/` (or framework equivalent) folder holding the standalone dashboard `.html` files.
3. **Confirm the dashboard convention.** Existing dashboards are self-contained static HTML (Plotly/D3) at `…/research/<slug>/<name>.html`, embedded by iframe and linkable full-screen. Produce dashboards the same way (Plotly `write_html(..., include_plotlyjs="cdn", full_html=True)`).
4. **Add to the research index / homepage** card list with abstract and tags once content exists.
5. **If the site repo is not reachable in this environment:** build everything in this working folder as a drop-in bundle (`/site-dropin/` containing the page content file + the dashboards folder + an integration README), so Dhruv can copy it into his repo. Decide this at the start of Phase 0 and state which path was taken.

> **Do not** restyle the site or touch unrelated pages. Reuse existing CSS/components; match typography, the section-header style (`[ 01 · ACTIVE WORK ]` motif), and the footer.

---

## 3. Content architecture — the report

Single long page with a sticky section nav (this is a large piece; the nav makes it navigable), structured in five parts plus a methods appendix. Each part ends with **"Strongest objections"** and **"What the data cannot see."** Target depth: comparable rigor to the Montreal hedonic piece, scaled up across parts. Roughly **9,000–14,000 words** of prose plus **~16–20 interactive dashboards** — with **Part I deliberately the longest, most quantitative section** (the investment/risk/market analysis is the lead and the draw), and Part II held at full depth as the empirical backbone of the proposal.

```
I.    The Event        — IPO event study; investment + risk + market analysis (LEAD PART, expanded)
II.   The Entanglement — how much public money built these private fortunes; the 2008 counterfactual
III.  The Fund         — Social Wealth Fund funded by an EQUITY CONDITION on public support; precedent; simulation
IV.   The Tax          — STANDALONE evaluation of an accrual/mark-to-market tax on unrealized gains (separable from III)
V.    The Argument     — luck vs desert, job-creation, economic democracy (the normative spine)
A.    Methods Appendix — data, models, assumptions, reproducibility, limitations
```

Parts are sequenced so the *positive analysis* (I–II, what is) earns the reader's trust before the *normative/design* analysis (III–V, what could be). **Parts III and IV are independent proposals**: the fund stands entirely on the equity condition; the unrealized-gains tax is evaluated on its own merits. Either can be adopted without the other. Part I carries the most weight by design — it is the part most readers arrive for, and it is where the project's quantitative credibility is established.

---

## 4. Part I — The Event: investment, risk, and market analysis  *(lead part — most depth)*

**The Question.** Is the largest IPO in history priced like a business or like a moment? What does the historical record of record-breaking and mega-IPOs predict for SPCX over the lockup, index-inclusion, and 1–3 year horizons, and what does an event this size do to the market around it?

> This is the report's centerpiece and longest section. It should read as a self-contained, publication-grade equity + market analysis that a finance reader would take seriously on its own, *before* any policy argument. Aim for the depth of a sell-side initiation note crossed with the site's causal-inference honesty.

### 4.1 The deal and its mechanics
- Anatomy of the offering: 555,555,555 shares at $135, ~$75B gross, the **greenshoe / over-allotment** (+83.33M ≈ +$11.2B) and how stabilization works; primary vs secondary shares (how much is new capital vs insider cash-out); the resulting **public float** and free-float vs Musk's retained/controlled stake.
- Use-of-proceeds and pro-forma balance sheet from the prospectus; what the raise funds (launch capex, xAI compute, Starlink build-out).
- Share-class structure: map the dual-class/super-voting arrangement and compute **economic vs voting** ownership for the public float.

### 4.2 Valuation (the core quantitative work)
No positive earnings → build valuation from **sales, segments, and scenarios**, not P/E.
- **Comps table:** trailing/forward **EV/Sales** and growth-adjusted multiples vs a curated peer set (frontier-AI privates, satellite-broadband, launch/defense, hyperscalers as a compute proxy). Put the ~95× trailing-sales multiple in honest context (is it a Starlink multiple, an AI multiple, or a narrative multiple?).
- **Sum-of-the-parts (SOTP)** with each segment modeled explicitly:
  - **Starlink** (the profitable engine): ARPU × 9M+ subs, subscriber-growth S-curve, churn, gross margin, TAM; value on subscription/SaaS-style comps. This deserves its own mini deep-dive since it likely carries most of the defensible value.
  - **Launch** (Falcon/Starship): contracted backlog, launch cadence, $/kg trajectory, commercial vs government mix.
  - **xAI**: loss-making; value against the most recent frontier-AI private marks, with a wide band and an explicit "option value vs cash burn" treatment.
  - Reconcile the SOTP range to the $1.77T headline; show where the market's number sits in the distribution.
- **Reverse-DCF / implied-expectations:** solve for the revenue CAGR and steady-state margin the price implies at a plausible WACC. Headline the result as the **"what you must believe"** number, with a sensitivity grid (growth × margin × discount rate).
- **Scenario DCF:** explicit bull/base/bear with stated drivers and probabilities.

### 4.3 First-day pop and underpricing
- Locate the +19% close (and +25% intraday high) in the distribution of mega-IPO first-day returns.
- Quantify money "left on the table": ~555.6M × ($161−$135) ≈ **~$14B** notional first-day transfer from issuer to allocated investors; discuss book-building, allocation, and what underpricing of *this* size signals.
- **Long-run IPO underperformance:** situate against Ritter's post-IPO 3–5 year drift evidence and the mega-IPO subset specifically; flag the base rate honestly.

### 4.4 Risk analysis (full register + heatmap)
Build a structured risk register scored on **likelihood × impact**, quantified where possible, and rendered as an interactive heatmap:
- **Control / governance:** super-voting founder control; key-person (Musk) risk; related-party dynamics post-xAI merger; board independence.
- **Customer concentration:** dependence on U.S. government (NASA/DoD) revenue; quantify the government share of revenue from the prospectus and Part II data.
- **Regulatory:** FAA launch licensing, FCC spectrum & orbital-debris rules, antitrust, CFIUS/national-security, ITAR export controls.
- **Competition:** Amazon Kuiper, Blue Origin, Rocket Lab, Chinese state launch & satellite-internet constellations; frontier-AI competition for xAI.
- **Financial:** consolidated −$4.9B net loss, xAI cash burn, capex intensity, dilution path from greenshoe + future raises; refinancing/rate sensitivity (long-duration cash flows).
- **Market-structure / technical:** lockup overhang, float scarcity, index-timing, single-name concentration.
- **Valuation / sentiment:** multiple-compression risk if the AI/space narrative turns.

### 4.5 Market structure, flows, and price-discovery
- **Lockup waterfall:** identify the actual lockup terms/dates from the prospectus (often staged — e.g., 90/180-day tranches and price-trigger early releases); model the **supply shock** at each unlock and the historical price reaction of comparable unlocks.
- **Index-inclusion mechanics & flows:** eligibility/timing for **Nasdaq-100** (fast-track rules) and **S&P 500** (note the GAAP-profitability gate may delay S&P 500 entry given the net loss). Model the **passive demand** a ~$1.77T addition would create (estimate index AUM × target weight) and the likely price impact and front-running window.
- **Liquidity & microstructure:** float-adjusted turnover, expected bid-ask spread and depth, the role of the greenshoe in early price support.
- **Derivatives & positioning** (as data allows): options listing and implied volatility, short interest and borrow cost once available.
- **Factor / beta profile:** estimate SPCX beta and factor loadings (growth/duration/AI-momentum) from early trading; how rate moves should transmit to a long-duration name.

### 4.6 Broader-market and sector spillovers
- **Peer event-study:** abnormal returns (market-model CARs, proper SEs) around the SPCX debut for listed space/satellite/defense peers (Rocket Lab, AST SpaceMobile, Planet, Intelsat/SES, Iridium, defense primes) and for **Tesla** (read-through to Musk-complex valuation).
- **Index concentration & breadth:** what a single ~$1.77T listing does to already-elevated top-10 index weight and market breadth; liquidity-diversion question (does a mega-IPO pull flows from other names?).
- **"Mega-IPO as top signal":** test the folk claim that record IPOs cluster near market tops using the comparable set (event-time forward market returns after each record IPO).

### 4.7 The comparable set (build a reusable dataset)
Assemble `data/ipos/comparables.csv`: date, gross proceeds (nominal + CPI-adjusted), first-day return, 1m/3m/6m/1y/3y total return vs market, sector, profitability-at-IPO flag, dual-class flag, lockup terms.

> Saudi Aramco (2019) · Alibaba (2014) · SoftBank Corp (2018) · NTT DoCoMo / NTT (1987/1998) · Visa (2008) · Facebook/Meta (2012) · **General Motors (2010 re-IPO — the bailout bridge to Parts II–III)** · AIA (2010) · Glencore (2011) · Rivian (2021) · Uber (2019) · Snowflake (2020) · ARM (2023) · Reddit (2024) · Coupang (2021) · Airbnb (2020). Include a representative SPAC/de-SPAC for contrast.

### 4.8 Synthesis: the bull, base, and bear case
Pull §4.2–4.7 into one explicit investment view with probabilities, the key swing variables (Starlink margin trajectory, xAI burn, lockup supply, index flows), and the single "what you must believe" sentence for each scenario.

### 4.9 Predictions (the part that makes it "living")
State explicit, falsifiable predictions with confidence bands and **let the pipeline score them weekly** (see §11):
- Lockup-expiry price reaction (sign, magnitude, window) at each unlock tranche.
- Index-inclusion bump (event window) for Nasdaq-100 and, if/when eligible, S&P 500.
- 3-month and 12-month total return vs Nasdaq-100, as a base/bull/bear fan chart.
- Peer-spillover direction and magnitude.

**Dashboards for Part I:** (1) IPO league table — proceeds nominal vs CPI-adjusted; (2) first-day-pop distribution with SPCX marked; (3) post-IPO drift curves for comparables (event-time index); (4) **SOTP builder** (per-segment assumptions → implied valuation vs the $1.77T mark); (5) **reverse-DCF / "what you must believe"** sensitivity grid; (6) **risk heatmap** (likelihood × impact, interactive); (7) **lockup-waterfall + index-flow** model (supply/demand timeline); (8) **live SPCX price + prediction tracker** (predicted fan vs realized, auto-updating).

---

## 5. Part II — The Entanglement: public money, private fortunes, and the 2008 counterfactual

**The Question.** How much of the value being capitalized at IPO was underwritten by the public — through contracts, subsidies, guarantees, spectrum, and tax incentives — and what would the public hold today if, in past rescues, it had *kept* the equity it took instead of selling it back?

### 5.1 Quantify SpaceX's (and Tesla's) public scaffolding
Build `data/subsidies/` from primary sources:
- **Federal contracts & grants** via **USAspending.gov API** (recipient = SpaceX and subsidiaries): NASA Commercial Crew, Commercial Resupply (CRS-1/2), Artemis Human Landing System, Space Force/NSSL launch awards; cumulative obligated dollars over time.
- **FCC Starlink subsidy:** RDOF award (~$885.5M, 2020) and its subsequent rescission/denial (2022–2023) — a clean case study in the public underwriting an asset.
- **State/local incentives** via **Good Jobs First Subsidy Tracker** (Boca Chica/Starbase TX, Florida; Tesla Nevada Gigafactory ~$1.3B, NY Buffalo, ZEV credit revenue as context).
- Frame carefully: contracts are payment for services rendered, not pure gifts — say so. The argument is about *who bears risk and who captures upside*, not that every dollar was a handout. Present the honest version.

### 5.2 The retroactive counterfactual (the proof-of-concept for the equity condition)
This is the empirical backbone that earns Part III's proposal. It answers: *had an equity-on-public-support rule existed, what would the public hold today?* Two layers:
- **2008 bailouts.** Assemble **TARP transaction-level data** (U.S. Treasury): disbursements, the equity/warrants actually taken (e.g., GM ~60.8%, AIG ~92%, Citigroup stake/warrants, the CPP bank preferreds + warrants), and the **actual disposition** (when sold, at what price, realized gain/loss — including the ~$11B realized loss on the auto bailout). Then build the **"kept-it" counterfactual portfolio**: suppose each stake had been *retained* and pooled (or converted to a market-index sleeve at the disposition date) rather than sold; compute value through today vs what Treasury actually realized.
- **Subsidies & procurement (the SpaceX-relevant layer).** Extend the same logic to material non-bailout support: had a small equity claim been attached to major subsidies/procurement (the SpaceX NASA/DoD/FCC dollars from §5.1, plus comparable cases), what stake — and what present value — would the public fund hold? This is the bridge that makes the equity condition concrete, not just a finance-crisis story.
- Be rigorous about assumptions (dividends/reinvestment, dilution, that some firms would have failed without restructuring, survivorship, how to size an equity claim against a service contract vs a pure subsidy). Put every assumption in the methods appendix and expose the key ones as dashboard toggles. Label this clearly as an *illustrative counterfactual*, **not** an identified causal estimate.

**Dashboards for Part II:** (1) SpaceX cumulative federal obligations timeline (USAspending); (2) subsidy map (state/local); (3) **"what if we'd kept it" counterfactual** — realized vs retained value for the 2008 stakes, with assumption sliders; (4) **retroactive equity-condition estimate** — implied public stake & present value across bailouts + major subsidies.

**Strongest objections to pre-empt here:** contracts are payment for services, not gifts (so an equity claim against a contract is conceptually different from one against a bailout — say so and treat them separately); government equity can distort restructuring incentives; hindsight bias (we know markets recovered); retroactive application raises fairness/takings concerns (flagged here, addressed in Part III). Address each.

---

## 6. Part III — The Fund: a Social Wealth Fund funded by an equity condition on public support

**The Question.** If the public underwrites private companies — through bailouts, subsidies, and procurement — what mechanism lets it *hold* a commensurate claim on the upside rather than forfeit it, pool that claim in a fund that pays a broad dividend or funds public goods, and do so without the pathologies of state ownership? The **primary funding mechanism this report proposes is an equity condition on public support.** Global precedent (§6.1) informs the fund's *governance and distribution*, not primarily its funding.

### 6.1 Comparative precedent (build `data/swf/`)
| Fund | Funding source | Size (latest) | Distribution model | Governance lesson |
|---|---|---|---|---|
| **Norway GPFG** (NBIM) | Petroleum revenue | ~$1.7–1.8T; owns ~1.5% of global listed equities | Fiscal spending rule (~3% of fund/yr into budget) | Arms-length mgmt, broad indexing, Council on Ethics exclusions, transparency |
| **Alaska Permanent Fund** (APFC) | Oil royalties | ~$80B | **Universal citizen dividend (PFD)**, annual | Direct dividend builds political durability |
| **Singapore Temasek / GIC** | State reserves / surpluses | Temasek ~$300B+; GIC large | Reinvested; funds budget via NIRC | Active, commercial mandate; insulation from politics |
| **Australia Future Fund** | Budget surpluses | ~A$200B+ | Pre-funds public pension liabilities | Clear, narrow mandate |
| **Saudi PIF** | Oil + asset transfers | ~$900B+ | Domestic transformation | Cautionary: concentration & politicization risk |

### 6.2 The equity condition — the primary funding mechanism (design in detail)
The rule: **when a public company receives a bailout, or material subsidy/procurement support above a defined threshold, the public receives a commensurate equity stake**, transferred to the Social Wealth Fund and held (in principle) in perpetuity. Specify it precisely:
- **Trigger & threshold.** What counts as "material support" — direct bailouts and capital injections; loan guarantees (priced as an option); grants and subsidies above $X or above Y% of revenue; large sole-source/cost-plus procurement; tax incentives above a threshold. Distinguish **support that should convert to equity** (bailouts, subsidies, guarantees) from **arms-length payment for services** (a competitively-bid launch contract), where an equity claim is harder to justify — be explicit about where the line sits and why.
- **Sizing the stake.** A transparent formula: stake value ≈ a multiple of the subsidy/guarantee's fair value (e.g., warrants struck at the support date, à la the 1979 Chrysler rescue and TARP CPP warrants), so the public is compensated like any at-risk capital provider. Show worked examples (what SpaceX's NASA/FCC/state support would have implied).
- **Prospective application.** The default, cleanest version: the condition attaches to *future* support. Going forward, the SpaceX-style pipeline of public dollars would steadily capitalize the fund.
- **Retroactive application (evaluate carefully).** Assess applying it to past support — via the §5.2 counterfactual for illustration, and as live policy via mechanisms like a one-time conversion of outstanding obligations or a time-limited "claw-forward." Treat the **fairness and Fifth-Amendment takings** questions head-on; note which retroactive designs are most defensible (e.g., applying only to ongoing/renewing support, or offering it as a condition of *continued* eligibility rather than a backward seizure).
- **Form of the equity.** **Non-voting or independently-stewarded shares** by default, to neutralize the "the government will run companies" objection while preserving the public's economic claim.

### 6.3 Precedent that the equity condition is normal, not radical
- **It has been done:** the 1979 **Chrysler** federal loan guarantee took **warrants** — and the Treasury *profited*; **TARP** took warrants and equity across the banks (the bank programs broadly returned a profit); the **UK** took majority stakes in RBS and Lloyds; **In-Q-Tel** and development-finance institutions routinely take equity for public capital. The novelty here is not taking the stake — it is **retaining and pooling** it in a fund instead of selling it back at the first opportunity.
- Contrast with the actual 2008 disposition (Part II): stakes sold 2010–2014, upside forfeited.

### 6.4 Comparative precedent for governance & distribution
Use §6.1's fund table plus:
- **Meidner Plan (Sweden, 1970s):** wage-earner funds and gradual collective ownership via dilutive issuance — a cautionary tale on political durability (design for broad buy-in).
- **Citizen's-wealth-fund proposals** (People's Policy Project / Bruenig; Roosevelt Institute; UK IPPR Citizens' Wealth Fund; Atkinson's capital-endowment idea): non-voting public equity + a universal dividend. (Their *dilutive-scrip* funding route is presented as a **secondary/optional** top-up, not this report's primary mechanism.)

### 6.5 The fund's design (governance, distribution, secondary funding)
1. **Funding stack:** **(primary)** the equity condition of §6.2 — prospective, with the retroactive estimate as evidence; **(secondary/optional)** retained legacy crisis-era equity, an optional modest dilutive-scrip top-up, and — *only if separately adopted* — in-kind shares from the Part IV tax. **The fund stands on the equity condition alone.**
2. **Governance against capture:** independent, professionalized management at arms length from the legislature (Norway/NBIM model); statutory mandate; broad diversification / near-indexing to avoid "picking winners"; non-voting/independently-stewarded shares; transparency and an ethics council; a constitutional/statutory lock against political raiding.
3. **Distribution:** a hybrid — a universal **citizen's dividend** (Alaska's durability lesson) plus a ring-fenced allocation to social programs; a spending rule (Norway's ~3% real) to keep it perpetual.
4. **Economic-democracy link (bridge to Part V):** even non-voting public ownership creates accountability and a claim on returns; optionally pair with governance-representation channels (worker/citizen seats) discussed in Part V.

### 6.6 Simulation
Build a **fund-growth simulator**: inflows driven by the **equity-condition rule** (sliders for trigger threshold, stake-sizing multiple, prospective vs prospective+retroactive, plus optional scrip/tax top-ups), a return assumption, a spending/dividend rule, and a horizon → project fund AUM, annual **dividend per capita**, and total distributions. Stress-test against a 2008-style drawdown. Calibrate returns to GPFG's actual long-run real return. Include a "SpaceX-only" illustration (what this single company's public support would contribute).

**Dashboards for Part III:** (1) global SWF comparison (size, funding, distribution, governance); (2) **equity-condition fund simulator** (rule parameters → AUM + per-capita dividend over time); (3) Alaska PFD history vs a hypothetical U.S. fund dividend; (4) precedent timeline (Chrysler warrants → TARP → UK stakes → proposed condition).

**Strongest objections:** **moral hazard** (does guaranteed public equity encourage rent-seeking for subsidies? — counter: the stake *prices* the support and dampens the upside of capture); state ownership distorts markets / soft-budget constraints; political raiding; crowding out private investment; chilling effect on firms accepting public contracts / **competitiveness & WTO-subsidy-rule** concerns; **retroactive takings**; the Meidner political-durability failure; "creeping nationalization." Answer each via the non-voting + arms-length + spending-rule + warrant-priced-stake + dividend-durability design, and concede where concessions are due.

---

## 7. Part IV — The Tax: making an accrual tax on unrealized gains work  *(standalone; separable from Part III)*

**The Question.** Most great fortunes are unrealized capital gains that are never taxed (the holder borrows against them and dies, with basis stepped up). *Independently of whether the Part III fund exists*, can you tax accruing gains in a way that is administrable, liquidity-sensitive, **symmetric** (it remunerates losses), and constitutionally plausible? This part evaluates the unrealized-gains tax **on its own merits** — rationale, design, revenue, objections. Where the proceeds go (general revenue, program funding, or *optionally* capitalizing the Social Wealth Fund) is a **separate** downstream choice, addressed briefly at the end and not assumed.

### 7.1 The problem, quantified
- **"Buy, borrow, die":** explain SBLOCs/pledged-asset lines (borrow against appreciated stock at low rates, spend tax-free) and **stepped-up basis at death** (IRC §1014) erasing the gain. Use a worked example with real-ish numbers.
- **Scale:** estimate the stock of **unrealized gains** held by the top 1%/0.1% and the **realization gap** using the Fed's **Distributional Financial Accounts (DFA)**, the **Survey of Consumer Finances (SCF)**, and the Saez–Zucman / Realtime Inequality data. Present "how much wealth is effectively outside the income-tax base."

### 7.2 The proposals to evaluate
- **Wyden "Billionaires Income Tax":** annual **mark-to-market** for *tradable* assets (thresholds: >$1B net worth or >$100M income for 3 yrs); for *non-tradable* assets, a **deferral-recapture / lookback interest charge** at realization instead of annual valuation.
- **Biden "Billionaire Minimum Income Tax":** a 25% minimum on total income *including* unrealized gains for households >$100M.
- **Academic designs:** retrospective/accrual-equivalent taxation and the **deferral-charge (Auerbach–Bradford) approach** that mimics accrual without annual valuation — the key tool for illiquid assets.

### 7.3 The two hard problems and this report's solutions
1. **Liquidity / the "dry tax" problem** (owe tax on gains with no cash):
   - Tradable assets → annual mark-to-market (cash is realizable).
   - Illiquid/private assets → **deferral-charge at realization** (no annual valuation needed), *or*
   - **Elect to pay in kind with shares** (or other assets), settling the liability without forcing a sale — which removes the liquidity objection. *If* the Part III fund exists, those shares are a natural destination, but in-kind payment works regardless (the government can hold or auction them); **the tax does not presuppose the fund.**
   - Multi-year installment options for lumpy liabilities.
2. **Symmetry / remunerating losses** (the user's explicit ask):
   - The tax must be **two-sided**: when marked assets fall, the taxpayer receives a **refundable loss credit** or **carryback with an interest factor**, so the government is a genuine silent partner in gains *and* losses, not a fair-weather one.
   - Discuss refundability limits, anti-gaming (wash-sale-style rules), and why symmetry is what makes accrual taxation *fair* rather than confiscatory. The deferral-charge design is inherently closer to symmetric because it prices the time value of deferral both ways.

### 7.4 The objections — engaged, not dodged
- **Valuation** of private/illiquid assets → why the tradable/non-tradable split + deferral charge sidesteps most valuation disputes.
- **Capital flight / expatriation / migration** → review the actual evidence (Young et al. "Myth of Millionaire Tax Flight"; the mixed European wealth-tax record and *why* — design flaws, exemptions, low thresholds — vs a narrow, high-threshold, exit-tax-backstopped design).
- **Administrability** → narrow base (a few thousand taxpayers), reuse of existing brokerage reporting.
- **Constitutionality** → **Moore v. United States (2024)**: the Court upheld the Mandatory Repatriation Tax on narrow grounds and *expressly declined* to resolve whether realization is constitutionally required; map the live risk and the designs most likely to survive (income-tax framing vs a 16th-Amendment realization challenge), plus the corporate-tax-integration and double-tax issues.
- **Incentives / lock-in** → accrual taxation actually *reduces* the lock-in distortion of the realization system; address innovation/risk-taking concerns.

### 7.5 Revenue model
Build a **revenue + behavioral model**: base (# of taxpayers, stock of unrealized gains from DFA/SCF), rate, expected return, **avoidance/migration elasticity** (scenario slider), and **loss-refund drag** → annual revenue. Show base/conservative/aggressive scenarios; be explicit that high-end estimates are sensitive to elasticities. Treat **earmarking** (general revenue vs program funding vs optional fund capitalization) as a separable downstream toggle — the tax's case stands on horizontal equity and the closed loophole regardless of destination.

**Dashboards for Part IV:** (1) "buy-borrow-die" explainer (interactive worked example: appreciation → borrow → step-up vs accrual tax); (2) unrealized-gains-by-wealth-percentile (DFA/SCF); (3) **revenue simulator** with avoidance + loss-refund toggles; (4) symmetric-treatment illustration (gain years vs loss years, with/without remuneration).

---

## 8. Part V — The Argument: luck, desert, and economic democracy (normative spine)

**The Question.** Why is public claim and public control over the most powerful productive assets *legitimate* — not merely useful? This part supplies the normative justification the policy parts lean on.

Make the case clearly, then steelman the opposition and respond. Cover:
- **Luck vs. desert.** Rawls's "natural lottery" and original position; Dworkin's brute-luck vs option-luck; the empirical literature on luck in success (Frank, *Success and Luck*); Hayek's *own* point that market rewards track value-to-others, not moral desert. The "many tried to recreate their success and couldn't" intuition → regression to the mean, survivorship bias, and the role of inheritance and timing (cite intergenerational-mobility evidence; Chetty et al.).
- **"The rich are the job creators."** The demand-side rebuttal (Hanauer's "middle-out"; consumption and the multiplier); evidence on where job creation actually comes from (young firms, not the wealthy per se — Haltiwanger); the distinction between *the market* coordinating production and *individuals* capturing its rewards.
- **Economic democracy & accountability.** Robert Dahl, *A Preface to Economic Democracy*; Elizabeth Anderson, *Private Government* (firms as unaccountable governments over workers' waking lives — the user's "a third of your life / half your waking life at work, so why is democracy confined to the other hours?" framing); codetermination evidence (German *Mitbestimmung* / works councils, and what the empirical literature finds about productivity and stability). Tie back: a SWF + governance channels extend democratic accountability to concentrated economic power.

**Strongest objections:** desert-based and libertarian property-rights defenses (Nozick); Hayekian knowledge/coordination and the innovation-incentive argument; public-choice/government-failure skepticism. Present each at full strength, then respond. End the part by stating honestly what remains genuinely contested (it's a values disagreement, not only an empirical one).

---

## 9. Data & automation architecture

### 9.1 Principles
- **Single source of truth:** every number lives once, in `data/`, read by both prose (via a small templating/`facts.yaml` mechanism) and dashboards. No number hard-coded twice.
- **Raw is immutable & dated:** snapshots land in `data/raw/<source>/<YYYY-MM-DD>/`; processing reads raw, writes `data/processed/`.
- **Fail safe:** a failed fetch must never overwrite good data; validate (row counts, schema, sanity bounds) before promoting a snapshot; keep last-good.
- **Reproducible & fast:** pinned deps; the whole pipeline should run end-to-end in minutes (match the house "under two minutes" ethos where feasible), cache slow pulls.
- **Deterministic dashboards:** dashboards build from `data/processed/` only.

### 9.2 Stack
Python: `pandas`, `numpy`, `statsmodels` (event studies, regressions, HC3 SEs), `scikit-learn`/`lightgbm` (cross-checks), `plotly` (dashboards as static HTML, `include_plotlyjs="cdn"`), `requests`/`httpx`, `pyyaml`, `pyarrow`. Use `yfinance`/`stooq` for prices, `pandas_datareader`/FRED for macro. Pin in `requirements.txt` (or `uv`/`pyproject.toml`).

### 9.3 Pipeline stages (`pipeline/`, numbered like the existing projects)
```
00_fetch.py      # pull from each source → data/raw/<source>/<date>/ (with validation + last-good fallback)
10_clean.py      # normalize, join, → data/processed/*.parquet
20_models.py     # event studies, SOTP/reverse-DCF, TARP counterfactual, fund sim, revenue sim
30_score.py      # update the predicted-vs-realized tracker (Part I)
40_dashboards.py # regenerate all *.html dashboards from data/processed
50_facts.py      # regenerate facts.yaml / injected numbers + "last updated" timestamp
```
Each stage is independently runnable and logs what it did. A top-level `run.py`/`make all` chains them.

### 9.4 Orchestration (the "self-updating" requirement)
- **GitHub Actions** workflow `.github/workflows/update.yml`, **weekly cron** (e.g., `0 13 * * 1`, Monday — matching the site's "updated weekly" language), plus manual `workflow_dispatch`.
- Steps: checkout → setup Python (cached) → run pipeline → if `data/processed` or dashboards changed, commit & push → site's existing deploy (Vercel/Netlify/Pages) rebuilds automatically.
- Store any API keys as GitHub repo **secrets**; document required secrets in the integration README. Prefer keyless sources where possible (USAspending, FRED with free key, yfinance).
- Add a **status footer** on the page: "Data last updated: {timestamp} · next scheduled refresh: weekly."

> If Dhruv prefers, a Cowork **scheduled task** can mirror the weekly run as a backup/notifier — note this as an option, don't assume it.

---

## 10. Dashboards (inventory)

Build as standalone Plotly HTML under the project's static dashboard folder; embed by iframe with an "open full screen" link (house pattern). Minimum set:

*Part I (lead — most dashboards):*
1. IPO league table (proceeds nominal vs CPI-adjusted)
2. First-day-pop distribution, SPCX marked
3. Post-IPO drift, event-time, comparables
4. **SOTP builder** (per-segment assumptions → implied valuation vs $1.77T)
5. **Reverse-DCF "what you must believe"** sensitivity grid
6. **Risk heatmap** (likelihood × impact, interactive)
7. **Lockup-waterfall + index-flow** model (supply/demand timeline)
8. **Live SPCX price + prediction tracker** (auto-updating)

*Part II:*
9. SpaceX cumulative federal obligations timeline
10. Subsidy map (state/local)
11. "Kept-it" 2008 counterfactual (assumption sliders)
12. **Retroactive equity-condition estimate** (implied public stake & PV across bailouts + major subsidies)

*Part III:*
13. Global SWF comparison (size, funding, distribution, governance)
14. **Equity-condition fund simulator** (rule parameters → AUM + per-capita dividend)
15. Alaska PFD history vs a hypothetical U.S. dividend
16. Precedent timeline (Chrysler warrants → TARP → UK stakes → proposed condition)

*Part IV (standalone):*
17. Buy-borrow-die interactive explainer
18. Unrealized gains by wealth percentile
19. **Accrual-tax revenue simulator** (avoidance + loss-refund toggles)
20. Symmetric-treatment illustration (gain vs loss years, with/without remuneration)

Keep dashboards lightweight, mobile-friendly, and theme-matched (read existing dashboard CSS).

---

## 11. The "living analysis" — predicted-vs-realized tracker

This is what makes the piece genuinely living and on-brand:
- At publish, freeze the Part I predictions (lockup reaction, index bump, 3m/12m return fan, peer spillover) into `data/predictions/predictions.yaml` with timestamps and confidence bands.
- `30_score.py` runs weekly: pulls realized SPCX + benchmark returns, computes realized vs predicted, updates a scorecard and the tracker dashboard, and appends to a public changelog ("As of {date}: 3-month call is tracking within band / outside band").
- This demonstrates intellectual honesty (predictions are scored, not quietly forgotten) and gives readers a reason to return.

---

## 12. Methodology standards (match the house bar)
- **Event studies:** define estimation/event windows explicitly; market-model or FF-factor abnormal returns; report CARs with proper SEs; **HC3** robust SEs on regressions (as in the Montreal piece).
- **Cross-validation of claims:** where a regression result carries weight, corroborate with a second method (e.g., LightGBM + SHAP) so a finding isn't a single-spec artifact — the site's signature move.
- **Every assumption visible:** counterfactual, simulator, and revenue-model assumptions live in the methods appendix and, where they drive results, are exposed as dashboard toggles.
- **"What the data cannot see"** subsection in every part: private-asset valuation opacity, behavioral elasticities are uncertain, counterfactuals are not identified causal estimates, etc. Distinguish *descriptive/illustrative* models from *causal* claims clearly.
- **Sourcing:** primary sources for every figure (prospectus, Treasury, USAspending, Fed, NBIM, APFC, CBO/JCT, peer-reviewed papers). Maintain a `SOURCES.md` and inline citations/footnotes in the house style.

---

## 13. Phased execution plan

> Each phase has a definition-of-done. Phases 1–2 are positive analysis; 3–5 are design/normative; 6 integrates; 7 automates; 8 verifies. A coding agent should work phase by phase, committing per phase.

**Phase 0 — Setup & integration recon** *(done when: stack detected; slug/page scaffold created; dashboard convention confirmed; repo layout from §15 created).*
- Detect site framework; mirror an existing research page's structure; create page scaffold + static dashboards folder; init `data/`, `pipeline/`, `.github/workflows/`.

**Phase 1 — The Event (Part I) — the lead; build it deepest** *(done when: comparables dataset built; valuation (SOTP + reverse-DCF + scenario), full risk register/heatmap, market-structure/flows, and peer event-studies written and computed; predictions frozen; dashboards 1–8 live).*
- Re-verify IPO facts → `facts/ipo_facts.yaml`; build comparables dataset; run event studies, SOTP + reverse-DCF + scenario DCF, lockup/index-flow model, risk heatmap; write the expanded Part I; freeze predictions.

**Phase 2 — The Entanglement (Part II)** *(done when: USAspending + subsidy data pulled; the retroactive counterfactual computed for the 2008 bailouts AND extended to major subsidies/procurement with documented assumptions; dashboards 9–12 live; Part II written at full depth).*

**Phase 3 — The Fund (Part III)** *(done when: the equity-condition mechanism is fully specified — trigger/threshold, stake-sizing formula, prospective + retroactive treatment, non-voting form; SWF comparative dataset built; equity-condition fund simulator working; design + precedent + objections incl. moral hazard, takings, competitiveness written; dashboards 13–16 live).*

**Phase 4 — The Tax (Part IV, standalone)** *(done when: DFA/SCF unrealized-gains data pulled; revenue + symmetry models built; the tax written as a self-standing policy with a liquidity solution (deferral-charge / in-kind / installments) and symmetric loss remuneration; earmarking treated as separable; dashboards 17–20 live).*

**Phase 5 — The Argument (Part V)** *(done when: normative section written with steelmanned objections and responses; citations in place).*

**Phase 6 — Assemble & integrate** *(done when: full page assembled with sticky nav, abstract, tags, status badge, last-updated footer; added to research index/homepage; renders correctly in the live framework; mobile-checked).*

**Phase 7 — Automate** *(done when: GitHub Actions weekly workflow runs the full pipeline green, regenerates dashboards + facts, commits, triggers deploy; secrets documented; fail-safe + last-good verified).*

**Phase 8 — Verification & honesty pass** *(done when: every figure traced to a primary source; numbers consistent between prose and dashboards; predictions tracker scoring correctly; objections sections present in every part; "what the data cannot see" present in every part; a fresh read confirms the advocacy is earned, not asserted).*

---

## 14. Data sources & APIs (reference)

| Domain | Source | Access | Cadence | Keyless? |
|---|---|---|---|---|
| SPCX & peer prices, indices | yfinance / Stooq / Alpha Vantage | API/lib | daily→weekly | yfinance/Stooq yes |
| Macro (CPI, rates) | FRED | API | as needed | free key |
| Federal contracts/grants | **USAspending.gov** API | REST | weekly | yes |
| State/local subsidies | Good Jobs First Subsidy Tracker | download/scrape | quarterly | yes |
| FCC Starlink (RDOF) | FCC | download | static | yes |
| NASA contracts | NASA / USAspending | REST | weekly | yes |
| 2008 bailout | U.S. Treasury TARP transaction data | download | static | yes |
| Wealth distribution / unrealized gains | Fed **DFA**, **SCF**; Realtime Inequality (Saez–Zucman) | download/API | quarterly | yes |
| Norway SWF | NBIM (returns/holdings) | download | quarterly | yes |
| Alaska SWF | APFC / PFD division | download | annual | yes |
| Other SWFs | SWF Institute, fund annual reports | download | annual | mostly |
| Tax-policy estimates | CBO, JCT, Tax Policy Center, Tax Foundation | download | as needed | yes |

> Respect each source's license/ToS; cite CC/attribution as the Montreal piece does (e.g., "USAspending.gov public domain"). Prefer official downloads over scraping; if scraping is unavoidable, throttle and cache.

## 15. Repo / folder layout
```
spacex-social-wealth-fund/
├── plan.md                      # this file
├── README.md                    # how to run, secrets, integration notes
├── requirements.txt             # pinned
├── run.py                       # chains pipeline stages
├── data/
│   ├── facts/ipo_facts.yaml     # single source of truth for headline numbers
│   ├── predictions/predictions.yaml
│   ├── raw/<source>/<YYYY-MM-DD>/
│   └── processed/*.parquet
├── pipeline/
│   ├── 00_fetch.py 10_clean.py 20_models.py 30_score.py 40_dashboards.py 50_facts.py
├── models/                      # SOTP, TARP counterfactual, fund sim, revenue sim modules
├── dashboards/                  # build scripts → static html
├── site-dropin/                 # page content (MDX/md) + dashboards/, if site repo not directly editable
├── SOURCES.md
└── .github/workflows/update.yml # weekly cron
```

## 16. Acceptance criteria (definition of done for the whole project)
- The page is live at `/research/spacex-social-wealth-fund`, matches house style, and is linked from the research index/homepage.
- All five parts + methods appendix are written; each policy/normative part contains a **"Strongest objections"** response and each part contains a **"What the data cannot see."**
- **Part I is the most developed section** (depth, prose, and dashboard count) — it reads as a standalone publication-grade equity/market analysis.
- ≥16 interactive dashboards live and theme-matched; the live SPCX/prediction tracker updates.
- Every headline figure traces to a primary source in `SOURCES.md`; prose and dashboards never disagree on a number.
- The GitHub Actions weekly pipeline runs green, regenerates data + dashboards + facts + the prediction scorecard, commits, and triggers a deploy; fail-safe verified.
- **The SWF (Part III) is funded primarily by the equity condition** — the mechanism is specified concretely (trigger/threshold, stake-sizing, prospective + retroactive treatment, non-voting form) and backed by the §5.2 retroactive estimate. **Part III does not depend on Part IV.**
- **The tax (Part IV) is evaluated as a standalone policy** and explicitly delivers the two requested features: **symmetric loss remuneration** and a **liquidity solution** (deferral-charge / installments / optional in-kind payment); routing proceeds to the fund is presented as an *optional* downstream choice, not a dependency.
- The advocacy is *earned*: claims are sourced/computed and the best counterarguments are engaged.

## 17. Citations to gather (starter list — verify/expand in Phase 8)
SpaceX S-1/424B prospectus; U.S. Treasury TARP reports & GM stake disposition; **Chrysler Corporation Loan Guarantee Act (1979) and the Treasury's warrant profit**; **UK RBS/Lloyds bank-stake history (UKFI/UKGI)**; constitutional sources on takings/retrospective taxation; WTO Agreement on Subsidies and Countervailing Measures (competitiveness angle); USAspending.gov; FCC RDOF orders; Fed DFA/SCF; NBIM & APFC annual reports; Ritter IPO underpricing/long-run-performance papers; Auerbach–Bradford on retrospective taxation; Wyden Billionaires Income Tax white paper; Treasury Greenbook (Billionaire Minimum Income Tax); *Moore v. United States* (2024); Saez & Zucman; Young et al. on millionaire migration; Bruenig/People's Policy Project social-wealth-fund proposals; IPPR Citizens' Wealth Fund; the Meidner Plan; Rawls *A Theory of Justice*; Dworkin on luck; Frank *Success and Luck*; Chetty et al. mobility; Haltiwanger on firm-age job creation; Dahl *A Preface to Economic Democracy*; Anderson *Private Government*; codetermination empirical literature.

## 18. Open questions for Dhruv (non-blocking — sensible defaults assumed)
1. **One long page vs. a hub + sub-pages?** Default: one long page with sticky section nav (matches existing projects). Switch to a hub if it gets too long — likely, given Part I's expanded scope.
2. **Equity condition — retroactive scope?** How far to push retroactivity: illustrative-only (the §5.2 counterfactual), apply to *ongoing/renewing* support, or a full "claw-forward"? Default: lead with the **prospective** rule; present retroactivity as (a) an illustrative counterfactual and (b) a defensible "condition of continued eligibility" variant, with the takings analysis attached.
3. **Equity condition — trigger & stake-sizing?** What counts as "material support," and how big is the stake? Default: a **warrant-priced** stake on bailouts/guarantees/subsidies above a $X or Y%-of-revenue threshold; arms-length, competitively-bid service contracts excluded or treated separately.
4. **Distribution — citizen dividend vs. program funding?** Default: present both; lead with a hybrid.
5. **Tax threshold to model** ($100M / $1B net worth)? Default: model both, headline the $1B (Wyden) tier for defensibility.
6. **Any API keys you already have** (Alpha Vantage, FRED)? Default: keyless sources first; add keys as secrets if provided.
7. **Branding of the fund** for the piece (e.g., "American Permanent Fund" / "Citizens' Wealth Fund")? Default: "Citizens' Wealth Fund."
```

# peacekeeping-for-profit-update

Do poorer countries send soldiers to UN peacekeeping missions to earn money? This project builds the data needed to test that question with recent figures, following the argument of Coleman and Nyblade (2018).

**Status:** the data and indicators are complete and checked. Applying the authors' exact test is the next step and will be added once their criteria are confirmed from the paper itself.

![Estimated UN reimbursements as a share of military spending](figures/reimbursement_share_of_military_spending_2019.png)

## What this is and why it matters

The UN does not have its own army. Countries lend it soldiers and police, and the UN pays those governments a fixed amount per soldier per month, currently $1,448. For a rich country this is small, but for a poor country with a small military budget it can be a large source of money. That has led to a popular claim that some countries send peacekeepers mainly for profit.

Coleman and Nyblade (2018) argue that this claim is overstated: profit can plausibly explain contributions only when a country's deployment is large compared with its armed forces and military spending, and only for a limited group of countries. This repository brings together the data to check that argument with figures up to 2026: how many personnel each country sent every month since 1990, the size of its armed forces, its military spending, and an estimate of what the UN paid it.

It can be used to see which countries depend most on UN payments, how that changed as missions closed, and to test claims about "peacekeeping for profit" with official numbers.

## The reference study

Katharina P. Coleman and Benjamin Nyblade. 2018. "Peacekeeping for profit? The scope and limits of 'mercenary' UN peacekeeping." *Journal of Peace Research* 55 (6): 726-741. https://doi.org/10.1177/0022343318775784

The authors' data and code are not in the journal's replication archive, so this is an update built from public sources, not a replication of their files.

## The data

| File | Contents |
|---|---|
| [`data/clean/un_personnel_monthly.csv`](data/clean/un_personnel_monthly.csv) | One row per country per month, Nov 1990 to Jul 2026: personnel by category, the UN rate in force, estimated reimbursement |
| [`data/clean/panel_country_year.csv`](data/clean/panel_country_year.csv) | One row per country per year, with the indicators below |

Main columns of the yearly file:

| Column | Meaning |
|---|---|
| `avg_troops`, `avg_formed_police_units`, `avg_individual_police`, `avg_police_total`, `avg_staff_officers`, `avg_experts_on_mission` | Average personnel deployed over the year, by category |
| `avg_contingent` | Troops plus formed police units: the units the UN reimburses at its monthly rate |
| `avg_total_uniformed` | All uniformed personnel |
| `months_with_data`, `months_contributing` | Months the UN has data for that year, and months the country had anyone deployed |
| `est_reimbursement_usd` | Contingent personnel x the UN monthly rate, summed over the year (only for years with a verified rate in every month: 2015 onward) |
| `armed_forces_personnel` | Size of the country's armed forces (World Bank; available to 2020) |
| `military_expenditure_usd`, `military_expenditure_pct_gdp` | Military spending (World Bank, based on SIPRI) |
| `gdp_per_capita_usd` | Income per person (World Bank) |
| `contingent_pct_of_armed_forces` | Deployed contingents as a percent of the armed forces |
| `reimbursement_pct_of_military_expenditure` | Estimated UN payments as a percent of military spending |

## Read this first

- **The reimbursement is an estimate of gross payments to governments, not profit.** Countries pay their own costs of deploying, and how much reaches individual soldiers varies by country.
- **Equipment payments are not included.** The UN also pays separately for contingent-owned equipment, so total payments are higher than shown.
- **Rates before July 2014 are not included yet.** They will be added only once checked against an official UN document.
- **Yearly averages count months with no contribution as zero.** The UN's own annual figures average each category only over the months it was reported, which overstates countries that left or joined a mission during the year (see the check report).
- Before 2010 the UN recorded police as one total; the split into individual police and formed police units exists only for the last few years before 2010.

## How the numbers were checked

Run by [`code/02_check_panel.py`](code/02_check_panel.py); results in [`data/clean/check_report.md`](data/clean/check_report.md).

1. The monthly data, averaged the way the UN does, matches the UN's separately published annual figures for all 2,115 country-years from 2010 onward.
2. Months missing from the data are listed (none from 2010 to July 2026).
3. The join between the UN's pre-2010 and post-2010 datasets was checked (98,194 in December 2009, 99,943 in January 2010).
4. Values that are impossible, such as more personnel deployed than the country's whole armed forces, are screened.
5. Every reimbursement rate was checked against the UN document named next to it in `data/raw/un_troop_reimbursement_rates.csv`.

## Reproduce it

```
pip install -r requirements.txt
python code/01_build_panel.py
python code/02_check_panel.py
python code/03_make_figures.py
```

## Sources and license

Sources and download dates are in [`data/README.md`](data/README.md). Code: MIT (see [`LICENSE`](LICENSE)). The clean dataset: CC BY 4.0.

## Cite

See [`CITATION.cff`](CITATION.cff).

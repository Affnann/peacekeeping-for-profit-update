# Data

## Sources

| File in `raw/` | Source | Publisher | Address | Downloaded on | Terms |
|---|---|---|---|---|---|
| `un_DPO-UCHISTORICAL.csv.gz` | Historical Uniformed Personnel Contribution (monthly, by country and mission, Jan 2010 onward) | United Nations, Department of Peace Operations, via the Peace and Security Data Hub | https://psdata.un.org (API: https://api.psdata.un.org/public/data/DPO-UCHISTORICAL/csv) | 29 Oct 2026 | UN open data |
| `un_DPPADPO-UCPre2010.csv.gz` | Historical Uniformed Personnel Contribution prior to 2010 (Nov 1990 to Dec 2009) | as above | https://api.psdata.un.org/public/data/DPPADPO-UCPre2010/csv | 29 Oct 2026 | UN open data |
| `un_DataCommons-UCHISTORICAL.csv.gz` | Annual Uniformed Personnel Contribution Statistics (yearly averages, 2010 onward) | as above | https://api.psdata.un.org/public/data/DataCommons-UCHISTORICAL/csv | 29 Oct 2026 | UN open data |
| `worldbank_MS.MIL.TOTL.P1.json.gz` | Armed forces personnel, total | World Bank, World Development Indicators | https://api.worldbank.org/v2/country/all/indicator/MS.MIL.TOTL.P1 | 29 Oct 2026 | CC BY 4.0 |
| `worldbank_MS.MIL.XPND.CD.json.gz` | Military expenditure (current US$; World Bank series based on SIPRI) | as above | .../indicator/MS.MIL.XPND.CD | 29 Oct 2026 | CC BY 4.0 |
| `worldbank_MS.MIL.XPND.GD.ZS.json.gz` | Military expenditure (% of GDP) | as above | .../indicator/MS.MIL.XPND.GD.ZS | 29 Oct 2026 | CC BY 4.0 |
| `worldbank_NY.GDP.PCAP.CD.json.gz` | GDP per capita (current US$) | as above | .../indicator/NY.GDP.PCAP.CD | 29 Oct 2026 | CC BY 4.0 |
| `un_troop_reimbursement_rates.csv` | UN reimbursement rate per soldier per month, typed from the official documents named in its `source` column | United Nations General Assembly | see file | 29 Oct 2026 | UN documents |

## Notes

- Files ending in `.gz` are compressed but otherwise unchanged.
- The UN notes that some months are missing in both troop-contribution datasets.
- World Bank armed forces data ends in 2020.
- Reimbursement rates before July 2014 are not yet included; they will be added only once checked against an official UN document.

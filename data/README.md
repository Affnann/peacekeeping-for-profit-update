# Data

## Sources

| Data | Source | Where it comes from | Terms |
|---|---|---|---|
| UN uniformed personnel by country and month, Nov 1990 to Jul 2026 | United Nations, Peace and Security Data Hub (psdata.un.org), via **peacekeeping-tracker v1.0.0** (Azom 2026, https://doi.org/10.5281/zenodo.23752307) | Rebuilt locally by `code/00_get_un_data.py`, which runs peacekeeping-tracker's own download and build code at tag v1.0.0 | UN terms of use: personal, non-commercial use; no redistribution. Not stored in this repository |
| UN standard reimbursement rates | UN General Assembly resolutions 68/281, 72/285, 76/276 and 80/272, as tabulated in peacekeeping-tracker v1.0.0 (`data/reference/reimbursement_rates.csv`) | Read from the pinned peacekeeping-tracker clone | CC BY 4.0 (the table) |
| Armed forces personnel, total (`MS.MIL.TOTL.P1`) | World Bank, World Development Indicators | `worldbank/`, downloaded 29 Oct 2026 from https://api.worldbank.org/v2/country/all/indicator/MS.MIL.TOTL.P1 | CC BY 4.0 |
| Military expenditure, current US$ (`MS.MIL.XPND.CD`; based on SIPRI) | as above | `worldbank/`, downloaded 29 Oct 2026 | CC BY 4.0 |
| Military expenditure, % of GDP (`MS.MIL.XPND.GD.ZS`) | as above | `worldbank/`, downloaded 29 Oct 2026 | CC BY 4.0 |
| GDP per capita, current US$ (`NY.GDP.PCAP.CD`) | as above | `worldbank/`, downloaded 29 Oct 2026 | CC BY 4.0 |

## Folders

- `worldbank/`: the World Bank files as downloaded (compressed, otherwise unchanged). In the repository.
- `build/`: the full panel, created by `code/01_build_panel.py`. Not in the repository, because it contains UN figures.
- `check_report.md`: the output of `code/02_check_panel.py`.

## Notes

- The UN serves its files with rows in a varying order, so a fresh download's fingerprint can differ from the one recorded in peacekeeping-tracker even when the content is the same. peacekeeping-tracker's check that the rebuild matches its v1.0.0 monthly totals is the test that matters, and `code/00_get_un_data.py` stops if it fails.
- World Bank armed forces data ends in 2020.

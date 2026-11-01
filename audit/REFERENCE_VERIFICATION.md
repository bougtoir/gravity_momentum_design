# REFERENCE_VERIFICATION.md — independent verification of all 25 references

Method: existing REFERENCE_AUDIT.md (live search, 2026-09-26) re-confirmed plus a
fresh pass over every identifier via Crossref API, PubMed/PMC E-utilities, and
NTRS records. Corrections applied to scripts/make_manuscript.py REFS.

| # | Key | Verified identity | Source | Discrepancy / fix |
|---|-----|-------------------|--------|-------------------|
| 1 | Newman1992 | Newman DJ, MIT thesis 1992 | MIT hdl | none |
| 2 | Richter2017 | Front Physiol 2017;8, PMC5559498 | PMC esummary | none |
| 3 | Muscle2021 | J Appl Physiol 2021, PMC8279339 | PMC esummary | none |
| 4 | JSASS2012 | Trans JSASS Aerosp Technol Jpn 2012;10 | Crossref 10.2322/tastj.10.pp_5 | none |
| 5 | Macaulay2024 | npj Microgravity 2024 | Crossref 10.1038/s41526-024-00422-3 | none |
| 6 | Valle2023 | IEEE Aerospace Conf 2023 | Crossref 10.1109/AERO55745.2023.10115603 | none |
| 7 | Bekdash2020 | NASA NTRS 20205003610 (ARGOS) | NTRS | none |
| 8 | NTRS2014 | NASA NTRS 20140017135 | NTRS | none |
| 9 | NASASTD3001 | NASA-STD-3001 Vol.2 | NASA | none |
| 10 | MirDisturb | J Spacecr Rockets 2001 | Crossref 10.2514/2.3719 | none |
| 11 | EDLS1987 | Proc Hum Factors Soc 1987;31:725 | prior audit | none |
| 12 | RCOF2022 | Sensors 2022, PMC9581656 | PMC esummary | none |
| 13 | FrictionFalls2024 | Sci Rep 2024 | Crossref 10.1038/s41598-024-81361-7 | none |
| 14 | Winter | Winter DA, Wiley textbook | publisher | none |
| 15 | ISO9379 | ISO 9379:2005 | ISO | none |
| 16 | UFAS | UFAS/ADA A4.13.11 | standard | none |
| 17 | DoorForce2015 | Int J Ind Ergon 2015 | Crossref 10.1016/j.ergon.2015.05.010 | FIXED: DOI previously pointed to an unrelated Measurement paper; journal corrected |
| 18 | SitStand1999 | J Neurophysiol 1999, PMID 10601437 | PubMed esummary | FIXED: journal was "J Biomech", actual is J Neurophysiol; title corrected |
| 19 | SitStandKin | Med Eng Phys, PMC1929086 | PMC esummary | none |
| 20 | HandrailStair2011 | Gait Posture 2011, PMID 21816614 | PubMed esummary | none (title normalized) |
| 21 | HandrailLoad2018 | Appl Ergon 2018 | prior audit | none |
| 22 | Sobol2001 | Math Comput Simul 2001;55:271-280 | Crossref 10.1016/S0378-4754(00)00270-6 | FIXED: title completed, DOI added |
| 23 | Waclavicek2019 | IAC-19-E5.1-49818, 2019 | IAC proceedings | none |
| 24 | DSMHabitat2023 | Buildings 2023;13(5):1284 | Crossref 10.3390/buildings13051284 | FIXED: DOI added |
| 25 | Hall2016 | AIAA SPACE 2016 | Crossref 10.2514/6.2016-5388 | none |

Result: 25/25 references real; 4 records corrected (DoorForce2015, SitStand1999,
Sobol2001, DSMHabitat2023). Caveat: two repository-style records (MIT hdl,
NTRS) carry stable identifiers rather than DOIs — disclosed.

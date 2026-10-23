# Frozen 17-case convergence data

`CONVERGENCE_17_CASES.json` and `ERRORS_AND_RATES_17_CASES.csv` are byte-preserved copies of the accepted 2026-10-22 snapshot. No finite-element calculation or field reintegration was performed for this repository update.

- One reference problem: `fhd-continuous-polynomial-v1`, unit cube, ten physical parameters equal to one, time factor exp(t/2).
- All cases use T=2 and dt=1/(2K); grids are 5+5+4+3 for orders 1 to 4.
- Seven full norms per case; the six nonpressure norms use T=2. Pressure uses the mean-zero last-step weighted RK stages.
- Rates are log(E_coarse/E_fine)/log(K_fine/K_coarse), based on unrounded errors. A first-grid rate is absent, not zero. Absolute and relative pressure rates can differ because the reference norm changes with stage times.
- `curl_diagnostics.json` contains the 17 previously checked absolute sampled curl maxima, not rates or proved continuous infinity norms.
- `rk_tableaux.json` is copied from existing archived tableau files. All 17 source tableau hashes were verified during migration; each scheme has one common tableau.
- `FINAL_17_DATA_AUDIT.json` and `evidence/` retain the existing provenance and completion metadata. `provenance.json` binds the public files and unchanged manuscript/assets by SHA256.

The original JSON status string `partial_accepted_production_results` is historical and intentionally unchanged. Its counts are 17/17; the final audit and completion records establish completion. Some original RESULT files similarly retain `convergence_accepted=false` while independent admission and integrity records establish acceptance. No failed historical run has been relabelled successful.

Fields such as `case`, `base_table`, `original_time_case`, and admission paths identify files in the external research archive. They are not broken relative links to files promised in this repository. Third-order K8 preserves both the failed original monitor run and the independent endpoint recovery path.

Run `make check` from the repository root to verify hashes, all 119 CSV records, relative-error identities, 182 rates, RK stage times/weights, and all eight manuscript tables. This checks the published scalar data and provenance; it does not independently re-audit all external native checkpoint arrays.

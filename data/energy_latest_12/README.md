# Latest order-1/order-2 unforced energy data

Six cases: each order uses K=8, T=0.5, dt=1/16, 1/32, 1/64; 112 steps and 118 records including t=0. These are separate new runs with the latest accepted solver core and the same continuous energy initial fields/physical parameters/zero-input conditions as the accepted order-3/order-4 runs. Old data and all 17 convergence results are preserved.

See [scope, verification and lineage](../../docs/ENERGY_LATEST12.md). `curves.csv` stores endpoint energy, its ratio to that trajectory's initial energy, dt-integrated physical `dissipation`, `numerical_dissipation` (nonnegative backward-Euler increment term; zero for midpoint), source/boundary `load`, signed zero-input `gap=E_new-E_old+D+N`, its scaled `relative_gap`, and both cumulative dissipation terms. Step zero contains placeholders of zero for the per-step terms. The scaled denominator is E_new+E_old+D+abs(N). The gap deliberately does not subtract algebraic free-residual work.

`cases.json.gz` preserves full scalar configs and steps, initial checks, accounting and acceptance. `small_grid_gates.json` contains the accepted K2 checks. `driver_validation_history.json` retains the initial failed diagnostic attempt and exact repair scope. `raw_checkpoint_manifest.json` lists external native files with hashes and sizes. `source_manifest.json` and `solver_lineage.json` bind frozen solver and input-adapter files; full solver/field sources remain in the research archive.

`EXPORT.json` binds the exported files. `provenance.json` binds the manuscript extension and all protected earlier data. Absolute archive roots in public metadata use <FHD_ARCHIVE>. Run `make energy-figures` and `make check`; neither command runs FEM/MPI or changes server data.

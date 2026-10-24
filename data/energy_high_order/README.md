# Six supplemental energy trajectories

Orders 3 and 4 each use K=8, T=0.5 and dt=1/16, 1/32, 1/64. The six completed cases contain 112 steps and 118 CSV records including t=0. All final jobs have COMPLETED/0:0 status and PASS acceptance. This directory is separate from the frozen 17-case convergence study.

See [experiment, acceptance and recovery details](../../docs/ENERGY_HIGH_ORDER.md). The continuous initial fields are those in the paper's energy subsection; body/external sources are zero, essential traces homogeneous, and physical parameters all one.

`curves.csv` columns:

| Column | Meaning |
|---|---|
| order, K, dt, dt_denominator | Temporal order, spatial mesh parameter, step size and its denominator |
| step, time | Stored endpoint index and time, including initial step 0 |
| energy | Discrete energy E at this endpoint |
| normalized_energy | E divided by this trajectory's own initial energy |
| dissipation | dt-weighted Gauss-stage dissipation integral for this step; zero at step 0 |
| load | Step-integrated source work; zero for all six runs |
| gap | Signed E(n+1)-E(n)+dissipation-load |
| relative_gap | Absolute gap divided by E(n+1)+E(n)+dissipation+absolute(load) |
| cumulative_dissipation | Sum of the step-integrated dissipation through this endpoint |

The old energy CSV uses a different dissipation-column convention. Use the respective energy/normalized-energy columns for combined plotting; do not mix the dissipation columns.

`cases.json.gz` is a lossless JSON archive of configs, initial projections, per-step scalar diagnostics, acceptance, final accounting and recovery evidence. `energy_summary.json` preserves the full-precision acceptance summaries. `small_grid_gates.json` and `recovery_protocol.json` retain independent small-grid/oracle/quadrature, guard-control and strict-recovery checks, including the failed initial fourth-order replay attempt.

`raw_checkpoint_manifest.json` contains relative paths, sizes and SHA256 values for 7,770 original checkpoint files in the accepted trajectories and validation runs (8,742,705,728 bytes); the native vectors are retained on the compute server and are not included in Git. The manifest includes each accepted formal endpoint from t=0 through T=0.5 and every MPI rank. `solver_source_manifest.json` identifies frozen private solver sources; it does not distribute or provide an executable solver.

`EXPORT.json` hashes the ten exported data/evidence files. `provenance.json` additionally binds the original and updated manuscript hashes and the unchanged text outside the energy subsection. Public metadata replaces the absolute research-archive root with `<FHD_ARCHIVE>`; source hashes refer to the raw originals. Failed/interrupted original jobs are not relabeled as completed: accepted replacement jobs and exact-restoration evidence are explicitly identified.

Run `make energy-figures` for CSV-only plotting and `make check` for standard-library numerical/provenance checks. These commands do not run a PDE solver or alter server data.

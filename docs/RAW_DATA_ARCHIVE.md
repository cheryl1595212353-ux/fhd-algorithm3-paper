# External native data and traceability

This is a paper collaboration repository. Full solver sources, native finite-element vectors, per-rank checkpoints, failed runs, diagnostic matrices, runtime environments and compilation caches remain in the external FHD research archive. They were not deleted, compressed, moved or recomputed during this migration.

The source-relative paths and SHA256 values in `data/convergence_17/FINAL_17_DATA_AUDIT.json`, the frozen JSON/CSV and the completion records identify the archived inputs. These names intentionally do not depend on a collaborator's absolute home directory. Obtaining the raw archive requires access from the project maintainer; no public raw-data download is claimed here.

The final second-order K32 run is 47092087: 128 steps from t=0, COMPLETED/0:0, 4,603 archived files and 4,128 checked NPZ checkpoint files. Third-order K16 is 46959367. Their existing completion records are included in `data/convergence_17/evidence/`.

Preserved failures include the K32 59-step monitor interruption, the later 110-step disk-full run, the strict coefficient restart failure and the original third-order K8 monitor failure. The accepted K32 is a full rerun, not a relabelled partial run. The third-order K8 value retains its independently accepted endpoint-recovery provenance.

Reproduction levels:

1. `make check`: scalar data arithmetic, source hashes, published table cells and figure provenance.
2. `make tables`, `make figures`, `make preview`: table fragments, plots and paper PDFs from existing data.
3. Repeating finite-element solves or reintegrating native fields: requires the separate solver/data/environment archive and an appropriate compute allocation; not implemented or executed by this paper repository.

## Supplemental energy archive

The six new order-3/order-4 energy cases are separate from the frozen 17 convergence cases. `data/energy_high_order/raw_checkpoint_manifest.json` lists every accepted formal-run checkpoint from t=0 through T=0.5, plus the validation checkpoints, with file sizes and SHA256 hashes. Full fields remain under the archive-relative `energy_decay_34_20261023` and `energy_decay_4_border_20261023` experiment roots. Public metadata replaces the absolute archive root with `<FHD_ARCHIVE>`.

The complete scalar records, source hashes, Slurm accounting and interruption/recovery evidence are included; complete solver source is not distributed here. Four original formal runs failed when the old monitor timed out, and their failed status and raw files remain preserved. Accepted replacements use validated native checkpoint restoration and verify the copied prefix and original files. The failed initial fourth-order recovery trial remains documented separately from the successful qualified replay and final production results. See [energy provenance](ENERGY_HIGH_ORDER.md) for the exact jobs and acceptance boundaries.

The subsequent latest order-1/order-2 supplement is in the separate archive-relative `energy_decay_12_20261024` root. Public scalar data, per-step/checkpoint hashes, frozen-core lineage and the preserved initial diagnostic failure are recorded in `data/energy_latest_12/`. No previous energy or convergence run is overwritten; see [latest energy scope](ENERGY_LATEST12.md).

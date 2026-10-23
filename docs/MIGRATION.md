# Repository refresh: 2026-10-23

The previous main commit is `92a574ed028bdeb5f3fdac866a413cf50b10ee1b` (2026-09-28). This update adopts the approved 2026-10-22 manuscript and frozen 17-case results. All Git history is preserved. The old convergence files and experimental TeX fragments are moved into `legacy/2026-09-28/`; the complete older repository remains available by its commit ID. An additional archive ref is part of the publication plan.

## Changes

- Replace the old manuscript with the complete approved higher-order TeX, byte for byte; do not alter its mathematics or scientific conclusions.
- Publish all 17 cases (5+5+4+3), seven norms, exact JSON/CSV, sampled curl values, archived RK tableaus and existing completion/provenance evidence.
- Preserve 32 energy/application data and figure files by SHA256; preserve their original plotting helpers.
- Regenerate absolute/relative convergence plots from the frozen data. Fix the legend/notes spacing in the display only.
- Add standard-library validation, eight-table fragment generation, a portable compiler wrapper, and full/excerpt PDF export.
- Use the full manuscript as the only active TeX source. The numerical preview is an exact page excerpt (pages 19-30), not a separate, potentially stale experimental text.
- Document the joint h/dt study, nonhomogeneous extension, actual RK-stage pressure, historical acceptance labels and external raw archive.

## Completed local validation

- Frozen JSON and CSV SHA256 match the accepted snapshot.
- 17 configurations, 119 CSV records, seven norms, 182 absolute/relative rates, pressure weights/times and all eight TeX tables checked.
- 238 printed error cells, 182 printed Rate values and 17 sampled curl values match the frozen data.
- Current main.tex is byte-identical to the approved source; all 32 PDF pages have identical extracted text and identical 90-DPI raster pixels to the approved 32-page PDF.
- `make check tables preview` completed with Tectonic 0.17.0. The full PDF has 32 pages; the numerical/appendix excerpt has 12 pages.
- Both convergence figures were regenerated with Matplotlib 3.10.9 and visually reviewed. All 32 manuscript pages were reviewed in contact sheets; representative main and appendix tables were inspected at full page size.

Detailed scalar checks are in `DATA_VALIDATION.json`; final visual/build evidence is in `VALIDATION.json`.

## Preserved warnings

The approved source already contains duplicate bibliography keys `LiuYin2022`, `ShinLeeLee2017`, and `ShinLee2020`, plus approximately 4.53pt and 0.98pt Overfull hbox warnings in existing theory/flow text. These remain recorded; there are no new undefined references or missing glyphs. The reviewed pages are not clipped. Fixing the bibliography or mathematical text is outside this repository organization update.

No FEM/MPI solve, field reintegration, cluster submission, deletion, compression or movement of server raw data was performed. Only existing scalar data were checked and used to generate publication artifacts. No PR merge is authorized in this task.

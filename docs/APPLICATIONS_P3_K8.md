# Third-order K8 application figures

These six figures use user-selected saved states: **channel t=0.640 (step 128)** and **backward-facing step t=0.585 (step 117)**. The complete trajectories still end at T=2: K=8, third-order time and spatial discretization, dt=0.005, 400 time steps, 404 coupled solves, and 401 saved states per case. Production jobs are 47867091 (channel) and 47867092 (step); both completed and passed the original numerical and native-data checks.

The presentation follows Dong et al., *Journal of Computational Physics* 549 (2026), 114617, DOI [10.1016/j.jcp.2025.114617](https://doi.org/10.1016/j.jcp.2025.114617), Figs. 13-15 and 19-21: white wireframe geometry, paired panels, blue-cream-red magnitude colors and horizontal color bars. Our left panels are **instantaneous vector glyphs**, not integrated streamlines or particle paths. The fields are velocity u, magnetization m and particle angular velocity omega (not fluid vorticity).

The right panels show the norm of all three vector components on z=0.1 for the channel and y=0.1 for the step. The solid step is masked. Each pair uses a shared linear color range fixed across the saved trajectory. Arrow length is linear in magnitude; center-section colors are interpolated only for display. No temporal interpolation, RT vertex averaging, polynomial recovery or artificial amplitude rescaling is used.

The project retains its own magnetic diffusion, forcing and boundary conditions. The visual reference does not imply reproduction of Dong's physical model. These snapshots do not independently establish convergence, mesh independence, a steady state or a periodic limiting state.

The plots reuse the accepted double-precision FE samples from export jobs 47925166 (center sections) and 47928194 (volume glyphs); the selected-time render reuses the same accepted samples without any PDE solve. Its job ID and selected steps are recorded in the figure manifest. Velocity and magnetization retain 300 volume glyph sites for the channel and 264 for the step. Angular velocity instead uses 192 native FE evaluations on four spaced transverse sections; the right-panel section lattices remain 81 x 17 and 81 x 33 with the solid mask, respectively. Sample maxima are not exact maxima over the entire FE domain. Figure/source hashes are recorded in `figures/applications_p3_K8/RENDER_MANIFEST.json`.

This GitHub update publishes the figures, updated manuscript/PDFs, and concise figure validation. Full selected-time samples, rendering scripts and detailed production audits remain in the verified local and Extreme Pro archive. They are not added to this public repository by this update. Existing published convergence and energy data remain unchanged.

Removing the two explicitly marked manuscript additions restores the prior merged main.tex byte for byte. Local standard-library checks preserve all earlier convergence/energy validations and additionally check every new PDF/PNG hash:

```bash
make check tables
```

The new main.pdf has 37 pages: convergence curves on page 24, channel figures on page 31, and step figures on page 32. PR #4 remains separate and unmerged.

## Spaced angular-velocity groups

The angular-velocity glyphs are sampled at x=0.125, 0.375, 0.625, 0.875. Each section uses two concentric geometric seed curves (radial fractions 0.55 and 1), with 24 azimuthal sites per curve. The outer semiaxes are 0.08 in y and z, centered at y=z=0.1; the step's upstream section uses center z=0.15 and vertical semiaxis 0.035 to stay inside the fluid. These curves select sample locations, not vector directions or reconstructed trajectories. Every vector is evaluated directly from the native finite-element angular-velocity field. The display therefore does not imply isolated physical vortices or zero angular velocity in the spaces between sections.

Read-only sampling job 48064992 checked all 52 frozen source files, 32 native frame shards per case, exact FE layout and ghosts. Values at the existing 300/264 control sites agree exactly with the accepted samples. No PDE steps were advanced. Only the two omega figures changed: their cameras, full-vector-norm color limits, selected times and right-panel pixels are identical to the previous selected-time version. The final display render is job 48066714. The linear omega arrow display factor was shortened from 0.075 to 0.030, and the shaft/head sizes increased slightly so directions remain legible at manuscript size. The other four application figures are byte-identical. Detailed samples and scripts remain in the external-disk reproduction package.

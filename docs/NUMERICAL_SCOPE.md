# Numerical scope and interpretation

The latest table uses one continuous polynomial manufactured solution for all four methods. It is a joint h/dt refinement study at T=2, dt=1/(2K), with grids 2/4/8/16/32 for orders 1 and 2, 2/4/8/16 for order 3, and 2/4/8 for order 4.

The Rosensweig volume equations, extrapolated Gauss framework, finite-element families and block-elimination structure are retained. The manufactured solution, nonhomogeneous boundary lifting, divergence-constrained magnetization initialization, divergence-preserving velocity energy projection and auxiliary endpoint recovery are substantive implementation choices described in the manuscript. The good rates for this problem do not establish that every defect of the original homogeneous-boundary problem has been repaired.

## What the norms mean

The reported u-H1, omega-H1, m-H(div), H-H(curl), k-L2 and phi-H1 quantities are terminal full norms. Pressure is a mean-zero, positively weighted L2 norm over the actual RK stages of the final step. It is neither a general endpoint pressure error nor a time-integrated pressure norm. For backward Euler alone, the one stage occurs at T.

The first-order finest pressure rate is 1.757620264. The fourth-order relative pressure rate is 4.527015520, while its absolute rate is 4.504825573 (the exact stored float remains authoritative). The roughly 0.02219 difference is caused by the stage reference norm. These observations are not rounded into nominal integer orders and are not a general superconvergence claim. The remaining departure from the nominal rate has not been isolated to a unique cause.

## Limits of the evidence

- The main 17-case table alone does not separately prove time and space orders.
- Nonzero boundary work in the extended energy balance cannot replace the homogeneous-boundary dissipation theorem.
- H=grad(phi) and a small sampled curl diagnostic do not establish an independent zero-error Maxwell divergence constraint at every time layer.
- Fourth-order K16 results are not present; the fourth-order series stops at K8 after the recorded resource assessment.
- The old energy and channel/step experiments retain their original parameters and interpretation. No new K12 step-flow completion or final grid-independence claim is added.
- The earlier review raised the external-field sigma sign and missing gradient in the printed potential mass term of the 1016 paper. This repository migration does not resolve those author-level theoretical questions or change the approved equations.

The 2026-10-23 migration preserved the approved 2026-10-22 revised TeX byte for byte. The subsequent energy update changes only the energy subsection; the prefix and suffix outside that subsection, all 17 convergence datasets/tables, and the original energy/application assets remain unchanged and are checked by hashes.

Six additional homogeneous-boundary, unforced third-/fourth-order energy trajectories at K=8, T=0.5 and dt=1/16, 1/32, 1/64 now supplement the original first-/second-order curves. All six reach the endpoint and pass full-residual, energy-balance, checkpoint and recovery acceptance. The panels share axes and use each curve's own initial discrete energy. Different orders retain their corresponding spatial finite-element spaces, so these curves do not isolate temporal accuracy. See [energy scope and provenance](ENERGY_HIGH_ORDER.md).

The latest order-1/order-2 solver now supplies six new unforced energy trajectories using the same continuous energy initial fields and homogeneous conditions as the accepted order-3/order-4 cases. All old scalar datasets and figures remain archived. Backward-Euler numerical dissipation is included explicitly in the energy balance. See [latest energy update](ENERGY_LATEST12.md).

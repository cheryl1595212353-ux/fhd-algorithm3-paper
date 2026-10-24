"""Validate published data, tables and preserved assets without a PDE run."""
import argparse
import json
from pathlib import Path
from convergence_data import ROOT, DATA, sha256, load_checked
from generate_tables import rendered_tables, check_manuscript


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    _, _, counts = load_checked()
    tables, _ = rendered_tables()
    check_manuscript(tables)
    provenance = json.loads((DATA / "provenance.json").read_text())
    high_order_energy = None
    if (ROOT / "data/energy_high_order/provenance.json").exists():
        from validate_high_order_energy import validate
        high_order_energy = validate()
    elif sha256(ROOT / "main.tex") != provenance["approved_manuscript_sha256"]:
        raise ValueError("main.tex differs from the approved manuscript snapshot")
    for rel, digest in provenance["preserved_energy_and_application_files_sha256"].items():
        if sha256(ROOT / rel) != digest:
            raise ValueError(f"Preserved energy/application asset changed: {rel}")
    plot_proofs = []
    for kind in ("absolute", "relative"):
        stem = ROOT / "figures/convergence_17" / (kind + "_errors")
        proof = stem.with_suffix(".source.json")
        if not proof.exists():
            raise ValueError(f"Missing figure provenance: {proof.name}; run make figures")
        if proof.exists():
            p = json.loads(proof.read_text())
            if p["input_sha256"] != provenance["frozen_data_sha256"]:
                raise ValueError("Figure input hash differs")
            if p["script_sha256"] != sha256(ROOT / "scripts/plot_convergence.py"):
                raise ValueError("Figure script has changed since rendering")
            for suffix, digest in p["outputs_sha256"].items():
                if sha256(stem.with_suffix(suffix)) != digest:
                    raise ValueError("Rendered figure changed")
            plot_proofs.append(kind)
    result = {"status": "passed", **counts, "tables": len(tables),
              "printed_error_cells": 238, "printed_rate_cells": 182,
              "approved_manuscript_byte_identical": sha256(ROOT / "main.tex") == provenance["approved_manuscript_sha256"],
              "supplemental_high_order_energy": high_order_energy,
              "preserved_energy_application_assets": len(provenance["preserved_energy_and_application_files_sha256"]),
              "figure_provenance_checked": plot_proofs,
              "scope": "Existing data arithmetic, CSV, TeX tables, hashes and plot provenance. No FEM/MPI, field reintegration, job submission or remote data changes."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

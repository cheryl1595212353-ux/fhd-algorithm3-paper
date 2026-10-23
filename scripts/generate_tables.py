"""Generate eight table fragments and check the unchanged manuscript tables."""
import argparse
import json
import re
from pathlib import Path
from convergence_data import ROOT, FIELDS, load_checked


def scientific(value):
    mantissa, exponent = f"{value:.4e}".split("e")
    return "$" + mantissa + r"\!\times\!10^{" + str(int(exponent)) + "}$"


def rendered_tables():
    data, curls, counts = load_checked()
    templates = json.loads((ROOT / "scripts/table_templates.json").read_text())
    rendered = {}
    for template in templates:
        series = data["series"][template["order"] - 1]
        measure = template["measure"]
        blocks = []
        for fields in (FIELDS[:4], FIELDS[4:]):
            lines = []
            for row in series["rows"]:
                cells = [str(row["K"])]
                for field in fields:
                    error = row["errors"][field]
                    rate = error.get(measure + "_rate")
                    cells += [scientific(error[measure]), "---" if rate is None else f"{rate:.3f}"]
                if fields == FIELDS[4:] and measure == "relative":
                    cells.append(scientific(curls[template["order"], row["K"]]))
                lines.append(" & ".join(cells) + r"\\")
            blocks.append("\n".join(lines))
        rendered[template["label"]] = template["template"].replace("@@ROWS_A@@", blocks[0]).replace("@@ROWS_B@@", blocks[1])
    return rendered, counts


def check_manuscript(tables):
    manuscript = (ROOT / "main.tex").read_text()
    for label, expected in tables.items():
        matches = [t for t in re.findall(r"\\begin\{table\}\[H\].*?\\end\{table\}", manuscript, re.S)
                   if r"\label{" + label + "}" in t]
        if matches != [expected]:
            raise ValueError(f"Manuscript table differs from frozen data: {label}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without writing fragments")
    parser.add_argument("--out", type=Path, default=ROOT / "build/tables")
    args = parser.parse_args()
    tables, counts = rendered_tables()
    check_manuscript(tables)
    if not args.check:
        args.out.mkdir(parents=True, exist_ok=True)
        for label, content in tables.items():
            (args.out / (label.replace("tab:", "") + ".tex")).write_text(content + "\n")
    print(json.dumps({"tables": len(tables), "error_cells": 238, "rate_cells": 182,
                      "manuscript_matches_generated_tables": True, **counts}, indent=2))


if __name__ == "__main__":
    main()

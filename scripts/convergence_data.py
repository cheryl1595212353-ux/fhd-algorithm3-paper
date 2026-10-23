"""Read and check frozen paper data; never import a numerical solver."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/convergence_17"
FIELDS = ("u_H1", "p_stage_weighted_L2", "omega_H1", "m_Hdiv", "H_Hcurl", "k_L2", "phi_H1")
GRIDS = {1: [2, 4, 8, 16, 32], 2: [2, 4, 8, 16, 32], 3: [2, 4, 8, 16], 4: [2, 4, 8]}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def close(actual, expected, context):
    if not math.isclose(actual, expected, rel_tol=2e-12, abs_tol=1e-14):
        raise ValueError(f"{context}: {actual!r} != {expected!r}")


def load_checked():
    data = json.loads((DATA / "CONVERGENCE_17_CASES.json").read_text())
    provenance = json.loads((DATA / "provenance.json").read_text())
    for name, key in [("CONVERGENCE_17_CASES.json", "frozen_data_sha256"),
                      ("ERRORS_AND_RATES_17_CASES.csv", "frozen_csv_sha256"),
                      ("curl_diagnostics.json", "curl_diagnostics_sha256"),
                      ("rk_tableaux.json", "rk_tableaux_sha256")]:
        if sha256(DATA / name) != provenance[key]:
            raise ValueError(f"Frozen input changed: {name}")
    if data["verified_cases"] != 17 or data["target_cases"] != 17:
        raise ValueError("Expected 17 accepted cases")
    if [s["order"] for s in data["series"]] != [1, 2, 3, 4]:
        raise ValueError("Unexpected scheme order list")
    index = {}
    tableaux = json.loads((DATA / "rk_tableaux.json").read_text())
    rate_count = 0
    for series in data["series"]:
        order = series["order"]
        if [r["K"] for r in series["rows"]] != GRIDS[order]:
            raise ValueError(f"Unexpected grids for order {order}")
        previous = None
        for row in series["rows"]:
            K = row["K"]
            if row["order"] != order or row["T"] != 2 or row["dt"] != 1 / (2 * K):
                raise ValueError(f"Inconsistent configuration: order {order}, K{K}")
            if set(row["errors"]) != set(FIELDS):
                raise ValueError("Unexpected error fields")
            for field in FIELDS:
                e = row["errors"][field]
                for kind in ("absolute", "relative", "reference_norm"):
                    if not math.isfinite(e[kind]) or e[kind] <= 0:
                        raise ValueError(f"Invalid {field}/{kind}")
                close(e["relative"], e["absolute"] / e["reference_norm"], field)
                for kind in ("absolute", "relative"):
                    rate = e.get(kind + "_rate")
                    if previous is None:
                        if rate is not None:
                            raise ValueError("First grid must not have a rate")
                    else:
                        expected = math.log(previous["errors"][field][kind] / e[kind]) / math.log(K / previous["K"])
                        close(rate, expected, f"{order}/{K}/{field}/{kind}_rate")
                        rate_count += 1
                index[order, K, field] = (row, e)
            pressure = row["errors"]["p_stage_weighted_L2"]
            tableau = tableaux[str(order)]["tableau"]
            if "tableau" in row and row["tableau"] != tableau:
                raise ValueError("Embedded and archived RK tableaus differ")
            stages, weights, nodes = pressure["stages"], tableau["b"], tableau["c"]
            times = row.get("pressure_stage_times", [s["time"] for s in stages])
            if not (len(stages) == len(weights) == len(nodes) == len(times)) or any(b <= 0 for b in weights):
                raise ValueError("Invalid pressure quadrature")
            close(sum(weights), 1.0, "RK weights")
            for stage, c, time in zip(stages, nodes, times):
                close(stage["time"], 2 - row["dt"] + c * row["dt"], "stage time")
                close(time, stage["time"], "stored stage time")
            for kind in ("absolute", "reference_norm"):
                close(pressure[kind], math.sqrt(sum(b * s[kind] ** 2 for b, s in zip(weights, stages))), "weighted pressure " + kind)
            previous = row
    with (DATA / "ERRORS_AND_RATES_17_CASES.csv").open(newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    seen = set()
    for record in csv_rows:
        key = int(record["order"]), int(record["K"]), record["norm"]
        if key in seen or key not in index:
            raise ValueError(f"Duplicate or unknown CSV row: {key}")
        seen.add(key)
        row, error = index[key]
        for name in ("absolute", "relative", "reference_norm", "absolute_rate", "relative_rate"):
            expected = error.get(name)
            if expected is None:
                if record[name] != "":
                    raise ValueError("CSV first-row rate must be empty")
            else:
                close(float(record[name]), expected, f"CSV {key}/{name}")
        if record["case"] != row["case"] or record["result_sha256"] != row["result_sha256"]:
            raise ValueError("CSV provenance differs from JSON")
        close(float(record["T"]), row["T"], "CSV T")
        close(float(record["dt"]), row["dt"], "CSV dt")
    if len(seen) != 119 or set(index) != seen:
        raise ValueError("Expected exactly 119 case/norm records")
    curls = json.loads((DATA / "curl_diagnostics.json").read_text())["rows"]
    curl_index = {(r["order"], r["K"]): r["value"] for r in curls}
    if len(curls) != 17 or set(curl_index) != {(o, k) for o, k, _ in index}:
        raise ValueError("Invalid curl diagnostics coverage")
    if any(not math.isfinite(v) or v < 0 for v in curl_index.values()):
        raise ValueError("Invalid curl diagnostic")
    return data, curl_index, {"cases": 17, "error_records": 119,
                              "absolute_and_relative_rates": rate_count,
                              "csv_rows": len(csv_rows), "curl_diagnostics": 17}

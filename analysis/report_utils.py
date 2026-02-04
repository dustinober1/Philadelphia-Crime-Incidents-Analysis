import json
from typing import Any


def _map_test_item(item: dict[str, Any]) -> dict[str, Any]:
    # Try common key variants and normalize to canonical keys
    out = {}
    # name
    out["test_name"] = (
        item.get("test_name") or item.get("name") or item.get("test") or item.get("testName")
    )
    # statistic value
    out["statistic"] = (
        item.get("statistic")
        or item.get("stat")
        or item.get("stat_value")
        or item.get("statistic_value")
    )
    # p-value
    out["p_value"] = (
        item.get("p_value") or item.get("pvalue") or item.get("p") or item.get("pValue")
    )
    # effect size
    out["effect_size"] = (
        item.get("effect_size") or item.get("effect") or item.get("d") or item.get("cohen_d")
    )
    # conclusion / interpretation
    out["conclusion"] = item.get("conclusion") or item.get("interpretation") or item.get("result")
    # confidence interval
    ci = item.get("ci") or item.get("ci_lower") or None
    if isinstance(ci, (list, tuple)) and len(ci) >= 2:
        out["ci_lower"], out["ci_upper"] = ci[0], ci[1]
    else:
        out["ci_lower"] = item.get("ci_lower") or item.get("ciLower") or None
        out["ci_upper"] = item.get("ci_upper") or item.get("ciUpper") or None

    # Ensure minimal keys
    return out


def normalize_heat_crime_json(in_path: str, out_path: str) -> None:
    """Read an existing heat-crime statistical tests JSON and write a normalized schema.

    The canonical schema is:
    {"tests": [ {"test_name":..., "statistic":..., "p_value":..., "effect_size":..., "conclusion":..., "ci_lower":..., "ci_upper":...}, ... ] }
    """
    with open(in_path, encoding="utf-8") as f:
        data = json.load(f)

    tests: list[dict[str, Any]] = []

    # If data is a dict with top-level "tests" or similar
    if isinstance(data, dict):
        # If it already matches schema
        if "tests" in data and isinstance(data["tests"], list):
            source_tests = data["tests"]
        else:
            # attempt to find list-like values
            # common keys to check
            for key in ("results", "tests", "statistical_tests", "analysis"):
                if key in data and isinstance(data[key], list):
                    source_tests = data[key]
                    break
            else:
                # If the dict itself encodes a single test
                source_tests = [data]
    elif isinstance(data, list):
        source_tests = data
    else:
        source_tests = [{"raw": data}]

    for item in source_tests:
        if not isinstance(item, dict):
            # wrap non-dict items
            tests.append({"test_name": str(item)})
            continue
        mapped = _map_test_item(item)
        # fallback: if test_name missing, try to infer from keys
        if not mapped.get("test_name"):
            # look for first string-valued key
            for k, v in item.items():
                if isinstance(v, str) and len(str(v)) < 40:
                    mapped["test_name"] = mapped.get("test_name") or f"test_{k}"
                    break
        tests.append(mapped)

    out = {"tests": tests}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def load_normalized(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m analysis.report_utils <in.json> <out.json>")
        sys.exit(2)
    normalize_heat_crime_json(sys.argv[1], sys.argv[2])

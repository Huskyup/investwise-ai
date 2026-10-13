"""Compare unchanged ML in separate app and D5 processes on the existing 11 replies.

This is a numerical/software parity check, not a new semantic evaluation. It
never loads Qwen or reads credentials, test.csv or supplementary training data.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = ROOT / "docs/d5-semantic-repair/evidence/after/inputs.json"
FIELDS = ("candidate_option_id", "ordinary_bucket", "model_uncertain",
          "semantic_undecided", "intent_set", "option_set",
          "intent_probabilities", "option_probabilities")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def child(route):
    if route == "main":
        sys.path.insert(0, str(ROOT))
        from ai.question_spec import BusinessSpec
        from ai.all_question_ml import build_all_question_ml_resolver
        spec = BusinessSpec.load(ROOT / "config/business-decision-spec.json")
        resolver = build_all_question_ml_resolver(spec, ROOT / "data/nlp/all_questions")
        implementation = ROOT / "ai/all_question_ml.py"
    else:
        sys.path.insert(0, str(HERE))
        from local_session import load_baseline
        from ai.question_spec import BusinessSpec
        spec = BusinessSpec.load(HERE / "runtime/config/business-decision-spec.json")
        resolver, _ = load_baseline(spec)
        implementation = HERE / "baseline_ml.py"
    rows = json.loads(INPUTS.read_text())["rows"]
    if [row["id"] for row in rows] != [f"D5-STD-{number:02d}" for number in range(1, 12)]:
        raise ValueError("Only the original eleven ordered examples are allowed")
    output = []
    for row in rows:
        resolution = resolver.resolve("D5", row["text"])
        result = {field: getattr(resolution, field) for field in FIELDS}
        result["intent_set"] = sorted(result["intent_set"])
        result["option_set"] = sorted(result["option_set"])
        result.update(id=row["id"], input=row["text"])
        output.append(result)
    from ai import conformal, question_spec, text_classifier
    print(json.dumps({"route": route, "python": sys.version,
        "executable": sys.executable, "versions": {package: version(package)
            for package in ("numpy", "scikit-learn", "scipy")},
        "implementation_sha256": sha(implementation),
        "dependency_sha256": {name: sha(Path(module.__file__)) for name, module in (
            ("conformal", conformal), ("text_classifier", text_classifier),
            ("question_spec", question_spec))},
        "main_spec_sha256": sha(ROOT / "config/business-decision-spec.json"),
        "packaged_spec_sha256": sha(HERE / "runtime/config/business-decision-spec.json"),
        "train_sha256": sha(ROOT / "data/nlp/all_questions/train.csv"),
        "calibration_sha256": sha(ROOT / "data/nlp/all_questions/calibration.csv"),
        "inputs_sha256": sha(INPUTS), "resolver_source_hash": resolver.source_hash,
        "records": output}, ensure_ascii=False, allow_nan=False))


def write_once(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--local-python", type=Path,
                        default=Path.home() / ".venvs/investwise-d5/bin/python")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--child", choices=("main", "snapshot"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        child(args.child)
        return 0
    if args.output is None:
        parser.error("--output is required")
    output_dir = args.output.expanduser().absolute()
    if output_dir.is_symlink() or output_dir.resolve().is_relative_to(ROOT):
        parser.error("--output must be outside the repository")
    output_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    results = {}
    for route, python in (("main", args.main_python), ("snapshot", args.local_python)):
        result = subprocess.run([str(python), "-B", str(Path(__file__).resolve()),
                                 "--child", route], cwd=ROOT, capture_output=True,
                                 text=True, timeout=120, check=True)
        results[route] = json.loads(result.stdout)
        write_once(output_dir / f"{route}.json", results[route])
    differences = []
    max_probability_difference = 0.0
    for left, right in zip(results["main"]["records"], results["snapshot"]["records"], strict=True):
        if left["id"] != right["id"] or left["input"] != right["input"]:
            raise ValueError("The two processes did not receive identical inputs")
        for field in FIELDS:
            if left[field] != right[field]:
                differences.append({"id": left["id"], "field": field,
                                    "main": left[field], "snapshot": right[field]})
            if field.endswith("probabilities"):
                keys = set(left[field]) | set(right[field])
                for key in keys:
                    max_probability_difference = max(max_probability_difference,
                        abs(left[field].get(key, 0.0) - right[field].get(key, 0.0)))
    identities_match = all(results["main"][field] == results["snapshot"][field]
        for field in ("implementation_sha256", "main_spec_sha256", "train_sha256",
                      "calibration_sha256", "inputs_sha256", "resolver_source_hash"))
    summary = {"check": "unchanged_ml_separate_process_parity", "cases": 11,
        "fields_compared": list(FIELDS), "exact_equality": not differences,
        "baseline_identities_equal": identities_match,
        "max_probability_difference": max_probability_difference,
        "passed": not differences and identities_match,
        "differences": differences, "local_qwen_calls": 0,
        "new_semantic_inputs": 0, "retry": False,
        "limitation": "Parity verifies reuse of the baseline, not semantic correctness."}
    write_once(output_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

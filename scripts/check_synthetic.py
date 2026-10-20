"""CI gate: every outcome the pack produces must be labeled synthetic.

Exits non-zero (failing the pipeline) if any scenario returns an outcome
without synthetic=True and the synthetic label.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.baseball_pack import SYNTHETIC_LABEL, evaluate  # noqa: E402

scenarios = json.loads(pathlib.Path("fixtures/scenarios.json").read_text())
failures = 0
for sc in scenarios:
    name = sc.pop("name")
    out = evaluate(sc)
    ok = out.get("synthetic") is True and out.get("label") == SYNTHETIC_LABEL
    print(f"{'PASS' if ok else 'FAIL'}  {name}  ->  {out.get('recommendation', out.get('status'))}")
    failures += not ok

if failures:
    print(f"\n{failures} outcome(s) missing the synthetic label. Failing the build.")
    sys.exit(1)
print(f"\nAll {len(scenarios)} outcomes are labeled synthetic.")

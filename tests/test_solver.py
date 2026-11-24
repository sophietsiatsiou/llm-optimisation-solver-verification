import json
from pathlib import Path

from optverify.evaluate import load_cases
from optverify.schema import Formulation
from optverify.solver import solve_formulation

DATA = Path(__file__).resolve().parents[1] / "data" / "benchmark.json"


def test_reference_cases_are_feasible():
    for case in load_cases(DATA):
        result = solve_formulation(Formulation.model_validate(case["reference"]))
        assert result["feasible"]
        assert result["status"] == "OPTIMAL"


def test_product_mix_objective():
    case = next(c for c in load_cases(DATA) if c["id"] == "product_mix")
    result = solve_formulation(Formulation.model_validate(case["reference"]))
    assert abs(result["objective"] - 22) < 1e-6

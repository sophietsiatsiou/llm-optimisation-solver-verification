"""Benchmark formulation generation and solver-based verification."""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from optverify.schema import Formulation
from optverify.solver import solve_formulation


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, list):
        raise ValueError("benchmark file must contain a JSON list")
    return data


def canonical(formulation: Formulation) -> dict[str, Any]:
    """Canonicalized representation for exact reference comparison."""
    obj = formulation.model_dump()
    obj["variables"] = sorted(obj["variables"], key=lambda v: v["name"])
    obj["objective"]["coefficients"] = dict(sorted(obj["objective"]["coefficients"].items()))
    obj["constraints"] = sorted(
        [
            {
                **constraint,
                "coefficients": dict(sorted(constraint["coefficients"].items())),
            }
            for constraint in obj["constraints"]
        ],
        key=lambda c: c["name"],
    )
    return obj


def mathematical_signature(formulation: Formulation) -> tuple:
    """Create a name-independent signature of a small linear formulation.

    Variable names, constraint names and ordering are ignored.
    Objective coefficients, bounds and constraint mathematics are preserved.
    """
    variable_names = [v.name for v in formulation.variables]
    variables_by_name = {v.name: v for v in formulation.variables}

    signatures = []

    # Try every possible variable ordering. This allows different variable
    # names and variable ordering to be compared consistently.
    for ordered_names in permutations(variable_names):
        bounds = tuple(
            (
                variables_by_name[name].lower,
                variables_by_name[name].upper,
            )
            for name in ordered_names
        )

        objective = tuple(
            round(formulation.objective.coefficients.get(name, 0.0), 10)
            for name in ordered_names
        )

        constraints = []
        for constraint in formulation.constraints:
            coefficients = tuple(
                round(constraint.coefficients.get(name, 0.0), 10)
                for name in ordered_names
            )
            constraints.append(
                (
                    constraint.sense,
                    round(constraint.rhs, 10),
                    coefficients,
                )
            )

        signature = (
            formulation.sense,
            bounds,
            objective,
            tuple(sorted(constraints)),
        )
        signatures.append(signature)

    # repr provides a consistent ordering even when some bounds are None.
    return min(signatures, key=repr)


def evaluate_case(case: dict[str, Any], raw_output: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "case_id": case["id"],
        "valid_json": False,
        "generated_formulation": None,
        "valid_schema": False,
        "solver_status": None,
        "feasible": False,
        "objective": None,
        "objective_abs_error": None,
        "objective_relative_error": None,
        "reference_match": False,
        "mathematical_match": False,
        "error": None,
    }
    try:
        parsed = json.loads(raw_output)
        result["valid_json"] = True
        result["generated_formulation"] = parsed
    except json.JSONDecodeError as exc:
        result["error"] = f"JSON parse error: {exc}"
        return result

    try:
        formulation = Formulation.model_validate(parsed)
        result["valid_schema"] = True
    except ValidationError as exc:
        result["error"] = f"Schema validation error: {exc}"
        return result

    try:
        solved = solve_formulation(formulation)
        result["solver_status"] = solved["status"]
        result["feasible"] = solved["feasible"]
        result["objective"] = solved["objective"]
        if solved["objective"] is not None and case.get("known_optimum") is not None:
            error = abs(solved["objective"] - case["known_optimum"])
            result["objective_abs_error"] = error
            denominator = max(abs(case["known_optimum"]), 1e-12)
            result["objective_relative_error"] = error / denominator
        reference = Formulation.model_validate(case["reference"])
        result["reference_match"] = canonical(formulation) == canonical(reference)
        result["mathematical_match"] = (
            mathematical_signature(formulation)
            == mathematical_signature(reference)
        )
    except Exception as exc:  # Keep one failed case from stopping the whole benchmark.
        result["error"] = f"Solver/evaluation error: {type(exc).__name__}: {exc}"
    return result


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    if total == 0:
        return {"cases": 0}
    valid = sum(row["valid_schema"] for row in results)
    feasible = sum(row["feasible"] for row in results)
    matched = sum(row["reference_match"] for row in results)
    mathematically_matched = sum(
        row["mathematical_match"] for row in results
    )
    errors = [row["objective_abs_error"] for row in results if row["objective_abs_error"] is not None]
    return {
        "cases": total,
        "schema_valid_rate": valid / total,
        "solver_feasible_rate": feasible / total,
        "exact_reference_match_rate": matched / total,
        "mean_objective_absolute_error": sum(errors) / len(errors) if errors else None,
        "mathematical_match_rate": mathematically_matched / total,
    }

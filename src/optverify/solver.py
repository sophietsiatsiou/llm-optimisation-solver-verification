"""Solve validated continuous linear programs with OR-Tools GLOP."""
from __future__ import annotations

from typing import Any

from ortools.linear_solver import pywraplp

from optverify.schema import Formulation


def solve_formulation(formulation: Formulation) -> dict[str, Any]:
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        raise RuntimeError("OR-Tools GLOP solver is unavailable")

    variables = {}
    for variable in formulation.variables:
        lb = -solver.infinity() if variable.lower is None else variable.lower
        ub = solver.infinity() if variable.upper is None else variable.upper
        variables[variable.name] = solver.NumVar(lb, ub, variable.name)

    objective = solver.Objective()
    for name, coefficient in formulation.objective.coefficients.items():
        objective.SetCoefficient(variables[name], coefficient)
    if formulation.sense == "max":
        objective.SetMaximization()
    else:
        objective.SetMinimization()

    for constraint in formulation.constraints:
        if constraint.sense == "<=":
            row = solver.Constraint(-solver.infinity(), constraint.rhs, constraint.name)
        elif constraint.sense == ">=":
            row = solver.Constraint(constraint.rhs, solver.infinity(), constraint.name)
        else:
            row = solver.Constraint(constraint.rhs, constraint.rhs, constraint.name)
        for name, coefficient in constraint.coefficients.items():
            row.SetCoefficient(variables[name], coefficient)

    status = solver.Solve()
    status_names = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }
    result: dict[str, Any] = {
        "status": status_names.get(status, f"UNKNOWN_{status}"),
        "feasible": status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE),
        "objective": None,
        "variables": {},
    }
    if result["feasible"]:
        result["objective"] = objective.Value()
        result["variables"] = {name: var.solution_value() for name, var in variables.items()}
    return result

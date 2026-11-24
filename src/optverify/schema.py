"""Data models and validation for a linear optimisation formulation."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Variable(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    lower: float | None = 0.0
    upper: float | None = None

    @model_validator(mode="after")
    def check_bounds(self) -> "Variable":
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError(f"lower bound exceeds upper bound for {self.name}")
        return self


class LinearConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    coefficients: dict[str, float]
    sense: Literal["<=", ">=", "=="]
    rhs: float


class Objective(BaseModel):
    model_config = ConfigDict(extra="forbid")
    coefficients: dict[str, float]


class Formulation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    sense: Literal["min", "max"]
    variables: list[Variable]
    objective: Objective
    constraints: list[LinearConstraint]

    @model_validator(mode="after")
    def validate_references(self) -> "Formulation":
        names = [v.name for v in self.variables]
        if not names:
            raise ValueError("at least one decision variable is required")
        if len(names) != len(set(names)):
            raise ValueError("variable names must be unique")
        known = set(names)
        for label, coefficients in [("objective", self.objective.coefficients)] + [
            (c.name, c.coefficients) for c in self.constraints
        ]:
            unknown = set(coefficients) - known
            if unknown:
                raise ValueError(f"{label} references unknown variables: {sorted(unknown)}")
        return self

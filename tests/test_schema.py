import pytest
from pydantic import ValidationError

from optverify.schema import Formulation


def test_unknown_variable_is_rejected():
    payload = {
        "name": "bad",
        "sense": "max",
        "variables": [{"name": "x", "lower": 0, "upper": None}],
        "objective": {"coefficients": {"z": 1}},
        "constraints": [],
    }
    with pytest.raises(ValidationError):
        Formulation.model_validate(payload)

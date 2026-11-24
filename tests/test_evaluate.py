
from optverify.evaluate import mathematical_signature
from optverify.schema import Formulation


def test_mathematical_signature_ignores_variable_names():
    reference = Formulation.model_validate({
        "name": "reference",
        "sense": "max",
        "variables": [
            {"name": "x", "lower": 0, "upper": None},
            {"name": "y", "lower": 0, "upper": None},
        ],
        "objective": {
            "coefficients": {"x": 3, "y": 5}
        },
        "constraints": [
            {
                "name": "labour",
                "coefficients": {"x": 2, "y": 1},
                "sense": "<=",
                "rhs": 10,
            }
        ],
    })

    renamed = Formulation.model_validate({
        "name": "different_name",
        "sense": "max",
        "variables": [
            {"name": "chairs", "lower": 0, "upper": None},
            {"name": "tables", "lower": 0, "upper": None},
        ],
        "objective": {
            "coefficients": {"chairs": 3, "tables": 5}
        },
        "constraints": [
            {
                "name": "different_constraint_name",
                "coefficients": {"chairs": 2, "tables": 1},
                "sense": "<=",
                "rhs": 10,
            }
        ],
    })

    assert mathematical_signature(reference) == mathematical_signature(renamed)



def test_mathematical_signature_detects_changed_constraint():
    original = Formulation.model_validate({
        "name": "original",
        "sense": "max",
        "variables": [
            {"name": "x", "lower": 0, "upper": None},
            {"name": "y", "lower": 0, "upper": None},
        ],
        "objective": {
            "coefficients": {"x": 3, "y": 5}
        },
        "constraints": [
            {
                "name": "labour",
                "coefficients": {"x": 2, "y": 1},
                "sense": "<=",
                "rhs": 10,
            }
        ],
    })

    changed = Formulation.model_validate({
        "name": "changed",
        "sense": "max",
        "variables": [
            {"name": "x", "lower": 0, "upper": None},
            {"name": "y", "lower": 0, "upper": None},
        ],
        "objective": {
            "coefficients": {"x": 3, "y": 5}
        },
        "constraints": [
            {
                "name": "labour",
                "coefficients": {"x": 2, "y": 1},
                "sense": "<=",
                "rhs": 12,
            }
        ],
    })

    assert mathematical_signature(original) != mathematical_signature(changed)

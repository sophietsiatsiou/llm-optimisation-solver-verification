"""Command-line interface."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table

from optverify.evaluate import evaluate_case, load_cases, summarize
from optverify.providers import OllamaProvider, OpenAIProvider, ReferenceProvider
from optverify.schema import Formulation
from optverify.solver import solve_formulation

app = typer.Typer(no_args_is_help=True)
DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data" / "benchmark.json"


@app.command()
def validate(data: Path = DEFAULT_DATA) -> None:
    """Validate all reference formulations and their solver outputs."""
    cases = load_cases(data)
    for case in cases:
        formulation = Formulation.model_validate(case["reference"])
        solved = solve_formulation(formulation)
        print(f"[green]OK[/green] {case['id']}: {solved['status']} objective={solved['objective']}")
        if not solved["feasible"]:
            raise typer.Exit(code=1)


@app.command()
def solve(case: str = typer.Option(..., "--case"), data: Path = DEFAULT_DATA) -> None:
    """Solve a single reference case."""
    cases = load_cases(data)
    selected = next((item for item in cases if item["id"] == case), None)
    if selected is None:
        raise typer.BadParameter(f"Unknown case {case!r}; available: {[c['id'] for c in cases]}")
    result = solve_formulation(Formulation.model_validate(selected["reference"]))
    print_json(result)


@app.command()
def benchmark(
    provider: str = typer.Option(
        "reference",
        help="Provider: reference, openai or ollama",
    ),
    model: str = typer.Option(
        "gpt-4.1-mini",
        help="Model name for the selected provider",
    ),
    data: Path = DEFAULT_DATA,
    output: Path = Path("outputs/benchmark_results.json"),
) -> None:
    """Run benchmark and save per-case results plus aggregate metrics."""
    cases = load_cases(data)
    if provider == "reference":
        generator = ReferenceProvider()
    elif provider == "openai":
        generator = OpenAIProvider(model=model)
    elif provider == "ollama":
        generator = OllamaProvider(model=model)
    else:
        raise typer.BadParameter(
            "provider must be 'reference', 'openai' or 'ollama'"
        )

    rows = []
    for case in cases:
        try:
            raw = generator.formulate(case, model=model)
        except Exception as exc:
            raw = ""
            row = evaluate_case(case, raw)
            row["error"] = f"Provider error: {type(exc).__name__}: {exc}"
        else:
            row = evaluate_case(case, raw)
        row["provider"] = provider
        row["model"] = model if provider in ("openai", "ollama") else None
        rows.append(row)

    report = {"summary": summarize(rows), "results": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    table = Table(title="Optimisation formulation benchmark")
    table.add_column("Case")
    table.add_column("Schema")
    table.add_column("Feasible")
    table.add_column("Ref match")
    table.add_column("Obj. abs. error")
    for row in rows:
        table.add_row(
            row["case_id"],
            str(row["valid_schema"]),
            str(row["feasible"]),
            str(row["reference_match"]),
            str(row["objective_abs_error"]),
        )
    print(table)
    print(report["summary"])
    print(f"Saved: {output}")


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2))

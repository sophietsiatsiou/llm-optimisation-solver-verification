# Usage Guide

## LLM-Based Mathematical Optimisation with Solver Verification

This document explains how to install, configure and run the project.

It is written for someone who wants to use the existing implementation without needing to understand every internal module first.

The guide uses:
- Python 3.11.
- Ollama for local LLM execution.
- Qwen 2.5 (7B) as the formulation model.
- Pydantic for validation.
- Google OR-Tools for optimisation.

No paid API key is required for the Ollama workflow.

---

# 1. Prerequisites

Before starting, make sure you have:

| Requirement | Purpose |
|---|---|
| Python 3.10 or newer | Runs the project |
| pip | Installs Python dependencies |
| Git | Clones the repository |
| Ollama | Runs the local LLM |
| Internet connection | Downloads dependencies and the model |

Python 3.11 is the recommended version for the current implementation.

Check your Python installation:

```bash
python3 --version
```

Check pip:

```bash
python3 -m pip --version
```

---

# 2. Download the Repository

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd LLM-optimisation-solver-verification
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual GitHub repository URL.

If you have already downloaded the project, simply open Terminal in its main directory.

The main directory should contain:

```text
README.md
USAGE.md
pyproject.toml
data/
src/
tests/
```

---

# 3. Install Python Dependencies

Install the project and its development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

This installs the project in editable mode and installs the dependencies required for development and testing.

The main dependencies include:

- Pydantic: formulation validation.
- OR-Tools: mathematical optimisation.
- Typer: command-line interface.
- Pytest: automated testing.

The project also includes an optional OpenAI provider, but it is not required for the local Ollama workflow.

---

# 4. Install and Configure Ollama

Ollama allows you to run an LLM locally instead of sending prompts to a paid external API.

Download Ollama from:

https://ollama.com/download

Install the version appropriate for your operating system.

Start Ollama.

On macOS, opening the Ollama application starts its local service.

Check that the command-line interface is available:

```bash
ollama --version
```

Download the model:

```bash
ollama pull qwen2.5:7b
```

This downloads Qwen 2.5 with approximately 7 billion parameters.

The model requires several gigabytes of storage.

Check that the model is installed:

```bash
ollama list
```

You should see an entry similar to:

```text
NAME          ID          SIZE
qwen2.5:7b    ...         4.7 GB
```

The exact size and model identifier may vary depending on the downloaded model version.

## 4.1. Test the model

Run:

```bash
ollama run qwen2.5:7b
```

You can now interact with the model directly.

For example, enter:

```text
Explain what a linear programming optimisation problem is.
```

If the model responds, the local installation is working.

Exit the interactive session with:

```text
/bye
```

---

# 5. Understand the Local API

The Python project communicates with Ollama through its local HTTP API.

The default address is:

```text
http://localhost:11434
```

You can check whether the API is responding with:

```bash
curl http://localhost:11434/api/tags
```

A successful response returns information about the locally installed models.

The project sends requests to Ollama's chat endpoint:

```text
http://localhost:11434/api/chat
```

The `OllamaProvider` class in `src/optverify/providers.py` handles this communication.

You do not need to call the API manually when running the benchmark.

---

# 6. Run the Project

The project provides three main operations:

1. Validate the benchmark dataset.
2. Solve an individual reference problem.
3. Run a complete benchmark.

The current tested way to invoke the CLI is through Python:

```bash
python3 -c 'from optverify.cli import app; app()'
```

Run commands from the project's root directory.

## 6.1. Validate the benchmark dataset

Run:

```bash
python3 -c 'from optverify.cli import app; app()' validate
```

This checks the benchmark data and its reference formulations.

## 6.2. Solve an individual problem

For example, solve the product-mix problem:

```bash
python3 -c 'from optverify.cli import app; app()' solve --case product_mix
```

The solver uses the predefined reference formulation for this case.

The output includes information such as:
- Solver status.
- Feasibility.
- Objective value.
- Decision-variable values.

This operation tests the mathematical optimisation component without involving the LLM.

## 6.3. Run the reference benchmark

Before using the LLM, run the reference benchmark:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark
```

The default provider is `reference`.

This tests the complete validation, solver and evaluation pipeline using predefined correct formulations.

It is useful as a baseline to confirm that the pipeline works independently of LLM performance.

## 6.4. Run the Ollama benchmark

Once Ollama is running and Qwen 2.5 is installed, execute:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark --provider ollama --model qwen2.5:7b
```

This runs the benchmark using the local LLM.

For each case, the system:

1. Sends the natural-language problem to Qwen 2.5.
2. Receives a JSON formulation.
3. Parses and validates the JSON.
4. Checks the formulation against the Pydantic schema.
5. Passes valid formulations to OR-Tools.
6. Solves the resulting linear programming problem.
7. Compares the formulation and solution with the reference.
8. Records the evaluation metrics.

The first run may take longer because the model needs to be loaded into memory.

## 6.5. Save benchmark results

You can specify where the benchmark results should be saved:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark --provider ollama --model qwen2.5:7b --output outputs/ollama_benchmark_results.json
```

The results are saved as a JSON file.

This allows you to inspect individual cases and retain benchmark outputs for later analysis.

---

# 7. Understand the Benchmark Results

The benchmark reports several metrics.

| Metric | Explanation |
|---|---|
| `valid_json` | Was the LLM response valid JSON? |
| `valid_schema` | Did the response satisfy the Pydantic schema? |
| `solver_status` | What status did OR-Tools return? |
| `feasible` | Did the generated model have a feasible solution? |
| `objective` | What objective value did the solver calculate? |
| `objective_abs_error` | How far was the objective from the known optimum? |
| `objective_relative_error` | Relative objective-value error |
| `reference_match` | Did the formulation match the canonical reference? |
| `mathematical_match` | Did the formulation match the reference under the name-independent signature comparison? |

## 7.1. Why are there two formulation comparison metrics?

Consider these two objective functions:

```text
3x + 5y
```

and:

```text
3chairs + 5tables
```

The variable names differ, but the mathematical meaning can be identical if all corresponding constraints and bounds also match.

`reference_match` checks the canonical formulation, including names.

`mathematical_match` ignores variable names, constraint names and ordering.

The current mathematical-signature comparison does not cover every possible mathematical equivalence, such as equivalent constraints expressed after multiplying both sides by a positive constant.

## 7.2. Why is objective error important?

Suppose the reference optimum is:

```text
440
```

and the generated formulation produces:

```text
440
```

The absolute objective error is:

```text
0
```

However, this does not prove that the generated formulation is correct.

A different formulation might produce the same objective value by coincidence.

For this reason, the project reports objective accuracy together with feasibility and formulation comparisons.

---

# 8. Run the Automated Tests

The project includes automated tests.

Run the complete suite:

```bash
python3 -m pytest -v
```

The tests cover:

- Schema validation.
- Rejection of unknown decision variables.
- Solver feasibility.
- Correct objective calculation.
- Formulation comparison under variable renaming.
- Detection of changed constraint values.

A successful run should show five passing tests in the current version.

---

# 9. Using a Different LLM

The project supports different formulation providers.

The available providers are:

| Provider | Description |
|---|---|
| `reference` | Uses predefined reference formulations |
| `ollama` | Uses a locally running Ollama model |
| `openai` | Uses the optional OpenAI-compatible API provider |

To use another Ollama model, first download it:

```bash
ollama pull <MODEL_NAME>
```

Then specify it in the benchmark command:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark --provider ollama --model <MODEL_NAME>
```

The selected model must support the required chat and JSON response functionality.

## Optional: OpenAI provider

The project also includes an optional OpenAI provider.

Install its dependency:

```bash
python3 -m pip install -e ".[llm]"
```

Set your API key:

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
```

Then run:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark --provider openai --model gpt-4.1-mini
```

An API key is not necessary for the Ollama provider.

Never commit API keys to the repository.

---

# 10. Troubleshooting

## Ollama connection error

If you receive a connection error, check that the Ollama application is running.

Test the API:

```bash
curl http://localhost:11434/api/tags
```

If the API does not respond, restart Ollama.

## Model not found

Check the installed models:

```bash
ollama list
```

If Qwen is missing, download it:

```bash
ollama pull qwen2.5:7b
```

## Python module not found

Make sure you are inside the project directory and have installed the project:

```bash
python3 -m pip install -e ".[dev]"
```

## Command `optverify` not found

The current tested setup invokes the Typer CLI through Python:

```bash
python3 -c 'from optverify.cli import app; app()' --help
```

Use this invocation instead of relying on the standalone `optverify` command.

## Invalid formulation

An LLM may return JSON that is valid but does not satisfy the expected schema.

This is an important part of the experiment.

The evaluation pipeline records parsing and schema-validation failures rather than treating every model response as a correct formulation.

---

# 11. Important Limitations

The current implementation supports continuous linear programming.

It does not currently support:
- Integer programming.
- Mixed-integer linear programming.
- Nonlinear optimisation.
- Multi-objective optimisation.
- Automatic clarification of ambiguous prompts.
- Full mathematical equivalence checking.

The benchmark contains three small synthetic examples and should not be interpreted as evidence of general performance across arbitrary optimisation problems.

A solver can verify a generated mathematical model, but it cannot independently determine whether that model faithfully represents the original natural-language description.

Human review and stronger benchmark datasets remain important.

---

# 12. Quick Command Reference

For convenience, the most frequently used commands are collected below.

| Task | Command |
|---|---|
| Check Python | `python3 --version` |
| Install dependencies | `python3 -m pip install -e ".[dev]"` |
| Check Ollama | `ollama list` |
| Download Qwen | `ollama pull qwen2.5:7b` |
| Check Ollama API | `curl http://localhost:11434/api/tags` |
| Validate benchmark | `python3 -c 'from optverify.cli import app; app()' validate` |
| Solve product mix | `python3 -c 'from optverify.cli import app; app()' solve --case product_mix` |
| Run reference benchmark | `python3 -c 'from optverify.cli import app; app()' benchmark` |
| Run Ollama benchmark | `python3 -c 'from optverify.cli import app; app()' benchmark --provider ollama --model qwen2.5:7b` |
| Run tests | `python3 -m pytest -v` |

---

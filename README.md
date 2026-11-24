# LLM-Based Mathematical Optimisation with Solver Verification

## 1. Project Overview

This project explores how Large Language Models (LLMs) can translate natural-language mathematical optimisation problems into structured Linear Programming (LP) formulations, and how mathematical optimisation solvers can be used to verify the generated formulations.

The system follows a pipeline in which an LLM interprets a problem description and produces a structured mathematical model. The model is then validated using Pydantic and passed to Google OR-Tools to check feasibility and calculate an optimal solution.

The project also includes a benchmark evaluation pipeline to compare LLM-generated formulations against reference formulations.

The main objective is to demonstrate how LLMs and traditional mathematical optimisation tools can work together: the LLM handles natural-language interpretation, while a deterministic optimisation solver performs the mathematical computation.

**Key technologies:**
- Python 3.11
- Large Language Models (LLMs)
- Ollama
- Qwen 2.5 7B
- Pydantic
- Google OR-Tools
- pytest

## 2. Motivation

Mathematical optimisation problems are often described in natural language. Before they can be solved computationally, they must be translated into a mathematical formulation containing:

- Decision variables.
- An objective function.
- Constraints.
- Variable bounds.

This translation requires understanding the problem's meaning and expressing it mathematically.

LLMs can interpret natural-language descriptions and generate structured outputs, but their mathematical formulations are not guaranteed to be correct. A model might misunderstand a constraint, omit a requirement, or introduce an incorrect coefficient.

This project investigates a practical approach to reducing that risk by combining LLM-generated formulations with formal validation and mathematical solver verification.

Rather than relying only on an LLM's generated answer, the system uses Pydantic and OR-Tools to validate the model's structure and test whether the resulting optimisation problem can be solved.

An important distinction is that a solver can verify whether a given mathematical formulation is feasible and solve it correctly, but it cannot independently guarantee that the formulation accurately represents the original natural-language problem. This is why comparison against reference formulations is also included.

## 3. Project Objectives

The project has five main objectives:

1. **Natural-language interpretation:** Use an LLM to translate an optimisation problem described in natural language into a structured linear programming formulation.
2. **Structured output validation:** Use Pydantic to validate the generated formulation, including its variables, objective function, constraints, and mathematical references.
3. **Solver-based verification:** Use Google OR-Tools to solve the generated linear programming problem and check its feasibility.
4. **Benchmark evaluation:** Compare generated formulations and their solutions against known reference formulations.
5. **Local LLM experimentation:** Run an open-weight language model locally through Ollama, avoiding the need for a paid external LLM API.

## 4. System Architecture

The project uses a modular pipeline:

```text
Natural-Language Optimisation Problem
                 |
                 v
          LLM Provider
       (Ollama / Reference)
                 |
                 v
      Structured LP Formulation
                 |
                 v
       Pydantic Validation
                 |
                 v
       Google OR-Tools Solver
                 |
                 v
       Feasibility and Solution
                 |
                 v
        Benchmark Evaluation
                 |
                 v
          Evaluation Metrics
```

### Pipeline Explanation

**1. Natural-language input**

An optimisation problem is provided as a text description. It explains the objective, decision context, and relevant constraints.

**2. LLM formulation**

The selected provider interprets the problem and generates a structured representation of the mathematical model.

The local implementation uses Qwen 2.5 7B through Ollama. A reference provider is also available for testing the pipeline with predefined formulations.

**3. Pydantic validation**

The generated output is checked against predefined Pydantic models. This ensures that the formulation has the expected structure and that referenced variables and coefficients are valid.

**4. OR-Tools solver**

A validated formulation is translated into an optimisation model using Google OR-Tools.

The solver determines whether the model is feasible and, when possible, calculates its optimal objective value and decision variable values.

**5. Evaluation**

The generated formulation is compared with the reference formulation. The evaluation considers structural validity, solver feasibility, exact reference matching, mathematical signature matching, and objective-value error.

## 5. Project Structure / Main Components

```text
LLM-optimisation-solver-verification/
│
├── data/
│   └── benchmark.json
│
├── src/
│   └── optverify/
│       ├── __init__.py
│       ├── schema.py
│       ├── solver.py
│       ├── providers.py
│       ├── evaluate.py
│       └── cli.py
│
├── tests/
│   ├── test_schema.py
│   ├── test_solver.py
│   └── test_evaluate.py
│
├── README.md
├── USAGE.md
├── pyproject.toml
└── .gitignore
```

### Main Components

| File | Responsibility |
|---|---|
| `schema.py` | Defines and validates the mathematical formulation using Pydantic models. |
| `solver.py` | Converts validated formulations into OR-Tools models and solves them. |
| `providers.py` | Implements the reference, Ollama, and OpenAI-compatible LLM providers. |
| `evaluate.py` | Loads benchmark cases, evaluates generated formulations, and calculates performance metrics. |
| `cli.py` | Provides command-line commands for validation, solving, and benchmarking. |
| `benchmark.json` | Contains the benchmark problems and their reference formulations. |
| `tests/` | Contains automated tests for schemas, solver behaviour, and evaluation logic. |

### Main Technologies

- **Python:** Core programming language.
- **Ollama:** Runs the language model locally.
- **Qwen 2.5 7B:** Local language model used for natural-language-to-LP formulation.
- **Pydantic:** Validates the structure and consistency of generated mathematical models.
- **Google OR-Tools:** Solves the resulting linear programming problems using the GLOP solver.
- **pytest:** Runs automated tests.

## 6. Benchmark Dataset and Data Sources

### Dataset Overview

The project uses a small, custom-built benchmark dataset stored in:

`data/benchmark.json`

The dataset was created specifically for this project to evaluate how effectively an LLM translates natural-language optimisation problems into structured linear programming formulations.

It contains three illustrative optimisation problems:

| Benchmark case | Objective | Main constraints |
|---|---|---|
| Product Mix | Maximise production profit | Available production resources |
| Diet Cost | Minimise total food cost | Nutritional requirements |
| Production Capacity | Maximise production value | Production resource limits |

### Data Sources and Preparation

The benchmark examples were manually designed for this project. They were not downloaded from an external dataset or retrieved from a third-party database.

Each benchmark case contains a natural-language problem description and a corresponding reference mathematical formulation.

The reference formulation specifies:
- Decision variables and their bounds.
- The objective function and whether it should be maximised or minimised.
- Linear constraints, including their coefficients, comparison operators, and right-hand-side values.

The reference formulations provide the expected mathematical models against which generated formulations can be evaluated.

Their expected feasibility and optimal objective values were checked using Google OR-Tools.

The examples were deliberately kept small and interpretable. This makes it easier to inspect the generated formulations, identify modelling errors, and understand differences between an LLM-generated model and its reference.

### How the Data Is Used

The benchmark dataset is used throughout the evaluation pipeline:

1. **Load benchmark cases:** The evaluation module reads the problem descriptions and reference formulations from `data/benchmark.json`.
2. **Generate formulations:** The selected provider receives each natural-language problem and generates a structured LP formulation. For example, the Ollama provider sends the problem to Qwen 2.5 7B.
3. **Validate the output:** The generated formulation is checked against the Pydantic schema.
4. **Solve the formulation:** Valid formulations are passed to Google OR-Tools to determine feasibility and calculate an optimal solution.
5. **Compare against references:** The generated formulation and solution are compared with the reference formulation and its expected results.
6. **Calculate evaluation metrics:** The evaluation module summarises schema validity, solver feasibility, reference matching, and objective-value error.

The dataset therefore provides a controlled set of examples for evaluating the complete natural-language-to-optimisation pipeline.

### Input Data and Generated Results

It is useful to distinguish between the benchmark input data and the experimental results:

| Data type | Description | Location |
|---|---|---|
| Benchmark input data | Original problem descriptions and reference formulations | `data/benchmark.json` |
| Generated results | LLM-generated formulations and evaluation summaries | Saved to an output JSON file when requested |

The generated results are produced by running the benchmark; they are not part of the original benchmark input.

### Dataset Limitations

The current benchmark contains only three manually constructed examples. It is intended as a proof of concept and a demonstration of the complete LLM-to-solver verification pipeline, rather than a comprehensive evaluation dataset.

The examples do not represent a statistically diverse or independently collected dataset. Therefore, the reported results should be interpreted as performance on this particular benchmark, not as evidence of general LLM performance across all mathematical optimisation problems.

Future extensions could include:
- A larger and more diverse set of linear programming problems.
- Problems with different numbers of decision variables and constraints.
- More challenging or ambiguous natural-language descriptions.
- Independently sourced optimisation problems with documented reference solutions.
- Larger evaluation sets to support more meaningful performance comparisons.

## 7. Benchmark Design and Evaluation Metrics

The benchmark evaluates the ability of an LLM to translate natural-language optimisation problems into valid and mathematically equivalent linear programming formulations.

Three benchmark problems are currently included:
- Product Mix.
- Diet Cost.
- Production Capacity.

Each case contains a reference formulation against which the generated model can be evaluated.

### Evaluation Metrics

**1. Schema Validity Rate**

Measures the proportion of generated formulations that pass Pydantic validation.

This indicates whether the LLM produces outputs with the expected structure and valid mathematical references.

**2. Solver Feasibility Rate**

Measures the proportion of schema-valid generated formulations that can be solved feasibly by OR-Tools.

This indicates whether the generated mathematical models can be solved under their stated constraints and bounds.

**3. Exact Reference Match Rate**

Measures the proportion of generated formulations that exactly match their reference formulations after canonical ordering.

This is a strict comparison: differences in variable names or constraint names can result in a mismatch even when the underlying mathematics is equivalent.

**4. Mathematical Signature Match Rate**

Measures whether the generated formulation matches the reference formulation using a name-independent mathematical signature.

The current implementation accounts for variable renaming and ordering differences. It does not establish equivalence under every possible algebraic transformation.

**5. Mean Objective Absolute Error**

Measures the average absolute difference between the generated formulation's optimal objective value and the reference objective value.

A smaller value indicates closer agreement in objective value.

However, matching objective values alone does not prove that two mathematical formulations are equivalent.

## 8. Experimental Results

The local LLM benchmark was run using:

- **Model:** Qwen 2.5 7B
- **Runtime:** Ollama
- **Quantisation:** Q4_K_M
- **Number of benchmark cases:** 3

### Qwen 2.5 7B Results

| Metric | Result |
|---|---:|
| Schema validity rate | 100% |
| Solver feasibility rate | 100% |
| Exact reference match rate | 0% |
| Mathematical signature match rate | 100% |
| Mean objective absolute error | Approximately 0 |

### Interpretation

The model successfully generated schema-valid formulations for all three benchmark problems.

All generated formulations were also feasible and solvable using OR-Tools.

The exact reference match rate was 0% because the model used different variable and constraint names from those in the reference formulations.

However, the name-independent mathematical signature comparison matched all three generated formulations with their references.

The mean objective absolute error was approximately zero, indicating that the generated formulations produced the same optimal objective values as the reference formulations on these benchmark cases.

These results demonstrate that the LLM can generate mathematically consistent formulations for the three examples tested.

Nevertheless, the benchmark is small, and the results should not be interpreted as proof of general mathematical reasoning reliability.

### Reference Provider

A reference provider is also included to test the validation, solving, and evaluation pipeline using predefined reference formulations.

This provides a baseline for checking that the evaluation pipeline can correctly process the benchmark cases.

## 9. Limitations

The project demonstrates a working LLM-to-solver pipeline, but several limitations remain.

**Small benchmark dataset**

Only three manually constructed optimisation problems are included. This is insufficient to draw broad conclusions about LLM performance.

**Formulation correctness**

A mathematically feasible and optimal solution does not necessarily mean the original natural-language problem was interpreted correctly. OR-Tools solves the formulation it receives; it does not verify whether the formulation captures the user's intended meaning.

**Limited mathematical equivalence checking**

The mathematical signature comparison accounts for variable renaming and ordering differences, but it is not a complete mathematical equivalence checker.

**Continuous linear programming scope**

The current solver implementation uses continuous linear programming. It does not currently support integer or mixed-integer programming.

**LLM reliability**

LLMs may produce incorrect coefficients, omit constraints, or misinterpret ambiguous descriptions. A schema-valid formulation can still be semantically incorrect.

**Hardware and model constraints**

Running a local 7B parameter model requires sufficient memory and computational resources. Model performance may also vary depending on hardware, quantisation, and prompt design.

## 10. Installation and Usage

The project uses Python and Google OR-Tools, with Ollama providing local LLM inference.

For detailed installation instructions, provider configuration, example commands, and troubleshooting, see:

**[USAGE.md](USAGE.md)**

### Quick Start

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/llm-optimisation-solver-verification.git
cd llm-optimisation-solver-verification
```

Install the project and development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Install Ollama from [https://ollama.com](https://ollama.com), then download the model:

```bash
ollama pull qwen2.5:7b
```

Make sure the Ollama service is running.

Run the benchmark using the local model:

```bash
python3 -c 'from optverify.cli import app; app()' benchmark --provider ollama --model qwen2.5:7b
```

Run the automated tests:

```bash
python3 -m pytest -v
```

For more detailed instructions, including how to validate and solve individual formulations and how to use the reference and OpenAI-compatible providers, consult [USAGE.md](USAGE.md).

---

## Author

Developed as a portfolio project exploring the integration of Large Language Models, mathematical optimisation, structured validation, and solver-based verification.
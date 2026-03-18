# Python - Optimization Engine Module

## Overview

This folder contains the Python computation backend for the HFS-SDST scheduling project.
It implements optimization algorithms, core scheduling models, and output generation used by the UI module.

## Scope

This README covers only the Python submodule in `Python/`.
It does not describe the full repository architecture or JavaFX frontend internals.

## Tech Stack

- Python 3.8+
- NumPy
- Matplotlib
- Pytest (for tests)

## Project Layout

```text
Python/
├── main.py
├── benchmark.py
├── algorithms/
│   ├── greedy.py
│   ├── tabu_search.py
│   └── branch_and_bound.py
├── core/
│   ├── schedule.py
│   ├── job.py
│   └── machine.py
├── utils/
│   └── gantt_chart.py
└── tests/
```

## Installation

```bash
cd Python
pip install -r requirements.txt
```

## Quick Start

Run optimization for an input instance:

```bash
python main.py ../data/input.json
```

Run with Gantt generation (if supported by current CLI options):

```bash
python main.py ../data/input.json --plot
```

Run benchmark mode:

```bash
python main.py --test
```

## Input/Output Contract

### Input

The module expects a JSON instance with fields such as:

- `algorithm` (`greedy`, `tabu`, `bnb`)
- `num_stages`, `num_jobs`
- `machines_per_stage`
- `learning_coeff`, `learning_stages`
- `processing_times` (`[job][stage][machine]`)
- `setup_times` (`[from_job][to_job][stage][machine]`)

### Output

The solver writes output to `../results/result.json` including:

- execution time,
- algorithm name,
- objective value (`C_max`),
- detailed schedule,
- optional path to generated Gantt chart.

## Algorithms

- Greedy MSTF: fastest heuristic, good baseline.
- Tabu Search: metaheuristic with better quality/time tradeoff.
- Branch and Bound: exact approach, practical only for small instances.

### Practical recommendation

- Up to about 10 jobs: consider Branch and Bound.
- Medium instances: Tabu Search is usually the best compromise.
- Large instances: Greedy for quick feasible solutions.

## Runtime Flow

1. `main.py` reads and validates JSON input.
2. `core/` builds scheduling objects.
3. `algorithms/` runs selected optimization.
4. Results are serialized to `../results/result.json`.
5. `utils/gantt_chart.py` can generate chart output.

## Testing and Validation

Run tests:

```bash
pytest
```

For a detailed testing guide (test structure, scripts, coverage, and troubleshooting), see [TESTING.md](TESTING.md).

Optional helpers available in this module:

- `run_tests.bat`
- `run_tests.sh`
- `run_tests_coverage.bat`

## Troubleshooting

- Missing dependencies: reinstall with `pip install -r requirements.txt`.
- Input file not found: verify path and current working directory.
- Empty or missing results: check console errors and write permissions for `../results/`.
- Very long runtime with `bnb`: expected on larger instances; use `tabu` or `greedy`.

## Development Notes

- Keep algorithm logic in `algorithms/` and shared models in `core/`.
- Preserve JSON schema compatibility with UI and data modules.
- Add tests for any change in objective calculation or schedule serialization.
- Avoid committing temporary runtime files generated during experiments.

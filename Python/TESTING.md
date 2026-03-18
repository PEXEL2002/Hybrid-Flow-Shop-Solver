# Unit Testing Guide (Python Module)

This document describes unit tests for the Python module and how to run them with the current project structure.

## Scope

The guide applies to the folder structure:

- `Python/tests/` - test files and fixtures
- `Python/run_tests.bat` - Windows helper script
- `Python/run_tests.sh` - Linux/macOS helper script
- `Python/run_tests_coverage.bat` - Windows coverage script

## Current Test Structure

Unit tests are located in `Python/tests/`:

- `test_job.py`
- `test_machine.py`
- `test_schedule.py`
- `test_greedy.py`
- `test_tabu_search.py`
- `test_branch_and_bound.py`
- `test_gantt_chart.py`
- `test_main.py`
- `conftest.py` (shared fixtures)

## Prerequisites

1. Python 3.8+
2. Install runtime dependencies:

```bash
cd Python
pip install -r requirements.txt
```

3. Install test dependencies:

```bash
pip install -r tests/requirements-test.txt
```

Note: test requirements are currently stored in `tests/requirements-test.txt`.

## Running Tests

Run from the `Python/` directory.

### 1) Run all unit tests

```bash
python -m pytest tests -v --tb=short
```

### 2) Run one test file

```bash
python -m pytest tests/test_schedule.py -v
```

### 3) Run one test class

```bash
python -m pytest tests/test_tabu_search.py::TestTabuSearch -v
```

### 4) Run one test case

```bash
python -m pytest tests/test_job.py::TestJobInitialization::test_job_creation_with_valid_data -v
```

### 5) Stop on first failure

```bash
python -m pytest tests -x -v
```

### 6) Show print output (no capture)

```bash
python -m pytest tests -v --capture=no
```

## Helper Scripts

### Windows

```bash
cd Python
run_tests.bat
```

With custom arguments:

```bash
run_tests.bat tests/test_main.py -v
```

### Linux/macOS

```bash
cd Python
chmod +x run_tests.sh
./run_tests.sh
```

## Coverage

### Windows script

```bash
cd Python
run_tests_coverage.bat
```

### Direct pytest command (all platforms)

```bash
python -m pytest tests \
  --cov=core \
  --cov=algorithms \
  --cov=utils \
  --cov=main \
  --cov-report=term-missing \
  --cov-report=html
```

HTML report is generated in `Python/htmlcov/index.html`.

## Recommended Pre-Commit Workflow

1. Run all tests:

```bash
python -m pytest tests -v
```

2. Run coverage for core modules:

```bash
python -m pytest tests --cov=core --cov=algorithms --cov=utils --cov-report=term-missing
```

3. If changing CLI behavior in `main.py`, run:

```bash
python -m pytest tests/test_main.py -v --capture=no
```

## Troubleshooting

### Error: No module named pytest

```bash
pip install -r tests/requirements-test.txt
```

### Error: No module named pytest_cov

```bash
pip install pytest-cov
```

### Tests cannot find project modules

- Ensure you run commands from `Python/`.
- Prefer `python -m pytest ...` over plain `pytest`.

### Gantt chart tests fail in headless environment

- Use mocked tests from `test_gantt_chart.py`.
- Avoid forcing GUI backends for matplotlib.

## Notes

- Existing helper scripts still print install hints for `requirements-test.txt` in the module root.
- In the current structure, the active file is `tests/requirements-test.txt`.

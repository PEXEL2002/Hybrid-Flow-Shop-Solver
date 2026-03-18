# Quick Start - Unit Tests

A short guide for running unit tests in this project.

## 1) Install test dependencies

From the `Python/` directory:

```bash
pip install -r tests/requirements-test.txt
```

## 2) Run all tests

```bash
python -m pytest tests -v
```

## 3) Run one test file

```bash
python -m pytest tests/test_schedule.py -v
```

## 4) Run with coverage

```bash
python -m pytest tests --cov=core --cov=algorithms --cov=utils --cov-report=term-missing --cov-report=html
```

Coverage HTML report:

```text
Python/htmlcov/index.html
```

## Helper scripts

### Windows

From `Python/`:

```bash
run_tests.bat
run_tests_coverage.bat
```

### Linux/macOS

From `Python/`:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Useful commands

```bash
# stop on first failure
python -m pytest tests -x -v

# show print output
python -m pytest tests -v --capture=no

# run only last failed tests
python -m pytest tests --lf
```

## Troubleshooting

- `No module named pytest`: install `tests/requirements-test.txt`.
- Import/path issues: run commands from `Python/`.
- Coverage command fails: install `pytest-cov`.

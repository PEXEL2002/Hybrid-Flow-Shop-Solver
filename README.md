# Hybrid Flow Shop Solver (HFS-SDST)

A production scheduling application for the Hybrid Flow Shop problem with sequence-dependent setup times (SDST) and learning effects.

## About the Project

The project combines:

- a JavaFX UI layer for instance definition and result presentation,
- a Python optimization engine,
- JSON-based data exchange through `data/` and `results/`.

The main objective is to minimize $C_{max}$, the completion time of the last job (makespan).

## Scheduling Problem (Brief)

The addressed problem is HFS-SDST:

- **HFS (Hybrid Flow Shop)**: jobs pass through consecutive production stages, with multiple parallel machines available at each stage.
- **SDST (Sequence-Dependent Setup Times)**: setup time depends on the order of jobs.
- **Learning effect**: processing times may decrease with the job position in the sequence.

In practice, this is a complex combinatorial optimization problem where schedule quality depends on both job sequencing and machine assignment.

## Technology Stack

![Java](https://img.shields.io/badge/Java-17-orange?logo=openjdk&logoColor=white)
![JavaFX](https://img.shields.io/badge/JavaFX-21.0.1-0A4B8C)
![Maven](https://img.shields.io/badge/Maven-3.6%2B-C71A36?logo=apachemaven&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-enabled-11557C)
![Pytest](https://img.shields.io/badge/Pytest-tests-0A9EDC?logo=pytest&logoColor=white)

- **Java 17** - desktop application and UI logic.
- **JavaFX 21.0.1** - user interface and result visualization.
- **Maven 3.6+** - Java module build system.
- **Python 3.8+** - optimization engine.
- **Matplotlib** - Gantt chart generation.
- **Pytest** - unit testing for the Python module.

## Repository Architecture

```text
Hybrid-Flow-Shop-Solver/
├── start.bat
├── README.md
├── Demo_Ui/
│   ├── README.md
│   └── javafx-ui/
├── Python/
│   ├── README.md
│   ├── TESTING.md
│   ├── main.py
│   ├── algorithms/
│   ├── core/
│   ├── utils/
│   └── tests/
├── data/
│   └── README.md
└── results/
```

Module documentation:

- UI: [Demo_Ui/README.md](Demo_Ui/README.md)
- Python backend: [Python/README.md](Python/README.md)
- Python tests: [Python/TESTING.md](Python/TESTING.md)
- Input data: [data/README.md](data/README.md)

## Available Algorithms

- **Greedy MSTF** - fast baseline heuristic.
- **Tabu Search** - metaheuristic with a strong quality/time tradeoff.
- **Branch and Bound** - exact method, recommended for small instances.

## Requirements

- Java 17+
- Maven 3.6+
- Python 3.8+

## Quick Start (Windows)

From the project root:

```bash
start.bat
```

The startup script prepares the environment and launches the application.

## Manual Run

1. Install Python dependencies:

```bash
cd Python
pip install -r requirements.txt
cd ..
```

2. Start the JavaFX interface:

```bash
cd Demo_Ui/javafx-ui
mvn clean javafx:run
```

## Data Flow

1. The user defines a problem instance in the UI.
2. The UI writes input to `data/input_<timestamp>.json`.
3. The Python module runs optimization.
4. The result is written to `results/result.json`.
5. The UI presents metrics and a Gantt chart.

## Input and Output Format

Input example (JSON):

```json
{
  "algorithm": "tabu",
  "num_stages": 2,
  "num_jobs": 3,
  "machines_per_stage": [1, 2],
  "learning_coeff": 0.15,
  "learning_stages": "10",
  "processing_times": [...],
  "setup_times": [...]
}
```

Output example (JSON):

```json
{
  "time_in_ms": 3123,
  "Algorithm": "Tabu Search",
  "C_max": 101.48,
  "gant_diagram": "<path-to-png>",
  "schedule": [...]
}
```

## Practical Guidance

- Up to around 10 jobs: Branch and Bound can be considered.
- Medium instances: Tabu Search is usually the best compromise.
- Large instances: use Greedy for fast feasible solutions.

## Testing

![Tests](https://img.shields.io/badge/Tests-159%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-94%25-greenyellow)

Unit test coverage is 94% for optimization-related code (Branch and Bound, Greedy, Tabu Search) and key domain classes (Job, Machine, Schedule).

Quick command:

```bash
cd Python
python -m pytest tests -v
```

Detailed testing and coverage guide: [Python/TESTING.md](Python/TESTING.md).

## Author

Bartłomiej Adam Kuk  
Politechnika Wrocławska, Wydział Informatyki i Telekomunikacji

## License

Project prepared as part of an engineering thesis.

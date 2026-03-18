# Demo_UI - JavaFX Frontend Module

## Overview

This folder contains the JavaFX user interface for the HFS-SDST scheduling application.
It is a frontend submodule (not the full repository) responsible for:

- collecting problem input,
- launching optimization in the Python backend,
- displaying results (including Gantt visualization).

## Scope

This README documents only the UI module located in `Demo_UI/`.
Repository-wide architecture, Python internals, and research/benchmark details are documented in the root-level docs.

## Tech Stack

- Java 17
- JavaFX 21.0.1
- Maven 3.6+
- Gson 2.10.1

## Project Layout

```text
Demo_UI/
└── javafx-ui/
    ├── pom.xml
    ├── src/main/java/pl/pwr/inz/hfs/ui/
    │   ├── SchedulerApplication.java
    │   ├── model/
    │   ├── service/PythonService.java
    │   └── view/
    └── src/main/resources/
        ├── images/
        └── styles/application.css
```

## Key Components

- SchedulerApplication: application entry point and stage setup.
- View layer: algorithm selection, input forms, progress screen, and results screen.
- PythonService: JSON-based integration with the Python solver.

## Supported Algorithms (UI Selection)

The UI allows selecting the algorithms exposed by the backend (for example: greedy, tabu, branch-and-bound).
Final availability depends on backend implementation and input constraints.

## Input and Output Contract

- Input payload: JSON problem instance saved in the data directory.
- Output payload: JSON result file read from `results/result.json`.
- The UI expects valid matrix dimensions for processing and setup times.
- The UI performs validation before process launch, but backend validation remains authoritative.

## Runtime Flow

1. User selects an algorithm and enters instance parameters.
2. UI saves input as JSON in the data directory.
3. UI runs Python/main.py.
4. UI reads results from results/result.json.
5. Results view shows Cmax and schedule output.

## Run

From this module:

```bash
cd Demo_UI/javafx-ui
mvn clean javafx:run
```

Or from repository root:

```bash
start.bat
```

## Integration Notes

- Input files are written to ../data/.
- Output is read from ../results/result.json.
- Python must be available and the Python module directory must exist.

## Configuration Notes

- Java version: use Java 17 for compatibility with the current build.
- Build tool: Maven wrapper is not included, so use system Maven.
- Relative paths are resolved from the runtime working directory; run from expected project locations.

## Development Notes

- Keep view classes focused on presentation and user interaction.
- Put process orchestration and file I/O in service classes.
- Keep JSON models aligned with backend schema changes.
- Avoid committing generated runtime files.

## Troubleshooting

- Python not found: verify PATH and repository structure.
- No results shown: check Python process logs and confirm results/result.json exists.
- Maven build issues: run mvn clean install in Demo_UI/javafx-ui.

## Quick Verification Checklist

1. App starts with `mvn clean javafx:run`.
2. Algorithm selection and form navigation work correctly.
3. A JSON input file is created in the data directory.
4. Python process completes without runtime errors.
5. Results screen shows objective value and schedule output.

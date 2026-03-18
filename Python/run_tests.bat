@echo off
REM Skrypt do uruchamiania testów jednostkowych
REM Użycie: run_tests.bat [opcje]

setlocal

echo ============================================
echo   Testy jednostkowe HFS-SDST Scheduler
echo ============================================
echo.

REM Sprawdź czy pytest jest zainstalowany
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [BŁĄD] pytest nie jest zainstalowany!
    echo Zainstaluj zależności: pip install -r requirements-test.txt
    exit /b 1
)

REM Jeśli podano argument, użyj go
if not "%~1"=="" (
    echo Uruchamianie testów: %*
    python -m pytest %*
    goto :end
)

REM Domyślne uruchomienie wszystkich testów
echo Uruchamianie wszystkich testów...
echo.

REM Uruchom testy modułami (aby uniknąć problemów ze stdout)
echo [1/8] Testy klasy Job...
python -m pytest tests/test_job.py -v --tb=line

echo.
echo [2/8] Testy klasy Machine...
python -m pytest tests/test_machine.py -v --tb=line

echo.
echo [3/8] Testy klasy Schedule...
python -m pytest tests/test_schedule.py -v --tb=line

echo.
echo [4/8] Testy algorytmu MinSTF...
python -m pytest tests/test_greedy.py -v --tb=line

echo.
echo [5/8] Testy algorytmu Tabu Search...
python -m pytest tests/test_tabu_search.py -v --tb=line

echo.
echo [6/8] Testy algorytmu Branch and Bound...
python -m pytest tests/test_branch_and_bound.py -v --tb=line

echo.
echo [7/8] Testy GanttChart...
python -m pytest tests/test_gantt_chart.py -v --tb=line --capture=no

echo.
echo [8/8] Testy głównego modułu...
python -m pytest tests/test_main.py -v --tb=line --capture=no

echo.
echo ============================================
echo   Wszystkie testy zakończone!
echo ============================================

:end
endlocal

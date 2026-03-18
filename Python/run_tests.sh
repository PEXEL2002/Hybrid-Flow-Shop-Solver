#!/bin/bash
# Skrypt do uruchamiania testów jednostkowych (Linux/Mac)
# Użycie: ./run_tests.sh [opcje]

set -e

echo "============================================"
echo "   Testy jednostkowe HFS-SDST Scheduler"
echo "============================================"
echo ""

# Sprawdź czy pytest jest zainstalowany
if ! python -m pytest --version > /dev/null 2>&1; then
    echo "[BŁĄD] pytest nie jest zainstalowany!"
    echo "Zainstaluj zależności: pip install -r requirements-test.txt"
    exit 1
fi

# Jeśli podano argument, użyj go
if [ $# -gt 0 ]; then
    echo "Uruchamianie testów: $@"
    python -m pytest "$@"
    exit 0
fi

# Domyślne uruchomienie wszystkich testów
echo "Uruchamianie wszystkich testów..."
echo ""

echo "[1/8] Testy klasy Job..."
python -m pytest tests/test_job.py -v --tb=line

echo ""
echo "[2/8] Testy klasy Machine..."
python -m pytest tests/test_machine.py -v --tb=line

echo ""
echo "[3/8] Testy klasy Schedule..."
python -m pytest tests/test_schedule.py -v --tb=line

echo ""
echo "[4/8] Testy algorytmu MinSTF..."
python -m pytest tests/test_greedy.py -v --tb=line

echo ""
echo "[5/8] Testy algorytmu Tabu Search..."
python -m pytest tests/test_tabu_search.py -v --tb=line

echo ""
echo "[6/8] Testy algorytmu Branch and Bound..."
python -m pytest tests/test_branch_and_bound.py -v --tb=line

echo ""
echo "[7/8] Testy GanttChart..."
python -m pytest tests/test_gantt_chart.py -v --tb=line --capture=no

echo ""
echo "[8/8] Testy głównego modułu..."
python -m pytest tests/test_main.py -v --tb=line --capture=no

echo ""
echo "============================================"
echo "   Wszystkie testy zakończone!"
echo "============================================"

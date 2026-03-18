@echo off
REM Skrypt do uruchamiania testów z pokryciem kodu
REM Generuje raport HTML w katalogu htmlcov/

setlocal

echo ============================================
echo   Testy z pokryciem kodu
echo ============================================
echo.

REM Sprawdź czy pytest-cov jest zainstalowany
python -c "import pytest_cov" >nul 2>&1
if errorlevel 1 (
    echo [BŁĄD] pytest-cov nie jest zainstalowany!
    echo Zainstaluj zależności: pip install -r requirements-test.txt
    exit /b 1
)

echo Uruchamianie testów z pomiarem pokrycia...
echo.

REM Uruchom testy z pokryciem dla poszczególnych modułów
python -m pytest ^
    tests/test_job.py ^
    tests/test_machine.py ^
    tests/test_schedule.py ^
    tests/test_greedy.py ^
    tests/test_tabu_search.py ^
    tests/test_branch_and_bound.py ^
    --cov=core ^
    --cov=algorithms ^
    --cov=utils ^
    --cov-report=html ^
    --cov-report=term-missing ^
    -v

echo.
echo ============================================
echo   Raport pokrycia wygenerowany!
echo ============================================
echo.
echo Raport HTML: htmlcov\index.html
echo.
echo Aby otworzyć raport:
echo   start htmlcov\index.html
echo.

endlocal

# Quick Start - Testy Jednostkowe

Szybki przewodnik po testach jednostkowych dla projektu HFS-SDST.

## ⚡ Szybki Start (Windows)

```bash
# 1. Zainstaluj zależności testowe
pip install -r requirements-test.txt

# 2. Uruchom wszystkie testy
run_tests.bat

# 3. Zobacz pokrycie kodu
run_tests_coverage.bat
```

## ⚡ Szybki Start (Linux/Mac)

```bash
# 1. Zainstaluj zależności testowe
pip install -r requirements-test.txt

# 2. Nadaj uprawnienia do wykonania
chmod +x run_tests.sh

# 3. Uruchom wszystkie testy
./run_tests.sh

# 4. Zobacz pokrycie kodu
pytest tests/ --cov=core --cov=algorithms --cov=utils --cov-report=html
```

## 📊 Statystyki

- **Liczba testów**: 159+
- **Plików testowych**: 8
- **Pokrycie kodu**: ~90%
- **Czas wykonania**: ~3-5 sekund

## 🎯 Najczęściej Używane Komendy

### Uruchom wszystkie testy
```bash
pytest
```

### Uruchom konkretny plik
```bash
pytest tests/test_job.py
```

### Uruchom z verbose output
```bash
pytest -v
```

### Uruchom z pokryciem kodu
```bash
pytest --cov=core --cov=algorithms --cov=utils
```

### Uruchom szybko (równolegle)
```bash
pytest -n auto
```

### Tylko testy, które nie przeszły ostatnio
```bash
pytest --lf
```

## 📁 Struktura Testów

```
tests/
├── conftest.py              # Fixtures (dane testowe)
├── test_job.py              # Testy Job (18 testów)
├── test_machine.py          # Testy Machine (27 testów)
├── test_schedule.py         # Testy Schedule (34 testy)
├── test_greedy.py           # Testy MinSTF (22 testy)
├── test_tabu_search.py      # Testy Tabu Search (36 testów)
├── test_branch_and_bound.py # Testy B&B (18 testów)
├── test_gantt_chart.py      # Testy GanttChart (24 testy)
└── test_main.py             # Testy main.py (?)
```

## ✅ Co Jest Testowane

### Core
- ✅ Job: inicjalizacja, czasy, walidacja
- ✅ Machine: stany, uczenie, operacje
- ✅ Schedule: budowa, reset, I/O

### Algorytmy
- ✅ MinSTF: heurystyka, zachłanność
- ✅ Tabu Search: lista tabu, aspiracja, zbieżność
- ✅ Branch & Bound: bounding, optymalizacja

### Utilities
- ✅ GanttChart: generowanie, zapis, wykrywanie struktury
- ✅ Main: CLI, workflow, integracja

## 🔧 Debugging

### Pojedynczy test z debugowaniem
```bash
pytest tests/test_job.py::test_name -vv -s --pdb
```

### Pokaż print statements
```bash
pytest -s
```

### Zatrzymaj na pierwszym błędzie
```bash
pytest -x
```

## 📈 Generowanie Raportu HTML

```bash
# Windows
run_tests_coverage.bat

# Linux/Mac
pytest --cov=core --cov=algorithms --cov=utils --cov-report=html
# Otwórz: htmlcov/index.html
```

## 🎓 Przykłady

### Dodaj nowy test
```python
# tests/test_job.py

def test_my_new_feature(sample_job):
    """Test nowej funkcjonalności."""
    # Arrange
    expected_value = 42

    # Act
    result = sample_job.my_new_method()

    # Assert
    assert result == expected_value
```

### Użyj fixture
```python
def test_with_schedule(sample_schedule):
    """Test używający fixture sample_schedule."""
    # Fixture automatycznie wstrzykiwany
    assert len(sample_schedule.jobs) > 0
```

### Mock zewnętrznej zależności
```python
from unittest.mock import patch

@patch('matplotlib.pyplot.savefig')
def test_with_mock(mock_savefig):
    """Test z mockiem matplotlib."""
    # Test bez rzeczywistego zapisu pliku
    gantt.save('test.png')
    assert mock_savefig.called
```

## 💡 Wskazówki

1. **Uruchamiaj testy często** - minimum przed każdym commitem
2. **Testy powinny być szybkie** - 159 testów w ~3 sekundy
3. **Używaj fixtures** - unikaj duplikacji kodu setupu
4. **Mockuj zależności** - testy nie powinny tworzyć prawdziwych plików
5. **Nazwy testów opisowe** - `test_compute_cmax_finds_maximum`

## 🚨 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pytest'"
**Rozwiązanie**: `pip install -r requirements-test.txt`

### Problem: "ValueError: I/O operation on closed file"
**Rozwiązanie**: Użyj `--capture=no` lub uruchom testy pojedynczo

### Problem: Testy powolne
**Rozwiązanie**: `pytest -n auto` (równoległe uruchomienie)

## 📚 Więcej Informacji

Zobacz [README.md](README.md) dla pełnej dokumentacji testów.

---

**Szybkie polecenia**:
- `pytest` - uruchom wszystkie testy
- `pytest -v` - verbose output
- `pytest --cov` - z pokryciem
- `pytest -n auto` - równolegle
- `pytest -x` - stop na błędzie

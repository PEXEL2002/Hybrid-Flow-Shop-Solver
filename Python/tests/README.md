# Testy Jednostkowe - HFS-SDST Scheduler

Kompleksowe testy jednostkowe dla systemu optymalizacji harmonogramów HFS-SDST (Hybrid Flow Shop with Sequence-Dependent Setup Times).

## 📋 Spis Treści

- [Instalacja](#instalacja)
- [Uruchamianie Testów](#uruchamianie-testów)
- [Struktura Testów](#struktura-testów)
- [Pokrycie Kodu](#pokrycie-kodu)
- [Konwencje](#konwencje)

## 🔧 Instalacja

### 1. Zainstaluj zależności testowe

```bash
cd Python
pip install -r requirements-test.txt
```

### 2. Zainstaluj zależności projektu (jeśli jeszcze nie zainstalowano)

```bash
pip install matplotlib
```

## 🚀 Uruchamianie Testów

### Wszystkie testy

```bash
pytest
```

### Konkretny plik testowy

```bash
pytest tests/test_job.py
pytest tests/test_machine.py
pytest tests/test_schedule.py
pytest tests/test_greedy.py
pytest tests/test_tabu_search.py
pytest tests/test_branch_and_bound.py
pytest tests/test_gantt_chart.py
pytest tests/test_main.py
```

### Konkretna klasa lub test

```bash
# Konkretna klasa testowa
pytest tests/test_job.py::TestJobInitialization

# Konkretny test
pytest tests/test_job.py::TestJobInitialization::test_job_creation_with_valid_data
```

### Z wyświetlaniem szczegółów

```bash
# Verbose mode
pytest -v

# Bardzo szczegółowy output
pytest -vv

# Pokaż print statements
pytest -s
```

### Równoległe uruchamianie (szybsze)

```bash
# Użyj wszystkich rdzeni procesora
pytest -n auto

# Użyj określonej liczby rdzeni
pytest -n 4
```

### Z pokryciem kodu

```bash
# Podstawowy raport pokrycia
pytest --cov=core --cov=algorithms --cov=utils

# Raport HTML
pytest --cov=core --cov=algorithms --cov=utils --cov-report=html

# Raport w terminalu z brakującymi liniami
pytest --cov=core --cov=algorithms --cov=utils --cov-report=term-missing
```

### Tylko szybkie testy (bez integracyjnych)

```bash
pytest -m "not slow"
```

## 📁 Struktura Testów

```
tests/
├── __init__.py              # Pakiet testów
├── conftest.py              # Fixtures współdzielone między testami
├── test_job.py              # Testy dla klasy Job
├── test_machine.py          # Testy dla klasy Machine
├── test_schedule.py         # Testy dla klasy Schedule
├── test_greedy.py           # Testy dla algorytmu MinSTF
├── test_tabu_search.py      # Testy dla algorytmu Tabu Search
├── test_branch_and_bound.py # Testy dla algorytmu Branch & Bound
├── test_gantt_chart.py      # Testy dla generatora wykresów Gantta
└── test_main.py             # Testy dla głównego modułu programu
```

## 📊 Szczegółowy Opis Testów

### test_job.py (Klasa Job)
- **TestJobInitialization**: Tworzenie obiektów zadań
- **TestJobGetProcessingTime**: Pobieranie czasów przetwarzania
- **TestJobGetSetupTime**: Pobieranie czasów przezbrojenia
- **TestJobSetStageTimes**: Ustawianie i walidacja czasów

**Pokrycie**: Inicjalizacja, gettery, settery, walidacja danych

### test_machine.py (Klasa Machine)
- **TestMachineInitialization**: Tworzenie maszyn
- **TestMachineStartSetup**: Operacje przezbrojenia
- **TestMachineStartProcessing**: Operacje przetwarzania
- **TestMachineComputeProcessingTime**: Efekt krzywej uczenia
- **TestMachineIntegration**: Scenariusze integracyjne

**Pokrycie**: Cykl życia maszyny, efekt uczenia, zarządzanie stanem

### test_schedule.py (Klasa Schedule)
- **TestScheduleInitialization**: Tworzenie harmonogramu
- **TestScheduleLoadFromJson**: Wczytywanie danych z JSON
- **TestScheduleBuildFromSequence**: Budowa harmonogramu z sekwencji
- **TestScheduleComputeCmax**: Obliczanie makespan
- **TestScheduleResetRuntimeState**: Reset stanu
- **TestScheduleIntegration**: Pełne scenariusze

**Pokrycie**: I/O, budowa harmonogramu, obliczenia, persistence

### test_greedy.py (Algorytm MinSTF)
- **TestMinSTFInitialization**: Inicjalizacja algorytmu
- **TestMinSTFCalculateSetupTime**: Obliczanie czasów przezbrojenia
- **TestMinSTFRun**: Uruchamianie algorytmu
- **TestMinSTFGreedyLogic**: Logika zachłanna
- **TestMinSTFEdgeCases**: Przypadki brzegowe

**Pokrycie**: Heurystyka, deterministyczność, optymalizacja

### test_tabu_search.py (Algorytm Tabu Search)
- **TestTabuSearchInitialization**: Parametry algorytmu
- **TestTabuSearchGenerateNeighborhood**: Generowanie sąsiedztwa
- **TestTabuSearchIsTabu**: Lista tabu
- **TestTabuSearchSelectBestNeighbor**: Kryterium aspiracji
- **TestTabuSearchRun**: Pełne działanie algorytmu
- **TestTabuSearchIntegration**: Porównanie z innymi algorytmami

**Pokrycie**: Metaheurystyka, lista tabu, kryterium aspiracji, zbieżność

### test_branch_and_bound.py (Algorytm B&B)
- **TestBranchAndBoundComputeLowerBound**: Dolne ograniczenia
- **TestBranchAndBoundRun**: Przeszukiwanie drzewa
- **TestBranchAndBoundOptimality**: Weryfikacja optymalności
- **TestBranchAndBoundPruning**: Obcinanie gałęzi

**Pokrycie**: Algorytm dokładny, bounding, optymalność

### test_gantt_chart.py (Wykresy Gantta)
- **TestGanttChartInitialization**: Tworzenie wykresów
- **TestGanttChartFromFile**: Wczytywanie z pliku
- **TestGanttChartGenerate**: Generowanie wizualizacji
- **TestGanttChartSave**: Zapisywanie do pliku

**Pokrycie**: Wizualizacja, I/O, rendering (z mockami matplotlib)

### test_main.py (Główny program)
- **TestGetResultsDir**: Zarządzanie katalogami
- **TestRunAlgorithm**: Uruchamianie algorytmów
- **TestMainFunction**: Parsowanie argumentów CLI
- **TestMainIntegration**: Pełne scenariusze end-to-end

**Pokrycie**: CLI, workflow, integracja komponentów

## 🎯 Pokrycie Kodu

### Generowanie raportu pokrycia

```bash
# Terminal report
pytest --cov=core --cov=algorithms --cov=utils --cov-report=term-missing

# HTML report (bardziej czytelny)
pytest --cov=core --cov=algorithms --cov=utils --cov-report=html
# Otwórz: htmlcov/index.html
```

### Oczekiwane pokrycie

- **core/**: ~95%
- **algorithms/**: ~90%
- **utils/**: ~85%
- **main.py**: ~80%

## 🧪 Fixtures (conftest.py)

### Dostępne fixtures

- `sample_setup_times`: Przykładowe czasy przezbrojenia
- `sample_processing_times`: Przykładowe czasy przetwarzania
- `sample_job`: Przykładowy obiekt Job
- `sample_machine`: Przykładowa maszyna bez uczenia
- `sample_learning_machine`: Maszyna z efektem uczenia
- `sample_schedule_data`: Dane harmonogramu w pliku JSON
- `sample_schedule`: Załadowany obiekt Schedule
- `sample_result_data`: Przykładowe wyniki algorytmu
- `temp_json_file`: Generator tymczasowych plików JSON
- `mock_matplotlib`: Mock dla matplotlib (testy bez GUI)

### Przykład użycia

```python
def test_my_feature(sample_schedule, sample_job):
    """Test wykorzystujący fixtures."""
    # sample_schedule i sample_job są automatycznie wstrzykiwane
    assert len(sample_schedule.jobs) > 0
    assert sample_job.id >= 0
```

## 📝 Konwencje

### Nazewnictwo testów

```python
def test_<co_testujesz>_<scenariusz>():
    """Krótki opis co test sprawdza."""
    # Arrange (przygotowanie)
    # Act (wykonanie)
    # Assert (weryfikacja)
```

### Organizacja klas testowych

```python
class TestFeatureName:
    """Testy dla konkretnej funkcjonalności."""

    def test_basic_case(self):
        """Test podstawowego przypadku."""
        pass

    def test_edge_case(self):
        """Test przypadku brzegowego."""
        pass
```

### Mocki i Patche

```python
from unittest.mock import Mock, patch, MagicMock

# Mock obiektu
@patch('module.ClassName')
def test_with_mock(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance
    # Test

# Mock funkcji
@patch('builtins.print')
def test_print_output(mock_print):
    # Test
    assert mock_print.called
```

## 🐛 Debugging Testów

### Uruchom jeden test w trybie debug

```bash
pytest tests/test_job.py::test_name -vv -s
```

### Zatrzymaj na pierwszym błędzie

```bash
pytest -x
```

### Pokaż lokalne zmienne przy błędzie

```bash
pytest -l
```

### Interaktywny debugger przy błędzie

```bash
pytest --pdb
```

## 📈 Continuous Integration

### GitHub Actions (przykładowy workflow)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 💡 Wskazówki

1. **Uruchamiaj testy często** podczas development
2. **Pisz testy przed fixem** (TDD) dla bugów
3. **Używaj fixtures** zamiast duplikować kod setupu
4. **Mockuj zależności zewnętrzne** (pliki, network, matplotlib)
5. **Testy powinny być szybkie** (< 1s na test)
6. **Każdy test powinien testować jedną rzecz**
7. **Używaj opisowych nazw** testów i komunikatów assert

## 🤝 Contribution

Przy dodawaniu nowego kodu:

1. Napisz testy jednostkowe
2. Upewnij się, że wszystkie testy przechodzą: `pytest`
3. Sprawdź pokrycie: `pytest --cov`
4. Cel: pokrycie ≥ 85%

## 📞 Wsparcie

W przypadku problemów z testami:

1. Sprawdź logi pytest: `pytest -vv`
2. Uruchom konkretny test w trybie debug: `pytest -vv -s test_file.py::test_name`
3. Sprawdź fixture w conftest.py
4. Zweryfikuj wersje zależności: `pip list`

---

**Autor**: System testów jednostkowych dla HFS-SDST Scheduler
**Wersja**: 1.0
**Framework**: pytest 7.4+
**Python**: 3.8+

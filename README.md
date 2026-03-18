# Aplikacja Harmonogramowania Produkcji HFS

**Autor:** Bartłomiej Adam Kuk
**Temat:** Aplikacja wspomagająca harmonogramowanie produkcji dla wybranego zagadnienia szeregowania zadań

## Opis

Aplikacja do harmonogramowania produkcji dla problemu Hybrid Flow Shop z sekwencyjnie-zależnymi czasami przezbrojeń (HFS-SDST) z efektem uczenia się.

## Wymagania

- **Java** 17 lub nowsza - [Pobierz tutaj](https://adoptium.net/)
- **Maven** 3.6+ - [Pobierz tutaj](https://maven.apache.org/download.cgi)
- **Python** 3.8+ - [Pobierz tutaj](https://www.python.org/downloads/)

## Szybkie uruchomienie

### Windows

Uruchom plik `start.bat` w głównym folderze projektu:

```bash
start.bat
```

Skrypt automatycznie:
1. Sprawdzi wszystkie wymagania
2. Zainstaluje zależności Python
3. Uruchomi aplikację

### Ręczne uruchomienie

#### 1. Instalacja zależności Python

```bash
cd Python
pip install -r requirements.txt
cd ..
```

#### 2. Uruchomienie aplikacji Java

```bash
cd Demo_UI/javafx-ui
mvn javafx:run
```

## Struktura projektu

```
inz/
├── start.bat              # Skrypt uruchamiający całą aplikację
├── README.md              # Ten plik
├── Demo_UI/              # Interfejs graficzny (Java + JavaFX)
│   ├── README.md         # Dokumentacja Demo_UI
│   └── javafx-ui/
│       └── src/          # Kod źródłowy aplikacji
├── Python/               # Część obliczeniowa (algorytmy)
│   ├── README.md         # Dokumentacja Python
│   ├── main.py           # Główny skrypt Python
│   ├── requirements.txt  # Zależności Python
│   ├── algorithms/       # Implementacje algorytmów
│   ├── core/             # Klasy bazowe
│   └── utils/            # Narzędzia pomocnicze
├── data/                 # Folder na dane wejściowe (pliki JSON)
└── results/              # Folder na wyniki (JSON + diagramy PNG)
```

## Algorytmy

Aplikacja implementuje następujące algorytmy:

1. **Greedy MSTF** - algorytm zachłanny (Minimum Setup Time First)
2. **Tabu Search** - przeszukiwanie tabu
3. **Branch & Bound** - metoda podziału i ograniczeń

## Format danych wejściowych

Aplikacja przyjmuje dane w formacie JSON:

```json
{
  "algorithm": "bnb",
  "num_stages": 2,
  "num_jobs": 3,
  "machines_per_stage": [1, 2],
  "learning_coeff": 0.15,
  "learning_stages": "10",
  "processing_times": [...],
  "setup_times": [...]
}
```

## Format wyników

Wyniki są zapisywane w pliku `result.json`:

```json
{
  "time_in_ms": 3123,
  "Algorithm": "Branch & Bound",
  "gant_diagram": "<ścieżka do diagramu>",
  "C_max": 101.48,
  "schedule": [...]
}
```

## Workflow danych

1. **Wprowadzanie danych** → Użytkownik wprowadza parametry w Demo_UI
2. **Zapis instancji** → Dane zapisywane do `data/input_<timestamp>.json`
3. **Wywołanie Pythona** → Demo_UI uruchamia `Python/main.py` z plikiem wejściowym
4. **Optymalizacja** → Python wykonuje algorytm i zapisuje wyniki do `results/result.json`
5. **Wizualizacja** → Demo_UI odczytuje wyniki i wyświetla użytkownikowi

## Problem HFS-SDST z efektem uczenia się

- **HFS** = Hybrid Flow Shop (warsztaty przepływowe z maszynami równoległymi)
- **SDST** = Sequence-Dependent Setup Times (czasy przezbrojeń zależne od sekwencji)
- **Efekt uczenia się**: Im więcej zadań wykonano, tym szybciej są przetwarzane

**Cel:** Minimalizacja C_max (czasu zakończenia ostatniego zadania)

## Ograniczenia

- Maksymalna liczba zadań: **50**
- Maksymalna liczba etapów: **20**
- Algorytm B&B zalecany tylko dla ≤10 zadań (czas obliczeniowy rośnie wykładniczo)

## Wsparcie techniczne

W przypadku problemów sprawdź:
1. Czy wszystkie wymagania są zainstalowane
2. Czy Java, Maven i Python są dodane do PATH
3. Logi w konsoli podczas uruchamiania
4. Czy foldery `data/` i `results/` istnieją

## Licencja

Projekt stworzony na potrzeby pracy inżynierskiej.
Politechnika Wrocławska © 2024

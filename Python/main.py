"""Program główny do optymalizacji harmonogramu HFS-SDST.

Przykłady użycia:
    python main.py --test           # benchmark wszystkich algorytmów
    python main.py                  # oblicz dla default.json
    python main.py data.json        # oblicz dla data.json
    python main.py data.json --plot # oblicz i wygeneruj wykres Gantta
"""

import sys
import argparse
import json
import os

from core.schedule import Schedule
from algorithms.greedy import MinSTF
from algorithms.tabu_search import TabuSearch
from algorithms.branch_and_bound import BranchAndBound
from benchmark import run_benchmark
from utils.gantt_chart import GanttChart


def get_results_dir():
    """Zwraca ścieżkę do katalogu results.

    Returns:
        str: Ścieżka absolutna do katalogu results.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.abspath(os.path.join(script_dir, "..", "results"))
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def generate_gantt_only(input_file, output_file=None):
    """Generuje wykres Gantta z istniejącego pliku harmonogramu.

    Args:
        input_file (str): Ścieżka do pliku JSON z harmonogramem.
        output_file (str, optional): Ścieżka do pliku wyjściowego PNG.

    Returns:
        str: Ścieżka do wygenerowanego wykresu.
    """
    print(f"[GANTT] Wczytywanie harmonogramu z: {input_file}")

    try:
        gantt = GanttChart.from_file(input_file)
        gantt.print_info()

        if output_file is None:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(get_results_dir(), f"{base_name}_gantt.png")

        print(f"\n[GANTT] Generowanie wykresu Gantta...")
        print(f"[GANTT] Plik wyjściowy: {output_file}")

        saved_path = gantt.save(output_file, show=False, update_source=True)

        if os.path.exists(saved_path):
            file_size = os.path.getsize(saved_path)
            print(f"[SUCCESS] Wykres Gantta zapisany pomyślnie!")
            print(f"[SUCCESS] Lokalizacja: {saved_path}")
            print(f"[SUCCESS] Rozmiar: {file_size / 1024:.1f} KB")
            print(f"[UPDATE] Zaktualizowano plik {input_file} z nową ścieżką do wykresu")
            return saved_path
        else:
            print("[ERROR] Nie udało się utworzyć pliku wykresu")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Błąd parsowania JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_algorithm(input_file, plot=False):
    """Uruchamia algorytm optymalizacji określony w pliku JSON.

    Args:
        input_file (str): Ścieżka do pliku z danymi wejściowymi.
        plot (bool, optional): Czy wygenerować wykres Gantta. Domyślnie False.

    Returns:
        dict: Wyniki działania algorytmu.
    """

    print(f"\n[MAIN] Wczytywanie danych z pliku: {input_file}")

    # Wczytaj dane
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Pobierz algorytm z pliku JSON (domyślnie tabu)
    algorithm = data.get("algorithm", "tabu").lower()

    schedule = Schedule()
    schedule.load_from_json(input_file)

    print(f"[MAIN] Dane wejsciowe:")
    print(f"  - Algorytm: {algorithm}")
    print(f"  - Liczba zadan: {len(schedule.jobs)}")
    print(f"  - Liczba etapow: {schedule.num_stages}")
    print(f"  - Maszyny na etapach: {schedule.machines_per_stage}")
    print(f"  - Wspolczynnik uczenia (alpha): {schedule.learning_coeff}")
    print(f"  - Etapy z uczeniem: {schedule.learning_stages}")

    # Wybór algorytmu
    algo_map = {
        "greedy": ("MinSTF", MinSTF),
        "tabu": ("Tabu Search", TabuSearch),
        "bnb": ("Branch & Bound", BranchAndBound),
        "b&b": ("Branch & Bound", BranchAndBound)
    }

    if algorithm not in algo_map:
        print(f"[ERROR] Nieznany algorytm: {algorithm}")
        print(f"[ERROR] Dostepne algorytmy: greedy, tabu, bnb")
        sys.exit(1)

    algo_name, algo_class = algo_map[algorithm]
    print(f"\n[MAIN] Uruchamianie algorytmu: {algo_name}")

    # Uruchomienie algorytmu
    if algorithm in ["tabu"]:
        algo = algo_class(schedule, max_iter=100, tabu_tenure=10, no_improve_limit=10)
    else:
        algo = algo_class(schedule)

    internal_results = algo.run()

    # Przygotuj wyniki w wymaganym formacie
    results = {
        "time_in_ms": internal_results["time_in_ms"],
        "Algorithm": algo_name,
        "C_max": internal_results["C_max"],
        "schedule": internal_results["schedule"]
    }

    # Wyświetl wyniki
    print(f"\n[MAIN] Wyniki:")
    print(f"  - Algorytm: {results['Algorithm']}")
    print(f"  - C_max: {results['C_max']:.2f}")
    print(f"  - Czas wykonania: {results['time_in_ms'] / 1000:.3f}s")
    print(f"  - Sekwencja: {algo.best_sequence}")

    # Pobierz katalog results
    results_dir = get_results_dir()

    # Generowanie diagramu Gantta (zawsze)
    gantt_file = os.path.join(results_dir, "result_gantt.png")
    print(f"\n[GANTT] Generowanie diagramu Gantta...")
    print(f"[GANTT] Sciezka do diagramu: {gantt_file}")
    try:
        # Utwórz wykres bezpośrednio z wyników (bez tymczasowego pliku)
        gantt = GanttChart.from_results(results)
        gantt.save(gantt_file, show=plot, update_source=False)

        print(f"[GANTT] Zapisano diagram do: {gantt_file}")

        # Dodaj ścieżkę do diagramu w wynikach - już mamy absolutną ścieżkę
        results["gant_diagram"] = gantt_file

    except Exception as e:
        print(f"[WARNING] Blad podczas generowania diagramu Gantta: {e}")
        import traceback
        traceback.print_exc()
        results["gant_diagram"] = None

    # Zapis wyników do result.json (z informacją o diagramie)
    output_file = os.path.join(results_dir, "result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\n[OUTPUT] Zapisano wyniki do: {output_file}")

    return results


def main():
    """Główna funkcja programu."""

    parser = argparse.ArgumentParser(
        description="Optymalizacja harmonogramu HFS-SDST",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python main.py --test                      # benchmark wszystkich algorytmów
  python main.py                             # oblicz dla default.json
  python main.py data.json                   # oblicz dla data.json
  python main.py data.json --plot            # oblicz i wygeneruj wykres Gantta
  python main.py --gantt result.json         # wygeneruj wykres Gantta z istniejącego harmonogramu
  python main.py --gantt result.json out.png # wygeneruj wykres Gantta do pliku out.png

Uwaga: Algorytm jest określany w pliku JSON (pole "algorithm": "tabu"|"greedy"|"bnb")
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Uruchom benchmark wszystkich algorytmow"
    )

    parser.add_argument(
        "--plot",
        action="store_true",
        help="Wygeneruj wykres Gantta"
    )

    parser.add_argument(
        "--gantt",
        metavar="SCHEDULE_FILE",
        help="Generuj tylko wykres Gantta z istniejącego harmonogramu"
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        default="../data/default.json",
        help="Plik wejsciowy z danymi (domyslnie: ../data/default.json)"
    )

    parser.add_argument(
        "output_file",
        nargs="?",
        help="Plik wyjściowy dla wykresu Gantta (używane z --gantt)"
    )

    args = parser.parse_args()

    # Tryb testowy - benchmark
    if args.test:
        print("[MAIN] Uruchamianie benchmarku...")
        run_benchmark(input_file="../data/test.json", output_dir="../results")
        return

    # Tryb generowania wykresu Gantta z istniejącego harmonogramu
    if args.gantt:
        if not os.path.exists(args.gantt):
            print(f"[ERROR] Plik nie istnieje: {args.gantt}")
            sys.exit(1)

        generate_gantt_only(args.gantt, args.input_file if args.input_file != "../data/default.json" else None)
        return

    # Tryb normalny - pojedynczy algorytm
    if not os.path.exists(args.input_file):
        print(f"[ERROR] Plik nie istnieje: {args.input_file}")
        sys.exit(1)

    run_algorithm(
        input_file=args.input_file,
        plot=args.plot
    )


if __name__ == "__main__":
    main()

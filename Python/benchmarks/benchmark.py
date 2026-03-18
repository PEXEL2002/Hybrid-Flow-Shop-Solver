"""
Moduł do porównawczego testowania algorytmów optymalizacji HFS-SDST.

Funkcja run_benchmark() uruchamia wszystkie algorytmy (Natural, Greedy, Tabu Search, B&B)
i generuje szczegółowy raport porównawczy.
"""

import sys
import io
import json
import os

# Ustawienie kodowania UTF-8 dla Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from core.schedule import Schedule
from algorithms.branch_and_bound import BranchAndBound
from algorithms.greedy import MinSTF
from algorithms.tabu_search import TabuSearch
from utils.gantt_chart import generate_gantt_from_file


def print_separator(title=None):
    """Wyświetla separator wizualny."""
    if title:
        print(f"\n{'='*80}")
        print(f"{title:^80}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}")


def run_benchmark(input_file="test_8jobs_2stages.json", output_dir="../results"):
    """
    Uruchamia benchmark wszystkich algorytmów i generuje raport porównawczy.

    Args:
        input_file (str): ścieżka do pliku z danymi wejściowymi
        output_dir (str): katalog do zapisu wyników

    Returns:
        dict: słownik z wynikami wszystkich algorytmów
    """

    os.makedirs(output_dir, exist_ok=True)

    print_separator("TESTY ALGORYTMOW OPTYMALIZACJI HFS-SDST")

    # Wczytaj dane i wyświetl informacje
    print(f"\n[DATA] Wczytano dane z pliku: {input_file}")
    schedule_natural = Schedule()
    schedule_natural.load_from_json(input_file)
    print(f"  - Liczba zadan: {len(schedule_natural.jobs)}")
    print(f"  - Liczba etapow: {schedule_natural.num_stages}")
    print(f"  - Maszyny na etapach: {schedule_natural.machines_per_stage}")
    print(f"  - Wspolczynnik uczenia (alpha): {schedule_natural.learning_coeff}")
    print(f"  - Etapy z uczeniem: {schedule_natural.learning_stages}")

    # ========================================================================
    # TEST 1: Permutacja naturalna
    # ========================================================================

    print("\n[NATURAL] Budowanie harmonogramu naturalnego...")
    cmax_natural = schedule_natural.build_from_sequence(list(range(len(schedule_natural.jobs))))
    natural_sequence = list(range(len(schedule_natural.jobs)))

    print(f"[NATURAL] C_max = {cmax_natural:.2f}")

    # Zapis harmonogramu naturalnego
    natural_out = os.path.join(output_dir, "natural_schedule.json")
    natural_data = {
        "algorithm": "Natural Order",
        "C_max": cmax_natural,
        "time_in_ms": 0,
        "schedule": schedule_natural.schedule
    }

    with open(natural_out, "w", encoding="utf-8") as f:
        json.dump(natural_data, f, indent=4, ensure_ascii=False)
    print(f"[OUTPUT] Zapisano: {natural_out}")

    # Generowanie diagramu Gantta dla Natural
    try:
        natural_gantt = os.path.join(output_dir, "natural_gantt.png")
        generate_gantt_from_file(natural_out, natural_gantt, show=False)
        natural_data["gantt_diagram"] = natural_gantt
        # Zaktualizuj plik JSON z informacją o diagramie
        with open(natural_out, "w", encoding="utf-8") as f:
            json.dump(natural_data, f, indent=4, ensure_ascii=False)
        print(f"[GANTT] Wygenerowano diagram: {natural_gantt}")
    except Exception as e:
        print(f"[WARNING] Błąd generowania diagramu: {e}")
        natural_data["gantt_diagram"] = None

    # ========================================================================
    # TEST 2: Algorytm Greedy MSTF
    # ========================================================================

    schedule_greedy = Schedule()
    schedule_greedy.load_from_json(input_file)

    greedy_algo = MinSTF(schedule_greedy)
    greedy_results = greedy_algo.run()

    cmax_greedy = greedy_results["C_max"]

    # Zapis harmonogramu heurystycznego
    greedy_out = os.path.join(output_dir, "greedy_schedule.json")
    with open(greedy_out, "w", encoding="utf-8") as f:
        json.dump(greedy_results, f, indent=4, ensure_ascii=False)
    print(f"[OUTPUT] Zapisano: {greedy_out}")

    # Generowanie diagramu Gantta dla Greedy
    try:
        greedy_gantt = os.path.join(output_dir, "greedy_gantt.png")
        generate_gantt_from_file(greedy_out, greedy_gantt, show=False)
        greedy_results["gantt_diagram"] = greedy_gantt
        # Zaktualizuj plik JSON z informacją o diagramie
        with open(greedy_out, "w", encoding="utf-8") as f:
            json.dump(greedy_results, f, indent=4, ensure_ascii=False)
        print(f"[GANTT] Wygenerowano diagram: {greedy_gantt}")
    except Exception as e:
        print(f"[WARNING] Błąd generowania diagramu: {e}")
        greedy_results["gantt_diagram"] = None

    # ========================================================================
    # TEST 3: Algorytm Tabu Search
    # ========================================================================

    schedule_tabu = Schedule()
    schedule_tabu.load_from_json(input_file)

    tabu_algo = TabuSearch(schedule_tabu, max_iter=100, tabu_tenure=10, no_improve_limit=10)
    tabu_results = tabu_algo.run()

    cmax_tabu = tabu_results["C_max"]

    # Zapis harmonogramu Tabu Search
    tabu_out = os.path.join(output_dir, "tabu_schedule.json")
    with open(tabu_out, "w", encoding="utf-8") as f:
        json.dump(tabu_results, f, indent=4, ensure_ascii=False)
    print(f"[OUTPUT] Zapisano: {tabu_out}")

    # Generowanie diagramu Gantta dla Tabu Search
    try:
        tabu_gantt = os.path.join(output_dir, "tabu_gantt.png")
        generate_gantt_from_file(tabu_out, tabu_gantt, show=False)
        tabu_results["gantt_diagram"] = tabu_gantt
        # Zaktualizuj plik JSON z informacją o diagramie
        with open(tabu_out, "w", encoding="utf-8") as f:
            json.dump(tabu_results, f, indent=4, ensure_ascii=False)
        print(f"[GANTT] Wygenerowano diagram: {tabu_gantt}")
    except Exception as e:
        print(f"[WARNING] Błąd generowania diagramu: {e}")
        tabu_results["gantt_diagram"] = None

    # ========================================================================
    # TEST 4: Algorytm Branch & Bound
    # ========================================================================

    schedule_bnb = Schedule()
    schedule_bnb.load_from_json(input_file)

    bnb_algo = BranchAndBound(schedule_bnb)
    bnb_results = bnb_algo.run()

    cmax_bnb = bnb_results["C_max"]

    # Zapis harmonogramu B&B
    bnb_out = os.path.join(output_dir, "bnb_schedule.json")
    with open(bnb_out, "w", encoding="utf-8") as f:
        json.dump(bnb_results, f, indent=4, ensure_ascii=False)
    print(f"[OUTPUT] Zapisano: {bnb_out}")

    # Generowanie diagramu Gantta dla Branch & Bound
    try:
        bnb_gantt = os.path.join(output_dir, "bnb_gantt.png")
        generate_gantt_from_file(bnb_out, bnb_gantt, show=False)
        bnb_results["gantt_diagram"] = bnb_gantt
        # Zaktualizuj plik JSON z informacją o diagramie
        with open(bnb_out, "w", encoding="utf-8") as f:
            json.dump(bnb_results, f, indent=4, ensure_ascii=False)
        print(f"[GANTT] Wygenerowano diagram: {bnb_gantt}")
    except Exception as e:
        print(f"[WARNING] Błąd generowania diagramu: {e}")
        bnb_results["gantt_diagram"] = None

    # ========================================================================
    # PORÓWNANIE WYNIKÓW
    # ========================================================================

    print_separator("PODSUMOWANIE I POROWNANIE WYNIKOW")
    print(f"{'Algorytm':<30} {'Sekwencja':<25} {'C_max':<12} {'Czas [ms]':<12}")
    print("-" * 80)

    # Permutacja naturalna
    print(f"{'Permutacja naturalna':<30} {str(natural_sequence):<25} {cmax_natural:<12.2f} {'—':<12}")

    # Greedy MSTF
    greedy_seq_str = str(greedy_algo.best_sequence)
    greedy_time_ms = greedy_results["time_in_ms"]
    greedy_time_s = greedy_time_ms / 1000
    print(f"{'Greedy (MSTF)':<30} {greedy_seq_str:<25} {cmax_greedy:<12.2f} {greedy_time_ms:<12.2f}")

    # Tabu Search
    tabu_seq_str = str(tabu_algo.best_sequence)
    tabu_time_ms = tabu_results["time_in_ms"]
    tabu_time_s = tabu_time_ms / 1000
    print(f"{'Tabu Search':<30} {tabu_seq_str:<25} {cmax_tabu:<12.2f} {tabu_time_ms:<12.2f}")

    # Branch & Bound
    bnb_seq_str = str(bnb_algo.best_sequence)
    bnb_time_ms = bnb_results["time_in_ms"]
    bnb_time_s = bnb_time_ms / 1000
    print(f"{'Branch & Bound (optimal)':<30} {bnb_seq_str:<25} {cmax_bnb:<12.2f} {bnb_time_ms:<12.2f}")

    print("-" * 80)
    print()

    # Analiza jakości rozwiązań
    print("\nAnaliza jakosci:")
    print("-" * 80)

    # Poprawa względem permutacji naturalnej
    improvement_greedy = ((cmax_natural - cmax_greedy) / cmax_natural) * 100
    improvement_tabu = ((cmax_natural - cmax_tabu) / cmax_natural) * 100
    improvement_bnb = ((cmax_natural - cmax_bnb) / cmax_natural) * 100

    print(f"Poprawa MSTF względem naturalnej:       {improvement_greedy:+.2f}%")
    print(f"Poprawa Tabu Search względem naturalnej:{improvement_tabu:+.2f}%")
    print(f"Poprawa B&B względem naturalnej:        {improvement_bnb:+.2f}%")

    # Jakość algorytmów względem optimum
    if cmax_bnb > 0:
        gap_greedy = ((cmax_greedy - cmax_bnb) / cmax_bnb) * 100
        gap_tabu = ((cmax_tabu - cmax_bnb) / cmax_bnb) * 100
        print(f"\nGap MSTF względem optimum (B&B):        {gap_greedy:+.2f}%")
        print(f"Gap Tabu Search względem optimum (B&B): {gap_tabu:+.2f}%")

    # Przyspieszenie czasowe
    if bnb_time_s > 0:
        speedup_greedy = bnb_time_s / greedy_time_s if greedy_time_s > 0 else float('inf')
        speedup_tabu = bnb_time_s / tabu_time_s if tabu_time_s > 0 else float('inf')
        print(f"\nPrzyspieszenie MSTF vs B&B:             {speedup_greedy:.1f}x")
        print(f"Przyspieszenie Tabu Search vs B&B:      {speedup_tabu:.1f}x")

    print("\nWnioski:")
    print("-" * 80)

    # Analiza MSTF
    if abs(cmax_greedy - cmax_bnb) < 0.01:
        print("- Algorytm heurystyczny MSTF znalazl rozwiazanie OPTYMALNE!")
    elif improvement_greedy > 0:
        print(f"- Algorytm heurystyczny MSTF poprawil wynik o {improvement_greedy:.2f}%")
    else:
        print(f"- Algorytm heurystyczny MSTF nie poprawil wyniku naturalnego")

    # Analiza Tabu Search
    if abs(cmax_tabu - cmax_bnb) < 0.01:
        print("- Algorytm Tabu Search znalazl rozwiazanie OPTYMALNE!")
    elif improvement_tabu > 0:
        print(f"- Algorytm Tabu Search poprawil wynik o {improvement_tabu:.2f}%")
    else:
        print(f"- Algorytm Tabu Search nie poprawil wyniku naturalnego")

    # Porównanie Tabu Search vs MSTF
    if cmax_tabu < cmax_greedy:
        improvement_tabu_vs_greedy = ((cmax_greedy - cmax_tabu) / cmax_greedy) * 100
        print(f"- Tabu Search poprawil wynik MSTF o {improvement_tabu_vs_greedy:.2f}%")
    elif abs(cmax_tabu - cmax_greedy) < 0.01:
        print("- Tabu Search i MSTF osiagnely identyczne wyniki")
    else:
        print("- MSTF osiagnal lepszy wynik niz Tabu Search")

    print(f"\n- Algorytm B&B znalazl rozwiazanie optymalne z C_max = {cmax_bnb:.2f}")
    print(f"- Heurystyka MSTF byla {speedup_greedy:.1f}x szybsza niz B&B")
    print(f"- Tabu Search byl {speedup_tabu:.1f}x szybszy niz B&B")

    print_separator()

    # Zwróć wyniki
    return {
        "natural": {
            "sequence": natural_sequence,
            "C_max": cmax_natural
        },
        "greedy": {
            "sequence": greedy_algo.best_sequence,
            "C_max": cmax_greedy,
            "time_s": greedy_time_s
        },
        "tabu": {
            "sequence": tabu_algo.best_sequence,
            "C_max": cmax_tabu,
            "time_s": tabu_time_s
        },
        "bnb": {
            "sequence": bnb_algo.best_sequence,
            "C_max": cmax_bnb,
            "time_s": bnb_time_s
        }
    }

if "__main__" == __name__:
    run_benchmark()
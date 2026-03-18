"""Skrypt do przeprowadzenia kompleksowych badań wydajności algorytmów HFS-SDST.

Ten skrypt przeprowadza dwa zestawy eksperymentów:
- Zestaw 1: Wpływ liczby zadań (N) na wydajność
- Zestaw 2: Wpływ liczby etapów (E) na wydajność

Dla każdej konfiguracji wykonywane jest 100 uruchomień na losowych instancjach,
a wyniki są uśredniane i wizualizowane.
"""

import json
import random
import time
import os
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

from core.schedule import Schedule
from algorithms.greedy import MinSTF
from algorithms.tabu_search import TabuSearch
from algorithms.branch_and_bound import BranchAndBound


# ============================================================================
# KONFIGURACJA BADAŃ
# ============================================================================

# Zakresy losowania danych
PROCESSING_TIME_RANGE = (10, 20)
SETUP_TIME_RANGE = (5, 10)

# Współczynnik uczenia
LEARNING_COEFFICIENT = 0.3

# Liczba powtórzeń dla każdej konfiguracji
NUM_ITERATIONS = 1

# Zestaw 1: Wpływ liczby zadań (N)
SET1_N_VALUES = [2, 4, 8, 10, 16, 32]  # Branch & Bound do N=32
SET1_E = 5
SET1_M = 5

# Zestaw 2: Wpływ liczby etapów (E)
SET2_N = 16
SET2_E_VALUES = [2, 4, 8, 16, 32]
SET2_M = 5

# Folder wyjściowy
OUTPUT_DIR = Path("badania")


# ============================================================================
# FUNKCJE GENEROWANIA INSTANCJI
# ============================================================================

def generate_learning_stages_string(num_stages):
    """Generuje string learning_stages: ostatni etap uczący się = '1', reszta = '0'.

    Args:
        num_stages (int): Liczba etapów

    Returns:
        str: String binarny, np. dla 5 etapów: "00001"
    """
    if num_stages == 1:
        return "1"
    return "0" * (num_stages - 1) + "1"


def generate_random_instance(n_jobs, n_stages, n_machines_per_stage):
    """Generuje losową instancję problemu HFS-SDST.

    Args:
        n_jobs (int): Liczba zadań
        n_stages (int): Liczba etapów
        n_machines_per_stage (int): Liczba maszyn na każdy etap

    Returns:
        dict: Słownik z danymi problemu w formacie JSON
    """
    # Czasy przetwarzania: processing_times[job][stage][machine]
    processing_times = [
        [[random.randint(*PROCESSING_TIME_RANGE) for _ in range(n_machines_per_stage)]
         for _ in range(n_stages)]
        for _ in range(n_jobs)
    ]

    # Czasy przezbrojeń: setup_times[from_job][to_job][stage][machine]
    setup_times = [
        [
            [[random.randint(*SETUP_TIME_RANGE) for _ in range(n_machines_per_stage)]
             for _ in range(n_stages)]
            for _ in range(n_jobs)
        ]
        for _ in range(n_jobs)
    ]

    # Konfiguracja uczenia: ostatni etap uczący się
    learning_stages = generate_learning_stages_string(n_stages)

    return {
        "num_stages": n_stages,
        "machines_per_stage": [n_machines_per_stage] * n_stages,
        "processing_times": processing_times,
        "setup_times": setup_times,
        "learning_coefficient": LEARNING_COEFFICIENT,
        "learning_stages": learning_stages
    }


def load_instance_to_schedule(instance_data):
    """Ładuje instancję do obiektu Schedule.

    Args:
        instance_data (dict): Dane instancji

    Returns:
        Schedule: Obiekt harmonogramu z załadowaną instancją
    """
    # Zapisz tymczasowo do pliku (wymagane przez load_from_json)
    temp_file = OUTPUT_DIR / "temp_instance.json"
    with open(temp_file, 'w') as f:
        json.dump(instance_data, f)

    schedule = Schedule()
    schedule.load_from_json(str(temp_file))

    # Usuń plik tymczasowy
    temp_file.unlink()

    return schedule


# ============================================================================
# FUNKCJE URUCHAMIANIA ALGORYTMÓW
# ============================================================================

def run_algorithm_on_instance(algorithm_name, instance_data):
    """Uruchamia wybrany algorytm na instancji.

    Args:
        algorithm_name (str): Nazwa algorytmu ('greedy', 'tabu', 'bnb')
        instance_data (dict): Dane instancji

    Returns:
        dict: Wyniki zawierające runtime, cmax, sequence
    """
    import sys
    from io import StringIO

    schedule = load_instance_to_schedule(instance_data)

    if algorithm_name == 'greedy':
        algo = MinSTF(schedule)
    elif algorithm_name == 'tabu':
        algo = TabuSearch(schedule, max_iter=100, tabu_tenure=10, no_improve_limit=10)
    elif algorithm_name == 'bnb':
        algo = BranchAndBound(schedule)
    else:
        raise ValueError(f"Nieznany algorytm: {algorithm_name}")

    # Wyłącz printy z algorytmów
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        results = algo.run()
    finally:
        sys.stdout = old_stdout

    return {
        'runtime': results['time_in_ms'] / 1000.0,  # Konwersja z ms na s
        'cmax': results['C_max'],
        'sequence': algo.best_sequence
    }


def run_experiment_configuration(n_jobs, n_stages, n_machines, algorithms, iterations=100):
    """Uruchamia eksperymenty dla danej konfiguracji parametrów.

    Args:
        n_jobs (int): Liczba zadań
        n_stages (int): Liczba etapów
        n_machines (int): Liczba maszyn na etap
        algorithms (list): Lista nazw algorytmów do przetestowania
        iterations (int): Liczba powtórzeń

    Returns:
        dict: Słownik z wynikami dla każdego algorytmu
    """
    print(f"\n{'='*80}")
    print(f"Konfiguracja: N={n_jobs}, E={n_stages}, M={n_machines}")
    print(f"Algorytmy: {algorithms}, Iteracje: {iterations}")
    print(f"{'='*80}")

    results = {algo: {'runtimes': [], 'cmax_values': []} for algo in algorithms}

    for iteration in range(iterations):
        # Generuj nową losową instancję
        instance = generate_random_instance(n_jobs, n_stages, n_machines)

        # Wyświetl progress co 10 iteracji lub na końcu
        if (iteration + 1) % 10 == 0 or iteration == 0:
            print(f"[INFO] E = {n_stages}, N = {n_jobs} | Iteracja {iteration + 1}/{iterations}")

        # Uruchom każdy algorytm na tej samej instancji (bez wyświetlania szczegółów)
        for algo_name in algorithms:
            result = run_algorithm_on_instance(algo_name, instance)
            results[algo_name]['runtimes'].append(result['runtime'])
            results[algo_name]['cmax_values'].append(result['cmax'])

    # Oblicz statystyki
    statistics = {}
    for algo_name in algorithms:
        runtimes = results[algo_name]['runtimes']
        statistics[algo_name] = {
            'mean_runtime': np.mean(runtimes),
            'std_runtime': np.std(runtimes),
            'mean_cmax': np.mean(results[algo_name]['cmax_values']),
            'std_cmax': np.std(results[algo_name]['cmax_values'])
        }

        print(f"  {algo_name:12s}: T_avg={statistics[algo_name]['mean_runtime']:.4f}s "
              f"± {statistics[algo_name]['std_runtime']:.4f}s, "
              f"Cmax_avg={statistics[algo_name]['mean_cmax']:.2f}")

    return statistics


# ============================================================================
# ZESTAW 1: WPŁYW LICZBY ZADAŃ (N)
# ============================================================================

def run_set1_experiments():
    """Przeprowadza Zestaw 1: Wpływ liczby zadań na wydajność."""
    print("\n" + "="*80)
    print("ZESTAW 1: WPŁYW LICZBY ZADAŃ (N)")
    print("="*80)

    results = {}

    for n in SET1_N_VALUES:
        # Dla N > 32 pomijamy Branch & Bound
        if n <= 16:
            algorithms = ['greedy', 'tabu', 'bnb']
        else:
            algorithms = ['greedy', 'tabu']
            print(f"\n⚠️  Branch & Bound pominięty dla N={n} (zbyt długi czas wykonania)")

        stats = run_experiment_configuration(
            n_jobs=n,
            n_stages=SET1_E,
            n_machines=SET1_M,
            algorithms=algorithms,
            iterations=NUM_ITERATIONS
        )
        results[n] = stats

    return results


# ============================================================================
# ZESTAW 2: WPŁYW LICZBY ETAPÓW (E)
# ============================================================================

def run_set2_experiments():
    """Przeprowadza Zestaw 2: Wpływ liczby etapów na wydajność."""
    print("\n" + "="*80)
    print("ZESTAW 2: WPŁYW LICZBY ETAPÓW (E)")
    print("="*80)

    results = {}
    algorithms = ['greedy', 'tabu', 'bnb']

    for e in SET2_E_VALUES:
        stats = run_experiment_configuration(
            n_jobs=SET2_N,
            n_stages=e,
            n_machines=SET2_M,
            algorithms=algorithms,
            iterations=NUM_ITERATIONS
        )
        results[e] = stats

    return results


# ============================================================================
# EKSPORT WYNIKÓW
# ============================================================================

def save_results_to_json(set1_results, set2_results):
    """Zapisuje wyniki do plików JSON."""
    output_file_1 = OUTPUT_DIR / "set1_results.json"
    output_file_2 = OUTPUT_DIR / "set2_results.json"

    with open(output_file_1, 'w') as f:
        json.dump(set1_results, f, indent=2)

    with open(output_file_2, 'w') as f:
        json.dump(set2_results, f, indent=2)

    print(f"\n✓ Wyniki zapisane do: {output_file_1} i {output_file_2}")


def save_results_to_csv(set1_results, set2_results):
    """Zapisuje wyniki do plików CSV."""

    # Zestaw 1
    csv_file_1 = OUTPUT_DIR / "set1_results.csv"
    with open(csv_file_1, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'Algorithm', 'Mean_Runtime', 'Std_Runtime', 'Mean_Cmax', 'Std_Cmax'])

        for n, stats in set1_results.items():
            for algo, data in stats.items():
                writer.writerow([
                    n, algo,
                    data['mean_runtime'], data['std_runtime'],
                    data['mean_cmax'], data['std_cmax']
                ])

    # Zestaw 2
    csv_file_2 = OUTPUT_DIR / "set2_results.csv"
    with open(csv_file_2, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['E', 'Algorithm', 'Mean_Runtime', 'Std_Runtime', 'Mean_Cmax', 'Std_Cmax'])

        for e, stats in set2_results.items():
            for algo, data in stats.items():
                writer.writerow([
                    e, algo,
                    data['mean_runtime'], data['std_runtime'],
                    data['mean_cmax'], data['std_cmax']
                ])

    print(f"✓ Wyniki CSV zapisane do: {csv_file_1} i {csv_file_2}")


# ============================================================================
# GENEROWANIE TABELI LATEX
# ============================================================================

def generate_latex_table(set1_results):
    """Generuje tabelę LaTeX z wynikami dla największej instancji (N=32)."""

    latex_file = OUTPUT_DIR / "results_table.tex"

    # Znajdź największe N dla którego mamy wszystkie algorytmy
    max_n_with_bnb = max([n for n in set1_results.keys() if 'bnb' in set1_results[n]])
    stats = set1_results[max_n_with_bnb]

    latex_content = f"""% Tabela wyników eksperymentów - Zestaw 1 (N={max_n_with_bnb}, E={SET1_E}, M={SET1_M})
% Wymagane pakiety: \\usepackage{{booktabs}}

\\begin{{table}}[htbp]
\\centering
\\caption{{Porównanie wydajności algorytmów dla instancji N={max_n_with_bnb}, E={SET1_E}, M={SET1_M} (średnia z {NUM_ITERATIONS} uruchomień).}}
\\label{{tab:algorithm_comparison}}
\\begin{{tabular}}{{l c c c c}}
\\toprule
\\textbf{{Algorytm}} & \\textbf{{Czas śr. [s]}} & \\textbf{{Odch. std. [s]}} & \\textbf{{C\\_max śr.}} & \\textbf{{C\\_max std.}} \\\\
\\midrule
"""

    algo_names = {
        'greedy': 'MinSTF (Greedy)',
        'tabu': 'Tabu Search',
        'bnb': 'Branch \\& Bound'
    }

    for algo in ['greedy', 'tabu', 'bnb']:
        if algo in stats:
            data = stats[algo]
            latex_content += f"{algo_names[algo]} & {data['mean_runtime']:.4f} & {data['std_runtime']:.4f} & "
            latex_content += f"{data['mean_cmax']:.2f} & {data['std_cmax']:.2f} \\\\\n"

    latex_content += """\\bottomrule
\\end{tabular}
\\end{table}

% Instrukcje użycia:
% 1. W preambule dokumentu dodaj: \\usepackage{booktabs}
% 2. Wstaw powyższy kod w miejscu, gdzie chcesz mieć tabelę
% 3. Użyj \\ref{tab:algorithm_comparison} aby odwołać się do tabeli w tekście
"""

    with open(latex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"✓ Tabela LaTeX zapisana do: {latex_file}")


# ============================================================================
# WIZUALIZACJA - WYKRESY LINIOWO-PUNKTOWE
# ============================================================================

def theoretical_complexity(n, complexity_type, k=100):
    """Oblicza teoretyczną złożoność obliczeniową (znormalizowaną).

    Args:
        n: Rozmiar problemu
        complexity_type: 'greedy', 'tabu', 'bnb'
        k: Liczba iteracji dla Tabu Search

    Returns:
        float: Względna wartość złożoności
    """
    if complexity_type == 'greedy':
        return n ** 2
    elif complexity_type == 'tabu':
        return k * (n ** 2)
    elif complexity_type == 'bnb':
        # Dla n! używamy aproksymacji Stirlinga: n! ≈ (n/e)^n
        if n <= 1:
            return 1
        return (n / np.e) ** n
    return 1


def plot_set1_results(set1_results):
    """Generuje wykres liniowo-punktowy dla Zestawu 1 z złożonościami teoretycznymi."""

    fig, ax = plt.subplots(figsize=(12, 7))

    # Przygotowanie danych
    algorithms = ['greedy', 'tabu', 'bnb']
    algo_names = {
        'greedy': 'MinSTF (Greedy)',
        'tabu': 'Tabu Search',
        'bnb': 'Branch & Bound'
    }
    colors = {'greedy': 'blue', 'tabu': 'green', 'bnb': 'red'}
    markers = {'greedy': 'o', 'tabu': 's', 'bnb': '^'}

    # Faktyczne czasy wykonania
    for algo in algorithms:
        n_values = []
        runtimes = []

        for n in sorted(set1_results.keys()):
            if algo in set1_results[n]:
                n_values.append(n)
                runtimes.append(set1_results[n][algo]['mean_runtime'])

        if n_values:
            # Linia ciągła z punktami (liniowo-punktowy)
            ax.plot(n_values, runtimes,
                   marker=markers[algo],
                   color=colors[algo],
                   linewidth=2,
                   markersize=8,
                   label=f'{algo_names[algo]} (faktyczny)')

    # Złożoności teoretyczne (linie przerywane)
    n_theoretical = np.array(sorted(set1_results.keys()))

    for algo in algorithms:
        # Tylko dla wartości N, dla których mamy dane
        n_vals_with_data = [n for n in n_theoretical if algo in set1_results[n]]

        if n_vals_with_data:
            complexities = [theoretical_complexity(n, algo) for n in n_vals_with_data]

            # Normalizacja: dopasuj skalę teoretyczną do faktycznej
            actual_runtimes = [set1_results[n][algo]['mean_runtime'] for n in n_vals_with_data]
            if len(actual_runtimes) > 0 and len(complexities) > 0:
                scale_factor = actual_runtimes[-1] / complexities[-1]
                complexities_scaled = [c * scale_factor for c in complexities]

                ax.plot(n_vals_with_data, complexities_scaled,
                       linestyle='--',
                       color=colors[algo],
                       linewidth=1.5,
                       alpha=0.7,
                       label=f'{algo_names[algo]} (teoretyczny)')

    ax.set_xlabel('Liczba Zadań (N)', fontsize=12)
    ax.set_ylabel('Średni Czas Wykonania [s]', fontsize=12)
    ax.set_title('Porównanie złożoności teoretycznej z faktyczną algorytmów optymalizacji',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Zapisz wykres
    plot_file_png = OUTPUT_DIR / "set1_plot.png"
    plot_file_pdf = OUTPUT_DIR / "set1_plot.pdf"
    plt.savefig(plot_file_png, dpi=300, bbox_inches='tight')
    plt.savefig(plot_file_pdf, bbox_inches='tight')
    plt.close()

    print(f"✓ Wykres Zestaw 1 zapisany do: {plot_file_png} i {plot_file_pdf}")


def plot_set2_results(set2_results):
    """Generuje wykres liniowo-punktowy dla Zestawu 2."""

    fig, ax = plt.subplots(figsize=(12, 7))

    algorithms = ['greedy', 'tabu', 'bnb']
    algo_names = {
        'greedy': 'MinSTF (Greedy)',
        'tabu': 'Tabu Search',
        'bnb': 'Branch & Bound'
    }
    colors = {'greedy': 'blue', 'tabu': 'green', 'bnb': 'red'}
    markers = {'greedy': 'o', 'tabu': 's', 'bnb': '^'}

    for algo in algorithms:
        e_values = []
        runtimes = []

        for e in sorted(set2_results.keys()):
            if algo in set2_results[e]:
                e_values.append(e)
                runtimes.append(set2_results[e][algo]['mean_runtime'])

        if e_values:
            # Linia ciągła z punktami (liniowo-punktowy)
            ax.plot(e_values, runtimes,
                   marker=markers[algo],
                   color=colors[algo],
                   linewidth=2,
                   markersize=8,
                   label=algo_names[algo])

    ax.set_xlabel('Liczba Etapów (E)', fontsize=12)
    ax.set_ylabel('Średni Czas Wykonania [s]', fontsize=12)
    ax.set_title('Porównanie wpływu liczby etapów dla każdego z algorytmów',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Zapisz wykres
    plot_file_png = OUTPUT_DIR / "set2_plot.png"
    plot_file_pdf = OUTPUT_DIR / "set2_plot.pdf"
    plt.savefig(plot_file_png, dpi=300, bbox_inches='tight')
    plt.savefig(plot_file_pdf, bbox_inches='tight')
    plt.close()

    print(f"✓ Wykres Zestaw 2 zapisany do: {plot_file_png} i {plot_file_pdf}")


# ============================================================================
# GŁÓWNA FUNKCJA
# ============================================================================

def main():
    """Główna funkcja uruchamiająca pełne badanie."""

    print("\n" + "="*80)
    print("BADANIE WYDAJNOŚCI ALGORYTMÓW HFS-SDST")
    print("="*80)
    print(f"Konfiguracja:")
    print(f"  - Zakresy: Czas procesowania={PROCESSING_TIME_RANGE}, Setup={SETUP_TIME_RANGE}")
    print(f"  - Współczynnik uczenia: {LEARNING_COEFFICIENT}")
    print(f"  - Iteracje na konfigurację: {NUM_ITERATIONS}")
    print(f"  - Folder wyjściowy: {OUTPUT_DIR}")
    print("="*80)

    # Utwórz folder wyjściowy
    OUTPUT_DIR.mkdir(exist_ok=True)

    start_time = time.time()

    # Przeprowadź eksperymenty
    set1_results = run_set1_experiments()
    set2_results = run_set2_experiments()

    # Zapisz wyniki
    save_results_to_json(set1_results, set2_results)
    save_results_to_csv(set1_results, set2_results)
    generate_latex_table(set1_results)

    # Wygeneruj wykresy
    plot_set1_results(set1_results)
    plot_set2_results(set2_results)

    total_time = time.time() - start_time

    print("\n" + "="*80)
    print(f"✓ BADANIE ZAKOŃCZONE POMYŚLNIE!")
    print(f"✓ Całkowity czas wykonania: {total_time:.2f}s ({total_time/60:.2f} min)")
    print(f"✓ Wszystkie wyniki zapisane w folderze: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()

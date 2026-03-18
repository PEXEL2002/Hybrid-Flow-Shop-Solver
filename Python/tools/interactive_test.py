"""
Interaktywny program do testowania algorytmów optymalizacji HFS-SDST.

Umożliwia:
- Generację instancji problemu z parametrami użytkownika
- Porównanie wszystkich algorytmów
- Wizualizację wyników (wykresy porównawcze + diagramy Gantta)
- Eksport szczegółowych raportów

Użycie:
    python interactive_test.py
"""

import sys
import io
import json
import os
import random
import matplotlib.pyplot as plt
from datetime import datetime

# Ustawienie kodowania UTF-8 dla Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from core.schedule import Schedule
from algorithms.greedy import MinSTF
from algorithms.tabu_search import TabuSearch
from algorithms.branch_and_bound import BranchAndBound
from utils.gantt_chart import generate_gantt_from_file


def print_header(text):
    """Wyświetla nagłówek."""
    print(f"\n{'='*80}")
    print(f"{text:^80}")
    print(f"{'='*80}\n")


def print_section(text):
    """Wyświetla sekcję."""
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}")


def get_user_input(prompt, default, input_type=str, min_val=None, max_val=None):
    """
    Pobiera input od użytkownika z walidacją.

    Args:
        prompt: tekst pytania
        default: wartość domyślna
        input_type: typ danych (int, float, str)
        min_val: minimalna wartość (dla int/float)
        max_val: maksymalna wartość (dla int/float)
    """
    while True:
        try:
            user_input = input(f"{prompt} [domyślnie: {default}]: ").strip()

            if user_input == "":
                return default

            value = input_type(user_input)

            if input_type in [int, float]:
                if min_val is not None and value < min_val:
                    print(f"Wartość musi być >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Wartość musi być <= {max_val}")
                    continue

            return value
        except ValueError:
            print(f"Nieprawidłowa wartość. Oczekiwano typu {input_type.__name__}")


def generate_instance_interactive():
    """
    Interaktywnie generuje instancję problemu na podstawie parametrów użytkownika.

    Returns:
        dict: dane problemu w formacie JSON
    """
    print_header("GENERATOR INSTANCJI HFS-SDST")

    print("Podaj parametry problemu:")
    print("(Naciśnij Enter, aby użyć wartości domyślnej)\n")

    # Podstawowe parametry
    num_jobs = get_user_input("Liczba zadań", 8, int, min_val=2, max_val=15)
    num_stages = get_user_input("Liczba etapów", 2, int, min_val=1, max_val=5)

    # Maszyny na każdym etapie
    print("\nLiczba maszyn na każdym etapie:")
    machines_per_stage = []
    for stage in range(num_stages):
        num_machines = get_user_input(f"  Etap {stage+1}", 2, int, min_val=1, max_val=5)
        machines_per_stage.append(num_machines)

    # Efekt uczenia
    print("\nParametry efektu uczenia:")
    learning_coeff = get_user_input("Współczynnik uczenia (α)", 0.1, float, min_val=0.0, max_val=1.0)

    print("\nEtapy z efektem uczenia (0=nie, 1=tak):")
    learning_stages = ""
    for stage in range(num_stages):
        has_learning = get_user_input(f"  Etap {stage+1}", "1" if stage > 0 else "0", str)
        learning_stages += "1" if has_learning in ["1", "y", "yes", "tak"] else "0"

    # Zakresy czasów
    print("\nZakresy czasów:")
    proc_time_min = get_user_input("Min czas przetwarzania", 5, int, min_val=1)
    proc_time_max = get_user_input("Max czas przetwarzania", 20, int, min_val=proc_time_min)

    setup_time_min = get_user_input("Min czas przezbrojenia", 1, int, min_val=0)
    setup_time_max = get_user_input("Max czas przezbrojenia", 5, int, min_val=setup_time_min)
    setup_self_factor = get_user_input("Współczynnik self-setup (0.0-1.0)", 0.5, float, min_val=0.0, max_val=1.0)

    print("\n[INFO] Generowanie czasów przetwarzania i przezbrojenia...")

    # Generacja czasów przetwarzania
    processing_times = []
    for job in range(num_jobs):
        job_stages = []
        for stage in range(num_stages):
            stage_machines = []
            for machine in range(machines_per_stage[stage]):
                time = random.randint(proc_time_min, proc_time_max)
                stage_machines.append([time])
            job_stages.append(stage_machines)
        processing_times.append(job_stages)

    # Generacja czasów przezbrojenia
    setup_times = []
    for from_job in range(num_jobs):
        from_job_setups = []
        for to_job in range(num_jobs):
            to_job_setups = []
            for stage in range(num_stages):
                stage_setups = []
                for machine in range(machines_per_stage[stage]):
                    if from_job == to_job:
                        # Self-setup - zazwyczaj krótszy
                        time = int(setup_time_min + (setup_time_max - setup_time_min) * setup_self_factor)
                    else:
                        time = random.randint(setup_time_min, setup_time_max)
                    stage_setups.append([time])
                to_job_setups.append(stage_setups)
            from_job_setups.append(to_job_setups)
        setup_times.append(from_job_setups)

    # Utworzenie struktury danych
    instance = {
        "algorithm": "tabu",  # domyślny algorytm
        "num_jobs": num_jobs,
        "num_stages": num_stages,
        "machines_per_stage": machines_per_stage,
        "learning_coefficient": learning_coeff,
        "learning_stages": learning_stages,
        "processing_times": processing_times,
        "setup_times": setup_times
    }

    print("\n[SUCCESS] Instancja została wygenerowana!")
    print(f"  - Zadania: {num_jobs}")
    print(f"  - Etapy: {num_stages}")
    print(f"  - Maszyny: {machines_per_stage}")
    print(f"  - Uczenie: α={learning_coeff}, etapy={learning_stages}")

    return instance


def save_instance(instance, output_dir="../data"):
    """Zapisuje instancję do pliku JSON."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"instance_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(instance, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] Instancja zapisana do: {filepath}")
    return filepath


def run_all_algorithms(instance_file, output_dir="../results"):
    """
    Uruchamia wszystkie algorytmy dla danej instancji i zbiera wyniki.

    Args:
        instance_file: ścieżka do pliku z instancją
        output_dir: katalog na wyniki

    Returns:
        dict: wyniki wszystkich algorytmów
    """
    print_header("URUCHAMIANIE ALGORYTMÓW")

    os.makedirs(output_dir, exist_ok=True)

    # Wczytaj dane
    with open(instance_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    num_jobs = len(data["processing_times"])
    print(f"Problem: {num_jobs} zadań, {data['num_stages']} etapów")
    print(f"Maszyny: {data['machines_per_stage']}")
    print(f"Uczenie: α={data['learning_coefficient']}, etapy={data['learning_stages']}")

    results = {}

    # === PERMUTACJA NATURALNA ===
    print_section("1/4: Permutacja Naturalna (baseline)")
    schedule_natural = Schedule()
    schedule_natural.load_from_json(instance_file)
    natural_sequence = list(range(num_jobs))
    cmax_natural = schedule_natural.build_from_sequence(natural_sequence)

    results["Natural"] = {
        "sequence": natural_sequence,
        "C_max": cmax_natural,
        "time_ms": 0,
        "schedule": schedule_natural.to_json()
    }
    print(f"C_max = {cmax_natural:.2f}")

    # === MinSTF ===
    print_section("2/4: MinSTF (heurystyka)")
    schedule_greedy = Schedule()
    schedule_greedy.load_from_json(instance_file)

    algo_greedy = MinSTF(schedule_greedy)
    greedy_results = algo_greedy.run()

    results["Greedy"] = {
        "sequence": algo_greedy.best_sequence,
        "C_max": greedy_results["C_max"],
        "time_ms": greedy_results["time_in_ms"],
        "schedule": greedy_results["schedule"]
    }
    print(f"C_max = {greedy_results['C_max']:.2f} (czas: {greedy_results['time_in_ms']:.2f}ms)")

    # === TABU SEARCH ===
    print_section("3/4: Tabu Search (metaheurystyka)")
    schedule_tabu = Schedule()
    schedule_tabu.load_from_json(instance_file)

    algo_tabu = TabuSearch(schedule_tabu, max_iter=100, tabu_tenure=10, no_improve_limit=20)
    tabu_results = algo_tabu.run()

    results["Tabu Search"] = {
        "sequence": algo_tabu.best_sequence,
        "C_max": tabu_results["C_max"],
        "time_ms": tabu_results["time_in_ms"],
        "schedule": tabu_results["schedule"]
    }
    print(f"C_max = {tabu_results['C_max']:.2f} (czas: {tabu_results['time_in_ms']:.2f}ms)")

    # === BRANCH & BOUND ===
    if num_jobs <= 10:
        print_section("4/4: Branch & Bound (algorytm dokładny)")
        schedule_bnb = Schedule()
        schedule_bnb.load_from_json(instance_file)

        algo_bnb = BranchAndBound(schedule_bnb)
        bnb_results = algo_bnb.run()

        results["Branch & Bound"] = {
            "sequence": algo_bnb.best_sequence,
            "C_max": bnb_results["C_max"],
            "time_ms": bnb_results["time_in_ms"],
            "schedule": bnb_results["schedule"]
        }
        print(f"C_max = {bnb_results['C_max']:.2f} (czas: {bnb_results['time_in_ms']:.2f}ms)")
    else:
        print_section("4/4: Branch & Bound (POMINIĘTO)")
        print("[WARNING] Branch & Bound pominięty - zbyt duża instancja (n > 10)")
        results["Branch & Bound"] = None

    return results


def generate_comparison_charts(results, output_dir="../results"):
    """
    Generuje wykresy porównawcze algorytmów.

    Args:
        results: słownik z wynikami algorytmów
        output_dir: katalog na wykresy
    """
    print_section("GENEROWANIE WYKRESÓW PORÓWNAWCZYCH")

    os.makedirs(output_dir, exist_ok=True)

    # Przygotowanie danych
    algorithms = []
    cmax_values = []
    time_values = []
    colors = []

    color_map = {
        "Natural": "#95a5a6",
        "Greedy": "#3498db",
        "Tabu Search": "#e74c3c",
        "Branch & Bound": "#2ecc71"
    }

    for algo_name, data in results.items():
        if data is not None:
            algorithms.append(algo_name)
            cmax_values.append(data["C_max"])
            time_values.append(data["time_ms"])
            colors.append(color_map.get(algo_name, "#34495e"))

    # Wykres 1: Porównanie C_max
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    bars1 = ax1.bar(algorithms, cmax_values, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('C_max (czas zakończenia)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Algorytm', fontsize=12, fontweight='bold')
    ax1.set_title('Porównanie jakości rozwiązań (C_max)', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Dodaj wartości na słupkach
    for bar, value in zip(bars1, cmax_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}',
                ha='center', va='bottom', fontweight='bold')

    # Dodaj % poprawy względem Natural
    natural_cmax = results["Natural"]["C_max"]
    for i, (bar, value) in enumerate(zip(bars1, cmax_values)):
        if algorithms[i] != "Natural":
            improvement = ((natural_cmax - value) / natural_cmax) * 100
            ax1.text(bar.get_x() + bar.get_width()/2., height * 0.5,
                    f'{improvement:+.1f}%',
                    ha='center', va='center', fontsize=9,
                    color='white' if improvement > 0 else 'red',
                    fontweight='bold')

    # Wykres 2: Porównanie czasu wykonania (bez Natural, skala log)
    algo_with_time = [a for a, t in zip(algorithms, time_values) if t > 0]
    time_with_values = [t for t in time_values if t > 0]
    colors_with_time = [c for c, t in zip(colors, time_values) if t > 0]

    bars2 = ax2.bar(algo_with_time, time_with_values, color=colors_with_time, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('Czas wykonania [ms] (skala log)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Algorytm', fontsize=12, fontweight='bold')
    ax2.set_title('Porównanie czasu wykonania', fontsize=14, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Dodaj wartości na słupkach
    for bar, value in zip(bars2, time_with_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}ms',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    chart_file = os.path.join(output_dir, "comparison_chart.png")
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    print(f"[SAVED] Wykres porównawczy: {chart_file}")
    plt.close()

    # Wykres 3: Detailed comparison (quality vs time trade-off)
    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter plot - czas vs jakość
    for i, algo in enumerate(algorithms):
        if time_values[i] > 0:  # pomiń Natural (czas = 0)
            x = time_values[i]
            y = cmax_values[i]
            ax.scatter(x, y, s=300, c=[colors[i]], alpha=0.6, edgecolor='black', linewidth=2)
            ax.annotate(algo, (x, y), fontsize=11, fontweight='bold',
                       ha='center', va='center')

    ax.set_xlabel('Czas wykonania [ms] (skala log)', fontsize=12, fontweight='bold')
    ax.set_ylabel('C_max (czas zakończenia)', fontsize=12, fontweight='bold')
    ax.set_title('Trade-off: Jakość rozwiązania vs Czas wykonania', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, linestyle='--')

    # Dodaj linię Pareto (optymalne rozwiązania)
    if len(time_with_values) > 1:
        ax.axhline(y=min(cmax_values), color='green', linestyle='--',
                  alpha=0.5, label='Najlepsza jakość')
        ax.legend()

    plt.tight_layout()
    tradeoff_file = os.path.join(output_dir, "tradeoff_chart.png")
    plt.savefig(tradeoff_file, dpi=300, bbox_inches='tight')
    print(f"[SAVED] Wykres trade-off: {tradeoff_file}")
    plt.close()


def generate_gantt_charts(results, output_dir="../results"):
    """Generuje diagramy Gantta dla wszystkich algorytmów."""
    print_section("GENEROWANIE DIAGRAMÓW GANTTA")

    for algo_name, data in results.items():
        if data is None:
            continue

        # Zapisz tymczasowy plik JSON
        temp_file = os.path.join(output_dir, f"temp_{algo_name.replace(' ', '_').lower()}.json")
        result_data = {
            "Algorithm": algo_name,
            "C_max": data["C_max"],
            "time_in_ms": data["time_ms"],
            "schedule": data["schedule"]
        }

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        # Wygeneruj diagram
        gantt_file = os.path.join(output_dir, f"gantt_{algo_name.replace(' ', '_').lower()}.png")
        try:
            generate_gantt_from_file(temp_file, gantt_file, show=False)
            print(f"[SAVED] Diagram Gantta ({algo_name}): {gantt_file}")
        except Exception as e:
            print(f"[ERROR] Błąd generowania diagramu dla {algo_name}: {e}")

        # Usuń tymczasowy plik
        if os.path.exists(temp_file):
            os.remove(temp_file)


def generate_report(results, output_dir="../results"):
    """Generuje szczegółowy raport tekstowy."""
    print_section("GENEROWANIE RAPORTU")

    report_file = os.path.join(output_dir, "report.txt")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("RAPORT PORÓWNAWCZY ALGORYTMÓW HFS-SDST\n")
        f.write("="*80 + "\n\n")

        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Tabela wyników
        f.write("-"*80 + "\n")
        f.write(f"{'Algorytm':<20} {'Sekwencja':<30} {'C_max':<12} {'Czas [ms]':<12}\n")
        f.write("-"*80 + "\n")

        for algo_name, data in results.items():
            if data is not None:
                seq_str = str(data["sequence"][:10])  # pierwsze 10 elementów
                if len(data["sequence"]) > 10:
                    seq_str = seq_str[:-1] + ",...]"
                f.write(f"{algo_name:<20} {seq_str:<30} {data['C_max']:<12.2f} {data['time_ms']:<12.2f}\n")

        f.write("-"*80 + "\n\n")

        # Analiza
        f.write("ANALIZA WYNIKÓW:\n")
        f.write("-"*80 + "\n\n")

        natural_cmax = results["Natural"]["C_max"]
        best_cmax = min(data["C_max"] for data in results.values() if data is not None)

        for algo_name, data in results.items():
            if data is not None and algo_name != "Natural":
                improvement = ((natural_cmax - data["C_max"]) / natural_cmax) * 100
                gap_to_best = ((data["C_max"] - best_cmax) / best_cmax) * 100 if best_cmax > 0 else 0

                f.write(f"{algo_name}:\n")
                f.write(f"  - Poprawa względem Natural: {improvement:+.2f}%\n")
                f.write(f"  - Gap względem najlepszego: {gap_to_best:+.2f}%\n")
                f.write(f"  - Czas wykonania: {data['time_ms']:.2f}ms\n")

                if results.get("Branch & Bound") and algo_name != "Branch & Bound":
                    optimal_cmax = results["Branch & Bound"]["C_max"]
                    gap_to_optimal = ((data["C_max"] - optimal_cmax) / optimal_cmax) * 100
                    f.write(f"  - Gap względem optimum (B&B): {gap_to_optimal:+.2f}%\n")

                f.write("\n")

        # Wnioski
        f.write("\nWNIOSKI:\n")
        f.write("-"*80 + "\n")

        best_algo = min(results.items(),
                       key=lambda x: x[1]["C_max"] if x[1] is not None else float('inf'))
        f.write(f"- Najlepsze rozwiązanie: {best_algo[0]} (C_max = {best_algo[1]['C_max']:.2f})\n")

        fastest_algo = min(((k, v) for k, v in results.items() if v and v["time_ms"] > 0),
                          key=lambda x: x[1]["time_ms"])
        f.write(f"- Najszybszy algorytm: {fastest_algo[0]} ({fastest_algo[1]['time_ms']:.2f}ms)\n")

        if results.get("Branch & Bound"):
            f.write(f"- Rozwiązanie optymalne (B&B): {results['Branch & Bound']['C_max']:.2f}\n")

        f.write("\n" + "="*80 + "\n")

    print(f"[SAVED] Raport tekstowy: {report_file}")


def main():
    """Główna funkcja programu."""
    print_header("INTERAKTYWNY TESTER ALGORYTMÓW HFS-SDST")

    print("Wybierz tryb pracy:")
    print("  1. Wygeneruj nową instancję i przetestuj")
    print("  2. Użyj istniejącego pliku")

    choice = get_user_input("Wybór", "1", str)

    instance_file = None

    if choice == "1":
        # Generuj nową instancję
        instance = generate_instance_interactive()

        save_choice = get_user_input("\nCzy zapisać instancję do pliku? (y/n)", "y", str)
        if save_choice.lower() in ["y", "yes", "tak", "t"]:
            instance_file = save_instance(instance)
        else:
            # Zapisz tymczasowo
            temp_dir = "../data/temp"
            os.makedirs(temp_dir, exist_ok=True)
            instance_file = os.path.join(temp_dir, "temp_instance.json")
            with open(instance_file, "w", encoding="utf-8") as f:
                json.dump(instance, f, indent=2, ensure_ascii=False)

    else:
        # Użyj istniejącego pliku
        default_file = "../data/default.json"
        instance_file = get_user_input("\nŚcieżka do pliku", default_file, str)

        if not os.path.exists(instance_file):
            print(f"[ERROR] Plik nie istnieje: {instance_file}")
            return

    # Uruchom algorytmy
    output_dir = "../results/interactive_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    results = run_all_algorithms(instance_file, output_dir)

    # Generuj wizualizacje
    generate_comparison_charts(results, output_dir)
    generate_gantt_charts(results, output_dir)
    generate_report(results, output_dir)

    print_header("ZAKOŃCZONO")
    print(f"Wszystkie wyniki zapisane w: {output_dir}")
    print("\nWygenerowane pliki:")
    print(f"  - comparison_chart.png    (wykres porównawczy C_max)")
    print(f"  - tradeoff_chart.png      (trade-off: jakość vs czas)")
    print(f"  - gantt_*.png             (diagramy Gantta)")
    print(f"  - report.txt              (szczegółowy raport tekstowy)")
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program przerwany przez użytkownika.")
    except Exception as e:
        print(f"\n[ERROR] Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()

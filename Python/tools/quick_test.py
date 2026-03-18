"""
Szybki test algorytmów z parametrami z linii poleceń.

Użycie:
    python quick_test.py                           # domyślne parametry (8 zadań, 2 etapy)
    python quick_test.py --jobs 10 --stages 3      # własne parametry
    python quick_test.py --help                    # pomoc

Generuje instancję problemu i porównuje wszystkie algorytmy.
"""

import sys
import io
import json
import os
import random
import argparse
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


def generate_random_instance(num_jobs, num_stages, machines_per_stage=None,
                            learning_coeff=0.1, proc_time_range=(5, 20),
                            setup_time_range=(1, 5)):
    """
    Generuje losową instancję problemu HFS-SDST.

    Args:
        num_jobs: liczba zadań
        num_stages: liczba etapów
        machines_per_stage: lista liczby maszyn na etapach (None = automatyczne)
        learning_coeff: współczynnik uczenia
        proc_time_range: zakres czasów przetwarzania (min, max)
        setup_time_range: zakres czasów przezbrojenia (min, max)

    Returns:
        dict: instancja problemu
    """
    if machines_per_stage is None:
        # Domyślnie: 1-2 maszyny na etap, losowo
        machines_per_stage = [random.randint(1, 2) for _ in range(num_stages)]

    # Uczenie na wszystkich etapach oprócz pierwszego
    learning_stages = "0" + "1" * (num_stages - 1)

    # Generacja czasów przetwarzania
    proc_min, proc_max = proc_time_range
    processing_times = []
    for job in range(num_jobs):
        job_stages = []
        for stage in range(num_stages):
            stage_machines = []
            for machine in range(machines_per_stage[stage]):
                time = random.randint(proc_min, proc_max)
                stage_machines.append([time])
            job_stages.append(stage_machines)
        processing_times.append(job_stages)

    # Generacja czasów przezbrojenia
    setup_min, setup_max = setup_time_range
    setup_times = []
    for from_job in range(num_jobs):
        from_job_setups = []
        for to_job in range(num_jobs):
            to_job_setups = []
            for stage in range(num_stages):
                stage_setups = []
                for machine in range(machines_per_stage[stage]):
                    if from_job == to_job:
                        # Self-setup - 50% normalnego czasu
                        time = int(setup_min + (setup_max - setup_min) * 0.5)
                    else:
                        time = random.randint(setup_min, setup_max)
                    stage_setups.append([time])
                to_job_setups.append(stage_setups)
            from_job_setups.append(to_job_setups)
        setup_times.append(from_job_setups)

    return {
        "algorithm": "tabu",
        "num_jobs": num_jobs,
        "num_stages": num_stages,
        "machines_per_stage": machines_per_stage,
        "learning_coefficient": learning_coeff,
        "learning_stages": learning_stages,
        "processing_times": processing_times,
        "setup_times": setup_times
    }


def run_test(instance, output_dir, run_bnb=True):
    """
    Uruchamia wszystkie algorytmy dla danej instancji.

    Args:
        instance: dane problemu
        output_dir: katalog na wyniki
        run_bnb: czy uruchamiać Branch & Bound

    Returns:
        dict: wyniki wszystkich algorytmów
    """
    os.makedirs(output_dir, exist_ok=True)

    # Zapisz instancję
    instance_file = os.path.join(output_dir, "instance.json")
    with open(instance_file, "w", encoding="utf-8") as f:
        json.dump(instance, f, indent=2, ensure_ascii=False)

    num_jobs = instance["num_jobs"]
    num_stages = instance["num_stages"]

    print(f"\n{'='*80}")
    print(f"{'QUICK TEST - PORÓWNANIE ALGORYTMÓW':^80}")
    print(f"{'='*80}\n")

    print(f"Instancja: {num_jobs} zadań, {num_stages} etapów")
    print(f"Maszyny: {instance['machines_per_stage']}")
    print(f"Uczenie: α={instance['learning_coefficient']}, etapy={instance['learning_stages']}\n")

    results = {}

    # === NATURAL ===
    print("[1/4] Natural Order...")
    schedule = Schedule()
    schedule.load_from_json(instance_file)
    natural_seq = list(range(num_jobs))
    cmax_natural = schedule.build_from_sequence(natural_seq)
    results["Natural"] = {
        "sequence": natural_seq,
        "C_max": cmax_natural,
        "time_ms": 0
    }
    print(f"      C_max = {cmax_natural:.2f}")

    # === GREEDY ===
    print("[2/4] MinSTF...")
    schedule = Schedule()
    schedule.load_from_json(instance_file)
    algo = MinSTF(schedule)
    res = algo.run()
    results["Greedy"] = {
        "sequence": algo.best_sequence,
        "C_max": res["C_max"],
        "time_ms": res["time_in_ms"]
    }
    improvement = ((cmax_natural - res["C_max"]) / cmax_natural) * 100
    print(f"      C_max = {res['C_max']:.2f} ({improvement:+.1f}%) | Czas: {res['time_in_ms']:.2f}ms")

    # === TABU SEARCH ===
    print("[3/4] Tabu Search...")
    schedule = Schedule()
    schedule.load_from_json(instance_file)
    algo = TabuSearch(schedule, max_iter=100, tabu_tenure=10, no_improve_limit=20)
    res = algo.run()
    results["Tabu"] = {
        "sequence": algo.best_sequence,
        "C_max": res["C_max"],
        "time_ms": res["time_in_ms"]
    }
    improvement = ((cmax_natural - res["C_max"]) / cmax_natural) * 100
    print(f"      C_max = {res['C_max']:.2f} ({improvement:+.1f}%) | Czas: {res['time_in_ms']:.2f}ms")

    # === BRANCH & BOUND ===
    if run_bnb and num_jobs <= 10:
        print("[4/4] Branch & Bound...")
        schedule = Schedule()
        schedule.load_from_json(instance_file)
        algo = BranchAndBound(schedule)
        res = algo.run()
        results["B&B"] = {
            "sequence": algo.best_sequence,
            "C_max": res["C_max"],
            "time_ms": res["time_in_ms"]
        }
        improvement = ((cmax_natural - res["C_max"]) / cmax_natural) * 100
        print(f"      C_max = {res['C_max']:.2f} ({improvement:+.1f}%) | Czas: {res['time_in_ms']:.2f}ms")
    else:
        print("[4/4] Branch & Bound... SKIPPED (n > 10)")
        results["B&B"] = None

    # === PODSUMOWANIE ===
    print(f"\n{'='*80}")
    print(f"{'PODSUMOWANIE':^80}")
    print(f"{'='*80}\n")

    print(f"{'Algorytm':<15} {'C_max':<12} {'Poprawa':<12} {'Czas [ms]':<12} {'Sekwencja':<30}")
    print("-"*80)

    for name, data in results.items():
        if data:
            improvement = ((cmax_natural - data["C_max"]) / cmax_natural) * 100 if name != "Natural" else 0
            seq_str = str(data["sequence"][:8])
            if len(data["sequence"]) > 8:
                seq_str = seq_str[:-1] + ",...]"
            time_str = f"{data['time_ms']:.2f}" if data["time_ms"] > 0 else "—"
            improve_str = f"{improvement:+.1f}%" if name != "Natural" else "baseline"
            print(f"{name:<15} {data['C_max']:<12.2f} {improve_str:<12} {time_str:<12} {seq_str:<30}")

    print("-"*80)

    # Najlepszy algorytm
    best = min((k, v) for k, v in results.items() if v is not None)
    print(f"\n✓ Najlepsze rozwiązanie: {best[0]} (C_max = {best[1]['C_max']:.2f})")

    if results.get("B&B"):
        print(f"✓ Rozwiązanie optymalne: {results['B&B']['C_max']:.2f}")

    print(f"\n{'='*80}\n")

    # Zapisz wyniki
    results_file = os.path.join(output_dir, "results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Wyniki zapisane w: {output_dir}")

    return results


def main():
    """Główna funkcja programu."""
    parser = argparse.ArgumentParser(
        description="Szybki test algorytmów HFS-SDST",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python quick_test.py                              # domyślne: 8 zadań, 2 etapy
  python quick_test.py --jobs 10 --stages 3         # 10 zadań, 3 etapy
  python quick_test.py -j 6 -s 2 -a 0.2            # z własnym współczynnikiem uczenia
  python quick_test.py --jobs 12 --no-bnb          # bez Branch & Bound
        """
    )

    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=8,
        help="Liczba zadań (domyślnie: 8)"
    )

    parser.add_argument(
        "-s", "--stages",
        type=int,
        default=2,
        help="Liczba etapów (domyślnie: 2)"
    )

    parser.add_argument(
        "-a", "--alpha",
        type=float,
        default=0.1,
        help="Współczynnik uczenia (domyślnie: 0.1)"
    )

    parser.add_argument(
        "-m", "--machines",
        type=str,
        default=None,
        help="Liczba maszyn na etapach (np. '2,2,1')"
    )

    parser.add_argument(
        "--proc-min",
        type=int,
        default=5,
        help="Min czas przetwarzania (domyślnie: 5)"
    )

    parser.add_argument(
        "--proc-max",
        type=int,
        default=20,
        help="Max czas przetwarzania (domyślnie: 20)"
    )

    parser.add_argument(
        "--setup-min",
        type=int,
        default=1,
        help="Min czas przezbrojenia (domyślnie: 1)"
    )

    parser.add_argument(
        "--setup-max",
        type=int,
        default=5,
        help="Max czas przezbrojenia (domyślnie: 5)"
    )

    parser.add_argument(
        "--no-bnb",
        action="store_true",
        help="Nie uruchamiaj Branch & Bound"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Katalog na wyniki (domyślnie: ../results/quick_test_TIMESTAMP)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed dla generatora liczb losowych (dla powtarzalności)"
    )

    args = parser.parse_args()

    # Ustaw seed jeśli podany
    if args.seed is not None:
        random.seed(args.seed)
        print(f"[INFO] Ustawiono seed: {args.seed}")

    # Parsuj maszyny
    machines_per_stage = None
    if args.machines:
        machines_per_stage = [int(x.strip()) for x in args.machines.split(",")]
        if len(machines_per_stage) != args.stages:
            print(f"[ERROR] Liczba maszyn ({len(machines_per_stage)}) nie pasuje do liczby etapów ({args.stages})")
            return

    # Generuj instancję
    print("\n[INFO] Generowanie losowej instancji...")
    instance = generate_random_instance(
        num_jobs=args.jobs,
        num_stages=args.stages,
        machines_per_stage=machines_per_stage,
        learning_coeff=args.alpha,
        proc_time_range=(args.proc_min, args.proc_max),
        setup_time_range=(args.setup_min, args.setup_max)
    )

    # Katalog na wyniki
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"../results/quick_test_{timestamp}"

    # Uruchom test
    run_test(instance, output_dir, run_bnb=not args.no_bnb)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program przerwany przez użytkownika.")
    except Exception as e:
        print(f"\n[ERROR] Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()

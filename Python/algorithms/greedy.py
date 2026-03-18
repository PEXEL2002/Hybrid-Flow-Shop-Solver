"""Algorytm zachłanny Min Setup Time First (MSTF).

Heurystyka konstrukcyjna dla problemu HFS-SDST z efektem uczenia.
Minimalizuje czasy przezbrojeń poprzez sekwencyjny wybór zadania
o najmniejszym czasie przezbrojenia.

Złożoność czasowa: O(n²), gdzie n to liczba zadań.
"""

import time
from algorithms.base_algorithm import BaseAlgorithm


class MinSTF(BaseAlgorithm):
    """Algorytm Min Setup Time First (MSTF).

    Heurystyka zachłanna budująca permutację zadań poprzez iteracyjny
    wybór zadania o minimalnym czasie przezbrojenia względem poprzednio
    wybranego zadania.

    Pierwsze zadanie wybierane jest deterministycznie (najmniejszy czas
    przezbrojenia samego ze sobą), następnie każde kolejne zadanie
    minimalizuje łączny czas przezbrojenia na wszystkich etapach i maszynach.
    """

    def __init__(self, schedule):
        """Inicjalizuje algorytm MinSTF.

        Args:
            schedule (Schedule): Obiekt harmonogramu z danymi problemu.
        """
        super().__init__(schedule, name="MinSTF")

    def _calculate_setup_time(self, job_id, prev_job_id=None):
        """Oblicza średni czas przezbrojenia dla zadania.

        Uśrednia czasy przezbrojenia na wszystkich etapach i maszynach.

        Args:
            job_id (int): Identyfikator zadania docelowego.
            prev_job_id (int, optional): Identyfikator zadania poprzedniego.
                Jeśli None, oblicza self-setup (inicjalne przezbrojenie).

        Returns:
            float: Średni czas przezbrojenia.
        """
        if prev_job_id is None:
            prev_job_id = job_id

        job = self.schedule.jobs[job_id]
        setup_times = [
            job.get_setup_time(prev_job_id, stage, machine)
            for stage in range(self.schedule.num_stages)
            for machine in range(self.schedule.machines_per_stage[stage])
        ]

        return sum(setup_times) / len(setup_times) if setup_times else 0.0

    def run(self):
        """Uruchamia algorytm MSTF.

        Algorytm:
        1. Wybiera pierwsze zadanie o najmniejszym self-setup
        2. Iteracyjnie dodaje zadania o minimalnym czasie przezbrojenia
           względem ostatnio dodanego zadania
        3. Buduje pełny harmonogram dla znalezionej sekwencji

        Returns:
            dict: Wyniki zawierające C_max, czas wykonania i harmonogram.
        """
        start_time = time.time()
        n_jobs = len(self.schedule.jobs)

        print(f"\n[MinSTF] Uruchamianie algorytmu MinSTF...")

        remaining_jobs = set(range(n_jobs))
        sequence = []

        # === Krok 1: Wybór pierwszego zadania (najmniejszy self-setup) ===
        min_self_setup = float('inf')
        first_job = 0

        for candidate in remaining_jobs:
            avg_setup = self._calculate_setup_time(candidate)
            if avg_setup < min_self_setup:
                min_self_setup = avg_setup
                first_job = candidate

        sequence.append(first_job)
        remaining_jobs.remove(first_job)

        # === Krok 2: Iteracyjny wybór kolejnych zadań ===
        while remaining_jobs:
            last_job = sequence[-1]
            min_setup = float('inf')
            best_job = None

            # --- Wybór zadania o minimalnym czasie przezbrojenia ---
            for candidate in remaining_jobs:
                avg_setup = self._calculate_setup_time(candidate, last_job)
                if avg_setup < min_setup:
                    min_setup = avg_setup
                    best_job = candidate

            sequence.append(best_job)
            remaining_jobs.remove(best_job)

        # === Budowa pełnego harmonogramu dla znalezionej sekwencji ===
        cmax = self.schedule.build_from_sequence(sequence)

        self.best_sequence = sequence
        self.best_cmax = cmax
        self.result_schedule = self.schedule.to_json()
        self.runtime = time.time() - start_time

        print(f"[MinSTF] Zakończono. C_max = {cmax:.2f}, Czas: {self.runtime:.3f}s")

        return self.get_results()

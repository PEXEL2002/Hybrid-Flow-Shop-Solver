from copy import deepcopy
import math
import time
from .base_algorithm import BaseAlgorithm

class BranchAndBound(BaseAlgorithm):
    """Algorytm Branch and Bound dla problemu HFS-SDST.

    Algorytm dokładny przeszukujący drzewo rozwiązań z obcinaniem
    gałęzi na podstawie dolnego ograniczenia (lower bound).

    Attributes:
        ub_start (float): Początkowe górne ograniczenie (upper bound).
    """

    def __init__(self, schedule):
        """Inicjalizuje algorytm Branch and Bound.

        Args:
            schedule (Schedule): Obiekt harmonogramu z danymi problemu.
        """
        super().__init__(schedule, name="Branch and Bound")
        self.ub_start = math.inf

    def compute_lower_bound(self, partial_seq, remaining_jobs):
        """Oblicza dolne ograniczenie dla częściowej permutacji.

        Oblicza rzeczywisty Cmax dla partial_seq. Jeśli są pozostałe zadania,
        dolne ograniczenie = current_cmax (zachowawcze podejście).

        Args:
            partial_seq (list[int]): Częściowa permutacja zadań.
            remaining_jobs (list[int]): Pozostałe zadania do zaplanowania.

        Returns:
            float: Dolne ograniczenie Cmax dla częściowego rozwiązania.
        """
        if not partial_seq:
            return 0.0

        # Oblicz rzeczywisty Cmax dla partial_seq
        temp = deepcopy(self.schedule)
        current_cmax = temp.build_from_sequence(partial_seq)

        return current_cmax

    def run(self):
        """Uruchamia algorytm Branch and Bound.

        Przeszukuje drzewo rozwiązań metodą DFS z obcinaniem gałęzi.
        Górne ograniczenie inicjalizowane jest harmonogramem naturalnym.

        Returns:
            dict: Wyniki zawierające C_max, czas wykonania i harmonogram.
        """
        start_time = time.time()

        print(f"\n[B&B] Uruchamianie algorytmu Branch & Bound...")

        n = len(self.schedule.jobs)

        # === Inicjalizacja górnego ograniczenia (UB) harmonogramem naturalnym ===
        temp = deepcopy(self.schedule)
        ub = temp.build_from_sequence(list(range(n)))
        best_cmax = ub
        best_seq = list(range(n))

        stack = [([], list(range(n)))]

        while stack:
            partial, remaining = stack.pop()

            # === Sprawdzenie pełnego rozwiązania ===
            if not remaining:
                temp = deepcopy(self.schedule)
                cmax = temp.build_from_sequence(partial)

                # --- Aktualizacja najlepszego rozwiązania (UB) ---
                if cmax < best_cmax:
                    best_cmax = cmax
                    best_seq = partial
                continue

            # === Obliczenie dolnego ograniczenia (LB) ===
            lb = self.compute_lower_bound(partial, remaining)

            # --- Odcięcie gałęzi: LB >= UB ---
            if lb >= best_cmax:
                continue

            # === Rozwijanie gałęzi - dodanie kolejnych zadań ===
            for j in remaining:
                new_partial = partial + [j]
                new_remaining = [r for r in remaining if r != j]
                stack.append((new_partial, new_remaining))

        self.best_sequence = best_seq
        self.best_cmax = best_cmax

        temp = deepcopy(self.schedule)
        temp.build_from_sequence(best_seq)
        self.result_schedule = temp.to_json()

        end_time = time.time()
        self.runtime = end_time - start_time

        print(f"[B&B] Zakończono. C_max = {best_cmax:.2f}, Czas: {self.runtime:.3f}s")

        return self.get_results()

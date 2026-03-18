"""Algorytm metaheurystyczny Tabu Search.

Metaheurystyka dla problemu HFS-SDST z efektem uczenia.
Przeszukuje sąsiedztwo z pamięcią krótkoterminową (lista tabu)
oraz kryterium aspiracji, umożliwiając ucieczkę z lokalnych minimów.

Złożoność czasowa: O(k × n²), gdzie k to liczba iteracji, n to liczba zadań.
"""

import time
from algorithms.base_algorithm import BaseAlgorithm
from algorithms.greedy import MinSTF


class TabuSearch(BaseAlgorithm):
    """Algorytm Tabu Search dla problemu HFS-SDST.

    Metaheurystyka iteracyjnie przeszukująca przestrzeń rozwiązań poprzez
    ruchy swap w sąsiedztwie, z zakazem powrotu do ostatnio odwiedzonych
    rozwiązań oraz możliwością złamania zakazu przy kryterium aspiracji.

    Attributes:
        max_iter (int): Maksymalna liczba iteracji.
        tabu_tenure (int): Długość listy tabu (liczba iteracji).
        no_improve_limit (int): Limit iteracji bez poprawy dla wcześniejszego stopu.
        tabu_list (dict): Mapa ruchów tabu {(i,j): iteracja_wygaśnięcia}.
        iterations_performed (int): Liczba wykonanych iteracji.
        iterations_without_improvement (int): Liczba iteracji bez poprawy.
    """

    def __init__(self, schedule, max_iter=100, tabu_tenure=10, no_improve_limit=10):
        """Inicjalizuje algorytm Tabu Search.

        Args:
            schedule (Schedule): Obiekt harmonogramu z danymi problemu.
            max_iter (int, optional): Maksymalna liczba iteracji. Domyślnie 100.
            tabu_tenure (int, optional): Długość listy tabu. Domyślnie 10.
            no_improve_limit (int, optional): Limit iteracji bez poprawy. Domyślnie 10.
        """
        super().__init__(schedule, name="Tabu-Search")
        self.max_iter = max_iter
        self.tabu_tenure = tabu_tenure
        self.no_improve_limit = no_improve_limit
        self.tabu_list = {}
        self.iterations_performed = 0
        self.iterations_without_improvement = 0

    def run(self):
        """Uruchamia algorytm Tabu Search.

        Generuje rozwiązanie początkowe metodą MinSTF, następnie iteracyjnie
        przeszukuje sąsiedztwo z wykorzystaniem listy tabu i kryterium aspiracji.

        Returns:
            dict: Wyniki zawierające C_max, czas wykonania i harmonogram.
        """
        start_time = time.time()
        n_jobs = len(self.schedule.jobs)

        print(f"\n[TABU] Uruchamianie algorytmu Tabu Search...")
        print(f"[TABU] Parametry: max_iter={self.max_iter}, tabu_tenure={self.tabu_tenure}, no_improve_limit={self.no_improve_limit}")

        # === Generacja rozwiązania początkowego (MinSTF) ===
        current_sequence = self._generate_initial_solution()
        current_cmax = self.schedule.build_from_sequence(current_sequence)

        best_sequence = current_sequence.copy()
        best_cmax = current_cmax

        print(f"[TABU] Rozwiazanie poczatkowe: C_max = {current_cmax:.2f}")

        for iteration in range(self.max_iter):
            self.iterations_performed = iteration + 1

            # === Generacja sąsiedztwa (operacja swap) ===
            neighbors = self._generate_neighborhood(current_sequence)

            # === Wybór najlepszego sąsiada z uwzględnieniem listy tabu ===
            best_neighbor, best_neighbor_cmax, move = self._select_best_neighbor(
                neighbors, current_sequence, best_cmax, iteration
            )

            current_sequence = best_neighbor
            current_cmax = best_neighbor_cmax

            # --- Aktualizacja globalnie najlepszego rozwiązania ---
            if current_cmax < best_cmax:
                best_sequence = current_sequence.copy()
                best_cmax = current_cmax
                self.iterations_without_improvement = 0
                print(f"[TABU] Iteracja {iteration+1}: nowe najlepsze! C_max = {best_cmax:.2f}")
            else:
                self.iterations_without_improvement += 1
                if (iteration + 1) % 20 == 0:
                    print(f"[TABU] Iteracja {iteration+1}: najlepszy C_max = {best_cmax:.2f}")

            # === Dodanie ruchu do listy tabu ===
            if move:
                self._add_to_tabu(move, iteration)

            # --- Kryterium stopu: brak poprawy ---
            if self.iterations_without_improvement >= self.no_improve_limit:
                break

        best_cmax = self.schedule.build_from_sequence(best_sequence)

        self.best_sequence = best_sequence
        self.best_cmax = best_cmax
        self.result_schedule = self.schedule.to_json()
        self.runtime = time.time() - start_time

        print(f"[TABU] Zakończono po {self.iterations_performed} iteracjach. C_max = {best_cmax:.2f}, Czas: {self.runtime:.3f}s")

        return self.get_results()

    def _generate_initial_solution(self):
        """Generuje rozwiązanie początkowe za pomocą algorytmu MinSTF.

        Returns:
            list[int]: Permutacja zadań wygenerowana przez MinSTF.
        """
        minstf = MinSTF(self.schedule)
        minstf.run()
        return minstf.best_sequence

    def _generate_neighborhood(self, sequence):
        """Generuje sąsiedztwo bieżącego rozwiązania operacją swap.

        Sąsiedztwo N(S) zawiera wszystkie permutacje powstałe przez zamianę
        miejscami dwóch zadań w sekwencji.

        Args:
            sequence (list[int]): Bieżąca permutacja zadań.

        Returns:
            list[tuple]: Lista krotek (nowa_sekwencja, (i, j)) dla każdego możliwego swap.
        """
        n = len(sequence)
        neighbors = []

        for i in range(n):
            for j in range(i + 1, n):
                neighbor = sequence.copy()
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbors.append((neighbor, (i, j)))

        return neighbors

    def _select_best_neighbor(self, neighbors, current_sequence, global_best_cmax, current_iteration):
        """Wybiera najlepszego sąsiada z uwzględnieniem listy tabu.

        Reguły wyboru:
        1. Preferuj sąsiada z najmniejszym C_max
        2. Ruch tabu dozwolony jeśli spełnia kryterium aspiracji (C_max < global_best)

        Args:
            neighbors (list[tuple]): Lista krotek (sekwencja, ruch).
            current_sequence (list[int]): Bieżąca sekwencja.
            global_best_cmax (float): Najlepszy dotychczas znaleziony C_max.
            current_iteration (int): Numer bieżącej iteracji.

        Returns:
            tuple: (najlepsza_sekwencja, C_max, ruch).
        """
        best_neighbor = None
        best_cmax = float('inf')
        best_move = None

        for neighbor_seq, move in neighbors:
            # --- Sprawdzenie czy ruch jest na liście tabu ---
            if self._is_tabu(move, current_iteration):
                neighbor_cmax = self.schedule.build_from_sequence(neighbor_seq)

                # === Kryterium aspiracji: akceptacja ruchu tabu jeśli poprawia globalnie najlepsze ===
                if neighbor_cmax < global_best_cmax:
                    if neighbor_cmax < best_cmax:
                        best_neighbor = neighbor_seq
                        best_cmax = neighbor_cmax
                        best_move = move
                continue

            # --- Ruch nie jest tabu - ocena standardowa ---
            neighbor_cmax = self.schedule.build_from_sequence(neighbor_seq)

            if neighbor_cmax < best_cmax:
                best_neighbor = neighbor_seq
                best_cmax = neighbor_cmax
                best_move = move

        # === Awaryjne rozwiązanie: wybór najlepszego sąsiada ignorując listę tabu ===
        if best_neighbor is None:
            for neighbor_seq, move in neighbors:
                neighbor_cmax = self.schedule.build_from_sequence(neighbor_seq)
                if neighbor_cmax < best_cmax:
                    best_neighbor = neighbor_seq
                    best_cmax = neighbor_cmax
                    best_move = move

        return best_neighbor, best_cmax, best_move

    def _is_tabu(self, move, current_iteration):
        """Sprawdza czy ruch znajduje się na liście tabu.

        Args:
            move (tuple): Para (i, j) oznaczająca zamianę zadań.
            current_iteration (int): Numer bieżącej iteracji.

        Returns:
            bool: True jeśli ruch jest tabu, False w przeciwnym razie.
        """
        i, j = move
        moves_to_check = [(i, j), (j, i)]

        # === Sprawdzenie obu reprezentacji ruchu (i,j) i (j,i) ===
        for m in moves_to_check:
            if m in self.tabu_list:
                expiration_iter = self.tabu_list[m]
                # --- Ruch jest tabu jeśli jeszcze nie wygasł ---
                if current_iteration < expiration_iter:
                    return True

        return False

    def _add_to_tabu(self, move, current_iteration):
        """Dodaje ruch do listy tabu.

        Ruch pozostanie na liście przez tabu_tenure iteracji.

        Args:
            move (tuple): Para (i, j) oznaczająca zamianę zadań.
            current_iteration (int): Numer bieżącej iteracji.
        """
        i, j = move
        # === Obliczenie iteracji wygaśnięcia ===
        expiration_iter = current_iteration + self.tabu_tenure

        # --- Dodanie obu reprezentacji ruchu do listy tabu ---
        self.tabu_list[(i, j)] = expiration_iter
        self.tabu_list[(j, i)] = expiration_iter

        # === Czyszczenie wygasłych wpisów ===
        self._clean_tabu_list(current_iteration)

    def _clean_tabu_list(self, current_iteration):
        """Usuwa wygasłe wpisy z listy tabu.

        Args:
            current_iteration (int): Numer bieżącej iteracji.
        """
        expired_moves = [move for move, exp_iter in self.tabu_list.items()
                        if exp_iter <= current_iteration]
        for move in expired_moves:
            del self.tabu_list[move]


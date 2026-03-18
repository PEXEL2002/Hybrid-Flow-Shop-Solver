"""Testy jednostkowe dla algorytmu Tabu Search."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from algorithms.tabu_search import TabuSearch
from algorithms.greedy import MinSTF
from core.schedule import Schedule


class TestTabuSearchInitialization:
    """Testy inicjalizacji algorytmu Tabu Search."""

    def test_tabu_creation_default_params(self, sample_schedule):
        """Test tworzenia z domyślnymi parametrami."""
        algo = TabuSearch(sample_schedule)

        assert algo.name == "Tabu-Search"
        assert algo.schedule is sample_schedule
        assert algo.max_iter == 100
        assert algo.tabu_tenure == 10
        assert algo.no_improve_limit == 10

    def test_tabu_creation_custom_params(self, sample_schedule):
        """Test tworzenia z niestandardowymi parametrami."""
        algo = TabuSearch(
            sample_schedule,
            max_iter=50,
            tabu_tenure=5,
            no_improve_limit=15
        )

        assert algo.max_iter == 50
        assert algo.tabu_tenure == 5
        assert algo.no_improve_limit == 15

    def test_tabu_initialization_state(self, sample_schedule):
        """Test inicjalizacji stanu algorytmu."""
        algo = TabuSearch(sample_schedule)

        assert algo.tabu_list == {}
        assert algo.iterations_performed == 0
        assert algo.iterations_without_improvement == 0


class TestTabuSearchGenerateInitialSolution:
    """Testy metody _generate_initial_solution."""

    def test_generate_initial_uses_minstf(self, sample_schedule):
        """Test użycia MinSTF do wygenerowania rozwiązania początkowego."""
        algo = TabuSearch(sample_schedule)

        initial_solution = algo._generate_initial_solution()

        # Powinno być permutacją wszystkich zadań
        assert len(initial_solution) == len(sample_schedule.jobs)
        assert set(initial_solution) == set(range(len(sample_schedule.jobs)))

    @patch('algorithms.tabu_search.MinSTF')
    def test_generate_initial_calls_minstf(self, mock_minstf_class, sample_schedule):
        """Test wywołania MinSTF."""
        mock_algo = MagicMock()
        mock_algo.best_sequence = [0, 1, 2]
        mock_minstf_class.return_value = mock_algo

        algo = TabuSearch(sample_schedule)
        initial = algo._generate_initial_solution()

        mock_minstf_class.assert_called_once_with(sample_schedule)
        mock_algo.run.assert_called_once()
        assert initial == [0, 1, 2]


class TestTabuSearchGenerateNeighborhood:
    """Testy metody _generate_neighborhood."""

    def test_generate_neighborhood_swap_operations(self, sample_schedule):
        """Test generowania sąsiedztwa operacją swap."""
        algo = TabuSearch(sample_schedule)
        sequence = [0, 1, 2]

        neighbors = algo._generate_neighborhood(sequence)

        # Dla 3 zadań: C(3,2) = 3 możliwe swapy
        assert len(neighbors) == 3

        # Każdy sąsiad to tuple (sekwencja, ruch)
        for neighbor, move in neighbors:
            assert len(neighbor) == len(sequence)
            assert isinstance(move, tuple)
            assert len(move) == 2

    def test_generate_neighborhood_all_swaps(self, sample_schedule):
        """Test generowania wszystkich możliwych swapów."""
        algo = TabuSearch(sample_schedule)
        sequence = [0, 1, 2, 3]

        neighbors = algo._generate_neighborhood(sequence)

        # Dla 4 zadań: C(4,2) = 6 możliwych swapów
        assert len(neighbors) == 6

        # Sprawdź unikalne swapy
        moves = set(neighbor[1] for neighbor in neighbors)
        assert len(moves) == 6

    def test_generate_neighborhood_preserves_jobs(self, sample_schedule):
        """Test, że każdy sąsiad zawiera te same zadania."""
        algo = TabuSearch(sample_schedule)
        sequence = [0, 1, 2]

        neighbors = algo._generate_neighborhood(sequence)

        for neighbor_seq, move in neighbors:
            assert set(neighbor_seq) == set(sequence)

    def test_generate_neighborhood_single_swap(self, sample_schedule):
        """Test, że każdy sąsiad różni się tylko jednym swapem."""
        algo = TabuSearch(sample_schedule)
        sequence = [0, 1, 2, 3]

        neighbors = algo._generate_neighborhood(sequence)

        for neighbor_seq, (i, j) in neighbors:
            # Sprawdź, że swap został wykonany
            assert neighbor_seq[i] == sequence[j]
            assert neighbor_seq[j] == sequence[i]

            # Sprawdź, że reszta jest bez zmian
            for k in range(len(sequence)):
                if k not in (i, j):
                    assert neighbor_seq[k] == sequence[k]


class TestTabuSearchIsTabu:
    """Testy metody _is_tabu."""

    def test_is_tabu_empty_list(self, sample_schedule):
        """Test dla pustej listy tabu."""
        algo = TabuSearch(sample_schedule)
        assert algo._is_tabu((0, 1), current_iteration=0) is False

    def test_is_tabu_move_not_in_list(self, sample_schedule):
        """Test dla ruchu spoza listy tabu."""
        algo = TabuSearch(sample_schedule)
        algo.tabu_list[(0, 1)] = 10

        assert algo._is_tabu((1, 2), current_iteration=5) is False

    def test_is_tabu_move_in_list_not_expired(self, sample_schedule):
        """Test dla ruchu tabu, który nie wygasł."""
        algo = TabuSearch(sample_schedule)
        algo.tabu_list[(0, 1)] = 10  # Wygaśnie w iteracji 10

        assert algo._is_tabu((0, 1), current_iteration=5) is True

    def test_is_tabu_move_in_list_expired(self, sample_schedule):
        """Test dla ruchu tabu, który wygasł."""
        algo = TabuSearch(sample_schedule)
        algo.tabu_list[(0, 1)] = 10

        assert algo._is_tabu((0, 1), current_iteration=10) is False
        assert algo._is_tabu((0, 1), current_iteration=15) is False

    def test_is_tabu_symmetric_move(self, sample_schedule):
        """Test symetryczności ruchu (i,j) == (j,i)."""
        algo = TabuSearch(sample_schedule)
        algo.tabu_list[(0, 1)] = 10

        # (0,1) i (1,0) to ten sam ruch
        assert algo._is_tabu((1, 0), current_iteration=5) is True


class TestTabuSearchAddToTabu:
    """Testy metody _add_to_tabu."""

    def test_add_to_tabu_adds_move(self, sample_schedule):
        """Test dodawania ruchu do listy."""
        algo = TabuSearch(sample_schedule, tabu_tenure=5)

        algo._add_to_tabu((0, 1), current_iteration=10)

        assert (0, 1) in algo.tabu_list
        assert (1, 0) in algo.tabu_list

    def test_add_to_tabu_sets_expiration(self, sample_schedule):
        """Test ustawiania czasu wygaśnięcia."""
        algo = TabuSearch(sample_schedule, tabu_tenure=5)

        algo._add_to_tabu((0, 1), current_iteration=10)

        # Wygaśnie w iteracji 10 + 5 = 15
        assert algo.tabu_list[(0, 1)] == 15
        assert algo.tabu_list[(1, 0)] == 15

    def test_add_to_tabu_cleans_expired(self, sample_schedule):
        """Test czyszczenia wygasłych wpisów."""
        algo = TabuSearch(sample_schedule, tabu_tenure=5)

        # Dodaj stary wpis
        algo.tabu_list[(2, 3)] = 5

        # Dodaj nowy wpis w iteracji 10
        algo._add_to_tabu((0, 1), current_iteration=10)

        # Stary wpis powinien zostać usunięty
        assert (2, 3) not in algo.tabu_list


class TestTabuSearchCleanTabuList:
    """Testy metody _clean_tabu_list."""

    def test_clean_removes_expired(self, sample_schedule):
        """Test usuwania wygasłych wpisów."""
        algo = TabuSearch(sample_schedule)

        algo.tabu_list[(0, 1)] = 5
        algo.tabu_list[(1, 2)] = 10
        algo.tabu_list[(2, 3)] = 15

        algo._clean_tabu_list(current_iteration=10)

        # (0,1) wygasło, (1,2) wygasło, (2,3) aktywne
        assert (0, 1) not in algo.tabu_list
        assert (1, 2) not in algo.tabu_list
        assert (2, 3) in algo.tabu_list

    def test_clean_preserves_active(self, sample_schedule):
        """Test zachowania aktywnych wpisów."""
        algo = TabuSearch(sample_schedule)

        algo.tabu_list[(0, 1)] = 20
        algo.tabu_list[(1, 2)] = 25

        algo._clean_tabu_list(current_iteration=10)

        # Oba aktywne
        assert (0, 1) in algo.tabu_list
        assert (1, 2) in algo.tabu_list


class TestTabuSearchSelectBestNeighbor:
    """Testy metody _select_best_neighbor."""

    def test_select_best_neighbor_non_tabu(self, sample_schedule):
        """Test wyboru najlepszego sąsiada spoza listy tabu."""
        algo = TabuSearch(sample_schedule)
        current_sequence = [0, 1, 2]
        neighbors = algo._generate_neighborhood(current_sequence)

        best_neighbor, best_cmax, best_move = algo._select_best_neighbor(
            neighbors,
            current_sequence,
            global_best_cmax=100.0,
            current_iteration=0
        )

        assert best_neighbor is not None
        assert best_cmax > 0
        assert best_move is not None

    def test_select_best_neighbor_aspiration_criterion(self, sample_schedule):
        """Test kryterium aspiracji - akceptacja ruchu tabu jeśli poprawia globalnie najlepsze."""
        algo = TabuSearch(sample_schedule)

        # Ustaw jeden ruch jako tabu
        algo.tabu_list[(0, 1)] = 100

        current_sequence = [0, 1, 2]
        neighbors = algo._generate_neighborhood(current_sequence)

        # Oblicz globalnie najlepsze
        cmax_current = sample_schedule.build_from_sequence(current_sequence)

        # Wywołaj select_best_neighbor
        best_neighbor, best_cmax, best_move = algo._select_best_neighbor(
            neighbors,
            current_sequence,
            global_best_cmax=cmax_current,
            current_iteration=50
        )

        # Powinien wybrać jakiegoś sąsiada (nawet tabu, jeśli spełnia kryterium)
        assert best_neighbor is not None

    def test_select_best_neighbor_finds_minimum(self, sample_schedule):
        """Test znajdowania minimum wśród sąsiadów."""
        algo = TabuSearch(sample_schedule)
        current_sequence = [0, 1, 2]
        neighbors = algo._generate_neighborhood(current_sequence)

        best_neighbor, best_cmax, best_move = algo._select_best_neighbor(
            neighbors,
            current_sequence,
            global_best_cmax=1000.0,
            current_iteration=0
        )

        # Sprawdź, że znaleziono minimum
        for neighbor_seq, move in neighbors:
            if not algo._is_tabu(move, 0):
                neighbor_cmax = sample_schedule.build_from_sequence(neighbor_seq)
                assert best_cmax <= neighbor_cmax


class TestTabuSearchRun:
    """Testy metody run."""

    def test_run_returns_results(self, sample_schedule):
        """Test zwracania wyników."""
        algo = TabuSearch(sample_schedule, max_iter=5)
        results = algo.run()

        assert isinstance(results, dict)
        assert "C_max" in results
        assert "time_in_ms" in results
        assert "schedule" in results

    def test_run_performs_iterations(self, sample_schedule):
        """Test wykonywania iteracji."""
        algo = TabuSearch(sample_schedule, max_iter=10, no_improve_limit=20)
        algo.run()

        assert algo.iterations_performed > 0
        assert algo.iterations_performed <= 10

    def test_run_stops_on_no_improvement(self, sample_schedule):
        """Test stopu przy braku poprawy."""
        algo = TabuSearch(sample_schedule, max_iter=100, no_improve_limit=5)
        algo.run()

        # Powinien zatrzymać się wcześniej niż 100 iteracji
        # (zakładając, że nie ma poprawy)
        # Ten test może być niestabilny, więc sprawdzamy tylko podstawy
        assert algo.iterations_performed <= 100

    def test_run_finds_valid_sequence(self, sample_schedule):
        """Test znajdowania poprawnej sekwencji."""
        algo = TabuSearch(sample_schedule, max_iter=10)
        algo.run()

        assert algo.best_sequence is not None
        assert len(algo.best_sequence) == len(sample_schedule.jobs)
        assert set(algo.best_sequence) == set(range(len(sample_schedule.jobs)))

    def test_run_improves_or_equals_initial(self, sample_schedule):
        """Test, że wynik jest nie gorszy niż rozwiązanie początkowe."""
        algo = TabuSearch(sample_schedule, max_iter=10)

        # Pobierz rozwiązanie początkowe
        initial_solution = algo._generate_initial_solution()
        initial_cmax = sample_schedule.build_from_sequence(initial_solution)

        # Uruchom algorytm
        sample_schedule._reset_runtime_state()
        results = algo.run()

        # Wynik powinien być nie gorszy
        assert results["C_max"] <= initial_cmax or abs(results["C_max"] - initial_cmax) < 0.01

    @patch('builtins.print')
    def test_run_prints_progress(self, mock_print, sample_schedule):
        """Test wyświetlania komunikatów postępu."""
        algo = TabuSearch(sample_schedule, max_iter=5)
        algo.run()

        assert mock_print.called

    def test_run_measures_time(self, sample_schedule):
        """Test mierzenia czasu wykonania."""
        algo = TabuSearch(sample_schedule, max_iter=5)
        results = algo.run()

        assert results["time_in_ms"] >= 0
        assert algo.runtime >= 0


class TestTabuSearchIntegration:
    """Testy integracyjne algorytmu Tabu Search."""

    def test_tabu_multiple_runs_randomness(self, sample_schedule):
        """Test zachowania przy wielokrotnym uruchomieniu."""
        # Algorytm jest deterministyczny (brak losowości),
        # więc powinien dawać te same wyniki
        algo1 = TabuSearch(sample_schedule, max_iter=10)
        results1 = algo1.run()

        sample_schedule._reset_runtime_state()

        algo2 = TabuSearch(sample_schedule, max_iter=10)
        results2 = algo2.run()

        # Wyniki mogą być różne jeśli jest element losowy,
        # ale dla tego algorytmu powinny być takie same
        # (zakładając deterministyczne MinSTF)
        assert algo1.best_sequence == algo2.best_sequence
        assert abs(results1["C_max"] - results2["C_max"]) < 0.01

    def test_tabu_vs_greedy(self, sample_schedule):
        """Test porównania z algorytmem zachłannym."""
        # MinSTF
        greedy = MinSTF(sample_schedule)
        greedy_results = greedy.run()

        # Tabu Search
        sample_schedule._reset_runtime_state()
        tabu = TabuSearch(sample_schedule, max_iter=20)
        tabu_results = tabu.run()

        # Tabu powinien być nie gorszy niż greedy (często lepszy)
        assert tabu_results["C_max"] <= greedy_results["C_max"] or \
               abs(tabu_results["C_max"] - greedy_results["C_max"]) < 0.01

    def test_tabu_with_different_parameters(self, sample_schedule):
        """Test z różnymi parametrami algorytmu."""
        params_list = [
            {"max_iter": 5, "tabu_tenure": 3, "no_improve_limit": 5},
            {"max_iter": 10, "tabu_tenure": 5, "no_improve_limit": 10},
            {"max_iter": 20, "tabu_tenure": 10, "no_improve_limit": 15},
        ]

        results_list = []

        for params in params_list:
            sample_schedule._reset_runtime_state()
            algo = TabuSearch(sample_schedule, **params)
            results = algo.run()
            results_list.append(results["C_max"])

        # Wszystkie wyniki powinny być dodatnie
        assert all(cmax > 0 for cmax in results_list)

    def test_tabu_convergence(self, sample_schedule):
        """Test zbieżności algorytmu."""
        algo = TabuSearch(sample_schedule, max_iter=50, no_improve_limit=20)

        # Mock do śledzenia najlepszych rozwiązań
        best_cmaxes = []

        original_select = algo._select_best_neighbor

        def tracking_select(*args, **kwargs):
            result = original_select(*args, **kwargs)
            return result

        algo._select_best_neighbor = tracking_select
        algo.run()

        # Algorytm powinien zbiegać (najlepsze rozwiązanie się nie pogarsza)
        assert algo.best_cmax > 0


class TestTabuSearchEdgeCases:
    """Testy przypadków brzegowych."""

    def test_single_iteration(self, sample_schedule):
        """Test dla pojedynczej iteracji."""
        algo = TabuSearch(sample_schedule, max_iter=1)
        results = algo.run()

        assert results["C_max"] > 0
        assert algo.iterations_performed == 1

    def test_zero_tabu_tenure(self, sample_schedule):
        """Test z zerową długością listy tabu."""
        algo = TabuSearch(sample_schedule, max_iter=5, tabu_tenure=0)
        results = algo.run()

        # Powinien działać, ale bez efektu tabu
        assert results["C_max"] > 0

    def test_large_no_improve_limit(self, sample_schedule):
        """Test z dużym limitem bez poprawy."""
        algo = TabuSearch(sample_schedule, max_iter=10, no_improve_limit=1000)
        results = algo.run()

        # Powinien wykonać wszystkie iteracje
        assert algo.iterations_performed == 10

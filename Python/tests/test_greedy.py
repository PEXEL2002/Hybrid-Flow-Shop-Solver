"""Testy jednostkowe dla algorytmu MinSTF (Greedy)."""

import pytest
from unittest.mock import Mock, patch
from algorithms.greedy import MinSTF
from core.schedule import Schedule


class TestMinSTFInitialization:
    """Testy inicjalizacji algorytmu MinSTF."""

    def test_minstf_creation(self, sample_schedule):
        """Test tworzenia obiektu MinSTF."""
        algo = MinSTF(sample_schedule)

        assert algo.name == "MinSTF"
        assert algo.schedule is sample_schedule
        assert algo.best_sequence is None
        assert algo.best_cmax is None

    def test_minstf_inherits_from_base(self, sample_schedule):
        """Test dziedziczenia z BaseAlgorithm."""
        algo = MinSTF(sample_schedule)

        # Powinien mieć metody z klasy bazowej
        assert hasattr(algo, "run")
        assert hasattr(algo, "get_results")


class TestMinSTFCalculateSetupTime:
    """Testy metody _calculate_setup_time."""

    def test_calculate_self_setup_time(self, sample_schedule):
        """Test obliczania czasu self-setup."""
        algo = MinSTF(sample_schedule)

        # Self-setup dla zadania 0 (prev_job=None)
        setup_time = algo._calculate_setup_time(job_id=0, prev_job_id=None)

        assert setup_time >= 0
        assert isinstance(setup_time, float)

    def test_calculate_setup_time_between_jobs(self, sample_schedule):
        """Test obliczania czasu przezbrojenia między zadaniami."""
        algo = MinSTF(sample_schedule)

        # Przezbrojenie z zadania 0 do zadania 1
        setup_time = algo._calculate_setup_time(job_id=1, prev_job_id=0)

        assert setup_time >= 0
        assert isinstance(setup_time, float)

    def test_calculate_setup_time_is_average(self, sample_schedule):
        """Test uśredniania czasów przezbrojenia."""
        algo = MinSTF(sample_schedule)

        # Powinien być średnią dla wszystkich etapów i maszyn
        setup_time = algo._calculate_setup_time(job_id=0, prev_job_id=None)

        # Dla sample_schedule_data: self-setup [0][0] = [[1.0, 1.0], [1.0, 1.0]]
        # Średnia = (1.0 + 1.0 + 1.0 + 1.0) / 4 = 1.0
        assert setup_time == 1.0

    def test_calculate_setup_time_different_jobs(self, sample_schedule):
        """Test różnych czasów dla różnych par zadań."""
        algo = MinSTF(sample_schedule)

        time_01 = algo._calculate_setup_time(job_id=1, prev_job_id=0)
        time_02 = algo._calculate_setup_time(job_id=2, prev_job_id=0)

        # Czasy mogą być różne (ale nie muszą)
        assert time_01 >= 0
        assert time_02 >= 0


class TestMinSTFRun:
    """Testy metody run."""

    def test_run_returns_results(self, sample_schedule):
        """Test zwracania wyników."""
        algo = MinSTF(sample_schedule)
        results = algo.run()

        assert isinstance(results, dict)
        assert "C_max" in results
        assert "time_in_ms" in results
        assert "schedule" in results

    def test_run_finds_sequence(self, sample_schedule):
        """Test znajdowania sekwencji."""
        algo = MinSTF(sample_schedule)
        algo.run()

        assert algo.best_sequence is not None
        assert len(algo.best_sequence) == len(sample_schedule.jobs)

    def test_run_sequence_contains_all_jobs(self, sample_schedule):
        """Test, że sekwencja zawiera wszystkie zadania."""
        algo = MinSTF(sample_schedule)
        algo.run()

        # Sprawdź, że każde zadanie występuje dokładnie raz
        assert set(algo.best_sequence) == set(range(len(sample_schedule.jobs)))

    def test_run_computes_cmax(self, sample_schedule):
        """Test obliczania Cmax."""
        algo = MinSTF(sample_schedule)
        results = algo.run()

        assert results["C_max"] > 0
        assert algo.best_cmax == results["C_max"]

    def test_run_measures_time(self, sample_schedule):
        """Test mierzenia czasu wykonania."""
        algo = MinSTF(sample_schedule)
        results = algo.run()

        assert results["time_in_ms"] >= 0
        assert algo.runtime >= 0

    def test_run_creates_schedule(self, sample_schedule):
        """Test tworzenia harmonogramu."""
        algo = MinSTF(sample_schedule)
        results = algo.run()

        assert isinstance(results["schedule"], list)
        assert len(results["schedule"]) > 0

    @patch('builtins.print')
    def test_run_prints_progress(self, mock_print, sample_schedule):
        """Test wyświetlania komunikatów."""
        algo = MinSTF(sample_schedule)
        algo.run()

        # Sprawdź, że były wywołania print
        assert mock_print.called

    def test_run_deterministic(self, sample_schedule):
        """Test deterministyczności algorytmu."""
        algo1 = MinSTF(sample_schedule)
        results1 = algo1.run()

        # Reset schedule
        sample_schedule._reset_runtime_state()

        algo2 = MinSTF(sample_schedule)
        results2 = algo2.run()

        # Te same dane wejściowe -> te same wyniki
        assert algo1.best_sequence == algo2.best_sequence
        assert abs(results1["C_max"] - results2["C_max"]) < 0.01


class TestMinSTFGreedyLogic:
    """Testy logiki zachłannej algorytmu."""

    def test_first_job_has_min_self_setup(self, sample_schedule):
        """Test wyboru pierwszego zadania (najmniejszy self-setup)."""
        algo = MinSTF(sample_schedule)
        algo.run()

        first_job = algo.best_sequence[0]

        # Sprawdź, że pierwsze zadanie ma minimalny self-setup
        self_setup_times = [
            algo._calculate_setup_time(job_id=j, prev_job_id=None)
            for j in range(len(sample_schedule.jobs))
        ]

        assert algo._calculate_setup_time(first_job, None) == min(self_setup_times)

    def test_greedy_selection(self, sample_schedule):
        """Test zachłannego wyboru kolejnych zadań."""
        algo = MinSTF(sample_schedule)
        algo.run()

        # Dla każdej pary kolejnych zadań w sekwencji,
        # wybrane zadanie powinno minimalizować setup
        sequence = algo.best_sequence

        for i in range(len(sequence) - 1):
            prev_job = sequence[i]
            chosen_job = sequence[i + 1]
            remaining_jobs = sequence[i + 1:]

            # Oblicz setup dla wybranego zadania
            chosen_setup = algo._calculate_setup_time(chosen_job, prev_job)

            # Sprawdź, że nie było lepszego wyboru wśród pozostałych
            for other_job in remaining_jobs:
                other_setup = algo._calculate_setup_time(other_job, prev_job)
                # chosen_job powinien mieć setup <= pozostałych
                assert chosen_setup <= other_setup or abs(chosen_setup - other_setup) < 0.01


class TestMinSTFGetResults:
    """Testy metody get_results."""

    def test_get_results_format(self, sample_schedule):
        """Test formatu wyników."""
        algo = MinSTF(sample_schedule)
        algo.run()
        results = algo.get_results()

        assert "C_max" in results
        assert "time_in_ms" in results
        assert "schedule" in results

    def test_get_results_values(self, sample_schedule):
        """Test poprawności wartości w wynikach."""
        algo = MinSTF(sample_schedule)
        algo.run()
        results = algo.get_results()

        assert results["C_max"] == algo.best_cmax
        assert results["time_in_ms"] == round(algo.runtime * 1000, 3)
        assert results["schedule"] == algo.result_schedule


class TestMinSTFEdgeCases:
    """Testy przypadków brzegowych."""

    def test_single_job(self, tmp_path):
        """Test dla pojedynczego zadania."""
        data = {
            "num_stages": 1,
            "machines_per_stage": [1],
            "learning_coefficient": 0.0,
            "learning_stages": "0",
            "processing_times": [[[5.0]]],
            "setup_times": [[[[1.0]]]],
        }

        import json
        file_path = tmp_path / "single_job.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        schedule = Schedule()
        schedule.load_from_json(str(file_path))

        algo = MinSTF(schedule)
        results = algo.run()

        assert results["C_max"] > 0
        assert algo.best_sequence == [0]

    def test_two_jobs(self, tmp_path):
        """Test dla dwóch zadań."""
        data = {
            "num_stages": 1,
            "machines_per_stage": [1],
            "learning_coefficient": 0.0,
            "learning_stages": "0",
            "processing_times": [[[5.0]], [[6.0]]],
            "setup_times": [
                [[[1.0]], [[2.0]]],
                [[[3.0]], [[1.5]]],
            ],
        }

        import json
        file_path = tmp_path / "two_jobs.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        schedule = Schedule()
        schedule.load_from_json(str(file_path))

        algo = MinSTF(schedule)
        results = algo.run()

        assert len(algo.best_sequence) == 2
        assert set(algo.best_sequence) == {0, 1}


class TestMinSTFIntegration:
    """Testy integracyjne algorytmu MinSTF."""

    def test_minstf_with_different_instances(self, tmp_path):
        """Test algorytmu na różnych instancjach."""
        import json

        instances = [
            # Mała instancja
            {
                "num_stages": 2,
                "machines_per_stage": [1, 1],
                "learning_coefficient": 0.0,
                "learning_stages": "00",
                "processing_times": [[[5.0], [4.0]], [[6.0], [5.0]]],
                "setup_times": [
                    [[[1.0], [2.0]], [[2.0], [1.5]]],
                    [[[2.5], [1.0]], [[1.5], [2.0]]],
                ],
            },
            # Większa instancja
            {
                "num_stages": 2,
                "machines_per_stage": [2, 2],
                "learning_coefficient": 0.2,
                "learning_stages": "01",
                "processing_times": [
                    [[5.0, 6.0], [4.0, 5.0]],
                    [[4.0, 5.0], [6.0, 7.0]],
                    [[6.0, 7.0], [5.0, 6.0]],
                    [[7.0, 8.0], [6.0, 7.0]],
                ],
                "setup_times": [
                    [
                        [[1.0, 1.0], [1.0, 1.0]],
                        [[2.0, 2.5], [2.0, 2.5]],
                        [[3.0, 3.5], [3.0, 3.5]],
                        [[2.5, 3.0], [2.5, 3.0]],
                    ],
                    [
                        [[2.5, 2.0], [2.5, 2.0]],
                        [[1.5, 1.5], [1.5, 1.5]],
                        [[2.0, 2.5], [2.0, 2.5]],
                        [[3.0, 3.5], [3.0, 3.5]],
                    ],
                    [
                        [[3.5, 3.0], [3.5, 3.0]],
                        [[2.5, 2.0], [2.5, 2.0]],
                        [[2.0, 2.0], [2.0, 2.0]],
                        [[2.5, 2.5], [2.5, 2.5]],
                    ],
                    [
                        [[3.0, 3.5], [3.0, 3.5]],
                        [[3.5, 3.0], [3.5, 3.0]],
                        [[2.5, 2.5], [2.5, 2.5]],
                        [[2.0, 2.0], [2.0, 2.0]],
                    ],
                ],
            },
        ]

        for i, instance_data in enumerate(instances):
            file_path = tmp_path / f"instance_{i}.json"
            with open(file_path, "w") as f:
                json.dump(instance_data, f)

            schedule = Schedule()
            schedule.load_from_json(str(file_path))

            algo = MinSTF(schedule)
            results = algo.run()

            # Podstawowe sprawdzenia
            assert results["C_max"] > 0
            assert len(algo.best_sequence) == len(instance_data["processing_times"])
            assert results["time_in_ms"] >= 0

    def test_minstf_vs_natural_order(self, sample_schedule):
        """Test porównania z kolejnością naturalną."""
        # MinSTF
        algo = MinSTF(sample_schedule)
        results_minstf = algo.run()
        cmax_minstf = results_minstf["C_max"]

        # Kolejność naturalna
        sample_schedule._reset_runtime_state()
        cmax_natural = sample_schedule.build_from_sequence([0, 1, 2])

        # MinSTF powinien być nie gorszy niż kolejność naturalna
        assert cmax_minstf <= cmax_natural or abs(cmax_minstf - cmax_natural) < 0.01

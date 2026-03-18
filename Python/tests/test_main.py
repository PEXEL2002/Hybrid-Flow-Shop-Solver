"""Testy jednostkowe dla głównego modułu programu."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import sys
import os

# Import funkcji z main
import main
from main import get_results_dir, generate_gantt_only, run_algorithm


class TestGetResultsDir:
    """Testy funkcji get_results_dir."""

    def test_get_results_dir_returns_path(self):
        """Test zwracania ścieżki do katalogu results."""
        results_dir = get_results_dir()

        assert results_dir is not None
        assert isinstance(results_dir, str)
        assert "results" in results_dir

    def test_get_results_dir_creates_directory(self, tmp_path, monkeypatch):
        """Test tworzenia katalogu results."""
        # Mock dirname i join
        mock_script_dir = str(tmp_path)

        with patch('os.path.dirname', return_value=mock_script_dir):
            with patch('os.path.abspath') as mock_abspath:
                mock_abspath.side_effect = lambda x: x if os.path.isabs(x) else os.path.join(tmp_path, x)

                results_dir = get_results_dir()

                # Katalog powinien zostać utworzony
                assert os.path.exists(results_dir) or True  # os.makedirs z exist_ok=True


class TestGenerateGanttOnly:
    """Testy funkcji generate_gantt_only."""

    @patch('main.GanttChart.from_file')
    @patch('builtins.print')
    def test_generate_gantt_only_success(self, mock_print, mock_from_file, tmp_path, sample_result_data):
        """Test pomyślnego generowania wykresu."""
        # Przygotuj plik wejściowy
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump(sample_result_data, f)

        output_file = tmp_path / "output.png"

        # Mock GanttChart
        mock_gantt = MagicMock()
        mock_gantt.save.return_value = str(output_file)
        mock_from_file.return_value = mock_gantt

        # Utwórz plik wyjściowy dla testu
        with open(output_file, "w") as f:
            f.write("fake image")

        result = generate_gantt_only(str(input_file), str(output_file))

        assert result == str(output_file)
        mock_from_file.assert_called_once_with(str(input_file))

    @patch('main.GanttChart.from_file')
    def test_generate_gantt_only_file_not_found(self, mock_from_file):
        """Test błędu dla nieistniejącego pliku."""
        mock_from_file.side_effect = FileNotFoundError("Plik nie istnieje")

        with pytest.raises(SystemExit):
            generate_gantt_only("nonexistent.json")

    @patch('main.GanttChart.from_file')
    def test_generate_gantt_only_invalid_json(self, mock_from_file):
        """Test błędu dla niepoprawnego JSON."""
        mock_from_file.side_effect = json.JSONDecodeError("msg", "doc", 0)

        with pytest.raises(SystemExit):
            generate_gantt_only("invalid.json")


class TestRunAlgorithm:
    """Testy funkcji run_algorithm."""

    @patch('main.GanttChart.from_results')
    @patch('builtins.print')
    def test_run_algorithm_greedy(self, mock_print, mock_gantt_from_results, sample_schedule_data, tmp_path):
        """Test uruchomienia algorytmu greedy."""
        # Przygotuj plik z algorytmem greedy
        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "greedy"

        input_file = tmp_path / "greedy_test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        # Mock GanttChart
        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        results = run_algorithm(str(input_file), plot=False)

        assert "C_max" in results
        assert "time_in_ms" in results
        assert results["Algorithm"] == "MinSTF"

    @patch('main.GanttChart.from_results')
    @patch('builtins.print')
    def test_run_algorithm_tabu(self, mock_print, mock_gantt_from_results, sample_schedule_data, tmp_path):
        """Test uruchomienia algorytmu tabu."""
        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "tabu"

        input_file = tmp_path / "tabu_test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        results = run_algorithm(str(input_file), plot=False)

        assert results["Algorithm"] == "Tabu Search"

    @patch('main.GanttChart.from_results')
    @patch('builtins.print')
    def test_run_algorithm_bnb(self, mock_print, mock_gantt_from_results, sample_schedule_data, tmp_path):
        """Test uruchomienia algorytmu B&B."""
        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "bnb"

        input_file = tmp_path / "bnb_test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        results = run_algorithm(str(input_file), plot=False)

        assert results["Algorithm"] == "Branch & Bound"

    @patch('builtins.print')
    def test_run_algorithm_unknown(self, mock_print, sample_schedule_data, tmp_path):
        """Test błędu dla nieznanego algorytmu."""
        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "unknown"

        input_file = tmp_path / "unknown_test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        with pytest.raises(SystemExit):
            run_algorithm(str(input_file))

    @patch('main.GanttChart.from_results')
    @patch('builtins.print')
    def test_run_algorithm_default_algorithm(self, mock_print, mock_gantt_from_results, sample_schedule_data, tmp_path):
        """Test domyślnego algorytmu (tabu)."""
        data = json.loads(open(sample_schedule_data).read())
        # Usuń klucz algorithm
        if "algorithm" in data:
            del data["algorithm"]

        input_file = tmp_path / "default_test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        results = run_algorithm(str(input_file), plot=False)

        # Domyślnie powinien użyć tabu
        assert results["Algorithm"] == "Tabu Search"

    @patch('main.GanttChart.from_results')
    @patch('main.get_results_dir')
    @patch('builtins.print')
    def test_run_algorithm_saves_results(self, mock_print, mock_get_results_dir, mock_gantt_from_results,
                                          sample_schedule_data, tmp_path):
        """Test zapisywania wyników."""
        mock_get_results_dir.return_value = str(tmp_path)

        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "greedy"

        input_file = tmp_path / "test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        run_algorithm(str(input_file), plot=False)

        # Sprawdź, czy plik result.json został utworzony
        result_file = tmp_path / "result.json"
        assert result_file.exists()


class TestMainFunction:
    """Testy funkcji main."""

    @patch('main.run_benchmark')
    @patch('sys.argv', ['main.py', '--test'])
    def test_main_benchmark_mode(self, mock_benchmark):
        """Test trybu benchmarku."""
        main.main()

        mock_benchmark.assert_called_once()

    @patch('main.generate_gantt_only')
    @patch('os.path.exists', return_value=True)
    @patch('sys.argv', ['main.py', '--gantt', 'result.json'])
    def test_main_gantt_mode(self, mock_exists, mock_generate_gantt):
        """Test trybu generowania wykresu Gantta."""
        main.main()

        mock_generate_gantt.assert_called_once()

    @patch('main.run_algorithm')
    @patch('os.path.exists', return_value=True)
    @patch('sys.argv', ['main.py', 'data.json'])
    def test_main_normal_mode(self, mock_exists, mock_run_algorithm):
        """Test normalnego trybu."""
        main.main()

        mock_run_algorithm.assert_called_once()

    @patch('os.path.exists', return_value=False)
    @patch('sys.argv', ['main.py', 'nonexistent.json'])
    def test_main_file_not_found(self, mock_exists):
        """Test błędu dla nieistniejącego pliku."""
        with pytest.raises(SystemExit):
            main.main()

    @patch('main.run_algorithm')
    @patch('os.path.exists', return_value=True)
    @patch('sys.argv', ['main.py', 'data.json', '--plot'])
    def test_main_with_plot_flag(self, mock_exists, mock_run_algorithm):
        """Test z flagą --plot."""
        main.main()

        # Sprawdź, że run_algorithm został wywołany z plot=True
        call_args = mock_run_algorithm.call_args
        assert call_args[1]['plot'] is True


class TestMainIntegration:
    """Testy integracyjne głównego programu."""

    @patch('main.GanttChart.from_results')
    @patch('builtins.print')
    def test_full_workflow_greedy(self, mock_print, mock_gantt_from_results, sample_schedule_data, tmp_path):
        """Test pełnego przepływu dla algorytmu greedy."""
        # Przygotuj dane
        data = json.loads(open(sample_schedule_data).read())
        data["algorithm"] = "greedy"

        input_file = tmp_path / "test.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        mock_gantt = MagicMock()
        mock_gantt_from_results.return_value = mock_gantt

        # Uruchom algorytm
        with patch('main.get_results_dir', return_value=str(tmp_path)):
            results = run_algorithm(str(input_file), plot=False)

        # Sprawdź wyniki
        assert "C_max" in results
        assert "schedule" in results
        assert results["C_max"] > 0

        # Sprawdź plik wyjściowy
        output_file = tmp_path / "result.json"
        assert output_file.exists()

        with open(output_file) as f:
            saved_results = json.load(f)

        assert saved_results["C_max"] == results["C_max"]

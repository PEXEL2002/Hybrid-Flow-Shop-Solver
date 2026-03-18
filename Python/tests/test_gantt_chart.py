"""Testy jednostkowe dla modułu generowania wykresów Gantta."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os
from utils.gantt_chart import GanttChart, generate_gantt_from_file, generate_gantt_from_schedule


class TestGanttChartInitialization:
    """Testy inicjalizacji obiektu GanttChart."""

    def test_gantt_creation_empty(self):
        """Test tworzenia pustego wykresu."""
        gantt = GanttChart()

        assert gantt.schedule == []
        assert gantt.cmax == 0
        assert gantt.algorithm == ''
        assert gantt.num_stages == 0

    def test_gantt_creation_with_dict(self, sample_result_data):
        """Test tworzenia z danych w formacie dict."""
        gantt = GanttChart(sample_result_data)

        assert gantt.schedule == sample_result_data["schedule"]
        assert gantt.cmax == sample_result_data["C_max"]
        assert gantt.algorithm == sample_result_data["Algorithm"]

    def test_gantt_creation_with_list(self):
        """Test tworzenia z listy operacji."""
        schedule_list = [
            {"type": "operation", "job": 0, "stage": 0, "machine": 0, "start": 0.0, "end": 5.0}
        ]

        gantt = GanttChart(schedule_list)

        assert gantt.schedule == schedule_list
        assert gantt.cmax == 5.0


class TestGanttChartFromFile:
    """Testy metody from_file."""

    def test_from_file_loads_data(self, temp_json_file, sample_result_data):
        """Test wczytywania danych z pliku."""
        file_path = temp_json_file(sample_result_data, "gantt_test.json")

        gantt = GanttChart.from_file(file_path)

        assert gantt.schedule == sample_result_data["schedule"]
        assert gantt.cmax == sample_result_data["C_max"]
        assert gantt._source_file is not None

    def test_from_file_nonexistent_raises_error(self):
        """Test błędu dla nieistniejącego pliku."""
        with pytest.raises(FileNotFoundError):
            GanttChart.from_file("nonexistent_file.json")

    def test_from_file_missing_schedule_key(self, temp_json_file):
        """Test błędu dla pliku bez klucza 'schedule'."""
        data = {"C_max": 10.0}  # Brak 'schedule'
        file_path = temp_json_file(data)

        with pytest.raises(ValueError, match="nie zawiera klucza 'schedule'"):
            GanttChart.from_file(file_path)

    def test_from_file_invalid_json(self, tmp_path):
        """Test błędu dla niepoprawnego JSON."""
        file_path = tmp_path / "invalid.json"
        with open(file_path, "w") as f:
            f.write("{invalid json")

        with pytest.raises(json.JSONDecodeError):
            GanttChart.from_file(str(file_path))


class TestGanttChartFromResults:
    """Testy metody from_results."""

    def test_from_results_creates_gantt(self, sample_result_data):
        """Test tworzenia z wyników algorytmu."""
        gantt = GanttChart.from_results(sample_result_data)

        assert gantt.schedule == sample_result_data["schedule"]
        assert gantt.cmax == sample_result_data["C_max"]
        assert gantt.algorithm == sample_result_data["Algorithm"]


class TestGanttChartFromScheduleObject:
    """Testy metody from_schedule_object."""

    def test_from_schedule_object(self, sample_schedule):
        """Test tworzenia z obiektu Schedule."""
        sample_schedule.build_from_sequence([0, 1, 2])

        gantt = GanttChart.from_schedule_object(sample_schedule, algorithm="Test")

        assert len(gantt.schedule) > 0
        assert gantt.cmax == sample_schedule.Cmax
        assert gantt.algorithm == "Test"


class TestGanttChartDetectStructure:
    """Testy metody _detect_structure."""

    def test_detect_structure_finds_stages(self, sample_result_data):
        """Test wykrywania liczby etapów."""
        gantt = GanttChart(sample_result_data)

        assert gantt.num_stages > 0

    def test_detect_structure_finds_machines(self):
        """Test wykrywania maszyn na etapach."""
        data = {
            "schedule": [
                {"type": "operation", "job": 0, "stage": 0, "machine": 0, "start": 0, "end": 5},
                {"type": "operation", "job": 1, "stage": 0, "machine": 1, "start": 0, "end": 5},
                {"type": "operation", "job": 0, "stage": 1, "machine": 0, "start": 5, "end": 10},
            ]
        }

        gantt = GanttChart(data)

        assert gantt.num_stages == 2
        assert 0 in gantt.machines_per_stage
        assert 1 in gantt.machines_per_stage
        assert 0 in gantt.machines_per_stage[0]
        assert 1 in gantt.machines_per_stage[0]


class TestGanttChartGetJobColor:
    """Testy metody _get_job_color."""

    def test_get_job_color_returns_color(self):
        """Test zwracania koloru dla zadania."""
        gantt = GanttChart()

        color = gantt._get_job_color(0)

        assert isinstance(color, str)
        assert color.startswith('#')

    def test_get_job_color_cycles(self):
        """Test cykliczności kolorów."""
        gantt = GanttChart()

        num_colors = len(gantt.JOB_COLORS)
        color_0 = gantt._get_job_color(0)
        color_n = gantt._get_job_color(num_colors)

        # Powinny być takie same (cykl)
        assert color_0 == color_n


class TestGanttChartCreateMachineLabels:
    """Testy metody _create_machine_labels."""

    def test_create_machine_labels_format(self):
        """Test formatu etykiet maszyn."""
        data = {
            "schedule": [
                {"type": "operation", "job": 0, "stage": 0, "machine": 0, "start": 0, "end": 5},
                {"type": "operation", "job": 0, "stage": 1, "machine": 1, "start": 5, "end": 10},
            ]
        }

        gantt = GanttChart(data)
        labels, positions = gantt._create_machine_labels()

        assert len(labels) == len(positions)
        assert all(isinstance(label, str) for label in labels)
        assert "Stage" in labels[0]


class TestGanttChartGetInfo:
    """Testy metody get_info."""

    def test_get_info_returns_dict(self, sample_result_data):
        """Test zwracania informacji jako dict."""
        gantt = GanttChart(sample_result_data)

        info = gantt.get_info()

        assert isinstance(info, dict)
        assert "algorithm" in info
        assert "cmax" in info
        assert "num_operations" in info


class TestGanttChartNumOperations:
    """Testy właściwości num_operations."""

    def test_num_operations_count(self, sample_result_data):
        """Test liczenia operacji."""
        gantt = GanttChart(sample_result_data)

        assert gantt.num_operations == len(sample_result_data["schedule"])


class TestGanttChartPrintInfo:
    """Testy metody print_info."""

    @patch('builtins.print')
    def test_print_info_prints(self, mock_print, sample_result_data):
        """Test wyświetlania informacji."""
        gantt = GanttChart(sample_result_data)

        gantt.print_info()

        assert mock_print.called


class TestGanttChartGenerate:
    """Testy metody generate."""

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_generate_creates_plot(self, mock_show, mock_savefig, mock_subplots, sample_result_data):
        """Test generowania wykresu."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        gantt = GanttChart(sample_result_data)
        fig = gantt.generate(show=False)

        assert mock_subplots.called

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    def test_generate_saves_file(self, mock_savefig, mock_subplots, sample_result_data, tmp_path):
        """Test zapisywania pliku."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        output_file = tmp_path / "test_gantt.png"
        gantt = GanttChart(sample_result_data)

        gantt.generate(output_file=str(output_file), show=False)

        assert mock_savefig.called


class TestGanttChartSave:
    """Testy metody save."""

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    def test_save_returns_path(self, mock_savefig, mock_subplots, sample_result_data, tmp_path):
        """Test zwracania ścieżki do pliku."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        output_file = tmp_path / "test_gantt.png"
        gantt = GanttChart(sample_result_data)

        saved_path = gantt.save(str(output_file), show=False, update_source=False)

        assert saved_path is not None
        assert isinstance(saved_path, str)

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    def test_save_creates_directory(self, mock_savefig, mock_subplots, sample_result_data, tmp_path):
        """Test tworzenia katalogu docelowego."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        output_file = tmp_path / "subdir" / "test_gantt.png"
        gantt = GanttChart(sample_result_data)

        gantt.save(str(output_file), show=False, update_source=False)

        assert output_file.parent.exists()


class TestGanttChartHelperFunctions:
    """Testy funkcji pomocniczych."""

    @patch('utils.gantt_chart.GanttChart.from_file')
    @patch('utils.gantt_chart.GanttChart.generate')
    def test_generate_gantt_from_file(self, mock_generate, mock_from_file):
        """Test funkcji generate_gantt_from_file."""
        mock_gantt = MagicMock()
        mock_from_file.return_value = mock_gantt

        generate_gantt_from_file("test.json", "output.png", show=False)

        mock_from_file.assert_called_once_with("test.json")
        mock_gantt.generate.assert_called_once()

    @patch('utils.gantt_chart.GanttChart.from_schedule_object')
    @patch('utils.gantt_chart.GanttChart.generate')
    def test_generate_gantt_from_schedule(self, mock_generate, mock_from_obj, sample_schedule):
        """Test funkcji generate_gantt_from_schedule."""
        mock_gantt = MagicMock()
        mock_from_obj.return_value = mock_gantt

        generate_gantt_from_schedule(sample_schedule, "output.png", show=False)

        mock_from_obj.assert_called_once()
        mock_gantt.generate.assert_called_once()


class TestGanttChartIntegration:
    """Testy integracyjne generowania wykresów."""

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.savefig')
    def test_full_workflow(self, mock_savefig, mock_subplots, sample_schedule, tmp_path):
        """Test pełnego przepływu generowania wykresu."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 1. Zbuduj harmonogram
        sample_schedule.build_from_sequence([0, 1, 2])

        # 2. Utwórz wykres Gantta
        gantt = GanttChart.from_schedule_object(sample_schedule, "Test Algorithm")

        # 3. Zapisz wykres
        output_file = tmp_path / "gantt.png"
        saved_path = gantt.save(str(output_file), show=False, update_source=False)

        assert saved_path is not None
        assert mock_savefig.called

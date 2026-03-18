"""Testy jednostkowe dla klasy Schedule."""

import pytest
import json
import tempfile
from core.schedule import Schedule
from core.job import Job
from core.machine import Machine


class TestScheduleInitialization:
    """Testy inicjalizacji obiektu Schedule."""

    def test_schedule_creation(self):
        """Test tworzenia pustego harmonogramu."""
        schedule = Schedule()

        assert schedule.jobs == []
        assert schedule.machines == []
        assert schedule.schedule == []
        assert schedule.num_stages == 0
        assert schedule.machines_per_stage == []
        assert schedule.Cmax == 0.0
        assert schedule.learning_stages == ""
        assert schedule.learning_coeff == 0.0


class TestScheduleLoadFromJson:
    """Testy wczytywania danych z pliku JSON."""

    def test_load_from_json_basic(self, sample_schedule_data):
        """Test wczytywania podstawowych danych."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        assert schedule.num_stages == 2
        assert schedule.machines_per_stage == [2, 2]
        assert schedule.learning_coeff == 0.3
        assert schedule.learning_stages == "01"

    def test_load_from_json_creates_jobs(self, sample_schedule_data):
        """Test tworzenia obiektów Job."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        assert len(schedule.jobs) == 3
        assert all(isinstance(job, Job) for job in schedule.jobs)
        assert schedule.jobs[0].id == 0
        assert schedule.jobs[1].id == 1
        assert schedule.jobs[2].id == 2

    def test_load_from_json_creates_machines(self, sample_schedule_data):
        """Test tworzenia obiektów Machine."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        # 2 etapy, po 2 maszyny = 4 maszyny łącznie
        assert len(schedule.machines) == 2
        assert len(schedule.machines[0]) == 2
        assert len(schedule.machines[1]) == 2

        # Sprawdź typy
        for stage in schedule.machines:
            for machine in stage:
                assert isinstance(machine, Machine)

    def test_load_from_json_learning_stages(self, sample_schedule_data):
        """Test konfiguracji etapów z uczeniem."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        # learning_stages = "01" -> etap 0: bez uczenia, etap 1: z uczeniem
        assert schedule.machines[0][0].is_learning is False
        assert schedule.machines[1][0].is_learning is True

    def test_load_from_json_default_learning_coeff(self, tmp_path):
        """Test domyślnej wartości learning_coefficient."""
        data = {
            "num_stages": 1,
            "machines_per_stage": [1],
            "processing_times": [[[5.0]]],
            "setup_times": [[[[1.0]]]],
        }

        file_path = tmp_path / "test.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        schedule = Schedule()
        schedule.load_from_json(str(file_path))

        assert schedule.learning_coeff == 0.0
        assert schedule.learning_stages == "0"

    def test_load_from_json_stores_raw_data(self, sample_schedule_data):
        """Test przechowywania surowych danych."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        assert schedule._raw_data is not None
        assert isinstance(schedule._raw_data, dict)


class TestScheduleAddOperation:
    """Testy metody add_operation."""

    def test_add_operation_setup(self, sample_schedule):
        """Test dodawania operacji przezbrojenia."""
        sample_schedule.add_operation(
            "setup",
            from_job=0,
            to_job=1,
            stage=0,
            machine=0,
            start=0.0,
            end=2.0
        )

        assert len(sample_schedule.schedule) == 1
        op = sample_schedule.schedule[0]
        assert op["type"] == "setup"
        assert op["from_job"] == 0
        assert op["to_job"] == 1
        assert op["stage"] == 0
        assert op["machine"] == 0
        assert op["start"] == 0.0
        assert op["end"] == 2.0

    def test_add_operation_processing(self, sample_schedule):
        """Test dodawania operacji przetwarzania."""
        sample_schedule.add_operation(
            "operation",
            job=1,
            stage=1,
            machine=1,
            start=5.0,
            end=10.0
        )

        assert len(sample_schedule.schedule) == 1
        op = sample_schedule.schedule[0]
        assert op["type"] == "operation"
        assert op["job"] == 1
        assert op["start"] == 5.0
        assert op["end"] == 10.0

    def test_add_multiple_operations(self, sample_schedule):
        """Test dodawania wielu operacji."""
        sample_schedule.add_operation("setup", stage=0, machine=0, start=0.0, end=1.0)
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=1.0, end=5.0)

        assert len(sample_schedule.schedule) == 2


class TestScheduleComputeCmax:
    """Testy metody compute_Cmax."""

    def test_compute_cmax_empty_schedule(self, sample_schedule):
        """Test dla pustego harmonogramu."""
        cmax = sample_schedule.compute_Cmax()
        assert cmax == 0.0

    def test_compute_cmax_single_operation(self, sample_schedule):
        """Test dla pojedynczej operacji."""
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=0.0, end=10.0)

        cmax = sample_schedule.compute_Cmax()
        assert cmax == 10.0
        assert sample_schedule.Cmax == 10.0

    def test_compute_cmax_multiple_operations(self, sample_schedule):
        """Test dla wielu operacji."""
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=0.0, end=5.0)
        sample_schedule.add_operation("operation", job=1, stage=0, machine=1, start=0.0, end=8.0)
        sample_schedule.add_operation("operation", job=2, stage=1, machine=0, start=5.0, end=12.0)

        cmax = sample_schedule.compute_Cmax()
        assert cmax == 12.0

    def test_compute_cmax_finds_maximum(self, sample_schedule):
        """Test znajdowania maksymalnego czasu zakończenia."""
        times = [3.5, 7.2, 15.8, 12.1, 9.4]
        for i, end_time in enumerate(times):
            sample_schedule.add_operation(
                "operation",
                job=i,
                stage=0,
                machine=0,
                start=0.0,
                end=end_time
            )

        cmax = sample_schedule.compute_Cmax()
        assert cmax == max(times)


class TestScheduleBuildFromSequence:
    """Testy metody build_from_sequence."""

    def test_build_from_sequence_natural_order(self, sample_schedule):
        """Test budowy harmonogramu dla kolejności naturalnej."""
        sequence = [0, 1, 2]
        cmax = sample_schedule.build_from_sequence(sequence)

        assert cmax > 0
        assert sample_schedule.Cmax == cmax
        assert len(sample_schedule.schedule) > 0

    def test_build_from_sequence_creates_operations(self, sample_schedule):
        """Test tworzenia operacji dla sekwencji."""
        sequence = [0, 1, 2]
        sample_schedule.build_from_sequence(sequence)

        # Dla każdego zadania i etapu powinien być setup i operation
        # 3 zadania × 2 etapy × 2 operacje = 12 operacji
        assert len(sample_schedule.schedule) == 12

        # Sprawdź typy operacji
        setup_ops = [op for op in sample_schedule.schedule if op["type"] == "setup"]
        proc_ops = [op for op in sample_schedule.schedule if op["type"] == "operation"]

        assert len(setup_ops) == 6
        assert len(proc_ops) == 6

    def test_build_from_sequence_different_order(self, sample_schedule):
        """Test budowy dla różnych kolejności."""
        sequence1 = [0, 1, 2]
        cmax1 = sample_schedule.build_from_sequence(sequence1)

        # Reset i nowa sekwencja
        schedule2 = Schedule()
        schedule2._raw_data = sample_schedule._raw_data
        schedule2._reset_runtime_state()

        sequence2 = [2, 1, 0]
        cmax2 = schedule2.build_from_sequence(sequence2)

        # Różne sekwencje mogą dawać różne Cmax
        # (nie sprawdzamy czy są różne, bo mogą być przypadkiem równe)
        assert cmax1 > 0
        assert cmax2 > 0

    def test_build_from_sequence_respects_precedence(self, sample_schedule):
        """Test przestrzegania kolejności etapów."""
        sequence = [0, 1]
        sample_schedule.build_from_sequence(sequence)

        # Dla każdego zadania: etap 1 musi zakończyć się po etapie 0
        for job_id in sequence:
            job_ops = [op for op in sample_schedule.schedule
                      if op.get("job") == job_id and op["type"] == "operation"]

            if len(job_ops) >= 2:
                stage_0_end = max(op["end"] for op in job_ops if op["stage"] == 0)
                stage_1_start = min(op["start"] for op in job_ops if op["stage"] == 1)

                # Etap 1 nie może rozpocząć się przed zakończeniem etapu 0
                assert stage_1_start >= stage_0_end

    def test_build_from_sequence_updates_job_times(self, sample_schedule):
        """Test aktualizacji czasów w obiektach Job."""
        sequence = [0, 1, 2]
        sample_schedule.build_from_sequence(sequence)

        for job in sample_schedule.jobs:
            # Każde zadanie powinno mieć przypisane maszyny
            for stage in range(sample_schedule.num_stages):
                assert job.machine_assignment[stage] >= 0

            # Czasy powinny być niezerowe
            assert job.total_time > 0


class TestScheduleResetRuntimeState:
    """Testy metody _reset_runtime_state."""

    def test_reset_clears_schedule(self, sample_schedule):
        """Test czyszczenia harmonogramu."""
        # Dodaj operacje
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=0.0, end=5.0)
        assert len(sample_schedule.schedule) > 0

        # Reset
        sample_schedule._reset_runtime_state()

        assert len(sample_schedule.schedule) == 0
        assert sample_schedule.Cmax == 0.0

    def test_reset_recreates_jobs(self, sample_schedule):
        """Test odtwarzania obiektów Job."""
        # Zmodyfikuj zadanie
        sample_schedule.jobs[0].total_time = 999.0

        # Reset
        sample_schedule._reset_runtime_state()

        # Zadanie powinno być odtworzone
        assert sample_schedule.jobs[0].total_time == 0.0

    def test_reset_recreates_machines(self, sample_schedule):
        """Test odtwarzania obiektów Machine."""
        # Zmodyfikuj maszynę
        sample_schedule.machines[0][0].processed_jobs = 100

        # Reset
        sample_schedule._reset_runtime_state()

        # Maszyna powinna być odtworzona
        assert sample_schedule.machines[0][0].processed_jobs == 0

    def test_reset_requires_raw_data(self):
        """Test wymagania surowych danych."""
        schedule = Schedule()

        with pytest.raises(RuntimeError, match="Brak surowych danych"):
            schedule._reset_runtime_state()

    def test_reset_preserves_raw_data(self, sample_schedule):
        """Test zachowania surowych danych."""
        original_data = sample_schedule._raw_data

        sample_schedule._reset_runtime_state()

        assert sample_schedule._raw_data is original_data


class TestScheduleToJson:
    """Testy metody to_json."""

    def test_to_json_returns_schedule(self, sample_schedule):
        """Test zwracania harmonogramu."""
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=0.0, end=5.0)

        json_data = sample_schedule.to_json()

        assert json_data == sample_schedule.schedule
        assert isinstance(json_data, list)


class TestScheduleSaveToFile:
    """Testy metody save_to_file."""

    def test_save_to_file_creates_file(self, sample_schedule, tmp_path):
        """Test tworzenia pliku."""
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=0.0, end=5.0)

        output_file = tmp_path / "output.json"
        sample_schedule.save_to_file(str(output_file))

        assert output_file.exists()

    def test_save_to_file_correct_format(self, sample_schedule, tmp_path):
        """Test poprawności formatu zapisu."""
        sample_schedule.add_operation("setup", stage=0, machine=0, start=0.0, end=1.0)
        sample_schedule.add_operation("operation", job=0, stage=0, machine=0, start=1.0, end=5.0)

        output_file = tmp_path / "output.json"
        sample_schedule.save_to_file(str(output_file))

        with open(output_file) as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 2


class TestScheduleCalculateTotalTime:
    """Testy metody _calculate_total_time."""

    def test_calculate_total_time(self, sample_schedule):
        """Test obliczania całkowitego czasu."""
        job = sample_schedule.jobs[0]
        total_time = sample_schedule._calculate_total_time(
            job=job,
            stage=0,
            machine_idx=0,
            machines=sample_schedule.machines
        )

        # Powinien być większy od zera
        assert total_time > 0

    def test_calculate_total_time_includes_setup(self, sample_schedule):
        """Test uwzględniania czasu przezbrojenia."""
        # Symuluj, że maszyna jest zajęta
        machine = sample_schedule.machines[0][0]
        machine.available_time = 10.0
        machine.last_job = 1

        job = sample_schedule.jobs[0]
        total_time = sample_schedule._calculate_total_time(
            job=job,
            stage=0,
            machine_idx=0,
            machines=sample_schedule.machines
        )

        # Powinien uwzględniać dostępność maszyny + setup + przetwarzanie
        assert total_time >= 10.0


class TestScheduleRepr:
    """Testy reprezentacji tekstowej obiektu Schedule."""

    def test_repr_empty_schedule(self):
        """Test reprezentacji pustego harmonogramu."""
        schedule = Schedule()
        repr_str = repr(schedule)

        assert "Schedule" in repr_str
        assert "0 operacji" in repr_str
        assert "Cmax=0.00" in repr_str

    def test_repr_with_operations(self, sample_schedule):
        """Test reprezentacji z operacjami."""
        sample_schedule.build_from_sequence([0, 1, 2])

        repr_str = repr(sample_schedule)

        assert "Schedule" in repr_str
        assert "operacji" in repr_str
        assert "Cmax=" in repr_str


class TestScheduleIntegration:
    """Testy integracyjne dla Schedule."""

    def test_full_scheduling_workflow(self, sample_schedule_data):
        """Test pełnego procesu planowania."""
        # 1. Wczytaj dane
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        # 2. Zbuduj harmonogram
        sequence = [0, 1, 2]
        cmax = schedule.build_from_sequence(sequence)

        # 3. Sprawdź wyniki
        assert cmax > 0
        assert len(schedule.schedule) > 0
        assert schedule.Cmax == cmax

        # 4. Zapisz do pliku
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        schedule.save_to_file(output_file)

        # 5. Sprawdź plik
        with open(output_file) as f:
            data = json.load(f)
        assert len(data) == len(schedule.schedule)

    def test_multiple_sequence_evaluations(self, sample_schedule_data):
        """Test ewaluacji wielu sekwencji."""
        schedule = Schedule()
        schedule.load_from_json(sample_schedule_data)

        sequences = [
            [0, 1, 2],
            [2, 1, 0],
            [1, 0, 2],
        ]

        results = []
        for seq in sequences:
            schedule._reset_runtime_state()
            cmax = schedule.build_from_sequence(seq)
            results.append(cmax)

        # Wszystkie wyniki powinny być dodatnie
        assert all(cmax > 0 for cmax in results)

    def test_learning_effect_impact(self, tmp_path):
        """Test wpływu efektu uczenia na Cmax."""
        # Dane bez uczenia
        data_no_learning = {
            "num_stages": 1,
            "machines_per_stage": [1],
            "learning_coefficient": 0.0,
            "learning_stages": "0",
            "processing_times": [[[10.0]], [[10.0]], [[10.0]]],
            "setup_times": [
                [[[0.0]], [[0.0]], [[0.0]]],
                [[[0.0]], [[0.0]], [[0.0]]],
                [[[0.0]], [[0.0]], [[0.0]]],
            ],
        }

        # Dane z uczeniem
        data_with_learning = data_no_learning.copy()
        data_with_learning["learning_coefficient"] = 0.5
        data_with_learning["learning_stages"] = "1"

        # Test bez uczenia
        file1 = tmp_path / "no_learning.json"
        with open(file1, "w") as f:
            json.dump(data_no_learning, f)

        schedule1 = Schedule()
        schedule1.load_from_json(str(file1))
        cmax1 = schedule1.build_from_sequence([0, 1, 2])

        # Test z uczeniem
        file2 = tmp_path / "with_learning.json"
        with open(file2, "w") as f:
            json.dump(data_with_learning, f)

        schedule2 = Schedule()
        schedule2.load_from_json(str(file2))
        cmax2 = schedule2.build_from_sequence([0, 1, 2])

        # Z uczeniem powinien być krótszy Cmax
        assert cmax2 < cmax1

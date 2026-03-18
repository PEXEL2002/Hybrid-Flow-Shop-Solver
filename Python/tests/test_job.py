"""Testy jednostkowe dla klasy Job."""

import pytest
from core.job import Job


class TestJobInitialization:
    """Testy inicjalizacji obiektu Job."""

    def test_job_creation_with_valid_data(self, sample_processing_times, sample_setup_times):
        """Test tworzenia zadania z poprawnymi danymi."""
        job = Job(job_id=0, stages=sample_processing_times[0], setup_times=sample_setup_times)

        assert job.id == 0
        assert job.stages == sample_processing_times[0]
        assert job.setup_times == sample_setup_times
        assert job.name == "Job_0"

    def test_job_creation_with_custom_name(self, sample_processing_times, sample_setup_times):
        """Test tworzenia zadania z niestandardową nazwą."""
        job = Job(
            job_id=1,
            stages=sample_processing_times[1],
            setup_times=sample_setup_times,
            name="CustomJob"
        )

        assert job.id == 1
        assert job.name == "CustomJob"

    def test_job_initialization_arrays(self, sample_processing_times, sample_setup_times):
        """Test inicjalizacji tablic czasowych."""
        job = Job(job_id=0, stages=sample_processing_times[0], setup_times=sample_setup_times)

        # Sprawdź długości tablic
        num_stages = len(sample_processing_times[0])
        assert len(job.machine_assignment) == num_stages
        assert len(job.completion_times) == num_stages
        assert len(job.start_processing_times) == num_stages
        assert len(job.start_setup_times) == num_stages
        assert len(job.end_setup_times) == num_stages

        # Sprawdź wartości początkowe
        assert all(ma == -1 for ma in job.machine_assignment)
        assert all(ct == 0.0 for ct in job.completion_times)
        assert job.total_time == 0.0


class TestJobGetProcessingTime:
    """Testy metody get_processing_time."""

    def test_get_processing_time_scalar(self, sample_job):
        """Test pobierania czasu przetwarzania - wartość skalarna."""
        proc_time = sample_job.get_processing_time(stage=0, machine=0)
        assert proc_time == 5.0
        assert isinstance(proc_time, float)

    def test_get_processing_time_list_format(self, sample_setup_times):
        """Test pobierania czasu przetwarzania - format listowy."""
        # Dane w formacie [[5.0], [4.0]]
        stages = [[[5.0], [6.0]], [[4.0], [5.0]]]
        job = Job(job_id=0, stages=stages, setup_times=sample_setup_times)

        proc_time = job.get_processing_time(stage=0, machine=0)
        assert proc_time == 5.0
        assert isinstance(proc_time, float)

    def test_get_processing_time_different_machines(self, sample_job):
        """Test pobierania różnych czasów dla różnych maszyn."""
        time_m0 = sample_job.get_processing_time(stage=0, machine=0)
        time_m1 = sample_job.get_processing_time(stage=0, machine=1)

        assert time_m0 == 5.0
        assert time_m1 == 6.0

    def test_get_processing_time_different_stages(self, sample_job):
        """Test pobierania różnych czasów dla różnych etapów."""
        time_s0 = sample_job.get_processing_time(stage=0, machine=0)
        time_s1 = sample_job.get_processing_time(stage=1, machine=0)

        assert time_s0 == 5.0
        assert time_s1 == 4.0


class TestJobGetSetupTime:
    """Testy metody get_setup_time."""

    def test_get_self_setup_time_with_none(self, sample_job):
        """Test pobierania czasu self-setup (prev_job=None)."""
        setup_time = sample_job.get_setup_time(prev_job=None, stage=0, machine=0)
        assert setup_time == 1.0  # setup_times[0][0][0][0]

    def test_get_self_setup_time_with_minus_one(self, sample_job):
        """Test pobierania czasu self-setup (prev_job=-1)."""
        setup_time = sample_job.get_setup_time(prev_job=-1, stage=0, machine=0)
        assert setup_time == 1.0

    def test_get_setup_time_from_different_job(self, sample_processing_times, sample_setup_times):
        """Test pobierania czasu przezbrojenia między różnymi zadaniami."""
        job1 = Job(job_id=1, stages=sample_processing_times[1], setup_times=sample_setup_times)

        # Przezbrojenie z zadania 0 do zadania 1
        setup_time = job1.get_setup_time(prev_job=0, stage=0, machine=0)
        assert setup_time == 2.0  # setup_times[0][1][0][0]

    def test_get_setup_time_list_format(self, sample_setup_times):
        """Test pobierania czasu przezbrojenia w formacie listowym."""
        # Modyfikacja danych - format listowy
        # setup_times[from_job][to_job][stage][machine]
        setup_list = [
            [[[1.0], [1.0]], [[2.0], [2.5]]],  # Z zadania 0 -> do 0, do 1
            [[[3.0], [3.5]], [[1.5], [1.5]]],  # Z zadania 1 -> do 0, do 1
        ]
        stages = [[5.0, 6.0], [4.0, 5.0]]
        job = Job(job_id=1, stages=stages, setup_times=setup_list)

        # Setup z zadania 0 do zadania 1, etap 0, maszyna 0
        setup_time = job.get_setup_time(prev_job=0, stage=0, machine=0)
        assert setup_time == 2.0  # setup_list[0][1][0][0] = [2.0][0] = 2.0
        assert isinstance(setup_time, float)

    def test_get_setup_time_different_machines(self, sample_job):
        """Test różnych czasów przezbrojenia dla różnych maszyn."""
        time_m0 = sample_job.get_setup_time(prev_job=None, stage=0, machine=0)
        time_m1 = sample_job.get_setup_time(prev_job=None, stage=0, machine=1)

        assert time_m0 == 1.0
        assert time_m1 == 1.0


class TestJobSetStageTimes:
    """Testy metody set_stage_times."""

    def test_set_stage_times_valid(self, sample_job):
        """Test ustawiania poprawnych czasów dla etapu."""
        sample_job.set_stage_times(
            stage=0,
            machine=1,
            setup_start=0.0,
            setup_end=1.0,
            proc_start=1.0,
            proc_end=6.0
        )

        assert sample_job.start_setup_times[0] == 0.0
        assert sample_job.end_setup_times[0] == 1.0
        assert sample_job.start_processing_times[0] == 1.0
        assert sample_job.completion_times[0] == 6.0
        assert sample_job.machine_assignment[0] == 1
        assert sample_job.total_time == 6.0

    def test_set_stage_times_multiple_stages(self, sample_job):
        """Test ustawiania czasów dla wielu etapów."""
        # Etap 0
        sample_job.set_stage_times(0, 0, 0.0, 1.0, 1.0, 6.0)
        # Etap 1
        sample_job.set_stage_times(1, 1, 6.0, 8.0, 8.0, 12.0)

        assert sample_job.total_time == 12.0
        assert sample_job.machine_assignment == [0, 1]

    def test_set_stage_times_invalid_proc_before_setup(self, sample_job):
        """Test walidacji - przetwarzanie przed zakończeniem setupu."""
        with pytest.raises(ValueError, match="nie może być wcześniejszy niż koniec przezbrojenia"):
            sample_job.set_stage_times(
                stage=0,
                machine=0,
                setup_start=0.0,
                setup_end=5.0,
                proc_start=3.0,  # Przed końcem setupu!
                proc_end=10.0
            )

    def test_set_stage_times_invalid_end_before_start(self, sample_job):
        """Test walidacji - zakończenie przed rozpoczęciem."""
        with pytest.raises(ValueError, match="nie może być wcześniejszy niż czas rozpoczęcia"):
            sample_job.set_stage_times(
                stage=0,
                machine=0,
                setup_start=0.0,
                setup_end=1.0,
                proc_start=10.0,
                proc_end=5.0  # Przed rozpoczęciem!
            )

    def test_set_stage_times_updates_total_time(self, sample_job):
        """Test aktualizacji total_time."""
        sample_job.set_stage_times(0, 0, 0.0, 1.0, 1.0, 5.0)
        assert sample_job.total_time == 5.0

        # Drugi etap z dłuższym czasem
        sample_job.set_stage_times(1, 0, 5.0, 6.0, 6.0, 15.0)
        assert sample_job.total_time == 15.0

    def test_set_stage_times_with_delay(self, sample_job):
        """Test z opóźnieniem między etapami."""
        # Przetwarzanie może rozpocząć się po zakończeniu setupu
        sample_job.set_stage_times(
            stage=0,
            machine=0,
            setup_start=0.0,
            setup_end=2.0,
            proc_start=5.0,  # Opóźnienie po setupie
            proc_end=10.0
        )

        assert sample_job.start_processing_times[0] == 5.0
        assert sample_job.completion_times[0] == 10.0

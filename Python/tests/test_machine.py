"""Testy jednostkowe dla klasy Machine."""

import pytest
from core.machine import Machine


class TestMachineInitialization:
    """Testy inicjalizacji obiektu Machine."""

    def test_machine_creation_without_learning(self):
        """Test tworzenia maszyny bez efektu uczenia."""
        machine = Machine(stage_id=0, machine_id=1, is_learning=False)

        assert machine.stage_id == 0
        assert machine.machine_id == 1
        assert machine.is_learning is False
        assert machine.state == "free"
        assert machine.last_job is None
        assert machine.available_time == 0.0
        assert machine.processed_jobs == 0

    def test_machine_creation_with_learning(self):
        """Test tworzenia maszyny z efektem uczenia."""
        machine = Machine(stage_id=2, machine_id=0, is_learning=True)

        assert machine.stage_id == 2
        assert machine.machine_id == 0
        assert machine.is_learning is True

    def test_machine_creation_default_learning(self):
        """Test domyślnej wartości parametru is_learning."""
        machine = Machine(stage_id=0, machine_id=0)

        assert machine.is_learning is False


class TestMachineStartSetup:
    """Testy metody start_setup."""

    def test_start_setup_changes_state(self, sample_machine):
        """Test zmiany stanu maszyny podczas setupu."""
        assert sample_machine.state == "free"

        end_time = sample_machine.start_setup(start_time=0.0, setup_duration=2.0)

        assert sample_machine.state == "setup"
        assert end_time == 2.0

    def test_start_setup_updates_available_time(self, sample_machine):
        """Test aktualizacji czasu dostępności."""
        sample_machine.start_setup(start_time=5.0, setup_duration=3.0)

        assert sample_machine.available_time == 8.0

    def test_start_setup_returns_correct_end_time(self, sample_machine):
        """Test poprawności zwracanego czasu zakończenia."""
        end_time = sample_machine.start_setup(start_time=10.0, setup_duration=2.5)

        assert end_time == 12.5
        assert isinstance(end_time, float)

    def test_start_setup_with_zero_duration(self, sample_machine):
        """Test setupu z zerowym czasem trwania."""
        end_time = sample_machine.start_setup(start_time=5.0, setup_duration=0.0)

        assert end_time == 5.0
        assert sample_machine.available_time == 5.0

    def test_start_setup_consecutive_calls(self, sample_machine):
        """Test kolejnych wywołań start_setup."""
        sample_machine.start_setup(start_time=0.0, setup_duration=2.0)
        assert sample_machine.available_time == 2.0

        sample_machine.start_setup(start_time=2.0, setup_duration=3.0)
        assert sample_machine.available_time == 5.0


class TestMachineStartProcessing:
    """Testy metody start_processing."""

    def test_start_processing_changes_state(self, sample_machine):
        """Test zmiany stanu maszyny podczas przetwarzania."""
        end_time = sample_machine.start_processing(
            job_id=1,
            start_time=0.0,
            process_duration=5.0
        )

        assert sample_machine.state == "busy"
        assert end_time == 5.0

    def test_start_processing_updates_last_job(self, sample_machine):
        """Test aktualizacji last_job."""
        sample_machine.start_processing(job_id=3, start_time=0.0, process_duration=5.0)

        assert sample_machine.last_job == 3

    def test_start_processing_increments_processed_jobs(self, sample_machine):
        """Test inkrementacji licznika przetworzonych zadań."""
        assert sample_machine.processed_jobs == 0

        sample_machine.start_processing(job_id=0, start_time=0.0, process_duration=5.0)
        assert sample_machine.processed_jobs == 1

        sample_machine.start_processing(job_id=1, start_time=5.0, process_duration=3.0)
        assert sample_machine.processed_jobs == 2

    def test_start_processing_updates_available_time(self, sample_machine):
        """Test aktualizacji czasu dostępności."""
        sample_machine.start_processing(job_id=0, start_time=2.0, process_duration=4.0)

        assert sample_machine.available_time == 6.0

    def test_start_processing_returns_correct_end_time(self, sample_machine):
        """Test poprawności zwracanego czasu zakończenia."""
        end_time = sample_machine.start_processing(
            job_id=2,
            start_time=10.0,
            process_duration=7.5
        )

        assert end_time == 17.5
        assert isinstance(end_time, float)

    def test_start_processing_multiple_jobs(self, sample_machine):
        """Test przetwarzania wielu zadań kolejno."""
        # Zadanie 0
        sample_machine.start_processing(job_id=0, start_time=0.0, process_duration=5.0)
        assert sample_machine.last_job == 0
        assert sample_machine.processed_jobs == 1

        # Zadanie 1
        sample_machine.start_processing(job_id=1, start_time=5.0, process_duration=3.0)
        assert sample_machine.last_job == 1
        assert sample_machine.processed_jobs == 2


class TestMachineFinishJob:
    """Testy metody finish_job."""

    def test_finish_job_changes_state(self, sample_machine):
        """Test zmiany stanu po zakończeniu zadania."""
        sample_machine.start_processing(job_id=0, start_time=0.0, process_duration=5.0)
        assert sample_machine.state == "busy"

        sample_machine.finish_job()
        assert sample_machine.state == "free"

    def test_finish_job_preserves_other_attributes(self, sample_machine):
        """Test zachowania innych atrybutów po finish_job."""
        sample_machine.start_processing(job_id=2, start_time=0.0, process_duration=5.0)

        sample_machine.finish_job()

        # Te wartości powinny zostać zachowane
        assert sample_machine.last_job == 2
        assert sample_machine.processed_jobs == 1
        assert sample_machine.available_time == 5.0


class TestMachineComputeProcessingTime:
    """Testy metody compute_processing_time z efektem uczenia."""

    def test_compute_processing_time_no_learning(self, sample_machine):
        """Test bez efektu uczenia (is_learning=False)."""
        base_time = 10.0
        effective_time = sample_machine.compute_processing_time(base_time, learning_coeff=0.3)

        assert effective_time == base_time

    def test_compute_processing_time_zero_coefficient(self, sample_learning_machine):
        """Test z zerowym współczynnikiem uczenia."""
        base_time = 10.0
        effective_time = sample_learning_machine.compute_processing_time(
            base_time,
            learning_coeff=0.0
        )

        assert effective_time == base_time

    def test_compute_processing_time_first_job(self, sample_learning_machine):
        """Test czasu dla pierwszego zadania (r=1)."""
        base_time = 10.0
        learning_coeff = 0.3

        # Pierwsze zadanie: r=1, więc t_r = t_1 * 1^(-0.3) = t_1
        effective_time = sample_learning_machine.compute_processing_time(
            base_time,
            learning_coeff
        )

        assert effective_time == base_time

    def test_compute_processing_time_second_job(self, sample_learning_machine):
        """Test efektu uczenia dla drugiego zadania."""
        base_time = 10.0
        learning_coeff = 0.3

        # Symulacja przetworzenia pierwszego zadania
        sample_learning_machine.start_processing(job_id=0, start_time=0.0, process_duration=10.0)

        # Drugie zadanie: r=2, więc t_r = 10.0 * 2^(-0.3)
        effective_time = sample_learning_machine.compute_processing_time(
            base_time,
            learning_coeff
        )

        expected_time = base_time * (2 ** (-learning_coeff))
        assert abs(effective_time - expected_time) < 0.001

    def test_compute_processing_time_learning_curve(self, sample_learning_machine):
        """Test krzywej uczenia dla wielu zadań."""
        base_time = 100.0
        learning_coeff = 0.5

        times = []
        for i in range(5):
            effective_time = sample_learning_machine.compute_processing_time(
                base_time,
                learning_coeff
            )
            times.append(effective_time)

            # Symulacja zakończenia zadania
            sample_learning_machine.start_processing(
                job_id=i,
                start_time=0.0,
                process_duration=effective_time
            )

        # Sprawdź, że czasy maleją (efekt uczenia)
        for i in range(1, len(times)):
            assert times[i] < times[i - 1]

    def test_compute_processing_time_strong_learning(self, sample_learning_machine):
        """Test silnego efektu uczenia (α=0.5)."""
        base_time = 100.0
        learning_coeff = 0.5

        # Pierwsze zadanie
        time_1 = sample_learning_machine.compute_processing_time(base_time, learning_coeff)
        sample_learning_machine.start_processing(job_id=0, start_time=0.0, process_duration=time_1)

        # Dziesiąte zadanie
        for i in range(1, 10):
            t = sample_learning_machine.compute_processing_time(base_time, learning_coeff)
            sample_learning_machine.start_processing(job_id=i, start_time=0.0, process_duration=t)

        time_10 = sample_learning_machine.compute_processing_time(base_time, learning_coeff)

        # r=11, t_11 = 100 * 11^(-0.5) ≈ 30.15
        expected_time = base_time * (11 ** (-learning_coeff))
        assert abs(time_10 - expected_time) < 0.01

    def test_compute_processing_time_moderate_learning(self, sample_learning_machine):
        """Test umiarkowanego efektu uczenia (α=0.3)."""
        base_time = 50.0
        learning_coeff = 0.3

        # Przetwórz 3 zadania
        for i in range(3):
            t = sample_learning_machine.compute_processing_time(base_time, learning_coeff)
            sample_learning_machine.start_processing(job_id=i, start_time=0.0, process_duration=t)

        # Czwarte zadanie: r=4, t_4 = 50 * 4^(-0.3)
        time_4 = sample_learning_machine.compute_processing_time(base_time, learning_coeff)
        expected_time = base_time * (4 ** (-learning_coeff))

        assert abs(time_4 - expected_time) < 0.01


class TestMachineRepr:
    """Testy reprezentacji tekstowej obiektu Machine."""

    def test_repr_initial_state(self, sample_machine):
        """Test reprezentacji dla nowej maszyny."""
        repr_str = repr(sample_machine)

        assert "Machine" in repr_str
        assert "S0_M0" in repr_str
        assert "state=free" in repr_str
        assert "last_job=None" in repr_str
        assert "avail=0.00" in repr_str
        assert "jobs=0" in repr_str

    def test_repr_after_processing(self, sample_machine):
        """Test reprezentacji po przetworzeniu zadania."""
        sample_machine.start_processing(job_id=2, start_time=0.0, process_duration=10.5)

        repr_str = repr(sample_machine)

        assert "state=busy" in repr_str
        assert "last_job=2" in repr_str
        assert "avail=10.50" in repr_str
        assert "jobs=1" in repr_str


class TestMachineIntegration:
    """Testy integracyjne symulujące rzeczywiste scenariusze."""

    def test_complete_workflow_setup_and_processing(self, sample_machine):
        """Test pełnego cyklu: setup -> przetwarzanie -> finish."""
        # Setup
        setup_end = sample_machine.start_setup(start_time=0.0, setup_duration=2.0)
        assert sample_machine.state == "setup"
        assert setup_end == 2.0

        # Przetwarzanie
        proc_end = sample_machine.start_processing(
            job_id=5,
            start_time=2.0,
            process_duration=8.0
        )
        assert sample_machine.state == "busy"
        assert proc_end == 10.0
        assert sample_machine.last_job == 5

        # Zakończenie
        sample_machine.finish_job()
        assert sample_machine.state == "free"

    def test_multiple_jobs_with_learning(self, sample_learning_machine):
        """Test przetwarzania wielu zadań z efektem uczenia."""
        base_time = 20.0
        learning_coeff = 0.4

        total_time = 0.0
        for job_id in range(4):
            # Setup
            setup_end = sample_learning_machine.start_setup(
                start_time=total_time,
                setup_duration=1.0
            )

            # Oblicz czas przetwarzania z uczeniem
            proc_time = sample_learning_machine.compute_processing_time(
                base_time,
                learning_coeff
            )

            # Przetwarzanie
            proc_end = sample_learning_machine.start_processing(
                job_id=job_id,
                start_time=setup_end,
                process_duration=proc_time
            )

            total_time = proc_end

        # Sprawdź, że przetworzono wszystkie zadania
        assert sample_learning_machine.processed_jobs == 4
        assert sample_learning_machine.last_job == 3

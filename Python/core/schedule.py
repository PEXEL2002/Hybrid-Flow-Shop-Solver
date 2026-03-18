import json
from core.job import Job
from core.machine import Machine

class Schedule:
    """Zarządza harmonogramem w problemie HFS-SDST.

    Odpowiada za wczytywanie danych, budowę harmonogramu,
    obliczanie Cmax i eksport wyników.

    Attributes:
        jobs (list[Job]): Lista zadań do zaplanowania.
        machines (list[list[Machine]]): Dwuwymiarowa lista maszyn [etap][maszyna].
        schedule (list[dict]): Lista operacji (setup i operation).
        num_stages (int): Liczba etapów w problemie.
        machines_per_stage (list[int]): Liczba maszyn na każdym etapie.
        Cmax (float): Maksymalny czas zakończenia (makespan).
        learning_stages (str): String binarny określający etapy z uczeniem.
        learning_coeff (float): Współczynnik krzywej uczenia.
    """

    def __init__(self):
        """Inicjalizuje pusty harmonogram."""
        self._raw_data = None
        self.jobs = []
        self.machines = []
        self.schedule = []
        self.num_stages = 0
        self.machines_per_stage = []
        self.Cmax = 0.0
        self.learning_stages = ""
        self.learning_coeff = 0.0

    def load_from_json(self, file_path):
        """Wczytuje dane problemu z pliku JSON.

        Tworzy obiekty Job i Machine na podstawie danych wejściowych.

        Args:
            file_path (str): Ścieżka do pliku JSON z danymi problemu.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        self._raw_data = data
        self.num_stages = data["num_stages"]
        self.machines_per_stage = data["machines_per_stage"]
        self.learning_coeff = data.get("learning_coefficient", 0.0)
        self.learning_stages = data.get("learning_stages", "0" * self.num_stages)
        self.setup_times = data["setup_times"]
        self.processing_times = data["processing_times"]

        self.jobs = [
            Job(
                job_id=j,
                stages=self.processing_times[j],
                setup_times=self.setup_times
            )
            for j in range(len(self.processing_times))
        ]

        self.machines = [
            [Machine(stage_id=s, machine_id=m, is_learning=self.learning_stages[s] == "1")
             for m in range(self.machines_per_stage[s])]
            for s in range(self.num_stages)
        ]

    def build_natural_schedule(self):
        """Buduje harmonogram dla naturalnej kolejności zadań.

        Zadania przetwarzane są w kolejności 0, 1, 2, ..., n-1.
        Setup na kolejnym etapie może rozpocząć się przed zakończeniem
        operacji z poprzedniego etapu.
        """
        sequence = list(range(len(self.jobs)))
        self.schedule = []

        for j in sequence:
            job = self.jobs[j]
            prev_stage_end = 0.0
            for s in range(self.num_stages):
                m = min(range(self.machines_per_stage[s]), key=lambda k: self.machines[s][k].available_time)
                machine = self.machines[s][m]
                prev_job = machine.last_job

                setup_duration = job.get_setup_time(prev_job, s, m)
                setup_start = machine.available_time
                setup_end = machine.start_setup(setup_start, setup_duration)

                base_time = job.get_processing_time(s, m)
                proc_time = machine.compute_processing_time(base_time, self.learning_coeff)
                proc_start = max(setup_end, prev_stage_end)
                proc_end = machine.start_processing(job.id, proc_start, proc_time)

                job.set_stage_times(s, m, setup_start, setup_end, proc_start, proc_end)

                self.add_operation(
                    "setup",
                    from_job=(prev_job if prev_job is not None else job.id),
                    to_job=job.id,
                    stage=s,
                    machine=m,
                    start=setup_start,
                    end=setup_end
                )
                self.add_operation(
                    "operation",
                    job=job.id,
                    stage=s,
                    machine=m,
                    start=proc_start,
                    end=proc_end
                )

                prev_stage_end = proc_end

        self.Cmax = self.compute_Cmax()

    def add_operation(self, op_type, **kwargs):
        """Dodaje operację do harmonogramu.

        Args:
            op_type (str): Typ operacji ('setup' lub 'operation').
            **kwargs: Dodatkowe parametry operacji (job, stage, machine, start, end).
        """
        entry = {"type": op_type}
        entry.update(kwargs)
        self.schedule.append(entry)

    def compute_Cmax(self):
        """Oblicza i zwraca maksymalny czas zakończenia (makespan).

        Returns:
            float: Maksymalny czas zakończenia wszystkich operacji.
        """
        if not self.schedule:
            return 0.0
        self.Cmax = max(op["end"] for op in self.schedule)
        return self.Cmax

    def to_json(self):
        """Zwraca harmonogram w formacie JSON.

        Returns:
            list[dict]: Lista operacji harmonogramu.
        """
        return self.schedule

    def save_to_file(self, file_path):
        """Zapisuje harmonogram do pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku wyjściowego.
        """
        with open(file_path, "w") as f:
            json.dump(self.schedule, f, indent=4)

    def _calculate_total_time(self, job, stage, machine_idx, machines):
        """Oblicza całkowity czas zakończenia zadania na maszynie.

        Uwzględnia dostępność maszyny, czas przezbrojenia i przetwarzania.

        Args:
            job (Job): Obiekt zadania.
            stage (int): Numer etapu.
            machine_idx (int): Indeks maszyny na etapie.
            machines (list[list[Machine]]): Dwuwymiarowa lista maszyn.

        Returns:
            float: Całkowity czas zakończenia zadania.
        """
        machine = machines[stage][machine_idx]
        prev_job = machine.last_job
        setup_dur = job.get_setup_time(prev_job, stage, machine_idx)
        base_time = job.get_processing_time(stage, machine_idx)
        proc_time = machine.compute_processing_time(base_time, self.learning_coeff)
        return machine.available_time + setup_dur + proc_time

    def build_from_sequence(self, sequence):
        """Buduje harmonogram dla zadanej permutacji zadań.

        Tworzy pełny harmonogram (setup + operation) i oblicza Cmax.

        Args:
            sequence (list[int]): Kolejność zadań do zaplanowania (np. [0, 1, 2]).

        Returns:
            float: Maksymalny czas zakończenia (Cmax).
        """
        self._reset_runtime_state()

        jobs = self.jobs
        machines = self.machines
        mps = self.machines_per_stage
        S = self.num_stages

        for j in sequence:
            job = jobs[j]
            prev_stage_end = 0.0

            for s in range(S):
                if mps[s] >= 2:
                    m = min(range(mps[s]), key=lambda k: self._calculate_total_time(job, s, k, machines))
                else:
                    m = 0

                machine = machines[s][m]
                prev_job = machine.last_job

                setup_dur = job.get_setup_time(prev_job, s, m)
                setup_start = machine.available_time
                setup_end = machine.start_setup(setup_start, setup_dur)

                base_time = job.get_processing_time(s, m)
                proc_time = machines[s][m].compute_processing_time(base_time, self.learning_coeff)
                proc_start = max(setup_end, prev_stage_end)
                proc_end = machine.start_processing(job.id, proc_start, proc_time)

                job.set_stage_times(s, m, setup_start, setup_end, proc_start, proc_end)

                self.add_operation(
                    "setup",
                    from_job=(prev_job if prev_job is not None else job.id),
                    to_job=job.id,
                    stage=s,
                    machine=m,
                    start=setup_start,
                    end=setup_end
                )
                self.add_operation(
                    "operation",
                    job=job.id,
                    stage=s,
                    machine=m,
                    start=proc_start,
                    end=proc_end
                )
                prev_stage_end = proc_end
        self.Cmax = self.compute_Cmax()
        return self.Cmax

    def __repr__(self):
        return f"Schedule: {len(self.schedule)} operacji, Cmax={self.Cmax:.2f}"

    def _reset_runtime_state(self):
        """Resetuje stan harmonogramu do stanu początkowego.

        Odtwarza stan maszyn i zadań na podstawie surowych danych.
        Czyści harmonogram i Cmax. Używane przed każdą budową harmonogramu.

        Raises:
            RuntimeError: Gdy brak surowych danych (nie wywołano load_from_json).
        """
        if self._raw_data is None:
            raise RuntimeError("Brak surowych danych w Schedule (_raw_data is None). Użyj load_from_json().")

        data = self._raw_data
        self.num_stages = data["num_stages"]
        self.machines_per_stage = data["machines_per_stage"]
        self.learning_coeff = data.get("learning_coefficient", 0.0)
        self.learning_stages = data.get("learning_stages", "0" * self.num_stages)
        self.setup_times = data["setup_times"]
        self.processing_times = data["processing_times"]

        self.jobs = [
            Job(j, self.processing_times[j], self.setup_times)
            for j in range(len(self.processing_times))
        ]
        self.machines = [
            [Machine(stage_id=s, machine_id=m, is_learning=self.learning_stages[s] == "1")
             for m in range(self.machines_per_stage[s])]
            for s in range(self.num_stages)
        ]

        self.schedule = []
        self.Cmax = 0.0


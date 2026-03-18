class Job:
    """Reprezentuje jedno zadanie w problemie HFS-SDST z efektami uczenia.

    Attributes:
        id (int): Identyfikator zadania.
        stages (list[list[float]]): Czasy przetwarzania dla każdego etapu i maszyny.
        setup_times (list): Czterowymiarowa tablica czasów przezbrojenia [i][j][a][k].
        machine_assignment (list[int]): Przypisanie maszyn do poszczególnych etapów.
        completion_times (list[float]): Czasy zakończenia każdego etapu.
        start_processing_times (list[float]): Czasy rozpoczęcia przetwarzania na każdym etapie.
        start_setup_times (list[float]): Czasy rozpoczęcia przezbrojenia na każdym etapie.
        end_setup_times (list[float]): Czasy zakończenia przezbrojenia na każdym etapie.
        total_time (float): Całkowity czas realizacji zadania.
        name (str): Nazwa zadania.
    """

    def __init__(self, job_id, stages, setup_times, name=None):
        """Inicjalizuje obiekt zadania.

        Args:
            job_id (int): Identyfikator zadania.
            stages (list[list[float]]): Czasy przetwarzania dla etapów i maszyn.
            setup_times (list): Czterowymiarowa tablica czasów przezbrojenia.
            name (str, optional): Nazwa zadania. Jeśli nie podano, generowana automatycznie.
        """
        self.id = job_id
        self.stages = stages
        self.setup_times = setup_times
        self.machine_assignment = [-1 for _ in range(len(stages))]
        self.completion_times = [0.0 for _ in range(len(stages))]
        self.start_processing_times = [0.0 for _ in range(len(stages))]
        self.start_setup_times = [0.0 for _ in range(len(stages))]
        self.end_setup_times = [0.0 for _ in range(len(stages))]
        self.total_time = 0.0
        self.name = name or f"Job_{job_id}"

    def get_processing_time(self, stage: int, machine: int) -> float:
        """Zwraca bazowy czas przetwarzania dla danego etapu i maszyny.

        Obsługuje dane w formacie listowym (np. [10]) i skalarnym.

        Args:
            stage (int): Numer etapu.
            machine (int): Numer maszyny.

        Returns:
            float: Bazowy czas przetwarzania.
        """
        base_time = self.stages[stage][machine]
        if isinstance(base_time, list):
            base_time = base_time[0]
        return float(base_time)

    def get_setup_time(self, prev_job: int, stage: int, machine: int) -> float:
        """Zwraca czas przezbrojenia maszyny.

        Oblicza czas przezbrojenia potrzebny do uruchomienia tego zadania
        po wykonaniu zadania poprzedniego na danym etapie i maszynie.
        Dla pierwszego zadania (prev_job = None lub -1) zwraca czas
        inicjalnego przygotowania maszyny.

        Format: setup_times[i][j][a][k] oznacza czas przezbrojenia
        z zadania i do zadania j na etapie a i maszynie k.

        Args:
            prev_job (int): Identyfikator poprzedniego zadania lub None/-1.
            stage (int): Numer etapu.
            machine (int): Numer maszyny.

        Returns:
            float: Czas przezbrojenia.
        """
        if prev_job is None or prev_job == -1:
            setup_val = self.setup_times[self.id][self.id][stage][machine]
        else:
            setup_val = self.setup_times[prev_job][self.id][stage][machine]

        if isinstance(setup_val, list):
            setup_val = setup_val[0]
        return float(setup_val)

    def set_stage_times(self, stage, machine, setup_start, setup_end, proc_start, proc_end):
        """Ustawia czasy przetwarzania i przezbrojenia dla danego etapu.

        Waliduje poprawność czasową i aktualizuje wszystkie powiązane atrybuty.

        Args:
            stage (int): Numer etapu.
            machine (int): Numer maszyny.
            setup_start (float): Czas rozpoczęcia przezbrojenia.
            setup_end (float): Czas zakończenia przezbrojenia.
            proc_start (float): Czas rozpoczęcia przetwarzania.
            proc_end (float): Czas zakończenia przetwarzania.

        Raises:
            ValueError: Gdy czasy są niespójne (przetwarzanie przed setupem lub
                       zakończenie przed rozpoczęciem).
        """
        if proc_start < setup_end:
            raise ValueError(
                f"[Job {self.id}] Czas rozpoczęcia przetwarzania ({proc_start}) "
                f"nie może być wcześniejszy niż koniec przezbrojenia ({setup_end}) na etapie {stage}."
            )
        if proc_end < proc_start:
            raise ValueError(
                f"[Job {self.id}] Czas zakończenia etapu ({proc_end}) "
                f"nie może być wcześniejszy niż czas rozpoczęcia przetwarzania ({proc_start})."
            )

        self.start_setup_times[stage] = setup_start
        self.end_setup_times[stage] = setup_end
        self.start_processing_times[stage] = proc_start
        self.completion_times[stage] = proc_end
        self.machine_assignment[stage] = machine

        self.total_time = max(self.completion_times)
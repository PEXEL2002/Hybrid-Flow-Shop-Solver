class Machine:
    """Reprezentuje pojedynczą maszynę w środowisku HFS-SDST.

    Attributes:
        stage_id (int): Numer etapu, do którego należy maszyna.
        machine_id (int): Numer maszyny w obrębie etapu.
        state (str): Aktualny stan maszyny ('free', 'setup', 'busy').
        last_job (int | None): Identyfikator ostatnio wykonanego zadania.
        is_learning (bool): Czy maszyna podlega efektowi uczenia.
        available_time (float): Czas, od którego maszyna jest dostępna.
        processed_jobs (int): Liczba przetworzonych zadań na tej maszynie.
    """

    def __init__(self, stage_id: int, machine_id: int, is_learning: bool = False):
        """Inicjalizuje obiekt maszyny.

        Args:
            stage_id (int): Numer etapu.
            machine_id (int): Numer maszyny.
            is_learning (bool, optional): Czy maszyna podlega efektowi uczenia. Domyślnie False.
        """
        self.stage_id = stage_id
        self.machine_id = machine_id
        self.state = "free"
        self.last_job = None
        self.is_learning = is_learning
        self.available_time = 0.0
        self.processed_jobs = 0

    def start_setup(self, start_time: float, setup_duration: float) -> float:
        """Rozpoczyna przezbrojenie maszyny.

        Ustawia stan maszyny na 'setup' i aktualizuje czas dostępności.

        Args:
            start_time (float): Czas rozpoczęcia przezbrojenia.
            setup_duration (float): Czas trwania przezbrojenia.

        Returns:
            float: Czas zakończenia przezbrojenia.
        """
        self.state = "setup"
        end_time = start_time + float(setup_duration)
        self.available_time = end_time
        return end_time

    def start_processing(self, job_id: int, start_time: float, process_duration: float) -> float:
        """Rozpoczyna przetwarzanie zadania.

        Ustawia stan maszyny na 'busy' i aktualizuje wszystkie powiązane atrybuty.

        Args:
            job_id (int): Identyfikator przetwarzanego zadania.
            start_time (float): Czas rozpoczęcia przetwarzania.
            process_duration (float): Czas trwania przetwarzania.

        Returns:
            float: Czas zakończenia przetwarzania.
        """
        self.state = "busy"
        end_time = start_time + float(process_duration)
        self.available_time = end_time
        self.last_job = job_id
        self.processed_jobs += 1
        return end_time

    def finish_job(self):
        """Oznacza maszynę jako wolną po zakończeniu operacji."""
        self.state = "free"

    def compute_processing_time(self, base_time: float, learning_coeff: float = 0.0):
        """Oblicza efektywny czas przetwarzania z uwzględnieniem efektu uczenia.

        Stosuje wzór krzywej uczenia: t_r = t_1 × r^(-α)
        gdzie:
        - t_r: czas r-tego powtórzenia zadania
        - t_1: bazowy czas pierwszego wykonania
        - r: numer powtórzenia (1, 2, 3, ...)
        - α: współczynnik uczenia

        Przykładowe wartości współczynnika:
        - α = 0.0 → brak efektu uczenia (t_r = t_1)
        - α = 0.3 → umiarkowane uczenie
        - α = 0.5 → silne uczenie

        Args:
            base_time (float): Bazowy czas operacji.
            learning_coeff (float, optional): Współczynnik uczenia (α). Domyślnie 0.0.

        Returns:
            float: Efektywny czas przetwarzania z uwzględnieniem uczenia.
        """
        if not self.is_learning or learning_coeff == 0.0:
            return base_time

        r = self.processed_jobs + 1
        effective_time = base_time * (r ** (-learning_coeff))
        return effective_time

    def __repr__(self):
        return (f"Machine(S{self.stage_id}_M{self.machine_id}, "
                f"state={self.state}, last_job={self.last_job}, "
                f"avail={self.available_time:.2f}, jobs={self.processed_jobs})")

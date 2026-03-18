from abc import ABC, abstractmethod
import time

class BaseAlgorithm(ABC):
    """Abstrakcyjna klasa bazowa dla algorytmów szeregowania.

    Definiuje wspólny interfejs i strukturę danych dla wszystkich
    algorytmów rozwiązujących problem HFS-SDST.

    Attributes:
        name (str): Nazwa algorytmu.
        schedule (Schedule): Obiekt harmonogramu z danymi problemu.
        best_sequence (list[int]): Najlepsza znaleziona permutacja zadań.
        best_cmax (float): Najlepszy znaleziony makespan.
        result_schedule (list[dict]): Harmonogram operacji dla najlepszego rozwiązania.
        runtime (float): Czas wykonania algorytmu w sekundach.
    """

    def __init__(self, schedule, name="BaseAlgorithm"):
        """Inicjalizuje algorytm.

        Args:
            schedule (Schedule): Obiekt harmonogramu z danymi problemu.
            name (str, optional): Nazwa algorytmu. Domyślnie "BaseAlgorithm".
        """
        self.name = name
        self.schedule = schedule
        self.best_sequence = None
        self.best_cmax = None
        self.result_schedule = None
        self.runtime = 0.0

    @abstractmethod
    def run(self):
        """Uruchamia algorytm szeregowania.

        Metoda abstrakcyjna do implementacji w klasach pochodnych.

        Returns:
            dict: Wyniki działania algorytmu.
        """
        pass

    def get_results(self):
        """Zwraca wyniki działania algorytmu w ustandaryzowanym formacie.

        Returns:
            dict: Słownik zawierający:
                - C_max (float): Maksymalny czas zakończenia.
                - time_in_ms (float): Czas wykonania w milisekundach.
                - schedule (list[dict]): Lista operacji harmonogramu.
        """
        return {
            "C_max": self.best_cmax,
            "time_in_ms": round(self.runtime * 1000, 3),
            "schedule": self.result_schedule
        }

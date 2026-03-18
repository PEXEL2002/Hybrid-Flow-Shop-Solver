"""Generator diagramu Gantta dla harmonogramu HFS-SDST.

Wizualizuje harmonogram produkcji z podziałem na etapy i maszyny:
- Przezbrojenia (setup): szary kolor z ramką i wzorem ukośnych linii
- Operacje: kolorowe prostokąty bez ramek, każde zadanie ma unikalny kolor
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import json
import os


class GanttChart:
    """Generuje diagram Gantta dla harmonogramu produkcji.

    Attributes:
        JOB_COLORS (list[str]): Paleta kolorów dla zadań.
        SETUP_COLOR (str): Kolor przezbrojenia.
        SETUP_EDGE_COLOR (str): Kolor ramki przezbrojenia.
        SETUP_HATCH (str): Wzór wypełnienia przezbrojenia.
    """

    JOB_COLORS = [
        '#FFD700', '#87CEEB', '#FF6B6B', '#4ECDC4',
        '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3',
        '#A8E6CF', '#FFD3B6', '#FFA07A', '#98D8C8',
    ]

    SETUP_COLOR = '#CCCCCC'
    SETUP_EDGE_COLOR = '#666666'
    SETUP_HATCH = '///'

    def __init__(self, schedule_data=None):
        """Inicjalizuje generator diagramu Gantta.

        Args:
            schedule_data (dict | list, optional): Dane harmonogramu:
                - dict: oczekiwany klucz 'schedule' z listą operacji
                - list: bezpośrednia lista operacji
                - None: pusty harmonogram
        """
        self._raw_data = schedule_data if isinstance(schedule_data, dict) else {}
        self._source_file = None

        if schedule_data is None:
            self.schedule = []
            self.cmax = 0
            self.algorithm = ''
        elif isinstance(schedule_data, dict):
            self.schedule = schedule_data.get('schedule', [])
            self.cmax = schedule_data.get('C_max', 0)
            self.algorithm = schedule_data.get('Algorithm') or schedule_data.get('algorithm', '')
        else:
            self.schedule = schedule_data
            self.cmax = max(op['end'] for op in self.schedule) if self.schedule else 0
            self.algorithm = ''

        self.num_stages = 0
        self.machines_per_stage = {}
        self._detect_structure()

    @classmethod
    def from_file(cls, input_file):
        """
        Tworzy obiekt GanttChart z pliku JSON.

        Args:
            input_file (str): ścieżka do pliku JSON z harmonogramem

        Returns:
            GanttChart: obiekt z wczytanym harmonogramem

        Raises:
            FileNotFoundError: jeśli plik nie istnieje
            ValueError: jeśli plik nie zawiera klucza 'schedule'
            json.JSONDecodeError: jeśli plik nie jest poprawnym JSON
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Plik nie istnieje: {input_file}")

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'schedule' not in data:
            raise ValueError(f"Plik nie zawiera klucza 'schedule': {input_file}")

        instance = cls(data)
        instance._source_file = os.path.abspath(input_file)
        return instance

    @classmethod
    def from_schedule_object(cls, schedule_obj, algorithm='Schedule'):
        """
        Tworzy obiekt GanttChart z obiektu Schedule.

        Args:
            schedule_obj: obiekt Schedule z harmonogramem
            algorithm (str): nazwa algorytmu do wyświetlenia

        Returns:
            GanttChart: obiekt z harmonogramem
        """
        data = {
            'schedule': schedule_obj.schedule,
            'C_max': schedule_obj.Cmax,
            'algorithm': algorithm
        }
        return cls(data)

    @classmethod
    def from_results(cls, results_dict):
        """
        Tworzy obiekt GanttChart z wyników algorytmu.

        Args:
            results_dict (dict): słownik z wynikami algorytmu
                (oczekiwane klucze: 'schedule', 'C_max', 'Algorithm')

        Returns:
            GanttChart: obiekt z harmonogramem
        """
        return cls(results_dict)

    @property
    def num_operations(self):
        """Zwraca liczbę operacji w harmonogramie."""
        return len(self.schedule)

    def get_info(self):
        """
        Zwraca słownik z informacjami o harmonogramie.

        Returns:
            dict: informacje o harmonogramie
        """
        return {
            'algorithm': self.algorithm,
            'cmax': self.cmax,
            'num_operations': self.num_operations,
            'num_stages': self.num_stages,
            'source_file': self._source_file
        }

    def print_info(self):
        """Wyświetla informacje o harmonogramie."""
        info = self.get_info()
        print(f"[INFO] Algorytm: {info['algorithm']}")
        print(f"[INFO] C_max: {info['cmax']:.2f}")
        print(f"[INFO] Liczba operacji: {info['num_operations']}")
        if info['source_file']:
            print(f"[INFO] Plik źródłowy: {info['source_file']}")

    def save(self, output_file, figsize=(14, 8), show=False, title=None, update_source=True):
        """
        Generuje i zapisuje diagram Gantta do pliku.

        Args:
            output_file (str): ścieżka do pliku wyjściowego PNG
            figsize (tuple): rozmiar figury (szerokość, wysokość)
            show (bool): czy wyświetlić wykres
            title (str, optional): tytuł wykresu
            update_source (bool): czy zaktualizować plik źródłowy o ścieżkę do wykresu

        Returns:
            str: ścieżka do zapisanego pliku (absolutna)
        """
        # Upewnij się, że katalog docelowy istnieje
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Generuj wykres
        self.generate(output_file=output_file, figsize=figsize, show=show, title=title)

        abs_output = os.path.abspath(output_file)

        # Zaktualizuj plik źródłowy jeśli istnieje
        if update_source and self._source_file and os.path.exists(self._source_file):
            try:
                with open(self._source_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['gant_diagram'] = abs_output
                with open(self._source_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass  # Ignoruj błędy aktualizacji

        return abs_output

    def _detect_structure(self):
        """Wykrywa strukturę etapów i maszyn z harmonogramu."""
        for op in self.schedule:
            stage = op['stage']
            machine = op['machine']
            self.num_stages = max(self.num_stages, stage + 1)
            if stage not in self.machines_per_stage:
                self.machines_per_stage[stage] = set()
            self.machines_per_stage[stage].add(machine)

        for stage in self.machines_per_stage:
            self.machines_per_stage[stage] = sorted(list(self.machines_per_stage[stage]))

    def _get_job_color(self, job_id):
        """Zwraca kolor dla danego zadania.

        Args:
            job_id (int): Identyfikator zadania.

        Returns:
            str: Kod koloru w formacie hex.
        """
        return self.JOB_COLORS[job_id % len(self.JOB_COLORS)]

    def _create_machine_labels(self):
        """Tworzy etykiety dla osi Y wykresu Gantta.

        Returns:
            tuple: (labels, positions) - lista etykiet i ich pozycji.
        """
        labels = []
        positions = []
        current_pos = 0

        for stage in range(self.num_stages):
            machines = self.machines_per_stage.get(stage, [])
            for machine in machines:
                labels.append(f'Stage {stage}, M{machine}')
                positions.append(current_pos)
                current_pos += 1

        return labels, positions

    def generate(self, output_file=None, figsize=(14, 8), show=True, title=None):
        """Generuje diagram Gantta.

        Args:
            output_file (str, optional): Ścieżka do pliku wyjściowego (np. 'gantt.png').
            figsize (tuple, optional): Rozmiar figury (szerokość, wysokość). Domyślnie (14, 8).
            show (bool, optional): Czy wyświetlić wykres. Domyślnie True.
            title (str, optional): Tytuł wykresu. Jeśli None, generowany automatycznie.

        Returns:
            matplotlib.figure.Figure: Obiekt figury matplotlib.
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Tworzenie map pozycji dla każdej maszyny
        machine_positions = {}
        current_pos = 0
        for stage in range(self.num_stages):
            machines = self.machines_per_stage.get(stage, [])
            for machine in machines:
                machine_positions[(stage, machine)] = current_pos
                current_pos += 1

        # Rysowanie operacji
        for op in self.schedule:
            stage = op['stage']
            machine = op['machine']
            start = op['start']
            end = op['end']
            duration = end - start
            y_pos = machine_positions[(stage, machine)]

            if op['type'] == 'setup':
                # Przezbrojenie - szare z ramką i wzorem
                rect = Rectangle(
                    (start, y_pos - 0.4),
                    duration,
                    0.8,
                    facecolor=self.SETUP_COLOR,
                    edgecolor=self.SETUP_EDGE_COLOR,
                    linewidth=1.5,
                    hatch=self.SETUP_HATCH,
                    alpha=0.7
                )
                ax.add_patch(rect)

                # Etykieta dla setupu
                from_job = op.get('from_job', '?')
                to_job = op.get('to_job', '?')
                if duration > 2:  # Wyświetl tekst tylko jeśli jest miejsce
                    ax.text(
                        start + duration / 2,
                        y_pos,
                        f'S{from_job}→{to_job}',
                        ha='center',
                        va='center',
                        fontsize=7,
                        color='black',
                        weight='normal'
                    )

            elif op['type'] == 'operation':
                # Operacja - kolorowa bez ramki
                job_id = op['job']
                color = self._get_job_color(job_id)

                rect = Rectangle(
                    (start, y_pos - 0.4),
                    duration,
                    0.8,
                    facecolor=color,
                    edgecolor='none',  # Bez ramki
                    linewidth=0,
                    alpha=0.9
                )
                ax.add_patch(rect)

                # Etykieta dla operacji
                if duration > 1.5:  # Wyświetl tekst tylko jeśli jest miejsce
                    ax.text(
                        start + duration / 2,
                        y_pos,
                        f'J{job_id}',
                        ha='center',
                        va='center',
                        fontsize=9,
                        color='black',
                        weight='bold'
                    )

        # Konfiguracja osi
        labels, positions = self._create_machine_labels()
        ax.set_yticks(positions)
        ax.set_yticklabels(labels)
        ax.set_ylim(-0.5, len(positions) - 0.5)

        # Oś X
        ax.set_xlabel('Czas', fontsize=12, weight='bold')
        ax.set_xlim(0, self.cmax * 1.05)  # Dodatkowe 5% przestrzeni

        # Siatka
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

        # Tytuł
        if title is None:
            if self.algorithm:
                title = f'Diagram Gantta - {self.algorithm}\nCmax = {self.cmax:.2f}'
            else:
                title = f'Diagram Gantta\nCmax = {self.cmax:.2f}'
        ax.set_title(title, fontsize=14, weight='bold', pad=20)

        # Legenda
        legend_elements = []

        # Dodaj przykładowe zadania do legendy
        num_jobs = len(set(op.get('job', -1) for op in self.schedule if op['type'] == 'operation'))
        for job_id in range(min(num_jobs, len(self.JOB_COLORS))):
            legend_elements.append(
                mpatches.Patch(
                    facecolor=self._get_job_color(job_id),
                    edgecolor='none',
                    label=f'Zadanie {job_id}'
                )
            )

        # Dodaj setup do legendy
        legend_elements.append(
            mpatches.Patch(
                facecolor=self.SETUP_COLOR,
                edgecolor=self.SETUP_EDGE_COLOR,
                hatch=self.SETUP_HATCH,
                label='Przezbrojenie'
            )
        )

        ax.legend(
            handles=legend_elements,
            loc='upper right',
            fontsize=9,
            framealpha=0.9
        )

        plt.tight_layout()

        # Zapis do pliku
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Diagram Gantta zapisany do: {output_file}")

        # Wyświetlenie
        if show:
            plt.show()

        return fig


def generate_gantt_from_file(input_file, output_file=None, show=True):
    """
    Funkcja pomocnicza do generowania diagramu Gantta z pliku JSON.

    Args:
        input_file (str): ścieżka do pliku JSON z harmonogramem
        output_file (str, optional): ścieżka do pliku wyjściowego (np. 'gantt.png')
        show (bool): czy wyświetlić wykres

    Returns:
        matplotlib.figure.Figure: obiekt figury matplotlib

    Example:
        >>> generate_gantt_from_file('result.json', 'gantt.png')
    """
    gantt = GanttChart.from_file(input_file)
    return gantt.generate(output_file=output_file, show=show)


def generate_gantt_from_schedule(schedule_obj, output_file=None, show=True, algorithm='Schedule'):
    """
    Funkcja pomocnicza do generowania diagramu Gantta z obiektu Schedule.

    Args:
        schedule_obj: obiekt Schedule z harmonogramem
        output_file (str, optional): ścieżka do pliku wyjściowego
        show (bool): czy wyświetlić wykres
        algorithm (str): nazwa algorytmu do wyświetlenia

    Returns:
        matplotlib.figure.Figure: obiekt figury matplotlib

    Example:
        >>> from core.schedule import Schedule
        >>> schedule = Schedule()
        >>> schedule.load_from_json('data/instance.json')
        >>> schedule.build_natural_schedule()
        >>> generate_gantt_from_schedule(schedule, 'gantt.png')
    """
    gantt = GanttChart.from_schedule_object(schedule_obj, algorithm=algorithm)
    return gantt.generate(output_file=output_file, show=show)


if __name__ == '__main__':
    # Przykład użycia
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        generate_gantt_from_file(input_file, output_file)
    else:
        print("Użycie: python gantt_chart.py <plik_wejściowy.json> [plik_wyjściowy.png]")
        print("\nPrzykład:")
        print("  python gantt_chart.py result.json gantt.png")
        print("\nLub w kodzie Python:")
        print("  from utils.gantt_chart import generate_gantt_from_file")
        print("  generate_gantt_from_file('result.json', 'gantt.png')")

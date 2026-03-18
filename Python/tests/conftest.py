"""Fixtures i konfiguracja dla testów pytest.

Ten moduł zawiera współdzielone fixtures używane w testach jednostkowych.
"""

import pytest
import json
import os
import tempfile
from core.job import Job
from core.machine import Machine
from core.schedule import Schedule


@pytest.fixture
def sample_setup_times():
    """Fixture z przykładowymi czasami przezbrojenia.

    Returns:
        list: 4-wymiarowa tablica czasów przezbrojenia [i][j][stage][machine].
    """
    # 3 zadania, 2 etapy, 2 maszyny na każdym etapie
    return [
        [  # Z zadania 0
            [[1.0, 1.0], [1.0, 1.0]],  # do zadania 0
            [[2.0, 2.5], [2.0, 2.5]],  # do zadania 1
            [[3.0, 3.5], [3.0, 3.5]],  # do zadania 2
        ],
        [  # Z zadania 1
            [[2.5, 2.0], [2.5, 2.0]],  # do zadania 0
            [[1.5, 1.5], [1.5, 1.5]],  # do zadania 1
            [[2.0, 2.5], [2.0, 2.5]],  # do zadania 2
        ],
        [  # Z zadania 2
            [[3.5, 3.0], [3.5, 3.0]],  # do zadania 0
            [[2.5, 2.0], [2.5, 2.0]],  # do zadania 1
            [[2.0, 2.0], [2.0, 2.0]],  # do zadania 2
        ],
    ]


@pytest.fixture
def sample_processing_times():
    """Fixture z przykładowymi czasami przetwarzania.

    Returns:
        list: Czasy przetwarzania dla każdego zadania [job][stage][machine].
    """
    return [
        [[5.0, 6.0], [4.0, 5.0]],  # Zadanie 0
        [[4.0, 5.0], [6.0, 7.0]],  # Zadanie 1
        [[6.0, 7.0], [5.0, 6.0]],  # Zadanie 2
    ]


@pytest.fixture
def sample_job(sample_processing_times, sample_setup_times):
    """Fixture z przykładowym obiektem Job.

    Returns:
        Job: Obiekt zadania z danymi testowymi.
    """
    return Job(
        job_id=0,
        stages=sample_processing_times[0],
        setup_times=sample_setup_times
    )


@pytest.fixture
def sample_machine():
    """Fixture z przykładową maszyną bez efektu uczenia.

    Returns:
        Machine: Obiekt maszyny bez uczenia.
    """
    return Machine(stage_id=0, machine_id=0, is_learning=False)


@pytest.fixture
def sample_learning_machine():
    """Fixture z przykładową maszyną z efektem uczenia.

    Returns:
        Machine: Obiekt maszyny z uczeniem.
    """
    return Machine(stage_id=1, machine_id=0, is_learning=True)


@pytest.fixture
def sample_schedule_data(tmp_path):
    """Fixture z przykładowymi danymi harmonogramu w pliku JSON.

    Args:
        tmp_path: Fixture pytest z tymczasowym katalogiem.

    Returns:
        str: Ścieżka do pliku JSON z danymi.
    """
    data = {
        "num_stages": 2,
        "machines_per_stage": [2, 2],
        "learning_coefficient": 0.3,
        "learning_stages": "01",
        "processing_times": [
            [[5.0, 6.0], [4.0, 5.0]],
            [[4.0, 5.0], [6.0, 7.0]],
            [[6.0, 7.0], [5.0, 6.0]],
        ],
        "setup_times": [
            [
                [[1.0, 1.0], [1.0, 1.0]],
                [[2.0, 2.5], [2.0, 2.5]],
                [[3.0, 3.5], [3.0, 3.5]],
            ],
            [
                [[2.5, 2.0], [2.5, 2.0]],
                [[1.5, 1.5], [1.5, 1.5]],
                [[2.0, 2.5], [2.0, 2.5]],
            ],
            [
                [[3.5, 3.0], [3.5, 3.0]],
                [[2.5, 2.0], [2.5, 2.0]],
                [[2.0, 2.0], [2.0, 2.0]],
            ],
        ],
    }

    file_path = tmp_path / "test_data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    return str(file_path)


@pytest.fixture
def sample_schedule(sample_schedule_data):
    """Fixture z przykładowym obiektem Schedule.

    Args:
        sample_schedule_data: Fixture ze ścieżką do pliku JSON.

    Returns:
        Schedule: Załadowany obiekt harmonogramu.
    """
    schedule = Schedule()
    schedule.load_from_json(sample_schedule_data)
    return schedule


@pytest.fixture
def sample_result_data():
    """Fixture z przykładowymi wynikami algorytmu.

    Returns:
        dict: Wyniki w formacie zgodnym z algorytmami.
    """
    return {
        "C_max": 25.5,
        "time_in_ms": 150.0,
        "Algorithm": "Test Algorithm",
        "schedule": [
            {
                "type": "setup",
                "from_job": 0,
                "to_job": 0,
                "stage": 0,
                "machine": 0,
                "start": 0.0,
                "end": 1.0
            },
            {
                "type": "operation",
                "job": 0,
                "stage": 0,
                "machine": 0,
                "start": 1.0,
                "end": 6.0
            },
        ]
    }


@pytest.fixture
def temp_json_file(tmp_path):
    """Fixture tworzący tymczasowy plik JSON.

    Args:
        tmp_path: Fixture pytest z tymczasowym katalogiem.

    Returns:
        callable: Funkcja zwracająca ścieżkę do pliku JSON.
    """
    def _create_json_file(data, filename="test.json"):
        file_path = tmp_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return str(file_path)

    return _create_json_file


@pytest.fixture
def mock_matplotlib(monkeypatch):
    """Fixture mockujący matplotlib.pyplot dla testów bez GUI.

    Args:
        monkeypatch: Fixture pytest do monkeypatching.
    """
    import matplotlib.pyplot as plt

    def mock_savefig(*args, **kwargs):
        pass

    def mock_show():
        pass

    monkeypatch.setattr(plt, "savefig", mock_savefig)
    monkeypatch.setattr(plt, "show", mock_show)

import csv
import os
from datetime import datetime


def write_csv_log(path: str, fieldnames: list, rows: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class StepClock:
    def __init__(self):
        self._step = 0

    def next(self) -> str:
        self._step += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return f"{now} (step {self._step})"

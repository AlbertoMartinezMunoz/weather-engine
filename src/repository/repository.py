import os
from pathlib import Path


class Repository:
    def __init__(self, path: Path):
        self._path = Path(path)

    def _file_path(self, station_id: str, year: int, month: int) -> Path:
        if not 1 <= month <= 12:
            raise ValueError(f"month must be between 1 and 12, got {month}")
        return self._path / station_id / f"{station_id}.{year:04d}-{month:02d}.json"

    def exists(self, station_id: str, year: int, month: int) -> bool:
        return self._file_path(station_id, year, month).is_file()

    def read_raw(self, station_id: str, year: int, month: int) -> str:
        with self._file_path(station_id, year, month).open("r", encoding="utf-8") as file:
            return file.read()

    def save_raw(self, station_id: str, year: int, month: int, data: str) -> Path:
        file_path = self._file_path(station_id, year, month)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = file_path.with_name(file_path.name + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as file:
            file.write(data)
        os.replace(tmp_path, file_path)

        return file_path

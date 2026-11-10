from pathlib import Path


class Repository:
    def __init__(self, path: Path):
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)

    def save_raw(self, filename: str, data: str) -> None:
        file_path = self._path / filename

        with file_path.open("w", encoding="utf-8") as file:
            file.write(data)

        return file_path

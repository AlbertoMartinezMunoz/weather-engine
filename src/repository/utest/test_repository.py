from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from repository.repository import Repository


@dataclass(frozen=True)
class RepositoryContext:
    path: Path
    filename: str
    repository: Repository
    mkdir_mock: MagicMock
    file_mock: MagicMock


@pytest.fixture
def set_up(mocker):
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    mock_file = mocker.mock_open()
    mocker.patch("pathlib.Path.open", mock_file)
    path = "/raw/file/storage/path"
    yield RepositoryContext(
        path=Path(path),
        filename="file.raw",
        repository=Repository(path=path),
        mkdir_mock=mkdir_mock,
        file_mock=mock_file,
    )


def test_given_repository_when_saving_raw_data_then_return_raw_data_file_path(mocker, set_up):
    expected = str(set_up.path / set_up.filename)
    assert expected == str(set_up.repository.save_raw(filename="file.raw", data="raw file data"))


def test_given_repository_when_saving_raw_data_then_write_raw_data(mocker, set_up):
    set_up.repository.save_raw(filename="file.raw", data="raw file data")
    set_up.mkdir_mock.assert_called_with(parents=True, exist_ok=True)
    set_up.file_mock.assert_called_once_with("w", encoding="utf-8")
    set_up.file_mock().write.assert_called_once_with("raw file data")

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from repository.repository import Repository


@dataclass(frozen=True)
class RepositoryContext:
    path: Path
    repository: Repository
    mkdir_mock: MagicMock
    file_mock: MagicMock
    replace_mock: MagicMock


@pytest.fixture
def set_up(mocker):
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    mock_file = mocker.mock_open()
    mocker.patch("pathlib.Path.open", mock_file)
    replace_mock = mocker.patch("os.replace")
    path = "/raw/file/storage/path"
    yield RepositoryContext(
        path=Path(path),
        repository=Repository(path=path),
        mkdir_mock=mkdir_mock,
        file_mock=mock_file,
        replace_mock=replace_mock,
    )


def test_given_repository_when_saving_raw_data_then_return_raw_data_file_path(mocker, set_up):
    expected = set_up.path / "2422" / "2422.2026-10.json"
    assert expected == set_up.repository.save_raw("2422", 2026, 10, "raw file data")


def test_given_repository_when_saving_raw_data_then_create_station_folder_and_write_data(mocker, set_up):
    set_up.repository.save_raw("2422", 2026, 10, "raw file data")
    set_up.mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)
    set_up.file_mock.assert_called_once_with("w", encoding="utf-8")
    set_up.file_mock().write.assert_called_once_with("raw file data")


def test_given_repository_when_saving_raw_data_then_rename_temp_file_to_final_file(mocker, set_up):
    set_up.repository.save_raw("2422", 2026, 10, "raw file data")
    final = set_up.path / "2422" / "2422.2026-10.json"
    set_up.replace_mock.assert_called_once_with(final.with_name("2422.2026-10.json.tmp"), final)


def test_given_failure_while_writing_when_saving_raw_data_then_do_not_rename_temp_file(mocker, set_up):
    set_up.file_mock().write.side_effect = OSError("disk full")
    with pytest.raises(OSError):
        set_up.repository.save_raw("2422", 2026, 10, "raw file data")
    set_up.replace_mock.assert_not_called()


def test_given_existing_file_when_checking_if_exists_then_check_the_monthly_file(mocker, set_up):
    is_file_mock = mocker.patch("pathlib.Path.is_file", autospec=True, return_value=True)
    assert set_up.repository.exists("2422", 2026, 10) is True
    is_file_mock.assert_called_once_with(set_up.path / "2422" / "2422.2026-10.json")


def test_given_missing_file_when_checking_if_exists_then_return_false(mocker, set_up):
    mocker.patch("pathlib.Path.is_file", return_value=False)
    assert set_up.repository.exists("2422", 2026, 10) is False


def test_given_repository_when_reading_raw_data_then_return_file_content(mocker, set_up):
    mocker.patch("pathlib.Path.open", mocker.mock_open(read_data="[]"))
    assert set_up.repository.read_raw("2422", 2026, 10) == "[]"


@pytest.mark.parametrize("month", [0, 13, -1])
def test_given_invalid_month_when_using_repository_then_raise_value_error(set_up, month):
    with pytest.raises(ValueError):
        set_up.repository.exists("2422", 2026, month)
    with pytest.raises(ValueError):
        set_up.repository.save_raw("2422", 2026, month, "data")

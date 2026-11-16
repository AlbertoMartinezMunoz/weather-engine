import calendar
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import dotenv
import pytest
from pytest_bdd import given, parsers, scenarios, then, when


def find_project_root() -> Path:
    for folder in Path(__file__).resolve().parents:
        if (folder / "scripts" / "acquisition.py").is_file():
            return folder
    raise RuntimeError("Could not find the project root (no scripts/acquisition.py above this file)")


PROJECT_ROOT = find_project_root()
SCRIPT = PROJECT_ROOT / "scripts" / "acquisition.py"
WEATHER_STATION_ID = "2422"

scenarios("features/acquisition.feature")


def dotenv_value(key: str):
    """Value of `key` in the project's .env file (EnvConfig gives it priority over os.environ)."""
    return dotenv.dotenv_values(PROJECT_ROOT / ".env").get(key)


@pytest.fixture(autouse=True)
def require_api_key():
    if not (dotenv_value("AEMET_API_KEY") or os.environ.get("AEMET_API_KEY")):
        pytest.skip("AEMET_API_KEY is not set in the environment or in .env")


@pytest.fixture
def storage(tmp_path) -> Path:
    return tmp_path / "storage"


@pytest.fixture
def env():
    return dict(os.environ)


@pytest.fixture
def result():
    return {}


def store_month(storage: Path, year: int, month: int, content: str = "[]") -> None:
    path = storage / WEATHER_STATION_ID / f"{WEATHER_STATION_ID}.{year:04d}-{month:02d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def months_between(first: str, last: str):
    year, month = map(int, first.split("-"))
    end_year, end_month = map(int, last.split("-"))
    while (year, month) <= (end_year, end_month):
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def run_script(result, env, *arguments) -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=False,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    result["completed"] = completed


# --- Given ---------------------------------------------------------------


@given("an empty temporary storage folder")
def empty_storage(storage):
    assert not storage.exists()


@given(parsers.parse("the station {station_id} is configured"))
def station_configured(env, station_id):
    configured = dotenv_value("WEATHER_STATION_ID")
    if configured and configured != station_id:
        pytest.skip(f".env defines WEATHER_STATION_ID={configured} and takes priority over the environment")
    env["WEATHER_STATION_ID"] = station_id


@given(parsers.parse('the API key "{api_key}" is configured'))
def api_key_configured(env, api_key):
    if dotenv_value("AEMET_API_KEY"):
        pytest.skip(".env defines AEMET_API_KEY and takes priority over the environment")
    env["AEMET_API_KEY"] = api_key


@given(parsers.parse('the month "{month}" is already stored with the content "{content}"'))
def month_already_stored(storage, month, content):
    year, mon = map(int, month.split("-"))
    store_month(storage, year, mon, content)


@given(parsers.parse('every month from "{first}" to "{last}" is already stored'))
def months_already_stored(storage, first, last):
    for year, month in months_between(first, last):
        store_month(storage, year, month)


# --- When ----------------------------------------------------------------


@when(parsers.parse('I download the month "{month}"'))
def download_month(result, env, storage, month):
    run_script(result, env, "-p", str(storage), "-m", month)


@when("I download without specifying a month")
def download_without_month(result, env, storage):
    run_script(result, env, "-p", str(storage))


@when("I download the current month")
def download_current_month(result, env, storage):
    run_script(result, env, "-p", str(storage), "-m", date.today().strftime("%Y-%m"))


@when("I run the download script without arguments")
def run_without_arguments(result, env):
    run_script(result, env)


# --- Then ----------------------------------------------------------------


@then(parsers.parse("the download exits with code {code:d}"))
def exits_with_code(result, code):
    completed = result["completed"]
    assert completed.returncode == code, f"stdout: {completed.stdout}\nstderr: {completed.stderr}"


@then(parsers.parse('the file "{relative_path}" exists in the storage folder'))
def file_exists(storage, relative_path):
    assert (storage / relative_path).is_file()


@then(parsers.parse('the file holds valid daily records of station "{station_id}" for the month "{month}"'))
def file_holds_valid_records(storage, station_id, month):
    year, mon = map(int, month.split("-"))
    path = storage / station_id / f"{station_id}.{month}.json"
    records = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(records, list)
    assert 1 <= len(records) <= calendar.monthrange(year, mon)[1]
    assert {r["indicativo"] for r in records} == {station_id}
    assert all(r["fecha"].startswith(month) for r in records)
    assert len({r["fecha"] for r in records}) == len(records)  # one record per day


@then(parsers.parse('the file "{relative_path}" still has the content "{content}"'))
def file_keeps_content(storage, relative_path, content):
    assert (storage / relative_path).read_text(encoding="utf-8") == content


@then(parsers.parse("the storage folder holds {count:d} files"))
def storage_holds_files(storage, count):
    files = [p for p in storage.rglob("*") if p.is_file()] if storage.exists() else []
    assert len(files) == count, sorted(p.name for p in files)[-5:]


@then(parsers.parse('the output mentions "{message}"'))
def output_mentions(result, message):
    assert message in result["completed"].stdout


@then(parsers.parse('the error output mentions "{message}"'))
def error_output_mentions(result, message):
    assert message in result["completed"].stderr

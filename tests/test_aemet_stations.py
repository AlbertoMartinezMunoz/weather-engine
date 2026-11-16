import ast
import shlex
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))
import pytest
from pytest_bdd import parsers, scenarios, then, when

from envconfig.envconfig import EnvConfig

SCRIPT = PROJECT_ROOT / "scripts" / "aemet_stations.py"

scenarios("features/aemet_stations.feature")


@pytest.fixture(autouse=True)
def require_api_key():
    if not EnvConfig().get("AEMET_API_KEY"):
        pytest.skip("AEMET_API_KEY is not set")


@pytest.fixture
def result():
    return {}


@when(parsers.parse('I run the script live with "{arguments}"'))
def run_script_live(result, arguments):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *shlex.split(arguments)],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    result["completed"] = completed


def stations(result) -> list[dict]:
    lines = result["completed"].stdout.splitlines()
    return [ast.literal_eval(line) for line in lines if line.strip()]


@then(parsers.parse("the live script exits with code {code:d}"))
def exits_with_code(result, code):
    completed = result["completed"]
    assert completed.returncode == code, completed.stderr


@then("the live script exits with an error")
def exits_with_error(result):
    assert result["completed"].returncode != 0


@then(parsers.parse("the live script prints {count:d} stations"))
def prints_stations(result, count):
    assert len(stations(result)) == count


@then("the printed distances are sorted ascending")
def distances_sorted(result):
    distances = [s["distance_km"] for s in stations(result)]
    assert distances == sorted(distances)


@then(parsers.parse("the closest printed station is less than {km:d} km away"))
def closest_is_near(result, km):
    assert stations(result)[0]["distance_km"] < km


@then("the live error output mentions an AEMET failure")
def error_mentions_aemet(result):
    stderr = result["completed"].stderr
    assert "AEMET error" in stderr or "401" in stderr

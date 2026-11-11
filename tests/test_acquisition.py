import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when


def empty_to_none(value):
    return None if value.strip() == "" else value


@pytest.fixture
def script_params():
    return {}


@scenario("features/acquisition.feature", "Script Parameters Integrity")
def test_script_parameters_integrity():
    pass


@scenario("features/acquisition.feature", "Data is Stored at Output Path")
def test_data_is_stored_at_output_path():
    pass


@given(parsers.re("output path is (?P<path>.*?)"), converters={"path": empty_to_none})
def set_output_path(tmp_path, script_params, path):
    if path:
        script_params["--output-dir"] = str(tmp_path / path)
    else:
        script_params["--output-dir"] = path


@given(parsers.re("start date is (?P<date>.*?)"), converters={"date": empty_to_none})
def set_start_date(script_params, date):
    script_params["--start-date"] = date


@given(parsers.re("end date is (?P<date>.*?)"), converters={"date": empty_to_none})
def set_end_date(script_params, date):
    script_params["--end-date"] = date


@given(parsers.parse("configuration file path is {path}"))
def set_config_path(script_params, path):
    script_params["--config"] = path


@when("the acquisition script is launched", target_fixture="script_result")
def run_script(script_params):
    command = ["python", "./scripts/acquisition.py"]
    if script_params.get("--output-dir"):
        command.append("-o=" + script_params["--output-dir"])
    if script_params.get("--start-date"):
        command.append("-s=" + script_params["--start-date"])
    if script_params.get("--end-date"):
        command.append("-e=" + script_params["--end-date"])
    if script_params.get("--config"):
        command.append("-c=" + script_params["--config"])

    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


@then(parsers.re("an (?P<error>.*?) error is notified"))
def missing_output_path_error(script_result, error):
    script_error = script_result.stderr.strip().splitlines()[-1]
    assert script_error == "acquisition.py: error: the following arguments are required: " + error


@then("a date ordering error is notified")
def date_ordering_error(script_result):
    script_error = script_result.stderr.strip().splitlines()[-1]
    assert script_error == "Error: Start date cannot be later than end date."


@then("the script returns success")
def script_returns_success(script_result):
    assert script_result.returncode == 0


@then("data is stored at output path")
def data_is_stored_at_output_path(script_params, script_result):
    f = Path(script_params["--output-dir"]) / ("raw/aemet/" + script_params["--start-date"] + ".raw")
    assert f.exists()
    assert f.read_text() == "Datos de prueba " + script_params["--start-date"]

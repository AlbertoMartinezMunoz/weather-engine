import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, then, when


def empty_to_none(value):
    return None if value.strip() == "" else value


@pytest.fixture
def script_params():
    return {}


@scenario("features/envconfig.feature", "Script Parameters Integrity")
def test_script_parameters_integrity():
    pass


@scenario("features/envconfig.feature", "Env Config Get Key")
def test_envconfig_get_key():
    pass


@scenario("features/envconfig.feature", "Env Config Get Bad Key")
def test_envconfig_get_bad_key():
    pass


@given(parsers.re("env file path is (?P<path>.*?)"), converters={"path": empty_to_none})
def set_env_file_path(script_params, path):
    script_params["--env-file"] = path


@given(parsers.re("env key is (?P<key>.*?)"), converters={"key": empty_to_none})
def set_env_key(script_params, key):
    script_params["--key"] = key


@when("the envconfig script is launched", target_fixture="script_result")
def run_script(script_params):
    command = ["python", "./scripts/envconfig.py"]
    if script_params.get("--env-file"):
        command.append("-e=" + script_params["--env-file"])
    if script_params.get("--key"):
        command.append("-k=" + script_params["--key"])

    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


@then(parsers.re("an (?P<error>.*?) error is notified"))
def missing_output_path_error(script_result, error):
    script_error = script_result.stderr.strip().splitlines()[-1]
    assert script_error == "envconfig.py: error: the following arguments are required: " + error


@then("the script returns success")
def script_returns_success(script_result):
    assert script_result.returncode == 0


@then("the script fails")
def script_fails(script_result):
    assert script_result.returncode == 1


@then(parsers.re("the script returns (?P<key>.*?) and (?P<value>.*?)"))
def script_returns_key_and_value(script_result, key, value):
    expected = f"{key}='{value}'"
    output = script_result.stdout[:-1]
    assert expected == output


@then(parsers.re("the script returns (?P<key>.*?) not found error"))
def bad_key_error(script_params, script_result, key):
    path = Path(script_params["--env-file"])
    script_error = script_result.stderr.strip().splitlines()[-1]
    assert script_error == f"Error: No '{key}' key found. Check your .env file ({path})."

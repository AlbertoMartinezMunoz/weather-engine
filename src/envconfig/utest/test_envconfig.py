import re
from dataclasses import dataclass

import pytest

from envconfig.envconfig import EnvConfig


@dataclass(frozen=True)
class EnvConfigContext:
    env_path: str
    expected: dict
    envconfig: EnvConfig


@pytest.fixture
def set_up(mocker):
    dict = {
        "KEY": "value",
    }
    env_path = "./dummy/path"

    mocker.patch("dotenv.find_dotenv")
    mocker.patch("dotenv.dotenv_values", return_value=dict)

    yield EnvConfigContext(env_path=env_path, envconfig=EnvConfig(path=env_path), expected=dict)


def test_given_env_configuration_when_getting_key_then_value_is_returned(set_up):
    assert set_up.expected["KEY"] == set_up.envconfig.get("KEY")


def test_given_env_configuration_when_getting_new_key_then_exception_is_raised(set_up):
    key = "BAD_KEY"
    expected_message = f"No '{key}' key found. Check your .env file ({set_up.env_path})."

    with pytest.raises(ValueError, match=re.escape(expected_message)):
        set_up.envconfig.get(key)

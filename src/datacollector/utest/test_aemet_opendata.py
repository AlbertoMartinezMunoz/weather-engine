import json
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
import requests

from datacollector.aemet_opendata import AemetOpenDataClient

API_KEY = "secret-key"
DATA_URL = "https://opendata.aemet.es/opendata/sh/abc123"
BASE_URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos"


@dataclass(frozen=True)
class ClientContext:
    client: AemetOpenDataClient
    get_mock: MagicMock


def response(payload) -> MagicMock:
    fake = MagicMock()
    fake.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return fake


@pytest.fixture
def set_up(mocker):
    get_mock = mocker.patch("requests.get")
    yield ClientContext(
        client=AemetOpenDataClient(api_key=API_KEY),
        get_mock=get_mock,
    )


@pytest.mark.parametrize(
    "year, month, last_day",
    [(2026, 10, 31), (2026, 2, 28), (2024, 2, 29)],
)
def test_given_client_when_fetching_month_then_request_the_whole_month_of_the_station(set_up, year, month, last_day):
    set_up.get_mock.side_effect = [response({"estado": 200, "datos": DATA_URL}), response([])]
    set_up.client.fetch_month("2422", year, month)
    expected_url = (
        f"{BASE_URL}/fechaini/{year}-{month:02d}-01T00:00:00UTC"
        f"/fechafin/{year}-{month:02d}-{last_day:02d}T23:59:59UTC/estacion/2422"
    )
    assert set_up.get_mock.call_args_list[0] == ((expected_url,), {"headers": {"api_key": API_KEY}, "timeout": 30})


def test_given_successful_metadata_when_fetching_month_then_request_the_data_url_with_api_key(set_up):
    set_up.get_mock.side_effect = [response({"estado": 200, "datos": DATA_URL}), response([])]
    set_up.client.fetch_month("2422", 2026, 10)
    assert set_up.get_mock.call_count == 2
    assert set_up.get_mock.call_args_list[1] == ((DATA_URL,), {"headers": {"api_key": API_KEY}, "timeout": 30})


def test_given_successful_metadata_when_fetching_month_then_return_the_daily_records(set_up):
    records = [{"fecha": "2026-10-01", "tmax": "21,5"}, {"fecha": "2026-10-02", "tmax": "19,0"}]
    set_up.get_mock.side_effect = [response({"estado": 200, "datos": DATA_URL}), response(records)]
    assert set_up.client.fetch_month("2422", 2026, 10) == records


def test_given_accents_in_the_data_when_fetching_month_then_decode_them_as_utf8(set_up):
    records = [{"nombre": "ÁVILA", "provincia": "ÁVILA"}]
    set_up.get_mock.side_effect = [response({"estado": 200, "datos": DATA_URL}), response(records)]
    assert set_up.client.fetch_month("2422", 2026, 10) == records


def test_given_no_data_for_the_month_when_fetching_month_then_return_empty_list(set_up):
    set_up.get_mock.side_effect = [response({"estado": 404, "descripcion": "No hay datos"})]
    assert set_up.client.fetch_month("2422", 2026, 10) == []


def test_given_no_data_for_the_month_when_fetching_month_then_do_not_request_the_data_url(set_up):
    set_up.get_mock.side_effect = [response({"estado": 404, "descripcion": "No hay datos"})]
    set_up.client.fetch_month("2422", 2026, 10)
    set_up.get_mock.assert_called_once()


@pytest.mark.parametrize("estado", [401, 429, 500])
def test_given_unexpected_status_when_fetching_month_then_raise_runtime_error(set_up, estado):
    set_up.get_mock.side_effect = [response({"estado": estado, "descripcion": "error"})]
    with pytest.raises(RuntimeError, match="AEMET error"):
        set_up.client.fetch_month("2422", 2026, 10)


def test_given_missing_status_when_fetching_month_then_raise_runtime_error(set_up):
    set_up.get_mock.side_effect = [response({"descripcion": "unexpected body"})]
    with pytest.raises(RuntimeError):
        set_up.client.fetch_month("2422", 2026, 10)


def test_given_http_error_on_metadata_when_fetching_month_then_propagate_it_without_requesting_data(set_up):
    failing = MagicMock()
    failing.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")
    set_up.get_mock.side_effect = [failing]
    with pytest.raises(requests.HTTPError):
        set_up.client.fetch_month("2422", 2026, 10)
    set_up.get_mock.assert_called_once()


def test_given_http_error_on_data_when_fetching_month_then_propagate_it(set_up):
    failing = MagicMock()
    failing.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    set_up.get_mock.side_effect = [response({"estado": 200, "datos": DATA_URL}), failing]
    with pytest.raises(requests.HTTPError):
        set_up.client.fetch_month("2422", 2026, 10)

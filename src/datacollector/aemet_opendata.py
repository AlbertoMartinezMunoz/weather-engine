import calendar
import json

import requests

BASE_URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos"


class AemetOpenDataClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _get_json(self, url, api_key):
        resp = requests.get(url, headers={"api_key": api_key}, timeout=30)
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8", errors="replace"))

    def fetch_month(self, station_id, year, month):
        last_day = calendar.monthrange(year, month)[1]
        url = (
            f"{BASE_URL}/fechaini/{year}-{month:02d}-01T00:00:00UTC"
            f"/fechafin/{year}-{month:02d}-{last_day:02d}T23:59:59UTC/estacion/{station_id}"
        )

        # AEMET answers with a JSON containing the real data URL in "datos"
        meta = self._get_json(url, self._api_key)
        if meta.get("estado") == 404:
            return []
        if meta.get("estado") != 200:
            raise RuntimeError(f"AEMET error: {meta}")
        return self._get_json(meta["datos"], self._api_key)

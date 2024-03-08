import time
from typing import Union
from redis import Redis


class RedisClient:
    def __init__(self, host: str, port: int = 6379, *args, **kwargs):
        self._rds = Redis(host=host, port=port)
        self._ts = self._rds.ts()


    def get_current_temperature(self) -> Union[float, None]:
        val = self._ts.get('temp')
        return float(val[1]) if val else None


    def get_current_pressure(self) -> Union[float, None]:
        val = self._ts.get('pres')
        return float(val[1]) if val else None


    def get_temperature_series_three_hours(self) -> list[tuple[int, float]]:
        now = round(time.time() * 1000)
        three_hours_ago = now - (3*60*60*1000)

        return self._ts.range('temp', three_hours_ago, now)


    def get_pressure_series_three_hours(self) -> list[tuple[int, float]]:
        """gets pressure series as list of unix timestamp (millis) and floats from three hours until now
        """
        now = round(time.time() * 1000) # millis
        three_hours_ago = now - (3*60*60*1000)

        return self._ts.range('pres', three_hours_ago, now)


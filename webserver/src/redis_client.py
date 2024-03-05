import time
from redis import Redis


class RedisClient:
    def __init__(self, host: str, port: int = 6379, *args, **kwargs):
        self._rds = Redis(host=host, port=port)
        self._ts = self._rds.ts()

    def get_current_temperature(self) -> float:
        return float(self._ts.get('temp')[1])

    def get_current_pressure(self) -> float:
        return float(self._ts.get('pres')[1])

    def get_pressure_series_three_hours(self) -> list[tuple[int, float]]:
        """gets pressure series as list of unix timestamp (millis) and floats from three hours until now
        """
        now = round(time.time() * 1000) # millis
        three_hours_ago = now - (3*60*60*1000)

        return self._ts.range('pres', three_hours_ago, now)

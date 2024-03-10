import time
from typing import Union
from redis import Redis


class RedisClient:
    def __init__(self, host: str, port: int = 6379, prefix: str = '', *args, **kwargs):
        self._rds = Redis(host=host, port=port)
        self._ts = self._rds.ts()
        self._prefix = prefix

    def set_prefix(self, prefix: str) -> None:
        self._prefix = prefix


    def get_current_temperature(self) -> Union[float, None]:
        val_dht = self._ts.get(self._prefix + ':dht12:temp')
        val_bmp = self._ts.get(self._prefix + ':bmp280:temp')

        if None in (val_dht, val_bmp):
            return float((val_dht or val_bmp)[1]) if val_dht or val_bmp else None

        return (float(val_dht)+float(val_bmp))/2


    def get_current_pressure(self) -> Union[float, None]:
        val = self._ts.get(self._prefix + ':bmp280:press')
        return float(val[1]) if val else None


    def get_current_humidity(self) -> Union[float, None]:
        val = self._ts.get(self._prefix + ':dht12:humi')
        return float(val[1]) if val else None


    def get_pressure_series_three_hours(self) -> list[tuple[int, float]]:
        """gets pressure series as list of unix timestamp (millis) and floats from three hours until now
        """
        now = round(time.time() * 1000) # millis
        three_hours_ago = now - (3*60*60*1000)

        return self._ts.range(self._prefix + ':bmp280:press', three_hours_ago, now)


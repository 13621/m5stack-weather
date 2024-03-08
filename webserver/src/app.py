import json
import io
import os
import base64

from flask import Flask, render_template
from .redis_client import RedisClient
from .weather_calc import WeatherForecast, ZAMBRETTI_VALUES


app = Flask(__name__)
rdscl = RedisClient(os.environ.get("REDIS_HOSTNAME"), int(os.environ.get("REDIS_PORT")))


@app.route('/')
def root():
    curtemp = rdscl.get_current_temperature()

    fc = WeatherForecast(elevation=22,
                         temperature=curtemp,
                         pressure_series=rdscl.get_pressure_series_three_hours())

    forecast, _ = fc.get_forecast()

    return render_template('root.html',
                           pres=fc.pressure,
                           temp=curtemp,
                           forecast=forecast)


@app.route('/info')
def info():
    fc = WeatherForecast(elevation=22,
                         temperature=rdscl.get_current_temperature(),
                         pressure_series=rdscl.get_pressure_series_three_hours())

    forecast, zambretti_number = fc.get_forecast()

    zambretti_table = [] # [('steady', 0, 'fine'), ...]

    for p in ZAMBRETTI_VALUES.keys():
        for z in ZAMBRETTI_VALUES[p].keys():
            zambretti_table.append((p, z, ZAMBRETTI_VALUES[p][z]))

    zambretti_table.sort(key=lambda x: x[1])

    graph_rgb_b64 = base64.b64encode(fc.get_pressure_graph()).decode('ascii')

    return render_template('info.html',
                           pres=fc.pressure_sealevel,
                           temp=fc.temperature,
                           forecast=forecast,
                           zambretti_number=zambretti_number,
                           zambretti_table=zambretti_table,
                           plot=graph_rgb_b64)


def main():
    app.run()


if __name__ == '__main__':
    main()

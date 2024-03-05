import json
import io
import base64

from flask import Flask, render_template
from .redis_client import RedisClient
from .weather_calc import WeatherForecast


app = Flask('app')


@app.route('/')
def root():
    cl = RedisClient('localhost')

    curtemp = cl.get_current_temperature()
    curpres = cl.get_current_pressure()
    pres_series = cl.get_pressure_series_three_hours()

    fc = WeatherForecast(elevation=22,
                         temperature=curtemp,
                         pressure_series=pres_series)

    forecast, zambretti_number = fc.get_forecast()

    graph_rgb_b64 = base64.b64encode(fc.get_pressure_graph()).decode('ascii')

    return render_template('weather.html', pres=curpres, temp=curtemp, forecast=forecast, zambretti_number=zambretti_number, plot=graph_rgb_b64)

if __name__ == '__main__':
    app.run()

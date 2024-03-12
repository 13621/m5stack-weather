import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from datetime import datetime


ZAMBRETTI_VALUES = {
    'steady': {
        10: 'Settled Fine',
        11: 'Fine Weather',
        12: 'Fine, Possibly Showers',
        13: 'Fairly Fine, Showers Likely',
        14: 'Showery, Bright Intervals',
        15: 'Changeable, Some Rain',
        16: 'Unsettled, Rain At Times',
        17: 'Rain at Frequent Intervals',
        18: 'Very Unsettled, Rain',
        19: 'Stormy, Much Rain',
    },
    'rising': {
        20: 'Settled Fine',
        21: 'Fine Weather',
        22: 'Becoming Fine',
        23: 'Fairly Fine, Improving',
        24: 'Fairly Fine, Possibly Showers Early',
        25: 'Showery Early, Improving',
        26: 'Changeable, Mending',
        27: 'Rather Unsettled, Clearing Later',
        28: 'Unsettled, Probably Improving',
        29: 'Unsettled, Short Fine Intervals',
        30: 'Very Unsettled, Finer at Times',
        31: 'Stormy, Possibly Improving',
        32: 'Stormy, Much Rain',
    },
    'falling': {
        1: 'Settled Fine',
        2: 'Fine Weather',
        3: 'Fine, Becoming Less Settled',
        4: 'Fairly Fine, Showery Later',
        5: 'Showery, Becoming More Unsettled',
        6: 'Unsettled, Rain Later',
        7: 'Rain at Times, Worse Later',
        8: 'Rain at Times, Becoming Very Unsettled',
        9: 'Very Unsettled, Rain',
    },
    'unknown': {
        0: 'Unknown',
    },
}

ZAMBRETTI_CALC_FACTORS = {
    'falling': (127, 0.12),
    'steady': (144, 0.13),
    'rising': (185, 0.16),
    'unknown': (0, 0),
}


class WeatherForecast:
    def __init__(self, elevation: int, temperature: int, pressure_series: list[tuple[int, float]]):
        self.elevation = elevation if elevation else None
        self.temperature = self._get_temp_kelvin(temperature) if temperature else None
        self.pressure = pressure_series[-1][1] if len(pressure_series) > 1 else None
        self.pressure_series = pressure_series
        self.pressure_sealevel = self._get_pres_sealevel(self.pressure, self.temperature, self.elevation) \
            if self.pressure and self.temperature and self.elevation else None

    @staticmethod
    def _get_temp_kelvin(temp_c: float) -> float:
        return temp_c + 273.15

    @staticmethod
    def _get_pres_sealevel(pres: float, temp: float, height: float) -> float:
        return pres * pow(( 1 - (0.0065*height)/(temp + 0.0065*height) ), -5.257)

    def pressure_linear_regressed_function_coefs(self):
        if not getattr(self, '_pressure_coefs', None):
            x, y = zip(*self.pressure_series)
            self._pressure_coefs = list(np.polyfit(x, y, 1))
        return self._pressure_coefs

    def get_pressure_graph(self):
        # scatter plot
        x, y = zip(*self.pressure_series)
        fig, ax = plt.subplots()
        ax.scatter(x, y, s=1)

        # regression line
        xseq = np.arange(x[0], x[-1], 1000)
        fc = np.poly1d(self.pressure_linear_regressed_function_coefs())
        ax.plot(xseq, fc(xseq), c=(1.0, 0.0, 0.0))

        ax.set(xlabel='unix timestamp (millis)', 
               ylabel='air pressure (mbar)',
               title='Measured air pressure over time')
        ax.grid()

        output = io.BytesIO()
        fig.canvas.print_png(output)

        return output.getvalue()

    def get_pressure_trend(self) -> str:
        diff = self.pressure_linear_regressed_function_coefs()[0] *3*60*60*1000 # slope of function over 3 hours

        if 1050 > self.pressure_sealevel > 985 and diff <= -1.6:
            # between values and fall of 1.6 mbar
            return 'falling'

        if 1030 > self.pressure_sealevel > 947 and diff >= 1.6:
            return 'rising'

        if 1033 > self.pressure_sealevel > 960:# and (diff < 1.6 or diff > -1.6):
            return 'steady'

        return 'unknown'

    def get_forecast(self) -> tuple[str, int]:
        factor_a, factor_b = ZAMBRETTI_CALC_FACTORS[self.get_pressure_trend()]
        zambretti_number = round(factor_a - factor_b*self.pressure_sealevel)

        forecast = ZAMBRETTI_VALUES[self.get_pressure_trend()][zambretti_number]

        return forecast, zambretti_number

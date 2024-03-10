import time
import os

import numpy as np

from random import randint
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion

def on_connect(client, userdata, flags, rc, *args):
    print(f"connected ({rc})")


def main():
    client = Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    client.username_pw_set(username=os.environ.get("MQTT_USERNAME"),
                           password=os.environ.get("MQTT_PASSWORD"))

    client.connect(str(os.environ.get("MQTT_HOSTNAME")))

    pressure_function_coefs = [ ((randint(-2, 2) / 10) / (3*60*60*100)), randint(960, 1050) ]
    pressure_function = np.poly1d(pressure_function_coefs) # ex. -9e-9x + 1040
    print(f"Chose {str(pressure_function)} as function!")

    begin_time = time.time()

    while True:
        now_time_ms = (time.time() - begin_time) * 1000
        proj_pressure = pressure_function(now_time_ms)

        topics = ('niclasjann/bmp280/temp', 
                  'niclasjann/bmp280/press', 
                  'niclasjann/dht12/temp',
                  'niclasjann/dht12/humi')
        payloads = (randint(-5, 30), 
                    proj_pressure,
                    randint(-5, 30),
                    randint(0, 100))

        for i, t in enumerate(topics):
            client.publish(t, payloads[i])
            time.sleep(randint(0, 10) / 10)
        time.sleep(randint(0, 2))


if __name__ == '__main__':
    main()

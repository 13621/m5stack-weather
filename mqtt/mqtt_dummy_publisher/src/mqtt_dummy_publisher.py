import time
import os

from random import randint
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion

def on_connect(client, userdata, flags, rc, *args):
    print(f"connected ({rc})")


def main():
    client = Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    #client.username_pw_set(username=str(os.environ.get("MQTT_USERNAME")),
    #                       password=str(os.environ.get("MQTT_PASSWORD")))

    client.username_pw_set(username='testuser',
                           password='m8zjQgeXw$62Pbz8zvWFAUrpcatkTB^3f$pLAma%Erh7&q*M')

    client.connect(str(os.environ.get("MQTT_HOSTNAME")))

    while True:
        topics = ('test/temp', 'test/pres')
        payloads = (randint(-5, 30), randint(960, 1050))
        for i, t in enumerate(topics):
            client.publish(t, payloads[i])
            print("published", payloads[i], "in topic", t)
        time.sleep(randint(0, 2))


if __name__ == '__main__':
    main()

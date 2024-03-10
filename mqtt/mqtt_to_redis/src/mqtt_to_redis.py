import time
import os

from paho.mqtt.client import Client 
from paho.mqtt.enums import CallbackAPIVersion

from redis import Redis


def on_connect(client, userdata, flags, rc, *args):
    print(f"connected to MQTT ({rc})")
    client.subscribe('+/#')

def on_message(client, userdata, msg, timeseries, *args):
    current_unix_timestamp = time.time()
    
    ts_key = ":".join(msg.topic.split('/'))
    value = float(msg.payload)

    try:
        ts.create(ts_key, retention_msecs=3*60*60*1000)
    except:
        pass

    timeseries.add(ts_key, "*", value, duplicate_policy='LAST')


def main():
    rds = Redis(host=str(os.environ.get("REDIS_HOSTNAME")), port=int(os.environ.get("REDIS_PORT")))
    ts = rds.ts()

    client = Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = lambda *args: on_message(*args, timeseries=ts)

    client.username_pw_set(username=os.environ.get("MQTT_USERNAME"),
                           password=os.environ.get("MQTT_PASSWORD"))

    client.connect(str(os.environ.get("MQTT_HOSTNAME")))

    client.loop_forever()


if __name__ == '__main__':
    main()

import time

from paho.mqtt.client import Client 
from paho.mqtt.enums import CallbackAPIVersion

from redis import Redis


def on_connect(client, userdata, flags, rc, *args):
    print(f"connected ({rc})")
    client.subscribe('test/+')

def on_message(client, userdata, msg, timeseries, *args):
    current_unix_timestamp = time.time()
    print("received:", msg.payload, "topic:", msg.topic)
    
    ts_key = msg.topic.split('/')[1]
    value = float(msg.payload)

    timeseries.add(ts_key, "*", value, duplicate_policy='LAST')
    print("added:", ts.get(ts_key))


def main():
    rds = Redis(host='localhost', port=6379)
    ts = rds.ts()
    try:
        [ts.create(t, retention_msecs=3*60*60*1000) for t in ('temp', 'pres')]
    except:
        pass

    client = Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = lambda *args: on_message(*args, timeseries=ts)

    client.username_pw_set(username='testuser',
                       password='m8zjQgeXw$62Pbz8zvWFAUrpcatkTB^3f$pLAma%Erh7&q*M')

    print("connecting...")
    client.connect('212.227.171.44')

    client.loop_forever()


if __name__ == '__main__':
    main()

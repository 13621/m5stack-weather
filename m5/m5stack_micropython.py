from m5stack import *
from m5ui import *
from uiflow import *
from m5mqtt import M5mqtt
from machine import Pin, I2C
import sys
import bmp280


MQTT_HOSTNAME = "fixme"
MQTT_PORT = 1883
MQTT_USERNAME = "fixme"
MQTT_PASSWORD = "fixme"

setScreenColor(0x222222)

speaker.setVolume(0.1)
speaker.sing(220, 1)

data = bytearray(5)

temp_label = M5TextBox(30, 20, "TEMP", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
humi_label = M5TextBox(30, 60, "HUMI", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
bmp_temp_label = M5TextBox(30, 100, "TEMPBMP", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
press_label = M5TextBox(30, 140, "PRESS", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)
version_label = M5TextBox(30, 180, "VERSION", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)

version_label.setText('v'+sys.version)

i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
bmp = bmp280.BMP280(i2c)

m5mqtt = M5mqtt('board', MQTT_HOSTNAME, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, 300)
m5mqtt.start()

mqttbasetopic = 'niclasjann'

while True:
  # DHT12 TEMPERATURE, HUMIDITY
  data = i2c.readfrom_mem(0x5c, 0x00, 5)
  # |   0x00  |  0x01   |   0x02  |   0x03  |   0x04  | 
  # | hum_int | hum_dec | temp_int| temp_dec| checksum|

  if sum(data[:-1]) == data[-1]:
    # checksum matches, proceed
    temp = data[2] + data[3] * 0.1 # 0x02+0x03
    hum = data[0] + data[1] * 0.1 # 0x00#0x01

    temp_label.setText(str(temp) + ' C')
    humi_label.setText(str(hum) + ' %')
  
    m5mqtt.publish(mqttbasetopic +  '/dht12/temp', str(temp))
    m5mqtt.publish(mqttbasetopic + '/dht12/humi', str(hum))

  # BMP280 TEMPERATURE, PRESSURE
  bmp_temp, bmp_press = bmp.values

  bmp_temp_label.setText(str(bmp_temp)+' C')
  press_label.setText(str(bmp_press)+' hPa')

  m5mqtt.publish(mqttbasetopic + '/bmp280/temp', str(bmp_temp))
  m5mqtt.publish(mqttbasetopic + '/bmp280/press', str(bmp_press))
 
  wait_ms(5000)

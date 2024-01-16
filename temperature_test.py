import dht12
from machine import I2C, Pin


lcd.clear()

scl = Pin(22, Pin.OUT, Pin.PULL_UP)
sda = Pin(21, Pin.OUT, Pin.PULL_UP)

i2c = I2C(scl=scl, sda=sda)

dhti2c = dht12.DHTBaseI2C(i2c, 0x5c)
dhti2c.measure() # schlägt fehl

sensor = dht12.DHT12(dhti2c)

lcd.text(80, 80, str(sensor.temperature()), lcd.WHITE)

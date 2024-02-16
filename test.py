import machine, onewire, ds18x20, time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import network
import socket
import freesans20
import writer

""" Set up OLED """
WIDTH = 128
HEIGHT = 64

i2c = I2C(1, scl = Pin(3), sda = Pin(2), freq = 200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)


ds_pin = machine.Pin(16)
 
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
 
roms = ds_sensor.scan()
 
print('Found DS devices: ', roms)
 
def write_to_oled(temp):
    oled.fill(0)
    oled.text("TEMP", 0, 0)
    oled.text(str(temp), 0, 40)
    oled.show() 

while True:
 
  ds_sensor.convert_temp()
 
  time.sleep_ms(750)
 
  for rom in roms:
 
    tnum = round(ds_sensor.read_temp(rom), 2)
    print(tnum, " Celsius")
    write_to_oled(tnum)

  
 
  time.sleep(1)
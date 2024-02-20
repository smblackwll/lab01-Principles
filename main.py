from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep, sleep_ms
import network
import umail
import onewire
import ds18x20

""" Set up network connection """

# DeviceNet info
ssid = 'UI-DeviceNet'
password = 'UI-DeviceNet'

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Network connection failed.')
    else:
        print('Connected.')
        status = wlan.ifconfig()

""" Set up buttons """

button1 = Pin(9)
button2 = Pin(13)

""" Set up OLED """

WIDTH = 128
HEIGHT = 64

i2c = I2C(1, scl = Pin(3), sda = Pin(2), freq = 200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def write_to_oled(sensor_one_status, sensor_two_status, sensor_one_temp, sensor_two_temp):
    # Convert temps to fahrenheit
    #   sensor_one_fahrenheit = (sensor_one_temp * (9/5)) + 32
    #   sensor_two_fahrenheit = (sensor_two_temp * (9/5)) + 32

    oled.fill(0)
    oled.text("Sensor 01: " + str(sensor_one_status), 0, 5)
    oled.text("Sensor 02: " + str(sensor_two_status), 0, 35)
    if sensor_one_status == "OFF":
        oled.text("Temp: Not avail", 0, 15)
    else:
        oled.text("Temp: " + str(sensor_one_temp) + " C", 0, 15)
    if sensor_two_status == "OFF":
        oled.text("Temp: Not avail", 0, 45)
    else:
        oled.text("Temp: " + str(sensor_two_temp) + " C", 0, 45)
    oled.show()   
    sleep(0.1)

""" Set up DS18B20 """

ds_pin = Pin(16)
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
print('Found DS18B20 sensor with address: ', roms)

""" MAIN """
connect_to_wifi(ssid, password)

while True:
    ds.convert_temp()
    sleep_ms(10)
    # Button 1 is pressed, temp sensor 1 turned on. 
    if button1.value() == 0:
        sensor_one_status = "ON"
        sensor_one_temp = round(ds.read_temp(roms[0]), 1)
    else: 
        sensor_one_status = "OFF"
        
    if button2.value() == 0:
        sensor_two_status = "ON"
        sensor_two_temp = round(ds.read_temp(roms[1]), 1)
    else: 
        sensor_two_status = "OFF"

    write_to_oled(sensor_one_status, sensor_two_status, sensor_one_temp, sensor_two_temp)
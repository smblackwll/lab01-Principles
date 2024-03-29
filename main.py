from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep, sleep_ms
import network
import onewire
import ds18x20
import urequests
import json

""" Set up network connection """

# DeviceNet info
ssid = 'UI-DeviceNet'
password = 'UI-DeviceNet'

# Function for connecting to wifi, ssid = network id and password = network password
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Time-out after max_wait seconds so that not stuck in endless loop. Print error to screen is not able to connect
    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        sleep(1)

    # Failed connection if status is 3, otherwise connected
    if wlan.status() != 3:
        raise RuntimeError('Network connection failed.')
    else:
        print('Connected.')
        status = wlan.ifconfig()

""" Set up buttons """

# Buttons to control temp sensors 1 and 2
button1 = Pin(9)
button2 = Pin(13)

""" Set up OLED """

# Pixel width x height
WIDTH = 128
HEIGHT = 64

# Set up I2C, (I2C 1 or 0, scl pin number, sda pin number, frequency)
i2c = I2C(1, scl = Pin(3), sda = Pin(2), freq = 200000)

# Variable for the oled, screen width, height and i2c passed to initialize
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Function for writing the temperature and updating to screen
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

# Defaults
sensor_one_status = "OFF"
sensor_two_status = "OFF"
sensor_one_temp = 0
sensor_two_temp = 0

# DS_Pin is where the sensors are connected, in this case GPIO16 (pin 21)
ds_pin = Pin(16)
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
print('Found DS18B20 sensor with address: ', roms)

""" MAIN """

while True:
    # Convert sensor temperature to C
    ds.convert_temp()
    sleep_ms(100) # delay to allow conversion

    # Button 1 is pressed, temp sensor 1 turned on. 
    if button1.value() == 0:
        try:
            sensor_one_temp = round(ds.read_temp(roms[0]), 1)
            sensor_one_status = "ON"
        except Exception as e1: # user disconnected sensor
            print("Error reading sensor 1: ", e1)
            sensor_one_status = "D/C"
            sensor_one_temp = -1
    else: 
        sensor_one_status = "OFF"
        sensor_one_temp = 0.0
    
    # Button 2 is pressed, temp sensor 2 turned on
    if button2.value() == 0:
        try:
            sensor_two_temp = round(ds.read_temp(roms[1]), 1)
            sensor_two_status = "ON"
        except Exception as e2: # user disconnected sensor
            print("Error reading sensor 2: ", e2)
            sensor_two_status = "D/C"
            sensor_two_temp = -1
    else: 
        sensor_two_status = "OFF"
        sensor_two_temp = 0.0

    write_to_oled(sensor_one_status, sensor_two_status, sensor_one_temp, sensor_two_temp)

    connect_to_wifi(ssid, password)

    data = {
        "temp1": sensor_one_temp,  # t1 is the temperature 1 variable
        "temp2": sensor_two_temp # t2 is the temperature 2 variable
    }
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)


    url = 'http://172.234.206.64:8000/data'
    response = urequests.post(url, data=json_data, headers=headers)
    print(response.status_code)
    print(response.text)
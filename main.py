from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import onewire, ds18x20, time
import network
import socket
import freesans20
import writer

""" Set up temp sensors """

ds_pin = Pin(16)
 
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
 
roms = ds_sensor.scan()

print('Found DS devices: ', roms)

""" Set up OLED """
WIDTH = 128
HEIGHT = 64

i2c = I2C(1, scl = Pin(3), sda = Pin(2), freq = 200000)

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def write_to_oled(temp):
    oled.fill(0)
    oled.text("TEMP", 0, 0)
    oled.text(str(temp), 0, 40)
    oled.show()   


""" Set up webserver """
def webpage(reading):
    # Set up HTML template
    html = f"""<!DOCTYPE html>
            <html>
            <head>
                <title> Temperature </title>
                <meta http-equiv="refresh" content="10">
            </head>
            <body>
                <p> {reading} </p>
            </body>
            </html>
            """
    return str(html)

""" Set up network """
# Set up AP mode on pico w
def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while not ap.active():
        pass
    print('AP mode is active, you can now connect.')
    print('IP address to connect to: ' + ap.ifconfig()[0])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5) # listen for 5 because you can only have 5 devices connected to pico w

    prev_temp = None

    while True:
        try:
            conn, addr = s.accept()
            print('Connection from %s' % str(addr))
            request = conn.recv(1024)
            print('Content = %s' % str(request))

            ds_sensor.convert_temp()
            time.sleep_ms(750)
            temp_reading = round(ds_sensor.read_temp(roms[0]), 2)

            # If temp has changed, update the webpage
            if temp_reading != prev_temp:
                response = webpage(temp_reading)
                prev_temp = temp_reading # Update previous temp
            else:
                respone = webpage(prev_temp)

            conn.send(respone)
        except Exception as e:
            print("Exception: ", e)
        finally:
            conn.close()

""" MAIN """   
try:
    ap_mode('NAME', 'PASSWORD')
except KeyboardInterrupt:
    machine.reset()

while True:
 
  ds_sensor.convert_temp()
 
  time.sleep_ms(750)
 
  for rom in roms:
 
    tnum = round(ds_sensor.read_temp(rom), 2)
    print(tnum, " Celsius")
    write_to_oled(tnum)

  
 
  time.sleep(1)
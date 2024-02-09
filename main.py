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

def write_to_oled():
    oled.fill(0)
    oled.text("TEMP", 0, 0)
    oled.text("Test", 0, 40)
    oled.show()   

""" Set up network """
# SSID / password setup
ssid, password = 'TP-LINK_IoT', 'BNWIoT12!@'

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF) # STA is station AP is access point
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    addr = (ip, 80)
    connection = socket.socket()
    connection.bind(addr)
    connection.listen(1)
    return connection

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
    
def serve(connection):
    # Start a web server
    while True:
        write_to_oled()
        reading = 'Temperature: '
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        html = webpage(reading)
        client.send(html)
        client.close()
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
# Checkpoint 3

import machine
import ssd1306
import time
import network
import socket
import urequests
import json

# LCD Setup
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))	# setup I2C for screen
oled = ssd1306.SSD1306_I2C(128, 32, i2c)				# setup screen as I2C device
led = machine.Pin(2, machine.Pin.OUT)

# Connect ESP8266 to WiFi
# Example from: http://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html
sta_if = network.WLAN(network.STA_IF)					# setup ESP8266 as a station
ap_if = network.WLAN(network.AP_IF)						# setup ESP8266 as AP

def do_connect():
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Fam', 'pinkcoconut')	#(<SSID>, <password>)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()



def web_page():
  if led.value() == 0:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html




#Initiate on-board (server) socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80)) #empty string is localhost
s.listen(5)

#Listen for incoming commands from the phone (client)
while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)
  print('Content = %s' % request)


  led_on = request.find('/?led=on')
  led_off = request.find('/?led=off')
  if led_on == 6:
    print('LED ON')
    led.value(1)
  if led_off == 6:
    print('LED OFF')
    led.value(0)
  response = web_page()


  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()


oled.text("hello world", 0, 0)









oled.show()
# Execute: exec(open("chp3.py").read())

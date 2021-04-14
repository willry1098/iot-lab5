

import machine
import ssd1306
import time
import network
import usocket as socket
import urequests
import json


### MACHINE SETUP ###

# OLED Setup
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4)) # setup I2C for screen
oled = ssd1306.SSD1306_I2C(128, 32, i2c)        # setup screen as I2C device
led = machine.Pin(2, machine.Pin.OUT)

buttonA  = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP) # HOURS
buttonB  = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP) # MINUTES
buttonC  = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP) # SECONDS
alarmSet = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP) 

# Clock Setup
rtc = machine.RTC() # Using RTC to keep the time
rtc.datetime((2021, 4, 6, 0, 19, 40, 0, 0))

# Photoresistor setup
adc = machine.ADC(0)

# Connect ESP8266 to WiFi
# Example from: http://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html
sta_if = network.WLAN(network.STA_IF)         # setup ESP8266 as a station
ap_if = network.WLAN(network.AP_IF)           # setup ESP8266 as AP


### FUNCTION DEFINITIONS ###


def do_connect():
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Fam', 'pinkcoconut')  #(<SSID>, <password>)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()


def showWeather():
	# REQUEST LOCATION
	geoApiURL = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyDUUfLWy6buEVlkHc3FlGJf89hMcqFkWy8"
	jsonData  = {'content type':'application/json','content length':'0'}
	response  = urequests.post(geoApiURL, json=jsonData)

	jsonArray = response.json()
	print("Location", jsonArray['location'])

	lat = jsonArray['location']['lat']
	lng = jsonArray['location']['lng']

	# REQUEST WEATHER
	weatherKey = "d30ff2392e5e697b85285b731667265e"
	weatherApiURL = ("http://api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(lng)+"&appid="+weatherKey)
	response2  = urequests.post(weatherApiURL, json=jsonData)

	weatherArray = response2.json()
	condition = weatherArray['weather'][0]['description']
	temperature = weatherArray['main']['temp']-273.15

  # OUTPUT WEATHER
	print(temperature, "°C and", condition)

	outputTemp = str(temperature)+" degrees C"
	oled.text(outputTemp, 0, 0)
	outputWthr = str(condition)
	oled.text(outputWthr, 0, 10)

def showTime():
  #Setup time
  oled.fill(0)
  now = rtc.datetime()
  seconds = (now[6] + buttonCcount) % 60
  minutes = (now[5] + buttonBcount) % 60
  hours = (now[4] + buttonAcount) % 24
  output = "Time: " + str(hours) + ":" + str(minutes) + "." + str(seconds)
  oled.text(output, 0, 0)


### EXECUTIONAL CODE ###


#Initiate on-board (server) socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setblocking(False)
s.settimeout(0.5)
s.bind(('', 80)) #empty string is localhost
s.listen(3)


# Counters + Booleans

display = True
timeBool = False
command = ""

buttonAcount = 0
buttonBcount = 0
buttonCcount = 0

buttonAcountAlarm = 0
buttonBcountAlarm = 0
buttonCcountAlarm = 0

hours = 0
minutes = 0
seconds = 0

alarmSeconds = -1
alarmMinutes = 0
alarmHours   = 0

alarmRinging = False

#Listen for incoming commands from the phone (client)
while True:
  
  
    # adjust contrast
    brightness = int(adc.read() / 9) # [0, 113]
    oled.contrast(brightness)

    # check time buttons
    if (buttonC.value() == 0):
        buttonCcount += 1
    if (buttonB.value() == 0):
      buttonBcount += 1
    if (buttonA.value() == 0):
      buttonAcount += 1

    #Accept incoming Connection
    try:
      conn, addr = s.accept()
      print('Got a connection from %s' % str(addr))

      #parse request
      request = conn.recv(1024)
      request = str(request)
      print('Content = %s' % request)

      #Extract Command
      sub_str = " "
      occurrence = 2
      val = -1             # Finding nth occurrence of substring
      for i in range(0, occurrence):
        val = request.find(sub_str, val + 1)

      if (request != ""):
        command = request[16:val]
        command = command.replace("%20", " ")

      #Process Command
      if (command == "on"):
        oled.show()
        display = True
      elif (command == "off"):
        oled.fill(0)
        display = False
        oled.show()
      elif (command == "weather"):
        oled.fill(0)
        showWeather()
        timeBool = False
      elif (command == "time"):
        timeBool = not timeBool
      else:
        #Show Command
        oled.fill(0)
        print("Cmnd: " + command)
        oled.text("Cmnd: " + command, 0, 10)
        oled.show() 
        timeBool = False

      #GENERATE RESPONSE
      response = "All Good"
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      conn.close()

    except OSError:
      pass

    if (timeBool):
      showTime()

    if (display):
      oled.show()
    else:
      oled.fill(0)
  # End of if non-alarm mode
  

time.sleep(0.8)












# Execute: exec(open("server.py").read())





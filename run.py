#!/usr/bin/env python

#import mosquitto.publish as publish

import time
from mpu6050 import mpu6050
from subprocess import call

# Name of this sensor (the MQTT path):
mqttPath = 'udl/basement/dryer/'
# Whether or not to attempt to use an attached OLED display:
enableOLED = True
# The location of the MQTT server:
mqttServer = '10.0.0.126'
# The MQTT server port (default 1883):
mqttPort = 1883
# Frequency of MQTT messages (in seconds):
mqttFreq = 15
# Measurement frequency (in ms):
measureFreq = 200
# Percentage change of accelerometer readings to count as 'running':
jitter = 1
# Percentage of 'running' readings to change status:
statusChange = .75


#####

def mqttPub(path, value):
  #publish.single(mqttPath + "path", value, hostname=mqttServer, port=mqttPort)
  call(["mosquitto_pub", \
    "-h", str(mqttServer), \
    "-p", str(mqttPort), \
    "-t", str(mqttPath) + str(path), "-m", str(value)])

mpu = mpu6050(0x68)
# Prime readings so we have something to compare against
accel = mpu.get_accel_data()
lastX = accel['x']
lastY = accel['y']
lastZ = accel['z']

if enableOLED:
  call(["oled-exp", "-q", "-i"])


cycles = 0
running = 0
stopped = 0
status = "stopped"
sleeptime = float(measureFreq) / 1000
while True:
  accel = mpu.get_accel_data()
  # Measure percentage change since last reading on each axis
  # (a more accurate way to do this would be to get a differential but
  # honestly that level of accuracy is not needed here and is more
  # expensive to calculate)
  pX = abs(accel['x'] / (accel['x'] + lastX))
  pY = abs(accel['y'] / (accel['y'] + lastY))
  pZ = abs(accel['z'] / (accel['z'] + lastZ))

  if pX > jitter or pY > jitter or pZ > jitter:
    running = running + 1
  else:
    stopped = stopped + 1


  if (cycles >= mqttFreq):
    if status == "stopped":
      if running / (running + stopped) > statusChange:
        status = "running"
    else:
      if stopped / (running + stopped) > statusChange:
        status = "stopped"

    mqttPub("status", status)
    temp = mpu.get_temp()
    mqttPub("temperature", temp)

    cycles = 0
    running = 0
    stopped = 0

    if enableOLED:
      dtempC = "%.1f" % temp
      dtempF = "%.1f" % (9.0/5.0 * temp + 32)
      dX = "%.1f" % pX
      dY = "%.1f" % pY
      dZ = "%.1f" % pZ
      display = "Temp: " + dtempC + "'C (" + dtempF + "'F)" \
        + "\\nStatus: " + status \
        + "\\n\\n   dX: " + dX \
        + "\\n   dY: " + dY \
        + "\\n   dZ: " + dZ
      call(["oled-exp", "-q", "-c", "write", display])

  lastX = accel['x']
  lastY = accel['y']
  lastZ = accel['z']

  cycles = cycles + sleeptime
  time.sleep(sleeptime)

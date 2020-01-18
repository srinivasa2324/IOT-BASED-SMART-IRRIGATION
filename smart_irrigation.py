import RPi.GPIO as GPIO
import dht11
import time
import sys
import dht11
import datetime
import requests
import ibmiotf.application
import ibmiotf.device
import random

#Provide your IBM Watson Device Credentials
organization = "dyl4ga"
deviceType = "RaspberryPi"
deviceId = "1402"
authMethod = "token"
authToken = "987654321"

# Initialize GPIO
GPIO.setwarnings(False)
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.OUT)
p = GPIO.PWM(7, 50)
p.start(7.5)

# read data using pin 12
SensorInstance = dht11.DHT11(pin = 12)


# Initialize the device client.
T=0
H=0
SM=1

def myCommandCallback(cmd):
        print("Command received: %s" % cmd.data['command'])
        GPIO.setup(7,GPIO.OUT)

        if cmd.data['command'] == 'motoron':
                print("MOTOR IS ON")
                GPIO.output(7,True)
        elif cmd.data['command'] == 'motoroff':
                print("MOTOR IS OFF")
                GPIO.output(7,False)
        
       
        
        if cmd.command == "setInterval":
                if 'interval' not in cmd.data:
                        print("Error - command is missing required information: 'interval'")
                else:
                        interval = cmd.data['interval']
        elif cmd.command == "print":
                if 'message' not in cmd.data:
                        print("Error - command is missing required information: 'message'")
                else:
                        print(cmd.data['message'])

try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
	#..............................................
	
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()

def servo():
        p.ChangeDutyCycle(7.5) #Neutral (90Â°)
        time.sleep(0)
        print ("Servo Rotates 90 Â°C")
        p.ChangeDutyCycle(12.5) #180Â°
        time.sleep(2)
        print ("Servo Rotates 180 Â°C")
        p.ChangeDutyCycle(2.5) #0Â°
        time.sleep(2)
        print ("Servo Rotates 0 Â°C")
 
def soilmoist(channel):
        SM=GPIO.input(channel)
        print(SM)
        if SM==0:
                print ("Water Detected!")
        elif SM==1:
            servo()
            
 
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, soilmoist)  # assign function to GPIO PIN, Run function on change


while True:
        #Get Sensor Data from DHT11
        SensorData = SensorInstance.read()
        if SensorData.is_valid():
        #if True:
            T = SensorData.temperature
            H = SensorData.humidity
        else:
                soilmoist(channel)
        #Send Temperature & Humidity to IBM Watson
        data = {"d":{ 'temperature' : T, 'humidity': H, 'SM':SM }}
        #print data
        def myOnPublishCallback():
            print ("Published Temperature = %s C" % T, "Humidity = %s %%" % H, "SM = %s %%" % SM, "to IBM Watson")

        success = deviceCli.publishEvent("Data", "json", data, qos=0, on_publish=myOnPublishCallback)
        if not success:
            print("Not connected to IoTF")
        time.sleep(1)
        
        deviceCli.commandCallback = myCommandCallback

# Disconnect the device and application from the cloud
deviceCli.disconnect()

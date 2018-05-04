#!/usr/bin/env python3
import os
import sys
import time
import socket
import threading
import configparser
import paho.mqtt.client as mqtt
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_gps_v2 import BrickletGPSV2
from tinkerforge.bricklet_barometer import BrickletBarometer

config = configparser.ConfigParser()
config.read('/home/dapo/gateway/tinkerforgeconfig.ini')
cnf =  config['DEFAULT']

HOST = cnf["HOST"]
PORT = int(cnf["PORT"])
TEMPUID = cnf["TEMPUID"]
BARUID = cnf["BARUID"]
GPSUID = cnf["GPSUID"]

print("Host: " + str(HOST) + ", Port: " + str(PORT) + ", TEMPUID: " + str(TEMPUID) + ", BARUID: " + str(BARUID) + ", GPSUID: " + str(GPSUID) )

client_id = str(socket.gethostname())

# CWT to script dir
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
    print("Disconnected, exiting")
    sys.exit(1)

def sendMessage(client, pressure, temperature, longitude, latitude, altitude):
    # timestamp; pressure; temprature; longitude, latitude, altitude
    payload = "{};{};{};{};{};{}".format(time.time(), pressure, temperature, longitude, latitude, altitude.altitude)
    topic = "collectors/{}/metrics".format(client_id)
    success = client.publish(topic, payload, qos=0, retain=False)
    print("{}: {}".format(topic, payload))

if __name__ == "__main__":
    # Tinkerforge setup
    ipcon = IPConnection() 
    tempBricklet = BrickletTemperature(TEMPUID, ipcon)
    barometerBricklet = BrickletBarometer(BARUID, ipcon)
    gpsBricklet = BrickletGPSV2(GPSUID, ipcon) 
    ipcon.connect(HOST, PORT) 

    # MQTT Setup
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.tls_set("dapo.pem")
    client.username_pw_set("rpi", "p00rT7daH7Lnb0HzMfA0d+zY2fAOo3")
    client.connect("dapo.0x80.ch", 8883, 30)

    # Send loop
    while(True):
        time.sleep(5)
        try:
            latitude, _, longitude, _ = gpsBricklet.get_coordinates()
            altitude = gpsBricklet.get_altitude()
            temperature = tempBricklet.get_temperature()
            air_pressure = barometerBricklet.get_air_pressure()
            sendMessage(client, air_pressure,temperature,longitude,latitude,altitude)
        except e:
            print(e)

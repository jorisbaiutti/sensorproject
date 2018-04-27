#!/usr/bin/env python3

import time
import socket
import threading
import paho.mqtt.client as mqtt
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_gps_v2 import BrickletGPSV2
from tinkerforge.bricklet_barometer import BrickletBarometer

HOST = "localhost"
PORT = 4223
TEMPUID = "dR1"
BARUID = "k5Q"
GPSUID = "fc9"

client_id = str(socket.gethostname())

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    

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
    client.tls_set("cert.pem")
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

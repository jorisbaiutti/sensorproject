import time
import socket
import threading
import paho.mqtt.client as mqtt
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_gps_v2 import BrickletGPSV2
from tinkerforge.bricklet_barometer import BrickletBarometer

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    

def sendMessage(client, pressure,temprature,longitude,latitude, altitude):
    # timestamp; pressure; temprature; longitude, latitude, altitude
    
    payload = str(time.time()) + ";" + str(pressure) + ";" + str(temprature) + ";" + str(longitude) + ";" + str(latitude) + ";" + str(altitude)
    topic = "collectors/" + str(socket.gethostname()) + "/metrics"
    success = client.publish(topic, payload, qos=0, retain=False)
    print(success)
    print("%s: %s", topic, payload)



HOST = "localhost"
PORT = 4223
TEMPUID = "dR1" # Change XYZ to the UID of your Temperature Bricklet
BARUID = "k5Q"
GPSUID = "qGr"


if __name__ == "__main__":
    ipcon = IPConnection() 
    tempBricklet = BrickletTemperature(TEMPUID, ipcon)
    barometerBricklet = BrickletBarometer(BARUID, ipcon)
    gpsBricklet = BrickletGPSV2(GPSUID, ipcon) 
    ipcon.connect(HOST, PORT) 
    client = mqtt.Client(client_id=str(socket.gethostname()))
    client.on_connect = on_connect
    client.tls_set("cert.pem")
    client.username_pw_set("rpi", "p00rT7daH7Lnb0HzMfA0d+zY2fAOo3")
    client.connect("dapo.0x80.ch", 8883, 30)

    while(True):
        time.sleep(5)
        latitude, ns, longitude, ew = gpsBricklet.get_coordinates()
        altitude = gpsBricklet.get_altitude()
        temperature = tempBricklet.get_temperature()
        air_pressure = barometerBricklet.get_air_pressure()
        sendMessage(client, air_pressure,temperature,longitude,latitude,altitude)


    





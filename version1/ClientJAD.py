import socket
import json, time
import os
import PySimpleGUI as psg
from pathlib import Path

# Check if we are using the Raspberry Pi
IS_RPI = Path("/etc/rpi-issue").exists() # used to check - we are using the Pi
print('Raspberry Pi Connected:', IS_RPI)
# Error handling if we are not using the Raspberry Pi
if IS_RPI:
    print("Correct Hardware")
    try:
        sock = socket.socket()
    except socket.error as err:
        print("Socket creation failed with error %s" % (err))
# Setup socket to connect to Server
port = 1500
#address = '10.102.13.211' # of server, so we can read the vcgencmd data
address = '127.0.0.1' # to run on the Pi with local server
sock = socket.socket()
connected = False
def data():
    '''Sample the data 50 times'''
    for i in range(10):
        v = os.popen('vcgencmd measure_volts ain1').readline() # gets the core voltage using vcgencmd
        core = os.popen('vcgencmd measure_temp').readline() # gets the core temperature using vcgencmd
        pwm = os.popen('vcgencmd measure_clock core').readline() # gets the core PWM using vcgencmd
        mem = os.popen('vcgencmd get_mem gpu').readline() #gets the gpu memory using vcgencmd
        arm = os.popen('vcgencmd get_mem arm').readline() # gets the arm memory using vcgencmd7
        # Format the vcgencmds 
        jsonResult = {'it':i, 'volts':v, 'temp-core':core, 'clock':pwm, 'gpu':mem, 'arm':arm}
        jsonResult = json.dumps(jsonResult)
        jsonbyte = bytearray(jsonResult, 'utf-8')
        # Send the request to the Server every 2 seconds
        sock.send(jsonbyte)
        time.sleep(2)

try:
    # Connect to the socket
    sock.connect((address, port))
    # Run data function
    data()

# Error handling and clean exit if connection is lost
except socket.gaierror: # = short form for getaddrinfo()
    print('There was an error resolving the host')
    sock.close()
finally:
    print('Sorry lost connection')
    exit()

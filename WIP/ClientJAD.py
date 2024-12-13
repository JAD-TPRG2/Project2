import socket
import json, time
import os
import threading
import PySimpleGUI as sg
from pathlib import Path

# Check if we are using the Raspberry Pi
IS_RPI = Path("/etc/rpi-issue").exists() # used to check - we are using the Pi
print('Raspberry Pi Connected:', IS_RPI)
# Error handling if we are not using the Raspberry Pi
if not IS_RPI:
    print('Raspberry Pi Not Connected')
    exit()
# Setup socket to connect to Server
port = 1500
#address = '10.102.13.211' # of server, so we can read the vcgencmd data
address = '127.0.0.1' # to run on the Pi with local server
sock = socket.socket()
connected = False

# Setup GUI
sg.theme('Dark Green 4')
CIRCLE = '\u26ab'
CIRCLE_OUTLINE = '\u26aa'
def LED(colour, key):
    '''User defined element for LED'''
    return sg.Text(CIRCLE_OUTLINE, text_color=colour, key=key)

layout = [ [sg.Text('Connction:'), LED('GREEN', '-LED0_')], [sg.Button('Exit')]]

window = sg.Window('Client Connection', layout, font='Any 16')
def data():
    '''Sample the data 50 times'''
    for i in range(10):
        # gets the core voltage using vcgencmd
        v = os.popen('vcgencmd measure_volts ain1').readline()
        # gets the core temperature using vcgencmd
        core = os.popen('vcgencmd measure_temp').readline()
        # gets the core PWM using vcgencmd
        pwm = os.popen('vcgencmd measure_clock core').readline()
        #gets the gpu memory using vcgencmd
        mem = os.popen('vcgencmd get_mem gpu').readline()
        # gets the arm memory using vcgencmd7
        arm = os.popen('vcgencmd get_mem arm').readline()
        # Format the vcgencmds
        jsonResult = {'it':i, 'volts':v, 'temp-core':core, 'clock':pwm, 'gpu':mem, 'arm':arm}
        jsonResult = json.dumps(jsonResult)
        jsonbyte = bytearray(jsonResult, 'utf-8')
        # Send the request to the Server every 2 seconds
        sock.send(jsonbyte)
        time.sleep(2)
# Start connection
while not connected:
    try:
        # Connect to the socket
        sock.connect((address, port))
        connected = True
    # Error handling and clean exit if connection is lost
    except socket.gaierror: # = short form for getaddrinfo()
        print('There was an error resolving the host')
        sock.close()
    finally:
        print('Sorry lost connection')
        exit()
# Run data function on separate thread
threading.Thread(target=data, daemon=True).start()
# Run GUI
while True:
    event, values = window.read(timeout=200)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    window['-LED0_'].update(CIRCLE if connected else CIRCLE_OUTLINE)
window.close()
sock.close()

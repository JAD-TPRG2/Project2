'''ClientJAD'''
# Jeremy Domino (100919249)
# ClientJAD.py -- This client runs on Pi, sends Pi's your 5 arguments from the vcgencmds, sent as Json object
# TPRG2131 Section 02
# December 5, 2024
#
# This program is strictly my own work. Any material beyond course learning
# materials that is taken from the Web or other sources is properly cited,
# giving credit to the original author(s).
# Modified from code provided by Prof. Phil Jarvis
#
# This client only runs on the Pi, sends Pi's your 5 arguments from the vcgencmds, sent as Json object.

import socket
import json, time
import os
import threading
import PySimpleGUI as sg
from pathlib import Path

# Check if we are using the Raspberry Pi
IS_RPI = Path("/etc/rpi-issue").exists()  # Used to check if we are on the Pi
print('Raspberry Pi Connected:', IS_RPI)

# Error handling if we are not using the Raspberry Pi
if IS_RPI:
    print("Correct Hardware")
    try:
        sock = socket.socket()
    except socket.error as err:
        print("Socket creation failed with error %s" % (err))
else:
    print('Not a Raspberry Pi')
    exit()

# Setup socket to connect to Server
port = 1500
address = '192.168.2.43'
#address = '127.0.0.1'  # To run on the Pi with local server
connected = False
stop_event = threading.Event()

# Setup GUI
sg.theme('Dark Green 4')
CIRCLE = '\u26ab'
# Setup the LED
def LED(colour, key):
    '''User defined element for LED'''
    return sg.Text(CIRCLE, text_color=colour, key=key)
# Setup the Layout
layout = [
    [sg.Text('Connection: '), LED('GREEN', '-LED0_')],
    [sg.Button('Exit')]
]
# Setup window and title
window = sg.Window('Client Connection', layout, font='Any 16')

# Setup calls to the server and thread in the background
def data():
    '''Start a thread and sample the data 50 times'''
    global connected
    for i in range(50):
        try:
            # Get system info using vcgencmd
            v = os.popen('vcgencmd measure_volts').readline().strip()
            v = v.replace('volt=','')[:-1]
            core = os.popen('vcgencmd measure_temp').readline().strip()
            core = core.replace('temp=','')[:-2]
            pwm = os.popen('vcgencmd measure_clock core').readline().strip()
            pwm = pwm.replace('frequency(1)=','')
            hdmi = os.popen('vcgencmd measure_clock hdmi').readline().strip()
            hdmi = hdmi.replace('frequency(9)=','')
            arm = os.popen('vcgencmd measure_clock arm').readline().strip()
            arm = arm.replace('frequency(48)=','')

            # Prepare the JSON payload
            jsonResult = {
                'it': i,
                'volts': float(v),
                'temp-core': float(core),
                'clock': pwm,
                'hdmi': hdmi,
                'arm': arm
            }
            jsonResult = json.dumps(jsonResult)
            jsonbyte = bytearray(jsonResult, 'utf-8')
        except KeyboardInterrupt:
            print('Socket Closed')
            connected = False  # Update connection status
            stop_event.set()
            break
        
        try:
            # Send the request to the Server every 2 seconds
            sock.send(jsonbyte)
            time.sleep(2)
            # When threshold reached close socket and update status
            if i == 49:
                print('Threshold Reached')
                stop_event.set()
                sock.close()
                connected = False
                stop_event.set()
                break
        except OSError:
            print('Socket Closed')
            connected = False
            stop_event.set()  # Update connection status
            break

# Start connection
try:
    # Connect to the socket
    sock.connect((address, port))
    connected = True
    # Start the data thread
    thread = threading.Thread(target=data, daemon=True)
    thread.start()
except socket.gaierror:  # Short form for getaddrinfo()
    print('There was an error resolving the host')
    stop_event.set()
    sock.close()
except Exception:
    print('Lost Connection')
    stop_event.set()
    sock.close()
    connected = False

# Run GUI
while True:
    event, values = window.read(timeout=200)
    
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop_event.set()
        break

    # Check the connection status and update the LED color
    if connected:
        window['-LED0_'].update(CIRCLE, text_color='green')
    else:
        window['-LED0_'].update(CIRCLE, text_color='red')

window.close()
print('Connection Terminated')
sock.close()

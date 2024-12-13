import socket
import json
import time
import threading
import PySimpleGUI as sg

# Setup the socket
sock = socket.socket()
print("Socket successfully created")
port = 1500
sock.bind(('', port))  # Localhost for testing
sock.listen(5)
print("Socket is listening")
# Accept the connection (blocked until a connection is made)
c, addr = sock.accept()
print("Got connection from", addr)

# Setup data container
data_received = {}
receiving = False
# Setup LED
CIRCLE = '\u26ab'

def receive_data():
    '''Receive data in a separate thread'''
    global data_received
    global receiving
    while True:
        try:
            jsonReceived = c.recv(1024)
            if jsonReceived == b'':
                receiving = False  # Connection was closed or lost
                print('Connection Lost')
                break  # Exit the loop if the connection is lost
            else:
                receiving = True
            # Parse the received JSON data
            data = json.loads(jsonReceived)  
            # Extract values from the JSON data
            data_received = {
                'it': data['it']+1,
                'volts': round(data['volts'],1),
                'temp-core': data['temp-core'],
                'clock': data['clock'],
                'hdmi': data['hdmi'],
                'arm': data['arm']
            }
            time.sleep(1)  # Simulate processing time
        # Error hanlding (catch all)
        except json.JSONDecodeError:
            print("Failed to decode JSON data.")
            receiving = False
        except Exception:
            print(f"Lost connection from {addr}")
            receiving = False
            break

    # After loop ends
    c.close()
    # Close the socket connection
    sock.close()

def LED(colour, key):
    '''User defined element for LED'''
    return sg.Text(CIRCLE, text_color=colour, key=key)

def create_gui():
    '''Create the GUI'''
    sg.theme('Dark Green 4')
    # Setup the layout
    layout = [
        [sg.Text('Receiving Data', font=('Arial', 15)), LED('RED', '-LED-')],
        [sg.Text('Sample #', font=('Arial', 15)), sg.Text('', key='-SAMPLE-', font=('Arial', 15))],
        [sg.Text('Core Voltage(V):', font=('Arial', 15)), sg.Text('', key='-VOLTAGE-', font=('Arial', 15))],
        [sg.Text('Core Temperature(C):', font=('Arial', 15)), sg.Text('', key='-TEMP_CORE-', font=('Arial', 15))],
        [sg.Text('Core Clock(Hz):', font=('Arial', 15)), sg.Text('',key='-CLOCK-', font=('Arial', 15))],
        [sg.Text('HDMI Clock(Hz):', font=('Arial', 15)), sg.Text('', key='-HDMI-', font=('Arial', 15))],
        [sg.Text('ARM Clock(Hz):', font=('Arial', 15)), sg.Text('', key='-ARM-', font=('Arial', 15))],
        [sg.Button('Exit')]
    ]
    #Setup the window
    window = sg.Window('Server Connection', layout, font='Any 16')
    # Open the GUI with exit event
    while True:
        event, values = window.read(timeout=200)
        if event == sg.WIN_CLOSED or event == 'Exit':
            print('Program interrupted. Closing...')
            break
        # Update the GUI with the latest data
        if data_received:
            window['-SAMPLE-'].update(data_received['it'])
            window['-VOLTAGE-'].update(data_received['volts'])
            window['-TEMP_CORE-'].update(data_received['temp-core'])
            window['-CLOCK-'].update(data_received['clock'])
            window['-HDMI-'].update(data_received['hdmi'])
            window['-ARM-'].update(data_received['arm'])

        if not receiving:
            window['-LED-'].update(text_color='RED')
        else:
            window['-LED-'].update(text_color='GREEN')
    window.close()

if __name__ == '__main__':
    try:
        # Start the data receiving thread
        thread = threading.Thread(target=receive_data, daemon=True)
        thread.start()
        # Start the GUI in the main thread
        create_gui()
    # Error handling
    except KeyboardInterrupt:
        print('Program interrupted. Closing...')
        c.close()  # Make sure to close the connection if interrupted
        sock.close()  # Close the server socket as well
        exit()

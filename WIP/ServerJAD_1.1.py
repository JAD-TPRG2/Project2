import socket
import json
import time
import threading
import PySimpleGUI as sg

# Setup the socket
sock = socket.socket()
print("Socket successfully created")

port = 1500
sock.bind(('127.0.0.1', port))  # Localhost for testing
sock.listen(5)

print("Socket is listening")

# Accept the connection (blocked until a connection is made)
c, addr = sock.accept()
print("Got connection from", addr)

# Shared data variable to pass data from the thread to the GUI
data_received = {}

# Function for receiving data in a separate thread
def receive_data():
    global data_received
    while True:
        try:
            jsonReceived = c.recv(1024)
            
            if jsonReceived == b'':  # Connection was closed or lost
                print('Connection Lost')
                break  # Exit the loop if the connection is lost
            
            data = json.loads(jsonReceived)  # Parse the received JSON data
            
            # Extract values from the JSON data
            data_received = {
                'it': data.get('it'),
                'volts': data.get('volts'),
                'temp-core': data.get('temp-core'),
                'clock': data.get('clock'),
                'gpu': data.get('gpu'),
                'arm': data.get('arm')
            }
            
            time.sleep(1)  # Simulate processing time
        except json.JSONDecodeError:
            print("Failed to decode JSON data.")
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    # After loop ends
    c.close()
    sock.close()  # Close the socket connection

# GUI Layout and Window setup
def create_gui():
    layout = [
        [sg.Text('Receiving Data', font='Any 16')],
        [sg.Text('Sample #', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-SAMPLE_', font='Any 12')],
        [sg.Text('Volts', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-VOLTAGE_', font='Any 12')],
        [sg.Text('Temperature (Core)', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-TEMP_CORE_', font='Any 12')],
        [sg.Text('Clock', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-CLOCK_', font='Any 12')],
        [sg.Text('GPU', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-GPU_', font='Any 12')],
        [sg.Text('ARM', size=(15, 1), font='Any 12'), sg.Text('', size=(15, 1), key='-ARM_', font='Any 12')],
        [sg.Button('Exit')]
    ]

    window = sg.Window('Socket Data Receiver', layout, font='Any 16')

    # Update GUI continuously with new data from the socket
    while True:
        event, values = window.read(timeout=200)  # Check for events every 200 ms
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        # Update the GUI with the latest data
        if data_received:
            window['-SAMPLE_'].update(data_received.get('it', 'N/A'))
            window['-VOLTAGE_'].update(data_received.get('volts', 'N/A'))
            window['-TEMP_CORE_'].update(data_received.get('temp-core', 'N/A'))
            window['-CLOCK_'].update(data_received.get('clock', 'N/A'))
            window['-GPU_'].update(data_received.get('gpu', 'N/A'))
            window['-ARM_'].update(data_received.get('arm', 'N/A'))
    
    window.close()

if __name__ == '__main__':
    try:
        # Start the data receiving thread
        receive_thread = threading.Thread(target=receive_data, daemon=True)
        receive_thread.start()

        # Start the GUI in the main thread
        create_gui()

    except KeyboardInterrupt:
        print('Program interrupted. Closing...')
        c.close()  # Make sure to close the connection if interrupted
        sock.close()  # Close the server socket as well
        exit()

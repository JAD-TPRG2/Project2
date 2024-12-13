import socket
import json
import time

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

def main():
    while True:
        try:
            jsonReceived = c.recv(1024)
            
            if jsonReceived == b'':  # Connection was closed or lost
                print('Connection Lost')
                break  # Exit the loop if the connection is lost
            
            data = json.loads(jsonReceived)  # Parse the received JSON data
            
            # Extract values from the JSON data
            ret1 = data.get('it')
            ret2 = data.get('volts')
            ret3 = data.get('temp-core')
            ret4 = data.get('clock')
            ret5 = data.get('gpu')
            ret6 = data.get('arm')

            # Print the extracted data
            print(f'\nSample # {ret1 + 1}\n')
            print(f'Volts: {ret2}')
            print(f'Temperature (Core): {ret3}')
            print(f'Clock: {ret4}')
            print(f'GPU: {ret5}')
            print(f'ARM: {ret6}')
            
            time.sleep(1)  # Simulate processing time
        except json.JSONDecodeError:
            print("Failed to decode JSON data.")
        except Exception:
            print(f"Lost connection from {addr}")
            break

    # After loop ends
    c.close()
    sock.close()  # Close the socket connection

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Program interrupted. Closing...')
        c.close()  # Make sure to close the connection if interrupted
        sock.close()  # Close the server socket as well
        exit()

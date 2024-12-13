import socket
import json, time

sock = socket.socket()
print("Socket successfully created")

port = 1500
#sock.bind(('10.102.13.211', port))
sock.bind(('127.0.0.1', port)) # to run on the Pi with local server
sock.listen(5)

print("Socket is listening")
c, addr = sock.accept()
print("Got connection from", addr)

def main():
    while True:
        jsonReceived = c.recv(1024)
        #print('Json received (byte type)-->', jsonReceived)
        if jsonReceived == b'':
            print('Connection Lost')
            exit()
        data = json.loads(jsonReceived)
        ret = json.dumps(data, indent=0)
        ret1 = data['it']
        ret2 = data['volts']
        ret3 = data['temp-core']
        ret4 = data['clock']
        ret5 = data['gpu']
        ret6 = data['arm']

        print('\nSample # ', ret1, '\n')
        print(ret2)
        print(ret3)
        print(ret4)
        print(ret5)
        print(ret6)
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Bye...')
        exit()
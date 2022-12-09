# echo-client.py

import socket
import pickle

HOST = "MacBook-Pro-van-August.local"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
print (HOST)
print (PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    msg = s.recv(1024)
    #data = msg.decode("utf-8")
    leds = pickle.loads(msg)
    print(leds)
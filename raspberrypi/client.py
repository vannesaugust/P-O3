# echo-client.py

import socket
import pickle
from cryptography import fernet

HOST = "MacBook-Pro-van-August.local"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
print (HOST)
print (PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    msg = s.recv(1024)
    f = fernet
    key = 't75ggizya6BwEUJ6M8PL8pKy2Cg-FEkInqHeV9GXwZo='
    key = key.encode("ASCII")
    msg = f.Fernet(key).decrypt(msg)
    leds = pickle.loads(msg)
    print(leds)
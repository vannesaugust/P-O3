# echo-server.py

import socket
import pickle
from cryptography import fernet

leds = [['warmtepomp', 'droogkast', 'wasmachine', 'koelkast', 'vaatwas', 'robotmaaier', 'elektrische auto', 'elektrische fiets', 'batterij_ontladen', 'batterij_opladen','frigo'], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1]]
msg = pickle.dumps( leds )
f = fernet
key = 't75ggizya6BwEUJ6M8PL8pKy2Cg-FEkInqHeV9GXwZo='
key = key.encode("ASCII")
message = f.Fernet(key).encrypt(msg)
print(message)


HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")

while True:
    user_answer = input("leds on?").lower().strip()
    if user_answer == "true":
        clientsocket.send(msg)





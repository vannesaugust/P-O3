import socket
import pickle

import RPi.GPIO as GPIO #dit gaat enkel op de raspberry zelf enkel kunnen geïnstalleerd worden
import time

HOST = "MacBook-Pro-van-August.local"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
print (HOST)
print (PORT)
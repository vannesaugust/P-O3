import socket
import pickle
from cryptography import fernet

#import RPi.GPIO as GPIO #dit gaat enkel op de raspberry zelf enkel kunnen geïnstalleerd worden
#import time

#setup leds raspberry pi
LED_PIN_wasmachine = 2
LED_PIN_verwarming = 3
LED_PIN_droogkast = 4
LED_PIN_frigo = 17
LED_PIN_vaatwas = 27
LED_PIN_batterij_ontladen = 22
LED_PIN_batterij_opladen = 5
LED_PIN_auto = 6




GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_wasmachine, GPIO.OUT)
GPIO.setup(LED_PIN_verwarming, GPIO.OUT)
GPIO.setup(LED_PIN_droogkast, GPIO.OUT)
GPIO.setup(LED_PIN_frigo, GPIO.OUT)
GPIO.setup(LED_PIN_vaatwas, GPIO.OUT)
GPIO.setup(LED_PIN_batterij_ontladen, GPIO.OUT)
GPIO.setup(LED_PIN_batterij_opladen, GPIO.OUT)
GPIO.setup(LED_PIN_auto, GPIO.OUT)


#variables connectie
HOST = "MacBook-Pro-van-August.local"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
print (HOST)
print (PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    data = s.recv(1024)
    f = fernet
    key = 't75ggizya6BwEUJ6M8PL8pKy2Cg-FEkInqHeV9GXwZo='
    key = key.encode("ASCII")
    data = f.Fernet(key).decrypt(data)
    werking_leds = pickle.loads(data)
    print(werking_leds)
    for i in range(len(werking_leds[0])):
        if werking_leds[0][i] == 'wasmachine':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_wasmachine, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_wasmachine, GPIO.LOW)


        if werking_leds[0][i] == 'verwarming':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_verwarming, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_verwarming, GPIO.LOW)



        if werking_leds[0][i] == 'droogkast':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_droogkast, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_droogkast, GPIO.LOW)


        if werking_leds[0][i] == 'frigo':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_frigo, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_frigo, GPIO.LOW)


        if werking_leds[0][i] == 'vaatwas':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_vaatwas, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_vaatwas, GPIO.LOW)

        if werking_leds[0][i] == 'batterij_ontladen': #met rode LED
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_batterij_ontladen, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_batterij_ontladen, GPIO.LOW)

        if werking_leds[0][i] == 'batterij_opladen': #met groende LED
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_batterij_opladen, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_batterij_opladen, GPIO.LOW)


        if werking_leds[0][i] == 'auto':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_auto, GPIO.HIGH)

            else:
                GPIO.output(LED_PIN_auto, GPIO.LOW)



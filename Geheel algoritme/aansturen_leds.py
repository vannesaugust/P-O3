import RPi.GPIO as GPIO #dit gaat enkel op de raspberry zelf enkel kunnen geïnstalleerd worden
import time



#stel volgende lijst zijn de 11 apparaten die vast in ons huist zitten, deze moeten gezocht worden waar die ergens staan in onze lijst
#vervolgens moet die led branden als er 1 staat bij dat specifiek machine


#lijst met eerst de namen en vervolgens 24 uren verder begint dan de getalletjes

werking_leds = [[1,0,0,1],['wasmachine', 'verwarming', ]]


for i in range(len(werking_leds[0])):


LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(1)
GPIO.output(LED_PIN, GPIO.LOW)

GPIO.cleanup()
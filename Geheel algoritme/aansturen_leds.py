import RPi.GPIO as GPIO #dit gaat enkel op de raspberry zelf enkel kunnen geïnstalleerd worden
import time


LED_PIN_wasmachine = 17 #dit is het GPIO nummer en niet pinnummer
LED_PIN_verwarming = 27
werking_leds = [['wasmachine', 'verwarming'],[1,0]]
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_wasmachine, GPIO.OUT)
GPIO.setup(LED_PIN_verwarming, GPIO.OUT)
p = 1

#stel volgende lijst zijn de 11 apparaten die vast in ons huist zitten, deze moeten gezocht worden waar die ergens staan in onze lijst
#vervolgens moet die led branden als er 1 staat bij dat specifiek machine

#lijst met eerst de namen en vervolgens 24 uren verder begint dan de getalletjes
while p == 1:#while loop is om verschil te kunnen zien tussen aan en uit

    for i in range(len(werking_leds[0])):
        if werking_leds[0][i] == 'wasmachine':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_wasmachine, GPIO.HIGH)
                werking_leds[1][i] = 0 #om te testen
            else:
                GPIO.output(LED_PIN_wasmachine, GPIO.LOW)
                werking_leds[1][i] = 1#om te testen

        if werking_leds[0][i] == 'verwarming':
            if werking_leds[1][i] == 1:
                GPIO.output(LED_PIN_verwarming, GPIO.HIGH)
                werking_leds[1][i] = 0#om te testen
            else:
                GPIO.output(LED_PIN_verwarming, GPIO.LOW)
                werking_leds[1][i] = 1#om te testen

    time.sleep(2)
    #volgende code is gwn om het ledje te laten veranderen

#GPIO.cleanup() #dit zal ervoor zorgen dat de pinnen die output waren dat niet meer waren voor moest je er iets anders mee willen doen



#Hier komt de finale code

'''
import RPi.GPIO as GPIO #dit gaat enkel op de raspberry zelf enkel kunnen geïnstalleerd worden

LED_PIN_wasmachine = 17
LED_PIN_verwarming = 27
LED_PIN_droogkast = 22
LED_PIN_frigo = 10
LED_PIN_diepvries = 9
LED_PIN_vaatwas = 23
LED_PIN_batterij_ontladen = 24
LED_PIN_batterij_opladen = 25
LED_PIN_auto = 8



werking_leds = #een lijst die als volgend is opgebouwd : [[namen apparaten],[1,0 etc]]
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_wasmachine, GPIO.OUT)
GPIO.setup(LED_PIN_verwarming, GPIO.OUT)
GPIO.setup(LED_PIN_droogkast, GPIO.OUT)
GPIO.setup(LED_PIN_frigo, GPIO.OUT)
GPIO.setup(LED_PIN_diepvries, GPIO.OUT)
GPIO.setup(LED_PIN_vaatwas, GPIO.OUT)
GPIO.setup(LED_PIN_batterij_ontladen, GPIO.OUT)
GPIO.setup(LED_PIN_batterij_opladen, GPIO.OUT)
GPIO.setup(LED_PIN_auto, GPIO.OUT)


for i in range(len(werking_leds[0])):
    if werking_leds[0][i] == 'wasmachine':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_wasmachine, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_wasmachine, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen

    if werking_leds[0][i] == 'verwarming':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_verwarming, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_verwarming, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
                        
            
    if werking_leds[0][i] == 'droogkast':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_droogkast, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_droogkast, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
    
    if werking_leds[0][i] == 'frigo':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_frigo, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_frigo, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
    if werking_leds[0][i] == 'diepvries':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_diepvries, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_diepvries, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
    if werking_leds[0][i] == 'vaatwas':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_vaatwas, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_vaatwas, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
    if werking_leds[0][i] == 'batterij_ontladen': #met rode LED
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_batterij_ontladen, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_batterij_ontladen, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
    if werking_leds[0][i] == 'batterij_opladen': #met groende LED
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_batterij_opladen, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_batterij_opladen, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen
            
    if werking_leds[0][i] == 'auto':
        if werking_leds[1][i] == 1:
            GPIO.output(LED_PIN_auto, GPIO.HIGH)
            werking_leds[1][i] = 0  # om te testen
        else:
            GPIO.output(LED_PIN_auto, GPIO.LOW)
            werking_leds[1][i] = 1  # om te testen


'''
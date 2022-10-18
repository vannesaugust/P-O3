toestel = str(input("welk toestel?"))
verbruik = int(input("hoeveel verbruikt toestel?"))
bijhoudlijst = []
while toestel != 'stop':
    bijhoudlijst = bijhoudlijst + [[toestel, verbruik]]
    toestel = str(input("welk toestel?"))
    verbruik = int(input("hoeveel verbruikt toestel?"))



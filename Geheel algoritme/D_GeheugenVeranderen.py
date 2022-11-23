import sqlite3
#######################################################################################################################
lijst_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = ['/','/', '/', 5, 4, 3]
lijst_uren_na_elkaar = ['/','/', '/',5,'/', 3]
lijst_verbruiken = [15, -15, 10, 14, 10, 12]
lijst_deadlines = ['/','/','/', 10, 11, 12]
lijst_beginuur = ['/','/', '/', 3, 6, 4]
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]
lijst_exacte_uren = [['/'], ['/'], ['/'], ['/'], ['/'], ['/']]
"""
lijst_apparaten = ['Fridge', 'Elektric Bike', 'Elektric Car', 'Dishwasher', 'Washing Manchine', 'Freezer']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = [2, 2, 2, 2, 3, 2]
lijst_uren_na_elkaar = [2, '/', '/', 2, 3, 2]
lijst_verbruiken = [30.2,12,100,52,85,13]
lijst_deadlines = [15,17,14,'/',23,14]
lijst_beginuur = ['/', '/', '/', '/', 6, '/']
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]
lijst_exacte_uren = [['/'], ['/'], ['/'], ['/'], ['/'], ['/']]
"""
aantal_dagen_in_gemiddelde = 3

verbruik_gezin_totaal = [[3 for i in range(aantal_dagen_in_gemiddelde)] for p in range(24)]

vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]


lijst_batterij_namen = ["thuisbatterij"]
lijst_batterij_bovengrens = [200]
lijst_batterij_opgeslagen_energie = [10]
begin_temperatuur_huis = 20
aantal_zonnepanelen = 0  # IN DATABASE
oppervlakte_zonnepanelen = 0  # IN DATABASE
rendement_zonnepanelen = 0.20
min_temperatuur = 17  # IN DATABASE
max_temperatuur = 21  # IN DATABASE
# huidige_temperatuur = 20  # IN DATABASE
verbruik_warmtepomp = 200  # IN DATABASE
COP = 4  # IN DATABASE
U_waarde = 0.4  # IN DATABASE
oppervlakte_muren = 50  # IN DATABASE
volume_huis = 500  # IN DATABASE
#######################################################################################################################
# Ter illustratie
print("------------geheugen_veranderen------------")
print("*****Vooraf ingestelde lijsten*****")
print(lijst_apparaten)
print(lijst_verbruiken)
print(lijst_exacte_uren)
print(lijst_beginuur)
print(lijst_deadlines)
print(lijst_aantal_uren)
print(lijst_uren_na_elkaar)
print(lijst_batterij_bovengrens)
print(lijst_batterij_namen)
print(lijst_batterij_opgeslagen_energie)
print(begin_temperatuur_huis)
#######################################################################################################################
def uur_omzetten(exacte_uren1apparaat):
    # functie om exacte uren om te zetten in een string die makkelijk leesbaar is om later terug om te zetten
    # De string die in de database wordt gestopt moet met een accent beginnen en eindigen, anders kan sqlite geen
    # symbolen lezen
    string = "'"
    # Gaat alle apparaten af en kijkt naar de lijst van exacte uren van dat bepaalt apparaat
    for i2 in range(len(exacte_uren1apparaat)):
        # Als er geen uur in die lijst staat moet er een nul in de database gezet worden
        if exacte_uren1apparaat[i2] == "/":
            return str(0)
        # Anders aan de begin-string het uur toevoegen + een onderscheidingsteken
        else:
            string = string + str(exacte_uren1apparaat[i2]) + ":"
    # Als er geen uren meer toegevoegd moeten worden, moet het laatste onderscheidingsteken uit de string en moet een
    # accent toegevoegd worden
    string = string[0:-1] + "'"
    return string
#######################################################################################################################
# Verbinding maken met de database + cursor plaatsen (wss om te weten in welke database je wilt werken?)
con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
#######################################################################################################################
# Voor het geheugen
######################
# Aantal apparaten die in gebruik zijn berekenen
lengte = len(lijst_apparaten)
# Voor ieder apparaat de nodige gegevens in de database zetten
for i in range(lengte):
    # In de database staat alles in de vorm van een string
    NummerApparaat = str(i)
    # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
    naam = "'" + lijst_apparaten[i] + "'"
    # Voer het volgende uit
    cur.execute("UPDATE Geheugen SET Apparaten =" + naam +
                " WHERE Nummering =" + NummerApparaat)
    # Wanneer er geen gegevens in de lijst staan, staat die aangegeven met een "/"
    # Als dit het geval is, plaatsen we een 0 in de database die in TupleToList terug naar een "/" wordt omgezet
    if lijst_verbruiken[i] == "/":
        cur.execute("UPDATE Geheugen SET Wattages =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET Wattages =" + str(lijst_verbruiken[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    # Wanneer je een special teken gebruikt moet je het als een tuple ingeven met speciale notatie
    # uur_omzetten zorgt er voor dat dit op een overzichtelijke manier kan
    cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(lijst_exacte_uren[i]) +
                " WHERE Nummering =" + NummerApparaat)
    if lijst_beginuur[i] == "/":
        cur.execute("UPDATE Geheugen SET BeginUur =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET BeginUur =" + str(lijst_beginuur[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if lijst_deadlines[i] == "/":
        cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(lijst_deadlines[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if lijst_aantal_uren[i] == "/":
        cur.execute("UPDATE Geheugen SET UrenWerk =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET UrenWerk =" + str(lijst_aantal_uren[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if lijst_uren_na_elkaar[i] == "/":
        cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(lijst_uren_na_elkaar[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET SoortApparaat =" + "'" + lijst_soort_apparaat[i] + "'" +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET RememberSettings =" + str(lijst_remember_settings[i]) +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET Status =" + str(lijst_status[i]) +
                " WHERE Nummering =" + NummerApparaat)
#######################################################################################################################
# Voor zonnepanelen
######################
cur.execute("UPDATE Zonnepanelen SET Aantal =" + str(aantal_zonnepanelen))
cur.execute("UPDATE Zonnepanelen SET Oppervlakte =" + str(oppervlakte_zonnepanelen))
cur.execute("UPDATE Zonnepanelen SET Rendement =" + str(rendement_zonnepanelen))
#######################################################################################################################
# Voor de batterijen
######################
lengte2 = len(lijst_batterij_namen)
for i2 in range(lengte2):
    # In de database staat alles in de vorm van een string
    NummerApparaat = str(i2)
    # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
    naam = "'" + lijst_batterij_namen[i2] + "'"
    # Voer het volgende uit
    cur.execute("UPDATE Batterijen SET NamenBatterijen =" + naam +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Batterijen SET MaxEnergie =" + str(lijst_batterij_bovengrens[i2]) +
                " WHERE Nummering =" + NummerApparaat)
    if lijst_batterij_opgeslagen_energie[i2] == "/":
        cur.execute("UPDATE Batterijen SET OpgeslagenEnergie =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Batterijen SET OpgeslagenEnergie =" + str(lijst_batterij_opgeslagen_energie[i2]) +
                    " WHERE Nummering =" + NummerApparaat)
#######################################################################################################################
# Voor de temperatuur
######################
cur.execute("UPDATE Huisgegevens SET TemperatuurHuis =" + str(begin_temperatuur_huis))
cur.execute("UPDATE Huisgegevens SET MinTemperatuur =" + str(min_temperatuur))
cur.execute("UPDATE Huisgegevens SET MaxTemperatuur =" + str(max_temperatuur))
cur.execute("UPDATE Huisgegevens SET VerbruikWarmtepomp =" + str(verbruik_warmtepomp))
cur.execute("UPDATE Huisgegevens SET COP =" + str(COP))
cur.execute("UPDATE Huisgegevens SET UWaarde =" + str(U_waarde))
cur.execute("UPDATE Huisgegevens SET OppervlakteMuren =" + str(oppervlakte_muren))
cur.execute("UPDATE Huisgegevens SET VolumeHuis =" + str(volume_huis))
#######################################################################################################################
# Is nodig om de uitgevoerde veranderingen op te slaan
con.commit()
#######################################################################################################################
# Ter illustratie
print("*****Lijsten uit de database*****")
def print_lijsten():
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT Wattages FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT BeginUur FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT SoortApparaat FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT RememberSettings FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT Status FROM Geheugen")
    print(res.fetchall())

    res = cur.execute("SELECT Aantal FROM Zonnepanelen")
    print(res.fetchall())
    res = cur.execute("SELECT Oppervlakte FROM Zonnepanelen")
    print(res.fetchall())
    res = cur.execute("SELECT Rendement FROM Zonnepanelen")
    print(res.fetchall())

    res = cur.execute("SELECT NamenBatterijen FROM Batterijen")
    print(res.fetchall())
    res = cur.execute("SELECT MaxEnergie FROM Batterijen")
    print(res.fetchall())
    res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
    print(res.fetchall())

    res = cur.execute("SELECT TemperatuurHuis FROM Huisgegevens")
    print(res.fetchall())
print_lijsten()

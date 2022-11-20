import sqlite3
# importeren van lijsten die we doorkrijgen uit de interface
from I_MainApplication import lijst_apparaten
from I_MainApplication import lijst_verbruiken
from I_MainApplication import lijst_exacte_uren
from I_MainApplication import lijst_beginuur
from I_MainApplication import lijst_deadlines
from I_MainApplication import lijst_aantal_uren
from I_MainApplication import lijst_uren_na_elkaar
from I_MainApplication import lijst_batterij_bovengrens
from I_MainApplication import lijst_batterij_namen
from I_MainApplication import lijst_batterij_opgeslagen_energie
from I_MainApplication import begin_temperatuur_huis
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
"""
namen_apparaten = ["droogkast", 'robotmaaier', 'wasmachine', 'vaatwasser']
wattages_apparaten = [2500, 1700, 2700, 2100]
voorwaarden_apparaten_exacte_uren = [['/'], [1,7], [1], [1,1]]  # moet op deze uren werken
finale_tijdstip = [10, 10, 10, 11]  # wanneer toestel zeker klaar moet zijn
uur_werk_per_apparaat = [1, 2, 4, 3]  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer
uren_na_elkaar = [1, '/', 4, '/']
begin_uur = [1,1,1,1]
"""


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


# Verbinding maken met de database + cursor plaatsen (wss om te weten in welke database je wilt werken?)
con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
######################
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
######################
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
######################
# Voor de temperatuur
######################
cur.execute("UPDATE Huisgegevens SET TemperatuurHuis =" + str(begin_temperatuur_huis) +
            " WHERE Nummering =" + "0")
# Is nodig om de uitgevoerde veranderingen op te slaan
con.commit()

# Ter illustratie
print("*****Lijsten uit de database*****")
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
res = cur.execute("SELECT NamenBatterijen FROM Batterijen")
print(res.fetchall())
res = cur.execute("SELECT MaxEnergie FROM Batterijen")
print(res.fetchall())
res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
print(res.fetchall())

# oude code
'''
if exacte_uren1apparaat[i2] <= 9:
    string = string + "0" + str(exacte_uren1apparaat[i2]) + ":"
else:
    string = string + str(exacte_uren1apparaat[i2]) + ":"
'''
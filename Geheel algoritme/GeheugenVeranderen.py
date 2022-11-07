import sqlite3
# importeren van lijsten die we doorkrijgen uit de interface
from lijsten import namen_apparaten
from lijsten import wattages_apparaten
from lijsten import voorwaarden_apparaten_exacte_uren
from lijsten import finale_tijdstip
from lijsten import uur_werk_per_apparaat
from lijsten import uren_na_elkaar
from lijsten import begin_uur


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
con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()
# Aantal apparaten die in gebruik zijn berekenen
lengte = len(namen_apparaten)
# Voor ieder apparaat de nodige gegevens in de database zetten
for i in range(lengte):
    # In de database staat alles in de vorm van een string
    NummerApparaat = str(i)
    # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
    naam = "'" + namen_apparaten[i] + "'"
    # Voer het volgende uit
    cur.execute("UPDATE Geheugen SET Apparaten =" + naam +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET Wattages =" + str(wattages_apparaten[i]) +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(voorwaarden_apparaten_exacte_uren[i]) +
                " WHERE Nummering =" + NummerApparaat)
    # Wanneer er geen gegevens in de lijst staan, staat die aangegeven met een "/"
    # Als dit het geval is, plaatsen we een 0 in de database die in TupleToList terug naar een "/" wordt omgezet
    if begin_uur[i] == "/":
        cur.execute("UPDATE Geheugen SET BeginUur =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET BeginUur =" + str(begin_uur[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if finale_tijdstip[i] == "/":
        cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(finale_tijdstip[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if uur_werk_per_apparaat[i] == "/":
        cur.execute("UPDATE Geheugen SET UrenWerk =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET UrenWerk =" + str(uur_werk_per_apparaat[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    if uren_na_elkaar[i] == "/":
        cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
    else:
        cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(uren_na_elkaar[i]) +
                    " WHERE Nummering =" + NummerApparaat)
# Is nodig om de uitgevoerde veranderingen op te slaan
con.commit()

# Ter illustratie
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

# oude code
'''
if exacte_uren1apparaat[i2] <= 9:
    string = string + "0" + str(exacte_uren1apparaat[i2]) + ":"
else:
    string = string + str(exacte_uren1apparaat[i2]) + ":"
'''
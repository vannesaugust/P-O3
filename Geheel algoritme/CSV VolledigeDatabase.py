import csv
import sqlite3
# Altijd connecteren met de database als je deze wilt gebruiken
con = sqlite3.connect("VolledigeDatabase.db")
# Code dat nodig is om de andere opdrachten te kunnen laten runnen
cur = con.cursor()
# Aparte tabellen maken met een het aantal kolommen dat je wilt
cur.execute("CREATE TABLE Stroomprijzen(DatumBelpex, Prijs)")
cur.execute("CREATE TABLE Weer(DatumWeer, Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse)")
cur.execute("CREATE TABLE Geheugen(Nummering, Apparaten, Wattages, ExacteUren, BeginUur, FinaleTijdstip, UrenWerk, UrenNaElkaar)")
cur.execute("CREATE TABLE Zonnepanelen(Aantal)")
cur.execute("CREATE TABLE Batterijen(Soorten, MaxEnergie, OpgeslagenEnergie)")
# CSV-bestanden open, dit kan door de import van csv
with open("./Belpex2021-2022.csv", 'r') as file:
    # Gaat rij per rij af en splits de gegevens wanneer het de puntkomma tegenkomt
    csvreaderBelpex = csv.reader(file, delimiter=';')
    # Houdt 2 kolommen over en elk komt op een plaats van een vraagteken
    cur.executemany("INSERT INTO Stroomprijzen VALUES(?, ?)", csvreaderBelpex)
with open("./weather_data.csv", 'r') as file:
    csvreaderWeather = csv.reader(file)
    cur.executemany("INSERT INTO Weer VALUES(?, ?, ?, ?, ?)", csvreaderWeather)
# Op deze manier kunnen er maximaal 30 apparaten toegevoegd worden
lengte = 10
# Aanmaken van een nul matrix
ZeroMatrix = []
for i in range(lengte):
    # In de eerste kolom is een nummering nodig om later naar de juiste positie te verwijzen
    Row = [i]
    # Range(7) want er zijn 8 kolommen die aangemaakt moeten worden
    for i2 in range(7):
        # Geven alles voorlopig een nul om later via de interface het deze plaatste te vervangen naar het juiste
        Row.append(0)
    ZeroMatrix.append(Row)
cur.executemany("INSERT INTO Geheugen VALUES(?, ?, ?, ?, ?, ?, ?, ?)", ZeroMatrix)

AntalZonnepanelen = "6"
cur.executemany("INSERT INTO Zonnepanelen VALUES(?)", AntalZonnepanelen)

SoortenBatterijen = ["Thuisbatterij", "Auto"]
lengte2 = len(SoortenBatterijen)

ZeroMatrix2 = []
for i3 in range(lengte2):
    Row = [i3]
    for i4 in range(2):
        Row.append(0)
    ZeroMatrix2.append(Row)
cur.executemany("INSERT INTO Batterijen VALUES(?, ?, ?)", ZeroMatrix2)

# Als je iets in de database verandert moet je altijd con.commit() gebruiken zodat het goed wordt opgeslagen
con.commit()

# Op deze manier kan je kolommen van gegevens uit een bepaalde tabel halen
res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
print(res.fetchall())

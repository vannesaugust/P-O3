import csv
import sqlite3

from lijsten import namen_apparaten as NamenApparatenVAR

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

cur.execute("CREATE TABLE Stroomprijzen(DatumBelpex, Prijs)")
cur.execute("CREATE TABLE Weer(DatumWeer, Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse)")
cur.execute("CREATE TABLE Geheugen(Nummering, Apparaten, Wattages, ExacteUren, FinaleTijdstip, UrenWerk)")
cur.execute("CREATE TABLE Zonnepanelen(Aantal)")
cur.execute("CREATE TABLE Batterijen(Soorten, MaxEnergie, OpgeslagenEnergie)")


with open("./Belpex2021-2022.csv", 'r') as file:
    csvreaderBelpex = csv.reader(file, delimiter=';')
    cur.executemany("INSERT INTO Stroomprijzen VALUES(?, ?)", csvreaderBelpex)

with open("./weather_data.csv", 'r') as file:
    csvreaderWeather = csv.reader(file)
    cur.executemany("INSERT INTO Weer VALUES(?, ?, ?, ?, ?)", csvreaderWeather)

lengte = len(NamenApparatenVAR)

ZeroMatrix = []
for i in range(lengte):
    Row = [i]
    for i2 in range(5):
        Row.append(0)
    ZeroMatrix.append(Row)
cur.executemany("INSERT INTO Geheugen VALUES(?, ?, ?, ?, ?, ?)", ZeroMatrix)

AntalZonnepanelen = "6"
cur.executemany("INSERT INTO Zonnepanelen VALUES(?)", AntalZonnepanelen)

SoortenBatterijen = ["Thuisbatterij", "Auto"]
lengte2 = len(SoortenBatterijen)

ZeroMatrix2 = []
for i in range(lengte2):
    Row = [i]
    for i2 in range(2):
        Row.append(0)
    ZeroMatrix2.append(Row)
cur.executemany("INSERT INTO Batterijen VALUES(?, ?, ?)", ZeroMatrix2)

con.commit()

res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
print(res.fetchall())

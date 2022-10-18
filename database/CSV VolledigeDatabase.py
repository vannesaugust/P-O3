import csv
import sqlite3
import numpy
import numpy as np

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()
cur.execute("CREATE TABLE Stroomprijzen(DatumBelpex, Prijs)")
cur.execute("CREATE TABLE Weer(DatumWeer, Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse)")
cur.execute("CREATE TABLE Geheugen(Tijd, a, b, c, d, e, f, g, h, i, j)")

with open("Belpex2021-2022.csv", 'r') as file:
  csvreaderBelpex = csv.reader(file, delimiter=';')
  cur.executemany("INSERT INTO Stroomprijzen VALUES(?, ?)", csvreaderBelpex)

with open("weather_data.csv", 'r') as file:
  csvreaderWeather = csv.reader(file)
  cur.executemany("INSERT INTO Weer VALUES(?, ?, ?, ?, ?)", csvreaderWeather)

ZeroMatrix = []
for i in range(24):
    Row = [i]
    for i2 in range(10):
        Row.append(0)
    ZeroMatrix.append(Row)
cur.executemany("INSERT INTO Geheugen VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ZeroMatrix)
con.commit()

res = cur.execute("SELECT a FROM Geheugen")
print(res.fetchall())

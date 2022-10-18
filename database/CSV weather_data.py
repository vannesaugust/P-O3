import csv
import sqlite3

con = sqlite3.connect("WeatherDatabase.db")
cur = con.cursor()
cur.execute("CREATE TABLE WeatherDatabase(Date, WindSpeed, Temperature, RadiationDirect, RadiationDiffuse)")

with open("weather_data.csv", 'r') as file:
  csvreader = csv.reader(file)
  cur.executemany("INSERT INTO WeatherDatabase VALUES(?, ?, ?, ?, ?)", csvreader)

  con.commit()
res = cur.execute("SELECT Date FROM WeatherDatabase")
print(res.fetchall())
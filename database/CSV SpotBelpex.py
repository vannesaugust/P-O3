import csv
import sqlite3

con = sqlite3.connect("SpotBelpexDatabase.db")
cur = con.cursor()
cur.execute("CREATE TABLE SpotBelpexDatabase(Date, Euro)")

with open("./Belpex2022.csv", 'r') as file:
  csvreader = csv.reader(file, delimiter=';')
  cur.executemany("INSERT INTO SpotBelpexDatabase VALUES(?, ?)", csvreader)

  con.commit()
res = cur.execute("SELECT Date, Euro FROM SpotBelpexDatabase")
print(res.fetchall())




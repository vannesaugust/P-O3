import csv
import sqlite3
import numpy
import numpy as np

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

cur.execute("UPDATE Geheugen SET a = 1 WHERE tijd = 5")
con.commit()

res = cur.execute("SELECT a FROM Geheugen")
print(res.fetchall())
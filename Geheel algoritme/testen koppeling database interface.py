import sqlite3

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM Geheugen")
print(res.fetchall())

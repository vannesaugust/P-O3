import sqlite3


con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

cur.execute("UPDATE Geheugen SET tijd = 1 WHERE tijd = 2")
con.commit()

res = cur.execute("SELECT tijd FROM Geheugen")
print(res.fetchall())
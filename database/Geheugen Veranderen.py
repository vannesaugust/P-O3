import sqlite3

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT Apparaten FROM Geheugen")
lengte = len(res.fetchall())

from lijsten import namen_apparaten
from lijsten import wattages_apparaten
from lijsten import voorwaarden_apparaten_exacte_uren
from lijsten import finale_tijdstip
from lijsten import uur_werk_per_apparaat

for i in range(lengte-1):
    NummerApparaat = str(i)
    cur.execute("UPDATE Geheugen SET Wattages =" + str(wattages_apparaten[i]) + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execute("SELECT Wattages FROM Geheugen")
    print(res.fetchall())
    cur.execute("UPDATE Geheugen SET ExacteUren =" + "7.8" + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execut    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())e("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    cur.execute("UPDATE Geheugen SET ExacteUren =" + str(voorwaarden_apparaten_exacte_uren[i]) + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(finale_tijdstip[i]) + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())
    cur.execute("UPDATE Geheugen SET UrenWerk =" + str(uur_werk_per_apparaat[i]) + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    print(res.fetchall())
    cur.execute("UPDATE Geheugen SET Apparaten =" + str(namen_apparaten[i]) + " WHERE Apparaten =" + NummerApparaat)
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    print(res.fetchall())


con.commit()

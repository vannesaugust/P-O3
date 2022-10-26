import sqlite3

from lijsten import namen_apparaten
from lijsten import wattages_apparaten
from lijsten import voorwaarden_apparaten_exacte_uren
from lijsten import finale_tijdstip
from lijsten import uur_werk_per_apparaat


def uur_omzetten(exacte_uren1apparaat):
    string = "'"
    for i2 in range(len(exacte_uren1apparaat)):
        if exacte_uren1apparaat[i2] <= 9:
            string = string + "0" + str(exacte_uren1apparaat[i2]) + ":"
        else:
            string = string + str(exacte_uren1apparaat[i2]) + ":"
    string = string[0:-1] + "'"
    return string


con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT Nummering FROM Geheugen")
lengte = len(res.fetchall())

for i in range(lengte):
    NummerApparaat = str(i)
    naam = "'" + namen_apparaten[i] + "'"
    cur.execute("UPDATE Geheugen SET Apparaten =" + naam +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET Wattages =" + str(wattages_apparaten[i]) +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(voorwaarden_apparaten_exacte_uren[i]) +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(finale_tijdstip[i]) +
                " WHERE Nummering =" + NummerApparaat)
    cur.execute("UPDATE Geheugen SET UrenWerk =" + str(uur_werk_per_apparaat[i]) +
                " WHERE Nummering =" + NummerApparaat)

con.commit()
# Ter illustratie
res = cur.execute("SELECT Apparaten FROM Geheugen")
print(res.fetchall())
res = cur.execute("SELECT Wattages FROM Geheugen")
print(res.fetchall())
res = cur.execute("SELECT ExacteUren FROM Geheugen")
print(res.fetchall())
res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
print(res.fetchall())
res = cur.execute("SELECT UrenWerk FROM Geheugen")
print(res.fetchall())

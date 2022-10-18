import sqlite3

uur = int(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))

if len(maand) == 1:
    maand = "0" + maand

if int(maand) >= 9:
    tuple = (dag + "/" + maand + "/" + "2022 " + str(uur) + ":00:00",)
else:
    tuple = (dag + "/" + maand + "/" + "2021 " + str(uur) + ":00:00",)

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
Dates = res.fetchall()

index = [tup for tup in Dates].index(tuple)

res = cur.execute("SELECT Prijs FROM Stroomprijzen")
Prijzen = res.fetchall()

Prijzen24uur = []
for i in range(0, 24):
    prijs = Prijzen[index - i]
    prijsString = str(prijs)
    prijsCijfers = prijsString[6:-3]
    print(prijsCijfers)
    Prijzen24uur.append(prijsCijfers)
print(Prijzen24uur)


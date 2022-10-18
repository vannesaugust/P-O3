import sqlite3

uur = str(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))

if len(maand) == 1:
    maand = "0" + maand

if int(maand) >= 9:
    tupleBelpex = (dag + "/" + maand + "/" + "2021 " + uur + ":00:00",)
else:
    tupleBelpex = (dag + "/" + maand + "/" + "2022 " + uur + ":00:00",)

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
Dates = res.fetchall()

index = [tup for tup in Dates].index(tupleBelpex)

res = cur.execute("SELECT Prijs FROM Stroomprijzen")
Prijzen = res.fetchall()

Prijzen24uur = []
for i in range(0, 24):
    prijs = Prijzen[index - i]
    prijsString = str(prijs)
    prijsCijfers = prijsString[6:-3]
    prijsCijfersPunt = prijsCijfers.replace(",", ".")
    prijsFloat = float(prijsCijfersPunt)
    Prijzen24uur.append(prijsFloat)
print(Prijzen24uur)

if len(maand) == 1:
    maand = "0" + maand
if len(dag) == 1:
    dag = "0" + dag
if len(uur) == 1:
    uur = "0" + uur

tupleWeer = ( "2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT DatumWeer FROM Weer")
Dates = res.fetchall()

index = [tup for tup in Dates].index(tupleWeer)

res = cur.execute("SELECT Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse FROM Weer")
alleGegevens = res.fetchall()

TemperatuurList = []
RadiatieList = []
for i in range(0, 24):
    dagGegevens = alleGegevens[index + i]
    TemperatuurList.append(float(dagGegevens[0]))
    RadiatieList.append(float(dagGegevens[1]) + float(dagGegevens[2]))
Gegevens24uur = [TemperatuurList, RadiatieList]
print(Gegevens24uur)
import sqlite3

uur = str(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))
if len(maand) == 1:
    maand = "0" + maand
if len(dag) == 1:
    dag = "0" + dag
if len(uur) == 1:
    uur = "0" + uur

tuple = ( "2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT DatumWeer FROM Weer")
Dates = res.fetchall()

index = [tup for tup in Dates].index(tuple)

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
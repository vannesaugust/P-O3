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

con = sqlite3.connect("WeatherDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT Date FROM WeatherDatabase")
Dates = res.fetchall()

index = [tup for tup in Dates].index(tuple)

res = cur.execute("SELECT Temperature, RadiationDirect, RadiationDiffuse FROM WeatherDatabase")
alleGegevens = res.fetchall()
dagGegevens = alleGegevens[index]

dagGegevensList = [float(dagGegevens[0]), float(dagGegevens[1]) + float(dagGegevens[2])]

print(dagGegevensList)


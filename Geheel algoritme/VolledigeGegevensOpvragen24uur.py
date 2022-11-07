import sqlite3
# Datum die wordt ingegeven in de interface
uur = str(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))
#################################
# Deel 1 Gegevens Belpex opvragen
#################################

# In de Belpex database staan maanden aangeduid met twee cijfers bv: 07 of 11
if len(maand) == 1:
    maand = "0" + maand
# Datums lopen van 1 oktober 2021 tot 30 september
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
    prijsFloat = float(prijsCijfersPunt) / 1000000
    Prijzen24uur.append(prijsFloat)
# Print lijst met de prijzen van de komende 24 uur
print(Prijzen24uur)

#################################
# Deel 2 Gegevens Weer opvragen
#################################
if len(maand) == 1:
    maand = "0" + maand
if len(dag) == 1:
    dag = "0" + dag
if len(uur) == 1:
    uur = "0" + uur

tupleWeer = ("2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

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
    TemperatuurList.append(float(dagGegevens[1]))
    RadiatieList.append(float(dagGegevens[2]) + float(dagGegevens[3]))
Gegevens24uur = [TemperatuurList, RadiatieList]
# Print lijst onderverdeeld in een lijst met de temperaturen van de komende 24 uur
#                              en een lijst voor de radiatie van de komende 24 uur
print(Gegevens24uur)

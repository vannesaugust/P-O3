import sqlite3

uur = int(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))
if len(maand) == 1:
    maand = "0" + maand

con = sqlite3.connect("SpotBelpexDatabase.db")
cur = con.cursor()
Prijzen24uur = []
for i in range(0, 24):
    if uur == 24:
        dag = dag + 1
    else:
        uur = uur + i
    string = "'" + dag + "/" + maand + "/" + "2022 " + str(uur + i) + ":00:00" + "'"

    res = cur.execute("SELECT Euro FROM SpotBelpexDatabase WHERE Date = " + string)
    prijs = res.fetchall()[0]
    prijsString = str(prijs)
    prijsCijfers = prijsString[6:-3]
    print(prijsCijfers)
    Prijzen24uur.append(prijsCijfers)
print(Prijzen24uur)


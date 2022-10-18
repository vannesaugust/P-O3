import sqlite3

uur = int(input("Geef het uur: "))
dag = str(input("Geef de dag: "))
maand = str(input("Geef de maand: "))
if len(maand) == 1:
    maand = "0" + maand

string = "'" + dag + "/" + maand + "/" + "2022 " + str(uur) + ":00:00" + "'"

con = sqlite3.connect("SpotBelpexDatabase.db")
cur = con.cursor()
res = cur.execute("SELECT Date, Euro FROM SpotBelpexDatabase WHERE Date = " + string)
print(res.fetchall())

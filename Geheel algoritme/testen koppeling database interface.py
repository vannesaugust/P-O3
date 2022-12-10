import sqlite3

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM Stroomprijzen")
# print(res.fetchall())
res = cur.execute("SELECT Prijs FROM Stroomprijzen WHERE DatumBelpex LIKE '%/09/2022%'")
print("voor een maand:")
waarden_maand = res.fetchall()
print(waarden_maand)
totale_prijs = 0

for i in waarden_maand:
    prijs = i[0]
    print(prijs)
    prijs = prijs[4:]
    prijs = prijs[0:-3] + '.' + prijs[-2:]
    print(prijs)
    prijs = float(prijs)
    totale_prijs += prijs
gem_prijs = totale_prijs / len(waarden_maand)
print('gem_prijs is:')
print(gem_prijs)
print(len(waarden_maand))

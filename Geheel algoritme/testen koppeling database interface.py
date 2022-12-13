import sqlite3

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = cur.execute("SELECT Prijs FROM Stroomprijzen") # WHERE DatumBelpex LIKE '%23/12/2021%'")
Prijzen = res.fetchall()
print(Prijzen)
res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
Dates = res.fetchall()
tupleBelpex = ('11/12/2021 1:00:00',)
index = [tup for tup in Dates].index(tupleBelpex)
print(index)

'''
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
'''

Prijzen24uur = []
for i in range(0, 24):
    # Geeft de prijs op index -i
    prijs = Prijzen[index - i]
    # Database geeft altijd tuples terug dus eerst omzetten naar string
    prijsString = str(prijs)
    print("prijsstring")
    print(prijsString)
    # Het stuk waar geen informatie staat afsnijden
    prijsCijfers = prijsString[10:-3]
    # Komma vervangen naar een punt zodat het getal naar een float kan omgezet worden
    prijsCijfersPunt = prijsCijfers.replace(",", ".")
    # Delen door 1 000 om van MWh naar kWh te gaan
    prijsFloat = float(prijsCijfersPunt) / 1000
    # Toevoegen aan de rest van de prijzen
    Prijzen24uur.append(prijsFloat)
# Print lijst met de prijzen van de komende 24 uur
print("Prijzen24uur")
print(Prijzen24uur)


res1 = cur.execute("SELECT Prijs FROM Stroomprijzen WHERE DatumBelpex LIKE '%11/12/2021%'")
res2 = cur.execute("SELECT Prijs FROM Stroomprijzen WHERE DatumBelpex LIKE '%12/12/2021%'")
Prijzen = res2.fetchall()
Prijzen.append(res1.fetchall())
print(Prijzen)

Prijzen24uur = []
index = -1
for i in range(0, 24):
    # Geeft de prijs op index -i
    prijs = Prijzen[index - i]
    # Database geeft altijd tuples terug dus eerst omzetten naar string
    prijsString = str(prijs)
    # Het stuk waar geen informatie staat afsnijden
    prijsCijfers = prijsString[10:-3]
    # Komma vervangen naar een punt zodat het getal naar een float kan omgezet worden
    prijsCijfersPunt = prijsCijfers.replace(",", ".")
    # Delen door 1 000 om van MWh naar kWh te gaan
    prijsFloat = float(prijsCijfersPunt) / 1000
    # Toevoegen aan de rest van de prijzen
    Prijzen24uur.append(prijsFloat)
# Print lijst met de prijzen van de komende 24 uur
print("Prijzen24uur")
print(Prijzen24uur)

print("Prijzen24uur")
print(Prijzen24uur)
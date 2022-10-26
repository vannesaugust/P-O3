import sqlite3


def tuples_to_list(list_tuples, categorie):
    if categorie == "Apparaten":
        list_strings = [i[0] for i in list_tuples]
        return list_strings

    if categorie == "Wattages" or categorie == "FinaleTijdstip" or categorie == "UrenWerk":
        list_ints = [int(i[0]) for i in list_tuples]
        for i1 in range(len(list_ints)):
            if list_ints[i1] == 0:
                list_ints[i1] = "/"
        return list_ints

    if categorie == "ExacteUren":
        list_strings = [i[0] for i in list_tuples]
        list_ints = []
        for i2 in list_strings:
            lijst_uren = i2.split(":")
            lijst_uren_ints = []
            for uur in lijst_uren:
                lijst_uren_ints.append(int(uur))
            list_ints.append(lijst_uren_ints)
        return list_ints


con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()

res = cur.execute("SELECT Apparaten FROM Geheugen")
ListTuplesApparaten = res.fetchall()
Apparaten = tuples_to_list(ListTuplesApparaten, "Apparaten")
print(Apparaten)

res = cur.execute("SELECT Wattages FROM Geheugen")
ListTuplesWattages = res.fetchall()
Wattages = tuples_to_list(ListTuplesWattages, "Wattages")
print(Wattages)

res = cur.execute("SELECT ExacteUren FROM Geheugen")
ListTuplesExacteUren = res.fetchall()
ExacteUren = tuples_to_list(ListTuplesExacteUren, "ExacteUren")
print(ExacteUren)

res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
ListTuplesFinaleTijdstip = res.fetchall()
FinaleTijdstip = tuples_to_list(ListTuplesFinaleTijdstip, "FinaleTijdstip")
print(FinaleTijdstip)

res = cur.execute("SELECT UrenWerk FROM Geheugen")
ListTuplesUrenWerk = res.fetchall()
UrenWerk = tuples_to_list(ListTuplesUrenWerk, "UrenWerk")
print(UrenWerk)

import sqlite3


def tuples_to_list(ListTuples, categorie):
    List = []
    for i in range(len(ListTuples)):
        Tuple = ListTuples[i]
        String = str(Tuple)
        Slice = String[1:-2]

        if categorie == "Wattages" or categorie == "FinaleTijdstip" or categorie == "UrenWerk":
            End = int(Slice)
            if End == 0:
                List.append("")
            List.append(End)

        if categorie == "ExacteUren":
            Slice2 = Slice[1:-1]
            LijstUren = Slice2.split(":")
            LijstUrenInt = []
            for uur in LijstUren:
                LijstUrenInt.append(int(uur))
            List.append(LijstUrenInt)

        if categorie == "Apparaten":
            Slice2 = Slice[1:-1]
            List.append(Slice2)

    return List

onderwerpen = ["Wattages", "ExacteUren", "FinaleTijdstip", "UrenWerk", "Apparaten"]

con = sqlite3.connect("VolledigeDatabase.db")
cur = con.cursor()


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

res = cur.execute("SELECT Apparaten FROM Geheugen")
ListTuplesApparaten = res.fetchall()
Apparaten = tuples_to_list(ListTuplesApparaten, "Apparaten")
print(Apparaten)
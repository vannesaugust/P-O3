import sqlite3


def tuples_to_list(list_tuples, categorie, index_slice):
    # list_tuples = lijst van gegevens uit een categorie die de database teruggeeft
    # In de database staat alles in lijsten van tuples, maar aangezien het optimalisatie-algoritme met lijsten werkt
    # moeten we deze lijst van tuples nog omzetten naar een gewone lijst van strings of integers
    if categorie == "Apparaten":
        # zet alle tuples om naar strings
        list_strings = [i0[0] for i0 in list_tuples]
        for i1 in range(len(list_strings)):
            if list_strings[i1] == 0:
                list_strings = list_strings[:i1]
                return [list_strings, i1]
        return [list_strings, i1+1]

    if categorie == "Wattages" or categorie == "FinaleTijdstip" \
            or categorie == "UrenWerk" or categorie == "UrenNaElkaar" or categorie == "BeginUur":
        # Zet alle tuples om naar integers
        list_ints = [int(i2[0]) for i2 in list_tuples]
        list_ints = list_ints[:index_slice]
        # Gaat alle integers af en vervangt alle nullen naar "/"
        for i3 in range(len(list_ints)):
            if list_ints[i3] == 0:
                list_ints[i3] = "/"
        return list_ints

    if categorie == "ExacteUren":
        # Zet tuples om naar strings
        # Alle nullen worden wel als integers weergegeven
        list_strings = [i4[0] for i4 in list_tuples]
        list_strings = list_strings[:index_slice]
        list_ints = []
        # Als een string 0 wordt deze omgezet naar een "/"
        for i5 in list_strings:
            if i5 == 0:
                list_ints.append("/")
            else:
                # Splitst elke lijst waar een dubbelpunt in voorkomt zodat ieder uur nu apart in lijst_uren staat
                lijst_uren = i5.split(":")
                lijst_uren_ints = []
                # Overloopt alle uren en voegt deze toe aan de lijst van exacte uren die bij dat apparaat hoort
                for uur in lijst_uren:
                    lijst_uren_ints.append(int(uur))
                # Voegt de lijst van exacte uren van een apparaat bij de lijst van exacte uren van de andere apparaten
                list_ints.append(lijst_uren_ints)
        return list_ints


# Verbinding maken met de database + cursor plaatsen (wss om te weten in welke database je wilt werken?)
con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
# Zoekt de kolom Apparaten uit de tabel Geheugen
res = cur.execute("SELECT Apparaten FROM Geheugen")
# Geeft alle waarden in die kolom in de vorm van een lijst van tuples
ListTuplesApparaten = res.fetchall()
# Functie om lijst van tuples om te zetten naar lijst van strings of integers
index = -1
Antwoord = tuples_to_list(ListTuplesApparaten, "Apparaten", index)
Apparaten = Antwoord[0]
index = Antwoord[1]
# Idem vorige
res = cur.execute("SELECT Wattages FROM Geheugen")
ListTuplesWattages = res.fetchall()
Wattages = tuples_to_list(ListTuplesWattages, "Wattages", index)

res = cur.execute("SELECT ExacteUren FROM Geheugen")
ListTuplesExacteUren = res.fetchall()
ExacteUren = tuples_to_list(ListTuplesExacteUren, "ExacteUren", index)

res = cur.execute("SELECT BeginUur FROM Geheugen")
ListTuplesBeginUur = res.fetchall()
BeginUur = tuples_to_list(ListTuplesBeginUur, "BeginUur", index)

res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
ListTuplesFinaleTijdstip = res.fetchall()
FinaleTijdstip = tuples_to_list(ListTuplesFinaleTijdstip, "FinaleTijdstip", index)

res = cur.execute("SELECT UrenWerk FROM Geheugen")
ListTuplesUrenWerk = res.fetchall()
UrenWerk = tuples_to_list(ListTuplesUrenWerk, "UrenWerk", index)

res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
ListTuplesUrenNaElkaar = res.fetchall()
UrenNaElkaar = tuples_to_list(ListTuplesUrenNaElkaar, "UrenNaElkaar", index)


# Ter illustratie
print(Apparaten)
print(Wattages)
print(ExacteUren)
print(BeginUur)
print(FinaleTijdstip)
print(UrenWerk)
print(UrenNaElkaar)

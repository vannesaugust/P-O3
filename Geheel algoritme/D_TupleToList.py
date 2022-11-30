import sqlite3
#######################################################################################################################
def tuples_to_list(list_tuples, categorie, index_slice):
    # list_tuples = lijst van gegevens uit een categorie die de database teruggeeft
    # In de database staat alles in lijsten van tuples, maar aangezien het optimalisatie-algoritme met lijsten werkt
    # moeten we deze lijst van tuples nog omzetten naar een gewone lijst van strings of integers
    if categorie == "Apparaten" or categorie == "SoortApparaat" or categorie == "NamenBatterijen":
        # zet alle tuples om naar strings
        list_strings = [i0[0] for i0 in list_tuples]
        for i1 in range(len(list_strings)):
            if list_strings[i1] == 0:
                list_strings = list_strings[:i1]
                return list_strings
        return list_strings

    if categorie == "FinaleTijdstip" or categorie == "UrenWerk" or categorie == "UrenNaElkaar" or categorie == "BeginUur" \
            or categorie == "RememberSettings" or categorie == "Status":
        # Zet alle tuples om naar integers
        list_ints = [int(i2[0]) for i2 in list_tuples]
        if index_slice != -1:
            list_ints = list_ints[:index_slice]
        # Gaat alle integers af en vervangt alle nullen naar "/"
        for i3 in range(len(list_ints)):
            if list_ints[i3] == 0:
                list_ints[i3] = "/"
        return list_ints

    if categorie == "Wattages" or categorie == "MaxEnergie" or categorie == "OpgeslagenEnergie" or categorie == "Capaciteit":
        list_floats = [float(i2[0]) for i2 in list_tuples]
        if index_slice != -1:
            list_floats = list_floats[:index_slice]
        # Gaat alle integers af en vervangt alle nullen naar "/"
        for i3 in range(len(list_floats)):
            if list_floats[i3] == 0:
                list_floats[i3] = "/"
        return list_floats

    if categorie == "ExacteUren" or categorie == "VastVerbruik":
        # Zet tuples om naar strings
        # Alle nullen worden wel als integers weergegeven
        list_strings = [i4[0] for i4 in list_tuples]
        if index_slice != -1:
            list_strings = list_strings[:index_slice]
        list_ints = []
        # Als een string 0 wordt deze omgezet naar een "/"
        for i5 in list_strings:
            if i5 == 0:
                list_ints.append(["/"])
            else:
                # Splitst elke lijst waar een dubbelpunt in voorkomt zodat ieder uur nu apart in lijst_uren staat
                lijst_uren = i5.split(":")
                lijst_uren_ints = []
                # Overloopt alle uren en voegt deze toe aan de lijst van exacte uren die bij dat apparaat hoort
                if categorie == "ExacteUren":
                    for uur in lijst_uren:
                        lijst_uren_ints.append(int(uur))
                else:
                    for uur in lijst_uren:
                        lijst_uren_ints.append(float(uur))
                # Voegt de lijst van exacte uren van een apparaat bij de lijst van exacte uren van de andere apparaten
                list_ints.append(lijst_uren_ints)
        return list_ints
#######################################################################################################################
# ********** Tuples omzetten naar lijsten **********
# Verbinding maken met de database + cursor plaatsen (wss om te weten in welke database je wilt werken?)
con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
#######################################################################################################################
# Zoekt de kolom Apparaten uit de tabel Geheugen
res = cur.execute("SELECT Apparaten FROM Geheugen")
# Geeft alle waarden in die kolom in de vorm van een lijst van tuples
ListTuplesApparaten = res.fetchall()
# Functie om lijst van tuples om te zetten naar lijst van strings of integers
index = -1
Apparaten = tuples_to_list(ListTuplesApparaten, "Apparaten", index)
if len(Apparaten) != len(ListTuplesApparaten):
    index = len(Apparaten)
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

res = cur.execute("SELECT SoortApparaat FROM Geheugen")
ListTuplesSoortApparaat = res.fetchall()
SoortApparaat = tuples_to_list(ListTuplesSoortApparaat, "SoortApparaat", index)

res = cur.execute("SELECT Capaciteit FROM Geheugen")
ListTuplesCapaciteit = res.fetchall()
Capaciteit = tuples_to_list(ListTuplesCapaciteit, "Capaciteit", index)

res = cur.execute("SELECT RememberSettings FROM Geheugen")
ListTuplesRememberSettings = res.fetchall()
RememberSettings = tuples_to_list(ListTuplesRememberSettings, "RememberSettings", index)

res = cur.execute("SELECT Status FROM Geheugen")
ListTuplesStatus = res.fetchall()
Status = tuples_to_list(ListTuplesStatus, "Status", index)
#######################################################################################################################
index = -1
res = cur.execute("SELECT VastVerbruik FROM InfoLijsten24uur")
ListTuplesVastVerbruik = res.fetchall()
VastVerbruik = tuples_to_list(ListTuplesVastVerbruik, "VastVerbruik", index)
#######################################################################################################################
index = -1
res = cur.execute("SELECT Aantal FROM Zonnepanelen")
TupleAantal = res.fetchall()
Aantal = [int(i2[0]) for i2 in TupleAantal][0]

res = cur.execute("SELECT Oppervlakte FROM Zonnepanelen")
TupleOppervlakte = res.fetchall()
Oppervlakte = [float(i2[0]) for i2 in TupleOppervlakte][0]

res = cur.execute("SELECT Rendement FROM Zonnepanelen")
TupleRendement = res.fetchall()
Rendement = [float(i2[0]) for i2 in TupleRendement][0]
#######################################################################################################################
res = cur.execute("SELECT NaamBatterij FROM Batterijen")
TupleNaamBatterij = res.fetchall()
NaamBatterij = [str(i2[0]) for i2 in TupleNaamBatterij][0]

res = cur.execute("SELECT MaxEnergie FROM Batterijen")
TupleMaxEnergie = res.fetchall()
MaxEnergie = [float(i2[0]) for i2 in TupleMaxEnergie][0]

res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
TupleOpgeslagenEnergie = res.fetchall()
OpgeslagenEnergie = [float(i2[0]) for i2 in TupleOpgeslagenEnergie][0]
#######################################################################################################################
res = cur.execute("SELECT TemperatuurHuis FROM Huisgegevens")
TupleTemperatuurHuis = res.fetchall()
TemperatuurHuis = [float(i2[0]) for i2 in TupleTemperatuurHuis][0]

res = cur.execute("SELECT MinTemperatuur FROM Huisgegevens")
TupleMinTemperatuur = res.fetchall()
MinTemperatuur = [float(i2[0]) for i2 in TupleMinTemperatuur][0]

res = cur.execute("SELECT MaxTemperatuur FROM Huisgegevens")
TupleMaxTemperatuur = res.fetchall()
MaxTemperatuur = [float(i2[0]) for i2 in TupleMaxTemperatuur][0]

res = cur.execute("SELECT VerbruikWarmtepomp FROM Huisgegevens")
TupleVerbruikWarmtepomp = res.fetchall()
VerbruikWarmtepomp = [float(i2[0]) for i2 in TupleVerbruikWarmtepomp][0]

res = cur.execute("SELECT COP FROM Huisgegevens")
TupleCOP = res.fetchall()
COP = [float(i2[0]) for i2 in TupleCOP][0]

res = cur.execute("SELECT UWaarde FROM Huisgegevens")
TupleUWaarde = res.fetchall()
UWaarde = [float(i2[0]) for i2 in TupleUWaarde][0]

res = cur.execute("SELECT OppervlakteMuren FROM Huisgegevens")
TupleOppervlakteMuren = res.fetchall()
OppervlakteMuren = [float(i2[0]) for i2 in TupleOppervlakteMuren][0]

res = cur.execute("SELECT VolumeHuis FROM Huisgegevens")
TupleVolumeHuis = res.fetchall()
VolumeHuis = [float(i2[0]) for i2 in TupleVolumeHuis][0]

res = cur.execute("SELECT Kost FROM Huisgegevens")
TupleKost = res.fetchall()
Kost = [float(i2[0]) for i2 in TupleKost][0]
#######################################################################################################################
res = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
TupleSentinelOptimalisatie = res.fetchall()
SentinelOptimalisatie = [int(i2[0]) for i2 in TupleSentinelOptimalisatie][0]

res = cur.execute("SELECT SentinelInterface FROM ExtraWaarden")
TupleSentinelInterface = res.fetchall()
SentinelInterface = [int(i2[0]) for i2 in TupleSentinelInterface][0]

res = cur.execute("SELECT HuidigeDatum FROM ExtraWaarden")
TupleHuidigeDatum = res.fetchall()
HuidigeDatum = [i2[0] for i2 in TupleHuidigeDatum][0]

res = cur.execute("SELECT HuidigUur FROM ExtraWaarden")
TupleHuidigUur = res.fetchall()
HuidigUur = [int(i2[0]) for i2 in TupleHuidigUur][0]

res = cur.execute("SELECT TijdSeconden FROM ExtraWaarden")
TupleTijdSeconden = res.fetchall()
TijdSeconden = [int(i2[0]) for i2 in TupleTijdSeconden][0]
#######################################################################################################################
# Ter illustratie
print("----------TupleToList----------")

print(Apparaten)
print(Wattages)
print(ExacteUren)
print(BeginUur)
print(FinaleTijdstip)
print(UrenWerk)
print(UrenNaElkaar)
print(SoortApparaat)
print(Capaciteit)
print(RememberSettings)
print(Status)

print(VastVerbruik)

print(Aantal)
print(Oppervlakte)
print(Rendement)

print(NaamBatterij)
print(MaxEnergie)
print(OpgeslagenEnergie)

print(TemperatuurHuis)
print(Kost)

print(SentinelOptimalisatie)
print(SentinelInterface)
print(HuidigeDatum)
print(HuidigUur)
print(TijdSeconden)
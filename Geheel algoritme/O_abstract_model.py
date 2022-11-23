from sqlite3 import Cursor
from tkinter import *
from tkinter import messagebox
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import Calendar
from I_Spinbox import Spinbox1, Spinbox2, Spinbox3
import sqlite3
import time
import multiprocessing
import sqlite3
import pyomo.environ as pe
import pyomo.opt as po
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.interpolate import make_interp_spline
from multiprocessing import Value, Array

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = []
def tuples_to_list(list_tuples, categorie, index_slice):
    global con, cur, res
    # list_tuples = lijst van gegevens uit een categorie die de database teruggeeft
    # In de database staat alles in lijsten van tuples, maar aangezien het optimalisatie-algoritme met lijsten werkt
    # moeten we deze lijst van tuples nog omzetten naar een gewone lijst van strings of integers
    if categorie == "Apparaten" or categorie == "NamenBatterijen":
        # zet alle tuples om naar strings
        list_strings = [i0[0] for i0 in list_tuples]
        for i1 in range(len(list_strings)):
            if list_strings[i1] == 0:
                list_strings = list_strings[:i1]
                return [list_strings, i1]
        return [list_strings, len(list_strings)]

    if categorie == "FinaleTijdstip" or categorie == "UrenWerk" or categorie == "UrenNaElkaar" or categorie == "BeginUur":
        # Zet alle tuples om naar integers
        list_ints = [int(i2[0]) for i2 in list_tuples]
        list_ints = list_ints[:index_slice]
        # Gaat alle integers af en vervangt alle nullen naar "/"
        for i3 in range(len(list_ints)):
            if list_ints[i3] == 0:
                list_ints[i3] = "/"
        return list_ints

    if categorie == "Wattages" or categorie == "MaxEnergie" or categorie == "OpgeslagenEnergie" or categorie == "TemperatuurHuis":
        list_floats = [float(i2[0]) for i2 in list_tuples]
        list_floats = list_floats[:index_slice]
        # Gaat alle integers af en vervangt alle nullen naar "/"
        for i3 in range(len(list_floats)):
            if list_floats[i3] == 0:
                list_floats[i3] = "/"
        return list_floats

    if categorie == "ExacteUren":
        # Zet tuples om naar strings
        # Alle nullen worden wel als integers weergegeven
        list_strings = [i4[0] for i4 in list_tuples]
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
                for uur in lijst_uren:
                    lijst_uren_ints.append(int(uur))
                # Voegt de lijst van exacte uren van een apparaat bij de lijst van exacte uren van de andere apparaten
                list_ints.append(lijst_uren_ints)
        return list_ints
def gegevens_opvragen():
    global con, cur, res, Prijzen24uur, Gegevens24uur
    # Datum die wordt ingegeven in de interface
    uur = str(1)
    dag = str(1)
    maand = str(1)
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
    print("*****Lijsten uit CSV*****")
    print(tupleBelpex)
    # Geeft alle waardes in de kolom DatumBelpex en stop die in Dates
    res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
    Dates = res.fetchall()
    # Gaat alle tuples af in Dates, zoekt de tuple van de datum en geeft de index hiervan
    index = [tup for tup in Dates].index(tupleBelpex)
    # Geeft alle waardes in de kolom Prijs en stop die in Prijzen
    res = cur.execute("SELECT Prijs FROM Stroomprijzen")
    Prijzen = res.fetchall()
    # Nu prijzen voor de komende 24 uren zoeken
    Prijzen24uur = []
    for i in range(0, 24):
        # Geeft de prijs op index -i
        prijs = Prijzen[index - i]
        # Database geeft altijd tuples terug dus eerst omzetten naar string
        prijsString = str(prijs)
        # Het stuk waar geen informatie staat afsnijden
        prijsCijfers = prijsString[6:-3]
        # Komma vervangen naar een punt zodat het getal naar een float kan omgezet worden
        prijsCijfersPunt = prijsCijfers.replace(",", ".")
        # Delen door 1 000 000 om van MWh naar kWh te gaan
        prijsFloat = float(prijsCijfersPunt) / 1000
        # Toevoegen aan de rest van de prijzen
        Prijzen24uur.append(prijsFloat)
    # Print lijst met de prijzen van de komende 24 uur
    print("Prijzen24uur")
    print(Prijzen24uur)

    #################################
    # Deel 2 Gegevens Weer opvragen
    #################################
    # maanden, dagen en uren worden steeds voorgesteld met 2 cijfers
    if len(maand) == 1:
        maand = "0" + maand
    if len(dag) == 1:
        dag = "0" + dag
    if len(uur) == 1:
        uur = "0" + uur
    # Correcte constructie van de datum maken
    tupleWeer = ("2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

    res = cur.execute("SELECT DatumWeer FROM Weer")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleWeer)

    res = cur.execute("SELECT Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse FROM Weer")
    alleGegevens = res.fetchall()

    TemperatuurLijst = []
    RadiatieLijst = []
    for i in range(0, 24):
        dagGegevens = alleGegevens[index + i]
        TemperatuurLijst.append(float(dagGegevens[1]))
        RadiatieLijst.append((float(dagGegevens[2]) + float(dagGegevens[3])) / 1000)
    Gegevens24uur = [TemperatuurLijst, RadiatieLijst]
    # Print lijst onderverdeeld in een lijst met de temperaturen van de komende 24 uur
    #                              en een lijst voor de radiatie van de komende 24 uur
    print("Gegevens24uur")
    print(Gegevens24uur)

    return Prijzen24uur, Gegevens24uur
solver = po.SolverFactory('glpk')
m = pe.ConcreteModel()
###################################################################################################################
# ********** Tuples omzetten naar lijsten **********
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

index = -1
res = cur.execute("SELECT NamenBatterijen FROM Batterijen")
ListTuplesNamenBatterijen = res.fetchall()
Antwoord2 = tuples_to_list(ListTuplesNamenBatterijen, "NamenBatterijen", index)
NamenBatterijen = Antwoord2[0]
index = Antwoord2[1]

res = cur.execute("SELECT MaxEnergie FROM Batterijen")
ListTuplesMaxEnergie = res.fetchall()
MaxEnergie = tuples_to_list(ListTuplesMaxEnergie, "MaxEnergie", index)

res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
ListTuplesOpgeslagenEnergie = res.fetchall()
OpgeslagenEnergie = tuples_to_list(ListTuplesOpgeslagenEnergie, "OpgeslagenEnergie", index)

res = cur.execute("SELECT TemperatuurHuis FROM Huisgegevens")
ListTuplesTemperatuurHuis = res.fetchall()
TemperatuurHuis = tuples_to_list(ListTuplesTemperatuurHuis, "TemperatuurHuis", index)

index = -1
res = cur.execute("SELECT VastVerbruik FROM InfoLijsten24uur")
ListTuplesVastVerbruik = res.fetchall()
VastVerbruik = tuples_to_list(ListTuplesVastVerbruik, "VastVerbruik", index)

# Ter illustratie
print("----------TupleToList----------")
print(Apparaten)
print(Wattages)
print(ExacteUren)
print(BeginUur)
print(FinaleTijdstip)
print(UrenWerk)
print(UrenNaElkaar)
print(NamenBatterijen)
print(MaxEnergie)
print(OpgeslagenEnergie)
print(TemperatuurHuis)
###################################################################################################################
##### Gegevens uit de csv bestanden opvragen #####
print("----------GegevensOpvragen24uur----------")
Prijzen24uur, Gegevens24uur = gegevens_opvragen()
###################################################################################################################
##### Parameters updaten #####
EFFICIENTIE = 0.2
OPP_ZONNEPANELEN = 12
""" Uit tabel Stroomprijzen en Weer """
prijzen = Prijzen24uur
stroom_zonnepanelen = [irradiantie * EFFICIENTIE * OPP_ZONNEPANELEN for irradiantie in Gegevens24uur[1]]

""" Uit tabel Geheugen """
namen_apparaten = Apparaten
wattagelijst = Wattages
voorwaarden_apparaten_exact = ExacteUren
starturen = BeginUur
einduren = FinaleTijdstip
werkuren_per_apparaat = UrenWerk
uren_na_elkaarVAR = UrenNaElkaar

""" Extra gegevens voor het optimalisatiealgoritme """
aantal_apparaten = len(wattagelijst)
Delta_t = 1  # bekijken per uur
aantal_uren = len(prijzen)

""" Uit tabel Batterijen """
batterij_bovengrens = sum(MaxEnergie)
huidig_batterijniveau = sum(OpgeslagenEnergie)

""" Extra gegevens om realistischer te maken """
vast_verbruik_gezin = [12 for i in range(24)]
maximaal_verbruik_per_uur = [3500 for i in range(len(prijzen))]
verkoopprijs_van_zonnepanelen = [prijzen[p] / 2 for p in range(len(prijzen))]
verbruik_gezin_totaal = VastVerbruik

""" Uit tabel Huisgegevens """
begintemperatuur_huis = TemperatuurHuis[0]  # in graden C

""" Extra gegevens voor boilerfunctie """
verliesfactor_huis_per_uur = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # in graden C
temperatuurwinst_per_uur = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # in graden C
ondergrens = 17  # mag niet kouder worden dan dit
bovengrens = 22  # mag niet warmer worden dan dit

# controle op tegenstrijdigheden in code

assert len(wattagelijst) == len(namen_apparaten) == len(voorwaarden_apparaten_exact) == len(
    werkuren_per_apparaat)
for i in range(len(voorwaarden_apparaten_exact)):
    if type(werkuren_per_apparaat[i]) == int:
        assert len(voorwaarden_apparaten_exact[i]) <= werkuren_per_apparaat[i]
    for p in range(len(voorwaarden_apparaten_exact[i])):
        if len(voorwaarden_apparaten_exact[i]) > 0:
            if type(voorwaarden_apparaten_exact[i][p]) == int and type(einduren[i]) == int:
                assert voorwaarden_apparaten_exact[i][p] < einduren[i]

# Ter illustratie
print("----------ParametersBenoemen----------")
print("prijzen")
print(prijzen)
print("stroom_zonnepanelen")
print(stroom_zonnepanelen)
print("namen_apparaten")
print(namen_apparaten)
print("wattagelijst")
print(wattagelijst)
print("voorwaarden_apparaten_exact")
print(voorwaarden_apparaten_exact)
print("starturen")
print(starturen)
print("einduren")
print(einduren)
print("werkuren_per_apparaat")
print(werkuren_per_apparaat)
print("uren_na_elkaarVAR")
print(uren_na_elkaarVAR)


###################################################################################################################
# definiëren functies
def variabelen_constructor(lijst, aantal_apparaten, aantal_uren):
    for p in range(aantal_uren*aantal_apparaten): # totaal aantal nodige variabelen = uren maal apparaten
        lijst.add() # hier telkens nieuwe variabele aanmaken

def objectieffunctie(prijzen, variabelen, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen, vast_verbruik_gezin):
    obj_expr = 0
    for p in range(aantal_uren):
        subexpr = 0
        for q in range(len(wattagelijst)):
            subexpr = subexpr + wattagelijst[q]*variabelen[q*aantal_uren + (p+1)] # eerst de variabelen van hetzelfde uur samentellen om dan de opbrengst van zonnepanelen eraf te trekken
        obj_expr = obj_expr + Delta_t*prijzen[p] * (subexpr - stroom_zonnepanelen[p] + vast_verbruik_gezin[p])
    return obj_expr

def exacte_beperkingen(variabelen, voorwaarden_apparaten, aantal_apparaten, voorwaarden_apparaten_lijst, aantal_uren):
    for q in range(aantal_uren*aantal_apparaten):
        index_voor_voorwaarden = q//aantal_uren # hierdoor weet je bij welk apparaat de uur-constraint hoort
        indexnummers = voorwaarden_apparaten_lijst[index_voor_voorwaarden] # hier wordt de uur-constraint, horende bij een bepaald apparaat, opgevraagd
        for p in indexnummers:
            if type(p) != str: # kan ook dat er geen voorwaarde is, dan wordt de uitdrukking genegeerd
                voorwaarden_apparaten.add(expr=variabelen[p+ index_voor_voorwaarden*aantal_uren] == 1) # variabele wordt gelijk gesteld aan 1

def uiteindelijke_waarden(variabelen, aantaluren, namen_apparaten, wattagelijst, huidig_batterijniveau, verliesfactor, winstfactor, huidige_temperatuur):
    print('-' * 30)
    print('De totale kost is', pe.value(m.obj), 'euro') # de kost printen
    kost = pe.value(m.obj)

    print('-' * 30)
    print('toestand apparaten (0 = uit, 1 = aan):')
    for p in range(len(variabelen)):
        if p % aantaluren == 0: # hierdoor weet je wanneer je het volgende apparaat begint te beschrijven
            print('toestel nr.', p/aantaluren+1, '(', namen_apparaten[int(p/aantaluren)], ')') # opdeling maken per toestel
        print(pe.value(variabelen[p + 1]))
    apparaten_aanofuit = []
    for p in range(len(namen_apparaten)):
        apparaten_aanofuit.append(pe.value(variabelen[aantaluren*p+1]))
    i_ontladen = namen_apparaten.index('batterij_ontladen')
    i_opladen = namen_apparaten.index('batterij_opladen')
    nieuw_batterijniveau = pe.value(huidig_batterijniveau - variabelen[i_ontladen*aantaluren+1]*wattagelijst[i_ontladen] + variabelen[i_opladen*aantaluren+1]*wattagelijst[i_opladen])
    i_warmtepomp = namen_apparaten.index('warmtepomp')
    nieuwe_temperatuur = pe.value(huidige_temperatuur + winstfactor[0]*variabelen[aantaluren*i_warmtepomp+1] - verliesfactor[0])
    return kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur

def beperkingen_aantal_uur(werkuren_per_apparaat, variabelen, voorwaarden_werkuren, aantal_uren, einduren, types_apparaten):
    for p in range(len(werkuren_per_apparaat)):
        som = 0
        for q in range(1,aantal_uren+1):
            som = som + variabelen[p*aantal_uren + q] # hier neem je alle variabelen van hetzelfde apparaat, samen
        if type(werkuren_per_apparaat[p]) == int and ((type(einduren[p]) == int and einduren[p] <= aantal_uren)
                                                      or types_apparaten[p] == 'Always on'):
            voorwaarden_werkuren.add(expr = som == werkuren_per_apparaat[p]) # apparaat moet x uur aanstaan

def starttijd(variabelen, starturen, constraint_lijst_startuur, aantal_uren):
    for q in range(len(starturen)):
        if type(starturen[q]) != str:
            p = starturen[q]
            for s in range(1, p):
                constraint_lijst_startuur.add(expr= variabelen[aantal_uren*q + s] == 0)

def finaal_uur(finale_uren, variabelen, constraint_lijst_finaal_uur, aantal_uren):
    for q in range(len(finale_uren)):  # dit is welk aparaat het over gaat
        if type(finale_uren[q]) == int and finale_uren[q] <= aantal_uren:
            p = finale_uren[q]-1  # dit is het eind uur, hierna niet meer in werking
            for s in range(p + 1, aantal_uren + 1):
                constraint_lijst_finaal_uur.add(expr=variabelen[(aantal_uren*q) + s] == 0)

def aantal_uren_na_elkaar(uren_na_elkaarVAR, variabelen, constraint_lijst_aantal_uren_na_elkaar, aantal_uren,
                              variabelen_start, einduren):
        # Dat een bepaald apparaat x aantal uur moet werken staat al in beperking_aantal_uur dus niet meer hier
        # wel nog zeggen dat de som van de start waardes allemaal slechts 1 mag zijn
    for i in range(len(uren_na_elkaarVAR)):  # zegt welk apparaat
        if type(uren_na_elkaarVAR[i]) == int and (type(einduren[i]) == int and einduren[i] <= aantal_uren):
            opgetelde_start = 0
            for p in range(1, aantal_uren + 1):  # zegt welk uur het is
                opgetelde_start = opgetelde_start + variabelen_start[aantal_uren * i + p]
            #print('dit is eerste constraint', opgetelde_start)
            constraint_lijst_aantal_uren_na_elkaar.add(expr=opgetelde_start == 1)
    for i in range(len(uren_na_elkaarVAR)):  # dit loopt de apparaten af
        if type(uren_na_elkaarVAR[i]) == int and (type(einduren[i]) == int and einduren[i] <= aantal_uren):
            #print('dit is nieuwe i', i)
            k = 0
            som = 0
            for p in range(0, aantal_uren):  # dit loopt het uur af
                SENTINEL = 1
                #print('dit is een nieuwe p', p)
                    # print('juist of fout', k < uren_na_elkaarVAR[i], k, uren_na_elkaarVAR[i])
                    # print('juist of fout', k < p)
                while k < uren_na_elkaarVAR[i] and k < p + 1:
                        # print('EERSTE while')
                    som = som + variabelen_start[aantal_uren * i + p + 1]
                    k = k + 1
                    #print('dit is mijn som1', som, 'en is gelijk aan', variabelen[aantal_uren * i + p + 1])
                    constraint_lijst_aantal_uren_na_elkaar.add(expr=variabelen[aantal_uren * i + p + 1] == som)
                    SENTINEL = 0
                while k <= aantal_uren and k >= uren_na_elkaarVAR[i] and SENTINEL == 1:
                    #print('tweede while', 'eerste index', aantal_uren * i + p + 1, 'tweede index',
                            #aantal_uren * i + p - uren_na_elkaarVAR[i] +1)
                    som = som + variabelen_start[aantal_uren * i + p + 1] - variabelen_start[aantal_uren * i + p - uren_na_elkaarVAR[i] + 1]
                    #print('dit is mijn som2', som, 'en is gelijk aan', variabelen[aantal_uren * i + p + 1])
                    k = k + 1
                    SENTINEL = 0
                    constraint_lijst_aantal_uren_na_elkaar.add(expr=variabelen[aantal_uren * i + p + 1] == som)

def voorwaarden_max_verbruik(variabelen, max_verbruik_per_uur, constraintlijst_max_verbruik, wattagelijst, delta_t):
    totaal_aantal_uren = len(max_verbruik_per_uur)
    for p in range(1,len(max_verbruik_per_uur)+1):
        som = 0
        for q in range(len(wattagelijst)):
            som = som + delta_t*wattagelijst[q]*variabelen[q*totaal_aantal_uren + p]
        uitdrukking = (-max_verbruik_per_uur[p-1], som, max_verbruik_per_uur[p-1])
        constraintlijst_max_verbruik.add(expr= uitdrukking)

def voorwaarden_warmteboiler(apparaten, variabelen,voorwaardenlijst, warmteverliesfactor, warmtewinst, aanvankelijke_temperatuur, ondergrens, bovengrens, aantaluren):
    temperatuur_dit_uur = aanvankelijke_temperatuur
    if not 'warmtepomp' in apparaten:
        return
    index_warmteboiler = apparaten.index('warmtepomp')
    beginindex_in_variabelen = index_warmteboiler*aantaluren +1
    if aanvankelijke_temperatuur < ondergrens:
        voorwaardenlijst.add(expr= variabelen[beginindex_in_variabelen] == 1)
    elif aanvankelijke_temperatuur > bovengrens:
        voorwaardenlijst.add(expr= variabelen[beginindex_in_variabelen] == 0)
    else:
        index_verlies = 0
        for p in range(beginindex_in_variabelen,beginindex_in_variabelen + aantaluren):
            temperatuur_dit_uur = temperatuur_dit_uur-warmteverliesfactor[index_verlies] + warmtewinst[index_verlies]*variabelen[p]
            uitdrukking = (ondergrens, temperatuur_dit_uur, bovengrens)
            voorwaardenlijst.add(expr= uitdrukking)
            index_verlies = index_verlies + 1

def som_tot_punt(variabelen, beginpunt, eindpunt):
    som = 0
    for i in range(beginpunt, eindpunt+1):
        som = som + variabelen[i]
    return som

def voorwaarden_batterij(variabelen, constraintlijst, aantaluren, wattagelijst, namen_apparaten, huidig_batterijniveau, batterij_bovengrens):
    index_ontladen = namen_apparaten.index('batterij_ontladen')
    index_opladen = namen_apparaten.index('batterij_opladen')
    for q in range(1,aantaluren+1):
        som_ontladen = wattagelijst[index_ontladen]*som_tot_punt(variabelen, index_ontladen*aantaluren + 1, index_ontladen*aantaluren + q)
        som_opladen = wattagelijst[index_opladen]*som_tot_punt(variabelen, index_opladen*aantaluren + 1, index_opladen*aantaluren + q)
        verschil = som_opladen + som_ontladen + huidig_batterijniveau
        constraintlijst.add(expr= (0, verschil, batterij_bovengrens))
    for q in range(1,aantaluren+1):
        constraintlijst.add(expr= (None, variabelen[index_ontladen*aantaluren + q]+ variabelen[index_opladen*aantaluren+q], 1))

# een lijst maken die de stand van de batterij gaat bijhouden als aantal wat maal aantal uur
# op het einde van het programma dan aanpassen wat die batterij het laatste uur heeft gedaan en zo bijhouden in de database in die variabele
# het getal in die variabele trek je ook altijd op bij som ontladen en som ontladen hierboven

# deze functie zal het aantal uur dat het apparaat moet werken verlagen op voorwaarden dat het apparaat ingepland stond
# voor het eerste uur
def verlagen_aantal_uur(lijst, aantal_uren, te_verlagen_uren, namen_apparaten_def):  # voor aantal uur mogen er geen '/' ingegeven worden, dan crasht het
    global con, cur, res
    print("Urenwerk na functie verlagen_aantal_uur")
    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    print(res.fetchall())
    for i in range(len(te_verlagen_uren)):
        if pe.value(lijst[i * aantal_uren + 1]) == 1 and namen_apparaten_def[i] != "warmtepomp" and \
                namen_apparaten_def[i] != "batterij_ontladen" and namen_apparaten_def[i] != "batterij_opladen":
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(te_verlagen_uren[i] - 1) +
                        " WHERE Nummering =" + str(i))
            con.commit()
    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    print(res.fetchall())


def uur_omzetten(exacte_uren1apparaat):
    string = "'"
    for i2 in range(len(exacte_uren1apparaat)):
        if exacte_uren1apparaat[i2] == "/":
            return str(0)
        else:
            string = string + str(exacte_uren1apparaat[i2]) + ":"
    string = string[0:-1] + "'"
    return string


# deze functie zal exacte uren als 'aan' aanduiden op voorwaarde dat het eerste uur als 'aan' was aangeduid en er ook was aangeduid dat
# het apparaat x aantal uur na elkaar moest aanstaan, elk uur tot x-1 zal dan al naar 'aan' worden aangeduid voor de volgende berekeningen terug beginnen
def opeenvolging_opschuiven(lijst, aantal_uren, opeenvolgende_uren, oude_exacte_uren):
    global con, cur, res
    print("ExacteUren en eventueel UrenNaElkaar na functie opeenvolging_opschuiven ")
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
    print(res.fetchall())
    for i in range(len(opeenvolgende_uren)):
        if type(opeenvolgende_uren[i]) == int and pe.value(lijst[i * aantal_uren + 1]) == 1:
            nieuwe_exacte_uren = []
            for p in range(1, opeenvolgende_uren[i] + 1):  # dus voor opeenvolgende uren 5, p zal nu 1,2,3,4
                nieuwe_exacte_uren.append(p)
            cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(nieuwe_exacte_uren) +
                        " WHERE Nummering =" + str(i))
            cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                        " WHERE Nummering =" + str(i))
            con.commit()

            # Ter illustratie
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
    print(res.fetchall())

    # in database toevoegen dat i^de lijst 1,2,3,4 allen op 1 worden gezet dus bij in exact uur lijst, dus elke p in lijst i toevoegen

    # extra: bij dit apparaat '' zetten in de plaats van opeenvolgende aantal uur zodat die geen 24 constraints meer moet gaan maken achteraf


# deze functie zal alle exacte uren die er waren verlagen met 1, als het 0 wordt dan wordt het later verwijderd uit de lijst
def verlagen_exacte_uren(exacte_uren):
    global con, cur, res
    print("ExacteUren na functie verlagen_exacte_uren")
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    for i in range(len(exacte_uren)):  # dit gaat de apparaten af
        if exacte_uren[i] != ['/']:
            verlaagde_exacte_uren = []
            for uur in exacte_uren[i]:  # dit zal lopen over al de 'exacte uren' van een specifiek apparaat
                if len(exacte_uren[i]) != 1:
                    if uur - 1 != 0:
                        verlaagde_exacte_uren.append(uur - 1)
                else:
                    verlaagde_exacte_uren.append(uur - 1)
            if verlaagde_exacte_uren[0] == 0:
                verlaagde_exacte_uren = "/"
            cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(verlaagde_exacte_uren) +
                        " WHERE Nummering =" + str(i))
            con.commit()

            # Ter illustratie
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())


# deze functie zal een apparaat volledig verwijderen uit alle lijsten, wnr het aantal uur dat het moet werken op nul is gekomen
def verwijderen_uit_lijst_wnr_aantal_uur_0(aantal_uren_per_apparaat, lijst_met_wattages,
                                           exacte_uren, prijzen_stroom, einduren, aantal_uren):
    global con, cur, res
    # uren_na_elkaarVAR wordt gebaseerd op werkuren per apparaat dus die moet je niet zelf meer aanpassen
    print("Gegevens verwijderen na functie verwijderen_uit_lijst_wnr_aantal_uur_0")
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())
    for i in range(len(aantal_uren_per_apparaat)):
        if aantal_uren_per_apparaat[
            i] == "/":  # dan gaan we dit apparaat overal verwijderen uit alle lijsten die we hebben
            # eerst lijst met wattages apparaat verwijderen
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                        " WHERE Nummering =" + str(i))
            # geen nut
            # cur.execute("UPDATE Geheugen SET Wattages =" + str(0) +
            #            " WHERE Nummering =" + str(i))
            # cur.execute("UPDATE Geheugen SET ExacteUren =" + str(0) +
            #            " WHERE Nummering =" + str(i))
            # voorlopig niet doen
            # cur.execute("UPDATE Geheugen SET Apparaten =" + str(0) +
            #            " WHERE Nummering =" + str(i))
            con.commit()
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())


# deze functie zal het finale uur eentje verlagen
def verlagen_finale_uur(klaar_tegen_bepaald_uur):
    global con, cur, res
    print("FinaleTijdstip na functie verlagen_finale_uur")
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())
    for i in range(len(klaar_tegen_bepaald_uur)):
        if type(klaar_tegen_bepaald_uur[i]) == int:
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(klaar_tegen_bepaald_uur[i] - 1) +
                        " WHERE Nummering =" + str(i))
            con.commit()
            # Ter illustratie
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())


def verlagen_start_uur(start_op_bepaald_uur):
    global con, cur, res
    print("Startuur na functie verlagen_start_uur")
    res = cur.execute("SELECT BeginUur FROM Geheugen")
    print(res.fetchall())
    for i in range(len(start_op_bepaald_uur)):
        if type(start_op_bepaald_uur[i]) == int:
            cur.execute("UPDATE Geheugen SET BeginUur =" + str(start_op_bepaald_uur[i] - 1) +
                        " WHERE Nummering =" + str(i))
            con.commit()
        # Ter illustratie
    res = cur.execute("SELECT BeginUur FROM Geheugen")
    print(res.fetchall())
    # zo aanpassen in database nu
    # einduren[i] = einduren[i] - 1
def vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour):
    del verbruik_gezin_totaal[current_hour][0]
    verbruik_gezin_totaal[current_hour].append(uniform(2,4))

#######################################################################################################
#aanmaken lijst met binaire variabelen
m.apparaten = pe.VarList(domain=pe.Binary)
m.apparaten.construct()
variabelen_constructor(m.apparaten, aantal_apparaten, aantal_uren) # maakt variabelen aan die apparaten voorstellen

#objectief functie aanmaken
obj_expr = objectieffunctie(prijzen, m.apparaten, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen, vast_verbruik_gezin) # somfunctie die objectief creeërt
m.obj = pe.Objective(sense = pe.minimize, expr = obj_expr)

#aanmaken constraint om op exact uur aan of uit te staan
m.voorwaarden_exact = pe.ConstraintList() # voorwaarde om op een exact uur aan of uit te staan
m.voorwaarden_exact.construct()
exacte_beperkingen(m.apparaten, m.voorwaarden_exact,aantal_apparaten, voorwaarden_apparaten_exact, aantal_uren) # beperkingen met vast uur

#aanmaken constraint om aantal werkuren vast te leggen
m.voorwaarden_aantal_werkuren = pe.ConstraintList()
m.voorwaarden_aantal_werkuren.construct()
beperkingen_aantal_uur(werkuren_per_apparaat, m.apparaten, m.voorwaarden_aantal_werkuren, aantal_uren, einduren, types_apparaten) # moet x uur werken, maakt niet uit wanneer

# aanmaken constraint om startuur vast te leggen
m.voorwaarden_startuur = pe.ConstraintList()
m.voorwaarden_startuur.construct()
starttijd(m.apparaten, starturen, m.voorwaarden_startuur, aantal_uren)

#aanmaken constraint om een finaal uur vast te leggen
m.voorwaarden_finaal_uur = pe.ConstraintList()
m.voorwaarden_finaal_uur.construct()
finaal_uur(einduren, m.apparaten, m.voorwaarden_finaal_uur, aantal_uren) # moet na een bepaald uur klaarzijn

# Voor functie aantal_uren_na_elkaar
m.apparatenstart = pe.VarList(domain=pe.Binary)
m.apparatenstart.construct()
variabelen_constructor(m.apparatenstart, aantal_apparaten, aantal_uren)
m.voorwaarden_aantal_uren_na_elkaar = pe.ConstraintList()
aantal_uren_na_elkaar(uren_na_elkaarVAR, m.apparaten, m.voorwaarden_aantal_uren_na_elkaar, aantal_uren,
                          m.apparatenstart, einduren)

# voorwaarden maximale verbruik per uur
m.voorwaarden_maxverbruik = pe.ConstraintList()
m.voorwaarden_maxverbruik.construct()
voorwaarden_max_verbruik(m.apparaten, maximaal_verbruik_per_uur, m.voorwaarden_maxverbruik, wattagelijst, Delta_t)

# voorwaarden warmtepomp
m.voorwaarden_warmtepomp = pe.ConstraintList()
voorwaarden_warmteboiler(namen_apparaten, m.apparaten, m.voorwaarden_warmtepomp, verliesfactor_huis_per_uur, temperatuurwinst_per_uur, begintemperatuur_huis, ondergrens, bovengrens, aantal_uren)

# voorwaarden batterij
m.voorwaarden_batterij = pe.ConstraintList()
voorwaarden_batterij(m.apparaten, m.voorwaarden_batterij, aantal_uren, wattagelijst, namen_apparaten, huidig_batterijniveau, batterij_bovengrens)


result = solver.solve(m)

print(result)
# waarden teruggeven
vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour)
kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur = uiteindelijke_waarden(m.apparaten, aantal_uren, namen_apparaten, wattagelijst, huidig_batterijniveau, verliesfactor_huis_per_uur, temperatuurwinst_per_uur, begintemperatuur_huis)

# deze functies passen de lijsten aan, rekening houdend met de apparaten die gewerkt hebben op het vorige uur
verlagen_aantal_uur(m.apparaten, aantal_uren, werkuren_per_apparaat, namen_apparaten)

# deze lijn moet sws onder 'verlagen exacte uren' staan want anders voeg je iets toe aan de database en ga je vervolgens dit opnieuw verlagen
opeenvolging_opschuiven(m.apparaten, aantal_uren, uren_na_elkaarVAR, voorwaarden_apparaten_exact)

res = cur.execute("SELECT Apparaten FROM Geheugen")
ListTuplesApparaten = res.fetchall()
index = -1
Antwoord = tuples_to_list(ListTuplesApparaten, "Apparaten", index)
index = Antwoord[1]
res = cur.execute("SELECT ExacteUren FROM Geheugen")
ListTuplesExacteUren = res.fetchall()
ExacteUren = tuples_to_list(ListTuplesExacteUren, "ExacteUren", index)

verlagen_exacte_uren(ExacteUren)

res = cur.execute("SELECT UrenWerk FROM Geheugen")
ListTuplesUrenWerk = res.fetchall()
UrenWerk = tuples_to_list(ListTuplesUrenWerk, "UrenWerk", index)

verwijderen_uit_lijst_wnr_aantal_uur_0(UrenWerk, wattagelijst, voorwaarden_apparaten_exact, prijzen,
                                       einduren, aantal_uren)

res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
ListTuplesFinaleTijdstip = res.fetchall()
index_slice = -1
FinaleTijdstip = tuples_to_list(ListTuplesFinaleTijdstip, "FinaleTijdstip", index_slice)

verlagen_finale_uur(FinaleTijdstip)

verlagen_start_uur(starturen)

'''
#Nu zullen er op basis van de berekeningen aanpassingen moeten gedaan worden aan de database
#wnr iets het eerste uur wordt berekend als 'aan' dan moeten er bij de volgende berekeningen er mee rekening gehouden worden
#dat dat bepaald apparaat heeft gedraaid op dat uur, dus aantal draai uur is een uur minder, en wnr het drie uur na elkaar moest draaien en het eerste uur werd aangeduid als 'aan', dan moet bij de volgende berekening 1 en 2 nog als 'aan' aangeduid worden
#een batterij is eigenlijk ook gwn aantal uur dat die nog moet werken een uur verlagen

#nog overal in elke functie bijzetten wat er moet gebeuren als er geen integer in staat maar die string
'''
from sqlite3 import Cursor
from tkinter import *
from tkinter import messagebox
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import Calendar
from I_Spinbox import Spinbox2, Spinbox3
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
from random import uniform

########### Dark/Light mode en color theme instellen
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

############variabelen/lijsten aanmaken
current_date = '01-01-2016'
current_hour = 0
Prijzen24uur = []
Gegevens24uur = []
lijst_batterij_namen = ["thuisbatterij"]
lijst_batterij_bovengrens = [200]
lijst_batterij_opgeslagen_energie = [6]
begin_temperatuur_huis = 18
lijst_warmteverliezen = []
lijst_opwarming = []

# Nummering, Apparaten, Wattages, ExacteUren, BeginUur, FinaleTijdstip, UrenWerk, UrenNaElkaar, SoortApparaat, Capaciteit, RememberSettings, Status
con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = []
con.commit()
cur.close()
con.close()



def tuples_to_list(list_tuples, categorie, index_slice):
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

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res_apparaten = cur.execute("SELECT Apparaten FROM Geheugen")
lijst_apparaten = tuples_to_list(res_apparaten.fetchall(), "Apparaten", -1)[0]
maxlength = len(lijst_apparaten)
res_wattages = cur.execute("SELECT Wattages FROM Geheugen")
lijst_verbruiken = tuples_to_list(res_wattages.fetchall(), "Wattages", -1)[0:maxlength]
res_exaxteuren = cur.execute("SELECT ExacteUren FROM Geheugen")
lijst_exacte_uren = tuples_to_list(res_exaxteuren.fetchall(), "ExacteUren", -1)[0:maxlength]
res_beginuur = cur.execute("SELECT BeginUur FROM Geheugen")
lijst_beginuur = tuples_to_list(res_beginuur.fetchall(), "BeginUur", -1)[0:maxlength]
res_deadline = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
lijst_deadlines = tuples_to_list(res_deadline.fetchall(), "FinaleTijdstip", -1)[0:maxlength]
res_urenwerk = cur.execute("SELECT UrenWerk FROM Geheugen")
lijst_aantal_uren = tuples_to_list(res_urenwerk.fetchall(), "UrenWerk", -1)[0:maxlength]
res_urennaelkaar = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
lijst_uren_na_elkaar = tuples_to_list(res_urennaelkaar.fetchall(), "UrenNaElkaar", -1)[0:maxlength]
res_soortapparaat = cur.execute("SELECT SoortApparaat FROM Geheugen")
lijst_soort_apparaat = tuples_to_list(res_soortapparaat.fetchall(), "Apparaten", -1)[0]
res_capaciteit = cur.execute("SELECT Capaciteit FROM Geheugen")
lijst_capaciteit = tuples_to_list(res_capaciteit.fetchall(), "UrenNaElkaar", -1)[0:maxlength]
res_remembersettings = cur.execute("SELECT RememberSettings FROM Geheugen")
lijst_remember_settings = tuples_to_list(res_remembersettings.fetchall(), "UrenNaElkaar", -1)[0:maxlength]
res_status = cur.execute("SELECT Status FROM Geheugen")
lijst_status = tuples_to_list(res_status.fetchall(), "UrenNaElkaar", -1)[0:maxlength]

con.commit()
cur.close()
con.close()

"""
lijst_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = ['/','/', '/', 5, 4, 24]
lijst_uren_na_elkaar = ['/','/', '/',5,'/', 24]
lijst_verbruiken = [15, -14.344, 12.2, 14, 10, 12]
lijst_deadlines = ['/','/','/', 10, 11, 12]
lijst_beginuur = ['/','/', '/', 3, 6, 4]
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,0,0,0,0,0]
lijst_exacte_uren = [['/'], ['/'], ['/'], ['/'], ['/'], ['/']]

lijst_batterij_namen = ["thuisbatterij"]
lijst_batterij_bovengrens = [100]
lijst_batterij_opgeslagen_energie = [6]
begin_temperatuur_huis = 20

aantal_zonnepanelen = 0  # IN DATABASE
oppervlakte_zonnepanelen = 0  # IN DATABASE
rendement_zonnepanelen = 0.20
min_temperatuur = 17  # IN DATABASE
max_temperatuur = 21  # IN DATABASE
huidige_temperatuur = 20  # IN DATABASE
verbruik_warmtepomp = 200  # IN DATABASE
COP = 4  # IN DATABASE
U_waarde = 0.4  # IN DATABASE
oppervlakte_muren = 50  # IN DATABASE
volume_huis = 500  # IN DATABASE
"""
lijst_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = ['/','/', '/', 5, 4, 3]
lijst_uren_na_elkaar = ['/','/', '/',5,'/', 3]
lijst_verbruiken = [15, -15, 15, 14, 10, 12]
lijst_deadlines = ['/','/','/', 10, 11, 12]
lijst_beginuur = ['/','/', '/', 3, 6, 4]
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]
lijst_exacte_uren = [['/'], ['/'], ['/'], ['/'], ['/'], ['/']]
lijst_batterij_namen = ["thuisbatterij"]
lijst_batterij_bovengrens = [200]
lijst_batterij_opgeslagen_energie = [10]
begin_temperatuur_huis = 20
aantal_zonnepanelen = 0  # IN DATABASE
oppervlakte_zonnepanelen = 0  # IN DATABASE
rendement_zonnepanelen = 0.20
min_temperatuur = 17  # IN DATABASE
max_temperatuur = 21  # IN DATABASE
huidige_temperatuur = 20  # IN DATABASE
verbruik_warmtepomp = 200  # IN DATABASE
COP = 4  # IN DATABASE
U_waarde = 0.4  # IN DATABASE
oppervlakte_muren = 50  # IN DATABASE
volume_huis = 500  # IN DATABASE

aantal_dagen_in_gemiddelde = 3
# verbruik_gezin_totaal = [[3 for i in range(aantal_dagen_in_gemiddelde)] for p in range(24)]

# vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]


warmtepomp_status = 0

totale_batterijcapaciteit = 0  # IN DATABASE
batterij_power = 0
batterij_laadvermogen = 0
batterij_niveau = 0


current_production = 0  # MOET UIT DE DATABASE KOMEN #in de Hour change
current_consumption = 0  # MOET UIT DE DATABASE KOMEN


#######################################################################################################################
##### Algemene functies #####
def tuples_to_list(list_tuples, categorie, index_slice):
    global con, cur, res
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

    if categorie == "Wattages" or categorie == "MaxEnergie" or categorie == "OpgeslagenEnergie":
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
                for uur in lijst_uren:
                    lijst_uren_ints.append(int(uur))
                # Voegt de lijst van exacte uren van een apparaat bij de lijst van exacte uren van de andere apparaten
                list_ints.append(lijst_uren_ints)
        return list_ints
def geheugen_veranderen():
    global con, cur, res
    print("*****Vooraf ingestelde lijsten*****")
    print(lijst_apparaten)
    print(lijst_verbruiken)
    print(lijst_exacte_uren)
    print(lijst_beginuur)
    print(lijst_deadlines)
    print(lijst_aantal_uren)
    print(lijst_uren_na_elkaar)
    print(lijst_batterij_bovengrens)
    print(lijst_batterij_namen)
    print(lijst_batterij_opgeslagen_energie)
    print(begin_temperatuur_huis)

    def uur_omzetten(exacte_uren1apparaat):
        # functie om exacte uren om te zetten in een string die makkelijk leesbaar is om later terug om te zetten
        # De string die in de database wordt gestopt moet met een accent beginnen en eindigen, anders kan sqlite geen
        # symbolen lezen
        string = "'"
        # Gaat alle apparaten af en kijkt naar de lijst van exacte uren van dat bepaalt apparaat
        for i2 in range(len(exacte_uren1apparaat)):
            # Als er geen uur in die lijst staat moet er een nul in de database gezet worden
            if exacte_uren1apparaat[i2] == "/":
                return str(0)
            # Anders aan de begin-string het uur toevoegen + een onderscheidingsteken
            else:
                string = string + str(exacte_uren1apparaat[i2]) + ":"
        # Als er geen uren meer toegevoegd moeten worden, moet het laatste onderscheidingsteken uit de string en moet een
        # accent toegevoegd worden
        string = string[0:-1] + "'"
        return string

    #######################################################################################################################
    # Voor het geheugen
    ######################
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()
    # Aantal apparaten die in gebruik zijn berekenen
    lengte = len(lijst_apparaten)
    # Voor ieder apparaat de nodige gegevens in de database zetten
    for i in range(lengte):
        # In de database staat alles in de vorm van een string
        NummerApparaat = str(i)
        # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
        naam = "'" + lijst_apparaten[i] + "'"
        # Voer het volgende uit
        cur.execute("UPDATE Geheugen SET Apparaten =" + naam +
                    " WHERE Nummering =" + NummerApparaat)
        # Wanneer er geen gegevens in de lijst staan, staat die aangegeven met een "/"
        # Als dit het geval is, plaatsen we een 0 in de database die in TupleToList terug naar een "/" wordt omgezet
        if lijst_verbruiken[i] == "/":
            cur.execute("UPDATE Geheugen SET Wattages =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET Wattages =" + str(lijst_verbruiken[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        # Wanneer je een special teken gebruikt moet je het als een tuple ingeven met speciale notatie
        # uur_omzetten zorgt er voor dat dit op een overzichtelijke manier kan
        cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(lijst_exacte_uren[i]) +
                    " WHERE Nummering =" + NummerApparaat)
        if lijst_beginuur[i] == "/":
            cur.execute("UPDATE Geheugen SET BeginUur =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET BeginUur =" + str(lijst_beginuur[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if lijst_deadlines[i] == "/":
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(lijst_deadlines[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if lijst_aantal_uren[i] == "/":
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(lijst_aantal_uren[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if lijst_uren_na_elkaar[i] == "/":
            cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(lijst_uren_na_elkaar[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET SoortApparaat =" + "'" + lijst_soort_apparaat[i] + "'" +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET RememberSettings =" + str(lijst_remember_settings[i]) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Status =" + str(lijst_status[i]) +
                    " WHERE Nummering =" + NummerApparaat)
    #######################################################################################################################
    # Voor zonnepanelen
    ######################
    cur.execute("UPDATE Zonnepanelen SET Aantal =" + str(aantal_zonnepanelen))
    cur.execute("UPDATE Zonnepanelen SET Oppervlakte =" + str(oppervlakte_zonnepanelen))
    cur.execute("UPDATE Zonnepanelen SET Rendement =" + str(rendement_zonnepanelen))
    #######################################################################################################################
    # Voor de batterijen
    ######################
    lengte2 = len(lijst_batterij_namen)
    for i2 in range(lengte2):
        # In de database staat alles in de vorm van een string
        NummerApparaat = str(i2)
        # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
        naam = "'" + lijst_batterij_namen[i2] + "'"
        # Voer het volgende uit
        cur.execute("UPDATE Batterijen SET NamenBatterijen =" + naam +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Batterijen SET MaxEnergie =" + str(lijst_batterij_bovengrens[i2]) +
                    " WHERE Nummering =" + NummerApparaat)
        if lijst_batterij_opgeslagen_energie[i2] == "/":
            cur.execute("UPDATE Batterijen SET OpgeslagenEnergie =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Batterijen SET OpgeslagenEnergie =" + str(lijst_batterij_opgeslagen_energie[i2]) +
                        " WHERE Nummering =" + NummerApparaat)
    #######################################################################################################################
    # Voor de temperatuur
    ######################
    cur.execute("UPDATE Huisgegevens SET TemperatuurHuis =" + str(begin_temperatuur_huis))
    cur.execute("UPDATE Huisgegevens SET MinTemperatuur =" + str(min_temperatuur))
    cur.execute("UPDATE Huisgegevens SET MaxTemperatuur =" + str(max_temperatuur))
    cur.execute("UPDATE Huisgegevens SET VerbruikWarmtepomp =" + str(verbruik_warmtepomp))
    cur.execute("UPDATE Huisgegevens SET COP =" + str(COP))
    cur.execute("UPDATE Huisgegevens SET UWaarde =" + str(U_waarde))
    cur.execute("UPDATE Huisgegevens SET OppervlakteMuren =" + str(oppervlakte_muren))
    cur.execute("UPDATE Huisgegevens SET VolumeHuis =" + str(volume_huis))
    #######################################################################################################################
    # Ter illustratie
    print("*****Lijsten uit de database*****")
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT Wattages FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT BeginUur FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
    print(res.fetchall())
    res = cur.execute("SELECT NamenBatterijen FROM Batterijen")
    print(res.fetchall())
    res = cur.execute("SELECT MaxEnergie FROM Batterijen")
    print(res.fetchall())
    res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
    print(res.fetchall())
    con.commit()
    cur.close()
    con.close()
def gegevens_opvragen(uur_def, dag_def, maand_def):
    global con, cur, res, Prijzen24uur, Gegevens24uur, current_hour, current_date
    # Datum die wordt ingegeven in de interface
    uur = uur_def
    dag = dag_def
    maand = maand_def
    print(uur)
    print(dag)
    print(maand)
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
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()
    # Geeft alle waardes in de kolom DatumBelpex en stop die in Dates
    res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
    Dates = res.fetchall()
    # Gaat alle tuples af in Dates, zoekt de tuple van de datum en geeft de index hiervan
    index = [tup for tup in Dates].index(tupleBelpex)
    # Geeft alle waardes in de kolom Prijs en stop die in Prijzen
    res = cur.execute("SELECT Prijs FROM Stroomprijzen")
    Prijzen = res.fetchall()
    con.commit()
    cur.close()
    con.close()
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
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()
    res = cur.execute("SELECT DatumWeer FROM Weer")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleWeer)

    res = cur.execute("SELECT Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse FROM Weer")
    alleGegevens = res.fetchall()
    con.commit()
    cur.close()
    con.close()
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

##### Algoritme updaten #####
def update_algoritme():
    global con, cur, res, Prijzen24uur, Gegevens24uur, current_date, current_hour
    solver = po.SolverFactory('glpk')
    m = pe.ConcreteModel()
    #######################################################################################################################
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
    index = -1
    res = cur.execute("SELECT NamenBatterijen FROM Batterijen")
    ListTuplesNamenBatterijen = res.fetchall()
    NamenBatterijen = tuples_to_list(ListTuplesNamenBatterijen, "NamenBatterijen", index)
    if len(NamenBatterijen) != len(ListTuplesNamenBatterijen):
        index = len(NamenBatterijen)

    res = cur.execute("SELECT MaxEnergie FROM Batterijen")
    ListTuplesMaxEnergie = res.fetchall()
    MaxEnergie = tuples_to_list(ListTuplesMaxEnergie, "MaxEnergie", index)

    res = cur.execute("SELECT OpgeslagenEnergie FROM Batterijen")
    ListTuplesOpgeslagenEnergie = res.fetchall()
    OpgeslagenEnergie = tuples_to_list(ListTuplesOpgeslagenEnergie, "OpgeslagenEnergie", index)
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

    con.commit()
    cur.close()
    con.close()
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
    print(NamenBatterijen)
    print(MaxEnergie)
    print(OpgeslagenEnergie)
    print(TemperatuurHuis)
    print(VastVerbruik)
    ###################################################################################################################
    ##### Gegevens uit de csv bestanden opvragen #####
    print("----------GegevensOpvragen24uur----------")
    def date_plus_one():
        global current_date
        if current_date[0] == 0:
            day = int(current_date[1])
        else:
            day = int(current_date[0:2])
        if current_date[3] == 0:
            month = int(current_date[4])
        else:
            month = int(current_date[3:5])
        year = int(current_date[6:10])

        if (year % 400 == 0):
            leap_year = True
        elif (year % 100 == 0):
            leap_year = False
        elif (year % 4 == 0):
            leap_year = True
        else:
            leap_year = False

        if month in (1, 3, 5, 7, 8, 10, 12):
            month_length = 31
        elif month == 2:
            if leap_year:
                month_length = 29
            else:
                month_length = 28
        else:
            month_length = 30

        if day < month_length:
            day += 1
        else:
            day = 1
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

        if day < 10 and month < 10:
            current_date = '0' + str(day) + ':0' + str(month) + ':' + str(year)
        elif day < 10:
            current_date = '0' + str(day) + ':' + str(month) + ':' + str(year)
        elif month < 10:
            current_date = str(day) + ':0' + str(month) + ':' + str(year)
        else:
            current_date = str(day) + ':' + str(month) + ':' + str(year)
    current_hour = HuidigUur
    current_date = HuidigeDatum

    current_hour += 1
    if current_hour == 24:
        current_hour = 0
        date_plus_one()
    uur = str(current_hour)
    dag = str(int(current_date[0:2]))
    maand = str(current_date[3:5])
    Prijzen24uur, Gegevens24uur = gegevens_opvragen(uur,dag,maand)
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
    verbruik_gezin_totaal = VastVerbruik

    """ Extra gegevens voor het optimalisatiealgoritme """
    aantal_apparaten = len(wattagelijst)
    Delta_t = 1  # bekijken per uur
    aantal_uren = len(prijzen)

    """ Uit tabel Batterijen """
    batterij_bovengrens = sum(MaxEnergie)
    huidig_batterijniveau = sum(OpgeslagenEnergie)

    """ Extra gegevens om realistischer te maken """
    vast_verbruik_gezin = [12 for i in range(24)]
    maximaal_verbruik_per_uur = [8000 for i in range(len(prijzen))]
    verkoopprijs_van_zonnepanelen = [prijzen[p] / 2 for p in range(len(prijzen))]

    """ Uit tabel Huisgegevens """
    begintemperatuur_huis = TemperatuurHuis  # in graden C

    """ Extra gegevens voor boilerfunctie """
    verliesfactor_huis_per_uur = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # in graden C
    temperatuurwinst_per_uur = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # in graden C
    ondergrens = 17  # mag niet kouder worden dan dit
    bovengrens = 20  # mag niet warmer worden dan dit

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
    print("verbruik_gezin_totaal")
    print(verbruik_gezin_totaal)
    ###################################################################################################################
    # definiëren functies
    def variabelen_constructor(lijst, aantal_apparaten, aantal_uren):
        for p in range(aantal_uren * aantal_apparaten):  # totaal aantal nodige variabelen = uren maal apparaten
            lijst.add()  # hier telkens nieuwe variabele aanmaken

    def objectieffunctie(prijzen, variabelen, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen,
                         vast_verbruik_gezin):
        obj_expr = 0
        for p in range(aantal_uren):
            subexpr = 0
            for q in range(len(wattagelijst)):
                subexpr = subexpr + wattagelijst[q] * variabelen[q * aantal_uren + (
                            p + 1)]  # eerst de variabelen van hetzelfde uur samentellen om dan de opbrengst van zonnepanelen eraf te trekken
            obj_expr = obj_expr + Delta_t * prijzen[p] * (subexpr - stroom_zonnepanelen[p] + vast_verbruik_gezin[p])
        return obj_expr

    def exacte_beperkingen(variabelen, voorwaarden_apparaten, aantal_apparaten, voorwaarden_apparaten_lijst,
                           aantal_uren):
        for q in range(aantal_uren * aantal_apparaten):
            index_voor_voorwaarden = q // aantal_uren  # hierdoor weet je bij welk apparaat de uur-constraint hoort
            indexnummers = voorwaarden_apparaten_lijst[
                index_voor_voorwaarden]  # hier wordt de uur-constraint, horende bij een bepaald apparaat, opgevraagd
            for p in indexnummers:
                if type(p) != str:  # kan ook dat er geen voorwaarde is, dan wordt de uitdrukking genegeerd
                    voorwaarden_apparaten.add(expr=variabelen[
                                                       p + index_voor_voorwaarden * aantal_uren] == 1)  # variabele wordt gelijk gesteld aan 1

    # je kijkt het uur per uur, wnr het uur pos is dan tel je het er op de normale manier bij, wnr het iets negatief werd dan ga je een ander tarief pakken en tel je het zo bij die objectief

    def uiteindelijke_waarden(variabelen, aantaluren, namen_apparaten, wattagelijst, huidig_batterijniveau,
                              verliesfactor, winstfactor, huidige_temperatuur):
        print('-' * 30)
        print('De totale kost is', pe.value(m.obj), 'euro')  # de kost printen
        kost = pe.value(m.obj)

        print('-' * 30)
        print('toestand apparaten (0 = uit, 1 = aan):')
        for p in range(len(variabelen)):
            if p % aantaluren == 0:  # hierdoor weet je wanneer je het volgende apparaat begint te beschrijven
                print('toestel nr.', p / aantaluren + 1, '(', namen_apparaten[int(p / aantaluren)],
                      ')')  # opdeling maken per toestel
            print(pe.value(variabelen[p + 1]))
        apparaten_aanofuit = []
        for p in range(len(namen_apparaten)):
            apparaten_aanofuit.append(pe.value(variabelen[aantaluren * p + 1]))
        i_ontladen = namen_apparaten.index('batterij_ontladen')
        i_opladen = namen_apparaten.index('batterij_opladen')
        nieuw_batterijniveau = pe.value(
            huidig_batterijniveau - variabelen[i_ontladen * aantaluren + 1] * wattagelijst[i_ontladen] + variabelen[
                i_opladen * aantaluren + 1] * wattagelijst[i_opladen])
        i_warmtepomp = namen_apparaten.index('warmtepomp')
        nieuwe_temperatuur = pe.value(
            huidige_temperatuur + winstfactor[0] * variabelen[aantaluren * i_warmtepomp + 1] - verliesfactor[0])
        return kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur

    def beperkingen_aantal_uur(werkuren_per_apparaat, variabelen, voorwaarden_werkuren, aantal_uren, einduren, lijst_soort_apparaat):
        for p in range(len(werkuren_per_apparaat)):
            som = 0
            for q in range(1, aantal_uren + 1):
                som = som + variabelen[
                    p * aantal_uren + q]  # hier neem je alle variabelen van hetzelfde apparaat, samen
            if type(werkuren_per_apparaat[p]) == int and ((type(einduren[p]) == int and einduren[p] <= aantal_uren)
                                                          or lijst_soort_apparaat[p] == 'Always on'):
                voorwaarden_werkuren.add(expr=som == werkuren_per_apparaat[p])  # apparaat moet x uur aanstaan

    def starttijd(variabelen, starturen, constraint_lijst_startuur, aantal_uren):
        for q in range(len(starturen)):
            if type(starturen[q]) != str:
                p = starturen[q]
                for s in range(1, p):
                    constraint_lijst_startuur.add(expr=variabelen[aantal_uren * q + s] == 0)

    def finaal_uur(finale_uren, variabelen, constraint_lijst_finaal_uur, aantal_uren):
        for q in range(len(finale_uren)):  # dit is welk aparaat het over gaat
            if type(finale_uren[q]) == int and finale_uren[q] <= aantal_uren:
                p = finale_uren[q] - 1  # dit is het eind uur, hierna niet meer in werking
                for s in range(p + 1, aantal_uren + 1):
                    constraint_lijst_finaal_uur.add(expr=variabelen[(aantal_uren * q) + s] == 0)

    def aantal_uren_na_elkaar(uren_na_elkaarVAR, variabelen, constraint_lijst_aantal_uren_na_elkaar, aantal_uren,
                              variabelen_start, einduren):
        # Dat een bepaald apparaat x aantal uur moet werken staat al in beperking_aantal_uur dus niet meer hier
        # wel nog zeggen dat de som van de start waardes allemaal slechts 1 mag zijn
        for i in range(len(uren_na_elkaarVAR)):  # zegt welk apparaat
            if type(uren_na_elkaarVAR[i]) == int and (type(einduren[i]) == int and einduren[i] <= aantal_uren):
                opgetelde_start = 0
                for p in range(1, aantal_uren + 1):  # zegt welk uur het is
                    opgetelde_start = opgetelde_start + variabelen_start[aantal_uren * i + p]
                # print('dit is eerste constraint', opgetelde_start)
                constraint_lijst_aantal_uren_na_elkaar.add(expr=opgetelde_start == 1)
        for i in range(len(uren_na_elkaarVAR)):  # dit loopt de apparaten af
            if type(uren_na_elkaarVAR[i]) == int and (type(einduren[i]) == int and einduren[i] <= aantal_uren):
                # print('dit is nieuwe i', i)
                k = 0
                som = 0
                for p in range(0, aantal_uren):  # dit loopt het uur af
                    SENTINEL = 1
                    # print('dit is een nieuwe p', p)
                    # print('juist of fout', k < uren_na_elkaarVAR[i], k, uren_na_elkaarVAR[i])
                    # print('juist of fout', k < p)
                    while k < uren_na_elkaarVAR[i] and k < p + 1:
                        # print('EERSTE while')
                        som = som + variabelen_start[aantal_uren * i + p + 1]
                        k = k + 1
                        # print('dit is mijn som1', som, 'en is gelijk aan', variabelen[aantal_uren * i + p + 1])
                        constraint_lijst_aantal_uren_na_elkaar.add(expr=variabelen[aantal_uren * i + p + 1] == som)
                        SENTINEL = 0
                    while k <= aantal_uren and k >= uren_na_elkaarVAR[i] and SENTINEL == 1:
                        # print('tweede while', 'eerste index', aantal_uren * i + p + 1, 'tweede index',
                        # aantal_uren * i + p - uren_na_elkaarVAR[i] +1)
                        som = som + variabelen_start[aantal_uren * i + p + 1] - variabelen_start[
                            aantal_uren * i + p - uren_na_elkaarVAR[i] + 1]
                        # print('dit is mijn som2', som, 'en is gelijk aan', variabelen[aantal_uren * i + p + 1])
                        k = k + 1
                        SENTINEL = 0
                        constraint_lijst_aantal_uren_na_elkaar.add(expr=variabelen[aantal_uren * i + p + 1] == som)

    def voorwaarden_max_verbruik(variabelen, max_verbruik_per_uur, constraintlijst_max_verbruik, wattagelijst, delta_t):
        totaal_aantal_uren = len(max_verbruik_per_uur)
        for p in range(1, len(max_verbruik_per_uur) + 1):
            som = 0
            for q in range(len(wattagelijst)):
                som = som + delta_t * wattagelijst[q] * variabelen[q * totaal_aantal_uren + p]
            uitdrukking = (-max_verbruik_per_uur[p - 1], som, max_verbruik_per_uur[p - 1])
            constraintlijst_max_verbruik.add(expr=uitdrukking)

    def voorwaarden_warmteboiler(apparaten, variabelen, voorwaardenlijst, warmteverliesfactor, warmtewinst,
                                 aanvankelijke_temperatuur, ondergrens, bovengrens, aantaluren):
        temperatuur_dit_uur = aanvankelijke_temperatuur
        if not 'warmtepomp' in apparaten:
            return
        index_warmteboiler = apparaten.index('warmtepomp')
        beginindex_in_variabelen = index_warmteboiler * aantaluren + 1
        if aanvankelijke_temperatuur < ondergrens:
            voorwaardenlijst.add(expr=variabelen[beginindex_in_variabelen] == 1)
        elif aanvankelijke_temperatuur > bovengrens:
            voorwaardenlijst.add(expr=variabelen[beginindex_in_variabelen] == 0)
        else:
            index_verlies = 0
            for p in range(beginindex_in_variabelen, beginindex_in_variabelen + aantaluren):
                temperatuur_dit_uur = temperatuur_dit_uur - warmteverliesfactor[index_verlies] + warmtewinst[
                    index_verlies] * variabelen[p]
                uitdrukking = (ondergrens, temperatuur_dit_uur, bovengrens)
                voorwaardenlijst.add(expr=uitdrukking)
                index_verlies = index_verlies + 1

    def som_tot_punt(variabelen, beginpunt, eindpunt):
        som = 0
        for i in range(beginpunt, eindpunt + 1):
            som = som + variabelen[i]
        return som

    def voorwaarden_batterij(variabelen, constraintlijst, aantaluren, wattagelijst, namen_apparaten,
                             huidig_batterijniveau, batterij_bovengrens):
        index_ontladen = namen_apparaten.index('batterij_ontladen')
        index_opladen = namen_apparaten.index('batterij_opladen')
        for q in range(1, aantaluren + 1):
            som_ontladen = wattagelijst[index_ontladen] * som_tot_punt(variabelen, index_ontladen * aantaluren + 1,
                                                                       index_ontladen * aantaluren + q)
            som_opladen = wattagelijst[index_opladen] * som_tot_punt(variabelen, index_opladen * aantaluren + 1,
                                                                     index_opladen * aantaluren + q)
            verschil = som_opladen + som_ontladen + huidig_batterijniveau
            constraintlijst.add(expr=(0, verschil, batterij_bovengrens))
        for q in range(1, aantaluren + 1):
            constraintlijst.add(expr=(
            None, variabelen[index_ontladen * aantaluren + q] + variabelen[index_opladen * aantaluren + q], 1))

    # een lijst maken die de stand van de batterij gaat bijhouden als aantal wat maal aantal uur
    # op het einde van het programma dan aanpassen wat die batterij het laatste uur heeft gedaan en zo bijhouden in de database in die variabele
    # het getal in die variabele trek je ook altijd op bij som ontladen en som ontladen hierboven

    # deze functie zal het aantal uur dat het apparaat moet werken verlagen op voorwaarden dat het apparaat ingepland stond
    # voor het eerste uur
    def verlagen_aantal_uur(lijst, aantal_uren, te_verlagen_uren,
                            namen_apparaten_def):  # voor aantal uur mogen er geen '/' ingegeven worden, dan crasht het
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
        print("Urenwerk na functie verlagen_aantal_uur")
        res = cur.execute("SELECT UrenWerk FROM Geheugen")
        print(res.fetchall())
        for i in range(len(te_verlagen_uren)):
            if pe.value(lijst[i * aantal_uren + 1]) == 1 and namen_apparaten_def[i] != "warmtepomp" and \
                    namen_apparaten_def[i] != "batterij_ontladen" and namen_apparaten_def[i] != "batterij_opladen":
                cur.execute("UPDATE Geheugen SET UrenWerk =" + str(te_verlagen_uren[i] - 1) +
                            " WHERE Nummering =" + str(i))
        res = cur.execute("SELECT UrenWerk FROM Geheugen")
        print(res.fetchall())
        con.commit()
        cur.close()
        con.close()

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
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
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
                # Ter illustratie
        res = cur.execute("SELECT ExacteUren FROM Geheugen")
        print(res.fetchall())
        res = cur.execute("SELECT UrenNaElkaar FROM Geheugen")
        print(res.fetchall())

        con.commit()
        cur.close()
        con.close()
        # in database toevoegen dat i^de lijst 1,2,3,4 allen op 1 worden gezet dus bij in exact uur lijst, dus elke p in lijst i toevoegen

        # extra: bij dit apparaat '' zetten in de plaats van opeenvolgende aantal uur zodat die geen 24 constraints meer moet gaan maken achteraf

    # deze functie zal alle exacte uren die er waren verlagen met 1, als het 0 wordt dan wordt het later verwijderd uit de lijst
    def verlagen_exacte_uren(exacte_uren):
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
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

                # Ter illustratie
        res = cur.execute("SELECT ExacteUren FROM Geheugen")
        print(res.fetchall())

        con.commit()
        cur.close()
        con.close()

    # deze functie zal een apparaat volledig verwijderen uit alle lijsten, wnr het aantal uur dat het moet werken op nul is gekomen
    def verwijderen_uit_lijst_wnr_aantal_uur_0(aantal_uren_per_apparaat, lijst_met_wattages,
                                               exacte_uren, prijzen_stroom, einduren, aantal_uren):
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
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
        res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
        print(res.fetchall())

        con.commit()
        cur.close()
        con.close()

    # deze functie zal het finale uur eentje verlagen
    def verlagen_finale_uur(klaar_tegen_bepaald_uur):
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
        print("FinaleTijdstip na functie verlagen_finale_uur")
        res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
        print(res.fetchall())
        for i in range(len(klaar_tegen_bepaald_uur)):
            if type(klaar_tegen_bepaald_uur[i]) == int:
                cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(klaar_tegen_bepaald_uur[i] - 1) +
                            " WHERE Nummering =" + str(i))
                # Ter illustratie
        res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
        print(res.fetchall())

        con.commit()
        cur.close()
        con.close()

    def verlagen_start_uur(start_op_bepaald_uur):
        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()
        print("Startuur na functie verlagen_start_uur")
        res = cur.execute("SELECT BeginUur FROM Geheugen")
        print(res.fetchall())
        for i in range(len(start_op_bepaald_uur)):
            if type(start_op_bepaald_uur[i]) == int:
                cur.execute("UPDATE Geheugen SET BeginUur =" + str(start_op_bepaald_uur[i] - 1) +
                            " WHERE Nummering =" + str(i))
            # Ter illustratie
        res = cur.execute("SELECT BeginUur FROM Geheugen")
        print(res.fetchall())

        con.commit()
        cur.close()
        con.close()
        # zo aanpassen in database nu
        # einduren[i] = einduren[i] - 1

    def lijst_werking_leds(namen_apparaten, aan_of_uit):
        werking_leds = [[],[]]
        for i in namen_apparaten:
            werking_leds[0].append(i)
        for i in aan_of_uit:
            werking_leds[1].append(i)
        return werking_leds

    def vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour):
        print(verbruik_gezin_totaal)
        print(current_hour)
        del verbruik_gezin_totaal[current_hour][0]
        verbruik_gezin_totaal[current_hour].append(uniform(2, 4))
    #######################################################################################################
    # aanmaken lijst met binaire variabelen
    m.apparaten = pe.VarList(domain=pe.Binary)
    m.apparaten.construct()
    variabelen_constructor(m.apparaten, aantal_apparaten, aantal_uren)  # maakt variabelen aan die apparaten voorstellen
    # objectief functie aanmaken
    obj_expr = objectieffunctie(prijzen, m.apparaten, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen,
                                vast_verbruik_gezin)  # somfunctie die objectief creeërt
    m.obj = pe.Objective(sense=pe.minimize, expr=obj_expr)

    # aanmaken constraint om op exact uur aan of uit te staan
    m.voorwaarden_exact = pe.ConstraintList()  # voorwaarde om op een exact uur aan of uit te staan
    m.voorwaarden_exact.construct()
    exacte_beperkingen(m.apparaten, m.voorwaarden_exact, aantal_apparaten, voorwaarden_apparaten_exact,
                       aantal_uren)  # beperkingen met vast uur

    # aanmaken constraint om aantal werkuren vast te leggen
    m.voorwaarden_aantal_werkuren = pe.ConstraintList()
    m.voorwaarden_aantal_werkuren.construct()
    beperkingen_aantal_uur(werkuren_per_apparaat, m.apparaten, m.voorwaarden_aantal_werkuren, aantal_uren,
                           einduren, lijst_soort_apparaat)  # moet x uur werken, maakt niet uit wanneer

    # aanmaken constraint om startuur vast te leggen
    m.voorwaarden_startuur = pe.ConstraintList()
    m.voorwaarden_startuur.construct()
    starttijd(m.apparaten, starturen, m.voorwaarden_startuur, aantal_uren)

    # aanmaken constraint om een finaal uur vast te leggen
    m.voorwaarden_finaal_uur = pe.ConstraintList()
    m.voorwaarden_finaal_uur.construct()
    finaal_uur(einduren, m.apparaten, m.voorwaarden_finaal_uur, aantal_uren)  # moet na een bepaald uur klaarzijn

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
    voorwaarden_warmteboiler(namen_apparaten, m.apparaten, m.voorwaarden_warmtepomp, verliesfactor_huis_per_uur,
                             temperatuurwinst_per_uur, begintemperatuur_huis, ondergrens, bovengrens, aantal_uren)

    # voorwaarden batterij
    m.voorwaarden_batterij = pe.ConstraintList()
    voorwaarden_batterij(m.apparaten, m.voorwaarden_batterij, aantal_uren, wattagelijst, namen_apparaten,
                         huidig_batterijniveau, batterij_bovengrens)

    result = solver.solve(m)

    print(result)


    # waarden teruggeven
    vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour)
    kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur = uiteindelijke_waarden(m.apparaten, aantal_uren,
                                                                                               namen_apparaten,
                                                                                               wattagelijst,
                                                                                               huidig_batterijniveau,
                                                                                               verliesfactor_huis_per_uur,
                                                                                               temperatuurwinst_per_uur,
                                                                                               begintemperatuur_huis)

    # deze functies passen de lijsten aan, rekening houdend met de apparaten die gewerkt hebben op het vorige uur
    verlagen_aantal_uur(m.apparaten, aantal_uren, werkuren_per_apparaat, namen_apparaten)

    # deze lijn moet sws onder 'verlagen exacte uren' staan want anders voeg je iets toe aan de database en ga je vervolgens dit opnieuw verlagen
    opeenvolging_opschuiven(m.apparaten, aantal_uren, uren_na_elkaarVAR, voorwaarden_apparaten_exact)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT Apparaten FROM Geheugen")
    ListTuplesApparaten = res.fetchall()
    index = -1
    Apparaten = tuples_to_list(ListTuplesApparaten, "Apparaten", index)
    if len(Apparaten) != len(ListTuplesApparaten):
        index = len(Apparaten)
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    ListTuplesExacteUren = res.fetchall()
    ExacteUren = tuples_to_list(ListTuplesExacteUren, "ExacteUren", index)

    cur.close()
    con.close()

    verlagen_exacte_uren(ExacteUren)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT UrenWerk FROM Geheugen")
    ListTuplesUrenWerk = res.fetchall()
    UrenWerk = tuples_to_list(ListTuplesUrenWerk, "UrenWerk", index)

    cur.close()
    con.close()

    verwijderen_uit_lijst_wnr_aantal_uur_0(UrenWerk, wattagelijst, voorwaarden_apparaten_exact, prijzen,
                                           einduren, aantal_uren)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
    ListTuplesFinaleTijdstip = res.fetchall()
    FinaleTijdstip = tuples_to_list(ListTuplesFinaleTijdstip, "FinaleTijdstip", index)

    cur.close()
    con.close()

    verlagen_finale_uur(FinaleTijdstip)

    verlagen_start_uur(starturen)




    ###################################################################################################
    #Hier zal een lijst van [[namen],[aan of uit per apparaat]] geïmplementeerd worden, vervolgens moet de code uit 'aansturen leds' hier nog geplakt worden
    werking_leds = lijst_werking_leds(namen_apparaten, m.apparaten)
    '''
    #Nu zullen er op basis van de berekeningen aanpassingen moeten gedaan worden aan de database
    #wnr iets het eerste uur wordt berekend als 'aan' dan moeten er bij de volgende berekeningen er mee rekening gehouden worden
    #dat dat bepaald apparaat heeft gedraaid op dat uur, dus aantal draai uur is een uur minder, en wnr het drie uur na elkaar moest draaien en het eerste uur werd aangeduid als 'aan', dan moet bij de volgende berekening 1 en 2 nog als 'aan' aangeduid worden
    #een batterij is eigenlijk ook gwn aantal uur dat die nog moet werken een uur verlagen

    #nog overal in elke functie bijzetten wat er moet gebeuren als er geen integer in staat maar die string
    '''

###### FUNCTIES VOOR COMMUNICATIE MET DATABASE
def apparaat_toevoegen_database(namen_apparaten, wattages_apparaten, begin_uur, finale_tijdstip, uur_werk_per_apparaat,
                                uren_na_elkaar, soort_apparaat, capaciteit, remember_settings, status):
    global con, cur, res
    # In de database staat alles in de vorm van een string
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    apparaten = res.fetchall()
    for i in range(len(namen_apparaten)):
        # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
        NummerApparaat = str(i)
        naam = "'" + namen_apparaten[i] + "'"
        # Voer het volgende uit
        cur.execute("UPDATE Geheugen SET Apparaten = " + naam +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Wattages =" + str(wattages_apparaten[i]) +
                    " WHERE Nummering =" + NummerApparaat)

        # Wanneer er geen gegevens in de lijst staan, staat die aangegeven met een "/"
        # Als dit het geval is, plaatsen we een 0 in de database die in TupleToList terug naar een "/" wordt omgezet
        if begin_uur[i] == "/":
            cur.execute("UPDATE Geheugen SET BeginUur =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET BeginUur =" + str(begin_uur[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if finale_tijdstip[i] == "/":
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(finale_tijdstip[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if uur_werk_per_apparaat[i] == "/":
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(uur_werk_per_apparaat[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if uren_na_elkaar[i] == "/":
            cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(uren_na_elkaar[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if soort_apparaat[i] == "/":
            cur.execute("UPDATE Geheugen SET SoortApparaat =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            print("Deze moet ge hebben: ")
            print(soort_apparaat)
            cur.execute("UPDATE Geheugen SET SoortApparaat = '" + soort_apparaat[i] +
                        "' WHERE Nummering =" + NummerApparaat)
        if capaciteit[i] == "/":
            cur.execute("UPDATE Geheugen SET Capaciteit =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET Capaciteit =" + str(capaciteit[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if remember_settings[i] == "/":
            cur.execute("UPDATE Geheugen SET RememberSettings =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET RememberSettings =" + str(remember_settings[i]) +
                        " WHERE Nummering =" + NummerApparaat)
        if status[i] == "/":
            cur.execute("UPDATE Geheugen SET Status =" + str(0) +
                        " WHERE Nummering =" + NummerApparaat)
        else:
            cur.execute("UPDATE Geheugen SET Status =" + str(status[i]) +
                        " WHERE Nummering =" + NummerApparaat)

    for j in range(len(namen_apparaten), len(apparaten)):
        NummerApparaat = str(j)
        cur.execute("UPDATE Geheugen SET Apparaten = " + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Wattages =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET BeginUur =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET UrenWerk =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET UrenNaElkaar =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET SoortApparaat =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Capaciteit =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET RememberSettings =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Status =" + str(0) +
                    " WHERE Nummering =" + NummerApparaat)


    # Is nodig om de uitgevoerde veranderingen op te slaan
    con.commit()

# MainApplication: main window instellen + de drie tabs aanmaken met verwijzigen naar HomeFrame, ControlFrame en StatisticFrame
class MainApplication(CTk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_resolution = str(screen_width) + 'x' + str(screen_height) + '0' + '0'

        self.geometry(screen_resolution)
        self.title("SMART SOLAR HOUSE")
        self.iconbitmap('I_solarhouseicon.ico')

        my_notebook = ttk.Notebook(self)
        my_notebook.pack()

        frame_home = HomeFrame(my_notebook)
        frame_controls = ControlFrame(my_notebook)
        frame_statistics = StatisticFrame(my_notebook)

        frame_home.pack(fill='both', expand=1)
        frame_controls.pack(fill='both', expand=1)
        frame_statistics.pack(fill='both', expand=1)

        my_notebook.add(frame_home, text='HOME')
        my_notebook.add(frame_controls, text='CONTROLS')
        my_notebook.add(frame_statistics, text='STATISTICS')

# Home Frame aanmaken met titel, namen projectdeelnemers en kalender om datum te kiezen
class HomeFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent)

        frame_width = self.winfo_screenwidth()
        frame_height = self.winfo_screenheight()

        my_canvas = Canvas(self, width=frame_width, height=frame_height, bg=('gray16'))
        my_canvas.pack(fill="both", expand=True)

        frame1 = CTkFrame(self, padx=10, pady=10, width=0.5 * frame_width, height=0.16 * frame_height)
        frame1.pack_propagate('false')
        my_canvas.create_window((350, 50), window=frame1, anchor="nw")
        frame2 = CTkFrame(self, padx=10, pady=10, width=0.5 * frame_width, height=0.35 * frame_height)
        frame2.grid_propagate('false')
        my_canvas.create_window((350, 300), window=frame2, anchor="nw")
        frame3 = CTkFrame(self, padx=10, pady=10, width=0.5 * frame_width, height=0.1 * frame_height)
        frame3.grid_propagate('false')
        my_canvas.create_window((350, 800), window=frame3, anchor="nw")

        home_title = CTkLabel(frame1, text='SMART SOLAR HOUSE', text_font=('Biome', 60, 'bold'))
        home_subtitle = CTkLabel(frame1, text='Made by August Vannes, Jonas Thewis, Lander Verhoeven, Ruben Vanherpe,',
                                 text_font=('Biome', 15))
        home_subtitle2 = CTkLabel(frame1, text='Tibo Mattheus and Tijs Motmans', text_font=('Biome', 15))

        home_title.pack()
        home_subtitle.pack()
        home_subtitle2.pack()

        frame2.rowconfigure(0, uniform='uniform', weight=2)
        frame2.rowconfigure(1, uniform='uniform', weight=12)
        frame2.rowconfigure(2, uniform='uniform', weight=2)
        frame2.columnconfigure(0, uniform='uniform', weight=1)

        selected_date = CTkLabel(frame2, text='Here you can change the current date:', text_font=('Biome', 15))
        selected_date.grid(column=0, row=0, sticky='nsew', padx=5, pady=2)
        cal = Calendar(frame2, selectmode='day', date_pattern='dd-mm-y')
        cal.grid(column=0, row=1, sticky='nsew', padx=50, pady=5)

        def date_plus_one():
            global current_date
            if current_date[0] == 0:
                day = int(current_date[1])
            else:
                day = int(current_date[0:2])
            if current_date[3] == 0:
                month = int(current_date[4])
            else:
                month = int(current_date[3:5])
            year = int(current_date[6:10])

            if (year % 400 == 0):
                leap_year = True
            elif (year % 100 == 0):
                leap_year = False
            elif (year % 4 == 0):
                leap_year = True
            else:
                leap_year = False

            if month in (1, 3, 5, 7, 8, 10, 12):
                month_length = 31
            elif month == 2:
                if leap_year:
                    month_length = 29
                else:
                    month_length = 28
            else:
                month_length = 30

            if day < month_length:
                day += 1
            else:
                day = 1
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1

            if day < 10 and month < 10:
                current_date = '0' + str(day) + ':0' + str(month) + ':' + str(year)
            elif day < 10:
                current_date = '0' + str(day) + ':' + str(month) + ':' + str(year)
            elif month < 10:
                current_date = str(day) + ':0' + str(month) + ':' + str(year)
            else:
                current_date = str(day) + ':' + str(month) + ':' + str(year)

            label_day.configure(text=str(current_date[0:2]))
            label_month.configure(text=str(current_date[3:5]))
            label_year.configure(text=str(current_date[6:10]))

            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()

            cur.execute("UPDATE ExtraWaarden SET HuidigeDatum =" + "'" + current_date + "'")

            con.commit()
            cur.close()
            con.close()

        def hour_change():
            global current_hour, Prijzen24uur, Gegevens24uur, lijst_warmteverliezen, lijst_opwarming, con, cur, res
            global lijst_status

            current_hour += 1
            if current_hour == 24:
                current_hour = 0
                date_plus_one()
            if current_hour < 10:
                label_hours.configure(text='0' + str(current_hour))
            else:
                label_hours.configure(text=str(current_hour))

            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()

            cur.execute("UPDATE ExtraWaarden SET HuidigUur =" + str(current_hour))

            con.commit()
            cur.close()
            con.close()

            for nummer in range(3, len(lijst_apparaten)): #verwijdert de deadline als die niet onthouden moet worden
                if lijst_remember_settings[nummer] == 0:
                    if lijst_deadlines[nummer] == current_hour:
                        lijst_deadlines[nummer] = '/'

            uur = str(current_hour)
            dag = str(int(current_date[0:2]))
            maand = str(current_date[3:5])
            print("Interface**************************************************************")
            Prijzen24uur, Gegevens24uur = gegevens_opvragen(uur, dag, maand)
            lijst_buitentemperaturen = Gegevens24uur[0]
            binnentemperatuur = (max_temperatuur + min_temperatuur) / 2
            soortelijke_warmte_lucht = 1005
            massadichtheid_lucht = 1.275
            lijst_warmteverliezen = []
            lijst_opwarming = []
            for i in range(0, 24):
                heat_loss_hour = U_waarde * oppervlakte_muren * (lijst_buitentemperaturen[i] - binnentemperatuur)
                heat_gain_hour = COP * verbruik_warmtepomp
                heat_pump_on = heat_gain_hour + heat_loss_hour
                heat_pump_off = heat_loss_hour
                temp_diff_on = (heat_pump_on * 3600) / (soortelijke_warmte_lucht * massadichtheid_lucht * volume_huis)
                temp_diff_off = (heat_pump_off * 3600) / (soortelijke_warmte_lucht * massadichtheid_lucht * volume_huis)
                lijst_opwarming.append(temp_diff_on)
                lijst_warmteverliezen.append(temp_diff_off)

            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()

            res = cur.execute("SELECT Apparaten FROM Geheugen")
            ListTuplesApparaten = res.fetchall()
            index = -1
            Apparaten = tuples_to_list(ListTuplesApparaten, "Apparaten", index)
            if len(Apparaten) != len(ListTuplesApparaten):
                index = len(Apparaten)
            res_status = cur.execute("SELECT Status FROM Geheugen")
            lijst_status = tuples_to_list(res_status.fetchall(), "Status", index)
            print(lijst_status)

            con.commit()
            cur.close()
            con.close()

            #FrameApparaten.apparaten_in_frame(self,frame_met_apparaten)

            #Voor de grafiek productie vs consumptie:
            huidige_consumptie = 5  # EIG UIT DATABASE
            huidige_productie = 2  # EIG UIT DATABASE
            wegvallend_uur = lijst_uren.pop(0)
            lijst_uren.append(wegvallend_uur)
            lijst_consumptie.pop(0)
            lijst_consumptie.append(huidige_consumptie)
            lijst_productie.pop(0)
            lijst_productie.append(huidige_productie)
            grafiek_PvsC.clear()
            grafiek_PvsC.plot(lijst_uren, lijst_consumptie, lijst_productie)
            grafiek_PvsC.set_title("Energy production and consumption of the last 24 hours", fontsize=10, pad=10, color='white')
            grafiek_PvsC.legend(['Energy consumption', 'Energy production'], loc='upper right', facecolor='#262626',
                           edgecolor='#262626', labelcolor='white')
            grafiek_PvsC.set_ylabel('Energy (in kWh)', color='white')
            grafiek_PvsC.set_facecolor('#262626')
            grafiek_PvsC.set(xlim=(0, 23), ylim=(0, 10))
            grafiek_PvsC.set_xticks(lijst_uren, lijst_uren, rotation=45, color='white')
            canvas_PvsC.draw()

            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()

            res_sentinel = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
            TupleSENTINEL = res_sentinel.fetchall()

            cur.close()
            con.close()

            SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]
            if SENTINEL == -1:
                con = sqlite3.connect("D_VolledigeDatabase.db")
                cur = con.cursor()

                stringtijd = strftime('%S')
                inttijd = int(stringtijd)

                cur.execute("UPDATE ExtraWaarden SET TijdSeconden =" + str(inttijd))
                cur.execute("UPDATE ExtraWaarden SET SentinelOptimalisatie =" + str(0))


                con.commit()
                cur.close()
                con.close()

            label_hours.after(20000, hour_change)

        def grad_date():
            global current_date, current_hour, Prijzen24uur, Gegevens24uur
            current_date = cal.get_date()
            label_day.configure(text=str(current_date[0:2]))
            label_month.configure(text=str(current_date[3:5]))
            label_year.configure(text=str(current_date[6:10]))

        btn = CTkButton(frame2, text="Confirm the chosen date", command=grad_date)
        btn.grid(column=0, row=2, sticky='nsew', padx=40, pady=5)

        frame3.grid_rowconfigure(0, uniform='uniform', weight=1)
        frame3.grid_columnconfigure((0, 2, 6, 8), uniform='uniform', weight=5)
        frame3.grid_columnconfigure(4, uniform='uniform', weight=8)
        frame3.grid_columnconfigure((1, 3, 5, 7), uniform='uniform', weight=1)

        day = CTkFrame(frame3, bd=5, corner_radius=10)
        day.grid(row=3, column=0, padx=5, sticky='nsew')
        streep1 = CTkLabel(frame3, text='-', text_font=('Biome', 50, 'bold'))
        streep1.grid(row=3, column=1, sticky='nsew')
        month = CTkFrame(frame3, bd=5, corner_radius=10)
        month.grid(row=3, column=2, padx=5, sticky='nsew')
        streep2 = CTkLabel(frame3, text='-', text_font=('Biome', 50, 'bold'))
        streep2.grid(row=3, column=3, sticky='nsew')
        year = CTkFrame(frame3, bd=5, corner_radius=10)
        year.grid(row=3, column=4, padx=5, sticky='nsew')
        separator = ttk.Separator(frame3, orient='vertical')
        separator.grid(row=3, column=5, sticky='ns', pady=20)
        hours = CTkFrame(frame3, bd=5, corner_radius=10)
        hours.grid(row=3, column=6, padx=5, sticky='nsew')
        dubbel_punt = CTkLabel(frame3, text=':', text_font=('Biome', 50, 'bold'))
        dubbel_punt.grid(row=3, column=7, sticky='nsew')
        minutes = CTkFrame(frame3, bd=5, corner_radius=10)
        minutes.grid(row=3, column=8, padx=5, sticky='nsew')

        label_day = CTkLabel(day, text=str(current_date[0:2]), text_font=('Biome', 50))
        label_day.pack(fill='both', expand=1)
        label_month = CTkLabel(month, text=str(current_date[3:5]), text_font=('Biome', 50))
        label_month.pack(fill='both', expand=1)
        label_year = CTkLabel(year, text=str(current_date[6:10]), text_font=('Biome', 50))
        label_year.pack(fill='both', expand=1)
        if current_hour < 10:
            label_hours = CTkLabel(hours, text='0' + str(current_hour), text_font=('Biome', 50))
        else:
            label_hours = CTkLabel(hours, text=str(current_hour), text_font=('Biome', 50))
        label_hours.pack(fill='both', expand=1)
        label_minutes = CTkLabel(minutes, text='00', text_font=('Biome', 50))
        label_minutes.pack(fill='both', expand=1)

        label_hours.after(5000, hour_change)

# ControlFrame aanmaken met verwijzingen naar FrameTemperatuur, FrameBatterijen en FrameApparaten
class ControlFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=1)
        self.grid_rowconfigure((0, 1, 2), uniform="uniform", weight=1)

        frame_temperatuur = FrameTemperatuur(self)
        frame_batterijen = FrameBatterijen(self)
        frame_apparaten = FrameApparaten(self)
        frame_zonnepanelen = FrameZonnepanelen(self)

        frame_temperatuur.grid(row=0, column=0, padx=5, sticky='nsew')
        frame_batterijen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_apparaten.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')
        frame_zonnepanelen.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

# Frame om de temperatuur van het huis (warmtepomp) te regelen
class FrameTemperatuur(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Heat pump', text_font=('Biome', 15, 'bold'))
        title.grid(row=0, column=0, padx=5, sticky='nsew')

        frame1 = CTkFrame(self)
        frame1.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        frame1.rowconfigure(0, uniform='uniform', weight=4)
        frame1.rowconfigure(1, uniform='uniform', weight=1)
        frame1.columnconfigure((0, 1), uniform='uniform', weight=1)

        frame_settings = CTkFrame(frame1)
        frame_current_temperature = CTkFrame(frame1)
        if warmtepomp_status == 1:
            bg_color = "#74d747"
            status_text = 'ON'
        else:
            bg_color = "#f83636"
            status_text = 'OFF'
        label_status_warmtepomp = CTkLabel(frame1, text=status_text, bg_color=bg_color)

        frame_settings.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_current_temperature.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        label_status_warmtepomp.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        def configure_heat_pump():
            edit_pump = CTkToplevel(self)
            edit_pump.iconbitmap('I_solarhouseicon.ico')
            edit_pump.title('Configure heat pump')
            edit_pump.geometry('500x500')
            edit_pump.grab_set()

            edit_pump.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), uniform='uniform', weight=2)
            edit_pump.rowconfigure(14, uniform='uniform', weight=3)
            edit_pump.columnconfigure((0, 1), uniform='uniform', weight=1)

            def bewerk():
                global verbruik_warmtepomp, min_temperatuur, max_temperatuur, COP, U_waarde, oppervlakte_muren, volume_huis

                verbruik_warmtepomp = entry_verbruik.get()
                min_temperatuur = entry_min_temp.get()
                max_temperatuur = entry_max_temp.get()
                COP = entry_COP.get()
                U_waarde = entry_U_waarde.get()
                oppervlakte_muren = entry_opp_muren.get()
                volume_huis = entry_volume_huis.get()

                lijst_verbruiken[0] = verbruik_warmtepomp

                label_verbruik.configure(text='Power: ' + str(verbruik_warmtepomp) + ' kW')
                label_min_temp.configure(text='Mininum temperature: ' + str(min_temperatuur) + ' °C')
                label_max_temp.configure(text='Maximum temperature: ' + str(max_temperatuur) + ' °C')

                edit_pump.destroy()

            edit_min_temp = CTkLabel(edit_pump, text='Edit the minimum temparature of your house (in °C):')
            entry_min_temp = CTkEntry(edit_pump)
            entry_min_temp.insert(0, min_temperatuur)
            edit_max_temp = CTkLabel(edit_pump, text='Edit het maximum temperature of your house (in °C):')
            entry_max_temp = CTkEntry(edit_pump)
            entry_max_temp.insert(0, max_temperatuur)
            edit_verbruik = CTkLabel(edit_pump, text='Edit the power of the heat pump (in kW):')
            entry_verbruik = CTkEntry(edit_pump)
            entry_verbruik.insert(0, verbruik_warmtepomp)
            edit_COP = CTkLabel(edit_pump, text='Edit the COP (coëfficient of performance) of your heat pump: ')
            entry_COP = CTkEntry(edit_pump)
            entry_COP.insert(0, COP)
            edit_U_waarde = CTkLabel(edit_pump, text='Edit the U-value of the isolation in your house (in W/m².°C):')
            entry_U_waarde = CTkEntry(edit_pump)
            entry_U_waarde.insert(0, U_waarde)
            edit_opp_muren = CTkLabel(edit_pump,
                                      text='Edit the total surface of the walls (including the roof) in your house (in m²):')
            entry_opp_muren = CTkEntry(edit_pump)
            entry_opp_muren.insert(0, oppervlakte_muren)
            edit_volume_huis = CTkLabel(edit_pump, text='Edit the total volume of your house (in m³):')
            entry_volume_huis = CTkEntry(edit_pump)
            entry_volume_huis.insert(0, volume_huis)
            btn_confirm = CTkButton(edit_pump, text='Confirm', command=bewerk)
            btn_cancel = CTkButton(edit_pump, text='Cancel', command=edit_pump.destroy)

            edit_min_temp.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_min_temp.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_max_temp.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_max_temp.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_COP.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_COP.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_U_waarde.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_U_waarde.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_opp_muren.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_opp_muren.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_volume_huis.grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_volume_huis.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            btn_confirm.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')

        frame_settings.rowconfigure((0, 1, 2, 3), uniform='uniform', weight=1)
        frame_settings.columnconfigure(0, uniform='uniform', weight=1)

        label_verbruik = CTkLabel(frame_settings, text='Power: ' + str(verbruik_warmtepomp) + ' kW')
        label_min_temp = CTkLabel(frame_settings, text='Mininum temperature: ' + str(min_temperatuur) + ' °C')
        label_max_temp = CTkLabel(frame_settings, text='Maximum temperature: ' + str(max_temperatuur) + ' °C')
        btn_configure_heat_pump = CTkButton(frame_settings, text='Configure heat pump', command=configure_heat_pump)

        label_verbruik.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_min_temp.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        label_max_temp.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        btn_configure_heat_pump.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        frame_current_temperature.rowconfigure(0, uniform='uniform', weight=1)
        frame_current_temperature.rowconfigure(1, uniform='unform', weight=3)
        frame_current_temperature.columnconfigure(0, uniform='uniform', weight=1)

        label_production_title = CTkLabel(frame_current_temperature, text='Current Temperature:',
                                          text_font=('Biome', 10))
        label_production = CTkLabel(frame_current_temperature, text=str(huidige_temperatuur), text_font=('Biome', 60))

        label_production_title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_production.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# Frame om de status van de batterijen te controleren
class FrameBatterijen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Battery', text_font=('Biome', 15, 'bold'))
        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        frame1 = CTkFrame(self)
        frame1.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        frame1.rowconfigure(0, uniform='uniform', weight=1)
        frame1.columnconfigure((0, 1), uniform='uniform', weight=1)

        def batterij_bewerken():
            edit_battery = CTkToplevel(self)
            edit_battery.iconbitmap('I_solarhouseicon.ico')
            edit_battery.title('Configure batteries')
            edit_battery.geometry('300x300')
            edit_battery.grab_set()

            def bewerk():
                global totale_batterijcapaciteit, batterij_power, batterij_laadvermogen
                totale_batterijcapaciteit = float(entry_capacity.get())
                batterij_power = float(entry_power.get())
                batterij_laadvermogen = float(entry_laadvermogen.get())

                lijst_verbruiken[1] = - batterij_power
                lijst_verbruiken[2] = batterij_laadvermogen

                if totale_batterijcapaciteit == '' or batterij_power == '' or batterij_laadvermogen == "":
                    messagebox.showwarning('Warning', 'Please fill in all the boxes')
                else:
                    label_batterijcapaciteit.configure(
                        text='Total battery capacity: ' + str(totale_batterijcapaciteit) + ' kWh')
                    label_power.configure(text='Battery power: ' + str(batterij_power) + ' kW')
                    label_laadvermogen.configure(text='Load power: ' + str(batterij_laadvermogen) + ' kW')

                    if totale_batterijcapaciteit == 0:
                        percentage = 100
                    else:
                        percentage = int(int(batterij_niveau) / int(totale_batterijcapaciteit))
                    label_percentage.configure(text=str(percentage))
                    progress.set(percentage)

                    edit_battery.destroy()

            edit_battery.rowconfigure((0, 1, 2, 3, 4, 5), uniform='uniform', weight=2)
            edit_battery.rowconfigure((6), uniform='uniform', weight=3)
            edit_battery.columnconfigure((0, 1), uniform='uniform', weight=1)

            edit_capacity = CTkLabel(edit_battery, text='Fill in the total battery capacity (in kWh): ')
            entry_capacity = CTkEntry(edit_battery)
            entry_capacity.insert(0, totale_batterijcapaciteit)
            edit_power = CTkLabel(edit_battery, text='Fill in the battery power of your batteries (in kW): ')
            entry_power = CTkEntry(edit_battery)
            entry_power.insert(0, batterij_power)
            edit_laadvermogen = CTkLabel(edit_battery, text='Fill in the load power of your batteries (in kW): ')
            entry_laadvermogen = CTkEntry(edit_battery)
            entry_laadvermogen.insert(0, batterij_laadvermogen)

            btn_confirm = CTkButton(edit_battery, text='Confirm', command=bewerk)
            btn_cancel = CTkButton(edit_battery, text='Cancel', command=edit_battery.destroy)

            edit_capacity.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_capacity.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_power.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_power.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            edit_laadvermogen.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_laadvermogen.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            btn_confirm.grid(row=6, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel.grid(row=6, column=0, padx=5, pady=5, sticky='nsew')

        frame_toevoegen = CTkFrame(frame1)
        frame_batterijniveau = CTkFrame(frame1)

        frame_toevoegen.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_batterijniveau.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        frame_toevoegen.rowconfigure((0, 1, 2, 3), uniform='uniform', weight=1)
        frame_toevoegen.columnconfigure(0, uniform='uniform', weight=1)

        label_batterijcapaciteit = CTkLabel(frame_toevoegen,
                                            text='Total battery capacity: ' + str(totale_batterijcapaciteit) + ' kWh')
        label_power = CTkLabel(frame_toevoegen, text='Battery Power: ' + str(batterij_power) + ' kW')
        label_laadvermogen = CTkLabel(frame_toevoegen, text='Load Power: ' + str(batterij_laadvermogen) + ' kW')
        btn_batterij_toevoegen = CTkButton(frame_toevoegen, text='Conigure your batteries', command=batterij_bewerken)

        label_batterijcapaciteit.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_power.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        label_laadvermogen.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        btn_batterij_toevoegen.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        frame_batterijniveau.rowconfigure((0, 2), uniform='uniform', weight=1)
        frame_batterijniveau.rowconfigure(1, uniform='uniform', weight=3)
        frame_batterijniveau.columnconfigure(0, uniform='uniform', weight=1)

        label_battery_level = CTkLabel(frame_batterijniveau, text='Current battery level:')
        if totale_batterijcapaciteit == 0:
            percentage = 100
        else:
            percentage = batterij_niveau / totale_batterijcapaciteit
        label_percentage = CTkLabel(frame_batterijniveau, text=str(percentage) + '%', text_font=(('Biome'), 60))
        progress = CTkProgressBar(frame_batterijniveau)
        progress.set(percentage)

        label_battery_level.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_percentage.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        progress.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

# Frame om de zonnepanelen te controleren
class FrameZonnepanelen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='unifrom', weight=4)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Solar Panels', text_font=('Biome', 15, 'bold'))
        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        frame1 = CTkFrame(self)
        frame1.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        frame1.rowconfigure(0, uniform='uniform', weight=1)
        frame1.columnconfigure((0, 1), uniform='unifrom', weight=1)

        frame_oppervlakte = CTkFrame(frame1)
        frame_productie = CTkFrame(frame1)
        frame_oppervlakte.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_productie.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        frame_oppervlakte.rowconfigure((0, 1, 2, 3), uniform='uniform', weight=1)
        frame_oppervlakte.columnconfigure(0, uniform='uniform', weight=1)

        def zonnepanelen_bewerken():
            edit_panels = CTkToplevel(self)
            edit_panels.iconbitmap('I_solarhouseicon.ico')
            edit_panels.title('Configure solar panels')
            edit_panels.geometry('300x230')
            edit_panels.grab_set()

            def bewerk():
                global aantal_zonnepanelen, oppervlakte_zonnepanelen
                aantal_zonnepanelen = spinbox_aantal.get()
                oppervlakte_zonnepanelen = entry_oppervlakte.get()

                if aantal_zonnepanelen == '' or oppervlakte_zonnepanelen == '':
                    messagebox.showwarning('Warning', 'Please fill in all the boxes')
                else:
                    label_aantal_zonnepanelen.configure(text='Number of solar panels: ' + str(aantal_zonnepanelen))
                    label_oppervlakte_zonnepanelen.configure(text='Total area of solar panels: ' + str(
                        aantal_zonnepanelen * float(oppervlakte_zonnepanelen)) + ' m²')
                    edit_panels.destroy()

            edit_panels.rowconfigure((0, 1, 2, 3), uniform='uniform', weight=2)
            edit_panels.rowconfigure((4), uniform='uniform', weight=3)
            edit_panels.columnconfigure((0, 1), uniform='uniform', weight=1)

            label_aantal = CTkLabel(edit_panels, text='Fill in the total number of solar panels:')
            spinbox_aantal = Spinbox3(edit_panels, step_size=1)
            spinbox_aantal.set(aantal_zonnepanelen)
            label_oppervlakte = CTkLabel(edit_panels, text='Fill in the area of one solar panel (in m²):')
            entry_oppervlakte = CTkEntry(edit_panels)
            entry_oppervlakte.insert(0, oppervlakte_zonnepanelen)
            btn_confirm = CTkButton(edit_panels, text='Confirm', command=bewerk)
            btn_cancel = CTkButton(edit_panels, text='Cancel', command=edit_panels.destroy)

            label_aantal.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            spinbox_aantal.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            label_oppervlakte.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_oppervlakte.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            btn_confirm.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel.grid(row=4, column=0, padx=5, pady=5, sticky='nsew')

        label_aantal_zonnepanelen = CTkLabel(frame_oppervlakte,
                                             text='Number of solar panels: ' + str(aantal_zonnepanelen))
        label_oppervlakte_zonnepanelen = CTkLabel(frame_oppervlakte, text='Total area of solar panels: ' + str(
            oppervlakte_zonnepanelen) + ' m²')
        label_rendement = CTkLabel(frame_oppervlakte,
                                   text='Efficiency: ' + str(int(rendement_zonnepanelen * 100)) + ' %')
        btn_zonnepaneel_toevoegen = CTkButton(frame_oppervlakte, text='Configure your solar panels',
                                              command=zonnepanelen_bewerken)

        label_aantal_zonnepanelen.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_oppervlakte_zonnepanelen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        label_rendement.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        btn_zonnepaneel_toevoegen.grid(row=3, column=0, padx=10, pady=5, sticky='nsew')

        frame_productie.rowconfigure(0, uniform='uniform', weight=1)
        frame_productie.rowconfigure(1, uniform='unform', weight=3)
        frame_productie.columnconfigure(0, uniform='uniform', weight=1)

        label_production_title = CTkLabel(frame_productie, text='Current Production:', text_font=('Biome', 10))
        label_production = CTkLabel(frame_productie, text=str(current_production), text_font=('Biome', 60))

        label_production_title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_production.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# Frame om de apparaten in het huishouden te controleren
class FrameApparaten(CTkFrame):
    def __init__(self, parent):
        global frame_met_apparaten
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.grid_rowconfigure((0, 2), uniform="uniform", weight=1)
        self.grid_rowconfigure(1, uniform="uniform", weight=16)
        self.grid_columnconfigure((0, 1), uniform="uniform", weight=1)
        global frame_height
        global frame_width
        frame_height = self.winfo_screenheight()
        frame_width = self.winfo_screenwidth()

        btn_newdevice = CTkButton(self, text='Add new device', command=lambda: self.new_device(frame_met_apparaten))
        btn_newdevice.grid(row=2, column=1, padx=5, sticky='nsew')
        btn_editdevice = CTkButton(self, text='Edit existing device', command=lambda: self.edit_device(frame_met_apparaten))
        btn_editdevice.grid(row=2, column=0, padx=5, sticky='nsew')
        title = CTkLabel(self, text="Current Devices", text_font=('Biome', 15, 'bold'), pady=0)
        title.grid(row=0, column=0, columnspan=2, sticky='nsew')
        frame1 = CTkFrame(self, fg_color='gray', pady=0)
        frame1.grid(row=1, column=0, columnspan=2, sticky='nsew')

        my_canvas = Canvas(frame1)
        my_canvas.pack(side='left', fill='both', expand=1, pady=0)

        my_scrollbar = CTkScrollbar(frame1, orientation='vertical', command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill='y')

        frame_met_apparaten = CTkFrame(my_canvas, corner_radius=0)
        my_canvas.create_window((0, 0), window=frame_met_apparaten, anchor='nw', height=2000)

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        self.apparaten_in_frame(frame_met_apparaten)

    def apparaten_in_frame(self, frame_met_apparaten):
        for widget in frame_met_apparaten.winfo_children():
            widget.destroy()
        for nummer in range(3,len(lijst_apparaten)):
            naam = lijst_apparaten[nummer]
            soort = lijst_soort_apparaat[nummer]
            uren = lijst_aantal_uren[nummer]
            uren_na_elkaar = lijst_uren_na_elkaar[nummer]
            capaciteit = lijst_capaciteit[nummer]
            verbruik = lijst_verbruiken[nummer]
            deadline = lijst_deadlines[nummer]
            beginuur = lijst_beginuur[nummer]
            remember = lijst_remember_settings[nummer]
            status = lijst_status[nummer]
            APPARAAT(frame_met_apparaten, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember,
                     status)

    def new_device(self, frame_met_apparaten):

        new_window = CTkToplevel(self)
        new_window.iconbitmap('I_solarhouseicon.ico')
        new_window.title('Add new device')
        new_window.geometry('350x610')
        new_window.grab_set()

        new_window.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), uniform='uniform', weight=2)
        new_window.rowconfigure(13, uniform='uniform', weight=3)
        new_window.columnconfigure((0,1), uniform='uniform', weight=1)

        def show_rest(event):
            global entry_verbruik, spinbox_deadline, checkbox_deadline, spinbox_hours, checkbox_consecutive, \
                entry_capacity, checkbox_beginuur, spinbox_beginuur, checkbox_remember

            for widget in new_window.winfo_children()[4:]:
                widget.destroy()

            if entry_soort.get() == 'Device with battery':
                label_verbruik = CTkLabel(new_window, text='Fill in the load power of the device (in kW):')
                entry_verbruik = CTkEntry(new_window)
                label_capacity = CTkLabel(new_window, text='Fill in the battery capacity (in kWh):')
                entry_capacity = CTkEntry(new_window)
                label_beginuur = CTkLabel(new_window, text='In how many hours do you want the device to start?:')
                spinbox_beginuur = Spinbox3(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text='Start immediately', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='In how many hours do you want the device to be ready?:')
                spinbox_deadline = Spinbox3(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

                label_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                label_capacity.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_capacity.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                label_beginuur.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember.grid(row=12, column=0, columnspan=2, padx=50, pady=5, sticky='nsew')

            if entry_soort.get() == 'Consumer':
                label_verbruik = CTkLabel(new_window, text='Fill in the power of the device (in kW):')
                entry_verbruik = CTkEntry(new_window)
                label_hours = CTkLabel(new_window, text='Fill in the runtime of the device:')
                spinbox_hours = Spinbox2(new_window, step_size=1)
                checkbox_consecutive = CTkCheckBox(new_window, text='Consecutive hours')
                label_beginuur = CTkLabel(new_window, text='In how many hours do you want the device to start?: ')
                spinbox_beginuur = Spinbox3(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text='Start immediately', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='Im how many hours do you want the device to be ready?:')
                spinbox_deadline = Spinbox3(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

                label_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                label_hours.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_hours.grid(row=7, column=0, padx=8, pady=5, sticky='nsew')
                checkbox_consecutive.grid(row=7, column=1, padx=8, pady=5, sticky='nsew')
                label_beginuur.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember.grid(row=12, column=0, columnspan=2, padx=35, pady=5, sticky='nsew')

            if entry_soort.get() == 'Always on':
                label_verbruik = CTkLabel(new_window, text='Fill in the power of the device (in kW):')
                entry_verbruik = CTkEntry(new_window)
                label_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            btn_confirm = CTkButton(new_window, text='confirm', command=apparaat_toevoegen)
            btn_confirm.grid(row=13, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
            btn_cancel.grid(row=13, column=0, padx=5, pady=5, sticky='nsew')

        def apparaat_toevoegen():
            naam = entry_naam.get()
            soort = entry_soort.get()

            if soort == 'Always on':
                uren = 24
                uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = float(entry_verbruik.get())
                deadline = '/'
                beginuur = '/'
                remember = 1
                status = 1

            if soort == 'Device with battery':
                capaciteit = float(entry_capacity.get())
                verbruik = float(entry_verbruik.get())
                if checkbox_deadline.get() == 0:
                    uren = capaciteit // verbruik
                else:
                    uren = 0
                uren_na_elkaar = '/'
                if checkbox_beginuur.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur.get()
                if checkbox_deadline.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline.get()
                remember = checkbox_remember.get()
                status = 0

            if soort == 'Consumer':
                uren = spinbox_hours.get()
                if checkbox_consecutive.get() == 1:
                    uren_na_elkaar = uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = float(entry_verbruik.get())
                if checkbox_beginuur.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur.get()
                if checkbox_deadline.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline.get()
                remember = checkbox_remember.get()
                status = 0

            if naam == '' or soort == '' or uren == '' or uren_na_elkaar == '' or capaciteit == '' or deadline == '':
                messagebox.showwarning('Warning', 'Please make sure to fill in all the boxes')
            else:
                APPARAAT(frame_met_apparaten, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline,
                         beginuur, remember, status)
                apparaat_toevoegen_database(lijst_apparaten, lijst_verbruiken, lijst_beginuur, lijst_deadlines,
                                            lijst_aantal_uren, lijst_uren_na_elkaar, lijst_soort_apparaat,
                                            lijst_capaciteit, lijst_remember_settings, lijst_status)
                new_window.destroy()

        def checkbox_command():
            if checkbox_deadline.get() == 1:
                spinbox_deadline.inactiveer()
            else:
                spinbox_deadline.activeer()
            if checkbox_beginuur.get() == 1:
                spinbox_beginuur.inactiveer()
            else:
                spinbox_beginuur.activeer()

        label_naam = CTkLabel(new_window, text='Fill in the name of the device:')
        entry_naam = CTkEntry(new_window)
        label_soort = CTkLabel(new_window, text='Select the kind of the device:')
        lijst_soorten = ['Always on', 'Device with battery', 'Consumer']
        entry_soort = CTkComboBox(new_window, values=lijst_soorten, command=show_rest)
        entry_soort.set('')

        label_naam.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_naam.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        label_soort.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_soort.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_confirm = CTkButton(new_window, text='confirm', command=apparaat_toevoegen)
        btn_confirm.grid(row=13, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
        btn_cancel.grid(row=13, column=0, padx=5, pady=5, sticky='nsew')

    def edit_device(self, frame_met_apparaten):
        edit_window = CTkToplevel(self)
        edit_window.iconbitmap('I_solarhouseicon.ico')
        edit_window.title('Edit device')
        edit_window.geometry('350x650')
        edit_window.grab_set()

        edit_window.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), uniform='uniform', weight=2)
        edit_window.rowconfigure((13, 14), uniform='uniform', weight=3)
        edit_window.columnconfigure((0,1), uniform='uniform', weight=1)

        def apparaat_wijzigen():
            soort = lijst_soort_apparaat[apparaat_nummer]

            if soort == 'Always on':
                naam = entry_naam_2.get()
                uren = 24
                uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = float(entry_verbruik_2.get())
                deadline = '/'
                beginuur = '/'
                remember = 0
                status = 1

            if soort == 'Device with battery':
                naam = entry_naam_2.get()
                capaciteit = float(entry_capacity_2.get())
                verbruik = float(entry_verbruik_2.get())
                if checkbox_deadline.get() == 0:
                    uren = capaciteit/verbruik
                else:
                    uren = 0
                uren_na_elkaar = '/'
                if checkbox_beginuur_2.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur_2.get()
                if checkbox_deadline_2.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline_2.get()
                remember = checkbox_remember_2.get()
                status = 0

            if soort == 'Consumer':
                naam = entry_naam_2.get()
                uren = spinbox_hours_2.get()
                if checkbox_consecutive_2.get() == 1:
                    uren_na_elkaar = uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = float(entry_verbruik_2.get())
                if checkbox_beginuur_2.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur_2.get()
                if checkbox_deadline_2.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline_2.get()
                remember = checkbox_remember_2.get()
                status = 0

            kolom = apparaat_nummer % 3
            rij = apparaat_nummer // 3

            if naam == '' or capaciteit == '' or uren == '' or uren_na_elkaar == '' or verbruik == '' or deadline == '' or beginuur == '':
                messagebox.showwarning('Warning', 'Please make sure to fill in all the boxes')
            else:
                lijst_apparaten[apparaat_nummer] = naam
                lijst_soort_apparaat[apparaat_nummer] = soort
                lijst_capaciteit[apparaat_nummer] = capaciteit
                lijst_aantal_uren[apparaat_nummer] = uren
                lijst_uren_na_elkaar[apparaat_nummer] = uren_na_elkaar
                lijst_verbruiken[apparaat_nummer] = verbruik
                lijst_deadlines[apparaat_nummer] = deadline
                lijst_beginuur[apparaat_nummer] = beginuur
                lijst_remember_settings[apparaat_nummer] = remember
                lijst_status[apparaat_nummer] = status
                APPARAAT(frame_met_apparaten, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember,
                         status, column=kolom, row=rij)
                apparaat_toevoegen_database(lijst_apparaten, lijst_verbruiken, lijst_beginuur, lijst_deadlines,
                                            lijst_aantal_uren, lijst_uren_na_elkaar, lijst_soort_apparaat,
                                            lijst_capaciteit, lijst_remember_settings, lijst_status)
                edit_window.destroy()

        def show_options(event):
            global entry_naam_2, entry_verbruik_2, spinbox_deadline_2, checkbox_deadline_2, spinbox_hours_2, checkbox_consecutive_2, \
                entry_capacity_2, checkbox_beginuur_2, spinbox_beginuur_2, checkbox_remember_2
            global apparaat_nummer

            for widget in edit_window.winfo_children()[2:]:
                widget.destroy()

            apparaat_nummer = lijst_apparaten.index(choose_device.get())
            label_naam_2 = CTkLabel(edit_window, text='Edit the name of the device:')
            entry_naam_2 = CTkEntry(edit_window)
            entry_naam_2.delete(0, 'end')
            entry_naam_2.insert(0, lijst_apparaten[apparaat_nummer])

            label_naam_2.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_naam_2.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if lijst_soort_apparaat[apparaat_nummer] == 'Always on':
                label_verbruik_2 = CTkLabel(edit_window, text='Edit the power of the device (in kW):')
                entry_verbruik_2 = CTkEntry(edit_window)
                entry_verbruik_2.delete(0, 'end')
                entry_verbruik_2.insert(0, lijst_verbruiken[apparaat_nummer])

                label_verbruik_2.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_verbruik_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            else:
                if lijst_soort_apparaat[apparaat_nummer] == 'Device with battery':
                    label_verbruik_2 = CTkLabel(edit_window, text='Edit the load power of the device (in kW):')
                    entry_verbruik_2 = CTkEntry(edit_window)
                    entry_verbruik_2.delete(0, 'end')
                    entry_verbruik_2.insert(0, lijst_verbruiken[apparaat_nummer])
                    label_capacity_2 = CTkLabel(edit_window,
                                                text='Change the battery capacity from the device (in kWh):')
                    entry_capacity_2 = CTkEntry(edit_window)
                    entry_capacity_2.delete(0, 'end')
                    entry_capacity_2.insert(0, lijst_capaciteit[apparaat_nummer])
                    label_verbruik_2.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    entry_verbruik_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    label_capacity_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    entry_capacity_2.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

                if lijst_soort_apparaat[apparaat_nummer] == 'Consumer':
                    label_verbruik_2 = CTkLabel(edit_window, text='Edit the power of the device (in kW):')
                    entry_verbruik_2 = CTkEntry(edit_window)
                    entry_verbruik_2.delete(0, 'end')
                    entry_verbruik_2.insert(0, lijst_verbruiken[apparaat_nummer])
                    label_hours_2 = CTkLabel(edit_window, text='Edit the runtime of the device:')
                    spinbox_hours_2 = Spinbox2(edit_window, step_size=1)
                    checkbox_consecutive_2 = CTkCheckBox(edit_window, text='Consecutive hours')
                    spinbox_hours_2.set(lijst_aantal_uren[apparaat_nummer])
                    if lijst_aantal_uren[apparaat_nummer] == lijst_uren_na_elkaar[apparaat_nummer]:
                        checkbox_consecutive_2.select()

                    label_verbruik_2.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    entry_verbruik_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    label_hours_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    spinbox_hours_2.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')
                    checkbox_consecutive_2.grid(row=7, column=1, padx=5, pady=5, sticky='nsew')

                label_beginuur_2 = CTkLabel(edit_window, text='In how many hours do you want the device to start?')
                spinbox_beginuur_2 = Spinbox3(edit_window, step_size=1)
                checkbox_beginuur_2 = CTkCheckBox(edit_window, text='Start immediately', command=checkbox_command2)
                if lijst_beginuur[apparaat_nummer] == '/':
                    checkbox_beginuur_2.select()
                    spinbox_beginuur_2.inactiveer()
                else:
                    spinbox_beginuur_2.set(lijst_beginuur[apparaat_nummer])

                label_deadline_2 = CTkLabel(edit_window, text='In how many hours do you want the device to be ready?')
                spinbox_deadline_2 = Spinbox3(edit_window, step_size=1)
                checkbox_deadline_2 = CTkCheckBox(edit_window, text='No Deadline', command=checkbox_command1)
                if lijst_deadlines[apparaat_nummer] == '/':
                    checkbox_deadline_2.select()
                    spinbox_deadline_2.inactiveer()
                else:
                    spinbox_deadline_2.set(lijst_deadlines[apparaat_nummer])

                checkbox_remember_2 = CTkCheckBox(edit_window, text='Remember start time and deadline')
                if lijst_remember_settings[apparaat_nummer] == 1:
                    checkbox_remember_2.select()

                label_beginuur_2.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur_2.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur_2.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline_2.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline_2.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline_2.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember_2.grid(row=12, column=0, columnspan=2, padx=35, pady=5, sticky='nsew')

            btn_confirm_2 = CTkButton(edit_window, text='confirm', command=apparaat_wijzigen, state=NORMAL)
            btn_confirm_2.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel_2 = CTkButton(edit_window, text='cancel', command=edit_window.destroy)
            btn_cancel_2.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')
            btn_delete_device = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen,
                                          fg_color='red', state=NORMAL)
            btn_delete_device.grid(row=13, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        def apparaat_verwijderen():
            response = messagebox.askokcancel('Delete Device', 'Are you sure you want to delete this device?')
            if response == True:
                lijst_apparaten.pop(apparaat_nummer)
                lijst_soort_apparaat.pop(apparaat_nummer)
                lijst_capaciteit.pop(apparaat_nummer)
                lijst_aantal_uren.pop(apparaat_nummer)
                lijst_uren_na_elkaar.pop(apparaat_nummer)
                lijst_verbruiken.pop(apparaat_nummer)
                lijst_deadlines.pop(apparaat_nummer)
                lijst_beginuur.pop(apparaat_nummer)
                lijst_remember_settings.pop(apparaat_nummer)
                lijst_status.pop(apparaat_nummer)
                self.apparaten_in_frame(frame_met_apparaten)
                apparaat_toevoegen_database(lijst_apparaten, lijst_verbruiken, lijst_beginuur, lijst_deadlines,
                                            lijst_aantal_uren, lijst_uren_na_elkaar, lijst_soort_apparaat,
                                            lijst_capaciteit, lijst_remember_settings, lijst_status)
                edit_window.destroy()

        def checkbox_command1():
            if checkbox_deadline_2.get() == 1:
                spinbox_deadline_2.inactiveer()
            else:
                spinbox_deadline_2.activeer()

        def checkbox_command2():
            if checkbox_beginuur_2.get() == 1:
                spinbox_beginuur_2.inactiveer()
            else:
                spinbox_beginuur_2.activeer()

        text_choose = CTkLabel(edit_window, text='Choose the device you want to edit:')
        choose_device = CTkComboBox(edit_window, values=lijst_apparaten[3:], command=show_options)
        choose_device.set('')

        text_choose.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        choose_device.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_confirm_2 = CTkButton(edit_window, text='confirm', command=apparaat_wijzigen, state=DISABLED)
        btn_confirm_2.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel_2 = CTkButton(edit_window, text='cancel', command=edit_window.destroy)
        btn_cancel_2.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')
        btn_delete_device = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen, fg_color='red',
                                      state=DISABLED)
        btn_delete_device.grid(row=13, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

#code voor de kleine frame's in FrameApparaten
class APPARAAT(CTkFrame):
    def __init__(self, parent, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember,
                 status, column=None, row=None):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure('all', uniform="uniform", weight=1)
        self.columnconfigure('all', uniform='uniform', weight=1)

        if naam not in lijst_apparaten:
            lijst_apparaten.append(naam)
            lijst_soort_apparaat.append(soort)
            lijst_aantal_uren.append(uren)
            lijst_uren_na_elkaar.append(uren_na_elkaar)
            lijst_capaciteit.append(capaciteit)
            lijst_verbruiken.append(verbruik)
            lijst_deadlines.append(deadline)
            lijst_beginuur.append(beginuur)
            lijst_remember_settings.append(remember)
            lijst_status.append(status)

        nummer_apparaat = lijst_apparaten.index(naam)

        if column == None and row == None:
            rij = nummer_apparaat // 3
            kolom = nummer_apparaat % 3
        else:
            rij = row
            kolom = column
        self.grid(row=rij, column=kolom, sticky='nsew')

        label_naam = CTkLabel(self, text=naam, text_font=('Biome', 12, 'bold'))
        label_naam.grid(row=0, column=0, sticky='nsew')
        label_soort = CTkLabel(self, text=soort, text_font=('Biome', 10))
        label_soort.grid(row=1, column=0, sticky='nsew')
        if soort == 'Consumer':
            label_verbruik = CTkLabel(self, text='Power: ' + str(verbruik) + ' kW', text_font=('Biome', 10))
            label_verbruik.grid(row=2, column=0, sticky='nsew')
            if uren == uren_na_elkaar:
                na_elkaar = 'succesively'
            else:
                na_elkaar = 'random'
            label_uren = CTkLabel(self, text='Runtime left: ' + str(uren) + ' hours (' + na_elkaar + ')',
                                  text_font=('Biome', 10))
            label_uren.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/' and deadline == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            elif beginuur == '/' and deadline != '/':
                label_beginuur = CTkLabel(self, text='Device has started', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text='Device starts in: ' + str(beginuur) + ' hours',
                                          text_font=('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text='Needs to be ready in: ' + str(deadline) + ' hours',
                                          text_font=('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Device with battery':
            label_verbruik = CTkLabel(self, text='Load power: ' + str(verbruik) + ' kW', text_font=('Biome', 10))
            label_verbruik.grid(row=2, column=0, sticky='nsew')
            label_capaciteit = CTkLabel(self, text='Battery Capacity: ' + str(capaciteit) + ' kWh',
                                        text_font=('Biome', 10))
            label_capaciteit.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/' and deadline == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            elif beginuur == '/' and deadline != '/':
                label_beginuur = CTkLabel(self, text='Device is loading', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text='Device starts loading in: ' + str(beginuur) + ' hours',
                                          text_font=('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text='Needs to be ready in: ' + str(deadline) + ' hours',
                                          text_font=('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Always on':
            label_verbruik = CTkLabel(self, text='Power: ' + str(verbruik) + ' kW', text_font=('Biome', 10))
            label_verbruik.grid(row=2, column=0, sticky='nsew')
            white_space_1 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_1.grid(row=3, column=0, sticky='nsew')
            white_space_2 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_2.grid(row=4, column=0, sticky='nsew')
            white_space_3 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_3.grid(row=5, column=0, sticky='nsew')

        if status == 1:
            bg_color = "#74d747"
            status_text = 'ON'
        else:
            bg_color = "#f83636"
            status_text = 'OFF'
        status = CTkLabel(self, text=status_text, bg_color=bg_color, width=0.1185 * frame_width,
                          height=0.025 * frame_height)
        status.grid(row=6, column=0, padx=5, pady=5)

# StatisticFrame met verwijzingen naar ...
class StatisticFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, width=3840, height=2160)
        self.propagate('false')

        self.columnconfigure((0, 1), uniform='uniform', weight=2)
        self.columnconfigure(2, uniform='uniform', weight=3)
        self.rowconfigure(0, uniform='uniform', weight=2)
        self.rowconfigure(1, uniform='uniform', weight=1)

        frame_PvsC = FramePvsC(self)
        frame_verbruikers = FrameVerbruikers(self)
        frame_energieprijs = FrameEnergieprijs(self)
        frame_weer = FrameWeer(self)
        frame_totalen = FrameTotalen(self)

        frame_PvsC.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        frame_verbruikers.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        frame_energieprijs.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_weer.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        frame_totalen.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')

# Frame PvsC: grafiek van de productie en consumptie van energie
class FramePvsC(CTkFrame):
    def __init__(self, parent):
        global lijst_consumptie, lijst_productie,lijst_uren
        global grafiek_PvsC, canvas_PvsC
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.grid_propagate(FALSE)

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure((1,2), uniform='uniform', weight=4)
        self.columnconfigure(0, uniform='uniform', weight=2)
        self.columnconfigure(1, uniform='uniform', weight=1)


        title = CTkLabel(self, text='Production vs Consumption', text_font=('Biome', 15, 'bold'))
        frame_graph = CTkFrame(self)
        frame_graph.grid_propagate('false')
        frame_consumption = CTkFrame(self)
        frame_production = CTkFrame(self)

        title.grid(row=0, column=0,columnspan=2, padx=5, pady=5, sticky='nsew')
        frame_graph.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky='nsew')
        frame_consumption.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        frame_production.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        lijst_uren = []
        for i in range(0,24):
            if i < 10:
                lijst_uren.append('0' + str(i) + ':00')
            else:
                lijst_uren.append(str(i)+':00')

        lijst_consumptie = [1,4,2,3,2,3,5,3,2,4,4,2,1,2,5,2,4,2,4,2,6,3,4,7]
        lijst_productie = [1,4,2,5,3,5,4,3,7,4,2,1,4,2,5,3,5,3,3,5,3,6,3,1]
        #lijst_labels = ['','','','','','','','','','','','','','','','','','','','','','','','']

        figure = Figure(facecolor='#292929')
        grafiek_PvsC = figure.add_subplot()
        grafiek_PvsC.plot(lijst_uren, lijst_consumptie, lijst_productie)

        grafiek_PvsC.set_title("Energy production and consumption of the last 24 hours", fontsize=10, color= 'white', pad=10)
        grafiek_PvsC.legend(['Energy consumption', 'Energy production'], loc='upper right',
                       facecolor='#262626',edgecolor='#262626', labelcolor = 'white')
        grafiek_PvsC.set_ylabel('Energy (in kWh)', color='white')
        grafiek_PvsC.set_facecolor('#262626')
        grafiek_PvsC.set(xlim=(0, 23), ylim=(0, 10))
        grafiek_PvsC.set_xticks(lijst_uren, lijst_uren, rotation=45, color='white')

        canvas_PvsC = FigureCanvasTkAgg(figure, frame_graph)
        canvas_PvsC.draw()
        canvas_PvsC.get_tk_widget().pack(fill=BOTH, expand=1, anchor=CENTER, pady=10)

# FrameVerbruikers: cirkeldiagram met grootste verbruikers in het huis (eventueel)
class FrameVerbruikers(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.grid_propagate(FALSE)

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=9)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Consumers', text_font=('Biome', 15, 'bold'))
        frame_verbruikers = CTkFrame(self)

        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_verbruikers.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        lijst_labels = [lijst_apparaten[0]] + lijst_apparaten[3:]
        verbruik_per_apparaat = [5,1,2,3]

        figure = Figure(facecolor='#292929')
        pie_verbruikers = figure.add_subplot()
        pie_verbruikers.pie(verbruik_per_apparaat)

        #pie_verbruikers.set_legend(lijst_labels)

        canvas_verbruikers = FigureCanvasTkAgg(figure, frame_verbruikers)
        canvas_verbruikers.draw()
        canvas_verbruikers.get_tk_widget().pack(fill=BOTH, expand=1, anchor=CENTER, pady=10)

# FrameEnergieprijs: geeft huidige energieprijs weer
class FrameEnergieprijs(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.grid_propagate(FALSE)

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Energy Price', text_font=('Biome', 15, 'bold'))
        frame_prijs = CTkFrame(self)

        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_prijs.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# FrameWeer: geeft huidgie weerssituatie weer:
class FrameWeer(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.grid_propagate(FALSE)

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Weather', text_font=('Biome', 15, 'bold'))
        frame_weer = CTkFrame(self)

        title.grid(row=0, column=0,padx=5, pady=5, sticky='nsew')
        frame_weer.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# FrameTotalen: geeft nog enkele totalen statistieken weer:
class FrameTotalen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.grid_propagate(FALSE)

        self.rowconfigure(0, uniform='uniform', weight=1)
        self.rowconfigure(1, uniform='uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Totals', text_font=('Biome', 15, 'bold'))
        frame_totalen = CTkFrame(self)

        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_totalen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

def app_loop():
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res_sentinel = cur.execute("SELECT SentinelInterface FROM ExtraWaarden")
    TupleSENTINEL = res_sentinel.fetchall()

    con.commit()
    cur.close()
    con.close()

    SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]
    print("voor while **********************************************************************************************")
    while SENTINEL == -1:
        time.sleep(1)

        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()

        res_sentinel = cur.execute("SELECT SentinelInterface FROM ExtraWaarden")
        TupleSENTINEL = res_sentinel.fetchall()

        cur.close()
        con.close()

        SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]
        print(SENTINEL)

    print("voor main loop **********************************************************************************************")
    app = MainApplication()
    app.mainloop()
    print("------------Einde Programma------------")
    print(lijst_apparaten)
    print(lijst_verbruiken)
    print(lijst_deadlines)
    print(lijst_status)
    print(lijst_remember_settings)
    print(current_date)
    print(aantal_zonnepanelen)
    print(oppervlakte_zonnepanelen)
    print(Prijzen24uur)
    print(Gegevens24uur)
    print(lijst_opwarming)
    print(lijst_warmteverliezen)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    cur.execute("UPDATE ExtraWaarden SET SentinelOptimalisatie =" + str(1))
    res_sentinel = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
    TupleSENTINEL = res_sentinel.fetchall()

    con.commit()
    cur.close()
    con.close()

    SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]
    print(SENTINEL)

def algoritme_loop():
    update_algoritme()

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    cur.execute("UPDATE ExtraWaarden SET SentinelInterface =" + str(0))

    res_sentinel = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
    TupleSENTINEL = res_sentinel.fetchall()

    con.commit()
    cur.close()
    con.close()

    SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]

    while SENTINEL == -1:
        time.sleep(1)

        con = sqlite3.connect("D_VolledigeDatabase.db")
        cur = con.cursor()

        res_sentinel = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
        TupleSENTINEL = res_sentinel.fetchall()

        cur.close()
        con.close()

        SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT TijdSeconden FROM ExtraWaarden")
    TupleTijdSeconden = res.fetchall()

    cur.close()
    con.close()

    TijdSeconden = [int(i2[0]) for i2 in TupleTijdSeconden][0]
    TijdSeconden2 = TijdSeconden%10 + 10
    print("Tijdsecoden2:")
    print(TijdSeconden2)
    vw1 = TijdSeconden2
    vw2 = TijdSeconden2 + 100
    vw3 = TijdSeconden2 + 20
    vw4 = TijdSeconden2 + 300
    vw5 = TijdSeconden2 + 40
    vw6 = TijdSeconden2 + 500
    print(vw1)
    while SENTINEL == 0:
        time.sleep(1)
        stringtijd = strftime('%S')
        print("stringtijd")
        print(stringtijd)
        inttijd = int(stringtijd)
        print("inttijd:")
        print(inttijd)
        if inttijd == vw1 or inttijd == vw2 or inttijd == vw3 or inttijd == vw4 or inttijd == vw5 or inttijd == vw6:
            print("update")
            update_algoritme()

            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()

            res_sentinel = cur.execute("SELECT SentinelOptimalisatie FROM ExtraWaarden")
            TupleSENTINEL = res_sentinel.fetchall()

            cur.close()
            con.close()

            SENTINEL = [int(i2[0]) for i2 in TupleSENTINEL][0]
        else:
            time.sleep(0.5)

    print("loop gedaan------------------------------------------------------------------------------------------------")

p1 = multiprocessing.Process(target=app_loop)
p2 = multiprocessing.Process(target=algoritme_loop)
if __name__ == "__main__":
    print("------------geheugen_veranderen------------")
    geheugen_veranderen()
    p1.start()
    p2.start()
    p1.join()
    p2.join()
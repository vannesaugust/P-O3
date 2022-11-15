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

########### Dark/Light mode en color theme instellen
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

############variabelen/lijsten aanmaken
current_date = '01-01-2016'
current_hour = 1
Prijzen24uur = []
Gegevens24uur = []
lijst_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = ['/','/', '/', '/', 4, '/']
lijst_uren_na_elkaar = ['/','/', '/',5,'/', 3]
lijst_verbruiken = [15, -14.344, 12.2, 14, 10, 12]
lijst_deadlines = ['/','/','/', 10, 11, 12]
lijst_beginuur = ['/','/', '/', 3, 6, 4]
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]
voorwaarden_apparaten_exacte_uren = [['/'], ['/'], ['/'], ['/'], ['/'], ['/']]
"""
lijst_apparaten = ['Fridge', 'Elektric Bike', 'Elektric Car', 'Dishwasher', 'Washing Manchine', 'Freezer']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = [2, 2, 2, 2, 3, 2]
lijst_uren_na_elkaar = [2, '/', '/', 2, 3, 2]
lijst_verbruiken = [30,12,100,52,85,13]
lijst_deadlines = [15,17,14,'/',23,14]
lijst_beginuur = ['/', '/', '/', '/', 18, '/']
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]
lijst_SENTINEL = [1]
"""
aantal_zonnepanelen = 0
oppervlakte_zonnepanelen = 0
rendement_zonnepanelen = 0.20

min_temperatuur = 19
max_temperatuur = 21
huidige_temperatuur = 20
verbruik_warmtepomp = 0
U_waarde = 0
oppervlakte_muren = 0
volume_huis = 0
opwarmingssnelheid = []
warmteverlies = []
warmtepomp_status = 0

totale_batterijcapaciteit = 0
oplaadsnelheid = 0

current_production = 0 #MOET UIT DE DATABASE KOMEN
current_consumption = 0 #MOET UIT DE DATABASE KOMEN
##########################
def update_algoritme():
    import O_parameters_geheel

    solver = po.SolverFactory('glpk')
    m = pe.ConcreteModel()

    #######################################################################################################
    # definiëren functies
    def variabelen_constructor(lijst, aantal_apparaten, aantal_uren):
        for p in range(aantal_uren * aantal_apparaten):  # totaal aantal nodige variabelen = uren maal apparaten
            lijst.add()  # hier telkens nieuwe variabele aanmaken

    def objectieffunctie(prijzen, variabelen, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen):
        obj_expr = 0
        for p in range(aantal_uren):
            subexpr = 0
            for q in range(len(wattagelijst)):
                subexpr = subexpr + wattagelijst[q] * variabelen[q * aantal_uren + (
                            p + 1)]  # eerst de variabelen van hetzelfde uur samentellen om dan de opbrengst van zonnepanelen eraf te trekken
            obj_expr = obj_expr + Delta_t * prijzen[p] * (subexpr - stroom_zonnepanelen[p])
        return obj_expr

    def exacte_beperkingen(variabelen, voorwaarden_apparaten, aantal_apparaten, voorwaarden_apparaten_lijst,
                           aantal_uren):
        for q in range(aantal_uren * aantal_apparaten):
            index_voor_voorwaarden = q // aantal_uren  # hierdoor weet je bij welk apparaat de uur-constraint hoort
            indexnummers = voorwaarden_apparaten_lijst[
                index_voor_voorwaarden]  # hier wordt de uur-constraint, horende bij een bepaald apparaat, opgevraagd
            for p in indexnummers:
                if type(p) == int:  # kan ook dat er geen voorwaarde is, dan wordt de uitdrukking genegeerd
                    voorwaarden_apparaten.add(expr=variabelen[
                                                       p + index_voor_voorwaarden * aantal_uren] == 1)  # variabele wordt gelijk gesteld aan 1

    # je kijkt het uur per uur, wnr het uur pos is dan tel je het er op de normale manier bij, wnr het iets negatief werd dan ga je een ander tarief pakken en tel je het zo bij die objectief

    def uiteindelijke_waarden(variabelen, aantaluren, namen_apparaten):
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
        return kost, apparaten_aanofuit

    def beperkingen_aantal_uur(werkuren_per_apparaat, variabelen, voorwaarden_werkuren, aantal_uren):
        for p in range(len(werkuren_per_apparaat)):
            som = 0
            for q in range(1, aantal_uren + 1):
                som = som + variabelen[
                    p * aantal_uren + q]  # hier neem je alle variabelen van hetzelfde apparaat, samen
            if type(werkuren_per_apparaat[p]) == int:
                voorwaarden_werkuren.add(expr=som == werkuren_per_apparaat[p])  # apparaat moet x uur aanstaan

    def starttijd(variabelen, starturen, constraint_lijst_startuur, aantal_uren):
        for q in range(len(starturen)):
            if type(starturen[q]) != str:
                p = starturen[q]
                for s in range(1, p):
                    constraint_lijst_startuur.add(expr=variabelen[aantal_uren * q + s] == 0)

    def finaal_uur(finale_uren, variabelen, constraint_lijst_finaal_uur, aantal_uren):
        for q in range(len(finale_uren)):  # dit is welk aparaat het over gaat
            if type(finale_uren[q]) == int:
                p = finale_uren[q] - 1  # dit is het eind uur, hierna niet meer in werking
                for s in range(p + 1, aantal_uren + 1):
                    constraint_lijst_finaal_uur.add(expr=variabelen[(aantal_uren * q) + s] == 0)

    def aantal_uren_na_elkaar(uren_na_elkaarVAR, variabelen, constraint_lijst_aantal_uren_na_elkaar, aantal_uren,
                              variabelen_start):
        # Dat een bepaald apparaat x aantal uur moet werken staat al in beperking_aantal_uur dus niet meer hier
        # wel nog zeggen dat de som van de start waardes allemaal slechts 1 mag zijn
        for i in range(len(uren_na_elkaarVAR)):  # zegt welk apparaat
            if type(uren_na_elkaarVAR[i]) == int:
                opgetelde_start = 0
                for p in range(1, aantal_uren + 1):  # zegt welk uur het is
                    opgetelde_start = opgetelde_start + variabelen_start[aantal_uren * i + p]
                # print('dit is eerste constraint', opgetelde_start)
                constraint_lijst_aantal_uren_na_elkaar.add(expr=opgetelde_start == 1)
        for i in range(len(uren_na_elkaarVAR)):  # dit loopt de apparaten af
            if type(uren_na_elkaarVAR[i]) == int:
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
            uitdrukking = (-1, som, max_verbruik_per_uur[p - 1])
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
            for p in range(beginindex_in_variabelen, beginindex_in_variabelen + aantaluren):
                temperatuur_dit_uur = temperatuur_dit_uur - warmteverliesfactor + warmtewinst * variabelen[p]
                uitdrukking = (ondergrens, temperatuur_dit_uur, bovengrens)
                voorwaardenlijst.add(expr=uitdrukking)

    def som_tot_punt(variabelen, beginpunt, eindpunt):
        som = 0
        for i in range(beginpunt, eindpunt + 1):
            som = som + variabelen[i]
        return som

    def voorwaarden_batterij(variabelen, constraintlijst, aantaluren, wattagelijst, namen_apparaten,
                             huidig_batterijniveau):
        index_ontladen = namen_apparaten.index('batterij_ontladen')
        index_opladen = namen_apparaten.index('batterij_opladen')
        for q in range(1, aantaluren + 1):
            som_ontladen = wattagelijst[index_ontladen] * som_tot_punt(variabelen, index_ontladen * aantaluren + 1,
                                                                       index_ontladen * aantaluren + q)
            som_opladen = wattagelijst[index_opladen] * som_tot_punt(variabelen, index_opladen * aantaluren + 1,
                                                                     index_opladen * aantaluren + q)
            verschil = som_opladen + som_ontladen + huidig_batterijniveau
            constraintlijst.add(expr=(0, verschil, None))

    # een lijst maken die de stand van de batterij gaat bijhouden als aantal wat maal aantal uur
    # op het einde van het programma dan aanpassen wat die batterij het laatste uur heeft gedaan en zo bijhouden in de database in die variabele
    # het getal in die variabele trek je ook altijd op bij som onladen en som ontladen hierboven

    # deze functie zal het aantal uur dat het apparaat moet werken verlagen op voorwaarden dat het apparaat ingepland stond
    # voor het eerste uur
    def verlagen_aantal_uur(lijst, aantal_uren,
                            te_verlagen_uren):  # voor aantal uur mogen er geen '/' ingegeven worden, dan crasht het
        print("Urenwerk na functie verlagen_aantal_uur")
        for i in range(len(te_verlagen_uren)):
            if pe.value(lijst[i * aantal_uren + 1]) == 1:
                con = sqlite3.connect("D_VolledigeDatabase.db")
                cur = con.cursor()
                cur.execute("UPDATE Geheugen SET UrenWerk =" + str(te_verlagen_uren[i] - 1) +
                            " WHERE Nummering =" + str(i))
                con.commit()
                res = cur.execute("SELECT UrenWerk FROM Geheugen")
                print(res.fetchall())

                # nu moet het volgende gebeuren met de database
                # te_verlagen_uren[i] = te_verlagen_uren[i] - 1

    def uur_omzetten(exacte_uren1apparaat):
        string = "'"
        for i2 in range(len(exacte_uren1apparaat)):
            if exacte_uren1apparaat[i2] == "/":
                return str(0)
            else:
                string = string + str(exacte_uren1apparaat[i2]) + ":"
        string = string[0:-1] + "'"
        return string

    # deze fucntie zal exacte uren als 'aan' aanduiden op voorwaarde dat het eerste uur als 'aan' was aangeduid en er ook was aangeduid dat
    # het apparaat x aantal uur na elkaar moest aanstaan, elk uur tot x-1 zal dan al naar 'aan' worden aangeduid voor de volgende berekeningen terug beginnen
    def opeenvolging_opschuiven(lijst, aantal_uren, opeenvolgende_uren, oude_exacte_uren):
        print("ExacteUren en eventueel UrenNaElkaar na functie opeenvolging_opschuiven ")
        for i in range(len(opeenvolgende_uren)):
            if type(opeenvolgende_uren[i]) == int and pe.value(lijst[i * aantal_uren + 1]) == 1:
                nieuwe_exacte_uren = []
                for p in range(1, opeenvolgende_uren[i] + 1):  # dus voor opeenvolgende uren 5, p zal nu 1,2,3,4
                    nieuwe_exacte_uren.append(p)
                con = sqlite3.connect("D_VolledigeDatabase.db")
                cur = con.cursor()
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

    def exacte_uren_naar_lijst(list_tuples, categorie):
        if categorie == "ExacteUren":
            # Zet tuples om naar strings
            # Alle nullen worden wel als integers weergegeven
            list_strings = [i[0] for i in list_tuples]
            list_ints = []
            # Als een string 0 wordt deze omgezet naar een "/"
            for i2 in list_strings:
                if i2 == 0:
                    list_ints.append("/")
                else:
                    # Splitst elke lijst waar een dubbelpunt in voorkomt zodat ieder uur nu apart in lijst_uren staat
                    lijst_uren = i2.split(":")
                    lijst_uren_ints = []
                    # Overloopt alle uren en voegt deze toe aan de lijst van exacte uren die bij dat apparaat hoort
                    for uur in lijst_uren:
                        lijst_uren_ints.append(int(uur))
                    # Voegt de lijst van exacte uren van een apparaat bij de lijst van exacte uren van de andere apparaten
                    list_ints.append(lijst_uren_ints)
            return list_ints

    # deze functie zal alle exacte uren die er waren verlagen met 1, als het 0 wordt dan wordt het later verwijderd uit de lijst
    def verlagen_exacte_uren(exacte_uren):
        print("ExacteUren na functie verlagen_exacte_uren")
        for i in range(len(exacte_uren)):  # dit gaat de apparaten af
            if exacte_uren[i] != '/':
                verlaagde_exacte_uren = []
                for uur in exacte_uren[i]:  # dit zal lopen over al de 'exacte uren' van een specifiek apparaat
                    if len(exacte_uren[i]) != 1:
                        if uur - 1 != 0:
                            verlaagde_exacte_uren.append(uur - 1)
                    else:
                        verlaagde_exacte_uren.append(uur - 1)
                if len(verlaagde_exacte_uren) == 0:
                    verlaagde_exacte_uren.append(0)
                con = sqlite3.connect("D_digeDatabase.db")
                cur = con.cursor()
                cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(verlaagde_exacte_uren) +
                            " WHERE Nummering =" + str(i))
                con.commit()

                # Ter illustratie
                res = cur.execute("SELECT ExacteUren FROM Geheugen")
                print(res.fetchall())
        # dit aanpassen in de database
        # exacte_uren[i][q] = exacte_uren[i][q] - 1

    # deze functie zal een apparaat volledig verwijderen uit alle lijsten, wnr het aantal uur dat het moet werken op nul is gekomen
    def verwijderen_uit_lijst_wnr_aantal_uur_0(aantal_uren_per_apparaat, lijst_met_wattages,
                                               exacte_uren, prijzen_stroom, einduren, aantal_uren):
        # uren_na_elkaarVAR wordt gebaseerd op werkuren per apparaat dus die moet je niet zelf meer aanpassen
        print("Gegevens verwijderen na functie verwijderen_uit_lijst_wnr_aantal_uur_0")
        for i in aantal_uren_per_apparaat:
            if i == 0:  # dan gaan we dit apparaat overal verwijderen uit alle lijsten die we hebben
                # eerst lijst met wattages apparaat verwijderen
                con = sqlite3.connect("D_VolledigeDatabase.db")
                cur = con.cursor()
                cur.execute("UPDATE Geheugen SET Wattages =" + str(0) +
                            " WHERE Nummering =" + str(i))
                cur.execute("UPDATE Geheugen SET ExacteUren =" + str(0) +
                            " WHERE Nummering =" + str(i))
                cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(0) +
                            " WHERE Nummering =" + str(i))
                cur.execute("UPDATE Geheugen SET Apparaten =" + str(0) +
                            " WHERE Nummering =" + str(i))
                con.commit()
                res = cur.execute("SELECT Wattages FROM Geheugen")
                print(res.fetchall())
                res = cur.execute("SELECT ExacteUren FROM Geheugen")
                print(res.fetchall())
                res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
                print(res.fetchall())

    # deze functie zal het finale uur eentje verlagen
    def verlagen_finale_uur(klaar_tegen_bepaald_uur):
        print("FinaleTijdstip na functie verlagen_finale_uur")
        for i in range(len(klaar_tegen_bepaald_uur)):
            if type(klaar_tegen_bepaald_uur[i]) == int:
                con = sqlite3.connect("D_VolledigeDatabase.db")
                cur = con.cursor()
                cur.execute("UPDATE Geheugen SET FinaleTijdstip =" + str(klaar_tegen_bepaald_uur[i] - 1) +
                            " WHERE Nummering =" + str(i))
                con.commit()
            # Ter illustratie
            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()
            res = cur.execute("SELECT FinaleTijdstip FROM Geheugen")
            print(res.fetchall())
            # zo aanpassen in database nu
            # einduren[i] = einduren[i] - 1

    #######################################################################################################

    # variabelen
    from O_parameters_geheel import aantalapparaten as aantal_apparaten
    from O_parameters_geheel import wattages_apparaten as wattagelijst
    from O_parameters_geheel import voorwaarden_apparaten_exacte_uren as voorwaarden_apparaten_exact
    from O_parameters_geheel import tijdsstap as Delta_t
    from O_parameters_geheel import aantaluren as aantal_uren
    from O_parameters_geheel import prijslijst_stroomverbruik_per_uur as prijzen
    from O_parameters_geheel import finale_tijdstip as einduren
    from O_parameters_geheel import uur_werk_per_apparaat as werkuren_per_apparaat
    from O_parameters_geheel import stroom_per_uur_zonnepanelen as stroom_zonnepanelen
    from O_parameters_geheel import uren_na_elkaar as uren_na_elkaarVAR
    from O_parameters_geheel import namen_apparaten as namen_apparaten
    from O_parameters_geheel import begintemperatuur as begintemperatuur_huis
    from O_parameters_geheel import temperatuurwinst_per_uur as temperatuurwinst_per_uur
    from O_parameters_geheel import verliesfactor_huis_per_uur as verliesfactor_huis_per_uur
    from O_parameters_geheel import ondergrens as ondergrens
    from O_parameters_geheel import bovengrens as bovengrens
    from O_parameters_geheel import starturen as starturen
    from O_parameters_geheel import maximaal_verbruik_per_uur as maximaal_verbruik_per_uur
    from O_parameters_geheel import huidig_batterijniveau as huidig_batterijniveau

    # interface moet die sentinel in de database 0 maken als er op toevoegen wordt geduwd.
    # wnr er iets toegevoegd is, dan mag de sentinel weer op 1 worden gezet en dan zal er terug geoptimaliseerd worden
    #######################################################################################################

    # aanmaken lijst met binaire variabelen
    m.apparaten = pe.VarList(domain=pe.Binary)
    m.apparaten.construct()
    variabelen_constructor(m.apparaten, aantal_apparaten, aantal_uren)  # maakt variabelen aan die apparaten voorstellen

    # objectief functie aanmaken
    obj_expr = objectieffunctie(prijzen, m.apparaten, Delta_t, wattagelijst, aantal_uren,
                                stroom_zonnepanelen)  # somfunctie die objectief creeërt
    m.obj = pe.Objective(sense=pe.minimize, expr=obj_expr)

    # aanmaken constraint om op exact uur aan of uit te staan
    m.voorwaarden_exact = pe.ConstraintList()  # voorwaarde om op een exact uur aan of uit te staan
    m.voorwaarden_exact.construct()
    exacte_beperkingen(m.apparaten, m.voorwaarden_exact, aantal_apparaten, voorwaarden_apparaten_exact,
                       aantal_uren)  # beperkingen met vast uur

    # aanmaken constraint om aantal werkuren vast te leggen
    m.voorwaarden_aantal_werkuren = pe.ConstraintList()
    m.voorwaarden_aantal_werkuren.construct()
    beperkingen_aantal_uur(werkuren_per_apparaat, m.apparaten, m.voorwaarden_aantal_werkuren,
                           aantal_uren)  # moet x uur werken, maakt niet uit wanneer

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
                          m.apparatenstart)
    # voorwaarden maximale verbruik per uur
    m.voorwaarden_maxverbruik = pe.ConstraintList()
    m.voorwaarden_maxverbruik.construct()
    voorwaarden_max_verbruik(m.apparaten, maximaal_verbruik_per_uur, m.voorwaarden_maxverbruik, wattagelijst,
                             Delta_t)
    """
    # voorwaarden warmtepomp
    m.voorwaarden_warmtepomp = pe.ConstraintList()
    voorwaarden_warmteboiler(namen_apparaten, m.apparaten, m.voorwaarden_warmtepomp, verliesfactor_huis_per_uur, temperatuurwinst_per_uur, begintemperatuur_huis, ondergrens, bovengrens, aantal_uren)
    """
    # voorwaarden batterij
    m.voorwaarden_batterij = pe.ConstraintList()
    voorwaarden_batterij(m.apparaten, m.voorwaarden_batterij, aantal_uren, wattagelijst, namen_apparaten,
                         huidig_batterijniveau)

    result = solver.solve(m)

    print(result)

    kost, apparaten_aanofuit = uiteindelijke_waarden(m.apparaten, aantal_uren, namen_apparaten)

    # deze functies passen de lijsten aan, rekening houdend met de apparaten die gewerkt hebben op het vorige uur
    verlagen_aantal_uur(m.apparaten, aantal_uren, werkuren_per_apparaat)

    # deze lijn moet sws onder 'verlagen exacte uren' staan want anders voeg je iets toe aan de database en ga je vervolgens dit opnieuw verlagen
    opeenvolging_opschuiven(m.apparaten, aantal_uren, uren_na_elkaarVAR, voorwaarden_apparaten_exact)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()
    res = cur.execute("SELECT ExacteUren FROM Geheugen")
    ListTuplesExacteUren = res.fetchall()
    ExacteUren = exacte_uren_naar_lijst(ListTuplesExacteUren, "ExacteUren")

    verlagen_exacte_uren(ExacteUren)

    verwijderen_uit_lijst_wnr_aantal_uur_0(werkuren_per_apparaat, wattagelijst, voorwaarden_apparaten_exact, prijzen,
                                           einduren, aantal_uren)

    verlagen_finale_uur(einduren)
    '''
    #Nu zullen er op basis van de berekeningen aanpassingen moeten gedaan worden aan de database
    #wnr iets het eerste uur wordt berekend als 'aan' dan moeten er bij de volgende berekeningen er mee rekening gehouden worden
    #dat dat bepaald apparaat heeft gedraaid op dat uur, dus aantal draai uur is een uur minder, en wnr het drie uur na elkaar moest draaien en het eerste uur werd aangeduid als 'aan', dan moet bij de volgende berekening 1 en 2 nog als 'aan' aangeduid worden
    #een batterij is eigenlijk ook gwn aantal uur dat die nog moet werken een uur verlagen

    #nog overal in elke functie bijzetten wat er moet gebeuren als er geen integer in staat maar die string
    '''

def geheugen_veranderen():
    print(lijst_apparaten)
    print(lijst_verbruiken)
    print(voorwaarden_apparaten_exacte_uren)
    print(lijst_beginuur)
    print(lijst_deadlines)
    print(lijst_aantal_uren)
    print(lijst_uren_na_elkaar)
    def uur_omzetten(exacte_uren1apparaat):

        string = "'"
        for i2 in range(len(exacte_uren1apparaat)):
            if exacte_uren1apparaat[i2] == "/":
                return str(0)
            else:
                string = string + str(exacte_uren1apparaat[i2]) + ":"
        string = string[0:-1] + "'"
        return string

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    lengte = len(lijst_apparaten)
    for i in range(lengte):
        NummerApparaat = str(i)
        naam = "'" + lijst_apparaten[i] + "'"
        cur.execute("UPDATE Geheugen SET Apparaten =" + naam +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Wattages =" + str(lijst_verbruiken[i]) +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET ExacteUren =" + uur_omzetten(voorwaarden_apparaten_exacte_uren[i]) +
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
    con.commit()

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

def parameters_vernieuwen():
    EFFICIENTIE = 0.2
    OPP_ZONNEPANELEN = 12
    prijslijst_stroomverbruik_per_uur = Prijzen24uur

    stroom_per_uur_zonnepanelen = [irradiantie * EFFICIENTIE * OPP_ZONNEPANELEN for irradiantie in Gegevens24uur[1]]

    # namen_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
    namen_apparaten = Apparaten

    # wattages_apparaten = [15, -14.344, 12.2, 14, 10, 12]
    wattages_apparaten = Wattages

    # voorwaarden_apparaten_exacte_uren = [[], [], [], [], [], []]
    voorwaarden_apparaten_exacte_uren = ExacteUren

    aantalapparaten = len(wattages_apparaten)
    tijdsstap = 1  # bekijken per uur
    aantaluren = len(prijslijst_stroomverbruik_per_uur)

    # finale_tijdstip = ['/','/','/', 10, 11, 12]  # wanneer toestel zeker klaar moet zijn
    finale_tijdstip = FinaleTijdstip  # wanneer toestel zeker klaar moet zijn

    # uur_werk_per_apparaat = ['/','/', '/', '/', 4, '/']  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer
    uur_werk_per_apparaat = UrenWerk  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer

    # uren_na_elkaar = ['/','/', '/',5,'/', 3]
    uren_na_elkaar = UrenNaElkaar

    # starturen = ['/','/', '/', 3, 6, 4]
    starturen = BeginUur

    huidig_batterijniveau = 6
    maximaal_verbruik_per_uur = [3500 for i in range(len(prijslijst_stroomverbruik_per_uur))]

    verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p] / 2 for p in
                                     range(len(prijslijst_stroomverbruik_per_uur))]
    verliesfactor_huis_per_uur = 1  # in graden C
    temperatuurwinst_per_uur = 2  # in graden C
    begintemperatuur = 18  # in graden C
    ondergrens = 17  # mag niet kouder worden dan dit
    bovengrens = 22  # mag niet warmer worden dan dit

    # controle op tegenstrijdigheden in code
    assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(
        uur_werk_per_apparaat)
    for i in range(len(voorwaarden_apparaten_exacte_uren)):
        if type(uur_werk_per_apparaat[i]) == int:
            assert len(voorwaarden_apparaten_exacte_uren[i]) <= uur_werk_per_apparaat[i]
        for p in range(len(voorwaarden_apparaten_exacte_uren[i])):
            if len(voorwaarden_apparaten_exacte_uren[i]) > 0:
                if type(voorwaarden_apparaten_exacte_uren[i][p]) == int and type(finale_tijdstip[i]) == int:
                    assert voorwaarden_apparaten_exacte_uren[i][p] < finale_tijdstip[i]

    # Ter illustratie
    print(prijslijst_stroomverbruik_per_uur)
    print(stroom_per_uur_zonnepanelen)
    print(namen_apparaten)
    print(wattages_apparaten)
    print(voorwaarden_apparaten_exacte_uren)
    print(finale_tijdstip)
    print(uur_werk_per_apparaat)
    print(uren_na_elkaar)


##### Algemene functies
def TupleToList(list_tuples, categorie, index_slice):
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
            return [list_strings, len(list_strings)]

        if categorie == "Wattages" or categorie == "FinaleTijdstip" \
                or categorie == "UrenWerk" or categorie == "UrenNaElkaar" or categorie == "BeginUur" or categorie == "SentinelWaarde":
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

    res = cur.execute("SELECT SentinelWaarde FROM Geheugen")
    ListTuplesSentinelWaarde = res.fetchall()
    SentinelWaarde = tuples_to_list(ListTuplesSentinelWaarde, "SentinelWaarde", index)
    SENTINELWAARDE = SentinelWaarde[0]


###### FUNCTIES VOOR COMMUNICATIE MET DATABASE

def gegevens_opvragen(current_date):
    uur = "0"
    dag = str(int(current_date[0:2]))
    maand = current_date[3:5]

    # Gegevens Belpex opvragen
    if int(maand) >= 9:
        tupleBelpex = (dag + "/" + maand + "/" + "2021 " + uur + ":00:00",)
    else:
        tupleBelpex = (dag + "/" + maand + "/" + "2022 " + uur + ":00:00",)
    print(tupleBelpex)
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleBelpex)

    res = cur.execute("SELECT Prijs FROM Stroomprijzen")
    Prijzen = res.fetchall()

    Prijzen24uur = []
    for i in range(0, 24):
        prijs = Prijzen[index - i]
        prijsString = str(prijs)
        prijsCijfers = prijsString[6:-3]
        prijsCijfersPunt = prijsCijfers.replace(",", ".")
        prijsFloat = float(prijsCijfersPunt)
        Prijzen24uur.append(prijsFloat)
    # Print lijst met de prijzen van de komende 24 uur
    print(Prijzen24uur)

    # Gegevens Weer opvragen
    uur = "00"
    dag = current_date[0:2]
    maand = current_date[3:5]

    tupleWeer = ("2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT DatumWeer FROM Weer")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleWeer)

    res = cur.execute("SELECT Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse FROM Weer")
    alleGegevens = res.fetchall()

    TemperatuurList = []
    RadiatieList = []
    for i in range(0, 24):
        dagGegevens = alleGegevens[index + i]
        TemperatuurList.append(float(dagGegevens[1]))
        RadiatieList.append(float(dagGegevens[2]) + float(dagGegevens[3]))
    Gegevens24uur = [TemperatuurList, RadiatieList]
    # Print lijst onderverdeeld in een lijst met de temperaturen van de komende 24 uur
    #                              en een lijst voor de radiatie van de komende 24 uur
    print(Gegevens24uur)
    return Prijzen24uur, Gegevens24uur



def apparaat_toevoegen_database(namen_apparaten, wattages_apparaten, begin_uur, finale_tijdstip, uur_werk_per_apparaat, uren_na_elkaar):
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    # In de database staat alles in de vorm van een string
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    apparaten = res.fetchall()
    for i in range(len(namen_apparaten)):
        # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
        NummerApparaat = str(i)
        naam = "'" + namen_apparaten[i] + "'"
        print("naam: " + naam)
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
    for j in range(len(apparaten) - len(namen_apparaten)):
        cur.execute("UPDATE Geheugen SET Apparaten = " + naam +
                    " WHERE Nummering =" + NummerApparaat)
        cur.execute("UPDATE Geheugen SET Wattages =" + str(wattages_apparaten[i]) +
                    " WHERE Nummering =" + NummerApparaat)


    # Is nodig om de uitgevoerde veranderingen op te slaan
    con.commit()


def apparaat_editen_database(namen_apparaten, wattages_apparaten, begin_uur, finale_tijdstip, uur_werk_per_apparaat, uren_na_elkaar):
    con = sqlite3.connect("D_VolledigeDatabase.db")
    cur = con.cursor()

    # In de database staat alles in de vorm van een string
    res = cur.execute("SELECT Apparaten FROM Geheugen")
    apparaten = TupleToList(res.fetchall(), "Apparaten", -1)
    for i in range(len(namen_apparaten)):
        # Accenten vooraan en achteraan een string zijn nodig zodat sqlite dit juist kan lezen
        NummerApparaat = str(i)
        naam = "'" + namen_apparaten[i] + "'"
        print("naam: " + naam)
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
    # Is nodig om de uitgevoerde veranderingen op te slaan
    con.commit()



#MainApplication: main window instellen + de drie tabs aanmaken met verwijzigen naar HomeFrame, ControlFrame en StatisticFrame
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

#Home Frame aanmaken met titel, namen projectdeelnemers en kalender om datum te kiezen

class HomeFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent)

        frame_width = self.winfo_screenwidth()
        frame_height = self.winfo_screenheight()

        my_canvas = Canvas(self, width=frame_width, height=frame_height, bg=('gray16'))
        my_canvas.pack(fill="both", expand=True)

        frame1 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.16*frame_height)
        frame1.pack_propagate('false')
        my_canvas.create_window((350,50), window=frame1, anchor="nw")
        frame2 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.35*frame_height)
        frame2.grid_propagate('false')
        my_canvas.create_window((350, 300), window=frame2, anchor="nw")
        frame3 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.1*frame_height)
        frame3.grid_propagate('false')
        my_canvas.create_window((350, 800), window=frame3, anchor="nw")

        home_title = CTkLabel(frame1, text='SMART SOLAR HOUSE', text_font=('Biome',60, 'bold'))
        home_subtitle = CTkLabel(frame1, text='Made by August Vannes, Jonas Thewis, Lander Verhoeven, Ruben Vanherpe,',text_font=('Biome', 15))
        home_subtitle2 = CTkLabel(frame1, text= 'Tibo Mattheus and Tijs Motmans', text_font=('Biome', 15))

        home_title.pack()
        home_subtitle.pack()
        home_subtitle2.pack()

        frame2.rowconfigure(0, uniform= 'uniform', weight=2)
        frame2.rowconfigure(1, uniform='uniform', weight=12)
        frame2.rowconfigure(2, uniform='uniform', weight=2)
        frame2.columnconfigure(0, uniform='uniform', weight=1)

        selected_date = CTkLabel(frame2, text='Here you can change the current date:', text_font=('Biome',15))
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

        def hour_change():
            global current_hour, Prijzen24uur, Gegevens24uur
            current_hour += 1
            if current_hour == 25:
                current_hour = 1
                date_plus_one()
            if current_hour < 10:
                label_hours.configure(text='0' + str(current_hour))
            else:
                label_hours.configure(text= str(current_hour))
            update_algoritme()
            print(current_date)
            Prijzen24uur, Gegevens24uur = gegevens_opvragen(current_date)
            label_hours.after(15000, hour_change)

        def grad_date():
            global current_date, current_hour, Prijzen24uur, Gegevens24uur
            current_date = cal.get_date()
            label_day.configure(text=str(current_date[0:2]))
            label_month.configure(text=str(current_date[3:5]))
            label_year.configure(text=str(current_date[6:10]))


        btn = CTkButton(frame2, text="Confirm the chosen date",command=grad_date)
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
        hours= CTkFrame(frame3, bd=5, corner_radius=10)
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
            label_hours = CTkLabel(hours, text= str(current_hour), text_font=('Biome', 50))
        label_hours.pack(fill='both', expand=1)
        label_minutes = CTkLabel(minutes, text='00', text_font=('Biome', 50))
        label_minutes.pack(fill='both', expand=1)

        label_hours.after(15000, hour_change)

#ControlFrame aanmaken met verwijzingen naar FrameTemperatuur, FrameBatterijen en FrameApparaten

class ControlFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=1)
        self.grid_rowconfigure((0,1,2), uniform="uniform", weight=1)

        frame_temperatuur = FrameTemperatuur(self)
        frame_batterijen = FrameBatterijen(self)
        frame_apparaten = FrameApparaten(self)
        frame_zonnepanelen = FrameZonnepanelen(self)

        frame_temperatuur.grid(row=0, column=0, padx=5, sticky='nsew')
        frame_batterijen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_apparaten.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')
        frame_zonnepanelen.grid(row=2, column=0,padx=5, pady=5, sticky='nsew')

#Frame om de temperatuur van het huis (warmtepomp) te regelen

class FrameTemperatuur(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure(0, uniform = 'uniform', weight=1)
        self.rowconfigure(1, uniform = 'uniform', weight=5)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Heat pump', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, padx=5, sticky='nsew')

        frame1 = CTkFrame(self)
        frame1.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        frame1.rowconfigure((0,1,2), uniform='uniform', weight=3)
        frame1.rowconfigure(3, uniform='uniform', weight=4)
        frame1.columnconfigure((0,2), uniform='uniform', weight=20)
        frame1.columnconfigure(1, uniform='uniform', weight=1)

        def configure_heat_pump():
            edit_pump = CTkToplevel(self)
            edit_pump.iconbitmap('I_solarhouseicon.ico')
            edit_pump.title('Configure heat pump')
            edit_pump.geometry('300x230')
            edit_pump.grab_set()

            def bewerk():
                ...

            edit_verbruik = CTkLabel(edit_pump, text='Edit the energy usage of the heat pump:')
            entry_verbruik = CTkEntry(edit_pump)
            entry_verbruik.insert(0, verbruik_warmtepomp)


        label_verbruik = CTkLabel(frame1, text= 'Energy usage: ' + str(verbruik_warmtepomp) + ' kWh')
        label_opwarming = CTkLabel(frame1, text= 'Heating rate: ' + str(opwarmingssnelheid) + ' °C/s')
        label_warmteverlies = CTkLabel(frame1, text= 'Heat loss: ' + str(warmteverlies) + ' °C/s')
        label_huidige_temp = CTkLabel(frame1, text= 'Current temperature: ' + str(huidige_temperatuur) + ' °C')
        label_min_temp = CTkLabel(frame1, text= 'Mininum temperature: ' + str(min_temperatuur) + ' °C')
        label_max_temp = CTkLabel(frame1, text= 'Maximum temperature: ' + str(max_temperatuur) + ' °C')
        seperator = ttk.Separator(frame1, orient = 'vertical')
        btn_configure_heat_pump = CTkButton(frame1, text='Configure heat pump', command=configure_heat_pump)

        label_verbruik.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_opwarming.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        label_warmteverlies.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        label_huidige_temp.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        label_min_temp.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
        label_max_temp.grid(row=2, column=2, padx=5, pady=5, sticky='nsew')
        seperator.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky='nsew')
        btn_configure_heat_pump.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky='nsew')






#Frame om de status van de batterijen te controleren

class FrameBatterijen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Battery', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#Frame om de zonnepanelen te controleren

class FrameZonnepanelen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure(0, uniform = 'uniform', weight=1)
        self.rowconfigure(1, uniform= 'unifrom', weight=4)
        self.columnconfigure(0, uniform='uniform', weight=1)

        title = CTkLabel(self, text='Solar Panels', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        frame1 = CTkFrame(self)
        frame1.grid(row=1, column=0,padx=5, pady=5, sticky='nsew')

        frame1.rowconfigure(0, uniform='uniform', weight=1)
        frame1.columnconfigure((0,1), uniform='unifrom', weight=1)

        frame_oppervlakte = CTkFrame(frame1)
        frame_productie = CTkFrame(frame1)
        frame_oppervlakte.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        frame_productie.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        frame_oppervlakte.rowconfigure((0,1,2,3), uniform='uniform', weight=1)
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
                    label_oppervlakte_zonnepanelen.configure(text = 'Total area of solar panels: ' + str(aantal_zonnepanelen * float(oppervlakte_zonnepanelen)) + ' m²')
                    edit_panels.destroy()

            edit_panels.rowconfigure((0,1,2,3), uniform='uniform', weight=2)
            edit_panels.rowconfigure((4), uniform='uniform', weight=3)
            edit_panels.columnconfigure((0,1), uniform='uniform', weight=1)

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

        label_aantal_zonnepanelen = CTkLabel(frame_oppervlakte, text='Number of solar panels: '+ str(aantal_zonnepanelen))
        label_oppervlakte_zonnepanelen = CTkLabel(frame_oppervlakte, text= 'Total area of solar panels: '+ str(oppervlakte_zonnepanelen) + ' m²')
        label_rendement = CTkLabel(frame_oppervlakte, text= 'Efficiency: ' + str(int(rendement_zonnepanelen*100)) + ' %')
        btn_zonnepaneel_toevoegen = CTkButton(frame_oppervlakte, text='Configure your solar panels', command=zonnepanelen_bewerken)

        label_aantal_zonnepanelen.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_oppervlakte_zonnepanelen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        label_rendement.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        btn_zonnepaneel_toevoegen.grid(row=3, column=0, padx=10, pady=5, sticky='nsew')

        frame_productie.rowconfigure(0, uniform='uniform', weight=1)
        frame_productie.rowconfigure(1, uniform='unform', weight=3)
        frame_productie.columnconfigure(0, uniform='uniform', weight=1)

        label_production_title = CTkLabel(frame_productie, text='Current Production:', text_font=('Biome', 10))
        label_production = CTkLabel(frame_productie, text = str(current_production), text_font=('Biome',60))

        label_production_title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        label_production.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

#Frame om de apparaten in het huishouden te controleren
class FrameApparaten(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.grid_rowconfigure((0,2), uniform="uniform", weight=1)
        self.grid_rowconfigure(1, uniform="uniform", weight=16)
        self.grid_columnconfigure((0,1), uniform="uniform", weight=1)
        global frame_height
        global frame_width
        frame_height = self.winfo_screenheight()
        frame_width = self.winfo_screenwidth()

        btn_newdevice = CTkButton(self, text='Add new device', command=lambda: self.new_device(frame2))
        btn_newdevice.grid(row=2,column=1, padx=5, sticky='nsew')
        btn_editdevice = CTkButton(self, text='Edit existing device', command=lambda: self.edit_device(frame2))
        btn_editdevice.grid(row=2, column=0, padx=5, sticky='nsew')
        title = CTkLabel(self, text="Current Devices", text_font=('Microsoft Himalaya', 30, 'bold'), pady=0)
        title.grid(row=0,column=0,columnspan=2,sticky = 'nsew')
        frame1 = CTkFrame(self, fg_color='gray', pady=0)
        frame1.grid(row=1,column=0, columnspan=2, sticky='nsew')

        my_canvas = Canvas(frame1)
        my_canvas.pack(side='left',fill='both', expand=1, pady=0)

        my_scrollbar = CTkScrollbar(frame1,orientation='vertical', command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT,fill='y')

        frame2 = CTkFrame(my_canvas, corner_radius=0)
        my_canvas.create_window((0, 0), window=frame2, anchor='nw', height=2000)

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        self.apparaten_in_frame(frame2)

    def apparaten_in_frame(self,frame2):
        for widget in frame2.winfo_children():
            widget.destroy()
        for nummer in range(len(lijst_apparaten)):
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
            APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember,status)


    def new_device(self, frame2):
        new_window = CTkToplevel(self)
        new_window.iconbitmap('I_solarhouseicon.ico')
        new_window.title('Add a new device')
        new_window.geometry('300x610')
        new_window.grab_set()

        new_window.rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12), uniform='uniform', weight=2)
        new_window.rowconfigure(13, uniform='uniform', weight=3)
        new_window.columnconfigure('all', uniform='uniform', weight=1)

        def show_rest(event):
            global entry_verbruik, spinbox_deadline, checkbox_deadline, spinbox_hours, checkbox_consecutive, \
                entry_capacity, checkbox_beginuur, spinbox_beginuur, checkbox_remember

            for widget in new_window.winfo_children()[4:]:
                widget.destroy()

            label_verbruik = CTkLabel(new_window, text='Fill in the energy usage of the device:')
            entry_verbruik = CTkEntry(new_window)
            label_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if entry_soort.get() == 'Device with battery':
                label_capacity = CTkLabel(new_window, text='Fill in the battery capacity:')
                entry_capacity = CTkEntry(new_window)
                label_beginuur = CTkLabel(new_window, text='Set a start time for the device:')
                spinbox_beginuur = Spinbox1(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text ='No Starttime', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

                label_capacity.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_capacity.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                label_beginuur.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember.grid(row=12, column=0, columnspan=2, padx=35, pady=5, sticky='nsew')

            if entry_soort.get() == 'Consumer':
                label_hours = CTkLabel(new_window, text='Fill in the runtime of the device:')
                spinbox_hours = Spinbox2(new_window, step_size=1)
                checkbox_consecutive = CTkCheckBox(new_window, text= 'Consecutive hours')
                label_beginuur = CTkLabel(new_window, text='Set a start time for the device: ')
                spinbox_beginuur = Spinbox1(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text= 'No Starttime', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

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

            btn_confirm = CTkButton(new_window, text='confirm', command=apparaat_toevoegen)
            btn_confirm.grid(row=13, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
            btn_cancel.grid(row=13, column=0, padx=5, pady=5, sticky='nsew')

        def apparaat_toevoegen():
            naam= entry_naam.get()
            soort = entry_soort.get()

            if soort == 'Always on':
                uren = 24
                uren_na_elkaar = 24
                capaciteit = '/'
                verbruik = entry_verbruik.get()
                deadline = '/'
                beginuur = '/'
                remember = 1
                status = 1

            if soort == 'Device with battery':
                uren = '/'
                uren_na_elkaar = '/'
                capaciteit = entry_capacity.get()
                verbruik = entry_verbruik.get()
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
                verbruik = entry_verbruik.get()
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

            if naam=='' or soort=='' or uren=='' or uren_na_elkaar=='' or capaciteit=='' or deadline=='':
                messagebox.showwarning('Warning','Please make sure to fill in all the boxes')
            else:
                print("nog iets meer voor toevoegen: ")
                print(lijst_apparaten)
                APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember, status)
                print("vlak voor toevoegen: " )
                print(lijst_apparaten)
                apparaat_toevoegen_database(lijst_apparaten, lijst_verbruiken, lijst_beginuur, lijst_deadlines,
                                            lijst_aantal_uren, lijst_uren_na_elkaar)
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

    def edit_device(self, frame2):
        edit_window = CTkToplevel(self)
        edit_window.iconbitmap('I_solarhouseicon.ico')
        edit_window.title('Edit device')
        edit_window.geometry('300x650')
        edit_window.grab_set()

        edit_window.rowconfigure((0, 1, 2, 3, 4, 5,6,7,8,9,10,11,12), uniform='uniform', weight=2)
        edit_window.rowconfigure((13,14), uniform='uniform', weight=3)
        edit_window.columnconfigure('all', uniform='uniform', weight=1)

        def apparaat_wijzigen():
            soort = lijst_soort_apparaat[apparaat_nummer]

            if soort == 'Always on':
                naam = entry_naam_2.get()
                uren = 24
                uren_na_elkaar = 24
                capaciteit = '/'
                verbruik = entry_verbruik_2.get()
                deadline = '/'
                beginuur = '/'
                remember = 0
                status = 1

            if soort == 'Device with battery':
                naam = entry_naam_2.get()
                uren = '/'
                uren_na_elkaar = '/'
                capaciteit = entry_capacity_2.get()
                verbruik = entry_verbruik_2.get()
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
                uren = spinbox_hours_2.get()
                if checkbox_consecutive_2.get() == 1:
                    uren_na_elkaar = uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = entry_verbruik_2.get()
                if checkbox_beginuur_2.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur_2.get()
                if checkbox_deadline_2.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline_2.get()
                checkbox_remember_2.get()
                status = 0

            kolom = apparaat_nummer % 3
            rij = apparaat_nummer // 3

            if naam == '' or capaciteit == '' or uren == '' or uren_na_elkaar == '' or verbruik == '' or deadline == '' or beginuur == '':
                messagebox.showwarning('Warning','Please make sure to fill in all the boxes')
            else:
                lijst_apparaten[apparaat_nummer] = naam
                lijst_soort_apparaat[apparaat_nummer] = soort
                lijst_capaciteit[apparaat_nummer] = capaciteit
                lijst_aantal_uren[apparaat_nummer] = uren
                lijst_aantal_uren[apparaat_nummer] = uren_na_elkaar
                lijst_verbruiken[apparaat_nummer] = verbruik
                lijst_deadlines[apparaat_nummer] = deadline
                lijst_beginuur[apparaat_nummer] = beginuur
                lijst_remember_settings[apparaat_nummer] = remember
                lijst_status[apparaat_nummer] = status
                APPARAAT(frame2,naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur,remember,status, column=kolom, row=rij)
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
            entry_naam_2.delete(0,'end')
            entry_naam_2.insert(0,lijst_apparaten[apparaat_nummer])
            label_verbruik_2 = CTkLabel(edit_window, text='Edit the energy usage (in kWh):')
            entry_verbruik_2 = CTkEntry(edit_window)
            entry_verbruik_2.delete(0,'end')
            entry_verbruik_2.insert(0,lijst_verbruiken[apparaat_nummer])

            label_naam_2.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_naam_2.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            label_verbruik_2.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if lijst_soort_apparaat[apparaat_nummer] == 'Always on':
                pass

            else:
                if lijst_soort_apparaat[apparaat_nummer] == 'Device with battery':
                    label_capacity_2 = CTkLabel(edit_window, text='Change the battery capacity from the device:')
                    entry_capacity_2 = CTkEntry(edit_window)
                    entry_capacity_2.delete(0,'end')
                    entry_capacity_2.insert(0, lijst_capaciteit[apparaat_nummer])
                    label_capacity_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    entry_capacity_2.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

                if lijst_soort_apparaat[apparaat_nummer] == 'Consumer':
                    label_hours_2 = CTkLabel(edit_window, text='Edit the runtime of the device:')
                    spinbox_hours_2 = Spinbox2(edit_window, step_size=1)
                    checkbox_consecutive_2 = CTkCheckBox(edit_window, text='Consecutive hours')
                    spinbox_hours_2.set(lijst_aantal_uren[apparaat_nummer])
                    if lijst_aantal_uren[apparaat_nummer] == lijst_uren_na_elkaar[apparaat_nummer]:
                        checkbox_consecutive_2.select()

                    label_hours_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    spinbox_hours_2.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')
                    checkbox_consecutive_2.grid(row=7, column=1, padx=5, pady=5, sticky='nsew')

                label_beginuur_2 = CTkLabel(edit_window, text='Change the start time for the device:')
                spinbox_beginuur_2 = Spinbox1(edit_window, step_size=1)
                checkbox_beginuur_2 = CTkCheckBox(edit_window, text='No Start Time', command=checkbox_command2)
                if lijst_beginuur[apparaat_nummer] == '/':
                    checkbox_beginuur_2.select()
                    spinbox_beginuur_2.inactiveer()
                else:
                    spinbox_beginuur_2.set(lijst_beginuur[apparaat_nummer])

                label_deadline_2 = CTkLabel(edit_window, text='Change the deadline for the device:')
                spinbox_deadline_2 = Spinbox1(edit_window, step_size=1)
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
                checkbox_remember_2.grid(row=12, column=0,columnspan=2, padx=35, pady=5, sticky='nsew')

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
                self.apparaten_in_frame(frame2)
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

        text_choose = CTkLabel(edit_window,text='Choose the device you want to edit:')
        choose_device = CTkComboBox(edit_window, values=lijst_apparaten, command= show_options)
        choose_device.set('')

        text_choose.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        choose_device.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_confirm_2 = CTkButton(edit_window, text='confirm', command = apparaat_wijzigen, state=DISABLED)
        btn_confirm_2.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel_2 = CTkButton(edit_window, text='cancel', command = edit_window.destroy)
        btn_cancel_2.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')
        btn_delete_device = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen, fg_color='red', state=DISABLED)
        btn_delete_device.grid(row=13, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

class APPARAAT(CTkFrame):
    def __init__(self, parent, naam, soort, uren, uren_na_elkaar, capaciteit,verbruik,deadline, beginuur, remember, status, column=None, row=None):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure('all',uniform="uniform", weight=1)
        self.columnconfigure('all', uniform = 'uniform', weight=1)

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
        self.grid(row=rij,column=kolom, sticky='nsew')

        label_naam = CTkLabel(self, text=naam, text_font=('Biome', 12, 'bold'))
        label_naam.grid(row=0, column=0, sticky='nsew')
        label_soort = CTkLabel(self, text= soort, text_font=('Biome',10))
        label_soort.grid(row=1, column=0, sticky='nsew')
        label_verbruik = CTkLabel(self, text='Energy Usage: ' + str(verbruik) + ' kWh', text_font=('Biome', 10))
        label_verbruik.grid(row=2, column=0, sticky='nsew')
        if soort == 'Consumer':
            if uren == uren_na_elkaar:
                na_elkaar = 'succesively'
            else:
                na_elkaar = 'random'
            label_uren = CTkLabel(self, text= 'Daily use: ' + str(uren) + ' hours (' + na_elkaar + ')', text_font=('Biome', 10))
            label_uren.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text= 'Current start time: ' + str(beginuur) + 'u', text_font = ('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text= 'Current Deadline: ' + str(deadline) + 'u', text_font = ('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Device with battery':
            label_capaciteit = CTkLabel(self, text= 'Battery Capacity: ' + str(capaciteit) + ' kWh', text_font=('Biome', 10))
            label_capaciteit.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text='Current start time: ' + str(beginuur) + 'u',
                                          text_font=('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text='Current Deadline: ' + str(deadline) + 'u',
                                          text_font=('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Always on':
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
        status = CTkLabel(self, text=status_text, bg_color=bg_color, width=0.1185*frame_width, height= 0.025*frame_height)
        status.grid(row=6, column=0, padx=5, pady=5)

#StatisticFrame met verwijzingen naar ...
class StatisticFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, width=3840, height=2160)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=2)
        self.grid_columnconfigure(2, uniform="uniform", weight=3)
        self.grid_rowconfigure(0, uniform="uniform", weight=2)
        self.grid_rowconfigure(1, uniform="uniform", weight=1)

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

#Frame PvsC: grafiek van de productie en consumptie van energie

class FramePvsC(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Production vs Consumption', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameVerbruikers: cirkeldiagram met grootste verbruikers in het huis (eventueel)

class FrameVerbruikers(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Consumers', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameEnergieprijs: geeft huidige energieprijs weer

class FrameEnergieprijs(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Energy Price', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameWeer: geeft huidgie weerssituatie weer:

class FrameWeer(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Weather', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameTotalen: geeft nog enkele totalen statistieken weer:

class FrameTotalen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Totals', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
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
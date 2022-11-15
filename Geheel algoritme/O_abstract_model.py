import pyomo.environ as pe
import pyomo.opt as po

import O_parameters_geheel

import sqlite3

solver = po.SolverFactory('glpk')
m  = pe.ConcreteModel()
#######################################################################################################
# definiëren functies
def variabelen_constructor(lijst, aantal_apparaten, aantal_uren):
    for p in range(aantal_uren*aantal_apparaten): # totaal aantal nodige variabelen = uren maal apparaten
        lijst.add() # hier telkens nieuwe variabele aanmaken

def objectieffunctie(prijzen, variabelen, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen):
    obj_expr = 0
    for p in range(aantal_uren):
        subexpr = 0
        for q in range(len(wattagelijst)):
            subexpr = subexpr + wattagelijst[q]*variabelen[q*aantal_uren + (p+1)] # eerst de variabelen van hetzelfde uur samentellen om dan de opbrengst van zonnepanelen eraf te trekken
        obj_expr = obj_expr + Delta_t*prijzen[p] * (subexpr - stroom_zonnepanelen[p])
    return obj_expr

def exacte_beperkingen(variabelen, voorwaarden_apparaten, aantal_apparaten, voorwaarden_apparaten_lijst, aantal_uren):
    for q in range(aantal_uren*aantal_apparaten):
        index_voor_voorwaarden = q//aantal_uren # hierdoor weet je bij welk apparaat de uur-constraint hoort
        indexnummers = voorwaarden_apparaten_lijst[index_voor_voorwaarden] # hier wordt de uur-constraint, horende bij een bepaald apparaat, opgevraagd
        for p in indexnummers:
            if type(p) == int: # kan ook dat er geen voorwaarde is, dan wordt de uitdrukking genegeerd
                voorwaarden_apparaten.add(expr=variabelen[p+ index_voor_voorwaarden*aantal_uren] == 1) # variabele wordt gelijk gesteld aan 1

#je kijkt het uur per uur, wnr het uur pos is dan tel je het er op de normale manier bij, wnr het iets negatief werd dan ga je een ander tarief pakken en tel je het zo bij die objectief

def uiteindelijke_waarden(variabelen, aantaluren, namen_apparaten):
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
    return kost, apparaten_aanofuit

def beperkingen_aantal_uur(werkuren_per_apparaat, variabelen, voorwaarden_werkuren, aantal_uren):
    for p in range(len(werkuren_per_apparaat)):
        som = 0
        for q in range(1,aantal_uren+1):
            som = som + variabelen[p*aantal_uren + q] # hier neem je alle variabelen van hetzelfde apparaat, samen
        if type(werkuren_per_apparaat[p]) == int:
            voorwaarden_werkuren.add(expr = som == werkuren_per_apparaat[p]) # apparaat moet x uur aanstaan

def starttijd(variabelen, starturen, constraint_lijst_startuur, aantal_uren):
    for q in range(len(starturen)):
        if type(starturen[q]) != str:
            p = starturen[q]
            for s in range(1, p):
                constraint_lijst_startuur.add(expr= variabelen[aantal_uren*q + s] == 0)

def finaal_uur(finale_uren, variabelen, constraint_lijst_finaal_uur, aantal_uren):
    for q in range(len(finale_uren)):  # dit is welk aparaat het over gaat
        if type(finale_uren[q]) == int:
            p = finale_uren[q]-1  # dit is het eind uur, hierna niet meer in werking
            for s in range(p + 1, aantal_uren + 1):
                constraint_lijst_finaal_uur.add(expr=variabelen[(aantal_uren*q) + s] == 0)

def aantal_uren_na_elkaar(uren_na_elkaarVAR, variabelen, constraint_lijst_aantal_uren_na_elkaar, aantal_uren,
                              variabelen_start):
        # Dat een bepaald apparaat x aantal uur moet werken staat al in beperking_aantal_uur dus niet meer hier
        # wel nog zeggen dat de som van de start waardes allemaal slechts 1 mag zijn
    for i in range(len(uren_na_elkaarVAR)):  # zegt welk apparaat
        if type(uren_na_elkaarVAR[i]) == int:
            opgetelde_start = 0
            for p in range(1, aantal_uren + 1):  # zegt welk uur het is
                opgetelde_start = opgetelde_start + variabelen_start[aantal_uren * i + p]
            #print('dit is eerste constraint', opgetelde_start)
            constraint_lijst_aantal_uren_na_elkaar.add(expr=opgetelde_start == 1)
    for i in range(len(uren_na_elkaarVAR)):  # dit loopt de apparaten af
        if type(uren_na_elkaarVAR[i]) == int:
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
        uitdrukking = (-1, som, max_verbruik_per_uur[p-1])
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
        for p in range(beginindex_in_variabelen,beginindex_in_variabelen + aantaluren):
            temperatuur_dit_uur = temperatuur_dit_uur-warmteverliesfactor + warmtewinst*variabelen[p]
            uitdrukking = (ondergrens, temperatuur_dit_uur, bovengrens)
            voorwaardenlijst.add(expr= uitdrukking)

def som_tot_punt(variabelen, beginpunt, eindpunt):
    som = 0
    for i in range(beginpunt, eindpunt+1):
        som = som + variabelen[i]
    return som

def voorwaarden_batterij(variabelen, constraintlijst, aantaluren, wattagelijst, namen_apparaten, huidig_batterijniveau):
    index_ontladen = namen_apparaten.index('batterij_ontladen')
    index_opladen = namen_apparaten.index('batterij_opladen')
    for q in range(1,aantaluren+1):
        som_ontladen = wattagelijst[index_ontladen]*som_tot_punt(variabelen, index_ontladen*aantaluren + 1, index_ontladen*aantaluren + q)
        som_opladen = wattagelijst[index_opladen]*som_tot_punt(variabelen, index_opladen*aantaluren + 1, index_opladen*aantaluren + q)
        verschil = som_opladen + som_ontladen + huidig_batterijniveau
        constraintlijst.add(expr= (0, verschil, None))


#een lijst maken die de stand van de batterij gaat bijhouden als aantal wat maal aantal uur
#op het einde van het programma dan aanpassen wat die batterij het laatste uur heeft gedaan en zo bijhouden in de database in die variabele
#het getal in die variabele trek je ook altijd op bij som onladen en som ontladen hierboven

# deze functie zal het aantal uur dat het apparaat moet werken verlagen op voorwaarden dat het apparaat ingepland stond
# voor het eerste uur
def verlagen_aantal_uur(lijst, aantal_uren, te_verlagen_uren): #voor aantal uur mogen er geen '/' ingegeven worden, dan crasht het
    print("Urenwerk na functie verlagen_aantal_uur")
    for i in range(len(te_verlagen_uren)):
        if pe.value(lijst[i * aantal_uren + 1]) == 1:
            con = sqlite3.connect("D_VolledigeDatabase.db")
            cur = con.cursor()
            cur.execute("UPDATE Geheugen SET UrenWerk =" + str(te_verlagen_uren[i]-1) +
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

#deze fucntie zal exacte uren als 'aan' aanduiden op voorwaarde dat het eerste uur als 'aan' was aangeduid en er ook was aangeduid dat
#het apparaat x aantal uur na elkaar moest aanstaan, elk uur tot x-1 zal dan al naar 'aan' worden aangeduid voor de volgende berekeningen terug beginnen
def opeenvolging_opschuiven(lijst, aantal_uren, opeenvolgende_uren, oude_exacte_uren):
    print("ExacteUren en eventueel UrenNaElkaar na functie opeenvolging_opschuiven ")
    for i in range(len(opeenvolgende_uren)):
        if type(opeenvolgende_uren[i]) == int and pe.value(lijst[i * aantal_uren + 1]) == 1:
            nieuwe_exacte_uren = []
            for p in range(1, opeenvolgende_uren[i]+1): #dus voor opeenvolgende uren 5, p zal nu 1,2,3,4
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

    #extra: bij dit apparaat '' zetten in de plaats van opeenvolgende aantal uur zodat die geen 24 constraints meer moet gaan maken achteraf

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
            for uur in exacte_uren[i]: # dit zal lopen over al de 'exacte uren' van een specifiek apparaat
                if len(exacte_uren[i]) != 1:
                    if uur-1 != 0:
                        verlaagde_exacte_uren.append(uur-1)
                else:
                    verlaagde_exacte_uren.append(uur-1)
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

#deze functie zal een apparaat volledig verwijderen uit alle lijsten, wnr het aantal uur dat het moet werken op nul is gekomen
def verwijderen_uit_lijst_wnr_aantal_uur_0(aantal_uren_per_apparaat, lijst_met_wattages,
                                           exacte_uren, prijzen_stroom, einduren, aantal_uren):
    #uren_na_elkaarVAR wordt gebaseerd op werkuren per apparaat dus die moet je niet zelf meer aanpassen
    print("Gegevens verwijderen na functie verwijderen_uit_lijst_wnr_aantal_uur_0")
    for i in aantal_uren_per_apparaat:
        if i == 0: #dan gaan we dit apparaat overal verwijderen uit alle lijsten die we hebben
            #eerst lijst met wattages apparaat verwijderen
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



#deze functie zal het finale uur eentje verlagen
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
        #zo aanpassen in database nu
        #einduren[i] = einduren[i] - 1
        
        

#######################################################################################################

#variabelen
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

#interface moet die sentinel in de database 0 maken als er op toevoegen wordt geduwd.
#wnr er iets toegevoegd is, dan mag de sentinel weer op 1 worden gezet en dan zal er terug geoptimaliseerd worden
#######################################################################################################

#aanmaken lijst met binaire variabelen
m.apparaten = pe.VarList(domain=pe.Binary)
m.apparaten.construct()
variabelen_constructor(m.apparaten, aantal_apparaten, aantal_uren) # maakt variabelen aan die apparaten voorstellen

#objectief functie aanmaken
obj_expr = objectieffunctie(prijzen, m.apparaten, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen) # somfunctie die objectief creeërt
m.obj = pe.Objective(sense = pe.minimize, expr = obj_expr)

#aanmaken constraint om op exact uur aan of uit te staan
m.voorwaarden_exact = pe.ConstraintList() # voorwaarde om op een exact uur aan of uit te staan
m.voorwaarden_exact.construct()
exacte_beperkingen(m.apparaten, m.voorwaarden_exact,aantal_apparaten, voorwaarden_apparaten_exact, aantal_uren) # beperkingen met vast uur

#aanmaken constraint om aantal werkuren vast te leggen
m.voorwaarden_aantal_werkuren = pe.ConstraintList()
m.voorwaarden_aantal_werkuren.construct()
beperkingen_aantal_uur(werkuren_per_apparaat, m.apparaten, m.voorwaarden_aantal_werkuren, aantal_uren) # moet x uur werken, maakt niet uit wanneer

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



#deze functies passen de lijsten aan, rekening houdend met de apparaten die gewerkt hebben op het vorige uur
verlagen_aantal_uur(m.apparaten, aantal_uren, werkuren_per_apparaat)


#deze lijn moet sws onder 'verlagen exacte uren' staan want anders voeg je iets toe aan de database en ga je vervolgens dit opnieuw verlagen
opeenvolging_opschuiven(m.apparaten, aantal_uren, uren_na_elkaarVAR, voorwaarden_apparaten_exact)

con = sqlite3.connect("D_VolledigeDatabase.db")
cur = con.cursor()
res = cur.execute("SELECT ExacteUren FROM Geheugen")
ListTuplesExacteUren = res.fetchall()
ExacteUren = exacte_uren_naar_lijst(ListTuplesExacteUren, "ExacteUren")

verlagen_exacte_uren(ExacteUren)


verwijderen_uit_lijst_wnr_aantal_uur_0(werkuren_per_apparaat, wattagelijst, voorwaarden_apparaten_exact, prijzen, einduren, aantal_uren)

verlagen_finale_uur(einduren)
'''
#Nu zullen er op basis van de berekeningen aanpassingen moeten gedaan worden aan de database
#wnr iets het eerste uur wordt berekend als 'aan' dan moeten er bij de volgende berekeningen er mee rekening gehouden worden
#dat dat bepaald apparaat heeft gedraaid op dat uur, dus aantal draai uur is een uur minder, en wnr het drie uur na elkaar moest draaien en het eerste uur werd aangeduid als 'aan', dan moet bij de volgende berekening 1 en 2 nog als 'aan' aangeduid worden
#een batterij is eigenlijk ook gwn aantal uur dat die nog moet werken een uur verlagen

#nog overal in elke functie bijzetten wat er moet gebeuren als er geen integer in staat maar die string
'''
import pyomo.environ as pe
import pyomo.opt as po
from random import uniform

solver = po.SolverFactory('glpk')
m = pe.ConcreteModel()


#######################################################################################################
# definiëren functies
def variabelen_constructor(lijst, aantal_apparaten, aantal_uren):
    for p in range(aantal_uren * aantal_apparaten):  # totaal aantal nodige variabelen = uren maal apparaten
        lijst.add()  # hier telkens nieuwe variabele aanmaken


def objectieffunctie(prijzen, variabelen, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen, vast_verbruik_gezin,
                     batterij_ontladen, batterij_opladen):
    obj_expr = 0
    for p in range(aantal_uren):
        subexpr = 0
        for q in range(len(wattagelijst)):
            subexpr = subexpr + wattagelijst[q] * variabelen[q * aantal_uren + (
                        p + 1)]  # eerst de variabelen van hetzelfde uur samentellen om dan de opbrengst van zonnepanelen eraf te trekken
        obj_expr = obj_expr + Delta_t * prijzen[p] * (subexpr - stroom_zonnepanelen[p] + vast_verbruik_gezin[p] +
                                                      batterij_ontladen[p+1] + batterij_opladen[p+1])
    return obj_expr


def exacte_beperkingen(variabelen, voorwaarden_apparaten, aantal_apparaten, voorwaarden_apparaten_lijst, aantal_uren):
    for q in range(aantal_uren * aantal_apparaten):
        index_voor_voorwaarden = q // aantal_uren  # hierdoor weet je bij welk apparaat de uur-constraint hoort
        indexnummers = voorwaarden_apparaten_lijst[
            index_voor_voorwaarden]  # hier wordt de uur-constraint, horende bij een bepaald apparaat, opgevraagd
        for p in indexnummers:
            if type(p) != str:  # kan ook dat er geen voorwaarde is, dan wordt de uitdrukking genegeerd
                voorwaarden_apparaten.add(expr=variabelen[
                                                   p + index_voor_voorwaarden * aantal_uren] == 1)  # variabele wordt gelijk gesteld aan 1


def uiteindelijke_waarden(variabelen, aantaluren, namen_apparaten, wattagelijst, huidig_batterijniveau, verliesfactor,
                          winstfactor, huidige_temperatuur, batterij_ontladen, batterij_opladen):
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
    print('Batterij_ontladen:')
    for p in range(1, aantaluren + 1):
        print(pe.value(batterij_ontladen[p]))
    print('Batterij_opladen:')
    for p in range(1, aantaluren+1):
        print(pe.value(batterij_opladen[p]))

    apparaten_aanofuit = []
    for p in range(len(namen_apparaten)):
        apparaten_aanofuit.append(pe.value(variabelen[aantaluren * p + 1]))
    nieuw_batterijniveau = pe.value(
        huidig_batterijniveau + batterij_ontladen[1] + batterij_opladen[1])
    i_warmtepomp = namen_apparaten.index('warmtepomp')
    nieuwe_temperatuur = pe.value(
        huidige_temperatuur + winstfactor[0] * variabelen[aantaluren * i_warmtepomp + 1] - verliesfactor[0])
    batterij_ontladen_uur1 = pe.value(batterij_ontladen[1])
    batterij_opladen_uur1 = pe.value(batterij_opladen[1])
    som = batterij_opladen_uur1 + batterij_ontladen_uur1
    return kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur, som


def beperkingen_aantal_uur(werkuren_per_apparaat, variabelen, voorwaarden_werkuren, aantal_uren, einduren,
                           types_apparaten):
    for p in range(len(werkuren_per_apparaat)):
        som = 0
        for q in range(1, aantal_uren + 1):
            som = som + variabelen[p * aantal_uren + q]  # hier neem je alle variabelen van hetzelfde apparaat, samen
        if type(werkuren_per_apparaat[p]) == int and ((type(einduren[p]) == int and einduren[p] <= aantal_uren)
                                                      or types_apparaten[p] == 'Always on'):
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


def voorwaarden_max_verbruik(variabelen, max_verbruik_per_uur, constraintlijst_max_verbruik, wattagelijst, delta_t,
                             opbrengst_zonnepanelen, batterij_ontladen, batterij_opladen):
    totaal_aantal_uren = len(max_verbruik_per_uur)
    for p in range(1, len(max_verbruik_per_uur) + 1):
        som = 0
        for q in range(len(wattagelijst)):
            som = som + delta_t * wattagelijst[q] * (variabelen[q * totaal_aantal_uren + p])
        som = som + opbrengst_zonnepanelen[p-1] + batterij_opladen[p] + batterij_ontladen[p]
        uitdrukking = (-max_verbruik_per_uur[p - 1], som, max_verbruik_per_uur[p - 1])
        constraintlijst_max_verbruik.add(expr=uitdrukking)


def voorwaarden_warmteboiler(apparaten, variabelen,voorwaardenlijst, warmteverliesfactor, warmtewinst,
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


def voorwaarden_batterij(batterij_ontladen, batterij_opladen, constraintlijst, aantaluren,
                         huidig_batterijniveau, batterij_bovengrens):
    for q in range(1, aantaluren + 1):
        som_ontladen = som_tot_punt(batterij_ontladen, 1, q)
        som_opladen = som_tot_punt(batterij_opladen, 1, q)
        verschil = som_opladen + som_ontladen + huidig_batterijniveau
        constraintlijst.add(expr=(0, verschil, batterij_bovengrens))


'''
#deze functie zal het aantal uur dat het apparaat moet werken verlagen op voorwaarden dat het apparaat ingepland stond voor het eerste uur
def verlagen_aantal_uur(lijst, aantal_uren, te_verlagen_uren):
    for i in range(len(te_verlagen_uren)):
        if pe.value(lijst[i * aantal_uren + 1]) == 1:
            #nu moet het volgende gebeuren met de database
            #te_verlagen_uren[i] = te_verlagen_uren[i] - 1


# deze functie zal alle exacte uren die er waren verlagen met 1, als het 0 wordt dan wordt het verwijderd uit de lijst
def verlagen_exacte_uren(exacte_uren):
    for i in range(len(exacte_uren)):  # dit gaat de apparaten af
        for k in range(
            len(exacte_uren[i])):  # dit zal lopen over al de 'exacte uren' van een specifiek apparaat
    # dit aanpassen in de database
    # exacte_uren[i][q] = exacte_uren[i][q] - 1




#deze fucntie zal exacte uren als 'aan' aanduiden op voorwaarde dat het eerste uur als 'aan' was aangeduid en er ook was aangeduid dat
#het apparaat x aantal uur na elkaar moest aanstaan, elk uur tot x-1 zal dan al naar 'aan' worden aangeduid voor de volgende berekeningen terug beginnen
def opeenvolging_opschuiven(lijst, aantal_uren, opeenvolgende_uren):
    for i in range(len(opeenvolgende_uren)):
        if type(opeenvolgende_uren[i]) == int and pe.value(lijst[i * aantal_uren + 1]) == 1:
            for p in range(1,opeenvolgende_uren[i]): #dus voor opeenvolgende uren 5, p zal nu 1,2,3,4
                #in database toevoegen dat i^de lijst 1,2,3,4 allen op 1 worden gezet dus bij in exact uur lijst, dus elke p in lijst i toevoegen

    #extra: bij dit apparaat '' zetten in de plaats van opeenvolgende aantal uur zodat die geen 24 constraints meer moet gaan maken achteraf

#deze functie zal een apparaat volledig verwijderen uit alle lijsten, wnr het aantal uur dat het moet werken op nul is gekomen
def verwijderen_uit_lijst_wnr_aantal_uur_0(aantal_uren_per_apparaat, lijst_met_wattages,
                                           exacte_uren, prijzen_stroom, einduren, aantal_uren) #uren_na_elkaarVAR wordt gebaseerd op werkuren per apparaat dus die moet je niet zelf meer aanpassen

    for i in aantal_uren_per_apparaat:
        if aantal_uren_per_apparaat[i] == 0: #dan gaan we dit apparaat overal verwijderen uit alle lijsten die we hebben
            #eerst lijst met wattages apparaat verwijderen
            for p in range(aantal_uren):




#deze functie zal het finale uur eentje verlagen
def verlagen_finale_uur(klaar_tegen_bepaald_uur):
    for i in range(len(klaar_tegen_bepaald_uur)):
        #zo aanpassen in database nu
        #einduren[i] = einduren[i] - 1


'''


def vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour):
    del verbruik_gezin_totaal[current_hour][0]
    verbruik_gezin_totaal[current_hour].append(uniform(2, 4))


#######################################################################################################
# variabelen
from parameters_test import aantalapparaten as aantal_apparaten
from parameters_test import wattages_apparaten as wattagelijst
from parameters_test import voorwaarden_apparaten_exacte_uren as voorwaarden_apparaten_exact
from parameters_test import tijdsstap as Delta_t
from parameters_test import aantaluren as aantal_uren
from parameters_test import prijslijst_stroomverbruik_per_uur as prijzen
from parameters_test import finale_tijdstip as einduren
from parameters_test import uur_werk_per_apparaat as werkuren_per_apparaat
from parameters_test import stroom_per_uur_zonnepanelen as stroom_zonnepanelen
from parameters_test import uren_na_elkaar as uren_na_elkaarVAR
from parameters_test import namen_apparaten as namen_apparaten
from parameters_test import begintemperatuur as begintemperatuur_huis
from parameters_test import temperatuurwinst_per_uur as temperatuurwinst_per_uur
from parameters_test import verliesfactor_huis_per_uur as verliesfactor_huis_per_uur
from parameters_test import ondergrens as ondergrens
from parameters_test import bovengrens as bovengrens
from parameters_test import starturen as starturen
from parameters_test import maximaal_verbruik_per_uur as maximaal_verbruik_per_uur
from parameters_test import huidig_batterijniveau as huidig_batterijniveau
from parameters_test import batterij_bovengrens as batterij_bovengrens
from parameters_test import vast_verbruik_gezin as vast_verbruik_gezin
from parameters_test import current_hour as current_hour
from parameters_test import verbruik_gezin_totaal as verbruik_gezin_totaal
from parameters_test import types_apparaten as types_apparaten
from parameters_test import max_opladen_batterij as max_opladen_batterij
from parameters_test import max_ontladen_batterij as max_ontladen_batterij
#######################################################################################################
# aanmaken lijst met binaire variabelen
m.apparaten = pe.VarList(domain=pe.Binary)
m.apparaten.construct()
variabelen_constructor(m.apparaten, aantal_apparaten, aantal_uren)  # maakt variabelen aan die apparaten voorstellen

# variabelen aanmaken batterij en domein opleggen
m.batterij_ontladen = pe.VarList()
m.batterij_opladen = pe.VarList()
m.voorwaarden_batterij_grenzen = pe.ConstraintList()
variabelen_constructor(m.batterij_ontladen, 1, aantal_uren)
variabelen_constructor(m.batterij_opladen, 1, aantal_uren)
for p in range(1, aantal_uren+1):
    m.voorwaarden_batterij_grenzen.add(expr = (-max_ontladen_batterij, m.batterij_ontladen[p], 0))
    m.voorwaarden_batterij_grenzen.add(expr = (0, m.batterij_opladen[p], max_opladen_batterij))

# objectief functie aanmaken
obj_expr = objectieffunctie(prijzen, m.apparaten, Delta_t, wattagelijst, aantal_uren, stroom_zonnepanelen,
                            vast_verbruik_gezin, m.batterij_ontladen, m.batterij_opladen)  # somfunctie die objectief creeërt
m.obj = pe.Objective(sense=pe.minimize, expr=obj_expr)

# aanmaken constraint om op exact uur aan of uit te staan
m.voorwaarden_exact = pe.ConstraintList()  # voorwaarde om op een exact uur aan of uit te staan
m.voorwaarden_exact.construct()
exacte_beperkingen(m.apparaten, m.voorwaarden_exact, aantal_apparaten, voorwaarden_apparaten_exact,
                   aantal_uren)  # beperkingen met vast uur

# aanmaken constraint om aantal werkuren vast te leggen
m.voorwaarden_aantal_werkuren = pe.ConstraintList()
m.voorwaarden_aantal_werkuren.construct()
beperkingen_aantal_uur(werkuren_per_apparaat, m.apparaten, m.voorwaarden_aantal_werkuren, aantal_uren, einduren,
                       types_apparaten)  # moet x uur werken, maakt niet uit wanneer

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
voorwaarden_max_verbruik(m.apparaten, maximaal_verbruik_per_uur, m.voorwaarden_maxverbruik, wattagelijst, Delta_t,
                         stroom_zonnepanelen, m.batterij_ontladen, m.batterij_opladen)

# voorwaarden warmtepomp
m.voorwaarden_warmtepomp = pe.ConstraintList()
voorwaarden_warmteboiler(namen_apparaten, m.apparaten, m.voorwaarden_warmtepomp, verliesfactor_huis_per_uur,
                         temperatuurwinst_per_uur, begintemperatuur_huis, ondergrens, bovengrens, aantal_uren)

# voorwaarden batterij
m.voorwaarden_batterij = pe.ConstraintList()
voorwaarden_batterij(m.batterij_ontladen, m.batterij_opladen, m.voorwaarden_batterij, aantal_uren,
                     huidig_batterijniveau, batterij_bovengrens)

result = solver.solve(m)

print(result)
# waarden teruggeven
vast_verbruik_aanpassen(verbruik_gezin_totaal, current_hour)
kost, apparaten_aanofuit, nieuw_batterijniveau, nieuwe_temperatuur, pos_of_neg_opladen= uiteindelijke_waarden(m.apparaten, aantal_uren,
                                                                                            namen_apparaten,
                                                                                           wattagelijst,
                                                                                           huidig_batterijniveau,
                                                                                           verliesfactor_huis_per_uur,
                                                                                           temperatuurwinst_per_uur,
                                                                                           begintemperatuur_huis, m.batterij_ontladen,
                                                                                           m.batterij_opladen)
print('nieuw batterijniveau: ',nieuw_batterijniveau)
print(apparaten_aanofuit)
print('temperatuur: ', nieuwe_temperatuur)
print('batterij_opgeladen: ',pos_of_neg_opladen)
print('verbruik gezin aangepast: ',verbruik_gezin_totaal)

'''
#deze functies passen de lijsten aan, rekening houdend met de apparaten die gewerkt hebben op het vorige uur
verlagen_aantal_uur(m.apparaten, aantal_uren, werkuren_per_apparaat)

verlagen_exacte_uren(voorwaarden_apparaten_exact)

#deze lijn moet sws onder 'verlagen exacte uren' staan want anders voeg je iets toe aan de database en ga je vervolgens dit opnieuw verlagen
opeenvolging_opschuiven(m.apparaten, aantal_uren, uren_na_elkaarVAR)


verlagen_finale_uur(einduren)

verwijderen_uit_lijst_wnr_aantal_uur_0(werkuren_per_apparaat, wattagelijst, voorwaarden_apparaten_exact, prijzen, einduren, aantal_uren)


#Nu zullen er op basis van de berekeningen aanpassingen moeten gedaan worden aan de database
#wnr iets het eerste uur wordt berekend als 'aan' dan moeten er bij de volgende berekeningen er mee rekening gehouden worden
#dat dat bepaald apparaat heeft gedraaid op dat uur, dus aantal draai uur is een uur minder, en wnr het drie uur na elkaar moest draaien en het eerste uur werd aangeduid als 'aan', dan moet bij de volgende berekening 1 en 2 nog als 'aan' aangeduid worden
#een batterij is eigenlijk ook gwn aantal uur dat die nog moet werken een uur verlagen

#nog overal in elke functie bijzetten wat er moet gebeuren als er geen integer in staat maar die string
'''
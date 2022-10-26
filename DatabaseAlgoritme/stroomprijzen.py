import GeheugenVeranderen
import TupleToList
import VolledigeGegevensOpvragen24uur

from VolledigeGegevensOpvragen24uur import Prijzen24uur
from VolledigeGegevensOpvragen24uur import Gegevens24uur

from TupleToList import Apparaten
from TupleToList import Wattages
from TupleToList import ExacteUren
from TupleToList import FinaleTijdstip
from TupleToList import UrenWerk

prijslijst_stroomverbruik_per_uur = Prijzen24uur
print(prijslijst_stroomverbruik_per_uur)

stroom_per_uur_zonnepanelen = [radiatieuur * 0.2 * 12 for radiatieuur in Gegevens24uur[1]]
print(stroom_per_uur_zonnepanelen)

namen_apparaten = Apparaten
print(namen_apparaten)

wattages_apparaten = Wattages
print(wattages_apparaten)

voorwaarden_apparaten_exacte_uren = [[], [], [], []] # moet op deze uren werken
print(voorwaarden_apparaten_exacte_uren)

aantalapparaten = len(wattages_apparaten)
tijdsstap = 1 # bekijken per uur
aantaluren = len(prijslijst_stroomverbruik_per_uur)

finale_tijdstip = ['', '', '', ''] # wanneer toestel zeker klaar moet zijn
print(finale_tijdstip)

uur_werk_per_apparaat = UrenWerk # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer
print(uur_werk_per_apparaat)

uren_na_elkaar = [4,'', 4, '']
'''
na_elkaar= 'nee'

if na_elkaar == 'ja':
    uren_na_elkaar = uur_werk_per_apparaat
else:
    uren_na_elkaar = ['']*len(wattages_apparaten)

#controle op tegenstrijdigheden in code
assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat)
for i in range(len(voorwaarden_apparaten_exacte_uren)):
    if type(uur_werk_per_apparaat[i]) == int:
        assert len(voorwaarden_apparaten_exacte_uren[i]) <= uur_werk_per_apparaat[i]
    for p in range(len(voorwaarden_apparaten_exacte_uren[i])):
        if len(voorwaarden_apparaten_exacte_uren[i]) > 0:
            assert voorwaarden_apparaten_exacte_uren[i][p] < finale_tijdstip[i]
'''

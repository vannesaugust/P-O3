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
from TupleToList import UrenNaElkaar

EFFICIENTIE = 0.2
OPP_ZONNEPANELEN = 12
prijslijst_stroomverbruik_per_uur = Prijzen24uur

stroom_per_uur_zonnepanelen = [radiatieuur * EFFICIENTIE * OPP_ZONNEPANELEN for radiatieuur in Gegevens24uur[1]]

namen_apparaten = Apparaten

wattages_apparaten = Wattages

voorwaarden_apparaten_exacte_uren = ExacteUren  # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)
tijdsstap = 1  # bekijken per uur
aantaluren = len(prijslijst_stroomverbruik_per_uur)

finale_tijdstip = FinaleTijdstip  # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = UrenWerk  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer

uren_na_elkaar = UrenNaElkaar


prijslijst_stroomverbruik_per_uur = [1,2,3, 1, 4, 6, 7, 3, 1, 3, 6, 1]
verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
wattages_apparaten = [11, 13, 14, 10, 15]
verliesfactor_huis_per_uur = 1 # in graden C
temperatuurwinst_per_uur = 2 # in graden C
begintemperatuur = 18 # in graden C
ondergrens = 17 # mag niet kouder worden dan dit
bovengrens = 22 # mag niet warmer worden dan dit


#controle op tegenstrijdigheden in code
assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat)
for i in range(len(voorwaarden_apparaten_exacte_uren)):
    if type(uur_werk_per_apparaat[i]) == int:
        assert len(voorwaarden_apparaten_exacte_uren[i]) <= uur_werk_per_apparaat[i]
    for p in range(len(voorwaarden_apparaten_exacte_uren[i])):
        if len(voorwaarden_apparaten_exacte_uren[i]) > 0:
            assert voorwaarden_apparaten_exacte_uren[i][p] < finale_tijdstip[i]

for p in range(len(wattages_apparaten)):
    if type(uur_werk_per_apparaat[p]) == int:
        assert type(uren_na_elkaar[p]) == str
    if type(uren_na_elkaar[p]) == int:
        assert type(uur_werk_per_apparaat[p]) == str


# Ter illustratie
print(prijslijst_stroomverbruik_per_uur)
print(stroom_per_uur_zonnepanelen)
print(namen_apparaten)
print(wattages_apparaten)
print(voorwaarden_apparaten_exacte_uren)
print(finale_tijdstip)
print(uur_werk_per_apparaat)
print(UrenNaElkaar)
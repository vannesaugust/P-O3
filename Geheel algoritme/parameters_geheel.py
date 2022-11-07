# Geheugen voor de eerste keer veranderen met gegevens uit de interface
import GeheugenVeranderen

# Lijsten van tuples die de database teruggeeft omzetten in lijsten met integers of strings
import TupleToList

# Gegevens uit de CSV-bestanden opvragen voor de komende 24 uren vanaf een bepaalde datum en uur
import VolledigeGegevensOpvragen24uur

from VolledigeGegevensOpvragen24uur import Prijzen24uur
from VolledigeGegevensOpvragen24uur import Gegevens24uur

from TupleToList import Apparaten
from TupleToList import Wattages
from TupleToList import ExacteUren
from TupleToList import FinaleTijdstip
from TupleToList import UrenWerk
from TupleToList import UrenNaElkaar
from TupleToList import BeginUur

EFFICIENTIE = 0.2
OPP_ZONNEPANELEN = 12
prijslijst_stroomverbruik_per_uur = Prijzen24uur

stroom_per_uur_zonnepanelen = [irradiantie * EFFICIENTIE * OPP_ZONNEPANELEN for irradiantie in Gegevens24uur[1]]

namen_apparaten = Apparaten

wattages_apparaten = Wattages

voorwaarden_apparaten_exacte_uren = ExacteUren  # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)
tijdsstap = 1  # bekijken per uur
aantaluren = len(prijslijst_stroomverbruik_per_uur)

finale_tijdstip = FinaleTijdstip  # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = UrenWerk  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer

uren_na_elkaar = UrenNaElkaar
begin_uur = BeginUur


verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
verliesfactor_huis_per_uur = 1  # in graden C
temperatuurwinst_per_uur = 2  # in graden C
begintemperatuur = 18  # in graden C
ondergrens = 17  # mag niet kouder worden dan dit
bovengrens = 22  # mag niet warmer worden dan dit

# controle op tegenstrijdigheden in code
assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat)
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
print(UrenNaElkaar)

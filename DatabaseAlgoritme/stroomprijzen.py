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

# Ter illustratie
print(prijslijst_stroomverbruik_per_uur)
print(stroom_per_uur_zonnepanelen)
print(namen_apparaten)
print(wattages_apparaten)
print(voorwaarden_apparaten_exacte_uren)
print(finale_tijdstip)
print(uur_werk_per_apparaat)
print(UrenNaElkaar)

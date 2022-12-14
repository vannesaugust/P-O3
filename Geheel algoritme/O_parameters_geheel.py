# Geheugen voor de eerste keer veranderen met gegevens uit de interface
import D_GeheugenVeranderen

# Lijsten van tuples die de database teruggeeft omzetten in lijsten met integers of strings
import D_TupleToList

# Gegevens uit de CSV-bestanden opvragen voor de komende 24 uren vanaf een bepaalde datum en uur
import D_GegevensOpvragen24uur

from D_GegevensOpvragen24uur import Prijzen24uur
from D_GegevensOpvragen24uur import Gegevens24uur

from D_TupleToList import Apparaten
from D_TupleToList import Wattages
from D_TupleToList import ExacteUren
from D_TupleToList import FinaleTijdstip
from D_TupleToList import UrenWerk
from D_TupleToList import UrenNaElkaar
from D_TupleToList import BeginUur

EFFICIENTIE = 0.2
OPP_ZONNEPANELEN = 12
prijslijst_stroomverbruik_per_uur = Prijzen24uur

stroom_per_uur_zonnepanelen = [irradiantie * EFFICIENTIE * OPP_ZONNEPANELEN for irradiantie in Gegevens24uur[1]]

# namen_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen','droogkast', 'wasmachine', 'frigo']
namen_apparaten = Apparaten

# wattages_apparaten = [15, -14.344, 12.2, 14, 10, 12]
wattages_apparaten = Wattages

#voorwaarden_apparaten_exacte_uren = [[7, 8], [], [], [], [], []]
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


#verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
verliesfactor_huis_per_uur = [1 for i in range(24)]  # in graden C
temperatuurwinst_per_uur = [2 for i in range(24)]  # in graden C
begintemperatuur = 19  # in graden C
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
print(90*'-')
print('stroomverbruik per uur: ',prijslijst_stroomverbruik_per_uur)
print('stroom per uur zonnepanelen: ',stroom_per_uur_zonnepanelen)
print('namen apparaten: ',namen_apparaten)
print('wattages: ',wattages_apparaten)
print('voorwaarden exacte uren: ',voorwaarden_apparaten_exacte_uren)
print('starturen: ',starturen)
print('finale uren: ',finale_tijdstip)
print('uur werk (niet na elkaar): ', uur_werk_per_apparaat)
print('uur werk na elkaar: ',uren_na_elkaar)

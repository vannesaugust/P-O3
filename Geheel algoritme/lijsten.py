from MainApplication import lijst_apparaten
from MainApplication import lijst_verbruiken
from MainApplication import lijst_beginuur
from MainApplication import lijst_deadlines
from MainApplication import lijst_capaciteit
from MainApplication import lijst_aantal_uren
from MainApplication import lijst_soort_apparaat
from MainApplication import lijst_status
from MainApplication import lijst_uren_na_elkaar


namen_apparaten = lijst_apparaten
wattages_apparaten = lijst_verbruiken
voorwaarden_apparaten_exacte_uren = [['/'], [1,7], [1], [1,1], ['/'], ['/']]
finale_tijdstip = lijst_deadlines
uur_werk_per_apparaat = lijst_aantal_uren
uren_na_elkaar = lijst_uren_na_elkaar
print(namen_apparaten)
print(wattages_apparaten)
print(voorwaarden_apparaten_exacte_uren)
print(finale_tijdstip)
print(uur_werk_per_apparaat)
print(uren_na_elkaar)
"""
namen_apparaten = ["droogkast", 'robotmaaier', 'wasmachine', 'vaatwasser']
wattages_apparaten = [2500, 1700, 2700, 2100]
voorwaarden_apparaten_exacte_uren = [['/'], [1,7], [1], [1,1]]  # moet op deze uren werken
finale_tijdstip = [10, 10, 10, 11]  # wanneer toestel zeker klaar moet zijn
uur_werk_per_apparaat = [1, 2, 4, 3]  # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer
uren_na_elkaar = [1, '/', 4, '/']
"""


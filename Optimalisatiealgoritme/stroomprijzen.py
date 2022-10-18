prijslijst_stroomverbruik_per_uur = [1,2,3, 1, 4, 6, 7, 3, 1, 3, 6, 1]
namen_apparaten = ['droogkast', 'robotmaaier', 'wasmachine', 'frigo']
wattages_apparaten = [11, 13, 14, 10]
voorwaarden_apparaten_exacte_uren = [[7, 8], [5], [4], [10]] # moet op deze uren werken
aantalapparaten = len(wattages_apparaten)
tijdsstap = 1 # bekijken per uur
aantaluren = len(prijslijst_stroomverbruik_per_uur)
finale_tijdstip = [10, 10, 10, 11] # wanneer toestel zeker klaar moet zijn
uur_werk_per_apparaat = ['', 4, 5, 5] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer
stroom_per_uur_zonnepanelen = [i for i in range(6)] + [i for i in range(6, 0, -1)]

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


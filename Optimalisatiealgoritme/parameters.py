
prijslijst_stroomverbruik_per_uur = [1,2,3, 1, 4, 6, 7, 3, 1, 3, 6, 1]
verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
namen_apparaten = ['droogkast', 'robotmaaier', 'wasmachine', 'frigo']
wattages_apparaten = [11, 13, 14, 10]

warmtepomp = 'ja'
verbruik_warmtepomp = 15
verliesfactor_huis_per_uur = 1 # in graden C
temperatuurwinst_per_uur = 2 # in graden C
begintemperatuur = 18 # in graden C
ondergrens = 17 # mag niet kouder worden dan dit
bovengrens = 20 # mag niet warmer worden dan dit

voorwaarden_apparaten_exacte_uren = [[], [], [], [], []] # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)

tijdsstap = 1 # bekijken per uur

aantaluren = len(prijslijst_stroomverbruik_per_uur)

starturen = [3, 2, 3, 6, '/']
finale_tijdstip = [10, 10, 10, 11, '/'] # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = ['/', 4, 5, 4, '/'] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer

stroom_per_uur_zonnepanelen = [i for i in range(6)] + [i for i in range(6, 0, -1)]

maximaal_verbruik_per_uur = [350 for i in range(len(prijslijst_stroomverbruik_per_uur))]

uren_na_elkaar = [2, '/','/','/', '/']

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


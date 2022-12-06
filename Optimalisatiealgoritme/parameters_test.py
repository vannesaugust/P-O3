
prijslijst_stroomverbruik_per_uur = [0.0968, 0.09717, 0.09520999999999999, 0.11166, 0.14997, 0.14633000000000002, 0.14028, 0.12188, 0.10260999999999999, 0.09745999999999999, 0.08516, 0.05708]




prijslijst_negatief = [prijslijst_stroomverbruik_per_uur[p] /10 for p in range(len(prijslijst_stroomverbruik_per_uur))]

OPP_ZONNEPANELEN = 12.0
EFFICIENTIE = 0.2
stroom_per_uur_zonnepanelen = [0.15234167999040002, 0.0703075200024, 0.008647920000000002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]




aantaluren = len(prijslijst_stroomverbruik_per_uur)


#verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
namen_apparaten = ['warmtepomp','wasmachine', 'stofzuiger', 'droogkast']
wattages_apparaten = [2,3,3,4]

max_opladen_batterij = 6
max_ontladen_batterij = 4

types_apparaten = ['/','Device with battery', 'Always on', 'consumer' ]
verliesfactor_huis_per_uur = [1 for i in range(aantaluren)] # in graden C
temperatuurwinst_per_uur = [2 for i in range(aantaluren)] # in graden C
begintemperatuur = 22 # in graden C
ondergrens = 20 # mag niet kouder worden dan dit
bovengrens = 24 # mag niet warmer worden dan dit

huidig_batterijniveau = 4
batterij_bovengrens = 12

voorwaarden_apparaten_exacte_uren = [[],[], [], []] # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)

tijdsstap = 1 # bekijken per uur

current_hour = 4
aantal_dagen_in_gemiddelde = 3
verbruik_gezin_totaal = [[0.5, 1, 0.5] for p in range(aantaluren)]
vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]

starturen = ['/',1, 2, '/']
finale_tijdstip = ['/',7, 17, 18] # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = ['/',4, 7, 8] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer


maximaal_verbruik_per_uur = [3000 for i in range(len(prijslijst_stroomverbruik_per_uur))]

uren_na_elkaar = ['/','/','/', '/']

#controle op tegenstrijdigheden in code
assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat) == len(types_apparaten)
assert len(verliesfactor_huis_per_uur) == len(temperatuurwinst_per_uur) == aantaluren == len(maximaal_verbruik_per_uur)
for i in range(len(voorwaarden_apparaten_exacte_uren)):
    if type(uur_werk_per_apparaat[i]) == int:
        assert len(voorwaarden_apparaten_exacte_uren[i]) <= uur_werk_per_apparaat[i]
    for p in range(len(voorwaarden_apparaten_exacte_uren[i])):
        if len(voorwaarden_apparaten_exacte_uren[i]) > 0:
            assert voorwaarden_apparaten_exacte_uren[i][p] < finale_tijdstip[i]
'''
for p in range(len(wattages_apparaten)):
    if type(uur_werk_per_apparaat[p]) == int:
        assert type(uren_na_elkaar[p]) == str
    if type(uren_na_elkaar[p]) == int:
        assert type(uur_werk_per_apparaat[p]) == str
'''

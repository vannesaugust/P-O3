
prijslijst_stroomverbruik_per_uur = [0.01,0.02,0.03,0.07,0.04,0.05]


prijslijst_negatief = [prijslijst_stroomverbruik_per_uur[p] /2 for p in range(len(prijslijst_stroomverbruik_per_uur))]

OPP_ZONNEPANELEN = 12.0
EFFICIENTIE = 0.2
stroom_per_uur_zonnepanelen = [0.0009, 0.001, 0.0012, 0.0016, 0.0011, 0.0001]


aantaluren = len(prijslijst_stroomverbruik_per_uur)


#verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
namen_apparaten = ['warmtepomp','wasmachine', 'stofzuiger', 'droogkast']
wattages_apparaten = [2,3,3,4]

max_opladen_batterij = 4
max_ontladen_batterij = 6

types_apparaten = ['/','Device with battery', 'Always on', 'consumer' ]
verliesfactor_huis_per_uur = [1 for i in range(aantaluren)] # in graden C
temperatuurwinst_per_uur = [2 for i in range(aantaluren)] # in graden C
begintemperatuur = 21 # in graden C
ondergrens = 20 # mag niet kouder worden dan dit
bovengrens = 24 # mag niet warmer worden dan dit

huidig_batterijniveau = 4
batterij_bovengrens = 12

voorwaarden_apparaten_exacte_uren = [[],[], [], []] # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)

tijdsstap = 1 # bekijken per uur

current_hour = 4
aantal_dagen_in_gemiddelde = 3
verbruik_gezin_totaal = [[3, 4, 3] for p in range(aantaluren)]
vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]

starturen = ['/',1, 2, '/']
finale_tijdstip = ['/',4, 6, 6] # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = ['/',2, '/', '/'] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer


maximaal_verbruik_per_uur = [3000 for i in range(len(prijslijst_stroomverbruik_per_uur))]

uren_na_elkaar = ['/','/',3, 4]

#controle op tegenstrijdigheden in code
assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat) == len(types_apparaten)
assert len(verliesfactor_huis_per_uur) == len(temperatuurwinst_per_uur) == aantaluren == len(maximaal_verbruik_per_uur)
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


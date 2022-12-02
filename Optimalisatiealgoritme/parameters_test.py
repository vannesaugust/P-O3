
prijslijst_stroomverbruik_per_uur = [0.07511, 0.05091, 0.03767, 0.039700000000000006, 0.04059, 0.04326, 0.049659999999999996, 0.07005, 0.07679000000000001, 0.0841, 0.09473999999999999, 0.0968, 0.09717, 0.09520999999999999, 0.11166, 0.14997, 0.14633000000000002, 0.14028, 0.12188, 0.10260999999999999, 0.09745999999999999, 0.08516, 0.05708, 0.05259000000000000]

prijslijst_negatief = [prijslijst_stroomverbruik_per_uur[p] /2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
irradiantie = [0.0, 0.0, 0.0, 0.0, 0.0, 0.34669999999999995, 20.509099998, 50.409499997999994, 79.691899997, 99.42770000499999, 100.307500004, 63.475699996, 29.294800001, 3.6033000000000004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

OPP_ZONNEPANELEN = 12.0
EFFICIENTIE = 0.2
stroom_per_uur_zonnepanelen = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00083208, 0.04922183999520001, 0.12098279999519998, 0.1912605599928, 0.238626480012, 0.24073800000960002, 0.15234167999040002, 0.0703075200024, 0.008647920000000002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

aantaluren = len(prijslijst_stroomverbruik_per_uur)


#verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
namen_apparaten = ['warmtepomp','elektrische wagen', 'wasmachine', 'frigo']
wattages_apparaten = [11,14, 10, 12]

max_opladen_batterij = 4
max_ontladen_batterij = 6

wattage_warmtemomp = 11
types_apparaten = ['/','Device with battery', 'Always on', 'consumer' ]
verliesfactor_huis_per_uur = [1 for i in range(aantaluren)] # in graden C
temperatuurwinst_per_uur = [2 for i in range(aantaluren)] # in graden C
begintemperatuur = 20 # in graden C
ondergrens = 17 # mag niet kouder worden dan dit
bovengrens = 20 # mag niet warmer worden dan dit

huidig_batterijniveau = 10
batterij_bovengrens = 70

voorwaarden_apparaten_exacte_uren = [[],[], [], []] # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)

tijdsstap = 1 # bekijken per uur

current_hour = 4
aantal_dagen_in_gemiddelde = 3
verbruik_gezin_totaal = [[3, 4, 3] for p in range(aantaluren)]
vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]

starturen = ['/',3, '/', 4]
finale_tijdstip = ['/',24, '/', 17] # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = ['/',4, 20, '/'] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer


maximaal_verbruik_per_uur = [400 for i in range(len(prijslijst_stroomverbruik_per_uur))]

uren_na_elkaar = ['/','/','/', 5]

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

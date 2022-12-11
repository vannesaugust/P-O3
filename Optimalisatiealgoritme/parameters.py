
prijslijst_stroomverbruik_per_uur = [1, 2, 3, 2, 4, 6, 4, 2, 8, 6, 4, 2]
irradiantie = [1.0, 1.0, 1.0, 1.0, 1.0]
OPP_ZONNEPANELEN = 12.0
EFFICIENTIE = 0.2
stroom_per_uur_zonnepanelen = [4, 5, 6, 7, 3, 5, 7, 3, 1, 6, 8, 9]
aantaluren = len(prijslijst_stroomverbruik_per_uur)
verkoopprijs_van_zonnepanelen = [i/10 for i in prijslijst_stroomverbruik_per_uur]

#verkoopprijs_van_zonnepanelen = [prijslijst_stroomverbruik_per_uur[p]/2 for p in range(len(prijslijst_stroomverbruik_per_uur))]
namen_apparaten = ['warmtepomp','batterij_ontladen', 'batterij_opladen']
wattages_apparaten = [3, 4, 4]

types_apparaten = ['', '', '']

verliesfactor_huis_per_uur = [1 for i in range(aantaluren)] # in graden C
temperatuurwinst_per_uur = [2 for i in range(aantaluren)] # in graden C
begintemperatuur = 20 # in graden C
ondergrens = 17 # mag niet kouder worden dan dit
bovengrens = 20 # mag niet warmer worden dan dit

huidig_batterijniveau = 10
batterij_bovengrens = 200

voorwaarden_apparaten_exacte_uren = [[], [],[]] # moet op deze uren werken

aantalapparaten = len(wattages_apparaten)

tijdsstap = 1 # bekijken per uur

current_hour = 4
aantal_dagen_in_gemiddelde = 3
verbruik_gezin_totaal = [[3 for i in range(aantal_dagen_in_gemiddelde)] for p in range(aantaluren)]
vast_verbruik_gezin = [sum(verbruik_gezin_totaal[p])/len(verbruik_gezin_totaal[p]) for p in range(len(verbruik_gezin_totaal))]

starturen = ['/','/', '/']
finale_tijdstip = ['/','/','/'] # wanneer toestel zeker klaar moet zijn

uur_werk_per_apparaat = ['/',1, 1] # moet in bepaalde tijdsduur zoveel aan staan, maakt niet uit wanneer


maximaal_verbruik_per_uur = [3600 for i in range(len(prijslijst_stroomverbruik_per_uur))]

uren_na_elkaar = ['/','/', '/']

#controle op tegenstrijdigheden in code
'''assert len(wattages_apparaten) == len(namen_apparaten) == len(voorwaarden_apparaten_exacte_uren) == len(uur_werk_per_apparaat) == len(types_apparaten)
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
'''

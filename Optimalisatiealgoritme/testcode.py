# mogelijkheid: heel veel mogelijke variabelen aanmaken en dan slechts enkele ervan gebruiken

import pyomo.environ as pe
import pyomo.opt as po


solver = po.SolverFactory('glpk')

Delta_t = 1 # tijdsinterval (h)

# kost energie (varieert per tijdsinterval) (EUR/kWh)
from variabelen import prijslijst as prijzen


m = pe.ConcreteModel()

# Create variables: wm1, wm2, wm3: de aan/uit-stand van de wasmachine gedurende tijdsinterval t1, t2 en t3 respectivelijk



m.wm = pe.VarList(domain=pe.Binary)
m.dk = pe.VarList(domain=pe.Binary)
m.gm = pe.VarList(domain= pe.Binary)
for p in range(1,13):
    m.wm.add()
    m.dk.add()
    m.gm.add()
lijst =[m.wm, m.dk, m.gm]

from variabelen import wattages_apparaten as wattagelijst
# Set objective: zo weinig mogelijk kosten
obj_expr = 0
for p in range(len(lijst)):
    for q in range(1,len(lijst[0])+1):
        obj_expr = obj_expr + Delta_t * wattagelijst[p] * prijzen[q-1] * lijst[p][q]

print(obj_expr)

m.obj = pe.Objective(sense = pe.minimize, expr = obj_expr)

# Add constraints: de wasmachine moet gedurende 1 tijdsinterval aanstaan
from variabelen import voorwaarden_apparaten as voorwaarden

m.voorw = pe.ConstraintList()
for q in range(len(voorwaarden)):
    for p in range(len(voorwaarden[q])):
        index = voorwaarden[q][p]
        m.voorw.add(expr = lijst[q][index] == 1)

from variabelen import uur_klaar as finale_tijdstip
for q in range(len(finale_tijdstip)): #dit is welk aparaat het over gaat
    p = finale_tijdstip[q] #dit is het eind uur, hierna niet meer in werking
    for p in range(p + 1, 13):
        m.voorw.add(expr=lijst[q][p] == 0)

result = solver.solve(m)

print(result)

print(pe.value(m.obj))
for p in range(len(lijst)):
    for q in range(len(lijst[0])):
        print(pe.value(lijst[p][q+1]))

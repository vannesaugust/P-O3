import pyomo.environ as pe
import pyomo.opt as po


solver = po.SolverFactory('glpk')

wm1 = pe.Var(domain = pe.Binary)
wm2 = pe.Var(domain = pe.Binary)
wm3 = pe.Var(domain = pe.Binary)

apparatenlijst = [wm1, wm2, wm3]
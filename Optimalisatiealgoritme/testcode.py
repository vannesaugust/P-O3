import pyomo.environ as pe
import pyomo.opt as po

solver = po.SolverFactory('glpk')
m = pe.ConcreteModel()

x = pe.Var(domain= pe.Binary)
y = pe.Var(domain=pe.Binary)
z = x*y

U = 1
L = 0
m.voorwaarden = pe.ConstraintList()
m.voorwaarden.add((None, z, U*x))
m.voorwaarden.add((None, L*x, z))
m.voorwaarden.add((None, z, y-L*(1-x)))
m.voorwaarden.add((None, y-U*(1-x), z))
m.obj = pe.Objective(sense= pe.minimize, expr= z)
result = solver.solve(m)
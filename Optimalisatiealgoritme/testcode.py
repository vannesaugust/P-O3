import pyomo.environ as pe
import pyomo.opt as po

solver = po.SolverFactory('glpk')
m = pe.ConcreteModel()
m.x = pe.Var(domain= pe.Binary)

m.y = pe.Var()
m.z = pe.Var()

U = 14
L = -1
m.voorwaarden = pe.ConstraintList()
m.voorwaarden.add(expr= (None, m.z, U*m.x))
m.voorwaarden.add(expr=(None, L*m.x, m.z))
m.voorwaarden.add(expr=(None, m.z, m.y-L*(1-m.x)))
m.voorwaarden.add(expr=(None, m.y-U*(1-m.x), m.z))
m.obj = pe.Objective(sense= pe.maximize, expr= m.z)

result = solver.solve(m)
print(result)
print('z: ', pe.value(m.z))
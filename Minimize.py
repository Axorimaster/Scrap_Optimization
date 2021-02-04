import numpy as np
from scipy.optimize import linprog
inventario = [100.0,200.0,300.0,400.0,500.0,600.0,700.0,800.0]
costo = [200.0,300.0,400.0,500.0,600.0,700.0,800.0,900.0]


def bounds(inv, L_bond):
    for x in inv:
        bnd = (0, x)
        L_bond.append(bnd)
    return tuple(L_bond)

lhs = [[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]
b = [-29999],[30001]

L_bond = []
bnds = bounds(inventario,L_bond)
print(bnds)
lp_opt = linprog(c = costo, A_ub=lhs, b_ub=b,bounds=bnds)
print(lp_opt)
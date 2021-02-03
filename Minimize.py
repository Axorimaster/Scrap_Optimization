import numpy as np
from scipy.optimize import minimize

inventario = [100.0,200.0,300.0,400.0,500.0,600.0,700.0,800.0]
costo = [200.0,300.0,400.0,500.0,600.0,700.0,800.0,900.0]


def objective(x):
    return np.sum(x)


def constraint1(x):
    return x[0]*x[1]*x[2]*x[3]-25.0


def constraint2(x):
    sum_eq = 40.0
    for i in range(4):
        sum_eq = sum_eq - x[i]**2
    return sum_eq


def init():
    n = 8
    x0 = np.zeros(n)
    for i in range(8):
        x0[i] = 100.0
    return x0


def bonds():
    bnds = []
    for i in range(8):
        bond = (0, inventario[i])
        bnds.append(bond)

    return tuple(bnds)

def optimize():

    x0 = init()
    bnds = bonds()
    con1 = {'type': 'ineq', 'fun': constraint1}
    con2 = {'type': 'eq', 'fun': constraint2}
    cons = ([con1, con2])
    solution = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)
    print(solution.objective)
    return solution.x


# show final objective
print(optimize())

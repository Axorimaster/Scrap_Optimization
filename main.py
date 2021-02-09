import pandas as pd
import Simplex
from tabulate import tabulate
import numpy as np
from graphics import *


def round_col(df, nom_col):

    l_round = df[nom_col].tolist()
    l = [round(num,1) for num in l_round ]
    df.drop(columns=[nom_col])
    df[nom_col] = l


def calc_mix(prod_mes):
    df_inventario['Mix'] = (df_inventario['Uso'] / prod_mes)*100
    round_col(df_inventario, 'Mix')
    df_inventario['Costo'] = df_inventario['Uso'] * df_inventario['Precio']
    df_inventario['Carga'] = (df_inventario['Mix'] * carga)/100
    df_inventario['Volumen'] = df_inventario['Carga'] / df_inventario['Densidad']


def calc_contaminantes(comp, inventario):
    l_carga = inventario['Carga'].tolist()
    l_col = list(comp.columns)
    l_col.pop(0)
    l_cvalue = []
    for col in l_col:
        sum = 0
        l_cont = comp[col].tolist()
        for x in range(len(l_carga)):
            sum = sum + l_carga[x]*l_cont[x]

        l_cvalue.append(round(sum/35,2))
        print("Contenido de", col, ":", round(sum/35,2))

    return l_col,l_cvalue


def calc_cestas(inventario, v_max_cesta, l_max_cesta, n_cestas):

    inventario['Index'] = [0,1,2,3,4,5,6,7]
    df_base_scrap = inventario[inventario.Densidad <= 0.5]
    df_sdensidadmax = inventario.sort_values(by=['Densidad'], ascending=False)
    l_rho = df_sdensidadmax['Densidad'].tolist()
    l_base_scrap = list(df_base_scrap.index.values)


    l_sorted_scrap = list(df_sdensidadmax.index.values)
    l_vol = df_sdensidadmax['Volumen'].tolist()

    res_base_scrap = 0
    for scrap in l_base_scrap:
        res_base_scrap = res_base_scrap + inventario.loc[scrap, 'Volumen']
    res_base_scrap = res_base_scrap/n_cestas


    for cesta in range(n_cestas):
        l_vol_cesta = []
        x = 0
        nom_ces = str("Cesta N°"+str(cesta+1))

        for scrap in l_sorted_scrap:

            if scrap in l_base_scrap:
                scrap_load_vol = inventario.loc[scrap, 'Volumen']
                l_vol_cesta.append(scrap_load_vol/n_cestas)

            else:
                if (l_vol[x]) <= (v_max_cesta-sum(l_vol_cesta)-res_base_scrap-cesta*2):

                    scrap_load_vol = l_vol[x]
                    l_vol[x] = l_vol[x] - scrap_load_vol
                    l_vol_cesta.append(scrap_load_vol)

                else:

                    scrap_load_vol = (v_max_cesta-sum(l_vol_cesta)-res_base_scrap-cesta*2)
                    l_vol[x] = l_vol[x] - scrap_load_vol
                    l_vol_cesta.append(scrap_load_vol)

            x = x+1

        peso = 0

        for i in range(len(l_vol_cesta)):
            peso = peso+(l_vol_cesta[i]*l_rho[i])
            peso = round(peso,1)

        print("Peso",nom_ces,": ", peso)
        df_sdensidadmax[nom_ces] = l_vol_cesta
        round_col(df_sdensidadmax,nom_ces)

    df = df_sdensidadmax.sort_values(by=['Index'])
    res = df.drop(columns=['Index'])
    return(res)


##Input de datos operativos
prod_mes = int(input("Ingrese la producción mensual en toneladas: "))
carga = 35.0
vol_cesta = 28*0.95
carga_cesta = 15
num_cesta = int(input("Ingrese el número máximo de cestas: "))

##Setear display del df
pd.set_option("display.max_rows", None, "display.max_columns", None, "display.max_colwidth", 200)



##Lectura hoja de cálculo mix
df_inventario = pd.read_excel("Mix.xlsx", index_col=0, sheet_name='Inventario', usecols="A:F", nrows=8)
df_comp = pd.read_excel('Mix.xlsx', sheet_name='Composicion', index_col=None, usecols='A:J', nrows=8)


##Formateo de datos de precios e inventarios para Simplex
l_precios = df_inventario['Precio'].tolist()
l_precios.append(0)
l_inv = df_inventario['Inventario'].tolist()
l_lifeline = df_inventario['Lifeline'].tolist()
l_density = df_inventario['Densidad'].tolist()
l_rend = df_inventario['Rendimiento'].tolist()
l_inv_ll = list(map(lambda x, y: x - (x * y), l_inv, l_lifeline))


##Minimización del costo mediante Simplex
sol_dir = Simplex.minimize(8, 19, l_precios, l_inv_ll, prod_mes, l_density, num_cesta, vol_cesta, carga, l_rend)
if 'min' in sol_dir:
    sol_dir.pop('min')

L_uso = list(sol_dir.values())
df_inventario['Uso'] = L_uso

##Formateo de dataframe inventario
calc_mix(prod_mes)
L_costo = df_inventario['Costo'].tolist()


print("------------------RESULTADOS------------------")

##Cálculo del número de cestas
Scrap_vol = df_inventario['Volumen'].sum()
num_load = Scrap_vol/vol_cesta
print("Número de cestas: ", num_load)

##Cálculo del costo por tonelada de chatarra
Scrap_kpi = sum(L_costo) / sum(L_uso)

print("Costo por tonelada de chatarra: ", round(Scrap_kpi,2),"$/ton")


##Cálculo de contaminantes
print("-----------------CONTAMINANTES----------------")
L_cont,L_cvalue = calc_contaminantes(df_comp,df_inventario)

##Carga de cestas
print("--------------------CESTAS--------------------")
L_carga = df_inventario['Carga'].tolist()
df_res = calc_cestas(df_inventario, vol_cesta, carga_cesta, num_cesta)
print(tabulate(df_res, headers='keys', tablefmt='psql'))

"""
win = GraphWin(width=800, height=800) # create a window
win.setCoords(0, 0, 10, 10) # set the coordinates of the window; bottom left is (0, 0) and top right is (10, 10)
mySquare = Rectangle(Point(1, 1), Point(9, 9)) # create a rectangle from (1, 1) to (9, 9)
mySquare.draw(win) # draw it to the window
win.getMouse() # pause before closing


df_inventario.to_excel('Reporte.xlsx', sheet_name='Mix')
reporte = openpyxl.load_workbook(filename='Reporte.xlsx')
worksheet = reporte['Mix']
kpi_text = worksheet.cell(row=(len(l_inv) + 3), column=1, value='$/ton')
kpi_data = worksheet.cell(row=(len(l_inv) + 3), column=2, value=Scrap_kpi)
reporte.save('C:\\Users\\Rodrigo\\Documents\\SIDER\\Scrap Optimization\\Reportes\\Reporte.xlsx')
"""
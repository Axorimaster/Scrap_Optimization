import pandas as pd
import Simplex
from tabulate import tabulate


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
    df_inventario['Volumen Cesta'] = df_inventario['Carga'] / df_inventario['Densidad']


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

        l_cvalue.append(sum/35)
        print("Contenido de", col, ":", sum/35)

    return l_col,l_cvalue


##Input de datos operativos
prod_mes = int(input("Ingrese la producción mensual en toneladas: "))
carga = 35.0
vol_cesta = 28*0.95
num_cesta = int(input("Ingrese el número máximo de cestas: "))

##Setear display del df
pd.set_option("display.max_rows", None, "display.max_columns", None, "display.max_colwidth", 200)



##Lectura hoja de cálculo mix
df_inventario = pd.read_excel("Mix.xlsx", index_col=None, sheet_name='Inventario', usecols="A:F", nrows=8)
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

##Cálculo del número de cestas
Scrap_vol = df_inventario['Volumen Cesta'].sum()
num_load = Scrap_vol/vol_cesta
print("Número de cestas: ", num_load)

##Cálculo del costo por tonelada de chatarra
Scrap_kpi = sum(L_costo) / sum(L_uso)
print("Costo por tonelada de chatarra: ", Scrap_kpi)


print(tabulate(df_inventario, headers='keys', tablefmt='psql'))


##Cálculo de contaminantes
L_cont,L_cvalue = calc_contaminantes(df_comp,df_inventario)


"""
df_inventario.to_excel('Reporte.xlsx', sheet_name='Mix')
reporte = openpyxl.load_workbook(filename='Reporte.xlsx')
worksheet = reporte['Mix']
kpi_text = worksheet.cell(row=(len(l_inv) + 3), column=1, value='$/ton')
kpi_data = worksheet.cell(row=(len(l_inv) + 3), column=2, value=Scrap_kpi)
reporte.save('C:\\Users\\Rodrigo\\Documents\\SIDER\\Scrap Optimization\\Reportes\\Reporte.xlsx')
"""
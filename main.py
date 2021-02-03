import pandas as pd
import Simplex
import Obj


def round_col(df, nom_col):

    l_round = df[nom_col].tolist()
    l = [round(num,0) for num in l_round ]
    df.drop(columns=[nom_col])
    df[nom_col] = l


def calc_mix(prod_mes):
    df_inventario['Mix'] = (df_inventario['Uso'] / prod_mes)*100
    round_col(df_inventario, 'Mix')
    df_inventario['Costo'] = df_inventario['Uso'] * df_inventario['Precio']
    df_inventario['Carga'] = (df_inventario['Mix'] * carga)/100
    df_inventario['Volumen Cesta'] = df_inventario['Carga'] / df_inventario['Densidad']


def inv_lifeline(x, ll):
    return x - (x * ll)


##Input de datos operativos
prod_mes = int(input("Ingrese la producción mensual en toneladas: "))
carga = int(input("Ingrese las toneladas de carga del HE: "))
vol_cesta = int(input("Ingrese el volumen de carga de la cesta: "))
num_cesta = int(input("Ingrese el número máximo de cestas: "))

##Setear display del df
pd.set_option("display.max_rows", None, "display.max_columns", None)

##Lectura hoja de cálculo mix
df_inventario = pd.read_excel("Mix.xlsx", index_col=None, sheet_name='Inventario', usecols="A:E", nrows=8)
df_constrains = pd.read_excel('Mix.xlsx', sheet_name='Constrains', index_col=None, usecols='A:C', nrows=8)


##Formateo de datos de precios e inventarios para Simplex
l_precios = df_inventario['Precio'].tolist()
l_precios.append(0)
l_inv = df_inventario['Inventario'].tolist()
l_lifeline = df_inventario['Lifeline'].tolist()
l_density = df_inventario['Densidad'].tolist()
l_inv_ll = list(map(lambda x, y: x - (x * y), l_inv, l_lifeline))



##Minimización del costo mediante Simplex
L_uso = list(Simplex.minimize(8, 19, l_precios, l_inv_ll, prod_mes, l_density, num_cesta, vol_cesta, carga).values())
Cost = L_uso.pop(6)
df_inventario['Uso'] = L_uso

calc_mix(prod_mes)

Scrap_vol = df_inventario['Volumen Cesta'].sum()
num_load = Scrap_vol/vol_cesta
print("Número de cestas: ", num_load)


Scrap_kpi = Cost / prod_mes
print("Costo por tonelada de chatarra: ", Scrap_kpi)


print(df_inventario)
"""
df_inventario.to_excel('Reporte.xlsx', sheet_name='Mix')
reporte = openpyxl.load_workbook(filename='Reporte.xlsx')
worksheet = reporte['Mix']
kpi_text = worksheet.cell(row=(len(l_inv) + 3), column=1, value='$/ton')
kpi_data = worksheet.cell(row=(len(l_inv) + 3), column=2, value=Scrap_kpi)
reporte.save('C:\\Users\\Rodrigo\\Documents\\SIDER\\Scrap Optimization\\Reportes\\Reporte.xlsx')
"""
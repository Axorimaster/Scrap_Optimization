import pandas as pd
import Simplex
from tabulate import tabulate
import openpyxl as opy


def round_col(df, nom_col, r):

    l_round = df[nom_col].tolist()
    l = [round(num,r) for num in l_round ]
    df.drop(columns=[nom_col])
    df[nom_col] = l


def calc_mix():

    total_scrap = sum(df_inventario['Uso'].tolist())
    df_inventario['Mix'] = (df_inventario['Uso'] / total_scrap)*100
    df_inventario['Costo'] = (df_inventario['Uso'] * df_inventario['Precio'])/1000000
    df_inventario['Carga'] = (df_inventario['Mix'] * carga_eaf) / 100
    df_inventario['Volumen'] = df_inventario['Carga'] / df_inventario['Densidad']

    round_col(df_inventario, 'Volumen',0)
    round_col(df_inventario, 'Mix', 2)
    round_col(df_inventario, 'Carga', 0)
    round_col(df_inventario, 'Costo', 3)


def calc_contaminantes():
    l_carga = df_inventario['Carga'].tolist()
    l_col = list(df_comp.columns)
    l_col.pop(0)
    l_cvalue = []
    for col in l_col:
        sum = 0
        l_cont = df_comp[col].tolist()
        for x in range(len(l_carga)):
            sum = sum + l_carga[x]*l_cont[x]

        l_cvalue.append(round(sum/35,3))
        print("Contenido de", col, ":", round(sum/carga_eaf,3))

    df_cont = pd.DataFrame(list(zip(l_cvalue)), columns=['Valor'], index=l_col )
    return(df_cont)


def calc_cesta(inventario):

    inventario['Index'] = [0,1,2,3,4,5,6,7]

    df_base_scrap = inventario[inventario.Densidad <= 0.5]
    df_sdensidadmax = inventario.sort_values(by=['Potencia'], ascending=False)

    l_rho = df_sdensidadmax['Densidad'].tolist()

    l_scrap = list(inventario.index.values)
    l_base_scrap = list(df_base_scrap.index.values)
    l_sorted_scrap = list(df_sdensidadmax.index.values)

    l_sorted_peso = df_sdensidadmax['Carga'].tolist()
    l_peso = inventario['Carga'].tolist()

    liv_min = 2
    liv_max = 4
    ciz_min = 3
    ciz_max = 5

    for cesta in range(num_cesta):

        l_cesta = []
        x = 0
        nom_ces = str("Cesta N°"+str(cesta+1))


        for scrap in l_sorted_scrap:

            usindex = l_scrap.index(scrap)


            if scrap not in l_base_scrap:



                if l_sorted_peso[x] <= carga_cesta-sum(l_cesta):

                    scrap_load = l_peso[usindex]
                    l_sorted_peso[x] = l_sorted_peso[x]-scrap_load
                    l_peso[usindex] = l_peso[usindex]-scrap_load
                    l_cesta.append(scrap_load)




                else:

                    scrap_load = carga_cesta - sum(l_cesta)
                    l_sorted_peso[x] = l_sorted_peso[x] - scrap_load
                    l_peso[usindex] = l_peso[usindex] - scrap_load
                    l_cesta.append(scrap_load)



            else:

                if cesta+1 == num_cesta:

                    scrap_load = l_peso[usindex]
                    l_sorted_peso[x] = l_sorted_peso[x] - scrap_load
                    l_peso[usindex] = l_peso[usindex] - scrap_load
                    l_cesta.append(scrap_load)


                else:



                    if scrap == 'LIVIANA':

                        scrap_load = liv_min
                        l_peso[usindex] = l_peso[usindex] - scrap_load
                        l_sorted_peso[x] = l_sorted_peso[x] - scrap_load
                        l_cesta.append(scrap_load)

                    else:

                        scrap_load = ciz_min
                        l_sorted_peso[x] = l_sorted_peso[x] - scrap_load
                        l_peso[usindex] = l_peso[usindex] - scrap_load
                        l_cesta.append(scrap_load)



            x = x+1

        volumen = 0

        for i in range(len(l_cesta)):
            volumen = volumen+(l_cesta[i] / l_rho[i])
            volumen = round(volumen,1)

        print("Volumen", nom_ces, ": ", volumen)
        df_sdensidadmax[nom_ces] = l_cesta
        round_col(df_sdensidadmax,nom_ces,0)

    df = df_sdensidadmax.sort_values(by=['Index'])
    res = df.drop(columns=['Index'])
    return res


def calc_potencia(inventario):
    l_potencia = ((inventario['Potencia']*inventario['Mix'])/100).tolist()
    rend_ef = sum(((inventario['Rendimiento'] * inventario['Mix']) / 100).tolist())
    p_scrap = sum(l_potencia)
    p_escoria = (30*p_scrap)/455
    p_total = p_escoria + p_scrap
    e_quim = 3800
    e_el = (carga_eaf*p_total)-e_quim
    pot = 29500
    p_on = 60/(pot/e_el)
    p_off = 11
    ttt = p_on + p_off
    carga_ef = carga_eaf*rend_ef*0.98
    P = (carga_ef/ttt)*60

    return(round(P,1),round(ttt,1),round(p_on,1),round(p_total),round(e_el))


##Input de datos operativos
prod_mes = int(input("Ingrese la producción mensual en toneladas: "))
carga_eaf = 35.0
vol_cesta = 28*0.95
carga_cesta = 15
epsilon = 0
num_cesta = int(input("Ingrese el número máximo de cestas: "))

##Setear display del df
pd.set_option("display.max_rows", None, "display.max_columns", None, "display.max_colwidth", 200)


##Lectura hoja de cálculo mix
df_inventario = pd.read_excel("Mix.xlsx", index_col=0, sheet_name='Inventario', usecols="A:G", nrows=8)
df_comp = pd.read_excel('Mix.xlsx', sheet_name='Composicion', index_col=None, usecols='A:J', nrows=8)
df_res = (pd.read_excel('Mix.xlsx', sheet_name='Composicion', index_col=None, usecols='A:B', nrows=9, skiprows=11)).dropna()

##Formateo de datos de precios e inventarios para Simplex

l_precios = df_inventario['Precio'].tolist()
l_precios.append(0)
l_inv = df_inventario['Inventario'].tolist()
l_lifeline = df_inventario['Lifeline'].tolist()
l_density = df_inventario['Densidad'].tolist()
l_rend = df_inventario['Rendimiento'].tolist()
l_inv_ll = list(map(lambda x, y: x - (x * y), l_inv, l_lifeline))
l_res_max = df_res['Max'].tolist()
l_res_nombre = df_res['Elementos'].tolist()


##Minimización del costo mediante Simplex
sol_dir = Simplex.minimize(8, 23, l_precios, l_inv_ll, prod_mes, l_density, num_cesta, vol_cesta, carga_eaf, l_rend, df_comp, df_res, epsilon)
if 'min' in sol_dir:
    sol_dir.pop('min')

L_uso = list(sol_dir.values())
df_inventario['Uso'] = L_uso
round_col(df_inventario, 'Uso',0)

##Formateo de dataframe inventario
calc_mix(prod_mes)
produccion,ttt, power_on, potencia_unit, energia_el = calc_potencia(df_inventario)
L_costo = df_inventario['Costo'].tolist()


print("------------------RESULTADOS------------------")

##Cálculo del número de cestas
Scrap_vol = df_inventario['Volumen'].sum()
num_load = Scrap_vol/vol_cesta


##Cálculo del costo por tonelada de chatarra
Scrap_kpi = round((sum(L_costo)*1000000) / sum(L_uso),2)
l_mix = df_inventario['Mix'].tolist()
sum_rho = 0
for x in range(len(l_mix)):
    sum_rho = sum_rho + ((l_mix[x]/100)*l_density[x])

rho_cesta = round(sum_rho,2)

print("Costo por tonelada de chatarra:", Scrap_kpi,2,"$/ton")
print("Potencia requerida:",potencia_unit,"kWh/ton")
print("Energía eléctrica consumida:", energia_el,"kWh")
print("Power On:",power_on,"min")
print("Tap to tap:", ttt, "min")
print("Productividad:", produccion, "ton/h")
print("Densidad ponderada:",rho_cesta,"ton/m3")

##Cálculo de contaminantes
print("-----------------CONTAMINANTES----------------")
df_contaminantes = calc_contaminantes()

##Carga de cestas
print("--------------------CESTAS--------------------")
L_carga = df_inventario['Carga'].tolist()
df_res = calc_cesta(df_inventario)
pd.set_option('display.float_format', str)
print(tabulate(df_res, headers='keys', tablefmt='psql'))

"""
win = GraphWin(width=800, height=800) # create a window
win.setCoords(0, 0, 10, 10) # set the coordinates of the window; bottom left is (0, 0) and top right is (10, 10)
mySquare = Rectangle(Point(1, 1), Point(9, 9)) # create a rectangle from (1, 1) to (9, 9)
mySquare.draw(win) # draw it to the window
win.getMouse() # pause before closing
"""

l_indicadores = ["Costo","Potencia","E_el","P_on","TTT","Produccion", "Densidad"]
l_ind_val = [Scrap_kpi,potencia_unit,energia_el,power_on,ttt,produccion,rho_cesta]
l_ind_si = ["$/ton","kWh/ton","kWh","min","min","ton/h","ton/m3"]

df_indicadores = pd.DataFrame(list(zip(l_ind_val,l_ind_si)),columns=['Valores','Unidades'],index=l_indicadores)



workbook = opy.Workbook()
worksheet = workbook.active
worksheet.title = 'Reporte'
worksheet['A1'] = "REPORTE DE SIMULACIÓN"
worksheet.column_dimensions['A'].width =20
workbook.save('Reporte.xlsx')

book = opy.load_workbook('Reporte.xlsx')
writer = pd.ExcelWriter('Reporte.xlsx', engine='openpyxl')
writer.book = book

writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

df_indicadores.to_excel(writer, 'Reporte', startrow= 2)
df_res.to_excel(writer,'Reporte', startrow=11)
df_contaminantes.to_excel(writer, 'Reporte', startrow= 21)
worksheet['A13'] = "Concentración de contaminantes"



writer.save()
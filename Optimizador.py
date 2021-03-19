import pandas as pd
import Simplex
from tabulate import tabulate
import openpyxl as opy
from openpyxl.styles import Alignment
import math
import string
import numpy as np


def round_col(df, nom_col, r):
    l_round = df[nom_col].tolist()
    lista = []
    for val in l_round:
        if type(val) == str:
            lista.append(val)
        else:
            lista.append(round(val,r))

    df.drop(columns=[nom_col], inplace=True)
    df[nom_col] = lista


def calc_mix(n_coladas):

    total_scrap = sum(df_inventario['Carga'].tolist())
    df_inventario['Mix'] = (df_inventario['Carga'] / total_scrap) * 100
    df_inventario['Costo'] = ((df_inventario['Carga'] * df_inventario['Precio']) * n_coladas) / 1000000
    df_inventario['Uso'] = (df_inventario['Carga']) * n_coladas
    df_inventario['Volumen'] = df_inventario['Carga'] / df_inventario['Densidad']

    round_col(df_inventario, 'Volumen', 1)
    round_col(df_inventario, 'Mix', 2)
    round_col(df_inventario, 'Costo', 3)
    round_col(df_inventario, 'Uso', 0)


def calc_nconstrains():

    residual_cons = len(df_residual)
    var_const = 2*len(df_inventario)
    prod_constrain = 2
    vol_constrain = 1
    n_constrain = residual_cons+prod_constrain+var_const+vol_constrain

    return n_constrain


def calc_contaminantes(carga_eaf):

    l_carga = df_inventario['Carga'].tolist()
    l_col = list(df_comp.columns)

    l_cvalue = []
    for col in l_col:
        suma = 0
        l_cont = df_comp[col].tolist()
        for x in range(len(l_carga)):
            suma = suma + l_carga[x] * l_cont[x]

        l_cvalue.append(round(suma / 35, 3))
        print("Contenido de", col, ":", round(suma / carga_eaf, 6))

    df_cont = pd.DataFrame(list(zip(l_cvalue)), columns=['Valor'], index=l_col)
    return df_cont


def complete_cesta(l_sorted_scrap, l_scrap, l_cesta, l_peso, l_vol_cesta, l_rho, l_sorted_peso, n_base):

    x = l_sorted_scrap.index(n_base)
    usindex = l_scrap.index(n_base)

    while sum(l_cesta) < 15 and l_peso[usindex] > 0 and (sum(l_vol_cesta) + (1 / l_rho[x])) < 26.6:
        l_peso[usindex] = l_peso[usindex] - 1
        l_sorted_peso[x] = l_sorted_peso[x] - 1
        l_cesta[x] = l_cesta[x] + 1
        l_vol_cesta[x] = l_vol_cesta[x] + 1 / l_rho[x]


def calc_cesta(num_cestas, carga_cesta, vol_cesta, n_var):

    def fill_basket():

        x = 0
        l_cesta = []
        l_vol_cesta = []

        for scrap in l_sorted_scrap:

            usindex = l_scrap.index(scrap)

            if l_sorted_peso[x] <= 0:
                scrap_load = 0

            elif scrap not in l_base_scrap:

                if l_sorted_peso[x] <= carga_cesta - sum(l_cesta) and ((l_sorted_peso[x]/l_rho_sorted[x]) <= vol_cesta - sum(l_vol_cesta)):

                    scrap_load = l_peso[usindex]

                else:

                    scrap_load = carga_cesta - sum(l_cesta)

            else:

                if cesta + 1 == num_cestas:

                    scrap_load = l_peso[usindex]

                else:

                    if scrap == 'LIVIANA':

                        if l_sorted_peso[x] < liv_min:

                            scrap_load = l_sorted_peso[x]

                        else:

                            scrap_load = liv_min

                    else:

                        if l_sorted_peso[x] < ciz_min:

                            scrap_load = l_sorted_peso[x]

                        else:
                            if ciz_min <= carga_cesta-sum(l_cesta):
                                scrap_load = ciz_min
                            else:
                                scrap_load = carga_cesta-sum(l_cesta)

            scrap_load = round(scrap_load, 0)
            l_sorted_peso[x] = l_sorted_peso[x] - scrap_load
            l_peso[usindex] = l_peso[usindex] - scrap_load
            l_cesta.append(scrap_load)
            l_vol_cesta.append(scrap_load / l_rho_sorted[x])

            x = x + 1

        return l_cesta, l_vol_cesta

    l_index = []
    for x in range(n_var):
        l_index.append(x)
    df_inventario['Index'] = l_index

    l_nom_cestas = []
    l_peso = df_inventario['Carga'].tolist()
    df_base_scrap = df_inventario[df_inventario.Densidad <= 0.5]
    l_scrap = list(df_inventario.index.values)
    df_inventario.sort_values(by=['Potencia'], ascending=False,inplace=True)

    l_rho_sorted = df_inventario['Densidad'].tolist()
    l_pot_sorted = df_inventario['Potencia'].tolist()

    l_base_scrap = list(df_base_scrap.index.values)
    l_sorted_scrap = list(df_inventario.index.values)

    l_sorted_peso = df_inventario['Carga'].tolist()

    liv_min = 2
    ciz_min = 3

    l_kpi_cestas = []

    for cesta in range(num_cestas):

        nom_ces = str("Cesta N°" + str(cesta + 1))

        l_cesta, l_vol_cesta = fill_basket()

        n_base = 'CIZALLA'
        complete_cesta(l_sorted_scrap, l_scrap, l_cesta, l_peso, l_vol_cesta, l_rho_sorted, l_sorted_peso, n_base)
        n_base = 'LIVIANA'
        complete_cesta(l_sorted_scrap, l_scrap, l_cesta, l_peso, l_vol_cesta, l_rho_sorted, l_sorted_peso, n_base)

        df_inventario[nom_ces] = l_cesta
        round_col(df_inventario, nom_ces, 0)

        l_nom_cestas.append(nom_ces)
        l_kpi = kpi_cestas(df_inventario[nom_ces].tolist(), l_rho_sorted,l_pot_sorted)

        l_kpi_cestas.append(l_kpi)

    l_col = ['Peso [ton]', 'Volumen [m3]', 'Densidad [ton/m3]', 'Energía [kWh]']
    df_cestas = pd.DataFrame(l_kpi_cestas, columns=l_col, index=l_nom_cestas)

    for x in l_col:
        round_col(df_cestas,x,2)

    df_inventario.sort_values(by=['Index'], inplace=True)
    df_inventario.drop(columns=['Index'], inplace=True)

    return (df_cestas)


def calc_potencia(inventario, carga_eaf):
    l_potencia_unit = ((inventario['Potencia'] * inventario['Mix'])/100).tolist()
    rend_ef = sum(((inventario['Rendimiento'] * inventario['Mix'])/100).tolist())

    p_scrap = sum(l_potencia_unit)
    p_escoria = (30 * p_scrap) / 455
    p_total = p_escoria + p_scrap
    e_quim = 3800
    e_el = (carga_eaf * p_total) - e_quim
    pot = 29500
    p_on = 60 / (pot / e_el)
    p_off = 10.5
    ttt = p_on + p_off
    carga_ef = carga_eaf * rend_ef * 0.98
    p = (carga_ef / ttt) * 60

    return round(p, 1), round(ttt, 1), round(p_on, 1), round(p_total), round(e_el)


def gen_report(prod_mes, n_coladas, Scrap_kpi, potencia_unit, energia_el, power_on, ttt, steel, rho_cesta, num_cestas, n_var, df_contaminantes, df_cestas):

    l_alphabet = list(string.ascii_uppercase)
    l_indicadores = ['Acero Sólido', 'N° Coladas', "Costo", "Potencia", "E_el", "P_on", "TTT", "Produccion", "Densidad"]
    l_ind_val = [prod_mes,round(n_coladas, 0), round(Scrap_kpi, 2), potencia_unit, energia_el, power_on, ttt, steel,
                 rho_cesta]
    l_ind_si = ['ton/mes','col/mes', "$/ton", "kWh/ton", "kWh", "min", "min", "ton/h", "ton/m3"]

    df_indicadores = pd.DataFrame(list(zip(l_ind_val, l_ind_si)), columns=['Valores', 'Unidades'], index=l_indicadores)

    l_columns =  ['Precio [$/ton]', 'Densidad [ton/m3]', 'Inventario [ton/mes]', 'Rendimiento',
                      'Energía [kWh/ton]', 'Carga [ton]', 'Volumen [m3]', 'Mix', 'Costo [MMUSD]', 'Uso [ton]']

    for x in range(num_cestas):

        nom_cesta = "Cesta N°"+ str(x+1) +" [ton]"
        l_columns.append(nom_cesta)

    df_inventario.columns = l_columns

    workbook = opy.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Reporte'
    worksheet['A1'] = "REPORTE DE SIMULACIÓN"
    worksheet.column_dimensions['A'].width = 20

    worksheet['A37'] = "CONTRACIÓN DE CONTAMINANTES"
    worksheet['A25'] = "DATOS CESTAS"

    for x in range(n_var):
        worksheet.column_dimensions[l_alphabet[x+1]].width=12
    worksheet.row_dimensions[15].height = 30

    worksheet.sheet_view.showGridLines = False
    workbook.save('Reportes/Reporte.xlsx')

    book = opy.load_workbook('Reportes/Reporte.xlsx')
    writer = pd.ExcelWriter('Reportes/Reporte.xlsx', engine='openpyxl')
    writer.book = book

    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    df_indicadores.to_excel(writer, 'Reporte', startrow=2)
    df_inventario.to_excel(writer, 'Reporte', startrow=14)
    df_cestas.to_excel(writer, 'Reporte', startrow=25)
    df_contaminantes.to_excel(writer, 'Reporte', startrow=37)
    writer.save()

    workbook = opy.load_workbook('Reportes/Reporte.xlsx')
    worksheet = workbook.active

    for i in range(num_cestas + 5):
        letra = l_alphabet[i + 6]
        num_celda = str(16+len(df_inventario))
        nom_celda = str(letra+num_celda)
        num_fin_suma = str(15+len(df_inventario))
        comando = str("=SUM("+letra+"16:"+letra+num_fin_suma+")")
        worksheet[nom_celda] = comando


    for j in range(len(l_columns)):
        letra = l_alphabet[j+1]
        nom_celda = str(letra+"15")
        worksheet[nom_celda].alignment = Alignment(wrap_text=True, vertical='top', horizontal='center')

    for j in range(6):
        letra = l_alphabet[j+1]
        nom_celda = str(letra+"26")
        worksheet[nom_celda].alignment = Alignment(wrap_text=True, vertical='top', horizontal='center')

    workbook.save('Reportes/Reporte.xlsx')


def check_inv(l_inv_ll, l_rend):

    prod_mes = int(input("Ingrese la producción mensual en toneladas: "))
    inv_total = [a * b for a, b in zip(l_inv_ll, l_rend)]

    if sum(inv_total) < prod_mes:

        prod_max = sum(inv_total)
        prod_max = round((prod_max-500)/ 10000, 2) * 10000
        print("Inventario insuficiente. El mix se prepará para la mayor producción posible:", prod_max)
        return prod_max

    else:

        print("Inventario correcto.")
        return prod_mes


def check_carga(l_carga, carga_eaf):

    l_carga_round = [round(c,0) for c in l_carga]
    l_dec = []

    if sum(l_carga_round) != carga_eaf:

        print("Normalizar carga.")

        if sum(l_carga_round) < carga_eaf:

            for x in l_carga:
                decimal = math.modf(x)

                if decimal[0] <= 0.5 and abs(decimal[0] > 0.01):
                    l_dec.append(abs(decimal[0]))

                else:
                    l_dec.append(0)

            max_dec = max(l_dec)
            indx = l_dec.index(max_dec)
            l_carga_round[indx] = l_carga_round[indx] + 1

        elif sum(l_carga_round) > carga_eaf:
            for x in l_carga:

                decimal = math.modf(x)

                if decimal[0] >= 0.5 and abs(decimal[0] > 0.01):
                    l_dec.append(abs(decimal[0]))
                else:
                    l_dec.append(1)

            min_dec = min(l_dec)
            indx = l_dec.index(min_dec)
            l_carga_round[indx] = l_carga_round[indx] - 1

    df_inventario['Carga'] = l_carga_round
    print("Carga normalizada.")


def kpi_cestas(l_cesta,l_rho_sorted, l_pot_sorted):

    peso_cesta = (sum(l_cesta))
    volumen_cesta = sum([a/b for a,b in zip(l_cesta,l_rho_sorted)])
    if volumen_cesta == 0:
        densidad_cesta = 0
    else:
        densidad_cesta = peso_cesta/volumen_cesta
    energia_cesta = sum([a*b for a,b in zip(l_cesta,l_pot_sorted)])

    l_kpi = [peso_cesta,volumen_cesta,densidad_cesta,energia_cesta]

    return l_kpi


def calc_melting(df_cestas, num_cestas, df_inventario, rho_mix):

    l_vol = df_cestas['Volumen [m3]']
    l_densidad = df_cestas['Densidad [ton/m3]']
    l_peso = df_cestas['Peso [ton]']
    l_energia = df_cestas['Energía [kWh]']

    l_potencia = df_inventario['Potencia']
    l_carga = df_inventario['Carga']
    e_mix = sum([a * b for a, b in zip(l_potencia, l_carga)])

    l_melt_load = []
    l_vol_req = []
    l_energia_req =[]
    l_pon = []
    l_e_quim_esp = []
    l_e_quim = []
    l_flux_o2 = []
    l_el_esp = []
    l_el = []

    melting_factor = 0.70
    vol_factor = 0.05
    pot_cesta = 28.16
    ox_flux = 65
    e_reaccion = 4.4
    kt_factor = 0.70

    ox_flux_afino = 70
    pot_afino = 34
    e_reaccion_afino = 8.7

    for x in range(num_cestas):

        rho_cesta = l_densidad[x]
        peso_cesta = l_peso[x]

        if x+1 == num_cestas:

            vol_req = l_vol[x]*(1+vol_factor)
            melt_load = vol_req * rho_cesta

        else:

            vol_req = l_vol[x+1]*(1+vol_factor)
            melt_load = vol_req*rho_cesta



        if melt_load > peso_cesta:
            l_melt_load.append(peso_cesta)
        else:
            l_melt_load.append(melt_load)

        energia_req = (l_melt_load[x] * l_energia[x] * melting_factor) / peso_cesta
        l_energia_req.append(energia_req)

        l_vol_req.append(vol_req)

        q_factor = ox_flux*kt_factor*e_reaccion
        el_factor = (pot_cesta/60)*1000

        p_on_cesta = energia_req / (q_factor + el_factor)

        l_pon.append(p_on_cesta)

        ox_cesta = p_on_cesta * ox_flux
        e_quim_cesta = (ox_cesta * kt_factor * e_reaccion)
        e_quim_cesta_esp = e_quim_cesta/peso_cesta

        l_flux_o2.append(ox_cesta)
        l_e_quim_esp.append(e_quim_cesta_esp)
        l_e_quim.append(e_quim_cesta)

        e_el_esp = (energia_req - e_quim_cesta) / peso_cesta
        l_el_esp.append(e_el_esp)
        l_el.append(energia_req - e_quim_cesta)

    e_melting = sum(l_energia_req)
    e_afino = e_mix - e_melting
    t_afino = e_afino/((ox_flux_afino*kt_factor*e_reaccion_afino)+((pot_afino/60)*1000))
    e_quim_esp_afino = (ox_flux_afino*kt_factor*e_reaccion_afino*t_afino)/sum(l_peso)
    e_quim_afino = e_quim_esp_afino*sum(l_peso)
    e_el_esp_afino = (e_afino-e_quim_esp_afino)/sum(l_peso)
    e_el_afino = e_el_esp_afino*sum(l_peso)
    o2_afino = t_afino * ox_flux_afino

    e_quim_mix = sum(l_e_quim)
    e_el_mix = sum(l_el)

    df_cestas['Volumen requerido [m3]'] = l_vol_req
    df_cestas['Peso a fundir [ton]'] = l_melt_load
    df_cestas['Energía requerida [kWh]'] = l_energia_req
    df_cestas['Energía química específica [kWh/ton]'] = l_e_quim_esp
    df_cestas['Energía eléctrica específica [kWh/ton]'] = l_el_esp
    df_cestas['Power On [min]'] = l_pon
    df_cestas['Flujo de O2 [m3]'] = l_flux_o2


    round_col(df_cestas, 'Volumen requerido [m3]', 2)
    round_col(df_cestas, 'Peso a fundir [ton]', 2)
    round_col(df_cestas, 'Energía requerida [kWh]', 0)
    round_col(df_cestas, 'Energía química específica [kWh/ton]', 1)
    round_col(df_cestas, 'Energía eléctrica específica [kWh/ton]', 1)
    round_col(df_cestas, 'Power On [min]', 1)
    round_col(df_cestas, 'Flujo de O2 [m3]', 2)

    df_cestas.drop('Energía [kWh]', axis=1, inplace=True)
    df_cestas = df_cestas.transpose()

    e_quim_esp_total = (e_quim_afino+e_quim_mix)/sum(l_peso)
    e_el_total = (e_el_afino+e_el_mix)/sum(l_peso)
    ox_total = o2_afino + sum(l_flux_o2)
    p_on_total = sum(l_pon) + t_afino

    l_afino = [sum(l_peso), " ", rho_mix, " ", " ", e_afino, e_quim_esp_afino, e_el_esp_afino, t_afino, o2_afino]
    l_total = [" ", " ", " ", " ", " ", e_mix, e_quim_esp_total, e_el_total, p_on_total, ox_total]
    df_cestas['Afino'] = l_afino
    round_col(df_cestas, 'Afino', 2)
    df_cestas['Total'] = l_total
    round_col(df_cestas, 'Total', 2)

    print(tabulate(df_cestas, headers='keys', tablefmt='psql'))
    return(df_cestas)


def main(df_inventario, df_comp, df_residual):

    carga_eaf = 35.0
    vol_cesta = 28 * 0.95
    carga_cesta = 15
    epsilon = 0
    prod_unit = 31.2
    hot_heel = 6
    eaf_vol = 30
    rho_steel = 7

    num_cestas = int(input("Ingrese el número máximo de cestas: "))

    ##Setear display del df
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.max_colwidth", 200)

    ##Lectura hoja de cálculo mix
    n_cons = calc_nconstrains()
    n_var = len(df_inventario)

    ##Formateo de datos de precios e inventarios para Simplex

    l_precios = df_inventario['Precio'].tolist()
    l_precios.append(0)
    l_inv = df_inventario['Inventario'].tolist()
    l_lifeline = df_inventario['Lifeline'].tolist()
    l_density = df_inventario['Densidad'].tolist()
    l_rend = df_inventario['Rendimiento'].tolist()
    l_inv_ll = list(map(lambda x, y: x - (x * y), l_inv, l_lifeline))

    prod_mes = check_inv(l_inv_ll, l_rend)
    n_coladas = prod_mes / prod_unit

    ##Minimización del costo mediante Simplex
    err = True

    while err:

        sol_dir, err = Simplex.minimize(n_var, n_cons, l_precios, l_inv_ll, l_density, num_cestas, vol_cesta, carga_eaf,
                                        df_comp, df_residual, epsilon, n_coladas)
        if err:

            print("Error en el número de cestas. Se requiere una cesta adicional.")
            num_cestas = num_cestas + 1
            print("Número de cestas:", num_cestas)

        else:
            print("Número de cestas correcto.")
            err = False

    sol_dir, err = Simplex.minimize(n_var, n_cons, l_precios, l_inv_ll, l_density, num_cestas, vol_cesta, carga_eaf, df_comp,
                                    df_residual, epsilon, n_coladas)
    if 'min' in sol_dir:
        sol_dir.pop('min')

    l_carga = list(sol_dir.values())
    df_inventario['Carga'] = l_carga
    check_carga(l_carga, carga_eaf)

    ##Formateo de dataframe inventario
    calc_mix(n_coladas)
    steel, ttt, power_on, potencia_unit, energia_el = calc_potencia(df_inventario,carga_eaf)
    l_costo = df_inventario['Costo'].tolist() * 1000000

    print("------------------RESULTADOS------------------")

    ##Cálculo del número de cestas
    Scrap_vol = df_inventario['Volumen'].sum()
    num_load = Scrap_vol / vol_cesta

    ##Cálculo del costo por tonelada de chatarra
    Scrap_kpi = sum(l_costo) / prod_mes
    l_mix = df_inventario['Mix'].tolist()
    sum_rho = 0

    for x in range(len(l_mix)):
        sum_rho = sum_rho + ((l_mix[x] / 100) * l_density[x])

    rho_mix = round(sum_rho, 2)

    print("Num cestas:", num_load)
    print("N° de coladas:", round(n_coladas, 0))
    print("Costo chatarra por tonelada de acero:", round(Scrap_kpi, 2), "$/ton")
    print("Potencia requerida:", potencia_unit, "kWh/ton")
    print("Energía eléctrica consumida:", energia_el, "kWh")
    print("Power On:", power_on, "min")
    print("Tap to tap:", ttt, "min")
    print("Productividad:", steel, "ton/h")
    print("Densidad ponderada:", rho_mix, "ton/m3")
    df_inventario.drop(columns=['Lifeline'], inplace=True)

    ##Cálculo de contaminantes
    print("-----------------CONTAMINANTES----------------")
    df_contaminantes = calc_contaminantes(carga_eaf)

    ##Carga de cestas
    print("--------------------CESTAS--------------------")
    df_cestas = calc_cesta(num_cestas, carga_cesta, vol_cesta, n_var)

    df_cestas = calc_melting(df_cestas,num_cestas, df_inventario, rho_mix)



    report_ans = input("¿Desea generar un reporte? [Y/N] ")

    if report_ans == "Y":
        gen_report(prod_mes, n_coladas, Scrap_kpi, potencia_unit, energia_el, power_on, ttt, steel, rho_mix, num_cestas, n_var, df_contaminantes, df_cestas)

    return df_inventario


df_mix = pd.read_excel("Mix.xlsx", index_col=0, sheet_name='Inventario', usecols="A:P", nrows=8)
df_mix = df_mix[df_mix.Inventario != 0]
df_mix = np.split(df_mix, [6], axis=1)
df_inventario = df_mix[0]
df_comp = df_mix[1]

##df_comp = pd.read_excel('Mix.xlsx', sheet_name='Composicion', index_col=0, usecols='A:J', nrows=8)

df_residual = (pd.read_excel('Mix.xlsx', sheet_name='Composicion', index_col=None, usecols='A:B', nrows=9, skiprows=11)).dropna()

resultado = main(df_inventario,df_comp,df_residual)
print(tabulate(resultado, headers='keys', tablefmt='psql'))
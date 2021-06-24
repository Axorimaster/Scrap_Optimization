import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar


def main(hp_i, hp_f):
    l_horas = ['00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00',
               '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
               '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00',
               '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30',
               '22:00', '22:30', '23:00', '23:30']
    headers = {'User-Agent': 'Mozilla/5.0'}

    fecha_hoy = datetime.today()
    f_hoy_str = fecha_hoy.strftime('%Y/%m/%d')
    fecha_mes_i = datetime(fecha_hoy.year, fecha_hoy.month, 1)
    fecha_mes_i_str = str(fecha_mes_i.strftime('%d/%m/%Y'))

    d_mes = int(calendar.monthrange(year=int(fecha_hoy.year), month=int(fecha_hoy.month))[1])

    fecha_mes_f = fecha_mes_i + timedelta(days=d_mes - 1)
    fecha_mes_f_str = str(fecha_mes_f.strftime('%d/%m/%Y'))

    try:
        r = requests.post('https://www.coes.org.pe/Portal/portalinformacion/Demanda',
                          data=dict(fechaInicial=fecha_mes_i_str, fechaFinal=fecha_mes_f_str), headers=headers,
                          verify=False)

    except:
        r = requests.post('https://www.coes.org.pe/Portal/portalinformacion/Demanda',
                          data=dict(fechaInicial=fecha_mes_i_str, fechaFinal=fecha_mes_f_str), headers=headers,
                          verify='CERT\\coes.p7b')
    data = r.json()

    l_data = data['Data']

    l_fecha = []
    l_hora = []
    l_ejec = []
    l_pdia = []
    l_psemana = []

    for dire in l_data:

        f = dire['Fecha']
        date, h = f.split()
        l_fecha.append(date)
        l_hora.append(h)
        ej = dire['ValorEjecutado']
        l_ejec.append(ej)
        d = dire['ValorProgramacionDiaria']
        l_pdia.append(d)
        s = dire['ValorProgramacionSemanal']
        l_psemana.append(s)

    df_coes = pd.DataFrame(list(zip(l_fecha, l_hora, l_ejec, l_pdia, l_psemana)), columns=['Fecha', 'Hora', 'Ejecutado',
                                                                                           'Prog. Dia', 'Prog. Semana'])
    df_coes = df_coes.fillna(0.00)

    l_hp = []
    hp_index_i = l_horas.index(hp_i)
    hp_index_f = l_horas.index(hp_f)

    for i in range(hp_index_i - 1, hp_index_f):
        l_hp.append(l_hora[i])

    df_coes_hp = df_coes[df_coes['Hora'].isin(l_hp)]
    print(df_coes_hp)

    df_hp_hoy = df_coes_hp[df_coes_hp['Fecha'] == f_hoy_str]

    l_prog_s = df_hp_hoy['Prog. Semana'].tolist()
    l_prog_d = df_hp_hoy['Prog. Dia'].tolist()

    dict_coes = dict(iter(df_coes_hp.groupby('Fecha')))

    l_res_ejecutado = []
    dict_reultados_ej = {}
    dict_resultados_semana = {}
    dict_resultados_dia = {}
    l_res_h_semana = []
    l_res_h_dia = []

    for day in dict_coes.keys():

        df_dia = dict_coes[day]

        max_ej = df_dia['Ejecutado'].max()
        max_semana = df_dia['Prog. Semana'].max()
        max_dia = df_dia['Prog. Dia'].max()

        max_semana_h = df_dia.loc[df_dia['Prog. Semana'] == max_semana, 'Hora'].item()
        try:
            max_dia_h = df_dia.loc[df_dia['Prog. Dia'] == max_dia, 'Hora'].item()
        except ValueError:
            max_dia_h = 0.0

        index_data = list(dict_coes.keys()).index(day)
        index_hoy = list(dict_coes.keys()).index(f_hoy_str)

        if index_data < index_hoy:
            dict_resultados_semana[day] = 0

        else:
            dict_resultados_semana[day] = max_semana

        dict_reultados_ej[day] = max_ej
        dict_resultados_dia[day] = max_dia

        l_res_ejecutado.append(max_ej)
        l_res_h_semana.append(max_semana_h)
        l_res_h_dia.append(max_dia_h)

    l_max_dia = []
    l_max_ejecutado = []
    demanda_max = max(l_res_ejecutado)
    for n in range(len(l_res_ejecutado)):
        l_max_ejecutado.append(demanda_max)
        l_max_dia.append(0)

    l_dif_dia = []
    l_dif_s = []
    for x in range(len(l_prog_d)):
        l_dif_dia.append(demanda_max - l_prog_d[x])
        l_dif_s.append(demanda_max - l_prog_s[x])

    X = dict_coes.keys()
    print(list(X))
    X_axis = np.arange(len(X))
    indx_hoy = list(X).index(f_hoy_str)

    l_max_dia[indx_hoy] = dict_resultados_dia[f_hoy_str]

    """
    bar_list = plt.bar(X_axis, list(dict_resultados_semana.values()), label='Prog. Semana', width=0.9)
    bar_hoy = plt.bar(X_axis, l_max_dia, label='Prog. Día', color='green', width=0.9)
    bar_ej = plt.bar(X_axis, list(dict_reultados_ej.values()), label='Ejecutado', width=0.9, color='grey')
    plot_max = plt.plot(X_axis, l_max_ejecutado, label='Demanda Máxima', color='red', linestyle='dashed')

    plt.xticks(X_axis, X, rotation=90)
    plt.ylim([6400, 7000])
    plt.legend(loc=8)

    # plt.show()
    """

    df_diff = pd.DataFrame(data=zip(l_dif_s, l_dif_dia), columns=['Dif. Semana', 'Dif. Día'], index=l_hp)

    """
    fig, ax = plt.subplots(figsize=(20, 10))

    heatmap = ax.pcolor(df_diff, edgecolors='w', cmap='RdYlGn')
    ax.autoscale(tight=True)
    ax.set_aspect(0.4)
    # ax.xaxis.set_ticks_positions('top')
    ax.tick_params(bottom='off', top='off', left='off', right='off')

    plt.yticks(np.arange(len(df_diff.index)) + 0.5, df_diff.index, size=20)
    plt.xticks(np.arange(len(df_diff.columns)) + 0.5, df_diff.columns, rotation=0, size=15)
    
    for i in range(len(list(df_diff.index))):
        for j in range(len(list(df_diff.columns))):
            text = ax.text(j+0.5, i+0.5, round(df_diff.iloc[i][j], 2), ha='center', va='center', color='w', fontsize='x-large', fontweight='bold')

    #plt.show()
    """

    return list(dict_resultados_semana.values()), list(
        dict_reultados_ej.values()), l_max_ejecutado, X_axis, l_max_dia, X, df_diff

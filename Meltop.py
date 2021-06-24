from Optimizador import round_col


def calc_melting(df_cestas, num_cestas, df_inventario, l_fund_factor, l_pot_cesta, ox_flux, e_reaccion, kt_factor,
                 ox_flux_afino, pot_afino, e_reacc_ox, l_end_step, ox_flux_cesta):

    global melt_load, vol_req

    l_vol = df_cestas['Volumen [m3]'].tolist()
    l_densidad = df_cestas['Densidad [ton/m3]'].tolist()
    l_peso = df_cestas['Peso [ton]'].tolist()
    l_energia = df_cestas['Energía [kWh]'].tolist()

    rho_mix = round(sum(l_peso) / sum(l_vol), 2)

    l_potencia = df_inventario['Energia']
    l_carga = df_inventario['Carga']
    e_mix = sum([a * b for a, b in zip(l_potencia, l_carga)])

    l_melt_load = []
    l_diff_load = [0]
    l_vol_req = []
    l_energia_req = []
    l_pon = []
    l_t_ox = []
    l_e_quim_esp = []
    l_e_quim = []
    l_flux_o2 = []
    l_flux_o2_kt = []
    l_el_esp = []
    l_el = []
    l_e_ox = []
    l_t2 = []

    for x in range(num_cestas):

        peso_cesta = l_peso[x] + l_diff_load[x]

        if num_cestas == 3:
            if x == 0:

                rho_cesta = l_densidad[x] * 0.98
                vol_req = l_vol[x + 1]
                # melt_load = (vol_req * rho_cesta)
                melt_load = l_peso[x]

            elif x + 1 == num_cestas:
                rho_cesta = l_densidad[x]
                vol_req = peso_cesta / rho_cesta
                # melt_load = peso_cesta
                melt_load = l_peso[x]

            else:
                rho_cesta = l_densidad[x]
                vol_req = l_vol[x]
                # melt_load = vol_req * rho_cesta
                melt_load = l_peso[x]

        elif num_cestas == 4:
            if x == 0 or x == 1:
                rho_cesta = l_densidad[x] * 0.98
                vol_req = l_vol[x + 1]
                melt_load = l_peso[x]

            elif x + 1 == num_cestas:
                rho_cesta = l_densidad[x]
                vol_req = peso_cesta / rho_cesta
                melt_load = l_peso[x]

            else:
                rho_cesta = l_densidad[x]
                vol_req = l_vol[x]
                melt_load = l_peso[x]

        if melt_load >= peso_cesta:
            l_melt_load.append(peso_cesta)
            l_diff_load.append(0)

        else:
            l_melt_load.append(melt_load)
            l_diff_load.append(peso_cesta - melt_load)

        energia_req = (melt_load * l_energia[x] * l_fund_factor[x]) / l_peso[x]

        l_energia_req.append(energia_req)
        l_vol_req.append(vol_req)

        ox_factor = e_reacc_ox * kt_factor * ox_flux_cesta
        ox_esp = float(l_end_step[x])
        e_ox = ox_esp * l_peso[x]
        l_e_ox.append(e_ox)

        q_factor = ox_flux * kt_factor * e_reaccion
        el_factor = (float(l_pot_cesta[x]) / 60) * 1000

        # Anteriormente se usaba t2 = e_ox / (ox_factor)
        t2 = e_ox / (ox_factor+el_factor)
        l_t2.append(t2)

        t1 = (energia_req - (t2 * (ox_factor + el_factor))) / (q_factor + el_factor)

        p_on_cesta = t1 + t2

        l_pon.append(p_on_cesta)
        l_t_ox.append(t2)

        o2_kt = t2 * ox_flux_cesta
        o2_cesta = t1 * ox_flux + t2 * o2_kt

        l_flux_o2_kt.append(o2_kt)

        e_quim_cesta = t1 * q_factor + e_ox
        e_quim_cesta_esp = e_quim_cesta / l_peso[x]

        l_flux_o2.append(o2_cesta)
        l_e_quim_esp.append(e_quim_cesta_esp)
        l_e_quim.append(e_quim_cesta)

        if x == 0:
            e_el_esp = (energia_req / (l_peso[x] + 1)) - e_quim_cesta_esp
            l_el_esp.append(e_el_esp)
            l_el.append(energia_req - e_quim_cesta)

        else:
            e_el_esp = (energia_req / (peso_cesta - l_diff_load[x])) - e_quim_cesta_esp
            l_el_esp.append(e_el_esp)
            l_el.append(energia_req - e_quim_cesta)

    e_melting = sum(l_energia_req)
    e_afino = e_mix - e_melting

    t_afino = e_afino / ((ox_flux_afino * kt_factor * e_reacc_ox) + ((pot_afino / 60) * 1000))

    e_quim_esp_afino = (ox_flux_afino * kt_factor * e_reacc_ox * t_afino) / sum(l_peso)
    e_quim_afino = e_quim_esp_afino * sum(l_peso)

    e_el_esp_afino = (e_afino / sum(l_peso)) - e_quim_esp_afino
    e_el_afino = e_el_esp_afino * sum(l_peso)

    o2_afino = t_afino * ox_flux_afino

    e_quim_mix = sum(l_e_quim)
    e_el_mix = sum(l_el)
    e_ox_mix = sum(l_e_ox)

    df_cestas['Volumen requerido [m3]'] = l_vol_req
    df_cestas['Peso a fundir [ton]'] = l_melt_load
    df_cestas['Energía requerida [kWh]'] = l_energia_req
    df_cestas['Energía química específica [kWh/ton]'] = l_e_quim_esp
    df_cestas['Energía eléctrica específica [kWh/ton]'] = l_el_esp
    df_cestas['Power On [min]'] = l_pon

    # df_cestas['Energía de Ox. [kWh]'] = l_e_ox
    df_cestas['Flujo de O2 [m3]'] = l_flux_o2
    df_cestas['Flujo de O2 lanza [m3]'] = l_flux_o2_kt
    df_cestas['Tiempo Oxy. [min]'] = l_t2

    df_cestas = df_cestas.transpose()

    e_quim_esp_total = (e_quim_afino + e_quim_mix)
    e_el_total = (e_el_afino + e_el_mix)
    ox_total = o2_afino + sum(l_flux_o2)
    p_on_total = sum(l_pon) + t_afino

    ox_lanza_total = sum(l_flux_o2_kt) + o2_afino

    l_afino = [sum(l_peso), " ", rho_mix, " ", " ", " ", e_afino, e_quim_esp_afino, e_el_esp_afino, t_afino, o2_afino, o2_afino, " "]
    l_total = [" ", " ", " ", " ", " ", " ", e_mix, e_quim_esp_total, e_el_total, p_on_total, ox_total,
               ox_lanza_total, " "]

    df_cestas['Afino'] = l_afino
    df_cestas['Total'] = l_total

    for x in range(num_cestas):
        nom_cesta = str('Cesta N°' + str(x + 1))

        round_col(df_cestas, nom_cesta, 2)

    round_col(df_cestas, 'Afino', 2)
    round_col(df_cestas, 'Total', 2)

    l_el_esp.append(e_el_esp_afino)
    l_peso.append(sum(l_peso))

    return df_cestas, l_el_esp, l_peso

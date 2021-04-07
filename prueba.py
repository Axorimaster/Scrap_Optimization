import sqlite3
from pandastable import Table
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import Optimizador as Opt
import Meltop as Mlt
import tk_tools as tkt



##Creación y seteo de la ventana raíz
root = tk.Tk()
root.title("Kedalion MOS v.1.1")
root.iconbitmap('Images/kedalionicon.ico')
root.state('zoomed')

container = tk.Canvas(root)
main_frame = tk.Frame(container)
sb_h = tk.Scrollbar(root)
sb_v = tk.Scrollbar(root)

container.config(xscrollcommand=sb_h.set, yscrollcommand=sb_v.set, highlightthickness=0)
sb_h.config(orient=tk.HORIZONTAL, command=container.xview)
sb_v.config(orient=tk.VERTICAL, command=container.yview)

sb_h.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
sb_v.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
container.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
container.create_window(0, 0, window=main_frame, anchor=tk.NW)


# Funciones
def update_df_inventario():
    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    l_comp_scrap_names = df_inventario['Nombre'].tolist()

    return l_comp_scrap_names


def update_df_comp():
    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)


def compare_lists(l1, l2):
    l_bool = []
    if len(l1) == len(l2):
        for x in range(len(l1)):
            if l1[x] == l2[x]:
                l_bool.append(True)
            else:
                l_bool.append(False)
        if False in l_bool:
            return False
        else:
            return True

    else:
        return False


def compare_dfs(df1, df2):
    l_col_df1 = list(df1.columns)
    l_col_df2 = list(df2.columns)
    l_bool = []

    l_index = []
    for x in range(20):
        l_index.append(x)

    if compare_lists(l_col_df1, l_col_df2):

        if len(df1) != len(df2):
            return False
        else:
            for col in l_col_df1:
                column1 = df1[col].tolist()
                column2 = df2[col].tolist()

                if compare_lists(column1, column2):
                    l_bool.append(True)
                else:
                    l_bool.append(False)
            if False in l_bool:
                return False
            else:
                return True
    else:
        return False


def updateScroll():
    container.update_idletasks()
    container.config(scrollregion=main_frame.bbox())


def raise_frame(val):

    frame_indx = l_frames_names.index(val)
    frame = l_frames[frame_indx]

    for x in l_frames:
        if x == frame:
            x.grid(row=0, column=0)
        else:
            x.grid_forget()

    if frame_indx == 0:
        inv_query()

    elif frame_indx == 1:
        comp_query()
        comp_cmb.config(values=update_df_inventario())

    elif frame_indx == 2:
        res_load_inv()

    elif frame_indx == 3:
        res_load_inv()
        param_load_inv()
        param_checkifprod()
        calc_ncol()

    elif frame_indx == 5:

        try:
            bucket_sim()
        except:
            pass


def save_warning(df_1, df_2):

    if compare_lists(list(df_2.columns), ['a', 'b', 'c', 'd', 'e']):
        pass

    else:
        if compare_dfs(df_1, df_2):
            pass
        else:
            save_wrn = tk.messagebox.askquestion('Advertencia',
                                                 'Si sale ahora perderá todos los datos datos no guardados. ¿Desea continuar?',
                                                 icon='warning')
            if save_wrn == 'yes':
                pass
            else:
                return False


def cb(event):
    item = str(menu_tv.focus())
    next_frame_name = menu_tv.item(item, "text")
    next_frame_idx = l_frames_names.index(next_frame_name)

    if next_frame_idx != current_frame.get():

        if current_frame.get() == 0:
            df_1 = pd.read_sql_query("SELECT * FROM scrap_data", conn)
            df_1 = df_1[df_1.Nombre != '']
            df_2 = table_scrap.model.df
            if save_warning(df_1, df_2) == False:
                return

        elif current_frame.get() == 1:
            df_1 = pd.read_sql_query("SELECT * FROM comp_data", conn)
            df_1 = df_1[df_1.Nombre != '']
            df_2 = table_comp.model.df
            if save_warning(df_1, df_2) == False:
                return

        else:
            pass

    current_frame.set(next_frame_idx)
    raise_frame(next_frame_name)


###
def inv_save_sql():
    df_inventario.reset_index(drop=True, inplace=True)
    df_inventario.to_sql('scrap_data', conn, if_exists='replace', index=False)


def comp_save_sql():
    df_comp.reset_index(drop=True, inplace=True)
    df_comp.to_sql('comp_data', conn, if_exists='replace', index=False)


##
def inv_submit():

    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)

    if f_nombre.get() in df_inventario['Nombre'].tolist():
        messagebox.showerror(title="Error", message="Ya existe una chatarra con ese nombre")
        return
    else:
        precio = 0.0
        densidad = 0.0
        inventario = 0.0
        rendimiento = 0.0
        energia = 0.0

        l_inv_sql = [precio, densidad, inventario, rendimiento, energia]
        count = 0

        for entry in l_inv_entries:

            try:
                val = float(entry.get())
                l_inv_sql[count] = val

            except:
                l_inv_sql[count] = 0.0

            count += 1

        if f_nombre.get() == '':
            return

        else:
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO scrap_data VALUES (:f_nombre, :f_precio, :f_densidad, :f_inventario, :f_rendimiento, :f_energia)",
                {
                    'f_nombre': f_nombre.get(),
                    'f_precio': l_inv_sql[0],
                    'f_densidad': l_inv_sql[1],
                    'f_inventario': l_inv_sql[2],
                    'f_rendimiento': l_inv_sql[3],
                    'f_energia': l_inv_sql[4]
                })

            conn.commit()

            f_nombre.delete(0, tk.END)
            f_precio.delete(0, tk.END)
            f_densidad.delete(0, tk.END)
            f_energia.delete(0, tk.END)
            f_rendimiento.delete(0, tk.END)
            f_inventario.delete(0, tk.END)

            inv_query()

            comp_cmb.config(values=update_df_inventario())


def comp_submit():
    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)

    if comp_cmb.get() in df_comp['Nombre'].tolist():

        messagebox.showerror(title="Error", message="Ya existe una chatarra con ese nombre")
        return

    else:
        c_ = 0.0
        mn_ = 0.0
        si_ = 0.0
        p_ = 0.0
        cr_ = 0.0
        s_ = 0.0
        cu_ = 0.0
        ni_ = 0.0
        mo_ = 0.0

        l_comp_sql = [c_, mn_, si_, p_, cr_, s_, cu_, ni_, mo_]

        count = 0

        for entry in l_comp_entries:

            try:
                val = float(entry.get())
                l_comp_sql[count] = val

            except:
                l_comp_sql[count] = 0.0

            count += 1

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO comp_data VALUES (:f_nombre, :f_c, :f_mn, :f_si, :f_p, :f_cr, :f_s, :f_cu, :f_ni, :f_mo)",
            {
                'f_nombre': comp_cmb.get(),
                'f_c': l_comp_sql[0],
                'f_mn': l_comp_sql[1],
                'f_si': l_comp_sql[2],
                'f_p': l_comp_sql[3],
                'f_cr': l_comp_sql[4],
                'f_s': l_comp_sql[5],
                'f_cu': l_comp_sql[6],
                'f_ni': l_comp_sql[7],
                'f_mo': l_comp_sql[8]
            })

        conn.commit()
        comp_c_e.delete(0, tk.END)
        comp_mn_e.delete(0, tk.END)
        comp_si_e.delete(0, tk.END)
        comp_p_e.delete(0, tk.END)
        comp_cr_e.delete(0, tk.END)
        comp_s_e.delete(0, tk.END)
        comp_cu_e.delete(0, tk.END)
        comp_ni_e.delete(0, tk.END)
        comp_mo_e.delete(0, tk.END)

        comp_query()


##
def inv_query():
    global df_inventario

    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    df_inventario = df_inventario[df_inventario.Nombre != '']

    conn.commit()

    table_scrap.model.df = df_inventario
    table_scrap.autoResizeColumns()
    table_scrap.redraw()

    inv_n_scraps.set(len(df_inventario))


def comp_query():
    global df_comp

    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)

    conn.commit()

    table_comp.model.df = df_comp
    table_comp.autoResizeColumns()
    table_comp.redraw()


##
def inv_delete():
    ask = messagebox.askquestion(title='Eliminar', message='¿Desea eliminar este dato?')
    if ask == 'yes':
        row = table_scrap.getSelectedRows()
        del_item_name = (row['Nombre'].tolist())[0]

        cur = conn.cursor()
        cur.execute('DELETE FROM scrap_data WHERE Nombre=?', (del_item_name,))
        conn.commit()

        inv_query()
        update_df_inventario()

    else:
        return


def comp_delete():
    ask = messagebox.askquestion(title='Eliminar', message='¿Desea eliminar este dato?')
    if ask == 'yes':
        row = table_comp.getSelectedRows()
        del_item_name = (row['Nombre'].tolist())[0]

        cur = conn.cursor()
        cur.execute('DELETE FROM comp_data WHERE Nombre=?', (del_item_name,))
        conn.commit()

        comp_query()
        update_df_comp()

    else:
        return


def param_checkifprod():
    try:
        float(res_prod_e.get())
    except:
        messagebox.showwarning(title='Advertencia', message='Aún no se ha especificado una producción objetivo')


########################
def update_progress(update):
    progress.p_value.set(progress.p_value.get() + update)


def progress(*args):

    progress.progress_frame = tk.LabelFrame(tv_frame, height=75, width=200)

    progress.progress_label = tk.Label(progress.progress_frame, text="Calculando mix...")
    progress.progress_label.grid(row=4, column=0, pady=0, sticky='nsew')
    progress.p_value = tk.IntVar()
    progress.p_value.set(10)
    progress.progress_bar = ttk.Progressbar(progress.progress_frame, orient='horizontal', length=180, mode='determinate', maximum=100, variable=(progress.p_value))
    progress.progress_bar.grid(row=5, column=0, pady=10, padx=8, sticky='ew')

    progress.progress_frame.grid(row=4, column=0, columnspan=2)
    progress.progress_frame.grid_propagate(False)

    progress.progress_frame.after(500, start_sim)


def start_sim():

    global df_results, df_buckets, l_kpi

    param_load_inv()
    calc_ncol()

    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)

    print(df_inventario)

    carga_eaf = float(load_eaf.get())
    vol_cesta = float(volume_cesta.get())
    carga_cesta = float(load_cesta.get())
    n_coladas = float(n_col.get())

    num_cestas.set(num_cestas.get())
    n_cestas = int(num_cestas.get())

    input_prod = int(prod_obj.get())

    epsilon = tk.DoubleVar()
    epsilon.set(0)

    l_lifeline = []
    for slide in gen_slides.l_res_slides:
        res_ll = (float(slide.get())/100)
        l_lifeline.append(res_ll)

    base_scrap_dict = {}
    indx = 0

    for value in gen_checkboxes.l_values:

        if value.get() == True:

            scrap = gen_checkboxes.l_chbx[indx].cget('text')
            base = float(gen_checkboxes.l_entries[indx].get())

            base_scrap_dict[scrap] = base
            indx += 1

    success = False

    while success == False:

        if Opt.main(df_inventario, df_comp, n_cestas, input_prod, l_lifeline, epsilon.get(), base_scrap_dict, carga_eaf, vol_cesta, carga_cesta, n_coladas) == True:

            if auto_cestas.get() == True:

                num_cestas.set(num_cestas.get()+1)
                n_cestas = n_cestas + 1

                progress.progress_frame.after(100, update_progress(20))

            else:
                print(epsilon.get())
                epsilon.set(epsilon.get() + 0.05)
                progress.progress_frame.after(100, update_progress(20))

        else:

            success = True
            df_results, df_buckets, l_kpi = Opt.main(df_inventario, df_comp, n_cestas, input_prod, l_lifeline, epsilon.get(), base_scrap_dict, carga_eaf, vol_cesta, carga_cesta, n_coladas)
            progress.progress_frame.after(100, update_progress(100))

    df_results_disp = df_results.loc[:,'Carga':]
    df_results_disp.reset_index(inplace=True)
    table_rep.model.df = df_results_disp
    table_rep.autoResizeColumns()
    table_rep.redraw()

    progress.progress_frame.destroy()

    b_save.config(state='normal')

    i = 0
    for label in l_kpi_labels:
        label.config(text=str(l_kpi[i]))
        i += 1

    return


def bucket_sim():

    melting_factor = float(eff_melt.get())/100
    n_lanzas = int(nkt.get())
    pot_cesta = float(pot_prom_cesta.get())
    oxy_flux = (int(ox_flux.get()))*n_lanzas/60
    e_reaccion = float(ereac.get())
    kt_factor = float(eff_reac.get())/100
    oxy_flux_afino = (int(ox_flux_af.get()))*n_lanzas/60
    pot_afino = float(pot_promaf_cesta.get())
    e_reacc_ox = float(ereac_af.get())
    l_end_step = [40, 90, 120, 90]

    df_cestas, l_e_req, l_peso = Mlt.calc_melting(df_buckets,  num_cestas.get(), df_results, melting_factor, pot_cesta, oxy_flux, e_reaccion, kt_factor,oxy_flux_afino, pot_afino, e_reacc_ox, l_end_step)

    df_cestas.reset_index(inplace=True)
    table_cesta.model.df = df_cestas
    table_cesta.autoResizeColumns()
    table_cesta.redraw()

    l_cestas = list(df_cestas.columns)
    cesta_lblgrid.clear()

    for x in range(num_cestas.get()+1):

        l_grid = [l_cestas[x+1], round(l_e_req[x],0), l_peso[x]]
        cesta_lblgrid.add_row(l_grid)


def save_sim():

    print(df_results)

    save_file_path = tk.filedialog.asksaveasfilename(defaultextension='.csv')
    df_results.to_csv(save_file_path)


def comp_print_name(*args):
    l_nombres = df_comp['Nombre'].tolist()
    comp_values = df_comp.values.tolist()

    if comp_scrap_name.get() != ' ':

        comp_scrapname_label.configure(text='Se ha seleccionado {}'.format(comp_scrap_name.get()))

        if comp_scrap_name.get() in l_nombres:
            scrap_indx = l_nombres.index(comp_scrap_name.get())
            x = 0

            for entry in l_comp_entries:
                val = str(comp_values[scrap_indx][x + 1])
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, val)
                x += 1

        else:

            for entry in l_comp_entries:
                entry.config(state='normal')
                entry.delete(0, tk.END)

        comp_c_e.config(state='normal')
        comp_mn_e.config(state='normal')
        comp_si_e.config(state='normal')
        comp_p_e.config(state='normal')
        comp_cr_e.config(state='normal')
        comp_s_e.config(state='normal')
        comp_cu_e.config(state='normal')
        comp_ni_e.config(state='normal')
        comp_mo_e.config(state='normal')

    else:

        comp_scrapname_label.configure(text=' ')

        for entry in l_comp_entries:
            entry.config(state='disabled')


def gen_slides():

    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    l_inv_values = df_inventario['Inventario'].tolist()
    l_inv_names = df_inventario['Nombre'].tolist()
    l_inv_rend = df_inventario['Rendimiento'].tolist()
    gen_slides.l_inv_valid = []
    gen_slides.l_inv_rend_valid = []
    gen_slides.l_inv_valid_name = []

    for widget in res_llframe.winfo_children():
        widget.destroy()

    for x in range(len(df_inventario)):
        l_inv_values[x] = float(l_inv_values[x])
        if l_inv_values[x] != 0.0:
            gen_slides.l_inv_valid.append(l_inv_values[x])
            gen_slides.l_inv_valid_name.append(l_inv_names[x])
            gen_slides.l_inv_rend_valid.append(l_inv_rend[x])

    inv_n_scraps.set(len(gen_slides.l_inv_valid))

    gen_slides.l_res_slides = []
    gen_slides.l_res_sl_lb = []
    row = 0
    add = 0

    for x in range(inv_n_scraps.get()):
        slide = tk.Scale(res_llframe, orient='horizontal', tickinterval=100, from_=0, to=100, resolution=5,
                         showvalue=True, digits=0, sliderlength=15, label=gen_slides.l_inv_valid_name[x],
                         command=res_calc_inv)
        slide.set(100)
        slide.grid(row=row + add, column=0, padx=10, pady=2)
        sep = ttk.Separator(res_llframe, orient='horizontal')
        label = tk.Label(res_llframe, text=(slide.get() * gen_slides.l_inv_valid[x]) / 100)
        label.grid(row=row + add, column=1)
        sep.grid(row=row + 1 + add, column=0, columnspan=2, sticky='ew')

        row += 1
        add += 1
        gen_slides.l_res_slides.append(slide)
        gen_slides.l_res_sl_lb.append(label)


def gen_checkboxes():

    res_calc_inv()
    gen_checkboxes.l_chbx = []
    gen_checkboxes.l_values = []
    gen_checkboxes.l_entries = []

    for widget in param_sc_frame.winfo_children():
        widget.destroy()

    for x in range(len(gen_slides.l_inv_valid_name)):
        value = tk.BooleanVar()
        value.set(True)
        gen_checkboxes.l_values.append(value)

    for x in range(len(gen_slides.l_inv_valid_name)):
        chbx = ttk.Checkbutton(param_sc_frame, text=gen_slides.l_inv_valid_name[x], variable=gen_checkboxes.l_values[x], command=lambda i=x: activate_entry(i))
        chbx.grid(row=x + x, column=0, pady=2, padx=5, sticky='w')
        entry = ttk.Entry(param_sc_frame, width=7, state='disabled')
        entry.grid(row=x+x, column=1, pady=1, padx=2)
        lb = tk.Label(param_sc_frame, text='[ton]')
        lb.grid(row=x+x, column=2, pady=1, padx=2)

        gen_checkboxes.l_chbx.append(chbx)
        gen_checkboxes.l_entries.append(entry)



    for x in range(len(gen_slides.l_inv_valid_name)):
        if gen_slides.l_inv_valid_name[x] == 'LIVIANA' or gen_slides.l_inv_valid_name[x] == 'CIZALLA':
            gen_checkboxes.l_values[x].set(True)
            gen_checkboxes.l_entries[x].config(state='normal')
            if gen_slides.l_inv_valid_name[x] == 'LIVIANA':
                gen_checkboxes.l_entries[x].insert(0, '2')
            if gen_slides.l_inv_valid_name[x] == 'CIZALLA':
                gen_checkboxes.l_entries[x].insert(0, '2')

        else:
            gen_checkboxes.l_values[x].set(False)


def res_calc_inv(*args):

    sum = 0
    rend = 0
    x = 0
    l_res = []

    for slide in gen_slides.l_res_slides:
        porcentaje = (slide.get()) / 100
        inv = gen_slides.l_inv_valid[x]
        inv_ll = round(porcentaje * inv, 0)
        rend_unit = float(gen_slides.l_inv_rend_valid[x])
        rend_unit = inv_ll * rend_unit
        slide = gen_slides.l_res_sl_lb[x]
        slide.config(text=inv_ll)

        sum += round(inv_ll,0)
        rend += round(rend_unit,0)

        x += 1

    res_invll_disp_lb.config(text=sum)
    res_rend_disp_lb.config(text=rend)
    check_inv()

    l_res.append(sum)
    l_res.append(rend)

    return l_res


def res_load_inv(*args):

    l_bool = []

    try:
        for slide in gen_slides.l_res_slides:

            if slide.get() != 100:
                l_bool.append(True)

            else:
                l_bool.append(False)

        if True not in l_bool:
            gen_slides()

    except:

        gen_slides()


def param_load_inv(*args):

    try:

        df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
        l_inv_values = df_inventario['Inventario'].tolist()
        l_inv_names = df_inventario['Nombre'].tolist()

        l_inv_valid_name = []

        for x in range(len(df_inventario)):
            l_inv_values[x] = float(l_inv_values[x])
            if l_inv_values[x] != 0.0:
                l_inv_valid_name.append(l_inv_names[x])

        l_2 = []

        for chbx in gen_checkboxes.l_chbx:
            name = chbx.cget('text')
            l_2.append(name)

        if compare_lists(l_inv_valid_name, l_2):
            l_bool = []

            for x in range(len(gen_checkboxes.l_chbx)):

                if (gen_checkboxes.l_values[x]).get():
                    l_bool.append(True)

                else:
                    l_bool.append(False)

                x += 1

            if True not in l_bool:
                gen_checkboxes()

        else:
            gen_checkboxes()

    except:
        gen_checkboxes()


def check_inv(*args):
    try:
        prod = float(prod_obj.get())
        b_start.config(state='normal')


    except:
        prod = 0
        b_start.config(state='disabled')
        b_save.config(state='disabled')

    disp = float(res_rend_disp_lb.cget('text'))

    if prod >= disp:
        messagebox.showerror(title='Error',
                             message='La producción objetivo es mayor o igual al inventario disponible. La simulación puede fallar.')
        res_prod_e.select_range(0, 'end')

    else:
        return


def calc_ncol(*args):
    try:
        prod_mes = float(res_prod_e.get())
        eaf_prod = float(param_eafprod_e.get())
        n_coladas = str(round(prod_mes / eaf_prod, 0))
        n_col.set(n_coladas)

    except:
        n_col.set('0')


def activate_entry(n):

    try:

        val = gen_checkboxes.l_values[n]
        if val.get():
            gen_checkboxes.l_entries[n].config(state='normal')
            val.set(True)

        else:
            gen_checkboxes.l_entries[n].delete(0, 'end')
            gen_checkboxes.l_entries[n].config(state='disabled')
            val.set(False)
    except:

        return


def enable_num_cestas(*args):

    if auto_cestas.get() == True:
        num_cestas.set(1)
        res_ncestas_cmb.config(state='disabled')

    else:
        num_cestas.set(3)
        res_ncestas_cmb.config(state='normal')



# Frame del título y logo del programa
title_frame = tk.Frame(main_frame, padx=5, pady=5)
title_frame.grid(row=0, column=0, padx=0, pady=0, columnspan=2)

# Frame de display de otros frames del programa
disp_frame = tk.LabelFrame(main_frame, text="Config.", padx=20, pady=20, height=510, width=1165)
disp_frame.grid(row=1, column=1)
disp_frame.grid_propagate(False)

# Listado de frames
inv_frame = tk.Frame(disp_frame)
comp_frame = tk.Frame(disp_frame)
res_frame = tk.Frame(disp_frame)
param_frame = tk.Frame(disp_frame)
rep_frame = tk.Frame(disp_frame)
cesta_frame = tk.Frame(disp_frame)
graph_frame = tk.Frame(disp_frame)

l_frames = (inv_frame, comp_frame, res_frame, param_frame, rep_frame, cesta_frame, graph_frame)
l_frames_names = ['Inventario', 'Composición', 'Restricciones', 'Parámetros', 'Reporte', 'Cestas', 'Gráficos']
current_frame = tk.IntVar(master=None)
current_frame.set(1000)

# Frame de TreeView
tv_frame = tk.LabelFrame(main_frame, text="Menú", padx=20, pady=20, height=510, width=300)
tv_frame.grid(row=1, column=0, padx=20, pady=20)
tv_frame.grid_propagate(False)

"""
copyrght_lb = tk.Label(main_frame, text='Rodrigo Zambrano, 2021. Todos los derechos reservados.')
copyrght_lb.grid(row=2, column=1)
"""

# Conexión a SQLITE3
conn = sqlite3.connect('scrap.db')
cur = conn.cursor()

"""
cur.execute("CREATE TABLE scrap_data (Nombre TEXT, Precio FLOAT , Densidad FLOAT, Inventario INTEGER, Rendimiento FLOAT, Energia FLOAT)")
"""

##Frame del título del programa
img_1 = Image.open('Images/Kedalion.png')
img_2 = Image.open('Images/kedalion_desk.png')
img_1 = img_1.resize((580, 200), Image.ANTIALIAS)
kedalion_img = ImageTk.PhotoImage(img_1)
lb_1 = tk.Label(title_frame, image=kedalion_img)
lb_1.grid(row=0, column=0, columnspan=2)
img_2 = img_2.resize((12, 12), Image.ANTIALIAS)
tv_icon = ImageTk.PhotoImage(img_2)

##Menu Frame
menu_tv = ttk.Treeview(tv_frame)
menu_tv.grid(row=0, column=0, columnspan=2, sticky='nsew')
menu_top = menu_tv.insert("", tk.END, text=' Kedalion', image=tv_icon, tags='cd', open=True)
menu_datos = menu_tv.insert(menu_top, tk.END, text='Datos', tags='cd')
menu_simu = menu_tv.insert(menu_top, tk.END, text='Simulación', tags='cd')
menu_result = menu_tv.insert(menu_top, tk.END, text='Resultados', tags='cd')
menu_tv.insert(menu_datos, tk.END, text='Inventario', tags='cb')
menu_tv.insert(menu_datos, tk.END, text='Composición', tags='cb')
menu_tv.insert(menu_simu, tk.END, text='Restricciones', tags='cb')
menu_tv.insert(menu_simu, tk.END, text='Parámetros', tags='cb')
menu_tv.insert(menu_result, tk.END, text='Reporte', tags='cb')
menu_tv.insert(menu_result, tk.END, text='Cestas', tags='cb')
menu_tv.insert(menu_result, tk.END, text='Gráficos', tags='cb')
menu_tv.tag_bind('cb', '<Double-1>', cb)
menu_tv.tag_configure(tagname='cb', font=('Segoe', 10))
menu_tv.tag_configure(tagname='cd', font=('Segoe', 10))

b_quit = ttk.Button(tv_frame, text="Salir", command=root.destroy)
b_start = ttk.Button(tv_frame, text='Iniciar', command=progress, state='disabled')
b_save = ttk.Button(tv_frame, text='Guardar', command=save_sim, state='disabled')
b_start.grid(row=1, column=1, padx=10, pady=10)
b_quit.grid(row=1, column=0,padx=10, pady=10)
b_save.grid(row=2, column=0,padx=10, pady=10 )

##Inv frame
inv_bframe = tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=260)
inv_bframe.grid(row=1, column=1)
inv_bframe.grid_propagate(False)
inv_tframe = tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=858)
inv_tframe.grid(row=1, column=2)
inv_tframe.grid_propagate(False)

table_scrap = Table(inv_tframe, showstatusbar=True)
table_scrap.show()

inv_n_scraps = tk.IntVar()
inv_n_scraps.set(0)

inv_entries_lb = tk.Label(inv_bframe, text='Datos de Chatarra')
inv_entries_lb.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)

f_nombre = ttk.Entry(inv_bframe, width=10)
lb_nombre = tk.Label(inv_bframe, text="Nombre:")
f_nombre.grid(row=1, column=1, pady=5, padx=3)
lb_nombre.grid(row=1, column=0, pady=5, sticky='w', padx=2)

f_precio = ttk.Entry(inv_bframe, width=10)
lb_precio = tk.Label(inv_bframe, text="Precio:")
f_precio.grid(row=2, column=1, pady=5, padx=3)
lb_precio.grid(row=2, column=0, pady=5, sticky='w', padx=2)
lb_unit_precio = tk.Label(inv_bframe, text='[$/ton]')
lb_unit_precio.grid(row=2, column=2, pady=5, sticky='w')

f_densidad = ttk.Entry(inv_bframe, width=10)
lb_densidad = tk.Label(inv_bframe, text="Densidad:")
f_densidad.grid(row=3, column=1, pady=5, padx=3)
lb_densidad.grid(row=3, column=0, pady=5, sticky='w', padx=2)
lb_unit_densidad = tk.Label(inv_bframe, text='[m3/ton]')
lb_unit_densidad.grid(row=3, column=2, pady=5, sticky='w')

f_inventario = ttk.Entry(inv_bframe, width=10)
lb_inventario = tk.Label(inv_bframe, text="Inventario:")
f_inventario.grid(row=4, column=1, pady=5, padx=3)
lb_inventario.grid(row=4, column=0, pady=5, sticky='w', padx=2)
lb_unit_inv = tk.Label(inv_bframe, text='[ton]')
lb_unit_inv.grid(row=4, column=2, pady=5, sticky='w')

f_rendimiento = ttk.Entry(inv_bframe, width=10)
lb_rendimiento = tk.Label(inv_bframe, text="Rendimiento:")
f_rendimiento.grid(row=5, column=1, pady=5, padx=3)
lb_rendimiento.grid(row=5, column=0, pady=5, sticky='w', padx=2)

f_energia = ttk.Entry(inv_bframe, width=10)
lb_energia = tk.Label(inv_bframe, text="Energía: ")
f_energia.grid(row=6, column=1, pady=7, padx=3)
lb_energia.grid(row=6, column=0, pady=7, sticky='w', padx=2)
lb_unit_ener = tk.Label(inv_bframe, text='[kWh/ton]')
lb_unit_ener.grid(row=6, column=2, pady=5, sticky='w')

inv_separator1 = ttk.Separator(inv_bframe, orient='horizontal')
inv_separator1.grid(row=7, column=0, columnspan=3, pady=5, sticky='ew')

inv_submit_b = ttk.Button(inv_bframe, text="Añadir", command=inv_submit)
inv_query_b = ttk.Button(inv_bframe, text='Mostrar', command=inv_query)
inv_save_b = ttk.Button(inv_bframe, text='Guardar', command=inv_save_sql)
inv_delete_b = ttk.Button(inv_bframe, text='Eliminar', command=inv_delete)
inv_submit_b.grid(row=8, column=1, pady=10, ipadx=10, ipady=1.5)
inv_query_b.grid(row=9, column=1, pady=10, ipadx=10, ipady=1.5)
inv_save_b.grid(row=10, column=1, pady=10, ipadx=10, ipady=1.5)
inv_delete_b.grid(row=11, column=1, pady=10, ipadx=10, ipady=1.5)

l_inv_entries = [f_precio, f_densidad, f_inventario, f_rendimiento, f_energia]

# Composición Frame
comp_bframe = tk.LabelFrame(comp_frame, padx=10, pady=10, height=445, width=260)
comp_bframe.grid(row=1, column=1, sticky='nsew')
comp_bframe.grid_propagate(False)
comp_tframe = tk.LabelFrame(comp_frame, padx=10, pady=10, height=445, width=858)
comp_tframe.grid(row=1, column=2)
comp_tframe.grid_propagate(False)

table_comp = Table(comp_tframe, showstatusbar=True)
table_comp.show()

l_comp_scrap_names = []
l_comp_scrap_names.insert(0, " ")
comp_scrap_name = tk.StringVar(comp_frame)
comp_scrap_name.set(l_comp_scrap_names[0])
comp_cmb = ttk.Combobox(comp_bframe, width=22, textvariable=comp_scrap_name, values=l_comp_scrap_names,
                        state='readonly')
comp_cmb.grid(row=0, column=2, sticky='nsew', columnspan=3)

comp_cmb_label = tk.Label(comp_bframe, text='Nombre')
comp_cmb_label.grid(row=0, column=0, padx=10, columnspan=2)
comp_scrapname_label = tk.Label(comp_bframe, text='')
comp_scrapname_label.grid(row=1, column=0, columnspan=5, pady=5)
comp_scrap_name.trace('w', comp_print_name)

comp_separator1 = ttk.Separator(comp_bframe, orient='horizontal')
comp_separator1.grid(row=2, column=0, columnspan=5, pady=5, sticky='ew')

comp_blank_lb = tk.Label(comp_bframe, text='                     ')
comp_blank_lb.grid(row=3, column=2)

comp_c_lb = tk.Label(comp_bframe, text='C')
comp_c_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_c_lb.grid(row=3, column=0, pady=5)
comp_c_e.grid(row=3, column=1, pady=5)

comp_mn_lb = tk.Label(comp_bframe, text='Mn')
comp_mn_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_mn_lb.grid(row=3, column=3, pady=5)
comp_mn_e.grid(row=3, column=4, pady=5)

comp_si_lb = tk.Label(comp_bframe, text='Si')
comp_si_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_si_lb.grid(row=4, column=0, pady=5)
comp_si_e.grid(row=4, column=1, pady=5)

comp_p_lb = tk.Label(comp_bframe, text='P')
comp_p_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_p_lb.grid(row=4, column=3, pady=5)
comp_p_e.grid(row=4, column=4, pady=5)

comp_cr_lb = tk.Label(comp_bframe, text='Cr')
comp_cr_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_cr_lb.grid(row=5, column=0, pady=5)
comp_cr_e.grid(row=5, column=1, pady=5)

comp_s_lb = tk.Label(comp_bframe, text='S')
comp_s_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_s_lb.grid(row=5, column=3, pady=5)
comp_s_e.grid(row=5, column=4, pady=5)

comp_cu_lb = tk.Label(comp_bframe, text='Cu')
comp_cu_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_cu_lb.grid(row=6, column=0, pady=5)
comp_cu_e.grid(row=6, column=1, pady=5)

comp_ni_lb = tk.Label(comp_bframe, text='Ni')
comp_ni_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_ni_lb.grid(row=6, column=3, pady=5)
comp_ni_e.grid(row=6, column=4, pady=5)

comp_mo_lb = tk.Label(comp_bframe, text='Mo')
comp_mo_e = ttk.Entry(comp_bframe, width=5, state='disabled')
comp_mo_lb.grid(row=7, column=0, pady=5)
comp_mo_e.grid(row=7, column=1, pady=5)

comp_separator2 = ttk.Separator(comp_bframe, orient='horizontal')
comp_separator2.grid(row=8, column=0, columnspan=5, pady=5, sticky='ew')

comp_submit_b = ttk.Button(comp_bframe, text="Añadir", command=comp_submit)
comp_query_b = ttk.Button(comp_bframe, text='Mostrar', command=comp_query)
comp_save_b = ttk.Button(comp_bframe, text='Guardar', command=comp_save_sql)
comp_delete_b = ttk.Button(comp_bframe, text='Eliminar', command=comp_delete)
comp_submit_b.grid(row=9, column=0, pady=10, columnspan=5, ipadx=10, ipady=1.5)
comp_query_b.grid(row=10, column=0, pady=10, columnspan=5, ipadx=10, ipady=1.5)
comp_save_b.grid(row=11, column=0, pady=10, columnspan=5, ipadx=10, ipady=1.5)
comp_delete_b.grid(row=12, column=0, pady=10, columnspan=5, ipadx=10, ipady=1.5)

l_comp_entries = [comp_c_e, comp_mn_e, comp_si_e, comp_p_e, comp_cr_e, comp_s_e, comp_cu_e, comp_ni_e, comp_mo_e]

#Restricciones Frame
res_bframe = tk.LabelFrame(res_frame, padx=10, pady=10, height=445, width=260)
res_bframe.grid(row=1, column=1, sticky='nsew')
res_bframe.grid_propagate(False)
res_bframe.columnconfigure(0, weight=4)
res_bframe.columnconfigure(1, weight=1)
res_tframe = tk.LabelFrame(res_frame, padx=10, pady=10, height=445, width=858)
res_tframe.grid(row=1, column=2)
res_tframe.grid_propagate(False)

res_tframe1 = tk.Frame(res_tframe, height=420, width=400)
res_tframe1.pack_propagate(True)
res_tframe2 = tk.LabelFrame(res_tframe)
res_tframe1.grid(row=0, column=0)
res_tframe2.grid(row=0, column=1)

res_ll_cn = tk.Canvas(res_tframe1, confine=True, width=200, height=420)
res_cn_scb = ttk.Scrollbar(res_tframe1, orient='vertical', command=res_ll_cn.yview)
res_llframe = tk.Frame(res_ll_cn, width=20)
res_llframe.bind('<Configure>', lambda e: res_ll_cn.configure(scrollregion=res_ll_cn.bbox('all')))
res_ll_cn.create_window((0, 0), window=res_llframe, anchor='nw')
res_ll_cn.pack(side='left', fill='both', expand=False)
res_cn_scb.pack(side='right', fill='y', expand=False)

res_invll_text_lb = tk.Label(res_bframe, text='Inventario útil: ')
res_invll_disp_lb = tk.Label(res_bframe, text='')
res_invll_unit_lb = tk.Label(res_bframe, text='[ton/mes]')
res_rend_text_lb = tk.Label(res_bframe, text='Inventario met. : ')
res_rend_disp_lb = tk.Label(res_bframe, text='')
res_rend_unit_lb = tk.Label(res_bframe, text='[ton/mes]')
res_invll_text_lb.grid(row=0, column=0, sticky='w')
res_invll_disp_lb.grid(row=0, column=1, pady=5)
res_invll_unit_lb.grid(row=0, column=2, sticky='e')
res_rend_text_lb.grid(row=1, column=0, sticky='w')
res_rend_disp_lb.grid(row=1, column=1, pady=5)
res_rend_unit_lb.grid(row=1, column=2, sticky='e')

res_separator1 = ttk.Separator(res_bframe, orient='horizontal')
res_separator1.grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

prod_obj = tk.StringVar()
prod_obj.trace('w', check_inv)

res_prod_e = ttk.Entry(res_bframe, textvariable=prod_obj, width=10, justify='right')
res_prod_lb = tk.Label(res_bframe, text='Producción obj. :')
res_prod_unit_lb = tk.Label(res_bframe, text='[ton/mes]')
res_prod_e.grid(row=3, column=1, pady=5, sticky='e', padx=5)
res_prod_lb.grid(row=3, column=0, pady=5, sticky='w')
res_prod_unit_lb.grid(row=3, column=2, pady=5)

res_separator2 = ttk.Separator(res_bframe, orient='horizontal')
res_separator2.grid(row=4, column=0, columnspan=3, pady=5, sticky='ew')

num_cestas = tk.IntVar()
num_cestas.set(3)
res_ncestas_lb = tk.Label(res_bframe, text='Número de cestas:')
res_ncestas_cmb = ttk.Spinbox(res_bframe, textvariable=num_cestas, width=5, from_=1, to=10, increment=1, state='disabled')
auto_cestas = tk.BooleanVar()
auto_cestas.set(True)
res_ncestas_auto_chbx = ttk.Checkbutton(res_bframe, text='Auto', variable=auto_cestas, command=enable_num_cestas)
res_ncestas_cmb.set('1')
res_ncestas_cmb.grid(row=5, column=2, pady=5)
res_ncestas_lb.grid(row=5, column=0, pady=5, sticky='w', columnspan=2)
res_ncestas_auto_chbx.grid(row=5, column=1, pady=2)

res_separator3 = ttk.Separator(res_bframe, orient='horizontal')
res_separator3.grid(row=6, column=0, columnspan=3, pady=5, sticky='ew')

######################

param_eaf_frame = tk.LabelFrame(param_frame, text='Horno Eléctrico', height=120, width=265)
param_eaf_frame.grid(row=0, column=0, pady=5, padx=5)
param_eaf_frame.grid_propagate(False)

param_eafload_lb = tk.Label(param_eaf_frame, text='Carga objetivo EAF:')
param_eafload_unit_lb = tk.Label(param_eaf_frame, text='[ton]')
load_eaf = tk.StringVar()
load_eaf.set('35')
param_eafload_e = ttk.Spinbox(param_eaf_frame, width=7, textvariable=load_eaf, justify='center', from_=25, to=50,
                              increment=1)
param_eafload_lb.grid(row=0, column=0, padx=5, sticky='w', pady=5)
param_eafload_e.grid(row=0, column=1, padx=5, pady=5)
param_eafload_unit_lb.grid(row=0, column=2, padx=5, sticky='w', pady=5)

"""
param_eafvol_lb = tk.Label(param_eaf_frame, text='Volumen útil EAF:')
param_eafvol_unit_lb = tk.Label(param_eaf_frame, text='[m3]')
vol_eaf = tk.StringVar()
vol_eaf.set('30')
param_eafvol_e = ttk.Spinbox(param_eaf_frame, width=7, textvariable=vol_eaf, justify='center', from_=25, to=50,
                             increment=1)
param_eafvol_lb.grid(row=1, column=0, padx=5, sticky='w', pady=5)
param_eafvol_e.grid(row=1, column=1, padx=5, pady=5)
param_eafvol_unit_lb.grid(row=1, column=2, padx=5, sticky='w', pady=5)
"""

param_eafprod_lb = tk.Label(param_eaf_frame, text='Productividad EAF:')
param_eafprod_unit_lb = tk.Label(param_eaf_frame, text='[ton/col]')
prod_eaf = tk.StringVar()
prod_eaf.set('31.2')
param_eafprod_e = ttk.Spinbox(param_eaf_frame, width=7, textvariable=prod_eaf, justify='center', from_=25, to=50,
                              increment=0.1, command=calc_ncol)
param_eafprod_lb.grid(row=2, column=0, padx=5, sticky='w', pady=5)
param_eafprod_e.grid(row=2, column=1, padx=5, pady=5)
param_eafprod_unit_lb.grid(row=2, column=2, padx=5, sticky='w', pady=5)

param_eafcol_lb = tk.Label(param_eaf_frame, text='Coladas al mes:')
param_eafcol_unit_lb = tk.Label(param_eaf_frame, text='[col/mes]')
n_col = tk.StringVar()
param_eafcol_e = ttk.Entry(param_eaf_frame, width=9, textvariable=n_col, justify='center', state='readonly')
param_eafcol_lb.grid(row=3, column=0, padx=5, sticky='w', pady=5)
param_eafcol_e.grid(row=3, column=1, padx=5, pady=5)
param_eafcol_unit_lb.grid(row=3, column=2, padx=5, sticky='w', pady=5)

param_pequim_frame = tk.LabelFrame(param_frame, text='Paq. Químico y Eléctrico', height=310, width=265)
param_pequim_frame.grid(row=1, column=0, pady=5, padx=5)
param_pequim_frame.grid_propagate(False)

param_potprom_lb = ttk.Label(param_pequim_frame, text='Pot. prom. cesta:')
param_potprom_unit_lb = tk.Label(param_pequim_frame, text='[MW]')
pot_prom_cesta = tk.StringVar()
pot_prom_cesta.set('28.2')
param_potprom_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=pot_prom_cesta, justify='center', from_=10,
                              to=50, increment=0.1)
param_potprom_lb.grid(row=0, column=0, padx=5, sticky='w', pady=5)
param_potprom_e.grid(row=0, column=1, padx=5, pady=5)
param_potprom_unit_lb.grid(row=0, column=2, padx=5, sticky='w', pady=5)

param_potpromaf_lb = ttk.Label(param_pequim_frame, text='Pot. prom. afino:')
param_potpromaf_unit_lb = tk.Label(param_pequim_frame, text='[MW]')
pot_promaf_cesta = tk.StringVar()
pot_promaf_cesta.set('34')
param_potpromaf_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=pot_promaf_cesta, justify='center', from_=10,
                                to=50, increment=0.1)
param_potpromaf_lb.grid(row=1, column=0, padx=5, sticky='w', pady=5)
param_potpromaf_e.grid(row=1, column=1, padx=5, pady=5)
param_potpromaf_unit_lb.grid(row=1, column=2, padx=5, sticky='w', pady=5)

param_separator1 = ttk.Separator(param_pequim_frame, orient='horizontal')
param_separator1.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

param_nkt_lb = ttk.Label(param_pequim_frame, text='Número lanzas:')
nkt = tk.StringVar()
nkt.set('3')
param_nkt_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=nkt, justify='center', from_=1, to=10, increment=1)
param_nkt_lb.grid(row=3, column=0, padx=5, sticky='w', pady=5)
param_nkt_e.grid(row=3, column=1, padx=5, pady=5)

param_kt_ox_lb = ttk.Label(param_pequim_frame, text='Flujo O2 lanza:')
param_kt_ox_unit_lb = tk.Label(param_pequim_frame, text='[m3/h]')
ox_flux = tk.StringVar()
ox_flux.set('900')
param_kt_ox_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ox_flux, justify='center', from_=700, to=2600,
                            increment=10)
param_kt_ox_lb.grid(row=4, column=0, padx=5, sticky='w', pady=5)
param_kt_ox_e.grid(row=4, column=1, padx=5, pady=5)
param_kt_ox_unit_lb.grid(row=4, column=2, padx=5, sticky='w', pady=5)

param_kt_oxaf_lb = ttk.Label(param_pequim_frame, text='Flujo O2 lanza afino:')
param_kt_oxaf_unit_lb = tk.Label(param_pequim_frame, text='[m3/h]')
ox_flux_af = tk.StringVar()
ox_flux_af.set('1300')
param_kt_oxaf_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ox_flux_af, justify='center', from_=700,
                              to=2600, increment=10)
param_kt_oxaf_lb.grid(row=5, column=0, padx=5, sticky='w', pady=5)
param_kt_oxaf_e.grid(row=5, column=1, padx=5, pady=5)
param_kt_oxaf_unit_lb.grid(row=5, column=2, padx=5, sticky='w', pady=5)

param_ereac_lb = ttk.Label(param_pequim_frame, text='Energía reacc.:')
param_ereac_unit_lb = tk.Label(param_pequim_frame, text='[kWh/m3]')
ereac = tk.StringVar()
ereac.set('4.4')
param_ereac_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ereac, justify='center', from_=2.0, to=20.0,
                            increment=0.1)
param_ereac_lb.grid(row=6, column=0, padx=5, sticky='w', pady=5)
param_ereac_e.grid(row=6, column=1, padx=5, pady=5)
param_ereac_unit_lb.grid(row=6, column=2, padx=5, sticky='w', pady=1)

param_ereac_af_lb = ttk.Label(param_pequim_frame, text='Energía oxidación:')
param_ereac_af_unit_lb = tk.Label(param_pequim_frame, text='[kWh/m3]')
ereac_af = tk.StringVar()
ereac_af.set('7.2')
param_ereac_af_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ereac_af, justify='center', from_=2.0, to=20.0,
                               increment=0.1)
param_ereac_af_lb.grid(row=7, column=0, padx=5, sticky='w', pady=5)
param_ereac_af_e.grid(row=7, column=1, padx=5, pady=5)
param_ereac_af_unit_lb.grid(row=7, column=2, padx=5, sticky='w', pady=1)

param_effreac_lb = ttk.Label(param_pequim_frame, text='Eficiencia reacc.:')
param_effreac_unit_lb = tk.Label(param_pequim_frame, text='[%]')
eff_reac = tk.StringVar()
eff_reac.set('70')
param_effreac_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=eff_reac, justify='center', from_=0, to=100,
                              increment=1)
param_effreac_lb.grid(row=8, column=0, padx=5, sticky='w', pady=5)
param_effreac_e.grid(row=8, column=1, padx=5, pady=5)
param_effreac_unit_lb.grid(row=8, column=2, padx=5, sticky='w', pady=1)

param_effmelt_lb = ttk.Label(param_pequim_frame, text='Eficiencia fund.:')
param_effmelt_unit_lb = tk.Label(param_pequim_frame, text='[%]')
eff_melt = tk.StringVar()
eff_melt.set('78')
param_effmelt_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=eff_melt, justify='center', from_=0, to=100,
                              increment=1)
param_effmelt_lb.grid(row=9, column=0, padx=5, sticky='w', pady=5)
param_effmelt_e.grid(row=9, column=1, padx=5, pady=5)
param_effmelt_unit_lb.grid(row=9, column=2, padx=5, sticky='w', pady=1)

param_bc_frame = tk.LabelFrame(param_frame, text='Cestas', height=440, width=305)
param_bc_frame.grid(row=0, column=1, pady=5, padx=10, rowspan=2)
param_bc_frame.grid_propagate(False)

param_bcload_lb = tk.Label(param_bc_frame, text='Carga máx. cesta:')
param_bcload_unit_lb = tk.Label(param_bc_frame, text='[ton]')
load_cesta = tk.StringVar()
load_cesta.set('15')
param_bcload_e = ttk.Spinbox(param_bc_frame, width=7, textvariable=load_cesta, justify='center', from_=5, to=30,
                             increment=0.2)
param_bcload_lb.grid(row=0, column=0, padx=5, sticky='w', pady=5)
param_bcload_e.grid(row=0, column=1, padx=5, pady=5)
param_bcload_unit_lb.grid(row=0, column=2, padx=5, sticky='w', pady=5)

param_bcvol_lb = ttk.Label(param_bc_frame, text='Volumen máx. cesta:')
param_bcvol_unit_lb = tk.Label(param_bc_frame, text='[m3]')
volume_cesta = tk.StringVar()
volume_cesta.set('28')
param_bcvol_e = ttk.Spinbox(param_bc_frame, width=7, textvariable=volume_cesta, justify='center', from_=10, to=50,
                            increment=0.2)
param_bcvol_lb.grid(row=1, column=0, padx=5, sticky='w', pady=5)
param_bcvol_e.grid(row=1, column=1, padx=5, pady=5)
param_bcvol_unit_lb.grid(row=1, column=2, padx=5, sticky='w', pady=5)

param_bcfactor_lb = ttk.Label(param_bc_frame, text='Factor de llenado:')
param_bcfactor_unit_lb = tk.Label(param_bc_frame, text='[%]')
factor_cesta = tk.StringVar()
factor_cesta.set('97')
param_bcfactor_e = ttk.Spinbox(param_bc_frame, width=7, textvariable=factor_cesta, justify='center', from_=0, to=100,
                               increment=1)
param_bcfactor_lb.grid(row=2, column=0, padx=5, sticky='w', pady=5)
param_bcfactor_e.grid(row=2, column=1, padx=5, pady=5)
param_bcfactor_unit_lb.grid(row=2, column=2, padx=5, sticky='w', pady=5)

param_bc_separator1 = ttk.Separator(param_bc_frame, orient='horizontal')
param_bc_separator1.grid(row=3, column=0, columnspan=3, sticky='nsew',padx=5)

param_bc_lb = tk.Label(param_bc_frame, text='Seleccionar Chatarras Base:')
param_bc_lb.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky='w')

param_bc_bscrap_frame = tk.LabelFrame(param_bc_frame)
param_bc_bscrap_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
param_bc_bscrap_frame.pack_propagate(True)

param_bscrap_cn = tk.Canvas(param_bc_bscrap_frame, confine=True, width=235)
param_bscrap_cn.config(highlightthickness=0)
param_cn_scb = ttk.Scrollbar(param_bc_bscrap_frame, orient='vertical', command=param_bscrap_cn.yview)
param_sc_frame = tk.Frame(param_bscrap_cn)
param_sc_frame.bind('<Configure>', lambda e: param_bscrap_cn.configure(scrollregion=param_bscrap_cn.bbox('all')))
param_bscrap_cn.create_window((0, 0), window=param_sc_frame, anchor='nw')
param_bscrap_cn.pack(side='left', fill='both', expand=True, padx=10)
param_cn_scb.pack(side='right', fill='y', expand=False)


### Reporte

rep_disp_frame = tk.LabelFrame(rep_frame, text='Indicadores de Proceso',  width=1120, height=180)
rep_table_frame = tk.Frame(rep_frame, width=1120, height=200)
rep_disp_frame.grid(row=0, column=0)
rep_table_frame.grid(row=1, column=0, pady=10)
rep_disp_frame.grid_propagate(False)

rep_scrap_cost_lb = tk.Label(rep_disp_frame, text='Costo unitario chatarra:')
rep_scrap_cost_value_lb = tk.Label(rep_disp_frame, text='----')
rep_scrap_cost_unit_lb = tk.Label(rep_disp_frame, text='[$/ton]')
rep_scrap_cost_lb.grid(row=0, column=0, pady=5, padx=5, sticky='w')
rep_scrap_cost_value_lb.grid(row=0, column=1, pady=5, padx=5)
rep_scrap_cost_unit_lb.grid(row=0, column=2, pady=5, padx=5, sticky='ew')

rep_rho_mix_lb = tk.Label(rep_disp_frame, text='Densidad aparente:')
rep_rho_mix_value_lb = tk.Label(rep_disp_frame, text='----')
rep_rho_mix_unit_lb = tk.Label(rep_disp_frame, text='[ton/m3]')
rep_rho_mix_lb.grid(row=1, column=0, pady=5, padx=5, sticky='w')
rep_rho_mix_value_lb.grid(row=1, column=1, pady=5, padx=5)
rep_rho_mix_unit_lb.grid(row=1, column=2, pady=5, padx=5, sticky='ew')

rep_rend_mix_lb = tk.Label(rep_disp_frame, text='Rendimiento prom.:')
rep_rend_mix_value_lb = tk.Label(rep_disp_frame, text='----')
rep_rend_mix_unit_lb = tk.Label(rep_disp_frame, text='[%]')
rep_rend_mix_lb.grid(row=2, column=0, pady=5, padx=5, sticky='w')
rep_rend_mix_value_lb.grid(row=2, column=1, pady=5, padx=5)
rep_rend_mix_unit_lb.grid(row=2, column=2, pady=5, padx=5, sticky='ew')

rep_eunit_lb = tk.Label(rep_disp_frame, text='Energía fundición prom.:')
rep_eunit_value_lb = tk.Label(rep_disp_frame, text='----')
rep_eunit_unit_lb = tk.Label(rep_disp_frame, text='[kWh/ton]')
rep_eunit_lb.grid(row=3, column=0, pady=5, padx=5, sticky='w')
rep_eunit_value_lb.grid(row=3, column=1, pady=5, padx=5)
rep_eunit_unit_lb.grid(row=3, column=2, pady=5, padx=5, sticky='ew')

rep_etotal_lb = tk.Label(rep_disp_frame, text='Energía total:')
rep_etotal_value_lb = tk.Label(rep_disp_frame, text='----')
rep_etotal_unit_lb = tk.Label(rep_disp_frame, text='[kWh]')
rep_etotal_lb.grid(row=4, column=0, pady=5, padx=5, sticky='w')
rep_etotal_value_lb.grid(row=4, column=1, pady=5, padx=5)
rep_etotal_unit_lb.grid(row=4, column=2, pady=5, padx=5, sticky='ew')

l_kpi_labels = [rep_scrap_cost_value_lb, rep_rho_mix_value_lb, rep_rend_mix_value_lb, rep_eunit_value_lb, rep_etotal_value_lb]

table_rep = Table(rep_table_frame, showstatusbar=True, width=1050, height=200)
table_rep.show()


### Cestas

cesta_ntb = ttk.Notebook(cesta_frame, height=425, width=1080)
cesta_general_frame = tk.Frame(cesta_ntb)
cesta_preajuste_frame = tk.Frame(cesta_ntb)

cestas_table_frame = tk.Frame(cesta_general_frame)
cestas_table_frame.grid(row=0, column=0)
table_cesta = Table(cestas_table_frame, showstatusbar=True, width=980, height=300)
table_cesta.show()

cesta_lblgrid = tkt.LabelGrid(cesta_preajuste_frame, num_of_columns=3, headers=['Cestas', 'FIN DE FASE', 'Peso'])
cesta_lblgrid.grid(row=0, column=0)

cesta_ntb.add(cesta_general_frame, text='General', padding=15)
cesta_ntb.add(cesta_preajuste_frame, text='Preajuste', padding=15)


cesta_ntb.grid(row=0, column=1, sticky='nsew', padx=20)

############3

root.bind("<Configure>", updateScroll())
root.mainloop()

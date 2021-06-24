import sqlite3
from pandastable import Table
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font
from PIL import ImageTk, Image
import Optimizador as Opt
import Meltop as Mlt
import tk_tools as tkt
import pickle as pkl
from math import isnan
import tkcalendar as tkc
from datetime import datetime as date_t
from datetime import timedelta
import calendar as clndr
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import coes_scrapper
import matplotlib.pyplot as plt
import numpy as np



# Creación y seteo de la ventana raíz
root = tk.Tk()
root.title("Kedalion MOS v.1.1")

ked_icon = tk.PhotoImage(file='Images\\kedalion_logo.png')

root.iconphoto(False, ked_icon)
root.state('zoomed')
root.tk.call('tk', 'scaling')


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
def _on_mousewheel(event):
    container.yview_scroll(int(-1 * (event.delta / 120)), "units")
    updateScroll()


def update_df_inventario():
    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    l_comp_scrap_names = df_inventario['Nombre'].tolist()

    return l_comp_scrap_names


def update_df_adiciones():
    df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)
    l_adiciones_names = df_adiciones['Nombre'].tolist()

    return l_adiciones_names


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


    elif frame_indx == 2:
        res_load_inv()

    elif frame_indx == 3:
        res_load_inv()
        param_load_inv()
        param_checkifprod()
        calc_ncol()

    elif frame_indx == 5:

        try:

            if start_sim.success.get() == True:
                bucket_sim()
        except AttributeError:
            pass

    elif frame_indx == 7:
        nmetal_query()

    elif frame_indx == 8:
        adiciones_query()


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

        elif current_frame.get() == 7:
            df_1 = pd.read_sql_query("SELECT * FROM rendmetalico_data", conn)
            df_1 = df_1[df_1.Nombre != '']
            df_2 = table_nmetal.model.df
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


def nmet_save_sql():
    df_nmet.reset_index(drop=True, inplace=True)
    df_nmet.to_sql('rendmetalico_data', conn, if_exists='replace', index=False)


def adiciones_save_sql():
    df_adiciones.reset_index(drop=True, inplace=True)
    df_adiciones.to_sql('adit_data', conn, if_exists='replace', index=False)


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


def nmetal_submit_top(*args):
    def nmetal_submit(*args):

        saving = messagebox.askquestion("Guardar", "¿Desea sobreescribir los datos?")

        if saving == 'yes':

            name = nmet_top_cmb.get()
            l_submit_values = []
            for entry in l_nmet_entries:
                try:
                    l_submit_values.append(float(entry.get()))

                except ValueError:
                    l_submit_values.append(0.0)

            l_nmet_current_scrap_names = df_nmet['Nombre'].tolist()

            if name not in l_nmet_current_scrap_names:

                cur.execute(
                    "INSERT INTO rendmetalico_data VALUES (:f_nombre, :f_fe, :f_cao, :f_mgo, :f_al, :f_sio, :f_mno, :f_po, :f_feo, :f_s, :f_pc)",
                    {
                        'f_nombre': name,
                        'f_fe': l_submit_values[0],
                        'f_cao': l_submit_values[1],
                        'f_mgo': l_submit_values[2],
                        'f_al': l_submit_values[3],
                        'f_sio': l_submit_values[4],
                        'f_mno': l_submit_values[5],
                        'f_po': l_submit_values[6],
                        'f_feo': l_submit_values[7],
                        'f_s': l_submit_values[8],
                        'f_pc': l_submit_values[9]

                    })

                conn.commit()
                nmetal_query()
                entry_level.destroy()

            else:
                l_submit_values.insert(0, name)
                df_nmet.loc[df_nmet['Nombre'] == name, :] = l_submit_values
                df_nmet.reset_index(drop=True, inplace=True)
                df_nmet.to_sql('rendmetalico_data', conn, if_exists='replace', index=False)

            nmetal_query()
            entry_level.destroy()

        else:
            return

    def nmet_enable_entries(*args):

        l_df_nmet_names = df_nmet['Nombre'].tolist()

        if nmet_scrap_name.get() in l_df_nmet_names:
            l_values = (df_nmet.loc[df_nmet['Nombre'] == nmet_scrap_name.get(), 'Fe':'P/C']).values.tolist()
        else:
            l_values = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        if nmet_top_cmb.get() == " ":

            for entry in l_nmet_entries:
                entry.delete(0, tk.END)
                entry.config(state='disabled')

            nmetal_top_save_b.config(state='disabled')

        else:

            x = 0

            for entry in l_nmet_entries:
                entry.config(state='normal')

                if isnan(l_values[0][x]):
                    entry.delete(0, tk.END)
                    entry.insert(0, " ")
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, l_values[0][x])
                x += 1
            nmetal_top_save_b.config(state='normal')

    df_nmet = pd.read_sql_query("SELECT * FROM rendmetalico_data", conn)

    entry_level = tk.Toplevel(root)
    entry_level.title("Añadir composición de tierra en chatarra")
    entry_level.wm_geometry("510x200")
    entry_level.iconbitmap('Images/No-metalicos.ico')
    entry_level.grab_set()

    entry_title_lb = tk.Label(entry_level, text='Seleccionar chatarra: ')
    entry_title_lb.grid(row=0, column=0, padx=10, pady=10, sticky='e')

    entry_data_frame = tk.LabelFrame(entry_level, width=470, height=90)
    entry_data_frame.grid(row=1, column=0, pady=5, padx=20, sticky='nsew', columnspan=2)
    entry_data_frame.grid_propagate(False)

    l_nmet_name = ["Fe met.", "CaO", "MgO", "Al2O3", "SiO2", "MnO", "P2O5", "FeO", "S", "P/C"]
    l_nmet_entries = []

    for x in range(len(l_nmet_name)):
        nmet_lb = tk.Label(entry_data_frame, text=l_nmet_name[x])
        nmet_e = ttk.Entry(entry_data_frame, width=5, state='disabled')
        l_nmet_entries.append(nmet_e)

        if x < 5:
            nmet_lb.grid(row=0, column=x * 2, pady=10, padx=5)
            nmet_e.grid(row=0, column=(x * 2) + 1, pady=10, padx=5)
        else:
            nmet_lb.grid(row=1, column=x * 2 - 10, pady=10, padx=5)
            nmet_e.grid(row=1, column=(x * 2) + 1 - 10, pady=10, padx=5)

    l_nmet_scrap_names = update_df_inventario()
    l_nmet_scrap_names.insert(0, " ")
    nmet_scrap_name = tk.StringVar()

    nmet_scrap_name.set(l_nmet_scrap_names[0])
    nmet_top_cmb = ttk.Combobox(entry_level, width=22, textvariable=nmet_scrap_name, values=l_nmet_scrap_names,
                                state='readonly')
    nmet_top_cmb.bind('<<ComboboxSelected>>', nmet_enable_entries)
    nmet_top_cmb.grid(row=0, column=1, pady=10, padx=5, sticky='w')

    nmetal_top_save_b = ttk.Button(entry_level, text='Guardar', state='disabled', command=nmetal_submit)
    nmetal_top_save_b.grid(row=2, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)

    nmetal_top_quit_b = ttk.Button(entry_level, text='Salir', command=entry_level.destroy)
    nmetal_top_quit_b.grid(row=2, column=1, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)


def comp_submit_top(*args):

    def camp_submit(*args):

        saving = messagebox.askquestion("Guardar", "¿Desea sobreescribir los datos?")

        if saving == 'yes':

            name = comp_top_cmb.get()
            l_submit_values = []

            for entry in l_comp_top_entries:

                try:
                    l_submit_values.append(float(entry.get()))

                except ValueError:
                    l_submit_values.append(0.0)

            l_comp_current_scrap_names = df_comp['Nombre'].tolist()

            if name not in l_comp_current_scrap_names:

                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO comp_data VALUES (:f_nombre, :f_c, :f_mn, :f_si, :f_p, :f_cr, :f_s, :f_cu, :f_ni, :f_mo)",
                    {
                        'f_nombre': comp_top_cmb.get(),
                        'f_c': l_submit_values[0],
                        'f_mn': l_submit_values[1],
                        'f_si': l_submit_values[2],
                        'f_p': l_submit_values[3],
                        'f_cr': l_submit_values[4],
                        'f_s': l_submit_values[5],
                        'f_cu': l_submit_values[6],
                        'f_ni': l_submit_values[7],
                        'f_mo': l_submit_values[8]
                    })

                conn.commit()
                comp_query()
                entry_comp_level.destroy()

            else:
                l_submit_values.insert(0, name)
                df_comp.loc[df_comp['Nombre'] == name, :] = l_submit_values
                df_comp.reset_index(drop=True, inplace=True)
                df_comp.to_sql('comp_data', conn, if_exists='replace', index=False)

            comp_query()
            entry_comp_level.destroy()

        else:
            return

    def comp_enable_entries(*args):

        l_df_comp_names = df_comp['Nombre'].tolist()

        if comp_top_scrap_name.get() in l_df_comp_names:
            l_values = (df_comp.loc[df_comp['Nombre'] == comp_top_scrap_name.get(), 'C':]).values.tolist()
        else:
            l_values = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        if comp_top_cmb.get() == " ":

            for entry in l_comp_top_entries:
                entry.delete(0, tk.END)
                entry.config(state='disabled')

            comp_top_save_b.config(state='disabled')

        else:

            print(l_values)
            x = 0

            for entry in l_comp_top_entries:
                entry.config(state='normal')

                if isnan(l_values[0][x]):
                    entry.delete(0, tk.END)
                    entry.insert(0, " ")
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, l_values[0][x])
                x += 1
            comp_top_save_b.config(state='normal')

    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)

    entry_comp_level = tk.Toplevel(root)
    entry_comp_level.title("Añadir contaminantes en chatarra")
    entry_comp_level.wm_geometry("510x200")
    entry_comp_level.iconbitmap('Images/composicion_i.ico')
    entry_comp_level.grab_set()

    entry_title_lb = tk.Label(entry_comp_level, text='Seleccionar chatarra: ')
    entry_title_lb.grid(row=0, column=0, padx=10, pady=10, sticky='e')

    entry_data_frame = tk.LabelFrame(entry_comp_level, width=470, height=90)
    entry_data_frame.grid(row=1, column=0, pady=5, padx=20, sticky='nsew', columnspan=2)

    for x in range(10):
        entry_data_frame.grid_columnconfigure(x, weight=1)

    entry_data_frame.grid_propagate(False)

    l_comp_name = ["C", "Mn", "Si", "P", "Cr", "S", "Cu", "Ni", "Mo"]
    l_comp_top_entries = []

    for x in range(len(l_comp_name)):
        comp_lb = tk.Label(entry_data_frame, text=l_comp_name[x])
        comp_e = ttk.Entry(entry_data_frame, width=5, state='disabled')
        l_comp_top_entries.append(comp_e)

        if x < 5:
            comp_lb.grid(row=0, column=x * 2, pady=10, padx=5)
            comp_e.grid(row=0, column=(x * 2) + 1, pady=10, padx=5)
        else:
            comp_lb.grid(row=1, column=x * 2 - 10, pady=10, padx=5)
            comp_e.grid(row=1, column=(x * 2) + 1 - 10, pady=10, padx=5)

    l_comp_scrap_names = update_df_inventario()
    l_comp_scrap_names.insert(0, " ")

    comp_top_scrap_name = tk.StringVar()
    comp_top_scrap_name.set(l_comp_scrap_names[0])
    comp_top_cmb = ttk.Combobox(entry_comp_level, width=22, textvariable=comp_top_scrap_name, values=l_comp_scrap_names,
                                state='readonly')
    comp_top_cmb.bind('<<ComboboxSelected>>', comp_enable_entries)
    comp_top_cmb.grid(row=0, column=1, pady=10, padx=5, sticky='w')

    comp_top_save_b = ttk.Button(entry_comp_level, text='Guardar', state='disabled', command=camp_submit)
    comp_top_save_b.grid(row=2, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)

    comp_top_quit_b = ttk.Button(entry_comp_level, text='Salir', command=entry_comp_level.destroy)
    comp_top_quit_b.grid(row=2, column=1, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)


def adiciones_submit_top(*args):

    def adiciones_submit(*args):

        saving = messagebox.askquestion("Guardar", "¿Desea sobreescribir los datos?")

        if saving == 'yes':

            name = adiciones_top_cmb.get()
            l_submit_values = []
            for entry in l_adiciones_entries:
                try:
                    l_submit_values.append(float(entry.get()))

                except ValueError:
                    l_submit_values.append(0.0)

            l_adiciones_current_scrap_names = df_adiciones['Nombre'].tolist()

            if name not in l_adiciones_current_scrap_names:

                cur.execute(
                    "INSERT INTO adit_data VALUES (:f_nombre, :f_precio, :f_inv, :f_rho, :f_cao, :f_mgo, :f_c, :f_h2o, :f_s, :f_al2o3, :f_sio2)",
                    {
                        'f_nombre': name,
                        'f_precio': int(l_submit_values[0]),
                        'f_inv': l_submit_values[1],
                        'f_rho': l_submit_values[2],
                        'f_cao': l_submit_values[3],
                        'f_mgo': l_submit_values[4],
                        'f_c': l_submit_values[5],
                        'f_h2o': l_submit_values[6],
                        'f_s': l_submit_values[7],
                        'f_al2o3': l_submit_values[8],
                        'f_sio2': l_submit_values[9]

                    })

                conn.commit()
                adiciones_query()
                entry_level.destroy()

            else:
                l_submit_values.insert(0, name)
                df_adiciones.loc[df_adiciones['Nombre'] == name, :] = l_submit_values
                df_adiciones.reset_index(drop=True, inplace=True)
                df_adiciones.to_sql('adit_data', conn, if_exists='replace', index=False)

            adiciones_query()
            entry_level.destroy()

        else:
            return

    def adiciones_enable_entries(*args):

        l_df_adiciones_names = df_adiciones['Nombre'].tolist()

        if adiciones_scrap_name.get() in l_df_adiciones_names:
            l_values = (df_adiciones.loc[df_adiciones['Nombre'] == adiciones_scrap_name.get(), 'Precio':'SiO2']).values.tolist()
            print(l_values)
        else:
            l_values = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        if adiciones_top_cmb.get() == " ":

            for entry in l_adiciones_entries:
                entry.delete(0, tk.END)
                entry.config(state='disabled')

            adiciones_top_save_b.config(state='disabled')

        else:

            x = 0

            for entry in l_adiciones_entries:
                entry.config(state='normal')

                if isnan(float(l_values[0][x])):
                    entry.delete(0, tk.END)
                    entry.insert(0, " ")
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, l_values[0][x])
                x += 1
            adiciones_top_save_b.config(state='normal')

    df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)

    entry_level = tk.Toplevel(root)
    entry_level.title("Añadir datos de aditivo")
    entry_level.wm_geometry("510x200")
    entry_level.iconbitmap('Images\\Adicion.ico')
    entry_level.grab_set()

    entry_title_lb = tk.Label(entry_level, text='Seleccionar o ingresar nombre: ')
    entry_title_lb.grid(row=0, column=0, padx=10, pady=10, sticky='e')

    entry_data_frame = tk.LabelFrame(entry_level, width=470, height=90)
    entry_data_frame.grid(row=1, column=0, pady=5, padx=20, sticky='nsew', columnspan=2)
    entry_data_frame.grid_propagate(False)

    l_adiciones_name = ["Precio", "Inv.", "Dens.", "CaO", "MgO", "C", "H2O", "S", "Al2O3", "SiO2"]
    l_adiciones_entries = []

    for x in range(len(l_adiciones_name)):
        adi_lb = tk.Label(entry_data_frame, text=l_adiciones_name[x])
        adi_e = ttk.Entry(entry_data_frame, width=5, state='disabled')
        l_adiciones_entries.append(adi_e)

        if x < 5:
            adi_lb.grid(row=0, column=x * 2, pady=10, padx=5)
            adi_e.grid(row=0, column=(x * 2) + 1, pady=10, padx=5)
        else:
            adi_lb.grid(row=1, column=x * 2 - 10, pady=10, padx=5)
            adi_e.grid(row=1, column=(x * 2) + 1 - 10, pady=10, padx=5)

    l_adiciones_scrap_names = update_df_adiciones()
    l_adiciones_scrap_names.insert(0, " ")
    adiciones_scrap_name = tk.StringVar()

    adiciones_scrap_name.set(l_adiciones_scrap_names[0])
    adiciones_top_cmb = ttk.Combobox(entry_level, width=22, textvariable=adiciones_scrap_name, values=l_adiciones_scrap_names)
    #adiciones_top_cmb.bind('<<ComboboxSelected>>', nmet_enable_entries)
    adiciones_scrap_name.trace('w', adiciones_enable_entries)
    adiciones_top_cmb.grid(row=0, column=1, pady=10, padx=5, sticky='w')

    adiciones_top_save_b = ttk.Button(entry_level, text='Guardar', state='disabled', command=adiciones_submit)
    adiciones_top_save_b.grid(row=2, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)

    adiciones_top_quit_b = ttk.Button(entry_level, text='Salir', command=entry_level.destroy)
    adiciones_top_quit_b.grid(row=2, column=1, pady=10, columnspan=1, ipadx=10, ipady=1.5, padx=5)


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


def nmetal_query():
    global df_nmet

    df_nmet = pd.read_sql_query("SELECT * FROM rendmetalico_data", conn)

    conn.commit()

    table_nmetal.model.df = df_nmet
    table_nmetal.autoResizeColumns()
    table_nmetal.redraw()


def adiciones_query():
    global df_adiciones

    df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)

    conn.commit()

    table_adiciones.model.df = df_adiciones
    table_adiciones.autoResizeColumns()
    table_adiciones.redraw()


##
def inv_delete():
    ask = messagebox.askquestion(title='Eliminar', message='¿Desea eliminar este dato?')
    if ask == 'yes':

        row = table_scrap.getSelectedRows()
        del_item_name = (row['Nombre'].tolist())[0]

        cur = conn.cursor()
        cur.execute('DELETE FROM scrap_data WHERE Nombre=?', (del_item_name,))
        cur.execute('DELETE FROM comp_data WHERE Nombre=?', (del_item_name,))
        cur.execute('DELETE FROM rendmetalico_data WHERE Nombre=?', (del_item_name,))
        conn.commit()

        inv_query()
        comp_query()
        nmetal_query()
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


def nmet_delete():
    ask = messagebox.askquestion(title='Eliminar', message='¿Desea eliminar este dato?')
    if ask == 'yes':
        row = table_nmetal.getSelectedRows()
        del_item_name = (row['Nombre'].tolist())[0]

        cur = conn.cursor()
        cur.execute('DELETE FROM rendmetalico_data WHERE Nombre=?', (del_item_name,))
        conn.commit()

        nmetal_query()

    else:
        return


def adiciones_delete():

    ask = messagebox.askquestion(title='Eliminar', message='¿Desea eliminar este dato?')
    if ask == 'yes':
        row = table_adiciones.getSelectedRows()
        del_item_name = (row['Nombre'].tolist())[0]

        cur = conn.cursor()
        cur.execute('DELETE FROM adit_data WHERE Nombre=?', (del_item_name,))
        conn.commit()

        adiciones_query()

    else:
        return


##
def param_checkifprod():
    try:
        float(res_prod_e.get())
    except:
        messagebox.showwarning(title='Advertencia', message='Aún no se ha especificado una producción objetivo')


def update_progress(update):
    progress.p_value.set(progress.p_value.get() + update)


def progress(*args):
    progress.progress_frame = tk.LabelFrame(tv_frame, height=75, width=200)

    progress.progress_label = tk.Label(progress.progress_frame, text="Calculando mix...")
    progress.progress_label.grid(row=4, column=0, pady=0, sticky='nsew')
    progress.p_value = tk.IntVar()
    progress.p_value.set(10)
    progress.progress_bar = ttk.Progressbar(progress.progress_frame, orient='horizontal', length=180,
                                            mode='determinate', maximum=100, variable=(progress.p_value))
    progress.progress_bar.grid(row=5, column=0, pady=10, padx=8, sticky='ew')

    progress.progress_frame.grid(row=4, column=0, columnspan=2)
    progress.progress_frame.grid_propagate(False)

    progress.progress_frame.after(500, start_sim)


def update_potprom(*args):

    try:
        sum = 0

        for pot in l_pot_values:
            sum += float(pot.get())

        pot_prom = round(sum / num_cestas.get(), 1)
        pot_prom_cesta.set(str(pot_prom))

    except ValueError:
        pot_prom_cesta.set(0)


def calc_adi_nmetal():

    df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)
    adiciones_dict = {}
    l_wrong_cols = ['Nombre', 'Precio', 'Inventario', 'Densidad']
    l_keys = []

    for nmetal in list(df_adiciones.columns):

        l_comp = []
        if nmetal in l_wrong_cols:
            pass

        else:
            for aditivo in l_param_adi_valid_nombres:

                comp = df_adiciones[df_adiciones['Nombre']==aditivo][nmetal].tolist()
                l_comp.append(comp)

            adiciones_dict[nmetal] = l_comp


    l_del_key = []
    for key in adiciones_dict:

        sum = 0
        for x in range(len(l_param_adi_valid_nombres)):
            sum += adiciones_dict[key][x][0]

        if sum <= 0:
            l_del_key.append(key)

    for key in l_del_key:
        adiciones_dict.pop(key)

    l_aditivos_peso = []
    for entry in l_param_adi_entries:
        peso = float(entry.get())
        l_aditivos_peso.append(peso)

    for contaminante in adiciones_dict:
        sum_cont = 0
        for x in range(len(l_aditivos_peso)):
            sum_cont += l_aditivos_peso[x] * adiciones_dict[contaminante][x][0]/100
        adiciones_dict[contaminante] = round(sum_cont, 3)

    return adiciones_dict


def start_sim():

    global df_results, df_buckets, l_kpi, df_cont

    param_load_inv()
    calc_ncol()

    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)
    df_nmet = pd.read_sql_query("SELECT * FROM rendmetalico_data", conn)

    carga_eaf = float(load_eaf.get())
    vol_cesta = float(volume_cesta.get())
    carga_cesta = float(load_cesta.get())
    n_coladas = float(n_col.get())
    fact_cesta = float(factor_cesta.get())/100

    if auto_cestas.get() == True:
        num_cestas.set("1")

    n_cestas = int(num_cestas.get())

    input_prod = int(prod_obj.get())

    epsilon = tk.DoubleVar()
    epsilon.set(0)

    l_lifeline = []
    for slide in gen_slides.l_res_slides:
        res_ll = (float(slide.get()) / 100)
        l_lifeline.append(res_ll)

    base_scrap_dict = {}
    indx = 0

    for value in gen_checkboxes.l_values:

        if value.get() == True:
            scrap = gen_checkboxes.l_chbx[indx].cget('text')
            base = float(gen_checkboxes.l_entries[indx].get())
            b_max = float(gen_checkboxes.l_entries_max[indx].get())
            base_scrap_dict[scrap] = [base, b_max]
        indx += 1

    start_sim.success = tk.BooleanVar()
    start_sim.success.set(False)
    success = start_sim.success.get()
    n_simu = 0

    while success == False:

        if n_simu >= 8:
            messagebox.showerror('Fallo de simulación',
                                 message='Error: El programa no puedo hallar un mix que satisfaga las condiciones especificadas.')
            simu_success.set(False)
            progress.progress_frame.destroy()
            return

        if Opt.main(df_inventario, df_comp, n_cestas, input_prod, l_lifeline, epsilon.get(), base_scrap_dict, carga_eaf,
                    vol_cesta, carga_cesta, n_coladas, fact_cesta) == True:

            if auto_cestas.get() == True:

                num_cestas.set(num_cestas.get() + 1)
                n_cestas = n_cestas + 1

                progress.progress_frame.after(100, update_progress(20))
                n_simu += 1


            else:
                epsilon.set(epsilon.get() + 0.05)
                progress.progress_frame.after(100, update_progress(20))
                n_simu += 1

            simu_success.set(False)

        else:

            success = True
            df_results, df_buckets, l_kpi, df_cont = Opt.main(df_inventario, df_comp, n_cestas, input_prod, l_lifeline,
                                                              epsilon.get(), base_scrap_dict, carga_eaf, vol_cesta,
                                                              carga_cesta,
                                                              n_coladas, fact_cesta)
            progress.progress_frame.after(100, update_progress(100))
            start_sim.success.set(True)
            simu_success.set(True)

    df_results_disp = df_results.loc[:, 'Carga':]
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

    df_results['Tierra'] = (df_results['Carga'] * (1 - df_results['Rendimiento'])) * 1000

    l_nmet_name = ["Fe", "CaO", "MgO", "Al2O3", "SiO2", "MnO", "P2O5", "FeO", "S", "P/C"]
    df_results = pd.merge(df_results, df_nmet, on='Nombre', how='left')

    tierra_total = round(sum(df_results['Tierra'].tolist()), 2)
    rend_total = round(sum(df_results['Mix'] * df_results['Rendimiento']), 2)
    nmetal_dirtv_label.config(text=str(tierra_total))
    nmetal_rendv_label.config(text=rend_total)

    adi_dict = calc_adi_nmetal()

    j = 0
    for nmetalico in l_nmet_name:

        nmetalico_sum = round(sum((df_results['Tierra'] * df_results[nmetalico] / 100).tolist()), 2)
        print(nmetalico, nmetalico_sum)

        # Se afina el % de FeO en escoria
        if j == 7:
            nmetalico_sum = nmetalico_sum*1.15

        if nmetalico in adi_dict:
            nmetalico_sum += adi_dict[nmetalico]

        l_nmetal_lb[j].config(text=str(round(nmetalico_sum, 2)))

        if j == 0:
            tierra_total = tierra_total - nmetalico_sum

        if j == 9:
            # No se elimina los P/C de la suma de escoria. Antes tierra_total = tierra_total - nmetalico_sum
            tierra_total = tierra_total

        j += 1

    porcentaje_mn = float(df_cont.loc['Mn', 'Valor'])
    mn_scrap = porcentaje_mn * carga_eaf * 10
    mn_scrap_obj = carga_eaf * 0.0007 * 1000
    mn_oxidado = mn_scrap - mn_scrap_obj

    tierra_total += mn_oxidado

    nmetal_dirtv_label.config(text=str(round(tierra_total, 0)))
    b2 = round(float(nmetal_caov_label.cget("text")) / (float(nmetal_siov_label.cget("text"))), 2)
    b3 = round(float(nmetal_caov_label.cget("text")) / (
            float(nmetal_siov_label.cget("text")) + float(nmetal_alov_label.cget("text"))), 2)
    nmetal_b2v_label.config(text=b2)
    nmetal_b3v_label.config(text=b3)

    mgo = 0
    feo = 0

    for x in range(1, 9):

        porcentaje = round((float(l_nmetal_lb[x].cget('text')) / tierra_total) * 100, 2)
        porcentaje_str = str(porcentaje) + ' %'

        if x == 5:
            porcentaje = round(((float(l_nmetal_lb[x].cget('text')) + mn_oxidado) / tierra_total) * 100, 2)
            porcentaje_str = str(porcentaje) + ' %'

        if x == 2:
            mgo = porcentaje

        if x == 7:
            feo = porcentaje

        l_nmetal_lb[x].config(text=porcentaje_str)

    update_ISD_values(mgo, feo)
    update_mgob3_values(mgo, b2)

    energia_mn = 1.5855 * mn_oxidado
    factor_mn_o = 2 * 54.938 / 32
    o2_cons = mn_oxidado / factor_mn_o
    o2_vol = o2_cons / 1.429

    update_comp_values(df_cont, carga_eaf)

    print("manganeso chatarra:", mn_scrap, "manganeso oxidado:", mn_oxidado, "Oxigeno usado:", o2_vol)
    print("energia de ox", energia_mn)

    gen_tabs()

    return


def bucket_sim(*args):

    global l_pot_cesta, l_end_step, l_fund_factor

    n_lanzas = int(nkt.get())

    oxy_flux = (int(ox_flux.get())) * n_lanzas / 60
    oxy_flux_cesta = (int(ox_flux_cesta.get()) * n_lanzas) / 60
    e_reaccion = float(ereac.get())
    kt_factor = float(eff_reac.get()) / 100
    oxy_flux_afino = (int(ox_flux_af.get())) * n_lanzas / 60
    pot_afino = float(pot_promaf_cesta.get())
    e_reacc_ox = float(ereac_af.get())

    try:
        l_pot_cesta = []
        for x in range(num_cestas.get()):
            pot_cesta = float(l_pot_values[x].get())
            l_pot_cesta.append(pot_cesta)

    except NameError:
        pass

    try:
        l_end_step = []
        for x in range(num_cestas.get()):
            end_step = float(l_ends_values[x].get())
            l_end_step.append(end_step)

    except NameError:
        pass

    try:
        l_fund_factor = []
        for x in range(num_cestas.get()):
            fund_factor = float(l_fund_values[x].get()) / 100
            l_fund_factor.append(fund_factor)

    except NameError:
        pass

    try:
        df_cestas, l_e_req, l_peso = Mlt.calc_melting(df_buckets, num_cestas.get(), df_results, l_fund_factor,
                                                      l_pot_cesta,
                                                      oxy_flux, e_reaccion, kt_factor, oxy_flux_afino, pot_afino,
                                                      e_reacc_ox, l_end_step, oxy_flux_cesta)
    except NameError:
        print('xddddddddd')
        return

    df_cestas.reset_index(inplace=True)
    table_cesta.model.df = df_cestas
    table_cesta.autoResizeColumns()
    table_cesta.redraw()

    l_cestas = list(df_cestas.columns)
    cesta_lblgrid.clear()

    for x in range(num_cestas.get() + 1):
        l_grid = [l_cestas[x + 1], round(l_e_req[x], 0), l_peso[x]]
        cesta_lblgrid.add_row(l_grid)


def update_comp_values(df_cont, carga_eaf):
    l_cont = df_cont['Valor'].tolist()

    if comp_disp_var.get() == "1":
        for x in range(len(l_cont)):
            l_comp_labels[x].config(text=str(l_cont[x]) + ' %')

    elif comp_disp_var.get() == "0":
        for x in range(len(l_cont)):
            w_cont = round(carga_eaf * l_cont[x] * 10, 2)
            l_comp_labels[x].config(text=str(w_cont) + ' kg')


def update_ISD_values(mgo, feo):
    mgo_isd_value.set(mgo)
    feo_value.set(feo)

    draw_point()


def update_mgob3_values(mgo, b2):

    mgo_mgob3_value.set(mgo)
    b2_value.set(b2)

    draw_point_mgob3()


def change_comp_values(*args):

    if simu_success.get() == False:
        return
    else:

        l_cont = df_cont['Valor'].tolist()

        carga_eaf = float(load_eaf.get())

        if comp_disp_var.get() == "1":
            for x in range(len(l_cont)):
                l_comp_labels[x].config(text=str(l_cont[x]) + ' %')

        elif comp_disp_var.get() == "0":
            for x in range(len(l_cont)):
                w_cont = round(carga_eaf * l_cont[x] * 10, 2)
                l_comp_labels[x].config(text=str(w_cont) + ' kg')


def save_sim():
    save_file_path = tk.filedialog.asksaveasfilename(defaultextension='.keda')
    if save_file_path != '':
        save_file = open(save_file_path, 'wb')
        df_results.to_pickle(save_file)
    else:
        return


def load_sim():
    load_file_path = tk.filedialog.askopenfilename(
        initialdir="C:/Users/Rodrigo/Documents/SIDER/Documentación/Simulaciones Kedalion", title='Seleccionar archivo')

    if load_file_path != '':
        load_file = open(load_file_path, 'rb')
        resultado = pkl.load(load_file)

        print(resultado)
    else:
        return


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
    gen_checkboxes.l_entries_max = []

    for widget in param_sc_frame.winfo_children():
        widget.destroy()

    for x in range(len(gen_slides.l_inv_valid_name)):
        value = tk.BooleanVar()
        value.set(True)
        gen_checkboxes.l_values.append(value)

    for x in range(len(gen_slides.l_inv_valid_name)):
        chbx = ttk.Checkbutton(param_sc_frame, text=gen_slides.l_inv_valid_name[x], variable=gen_checkboxes.l_values[x],
                               command=lambda i=x: activate_entry(i))
        chbx.grid(row=x + x, column=0, pady=5, padx=5, sticky='w')

        entry_min = ttk.Entry(param_sc_frame, width=7, state='disabled')
        entry_min.grid(row=x + x, column=1, pady=5, padx=2)

        lb_min = tk.Label(param_sc_frame, text='[ton]')
        lb_min.grid(row=x + x, column=2, pady=5, padx=2)

        entry_max = ttk.Entry(param_sc_frame, width=7, state='disabled')
        entry_max.grid(row=x + x, column=3, pady=5, padx=2)

        lb_max = tk.Label(param_sc_frame, text='[ton]')
        lb_max.grid(row=x + x, column=4, pady=5, padx=2)

        gen_checkboxes.l_chbx.append(chbx)
        gen_checkboxes.l_entries.append(entry_min)
        gen_checkboxes.l_entries_max.append(entry_max)

    for x in range(len(gen_slides.l_inv_valid_name)):

        if gen_slides.l_inv_valid_name[x] == 'LIVIANA' or gen_slides.l_inv_valid_name[x] == 'CIZALLA':
            gen_checkboxes.l_values[x].set(True)
            gen_checkboxes.l_entries[x].config(state='normal')
            gen_checkboxes.l_entries_max[x].config(state='normal')
            if gen_slides.l_inv_valid_name[x] == 'LIVIANA':
                gen_checkboxes.l_entries[x].insert(0, '2')
                gen_checkboxes.l_entries_max[x].insert(0,'0')

            if gen_slides.l_inv_valid_name[x] == 'CIZALLA':
                gen_checkboxes.l_entries[x].insert(0, '2')
                gen_checkboxes.l_entries_max[x].insert(0, '0')

        else:
            gen_checkboxes.l_values[x].set(False)


def gen_adi_chechboxes(*args):

    global l_param_adi_bool, l_param_adi_chbxs, l_param_adi_entries, l_param_adi_valid_nombres

    update_df_adiciones()
    df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)
    l_adi_values = df_adiciones['Inventario'].tolist()
    l_adi_nombres = df_adiciones['Nombre'].tolist()

    l_param_adi_valid_nombres = []

    l_param_adi_chbxs = []
    l_param_adi_entries = []

    for widget in param_adi_sc_frame.winfo_children():
        widget.destroy()

    for x in range(len(df_adiciones)):

        if float(l_adi_values[x]) != 0:
            l_param_adi_valid_nombres.append(l_adi_nombres[x])

    l_param_adi_bool = []

    for x in range(len(l_param_adi_valid_nombres)):
        value = tk.BooleanVar()
        value.set(True)
        l_param_adi_bool.append(value)

    for x in range(len(l_param_adi_valid_nombres)):
        chbx = ttk.Checkbutton(param_adi_sc_frame, text=l_param_adi_valid_nombres[x], variable=l_param_adi_bool[x], command=lambda i=x: adi_activate_entry(i))
        chbx.grid(row=x + x, column=0, pady=5, padx=5, sticky='w')

        entry = ttk.Entry(param_adi_sc_frame, width=9, state='normal')
        entry.grid(row=x + x, column=1, pady=5, padx=2)

        unit_lb = tk.Label(param_adi_sc_frame, text='[kg]')
        unit_lb.grid(row=x + x, column=2, pady=5, padx=2)

        l_param_adi_chbxs.append(chbx)
        l_param_adi_entries.append(entry)

    for x in range(len(l_param_adi_valid_nombres)):

        if l_param_adi_valid_nombres[x] == 'ACOND.' or l_param_adi_valid_nombres[x] == 'CAL CALC.' or l_param_adi_valid_nombres[x] == 'ANTRACITA':
            l_param_adi_bool[x].set(True)
            l_param_adi_entries[x].config(state='normal')

            if l_param_adi_valid_nombres[x] == 'ACOND.':
                l_param_adi_entries[x].insert(0, '220')

            if l_param_adi_valid_nombres[x] == 'CAL CALC.':
                l_param_adi_entries[x].insert(0, '800')

            if l_param_adi_valid_nombres[x] == 'ANTRACITA':
                l_param_adi_entries[x].insert(0, '400')


        else:
            l_param_adi_bool[x].set(False)


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

        sum += round(inv_ll, 0)
        rend += round(rend_unit, 0)

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

    try:
        df_adiciones = pd.read_sql_query("SELECT * FROM adit_data", conn)
        l_adi_values = df_adiciones['Inventario'].tolist()
        l_adi_names = df_adiciones['Nombre'].tolist()

        l_adi_valid_names = []

        for x in range(len(df_adiciones)):
            l_adi_values[x] = float(l_adi_values[x])
            if l_adi_values[x] != 0.0:
                l_adi_valid_names.append(l_adi_names[x])

        l_3 = []

        for chbx in l_param_adi_chbxs:
            name = chbx.cget('text')
            l_3.append(name)

        if compare_lists(l_adi_valid_names, l_3):
            l_bool_adi = []

            for x in range(len(l_param_adi_chbxs)):

                if (l_param_adi_bool[x]).get():
                    l_bool_adi.append(True)

                else:
                    l_bool_adi.append(False)

                x += 1

            if True not in l_bool_adi:
                gen_adi_chechboxes()

        else:
            gen_adi_chechboxes()

    except:
        gen_adi_chechboxes()


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
            gen_checkboxes.l_entries_max[n].config(state='normal')
            gen_checkboxes.l_entries[n].delete(0, 'end')
            gen_checkboxes.l_entries_max[n].delete(0, 'end')
            gen_checkboxes.l_entries[n].insert(0, '0')
            gen_checkboxes.l_entries_max[n].insert(0, '0')
            val.set(True)

        else:
            gen_checkboxes.l_entries[n].delete(0, 'end')
            gen_checkboxes.l_entries_max[n].delete(0, 'end')
            gen_checkboxes.l_entries[n].config(state='disabled')
            gen_checkboxes.l_entries_max[n].config(state='disabled')
            val.set(False)

    except NameError:

        return


def adi_activate_entry(n):

    try:
        val = l_param_adi_bool[n]

        if val.get():
            l_param_adi_entries[n].config(state='normal')
            l_param_adi_entries[n].delete(0, 'end')
            l_param_adi_entries[n].insert(0, '0')

            val.set(True)

        else:
            l_param_adi_entries[n].delete(0, 'end')
            l_param_adi_entries[n].config(state='disabled')

            val.set(False)

    except NameError:

        return


def enable_num_cestas(*args):

    if auto_cestas.get() == True:
        num_cestas.set(1)
        res_ncestas_cmb.config(state='disabled')

    else:
        num_cestas.set(3)
        res_ncestas_cmb.config(state='normal')


def draw_point(*args):

    plot_id = float(graph_isd_b3_cmb.get())

    if plot_id == 1.0:

        ISD_plot_175.draw_axes()
        l_line_1 = []
        for x in range(23):
            l_line_1.append((x, (-0.3068182) * x + 17))
        ISD_plot_175.plot_line(l_line_1, color='blue')

        l_line_2 = []
        for x in range(23):
            l_line_2.append((x, (0.4659091) * x))
        ISD_plot_175.plot_line(l_line_2, color='blue')

        l_line_3 = []
        for x in range(22, 56):
            l_line_3.append((x, (-0.06969697) * x + 11.7833))
        ISD_plot_175.plot_line(l_line_3, color='blue')

        l_line_4 = []
        for x in range(22, 44):
            l_line_4.append((x, -1.168821 + (20474870 - -1.168821) / (1 + (x / 0.3412173) ** 3.457485)))
        ISD_plot_175.plot_line(l_line_4, color='blue')

        l_line_5 = []
        for x in range(21, 56):
            l_line_5.append((x, (-0.06969697) * x + 13.52441))
        ISD_plot_175.plot_line(l_line_5, color='blue', dashed=True)

        l_line_6 = []
        for x in range(19, 33):
            l_line_6.append((x, (-1.256 + (19118000 - -1.256) / (1 + (x / 0.5199405) ** 3.990436))))
        ISD_plot_175.plot_line(l_line_6, color='blue', dashed=True)

        l_line_7 = []
        for x in range(19, 22):
            l_line_7.append((x, ((-0.705 * (x ** 2)) + (29.065 * x) - 287.48)))
        ISD_plot_175.plot_line(l_line_7, color='blue', dashed=True)

        ISD_plot_175.plot_point(22, 10.25, size=6)

        try:
            x_coord = float(feo_value.get())
            y_coord = float(mgo_isd_value.get())
        except ValueError:
            return

        ISD_plot_175.plot_point(x_coord, y_coord, color='red', size=8)

    elif plot_id == 0.75:

        ISD_plot_15.draw_axes()
        l_line_1 = []
        for x in range(15):
            l_line_1.append((x, (-0.3169014) * x + 17))
        ISD_plot_15.plot_line(l_line_1, color='blue')

        l_line_2 = []
        for x in range(15):
            l_line_2.append((x, (0.8802817) * x))
        ISD_plot_15.plot_line(l_line_2, color='blue')

        l_line_3 = []
        for x in range(14, 56):
            l_line_3.append((x, (-0.06127451) * x + 13.3701))
        ISD_plot_15.plot_line(l_line_3, color='blue')

        l_line_4 = [(14.2, 12.5)]
        for x in range(15, 34):
            l_line_4.append((x, -1.155828 + (23822600 - -1.155828) / (1 + (x / 0.0881964) ** 2.828845)))
        ISD_plot_15.plot_line(l_line_4, color='blue')

        l_line_5 = []
        for x in range(14, 56):
            l_line_5.append((x, (-0.06495098) * x + 14.9223))
        ISD_plot_15.plot_line(l_line_5, color='blue', dashed=True)

        l_line_6 = []
        for x in range(11, 26):
            l_line_6.append((x, (-1.518042 + (46.12712 - -1.518042) / (1 + (x / 8.274652) ** 3.071736))))
        ISD_plot_15.plot_line(l_line_6, color='blue', dashed=True)

        l_line_7 = []
        for x in range(11, 15):
            l_line_7.append((x, ((-0.2262255 * (x ** 2)) + (6.169632 * x) - 27.99267)))
        ISD_plot_15.plot_line(l_line_7, color='blue', dashed=True)

        ISD_plot_15.plot_point(x=14.2, y=12.5, size=7)

        try:
            x_coord = float(feo_value.get())
            y_coord = float(mgo_isd_value.get())
        except ValueError:
            return

        ISD_plot_15.plot_point(x_coord, y_coord, color='red', size=8)

    elif plot_id == 1.25:

        ISD_plot_20.draw_axes()
        l_line_1 = []
        for x in range(27):
            l_line_1.append((x, (-0.3076923) * x + 17))
        ISD_plot_20.plot_line(l_line_1, color='blue')

        l_line_2 = []
        for x in range(27):
            l_line_2.append((x, (0.3461538) * x))
        ISD_plot_20.plot_line(l_line_2, color='blue')

        l_line_3 = []
        for x in range(26, 56):
            l_line_3.append((x, (-0.04310345) * x + 10.12069))
        ISD_plot_20.plot_line(l_line_3, color='blue')

        l_line_4 = []
        for x in range(26, 49):
            l_line_4.append((x, -0.4619961 + (15537880 - -0.4619961) / (1 + (x / 1.509489) ** 5.028619)))
        ISD_plot_20.plot_line(l_line_4, color='blue')

        l_line_5 = []
        for x in range(26, 56):
            l_line_5.append((x, (-0.0482758) * x + 11.75517))
        ISD_plot_20.plot_line(l_line_5, color='blue', dashed=True)

        l_line_6 = [(22.4, 9.9126)]
        for x in range(23, 37):
            l_line_6.append((x, (-0.7715791 + (15077200 - -0.7715791) / (1 + (x / 1.696116) ** 5.484917))))
        ISD_plot_20.plot_line(l_line_6, color='blue', dashed=True)

        l_line_7 = []
        for x in range(23, 27):
            l_line_7.append((x, (10.50001 + (-76309.03 - 10.50001) / (1 + (x / 20.91789) ** 125.7863))))
        ISD_plot_20.plot_line(l_line_7, color='blue', dashed=True)

        try:
            x_coord = float(feo_value.get())
            y_coord = float(mgo_isd_value.get())
        except ValueError:
            return

        ISD_plot_20.plot_point(26, 9, size=7)
        ISD_plot_20.plot_point(x_coord, y_coord, color='red', size=8)

    elif plot_id == 1.75:

        ISD_plot_25.draw_axes()
        l_line_1 = []
        for x in range(32):
            l_line_1.append((x, (-0.2968254) * x + 17))
        ISD_plot_25.plot_line(l_line_1, color='blue')

        l_line_2 = []
        for x in range(32):
            l_line_2.append((x, (0.2428571) * x))
        ISD_plot_25.plot_line(l_line_2, color='blue')

        l_line_3 = []
        for x in range(31, 56):
            l_line_3.append((x, (-0.02765957) * x + 8.521277))
        ISD_plot_25.plot_line(l_line_3, color='blue')

        l_line_4 = [(31.5, 7.65)]
        for x in range(32, 56):
            l_line_4.append((x, -0.3816039 + (15928160 - -0.381603) / (1 + (x / 1.8096) ** 5.076702)))
        ISD_plot_25.plot_line(l_line_4, color='blue')

        l_line_5 = []
        for x in range(31, 56):
            l_line_5.append((x, (-0.01787234) * x + 9.782979))
        ISD_plot_25.plot_line(l_line_5, color='blue', dashed=True)

        l_line_6 = []
        for x in range(27, 41):
            l_line_6.append((x, (-2.060893 + (4604940 - -2.060893) / (1 + (x / 1.080947) ** 4.061486))))
        ISD_plot_25.plot_line(l_line_6, color='blue', dashed=True)

        l_line_7 = []
        for x in range(27, 32):
            l_line_7.append((x, (9.326569 + (-2989339 - 9.326569) / (1 + (x / 14.7695) ** 23.908))))
        ISD_plot_25.plot_line(l_line_7, color='blue', dashed=True)

        try:
            x_coord = float(feo_value.get())
            y_coord = float(mgo_isd_value.get())
        except ValueError:
            return

        ISD_plot_25.plot_point(31.5, 7.65, size=7)
        ISD_plot_25.plot_point(x_coord, y_coord, color='red', size=8)


def draw_point_mgob3(*args):


    b2_coord = float(b2_value.get())
    mgo_b3_coord = float(mgo_mgob3_value.get())

    mgob3_plot.plot_point(b2_coord, mgo_b3_coord, size=8, color='red')


def plot_ISD(*args):

    plot_id = float(graph_isd_b3_cmb.get())

    if plot_id == 0.75:
        for widget in graph_display_isd_frame.winfo_children():
            widget.grid_forget()
        ISD_plot_15.grid(row=1, column=0)
        ISD_15_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)
        draw_point()

    elif plot_id == 1.0:
        for widget in graph_display_isd_frame.winfo_children():
            widget.grid_forget()
        ISD_plot_175.grid(row=1, column=0)
        ISD_175_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)
        draw_point()

    elif plot_id == 1.25:
        for widget in graph_display_isd_frame.winfo_children():
            widget.grid_forget()
        ISD_plot_20.grid(row=1, column=0)
        ISD_20_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)
        draw_point()

    elif plot_id == 1.75:
        for widget in graph_display_isd_frame.winfo_children():
            widget.grid_forget()
        ISD_plot_25.grid(row=1, column=0)
        ISD_25_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)
        draw_point()


def call_bucket_sim(*args):
    try:
        if start_sim.success.get() == True:
            bucket_sim()
        else:
            return

    except:
        pass


def draw_bucket(x, canvas):

    try:
        canvas.delete("draw")

    except NameError:
        pass

    l_load = df_results.iloc[:,11+x].tolist()

    l_name = df_results['Nombre'].tolist()
    l_rho = df_results['Densidad'].tolist()

    liv_indx = l_name.index('LIVIANA')
    l_value = []
    compress = False

    for x in range(len(df_results)):

        if l_name[x] == 'PESADA' and l_load[x] >= 4:

            compress = True

        l_value.append([l_load[x], l_rho[x]])

    if compress:
        l_value[liv_indx][1] = 0.6

    scrap_draw_dict = dict(zip(l_name, l_value))

    print(scrap_draw_dict)

    load_order = ['LIVIANA', 'PESADA', 'CIZALLA', 'IMPORTADA SHEADER']

    h = 0
    bucket_vol = 0
    #canvas.create_line(100,390-25,100,15, width=2)

    for scrap in load_order:
        print(scrap_draw_dict[scrap])
        if scrap_draw_dict[scrap][0] == 0:
            pass
        else:
            load_vol = round(scrap_draw_dict[scrap][0] / scrap_draw_dict[scrap][1], 2)
            bucket_vol += load_vol
            print("load_vol", load_vol)

            h = round(vol_to_h(bucket_vol, load_vol), 2)
            print(scrap, h)

            h_canvas = h * 1000 * 0.08084916

            canvas.create_line(50, 375 - h_canvas + 5, 220, 375 - h_canvas + 5, width=1, dash=(4, 2), tags='draw')
            canvas.create_text(140, 375 - h_canvas - 5 + 25, text=scrap, tags='draw')

    return bucket_vol


def vol_to_h(vol, load_vol):

    if vol <= 4.703:
        h = 40618 + ((0.009194222 - 40618) / (1 + ((vol / 106859400) ** 0.6377061)))

    elif 20.013 >= vol > 4.703:
        h = 0.1309946 * vol + 0.2283733

    elif 22.981 >= vol > 20.013:
        h = 17485.4 + (1.785195 - 17485.4) / (1 + (vol / 1188.092) ** 2.376838)

    elif 31.102 >= vol > 22.981:
        h = 0.1537384 * vol - 0.2685543

    else:
        h = 0

    return h


def export_report(*args):

    try:

        n_var = len(df_results) + 1
        save_file_path = tk.filedialog.asksaveasfilename(defaultextension='.xlsx')
        if save_file_path != '':
            Opt.gen_report(n_var, df_results, save_file_path, l_kpi)

        else:
            return

    except NameError:
        messagebox.showerror(title='Error', message='Aún no se ha completado una simulación exitosa.')
        return


def edit_mix(*args):

    try:
        n_var = len(df_results)

    except NameError:
        messagebox.showerror(title='Error', message='Aún no se ha completado una simulación exitosa.')
        return

    def sus_cesta():
        nc = int(n_cestas.get())
        nc = nc - 1
        n_cestas.set(nc)

        if nc == 1:
            nc_minus_btn.config(state='disabled')

        if nc < 8:
            nc_add_btn.config(state='normal')

        destroyed = l_cestas.pop(-1)
        destroyed.destroy()

        l_del_e = l_var.pop(-1)

        for entry in l_del_e:
            entry.destroy()

    def add_cesta():
        nc = int(n_cestas.get())
        nc = nc + 1
        n_cestas.set(nc)

        if nc > 1:
            nc_minus_btn.config(state='normal')

        if nc == 7:
            nc_add_btn.config(state='disabled')

        added_row = int(n_cestas.get()) + 1
        added_c_name = 'Cesta N°' + str(added_row-1)
        added_c_title = tk.Label(edit_cesta_frame, text=added_c_name)
        added_c_title.grid(row=0, column=added_row, pady=5, padx=5)

        l_cestas.append(added_c_title)

        l_var_c = []
        x = 0

        for nombre in l_nombres:
            carga_e = ttk.Entry(edit_cesta_frame, width=5)
            carga_e.grid(row=x+1, column=added_row, pady=5, padx=5)

            l_var_c.append(carga_e)

            x += 1

        l_var.append(l_var_c)

    edit_top = tk.Toplevel(root)
    edit_top.title("Editar Mix")
    edit_top.iconbitmap('Images\\Reportes.ico')
    edit_top.grab_set()

    edit_control_frame = tk.Frame(edit_top)
    edit_display_frame = tk.LabelFrame(edit_top)
    edit_cesta_frame = tk.LabelFrame(edit_top)

    edit_control_frame.grid(row=0, column=0, pady=10, padx=10)
    edit_display_frame.grid(row=1, column=0, pady=10, padx=10)
    edit_cesta_frame.grid(row=1, column=1, pady=10, padx=10)

    n_cestas = tk.StringVar()
    n_cestas.set(num_cestas.get())

    nc_lb = tk.Label(edit_control_frame, text='Número de cestas: ')
    nc_lb.grid(row=0, column=0)

    nc_add_btn = tk.Button(edit_control_frame, text='+', command=add_cesta, fg='green')
    nc_minus_btn = tk.Button(edit_control_frame, text='-', command=sus_cesta, fg='red')

    nc_add_btn.grid(row=0, column=3, pady=5, padx=10)
    nc_minus_btn.grid(row=0, column=1, pady=5, padx=10)

    nc_e = ttk.Entry(edit_control_frame, state='readonly', width=5, textvariable=n_cestas, justify='center')
    nc_e.grid(row=0, column=2)

    ###

    l_cestas = []

    l_nombres= df_results['Nombre'].tolist()
    l_carga = df_results['Carga'].tolist()

    nombre_lb = tk.Label(edit_display_frame, text='Nombre')
    nombre_lb.grid(row=0, column=0)

    carga_lb = tk.Label(edit_display_frame, text='Carga')
    carga_lb.grid(row=0, column=1)

    x = 0
    for nombre in l_nombres:
        label = tk.Label(edit_display_frame, text=nombre)
        label.grid(row=x + 1, column=0, pady=5, padx=5, sticky='w')

        load_lb = tk.Label(edit_display_frame, text=l_carga[x])
        load_lb.grid(row=x + 1, column=1, pady=5, padx=5, sticky='e')


        x += 1

    l_var = []
    i = 0
    for i in range(int(n_cestas.get())):
        c_name = 'Cesta N°' + str(i+1)
        c_title_lb = tk.Label(edit_cesta_frame, text=c_name)
        c_title_lb.grid(row=0, column=i, pady=5, padx=5)
        l_cestas.append(c_title_lb)

        l_var_c = []

        x = 0
        for nombre in l_nombres:

            l_values_cesta = df_results[c_name].tolist()

            carga_e = ttk.Entry(edit_cesta_frame, width=5)
            carga_e.grid(row=x+1, column=i, pady=5, padx=5)

            l_var_c.append(carga_e)

            carga_e.insert(0, l_values_cesta[x])

            x += 1

        l_var.append(l_var_c)


def gen_tabs(*args):

    global l_fund_values, l_pot_values, l_ends_values

    l_pfund_3 = [75, 85, 100]
    l_pfund_4 = [70, 80, 90, 100]
    l_pot_3 = [29, 29, 31]
    l_pot_4 = [26, 26, 27, 29]
    l_ends_3 = [50, 50, 60]
    l_ends_4 = [40, 40, 50, 60]

    l_fund_values =[]
    l_pot_values = []
    l_ends_values = []

    l_tabs = cesta_ntb.winfo_children()

    if len(l_tabs) > 2:

        for x in range(2, len(l_tabs)):

            l_tabs[x].destroy()

    n_cestas = int(num_cestas.get())

    for x in range(n_cestas):

        cesta_name = "Cesta N°"+str(x+1)
        tab = tk.Frame(cesta_ntb, bg='white')

        fund_var = tk.StringVar()
        ends_var = tk.StringVar()
        pot_var = tk.StringVar()

        pot_var.trace('w', update_potprom)

        tab_disp_frame = tk.LabelFrame(tab, text='Datos Cesta', height=380, width=400)
        tab_disp_frame.grid_propagate(False)
        tab_disp_frame.grid(row=0, column=0, padx=10, pady=10)

        tab_disp_fund_lb = tk.Label(tab_disp_frame, text='Porcentaje fund. de cesta: ')
        tab_disp_fund_cmb = ttk.Spinbox(tab_disp_frame, width=10, from_=0, to=100, wrap=True, increment=1, textvariable=fund_var)
        tab_disp_fund_unit = tk.Label(tab_disp_frame, text='[%]')

        tab_disp_fund_lb.grid(row=0, column=0, padx=5, pady=5)
        tab_disp_fund_cmb.grid(row=0, column=1, padx=5, pady=5)
        tab_disp_fund_unit.grid(row=0, column=2, padx=5, pady=5)

        tab_disp_pot_lb = tk.Label(tab_disp_frame, text='Potencia prom. de cesta: ')
        tab_disp_pot_cmb = ttk.Spinbox(tab_disp_frame, width=10, from_=20, to=60, wrap=True, increment=0.1, textvariable=pot_var)
        tab_disp_pot_unit = tk.Label(tab_disp_frame, text='[MW]')

        tab_disp_pot_lb.grid(row=1, column=0, padx=5, pady=5)
        tab_disp_pot_cmb.grid(row=1, column=1, padx=5, pady=5)
        tab_disp_pot_unit.grid(row=1, column=2, padx=5, pady=5)

        tab_disp_ends_lb = tk.Label(tab_disp_frame, text='End Step cesta: ')
        tab_disp_ends_cmb = ttk.Spinbox(tab_disp_frame, width=10, from_=0, to=300, wrap=True, increment=5, textvariable=ends_var)
        tab_disp_ends_unit = tk.Label(tab_disp_frame, text='[kWh/ton]')

        tab_disp_ends_lb.grid(row=2, column=0, padx=5, pady=5)
        tab_disp_ends_cmb.grid(row=2, column=1, padx=5, pady=5)
        tab_disp_ends_unit.grid(row=2, column=2, padx=5, pady=5)

        if n_cestas == 3:

            fund_var.set(l_pfund_3[x])
            pot_var.set(l_pot_3[x])
            ends_var.set(l_ends_3[x])

        elif n_cestas == 4:

            fund_var.set(l_pfund_4[x])
            pot_var.set(l_pot_4[x])
            ends_var.set(l_ends_4[x])

        else:
            fund_var.set(80)
            pot_var.set(30)
            ends_var.set(40)

        tab_layer_frame = tk.Frame(tab, bg='white')
        tab_cnv = tk.Canvas(tab_layer_frame, height=375, width=266, bg='white')

        tab_cnv.create_image(5, 5, image=cesta_bucket_img, anchor='nw')
        tab_cnv.grid(row=0, column=0)
        tab_layer_frame.grid(row=0, column=1, padx=5, pady=5)

        cesta_ntb.add(tab, text=cesta_name, padding=15)

        l_fund_values.append(fund_var)
        l_pot_values.append(pot_var)
        l_ends_values.append(ends_var)

        bucket_vol = draw_bucket(x, tab_cnv)

        tab_gauge = tkt.Gauge(tab_layer_frame, width=280, height=180, max_value=28, min_value=8, label='Volumen Cesta', unit='m3', red=95, yellow=90, divisions=28, bg='white')
        tab_gauge.grid(row=0, column=1, padx=25, pady=10, sticky='n')
        tab_gauge.set_value(bucket_vol)


def plot_graph(*args):

    graph = graph_select_cmb.get()

    graph_indx = l_graphs.index(graph)

    for widget in graph_display_frame.winfo_children():
        widget.grid_forget()

    for cwidget in graph_config_frame.winfo_children():

        w_index = graph_config_frame.winfo_children().index(cwidget)
        if w_index>=2:
            cwidget.grid_forget()

    if graph_indx == 0:

        graph_display_isd_frame.grid(row=0, column=0)
        graph_config_isd_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        plot_ISD()

    if graph_indx == 1:

        plot_mgob3()
        draw_point_mgob3()
        graph_display_mgob3_frame.grid(row=0, column=0)
        graph_config_mgob3_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)


def plot_mgob3(*args):

    mgob3_plot.draw_axes()
    k = float(graph_k_id.get())

    x = 0.5
    l_graph = []
    for j in range(15):
        x += 25/100
        l_graph.append((x,k*(x**(-0.876))))

    mgob3_plot.plot_line(l_graph, color='blue')
    draw_point_mgob3()


def calc_min_disp(*args):

    l_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    week = {}

    primer_dia = timedelta(days=-1)

    n_days = (res_end_date_value.get_date() - (res_start_date_value.get_date()+primer_dia)).days
    for i in range(n_days):
        day = clndr.day_name[((res_start_date_value.get_date()+primer_dia) + timedelta(days=i + 1)).weekday()]
        week[day] = week[day] + 1 if day in week else 1

    horas_parada = 0
    x = 0
    for day in l_days:
        try:
            horas_parada += week[day] * l_op_h[x]
        except KeyError:
            pass
        x += 1

    horas_parada += l_op_h[7]
    horas_parada += l_op_h[8]

    minutos_disp = round(n_days*24 - horas_parada)*60

    res_min_disp_value.config(text=minutos_disp)


def edit_h_op():

    def save_edit_hop():
        x = 0
        for entry in l_days_entries:
            l_op_h[x] = float(entry.get())
            x += 1

        calc_min_disp()
        edit_h_top.destroy()

        print(l_op_h)

    edit_h_top = tk.Toplevel(root)
    edit_h_top.iconbitmap('Images\\Restricciones.ico')
    edit_h_top.grab_set()
    edit_h_top.wm_geometry("250x380")

    l_days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo', 'Mantenimiento', 'Adicionales']
    l_days_entries = []

    edit_display_frame = tk.Frame(edit_h_top)
    edit_display_frame.columnconfigure(0, weight=1)
    edit_display_frame.columnconfigure(1, weight=1)
    edit_display_frame.pack()

    edit_col_name1 = tk.Label(edit_display_frame, text='Día')
    edit_col_name2 = tk.Label(edit_display_frame, text='Horas de parada')
    edit_col_name1.grid(row=0, column=0, pady=5, padx=10)
    edit_col_name2.grid(row=0, column=1, pady=5, padx=10)

    f1 = font.Font(edit_col_name1, edit_col_name1.cget('font'))
    f1.config(underline=True)
    edit_col_name1.configure(font=f1)

    f2 = font.Font(edit_col_name2, edit_col_name2.cget('font'))
    f2.config(underline=True)
    edit_col_name2.configure(font=f2)

    for x in range(9):

        if x < 7:

            entry = ttk.Entry(edit_display_frame, width=7)
            entry.insert(0, l_op_h[x])
            l_days_entries.append(entry)

            label = tk.Label(edit_display_frame, text=l_days[x])

            entry.grid(row=x+1, column=1, padx=10, pady=5)
            label.grid(row=x+1, column=0, padx=10, pady=5)

        elif x == 8:
            sep = ttk.Separator(edit_display_frame, orient='horizontal')
            sep.grid(row=x+1, column=0, columnspan=2, sticky='ew', pady=10)

            entry = ttk.Entry(edit_display_frame, width=7)
            entry.insert(0, l_op_h[x])
            l_days_entries.append(entry)

            label = tk.Label(edit_display_frame, text=l_days[x])

            entry.grid(row=x + 3, column=1, padx=10, pady=5)
            label.grid(row=x + 3, column=0, padx=10, pady=5)

        else:
            entry = ttk.Entry(edit_display_frame, width=7)
            entry.insert(0, l_op_h[x])
            l_days_entries.append(entry)

            label = tk.Label(edit_display_frame, text=l_days[x])

            entry.grid(row=x + 3, column=1, padx=10, pady=5)
            label.grid(row=x + 3, column=0, padx=10, pady=5)

    edit_save_btn = ttk.Button(edit_display_frame, text='Guardar', command=save_edit_hop)
    edit_save_btn.grid(row=20, column=0, columnspan=2, pady=10, padx=10)


def load_coes():

    try:

        for widget in ene_tframe.winfo_children():
            widget.destroy()

        bar_cont = tk.Frame(ene_tframe, height=420, width=580)
        bar_cont. pack_propagate(False)
        hm_cont = tk.Frame(ene_tframe, height=420, width=250)
        hm_cont.pack_propagate(False)

        l_semana, l_ej, l_max, X_axis, l_dia_max, X, df_diff = coes_scrapper.main('17:00', '23:00')

        fig = plt.Figure(figsize=(3, 2), dpi=100)
        fig_2 = plt.Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot()
        bx = fig_2.add_subplot()

        l_dias = []
        for x in range(len(X_axis)):
            day = list(X)[x]
            dia_num = day.split('/')[2]
            l_dias.append(dia_num)


        barras_1 = ax.bar(l_dias, l_semana, 0.9, label='Prog. Semanal')
        linea_1 = ax.plot(l_dias, l_max, color='red', linestyle='dashed', label='Máx. Ejecutado')
        barras_d = ax.bar(l_dias, l_dia_max, 0.9, color='green', label='Prog. Día')
        barr_ej  = ax.bar(l_dias, l_ej, 0.9, color='grey', label='Ejecutado')

        hmap = bx.pcolor(df_diff, edgecolors='w', cmap='RdYlGn')
        bx.autoscale(tight=True)
        bx.set_aspect(0.4)
        # ax.xaxis.set_ticks_positions('top')
        bx.tick_params(bottom='off', top='off', left='off', right='off', labelsize=8)
        ax.tick_params(bottom='off', top='off', left='off', right='off', labelsize=8)


        ax.set_ylim((6400, 7000))
        ax.legend(loc=8)
        # ax.xticks(X_axis, X, rotation=90)

        bx.set_yticks(np.arange(len(df_diff.index)) + 0.5)
        bx.set_yticklabels(list(df_diff.index))
        bx.set_xticks([0.5, 1.5])
        bx.set_xticklabels(list(df_diff.columns), rotation=0, fontsize='small')

        for i in range(len(list(df_diff.index))):
            for j in range(len(list(df_diff.columns))):
                text = bx.text(j + 0.5, i + 0.5, round(df_diff.iloc[i][j], 2), ha='center', va='center', color='w',
                               fontsize='small', fontweight='bold')

        ploot = FigureCanvasTkAgg(fig, bar_cont)
        ploot_2 = FigureCanvasTkAgg(fig_2, hm_cont)
        ploot.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        ploot_2.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        bar_cont.grid(row=0, column=0)
        hm_cont.grid(row=0, column=1)

    except ConnectionError:
        error = messagebox.showerror(title='Error de conexión', message='Fallo de comunicaicón con la web. Compruebe su conexión a internet.')
        return


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
nmetal_frame = tk.Frame(disp_frame)
adi_frame = tk.Frame(disp_frame)
analisis_frame = tk.Frame(disp_frame)
energy_frame = tk.Frame(disp_frame)

l_frames = (inv_frame, comp_frame, res_frame, param_frame, rep_frame, cesta_frame, graph_frame, nmetal_frame, adi_frame, analisis_frame, energy_frame)
l_frames_names = [' Chatarras', ' Composición', ' Restricciones', ' Parámetros', ' Reporte', ' Cestas', ' Gráficos',
                  ' No metálico', ' Adiciones', ' Análisis', ' Energía']

current_frame = tk.IntVar(master=None)
current_frame.set(1000)

# Frame de TreeView
tv_frame = tk.LabelFrame(main_frame, text="Menú", padx=20, pady=20, height=510, width=300)
tv_frame.grid(row=1, column=0, padx=20, pady=20)
tv_frame.grid_propagate(False)
tv_frame.columnconfigure(0, weight=1)

copyrght_lb = tk.Label(main_frame, text='SIDERPERU, 2021. Todos los derechos reservados.', fg='grey')
copyrght_lb.grid(row=2, column=0, columnspan=2, sticky='nsw', pady=0, padx=20)

# Conexión a SQLITE3
conn = sqlite3.connect('scrap.db')
cur = conn.cursor()

"""
cur.execute("CREATE TABLE scrap_data (Nombre TEXT, Precio FLOAT , Densidad FLOAT, Inventario INTEGER, Rendimiento FLOAT, Energia FLOAT)")
"""

# Frame del título del programa
img_1 = Image.open('Images\\Kedalion.png')
img_2 = Image.open('Images\\kedalion_logo.png')

save_icon = Image.open('Images\\Guardar.png')
start_icon = Image.open('Images\\Iniciar.png')
close_icon = Image.open('Images\\Salir.png')
load_icon = Image.open('Images\\Cargar.png')

scrap_icono = Image.open('Images\\chatarra.png')
inv_icono = Image.open('Images\\inventario_icon.png')
param_icono = Image.open('Images\\parametros_icon.png')
comp_icono = Image.open('Images\\composicion_icon.png')
res_icono = Image.open('Images\\restrcciones_icon.png')
nmet_icono = Image.open('Images\\nmet_icono.png')
rep_icono = Image.open('Images\\reportes_icon.png')
graph_icono = Image.open('Images\\graficos_icon.png')
cestas_icon = Image.open('Images\\chatarrera_icon.png')
adiciones_icon = Image.open('Images\\Adicion.png')
analisis_icon = Image.open('Images\\analisis.png')
cost_icon = Image.open('Images\\costo.png')
energy_icon = Image.open('Images\\energia.png')

img_1 = img_1.resize((580, 200), Image.ANTIALIAS)
kedalion_img = ImageTk.PhotoImage(img_1)
lb_1 = tk.Label(title_frame, image=kedalion_img)
lb_1.grid(row=0, column=0, columnspan=2)
img_2 = img_2.resize((12, 12), Image.ANTIALIAS)
tv_icon = ImageTk.PhotoImage(img_2)

save_icon = save_icon.resize((15, 15), Image.ANTIALIAS)
save_icon = ImageTk.PhotoImage(save_icon)
load_icon = load_icon.resize((15, 15), Image.ANTIALIAS)
load_icon = ImageTk.PhotoImage(load_icon)
start_icon = start_icon.resize((15, 15), Image.ANTIALIAS)
start_icon = ImageTk.PhotoImage(start_icon)
close_icon = close_icon.resize((15, 15), Image.ANTIALIAS)
close_icon = ImageTk.PhotoImage(close_icon)

scrap_icono = scrap_icono.resize((12,12), Image.ANTIALIAS)
scrap_icono = ImageTk.PhotoImage(scrap_icono)
inv_icono = inv_icono.resize((12, 12), Image.ANTIALIAS)
inv_icono = ImageTk.PhotoImage(inv_icono)
param_icono = param_icono.resize((12, 12), Image.ANTIALIAS)
param_icono = ImageTk.PhotoImage(param_icono)
comp_icono = comp_icono.resize((12, 12), Image.ANTIALIAS)
comp_icono = ImageTk.PhotoImage(comp_icono)
res_icono = res_icono.resize((12, 12), Image.ANTIALIAS)
res_icono = ImageTk.PhotoImage(res_icono)
nmet_icono = nmet_icono.resize((12, 12), Image.ANTIALIAS)
nmet_icono = ImageTk.PhotoImage(nmet_icono)
rep_icono = rep_icono.resize((12, 12), Image.ANTIALIAS)
rep_icono = ImageTk.PhotoImage(rep_icono)
graph_icono = graph_icono.resize((12, 12), Image.ANTIALIAS)
graph_icono = ImageTk.PhotoImage(graph_icono)
cestas_icon = cestas_icon.resize((12, 12), Image.ANTIALIAS)
cestas_icon = ImageTk.PhotoImage(cestas_icon)
adiciones_icon = adiciones_icon.resize((12, 12), Image.ANTIALIAS)
adiciones_icon = ImageTk.PhotoImage(adiciones_icon)
analisis_icon = analisis_icon.resize((12,12), Image.ANTIALIAS)
analisis_icon = ImageTk.PhotoImage(analisis_icon)
cost_icon = cost_icon.resize((12,12), Image.ANTIALIAS)
cost_icon = ImageTk.PhotoImage(cost_icon)
energy_icon = energy_icon.resize((12,12), Image.ANTIALIAS)
energy_icon = ImageTk.PhotoImage(energy_icon)

simu_success = tk.BooleanVar()
simu_success.set(False)

##Menu Frame
menu_tv = ttk.Treeview(tv_frame)
menu_tv.grid(row=0, column=0, columnspan=1, sticky='nsew', pady=15)
menu_top = menu_tv.insert("", tk.END, text=' Kedalion', image=tv_icon, tags='cd', open=True)
menu_datos = menu_tv.insert(menu_top, tk.END, text='Datos', tags='cd')
menu_simu = menu_tv.insert(menu_top, tk.END, text='Simulación', tags='cd')
menu_result = menu_tv.insert(menu_top, tk.END, text='Resultados', tags='cd')
menu_inv = menu_tv.insert(menu_datos, tk.END, text=' Inventario', tags='cd', image=inv_icono)
menu_costos = menu_tv.insert(menu_datos, tk.END, text=' Costos', tags='cd', image=cost_icon)

menu_tv.insert(menu_inv, tk.END, text=' Chatarras', tags='cb', image=scrap_icono)
menu_tv.insert(menu_inv, tk.END, text=' Composición', tags='cb', image=comp_icono)
menu_tv.insert(menu_inv, tk.END, text=' No metálico', tags='cb', image=nmet_icono)
menu_tv.insert(menu_inv, tk.END, text=' Adiciones', tags='cb', image=adiciones_icon)

menu_tv.insert(menu_costos, tk.END, text=' Energía', tags='cb', image=energy_icon)
menu_tv.insert(menu_costos, tk.END, text='Fijos', tags='cd')
menu_tv.insert(menu_costos, tk.END, text='Consumibles', tags='cd')

menu_tv.insert(menu_simu, tk.END, text=' Restricciones', tags='cb', image=res_icono)
menu_tv.insert(menu_simu, tk.END, text=' Parámetros', tags='cb', image=param_icono)

menu_tv.insert(menu_result, tk.END, text=' Reporte', tags='cb', image=rep_icono)
menu_tv.insert(menu_result, tk.END, text=' Cestas', tags='cb', image=cestas_icon)
menu_tv.insert(menu_result, tk.END, text=' Gráficos', tags='cb', image=graph_icono)
menu_tv.insert(menu_result, tk.END, text=' Análisis', tags='cb', image=analisis_icon)

menu_tv.tag_bind('cb', '<Double-1>', cb)
menu_tv.tag_configure(tagname='cb', font=('Segoe', 10))
menu_tv.tag_configure(tagname='cd', font=('Segoe', 10))

b_quit = ttk.Button(tv_frame, text=" Salir", command=root.destroy, cursor='hand1', image=close_icon, compound=tk.LEFT)
b_start = ttk.Button(tv_frame, text=' Iniciar', command=progress, state='disabled', cursor='hand1', image=start_icon,
                     compound=tk.LEFT)
b_save = ttk.Button(tv_frame, text=' Guardar', command=save_sim, state='disabled', cursor='hand1', image=save_icon,
                    compound=tk.LEFT)
b_load = ttk.Button(tv_frame, text=' Cargar', command=load_sim, cursor='hand1', image=load_icon, compound=tk.LEFT)
b_start.grid(row=1, column=0, padx=10, pady=10, columnspan=1)
b_quit.grid(row=4, column=0, padx=10, pady=10, columnspan=1)
b_save.grid(row=2, column=0, padx=10, pady=10, columnspan=1)
b_load.grid(row=3, column=0, padx=10, pady=10, columnspan=1)

##Inv frame
inv_bframe = tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=260)
inv_bframe.grid(row=1, column=1)
inv_bframe.grid_propagate(False)
inv_tframe = tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=858)
inv_tframe.grid(row=1, column=2)
inv_tframe.grid_propagate(False)

inv_disp_frame = tk.LabelFrame(inv_bframe, height=280, width=235, padx=10, pady=10)
inv_disp_frame.grid(row=0, column=0)
inv_disp_frame.grid_propagate(False)
inv_disp_frame.columnconfigure(0, weight=1)
inv_disp_frame.columnconfigure(1, weight=1)
inv_disp_frame.columnconfigure(2, weight=1)
inv_disp_frame.columnconfigure(3, weight=0)

table_scrap = Table(inv_tframe, showstatusbar=True)
table_scrap.show()

inv_n_scraps = tk.IntVar()
inv_n_scraps.set(0)

inv_entries_lb = tk.Label(inv_disp_frame, text='Datos de Chatarra')
inv_entries_lb.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)

f_nombre = ttk.Entry(inv_disp_frame, width=10)
lb_nombre = tk.Label(inv_disp_frame, text="Nombre:")
f_nombre.grid(row=1, column=1, pady=5, padx=3)
lb_nombre.grid(row=1, column=0, pady=5, sticky='w', padx=2)

f_precio = ttk.Entry(inv_disp_frame, width=10)
lb_precio = tk.Label(inv_disp_frame, text="Precio:")
f_precio.grid(row=2, column=1, pady=5, padx=3)
lb_precio.grid(row=2, column=0, pady=5, sticky='w', padx=2)
lb_unit_precio = tk.Label(inv_disp_frame, text='[$/ton]')
lb_unit_precio.grid(row=2, column=2, pady=5, sticky='w')

f_densidad = ttk.Entry(inv_disp_frame, width=10)
lb_densidad = tk.Label(inv_disp_frame, text="Densidad:")
f_densidad.grid(row=3, column=1, pady=5, padx=3)
lb_densidad.grid(row=3, column=0, pady=5, sticky='w', padx=2)
lb_unit_densidad = tk.Label(inv_disp_frame, text='[m3/ton]')
lb_unit_densidad.grid(row=3, column=2, pady=5, sticky='w')

f_inventario = ttk.Entry(inv_disp_frame, width=10)
lb_inventario = tk.Label(inv_disp_frame, text="Inventario:")
f_inventario.grid(row=4, column=1, pady=5, padx=3)
lb_inventario.grid(row=4, column=0, pady=5, sticky='w', padx=2)
lb_unit_inv = tk.Label(inv_disp_frame, text='[ton]')
lb_unit_inv.grid(row=4, column=2, pady=5, sticky='w')

f_rendimiento = ttk.Entry(inv_disp_frame, width=10)
lb_rendimiento = tk.Label(inv_disp_frame, text="Rendimiento:")
f_rendimiento.grid(row=5, column=1, pady=5, padx=3)
lb_rendimiento.grid(row=5, column=0, pady=5, sticky='w', padx=2)

f_energia = ttk.Entry(inv_disp_frame, width=10)
lb_energia = tk.Label(inv_disp_frame, text="Energía: ")
f_energia.grid(row=6, column=1, pady=7, padx=3)
lb_energia.grid(row=6, column=0, pady=7, sticky='w', padx=2)
lb_unit_ener = tk.Label(inv_disp_frame, text='[kWh/ton]')
lb_unit_ener.grid(row=6, column=2, pady=5, sticky='w')

inv_submit_b = ttk.Button(inv_bframe, text="Añadir", command=inv_submit)
inv_save_b = ttk.Button(inv_bframe, text='Guardar', command=inv_save_sql)
inv_delete_b = ttk.Button(inv_bframe, text='Eliminar', command=inv_delete)
inv_submit_b.grid(row=1, column=0, pady=10, ipadx=10, ipady=1.5)
inv_save_b.grid(row=3, column=0, pady=10, ipadx=10, ipady=1.5)
inv_delete_b.grid(row=4, column=0, pady=10, ipadx=10, ipady=1.5)

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

comp_disp_frame = tk.LabelFrame(comp_bframe, height=280, width=235, padx=10, pady=10)
comp_disp_frame.grid(row=0, column=0)
comp_disp_frame.grid_propagate(False)
comp_disp_frame.columnconfigure(0, weight=1)
comp_disp_frame.columnconfigure(1, weight=1)
comp_disp_frame.columnconfigure(2, weight=1)
comp_disp_frame.columnconfigure(3, weight=1)

comp_disp_var = tk.StringVar()
comp_disp_var.set("1")
comp_disp_var.trace('w', change_comp_values)

comp_unitkg_rdbt = ttk.Radiobutton(comp_disp_frame, text='Peso tot. [kg]', variable=comp_disp_var, value="0")
comp_unitkg_rdbt.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky='nsew')
comp_unitp_rdbt = ttk.Radiobutton(comp_disp_frame, text='Porcentaje [%]', variable=comp_disp_var, value="1")
comp_unitp_rdbt.grid(row=1, column=2, columnspan=2, pady=5, padx=5, sticky='nsew')

comp_sep_1 = ttk.Separator(comp_disp_frame, orient='horizontal')
comp_sep_1.grid(row=2, column=0, columnspan=4, sticky='ew', pady=10, padx=5)

comp_c_lb = tk.Label(comp_disp_frame, text='C:')
comp_c_e = ttk.Label(comp_disp_frame, text='-----')
comp_c_lb.grid(row=3, column=0, pady=5, sticky='w')
comp_c_e.grid(row=3, column=1, pady=5, sticky='w')

comp_mn_lb = tk.Label(comp_disp_frame, text='Mn:')
comp_mn_e = ttk.Label(comp_disp_frame, text='-----')
comp_mn_lb.grid(row=3, column=2, pady=5, sticky='w')
comp_mn_e.grid(row=3, column=3, pady=5, sticky='w')

comp_si_lb = tk.Label(comp_disp_frame, text='Si:')
comp_si_e = ttk.Label(comp_disp_frame, text='-----')
comp_si_lb.grid(row=4, column=0, pady=5, sticky='w')
comp_si_e.grid(row=4, column=1, pady=5, sticky='w')

comp_p_lb = tk.Label(comp_disp_frame, text='P:')
comp_p_e = ttk.Label(comp_disp_frame, text='-----')
comp_p_lb.grid(row=4, column=2, pady=5, sticky='w')
comp_p_e.grid(row=4, column=3, pady=5, sticky='w')

comp_cr_lb = tk.Label(comp_disp_frame, text='Cr:')
comp_cr_e = ttk.Label(comp_disp_frame, text='-----')
comp_cr_lb.grid(row=5, column=0, pady=5, sticky='w')
comp_cr_e.grid(row=5, column=1, pady=5, sticky='w')

comp_s_lb = tk.Label(comp_disp_frame, text='S:')
comp_s_e = ttk.Label(comp_disp_frame, text='-----')
comp_s_lb.grid(row=5, column=2, pady=5, sticky='w')
comp_s_e.grid(row=5, column=3, pady=5, sticky='w')

comp_cu_lb = tk.Label(comp_disp_frame, text='Cu:')
comp_cu_e = ttk.Label(comp_disp_frame, text='-----')
comp_cu_lb.grid(row=6, column=0, pady=5, sticky='w')
comp_cu_e.grid(row=6, column=1, pady=5, sticky='w')

comp_ni_lb = tk.Label(comp_disp_frame, text='Ni:')
comp_ni_e = ttk.Label(comp_disp_frame, text='-----')
comp_ni_lb.grid(row=6, column=2, pady=5, sticky='w')
comp_ni_e.grid(row=6, column=3, pady=5, sticky='w')

comp_mo_lb = tk.Label(comp_disp_frame, text='Mo:')
comp_mo_e = ttk.Label(comp_disp_frame, text='-----')
comp_mo_lb.grid(row=7, column=0, pady=5, sticky='w')
comp_mo_e.grid(row=7, column=1, pady=5, sticky='w')

comp_submit_b = ttk.Button(comp_bframe, text="Añadir", command=comp_submit_top)
comp_save_b = ttk.Button(comp_bframe, text='Guardar', command=comp_save_sql)
comp_delete_b = ttk.Button(comp_bframe, text='Eliminar', command=comp_delete)

comp_submit_b.grid(row=1, column=0, pady=10, ipadx=10, ipady=1.5, sticky='ns')
comp_save_b.grid(row=2, column=0, pady=10, ipadx=10, ipady=1.5, sticky='ns')
comp_delete_b.grid(row=3, column=0, pady=10, ipadx=10, ipady=1.5, sticky='ns')

l_comp_labels = [comp_c_e, comp_mn_e, comp_si_e, comp_p_e, comp_cr_e, comp_s_e, comp_cu_e, comp_ni_e, comp_mo_e]

# No metálico Frame
nmetal_bframe = tk.LabelFrame(nmetal_frame, height=445, width=260, padx=10, pady=10)
nmetal_tframe = tk.LabelFrame(nmetal_frame, height=445, width=858, padx=10, pady=10)

nmetal_bframe.grid_propagate(False)
nmetal_tframe.grid_propagate(False)
nmetal_bframe.grid(row=0, column=0, sticky='nsew')
nmetal_tframe.grid(row=0, column=1)

nmetal_disp_frame = tk.LabelFrame(nmetal_bframe, height=280, width=235, padx=10, pady=10)
nmetal_disp_frame.grid(row=1, column=0)
nmetal_disp_frame.grid_propagate(False)
nmetal_disp_frame.columnconfigure(0, weight=1)
nmetal_disp_frame.columnconfigure(1, weight=1)
nmetal_disp_frame.columnconfigure(2, weight=1)
nmetal_disp_frame.columnconfigure(3, weight=1)

table_nmetal = Table(nmetal_tframe, showstatusbar=True)
table_nmetal.show()

nmetal_rend_lb = tk.Label(nmetal_disp_frame, text='Rend.:')
nmetal_rendv_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_rend_lb.grid(row=0, column=0, padx=1, pady=5, sticky='w')
nmetal_rendv_label.grid(row=0, column=1, padx=1, pady=5, sticky='w')

nmetal_dirt_lb = tk.Label(nmetal_disp_frame, text='Escoria :')
nmetal_dirtv_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_dirt_lb.grid(row=0, column=2, padx=1, pady=5, sticky='w')
nmetal_dirtv_label.grid(row=0, column=3, padx=1, pady=5, sticky='w')

nmetal_sep_1 = ttk.Separator(nmetal_disp_frame, orient='horizontal')
nmetal_sep_1.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky='ew')

nmetal_fe_lb = tk.Label(nmetal_disp_frame, text='Fe met.:')
nmetal_fev_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_fe_lb.grid(row=1, column=0, padx=1, pady=5, sticky='w')
nmetal_fev_label.grid(row=1, column=1, padx=1, pady=5, sticky='w')

nmetal_cao_lb = tk.Label(nmetal_disp_frame, text='CaO :')
nmetal_caov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_cao_lb.grid(row=3, column=2, padx=1, pady=5, sticky='w')
nmetal_caov_label.grid(row=3, column=3, padx=1, pady=5, sticky='w')

nmetal_mgo_lb = tk.Label(nmetal_disp_frame, text='MgO :')
nmetal_mgov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_mgo_lb.grid(row=3, column=0, padx=1, pady=5, sticky='w')
nmetal_mgov_label.grid(row=3, column=1, padx=1, pady=5, sticky='w')

nmetal_alo_lb = tk.Label(nmetal_disp_frame, text='Al\u2082O\u2083 :')
nmetal_alov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_alo_lb.grid(row=4, column=2, padx=1, pady=5, sticky='w')
nmetal_alov_label.grid(row=4, column=3, padx=1, pady=5, sticky='w')

nmetal_sio_lb = tk.Label(nmetal_disp_frame, text='SiO\u2082 :')
nmetal_siov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_sio_lb.grid(row=4, column=0, padx=1, pady=5, sticky='w')
nmetal_siov_label.grid(row=4, column=1, padx=1, pady=5, sticky='w')

nmetal_mno_lb = tk.Label(nmetal_disp_frame, text='MnO :')
nmetal_mnov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_mno_lb.grid(row=5, column=2, padx=1, pady=5, sticky='w')
nmetal_mnov_label.grid(row=5, column=3, padx=1, pady=5, sticky='w')

nmetal_po_lb = tk.Label(nmetal_disp_frame, text='P\u2082O\u2085 :')
nmetal_pov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_po_lb.grid(row=5, column=0, padx=1, pady=5, sticky='w')
nmetal_pov_label.grid(row=5, column=1, padx=1, pady=5, sticky='w')

nmetal_feo_lb = tk.Label(nmetal_disp_frame, text='FeO :')
nmetal_feov_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_feo_lb.grid(row=6, column=2, padx=1, pady=5, sticky='w')
nmetal_feov_label.grid(row=6, column=3, padx=1, pady=5, sticky='w')

nmetal_s_lb = tk.Label(nmetal_disp_frame, text='S :')
nmetal_sv_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_s_lb.grid(row=6, column=0, padx=1, pady=5, sticky='w')
nmetal_sv_label.grid(row=6, column=1, padx=1, pady=5, sticky='w')

nmetal_pc_lb = tk.Label(nmetal_disp_frame, text='P/C :')
nmetal_pcv_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_pc_lb.grid(row=1, column=2, padx=1, pady=5, sticky='w')
nmetal_pcv_label.grid(row=1, column=3, padx=1, pady=5, sticky='w')

nmetal_sep_2 = ttk.Separator(nmetal_disp_frame, orient='horizontal')
nmetal_sep_2.grid(row=7, column=0, columnspan=4, padx=5, pady=10, sticky='ew')

nmetal_b2_lb = tk.Label(nmetal_disp_frame, text='B\u2082 :')
nmetal_b2v_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_b2_lb.grid(row=8, column=0, padx=1, pady=3, sticky='w')
nmetal_b2v_label.grid(row=8, column=1, padx=1, pady=3, sticky='w')

nmetal_b3_lb = tk.Label(nmetal_disp_frame, text='B\u2083 :')
nmetal_b3v_label = tk.Label(nmetal_disp_frame, text='----- ')
nmetal_b3_lb.grid(row=8, column=2, padx=1, pady=3, sticky='w')
nmetal_b3v_label.grid(row=8, column=3, padx=1, pady=3, sticky='w')

l_nmetal_lb = [nmetal_fev_label, nmetal_caov_label, nmetal_mgov_label, nmetal_alov_label, nmetal_siov_label,
               nmetal_mnov_label, nmetal_pov_label, nmetal_feov_label, nmetal_sv_label, nmetal_pcv_label]

nmetal_submit_b = ttk.Button(nmetal_bframe, text='Añadir', command=nmetal_submit_top)
nmetal_submit_b.grid(row=2, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')
nmetal_save_b = ttk.Button(nmetal_bframe, text='Guardar', command=nmet_save_sql)
nmetal_save_b.grid(row=3, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')
nmetal_del_b = ttk.Button(nmetal_bframe, text='Eliminar', command=nmet_delete)
nmetal_del_b.grid(row=4, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')

# Adiciones Frame

adiciones_bframe = tk.LabelFrame(adi_frame, height=445, width=260, padx=10, pady=10)
adiciones_tframe = tk.LabelFrame(adi_frame, height=445, width=858, padx=10, pady=10)

adiciones_bframe.grid_propagate(False)
adiciones_tframe.grid_propagate(False)
adiciones_bframe.grid(row=0, column=0, sticky='nsew')
adiciones_tframe.grid(row=0, column=1)

adiciones_disp_frame = tk.LabelFrame(adiciones_bframe, height=280, width=235, padx=10, pady=10)
adiciones_disp_frame.grid(row=1, column=0)
adiciones_disp_frame.grid_propagate(False)
adiciones_disp_frame.columnconfigure(0, weight=1)
adiciones_disp_frame.columnconfigure(1, weight=1)
adiciones_disp_frame.columnconfigure(2, weight=1)
adiciones_disp_frame.columnconfigure(3, weight=1)

table_adiciones = Table(adiciones_tframe, showstatusbar=True)
table_adiciones.show()

adiciones_submit_b = ttk.Button(adiciones_bframe, text='Añadir', command=adiciones_submit_top)
adiciones_submit_b.grid(row=2, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')
adiciones_save_b = ttk.Button(adiciones_bframe, text='Guardar', command=adiciones_save_sql)
adiciones_save_b.grid(row=3, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')
adiciones_del_b = ttk.Button(adiciones_bframe, text='Eliminar', command=adiciones_delete)
adiciones_del_b.grid(row=4, column=0, pady=10, columnspan=1, ipadx=10, ipady=1.5, sticky='ns')

# Restrictions Frame
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

res_invll_text_lb = tk.Label(res_bframe, text='Inventario disp.: ')
res_invll_disp_lb = tk.Label(res_bframe, text='')
res_invll_unit_lb = tk.Label(res_bframe, text='[ton]')
res_rend_text_lb = tk.Label(res_bframe, text='Inventario met. : ')
res_rend_disp_lb = tk.Label(res_bframe, text='')
res_rend_unit_lb = tk.Label(res_bframe, text='[ton]')
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
res_prod_unit_lb = tk.Label(res_bframe, text='[ton]')
res_prod_e.grid(row=3, column=1, pady=5, sticky='e', padx=5)
res_prod_lb.grid(row=3, column=0, pady=5, sticky='w')
res_prod_unit_lb.grid(row=3, column=2, pady=5, sticky='e')

res_separator2 = ttk.Separator(res_bframe, orient='horizontal')
res_separator2.grid(row=4, column=0, columnspan=3, pady=5, sticky='ew')

num_cestas = tk.IntVar()
num_cestas.set(3)
res_ncestas_lb = tk.Label(res_bframe, text='Número cestas:')
res_ncestas_cmb = ttk.Spinbox(res_bframe, textvariable=num_cestas, width=5, from_=1, to=10, increment=1,
                              state='disabled')
auto_cestas = tk.BooleanVar()
auto_cestas.set(True)
res_ncestas_auto_chbx = ttk.Checkbutton(res_bframe, text='Auto', variable=auto_cestas, command=enable_num_cestas)
res_ncestas_cmb.set('1')
res_ncestas_cmb.grid(row=5, column=2, pady=5)
res_ncestas_lb.grid(row=5, column=0, pady=5, sticky='w', columnspan=2)
res_ncestas_auto_chbx.grid(row=5, column=1, pady=2)

res_separator3 = ttk.Separator(res_bframe, orient='horizontal')
res_separator3.grid(row=6, column=0, columnspan=3, pady=5, sticky='ew')

res_start_date_lb = tk.Label(res_bframe, text='Fecha inicio:')
res_start_date_lb.grid(row=7, column=0, pady=5, sticky='w')

res_start_date_value = tkc.DateEntry(res_bframe, width=7)
res_start_date_value.grid(row=7, column=1, pady=5, columnspan=1)
res_start_date_value.bind('<<DateEntrySelected>>', calc_min_disp)

current_date = date_t.date(date_t.now())
tdelta = timedelta(weeks=4)
end_date = current_date+tdelta


res_end_date_lb = tk.Label(res_bframe, text='Fecha fin:')
res_end_date_lb.grid(row=8, column=0, pady=5, sticky='w')

res_end_date_value = tkc.DateEntry(res_bframe, width=7)
res_end_date_value.set_date(end_date)
res_end_date_value.grid(row=8, column=1, pady=5, columnspan=1)
res_end_date_value.bind('<<DateEntrySelected>>', calc_min_disp)

res_min_disp_lb = tk.Label(res_bframe, text='Minutos disp.:')
res_min_disp_lb.grid(row=9, column=0, pady=5, sticky='w')

res_min_disp_value = tk.Label(res_bframe)
res_min_disp_value.grid(row=9, column=1, pady=5, sticky='ew')

l_op_h = [4, 2.5, 2.5, 2.5, 4, 2.5, 1, 6, 10]

edit_image = Image.open('Images\\editar.png')
edit_image = edit_image.resize((12,12), Image.ANTIALIAS)
edit_image = ImageTk.PhotoImage(edit_image)

res_edit_hop_btn = tk.Button(res_bframe, height=1, width=2, image=edit_image, command=edit_h_op)
res_edit_hop_btn.grid(row=9, column=2, pady=5, sticky='nsew')

calc_min_disp()

res_separator4 = ttk.Separator(res_bframe, orient='horizontal')
res_separator4.grid(row=10, column=0, columnspan=3, pady=5, sticky='ew')




######################

param_eaf_frame = tk.LabelFrame(param_frame, text='Horno Eléctrico', height=120, width=265)
param_eaf_frame.grid(row=0, column=0, pady=5, padx=5)
param_eaf_frame.grid_propagate(False)

param_eafload_lb = tk.Label(param_eaf_frame, text='Carga objetivo EAF:')
param_eafload_unit_lb = tk.Label(param_eaf_frame, text='[ton]')
load_eaf = tk.StringVar()
load_eaf.set('37')
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
prod_eaf.set('32.8')
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
pot_prom_cesta.set('29.7')
param_potprom_e = ttk.Entry(param_pequim_frame, width=9, textvariable=pot_prom_cesta, justify='center',
                            state='readonly')
param_potprom_lb.grid(row=0, column=0, padx=5, sticky='w', pady=5)
param_potprom_e.grid(row=0, column=1, padx=5, pady=5)
param_potprom_unit_lb.grid(row=0, column=2, padx=5, sticky='w', pady=5)

param_potpromaf_lb = ttk.Label(param_pequim_frame, text='Pot. prom. afino:')
param_potpromaf_unit_lb = tk.Label(param_pequim_frame, text='[MW]')
pot_promaf_cesta = tk.StringVar()
pot_promaf_cesta.set('34.5')
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

param_kt_ox_lb = ttk.Label(param_pequim_frame, text='Flujo O2 comb.:')
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
param_kt_oxaf_lb.grid(row=6, column=0, padx=5, sticky='w', pady=5)
param_kt_oxaf_e.grid(row=6, column=1, padx=5, pady=5)
param_kt_oxaf_unit_lb.grid(row=6, column=2, padx=5, sticky='w', pady=5)

param_ereac_lb = ttk.Label(param_pequim_frame, text='Energía reacc.:')
param_ereac_unit_lb = tk.Label(param_pequim_frame, text='[kWh/m3]')
ereac = tk.StringVar()
ereac.set('4.4')
param_ereac_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ereac, justify='center', from_=2.0, to=20.0,
                            increment=0.1)
param_ereac_lb.grid(row=7, column=0, padx=5, sticky='w', pady=5)
param_ereac_e.grid(row=7, column=1, padx=5, pady=5)
param_ereac_unit_lb.grid(row=7, column=2, padx=5, sticky='w', pady=1)

param_ereac_af_lb = ttk.Label(param_pequim_frame, text='Energía oxidación:')
param_ereac_af_unit_lb = tk.Label(param_pequim_frame, text='[kWh/m3]')
ereac_af = tk.StringVar()
ereac_af.set('7.2')
param_ereac_af_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ereac_af, justify='center', from_=2.0, to=20.0,
                               increment=0.1)
param_ereac_af_lb.grid(row=8, column=0, padx=5, sticky='w', pady=5)
param_ereac_af_e.grid(row=8, column=1, padx=5, pady=5)
param_ereac_af_unit_lb.grid(row=8, column=2, padx=5, sticky='w', pady=1)

param_effreac_lb = ttk.Label(param_pequim_frame, text='Eficiencia reacc.:')
param_effreac_unit_lb = tk.Label(param_pequim_frame, text='[%]')
eff_reac = tk.StringVar()
eff_reac.set('50')
param_effreac_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=eff_reac, justify='center', from_=0, to=100,
                              increment=1)
param_effreac_lb.grid(row=9, column=0, padx=5, sticky='w', pady=5)
param_effreac_e.grid(row=9, column=1, padx=5, pady=5)
param_effreac_unit_lb.grid(row=9, column=2, padx=5, sticky='w', pady=1)

param_ktcesta_lb = ttk.Label(param_pequim_frame, text='Flujo O2 lanza cesta:')
param_ktcesta_unit_lb = tk.Label(param_pequim_frame, text='[m3/h]')
ox_flux_cesta = tk.StringVar()
ox_flux_cesta.set('1300')
param_ktcesta_e = ttk.Spinbox(param_pequim_frame, width=7, textvariable=ox_flux_cesta, justify='center', from_=700,
                              to=2600,
                              increment=10)
param_ktcesta_lb.grid(row=5, column=0, padx=5, sticky='w', pady=5)
param_ktcesta_e.grid(row=5, column=1, padx=5, pady=5)
param_ktcesta_unit_lb.grid(row=5, column=2, padx=5, sticky='w', pady=1)

param_bc_frame = tk.LabelFrame(param_frame, text='Cestas', height=120, width=265)
param_bc_frame.grid(row=0, column=1, pady=5, padx=10, rowspan=1)
param_bc_frame.grid_propagate(False)

param_bcload_lb = tk.Label(param_bc_frame, text='Carga máx. cesta:')
param_bcload_unit_lb = tk.Label(param_bc_frame, text='[ton]')
load_cesta = tk.StringVar()
load_cesta.set('30')
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

################
param_bscrap_frame = tk.LabelFrame(param_frame, text='Chatarras Base', height=440, width=400)
param_bscrap_frame.grid(row=0, column=2, padx=10, pady=10, rowspan=2, sticky='nsew')
param_bscrap_frame.grid_propagate(False)

param_bscrap_title_lb = tk.Label(param_bscrap_frame, text='  Nombre                                     Min.                      Max.')
param_bscrap_title_lb.grid(row=0, column=0, padx=5, pady=5)

param_bc_bscrap_frame = tk.LabelFrame(param_bscrap_frame)
param_bc_bscrap_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
param_bc_bscrap_frame.grid_propagate(True)

param_bscrap_cn = tk.Canvas(param_bc_bscrap_frame, confine=True, width=335, height=370)
param_bscrap_cn.config(highlightthickness=0)
param_cn_scb = ttk.Scrollbar(param_bc_bscrap_frame, orient='vertical', command=param_bscrap_cn.yview)
param_sc_frame = tk.Frame(param_bscrap_cn)
param_sc_frame.bind('<Configure>', lambda e: param_bscrap_cn.configure(scrollregion=param_bscrap_cn.bbox('all')))
param_bscrap_cn.create_window((0, 0), window=param_sc_frame, anchor='nw')
param_bscrap_cn.pack(side='left', fill='both', expand=True, padx=10)
param_cn_scb.pack(side='right', fill='y', expand=False)


###############
param_adi_frame = tk.LabelFrame(param_frame, text='Adiciones H.E.', height=310, width=265)
param_adi_frame.grid(row=1, column=1, pady=5, padx=10, rowspan=1)
param_adi_frame.grid_propagate(False)

param_big_frame = tk.LabelFrame(param_adi_frame)
param_big_frame.grid(row=0, column=0, padx=10, pady=5)

param_adi_cn = tk.Canvas(param_big_frame, confine=True, height=270, width=200)
param_adi_cn.config(highlightthickness=0)
param_adi_cn_scb = ttk.Scrollbar(param_big_frame, orient='vertical', command=param_adi_cn.yview)
param_adi_sc_frame = tk.Frame(param_adi_cn, height=268, width=198)
param_adi_sc_frame.columnconfigure(0, weight=10)
param_adi_sc_frame.columnconfigure(1, weight=3)
param_adi_sc_frame.columnconfigure(2, weight=1)
param_adi_sc_frame.grid_propagate(False)
param_adi_sc_frame.bind('<Configure>', lambda j: param_adi_cn.configure(scrollregion=param_adi_cn.bbox('all')))
param_adi_cn.create_window((0, 0), window=param_adi_sc_frame, anchor='nw')
param_adi_cn.pack(side='left', fill='both', expand=True, padx=10)
param_adi_cn_scb.pack(side='right', fill='y', expand=False)


# Reporte
rep_disp_frame = tk.LabelFrame(rep_frame, text='Indicadores de Proceso', width=1120, height=180)
rep_table_frame = tk.Frame(rep_frame, width=1120, height=200)
rep_disp_frame.grid(row=0, column=0)

rep_data_frame = tk.Frame(rep_disp_frame)
rep_data_frame.grid(row=0, column=0)

rep_table_frame.grid(row=1, column=0, pady=10)
rep_disp_frame.grid_propagate(False)

rep_scrap_cost_lb = tk.Label(rep_data_frame, text='Costo unitario chatarra:')
rep_scrap_cost_value_lb = tk.Label(rep_data_frame, text='----')
rep_scrap_cost_unit_lb = tk.Label(rep_data_frame, text='[$/ton]')
rep_scrap_cost_lb.grid(row=0, column=0, pady=5, padx=5, sticky='w')
rep_scrap_cost_value_lb.grid(row=0, column=1, pady=5, padx=5)
rep_scrap_cost_unit_lb.grid(row=0, column=2, pady=5, padx=5, sticky='ew')

rep_rho_mix_lb = tk.Label(rep_data_frame, text='Densidad aparente:')
rep_rho_mix_value_lb = tk.Label(rep_data_frame, text='----')
rep_rho_mix_unit_lb = tk.Label(rep_data_frame, text='[ton/m3]')
rep_rho_mix_lb.grid(row=1, column=0, pady=5, padx=5, sticky='w')
rep_rho_mix_value_lb.grid(row=1, column=1, pady=5, padx=5)
rep_rho_mix_unit_lb.grid(row=1, column=2, pady=5, padx=5, sticky='ew')

rep_rend_mix_lb = tk.Label(rep_data_frame, text='Rendimiento prom.:')
rep_rend_mix_value_lb = tk.Label(rep_data_frame, text='----')
rep_rend_mix_unit_lb = tk.Label(rep_data_frame, text='[%]')
rep_rend_mix_lb.grid(row=2, column=0, pady=5, padx=5, sticky='w')
rep_rend_mix_value_lb.grid(row=2, column=1, pady=5, padx=5)
rep_rend_mix_unit_lb.grid(row=2, column=2, pady=5, padx=5, sticky='ew')

rep_eunit_lb = tk.Label(rep_data_frame, text='Energía fundición prom.:')
rep_eunit_value_lb = tk.Label(rep_data_frame, text='----')
rep_eunit_unit_lb = tk.Label(rep_data_frame, text='[kWh/ton]')
rep_eunit_lb.grid(row=3, column=0, pady=5, padx=5, sticky='w')
rep_eunit_value_lb.grid(row=3, column=1, pady=5, padx=5)
rep_eunit_unit_lb.grid(row=3, column=2, pady=5, padx=5, sticky='ew')

rep_etotal_lb = tk.Label(rep_data_frame, text='Energía total:')
rep_etotal_value_lb = tk.Label(rep_data_frame, text='----')
rep_etotal_unit_lb = tk.Label(rep_data_frame, text='[kWh]')
rep_etotal_lb.grid(row=4, column=0, pady=5, padx=5, sticky='w')
rep_etotal_value_lb.grid(row=4, column=1, pady=5, padx=5)
rep_etotal_unit_lb.grid(row=4, column=2, pady=5, padx=5, sticky='ew')

rep_stotal_lb = tk.Label(rep_data_frame, text='Consumo chatarra:')
rep_stotal_value_lb = tk.Label(rep_data_frame, text='----')
rep_stotal_unit_lb = tk.Label(rep_data_frame, text='[ton]')
rep_stotal_lb.grid(row=0, column=3, pady=5, padx=5, sticky='w')
rep_stotal_value_lb.grid(row=0, column=4, pady=5, padx=5)
rep_stotal_unit_lb.grid(row=0, column=5, pady=5, padx=5, sticky='ew')

to_excel_icon = Image.open("Images\\to_Excel.png")
to_excel_icon = to_excel_icon.resize((25,25), Image.ANTIALIAS)
to_excel_icon = ImageTk.PhotoImage(to_excel_icon)
rep_export_excel_btn = tk.Button(rep_disp_frame, image=to_excel_icon, command=export_report)
rep_export_excel_btn.grid(row=0, column=1, padx=25, pady=5, sticky='n')

edit_mix_icon = Image.open('Images\\editar.png')
edit_mix_icon = edit_mix_icon.resize((25,25), Image.ANTIALIAS)
edit_mix_icon = ImageTk.PhotoImage(edit_mix_icon)

edit_mix_btn = tk.Button(rep_disp_frame, image=edit_mix_icon, command=edit_mix)
edit_mix_btn.grid(row=0, column=2, padx=10, pady=5, sticky='n')


l_kpi_labels = [rep_scrap_cost_value_lb, rep_rho_mix_value_lb, rep_rend_mix_value_lb, rep_eunit_value_lb,
                rep_etotal_value_lb, rep_stotal_value_lb]

table_rep = Table(rep_table_frame, showstatusbar=True, width=1050, height=200)
table_rep.show()

### Cestas

cesta_ntb = ttk.Notebook(cesta_frame, height=430, width=1080)
cesta_general_frame = tk.Frame(cesta_ntb, bg='white')
cesta_general_frame.bind('<Map>', bucket_sim)
cesta_preajuste_frame = tk.Frame(cesta_ntb, bg='white')

cesta_bucket_img = Image.open('Images\\bucketframe.png')
cesta_bucket_img = cesta_bucket_img.resize((261, 370), Image.ANTIALIAS)
cesta_bucket_img = ImageTk.PhotoImage(cesta_bucket_img)

cestas_table_frame = tk.Frame(cesta_general_frame)

cestas_table_frame.grid(row=0, column=0)
table_cesta = Table(cestas_table_frame, showstatusbar=True, width=980, height=300)
table_cesta.show()

cesta_lblgrid = tkt.LabelGrid(cesta_preajuste_frame, num_of_columns=3,
                              headers=[' Cestas ', ' FIN DE FASE [kWh] ', ' Peso [ton] '])
cesta_lblgrid.grid(row=0, column=0)

cesta_ntb.add(cesta_general_frame, text='General', padding=15)
cesta_ntb.add(cesta_preajuste_frame, text='Preajuste', padding=15)

cesta_ntb.grid(row=0, column=0, sticky='nsew', padx=10)

###########33

graph_display_frame = tk.LabelFrame(graph_frame, width=870, height=450)
graph_config_frame = tk.LabelFrame(graph_frame, width=250, height=450)
graph_config_frame.columnconfigure(0, weight=1)
graph_config_frame.columnconfigure(1, weight=2)

graph_config_frame.grid(row=0, column=0)
graph_display_frame.grid(row=0, column=1)
graph_display_frame.grid_propagate(False)
graph_config_frame.grid_propagate(False)

graph_select_lb = tk.Label(graph_config_frame, text='Gráfico:')
graph_select_lb.grid(row=0, column=0, padx=10, pady=10, sticky='w')

l_graphs = ['Slag Foaming', 'K[MgO][B\u2082]']

graph_select_cmb = ttk.Combobox(graph_config_frame, state='readonly', values=l_graphs, width=20)
graph_select_cmb.grid(row=0, column=1)
graph_select_cmb.bind("<<ComboboxSelected>>", plot_graph)

graph_display_isd_frame = tk.Frame(graph_display_frame)
graph_config_isd_frame = tk.LabelFrame(graph_config_frame)
# graph_display_isd_frame.grid(row=0, column=0)


graph_display_mgob3_frame = tk.Frame(graph_display_frame)
graph_config_mgob3_frame = tk.LabelFrame(graph_config_frame)

###########
mgob3_plot = tkt.Graph(graph_display_mgob3_frame, x_min=0, x_max=5, y_min=0, y_max=15, x_tick=0.5, y_tick=2, widthh=500,
                         heightt=350, dec_y_axis=2)
mgob3_plot.grid(row=1, column=0)
mgob3_title_lb = tk.Label(graph_display_mgob3_frame, text='Curva de equilibrio MgO vs. B\u2082', font=('Arial', 13))
mgob3_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)


###########
ISD_plot_175 = tkt.Graph(graph_display_isd_frame, x_min=0, x_max=55, y_min=0, y_max=19, x_tick=10, y_tick=5, widthh=500,
                         heightt=350)
ISD_plot_175.grid(row=1, column=0)
ISD_175_title_lb = tk.Label(graph_display_isd_frame, text='Diagrama de solubilidad isotérmica B3=1.0', font=('Arial', 13))


#####
ISD_plot_15 = tkt.Graph(graph_display_isd_frame, x_min=0, x_max=55, y_min=0, y_max=19, x_tick=10, y_tick=5, widthh=500,
                        heightt=350)
ISD_plot_15.config(width=550, height=350)
ISD_15_title_lb = tk.Label(graph_display_isd_frame, text='Diagrama de solubilidad isotérmica B3=0.75', font=('Arial', 13))
ISD_15_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)

#########3333

ISD_plot_20 = tkt.Graph(graph_display_isd_frame, x_min=0, x_max=55, y_min=0, y_max=19, x_tick=10, y_tick=5, widthh=500,
                        heightt=350)
ISD_plot_20.config(width=550, height=350)
ISD_20_title_lb = tk.Label(graph_display_isd_frame, text='Diagrama de solubilidad isotérmica B3=1.25', font=('Arial', 13))
ISD_20_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)

#########
ISD_plot_25 = tkt.Graph(graph_display_isd_frame, x_min=0, x_max=55, y_min=0, y_max=19, x_tick=10, y_tick=5, widthh=500,
                        heightt=350)
ISD_plot_25.config(width=550, height=350)
ISD_plot_25.grid(row=1, column=0)
ISD_25_title_lb = tk.Label(graph_display_isd_frame, text='Diagrama de solubilidad isotérmica B3=1.75', font=('Arial', 13))
ISD_25_title_lb.grid(row=0, column=0, sticky='nsew', pady=10)

########


mgo_isd_value = tk.StringVar()
mgo_isd_value.set("6")
mgo_isd_value.trace("w", draw_point)
mgo_isd_entry = ttk.Entry(graph_config_isd_frame, width=10, textvariable=mgo_isd_value, justify='right')
mgo_isd_title_lb = tk.Label(graph_config_isd_frame, text='%MgO en escoria')

feo_value = tk.StringVar()
feo_value.set("30")
feo_value.trace("w", draw_point)
feo_entry = ttk.Entry(graph_config_isd_frame, width=10, textvariable=feo_value, justify='right')
feo_title_lb = tk.Label(graph_config_isd_frame, text='%FeO en escoria')

graph_b3_l = ["0.75", "1.0", "1.25", "1.75"]

graph_isd_b3_id = tk.StringVar()
graph_isd_b3_id.set("1.75")
graph_isd_b3_cmb = ttk.Combobox(graph_config_isd_frame, state='readonly', values=graph_b3_l, width=7, textvariable=graph_isd_b3_id)
graph_isd_b3_cmb.bind("<<ComboboxSelected>>", plot_ISD)
graph_isd_b3_lb = tk.Label(graph_config_isd_frame, text='Basicidad B\u2082')

mgo_isd_entry.grid(row=1, column=1, padx=10, pady=10)
mgo_isd_title_lb.grid(row=1, column=0, padx=10, pady=10, sticky='w')
feo_entry.grid(row=2, column=1, pady=10, padx=10)
feo_title_lb.grid(row=2, column=0, pady=10, padx=10, sticky='w')
graph_isd_b3_cmb.grid(row=3, column=1, padx=10, pady=10)
graph_isd_b3_lb.grid(row=3, column=0, padx=10, pady=10, sticky='w')

##########
mgo_mgob3_value = tk.StringVar()
mgo_mgob3_value.set("6")
mgo_mgob3_value.trace("w", plot_mgob3)
mgo_mgob3_entry = ttk.Entry(graph_config_mgob3_frame, width=10, textvariable=mgo_mgob3_value, justify='right')
mgo_mgob3_title_lb = tk.Label(graph_config_mgob3_frame, text='%MgO en escoria')

b2_value = tk.StringVar()
b2_value.set("1.75")
b2_value.trace("w", plot_mgob3)
b2_entry = ttk.Entry(graph_config_mgob3_frame, width=10, textvariable=b2_value, justify='right')
b2_title_lb = tk.Label(graph_config_mgob3_frame, text='Índice B\u2082:')

mgob3_plot.plot_point(float(b2_value.get()), float(mgo_mgob3_value.get()), size=8, color='red')

graph_k_id = tk.StringVar()
graph_k_id.set("10.142")
graph_k_cmb = ttk.Spinbox(graph_config_mgob3_frame, from_=10, to=35, increment=0.1, width=7, textvariable=graph_k_id)
graph_k_id.trace("w", plot_mgob3)
graph_k_b3_lb = tk.Label(graph_config_mgob3_frame, text='Const. eq.  K')

mgo_mgob3_entry.grid(row=1, column=1, padx=10, pady=10)
mgo_mgob3_title_lb.grid(row=1, column=0, padx=10, pady=10, sticky='w')
b2_entry.grid(row=2, column=1, pady=10, padx=10)
b2_title_lb.grid(row=2, column=0, pady=10, padx=10, sticky='w')
graph_k_cmb.grid(row=3, column=1, padx=10, pady=10)
graph_k_b3_lb.grid(row=3, column=0, padx=10, pady=10, sticky='w')
########
# Energy Frame

ene_bframe = tk.LabelFrame(energy_frame, padx=10, pady=10, height=445, width=260)
ene_disp_btn = ttk.Button(ene_bframe, text='Display', command=load_coes)
ene_disp_btn.pack()
ene_bframe.grid(row=1, column=1)
ene_bframe.pack_propagate(False)
ene_tframe = tk.LabelFrame(energy_frame, padx=10, pady=10, height=445, width=858)

ene_tframe.grid(row=1, column=2)
ene_tframe.grid_propagate(False)



############3

root.bind("<Configure>", updateScroll())
container.bind_all("<MouseWheel>", _on_mousewheel)
root.mainloop()

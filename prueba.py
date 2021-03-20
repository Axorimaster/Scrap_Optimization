import sqlite3
from pandastable import Table
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from PIL import ImageTk, Image

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

sb_h.pack(fill=tk.X, side=tk.BOTTOM, expand= tk.FALSE)
sb_v.pack(fill=tk.Y, side=tk.RIGHT, expand= tk.FALSE)
container.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
container.create_window(0,0, window=main_frame, anchor=tk.NW)


#Funciones
def update_df_inventario():
    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)
    l_comp_scrap_names = df_inventario['Nombre'].tolist()

    return l_comp_scrap_names


def update_df_comp():
    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)


def compare_lists(l1,l2):

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


def compare_dfs(df1,df2):

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
    print(frame_indx)
    frame = l_frames[frame_indx]

    for x in l_frames:
        if x == frame:
            x.grid(row=0, column=0)
        else:
            x.grid_forget()

    if frame_indx == 0:
        inv_query()

    elif frame_indx ==1:
        comp_query()
        comp_cmb.config(values=update_df_inventario())

    elif frame_indx == 2:
        gen_slides()


    print(frame)


def save_warning(df_1, df_2):

    if compare_lists(list(df_2.columns),['a','b','c','d','e']):
        pass

    else:
        if compare_dfs(df_1,df_2):
            pass
        else:
            save_wrn = tk.messagebox.askquestion('Advertencia','Si sale ahora perderá todos los datos datos no guardados. ¿Desea continuar?', icon='warning')
            if save_wrn == 'yes':
                pass
            else:
                return False


def cb(event):

    item = str(menu_tv.focus())
    next_frame_name = menu_tv.item(item, "text")
    next_frame_idx = l_frames_names.index(next_frame_name)

    if next_frame_idx != current_frame.get():

        if current_frame.get()== 0:
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
    print(df_inventario)


def comp_save_sql():
    df_comp.reset_index(drop=True, inplace=True)
    df_comp.to_sql('comp_data', conn, if_exists='replace', index=False)


##
def inv_submit():
    df_inventario = pd.read_sql_query("SELECT * FROM scrap_data", conn)

    if f_nombre.get() in df_inventario['Nombre'].tolist():
        messagebox.showerror(title="Error",message="Ya existe una chatarra con ese nombre")
        return
    else:
        precio = 0.0
        densidad = 0.0
        inventario = 0.0
        rendimiento = 0.0
        energia = 0.0
        l_inv_sql = [precio,densidad,inventario,rendimiento,energia]
        count= 0

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

            cur.execute("INSERT INTO scrap_data VALUES (:f_nombre, :f_precio, :f_densidad, :f_inventario, :f_rendimiento, :f_energia)",
                        {
                            'f_nombre': f_nombre.get(),
                            'f_precio': l_inv_sql[0],
                            'f_densidad': l_inv_sql[1],
                            'f_inventario': l_inv_sql[2],
                            'f_rendimiento': l_inv_sql[3],
                            'f_energia': l_inv_sql[4]
                        })

            conn.commit()

            f_nombre.delete(0,tk.END)
            f_precio.delete(0,tk.END)
            f_densidad.delete(0,tk.END)
            f_energia.delete(0,tk.END)
            f_rendimiento.delete(0,tk.END)
            f_inventario.delete(0,tk.END)

            inv_query()

            comp_cmb.config(values=update_df_inventario())


def comp_submit():

    df_comp = pd.read_sql_query("SELECT * FROM comp_data", conn)


    if comp_cmb.get() in df_comp['Nombre'].tolist():

        messagebox.showerror(title="Error",message="Ya existe una chatarra con ese nombre")
        return

    else:

        cur=conn.cursor()
        cur.execute("INSERT INTO comp_data VALUES (:f_nombre, :f_c, :f_mn, :f_si, :f_p, :f_cr, :f_s, :f_cu, :f_ni, :f_mo)",
                    {
                        'f_nombre': comp_cmb.get(),
                        'f_c': float(comp_c_e.get()),
                        'f_mn': float(comp_mn_e.get()),
                        'f_si': float(comp_si_e.get()),
                        'f_p': float(comp_p_e.get()),
                        'f_cr': float(comp_cr_e.get()),
                        'f_s': float(comp_s_e.get()),
                        'f_cu': float(comp_cu_e.get()),
                        'f_ni': float(comp_ni_e.get()),
                        'f_mo': float(comp_mo_e.get())
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
    print(df_inventario)
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

    ask = messagebox.askquestion(title=None, message='¿Desea eliminar este dato?')
    if ask=='yes':
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
    ask = messagebox.askquestion(title=None, message='¿Desea eliminar este dato?')
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

########################
def start_sim():

    return


def comp_print_name(*args):

    l_nombres = df_comp['Nombre'].tolist()
    comp_values = df_comp.values.tolist()

    if comp_scrap_name.get() != ' ':

        comp_scrapname_label.configure(text='Se ha seleccionado {}'.format(comp_scrap_name.get()))

        if comp_scrap_name.get() in l_nombres:
            scrap_indx = l_nombres.index(comp_scrap_name.get())
            x=0

            for entry in l_comp_entries:

                val = str(comp_values[scrap_indx][x+1])
                print(val)
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, val)
                x+=1

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
    gen_slides.l_inv_valid = []
    l_inv_valid_name = []

    for widget in res_llframe.winfo_children():
        widget.destroy()

    for x in range(len(df_inventario)):
        l_inv_values[x] = float(l_inv_values[x])
        if l_inv_values[x] != 0.0:
            gen_slides.l_inv_valid.append(l_inv_values[x])
            l_inv_valid_name.append(l_inv_names[x])

    print(l_inv_values)

    inv_n_scraps.set(len(gen_slides.l_inv_valid))

    gen_slides.l_res_slides = []
    gen_slides.l_res_sl_lb = []
    row = 0

    for x in range(inv_n_scraps.get()):
        slide = tk.Scale(res_llframe, orient='horizontal', tickinterval=100, from_=0, to=100, resolution=5, showvalue=True, digits=0, sliderlength=15, label=l_inv_valid_name[x], command=res_calc_inv)
        slide.set(100)
        slide.grid(row=row, column=0, padx=10, pady=2)
        label = tk.Label(res_llframe, text=(slide.get()*gen_slides.l_inv_valid[x])/100)
        label.grid(row=row, column=1)

        row += 1
        gen_slides.l_res_slides.append(slide)
        gen_slides.l_res_sl_lb.append(label)


def res_calc_inv(*args):

    sum = 0
    x = 0

    for slide in gen_slides.l_res_slides:
        porcentaje = (slide.get())/100
        inv = gen_slides.l_inv_valid[x]
        inv_ll = round(porcentaje*inv,0)
        slide = gen_slides.l_res_sl_lb[x]
        slide.config(text=inv_ll)

        sum+=inv_ll


        x += 1

    res_invll_lb.config(text=sum)

    return(sum)



#Frame del título y logo del programa
title_frame = tk.Frame(main_frame, padx=5, pady=5)
title_frame.grid(row=0, column=0, padx=0, pady=0, columnspan =2)

#Frame de display de otros frames del programa
disp_frame = tk.LabelFrame(main_frame, text="Config.",padx=20, pady=20, height=510, width=1165)
disp_frame.grid(row=1, column=1)
disp_frame.grid_propagate(False)

#Listado de frames
inv_frame = tk.Frame(disp_frame)
comp_frame = tk.Frame(disp_frame)
res_frame = tk.Frame(disp_frame)
param_frame = tk.Frame(disp_frame)

l_frames = (inv_frame, comp_frame, res_frame, param_frame)
l_frames_names = ['Inventario', 'Composición', 'Restricciones', 'Parámetros']
current_frame = tk.IntVar(master=None)
current_frame.set(1000)

#Frame de TreeView
tv_frame = tk.LabelFrame(main_frame, text="Menú", padx=20, pady=20, height=510, width=300)
tv_frame.grid(row=1, column=0, padx=20, pady=20)
tv_frame.grid_propagate(False)

#Conexión a SQLITE3
conn = sqlite3.connect('scrap.db')
cur = conn.cursor()

"""
cur.execute("CREATE TABLE scrap_data (Nombre TEXT, Precio FLOAT , Densidad FLOAT, Inventario INTEGER, Rendimiento FLOAT, Energia FLOAT)")
"""

##Frame del título del programa
img_1 = Image.open('Images/Kedalion.png')
img_2 = Image.open('Images/kedalion_desk.png')
img_1 = img_1. resize((580, 200), Image. ANTIALIAS)
kedalion_img = ImageTk.PhotoImage(img_1)
lb_1 = tk.Label(title_frame, image=kedalion_img)
lb_1.grid(row=0, column=0, columnspan=2)
img_2 = img_2.resize((12,12), Image.ANTIALIAS)
tv_icon = ImageTk.PhotoImage(img_2)

##Menu Frame
menu_tv = ttk.Treeview(tv_frame)
menu_tv.grid(row=0, column=0, columnspan=2, sticky='nsew')
menu_top = menu_tv.insert("", tk.END, text=' Kedalion', image=tv_icon, tags=('cd'), open=True)
menu_datos = menu_tv.insert(menu_top, tk.END, text='Datos', tags=('cd'))
menu_simu = menu_tv.insert(menu_top, tk.END, text='Simulación', tags=('cd'))
menu_result = menu_tv.insert(menu_top, tk.END, text='Resultados', tags=('cd'))
menu_tv.insert(menu_datos, tk.END, text='Inventario', tags=('cb'))
menu_tv.insert(menu_datos, tk.END, text='Composición', tags=('cb'))
menu_tv.insert(menu_simu, tk.END, text='Restricciones', tags=('cb'))
menu_tv.insert(menu_simu, tk.END, text='Parámetros', tags=('cb'))
menu_tv.insert(menu_result, tk.END, text='Reporte', tags=('cb'))
menu_tv.insert(menu_result, tk.END, text='Gráficos', tags=('cb'))
menu_tv.tag_bind('cb','<Double-1>', cb)
menu_tv.tag_configure(tagname='cb' ,font=('Segoe', 10))
menu_tv.tag_configure(tagname='cd' ,font=('Segoe', 10))

b_quit = ttk.Button(tv_frame, text="Salir", command=root.quit)
b_start = ttk.Button(tv_frame, text='Iniciar', command=start_sim)
b_start.grid(row=1, column=1, padx=10, pady=10)
b_quit.grid(row=1, column=0)


##Inv frame
inv_bframe = tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=260)
inv_bframe.grid(row=1, column=1)
inv_bframe.grid_propagate(False)
inv_tframe =tk.LabelFrame(inv_frame, padx=10, pady=10, height=445, width=858)
inv_tframe.grid(row=1, column=2)
inv_tframe.grid_propagate(False)

table_scrap = Table(inv_tframe, showstatusbar=True)
table_scrap.show()

inv_n_scraps = tk.IntVar()
inv_n_scraps.set(0)

inv_entries_lb = tk.Label(inv_bframe, text='Datos de Chatarra')
inv_entries_lb.grid(row=0, column=0, columnspan=2, sticky='w',pady=5)

f_nombre = tk.Entry(inv_bframe, width=25)
lb_nombre = tk.Label(inv_bframe, text="Nombre")
f_nombre.grid(row=1, column=1, pady=5, sticky='e')
lb_nombre.grid(row=1, column=0, pady=5, sticky='w')

f_precio = tk.Entry(inv_bframe, width=25)
lb_precio = tk.Label(inv_bframe, text="Precio")
f_precio.grid(row=2, column=1, pady=5, sticky='e')
lb_precio.grid(row=2, column=0, pady=5, sticky='w')

f_densidad =tk.Entry(inv_bframe, width=25)
lb_densidad = tk.Label(inv_bframe, text="Densidad")
f_densidad.grid(row=3, column=1, pady=5, sticky='e')
lb_densidad.grid(row=3, column=0, pady=5, sticky='w')

f_inventario = tk.Entry(inv_bframe, width=25)
lb_inventario = tk.Label(inv_bframe, text="Inventario")
f_inventario.grid(row=4, column=1, pady=5, sticky='e')
lb_inventario.grid(row=4, column=0, pady=5, sticky='w')

f_rendimiento = tk.Entry(inv_bframe, width=25)
lb_rendimiento = tk.Label(inv_bframe, text="Rendimiento")
f_rendimiento.grid(row=5, column=1, pady=5, sticky='e')
lb_rendimiento.grid(row=5, column=0, pady=5, sticky='w')

f_energia = tk.Entry(inv_bframe, width=25)
lb_energia = tk.Label(inv_bframe, text="Energía")
f_energia.grid(row=6, column=1, pady=7, sticky='e')
lb_energia.grid(row=6, column=0, pady=7, sticky='w')

inv_separator1 = ttk.Separator(inv_bframe, orient='horizontal')
inv_separator1.grid(row=7, column=0, columnspan=2, pady=5, sticky='ew')

inv_submit_b = ttk.Button(inv_bframe, text="Añadir", command=inv_submit)
inv_query_b =ttk.Button(inv_bframe, text='Mostrar', command=inv_query)
inv_save_b = ttk.Button(inv_bframe, text='Guardar', command=inv_save_sql)
inv_delete_b = ttk.Button(inv_bframe, text='Eliminar', command=inv_delete)
inv_submit_b.grid(row=8, column=0, pady=10, columnspan=2, ipadx=10, ipady=1.5)
inv_query_b.grid(row=9, column=0, pady=10, columnspan=2, ipadx=10, ipady=1.5)
inv_save_b.grid(row=10, column=0, pady=10, columnspan=2, ipadx=10, ipady=1.5)
inv_delete_b.grid(row=11, column=0, pady=10, columnspan=2, ipadx=10, ipady=1.5)

l_inv_entries = [f_precio, f_densidad, f_inventario, f_rendimiento, f_energia]

#Composición Frame
comp_bframe = tk.LabelFrame(comp_frame, padx=10, pady=10, height=445, width=260)
comp_bframe.grid(row=1, column=1, sticky='nsew')
comp_bframe.grid_propagate(False)
comp_tframe =tk.LabelFrame(comp_frame, padx=10, pady=10, height=445, width=858)
comp_tframe.grid(row=1, column=2)
comp_tframe.grid_propagate(False)

table_comp = Table(comp_tframe, showstatusbar=True)
table_comp.show()

l_comp_scrap_names = []
l_comp_scrap_names.insert(0," ")
comp_scrap_name = tk.StringVar(comp_frame)
comp_scrap_name.set(l_comp_scrap_names[0])
comp_cmb = ttk.Combobox(comp_bframe, width=22, textvariable=comp_scrap_name, values=l_comp_scrap_names)
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
comp_c_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_c_lb.grid(row=3, column=0, pady=5)
comp_c_e.grid(row=3, column=1, pady=5)

comp_mn_lb = tk.Label(comp_bframe, text='Mn')
comp_mn_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_mn_lb.grid(row=3, column=3, pady=5)
comp_mn_e.grid(row=3, column=4, pady=5)

comp_si_lb = tk.Label(comp_bframe, text='Si')
comp_si_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_si_lb.grid(row=4, column=0, pady=5)
comp_si_e.grid(row=4, column=1, pady=5)

comp_p_lb = tk.Label(comp_bframe, text='P')
comp_p_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_p_lb.grid(row=4, column=3, pady=5)
comp_p_e.grid(row=4, column=4, pady=5)

comp_cr_lb = tk.Label(comp_bframe, text='Cr')
comp_cr_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_cr_lb.grid(row=5, column=0, pady=5)
comp_cr_e.grid(row=5, column=1, pady=5)

comp_s_lb = tk.Label(comp_bframe, text='S')
comp_s_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_s_lb.grid(row=5, column=3, pady=5)
comp_s_e.grid(row=5, column=4, pady=5)

comp_cu_lb = tk.Label(comp_bframe, text='Cu')
comp_cu_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_cu_lb.grid(row=6, column=0, pady=5)
comp_cu_e.grid(row=6, column=1, pady=5)

comp_ni_lb = tk.Label(comp_bframe, text='Ni')
comp_ni_e = tk.Entry(comp_bframe, width=5, state='disabled')
comp_ni_lb.grid(row=6, column=3, pady=5)
comp_ni_e.grid(row=6, column=4, pady=5)

comp_mo_lb = tk.Label(comp_bframe, text='Mo')
comp_mo_e = tk.Entry(comp_bframe, width=5, state='disabled')
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

##Restricciones Frame
res_bframe = tk.LabelFrame(res_frame, padx=10, pady=10, height=445, width=260)
res_bframe.grid(row=1, column=1, sticky='nsew')
res_bframe.grid_propagate(False)
res_tframe =tk.LabelFrame(res_frame, padx=10, pady=10, height=445, width=858)
res_tframe.grid(row=1, column=2)
res_tframe.pack_propagate(False)

res_ll_cn = tk.Canvas(res_tframe)
res_cn_scb = ttk.Scrollbar(res_tframe, orient='vertical', command=res_ll_cn.yview)
res_llframe = tk.Frame(res_ll_cn)

res_llframe.bind('<Configure>', lambda e: res_ll_cn.configure(scrollregion=res_ll_cn.bbox('all')))
res_ll_cn.create_window((0,0), window=res_llframe, anchor='nw')

res_ll_cn.pack(side='left', fill='both', expand=True)
res_cn_scb.pack(side='right', fill='y')

res_invll_lb = tk.Label(res_bframe, text=res_calc_inv)
res_invll_lb.grid(row=0, column=1)




root.bind("<Configure>", updateScroll())
root.mainloop()

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DRIVE (Tu conexión original) ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="wide")

# --- MOTOR DE UBICACIÓN (Tu lógica: 99 + secuencia ABCD +1) ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        if "-" not in ubi_str: return "99-01A"
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                      (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, 
                       fecha TEXT, ubicacion TEXT, deposito TEXT)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- INTERFAZ ESTILO DESKTOP COMPLETA ---
st.title("🖥️ LOGISTICA - SISTEMA DE GESTIÓN INTEGRAL")

# Botón de Sincronización (No se pierde)
if st.button("🔄 CLONAR DATOS DESDE DRIVE (LOGISTICA.EXE)"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA")
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS / MOVIMIENTOS", "📤 DESPACHO / SALIDAS", "📊 PLANILLA GENERAL"])

# --- TAB 1: MOVIMIENTOS ---
with tab1:
    st.subheader("Ingreso de Mercadería")
    
    # Búsqueda elástica por Nombre, Código o Barras
    bus_m = st.text_input("🔍 Buscar en Maestra (Escribe o Escanea)", key="bus_m")
    
    try:
        query_m = "SELECT * FROM maestra WHERE cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?"
        maestra_df = pd.read_sql(query_m, conn, params=(f'%{bus_m}%', f'%{bus_m}%', f'%{bus_m}%'))
        
        # Lista desplegable con Descripción Completa
        opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']} | {x['barras']}", axis=1).tolist()
        seleccion = st.selectbox("Seleccione el producto exacto:", options=[""] + opciones)
        
        if seleccion:
            item = maestra_df[maestra_df['cod_int'] == seleccion.split(" | ")[0]].iloc[0]
            cod_sel, nom_sel, bar_sel = item['cod_int'], item['nombre'], item['barras']
        else:
            cod_sel, nom_sel, bar_sel = "", "", ""
    except:
        cod_sel, nom_sel, bar_sel = "", "", ""

    with st.form("form_entrada", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_cod = st.text_input("Código Interno", value=cod_sel)
            f_nom = st.text_input("Descripción / Nombre", value=nom_sel)
            f_bar = st.text_input("Código de Barras", value=bar_sel)
            f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        
        with col2:
            f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
            f_ubi = st.text_input("Ubicación", value=motor_sugerencia_pc(conn))
            f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4, help="Solo números, el sistema pone la barra")

        if st.form_submit_button("⚡ REGISTRAR EN INVENTARIO"):
            if f_cod and len(f_venc_raw) == 4:
                # Formato mm/aa automático
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", 
                             (f_cod, f_can, f_nom, f_bar, f_venc, f_ubi, f_dep))
                conn.commit()
                st.success(f"Registrado: {f_nom} en {f_ubi}")
                st.rerun()

# --- TAB 2: DESPACHO ---
with tab2:
    st.subheader("Buscador de Stock para Despacho")
    bus_d = st.text_input("🔍 Buscar por Nombre, Código o Barras", key="bus_d")
    
    if bus_d:
        query_d = "SELECT rowid, * FROM inventario WHERE (cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?) AND cantidad > 0"
        res = pd.read_sql(query_d, conn, params=(f'%{bus_d}%', f'%{bus_d}%', f'%{bus_d}%'))
        
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} - Cantidad: {r['cantidad']}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Cód:** {r['cod_int']}")
                c1.write(f"**Barras:** {r['barras']}")
                c2.write(f"**Ubicación:** {r['ubicacion']}")
                c2.write(f"**Depósito:** {r['deposito']}")
                c3.write(f"**Vencimiento:** {r['fecha']}")
                
                cant_baja = st.number_input("Cantidad a retirar", min_value=1.0, max_value=float(r['cantidad']), key=f"del_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (cant_baja, r['rowid']))
                    conn.commit()
                    st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    st.subheader("Vista de Tablas (Excel Style)")
    modo = st.radio("Seleccionar Tabla:", ["Inventario", "Maestra"], horizontal=True)
    tabla = "inventario" if modo == "Inventario" else "maestra"
    
    df_ver = pd.read_sql(f"SELECT * FROM {tabla}", conn)
    st.dataframe(df_ver, use_container_width=True, hide_index=True)

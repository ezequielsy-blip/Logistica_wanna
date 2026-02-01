import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os
import re

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- MOTOR DE UBICACIÓN (Lógica idéntica a tu función sugerir_ubicacion de PC) ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        # Busca la última ubicación que empiece con 99-
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        
        if "-" not in ubi_str: return "99-01A"
        
        partes = ubi_str.split("-")
        cuerpo = partes[1] # Ejemplo: 01A
        
        # Extraer letra y número
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: # A, B o C -> Siguiente letra
                nueva_letra = ciclo[idx+1]
                nuevo_num = num_actual
            else: # Es D -> Vuelve a A y suma número
                nueva_letra = 'A'
                nuevo_num = num_actual + 1
        else:
            nueva_letra = 'A'
            nuevo_num = num_actual + 1
            
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except:
        return "99-01A"

# --- CONEXIÓN DB ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Estructura exacta de tu init_db de PC
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                      (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, 
                       fecha TEXT, ubicacion TEXT, deposito TEXT)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- INTERFAZ ---
st.title("📦 WMS PROFESIONAL MÓVIL")
st.info("Sincronizado con: LOGISTICA.EXE")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA")
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 MOVIMIENTOS", "📤 DESPACHO", "📊 PLANILLA"])

# --- TAB 1: MOVIMIENTOS (Basado en tu tab_mov) ---
with tab1:
    st.subheader("Entrada de Mercadería")
    try:
        maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
        cod_sel = st.selectbox("Buscar Producto (Maestra)", options=[""] + maestra_df['cod_int'].tolist())
        nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""
        ubi_sug = motor_sugerencia_pc(conn)
    except: cod_sel, nom_auto, ubi_sug = "", "", "99-01A"

    with st.form("form_mov", clear_on_submit=True):
        f_cod = st.text_input("Cod Int", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0)
        with c2: f_dep = st.selectbox("Depósito", ["DEPO 1", "DEPO 2"])
        
        c3, c4 = st.columns(2)
        # Formato fecha auto MM/AA
        with c3: f_venc_raw = st.text_input("Vencimiento (MM/AA)", placeholder="Ej: 1226", max_chars=4)
        with c4: f_ubi = st.text_input("Ubicación", value=ubi_sug)
        
        if st.form_submit_button("⚡ REGISTRAR MOVIMIENTO"):
            if f_cod and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                # Insert idéntico a tu función procesar_carga
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", 
                             (f_cod, f_can, f_nom, "", f_venc, f_ubi, f_dep))
                conn.commit()
                st.success(f"Cargado en {f_ubi}")
                st.rerun()

# --- TAB 2: DESPACHO (Basado en tu lógica de Salida) ---
with tab2:
    st.subheader("Salida de Mercadería")
    bus = st.text_input("🔍 Buscar por Nombre, Cod o Barras")
    if bus:
        query = f"""
            SELECT rowid, cod_int, nombre, cantidad, ubicacion, fecha, deposito 
            FROM inventario 
            WHERE (cod_int LIKE '%{bus}%' OR nombre LIKE '%{bus}%') 
            AND cantidad > 0
        """
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} | Stock: {r['cantidad']}"):
                # Micro-detalles solicitados
                st.write(f"**Vence:** {r['fecha']} | **Ubi:** {r['ubicacion']} | **Depo:** {r['deposito']}")
                
                baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()

# --- TAB 3: PLANILLA (Tu visor de PC) ---
with tab3:
    st.subheader("Planilla General")
    tabla_ver = st.radio("Ver tabla:", ["inventario", "maestra"], horizontal=True)
    try:
        df_full = pd.read_sql(f"SELECT * FROM {tabla_ver}", conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sincroniza para ver la planilla.")

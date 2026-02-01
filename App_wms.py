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

# --- LÓGICA DE UBICACIÓN (PC MODE: 99 -> ABCD) ---
def calcular_proxima_ubicacion(conn):
    try:
        df = pd.read_sql("SELECT ubicacion FROM inventario", conn)
        if df.empty: return "1"
        ubis = df['ubicacion'].astype(str).tolist()
        numeros = [int(u) for u in ubis if u.isdigit()]
        if not numeros:
            letras = [u for u in ubis if u.isalpha() and len(u)==1]
            if letras:
                ultima = max(letras)
                return chr(ord(ultima) + 1) if ultima < 'z' else "a1"
            return "1"
        max_num = max(numeros)
        if max_num < 99: return str(max_num + 1)
        else:
            letras = [u for u in ubis if u.isalpha() and len(u)==1]
            if not letras: return "a"
            ultima = max(letras)
            return chr(ord(ultima) + 1) if ultima < 'z' else "a1"
    except: return "1"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

st.title("🚀 SISTEMA LOGISTICA & STOCK")

if st.button("🔄 SINCRONIZAR TODO (DRIVE)"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA")
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Carga (Réplica LOGISTICA.exe)")
    try:
        maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
        cod_sel = st.selectbox("Código", options=[""] + maestra_df['cod_int'].tolist())
        nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""
        ubi_sug = calcular_proxima_ubicacion(conn)
    except: cod_sel, nom_auto, ubi_sug = "", "", "1"

    with st.form("carga", clear_on_submit=True):
        f_cod = st.text_input("Cód. Interno", value=cod_sel)
        f_nom = st.text_input("Descripción", value=nom_auto)
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", ["DEPO1", "DEPO2"])
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4, help="Ej: 1226")
        with c4: f_ubi = st.text_input("Ubicación Sugerida", value=ubi_sug)
        
        if st.form_submit_button("💾 REGISTRAR ENTRADA"):
            if f_cod and f_nom and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado con vencimiento {f_venc}")
                st.rerun()

with tab2:
    st.subheader("Salidas (Réplica APP_STOCK.py)")
    bus = st.text_input("🔍 Buscar por Nombre o Código", key="search_salida")
    if bus:
        # Traemos todos los campos necesarios para mostrar los detalles solicitados
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento 
            FROM inventario i 
            JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%') 
            AND i.cantidad > 0
        """
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            # Título del expander con nombre y stock total
            with st.expander(f"📦 {r['nombre']} - Stock: {r['cantidad']}"):
                # Mostramos los micro-detalles solicitados
                st.markdown(f"""
                **Detalles del Lote:**
                * 📅 **Vencimiento:** {r['vencimiento']}
                * 📍 **Ubicación:** {r['ubicacion']}
                * 🏢 **Depósito:** {r['deposito']}
                * 🔢 **Stock Disponible:** {r['cantidad']}
                """)
                
                baja = st.number_input(f"Cantidad a retirar ({r['nombre']})", 
                                       min_value=1.0, 
                                       max_value=float(r['cantidad']), 
                                       key=f"val_{r['rowid']}")
                
                if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.success(f"Salida confirmada: {baja} unidades de {r['nombre']}")
                    st.rerun()

with tab3:
    st.subheader("Planilla General (Excel Total)")
    try:
        df_full = pd.read_sql("""
            SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
            i.deposito as [Depo], i.ubicacion as [Ubi], i.vencimiento as [Vence] 
            FROM inventario i 
            JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE i.cantidad > 0
        """, conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except: st.info("Sincroniza para cargar la planilla.")

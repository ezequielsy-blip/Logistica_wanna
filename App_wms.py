import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DRIVE ---
# Usamos el link de descarga directa de Google
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
# Este link fuerza la descarga sin librerías extras
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# Estilo Tema Claro
st.markdown("""<style>.stApp { background-color: white; color: black; }</style>""", unsafe_allow_html=True)

def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        response = requests.get(URL_DIRECTA)
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f:
                f.write(response.content)
            st.success("✅ ¡Base de datos de la PC clonada!")
            st.rerun()
        else:
            st.error("No se pudo descargar. Revisa que el archivo en Drive sea 'Público'.")
    except Exception as e:
        st.error(f"Error: {e}")

# --- INICIO ---
st.set_page_config(page_title="LOGISTICA + STOCK", layout="centered")
st.title("📦 Sistema WMS Unificado")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

# Conexión
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# LAS 3 SOLAPAS
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Entradas")
    with st.form("f1", clear_on_submit=True):
        c = st.text_input("Código")
        n = st.text_input("Nombre")
        can = st.number_input("Cantidad", min_value=0.0)
        ub = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR ENTRADA"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (c, n))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", (c, can, ub, datetime.now().strftime('%d-%m-%Y')))
            conn.commit()
            st.success("¡Registrado!")

with tab2:
    st.subheader("Despacho")
    bus = st.text_input("🔍 Buscar...")
    if bus:
        df_res = pd.read_sql(f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{bus}%' OR ubicacion LIKE '%{bus}%'", conn)
        for i, r in df_res.iterrows():
            if r['cantidad'] > 0:
                with st.expander(f"📍 {r['ubicacion']} | Stock: {r['cantidad']}"):
                    baja = st.number_input("Sacar", min_value=1.0, key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()

with tab3:
    st.subheader("Inventario Completo")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Ubicación FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

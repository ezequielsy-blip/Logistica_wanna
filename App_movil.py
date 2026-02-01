import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import gdown
import os

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL = f'https://drive.google.com/uc?id={FILE_ID}'

# Forzar el tema claro
st.markdown("""<style>
    .stApp { background-color: white; color: black; }
    header {visibility: hidden;}
    </style>""", unsafe_allow_html=True)

# Función para sincronizar con Drive
def descargar_de_drive():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        gdown.download(URL, DB_NAME, quiet=False)
        st.success("✅ Datos clonados de la PC con éxito")
        st.rerun()
    except Exception as e:
        st.error("Error al conectar con Drive. Verifica el enlace.")

# --- INICIO ---
st.set_page_config(page_title="LOGISTICA + STOCK", layout="centered")
st.title("📦 Sistema WMS Unificado")

if st.button("🔄 CLONAR DATOS DESDE DRIVE (PC)"):
    descargar_de_drive()

# Conexión
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# LAS 3 PESTAÑAS (Aquí está la clave)
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Registrar Ingreso (LOGISTICA)")
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
    st.subheader("Buscador de Despacho (APP_STOCK)")
    bus = st.text_input("🔍 Buscar por Código o Ubicación")
    if bus:
        df_res = pd.read_sql(f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{bus}%' OR ubicacion LIKE '%{bus}%'", conn)
        for i, r in df_res.iterrows():
            if r['cantidad'] > 0:
                with st.expander(f"📍 {r['ubicacion']} | Stock: {r['cantidad']}"):
                    baja = st.number_input("Sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()

with tab3:
    st.subheader("Inventario Completo (EXCEL)")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Ubicación, fecha as Registro FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

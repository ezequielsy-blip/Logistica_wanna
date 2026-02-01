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

# Función para bajar la base de tu PC al Celular
def descargar_de_drive():
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        gdown.download(URL, DB_NAME, quiet=False)
        st.success("✅ Datos clonados de la PC con éxito")
        st.rerun()
    except Exception as e:
        st.error("Error al conectar con Drive. Verifica el enlace.")

# --- INICIO DE APP ---
st.set_page_config(page_title="WMS Master Unificado", layout="centered", initial_sidebar_state="collapsed")

# TEMA CLARO FORZADO POR CÓDIGO
st.markdown("""
    <style>
    .stApp { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 LOGISTICA + STOCK")

# BOTÓN DE SINCRONIZACIÓN
if st.button("🔄 CLONAR DATOS DESDE DRIVE (PC)"):
    descargar_de_drive()

# Conectar a la base descargada
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# Las 3 pestañas (Copia fiel de tus ejecutables)
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 EXCEL TOTAL"])

# 1. LOGISTICA (Igual a tu APP_LOGISTICA.exe)
with tab1:
    st.subheader("Ingreso de Mercadería")
    with st.form("form_log", clear_on_submit=True):
        f_cod = st.text_input("Código")
        f_nom = st.text_input("Nombre")
        f_can = st.number_input("Cantidad", min_value=0.0)
        f_ubi = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                         (f_cod, f_can, f_ubi, datetime.now().strftime('%d-%m-%Y')))
            conn.commit()
            st.success("Registrado")

# 2. APP_STOCK (Igual a tu buscador de despacho)
with tab2:
    st.subheader("Buscador de Despacho")
    bus = st.text_input("🔍 Buscar...")
    if bus:
        query = f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{bus}%' OR ubicacion LIKE '%{bus}%'"
        df_res = pd.read_sql(query, conn)
        for i, r in df_res.iterrows():
            if r['cantidad'] > 0:
                with st.expander(f"📍 {r['ubicacion']} | Stock: {r['cantidad']}"):
                    baja = st.number_input("Sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()

# 3. EXCEL TOTAL (Como tu Excel 2013)
with tab3:
    st.subheader("Inventario Completo")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Ubicación, fecha as Fecha FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

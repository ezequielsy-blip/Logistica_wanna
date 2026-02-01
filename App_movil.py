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

def descargar_de_drive():
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        gdown.download(URL, DB_NAME, quiet=False)
        st.sidebar.success("✅ Sincronizado con éxito")
    except Exception as e:
        st.sidebar.error("Error al conectar con Drive")

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

st.set_page_config(page_title="WMS Master", layout="centered")

# Botón de sincronización
if st.sidebar.button("🔄 Sincronizar con Drive"):
    descargar_de_drive()

# Inicializar DB y CREAR TABLAS (Esto evita el DatabaseError)
conn = conectar()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

st.title("🚀 WMS Logística & Stock")
tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 SALIDAS", "📊 STOCK TOTAL"])

with tab1:
    st.subheader("Ingreso (App Logística)")
    with st.form("in", clear_on_submit=True):
        c1 = st.text_input("Código")
        n1 = st.text_input("Nombre")
        ca1 = st.number_input("Cantidad", min_value=0.0)
        ub1 = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR ENTRADA"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (c1, n1))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", (c1, ca1, ub1, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success("Registrado")

with tab2:
    st.subheader("Despacho (App Stock)")
    bus = st.text_input("🔍 Buscar producto...")
    if bus:
        df = pd.read_sql(f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{bus}%' OR ubicacion LIKE '%{bus}%' AND cantidad > 0", conn)
        if not df.empty:
            for i, r in df.iterrows():
                with st.expander(f"📍 {r['ubicacion']} | Cant: {r['cantidad']}"):
                    baja = st.number_input("Sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()

with tab3:
    st.subheader("Inventario (Vista Excel)")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Ubicación FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

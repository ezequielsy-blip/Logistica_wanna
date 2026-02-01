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
        st.success("✅ Base sincronizada desde Google Drive")
        st.rerun()
    except Exception as e:
        st.error("Error al conectar con Drive. Verifica el enlace.")

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# --- INICIO DE APP ---
st.set_page_config(page_title="WMS Master Unificado", layout="centered")

# BOTÓN DE SINCRONIZACIÓN (Bien visible arriba)
if st.button("🔄 CLONAR DATOS DESDE DRIVE (PC)"):
    descargar_de_drive()

# Inicializar Base de Datos y Tablas
conn = conectar()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

st.title("📦 Gestión Logística & Stock")

# Las 3 pestañas que pediste (Copia fiel de tus apps)
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

# 1. LOGISTICA (Entradas)
with tab1:
    st.subheader("Registrar Ingreso de Mercadería")
    with st.form("form_log", clear_on_submit=True):
        f_cod = st.text_input("Código de Producto")
        f_nom = st.text_input("Nombre / Descripción")
        f_can = st.number_input("Cantidad", min_value=0.0)
        f_ubi = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR ENTRADA"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                         (f_cod, f_can, f_ubi, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success(f"Ingresado: {f_nom}")

# 2. APP_STOCK (Salidas/Buscador)
with tab2:
    st.subheader("Buscador para Despacho")
    bus = st.text_input("🔍 Buscar por Código o Ubicación")
    if bus:
        query = f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{bus}%' OR ubicacion LIKE '%{bus}%'"
        df_res = pd.read_sql(query, conn)
        if not df_res.empty:
            for i, r in df_res.iterrows():
                if r['cantidad'] > 0:
                    with st.expander(f"📍 {r['ubicacion']} | Stock: {r['cantidad']}"):
                        baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                        if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                            cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                            conn.commit()
                            st.success("Salida registrada")
                            st.rerun()
        else:
            st.info("No hay resultados con stock.")

# 3. EXCEL TOTAL (Vista General)
with tab3:
    st.subheader("Inventario Completo (Vista Excel)")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Ubicación, fecha as Registro FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

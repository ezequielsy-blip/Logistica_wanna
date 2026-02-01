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

# Función para descargar la base desde Drive
def descargar_de_drive():
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        gdown.download(URL, DB_NAME, quiet=False)
        st.success("✅ Base de datos sincronizada desde Drive")
    except Exception as e:
        st.error(f"Error al sincronizar: {e}")

# Función para conectar a la base local
def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LOGISTICA + STOCK", layout="centered")

# Sincronización inicial o por botón
if st.sidebar.button("🔄 Sincronizar con Drive"):
    descargar_de_drive()

# Inicializar conexión y tablas si no existen
conn = conectar()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

st.title("🚀 WMS Master Móvil")
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 DESPACHO", "📊 STOCK TOTAL"])

# --- TAB 1: LOGISTICA (Entradas) ---
with tab1:
    st.subheader("Ingreso de Mercadería")
    with st.form("form_entrada", clear_on_submit=True):
        f_cod = st.text_input("Código de Producto")
        f_nom = st.text_input("Nombre / Descripción")
        f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        f_ubi = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR ENTRADA"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                         (f_cod, f_can, f_ubi, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success(f"Ingresado: {f_nom} en {f_ubi}")

# --- TAB 2: DESPACHO (Salidas) ---
with tab2:
    st.subheader("Salida de Mercadería")
    busqueda = st.text_input("Buscar producto o ubicación...")
    if busqueda:
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion 
            FROM inventario i
            LEFT JOIN maestra m ON i.cod_int = m.cod_int
            WHERE i.cod_int LIKE '%{busqueda}%' OR m.nombre LIKE '%{busqueda}%' OR i.ubicacion LIKE '%{busqueda}%'
            AND i.cantidad > 0
        """
        df_res = pd.read_sql(query, conn)
        if not df_res.empty:
            for i, r in df_res.iterrows():
                with st.expander(f"📦 {r['nombre']} | Cant: {r['cantidad']} | 📍 {r['ubicacion']}"):
                    baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"n_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.success("Salida registrada")
                        st.rerun()
        else:
            st.warning("No se encontraron resultados.")

# --- TAB 3: STOCK TOTAL (Vista Excel 2013) ---
with tab3:
    st.subheader("Reporte de Inventario")
    query_total = """
        SELECT i.cod_int as Código, m.nombre as Producto, i.cantidad as Stock, i.ubicacion as Ubicación, i.fecha as Registro
        FROM inventario i
        LEFT JOIN maestra m ON i.cod_int = m.cod_int
        WHERE i.cantidad > 0
    """
    df_total = pd.read_sql(query_total, conn)
    st.dataframe(df_total, use_container_width=True)

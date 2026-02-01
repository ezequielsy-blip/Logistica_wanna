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

# Función para descargar la base de datos desde tu Google Drive
def descargar_de_drive():
    try:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        # Descarga el archivo de Drive al servidor de la App
        gdown.download(URL, DB_NAME, quiet=False)
        st.sidebar.success("✅ Base sincronizada desde Drive")
    except Exception as e:
        st.sidebar.error(f"Error al conectar con Drive: {e}")

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="WMS Master Móvil", layout="centered")

# Botón de sincronización en la barra lateral
if st.sidebar.button("🔄 Sincronizar con Drive"):
    descargar_de_drive()

# Inicializar DB y Tablas
conn = conectar()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

st.title("🚀 WMS Master Móvil")
st.write("Conectado a tu base de datos de PC")

# Las 3 solapas que pediste
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 INVENTARIO TOTAL"])

# --- 1. LOGISTICA (Igual a tu ejecutable de Entradas) ---
with tab1:
    st.subheader("Registro de Ingresos")
    with st.form("form_logistica", clear_on_submit=True):
        c_cod = st.text_input("Código de Producto")
        c_nom = st.text_input("Nombre / Descripción")
        c_can = st.number_input("Cantidad Entrante", min_value=0.0, step=1.0)
        c_ubi = st.text_input("Ubicación Destino")
        if st.form_submit_button("GUARDAR EN LOGISTICA"):
            if c_cod and c_nom:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (c_cod, c_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                             (c_cod, c_can, c_ubi, datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                st.success(f"Registrado: {c_nom} en {c_ubi}")
            else:
                st.warning("Por favor completa Código y Nombre")

# --- 2. APP_STOCK (Igual a tu buscador de despacho) ---
with tab2:
    st.subheader("Despacho de Mercadería")
    busqueda = st.text_input("🔍 Buscar por nombre, código o ubicación")
    
    if busqueda:
        # Busca en la tabla uniendo nombre de maestra y stock de inventario
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion 
            FROM inventario i
            LEFT JOIN maestra m ON i.col_int = m.cod_int
            WHERE (i.cod_int LIKE '%{busqueda}%' OR m.nombre LIKE '%{busqueda}%' OR i.ubicacion LIKE '%{busqueda}%')
            AND i.cantidad > 0
        """
        try:
            df_res = pd.read_sql(query, conn)
            if not df_res.empty:
                for i, r in df_res.iterrows():
                    with st.expander(f"📦 {r['nombre']} | Stock: {r['cantidad']} | 📍 {r['ubicacion']}"):
                        baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"b_{r['rowid']}")
                        if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                            cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                            conn.commit()
                            st.success("Salida registrada correctamente")
                            st.rerun()
            else:
                st.info("No se encontraron productos con stock.")
        except:
            # Si la base es nueva y no tiene datos aún
            st.warning("Carga productos en la pestaña LOGISTICA primero.")

# --- 3. INVENTARIO TOTAL (Vista tipo Excel 2013) ---
with tab3:
    st.subheader("Estado General del Depósito")
    query_total = """
        SELECT i.cod_int as Código, m.nombre as Producto, i.cantidad as Stock, i.ubicacion as Ubicación, i.fecha as Últ_Movimiento
        FROM inventario i
        LEFT JOIN maestra m ON i.cod_int = m.cod_int
        WHERE i.cantidad > 0
        ORDER BY i.fecha DESC
    """
    try:
        df_total = pd.read_sql(query_total, conn)
        st.dataframe(df_total, use_container_width=True)
    except:
        st.write("No hay datos para mostrar todavía.")

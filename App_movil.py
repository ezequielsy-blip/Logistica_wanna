import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="WMS Móvil", layout="centered")

# 2. CONEXIÓN Y CREACIÓN AUTOMÁTICA (Esto evita tus errores)
def iniciar_db():
    conn = sqlite3.connect('inventario_wms.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
    conn.commit()
    return conn

conn = iniciar_db()

st.title("📦 Sistema WMS Móvil")
tab1, tab2 = st.tabs(["📥 ENTRADAS", "📤 SALIDAS"])

# PESTAÑA DE ENTRADAS (LOGISTICA)
with tab1:
    st.subheader("Cargar Mercadería")
    with st.form("ingreso"):
        cod = st.text_input("Código")
        nom = st.text_input("Nombre")
        can = st.number_input("Cantidad", min_value=0.0)
        ubi = st.text_input("Ubicación")
        if st.form_submit_button("GUARDAR ENTRADA"):
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (cod, nom))
            c.execute("INSERT INTO inventario VALUES (?,?,?,?)", (cod, f"{can}", ubi, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success(f"Guardado: {nom}")

# PESTAÑA DE SALIDAS (STOCK/DESPACHO)
with tab2:
    st.subheader("Despacho")
    busqueda = st.text_input("Buscar producto...")
    if busqueda:
        query = f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{busqueda}%' OR ubicacion LIKE '%{busqueda}%'"
        df = pd.read_sql(query, conn)
        if not df.empty:
            for i, r in df.iterrows():
                st.write(f"📍 {r['ubicacion']} | Stock: {r['cantidad']}")
                if st.button(f"Descontar 1", key=str(r['rowid'])):
                    conn.execute(f"UPDATE inventario SET cantidad = cantidad - 1 WHERE rowid = {r['rowid']}")
                    conn.commit()
                    st.rerun()
        else:
            st.info("No hay stock. Cargá algo en ENTRADAS primero.")

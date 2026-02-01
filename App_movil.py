import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración visual
st.set_page_config(page_title="WMS Master Móvil", layout="centered")

# --- CONEXIÓN A BASE DE DATOS ---
# Nota: Para sincronizar con Drive real, usaremos el archivo local que Streamlit sincroniza
def conectar():
    conn = sqlite3.connect('inventario_wms.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
    conn.commit()
    return conn

conn = conectar()

st.title("🚀 Logística & Stock Unificado")

# Pestañas que unen tus 2 Apps de escritorio
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 INVENTARIO TOTAL"])

# 1. FUNCIÓN LOGISTICA (Entradas)
with tab1:
    st.subheader("Ingreso de Mercadería")
    with st.form("form_logistica"):
        c_cod = st.text_input("Código de Producto")
        c_nom = st.text_input("Nombre / Descripción")
        c_can = st.number_input("Cantidad Entrante", min_value=0.0)
        c_ubi = st.text_input("Ubicación Destino")
        if st.form_submit_button("REGISTRAR ENTRADA"):
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (c_cod, c_nom))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", (c_cod, c_can, c_ubi, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            st.success("Ingreso registrado correctamente")

# 2. FUNCIÓN APP_STOCK (Salidas/Despacho)
with tab2:
    st.subheader("Buscador de Despacho")
    busqueda = st.text_input("Buscar por nombre o código para sacar")
    if busqueda:
        df_salida = pd.read_sql(f"SELECT rowid, * FROM inventario WHERE cod_int LIKE '%{busqueda}%' AND cantidad > 0", conn)
        if not df_salida.empty:
            for i, r in df_salida.iterrows():
                with st.container():
                    col1, col2 = st.columns([2,1])
                    col1.write(f"📍 {r['ubicacion']} | Cant: {r['cantidad']}")
                    if col2.button(f"DESCONTAR", key=f"btn_{r['rowid']}"):
                        conn.execute(f"UPDATE inventario SET cantidad = cantidad - 1 WHERE rowid = {r['rowid']}")
                        conn.commit()
                        st.rerun()
        else:
            st.warning("No hay stock disponible.")

# 3. VISTA EXCEL (Inventario General)
with tab3:
    st.subheader("Estado Actual del Depósito")
    df_total = pd.read_sql("SELECT cod_int as Código, cantidad as Stock, ubicacion as Lugar, fecha as Registro FROM inventario WHERE cantidad > 0", conn)
    st.dataframe(df_total, use_container_width=True)

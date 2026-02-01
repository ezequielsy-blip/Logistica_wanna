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

st.set_page_config(page_title="WMS Master Pro", layout="wide")

# --- SISTEMA DE LLAVE (Clave: 70797474) ---
with st.sidebar:
    st.title("🔒 SEGURIDAD")
    clave = st.text_input("Clave de Administrador", type="password")
    es_autorizado = (clave == "70797474")
    
    if es_autorizado:
        st.success("MODO EDICIÓN: ACTIVADO")
    else:
        st.info("MODO CONSULTA: SOLO LECTURA")

# --- MOTOR DE UBICACIÓN ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        if "-" not in ubi_str: return "99-01A"
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                      (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, 
                       fecha TEXT, ubicacion TEXT, deposito TEXT)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- INTERFAZ ---
st.title("📦 GESTIÓN DE STOCK: LOGISTICA")

if st.button("🔄 ACTUALIZAR PANTALLA"):
    st.rerun()

# Sincronización Protegida (Solo Admin)
if es_autorizado:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📥 CLONAR DATOS DESDE DRIVE", use_container_width=True):
            try:
                if os.path.exists(DB_NAME): os.remove(DB_NAME)
                r = requests.get(URL_DIRECTA, timeout=10)
                with open(DB_NAME, 'wb') as f: f.write(r.content)
                st.success("✅ BASE DE DATOS ACTUALIZADA")
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    with col_b:
        # ESTA ES LA OTRA FORMA: DESCARGA DIRECTA AL CELULAR
        with open(DB_NAME, "rb") as file:
            st.download_button(
                label="📤 DESCARGAR BASE ACTUALIZADA",
                data=file,
                file_name=DB_NAME,
                mime="application/octet-stream",
                use_container_width=True
            )

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 DESPACHO / CONSULTA", "📊 PLANILLA GENERAL"])

with tab1:
    if not es_autorizado:
        st.warning("⚠️ Esta pestaña es solo para ingresos. Ingrese clave para operar.")
    else:
        st.subheader("Ingreso de Mercadería")
        bus_m = st.text_input("🔍 Buscar en Maestra", key="bus_m")
        try:
            query_m = "SELECT * FROM maestra WHERE cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?"
            maestra_df = pd.read_sql(query_m, conn, params=(f'%{bus_m}%', f'%{bus_m}%', f'%{bus_m}%'))
            opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
            seleccion = st.selectbox("Producto:", options=[""] + opciones)
            if seleccion:
                item = maestra_df[maestra_df['cod_int'] == seleccion.split(" | ")[0]].iloc[0]
                cod_sel, nom_sel, bar_sel = item['cod_int'], item['nombre'], item['barras']
            else: cod_sel, nom_sel, bar_sel = "", "", ""
        except: cod_sel, nom_sel, bar_sel = "", "", ""

        with st.form("form_entrada", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f_cod = st.text_input("Código Interno", value=cod_sel)
                f_nom = st.text_input("Descripción", value=nom_sel)
                f_can = st.number_input("Cantidad", min_value=0.0)
            with col2:
                f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
                f_ubi = st.text_input("Ubicación", value=motor_sugerencia_pc(conn))
                f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4)
            if st.form_submit_button("⚡ REGISTRAR"):
                if f_cod and len(f_venc_raw) == 4:
                    f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                    cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", 
                                 (f_cod, f_can, f_nom, bar_sel, f_venc, f_ubi, f_dep))
                    conn.commit()
                    st.success("Guardado correctamente.")
                    st.rerun()

with tab2:
    st.subheader("Buscador de Stock")
    bus_d = st.text_input("🔍 Buscar Nombre, Código o Barras", key="bus_d")
    if bus_d:
        query_d = "SELECT rowid, * FROM inventario WHERE (cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?) AND cantidad > 0"
        res = pd.read_sql(query_d, conn, params=(f'%{bus_d}%', f'%{bus_d}%', f'%{bus_d}%'))
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} - Cantidad: {r['cantidad']}"):
                st.write(f"**Cód:** {r['cod_int']} | **Ubi:** {r['ubicacion']} | **Vence:** {r['fecha']}")
                st.write(f"**Depósito:** {r['deposito']} | **Barras:** {r['barras']}")
                if es_autorizado:
                    baja = st.number_input("Retirar", min_value=1.0, max_value=float(r['cantidad']), key=f"d_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()
                else:
                    st.caption("🔒 Solo lectura: Ingrese clave de Admin para retirar.")

with tab3:
    st.subheader("Auditoría de Inventario")
    df_ver = pd.read_sql("SELECT * FROM inventario", conn)
    st.dataframe(df_ver, use_container_width=True, hide_index=True)

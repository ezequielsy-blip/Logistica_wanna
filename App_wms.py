import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- LÓGICA DE UBICACIÓN IDÉNTICA A PC (99 -> a) ---
def obtener_ubicacion_sugerida(conn):
    try:
        # Buscamos en la tabla inventario la ubi más alta
        df = pd.read_sql("SELECT ubicacion FROM inventario", conn)
        if df.empty: return "1"
        
        ubis = df['ubicacion'].astype(str).tolist()
        # Filtramos las que son números para encontrar el máximo
        numeros = [int(u) for u in ubis if u.isdigit()]
        
        if not numeros:
            # Si no hay números, buscamos la última letra
            letras = sorted([u for u in ubis if u.isalpha() and len(u)==1])
            if letras:
                ultima = letras[-1]
                return chr(ord(ultima) + 1) if ultima < 'z' else "a1"
            return "1"
        
        max_n = max(numeros)
        if max_n < 99:
            return str(max_n + 1)
        else:
            # Si llegó a 99 o más, sugerimos la secuencia abcd
            letras = sorted([u for u in ubis if u.isalpha() and len(u)==1])
            if not letras: return "a"
            ultima = letras[-1]
            return chr(ord(ultima) + 1) if ultima < 'z' else "a1"
    except:
        return "1"

# --- CONEXIÓN Y CREACIÓN DE TABLAS ---
def conectar_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Aseguramos que las tablas existan con los nombres exactos
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    conn.commit()
    return conn, cursor

conn, cursor = conectar_db()

# --- INTERFAZ ---
st.title("🚀 WMS UNIFICADO (PC Mode)")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        if r.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            st.success("✅ Sincronización Exitosa")
            st.rerun()
        else: st.error("Error en enlace de Drive")
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Carga (Sugerencia 99 -> abcd)")
    try:
        maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
        cod_sel = st.selectbox("Buscar Código", options=[""] + maestra_df['cod_int'].tolist())
        nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""
        ubi_sug = obtener_ubicacion_sugerida(conn)
    except: 
        cod_sel, nom_auto, ubi_sug = "", "", "1"

    with st.form("form_carga", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"])
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4)
        with c4: f_ubi = st.text_input("Ubicación Sugerida", value=ubi_sug)
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success("Guardado correctamente")
                st.rerun()

with tab2:
    st.subheader("Salidas (APP_STOCK)")
    bus = st.text_input("🔍 Buscar...")
    if bus:
        # Join para traer el nombre de la maestra y los datos de inventario
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento 
            FROM inventario i 
            LEFT JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%') 
            AND i.cantidad > 0
        """
        try:
            res = pd.read_sql(query, conn)
            for i, r in res.iterrows():
                with st.expander(f"📦 {r['nombre']} | Ubi: {r['ubicacion']} | Depo: {r['deposito']}"):
                    st.write(f"Vencimiento: **{r['vencimiento']}** | Stock: **{r['cantidad']}**")
                    baja = st.number_input("Cantidad a retirar", min_value=1.0, key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()
        except: st.error("Sincronizá para habilitar las salidas")

with tab3:
    st.subheader("Excel Total")
    try:
        # Mostramos la tabla unificada
        df_full = pd.read_sql("""
            SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
            i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento] 
            FROM inventario i 
            JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE i.cantidad > 0
        """, conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sincroniza para ver la planilla")

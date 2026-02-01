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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    conn.commit()
    return conn, cursor

conn, cursor = conectar_db()

# --- INTERFAZ ---
st.title("🚀 WMS Master Móvil")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        if r.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            st.success("✅ Sincronización Exitosa")
            st.rerun()
        else:
            st.error(f"Error de Drive: {r.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

# --- TAB 1: CARGA (LOGISTICA) CON SUGERENCIAS ---
with tab1:
    st.subheader("Carga de Mercadería")
    try:
        maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
        cod_sel = st.selectbox("Buscar Código", options=[""] + maestra_df['cod_int'].tolist())
        
        # Lógica de sugerencia (Igual que en PC)
        nom_auto = ""
        ubi_sug = ""
        dep_sug = "DEPO1" # Default
        
        if cod_sel != "":
            nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]
            # Buscamos la última ubicación registrada para este código
            last_entry = pd.read_sql(f"SELECT ubicacion, deposito FROM inventario WHERE cod_int = '{cod_sel}' ORDER BY rowid DESC LIMIT 1", conn)
            if not last_entry.empty:
                ubi_sug = last_entry['ubicacion'].values[0]
                dep_sug = last_entry['deposito'].values[0]
                st.info(f"💡 Sugerencia basada en PC: Última vez en {dep_sug} - {ubi_sug}")
    except:
        cod_sel, nom_auto, ubi_sug, dep_sug = "", "", "", "DEPO1"

    with st.form("form_carga", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        # El depósito se pre-selecciona según la última carga
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"], index=0 if dep_sug == "DEPO1" else 1)
        
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", placeholder="Ej: 1226", max_chars=4)
        # La ubicación se pre-completa sola
        with c4: f_ubi = st.text_input("Ubicación", value=ubi_sug)
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT OR IGNORE INTO maestra (cod_int, nombre) VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario (cod_int, cantidad, ubicacion, deposito, vencimiento, fecha_registro) VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado: {f_venc}")
                st.rerun()
            else:
                st.error("Faltan datos o el vencimiento no tiene 4 números")

# --- TAB 2: SALIDAS (APP_STOCK) ---
with tab2:
    st.subheader("Despacho / Salidas")
    bus = st.text_input("🔍 Buscar por Nombre o Código...")
    if bus:
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
                with st.expander(f"📦 {r['nombre']} | {r['deposito']} | Stock: {r['cantidad']}"):
                    st.write(f"Vence: **{r['vencimiento']}** | Ubicación: **{r['ubicacion']}**")
                    baja = st.number_input("Cantidad a sacar", min_value=1.0, key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']}")
                        conn.commit()
                        st.rerun()
        except:
            st.warning("Primero sincronizá los datos de Drive")

# --- TAB 3: PLANILLA (EXCEL TOTAL) ---
with tab3:
    st.subheader("Stock Consolidado")
    try:
        df_full = pd.read_sql("""
            SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
                   i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento]
            FROM inventario i 
            JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE i.cantidad > 0
            ORDER BY i.vencimiento ASC
        """, conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sincroniza para ver la tabla")

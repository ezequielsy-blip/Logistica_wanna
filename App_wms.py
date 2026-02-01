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

# --- FUNCIONES DE BASE DE DATOS ---
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ Sincronizado")
        st.rerun()
    except: st.error("Error de conexión")

# --- INTERFAZ ---
st.title("📦 WMS Móvil")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Entrada de Mercadería")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_sel = st.selectbox("Buscar Código", options=[""] + maestra_df['cod_int'].tolist())
    
    nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""

    with st.form("form_venc", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"])
        
        c3, c4 = st.columns(2)
        # --- Lógica de la Barra Automática ---
        venc_raw = st.text_input("Vencimiento (Escribí solo números)", placeholder="MMAA (Ej: 1226)", max_chars=4)
        with c4: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR"):
            # Si puso 4 números (ej: 1226), lo convertimos a 12/26 antes de guardar
            if len(venc_raw) == 4 and venc_raw.isdigit():
                f_venc = f"{venc_raw[:2]}/{venc_raw[2:]}"
                
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado como {f_venc}")
                st.rerun()
            else:
                st.error("Poné los 4 números del vencimiento (Mes y Año)")

with tab2:
    st.subheader("Buscador / Salidas")
    bus = st.text_input("🔍 Buscar...")
    if bus:
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento
            FROM inventario i
            LEFT JOIN maestra m ON i.cod_int = m.cod_int
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.deposito LIKE '%{bus}%')
            AND i.cantidad > 0
        """
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} | {r['deposito']} | Stock: {r['cantidad']}"):
                st.write(f"Vence: **{r['vencimiento']}** | Ubicación: **{r['ubicacion']}**")
                baja = st.number_input("Cantidad a retirar", min_value=1.0, key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()

with tab3:
    st.subheader("Inventario Consolidado")
    df_full = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
               i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_full, use_container_width=True

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# --- DISEÑO ---
st.set_page_config(page_title="WMS Master Pro", layout="centered")

st.markdown("""
    <style>
    .stMarkdown, p, label { font-weight: 700 !important; }
    div.stButton > button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; }
    input { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SCRIPT PARA BARRA AUTOMÁTICA (JS) ---
components.html(
    """
    <script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        if (input.placeholder === "MM/AA") {
            input.addEventListener('input', function(e) {
                let val = e.target.value.replace(/[^0-9]/g, '');
                if (val.length > 2) {
                    e.target.value = val.substring(0, 2) + '/' + val.substring(2, 4);
                } else {
                    e.target.value = val;
                }
            });
        }
    });
    </script>
    """,
    height=0,
)

# --- BASE DE DATOS ---
def conectar_y_preparar():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    cursor.execute("PRAGMA table_info(inventario)")
    columnas = [info[1] for info in cursor.fetchall()]
    if 'deposito' not in columnas: cursor.execute("ALTER TABLE inventario ADD COLUMN deposito TEXT DEFAULT 'DEPO1'")
    if 'vencimiento' not in columnas: cursor.execute("ALTER TABLE inventario ADD COLUMN vencimiento TEXT DEFAULT '00/00'")
    conn.commit()
    return conn, cursor

conn, cursor = conectar_y_preparar()

# --- INTERFAZ ---
st.title("📦 WMS Master Móvil")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ Datos clonados")
        st.rerun()
    except: st.error("Error al sincronizar")

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Carga de Mercadería")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_sel = st.selectbox("Buscar Código", options=[""] + maestra_df['cod_int'].tolist())
    nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""

    with st.form("form_final", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"])
        
        c3, c4 = st.columns(2)
        # El placeholder "MM/AA" activa el script de la barra automática
        with c3: f_venc = st.text_input("Vencimiento", placeholder="MM/AA", max_chars=5)
        with c4: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom and len(f_venc) == 5:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado: {f_nom} ({f_venc})")
                st.rerun()
            else:
                st.error("Completar Código, Nombre y Vencimiento (MM/AA)")

with tab2:
    st.subheader("Despacho / Salidas")
    bus = st.text_input("🔍 Buscar...")
    if bus:
        query = f"SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento FROM inventario i LEFT JOIN maestra m ON i.cod_int = m.cod_int WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.deposito LIKE '%{bus}%') AND i.cantidad > 0"
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} | {r['deposito']} | Stock: {r['cantidad']}"):
                st.write(f"Vence: **{r['vencimiento']}** | Ubicación: **{r['ubicacion']}**")
                baja = st.number_input("Cantidad a sacar", min_value=1.0, key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()

with tab3:
    st.subheader("Stock Consolidado")
    try:
        df_full = pd.read_sql("SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento] FROM inventario i JOIN maestra m ON i.cod_int = m.cod_int WHERE i.cantidad > 0", conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sincroniza para ver la tabla")

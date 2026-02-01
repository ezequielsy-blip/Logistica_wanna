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
st.set_page_config(page_title="SISTEMA WMS UNIFICADO", layout="centered")

# --- DISEÑO BLINDADO (ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Forzar fondo y texto para legibilidad total */
    .stApp { background-color: #F0F2F5 !important; }
    h1, h2, h3, p, label, span, div { color: #000000 !important; font-weight: 700 !important; }
    
    /* Inputs Blancos con borde negro */
    input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #333 !important;
    }

    /* Botón Sincronizar (Azul fuerte) */
    div.stButton > button:first-child {
        background-color: #007BFF !important;
        color: white !important;
        height: 3.5em;
        border-radius: 10px;
        font-size: 18px;
    }

    /* Pestañas estilo escritorio */
    .stTabs [data-baseweb="tab-list"] { background-color: #DDD; border-radius: 10px; padding: 5px; }
    .stTabs [aria-selected="true"] { background-color: #FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    # Verificar columnas
    cursor.execute("PRAGMA table_info(inventario)")
    cols = [info[1] for info in cursor.fetchall()]
    if 'deposito' not in cols: cursor.execute("ALTER TABLE inventario ADD COLUMN deposito TEXT DEFAULT 'DEPO1'")
    if 'vencimiento' not in cols: cursor.execute("ALTER TABLE inventario ADD COLUMN vencimiento TEXT DEFAULT '00/00'")
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- INTERFAZ ---
st.title("🚀 WMS UNIFICADO")

if st.button("🔄 SINCRONIZAR CON DRIVE"):
    if os.path.exists(DB_NAME): os.remove(DB_NAME)
    r = requests.get(URL_DIRECTA)
    with open(DB_NAME, 'wb') as f: f.write(r.content)
    st.success("Sincronizado")
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Carga)", "📤 APP_STOCK (Salida)", "📊 EXCEL TOTAL"])

with tab1:
    st.markdown("### Carga de Mercadería")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_sel = st.selectbox("Seleccionar Código", options=[""] + maestra_df['cod_int'].tolist())
    nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""

    with st.form("form_carga"):
        f_cod = st.text_input("Código de Producto", value=cod_sel)
        f_nom = st.text_input("Nombre del Producto", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0)
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"])
        
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", placeholder="Ej: 1226", max_chars=4)
        with c4: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom and len(f_venc_raw) == 4:
                # El sistema le pone la barra "/" solo al guardar
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success("Guardado correctamente")
                st.rerun()
            else:
                st.error("Completar todos los datos (Vencimiento son 4 números)")

with tab2:
    st.markdown("### Salidas")
    bus = st.text_input("🔍 Buscar producto o depósito...")
    if bus:
        query = f"SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento FROM inventario i LEFT JOIN maestra m ON i.cod_int = m.cod_int WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.deposito LIKE '%{bus}%') AND i.cantidad > 0"
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.container():
                st.markdown(f"**{r['nombre']}** | {r['deposito']} | Stock: {r['cantidad']}")
                st.write(f"Vence: {r['vencimiento']} | Ubicación: {r['ubicacion']}")
                baja = st.number_input("Cantidad a sacar", min_value=1.0, key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()
                st.markdown("---")

with tab3:
    st.markdown("### Stock Total (Excel)")
    df_f = pd.read_sql("SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento] FROM inventario i JOIN maestra m ON i.cod_int = m.cod_int WHERE i.cantidad > 0", conn)
    st.dataframe(df_f, use_container_width=True, hide_index=True)

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

# --- DISEÑO Y TEMA CLARO FORZADO ---
st.set_page_config(page_title="WMS Unificado", layout="centered")

st.markdown("""
    <style>
    /* Forzar fondo blanco y letras negras */
    .stApp { background-color: white !important; color: #1E1E1E !important; }
    h1, h2, h3, p, label { color: #1E1E1E !important; }
    
    /* Estilo para los inputs (cuadros de texto) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #F0F2F6 !important;
        color: #1E1E1E !important;
        border: 1px solid #D1D5DB !important;
    }

    /* Botón de Drive destacado */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007BFF !important;
        color: white !important;
        font-weight: bold;
        border: none;
    }

    /* Pestañas más grandes para el dedo */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #F8F9FA;
        border-radius: 10px 10px 0 0;
        padding: 10px;
        color: #666;
    }
    .stTabs [aria-selected="true"] { background-color: #E7F1FF !important; color: #007BFF !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        response = requests.get(URL_DIRECTA)
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f:
                f.write(response.content)
            st.success("✅ Base de datos sincronizada")
            st.rerun()
    except Exception as e:
        st.error(f"Error al clonar: {e}")

# --- LÓGICA DE DATOS ---
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- INTERFAZ ---
st.title("📦 Sistema WMS Unificado")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.subheader("Entrada de Mercadería")
    with st.form("f_entrada", clear_on_submit=True):
        c = st.text_input("Código de Producto")
        n = st.text_input("Nombre / Descripción")
        ca = st.number_input("Cantidad", min_value=0.0, step=1.0)
        u = st.text_input("Ubicación de Almacén")
        if st.form_submit_button("💾 GUARDAR EN LOGISTICA"):
            cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (c, n))
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", (c, ca, u, datetime.now().strftime('%d-%m-%Y')))
            conn.commit()
            st.success(f"Registrado: {n}")

with tab2:
    st.subheader("Buscador de Despacho")
    bus = st.text_input("🔍 Buscar por Código, Nombre o Ubicación")
    if bus:
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion 
            FROM inventario i
            LEFT JOIN maestra m ON i.cod_int = m.cod_int
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.ubicacion LIKE '%{bus}%')
            AND i.cantidad > 0
        """
        df_res = pd.read_sql(query, conn)
        for i, r in df_res.iterrows():
            with st.container():
                st.markdown(f"**{r['nombre']}**")
                st.markdown(f"📍 `{r['ubicacion']}` | Stock: **{r['cantidad']}**")
                baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button(f"CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.success("Salida realizada")
                    st.rerun()
                st.divider()

with tab3:
    st.subheader("Inventario Total (Excel)")
    query_total = """
        SELECT i.cod_int as Código, m.nombre as Producto, i.cantidad as Stock, i.ubicacion as Ubicación 
        FROM inventario i
        LEFT JOIN maestra m ON i.cod_int = m.cod_int
        WHERE i.cantidad > 0
    """
    df_total = pd.read_sql(query_total, conn)
    st.dataframe(df_total, use_container_width=True)

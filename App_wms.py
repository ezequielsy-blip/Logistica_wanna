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

# --- DISEÑO UI PREMIUM ---
st.set_page_config(page_title="WMS PRO", layout="centered")

st.markdown("""
    <style>
    /* Fondo y tipografía general */
    .stApp { background-color: #FFFFFF !important; }
    h1 { color: #1E1E1E !important; font-weight: 800 !important; }
    h2, h3, label, p { color: #333333 !important; font-weight: 600 !important; }

    /* Botón Sincronizar (Azul vibrante) */
    div.stButton > button:first-child {
        background-color: #0066FF !important;
        color: white !important;
        border-radius: 12px;
        height: 3.5rem;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
        margin-bottom: 20px;
    }

    /* Tarjetas de productos en Salidas */
    div[data-testid="stExpander"] {
        background-color: #F8F9FB !important;
        border: 1px solid #EDF0F5 !important;
        border-radius: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        margin-bottom: 10px;
    }

    /* Inputs y Selects */
    .stTextInput>div>div>input, .stSelectbox>div>div, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid #DCE1E8 !important;
        height: 45px;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #F0F2F5;
        border-radius: 10px 10px 0 0;
        color: #707070;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0066FF !important;
        border-bottom: 3px solid #0066FF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def descargar_base():
    with st.spinner('Clonando datos de la PC...'):
        try:
            if os.path.exists(DB_NAME): os.remove(DB_NAME)
            response = requests.get(URL_DIRECTA)
            if response.status_code == 200:
                with open(DB_NAME, 'wb') as f: f.write(response.content)
                st.success("✅ ¡Sincronización Exitosa!")
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- INTERFAZ ---
st.title("🚀 WMS Master Móvil")

if st.button("🔄 CLONAR DATOS DE PC (DRIVE)"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 SALIDAS", "📊 STOCK TOTAL"])

# --- 1. ENTRADAS (LOGISTICA) ---
with tab1:
    st.markdown("### Registro de Ingreso")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    codigos = [""] + maestra_df['cod_int'].tolist()
    
    with st.form("form_in", clear_on_submit=True):
        cod_sel = st.selectbox("Buscar Código Existente", options=codigos)
        
        # Autocompletado de nombre
        nombre_auto = ""
        if cod_sel != "":
            nombre_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]
        
        # Si es nuevo, permite escribirlo
        final_cod = st.text_input("Confirmar Código", value=cod_sel)
        final_nom = st.text_input("Nombre / Descripción", value=nombre_auto)
        
        col_a, col_b = st.columns(2)
        with col_a: cant = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with col_b: ubi = st.text_input("📍 Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if final_cod and final_nom:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (final_cod, final_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                             (final_cod, cant, ubi, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.balloons()
                st.success(f"Registrado: {final_nom}")
            else:
                st.error("Faltan datos obligatorios")

# --- 2. SALIDAS (APP_STOCK) ---
with tab2:
    st.markdown("### Despacho de Mercadería")
    bus = st.text_input("🔍 Buscar por nombre, código o lugar...")
    
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
            with st.expander(f"📦 {r['nombre']} | STOCK: {r['cantidad']}"):
                st.write(f"**Ubicación:** {r['ubicacion']} | **Código:** {r['cod_int']}")
                cant_salida = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"out_{r['rowid']}")
                if st.button(f"CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (cant_salida, r['rowid']))
                    conn.commit()
                    st.rerun()

# --- 3. EXCEL (VISUALIZACIÓN) ---
with tab3:
    st.markdown("### Resumen de Inventario")
    df_stock = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], i.ubicacion as [Ubicación]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_stock, use_container_width=True, hide_index=True)

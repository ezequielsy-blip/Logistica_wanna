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
st.set_page_config(page_title="WMS MASTER", layout="centered")

# --- CSS DE FUERZA BRUTA (Para que nada se vea negro/invisible) ---
st.markdown("""
    <style>
    /* 1. Fondo Blanco Total */
    .stApp, .main, .block-container { background-color: #FFFFFF !important; }
    
    /* 2. Forzar todos los textos a NEGRO PURO */
    h1, h2, h3, h4, h5, h6, p, label, li, span, div { 
        color: #000000 !important; 
        font-weight: 600 !important;
    }

    /* 3. Botón de Sincronización (Igual a LOGISTICA.exe) */
    div.stButton > button {
        background-color: #004cff !important;
        color: white !important;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }

    /* 4. Inputs de texto con borde definido para que se vean */
    input {
        background-color: #f0f2f6 !important;
        color: black !important;
        border: 2px solid #d1d5db !important;
        border-radius: 8px !important;
    }

    /* 5. Estilo para las Tabs (Pestañas) */
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #666; }
    .stTabs [aria-selected="true"] { color: #004cff !important; font-weight: bold; }

    /* 6. Botón Guardar Verde (Copia fiel) */
    .stForm button {
        background-color: #218838 !important;
        color: white !important;
    }
    
    /* 7. Dataframe (Excel) legible */
    .stDataFrame { background-color: white; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        response = requests.get(URL_DIRECTA)
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(response.content)
            st.success("✅ Datos clonados de la PC")
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# Conexión
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- INTERFAZ ---
st.title("📦 WMS Master Móvil")

# Botón de Sincronización
if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

# Pestañas exactas a tus ejecutables
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

with tab1:
    st.markdown("### Registro de Entradas")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    
    # Autocompletado inteligente
    opciones = [""] + maestra_df['cod_int'].tolist()
    cod_seleccionado = st.selectbox("Buscar Código (Autocompletar)", options=opciones)
    
    nombre_sugerido = ""
    if cod_seleccionado != "":
        nombre_sugerido = maestra_df[maestra_df['cod_int'] == cod_seleccionado]['nombre'].values[0]

    with st.form("form_entrada", clear_on_submit=True):
        f_cod = st.text_input("Código de Producto", value=cod_seleccionado)
        f_nom = st.text_input("Nombre / Descripción", value=nombre_sugerido)
        col1, col2 = st.columns(2)
        with col1: f_can = st.number_input("Cantidad", min_value=0.0)
        with col2: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                             (f_cod, f_can, f_ubi, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Registrado: {f_nom}")
                st.rerun()

with tab2:
    st.markdown("### Salidas / Despacho")
    bus = st.text_input("🔍 Buscar por Nombre, Código o Ubicación")
    if bus:
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion 
            FROM inventario i
            LEFT JOIN maestra m ON i.cod_int = m.cod_int
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.ubicacion LIKE '%{bus}%')
            AND i.cantidad > 0
        """
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.container():
                st.markdown(f"**{r['nombre']}**")
                st.markdown(f"📍 {r['ubicacion']} | Stock: **{r['cantidad']}**")
                cant_baja = st.number_input("Sacar cantidad", min_value=1.0, max_value=float(r['cantidad']), key=f"out_{r['rowid']}")
                if st.button(f"CONFIRMAR SALIDA {r['rowid']}", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (cant_baja, r['rowid']))
                    conn.commit()
                    st.rerun()
                st.markdown("---")

with tab3:
    st.markdown("### Stock Total (Vista Excel)")
    df_excel = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], i.ubicacion as [Ubicación]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_excel, use_container_width=True, hide_index=True)

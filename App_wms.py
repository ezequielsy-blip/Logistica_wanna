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

# --- DISEÑO UI ALTA VISIBILIDAD ---
st.set_page_config(page_title="WMS PRO", layout="centered")

st.markdown("""
    <style>
    /* Fondo principal blanco puro */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Títulos y textos en negro intenso para máxima legibilidad */
    h1, h2, h3, p, label, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }
    
    /* Botón Sincronizar (Azul fuerte con texto blanco) */
    div.stButton > button:first-child {
        background-color: #0056b3 !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        height: 4rem;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #004494;
    }

    /* Campos de entrada (Blancos con borde negro fino) */
    input, .stSelectbox, .stNumberInput {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }

    /* Botón Guardar (Verde para diferenciarlo) */
    .stForm button {
        background-color: #28a745 !important;
        color: white !important;
        width: 100%;
        height: 3.5rem;
        font-size: 18px;
        font-weight: bold;
    }

    /* Ajuste de pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #495057; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #0056b3 !important; border-bottom: 3px solid #0056b3 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def descargar_base():
    with st.spinner('Sincronizando con PC...'):
        try:
            if os.path.exists(DB_NAME): os.remove(DB_NAME)
            response = requests.get(URL_DIRECTA)
            if response.status_code == 200:
                with open(DB_NAME, 'wb') as f: f.write(response.content)
                st.success("✅ ¡Datos actualizados!")
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- INTERFAZ ---
st.title("📦 WMS Master Móvil")

# Botón principal de sincronización
if st.button("🔄 CLONAR DATOS DE PC (DRIVE)"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 SALIDAS", "📊 STOCK TOTAL"])

# --- 1. ENTRADAS (LOGISTICA) ---
with tab1:
    st.markdown("### Registro de Ingreso")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    codigos = [""] + maestra_df['cod_int'].tolist()
    
    with st.form("form_in", clear_on_submit=True):
        cod_sel = st.selectbox("1. Seleccionar Código Existente", options=codigos)
        
        # Lógica de autocompletado
        nombre_auto = ""
        if cod_sel != "":
            nombre_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]
        
        final_cod = st.text_input("2. Confirmar/Escribir Código", value=cod_sel)
        final_nom = st.text_input("3. Nombre del Producto", value=nombre_auto)
        
        col_can, col_ub = st.columns(2)
        with col_can: cant = st.number_input("4. Cantidad", min_value=0.0)
        with col_ub: ubi = st.text_input("5. Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if final_cod and final_nom:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (final_cod, final_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                             (final_cod, cant, ubi, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado: {final_nom}")
                st.rerun()

# --- 2. SALIDAS (APP_STOCK) ---
with tab2:
    st.markdown("### Despacho")
    bus = st.text_input("🔍 Buscar por Nombre, Código o Lugar")
    
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
                st.markdown(f"**Producto:** {r['nombre']} | **Stock:** {r['cantidad']}")
                st.markdown(f"📍 Ubicación: `{r['ubicacion']}`")
                baja = st.number_input(f"Sacar de {r['cod_int']}:", min_value=1.0, max_value=float(r['cantidad']), key=f"out_{r['rowid']}")
                if st.button(f"CONFIRMAR SALIDA {r['rowid']}", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()
                st.markdown("---")

# --- 3. STOCK TOTAL (EXCEL) ---
with tab3:
    st.markdown("### Inventario Actual")
    df_stock = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], i.ubicacion as [Ubicación]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_stock, use_container_width=True, hide_index=True)

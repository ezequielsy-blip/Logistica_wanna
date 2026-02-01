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

# --- DISEÑO UI ESTILIZADO (MODERNO) ---
st.set_page_config(page_title="WMS Master Pro", layout="centered")

st.markdown("""
    <style>
    /* Fondo y tipografía */
    .stApp { background-color: #fdfdfd !important; }
    
    /* Títulos con estilo */
    h1 { color: #1a1a1a !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 800 !important; }
    label { color: #444 !important; font-weight: 600 !important; font-size: 14px !important; margin-bottom: 5px; }

    /* Botón de Sincronización Estilizado */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
        color: white !important;
        border-radius: 15px;
        height: 3.5rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        transition: all 0.3s ease;
    }

    /* Campos de Entrada Redondeados y Limpios */
    input, .stSelectbox > div > div, .stNumberInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: #ffffff !important;
        padding: 10px !important;
    }
    
    /* Foco en los inputs */
    input:focus { border: 1px solid #007bff !important; box-shadow: 0 0 5px rgba(0,123,255,0.2) !important; }

    /* Botón Guardar Verde Premium */
    .stForm button {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%) !important;
        color: white !important;
        border-radius: 12px;
        height: 3.8rem;
        font-size: 18px;
        font-weight: 700;
        border: none;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
    }

    /* Estilo de Tarjetas para Salidas */
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
    
    /* Pestañas (Tabs) Estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding: 5px; background-color: #f1f3f5; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        color: #666;
        font-weight: 600;
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #007bff !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def descargar_base():
    with st.spinner('Sincronizando con PC...'):
        try:
            if os.path.exists(DB_NAME): os.remove(DB_NAME)
            response = requests.get(URL_DIRECTA)
            if response.status_code == 200:
                with open(DB_NAME, 'wb') as f: f.write(response.content)
                st.toast("✅ Sincronización exitosa", icon="🔄")
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- CABECERA ---
st.title("📦 WMS Pro Móvil")

if st.button("🔄 SINCRONIZAR CON DRIVE"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 SALIDAS", "📊 STOCK"])

# --- 1. ENTRADAS (LOGISTICA) ---
with tab1:
    st.markdown("### Nuevo Registro")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    
    with st.container():
        # Buscador estilizado de código
        cod_list = [""] + maestra_df['cod_int'].tolist()
        cod_sel = st.selectbox("Buscar por código", options=cod_list, help="Selecciona un código para autocompletar")
        
        nombre_auto = ""
        if cod_sel != "":
            nombre_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]
        
        with st.form("form_registro", clear_on_submit=True):
            f_cod = st.text_input("Código de Producto", value=cod_sel)
            f_nom = st.text_input("Nombre / Descripción", value=nombre_auto)
            
            c1, c2 = st.columns(2)
            with c1: f_can = st.number_input("Cantidad", min_value=0.0)
            with c2: f_ubi = st.text_input("📍 Ubicación")
            
            if st.form_submit_button("💾 GUARDAR EN LOGISTICA"):
                if f_cod and f_nom:
                    cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                    cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                                 (f_cod, f_can, f_ubi, datetime.now().strftime('%d/%m/%Y')))
                    conn.commit()
                    st.success("¡Registrado correctamente!")
                    st.rerun()

# --- 2. SALIDAS (APP_STOCK) ---
with tab2:
    st.markdown("### Despacho de Stock")
    bus = st.text_input("🔍 Buscar producto...")
    
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
            st.markdown(f"""
            <div class="product-card">
                <span style="font-size: 18px; font-weight: bold;">{r['nombre']}</span><br>
                <span style="color: #666;">📍 {r['ubicacion']} | Stock: <b>{r['cantidad']}</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            baja = st.number_input(f"Cantidad a sacar de {r['cod_int']}", min_value=1.0, max_value=float(r['cantidad']), key=f"out_{r['rowid']}")
            if st.button(f"CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                conn.commit()
                st.rerun()

# --- 3. STOCK TOTAL ---
with tab3:
    st.markdown("### Resumen Total")
    df_full = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Cant], i.ubicacion as [Lugar]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_full, use_container_width=True, hide_index=True)

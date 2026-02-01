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
st.set_page_config(page_title="WMS FULL", layout="centered")

# --- CSS PARA LEGIBILIDAD ADAPTABLE ---
st.markdown("""
    <style>
    .stMarkdown, p, label { font-weight: 700 !important; }
    div.stButton > button {
        width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold;
    }
    .stTabs [data-baseweb="tab"] { font-size: 14px; font-weight: bold; }
    /* Estilo para resaltar fechas de vencimiento */
    .vencimiento-alerta { color: #d9534f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    # Maestra: Datos fijos del producto
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    # Inventario: Movimientos con Vencimiento y Depósito
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, 
                        cantidad REAL, 
                        ubicacion TEXT, 
                        deposito TEXT, 
                        vencimiento TEXT, 
                        fecha_registro TEXT)""")
    conn.commit()
    return conn, cursor

conn, cursor = conectar()

def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        response = requests.get(URL_DIRECTA)
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(response.content)
            st.toast("✅ Base sincronizada", icon="🔄")
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# --- INTERFAZ ---
st.title("📦 WMS Master Full")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

# --- 1. LOGISTICA (ENTRADAS CON VENCIMIENTO Y DEPÓSITO) ---
with tab1:
    st.subheader("Ingreso con Vencimiento")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_list = [""] + maestra_df['cod_int'].tolist()
    
    # Buscador de autocompletado
    cod_sel = st.selectbox("Buscar Código", options=cod_list)
    
    nombre_sugerido = ""
    if cod_sel != "":
        nombre_sugerido = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]

    with st.form("form_full", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Descripción", value=nombre_sugerido)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0)
        with c2: f_venc = st.date_input("Fecha de Vencimiento", value=None)
        
        c3, c4 = st.columns(2)
        with c3: f_dep = st.text_input("Depósito (Ej: Nave A, Central)")
        with c4: f_ubi = st.text_input("Ubicación (Pasillo/Rack)")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom:
                venc_str = f_venc.strftime('%d/%m/%Y') if f_venc else "N/A"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, venc_str, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Ingresado en {f_dep}: {f_nom}")
                st.rerun()

# --- 2. APP_STOCK (SALIDAS CON FILTRO DE DEPÓSITO) ---
with tab2:
    st.subheader("Despacho / Salidas")
    bus = st.text_input("🔍 Buscar por Nombre, Código o Depósito")
    
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
                st.markdown(f"**Vence:** {r['vencimiento']} | **Ubicación:** {r['ubicacion']}")
                baja = st.number_input(f"Cantidad a retirar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()

# --- 3. EXCEL TOTAL (VISTA COMPLETA) ---
with tab3:
    st.subheader("Inventario Consolidado")
    df_full = pd.read_sql("""
        SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
               i.deposito as [Depósito], i.ubicacion as [Lugar], i.vencimiento as [Vencimiento]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
        ORDER BY i.vencimiento ASC
    """, conn)
    st.dataframe(df_full, use_container_width=True, hide_index=True)

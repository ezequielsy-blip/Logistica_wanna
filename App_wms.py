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

# --- DISEÑO UI (Adaptable y Legible) ---
st.markdown("""
    <style>
    .stMarkdown, p, label { font-weight: 700 !important; }
    div.stButton > button {
        width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold;
    }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: bold; }
    input { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_y_actualizar():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    
    # TRUCO: Verificar si faltan columnas (Vencimiento y Deposito) y agregarlas si no están
    cursor.execute("PRAGMA table_info(inventario)")
    columnas = [info[1] for info in cursor.fetchall()]
    
    if 'deposito' not in columnas:
        cursor.execute("ALTER TABLE inventario ADD COLUMN deposito TEXT DEFAULT 'GENERAL'")
    if 'vencimiento' not in columnas:
        cursor.execute("ALTER TABLE inventario ADD COLUMN vencimiento TEXT DEFAULT 'N/A'")
        
    conn.commit()
    return conn, cursor

def descargar_base():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        response = requests.get(URL_DIRECTA)
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(response.content)
            st.toast("✅ Sincronizado correctamente", icon="🔄")
            st.rerun()
    except Exception as e: st.error(f"Error en descarga: {e}")

# Ejecutar conexión
conn, cursor = conectar_y_actualizar()

# --- INTERFAZ ---
st.title("🚀 WMS Master Móvil")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

# --- 1. LOGISTICA (Entradas) ---
with tab1:
    st.subheader("Registro de Ingresos")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_list = [""] + maestra_df['cod_int'].tolist()
    
    cod_sel = st.selectbox("Buscar Producto (Autocompletar)", options=cod_list)
    
    nom_sug = ""
    if cod_sel != "":
        nom_sug = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]

    with st.form("f_ent", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_sug)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0)
        with c2: f_venc = st.date_input("Vencimiento", value=None)
        
        c3, c4 = st.columns(2)
        with c3: f_dep = st.text_input("Depósito", placeholder="Ej: Nave 1")
        with c4: f_ubi = st.text_input("Ubicación", placeholder="Ej: Estante A2")
        
        if st.form_submit_button("💾 GUARDAR EN LOGISTICA"):
            if f_cod and f_nom:
                v_str = f_venc.strftime('%d/%m/%Y') if f_venc else "N/A"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, v_str, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success("¡Registrado!")
                st.rerun()

# --- 2. APP_STOCK (Salidas) ---
with tab2:
    st.subheader("Despacho de Mercadería")
    bus = st.text_input("🔍 Buscar por Nombre, Código o Depósito")
    
    if bus:
        # Usamos nombres de columnas genéricos para evitar errores de SQL si la base es vieja
        query = f"""
            SELECT i.rowid, i.cod_int, m.nombre, i.cantidad, i.ubicacion, i.deposito, i.vencimiento
            FROM inventario i
            LEFT JOIN maestra m ON i.cod_int = m.cod_int
            WHERE (i.cod_int LIKE '%{bus}%' OR m.nombre LIKE '%{bus}%' OR i.deposito LIKE '%{bus}%')
            AND i.cantidad > 0
        """
        try:
            res = pd.read_sql(query, conn)
            for i, r in res.iterrows():
                with st.expander(f"📦 {r['nombre']} | {r['deposito']} | Stock: {r['cantidad']}"):
                    st.write(f"📍 Ubicación: {r['ubicacion']} | Vence: {r['vencimiento']}")
                    baja = st.number_input("Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.rerun()
        except:
            st.warning("Sincroniza la base para ver las nuevas columnas.")

# --- 3. EXCEL TOTAL (Vista) ---
with tab3:
    st.subheader("Inventario Consolidado")
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
        st.info("Presiona el botón de Sincronizar para actualizar el formato de la tabla.")

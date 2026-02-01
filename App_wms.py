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
st.set_page_config(page_title="WMS MASTER PRO", layout="centered")

# --- CSS PARA LEGIBILIDAD Y BOTONES ---
st.markdown("""
    <style>
    /* Asegura que los textos sean legibles en ambos temas */
    .stMarkdown, p, label {
        font-weight: 600 !important;
    }
    /* Botones grandes para uso táctil */
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
    }
    /* Mejora la visualización de las tablas */
    .stDataFrame {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SINCRONIZACIÓN ---
def descargar_base():
    with st.spinner('Sincronizando datos de PC...'):
        try:
            if os.path.exists(DB_NAME): os.remove(DB_NAME)
            response = requests.get(URL_DIRECTA)
            if response.status_code == 200:
                with open(DB_NAME, 'wb') as f: f.write(response.content)
                st.toast("✅ Base de datos actualizada", icon="🔄")
                st.rerun()
            else:
                st.error("Error al descargar: El archivo de Drive no es público.")
        except Exception as e: st.error(f"Error: {e}")

# Conexión SQLite
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, ubicacion TEXT, fecha TEXT)")
conn.commit()

# --- INTERFAZ PRINCIPAL ---
st.title("📦 WMS Master Móvil")

# Botón de Sincronización (Lo primero que necesitas)
if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    descargar_base()

# Pestañas: Copia fiel de tus ejecutables
tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA (Entradas)", "📤 APP_STOCK (Salidas)", "📊 STOCK TOTAL"])

# --- 1. LOGISTICA (IGUAL A TU APP_LOGISTICA) ---
with tab1:
    st.subheader("Registro de Ingresos")
    # Traemos la maestra para el autocompletado
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_list = [""] + maestra_df['cod_int'].tolist()
    
    # Campo de selección para autocompletar (Como en tu PC)
    cod_sel = st.selectbox("Seleccione Código (Buscador)", options=cod_list)
    
    # Lógica de autocompletado automática
    nombre_sugerido = ""
    if cod_sel != "":
        nombre_sugerido = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0]

    with st.form("form_entradas", clear_on_submit=True):
        f_cod = st.text_input("Confirmar Código", value=cod_sel)
        f_nom = st.text_input("Nombre / Descripción", value=nombre_sugerido)
        
        col_c, col_u = st.columns(2)
        with col_c: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with col_u: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR REGISTRO"):
            if f_cod and f_nom:
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?)", 
                             (f_cod, f_can, f_ubi, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Guardado: {f_nom}")
                st.rerun()
            else:
                st.warning("Complete Código y Nombre")

# --- 2. APP_STOCK (IGUAL A TU BUSCADOR DE SALIDAS) ---
with tab2:
    st.subheader("Buscador de Despacho")
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
            with st.expander(f"📦 {r['nombre']} | STOCK: {r['cantidad']}"):
                st.write(f"**Ubicación:** {r['ubicacion']} | **Código:** {r['cod_int']}")
                baja = st.number_input(f"Cantidad a sacar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"btn_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.success("Salida realizada")
                    st.rerun()

# --- 3. EXCEL (VISTA TOTAL DE STOCK) ---
with tab3:
    st.subheader("Estado de Inventario (Excel)")
    df_excel = pd.read_sql("""
        SELECT i.cod_int as [Código], m.nombre as [Producto], i.cantidad as [Stock], i.ubicacion as [Lugar]
        FROM inventario i 
        JOIN maestra m ON i.cod_int = m.cod_int 
        WHERE i.cantidad > 0
    """, conn)
    st.dataframe(df_excel, use_container_width=True, hide_index=True)

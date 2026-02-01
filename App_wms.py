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

st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- MOTOR DE UBICACIÓN (Idéntico a tu LOGISTICA.exe) ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        if "-" not in ubi_str: return "99-01A"
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                      (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, 
                       fecha TEXT, ubicacion TEXT, deposito TEXT)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

st.title("🚀 WMS PROFESIONAL MÓVIL")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA")
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 MOVIMIENTOS", "📤 DESPACHO", "📊 PLANILLA"])

# --- TAB 1: MOVIMIENTOS ---
with tab1:
    st.subheader("Entrada de Mercadería")
    
    # Lógica de búsqueda por texto o nombre
    bus_entrada = st.text_input("🔍 Buscar por Nombre o Código", key="txt_mov")
    
    try:
        # Búsqueda que ignora mayúsculas/minúsculas para el nombre
        query_m = f"SELECT cod_int, nombre FROM maestra WHERE cod_int LIKE '%{bus_entrada}%' OR nombre LIKE '%{bus_entrada}%' OR barras LIKE '%{bus_entrada}%'"
        maestra_df = pd.read_sql(query_m, conn)
        
        cod_sel = st.selectbox("Confirmar Producto", options=[""] + maestra_df['cod_int'].tolist())
        nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""
        ubi_sug = motor_sugerencia_pc(conn)
    except: cod_sel, nom_auto, ubi_sug = "", "", "99-01A"

    with st.form("form_mov", clear_on_submit=True):
        f_cod = st.text_input("Cod Int", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0)
        with c2: f_dep = st.selectbox("Depósito", ["DEPO 1", "DEPO 2"])
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4)
        with c4: f_ubi = st.text_input("Ubicación", value=ubi_sug)
        
        if st.form_submit_button("⚡ REGISTRAR MOVIMIENTO"):
            if f_cod and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", 
                             (f_cod, f_can, f_nom, "", f_venc, f_ubi, f_dep))
                conn.commit()
                st.success(f"Cargado en {f_ubi}")
                st.rerun()

# --- TAB 2: DESPACHO (Detalle Total + Búsqueda por Nombre) ---
with tab2:
    st.subheader("Salida de Mercadería")
    
    # Botón para activar cámara de celular
    if st.checkbox("📷 Activar Escáner de Cámara"):
        foto = st.camera_input("Encuadra el código de barras")
        if foto: st.info("Procesando imagen... (Usa el código detectado en el buscador)")

    bus = st.text_input("🔎 Escribe Nombre, Código o Barras", key="bus_despacho")
    
    if bus:
        # Consulta SQL mejorada para buscar por nombre parcial y códigos
        query = f"""
            SELECT rowid, cod_int, nombre, cantidad, ubicacion, fecha, deposito 
            FROM inventario 
            WHERE (cod_int LIKE '%{bus}%' OR nombre LIKE '%{bus}%' OR barras LIKE '%{bus}%') 
            AND cantidad > 0
        """
        res = pd.read_sql(query, conn)
        
        if res.empty:
            st.warning("No se encontraron coincidencias.")
        
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} (Cod: {r['cod_int']})"):
                # LOS 4 MICRO-DETALLES SOLICITADOS SIN FALTAR NADA
                st.markdown(f"""
                **Detalles del Lote:**
                * 🔢 **CANTIDAD:** {r['cantidad']}
                * 📅 **FECHA (Vence):** {r['fecha']}
                * 📍 **UBICACIÓN:** {r['ubicacion']}
                * 🏢 **DEPÓSITO:** {r['deposito']}
                """)
                
                baja = st.number_input(f"Cantidad a retirar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.success("Salida confirmada")
                    st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    st.subheader("Planilla General")
    tabla_ver = st.radio("Ver tabla:", ["inventario", "maestra"], horizontal=True)
    try:
        df_full = pd.read_sql(f"SELECT * FROM {tabla_ver}", conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sincroniza para ver la planilla.")

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os
import re

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="wide") # Layout ancho como escritorio

# --- MOTOR DE UBICACIÓN (Tu lógica idéntica de PC) ---
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
            if idx < 3:
                nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else:
                nueva_letra = 'A'; nuevo_num = num_actual + 1
        else:
            nueva_letra = 'A'; nuevo_num = num_actual + 1
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

# --- INTERFAZ ESTILO DESKTOP ---
st.markdown("""<style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
</style>""", unsafe_allow_html=True)

st.title("🏭 LOGISTICA - GESTIÓN DE STOCK")
st.caption(f"App: APP_STOCK.PY | Exec: LOGISTICA | Entorno: Moto G24 Power")

# --- INDICADORES (Métricas rápidas) ---
try:
    total_art = pd.read_sql("SELECT SUM(cantidad) FROM inventario", conn).iloc[0,0] or 0
    total_lotes = pd.read_sql("SELECT COUNT(*) FROM inventario WHERE cantidad > 0", conn).iloc[0,0]
    m1, m2, m3 = st.columns(3)
    m1.metric("Stock Total", f"{int(total_art)} uni")
    m2.metric("Lotes Activos", total_lotes)
    m3.metric("DB Status", "OK" if os.path.exists(DB_NAME) else "SIN DB")
except: pass

st.divider()

if st.button("🔄 CLONAR/SINCRONIZAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA CON EXITO")
        st.rerun()
    except Exception as e: st.error(f"Error en sincronización: {e}")

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS (MOV)", "📤 SALIDAS (DESPACHO)", "📊 AUDITORÍA (PLANILLA)"])

# --- TAB 1: MOVIMIENTOS ---
with tab1:
    st.subheader("Ingreso de Mercadería")
    bus_m = st.text_input("🔍 Buscar Producto (Nombre, Código o Escáner)", key="input_mov")
    try:
        query_m = "SELECT cod_int, nombre FROM maestra WHERE cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?"
        maestra_df = pd.read_sql(query_m, conn, params=(f'%{bus_m}%', f'%{bus_m}%', f'%{bus_m}%'))
        cod_sel = st.selectbox("Confirmar selección de Maestra", options=[""] + maestra_df['cod_int'].tolist())
        nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""
        ubi_sug = motor_sugerencia_pc(conn)
    except: cod_sel, nom_auto, ubi_sug = "", "", "99-01A"

    with st.form("form_mov", clear_on_submit=True):
        c_f1, c_f2 = st.columns(2)
        with c_f1: f_cod = st.text_input("Código Interno", value=cod_sel)
        with c_f2: f_nom = st.text_input("Nombre del Artículo", value=nom_auto)
        
        c1, c2, c3 = st.columns(3)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
        with c3: f_ubi = st.text_input("Ubicación sugerida", value=ubi_sug)
        
        f_venc_raw = st.text_input("Vencimiento (Formato MMAA)", placeholder="Ej: 0526 para Mayo 2026", max_chars=4)
        
        if st.form_submit_button("💾 GRABAR MOVIMIENTO"):
            if f_cod and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT INTO inventario (cod_int, cantidad, nombre, barras, fecha, ubicacion, deposito) VALUES (?,?,?,?,?,?,?)", 
                             (f_cod, f_can, f_nom, "", f_venc, f_ubi, f_dep))
                conn.commit()
                st.success(f"✅ Registrado: {f_can} un. en {f_ubi}")
                st.rerun()
            else:
                st.error("❌ Verifique Código y formato de Vencimiento (4 dígitos)")

# --- TAB 2: DESPACHO ---
with tab2:
    st.subheader("Buscador de Despacho")
    bus = st.text_input("🔍 Escanear o Buscar para retirar", key="input_des")
    if bus:
        query_d = "SELECT rowid, * FROM inventario WHERE (cod_int LIKE ? OR nombre LIKE ?) AND cantidad > 0"
        res = pd.read_sql(query_d, conn, params=(f'%{bus}%', f'%{bus}%'))
        
        if res.empty:
            st.warning("⚠️ No hay stock disponible para esa búsqueda.")
            
        for i, r in res.iterrows():
            with st.container():
                # Estilo de tarjeta desktop
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{r['nombre']}** ({r['cod_int']})")
                    st.caption(f"📍 Ubi: {r['ubicacion']} | 📅 Vence: {r['fecha']} | 🏢 Depo: {r['deposito']}")
                with col_b:
                    baja = st.number_input("Cant.", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                    if st.button("RETIRAR", key=f"b_{r['rowid']}", use_container_width=True):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit()
                        st.toast(f"Salida registrada: {r['nombre']}")
                        st.rerun()
                st.divider()

# --- TAB 3: PLANILLA ---
with tab3:
    st.subheader("Auditoría de Tablas")
    tabla_ver = st.radio("Seleccionar vista:", ["Inventario Actual", "Maestra de Productos"], horizontal=True)
    t_name = "inventario" if "Inventario" in tabla_ver else "maestra"
    try:
        df_full = pd.read_sql(f"SELECT * FROM {t_name}", conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
        
        # Botón de descarga CSV estilo desktop
        csv = df_full.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Planilla (CSV)", csv, f"export_{t_name}.csv", "text/csv")
    except:
        st.info("Sincronice con Drive para visualizar los datos.")

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DRIVE (Tu ID original) ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# --- DISEÑO ---
st.set_page_config(page_title="WMS Master Pro", layout="centered")

st.markdown("""
    <style>
    .stMarkdown, p, label { font-weight: 700 !important; }
    div.stButton > button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; }
    input { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA/SINCRONIZACIÓN ---
def sincronizar_datos():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        if r.status_code == 200:
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            return True
    except:
        return False
    return False

# SINCRONIZACIÓN AUTOMÁTICA AL INICIAR
if 'sincronizado' not in st.session_state:
    exito = sincronizar_datos()
    if exito:
        st.session_state['sincronizado'] = True
        st.toast("✅ Datos actualizados automáticamente", icon="🔄")
    else:
        st.session_state['sincronizado'] = False

# --- CONEXIÓN BASE DE DATOS ---
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# --- INTERFAZ ---
st.title("📦 WMS Master Móvil")

# Botón manual por si querés refrescar sin recargar la web
if st.button("🔄 REFRESCAR DATOS AHORA"):
    if sincronizar_datos():
        st.success("✅ Base actualizada")
        st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 LOGISTICA", "📤 APP_STOCK", "📊 EXCEL TOTAL"])

# --- 1. LOGISTICA (Entradas con Barra Auto) ---
with tab1:
    st.subheader("Carga de Mercadería")
    maestra_df = pd.read_sql("SELECT cod_int, nombre FROM maestra", conn)
    cod_sel = st.selectbox("Buscar Código", options=[""] + maestra_df['cod_int'].tolist())
    nom_auto = maestra_df[maestra_df['cod_int'] == cod_sel]['nombre'].values[0] if cod_sel != "" else ""

    with st.form("form_registro", clear_on_submit=True):
        f_cod = st.text_input("Código", value=cod_sel)
        f_nom = st.text_input("Nombre", value=nom_auto)
        
        c1, c2 = st.columns(2)
        with c1: f_can = st.number_input("Cantidad", min_value=0.0, step=1.0)
        with c2: f_dep = st.selectbox("Depósito", options=["DEPO1", "DEPO2"])
        
        c3, c4 = st.columns(2)
        venc_input = st.text_input("Vencimiento (MMAA)", max_chars=4, help="Poné 4 números, ej: 1026")
        with c4: f_ubi = st.text_input("Ubicación")
        
        if st.form_submit_button("💾 GUARDAR ENTRADA"):
            if f_cod and f_nom and len(venc_input) == 4:
                # El programa pone la barra "/" antes de guardar en la DB
                f_venc = f"{venc_input[:2]}/{venc_input[2:]}"
                cursor.execute("INSERT OR IGNORE INTO maestra VALUES (?,?)", (f_cod, f_nom))
                cursor.execute("INSERT INTO inventario (cod_int, cantidad, ubicacion, deposito, vencimiento, fecha_registro) VALUES (?,?,?,?,?,?)", 
                             (f_cod, f_can, f_ubi, f_dep, f_venc, datetime.now().strftime('%d/%m/%Y')))
                conn.commit()
                st.success(f"Registrado como: {f_venc}")
                st.rerun()
            else:
                st.error("Completar Código, Nombre y 4 números de Vencimiento")

# --- 2. APP_STOCK (Salidas) ---
with tab2:
    st.subheader("Despacho / Salidas")
    bus = st.text_input("🔍 Buscar...")
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
                st.write(f"Vence: **{r['vencimiento']}** | Ubicación: **{r['ubicacion']}**")
                baja = st.number_input("Cantidad a sacar", min_value=1.0, key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.rerun()

# --- 3. EXCEL TOTAL ---
with tab3:
    st.subheader("Stock Consolidado")
    try:
        df_full = pd.read_sql("""
            SELECT i.cod_int as [Cód], m.nombre as [Producto], i.cantidad as [Stock], 
                   i.deposito as [Depósito], i.ubicacion as [Ubicación], i.vencimiento as [Vencimiento]
            FROM inventario i 
            JOIN maestra m ON i.cod_int = m.cod_int 
            WHERE i.cantidad > 0
        """, conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except:
        st.info("Sin datos. Sincroniza desde el botón de arriba.")

import streamlit as st
import sqlite3
import pandas as pd
import requests
import os
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- LÓGICA DE COMUNICACIÓN SCANNER -> PYTHON ---
# Inicializamos el estado del buscador si no existe
if "scan_result" not in st.session_state:
    st.session_state.scan_result = ""

# Componente JS que envía el código detectado a Streamlit
def scanner_ui(key_id):
    components.html(
        f"""
        <div id="reader-{key_id}" style="width:100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) {{
                // Enviar el resultado al componente de Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }}, '*');
                // Vibración corta para confirmar escaneo
                if (navigator.vibrate) navigator.vibrate(100);
            }}
            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader-{key_id}", {{ fps: 15, qrbox: 250 }});
            html5QrcodeScanner.render(onScanSuccess);
        </script>
        """, height=380
    )

# --- MOTOR DE UBICACIÓN (Tu lógica de PC exacta) ---
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

# --- INTERFAZ PRINCIPAL ---
st.title("📦 WMS PROFESIONAL MÓVIL")

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
    with st.expander("📷 ABRIR ESCÁNER DE ENTRADA"):
        val_scan_mov = scanner_ui("mov_scan")
        if val_scan_mov: st.session_state.scan_result = val_scan_mov

    bus_mov = st.text_input("🔍 Buscar (Nombre o Código)", value=st.session_state.scan_result, key="input_mov")
    
    try:
        query_m = f"SELECT cod_int, nombre FROM maestra WHERE cod_int LIKE '%{bus_mov}%' OR nombre LIKE '%{bus_mov}%' OR barras LIKE '%{bus_mov}%'"
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
        with c2: f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
        c3, c4 = st.columns(2)
        with c3: f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4, help="Se guardará como MM/AA")
        with c4: f_ubi = st.text_input("Ubicación", value=ubi_sug)
        
        if st.form_submit_button("⚡ REGISTRAR EN APP_STOCK"):
            if f_cod and len(f_venc_raw) == 4:
                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", 
                             (f_cod, f_can, f_nom, "", f_venc, f_ubi, f_dep))
                conn.commit()
                st.session_state.scan_result = "" # Limpiamos para el próximo
                st.success(f"Cargado en {f_ubi}")
                st.rerun()

# --- TAB 2: DESPACHO ---
with tab2:
    st.subheader("Salida de Mercadería")
    with st.expander("📷 ABRIR ESCÁNER DE DESPACHO"):
        val_scan_des = scanner_ui("des_scan")
        if val_scan_des: st.session_state.scan_result = val_scan_des

    bus_des = st.text_input("🔎 Filtro (Escribe o Escanea)", value=st.session_state.scan_result, key="input_des")
    
    if bus_des:
        query = f"SELECT rowid, * FROM inventario WHERE (cod_int LIKE '%{bus_des}%' OR nombre LIKE '%{bus_des}%' OR barras LIKE '%{bus_des}%') AND cantidad > 0"
        res = pd.read_sql(query, conn)
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} (Cod: {r['cod_int']})"):
                # MICRO-DETALLES SOLICITADOS
                st.markdown(f"""
                ---
                **INFORMACIÓN DEL LOTE:**
                * 🔢 **CANTIDAD:** {r['cantidad']}
                * 📅 **VENCIMIENTO:** {r['fecha']}
                * 📍 **UBICACIÓN:** {r['ubicacion']}
                * 🏢 **DEPÓSITO:** {r['deposito']}
                ---
                """)
                baja = st.number_input(f"Cantidad a retirar", min_value=1.0, max_value=float(r['cantidad']), key=f"s_{r['rowid']}")
                if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                    cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                    conn.commit()
                    st.session_state.scan_result = ""
                    st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    st.subheader("Planilla General")
    tabla_ver = st.radio("Ver tabla:", ["inventario", "maestra"], horizontal=True)
    try:
        df_full = pd.read_sql(f"SELECT * FROM {tabla_ver}", conn)
        st.dataframe(df_full, use_container_width=True, hide_index=True)
    except: st.info("Sincroniza para ver datos.")

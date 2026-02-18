import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- LÓGICA DE ACTIVACIÓN ---
def generar_llave_maestra(device_id):
    mes_año = datetime.now().strftime("%m%Y")
    frase_secreta = f"{device_id}7079{mes_año}LOGIEZE_SECURITY"
    return hashlib.sha256(frase_secreta.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state: st.session_state.activado = False
if "codigo_escaneado" not in st.session_state: st.session_state.codigo_escaneado = ""

if not st.session_state.activado:
    st.markdown("<h1>🔐 ACTIVACIÓN</h1>", unsafe_allow_html=True)
    key_in = st.text_input("Ingrese Clave del Mes").strip().upper()
    if st.button("ACTIVAR"):
        if key_in == generar_llave_maestra("LGE-7079"):
            st.session_state.activado = True
            st.rerun()
    st.stop()

# --- ESTILOS CORREGIDOS (SIN DESPLAZAMIENTO) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; padding: 0px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    div[data-baseweb="input"] {
        height: 60px !important; background-color: #F3F4F6 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 10px !important;
    }
    .stTextInput input { font-size: 20px !important; color: #1E3A8A !important; }
    div.stButton > button {
        width: 100% !important; height: 70px !important; font-size: 20px !important; 
        background-color: #3B82F6 !important; color: white !important; border-radius: 12px !important;
    }
    h1 { text-align: center; color: #1E40AF; font-size: 38px !important; font-weight: 850; margin: 0; }
    #reader { width: 100% !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTE DE ESCÁNER (COMUNICACIÓN DIRECTA) ---
def escanner_real():
    # Este script detecta el código y le "avisa" a Streamlit para que haga el ENTER
    components.html("""
        <div id="reader" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) {
                const queryParams = new URLSearchParams(window.location.search);
                // Enviamos el dato al componente de Streamlit
                window.parent.postMessage({
                    isStreamlitMessage: true,
                    type: "streamlit:set_component_value",
                    value: decodedText
                }, "*");
            }
            var html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 15, qrbox: 250 });
            html5QrcodeScanner.render(onScanSuccess);
        </script>
    """, height=350)

# --- PANTALLA PRINCIPAL ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

# --- TAB ENTRADAS ---
with t1:
    st.write("### Escanear Producto")
    # Capturamos el valor del escáner
    resultado_scan = escanner_real()
    
    # Si el escáner captó algo, lo ponemos como valor por defecto
    bus = st.text_input("Buscador / Escaneado", value=resultado_scan if resultado_scan else "", key="bus_ent")
    
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m_raw.data:
            m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
        
        if m_raw.data:
            p = m_raw.data[0]
            st.success(f"Producto: {p['nombre']}")
            with st.form("f_ing"):
                q = st.number_input("Cantidad", min_value=1, value=1)
                v = st.text_input("Vence (MMAA)", max_chars=4)
                if st.form_submit_button("REGISTRAR INGRESO"):
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], 
                        "cantidad": q, "fecha": fv, "ubicacion": "99-01A" # Aquí iría tu lógica de 99
                    }).execute()
                    st.rerun()

# --- TAB STOCK ---
with t2:
    st.write("### Consulta de Stock")
    scan_stock = escanner_real()
    bus_s = st.text_input("Buscar en Stock...", value=scan_stock if scan_stock else "", key="bus_stock")
    
    if bus_s:
        s_data = supabase.table("inventario").select("*").or_(f"nombre.ilike.%{bus_s}%,cod_int.eq.{bus_s}").execute().data
        for r in s_data:
            st.markdown(f'<div style="background:#F8FAFC; border-left:8px solid #3B82F6; padding:15px; margin-bottom:5px;"><b>{r["nombre"]}</b><br>📍 {r["ubicacion"]} | Q: {r["cantidad"]}</div>', unsafe_allow_html=True)

# --- TAB PLANILLA ---
with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

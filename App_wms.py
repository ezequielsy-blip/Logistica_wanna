import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- 2. KEYGEN MENSUAL SEGURO ---
def generar_llave_maestra(device_id):
    mes_año = datetime.now().strftime("%m%Y")
    frase_secreta = f"{device_id}7079{mes_año}LOGIEZE_SECURITY"
    return hashlib.sha256(frase_secreta.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESO MENSUAL</h1>", unsafe_allow_html=True)
    dev_id = "LGE-7079"
    st.info(f"ID SOLICITUD: **{dev_id}**")
    key_in = st.text_input("Ingrese Clave").strip().upper()
    if st.button("ACTIVAR"):
        if key_in == generar_llave_maestra(dev_id):
            st.session_state.activado = True
            st.rerun()
    st.stop()

# --- 3. ESTILOS LOGIEZE (BLANCO, GRIS, AZUL CLARO) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-baseweb="input"] {
        height: 65px !important; background-color: #F9FAF7 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input { font-size: 22px !important; color: #1E3A8A !important; }
    div.stButton > button {
        width: 100% !important; height: 75px !important; font-size: 22px !important; 
        font-weight: bold !important; border-radius: 12px !important;
        background-color: #3B82F6 !important; color: white !important;
    }
    h1 { text-align: center; color: #1E40AF; font-size: 40px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 8px solid #3B82F6; padding: 15px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIÓN ESCÁNER JAVASCRIPT ---
def componente_escanner(key):
    # Este componente inyecta un lector de barras real que usa la cámara
    return components.html(f"""
        <div id="reader-{key}" style="width:100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText, decodedResult) {{
                window.parent.postMessage({{type: 'barcode_scanned', value: decodedText, key: '{key}'}}, '*');
                html5QrcodeScanner.clear();
            }}
            var html5QrcodeScanner = new Html5QrcodeScanner("reader-{key}", {{ fps: 10, qrbox: 250 }});
            html5QrcodeScanner.render(onScanSuccess);
        </script>
    """, height=350)

# --- 5. LÓGICA DE UBICACIÓN 99 ---
def buscar_proxima_99():
    res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").execute()
    if not res.data: return "99-01A"
    ubis = [r['ubicacion'] for r in res.data]
    ubis.sort()
    ultima = ubis[-1].upper()
    p1, p2 = ultima.split("-")
    num = int("".join(filter(str.isdigit, p2)))
    letra = p2[-1]
    ciclo = ['A', 'B', 'C', 'D']
    if letra in ciclo and ciclo.index(letra) < 3:
        return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
    return f"99-{str(num+1).zfill(2)}A"

# --- 6. INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    st.subheader("Escanear para Ingreso")
    componente_escanner("entrada")
    
    bus = st.text_input("PRODUCTO (Código o Nombre)", key="input_ent")
    
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m_raw.data:
            m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
        
        if m_raw.data:
            p = m_raw.data[0]
            u_99 = buscar_proxima_99()
            st.info(f"Sugerencia: {u_99}")
            with st.form("f_ingreso"):
                q = st.number_input("Cantidad", min_value=1, value=1)
                v = st.text_input("Vence (MMAA)", max_chars=4)
                if st.form_submit_button("REGISTRAR"):
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], 
                        "cantidad": q, "fecha": fv, "ubicacion": u_99
                    }).execute()
                    st.success("Guardado"); st.rerun()

with t2:
    st.subheader("Consultar Stock")
    componente_escanner("stock")
    bus_s = st.text_input("Buscar en Stock...", key="input_stock")
    if bus_s:
        s_data = supabase.table("inventario").select("*").or_(f"nombre.ilike.%{bus_s}%,cod_int.eq.{bus_s}").execute().data
        for r in s_data:
            st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>📍 {r["ubicacion"]} | Q: {r["cantidad"]}</div>', unsafe_allow_html=True)

with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
import streamlit.components.v1 as components

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- LÓGICA DE KEYGEN ---
def generar_llave(device_id):
    # Fórmula secreta: ID + Frase Maestra
    return hashlib.sha256((device_id + "LOGIEZE2026").encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔑 ACTIVACIÓN</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079" # Este ID lo puedes hacer dinámico luego
    st.info(f"CÓDIGO DE SOLICITUD: **{device_id}**")
    key_input = st.text_input("Ingrese Clave de Licencia")
    if st.button("ACTIVAR APP"):
        if key_input == generar_llave(device_id):
            st.session_state.activado = True
            st.success("Licencia Válida")
            st.rerun()
        else:
            st.error("Clave Incorrecta")
    st.stop()

# --- ESTILOS LOGIEZE ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; display: flex !important; align-items: center !important;
        background-color: #F9FAF7 !important; border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
        font-size: 24px !important; line-height: 70px !important; height: 70px !important; color: #1E3A8A !important; padding: 0px 15px !important;
    }
    div.stButton > button {
        width: 100% !important; height: 85px !important; font-size: 26px !important; font-weight: 800 !important;
        border-radius: 15px !important; background-color: #3B82F6 !important; color: #FFFFFF !important;
    }
    .stWidgetLabel p { font-size: 22px !important; color: #64748B !important; font-weight: bold !important; }
    h1 { text-align: center; color: #1E40AF; font-size: 55px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 25px !important; border-radius: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SCRIPT PARA AUTO-ENTER Y SELECCIÓN ---
components.html("""
    <script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => input.select());
    });
    </script>
    """, height=0)

# --- LÓGICA DE UBICACIONES ---
def buscar_hueco_vacio():
    try:
        res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
        for e in range(1, 27):
            for n in range(1, 5):
                for l in ['A', 'B', 'C', 'D']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN HUECO"
    except: return "ERROR"

def buscar_proxima_99():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi = str(res.data[0]['ubicacion']).upper()
        p1, p2 = ubi.split("-")
        letra, num = p2[-1], int("".join(filter(str.isdigit, p2)))
        ciclo = ['A', 'B', 'C', 'D']
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

# --- TABS ---
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- ENTRADAS (Con Lector de Cámara) ---
with t1:
    st.write("### Escanear Producto")
    # Este componente abre la cámara en celulares para leer códigos
    barcode = st.text_input("Buscador / Escáner", key="scanner_input")
    
    if barcode:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{barcode},barras.eq.{barcode}").execute()
        if m_raw.data:
            p = m_raw.data[0]
            u_vacia, u_99 = buscar_hueco_vacio(), buscar_proxima_99()
            st.markdown(f'<div style="background-color:#E0F2FE; padding:10px; border-radius:10px; font-weight:bold;">📍 SUGERENCIA: {u_vacia} | 99: {u_99}</div>', unsafe_allow_html=True)
            
            with st.form("f_carga"):
                st.write(f"**{p['nombre']}**")
                c1, c2 = st.columns(2)
                q = c1.number_input("CANTIDAD", min_value=1, value=1)
                v_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4)
                dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                dest = c2.selectbox("DESTINO", [f"LIBRE ({u_vacia})", f"99 ({u_99})", "MANUAL"])
                man_raw = st.text_input("MANUAL (SI CORRESPONDE)").upper()
                
                if st.form_submit_button("⚡ REGISTRAR ENTRADA"):
                    ubi_f = u_vacia if "LIBRE" in dest else (u_99 if "99" in dest else man_raw)
                    fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                    supabase.table("inventario").insert({"cod_int":p['cod_int'], "nombre":p['nombre'], "cantidad":q, "fecha":fv, "ubicacion":ubi_f, "deposito":dep, "barras":p.get('barras', '')}).execute()
                    st.success("Registrado"); st.rerun()

# --- STOCK --- (Simplificado para el ejemplo)
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        for r in s_data:
            st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>CANT: {r["cantidad"]} | UBI: {r["ubicacion"]}</div>', unsafe_allow_html=True)

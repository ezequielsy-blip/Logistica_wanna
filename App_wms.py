import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime

# --- CONFIGURACIÓN DE SUPABASE ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- KEYGEN DE ALTA SEGURIDAD (IMPREDECIBLE) ---
def generar_llave_maestra(device_id):
    # Usamos Mes, Año y una "Sal Secreta" para que nadie pueda adivinarla
    mes_año = datetime.now().strftime("%m%Y")
    # Cambia esta palabra "LOGIEZE_SECRET_2026" si alguna vez querés resetear todo
    frase_secreta = f"{device_id}7079{mes_año}LOGIEZE_SECURITY"
    return hashlib.sha256(frase_secreta.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

# Pantalla de Bloqueo
if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 SISTEMA PROTEGIDO</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079" 
    
    st.warning(f"Licencia requerida para: **{datetime.now().strftime('%B %Y')}**")
    st.info(f"CÓDIGO DE SOLICITUD: **{device_id}**")
    
    key_input = st.text_input("Ingrese Clave Mensual").strip().upper()
    
    if st.button("ACTIVAR LICENCIA"):
        if key_input == generar_llave_maestra(device_id):
            st.session_state.activado = True
            st.success("Activado")
            st.rerun()
        else:
            st.error("La clave no coincide para este mes.")
    st.stop()

# --- ESTILOS LOGIEZE ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; background-color: #F9FAF7 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input { font-size: 24px !important; color: #1E3A8A !important; }
    div.stButton > button {
        width: 100% !important; height: 85px !important; font-size: 26px !important; 
        background-color: #3B82F6 !important; color: white !important; border-radius: 15px !important;
    }
    h1 { text-align: center; color: #1E40AF; font-size: 55px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 20px; border-radius: 12px; margin-bottom: 10px; }
    .sugerencia-box { background-color: #DBEAFE; color: #1E40AF; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE UBICACIÓN ---
def buscar_hueco_vacio():
    res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
    ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
    for e in range(1, 27):
        for n in range(1, 5):
            for l in ['A', 'B', 'C', 'D']:
                ubi = f"{str(e).zfill(2)}-{n}{l}"
                if ubi not in ocupadas: return ubi
    return "99-01A"

def buscar_proxima_99():
    res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
    if not res.data: return "99-01A"
    ubi = str(res.data[0]['ubicacion']).upper()
    p1, p2 = ubi.split("-")
    letra, num = p2[-1], int("".join(filter(str.isdigit, p2)))
    ciclo = ['A', 'B', 'C', 'D']
    if letra in ciclo and ciclo.index(letra) < 3:
        return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
    return f"99-{str(num+1).zfill(2)}A"

# --- TABS PRINCIPALES ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    bus = st.text_input("🔍 ESCANEAR O BUSCAR")
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if m_raw.data:
            p = m_raw.data[0]
            u_v, u_9 = buscar_hueco_vacio(), buscar_proxima_99()
            st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_v} | 99: {u_9}</div>', unsafe_allow_html=True)
            with st.form("carga"):
                q = st.number_input("CANTIDAD", min_value=1, value=1)
                v = st.text_input("VENCE (MMAA)", max_chars=4)
                dep = st.selectbox("DEPÓSITO", ["depo1", "depo2"])
                if st.form_submit_button("REGISTRAR"):
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({"cod_int":p['cod_int'], "nombre":p['nombre'], "cantidad":q, "fecha":fv, "ubicacion":u_v, "deposito":dep}).execute()
                    st.success("Guardado"); st.rerun()

with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        for r in s_data:
            st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>UBI: {r["ubicacion"]} | Q: {r["cantidad"]}</div>', unsafe_allow_html=True)

with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- 2. SEGURIDAD: KEYGEN MENSUAL (CLAVE ADM: 70797474) ---
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
    key_in = st.text_input("Ingrese Clave del Mes").strip().upper()
    if st.button("ACTIVAR APP"):
        # CLAVE FEB 2026: 50C44026
        if key_in == generar_llave_maestra(dev_id):
            st.session_state.activado = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
    st.stop()

# --- 3. ESTILOS PERSONALIZADOS (BLANCO, GRIS, AZUL CLARO) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; background-color: #F9FAF7 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input { font-size: 24px !important; color: #1E3A8A !important; }
    div.stButton > button {
        width: 100% !important; height: 80px !important; font-size: 24px !important; 
        font-weight: bold !important; border-radius: 15px !important;
        background-color: #3B82F6 !important; color: white !important;
    }
    h1 { text-align: center; color: #1E40AF; font-size: 45px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 20px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #E2E8F0; }
    .sugerencia-box { background-color: #DBEAFE; color: #1E40AF; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNCIONES DE UBICACIÓN (99 ALTA + 1) ---
def buscar_proxima_99():
    res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").execute()
    if not res.data: return "99-01A"
    ubis = [r['ubicacion'] for r in res.data]
    ubis.sort(reverse=True)
    ultima = ubis[0].upper() # Ej: 99-01D
    p1, p2 = ultima.split("-")
    num = int("".join(filter(str.isdigit, p2)))
    letra = p2[-1]
    ciclo = ['A', 'B', 'C', 'D']
    if letra in ciclo and ciclo.index(letra) < 3:
        return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
    return f"99-{str(num+1).zfill(2)}A"

# --- 5. CUERPO PRINCIPAL ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

# LOGIN ADMINISTRADOR
with st.sidebar:
    st.header("🔐 Admin")
    u_admin = st.text_input("Usuario").lower()
    p_admin = st.text_input("Clave", type="password")
    es_admin = (u_admin == "admin" and p_admin == "70797474")

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB ENTRADAS ---
with t1:
    col_scan, col_text = st.columns([1, 4])
    with col_scan:
        cam_ent = st.camera_input("📷", key="cam_ent") # Escáner rápido
    
    # El buscador toma la cámara o el texto
    bus_val = ""
    if cam_ent: bus_val = "ESCANEADO" # Aquí iría la lógica de decodificación si se integra
    
    bus = col_text.text_input("🔍 BUSCAR O ESCANEAR", placeholder="Código o Nombre...", key="bus_ent")
    
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m_raw.data:
            m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
        
        if m_raw.data:
            p = m_raw.data[0]
            u_99 = buscar_proxima_99()
            st.markdown(f'<div class="sugerencia-box">📍 UBICACIÓN SUGERIDA: {u_99}</div>', unsafe_allow_html=True)
            
            with st.form("f_entrada", clear_on_submit=True):
                st.write(f"### {p['nombre']}")
                q = st.number_input("CANTIDAD", min_value=1, value=1)
                v = st.text_input("VENCIMIENTO (MMAA)", max_chars=4)
                dep = st.selectbox("DEPÓSITO", ["depo1", "depo2"])
                ubi_manual = st.text_input("UBICACIÓN (VACÍO PARA {u_99})").upper().replace("-", "")
                
                if st.form_submit_button("⚡ REGISTRAR"):
                    ubi_final = f"{ubi_manual[:2]}-{ubi_manual[2:]}" if ubi_manual else u_99
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, 
                        "fecha": fv, "ubicacion": ubi_final, "deposito": dep
                    }).execute()
                    st.success("Cargado correctamente"); st.rerun()

# --- TAB STOCK ---
with t2:
    col_scan2, col_text2 = st.columns([1, 4])
    with col_scan2:
        cam_stock = st.camera_input("📷", key="cam_stock")
    
    bus_s = col_text2.text_input("🔍 BUSCAR EN STOCK", key="bus_s")
    
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if not s_data:
             s_data = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s}").execute().data
        
        if s_data:
            for r in s_data:
                st.markdown(f"""<div class="stock-card">
                    <b>{r['nombre']}</b><br>
                    ID: {r['cod_int']} | Q: {r['cantidad']}<br>
                    📍 {r['ubicacion']} | {r['deposito']} | 📅 {r['fecha']}
                </div>""", unsafe_allow_html=True)
                
                if es_admin:
                    c_sal, c_pas = st.columns(2)
                    if c_sal.button("SALIDA", key=f"sal_{r['id']}"):
                        supabase.table("inventario").delete().eq("id", r['id']).execute()
                        st.rerun()

# --- TAB PLANILLA ---
with t3:
    st.write("### Vista General Excel 2013")
    p_raw = supabase.table("inventario").select("*").order("id", desc=True).limit(50).execute()
    if p_raw.data:
        st.dataframe(pd.DataFrame(p_raw.data), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR APP", type="secondary"):
    st.rerun()

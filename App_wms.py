import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LOGISTICA Master", layout="wide", initial_sidebar_state="collapsed")

# --- LÓGICA DE SEGURIDAD (KEYGEN IMPREDECIBLE) ---
def generar_llave_maestra(device_id):
    mes_año = datetime.now().strftime("%m%Y")
    frase_secreta = f"{device_id}7079{mes_año}LOGIEZE_SECURITY"
    return hashlib.sha256(frase_secreta.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESO LOGIEZE</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079" 
    st.warning(f"Licencia para: **{datetime.now().strftime('%B %Y')}**")
    key_input = st.text_input("Ingrese Clave del Mes").strip().upper()
    if st.button("ACTIVAR AHORA"):
        if key_input == generar_llave_maestra(device_id):
            st.session_state.activado = True
            st.rerun()
        else:
            st.error("Clave Incorrecta.")
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
        font-weight: 800 !important;
    }
    h1 { text-align: center; color: #1E40AF; font-size: 55px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 25px; border-radius: 12px; margin-bottom: 10px; }
    .sugerencia-box { background-color: #DBEAFE; color: #1E40AF; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; font-size: 20px; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UBICACIONES (Sugerencia 99 alta + 1) ---
def buscar_hueco_vacio():
    res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
    ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
    for e in range(1, 27):
        for n in range(1, 5):
            for l in ['A', 'B', 'C', 'D']:
                ubi = f"{str(e).zfill(2)}-{n}{l}"
                if ubi not in ocupadas: return ubi
    return "SIN HUECO"

def buscar_proxima_99():
    res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("ubicacion", desc=True).limit(1).execute()
    if not res.data: return "99-01A"
    ubi = str(res.data[0]['ubicacion']).upper() # Ejemplo: 99-05C
    p1, p2 = ubi.split("-")
    num = int("".join(filter(str.isdigit, p2)))
    letra = p2[-1]
    ciclo = ['A', 'B', 'C', 'D']
    if letra in ciclo and ciclo.index(letra) < 3:
        return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
    return f"99-{str(num+1).zfill(2)}A"

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

if "barcode" not in st.session_state:
    st.session_state.barcode = ""

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    # --- ESCÁNER DE CÓDIGO DE BARRAS ---
    with st.expander("📷 ABRIR ESCÁNER DE CÁMARA"):
        img_file = st.camera_input("Enfoca el código de barras")
        if img_file:
            # Aquí es donde normalmente procesarías la imagen. 
            # Como Streamlit corre en servidor, para APK se recomienda usar 
            # el lector de teclado de Android o un botón de JS.
            st.warning("Imagen capturada. El APK usará el lector láser automático.")

    bus = st.text_input("🔍 ESCANEAR O BUSCAR", value=st.session_state.barcode)
    
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if m_raw.data:
            p = m_raw.data[0]
            u_v, u_9 = buscar_hueco_vacio(), buscar_proxima_99()
            st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_v} | SUGERIDA: {u_9}</div>', unsafe_allow_html=True)
            
            with st.form("f_carga", clear_on_submit=True):
                st.write(f"### {p['nombre']} (ID: {p['cod_int']})")
                c1, c2 = st.columns(2)
                q = c1.number_input("CANTIDAD", min_value=1, value=1)
                v_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="1226")
                
                dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                dest = c2.selectbox("DESTINO", [f"LIBRE ({u_v})", f"99 ALTA ({u_9})", "MANUAL"])
                man_raw = st.text_input("MANUAL (EJ: 011A)").upper().replace("-", "")
                
                if st.form_submit_button("⚡ REGISTRAR"):
                    if "LIBRE" in dest: ubi_f = u_v
                    elif "99" in dest: ubi_f = u_9
                    else: ubi_f = f"{man_raw[:2]}-{man_raw[2:]}" if len(man_raw) > 2 else man_raw
                    
                    fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                    
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, 
                        "fecha": fv, "ubicacion": ubi_f, "deposito": dep
                    }).execute()
                    st.success("Registrado"); st.rerun()

with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        for r in s_data:
            st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>UBI: {r["ubicacion"]} | Q: {r["cantidad"]} | V: {r["fecha"]}</div>', unsafe_allow_html=True)

with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

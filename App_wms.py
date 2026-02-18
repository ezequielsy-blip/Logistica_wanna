import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- ESTILOS LOGIEZE (Blanco, Gris, Azul Claro) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .block-container { padding: 1rem !important; }
    
    /* Buscador Gigante */
    div[data-baseweb="input"] {
        height: 80px !important;
        background-color: #F3F4F6 !important;
        border: 3px solid #BFDBFE !important;
        border-radius: 15px !important;
    }
    .stTextInput input { font-size: 30px !important; color: #1E3A8A !important; font-weight: bold; }
    
    /* Botonera */
    div.stButton > button {
        height: 90px !important; font-size: 25px !important;
        background-color: #3B82F6 !important; color: white !important;
        border-radius: 15px !important; font-weight: 800 !important;
    }
    
    /* Tarjetas de Stock */
    .card {
        background-color: #F9FAF7; padding: 20px;
        border-left: 12px solid #3B82F6; border-radius: 10px;
        margin-bottom: 15px; border: 1px solid #E5E7EB;
    }
    h1 { color: #1E40AF; text-align: center; font-size: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA UBICACIÓN 99 ALTA + 1 ---
def proxima_99():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").execute()
        if not res.data: return "99-01A"
        ubis = sorted([r['ubicacion'] for r in res.data], reverse=True)
        u = ubis[0].upper()
        p1, p2 = u.split("-")
        num = int("".join(filter(str.isdigit, p2)))
        letra = p2[-1]
        ciclo = ['A', 'B', 'C', 'D']
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    # EL SECRETO: El buscador tiene el "focus". 
    # Al usar el teclado escáner del cel, pega el código y da ENTER solo.
    bus = st.text_input("🔍 ESCANEAR CÓDIGO", key="main_bus", placeholder="Scan here...")

    if bus:
        m = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m.data:
            m = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
        
        if m.data:
            p = m.data[0]
            u99 = proxima_99()
            st.markdown(f"<div style='text-align:center; font-size:20px; color:blue;'>Sugerencia: <b>{u99}</b></div>", unsafe_allow_html=True)
            
            with st.form("f_ingreso", clear_on_submit=True):
                st.write(f"### {p['nombre']}")
                q = st.number_input("CANTIDAD", min_value=1, value=1)
                v = st.text_input("VENCIMIENTO (MMAA)", max_chars=4)
                dep = st.selectbox("DEPÓSITO", ["depo1", "depo2"])
                if st.form_submit_button("⚡ REGISTRAR"):
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], 
                        "cantidad": q, "fecha": fv, "ubicacion": u99, "deposito": dep
                    }).execute()
                    st.success("CARGADO"); st.rerun()
        else:
            st.error("NO ENCONTRADO")

with t2:
    bus_s = st.text_input("🔍 BUSCAR EN STOCK", key="stk_bus")
    if bus_s:
        s_data = supabase.table("inventario").select("*").or_(f"nombre.ilike.%{bus_s}%,cod_int.eq.{bus_s}").execute().data
        for r in s_data:
            st.markdown(f"""<div class="card">
                <b>{r['nombre']}</b><br>
                ID: {r['cod_int']} | Q: {r['cantidad']}<br>
                📍 {r['ubicacion']} | {r['deposito']} | 📅 {r['fecha']}
            </div>""", unsafe_allow_html=True)

with t3:
    p_raw = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_raw: st.dataframe(pd.DataFrame(p_raw), use_container_width=True)

if st.button("🔄 REFRESCAR"):
    st.rerun()

import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- ESTILOS LOGIEZE (Corrección de Texto Cortado) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    h1 { text-align: center; color: #1E40AF; font-size: 50px !important; font-weight: 900; margin-bottom: 20px; }
    
    /* BOTONES GIGANTES CON TEXTO CENTRADO */
    div.stButton > button { 
        width: 100%; 
        height: 90px !important; 
        font-size: 24px !important; /* Bajé un poco para que no corte */
        font-weight: 800 !important; 
        border-radius: 15px !important; 
        background-color: #3B82F6 !important; 
        color: white !important;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2 !important; /* Evita que se corte arriba/abajo */
        padding: 10px !important;
    }
    
    /* INPUTS GRANDES */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { 
        font-size: 24px !important; 
        height: 70px !important; 
        background-color: #F9FAF7 !important; 
        border: 3px solid #BFDBFE !important; 
        border-radius: 12px !important; 
    }

    .sugerencia-box { 
        background-color: #EFF6FF; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #3B82F6; 
        color: #1E40AF; 
        font-size: 22px; 
        font-weight: bold;
    }

    .stock-card { 
        background-color: #F8FAFC; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 8px solid #94A3B8; 
        margin-bottom: 10px; 
        border: 1px solid #E2E8F0;
        font-size: 18px;
    }
    
    /* Pestañas más legibles */
    .stTabs [data-baseweb="tab"] {
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
with st.sidebar:
    st.header("🔐 Acceso")
    u_log = st.text_input("Usuario").lower()
    p_log = st.text_input("Contraseña", type="password")
    
    es_autorizado = (u_log == "admin" and p_log == "70797474")
    es_admin_maestro = es_autorizado
    
    if not es_autorizado and u_log and p_log:
        try:
            res_u = supabase.table("usuarios").select("*").eq("usuario", u_log).eq("clave", p_log).execute()
            if res_u.data:
                es_autorizado = True
        except: pass

# --- LOGICA 99 ---
def buscar_proxima_99():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("ubicacion", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi = str(res.data[0]['ubicacion']).upper()
        p1, p2 = ubi.split("-")
        letra = p2[-1]
        num = int("".join(filter(str.isdigit, p2)))
        ciclo = ['A', 'B', 'C', 'D']
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

tabs_list = ["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"]
if es_admin_maestro: tabs_list.append("👥 USUARIOS")
t1, t2, t3, *t_extra = st.tabs(tabs_list)

with t1:
    if es_autorizado:
        bus = st.text_input("🔍 BUSCAR PRODUCTO", key="ent_bus")
        if bus:
            m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
            m_data = m_raw.data if m_raw.data else supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute().data
            
            if m_data:
                p = m_data[0]
                u_99 = buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 SUGERIDA: {u_99}</div>', unsafe_allow_html=True)
                
                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']}")
                    q = st.number_input("CANTIDAD", min_value=1, value=1)
                    v_raw = st.text_input("VENCE (MMAA)", max_chars=4)
                    dep = st.selectbox("DEPÓSITO", ["depo1", "depo2"])
                    dest = st.selectbox("DESTINO", [f"SERIE 99 ({u_99})", "MANUAL"])
                    man_raw = st.text_input("MANUAL (EJ: 011A)").upper().replace("-", "")
                    
                    if st.form_submit_button("⚡ REGISTRAR"):
                        ubi_f = u_99 if "99" in dest else (f"{man_raw[:2]}-{man_raw[2:]}" if len(man_raw) > 2 else man_raw)
                        fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                        supabase.table("inventario").insert({
                            "cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, 
                            "fecha": fv, "ubicacion": ubi_f, "deposito": dep
                        }).execute()
                        st.success("¡Cargado!"); st.rerun()

with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if s_data:
            for r in s_data:
                st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>UBI: {r["ubicacion"]} | Q: {r["cantidad"]}</div>', unsafe_allow_html=True)
                if es_autorizado:
                    if st.button("SALIDA", key=f"sal_{r['id']}"):
                        supabase.table("inventario").delete().eq("id", r['id']).execute()
                        st.rerun()

with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(50).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

if es_admin_maestro:
    with t_extra[0]:
        st.header("👥 Usuarios")
        with st.form("nu"):
            nu = st.text_input("Usuario")
            np = st.text_input("Clave")
            if st.form_submit_button("REGISTRAR"):
                supabase.table("usuarios").insert({"usuario": nu.lower(), "clave": np}).execute()
                st.rerun()

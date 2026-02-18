import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS LOGIEZE ---
st.markdown("""
<style>
    .main { background-color: #FFFFFF; }
    h1 { text-align: center; color: #1E40AF; font-size: 50px !important; font-weight: 800; }

    /* Botones Gigantes */
    div.stButton > button {
        width: 100%; height: 85px !important; font-size: 24px !important;
        font-weight: 700 !important; border-radius: 15px !important;
        background-color: #3B82F6 !important; color: white !important;
    }

    /* Inputs y Selectbox (Sin cortes) */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 22px !important; height: 70px !important;
        background-color: #F9FAF7 !important; border: 2px solid #BFDBFE !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div { height: 70px !important; display: flex; align-items: center; }

    .sugerencia-box {
        background-color: #F0F9FF; padding: 20px; border-radius: 15px;
        border-left: 10px solid #3B82F6; color: #1E40AF; font-size: 22px; font-weight: bold;
    }

    .stock-card {
        background-color: #F8FAFC; padding: 18px; border-radius: 15px;
        border-left: 10px solid #94A3B8; margin-bottom: 12px; border: 1px solid #E2E8F0;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA UBICACIÓN 99 ---
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

# --- LOGIN ---
with st.sidebar:
    u_log = st.text_input("Usuario").lower()
    p_log = st.text_input("Contraseña", type="password")
    es_autorizado = (u_log == "admin" and p_log == "70797474")
    if not es_autorizado and u_log and p_log:
        try:
            res_u = supabase.table("usuarios").select("*").eq("usuario", u_log).eq("clave", p_log).execute()
            if res_u.data: es_autorizado = True
        except: pass

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- ENTRADAS ---
with t1:
    if es_autorizado:
        bus = st.text_input("🔍 BUSCAR PRODUCTO", key="ent_bus")
        if bus:
            m_raw = supabase.table("maestra").select("*").execute()
            m_data = [i for i in m_raw.data if str(i.get('cod_int')) == bus or str(i.get('barras')) == bus or bus.lower() in i.get('nombre').lower()]
            if m_data:
                p = m_data[0]
                u_99 = buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 PRÓXIMA 99: {u_99}</div>', unsafe_allow_html=True)
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
                        supabase.table("inventario").insert({"cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, "fecha": fv, "ubicacion": ubi_f, "deposito": dep}).execute()
                        st.rerun()

# --- STOCK / PASES (CORREGIDO) ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        # Búsqueda directa en Supabase para asegurar que traiga resultados
        if bus_s.isdigit():
            res_s = supabase.table("inventario").select("*").eq("cod_int", bus_s).execute()
        else:
            res_s = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute()
        
        if res_s.data:
            for r in res_s.data:
                curr_q = int(r['cantidad'])
                st.markdown(f"""<div class="stock-card">
                    <b>{r['nombre']}</b><br>
                    Q: {curr_q} | VENCE: {r['fecha']}<br>
                    📍 {r['ubicacion']} | {r['deposito']}
                </div>""", unsafe_allow_html=True)
                
                if es_autorizado:
                    col_sal, col_pas = st.columns(2)
                    qm = st.number_input(f"Cant. a mover ({r['id']})", min_value=1, max_value=curr_q, value=1, key=f"q_{r['id']}")
                    if col_sal.button("SALIDA", key=f"s_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.rerun()
                    if col_pas.button("PASAR", key=f"p_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':qm, 'fecha':r['fecha']}
                        st.rerun()
        else:
            st.warning("No se encontraron lotes con ese nombre o ID.")

# --- PLANILLA ---
with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

if st.button("🔄 ACTUALIZAR"):
    st.rerun()

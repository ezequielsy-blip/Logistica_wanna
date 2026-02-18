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
    h1 { text-align: center; color: #1E40AF; font-size: 45px !important; font-weight: 800; }

    /* Botones de acción principal (Grandes) */
    div.stButton > button {
        width: 100%; height: 80px !important; font-size: 24px !important;
        font-weight: 700 !important; border-radius: 15px !important;
        background-color: #3B82F6 !important; color: white !important;
    }

    /* BOTONES PEQUEÑOS (SALIDA/PASAR) - Para que entren lado a lado */
    [data-testid="column"] div.stButton > button {
        height: 55px !important; 
        font-size: 18px !important;
        background-color: #1E40AF !important;
    }

    /* Inputs y Selectbox */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 20px !important; height: 60px !important;
        background-color: #F9FAF7 !important; border: 2px solid #BFDBFE !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] > div { height: 60px !important; display: flex; align-items: center; }

    .stock-card {
        background-color: #F8FAFC; padding: 15px; border-radius: 12px;
        border-left: 8px solid #94A3B8; margin-bottom: 10px; border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

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

st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- ENTRADAS (Simplificado para el ejemplo) ---
with t1:
    if es_autorizado:
        st.write("### Carga de Mercadería")
        # Aquí iría tu lógica de entradas...

# --- STOCK / PASES (BOTONES LADO A LADO) ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        if bus_s.isdigit():
            res_s = supabase.table("inventario").select("*").eq("cod_int", bus_s).execute()
        else:
            res_s = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute()
        
        if res_s.data:
            for r in res_s.data:
                curr_q = int(r['cantidad'])
                st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>Q: {curr_q} | UBI: {r["ubicacion"]}</div>', unsafe_allow_html=True)
                
                if es_autorizado:
                    # Cantidad a mover arriba de los botones
                    qm = st.number_input(f"Cant. ({r['id']})", min_value=1, max_value=curr_q, value=1, key=f"q_{r['id']}")
                    
                    # COLUMNAS PARA BOTONES LADO A LADO
                    c_sal, c_pas = st.columns(2)
                    
                    if c_sal.button("SALIDA", key=f"s_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.rerun()
                    
                    if c_pas.button("PASAR", key=f"p_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':qm, 'fecha':r['fecha']}
                        st.rerun()
        else:
            st.warning("No se encontraron lotes.")

with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(20).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True)

if st.button("🔄 ACTUALIZAR"):
    st.rerun()

import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS (Botones grandes, en línea y recuadros) ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    div.stButton > button {
        width: 100%; height: 75px !important; font-size: 22px !important;
        font-weight: 700 !important; border-radius: 12px !important; 
        border: 2px solid #2C3E50 !important; color: white !important;
    }
    div.stForm button { background-color: #2D5A27 !important; border-color: #3E8E41 !important; } 
    div[data-testid="column"]:nth-of-type(1) button { background-color: #34495E !important; } 
    div[data-testid="column"]:nth-of-type(2) button { background-color: #1B2631 !important; } 
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 20px !important; height: 55px !important; 
        background-color: #1A1C23 !important; color: #ECF0F1 !important;
        border: 1px solid #34495E !important;
    }
    h1 { text-align: center; color: #FFFFFF; font-size: 55px !important; font-weight: 800; }
    .sugerencia-box { 
        background-color: #1C2833; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #3498DB; margin-bottom: 20px; color: #D5DBDB; 
    }
    .stock-card { 
        background-color: #17202A; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #2C3E50; margin-bottom: 12px; color: #EBEDEF; 
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- MOTORES DE SUGERENCIA ---
def sugerencia_fisica_vacia():
    try:
        res_inv = supabase.table("inventario").select("ubicacion").eq("deposito", "DEPO 1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res_inv.data] if res_inv.data else []
        for e in range(1, 28):
            for n in range(1, 7):
                for l in ['A', 'B', 'C', 'D', 'E']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN HUECOS"
    except: return "Error"

def sugerencia_99_proxima():
    try:
        res_99 = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res_99.data: return "99-01A"
        ubi_str = str(res_99.data[0]['ubicacion']).upper()
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_actual = int("".join(filter(str.isdigit, cuerpo)))
        ciclo = ['A', 'B', 'C', 'D']
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            nueva_letra = ciclo[idx+1] if idx < 3 else 'A'
            nuevo_num = num_actual if idx < 3 else num_actual + 1
        else: nueva_letra, nuevo_num = 'A', num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

with st.sidebar:
    clave = st.text_input("PIN", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 RECARGAR"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

with tab1:
    if es_autorizado:
        init_bus = st.session_state.transfer_data['cod_int'] if st.session_state.transfer_data else ""
        bus_m = st.text_input("🔍 PRODUCTO", value=init_bus, key="entrada_bus")
        
        if bus_m:
            res_m = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus_m},barras.eq.{bus_m},nombre.ilike.%{bus_m}%").execute()
            df_m = pd.DataFrame(res_m.data)
            if not df_m.empty:
                prod = df_m.iloc[0]
                ubi_vacia = sugerencia_fisica_vacia()
                ubi_99 = sugerencia_99_proxima()
                
                st.markdown(f'<div class="sugerencia-box">📍 <b>LIBRE:</b> {ubi_vacia} | <b>SIGUIENTE 99:</b> {ubi_99}</div>', unsafe_allow_html=True)

                with st.form("form_carga", clear_on_submit=True):
                    # Pre-carga de transferencia
                    def_q = float(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 0.0
                    def_v = st.session_state.transfer_data['fecha'].replace("/", "") if st.session_state.transfer_data else ""
                    def_d_idx = 1 if st.session_state.transfer_data and st.session_state.transfer_data['deposito_orig'] == "DEPO 1" else 0
                    
                    st.write(f"### {prod['nombre']}")
                    c1, c2 = st.columns(2)
                    f_can = c1.number_input("CANTIDAD", min_value=0.0, value=def_q)
                    f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", value=def_v, max_chars=4)
                    f_dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"], index=def_d_idx)
                    
                    # SELECTOR COMPLETO
                    res_e = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).execute()
                    df_e = pd.DataFrame(res_e.data)
                    op_ubi = [f"FISICA LIBRE ({ubi_vacia})", f"PROXIMA 99 ({ubi_99})"]
                    if not df_e.empty:
                        for _, l in df_e.iterrows():
                            op_ubi.append(f"SUMAR A: {l['ubicacion']} | {l['deposito']}")
                    op_ubi.append("OTRA (MANUAL)")
                    
                    sel_ubi = c2.selectbox("UBICACIÓN DESTINO", op_ubi)
                    f_ubi_manual = st.text_input("Escribir Manual:")

                    if st.form_submit_button("⚡ FINALIZAR CARGA"):
                        if f_can > 0 and len(f_venc_raw) == 4:
                            # Lógica de asignación de ubicación
                            if "FISICA LIBRE" in sel_ubi: f_ubi = ubi_vacia
                            elif "PROXIMA 99" in sel_ubi: f_ubi = ubi_99
                            elif "SUMAR A:" in sel_ubi: f_ubi = sel_ubi.split(": ")[1].split(" |")[0]
                            else: f_ubi = f_ubi_manual.upper()
                            
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            if match.data:
                                supabase.table("inventario").update({"cantidad": float(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int": prod['cod_int'], "nombre": prod['nombre'], "cantidad": f_can, "fecha": f_venc, "ubicacion": f_ubi, "deposito": f_dep, "barras": prod['barras']}).execute()
                            
                            st.session_state.transfer_data = None
                            st.

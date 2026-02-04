import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- GESTIÓN DE ESTADO PARA PASES ---
if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS MEJORADOS (Recuadros Grandes y Estéticos) ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    
    /* Forzar botones uno al lado del otro */
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    
    /* Botones Grandes y Estéticos */
    div.stButton > button {
        width: 100%; height: 75px !important; font-size: 22px !important;
        font-weight: 700 !important; border-radius: 12px !important; 
        border: 2px solid #2C3E50 !important; color: white !important;
        transition: 0.3s;
    }
    
    /* Colores Formales */
    div.stForm button { background-color: #2D5A27 !important; border-color: #3E8E41 !important; } /* Registrar */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #34495E !important; } /* Salida */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #1B2631 !important; } /* Pasar */

    /* Inputs y Selectores Grandes */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 20px !important; height: 55px !important; 
        background-color: #1A1C23 !important; color: #ECF0F1 !important;
        border: 1px solid #34495E !important; border-radius: 8px !important;
    }

    h1 { text-align: center; color: #FFFFFF; font-size: 55px !important; font-weight: 800; margin-bottom: 20px; text-shadow: 2px 2px 4px #000; }
    
    /* Recuadros Estéticos */
    .sugerencia-box { 
        background-color: #1C2833; padding: 20px; border-radius: 15px; 
        border: 1px solid #3498DB; border-left: 10px solid #3498DB; 
        margin-bottom: 20px; color: #D5DBDB; 
    }
    
    .stock-card { 
        background-color: #17202A; padding: 20px; border-radius: 15px; 
        border: 1px solid #2C3E50; border-left: 10px solid #2C3E50; 
        margin-bottom: 12px; color: #EBEDEF; 
    }
    
    .total-banner {
        background-color: #21618C; padding: 15px; border-radius: 12px;
        text-align: center; color: white; margin-bottom: 15px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE MOTOR DE SUGERENCIAS ---
def motor_sugerencia_pc():
    try:
        # 1. Buscar posiciones vacías (01-27, 1-6, A-E)
        niveles = [str(i) for i in range(1, 7)]
        letras = ['A', 'B', 'C', 'D', 'E']
        
        res_inv = supabase.table("inventario").select("ubicacion").eq("deposito", "DEPO 1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res_inv.data] if res_inv.data else []

        for e in range(1, 28):
            for n in niveles:
                for l in letras:
                    ubi_test = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi_test not in ocupadas:
                        return ubi_test 

        # 2. Serie 99 si no hay físicas libres
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
        else:
            nueva_letra, nuevo_num = 'A', num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

with st.sidebar:
    clave = st.text_input("PIN Acceso", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 REFRESCAR"): st.rerun()

# Definir pestañas (Sin Picking)
tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS (Incluye Modo Paso) ---
with tab1:
    if not es_autorizado:
        st.info("Ingrese clave para operar.")
    else:
        # Recuperar datos si viene de un PASO
        init_bus = ""
        if st.session_state.transfer_data:
            init_bus = st.session_state.transfer_data['cod_int']
            st.warning(f"🔄 PASO ACTIVO: Moviendo {st.session_state.transfer_data['cantidad']} unid.")

        bus_m = st.text_input("🔍 ESCANEAR O BUSCAR", value=init_bus, key="entrada_bus")
        
        if bus_m:
            res_m = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus_m},barras.eq.{bus_m},nombre.ilike.%{bus_m}%").execute()
            df_m = pd.DataFrame(res_m.data)
            
            if not df_m.empty:
                prod = df_m.iloc[0]
                ubi_sugerida = motor_sugerencia_pc()
                
                st.markdown(f'<div class="sugerencia-box">📍 Ubicación sugerida: <b style="font-size:24px;">{ubi_sugerida}</b></div>', unsafe_allow_html=True)

                with st.form("form_carga", clear_on_submit=True):
                    # Pre-cargar si hay transferencia
                    def_q = float(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 0.0
                    def_v = st.session_state.transfer_data['fecha'].replace("/", "") if st.session_state.transfer_data else ""
                    def_d_idx = 1 if st.session_state.transfer_data and st.session_state.transfer_data['deposito_orig'] == "DEPO 1" else 0
                    
                    st.write(f"### {prod['nombre']}")
                    c1, c2 = st.columns(2)
                    f_can = c1.number_input("CANTIDAD", min_value=0.0, value=def_q, step=1.0)
                    f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", value=def_v, max_chars=4)
                    
                    f_dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"], index=def_d_idx)
                    
                    # Ver lotes existentes
                    res_e = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).execute()
                    df_e = pd.DataFrame(res_e.data)
                    op_ubi = [f"SUGERIDA ({ubi_sugerida})"]
                    if not df_e.empty:
                        for _, l in df_e.iterrows():
                            op_ubi.append(f"EXISTE: {l['ubicacion']} | {l['deposito']}")
                    op_ubi.append("MANUAL")
                    sel_ubi = c2.selectbox("DESTINO", op_ubi)
                    
                    f_ubi_manual = st.text_input("Si eligió MANUAL:")

                    if st.form_submit_button("⚡ REGISTRAR CARGA"):
                        if f_can > 0 and len(f_venc_raw) == 4:
                            f_ubi = ubi_sugerida if "SUGERIDA" in sel_ubi else (sel_ubi.split(": ")[1].split(" |")[0] if "EXISTE:" in sel_ubi else f_ubi_manual.upper())
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            
                            # Upsert
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            if match.data:
                                supabase.table("inventario").update({"cantidad": float(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int": prod['cod_int'], "nombre": prod['nombre'], "cantidad": f_can, "fecha": f_venc, "ubicacion": f_ubi, "deposito": f_dep, "barras": prod['barras']}).execute()
                            
                            st.session_state.transfer_data = None
                            st.success("✅ ¡Carga Exitosa!")
                            st.rerun()

# --- TAB 2: STOCK / PASES (Botones Grandes lado a lado) ---
with tab2:
    bus_s = st.text_input("🔎 BUSCADOR STOCK / PASES", key="bus_s")
    if bus_s:
        res_s = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s},nombre.ilike.%{bus_s}%").execute()
        df_s = pd.DataFrame(res_s.data)
        if not df_s.empty:
            df_s = df_s[df_s['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f'<div class="total-banner"><h2>TOTAL: {df_s["cantidad"].sum()}</h2></div>', unsafe_allow_html=True)
            
            for _, r in df_s.iterrows():
                with st.container():
                    st.markdown(f"""<div class="stock-card">
                        <b style="font-size:22px;">{r['nombre']}</b><br>
                        Q: <span style="color:#F1C40F; font-size:20px;">{r['cantidad']}</span> | UBI: {r['ubicacion']} | {r['deposito']} | {r['fecha']}
                    </div>""", unsafe_allow_html=True)
                    
                    if es_autorizado:
                        cant_mov = st.number_input(f"Cantidad a mover (ID:{r['id']})", min_value=0.1, max_value=float(r['cantidad']), key=f"q_{r['id']}")
                        
                        csal, cpas = st.columns(2)
                        if csal.button("SALIDA", key=f"s_{r['id']}"):
                            nueva_q = float(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                        
                        if cpas.button("PASAR", key=f"p_{r['id']}"):
                            # 1. Restar del actual
                            nueva_q = float(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            # 2. Mandar a Tab Entradas pre-cargado
                            st.session_state.transfer_data = {'cod_int': r['cod_int'], 'cantidad': cant_mov, 'fecha': r['fecha'], 'deposito_orig': r['deposito']}
                            st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    res_p = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True, hide_index=True)

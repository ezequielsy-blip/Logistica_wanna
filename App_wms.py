import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- GESTIÓN DE ESTADO ---
if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS (Recuadros grandes, botones en línea y modo oscuro) ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    
    /* Botones Grandes */
    div.stButton > button {
        width: 100%; height: 80px !important; font-size: 24px !important;
        font-weight: 700 !important; border-radius: 15px !important; 
        color: white !important;
    }
    
    /* Colores Específicos */
    div.stForm button { background-color: #1E8449 !important; } /* Registrar */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #2E4053 !important; } /* Salida */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #1B2631 !important; } /* Pasar */

    /* Inputs Gigantes */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 22px !important; height: 60px !important; 
        background-color: #1A1C23 !important; color: #ECF0F1 !important;
        border: 2px solid #34495E !important; border-radius: 10px !important;
    }

    h1 { text-align: center; color: #FFFFFF; font-size: 60px !important; font-weight: 800; margin-bottom: 25px; }
    
    .sugerencia-box { 
        background-color: #1C2833; padding: 25px; border-radius: 15px; 
        border-left: 12px solid #3498DB; margin-bottom: 25px; color: #D5DBDB; font-size: 20px;
    }
    
    .stock-card { 
        background-color: #17202A; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #2C3E50; margin-bottom: 15px; color: #EBEDEF;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- MOTORES DE UBICACIÓN ---
def sugerencia_fisica_vacia():
    try:
        res_inv = supabase.table("inventario").select("ubicacion").eq("deposito", "DEPO 1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res_inv.data] if res_inv.data else []
        for e in range(1, 28):
            for n in range(1, 7):
                for l in ['A', 'B', 'C', 'D', 'E']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN ESPACIO"
    except: return "ERROR"

def sugerencia_99_proxima():
    try:
        res_99 = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res_99.data: return "99-01A"
        ubi_str = str(res_99.data[0]['ubicacion']).upper()
        # Lógica de secuencia 99 +1 abcd
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
    clave = st.text_input("CLAVE ADMIN", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 REFRESCAR SISTEMA"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB ENTRADAS ---
with tab1:
    if es_autorizado:
        # Recuperar datos si viene de un PASO
        init_bus = st.session_state.transfer_data['cod_int'] if st.session_state.transfer_data else ""
        if st.session_state.transfer_data:
            st.info(f"🔄 MODO PASO: Moviendo {int(st.session_state.transfer_data['cantidad'])} unidades")

        bus_m = st.text_input("🔍 ESCANEAR / BUSCAR", value=init_bus, key="entrada_bus")
        
        if bus_m:
            res_m = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus_m},barras.eq.{bus_m},nombre.ilike.%{bus_m}%").execute()
            df_m = pd.DataFrame(res_m.data)
            
            if not df_m.empty:
                prod = df_m.iloc[0]
                ubi_vacia = sugerencia_fisica_vacia()
                ubi_99 = sugerencia_99_proxima()
                
                st.markdown(f'<div class="sugerencia-box">📍 <b>UBI VACÍA:</b> {ubi_vacia} | <b>SIGUIENTE 99:</b> {ubi_99}</div>', unsafe_allow_html=True)

                with st.form("form_carga", clear_on_submit=True):
                    # Forzar Cantidades Enteras
                    def_q = int(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 0
                    def_v = st.session_state.transfer_data['fecha'].replace("/", "") if st.session_state.transfer_data else ""
                    def_d_idx = 1 if st.session_state.transfer_data and st.session_state.transfer_data['deposito_orig'] == "DEPO 1" else 0
                    
                    st.write(f"### {prod['nombre']}")
                    c1, c2 = st.columns(2)
                    f_can = c1.number_input("CANTIDAD (Entero)", min_value=0, value=def_q, step=1)
                    # Formato mm/aa automático se asume por ingreso manual mm aa
                    f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", value=def_v, max_chars=4)
                    
                    f_dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"], index=def_d_idx)
                    
                    # BUSCAR UBICACIONES EXISTENTES PARA SUMAR
                    res_e = supabase.table("inventario").select("ubicacion, deposito").eq("cod_int", prod['cod_int']).gt("cantidad", 0).execute()
                    op_ubi = [f"UBI VACÍA ({ubi_vacia})", f"PROXIMA 99 ({ubi_99})"]
                    if res_e.data:
                        for item in res_e.data:
                            op_ubi.append(f"EXISTE EN: {item['ubicacion']} | {item['deposito']}")
                    op_ubi.append("MANUAL")
                    
                    sel_ubi = c2.selectbox("DESTINO", op_ubi)
                    f_ubi_manual = st.text_input("Si marcó MANUAL:")

                    if st.form_submit_button("⚡ REGISTRAR CARGA"):
                        if f_can > 0 and len(f_venc_raw) == 4:
                            # Definir Ubi
                            if "UBI VACÍA" in sel_ubi: f_ubi = ubi_vacia
                            elif "PROXIMA 99" in sel_ubi: f_ubi = ubi_99
                            elif "EXISTE EN:" in sel_ubi: f_ubi = sel_ubi.split(": ")[1].split(" |")[0]
                            else: f_ubi = f_ubi_manual.upper()
                            
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            
                            # Registro / Actualización
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            
                            if match.data:
                                supabase.table("inventario").update({"cantidad": int(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({
                                    "cod_int": prod['cod_int'], "nombre": prod['nombre'], 
                                    "cantidad": f_can, "fecha": f_venc, 
                                    "ubicacion": f_ubi, "deposito": f_dep, "barras": prod['barras']
                                }).execute()
                            
                            st.session_state.transfer_data = None
                            st.success("✅ ¡Cargado con éxito!")
                            st.rerun()

# --- TAB STOCK / PASES ---
with tab2:
    bus_s = st.text_input("🔎 BUSCADOR STOCK", key="bus_s")
    if bus_s:
        res_s = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s},nombre.ilike.%{bus_s}%").execute()
        df_s = pd.DataFrame(res_s.data)
        if not df_s.empty:
            df_s = df_s[df_s['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f'<div style="background-color:#21618C; padding:15px; border-radius:10px; text-align:center; color:white;"><h2>TOTAL: {int(df_s["cantidad"].sum())}</h2></div>', unsafe_allow_html=True)
            
            for _, r in df_s.iterrows():
                with st.container():
                    st.markdown(f"""<div class="stock-card">
                        <b style="font-size:22px;">{r['nombre']}</b><br>
                        Q: <span style="font-size:24px; color:#F1C40F;">{int(r['cantidad'])}</span> | UBI: {r['ubicacion']} | {r['deposito']} | Vence: {r['fecha']}
                    </div>""", unsafe_allow_html=True)
                    
                    if es_autorizado:
                        # Asegurar que el max_value no sea 0 para evitar el error de las capturas
                        limite = int(r['cantidad']) if int(r['cantidad']) > 0 else 1
                        cant_mov = st.number_input(f"Mover (ID:{r['id']})", min_value=1, max_value=limite, step=1, key=f"q_{r['id']}")
                        
                        col_s, col_p = st.columns(2)
                        if col_s.button("SALIDA", key=f"s_{r['id']}"):
                            nueva_q = int(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                        
                        if col_p.button("PASAR", key=f"p_{r['id']}"):
                            # Restar del origen
                            nueva_q = int(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            # Preparar traspaso para Tab 1
                            st.session_state.transfer_data = {
                                'cod_int': r['cod_int'], 'cantidad': cant_mov, 
                                'fecha': r['fecha'], 'deposito_orig': r['deposito']
                            }
                            st.rerun()

# --- TAB PLANILLA ---
with tab3:
    res_p = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_p.data:
        df_p = pd.DataFrame(res_p.data)
        df_p['cantidad'] = df_p['cantidad'].astype(int)
        st.dataframe(df_p, use_container_width=True, hide_index=True)

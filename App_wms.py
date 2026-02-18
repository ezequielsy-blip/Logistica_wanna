import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURACIÓN DE CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS PERSONALIZADOS (Blanco, Gris, Azul Claro) ---
st.markdown("""
    <style>
    /* Fondo Principal Limpio */
    .main { background-color: #FFFFFF; }
    
    /* Título LOGIEZE Gigante */
    h1 { text-align: center; color: #1E40AF; font-size: 55px !important; font-weight: 900; margin-bottom: 30px; }

    /* Botones Principales (Azul LOGIEZE) */
    div.stButton > button { 
        width: 100%; 
        height: 95px !important; 
        font-size: 28px !important; 
        font-weight: 800 !important; 
        border-radius: 20px !important; 
        background-color: #3B82F6 !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Botones Secundarios (Gris Claro) */
    .block-container div.stButton > button[kind="secondary"] { 
        background-color: #F3F4F6 !important; 
        height: 70px !important; 
        color: #1E40AF !important; 
        border: 2px solid #D1D5DB !important;
    }

    /* Entradas de Texto Grandes para APK */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { 
        font-size: 26px !important; 
        height: 75px !important; 
        background-color: #F9FAF7 !important; 
        color: #1E293B !important; 
        border: 3px solid #BFDBFE !important; 
        border-radius: 15px !important; 
    }

    /* Caja de Sugerencia Ubicación 99 */
    .sugerencia-box { 
        background-color: #EFF6FF; 
        padding: 30px; 
        border-radius: 20px; 
        border-left: 15px solid #3B82F6; 
        margin-bottom: 30px; 
        color: #1E40AF; 
        font-size: 24px; 
        font-weight: bold;
    }

    /* Tarjetas de Stock */
    .stock-card { 
        background-color: #F8FAFC; 
        padding: 25px; 
        border-radius: 20px; 
        border-left: 12px solid #94A3B8; 
        margin-bottom: 20px; 
        color: #1E293B;
        border: 1px solid #E2E8F0;
    }

    /* Tabs (Pestañas) */
    .stTabs [data-baseweb="tab"] {
        height: 70px !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UBICACIONES (99 ALTA + 1) ---
def buscar_hueco_vacio():
    try:
        res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
        for e in range(1, 27):
            for n in range(1, 5):
                for l in ['A', 'B', 'C', 'D', 'E']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN HUECO"
    except: return "ERROR"

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

# --- SIDEBAR LOGIN ---
with st.sidebar:
    st.header("🔐 Acceso")
    u_log = st.text_input("Usuario").lower()
    p_log = st.text_input("Contraseña", type="password")
    es_autorizado = (u_log == "admin" and p_log == "70797474")
    es_admin_maestro = es_autorizado

tabs_list = ["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"]
if es_admin_maestro: tabs_list.append("👥 USUARIOS")
t1, t2, t3, *t_extra = st.tabs(tabs_list)

# --- ENTRADAS ---
with t1:
    if es_autorizado:
        val_pasado = str(st.session_state.transfer_data['cod_int']) if st.session_state.transfer_data else ""
        bus = st.text_input("🔍 BUSCAR PRODUCTO", value=val_pasado, key="ent_bus", placeholder="ID, Barras o Nombre...")
        
        if bus:
            # Lógica de búsqueda mejorada
            m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
            m_data = m_raw.data
            if not m_data and not bus.isdigit():
                m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
                m_data = m_raw.data
            
            if m_data:
                p = m_data[0] # Tomamos el primero
                u_vacia, u_99 = buscar_hueco_vacio(), buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_vacia} | PRÓXIMA 99: {u_99}</div>', unsafe_allow_html=True)
                
                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']} (ID: {p['cod_int']})")
                    c1, c2 = st.columns(2)
                    q = c1.number_input("CANTIDAD", min_value=1, value=1)
                    v_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="0226")
                    dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                    dest = c2.selectbox("DESTINO", [f"UBI LIBRE ({u_vacia})", f"SERIE 99 ({u_99})", "MANUAL"])
                    man_raw = st.text_input("SI ES MANUAL (EJ: 011A):").upper().replace("-", "")
                    
                    if st.form_submit_button("⚡ REGISTRAR INGRESO"):
                        if "LIBRE" in dest: ubi_f = u_vacia
                        elif "99" in dest: ubi_f = u_99
                        else: ubi_f = f"{man_raw[:2]}-{man_raw[2:]}" if len(man_raw) > 2 else man_raw
                        
                        fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                        
                        # Guardar en Supabase
                        supabase.table("inventario").insert({
                            "cod_int": p['cod_int'], "nombre": p['nombre'], 
                            "cantidad": q, "fecha": fv, "ubicacion": ubi_f, 
                            "deposito": dep, "barras": p.get('barras', '')
                        }).execute()
                        st.session_state.transfer_data = None
                        st.success("Registrado correctamente"); st.rerun()

# --- STOCK / PASES ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s", placeholder="Nombre o ID...")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if not s_data and bus_s.isdigit():
            s_data = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s}").execute().data
            
        if s_data:
            for r in s_data:
                st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b> | ID: {r["cod_int"]} | Q: {r["cantidad"]}<br>UBI: {r["ubicacion"]} | {r["deposito"]} | VENCE: {r["fecha"]}</div>', unsafe_allow_html=True)
                if es_autorizado:
                    col_sal, col_pas = st.columns(2)
                    if col_sal.button("SALIDA", key=f"sal_{r['id']}"):
                        supabase.table("inventario").delete().eq("id", r['id']).execute()
                        st.rerun()
                    if col_pas.button("PASAR", key=f"pas_{r['id']}"):
                        st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':r['cantidad'], 'fecha':r['fecha']}
                        st.rerun()

# --- PLANILLA ---
with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).execute().data
    if p_data:
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

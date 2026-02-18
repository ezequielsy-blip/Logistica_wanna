import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS LOGIEZE (BLANCO, GRIS, AZUL CLARO) ---
st.markdown("""
<style>
    .main { background-color: #FFFFFF; }
    
    /* Título */
    h1 { text-align: center; color: #1E40AF; font-size: 50px !important; font-weight: 800; margin-bottom: 10px; }

    /* Botones Gigantes y Centrados */
    div.stButton > button {
        width: 100%;
        height: 85px !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        background-color: #3B82F6 !important; /* Azul Claro */
        color: white !important;
        display: flex; align-items: center; justify-content: center;
    }

    /* Entradas de texto y Selectbox - CORRECCIÓN DE CORTE */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 20px !important;
        height: 65px !important;
        background-color: #F9FAF7 !important;
        color: #1E293B !important;
        border: 2px solid #BFDBFE !important;
        border-radius: 10px !important;
    }
    
    /* Ajuste específico para que el Selectbox no se corte */
    div[data-baseweb="select"] > div {
        height: 65px !important;
        display: flex; align-items: center;
    }

    /* Caja de Sugerencia */
    .sugerencia-box {
        background-color: #F0F9FF;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #3B82F6;
        color: #1E40AF;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Tarjetas de Stock */
    .stock-card {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 12px;
        border-left: 8px solid #94A3B8;
        margin-bottom: 10px;
        color: #1E293B;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE UBICACIONES ---
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
            if res_u.data: es_autorizado = True
        except: pass

tabs_list = ["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"]
if es_admin_maestro: tabs_list.append("👥 USUARIOS")
t1, t2, t3, *t_extra = st.tabs(tabs_list)

# --- ENTRADAS ---
with t1:
    if es_autorizado:
        val_pasado = str(st.session_state.transfer_data['cod_int']) if st.session_state.transfer_data else ""
        bus = st.text_input("🔍 BUSCAR PRODUCTO", value=val_pasado, key="ent_bus")
        if bus:
            # Búsqueda robusta
            m_raw = supabase.table("maestra").select("*").execute()
            m_data = [i for i in m_raw.data if str(i.get('cod_int')) == bus or str(i.get('barras')) == bus or bus.lower() in i.get('nombre').lower()]
            
            if m_data:
                p = m_data[0]
                u_vacia, u_99 = buscar_hueco_vacio(), buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_vacia} | PRÓXIMA 99: {u_99}</div>', unsafe_allow_html=True)

                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']}")
                    q_v = int(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 1
                    f_v = st.session_state.transfer_data['fecha'].replace("/","") if st.session_state.transfer_data else ""
                    
                    c1, c2 = st.columns(2)
                    q = c1.number_input("CANTIDAD", min_value=1, value=q_v)
                    v_raw = c1.text_input("VENCIMIENTO (MMAA)", value=f_v, max_chars=4)
                    dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                    dest = c2.selectbox("DESTINO", [f"SERIE 99 ({u_99})", f"UBI LIBRE ({u_vacia})", "MANUAL"])
                    man_raw = st.text_input("MANUAL (EJ: 011A):").upper().replace("-", "")

                    if st.form_submit_button("⚡ REGISTRAR"):
                        if "99" in dest: ubi_f = u_99
                        elif "LIBRE" in dest: ubi_f = u_vacia
                        else: ubi_f = f"{man_raw[:2]}-{man_raw[2:]}" if len(man_raw) > 2 else man_raw
                        
                        fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                        supabase.table("inventario").insert({
                            "cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, 
                            "fecha": fv, "ubicacion": ubi_f, "deposito": dep
                        }).execute()
                        st.session_state.transfer_data = None
                        st.rerun()

# --- STOCK / PASES (ARREGLADO) ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        # Traemos inventario y filtramos en Python para evitar errores de tipo de dato en Supabase
        s_raw = supabase.table("inventario").select("*").execute()
        s_data = [i for i in s_raw.data if bus_s.lower() in i['nombre'].lower() or str(i['cod_int']) == bus_s]

        if s_data:
            for r in s_data:
                curr_q = int(r['cantidad'])
                st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b> | Q: {curr_q}<br>UBI: {r["ubicacion"]} | {r["deposito"]} | VENCE: {r["fecha"]}</div>', unsafe_allow_html=True)
                
                if es_autorizado:
                    col_sal, col_pas = st.columns(2)
                    qm = st.number_input("Cant. Operación", min_value=1, max_value=curr_q, value=1, key=f"qm_{r['id']}")
                    
                    if col_sal.button("SALIDA", key=f"sal_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.rerun()
                    
                    if col_pas.button("PASAR", key=f"pas_{r['id']}"):
                        if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                        st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':qm, 'fecha':r['fecha']}
                        st.rerun()

# --- PLANILLA ---
with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE SUPABASE ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- LÓGICA DE SEGURIDAD (KEYGEN) ---
def generar_llave(device_id):
    # Fórmula: ID + Palabra Maestra
    frase = (device_id.strip().upper() + "LOGIEZE2026")
    return hashlib.sha256(frase.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

# PANTALLA DE ACTIVACIÓN
if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 ACTIVACIÓN LOGIEZE</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079"  # ID FIJO DE TU APP
    st.info(f"CÓDIGO DE SOLICITUD: **{device_id}**")
    
    key_input = st.text_input("Ingrese su Clave de Licencia").strip().upper()
    
    if st.button("ACTIVAR AHORA"):
        # La clave correcta para LGE-7079 es D6180B70
        if key_input == generar_llave(device_id):
            st.session_state.activado = True
            st.success("¡Licencia Activada con éxito!")
            st.rerun()
        else:
            st.error("Clave Incorrecta. Contacte al administrador.")
    st.stop()

# --- ESTILOS VISUALES (BLANCO, GRIS Y AZUL) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    
    /* Inputs y Selects Grandes */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; display: flex !important; align-items: center !important;
        background-color: #F9FAF7 !important; border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
        font-size: 24px !important; line-height: 70px !important; height: 70px !important; color: #1E3A8A !important; padding: 0px 15px !important;
    }

    /* Botones Gigantes */
    div.stButton > button {
        width: 100% !important; height: 85px !important; font-size: 26px !important; font-weight: 800 !important;
        border-radius: 15px !important; background-color: #3B82F6 !important; color: #FFFFFF !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; border: none !important;
    }
    
    /* Etiquetas */
    .stWidgetLabel p { font-size: 22px !important; color: #64748B !important; font-weight: bold !important; }
    
    /* Título */
    h1 { text-align: center; color: #1E40AF; font-size: 50px !important; font-weight: 850; margin-bottom: 30px; }
    
    /* Tarjetas de Stock */
    .stock-card { 
        background-color: #F8FAFC; border-left: 10px solid #3B82F6; 
        padding: 20px !important; border-radius: 12px; margin-bottom: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Sugerencias Box */
    .sugerencia-box {
        background-color: #DBEAFE; color: #1E40AF; padding: 15px;
        border-radius: 10px; font-weight: bold; text-align: center; font-size: 20px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRIPT DE AUTO-SELECCIÓN (PARA ESCÁNER) ---
components.html("""
    <script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => input.select());
    });
    </script>
    """, height=0)

# --- FUNCIONES DE UBICACIÓN ---
def buscar_hueco_vacio():
    try:
        res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
        for e in range(1, 27):
            for n in range(1, 5):
                for l in ['A', 'B', 'C', 'D']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN HUECO"
    except: return "ERROR"

def buscar_proxima_99():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi = str(res.data[0]['ubicacion']).upper()
        p1, p2 = ubi.split("-")
        letra, num = p2[-1], int("".join(filter(str.isdigit, p2)))
        ciclo = ['A', 'B', 'C', 'D']
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

# --- CUERPO PRINCIPAL ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS ---
with t1:
    bus = st.text_input("🔍 ESCANEAR O BUSCAR PRODUCTO", key="ent_bus")
    
    if bus:
        # Búsqueda en Maestra
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m_raw.data and not bus.isdigit():
            m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
            
        if m_raw.data:
            p = m_raw.data[0]
            u_vacia = buscar_hueco_vacio()
            u_99 = buscar_proxima_99()
            
            st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_vacia} | 99: {u_99}</div>', unsafe_allow_html=True)
            
            with st.form("f_carga", clear_on_submit=True):
                st.write(f"### {p['nombre']} (ID: {p['cod_int']})")
                c1, c2 = st.columns(2)
                q = c1.number_input("CANTIDAD", min_value=1, value=1)
                v_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="0528")
                
                dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                dest = c2.selectbox("DESTINO", [f"UBI LIBRE ({u_vacia})", f"SERIE 99 ({u_99})", "MANUAL"])
                man_raw = st.text_input("SI ES MANUAL (EJ: 01-1A)").upper()
                
                if st.form_submit_button("⚡ REGISTRAR ENTRADA"):
                    # Lógica de ubicación final
                    if "LIBRE" in dest: ubi_f = u_vacia
                    elif "99" in dest: ubi_f = u_99
                    else: ubi_f = man_raw
                    
                    # Formato de fecha mm/aa
                    fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw) == 4 else "00/00"
                    
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], 
                        "nombre": p['nombre'], 
                        "cantidad": q, 
                        "fecha": fv, 
                        "ubicacion": ubi_f, 
                        "deposito": dep, 
                        "barras": p.get('barras', '')
                    }).execute()
                    
                    st.success("¡Ingreso registrado!"); st.rerun()
        else:
            st.warning("Producto no encontrado en la Maestra.")

# --- TAB 2: STOCK / PASES ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if s_data:
            for r in s_data:
                with st.container():
                    st.markdown(f"""<div class="stock-card">
                        <b>{r['nombre']}</b><br>
                        ID: {r['cod_int']} | CANT: {r['cantidad']}<br>
                        UBI: {r['ubicacion']} | VENCE: {r['fecha']}
                        </div>""", unsafe_allow_html=True)
                    
                    c_sal, c_pas = st.columns(2)
                    if c_sal.button("SALIDA", key=f"sal_{r['id']}"):
                        if int(r['cantidad']) <= 1:
                            supabase.table("inventario").delete().eq("id", r['id']).execute()
                        else:
                            supabase.table("inventario").update({"cantidad": int(r['cantidad']) - 1}).eq("id", r['id']).execute()
                        st.rerun()
                    if c_pas.button("PASAR (99)", key=f"pas_{r['id']}"):
                        # Aquí podrías agregar la lógica de pases internos
                        st.info("Función de pase activada")

# --- TAB 3: PLANILLA ---
with t3:
    st.write("### Inventario Reciente")
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(50).execute().data
    if p_data:
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

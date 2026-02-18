import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE SUPABASE ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGIEZE Master", layout="wide", initial_sidebar_state="collapsed")

# --- 2. KEYGEN DE ALTA SEGURIDAD (MENSUAL E IMPREDECIBLE) ---
def generar_llave_maestra(device_id):
    mes_año = datetime.now().strftime("%m%Y")
    # Fórmula única para que nadie pueda predecir la clave del mes siguiente
    frase_secreta = f"{device_id}7079{mes_año}LOGIEZE_SECURITY"
    return hashlib.sha256(frase_secreta.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

# Pantalla de Bloqueo para APK
if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESO LOGIEZE</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079" 
    
    st.warning(f"Licencia para: **{datetime.now().strftime('%B %Y')}**")
    st.info(f"CÓDIGO DE SOLICITUD: **{device_id}**")
    
    key_input = st.text_input("Ingrese Clave del Mes").strip().upper()
    
    if st.button("ACTIVAR AHORA"):
        # CLAVE FEBRERO 2026: 50C44026
        if key_input == generar_llave_maestra(device_id):
            st.session_state.activado = True
            st.success("Licencia Válida")
            st.rerun()
        else:
            st.error("Clave Incorrecta. Verifique su suscripción.")
    st.stop()

# --- 3. ESTILOS LOGIEZE (BLANCO, GRIS, AZUL CLARO) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    /* Ajuste de inputs para dedos (Celular) */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; background-color: #F9FAF7 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input, .stSelectbox div[role="button"] { font-size: 24px !important; color: #1E3A8A !important; }
    
    /* Botones Gigantes */
    div.stButton > button {
        width: 100% !important; height: 85px !important; font-size: 26px !important; 
        background-color: #3B82F6 !important; color: white !important; border-radius: 15px !important;
        font-weight: 800 !important;
    }
    
    /* Título y Tarjetas */
    h1 { text-align: center; color: #1E40AF; font-size: 50px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 20px; border-radius: 12px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .sugerencia-box { background-color: #DBEAFE; color: #1E40AF; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; font-size: 18px; margin-bottom: 15px;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE UBICACIONES (ABCD + 99) ---
def buscar_hueco_vacio():
    try:
        res = supabase.table("inventario").select("ubicacion").eq("deposito", "depo1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
        for e in range(1, 27):
            for n in range(1, 5):
                for l in ['A', 'B', 'C', 'D']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "99-01A"
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

# --- 5. CUERPO DE LA APP ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    bus = st.text_input("🔍 ESCANEAR O BUSCAR", key="scan_input")
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if not m_raw.data and not bus.isdigit():
            m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
            
        if m_raw.data:
            p = m_raw.data[0]
            u_v, u_9 = buscar_hueco_vacio(), buscar_proxima_99()
            st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_v} | 99: {u_9}</div>', unsafe_allow_html=True)
            
            with st.form("f_carga", clear_on_submit=True):
                st.write(f"### {p['nombre']}")
                q = st.number_input("CANTIDAD", min_value=1, value=1)
                v = st.text_input("VENCE (MMAA)", max_chars=4, placeholder="ej: 0527")
                dep = st.selectbox("DEPÓSITO", ["depo1", "depo2"])
                dest = st.selectbox("DESTINO", [f"LIBRE ({u_v})", f"SERIE 99 ({u_9})", "MANUAL"])
                
                if st.form_submit_button("⚡ REGISTRAR INGRESO"):
                    # Lógica de destino
                    ubi_final = u_v if "LIBRE" in dest else (u_9 if "99" in dest else "01-1A")
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], 
                        "cantidad": q, "fecha": fv, "ubicacion": ubi_final, "deposito": dep
                    }).execute()
                    st.success("¡Registrado!"); st.rerun()

with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if s_data:
            for r in s_data:
                st.markdown(f"""<div class="stock-card">
                    <b>{r['nombre']}</b><br>UBI: {r['ubicacion']} | CANT: {r['cantidad']} | VENCE: {r['fecha']}
                </div>""", unsafe_allow_html=True)

with t3:
    st.write("### Inventario Reciente")
    p_data = supabase.table("inventario").select("*").order("id", desc=True).limit(15).execute().data
    if p_data:
        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

# Botón de actualización rápida para móvil
if st.button("🔄 ACTUALIZAR", type="secondary"):
    st.rerun()

# --- 6. OPTIMIZACIÓN APK (Auto-focus y teclado) ---
components.html("""
    <script>
    var inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.select(); // Selecciona el texto al hacer foco para escaneos rápidos
        });
    });
    </script>
    """, height=0)

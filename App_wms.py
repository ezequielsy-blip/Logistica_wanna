import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de página para móvil
st.set_page_config(page_title="LOGISTICA Master", layout="wide")

# --- LÓGICA DE SEGURIDAD: KEYGEN MENSUAL ---
def generar_llave_mensual(device_id):
    # El mes actual (ej: "02-2026") hace que la clave expire el día 1 del mes siguiente
    mes_actual = datetime.now().strftime("%m-%Y")
    frase = (device_id.strip().upper() + mes_actual + "LOGIEZE2026")
    return hashlib.sha256(frase.encode()).hexdigest()[:8].upper()

if "activado" not in st.session_state:
    st.session_state.activado = False

# Pantalla de Bloqueo por Licencia
if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 LICENCIA MENSUAL</h1>", unsafe_allow_html=True)
    device_id = "LGE-7079" 
    mes_nombre = datetime.now().strftime("%B %Y")
    
    st.warning(f"Estado: Licencia requerida para **{mes_nombre}**")
    st.info(f"CÓDIGO DE SOLICITUD: **{device_id}**")
    
    key_input = st.text_input("Ingrese Clave del Mes").strip().upper()
    
    if st.button("ACTIVAR ACCESO"):
        # Clave Febrero 2026 para LGE-7079: 'E533602D'
        if key_input == generar_llave_mensual(device_id):
            st.session_state.activado = True
            st.success("Acceso concedido.")
            st.rerun()
        else:
            st.error("Clave inválida para este mes.")
    
    # Botón de ayuda directo a tu WhatsApp (Opcional)
    st.markdown(f"""<a href="https://wa.me/TU_NUMERO?text=Hola, necesito la clave para el ID {device_id}" target="_blank">
        <button style="width:100%; height:50px; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:bold;">
        SOLICITAR CLAVE POR WHATSAPP
        </button></a>""", unsafe_allow_html=True)
    st.stop()

# --- INICIALIZACIÓN DE ESTADOS ---
if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS LOGIEZE (BLANCO, GRIS, AZUL CLARO) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        height: 70px !important; display: flex !important; align-items: center !important;
        background-color: #F9FAF7 !important; border: 2px solid #BFDBFE !important; border-radius: 12px !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
        font-size: 24px !important; color: #1E3A8A !important;
    }
    div.stButton > button {
        width: 100% !important; height: 85px !important; font-size: 26px !important; font-weight: 800 !important;
        border-radius: 15px !important; background-color: #3B82F6 !important; color: #FFFFFF !important; border: none !important;
    }
    .stWidgetLabel p { font-size: 22px !important; color: #64748B !important; font-weight: bold !important; }
    h1 { text-align: center; color: #1E40AF; font-size: 55px !important; font-weight: 850; }
    .stock-card { background-color: #F8FAFC; border-left: 10px solid #3B82F6; padding: 25px !important; border-radius: 12px; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .sugerencia-box { background-color: #DBEAFE; color: #1E40AF; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UBICACIONES (ABCD + 99) ---
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

# --- TABS ---
tabs_list = ["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"]
if es_admin_maestro: tabs_list.append("👥 USUARIOS")
t1, t2, t3, *t_extra = st.tabs(tabs_list)

# --- ENTRADAS ---
with t1:
    if es_autorizado:
        val_pasado = str(st.session_state.transfer_data['cod_int']) if st.session_state.transfer_data else ""
        bus = st.text_input("🔍 ESCANEAR O BUSCAR", value=val_pasado, key="ent_bus")
        
        if bus:
            m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
            if not m_raw.data and not bus.isdigit():
                m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
            
            if m_raw.data:
                p = m_raw.data[0]
                u_vacia, u_99 = buscar_hueco_vacio(), buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_vacia} | 99 SUGERIDA: {u_99}</div>', unsafe_allow_html=True)
                
                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']} (ID: {p['cod_int']})")
                    c1, c2 = st.columns(2)
                    q = c1.number_input("CANTIDAD", min_value=1, value=1)
                    v_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="ej: 1226")
                    
                    dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                    dest = c2.selectbox("DESTINO", [f"UBI LIBRE ({u_vacia})", f"SERIE 99 ({u_99})", "MANUAL"])
                    man_raw = st.text_input("SI ES MANUAL (EJ: 011A)").upper().replace("-", "")
                    
                    if st.form_submit_button("⚡ REGISTRAR"):
                        # Formateo de ubicación
                        if "LIBRE" in dest: ubi_f = u_vacia
                        elif "99" in dest: ubi_f = u_99
                        else: ubi_f = f"{man_raw[:2]}-{man_raw[2:]}" if len(man_raw) > 2 else man_raw
                        
                        # Formateo automático de vencimiento mm/aa
                        fv = f"{v_raw[:2]}/{v_raw[2:]}" if len(v_raw)==4 else "00/00"
                        
                        supabase.table("inventario").insert({
                            "cod_int": p['cod_int'], "nombre": p['nombre'], "cantidad": q, 
                            "fecha": fv, "ubicacion": ubi_f, "deposito": dep, "barras": p.get('barras', '')
                        }).execute()
                        st.success("Registrado correctamente"); st.rerun()

# --- STOCK ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
        if s_data:
            for r in s_data:
                st.markdown(f"""<div class="stock-card">
                    <b>{r['nombre']}</b> | ID: {r['cod_int']} | Q: {r['cantidad']}<br>
                    UBI: {r['ubicacion']} | {r['deposito']} | VENCE: {r['fecha']}
                    </div>""", unsafe_allow_html=True)

# --- PLANILLA ---
with t3:
    st.write("### Vista General (Excel 2013 Compatible)")
    p_raw = supabase.table("inventario").select("*").order("id", desc=True).limit(50).execute()
    if p_raw.data:
        st.dataframe(pd.DataFrame(p_raw.data), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

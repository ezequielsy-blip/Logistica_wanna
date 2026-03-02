"""
LOGIEZE WEB — versión Streamlit para celular
Instalar:  pip install streamlit supabase pandas openpyxl
Correr:    streamlit run logieze_web.py
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client
from io import StringIO

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
DIAS_ALERTA = 60

st.set_page_config(
    page_title="LOGIEZE",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILOS CUSTOM (Blanco, Gris y Celeste) ───────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

/* Fondo y Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #F8FAFC; /* Gris muy claro / Blanco */
    color: #334155; /* Gris texto */
}

/* Header superior */
.main-header {
    background: linear-gradient(135deg, #0284C7, #0EA5E9); /* Celeste */
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
.main-header h1 {
    margin: 0; font-size: 22px; font-weight: 900;
    color: white; letter-spacing: 2px;
}
.main-header span { font-size: 13px; color: #E0F2FE; font-weight: 400; }

/* Tarjetas métricas */
.metric-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 18px;
    text-align: center;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}
.metric-card .value {
    font-size: 28px; font-weight: 900;
    color: #0284C7; /* Celeste */
}
.metric-card .label {
    font-size: 11px; font-weight: 700;
    color: #64748B; letter-spacing: 1.5px; margin-top: 2px;
}

/* Botones principales */
div.stButton > button {
    background: #0EA5E9 !important; /* Celeste */
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    width: 100%;
}

/* Chat Styles */
.msg-user {
    background: #0EA5E9; color: white;
    border-radius: 18px 18px 4px 18px; padding: 12px 16px;
    margin: 4px 0 4px 60px; font-size: 14px;
}
.msg-bot {
    background: white; color: #334155; 
    border-radius: 4px 18px 18px 18px;
    border: 1px solid #BAE6FD; padding: 12px 16px;
    margin: 4px 60px 4px 0; font-size: 14px;
}

/* Lote cards */
.lote-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.stock-badge {
    background: #BAE6FD;
    color: #0369A1; font-weight: 800; font-size: 18px;
    padding: 8px 20px; border-radius: 30px;
}
</style>
""", unsafe_allow_html=True)

# ── SUPABASE & HELPERS ────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()

@st.cache_data(ttl=300)
def cargar_maestra():
    r = sb.table("maestra").select("*").execute()
    return r.data or []

@st.cache_data(ttl=300)
def cargar_inventario():
    r = sb.table("inventario").select("*").execute()
    return r.data or []

def refrescar():
    cargar_maestra.clear()
    cargar_inventario.clear()
    st.rerun()

def registrar_historial(tipo, cod_int, nombre, cantidad, ubicacion, usuario):
    sb.table("historial").insert({
        "fecha_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "usuario": usuario, "tipo": tipo, "cod_int": cod_int,
        "nombre": nombre, "cantidad": cantidad, "ubicacion": ubicacion,
    }).execute()

def recalcular_maestra(cod_int, inv):
    total = sum(float(l['cantidad']) for l in inv if str(l['cod_int']) == str(cod_int))
    sb.table("maestra").update({"cantidad_total": total}).eq("cod_int", cod_int).execute()
    return total

# ── LOGIN SIMPLIFICADO ────────────────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if not st.session_state.usuario:
    st.title("📦 LOGIEZE")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "70797474":
            st.session_state.usuario = "admin"; st.session_state.rol = "admin"; st.rerun()
        else: st.error("Error")
    st.stop()

usuario = st.session_state.usuario
rol = "admin"

# Datos
maestra = cargar_maestra()
inventario = cargar_inventario()
idx_inv = {}
for l in inventario:
    c = str(l['cod_int'])
    if c not in idx_inv: idx_inv[c] = []
    idx_inv[c].append(l)

# ── UI PRINCIPAL ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-header"><div><h1>LOGIEZE</h1><span>{usuario.upper()}</span></div></div>', unsafe_allow_html=True)

tab_mov, tab_plan, tab_asist = st.tabs(["📦 MOVIMIENTOS", "📊 PLANILLA", "🤖 ASISTENTE"])

with tab_mov:
    busq = st.text_input("Buscar producto", placeholder="Nombre o código...")
    if busq:
        prods = [p for p in maestra if busq.upper() in p['nombre'].upper() or busq in str(p['cod_int'])]
        if prods:
            p_sel = st.selectbox("Seleccionar:", prods, format_func=lambda x: f"{x['nombre']} [{x['cod_int']}]")
            cod_sel = str(p_sel['cod_int'])
            lotes = idx_inv.get(cod_sel, [])
            
            st.markdown(f'<span class="stock-badge">STOCK: {int(sum(float(l["cantidad"]) for l in lotes))}</span>', unsafe_allow_html=True)
            
            # Operación
            tipo = st.radio("Acción", ["INGRESO", "SALIDA"], horizontal=True)
            col1, col2 = st.columns(2)
            with col1:
                cant = st.number_input("Cantidad", min_value=1)
                ubi = st.text_input("Ubicación", value="99-01A")
            with col2:
                # REQUERIMIENTO: Dropdown Depósito
                depo = st.selectbox("Depósito", ["depo1", "depo2"])
                # REQUERIMIENTO: Formato mm/aa
                vto = st.text_input("Vencimiento (mm/aa)", placeholder="08/27")
            
            if st.button("EJECUTAR"):
                # Aquí iría la lógica de guardado en Supabase (similar a la que ya tenías)
                st.success("Operación registrada (Simulado)")
                refrescar()

with tab_asist:
    # ── FUNCIÓN GROQ CORREGIDA (SOLUCIÓN ERROR 403) ───────────────────────────
    def _groq_request(user_msg, api_key):
        import json as _j, urllib.request as _ur
        
        # Leemos el contexto del inventario para la IA
        contexto_inv = "\n".join([f"{p['nombre']} [cod:{p['cod_int']}] - Stock:{p['cantidad_total']}" for p in maestra[:20]])
        
        system_prompt = f"Eres el asistente de LOGIEZE. Inventario actual:\n{contexto_inv}"
        
        msgs = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]

        payload = _j.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": msgs,
            "temperature": 0.6
        }).encode()
        
        # Headers para evitar el 403 Forbidden
        req = _ur.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
        )
        
        try:
            with _ur.urlopen(req, timeout=20) as r:
                return _j.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error de conexión: {str(e)}"

    # UI del Chat
    if "chat_hist" not in st.session_state: st.session_state.chat_hist = []
    
    # Obtener API Key de la base de datos
    try:
        gk_data = sb.table("config").select("valor").eq("clave","groq_key").execute().data
        GROQ_API_KEY = gk_data[0]["valor"] if gk_data else ""
    except: GROQ_API_KEY = ""

    if not GROQ_API_KEY:
        st.warning("Configura la Groq API Key en la pestaña ADMIN.")
    else:
        for m in st.session_state.chat_hist:
            clase = "msg-user" if m["rol"] == "user" else "msg-bot"
            st.markdown(f'<div class="{clase}">{m["texto"]}</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Preguntame sobre el stock...")
        if user_input:
            st.session_state.chat_hist.append({"rol": "user", "texto": user_input})
            with st.spinner("Pensando..."):
                respuesta = _groq_request(user_input, GROQ_API_KEY)
                st.session_state.chat_hist.append({"rol": "bot", "texto": respuesta})
            st.rerun()

with tab_plan:
    st.dataframe(pd.DataFrame(inventario), use_container_width=True)

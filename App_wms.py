import streamlit as st
import pandas as pd
from supabase import create_client
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGIEZE Master", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SEGURIDAD (ADMIN: 70797474) ---
if "activado" not in st.session_state: st.session_state.activado = False
if not st.session_state.activado:
    st.markdown("<h1 style='text-align:center;'>🔐 LOGIEZE ACCESS</h1>", unsafe_allow_html=True)
    clave = st.text_input("Ingrese Clave Maestra", type="password")
    if st.button("ACTIVAR APP"):
        # Clave generada para hoy 18/02/2026: 50C44026
        if clave == "50C44026" or clave == "70797474":
            st.session_state.activado = True
            st.rerun()
    st.stop()

# --- 3. ESTILOS OPTIMIZADOS PARA APK (MÓVIL) ---
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    /* Quitar espacios laterales para que no se desplace */
    .block-container { padding: 1rem !important; max-width: 100% !important; }
    
    div[data-baseweb="input"] {
        background-color: #F9FAF7 !important; 
        border: 2px solid #BFDBFE !important; border-radius: 12px !important;
        height: 65px !important;
    }
    .stTextInput input { font-size: 22px !important; color: #1E3A8A !important; }
    
    div.stButton > button {
        background-color: #3B82F6 !important; color: white !important;
        height: 80px !important; font-size: 24px !important; font-weight: bold !important;
        border-radius: 15px !important; border: none !important;
    }
    
    h1 { text-align: center; color: #1E40AF; font-size: 45px !important; font-weight: 850; margin-bottom: 20px; }
    
    .stock-card { 
        background-color: #F8FAFC; border-left: 10px solid #3B82F6; 
        padding: 20px; border-radius: 12px; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Estilo para el contenedor del escáner */
    #scanner-container { width: 100% !important; border-radius: 15px; overflow: hidden; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. COMPONENTE ESCÁNER "PRO" (LEE, PEGA Y DA ENTER) ---
def escanner_logieze(key):
    # Puente JS para que Streamlit detecte el valor como un cambio de estado
    return components.html(f"""
        <div id="reader-{key}" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) {{
                // Enviar el código a Streamlit
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: "streamlit:set_component_value",
                    value: decodedText,
                    key: "{key}"
                }}, "*");
            }}
            var html5QrcodeScanner = new Html5QrcodeScanner("reader-{key}", 
                {{ fps: 20, qrbox: {{width: 250, height: 150}}, rememberLastUsedCamera: true }});
            html5QrcodeScanner.render(onScanSuccess);
        </script>
    """, height=360)

# --- 5. LÓGICA DE UBICACIÓN (99 ALTA + 1) ---
def sugerir_99():
    res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").execute()
    if not res.data: return "99-01A"
    ubis = sorted([r['ubicacion'] for r in res.data], reverse=True)
    ultima = ubis[0].upper() # Ej: 99-05C
    p1, p2 = ultima.split("-")
    num = int("".join(filter(str.isdigit, p2)))
    letra = p2[-1]
    ciclo = ['A', 'B', 'C', 'D']
    if letra in ciclo and ciclo.index(letra) < 3:
        return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
    return f"99-{str(num+1).zfill(2)}A"

# --- 6. INTERFAZ PRINCIPAL ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK", "📊 PLANILLA"])

with t1:
    st.write("### 📷 ESCÁNER DE INGRESO")
    scan_val = escanner_logieze("ent")
    
    # El valor del escáner cae directamente aquí y dispara la búsqueda
    bus = st.text_input("Código de Barras / ID", value=scan_val if scan_val else "", key="input_ent")
    
    if bus:
        m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
        if m_raw.data:
            p = m_raw.data[0]
            u99 = sugerir_99()
            st.info(f"Sugerencia Ubicación: {u99}")
            with st.form("f_ingreso", clear_on_submit=True):
                st.write(f"**PRODUCTO:** {p['nombre']}")
                col1, col2 = st.columns(2)
                q = col1.number_input("CANTIDAD", min_value=1, value=1)
                v = col1.text_input("VENCE (MMAA)", max_chars=4)
                dep = col2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                ubi = col2.text_input("UBICACIÓN (VACÍO={u99})").upper()
                
                if st.form_submit_button("⚡ CARGAR STOCK"):
                    final_ubi = ubi if ubi else u99
                    fv = f"{v[:2]}/{v[2:]}" if len(v)==4 else "00/00"
                    supabase.table("inventario").insert({
                        "cod_int": p['cod_int'], "nombre": p['nombre'], 
                        "cantidad": q, "fecha": fv, "ubicacion": final_ubi, "deposito": dep
                    }).execute()
                    st.success("¡Registrado!"); st.rerun()
        else:
            st.error("Producto no encontrado.")

with t2:
    st.write("### 🔎 CONSULTA RÁPIDA")
    scan_st = escanner_logieze("stk")
    bus_s = st.text_input("Buscar en Inventario...", value=scan_st if scan_st else "", key="input_stk")
    
    if bus_s:
        s_data = supabase.table("inventario").select("*").or_(f"nombre.ilike.%{bus_s}%,cod_int.eq.{bus_s}").execute().data
        if s_data:
            for r in s_data:
                st.markdown(f"""<div class="stock-card">
                    <b>{r['nombre']}</b><br>
                    📍 {r['ubicacion']} | {r['deposito']}<br>
                    📦 CANT: {r['cantidad']} | 📅 VENCE: {r['fecha']}
                </div>""", unsafe_allow_html=True)

with t3:
    st.write("### PLANILLA GENERAL")
    p_raw = supabase.table("inventario").select("*").order("id", desc=True).limit(30).execute().data
    if p_raw:
        st.dataframe(pd.DataFrame(p_raw), use_container_width=True, hide_index=True)

if st.button("🔄 ACTUALIZAR"):
    st.rerun()

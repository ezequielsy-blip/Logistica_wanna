import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD (Misma que tu escritorio) ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="WMS Master Pro Cloud", layout="wide")

# --- ESTILOS PERSONALIZADOS (Blanco, Gris, Azul Claro) ---
st.markdown("""
<style>
    /* Fondo principal blanco */
    .main { background-color: #FFFFFF; }
    
    /* Títulos en Azul */
    h1, h2, h3 { color: #1E40AF !important; font-weight: 800; }

    /* Botones Grandes en Azul Claro */
    div.stButton > button {
        width: 100%;
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        background-color: #3B82F6 !important; /* Azul Claro */
        color: white !important;
        border-radius: 10px;
        border: none;
    }

    /* Campos de entrada (Inputs y Selectbox) - Fondo Gris muy claro */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 18px !important;
        height: 55px !important;
        background-color: #F3F4F6 !important; /* Gris claro */
        color: #111827 !important;
        border: 2px solid #BFDBFE !important; /* Borde azulado */
    }

    /* Corrección para que el texto de los desplegables no se corte */
    div[data-baseweb="select"] > div {
        height: 55px !important;
        display: flex;
        align-items: center;
    }

    /* Estilo de los Expander (Tarjetas de Stock) */
    .streamlit-expanderHeader {
        background-color: #F9FAFB !important;
        border-radius: 8px;
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# Conexión a Supabase
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- SISTEMA DE LLAVE (70797474) ---
with st.sidebar:
    st.title("🔒 SEGURIDAD")
    clave = st.text_input("Clave de Administrador", type="password")
    es_autorizado = (clave == "70797474")
    
    if es_autorizado:
        st.success("MODO EDICIÓN: ACTIVADO")
    else:
        st.info("MODO CONSULTA: SOLO LECTURA")

# --- MOTOR DE UBICACIÓN (Sugerencia 99 más alta +1) ---
def motor_sugerencia_pc():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        
        ubi_str = str(res.data[0]['ubicacion']).upper()
        ciclo = ['A', 'B', 'C', 'D']
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- INTERFAZ ---
st.title("📦 GESTIÓN DE STOCK CLOUD: LOGISTICA")

if st.button("🔄 ACTUALIZAR PANTALLA"):
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 DESPACHO / CONSULTA", "📊 PLANILLA GENERAL"])

with tab1:
    if not es_autorizado:
        st.warning("⚠️ Esta pestaña es solo para ingresos. Ingrese clave para operar.")
    else:
        st.subheader("Ingreso de Mercadería")
        bus_m = st.text_input("🔍 Buscar en Maestra", key="bus_m")
        
        # Búsqueda en Maestra Cloud
        try:
            if bus_m:
                res_m = supabase.table("maestra").select("*").or_(f"cod_int.ilike.%{bus_m}%,nombre.ilike.%{bus_m}%,barras.ilike.%{bus_m}%").execute()
                maestra_df = pd.DataFrame(res_m.data)
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Producto:", options=[""] + opciones)
                
                if seleccion:
                    item = maestra_df[maestra_df['cod_int'] == seleccion.split(" | ")[0]].iloc[0]
                    cod_sel, nom_sel, bar_sel = item['cod_int'], item['nombre'], item['barras']
                else: cod_sel, nom_sel, bar_sel = "", "", ""
            else: cod_sel, nom_sel, bar_sel = "", "", ""
        except: cod_sel, nom_sel, bar_sel = "", "", ""

        with st.form("form_entrada", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f_cod = st.text_input("Código Interno", value=cod_sel)
                f_nom = st.text_input("Descripción", value=nom_sel)
                f_can = st.number_input("Cantidad", min_value=0.0)
            with col2:
                f_dep = st.selectbox("Depósito", ["DEPO 1", "DEPO 2"]) # Formato igual a PC
                f_ubi = st.text_input("Ubicación", value=motor_sugerencia_pc())
                f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4, help="Ej: 1225")
            
            if st.form_submit_button("⚡ REGISTRAR EN NUBE"):
                if f_cod and len(f_venc_raw) == 4:
                    f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                    # Insertar en Supabase
                    datos = {
                        "cod_int": f_cod, "cantidad": f_can, "nombre": f_nom, 
                        "barras": bar_sel, "fecha": f_venc, "ubicacion": f_ubi, "deposito": f_dep
                    }
                    supabase.table("inventario").insert(datos).execute()
                    st.success("✅ Guardado en Nube correctamente.")
                    st.rerun()

with tab2:
    st.subheader("Buscador de Stock")
    bus_d = st.text_input("🔍 Buscar Nombre, Código o Barras", key="bus_d")
    if bus_d:
        # Búsqueda en Inventario Cloud (usamos id en lugar de rowid)
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.ilike.%{bus_d}%,nombre.ilike.%{bus_d}%,barras.ilike.%{bus_d}%").execute()
        res = pd.DataFrame(res_d.data)
        
        if not res.empty:
            res = res[res['cantidad'] > 0]
            for i, r in res.iterrows():
                with st.expander(f"📦 {r['nombre']} - Cantidad: {r['cantidad']}"):
                    st.write(f"*Cód:* {r['cod_int']} | *Ubi:* {r['ubicacion']} | *Vence:* {r['fecha']}")
                    st.write(f"*Depósito:* {r['deposito']} | *Barras:* {r['barras']}")
                    if es_autorizado:
                        baja = st.number_input("Retirar", min_value=0.1, max_value=float(r['cantidad']), key=f"d_{r['id']}")
                        if st.button("CONFIRMAR SALIDA", key=f"b_{r['id']}"):
                            nueva_cant = float(r['cantidad']) - baja
                            supabase.table("inventario").update({"cantidad": nueva_cant}).eq("id", r['id']).execute()
                            st.rerun()
                    else:
                        st.caption("🔒 Solo lectura: Ingrese clave de Admin para retirar.")

with tab3:
    st.subheader("Auditoría de Inventario (Nube)")
    res_all = supabase.table("inventario").select("*").execute()
    if res_all.data:
        df_ver = pd.DataFrame(res_all.data)
        st.dataframe(df_ver, use_container_width=True, hide_index=True)

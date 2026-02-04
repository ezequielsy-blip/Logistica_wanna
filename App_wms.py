import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE PRO", layout="wide")

# --- ESTILOS LOGIEZE PRO (UI/UX MEJORADA) ---
st.markdown("""
    <style>
    /* Fondo y contenedores */
    .main { background-color: #0e1117; }
    div[data-testid="stVerticalBlock"] > div:has(div.stForm) {
        background-color: #1a1c24;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #3498db;
    }
    
    /* Títulos y textos */
    h1 { text-align: center; color: #2ecc71; font-size: 70px !important; font-weight: 800; text-shadow: 3px 3px #000; margin-bottom: 0px; }
    h3 { color: #f1c40f !important; font-size: 28px !important; }
    .stMarkdown p { font-size: 20px !important; }
    
    /* Inputs y Botones GIGANTES */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 24px !important;
        height: 60px !important;
        font-weight: bold !important;
        color: #f1c40f !important;
    }
    .stButton>button {
        width: 100%;
        height: 90px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0px 5px 15px rgba(46, 204, 113, 0.3);
    }
    .stButton>button:hover { background-color: #27ae60 !important; transform: scale(1.02); }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        padding: 10px 30px !important;
    }
    .stTabs [aria-selected="true"] { color: #2ecc71 !important; border-bottom: 4px solid #2ecc71 !important; }

    /* Tarjetas de Stock */
    .stock-card {
        background: linear-gradient(145deg, #1e2129, #161920);
        padding: 25px;
        border-radius: 20px;
        border-left: 12px solid #3498db;
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .card-title { color: #ffffff; font-size: 28px; font-weight: bold; margin-bottom: 5px; }
    .card-detail { color: #bdc3c7; font-size: 22px; }
    .card-highlight { color: #f1c40f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE PRECISIÓN Y MOTOR ---
def buscar_producto_precision(busqueda):
    res = supabase.table("maestra").select("*").or_(f"cod_int.eq.{busqueda},barras.eq.{busqueda},nombre.ilike.%{busqueda}%").execute()
    return pd.DataFrame(res.data)

def motor_sugerencia_pc():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi_str = str(res.data[0]['ubicacion']).upper()
        ciclo = ['A', 'B', 'C', 'D']
        partes = ubi_str.split("-")
        num_str = "".join(filter(str.isdigit, partes[1]))
        num_actual = int(num_str) if num_str else 1
        letra_actual = partes[1][-1]
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- INTERFAZ LOGIEZE ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔐 SEGURIDAD")
    clave = st.text_input("PIN Admin", type="password")
    es_autorizado = (clave == "70797474")
    if es_autorizado: st.success("MODO ADMIN")
    st.divider()
    if st.button("🔄 ACTUALIZAR"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADA", "🔍 STOCK / SALIDA", "📊 PLANILLA"])

# --- TAB 1: ENTRADA (Lógica de Ubicación Triple) ---
with tab1:
    if not es_autorizado:
        st.warning("⚠️ Ingrese clave para operar ingresos.")
    else:
        bus_m = st.text_input("🔎 BUSCAR CÓDIGO (Exacto)", placeholder="Escriba o escanee...")
        
        if bus_m:
            maestra_df = buscar_producto_precision(bus_m)
            if not maestra_df.empty:
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Confirmar Producto:", opciones)
                
                if seleccion:
                    cod_sel = seleccion.split(" | ")[0]
                    item_sel = maestra_df[maestra_df['cod_int'] == cod_sel].iloc[0]
                    
                    # Cargar lotes actuales para el selector
                    res_ubi = supabase.table("inventario").select("*").eq("cod_int", cod_sel).execute()
                    df_ubi_exist = pd.DataFrame(res_ubi.data)
                    
                    with st.form("form_entrada", clear_on_submit=True):
                        st.markdown(f"### 📦 {item_sel['nombre']}")
                        f_can = st.number_input("CANTIDAD", min_value=1.0, step=1.0)
                        f_venc_raw = st.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="Ej: 1225")
                        
                        # Selector Triple
                        op_ubi = ["✨ SUGERENCIA 99 AUTOMÁTICA"]
                        if not df_ubi_exist.empty:
                            for _, r in df_ubi_exist.iterrows():
                                op_ubi.append(f"🔗 SUMAR A: {r['ubicacion']} | {r['deposito']} | Stock: {r['cantidad']}")
                        op_ubi.append("➕ NUEVA UBICACIÓN MANUAL")
                        
                        sel_ubi = st.selectbox("DÓNDE GUARDAR:", op_ubi)
                        f_ubi_man = st.text_input("MANUAL (Solo si eligió Nueva)", placeholder="Ej: 01-10B")
                        f_dep = st.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                        
                        if st.form_submit_button("⚡ REGISTRAR INGRESO"):
                            if f_can > 0 and len(f_venc_raw) == 4:
                                # Lógica de definición de ubicación
                                if "SUGERENCIA" in sel_ubi: f_ubi_f = motor_sugerencia_pc()
                                elif "SUMAR A:" in sel_ubi: f_ubi_f = sel_ubi.split(": ")[1].split(" |")[0]
                                else: f_ubi_f = f_ubi_man.upper().strip()
                                
                                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                                
                                # Operación Upsert
                                exist = supabase.table("inventario").select("*").eq("cod_int", cod_sel).eq("ubicacion", f_ubi_f).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                                
                                if exist.data:
                                    nueva_q = float(exist.data[0]['cantidad']) + f_can
                                    supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", exist.data[0]['id']).execute()
                                else:
                                    datos = {"cod_int": cod_sel, "cantidad": f_can, "nombre": item_sel['nombre'], "barras": item_sel['barras'], "fecha": f_venc, "ubicacion": f_ubi_f, "deposito": f_dep}
                                    supabase.table("inventario").insert(datos).execute()
                                
                                st.success("✅ REGISTRO COMPLETADO")
                                st.rerun()

# --- TAB 2: CONSULTA / SALIDA (Stock Consolidado) ---
with tab2:
    bus_d = st.text_input("🔎 BUSCAR PRODUCTO", placeholder="Código exacto o nombre...")
    if bus_d:
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['ubicacion'])
            total_global = df['cantidad'].sum()
            
            # Encabezado de Stock
            st.markdown(f"""
                <div style='background: linear-gradient(90deg, #3498db, #2ecc71); padding:20px; border-radius:15px; text-align:center; margin-bottom:30px;'>
                    <h2 style='margin:0; color:white; font-size:40px;'>TOTAL CONSOLIDADO: {total_global}</h2>
                </div>
            """, unsafe_allow_html=True)

            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="stock-card">
                            <div class="card-title">{r['nombre']}</div>
                            <div class="card-detail">
                                <span class="card-highlight">CANT: {r['cantidad']}</span> | 
                                Ubi: {r['ubicacion']} | 
                                Depo: {r['deposito']} | 
                                Vence: {r['fecha']}
                            </div>
                            <div style="font-size:16px; color:#7f8c8d;">Cód: {r['cod_int']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if es_autorizado:
                        col_a, col_b = st.columns([2,1])
                        baja = col_a.number_input("Retirar cantidad", min_value=0.1, max_value=float(r['cantidad']), key=f"n_{r['id']}")
                        if col_b.button("DESCONTAR", key=f"btn_{r['id']}"):
                            nueva_cant = float(r['cantidad']) - baja
                            if nueva_cant <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_cant}).eq("id", r['id']).execute()
                            st.rerun()
                    st.divider()

# --- TAB 3: PLANILLA ---
with tab3:
    st.subheader("📊 Historial General de Inventario")
    res_all = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_all.data:
        st.dataframe(pd.DataFrame(res_all.data), use_container_width=True, hide_index=True)

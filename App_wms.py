import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD (Datos de tu Supabase) ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE - WMS Master", layout="wide")

# --- ESTILOS LOGIEZE (Máxima Visibilidad en Celular) ---
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stButton>button { 
        width: 100%; height: 85px; font-size: 26px !important; 
        font-weight: bold; border-radius: 15px; 
        background-color: #27ae60; color: white; border: 2px solid #2ecc71;
    }
    .stTextInput input, .stNumberInput input { 
        font-size: 24px !important; height: 65px !important; 
        background-color: #1e1e1e !important; color: #f1c40f !important;
    }
    h1 { text-align: center; color: #f1c40f; font-size: 65px !important; text-shadow: 3px 3px #000; }
    .stTabs [data-baseweb="tab"] { font-size: 22px; font-weight: bold; padding: 15px; }
    label { font-size: 20px !important; font-weight: bold !important; color: #bdc3c7 !important; }
    .stock-card { 
        background-color: #2c3e50; padding: 20px; border-radius: 12px; 
        border-left: 10px solid #f1c40f; margin-bottom: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE BÚSQUEDA Y UBICACIÓN ---
def buscar_maestra_precision(termino):
    # cod_int y barras exactos (.eq), nombre parcial (.ilike)
    res = supabase.table("maestra").select("*").or_(f"cod_int.eq.{termino},barras.eq.{termino},nombre.ilike.%{termino}%").execute()
    return pd.DataFrame(res.data)

def motor_sugerencia_pc():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi_str = str(res.data[0]['ubicacion']).upper()
        partes = ubi_str.split("-")
        num_actual = int("".join(filter(str.isdigit, partes[1])))
        letra_actual = partes[1][-1]
        ciclo = ['A', 'B', 'C', 'D']
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
    st.title("🔒 SEGURIDAD")
    clave = st.text_input("PIN Admin", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 ACTUALIZAR PANTALLA"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADA", "🔍 CONSULTA / SALIDA", "📊 PLANILLA GENERAL"])

# --- TAB 1: ENTRADAS (CON SELECTOR DE LOTES EXISTENTES) ---
with tab1:
    if not es_autorizado:
        st.warning("Ingrese su clave de administrador para habilitar la carga.")
    else:
        bus_m = st.text_input("🔎 ESCANEE O BUSQUE CÓDIGO", key="bus_entrada")
        if bus_m:
            df_m = buscar_maestra_precision(bus_m)
            if not df_m.empty:
                # Selección de producto
                prod = df_m.iloc[0] if len(df_m) == 1 else st.selectbox("Confirmar Producto:", df_m['nombre'])
                
                # Buscar si ya existe este producto en el inventario para ofrecer esas ubicaciones
                lotes_res = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).execute()
                df_lotes = pd.DataFrame(lotes_res.data)

                with st.form("form_entrada", clear_on_submit=True):
                    st.subheader(f"Cargando: {prod['nombre']}")
                    f_can = st.number_input("CANTIDAD", min_value=0.1, step=1.0)
                    f_venc_raw = st.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="Ej: 1225")
                    
                    # Lógica de Ubicación Sugerida / Existente
                    op_ubi = ["NUEVA (SERIE 99 AUTOMÁTICA)"]
                    if not df_lotes.empty:
                        for _, l in df_lotes.iterrows():
                            op_ubi.append(f"SUMAR A: {l['ubicacion']} | {l['deposito']} | Vence: {l['fecha']}")
                    op_ubi.append("OTRA (ENTRADA MANUAL)")
                    
                    sel_ubi = st.selectbox("UBICACIÓN DE DESTINO", op_ubi)
                    f_ubi_manual = st.text_input("UBICACIÓN MANUAL (Solo si seleccionó OTRA)", value="")
                    f_dep = st.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])

                    if st.form_submit_button("⚡ REGISTRAR ENTRADA"):
                        if len(f_venc_raw) == 4:
                            # Procesar ubicación final
                            if "SUMAR A:" in sel_ubi:
                                f_ubi = sel_ubi.split(": ")[1].split(" |")[0]
                            elif "NUEVA" in sel_ubi:
                                f_ubi = motor_sugerencia_pc()
                            else:
                                f_ubi = f_ubi_manual.upper().strip()
                            
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            
                            # Intentar sumar al lote existente (Upsert)
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            
                            if match.data:
                                nueva_q = float(match.data[0]['cantidad']) + f_can
                                supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", match.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({
                                    "cod_int": prod['cod_int'], "nombre": prod['nombre'], 
                                    "cantidad": f_can, "fecha": f_venc, "ubicacion": f_ubi, 
                                    "deposito": f_dep, "barras": prod['barras']
                                }).execute()
                            
                            st.success("✅ REGISTRO COMPLETADO")
                            st.rerun()

# --- TAB 2: CONSULTA Y SALIDAS ---
with tab2:
    bus_c = st.text_input("🔍 CONSULTAR STOCK (Código/Nombre/Barras)", key="bus_consulta")
    if bus_c:
        res_c = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_c},barras.eq.{bus_c},nombre.ilike.%{bus_c}%").execute()
        df_c = pd.DataFrame(res_c.data)
        
        if not df_c.empty:
            # Stock Consolidado arriba
            total_gral = df_c['cantidad'].sum()
            d1 = df_c[df_c['deposito'] == "DEPO 1"]['cantidad'].sum()
            d2 = df_c[df_c['deposito'] == "DEPO 2"]['cantidad'].sum()
            
            st.metric("STOCK TOTAL CONSOLIDADO", f"{total_gral}")
            col1, col2 = st.columns(2)
            col1.metric("DEPO 1", d1)
            col2.metric("DEPO 2", d2)
            
            st.divider()
            
            # Detalle por lote
            for _, r in df_c.sort_values(by=['ubicacion']).iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="stock-card">
                            <h3>{r['nombre']}</h3>
                            <p><b>CANT: {r['cantidad']}</b> | Ubi: {r['ubicacion']} | Vence: {r['fecha']}</p>
                            <p style='color:#bdc3c7;'>{r['deposito']} | Cód: {r['cod_int']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if es_autorizado:
                        col_sal, col_btn = st.columns([2,1])
                        baja = col_sal.number_input("Cantidad a retirar", min_value=0.1, max_value=float(r['cantidad']), key=f"sal_{r['id']}")
                        if col_btn.button("RETIRAR", key=f"btn_{r['id']}"):
                            nueva_q = float(r['cantidad']) - baja
                            if nueva_q <= 0:
                                supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else:
                                supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                    st.markdown("---")

# --- TAB 3: PLANILLA GENERAL ---
with tab3:
    st.subheader("Inventario Completo en Nube")
    res_inv = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_inv.data:
        st.dataframe(pd.DataFrame(res_inv.data), use_container_width=True, hide_index=True)

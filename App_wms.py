import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE PRO", layout="wide")

# --- ESTILOS PREMIUM LOGIEZE (Botones Gigantes y Colores Vibrantes) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div.stButton > button:first-child {
        background-color: #2ECC71; color: white; height: 80px; font-size: 28px !important;
        font-weight: bold; border-radius: 15px; border: none; box-shadow: 0px 4px 15px rgba(46, 204, 113, 0.3);
    }
    div.stButton > button:hover { background-color: #27AE60; border: none; color: white; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 24px !important; height: 60px !important; border-radius: 10px !important;
        background-color: #1A1C23 !important; color: #F1C40F !important; border: 1px solid #34495E !important;
    }
    .stTabs [data-baseweb="tab"] { font-size: 22px; font-weight: bold; color: #BDC3C7; padding: 20px; }
    .stTabs [aria-selected="true"] { color: #2ECC71 !important; border-bottom-color: #2ECC71 !important; }
    .sugerencia-box {
        background-color: #1B2631; padding: 20px; border-radius: 15px;
        border-left: 10px solid #3498DB; margin: 15px 0px;
    }
    .stock-card {
        background-color: #16191E; padding: 25px; border-radius: 20px;
        border: 1px solid #2C3E50; border-left: 12px solid #2980B9; margin-bottom: 20px;
    }
    h1 { text-align: center; color: #2ECC71; font-size: 70px !important; font-weight: 800; text-shadow: 2px 2px #000; }
    label { font-size: 20px !important; color: #ECF0F1 !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- MOTOR DE LÓGICA ---
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
    st.markdown("### 🔐 ACCESO ADMIN")
    clave = st.text_input("PIN", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 REFRESCAR SISTEMA"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / SALIDAS", "📊 PLANILLA"])

with tab1:
    if not es_autorizado:
        st.info("🔒 Ingrese clave para operar Entradas.")
    else:
        bus_m = st.text_input("🔎 ESCANEAR O BUSCAR CÓDIGO", key="bus_m")
        
        if bus_m:
            maestra_df = buscar_producto_precision(bus_m)
            if not maestra_df.empty:
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Confirmar Producto:", opciones)
                
                if seleccion:
                    cod_sel = seleccion.split(" | ")[0]
                    item_sel = maestra_df[maestra_df['cod_int'] == cod_sel].iloc[0]
                    
                    # Sugerencia Automática (Para mostrarla visualmente)
                    ubi_auto = motor_sugerencia_pc()
                    
                    st.markdown(f"""
                        <div class="sugerencia-box">
                            <h3 style='margin:0; color:#3498DB;'>🤖 Lógica de Ubicación</h3>
                            <p style='font-size:20px; margin:5px 0;'>La próxima ubicación sugerida es: <b>{ubi_auto}</b></p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Buscar lotes existentes
                    res_ubi = supabase.table("inventario").select("*").eq("cod_int", cod_sel).execute()
                    df_ubi_exist = pd.DataFrame(res_ubi.data)

                    with st.form("form_registro", clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            f_can = st.number_input("CANTIDAD", min_value=0.0, step=1.0)
                            f_venc_raw = st.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="Ej: 1225")
                        with col2:
                            f_dep = st.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                            op_ubi = [f"AUTOMÁTICA ({ubi_auto})"]
                            if not df_ubi_exist.empty:
                                for _, r in df_ubi_exist.iterrows():
                                    op_ubi.append(f"SUMAR A: {r['ubicacion']} | {r['deposito']} | Stock: {r['cantidad']}")
                            op_ubi.append("MANUAL (NUEVA)")
                            sel_modo_ubi = st.selectbox("DESTINO", op_ubi)
                        
                        f_ubi_manual = st.text_input("Si eligió MANUAL, escriba aquí:", value="")
                        
                        if st.form_submit_button("⚡ REGISTRAR CARGA"):
                            if f_can > 0 and len(f_venc_raw) == 4:
                                if "AUTOMÁTICA" in sel_modo_ubi: f_ubi_final = ubi_auto
                                elif "SUMAR A:" in sel_modo_ubi: f_ubi_final = sel_modo_ubi.split(": ")[1].split(" |")[0]
                                else: f_ubi_final = f_ubi_manual.upper().strip()

                                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                                match = supabase.table("inventario").select("*").eq("cod_int", cod_sel).eq("ubicacion", f_ubi_final).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                                
                                if match.data:
                                    nueva_q = float(match.data[0]['cantidad']) + f_can
                                    supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", match.data[0]['id']).execute()
                                else:
                                    supabase.table("inventario").insert({"cod_int": cod_sel, "cantidad": f_can, "nombre": item_sel['nombre'], "barras": item_sel['barras'], "fecha": f_venc, "ubicacion": f_ubi_final, "deposito": f_dep}).execute()
                                
                                st.balloons()
                                st.success(f"Ingresado en {f_ubi_final}")
                                st.rerun()

with tab2:
    bus_d = st.text_input("🔎 BUSCADOR DE STOCK", key="bus_d")
    if bus_d:
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f"<div style='background-color:#2980B9; padding:15px; border-radius:15px; text-align:center;'><h2>TOTAL: {df['cantidad'].sum()}</h2></div>", unsafe_allow_html=True)
            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f"""<div class="stock-card"><h3>{r['nombre']}</h3><p style='font-size:22px;'><b>CANT: {r['cantidad']}</b> | UBI: {r['ubicacion']} | {r['deposito']}</p></div>""", unsafe_allow_html=True)
                    if es_autorizado:
                        col_a, col_b = st.columns([2,1])
                        baja = col_a.number_input(f"Baja para ID {r['id']}", min_value=0.1, max_value=float(r['cantidad']), key=f"n_{r['id']}")
                        if col_b.button("SALIDA", key=f"btn_{r['id']}"):
                            nueva_q = float(r['cantidad']) - baja
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()

with tab3:
    st.subheader("Planilla General Cloud")
    res_inv = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_inv.data:
        st.dataframe(pd.DataFrame(res_inv.data), use_container_width=True, hide_index=True)

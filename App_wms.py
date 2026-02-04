import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE PRO", layout="wide")

# --- ESTILOS OPTIMIZADOS PARA MOBILE (SIN DESFASES) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div.stButton > button:first-child {
        background-color: #2ECC71 !important; color: white !important; 
        height: 70px !important; font-size: 22px !important;
        font-weight: bold !important; border-radius: 12px !important; 
        border: none !important; margin-top: 10px !important;
    }
    /* Botón secundario para Transferencias */
    div.stButton > button[key^="tr_"] {
        background-color: #3498DB !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 19px !important; height: 50px !important; 
        background-color: #1A1C23 !important; color: #F1C40F !important;
    }
    label { font-size: 17px !important; font-weight: bold !important; color: #ECF0F1 !important; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; padding: 12px; }
    .sugerencia-box {
        background-color: #1B2631; padding: 15px; border-radius: 12px;
        border-left: 8px solid #3498DB; margin-bottom: 15px;
    }
    .stock-card {
        background-color: #16191E; padding: 15px; border-radius: 15px;
        border-left: 10px solid #2980B9; margin-bottom: 10px;
    }
    h1 { text-align: center; color: #2ECC71; font-size: 50px !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE NEGOCIO ---
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

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔐 ACCESO ADMIN")
    clave = st.text_input("PIN", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 RECARGAR"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

with tab1:
    if es_autorizado:
        bus_m = st.text_input("🔎 BUSCAR CÓDIGO", key="bus_m")
        if bus_m:
            maestra_df = buscar_producto_precision(bus_m)
            if not maestra_df.empty:
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Confirmar:", opciones)
                if seleccion:
                    cod_sel = seleccion.split(" | ")[0]
                    item_sel = maestra_df[maestra_df['cod_int'] == cod_sel].iloc[0]
                    ubi_auto = motor_sugerencia_pc()
                    st.markdown(f'<div class="sugerencia-box">🔹 Sugerencia 99: <b style="color:#F1C40F;">{ubi_auto}</b></div>', unsafe_allow_html=True)
                    
                    res_ubi = supabase.table("inventario").select("*").eq("cod_int", cod_sel).execute()
                    df_ubi_exist = pd.DataFrame(res_ubi.data)

                    with st.form("form_registro", clear_on_submit=True):
                        st.write(f"Cargando: {item_sel['nombre']}")
                        c1, c2 = st.columns(2)
                        f_can = c1.number_input("CANTIDAD", min_value=0.0)
                        f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4)
                        f_dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                        op_ubi = [f"AUTO ({ubi_auto})"]
                        if not df_ubi_exist.empty:
                            for _, r in df_ubi_exist.iterrows():
                                op_ubi.append(f"EXISTE: {r['ubicacion']} | {r['deposito']} | Q:{r['cantidad']}")
                        op_ubi.append("MANUAL")
                        sel_modo_ubi = c2.selectbox("UBICACIÓN", op_ubi)
                        f_ubi_manual = st.text_input("UBICACIÓN MANUAL (Opcional):")
                        
                        if st.form_submit_button("⚡ REGISTRAR"):
                            if f_can > 0 and len(f_venc_raw) == 4:
                                f_ubi_final = ubi_auto if "AUTO" in sel_modo_ubi else (sel_modo_ubi.split(": ")[1].split(" |")[0] if "EXISTE:" in sel_modo_ubi else f_ubi_manual.upper())
                                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                                match = supabase.table("inventario").select("*").eq("cod_int", cod_sel).eq("ubicacion", f_ubi_final).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                                if match.data:
                                    supabase.table("inventario").update({"cantidad": float(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                                else:
                                    supabase.table("inventario").insert({"cod_int": cod_sel, "cantidad": f_can, "nombre": item_sel['nombre'], "barras": item_sel['barras'], "fecha": f_venc, "ubicacion": f_ubi_final, "deposito": f_dep}).execute()
                                st.success("¡Cargado!"); st.rerun()

with tab2:
    bus_d = st.text_input("🔎 BUSCADOR STOCK / PASES", key="bus_d")
    if bus_d:
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f"<div style='background-color:#2980B9; padding:10px; border-radius:10px; text-align:center;'><h3>TOTAL: {df['cantidad'].sum()}</h3></div>", unsafe_allow_html=True)
            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>Q: {r["cantidad"]} | Ubi: {r["ubicacion"]} | {r["deposito"]} | Vence: {r["fecha"]}</div>', unsafe_allow_html=True)
                    if es_autorizado:
                        col_x, col_y, col_z = st.columns([1.5,1,1])
                        cant_mov = col_x.number_input("Cantidad", min_value=0.1, max_value=float(r['cantidad']), key=f"q_{r['id']}")
                        
                        if col_y.button("SALIDA", key=f"btn_{r['id']}"):
                            nueva_q = float(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                        
                        if col_z.button("PASAR", key=f"tr_{r['id']}"):
                            # Lógica de Transferencia
                            depo_destino = "DEPO 2" if r['deposito'] == "DEPO 1" else "DEPO 1"
                            # 1. Restar del origen
                            nueva_q_orig = float(r['cantidad']) - cant_mov
                            if nueva_q_orig <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q_orig}).eq("id", r['id']).execute()
                            # 2. Sumar al destino (Upsert)
                            match_dest = supabase.table("inventario").select("*").eq("cod_int", r['cod_int']).eq("ubicacion", r['ubicacion']).eq("fecha", r['fecha']).eq("deposito", depo_destino).execute()
                            if match_dest.data:
                                supabase.table("inventario").update({"cantidad": float(match_dest.data[0]['cantidad']) + cant_mov}).eq("id", match_dest.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int": r['cod_int'], "cantidad": cant_mov, "nombre": r['nombre'], "barras": r['barras'], "fecha": r['fecha'], "ubicacion": r['ubicacion'], "deposito": depo_destino}).execute()
                            st.success(f"Movido a {depo_destino}"); st.rerun()

with tab3:
    res_inv = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_inv.data: st.dataframe(pd.DataFrame(res_inv.data), use_container_width=True, hide_index=True)

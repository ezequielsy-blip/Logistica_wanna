import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE PRO", layout="wide")

# --- ESTILOS FORMALES Y BOTONES EN LÍNEA FORZADOS ---
st.markdown("""
    <style>
    .main { background-color: #121417; }
    
    /* Forzar botones uno al lado del otro en móviles */
    [data-testid="column"] {
        display: inline-block !important;
        width: 48% !important;
        min-width: 48% !important;
    }
    
    div.stButton > button:first-child {
        width: 100%;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        color: white !important;
    }

    /* Colores Formales */
    /* Botón REGISTRAR (Verde Oliva) */
    div.stForm button { background-color: #3e4d35 !important; }
    
    /* Botón SALIDA (Gris Azulado) */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #4a5568 !important; }
    
    /* Botón PASAR (Azul Marino Tenue) */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #2c3e50 !important; }

    /* Inputs sobrios */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 16px !important;
        height: 45px !important;
        background-color: #1e2126 !important;
        color: #d1d5db !important;
        border: 1px solid #374151 !important;
    }

    label { font-size: 15px !important; color: #9ca3af !important; }
    
    .sugerencia-box {
        background-color: #1e2126;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #2c3e50;
        margin-bottom: 12px;
        color: #d1d5db;
    }

    .stock-card {
        background-color: #1e2126;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #4a5568;
        margin-bottom: 8px;
        color: #e5e7eb;
    }

    h1 { text-align: center; color: #f3f4f6; font-size: 40px !important; margin-bottom: 15px; }
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
    clave = st.text_input("PIN Admin", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 REFRESCAR"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS ---
with tab1:
    if es_autorizado:
        bus_m = st.text_input("🔎 BUSCAR CÓDIGO", key="bus_m")
        if bus_m:
            maestra_df = buscar_producto_precision(bus_m)
            if not maestra_df.empty:
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Confirmar Producto:", opciones)
                if seleccion:
                    cod_sel = seleccion.split(" | ")[0]
                    item_sel = maestra_df[maestra_df['cod_int'] == cod_sel].iloc[0]
                    ubi_auto = motor_sugerencia_pc()
                    st.markdown(f'<div class="sugerencia-box">Sugerencia 99: <b>{ubi_auto}</b></div>', unsafe_allow_html=True)
                    
                    res_ubi = supabase.table("inventario").select("*").eq("cod_int", cod_sel).execute()
                    df_ubi_exist = pd.DataFrame(res_ubi.data)

                    with st.form("form_registro", clear_on_submit=True):
                        st.write(f"**Item:** {item_sel['nombre']}")
                        c1, c2 = st.columns(2)
                        f_can = c1.number_input("CANTIDAD", min_value=0.0)
                        f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", max_chars=4)
                        f_dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                        op_ubi = [f"AUTO ({ubi_auto})"]
                        if not df_ubi_exist.empty:
                            for _, r in df_ubi_exist.iterrows():
                                op_ubi.append(f"EXISTE: {r['ubicacion']} | {r['deposito']} | Q:{r['cantidad']}")
                        op_ubi.append("MANUAL")
                        sel_modo_ubi = c2.selectbox("DESTINO", op_ubi)
                        f_ubi_manual = st.text_input("UBICACIÓN MANUAL:")
                        if st.form_submit_button("⚡ REGISTRAR"):
                            if f_can > 0 and len(f_venc_raw) == 4:
                                f_ubi_final = ubi_auto if "AUTO" in sel_modo_ubi else (sel_modo_ubi.split(": ")[1].split(" |")[0] if "EXISTE:" in sel_modo_ubi else f_ubi_manual.upper())
                                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                                match = supabase.table("inventario").select("*").eq("cod_int", cod_sel).eq("ubicacion", f_ubi_final).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                                if match.data:
                                    supabase.table("inventario").update({"cantidad": float(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                                else:
                                    supabase.table("inventario").insert({"cod_int": cod_sel, "cantidad": f_can, "nombre": item_sel['nombre'], "barras": item_sel['barras'], "fecha": f_venc, "ubicacion": f_ubi_final, "deposito": f_dep}).execute()
                                st.rerun()

# --- TAB 2: STOCK / PASES ---
with tab2:
    bus_d = st.text_input("🔎 BUSCAR", key="bus_d")
    if bus_d:
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f"<div style='background-color:#2c3e50; padding:10px; border-radius:8px; text-align:center;'><h3>STOCK: {df['cantidad'].sum()}</h3></div>", unsafe_allow_html=True)
            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>Q: {r["cantidad"]} | {r["ubicacion"]} | {r["deposito"]} | {r["fecha"]}</div>', unsafe_allow_html=True)
                    if es_autorizado:
                        cant_mov = st.number_input(f"Q a mover (ID:{r['id']})", min_value=0.1, max_value=float(r['cantidad']), key=f"q_{r['id']}")
                        
                        col_sal, col_pas = st.columns(2)
                        if col_sal.button("SALIDA", key=f"btn_{r['id']}"):
                            nueva_q = float(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                        
                        if col_pas.button("PASAR", key=f"tr_{r['id']}"):
                            depo_destino = "DEPO 2" if r['deposito'] == "DEPO 1" else "DEPO 1"
                            nueva_q_orig = float(r['cantidad']) - cant_mov
                            if nueva_q_orig <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q_orig}).eq("id", r['id']).execute()
                            match_dest = supabase.table("inventario").select("*").eq("cod_int", r['cod_int']).eq("ubicacion", r['ubicacion']).eq("fecha", r['fecha']).eq("deposito", depo_destino).execute()
                            if match_dest.data:
                                supabase.table("inventario").update({"cantidad": float(match_dest.data[0]['cantidad']) + cant_mov}).eq("id", match_dest.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int": r['cod_int'], "cantidad": cant_mov, "nombre": r['nombre'], "barras": r['barras'], "fecha": r['fecha'], "ubicacion": r['ubicacion'], "deposito": depo_destino}).execute()
                            st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    res_all = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_all.data: st.dataframe(pd.DataFrame(res_all.data), use_container_width=True, hide_index=True)

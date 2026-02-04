import streamlit as st
import pandas as pd
from datetime import datetime
import os
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE - Mobile WMS", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stButton>button { width: 100%; height: 70px; font-size: 22px !important; font-weight: bold; border-radius: 12px; margin-top: 10px; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { font-size: 20px !important; height: 50px !important; }
    label { font-size: 18px !important; color: #f1c40f !important; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; padding: 20px; }
    .stock-card { padding: 20px; border-radius: 15px; border-left: 10px solid #2980b9; background-color: #1e1e1e; margin-bottom: 15px; }
    h1 { text-align: center; color: #ffffff; font-size: 50px !important; text-shadow: 2px 2px #2980b9; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE BÚSQUEDA DE PRECISIÓN ---
def buscar_producto_precision(busqueda):
    # .eq para cod_int y barras (Exacto), .ilike para nombre (Contenido)
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
    if st.button("🔄 REFRESCAR APP"): st.rerun()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADA", "🔍 CONSULTA/SALIDA", "📊 PLANILLA"])

with tab1:
    if not es_autorizado:
        st.warning("Ingrese clave para registrar movimientos.")
    else:
        st.subheader("Carga de Mercadería")
        bus_m = st.text_input("🔎 Escanear o Buscar (Exacto por Código)", key="bus_m")
        
        if bus_m:
            maestra_df = buscar_producto_precision(bus_m)
            if not maestra_df.empty:
                opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
                seleccion = st.selectbox("Confirmar Producto:", opciones)
                
                if seleccion:
                    cod_sel = seleccion.split(" | ")[0]
                    item_sel = maestra_df[maestra_df['cod_int'] == cod_sel].iloc[0]
                    
                    # BUSCAR UBICACIONES EXISTENTES DE ESTE PRODUCTO
                    res_ubi = supabase.table("inventario").select("*").eq("cod_int", cod_sel).execute()
                    df_ubi_exist = pd.DataFrame(res_ubi.data)
                    
                    with st.form("form_logieze", clear_on_submit=True):
                        st.write(f"Cargando: **{item_sel['nombre']}**")
                        f_can = st.number_input("CANTIDAD", min_value=0.0, step=1.0)
                        f_venc_raw = st.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="Ej: 0528")
                        
                        # --- SELECTOR DE UBICACIÓN DINÁMICO ---
                        opciones_ubicacion = ["SUGERENCIA 99 (AUTOMÁTICA)"]
                        if not df_ubi_exist.empty:
                            for _, r in df_ubi_exist.iterrows():
                                opciones_ubicacion.append(f"SUMAR A: {r['ubicacion']} | {r['deposito']} | Stock: {r['cantidad']} | Vence: {r['fecha']}")
                        opciones_ubicacion.append("INGRESAR UBICACIÓN NUEVA")
                        
                        sel_modo_ubi = st.selectbox("¿DÓNDE GUARDAR?", opciones_ubicacion)
                        f_ubi_manual = st.text_input("UBICACIÓN MANUAL (Solo si eligió NUEVA)", value="")
                        f_dep = st.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                        
                        if st.form_submit_button("⚡ REGISTRAR CARGA"):
                            if f_can > 0 and len(f_venc_raw) == 4:
                                # Definir la ubicación final
                                if "SUGERENCIA 99" in sel_modo_ubi:
                                    f_ubi_final = motor_sugerencia_pc()
                                elif "SUMAR A:" in sel_modo_ubi:
                                    # Extraer la ubicación de la cadena del selectbox
                                    f_ubi_final = sel_modo_ubi.split(": ")[1].split(" |")[0]
                                else:
                                    f_ubi_final = f_ubi_manual.upper().strip()

                                f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                                
                                # LÓGICA DE ACTUALIZACIÓN O INSERCIÓN
                                exist = supabase.table("inventario").select("*").eq("cod_int", cod_sel).eq("ubicacion", f_ubi_final).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                                
                                if exist.data:
                                    nueva_q = float(exist.data[0]['cantidad']) + f_can
                                    supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", exist.data[0]['id']).execute()
                                else:
                                    datos = {"cod_int": cod_sel, "cantidad": f_can, "nombre": item_sel['nombre'], "barras": item_sel['barras'], "fecha": f_venc, "ubicacion": f_ubi_final, "deposito": f_dep}
                                    supabase.table("inventario").insert(datos).execute()
                                
                                st.success(f"¡{item_sel['nombre']} Registrado en {f_ubi_final}!")
                                st.rerun()

with tab2:
    bus_d = st.text_input("🔎 CONSULTAR STOCK (Exacto por Código)", key="bus_d")
    if bus_d:
        # Búsqueda precisa también en consulta
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['cod_int', 'fecha'])
            total_global = df['cantidad'].sum()
            st.markdown(f"<div style='background-color:#2980b9; padding:20px; border-radius:15px; text-align:center;'><h2>STOCK TOTAL: {total_global}</h2></div>", unsafe_allow_html=True)

            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f"""<div class="stock-card"><h3 style='margin:0;'>{r['nombre']}</h3><p><b>CANT: {r['cantidad']}</b> | Ubi: {r['ubicacion']} | Vence: {r['fecha']}</p></div>""", unsafe_allow_html=True)
                    if es_autorizado:
                        col_a, col_b = st.columns([2,1])
                        baja = col_a.number_input("Cantidad a retirar", min_value=0.1, max_value=float(r['cantidad']), key=f"n_{r['id']}")
                        if col_b.button("SALIDA", key=f"btn_{r['id']}"):
                            nueva_cant = float(r['cantidad']) - baja
                            if nueva_cant <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_cant}).eq("id", r['id']).execute()
                            st.rerun()

with tab3:
    st.subheader("Planilla Completa")
    res_all = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_all.data:
        st.dataframe(pd.DataFrame(res_all.data), use_container_width=True, hide_index=True)

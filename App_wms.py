import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE - WMS Master", layout="wide")

# --- GESTIÓN DE ESTADO (Para la transferencia) ---
if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS LOGIEZE (Formal y Botones en Línea) ---
st.markdown("""
    <style>
    .main { background-color: #121417; }
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    
    div.stButton > button {
        width: 100%; height: 65px !important; font-size: 20px !important;
        font-weight: bold !important; border-radius: 10px !important; border: none !important; color: white !important;
    }
    div.stForm button { background-color: #3e4d35 !important; } 
    div[data-testid="column"]:nth-of-type(1) button { background-color: #4a5568 !important; } 
    div[data-testid="column"]:nth-of-type(2) button { background-color: #2c3e50 !important; } 

    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 18px !important; height: 50px !important; background-color: #1e2126 !important; color: #d1d5db !important;
    }
    h1 { text-align: center; color: #f3f4f6; font-size: 50px !important; }
    .sugerencia-box { background-color: #1e2126; padding: 15px; border-radius: 8px; border-left: 6px solid #2c3e50; margin-bottom: 12px; color: #d1d5db; }
    .stock-card { background-color: #1e2126; padding: 15px; border-radius: 10px; border-left: 6px solid #4a5568; margin-bottom: 8px; color: #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LÓGICA DE BÚSQUEDA ---
def buscar_producto(termino):
    res = supabase.table("maestra").select("*").or_(f"cod_int.eq.{termino},barras.eq.{termino},nombre.ilike.%{termino}%").execute()
    return pd.DataFrame(res.data)

def motor_sugerencia_pc():
    try:
        # 1. BUSCAR POSICIONES EN 0 (Estantes 01-27, Niveles 1-6, A-E)
        niveles = [str(i) for i in range(1, 7)]
        letras = ['A', 'B', 'C', 'D', 'E']
        
        res_ocupadas = supabase.table("inventario").select("ubicacion").eq("deposito", "DEPO 1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res_ocupadas.data] if res_ocupadas.data else []

        for e in range(1, 28):
            for n in niveles:
                for l in letras:
                    ubi_test = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi_test not in ocupadas:
                        return ubi_test 

        # 2. SERIE 99 SI NO HAY VACÍAS
        res_99 = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res_99.data: return "99-01A"
        ubi_str = str(res_99.data[0]['ubicacion']).upper()
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_actual = int("".join(filter(str.isdigit, cuerpo)))
        ciclo = ['A', 'B', 'C', 'D']
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
    clave = st.text_input("PIN Admin", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 REFRESCAR"): st.rerun()

# Control de redirección por estado
default_tab = 0 if st.session_state.transfer_data else 1
tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS ---
with tab1:
    if es_autorizado:
        # Si venimos de una transferencia, pre-cargamos el buscador
        init_bus = ""
        if st.session_state.transfer_data:
            init_bus = st.session_state.transfer_data['cod_int']
            st.warning(f"🔄 Modo Transferencia Activo: Moviendo {st.session_state.transfer_data['cantidad']} unidades.")

        bus_m = st.text_input("🔍 ESCANEAR PRODUCTO", value=init_bus, key="entrada_bus")
        
        if bus_m:
            df_m = buscar_producto(bus_m)
            if not df_m.empty:
                prod = df_m.iloc[0] if len(df_m)==1 else st.selectbox("Seleccione:", df_m['nombre'])
                lotes = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).execute()
                df_lotes = pd.DataFrame(lotes.data)
                ubi_sugerida = motor_sugerencia_pc()
                
                st.markdown(f'<div class="sugerencia-box">📍 Sugerencia de posición libre: <b>{ubi_sugerida}</b></div>', unsafe_allow_html=True)

                with st.form("form_entrada", clear_on_submit=True):
                    # Valores por defecto si hay transferencia activa
                    def_q = float(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 0.1
                    def_v = st.session_state.transfer_data['fecha'].replace("/", "") if st.session_state.transfer_data else ""
                    def_d = "DEPO 2" if st.session_state.transfer_data and st.session_state.transfer_data['deposito_orig'] == "DEPO 1" else "DEPO 1"

                    st.write(f"**Cargando:** {prod['nombre']}")
                    c1, c2 = st.columns(2)
                    f_can = c1.number_input("CANTIDAD", min_value=0.0, value=def_q)
                    f_venc_raw = c1.text_input("VENCIMIENTO (MMAA)", value=def_v, max_chars=4)
                    f_dep = c2.selectbox("DEPÓSITO DESTINO", ["DEPO 1", "DEPO 2"], index=0 if def_d == "DEPO 1" else 1)
                    
                    opciones_ubi = [f"SUGERIDA ({ubi_sugerida})"]
                    if not df_lotes.empty:
                        for _, l in df_lotes.iterrows():
                            opciones_ubi.append(f"EXISTE: {l['ubicacion']} | {l['deposito']} | Q:{l['cantidad']}")
                    opciones_ubi.append("MANUAL")
                    
                    sel_ubi = c2.selectbox("UBICACIÓN", opciones_ubi)
                    f_ubi_manual = st.text_input("UBICACIÓN MANUAL (Si eligió MANUAL)")

                    if st.form_submit_button("⚡ FINALIZAR CARGA / PASO"):
                        if f_can > 0 and len(f_venc_raw) == 4:
                            f_ubi = ubi_sugerida if "SUGERIDA" in sel_ubi else (sel_ubi.split(": ")[1].split(" |")[0] if "EXISTE:" in sel_ubi else f_ubi_manual.upper())
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            
                            if match.data:
                                supabase.table("inventario").update({"cantidad": float(match.data[0]['cantidad']) + f_can}).eq("id", match.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int": prod['cod_int'], "nombre": prod['nombre'], "cantidad": f_can, "fecha": f_venc, "ubicacion": f_ubi, "deposito": f_dep, "barras": prod['barras']}).execute()
                            
                            # Limpiar estado de transferencia al terminar
                            st.session_state.transfer_data = None
                            st.success("✅ Operación completada con éxito")
                            st.rerun()

# --- TAB 2: STOCK / PASES ---
with tab2:
    bus_d = st.text_input("🔎 BUSCAR EN STOCK", key="bus_d")
    if bus_d:
        res_d = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_d},barras.eq.{bus_d},nombre.ilike.%{bus_d}%").execute()
        df = pd.DataFrame(res_d.data)
        if not df.empty:
            df = df[df['cantidad'] > 0].sort_values(by=['ubicacion'])
            st.markdown(f"<div style='background-color:#2c3e50; padding:10px; border-radius:8px; text-align:center;'><h3>TOTAL EN STOCK: {df['cantidad'].sum()}</h3></div>", unsafe_allow_html=True)
            for _, r in df.iterrows():
                with st.container():
                    st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b><br>Q: {r["cantidad"]} | {r["ubicacion"]} | {r["deposito"]} | {r["fecha"]}</div>', unsafe_allow_html=True)
                    if es_autorizado:
                        cant_mov = st.number_input(f"Cantidad (ID:{r['id']})", min_value=0.1, max_value=float(r['cantidad']), key=f"q_{r['id']}")
                        col_sal, col_pas = st.columns(2)
                        
                        if col_sal.button("SALIDA", key=f"btn_{r['id']}"):
                            nueva_q = float(r['cantidad']) - cant_mov
                            if nueva_q <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", r['id']).execute()
                            st.rerun()
                        
                        if col_pas.button("PASAR", key=f"tr_{r['id']}"):
                            # 1. Restar del lote original inmediatamente
                            nueva_q_orig = float(r['cantidad']) - cant_mov
                            if nueva_q_orig <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva_q_orig}).eq("id", r['id']).execute()
                            
                            # 2. Guardar datos en memoria para la pestaña de Entradas
                            st.session_state.transfer_data = {
                                'cod_int': r['cod_int'],
                                'cantidad': cant_mov,
                                'fecha': r['fecha'],
                                'deposito_orig': r['deposito']
                            }
                            # 3. Redirigir
                            st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    res_all = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_all.data: st.dataframe(pd.DataFrame(res_all.data), use_container_width=True, hide_index=True)

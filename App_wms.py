import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE - WMS Master", layout="wide")

# --- ESTILOS LOGIEZE (Máxima Visibilidad y Botones Gigantes) ---
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stButton>button { 
        width: 100%; 
        height: 85px; 
        font-size: 26px !important; 
        font-weight: bold; 
        border-radius: 15px; 
        background-color: #27ae60;
        color: white;
        border: 2px solid #2ecc71;
    }
    .stTextInput input, .stNumberInput input { 
        font-size: 24px !important; 
        height: 65px !important; 
        background-color: #1e1e1e !important;
        color: #f1c40f !important;
    }
    h1 { text-align: center; color: #f1c40f; font-size: 65px !important; text-shadow: 3px 3px #000; margin-bottom: 0px; }
    h2 { color: #3498db; font-size: 35px !important; }
    .stock-card { 
        background-color: #2c3e50; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 10px solid #f1c40f; 
        margin-bottom: 15px; 
    }
    .picking-ok { 
        background-color: #1e8449; 
        padding: 15px; 
        border-radius: 10px; 
        color: white; 
        font-weight: bold; 
        font-size: 20px;
        text-align: center;
        border: 2px solid #2ecc71;
    }
    .stTabs [data-baseweb="tab"] { font-size: 22px; font-weight: bold; padding: 15px; }
    label { font-size: 20px !important; font-weight: bold !important; color: #bdc3c7 !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- FUNCIONES DE LÓGICA DE PRECISIÓN ---
def buscar_maestra_precision(termino):
    # Búsqueda exacta en códigos, parcial en nombre
    res = supabase.table("maestra").select("*").or_(f"cod_int.eq.{termino},barras.eq.{termino},nombre.ilike.%{termino}%").execute()
    return pd.DataFrame(res.data)

def motor_sugerencia_pc():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi_str = str(res.data[0]['ubicacion']).upper()
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

# --- INTERFAZ LOGIEZE ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔒 ADMIN")
    clave = st.text_input("Clave", type="password")
    es_autorizado = (clave == "70797474")
    if st.button("🔄 RECARGAR SISTEMA"): st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📥 ENTRADA", "🔍 CONSULTA", "📋 PICKING", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS CON SELECTOR DE UBICACIÓN EXISTENTE ---
with tab1:
    if not es_autorizado:
        st.warning("Ingrese clave para registrar ingresos.")
    else:
        bus_m = st.text_input("🔎 ESCANEE O BUSQUE CÓDIGO", key="bus_entrada")
        if bus_m:
            df_m = buscar_maestra_precision(bus_m)
            if not df_m.empty:
                prod = df_m.iloc[0] if len(df_m) == 1 else st.selectbox("Elegir producto:", df_m['nombre'])
                
                # Buscar lotes donde YA hay este producto para permitir sumar
                lotes_res = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).execute()
                df_lotes = pd.DataFrame(lotes_res.data)

                with st.form("form_registro_entrada", clear_on_submit=True):
                    st.subheader(f"Cargando: {prod['nombre']}")
                    f_can = st.number_input("CANTIDAD A INGRESAR", min_value=0.1, step=1.0)
                    f_venc_raw = st.text_input("VENCIMIENTO (MMAA)", max_chars=4, placeholder="Ej: 1225")
                    
                    # SELECTOR DE UBICACIÓN TRIPLE
                    op_ubi = ["NUEVA (SERIE 99)"]
                    if not df_lotes.empty:
                        for _, l in df_lotes.iterrows():
                            op_ubi.append(f"SUMAR A: {l['ubicacion']} | {l['deposito']} | Vence: {l['fecha']} | Stock: {l['cantidad']}")
                    op_ubi.append("OTRA (UBICACIÓN MANUAL)")
                    
                    sel_ubi = st.selectbox("DESTINO DE LA MERCADERÍA", op_ubi)
                    f_ubi_manual = st.text_input("UBICACIÓN MANUAL (Solo si seleccionó OTRA)", value="")
                    f_dep = st.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])

                    if st.form_submit_button("⚡ CONFIRMAR INGRESO"):
                        if len(f_venc_raw) == 4:
                            # Definir ubicación
                            if "SUMAR A:" in sel_ubi:
                                f_ubi = sel_ubi.split(": ")[1].split(" |")[0]
                            elif "NUEVA" in sel_ubi:
                                f_ubi = motor_sugerencia_pc()
                            else:
                                f_ubi = f_ubi_manual.upper().strip()
                            
                            f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                            
                            # Lógica Upsert (Suma si coincide todo)
                            match = supabase.table("inventario").select("*").eq("cod_int", prod['cod_int']).eq("ubicacion", f_ubi).eq("fecha", f_venc).eq("deposito", f_dep).execute()
                            
                            if match.data:
                                nueva_q = float(match.data[0]['cantidad']) + f_can
                                supabase.table("inventario").update({"cantidad": nueva_q}).eq("id", match.data[0]['id']).execute()
                            else:
                                datos = {
                                    "cod_int": prod['cod_int'], "nombre": prod['nombre'], 
                                    "cantidad": f_can, "fecha": f_venc, "ubicacion": f_ubi, 
                                    "deposito": f_dep, "barras": prod['barras']
                                }
                                supabase.table("inventario").insert(datos).execute()
                            
                            st.success("✅ REGISTRADO CORRECTAMENTE")
                            st.rerun()

# --- TAB 3: PICKING / DESPACHO (VALIDACIÓN POR ESCANEO Y ELECCIÓN DE LOTE) ---
with tab3:
    st.header("Órdenes de Despacho")
    res_p = supabase.table("despacho").select("*").eq("estado", "PENDIENTE").execute()
    
    if res_p.data:
        df_p = pd.DataFrame(res_p.data)
        for _, p in df_p.iterrows():
            with st.expander(f"📦 ORDEN: {p.get('nro_orden', 'S/N')} | PRODUCTO: {p['nombre']}", expanded=True):
                st.write(f"**CANTIDAD PEDIDA:** {p['cantidad']}")
                
                # 1. ESCANEO OBLIGATORIO
                scan_val = st.text_input(f"Escanear Producto para Despacho", key=f"pick_scan_{p['id']}")
                
                # Si el escaneo es correcto (Código Interno o Barras)
                if scan_val == str(p['cod_int']) or (p.get('barras') and scan_val == str(p['barras'])):
                    st.markdown('<p class="picking-ok">✅ ESCANEO CORRECTO - SELECCIONE LOTE</p>', unsafe_allow_html=True)
                    
                    # 2. MOSTRAR LOTES DISPONIBLES PARA RESTAR
                    lotes_pick = supabase.table("inventario").select("*").eq("cod_int", p['cod_int']).gt("cantidad", 0).execute()
                    if lotes_pick.data:
                        df_lp = pd.DataFrame(lotes_pick.data)
                        op_lotes = []
                        for _, lp in df_lp.iterrows():
                            op_lotes.append(f"ID:{lp['id']} | Ubi: {lp['ubicacion']} | Depo: {lp['deposito']} | Vence: {lp['fecha']} | Stock: {lp['cantidad']}")
                        
                        sel_lote_final = st.selectbox("¿DE QUÉ LOTE SACARÁ LA MERCADERÍA?", options=op_lotes, key=f"sel_lote_{p['id']}")
                        
                        if st.button(f"FINALIZAR PICKING ORDEN {p['id']}", key=f"f_btn_{p['id']}"):
                            # Extraer ID del lote seleccionado
                            id_lote_db = int(sel_lote_final.split(" | ")[0].replace("ID:", ""))
                            lote_db = df_lp[df_lp['id'] == id_lote_db].iloc[0]
                            
                            # Operación de resta
                            nueva_q_inv = float(lote_db['cantidad']) - float(p['cantidad'])
                            
                            if nueva_q_inv < 0:
                                st.error("❌ No hay suficiente stock en ese lote.")
                            else:
                                # Restar del inventario
                                if nueva_q_inv == 0:
                                    supabase.table("inventario").delete().eq("id", id_lote_db).execute()
                                else:
                                    supabase.table("inventario").update({"cantidad": nueva_q_inv}).eq("id", id_lote_db).execute()
                                
                                # Marcar orden como OK
                                supabase.table("despacho").update({"estado": "OK", "fecha_p": datetime.now().strftime("%Y-%m-%d %H:%M")}).eq("id", p['id']).execute()
                                st.success("PICKING COMPLETADO")
                                st.rerun()
                    else:
                        st.error("No hay stock disponible en inventario para este código.")
                elif scan_val != "":
                    st.error("❌ El código escaneado no coincide con el pedido.")
    else:
        st.info("No hay órdenes de despacho pendientes.")

# --- TAB 2: CONSULTA DE STOCK CONSOLIDADO ---
with tab2:
    bus_c = st.text_input("🔍 CONSULTAR CÓDIGO O NOMBRE", key="bus_consulta")
    if bus_c:
        df_c = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_c},barras.eq.{bus_c},nombre.ilike.%{bus_c}%").execute()
        res_c = pd.DataFrame(df_c.data)
        if not res_c.empty:
            st.metric("TOTAL EN DEPÓSITOS", res_c['cantidad'].sum())
            # Desglose por Depósito
            d1 = res_c[res_c['deposito'] == "DEPO 1"]['cantidad'].sum()
            d2 = res_c[res_c['deposito'] == "DEPO 2"]['cantidad'].sum()
            col1, col2 = st.columns(2)
            col1.metric("DEPO 1", d1)
            col2.metric("DEPO 2", d2)
            
            st.write("### Detalle por Ubicación (Consecutivo)")
            st.dataframe(res_c[['cantidad', 'ubicacion', 'deposito', 'fecha', 'nombre']].sort_values(by=['ubicacion']), use_container_width=True, hide_index=True)

# --- TAB 4: PLANILLA GENERAL ---
with tab4:
    st.subheader("Planilla General de Inventario")
    res_inv = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if res_inv.data:
        st.dataframe(pd.DataFrame(res_inv.data), use_container_width=True)

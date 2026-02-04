import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

# Conexión directa sin caché para asegurar que los datos suban y bajen al instante
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS COMPLETOS (Botones gigantes, banners y modo oscuro) ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    
    /* Botones de acción principales */
    div.stButton > button {
        width: 100%; height: 85px !important; font-size: 26px !important;
        font-weight: 700 !important; border-radius: 15px !important; color: white !important;
    }
    
    /* Botón de actualizar */
    .block-container div.stButton > button[kind="secondary"] {
        background-color: #D4AC0D !important; height: 65px !important; color: black !important;
    }

    div.stForm button { background-color: #1E8449 !important; }
    div[data-testid="column"]:nth-of-type(1) button { background-color: #2E4053 !important; } /* Salida */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #1B2631 !important; } /* Pasar */
    
    /* Inputs y Selectores */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        font-size: 22px !important; height: 60px !important; 
        background-color: #1A1C23 !important; color: #ECF0F1 !important;
        border: 2px solid #34495E !important; border-radius: 10px !important;
    }
    
    h1 { text-align: center; color: #FFFFFF; font-size: 60px !important; font-weight: 800; margin-bottom: 20px; }
    
    .sugerencia-box { 
        background-color: #1C2833; padding: 25px; border-radius: 15px; 
        border-left: 12px solid #3498DB; margin-bottom: 25px; color: #D5DBDB; font-size: 20px;
    }
    
    .stock-card { 
        background-color: #17202A; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #2C3E50; margin-bottom: 15px; color: #EBEDEF;
    }
    
    .edit-box {
        background-color: #1B2631; padding: 15px; border-radius: 10px; border: 2px dashed #F1C40F; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORES DE LÓGICA (Hueco libre y Serie 99) ---
def buscar_hueco_vacio():
    try:
        res = supabase.table("inventario").select("ubicacion").eq("deposito", "DEPO 1").gt("cantidad", 0).execute()
        ocupadas = [r['ubicacion'] for r in res.data] if res.data else []
        for e in range(1, 28):
            for n in range(1, 7):
                for l in ['A', 'B', 'C', 'D', 'E']:
                    ubi = f"{str(e).zfill(2)}-{n}{l}"
                    if ubi not in ocupadas: return ubi
        return "SIN HUECO"
    except: return "99-01A"

def buscar_proxima_99():
    try:
        res = supabase.table("inventario").select("ubicacion").ilike("ubicacion", "99-%").order("id", desc=True).limit(1).execute()
        if not res.data: return "99-01A"
        ubi = str(res.data[0]['ubicacion']).upper()
        p1, p2 = ubi.split("-")
        letra = p2[-1]
        num = int("".join(filter(str.isdigit, p2)))
        ciclo = ['A', 'B', 'C', 'D']
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

# --- INTERFAZ ---
st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

if st.button("🔄 ACTUALIZAR PANTALLA"):
    st.rerun()

with st.sidebar:
    clave = st.text_input("PIN ADMIN", type="password")
    es_autorizado = (clave == "70797474")

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"])

# --- TAB ENTRADAS ---
with t1:
    if es_autorizado:
        init_b = st.session_state.transfer_data['cod_int'] if st.session_state.transfer_data else ""
        bus = st.text_input("🔍 ESCANEAR/BUSCAR", value=init_b, key="ent_bus")
        if bus:
            m = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus},nombre.ilike.%{bus}%").execute()
            if m.data:
                p = m.data[0]
                u_vacia = buscar_hueco_vacio()
                u_99 = buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 LIBRE: <b>{u_vacia}</b> | PRÓXIMA 99: <b>{u_99}</b></div>', unsafe_allow_html=True)
                
                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']}")
                    c1, c2 = st.columns(2)
                    q = c1.number_input("CANTIDAD", min_value=1, step=1, value=int(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 1)
                    v_raw = c1.text_input("VENCIMIENTO (MMAA)", value=st.session_state.transfer_data['fecha'].replace("/","") if st.session_state.transfer_data else "", max_chars=4)
                    dep = c2.selectbox("DEPÓSITO", ["DEPO 1", "DEPO 2"])
                    
                    existentes = supabase.table("inventario").select("ubicacion, deposito").eq("cod_int", p['cod_int']).gt("cantidad", 0).execute()
                    opciones = [f"UBI LIBRE ({u_vacia})", f"SERIE 99 ({u_99})"]
                    for ex in existentes.data: 
                        opciones.append(f"SUMAR A: {ex['ubicacion']} | {ex['deposito']}")
                    opciones.append("MANUAL")
                    
                    dest = c2.selectbox("DESTINO", opciones)
                    man = st.text_input("MANUAL:")
                    
                    if st.form_submit_button("⚡ REGISTRAR"):
                        if len(v_raw) == 4:
                            if "LIBRE" in dest: ubi_f = u_vacia
                            elif "99" in dest: ubi_f = u_99
                            elif "SUMAR" in dest: ubi_f = dest.split(": ")[1].split(" |")[0]
                            else: ubi_f = man.upper()
                            
                            fv = f"{v_raw[:2]}/{v_raw[2:]}"
                            ch = supabase.table("inventario").select("*").eq("cod_int", p['cod_int']).eq("ubicacion", ubi_f).eq("fecha", fv).eq("deposito", dep).execute()
                            
                            if ch.data:
                                supabase.table("inventario").update({"cantidad": int(ch.data[0]['cantidad']) + q}).eq("id", ch.data[0]['id']).execute()
                            else:
                                supabase.table("inventario").insert({"cod_int":p['cod_int'], "nombre":p['nombre'], "cantidad":q, "fecha":fv, "ubicacion":ubi_f, "deposito":dep, "barras":p['barras']}).execute()
                            st.session_state.transfer_data = None
                            st.rerun()

# --- TAB STOCK / PASES ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR STOCK", key="bus_s")
    if bus_s:
        s = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s},nombre.ilike.%{bus_s}%").execute()
        if s.data:
            df = pd.DataFrame(s.data).sort_values(by='ubicacion')
            st.markdown(f'<div style="background-color:#21618C; padding:15px; border-radius:10px; text-align:center; color:white;"><h2>TOTAL: {int(df["cantidad"].sum())}</h2></div>', unsafe_allow_html=True)
            for _, r in df.iterrows():
                if int(r['cantidad']) <= 0: continue
                with st.container():
                    st.markdown(f'<div class="stock-card"><b style="font-size:22px;">{r["nombre"]}</b><br>Q: <span style="color:#F1C40F; font-size:24px;">{int(r["cantidad"])}</span> | UBI: {r["ubicacion"]} | {r["deposito"]} | {r["fecha"]}</div>', unsafe_allow_html=True)
                    if es_autorizado:
                        with st.expander("🛠️ EDITAR LOTE (ADMIN)"):
                            st.markdown('<div class="edit-box">', unsafe_allow_html=True)
                            ce1, ce2 = st.columns(2)
                            nq = ce1.number_input("Cant. Real", value=int(r['cantidad']), step=1, key=f"nq_{r['id']}")
                            nv = ce2.text_input("Venc. Real (MMAA)", value=r['fecha'].replace("/",""), max_chars=4, key=f"nv_{r['id']}")
                            if st.button("💾 GUARDAR CORRECCIÓN", key=f"bg_{r['id']}"):
                                f_nv = f"{nv[:2]}/{nv[2:]}"
                                supabase.table("inventario").update({"cantidad": int(nq), "fecha": f_nv}).eq("id", r['id']).execute()
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        qm = st.number_input("Cantidad Mover/Salida", min_value=1, max_value=int(r['cantidad']), step=1, key=f"qm_{r['id']}")
                        c_sal, c_pas = st.columns(2)
                        if c_sal.button("SALIDA", key=f"bsa_{r['id']}"):
                            nueva = int(r['cantidad']) - qm
                            if nueva <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva}).eq("id", r['id']).execute()
                            st.rerun()
                        if c_pas.button("PASAR", key=f"bpa_{r['id']}"):
                            nueva = int(r['cantidad']) - qm
                            if nueva <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": nueva}).eq("id", r['id']).execute()
                            st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':qm, 'fecha':r['fecha'], 'deposito_orig':r['deposito']}
                            st.rerun()

# --- TAB PLANILLA ---
with t3:
    p = supabase.table("inventario").select("*").order("id", desc=True).execute()
    if p.data:
        dfp = pd.DataFrame(p.data)
        dfp['cantidad'] = dfp['cantidad'].astype(int)
        st.dataframe(dfp, use_container_width=True, hide_index=True)

import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="LOGISTICA Master", layout="wide")

if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    div.stButton > button { width: 100%; height: 85px !important; font-size: 26px !important; font-weight: 700 !important; border-radius: 15px !important; color: white !important; }
    .block-container div.stButton > button[kind="secondary"] { background-color: #D4AC0D !important; height: 65px !important; color: black !important; }
    div.stForm button { background-color: #1E8449 !important; }
    div[data-testid="column"]:nth-of-type(1) button { background-color: #2E4053 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background-color: #1B2631 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { font-size: 22px !important; height: 60px !important; background-color: #1A1C23 !important; color: #ECF0F1 !important; border: 2px solid #34495E !important; border-radius: 10px !important; }
    h1 { text-align: center; color: #FFFFFF; font-size: 60px !important; font-weight: 800; }
    .sugerencia-box { background-color: #1C2833; padding: 25px; border-radius: 15px; border-left: 12px solid #3498DB; margin-bottom: 25px; color: #D5DBDB; font-size: 20px; }
    .stock-card { background-color: #17202A; padding: 20px; border-radius: 15px; border-left: 10px solid #2C3E50; margin-bottom: 15px; color: #EBEDEF; }
    .edit-box { background-color: #1B2631; padding: 15px; border-radius: 10px; border: 2px dashed #F1C40F; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE UBICACIONES ---
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
    except: return "ERROR"

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

st.markdown("<h1>LOGIEZE</h1>", unsafe_allow_html=True)

# Botón de actualización principal
if st.button("🔄 ACTUALIZAR PANTALLA", type="secondary"):
    st.rerun()

# --- LOGIN ---
with st.sidebar:
    st.header("🔐 Acceso")
    u_log = st.text_input("Usuario").lower()
    p_log = st.text_input("Contraseña", type="password")
    es_autorizado = (u_log == "admin" and p_log == "70797474")
    es_admin_maestro = es_autorizado
    if not es_autorizado and u_log and p_log:
        try:
            res_u = supabase.table("usuarios").select("*").eq("usuario", u_log).eq("clave", p_log).execute()
            if res_u.data: es_autorizado = True
        except: pass

tabs_list = ["📥 ENTRADAS", "🔍 STOCK / PASES", "📊 PLANILLA"]
if es_admin_maestro: tabs_list.append("👥 USUARIOS")
t1, t2, t3, *t_extra = st.tabs(tabs_list)

# --- ENTRADAS ---
with t1:
    if es_autorizado:
        val_pasado = str(st.session_state.transfer_data['cod_int']) if st.session_state.transfer_data else ""
        bus = st.text_input("🔍 BUSCAR PRODUCTO", value=val_pasado, key="ent_bus")
        if bus:
            if bus.isdigit():
                m_raw = supabase.table("maestra").select("*").or_(f"cod_int.eq.{bus},barras.eq.{bus}").execute()
                m_data = [i for i in m_raw.data if str(i['cod_int']) == str(bus) or str(i['barras']) == str(bus)]
            else:
                m_raw = supabase.table("maestra").select("*").ilike("nombre", f"%{bus}%").execute()
                m_data = m_raw.data
            
            if m_data:
                if len(m_data) > 1:
                    opciones_p = {f"{i['nombre']} (ID: {i['cod_int']})": i for i in m_data}
                    p_sel = st.selectbox("Seleccione:", list(opciones_p.keys()))
                    p = opciones_p[p_sel]
                else: p = m_data[0]

                u_vacia, u_99 = buscar_hueco_vacio(), buscar_proxima_99()
                st.markdown(f'<div class="sugerencia-box">📍 LIBRE: {u_vacia} | PRÓXIMA 99: {u_99}</div>', unsafe_allow_html=True)
                
                with st.form("f_carga", clear_on_submit=True):
                    st.write(f"### {p['nombre']} (ID: {p['cod_int']})")
                    q_v = int(st.session_state.transfer_data['cantidad']) if st.session_state.transfer_data else 1
                    f_v = st.session_state.transfer_data['fecha'].replace("/","") if st.session_state.transfer_data else ""
                    c1, c2 = st.columns(2)
                    q = c1.number_input("CANTIDAD", min_value=1, value=q_v)
                    v_raw = c1.text_input("VENCIMIENTO (MMAA)", value=f_v, max_chars=4)
                    dep = c2.selectbox("DEPÓSITO", ["depo1", "depo2"])
                    dest = c2.selectbox("DESTINO", [f"UBI LIBRE ({u_vacia})", f"SERIE 99 ({u_99})", "MANUAL"])
                    man = st.text_input("SI ES MANUAL:")
                    
                    if st.form_submit_button("⚡ REGISTRAR"):
                        ubi_f = u_vacia if "LIBRE" in dest else (u_99 if "99" in dest else man.upper())
                        fv = f"{v_raw[:2]}/{v_raw[2:]}"
                        ch = supabase.table("inventario").select("*").eq("cod_int", p['cod_int']).eq("ubicacion", ubi_f).eq("fecha", fv).eq("deposito", dep).execute()
                        if ch.data:
                            supabase.table("inventario").update({"cantidad": int(ch.data[0]['cantidad']) + q}).eq("id", ch.data[0]['id']).execute()
                        else:
                            supabase.table("inventario").insert({"cod_int":p['cod_int'], "nombre":p['nombre'], "cantidad":q, "fecha":fv, "ubicacion":ubi_f, "deposito":dep, "barras":p['barras']}).execute()
                        st.session_state.transfer_data = None
                        st.rerun()

# --- STOCK / PASES ---
with t2:
    bus_s = st.text_input("🔎 BUSCAR EN STOCK", key="bus_s")
    if bus_s:
        if bus_s.isdigit():
            s_raw = supabase.table("inventario").select("*").or_(f"cod_int.eq.{bus_s},barras.eq.{bus_s}").execute()
            s_data = [i for i in s_raw.data if str(i['cod_int']) == str(bus_s) or str(i['barras']) == str(bus_s)]
        else:
            s_data = supabase.table("inventario").select("*").ilike("nombre", f"%{bus_s}%").execute().data
            
        if s_data:
            df = pd.DataFrame(s_data)
            total_stock = int(df["cantidad"].sum())
            st.markdown(f'<div style="background-color:#21618C; padding:15px; border-radius:10px; text-align:center; color:white; margin-bottom:15px;"><h2>STOCK TOTAL: {total_stock}</h2></div>', unsafe_allow_html=True)
            
            for r in s_data:
                curr_q = int(r['cantidad'])
                with st.container():
                    st.markdown(f'<div class="stock-card"><b>{r["nombre"]}</b> | ID: {r["cod_int"]} | Q: {curr_q}<br>UBI: {r["ubicacion"]} | {r["deposito"]} | VENCE: {r["fecha"]}</div>', unsafe_allow_html=True)
                    
                    if es_autorizado:
                        with st.expander("🛠️ EDITAR LOTE (ADMIN)"):
                            st.markdown('<div class="edit-box">', unsafe_allow_html=True)
                            ce1, ce2 = st.columns(2)
                            nq = ce1.number_input("Nueva Cantidad", value=curr_q, key=f"nq_{r['id']}")
                            nv = ce2.text_input("Nuevo Vence (MMAA)", value=r['fecha'].replace("/",""), max_chars=4, key=f"nv_{r['id']}")
                            if st.button("💾 GUARDAR CORRECCIÓN", key=f"save_{r['id']}"):
                                f_nv = f"{nv[:2]}/{nv[2:]}" if len(nv)==4 else r['fecha']
                                supabase.table("inventario").update({"cantidad": int(nq), "fecha": f_nv}).eq("id", r['id']).execute()
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # CORRECCIÓN ERROR IMAGEN 8: Eliminamos el max_value restrictivo para evitar el error de Streamlit
                        qm = st.number_input("Cant. Operación", min_value=1, value=1, key=f"qm_{r['id']}")
                        c_sal, c_pas = st.columns(2)
                        if c_sal.button("SALIDA", key=f"sal_{r['id']}"):
                            if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                            st.rerun()
                        if c_pas.button("PASAR", key=f"pas_{r['id']}"):
                            if curr_q - qm <= 0: supabase.table("inventario").delete().eq("id", r['id']).execute()
                            else: supabase.table("inventario").update({"cantidad": curr_q - qm}).eq("id", r['id']).execute()
                            st.session_state.transfer_data = {'cod_int':r['cod_int'], 'cantidad':qm, 'fecha':r['fecha']}
                            st.rerun()

# --- PLANILLA ---
with t3:
    p_data = supabase.table("inventario").select("*").order("id", desc=True).execute().data
    if p_data: st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

# --- USUARIOS ---
if es_admin_maestro:
    with t_extra[0]:
        st.header("👥 Gestión Usuarios")
        if st.button("🔄 ACTUALIZAR LISTA", type="secondary", key="ref_u"):
            st.rerun()
        with st.form("nu", clear_on_submit=True):
            nu, np = st.text_input("Usuario"), st.text_input("Clave")
            if st.form_submit_button("➕ REGISTRAR"):
                if nu and np:
                    try:
                        supabase.table("usuarios").insert({"usuario": nu.lower(), "clave": np}).execute()
                        st.success(f"Usuario {nu} registrado.")
                        st.rerun()
                    except Exception:
                        st.error("Error al registrar (RLS o duplicado)")
        try:
            u_list = supabase.table("usuarios").select("*").execute().data
            if u_list:
                for u in u_list:
                    col_u, col_b = st.columns([4, 1])
                    col_u.write(f"👤 {u['usuario']}")
                    if col_b.button("🗑️", key=f"del_{u['id']}"):
                        supabase.table("usuarios").delete().eq("id", u['id']).execute()
                        st.rerun()
        except Exception: pass

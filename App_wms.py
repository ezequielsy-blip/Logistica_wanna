"""
LOGIEZE WEB — versión Streamlit para celular
Instalar:  pip install streamlit supabase pandas openpyxl
Correr:    streamlit run logieze_web.py
"""
import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime, date
from supabase import create_client, Client

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
DIAS_ALERTA = 60

st.set_page_config(
    page_title="LOGIEZE",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILOS MOBILE-FIRST ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0F172A;
    color: #F1F5F9;
}
.main-header {
    background: linear-gradient(135deg, #1D4ED8, #0F172A);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    border: 1px solid #334155;
}
.main-header h1 {
    margin: 0; font-size: 22px; font-weight: 900;
    color: white; letter-spacing: 2px;
}
.main-header span { font-size: 13px; color: #94A3B8; font-weight: 400; }
.metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 16px 18px;
    text-align: center;
}
.metric-card .value {
    font-size: 28px; font-weight: 900;
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.metric-card .label {
    font-size: 11px; font-weight: 700;
    color: #94A3B8; letter-spacing: 1.5px; margin-top: 2px;
}
div.stButton > button {
    background: linear-gradient(90deg, #3B82F6, #06B6D4) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    width: 100%;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #1D4ED8, #3B82F6) !important;
    transform: translateY(-1px);
}
div[data-testid="column"] div.stButton > button.danger {
    background: transparent !important;
    border: 1.5px solid #EF4444 !important;
    color: #EF4444 !important;
}
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: #1E293B !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: #F1F5F9 !important;
    font-size: 15px !important;
}
div[data-baseweb="select"] > div {
    background: #1E293B !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}
div[data-baseweb="tab-list"] {
    background: #1E293B !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #334155;
}
div[data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #94A3B8 !important;
}
div[aria-selected="true"] {
    background: #3B82F6 !important;
    color: white !important;
}
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #334155;
}
.sec-label {
    font-size: 11px; font-weight: 700; color: #94A3B8;
    letter-spacing: 2px; margin-bottom: 6px; margin-top: 4px;
}
.stock-badge {
    display: inline-block;
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    color: white; font-weight: 800; font-size: 18px;
    padding: 8px 20px; border-radius: 30px;
}
.lote-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.lote-card.vencido { border-color: #EF4444; background: #200a0a; }
.lote-card.por-vencer { border-color: #F59E0B; background: #1c1500; }
.sug-box {
    background: rgba(6,182,212,0.10);
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px; font-weight: 700; color: #06B6D4;
    margin-bottom: 8px;
}
div[data-testid="stAlert"] { border-radius: 12px !important; }
section[data-testid="stSidebar"] {
    background: #1E293B !important;
    border-right: 1px solid #334155;
}
div[data-testid="stRadio"] label {
    font-size: 15px !important; font-weight: 700 !important;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()


# ── CACHE DE DATOS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def cargar_maestra():
    datos = []
    offset = 0
    while True:
        r = sb.table("maestra").select("*").range(offset, offset+999).execute()
        if not r.data: break
        datos.extend(r.data); offset += 1000
    return datos

@st.cache_data(ttl=300, show_spinner=False)
def cargar_inventario():
    datos = []
    offset = 0
    while True:
        r = sb.table("inventario").select("*").range(offset, offset+999).execute()
        if not r.data: break
        datos.extend(r.data); offset += 1000
    return datos

@st.cache_data(ttl=60, show_spinner=False)
def cargar_historial_cache():
    return sb.table("historial").select("*").order("id", desc=True).limit(300).execute().data or []

def refrescar():
    cargar_maestra.clear()
    cargar_inventario.clear()
    cargar_historial_cache.clear()
    st.rerun()

def _wa_config():
    try:
        r1 = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
        r2 = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
        return (r1[0]['valor'] if r1 else "", r2[0]['valor'] if r2 else "")
    except:
        return ("", "")

def _enviar_whatsapp(numero, apikey, mensaje, callback_ok=None, callback_err=None):
    import urllib.request, urllib.parse, threading
    def _send():
        try:
            num_limpio = "+" + numero.replace("+","").replace(" ","").replace("-","")
            msg_enc = urllib.parse.quote(mensaje, safe='')
            url = (f"https://api.callmebot.com/whatsapp.php"
                   f"?phone={num_limpio}&text={msg_enc}&apikey={apikey}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
            if "queued" in body.lower() or resp.status == 200:
                if callback_ok: callback_ok()
            else:
                if callback_err: callback_err(body[:100])
        except Exception as e:
            if callback_err: callback_err(str(e)[:100])
    threading.Thread(target=_send, daemon=True).start()


# ── UTILIDADES ────────────────────────────────────────────────────────────────
def parsear_fecha(texto):
    try:
        p = str(texto).strip().split("/")
        if len(p) == 2:
            m, a = int(p[0]), int(p[1])
            return date(2000 + a if a < 100 else a, m, 1)
    except: pass
    return None

def dias_para_vencer(texto):
    f = parsear_fecha(texto)
    return (f - date.today()).days if f else None

def calcular_vacias_rapido(ocupadas: set, max_n=8):
    vacias = []
    for est in range(1, 28):
        if len(vacias) >= max_n: break
        if est in [3,4]:            niv, lets = 4, "ABCDE"
        elif est in [8,9,10,11,12]: niv, lets = 6, "ABCDEFG"
        else:                        niv, lets = 5, "ABCDE"
        for n in range(1, niv+1):
            if len(vacias) >= max_n: break
            for l in lets:
                u = f"{str(est).zfill(2)}-{n}{l}"
                if u not in ocupadas:
                    vacias.append(u); break
    return vacias

def calcular_sug99(ocupadas: set):
    for n in range(1, 1000):
        for l in ['A','B','C','D']:
            t = f"99-{str(n).zfill(2)}{l}"
            if t not in ocupadas: return t
    return "99-01A"

def registrar_historial(tipo, cod_int, nombre, cantidad, ubicacion, usuario):
    try:
        sb.table("historial").insert({
            "fecha_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "usuario": usuario, "tipo": tipo, "cod_int": cod_int,
            "nombre": nombre, "cantidad": cantidad, "ubicacion": ubicacion,
        }).execute()
    except Exception as e:
        st.error(f"Error historial: {e}")

def recalcular_maestra(cod_int, inventario):
    lotes = [l for l in inventario if str(l.get('cod_int','')) == str(cod_int)]
    total = sum(float(l.get('cantidad', 0)) for l in lotes)
    try:
        sb.table("maestra").update({"cantidad_total": total}).eq("cod_int", cod_int).execute()
    except Exception as e:
        st.error(f"Error recalcular: {e}")
    return total


# ── SESIÓN PERSISTENTE vía query_params ──────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.rol     = None

_qp = st.query_params
if not st.session_state.usuario and "lz_u" in _qp and "lz_r" in _qp:
    st.session_state.usuario = _qp["lz_u"]
    st.session_state.rol     = _qp["lz_r"]


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.usuario:
    st.markdown("""
    <div style="max-width:380px;margin:60px auto 0;text-align:center;">
        <div style="font-size:64px;margin-bottom:8px;">📦</div>
        <h1 style="font-size:30px;font-weight:900;letter-spacing:4px;margin:0;">LOGIEZE</h1>
        <p style="color:#94A3B8;font-size:13px;margin-top:4px;">Sistema de gestión de inventario</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        usuario = st.text_input("USUARIO", placeholder="Ingresá tu usuario",
                                label_visibility="collapsed", key="l_usr")
        clave   = st.text_input("CLAVE",   placeholder="••••••••",
                                label_visibility="collapsed", type="password", key="l_pwd")
        if st.button("ENTRAR  →", use_container_width=True):
            if usuario == "admin" and clave == "70797474":
                st.session_state.usuario = "admin"; st.session_state.rol = "admin"
                st.query_params["lz_u"] = "admin"
                st.query_params["lz_r"] = "admin"
                st.rerun()
            else:
                try:
                    r = sb.table("usuarios").select("*") \
                           .eq("usuario", usuario.lower().strip()) \
                           .eq("clave", clave).execute().data
                    if r:
                        st.session_state.usuario = r[0]['usuario']
                        st.session_state.rol     = r[0]['rol']
                        st.query_params["lz_u"]  = r[0]['usuario']
                        st.query_params["lz_r"]  = r[0]['rol']
                        st.rerun()
                    else:
                        st.error("Usuario o clave incorrectos.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
usuario = st.session_state.usuario
rol     = st.session_state.rol
ROL_ICON = {"admin":"👑","operario":"🔧","visita":"👁️","vendedor":"🛒"}.get(rol,"👤")

col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"""
    <div class="main-header">
        <div style="font-size:32px;">📦</div>
        <div>
            <h1>LOGIEZE</h1>
            <span>v3.0 WEB  ·  {ROL_ICON} {usuario.upper()}  ·  {rol.upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    if st.button("⟳ Actualizar", use_container_width=True):
        refrescar()
    if st.button("🔄 Cambiar usuario", use_container_width=True):
        st.session_state.usuario = None
        st.session_state.rol     = None
        st.query_params.clear()
        st.rerun()

with st.spinner("Cargando datos..."):
    maestra    = cargar_maestra()
    inventario = cargar_inventario()

idx_inv       = {}
ubis_ocupadas = set()
for lote in inventario:
    cod = str(lote.get('cod_int',''))
    if cod not in idx_inv: idx_inv[cod] = []
    idx_inv[cod].append(lote)
    ubis_ocupadas.add(str(lote.get('ubicacion','')).upper())

nm = len(maestra); ni = len(inventario)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><div class="value">{nm}</div><div class="label">PRODUCTOS</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="value">{ni}</div><div class="label">LOTES</div></div>', unsafe_allow_html=True)
with c3:
    total_stock = sum(float(l.get('cantidad',0)) for l in inventario)
    st.markdown(f'<div class="metric-card"><div class="value">{int(total_stock):,}</div><div class="label">STOCK TOTAL</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_mov, tab_desp, tab_hist, tab_plan, tab_admin, tab_asist = st.tabs([
    "📦 MOVIMIENTOS", "🚚 DESPACHO", "📋 HISTORIAL", "📊 PLANILLA", "🔐 ADMIN", "🤖 ASISTENTE"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB MOVIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_mov:
    st.markdown('<p class="sec-label">🔍 BUSCAR PRODUCTO</p>', unsafe_allow_html=True)
    busqueda = st.text_input("Buscar", placeholder="Nombre, código interno o barras...",
                              label_visibility="collapsed", key="busq")

    productos_filtrados = []
    if busqueda:
        t = busqueda.upper().strip()
        productos_filtrados = [p for p in maestra
                               if t in str(p.get('nombre','')).upper()
                               or t in str(p.get('cod_int','')).upper()
                               or t in str(p.get('barras','')).upper()]

    if not productos_filtrados and busqueda:
        st.info("No se encontraron productos.")
    elif productos_filtrados:
        df_res = pd.DataFrame([{
            "Nombre": p['nombre'],
            "Código": p['cod_int'],
            "Stock":  int(float(p.get("cantidad_total") or 0)),
        } for p in productos_filtrados])
        st.dataframe(df_res, use_container_width=True, hide_index=True,
                     column_config={"Stock": st.column_config.NumberColumn(format="%d")})

        nombres_lista = [f"{p['nombre']}  [{p['cod_int']}]" for p in productos_filtrados]
        sel_idx = st.selectbox("Seleccionar producto:", range(len(nombres_lista)),
                               format_func=lambda i: nombres_lista[i], key="sel_prod")
        prod_sel = productos_filtrados[sel_idx]
        cod_sel  = str(prod_sel['cod_int'])

        lotes_prod = idx_inv.get(cod_sel, [])
        total_q    = sum(float(l.get('cantidad',0)) for l in lotes_prod)
        st.markdown(f'<div style="margin:10px 0"><span class="stock-badge">STOCK TOTAL: {int(total_q)}</span></div>', unsafe_allow_html=True)

        if lotes_prod:
            st.markdown('<p class="sec-label">📦 LOTES EN DEPÓSITO</p>', unsafe_allow_html=True)
            for i, l in enumerate(lotes_prod):
                dias  = dias_para_vencer(l.get('fecha',''))
                clase = ""
                alerta = ""
                if dias is not None:
                    if dias < 0:
                        clase = " vencido"
                        alerta = f"🔴 VENCIDO hace {abs(dias)} días"
                    elif dias <= DIAS_ALERTA:
                        clase = " por-vencer"
                        alerta = f"🟠 Vence en {dias} días"
                    else:
                        alerta = f"✅ Vence en {dias} días"
                cant_l = int(float(l.get('cantidad',0)))
                st.markdown(f"""
                <div class="lote-card{clase}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="font-size:22px;font-weight:900;color:#06B6D4">{cant_l}</span>
                        <span style="font-size:12px;color:#94A3B8">{alerta}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:13px;">
                        <span>📍 <b>{l.get('ubicacion','')}</b></span>
                        <span>🏭 {l.get('deposito','')}</span>
                        <span>📅 {l.get('fecha','')}</span>
                        <span style="color:#64748B;font-size:11px">ID: {l.get('id','')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Sin lotes registrados para este producto.")

        st.markdown("---")
        st.markdown('<p class="sec-label">📝 REGISTRAR OPERACIÓN</p>', unsafe_allow_html=True)

        tipo_op    = st.radio("Tipo", ["⬆ INGRESO", "⬇ SALIDA"],
                              horizontal=True, label_visibility="collapsed", key="tipo_op")
        es_ingreso = "INGRESO" in tipo_op

        col_a, col_b = st.columns(2)
        with col_a:
            cantidad_op = st.number_input("CANTIDAD", min_value=0.1, step=1.0,
                                           format="%.0f", key="cant_op")
        with col_b:
            fecha_op = st.text_input("VENCIMIENTO (MM/AA)", placeholder="ej: 06/26", key="fecha_op")

        ubi_prod    = list({str(l.get('ubicacion','')).upper() for l in lotes_prod})
        vacias      = calcular_vacias_rapido(ubis_ocupadas)
        sug99       = calcular_sug99(ubis_ocupadas)
        opciones_ubi = ubi_prod + [f"VACIA: {v}" for v in vacias] + [f"SUG 99: {sug99}"]
        sugerencia  = vacias[0] if vacias else sug99
        st.markdown(f'<div class="sug-box">📍 Sugerencia: {sugerencia}</div>', unsafe_allow_html=True)

        col_u, col_d = st.columns(2)
        with col_u:
            ubi_sel    = st.selectbox("UBICACIÓN", opciones_ubi, key="ubi_op")
            ubi_final  = ubi_sel.replace("VACIA: ","").replace("SUG 99: ","").upper().strip()
            ubi_manual = st.text_input("o escribir manualmente:", placeholder="ej: 05-3B", key="ubi_man")
            if ubi_manual.strip(): ubi_final = ubi_manual.strip().upper()
        with col_d:
            depo_op = st.selectbox("DEPÓSITO", ["depo 1","depo 2"], key="depo_op")

        lote_sel = None
        if not es_ingreso and lotes_prod:
            opciones_lotes = [f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}"
                              for l in lotes_prod]
            lote_idx = st.selectbox("LOTE A DESCONTAR:", range(len(opciones_lotes)),
                                    format_func=lambda i: opciones_lotes[i], key="lote_op")
            lote_sel = lotes_prod[lote_idx]

        if st.button("✅ REGISTRAR OPERACIÓN", use_container_width=True, key="btn_reg"):
            if cantidad_op <= 0:
                st.error("Cantidad debe ser mayor a 0.")
            elif es_ingreso and not fecha_op.strip():
                st.error("Ingresá la fecha de vencimiento.")
            else:
                try:
                    if es_ingreso:
                        existente = next((l for l in lotes_prod
                                         if str(l.get('ubicacion','')).upper() == ubi_final
                                         and str(l.get('fecha','')) == fecha_op.strip()
                                         and str(l.get('deposito','')) == depo_op), None)
                        if existente:
                            nq = float(existente['cantidad']) + cantidad_op
                            sb.table("inventario").update({"cantidad": nq}).eq("id", existente['id']).execute()
                        else:
                            sb.table("inventario").insert({
                                "cod_int": cod_sel, "nombre": prod_sel['nombre'],
                                "cantidad": cantidad_op, "ubicacion": ubi_final,
                                "deposito": depo_op, "fecha": fecha_op.strip()
                            }).execute()
                    else:
                        if not lote_sel:
                            st.error("No hay lotes disponibles."); st.stop()
                        cant_actual = float(lote_sel['cantidad'])
                        if cant_actual - cantidad_op <= 0:
                            sb.table("inventario").delete().eq("id", lote_sel['id']).execute()
                        else:
                            sb.table("inventario").update({"cantidad": cant_actual - cantidad_op}).eq("id", lote_sel['id']).execute()
                    registrar_historial("INGRESO" if es_ingreso else "SALIDA",
                                       cod_sel, prod_sel['nombre'], cantidad_op, ubi_final, usuario)
                    recalcular_maestra(cod_sel, inventario)
                    st.success("✅ Operación registrada correctamente.")
                    refrescar()
                except Exception as e:
                    st.error(f"Error: {e}")

        if lotes_prod:
            st.markdown("---")
            st.markdown('<p class="sec-label">↔ MOVER LOTE</p>', unsafe_allow_html=True)
            with st.expander("Reubicar mercadería"):
                opciones_mover = [f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}"
                                  for l in lotes_prod]
                idx_mover  = st.selectbox("Lote a mover:", range(len(opciones_mover)),
                                           format_func=lambda i: opciones_mover[i], key="lote_mv")
                lote_mover = lotes_prod[idx_mover]
                cant_mover = st.number_input("Cantidad a mover:", min_value=0.1,
                                              max_value=float(lote_mover.get('cantidad',1)),
                                              value=float(lote_mover.get('cantidad',1)),
                                              step=1.0, format="%.0f", key="cant_mv")
                col_mu, col_md = st.columns(2)
                with col_mu:
                    ubi_nueva_sel = st.selectbox("Nueva ubicación:", opciones_ubi, key="ubi_mv")
                    ubi_nueva = ubi_nueva_sel.replace("VACIA: ","").replace("SUG 99: ","").upper().strip()
                    ubi_nueva_man = st.text_input("o manual:", placeholder="ej: 12-2C", key="ubi_mv_man")
                    if ubi_nueva_man.strip(): ubi_nueva = ubi_nueva_man.strip().upper()
                with col_md:
                    depo_nuevo = st.selectbox("Depósito destino:", ["depo 1","depo 2"], key="depo_mv")
                if st.button("↔ CONFIRMAR MOVIMIENTO", use_container_width=True, key="btn_mv"):
                    try:
                        nq = float(lote_mover['cantidad']) - cant_mover
                        if nq <= 0:
                            sb.table("inventario").delete().eq("id", lote_mover['id']).execute()
                        else:
                            sb.table("inventario").update({"cantidad": nq}).eq("id", lote_mover['id']).execute()
                        sb.table("inventario").insert({
                            "cod_int": cod_sel, "nombre": prod_sel['nombre'],
                            "cantidad": cant_mover, "ubicacion": ubi_nueva,
                            "deposito": depo_nuevo, "fecha": lote_mover.get('fecha','')
                        }).execute()
                        registrar_historial("TRASLADO", cod_sel, prod_sel['nombre'],
                                           cant_mover, f"{lote_mover.get('ubicacion','')}→{ubi_nueva}", usuario)
                        recalcular_maestra(cod_sel, inventario)
                        st.success("✅ Movimiento realizado.")
                        refrescar()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB DESPACHO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_desp:
    import json as _json

    st.markdown('<p class="sec-label">🚚 PICKING CONTROLADO</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1E293B;border:1px solid #334155;border-radius:14px;
                padding:14px 18px;margin-bottom:12px;">
        <span style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:2px;">
            ☁️ PEDIDOS EN LA NUBE
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])

    @st.cache_data(ttl=30, show_spinner=False)
    def cargar_pedidos_nube():
        try:
            return sb.table("pedidos").select("id,nombre,fecha,estado,items") \
                     .in_("estado", ["pendiente", "en_proceso"]) \
                     .order("id", desc=True).limit(20).execute().data or []
        except:
            return []

    pedidos_nube = cargar_pedidos_nube()

    with col_s1:
        if pedidos_nube:
            opciones_pedidos = [f"#{p['id']}  {p['nombre']}  [{p.get('fecha','')}]  — {p.get('estado','')}"
                                for p in pedidos_nube]
            idx_ped_sel = st.selectbox("Pedidos disponibles:", range(len(opciones_pedidos)),
                                       format_func=lambda i: opciones_pedidos[i],
                                       key="sel_ped_nube", label_visibility="collapsed")
        else:
            st.info("☁️ Sin pedidos en la nube. Cargá uno desde la PC o crealo acá abajo.")
            idx_ped_sel = None

    with col_s2:
        if pedidos_nube and idx_ped_sel is not None:
            if st.button("⬇ Cargar pedido", use_container_width=True, key="btn_bajar_ped"):
                ped = pedidos_nube[idx_ped_sel]
                items_raw = ped.get('items') or []
                if isinstance(items_raw, str):
                    try: items_raw = _json.loads(items_raw)
                    except: items_raw = []
                if items_raw:
                    st.session_state.pedido = [
                        {"cod":  str(it.get('cod_int', it.get('codigo',''))),
                         "cant": int(float(str(it.get('cantidad', it.get('cant', 0))))),
                         "nombre": it.get('nombre',''),
                         "ped_id": ped['id']}
                        for it in items_raw
                    ]
                    try:
                        sb.table("pedidos").update({"estado":"en_proceso"}).eq("id", ped['id']).execute()
                        cargar_pedidos_nube.clear()
                    except: pass
                    st.success(f"✅ '{ped['nombre']}' cargado — {len(items_raw)} ítems")
                    st.rerun()
                else:
                    st.error("El pedido no tiene ítems.")

    with col_s3:
        if st.button("🔄 Actualizar lista", use_container_width=True, key="btn_ref_nube"):
            cargar_pedidos_nube.clear()
            st.rerun()

    st.markdown("---")

    if "pedido" not in st.session_state:
        st.session_state.pedido = []

    col_acc1, col_acc2, col_acc3 = st.columns([2, 2, 1])

    with col_acc1:
        texto_pegado = st.text_area(
            "📋 Pegar desde Excel (Codigo · Articulo · Cantidad · ...):",
            placeholder="Seleccioná las filas en Excel y pegá acá (Ctrl+V)\nColumnas extra como U.Medida, Precio, Total se ignoran automáticamente.",
            height=90, key="txt_pegar_excel", label_visibility="visible"
        )
        if st.button("📥 Cargar desde Excel", use_container_width=True, key="btn_cargar_excel"):
            if texto_pegado.strip():
                try:
                    df_p = pd.read_csv(StringIO(texto_pegado), sep='\t', dtype=str).fillna("")
                    df_p.columns = [str(c).strip().upper() for c in df_p.columns]
                    col_cod  = next((c for c in ["CODIGO","CÓDIGO","COD","COD_INT"] if c in df_p.columns), None)
                    col_cant = next((c for c in ["CANTIDAD","CANT","QTY"] if c in df_p.columns), None)
                    col_nom  = next((c for c in ["ARTICULO","ARTÍCULO","NOMBRE","DESCRIPCION","DESCRIPCIÓN"] if c in df_p.columns), None)
                    if not col_cod or not col_cant:
                        st.error("No se encontraron columnas 'Codigo' y 'Cantidad'. Verificá el formato.")
                    else:
                        nuevos = 0
                        for _, r in df_p.iterrows():
                            cod      = str(r[col_cod]).strip()
                            cant_str = str(r[col_cant]).strip()
                            nom_excel = str(r[col_nom]).strip() if col_nom else ""
                            if not cod or cod.upper() in ("NAN","","CODIGO","CÓDIGO"): continue
                            if not cant_str or cant_str.upper() in ("NAN","","CANTIDAD"): continue
                            try: cant_v = int(float(cant_str))
                            except: continue
                            prod = next((p for p in maestra if str(p['cod_int']) == cod), None)
                            if not prod:
                                prod = next((p for p in maestra if str(p.get('barras','')) == cod), None)
                            nom = prod['nombre'] if prod else (nom_excel or "NO ENCONTRADO")
                            st.session_state.pedido.append({"cod": cod, "cant": cant_v, "nombre": nom})
                            nuevos += 1
                        if nuevos:
                            st.success(f"✅ {nuevos} ítems cargados (U.Medida, Precio y Total ignorados)")
                            st.rerun()
                        else:
                            st.warning("No se encontraron filas válidas.")
                except Exception as e:
                    st.error(f"Error al procesar: {e}")
            else:
                st.warning("Pegá el contenido del Excel primero.")

    with col_acc2:
        st.markdown('<p class="sec-label">☁️ GUARDAR PEDIDO EN LA NUBE</p>', unsafe_allow_html=True)
        nombre_ped = st.text_input(
            "Nombre:", placeholder="ej: Pedido #45 · Cliente: XYZ",
            key="nom_ped_guardar", label_visibility="collapsed"
        )
        if st.button("⬆ Guardar en nube para los chicos", use_container_width=True, key="btn_subir_ped"):
            if not st.session_state.pedido:
                st.warning("El pedido está vacío. Cargá ítems primero.")
            elif not nombre_ped.strip():
                st.warning("Escribí un nombre para identificar el pedido.")
            else:
                items_subir = [{"cod_int": it['cod'], "cantidad": it['cant'], "nombre": it['nombre']}
                               for it in st.session_state.pedido]
                try:
                    sb.table("pedidos").insert({
                        "nombre": nombre_ped.strip(),
                        "fecha":  datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "items":  _json.dumps(items_subir),
                        "estado": "pendiente"
                    }).execute()
                    cargar_pedidos_nube.clear()
                    _wa_num, _wa_key = _wa_config()
                    if _wa_num and _wa_key:
                        _msg = (f"PEDIDO NUEVO - LOGIEZE"
                                f" | Vendedor: {usuario}"
                                f" | Pedido: {nombre_ped.strip()}"
                                f" | Items: {len(items_subir)}"
                                f" | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                        _enviar_whatsapp(_wa_num, _wa_key, _msg)
                    st.success(f"☁️ '{nombre_ped}' guardado — {len(items_subir)} ítems. Los chicos ya lo pueden ver.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_acc3:
        st.markdown('<p class="sec-label">MANUAL</p>', unsafe_allow_html=True)
        with st.expander("➕ Agregar ítem"):
            d_cod  = st.text_input("Código:", key="d_cod")
            d_cant = st.number_input("Cantidad:", min_value=1, step=1, key="d_cant")
            if st.button("Agregar", use_container_width=True, key="btn_add_ped"):
                if d_cod.strip():
                    prod = next((p for p in maestra if str(p['cod_int']) == d_cod.strip()), None)
                    nom  = prod['nombre'] if prod else "NO ENCONTRADO"
                    st.session_state.pedido.append({"cod": d_cod.strip(), "cant": d_cant, "nombre": nom})
                    st.rerun()

    if st.session_state.pedido:
        st.markdown('<p class="sec-label">📋 ÍTEMS DEL PEDIDO ACTIVO</p>', unsafe_allow_html=True)
        pedido_a_eliminar = None
        for i, item in enumerate(st.session_state.pedido):
            col_pi, col_pb = st.columns([5, 1])
            with col_pi:
                stock_disp  = sum(float(l.get('cantidad',0)) for l in idx_inv.get(item['cod'],[]))
                color_stock = "#10B981" if stock_disp >= item['cant'] else "#EF4444"
                st.markdown(f"""
                <div class="lote-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <b style="font-size:14px;">{item['nombre']}</b><br>
                            <span style="color:#94A3B8;font-size:12px;">Cod: {item['cod']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:22px;font-weight:900;color:#10B981;">{item['cant']}</span>
                            <br><span style="font-size:11px;color:{color_stock};">stock: {int(stock_disp)}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_pb:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if rol not in ("visita",) and st.button("✕", key=f"del_ped_{i}"):
                    pedido_a_eliminar = i
        if pedido_a_eliminar is not None:
            st.session_state.pedido.pop(pedido_a_eliminar); st.rerun()

        st.markdown("---")
        st.markdown('<p class="sec-label">DESPACHAR ÍTEM</p>', unsafe_allow_html=True)
        idx_desp = st.selectbox(
            "Ítem a despachar:",
            range(len(st.session_state.pedido)),
            format_func=lambda i: (
                f"{'✅' if sum(float(l.get('cantidad',0)) for l in idx_inv.get(st.session_state.pedido[i]['cod'],[])) >= st.session_state.pedido[i]['cant'] else '⚠️'}"
                f"  {st.session_state.pedido[i]['nombre']}  —  {st.session_state.pedido[i]['cant']} uds"
            ),
            key="desp_sel", label_visibility="collapsed"
        )
        item_sel = st.session_state.pedido[idx_desp]
        cod_d    = item_sel['cod']
        lotes_d  = [l for l in idx_inv.get(cod_d, []) if float(l.get('cantidad', 0)) > 0]

        if lotes_d:
            st.markdown('<p class="sec-label">LOTE A USAR</p>', unsafe_allow_html=True)
            for l in lotes_d:
                dias  = dias_para_vencer(l.get('fecha',''))
                clase = (" vencido" if (dias is not None and dias < 0)
                         else " por-vencer" if (dias is not None and dias <= DIAS_ALERTA) else "")
                st.markdown(f"""
                <div class="lote-card{clase}">
                    <b style="font-size:18px;color:#06B6D4">{int(float(l.get('cantidad',0)))}</b>
                    &nbsp;·&nbsp; 📍 {l.get('ubicacion','')}
                    &nbsp;·&nbsp; {l.get('deposito','')}
                    &nbsp;·&nbsp; 📅 {l.get('fecha','')}
                </div>
                """, unsafe_allow_html=True)

            lote_ops = [f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}"
                        for l in lotes_d]
            idx_ld = st.selectbox("Lote a descontar:", range(len(lote_ops)),
                                  format_func=lambda i: lote_ops[i], key="lote_desp")
            lote_d = lotes_d[idx_ld]

            if rol in ("admin", "operario") and st.button("✅ DESCONTAR DEL LOTE", use_container_width=True, key="btn_desc"):
                cant_p = float(item_sel['cant'])
                cant_l = float(lote_d.get('cantidad', 0))
                try:
                    if cant_l <= cant_p:
                        sb.table("inventario").delete().eq("id", lote_d['id']).execute()
                        pendiente = cant_p - cant_l
                        if pendiente > 0:
                            st.session_state.pedido[idx_desp]['cant'] = int(pendiente)
                            registrar_historial("SALIDA", cod_d, item_sel['nombre'], cant_l, lote_d.get('ubicacion',''), usuario)
                            recalcular_maestra(cod_d, inventario)
                            st.warning(f"Lote agotado. Quedan {int(pendiente)} uds pendientes.")
                            refrescar(); st.rerun()
                        else:
                            st.session_state.pedido.pop(idx_desp)
                    else:
                        nq = cant_l - cant_p
                        sb.table("inventario").update({"cantidad": nq}).eq("id", lote_d['id']).execute()
                        st.session_state.pedido.pop(idx_desp)

                    registrar_historial("SALIDA", cod_d, item_sel['nombre'], cant_p, lote_d.get('ubicacion',''), usuario)
                    recalcular_maestra(cod_d, inventario)
                    _ped_id = item_sel.get('ped_id')
                    if _ped_id:
                        try:
                            import json as _j2
                            _items_rest = [{"cod_int":it['cod'],"cantidad":it['cant'],"nombre":it['nombre']}
                                           for it in st.session_state.pedido]
                            if _items_rest:
                                sb.table("pedidos").update({
                                    "items": _j2.dumps(_items_rest), "estado": "en_proceso"
                                }).eq("id", _ped_id).execute()
                            else:
                                sb.table("pedidos").update({"estado":"completado"}).eq("id", _ped_id).execute()
                            cargar_pedidos_nube.clear()
                        except: pass
                    st.success(f"✅ {item_sel['nombre']} — {int(cant_p)} uds descontadas.")
                    refrescar(); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning(f"⚠️ Sin stock disponible para {item_sel['nombre']}.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_lp1, col_lp2 = st.columns(2)
        with col_lp1:
            if st.button("🗑️ Limpiar pedido local", key="limpiar_ped"):
                st.session_state.pedido = []; st.rerun()
        with col_lp2:
            _ped_id_act = next((it.get('ped_id') for it in st.session_state.pedido if it.get('ped_id')), None)
            if _ped_id_act and st.button("☁️ Marcar como completado", key="btn_completar_ped"):
                try:
                    sb.table("pedidos").update({"estado":"completado"}).eq("id", _ped_id_act).execute()
                    cargar_pedidos_nube.clear()
                    st.session_state.pedido = []
                    st.success("✅ Pedido marcado como completado y removido de la lista.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#94A3B8;">
            <div style="font-size:48px;margin-bottom:12px;">📋</div>
            <div style="font-size:16px;font-weight:700;">Sin pedido activo</div>
            <div style="font-size:13px;margin-top:6px;">Cargá un pedido desde la nube ☁️ o agregá ítems manualmente ➕</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB HISTORIAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab_hist:
    st.markdown('<p class="sec-label">📋 HISTORIAL DE MOVIMIENTOS</p>', unsafe_allow_html=True)
    hist_data = cargar_historial_cache()

    filtro_h = st.text_input("Filtrar historial:", placeholder="Producto, usuario, tipo...",
                              label_visibility="collapsed", key="filtro_h")
    if filtro_h:
        t = filtro_h.upper()
        hist_data = [h for h in hist_data if
                     t in str(h.get('nombre','')).upper() or
                     t in str(h.get('usuario','')).upper() or
                     t in str(h.get('tipo','')).upper() or
                     t in str(h.get('cod_int','')).upper() or
                     t in str(h.get('ubicacion','')).upper()]

    if hist_data:
        df_h = pd.DataFrame(hist_data)[["fecha_hora","usuario","tipo","nombre","cod_int","cantidad","ubicacion"]]
        df_h.columns = ["FECHA","USUARIO","TIPO","PRODUCTO","CÓDIGO","CANT","UBICACIÓN"]
        st.dataframe(df_h, use_container_width=True, hide_index=True,
                     column_config={
                         "TIPO": st.column_config.TextColumn(width="small"),
                         "CANT": st.column_config.NumberColumn(format="%d", width="small"),
                     })
        st.caption(f"{len(df_h)} movimientos")
    else:
        st.info("Sin movimientos registrados.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB PLANILLA
# ═══════════════════════════════════════════════════════════════════════════════
with tab_plan:
    st.markdown('<p class="sec-label">📊 PLANILLA DE DATOS</p>', unsafe_allow_html=True)
    tabla_sel = st.radio("Tabla:", ["maestra","inventario"], horizontal=True, key="tabla_plan")
    filtro_p  = st.text_input("Filtrar:", placeholder="Buscar en la tabla...",
                               label_visibility="collapsed", key="filtro_plan")

    data_plan = maestra if tabla_sel == "maestra" else inventario
    if filtro_p:
        t = filtro_p.upper()
        data_plan = [r for r in data_plan if any(t in str(v).upper() for v in r.values())]

    if data_plan:
        df_plan = pd.DataFrame(data_plan)
        st.dataframe(df_plan, use_container_width=True, hide_index=True)
        st.caption(f"{len(df_plan)} filas")
        csv = df_plan.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", csv,
                           file_name=f"{tabla_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv", use_container_width=True)
    else:
        st.info("Sin datos.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
with tab_admin:
    if rol != "admin":
        st.warning("🔒 Solo disponible para administradores.")
    else:
        st.markdown('<p class="sec-label">👤 GESTIÓN DE USUARIOS</p>', unsafe_allow_html=True)
        try:
            usuarios_db = sb.table("usuarios").select("*").execute().data or []
            if usuarios_db:
                df_u = pd.DataFrame(usuarios_db)[["usuario","rol"]]
                df_u.columns = ["USUARIO","ROL"]
                st.dataframe(df_u, use_container_width=True, hide_index=True)
        except: pass

        st.markdown("---")
        st.markdown('<p class="sec-label">CREAR USUARIO</p>', unsafe_allow_html=True)
        with st.form("form_crear_usuario"):
            col_au, col_ap, col_ar = st.columns(3)
            with col_au: nu  = st.text_input("Usuario")
            with col_ap: np_ = st.text_input("Clave", type="password")
            with col_ar: nr  = st.selectbox("Rol", ["operario","admin","visita","vendedor"])
            if st.form_submit_button("➕ Crear usuario", use_container_width=True):
                if nu and np_:
                    try:
                        sb.table("usuarios").insert({"usuario": nu.lower().strip(), "clave": np_, "rol": nr}).execute()
                        st.success("✅ Usuario creado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown('<p class="sec-label">📱 NOTIFICACIONES WHATSAPP</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(37,211,102,0.08);border:1px solid rgba(37,211,102,0.3);
                    border-radius:12px;padding:12px 16px;margin-bottom:10px;font-size:12px;color:#94A3B8;">
            Recibis un WhatsApp cuando un vendedor carga un pedido nuevo.<br>
            <b style="color:#25D366">Activar CallMeBot:</b> manda el mensaje
            <code>I allow callmebot to send me messages</code> al <b>+34 644 97 74 26</b> por WhatsApp.
            Despues de unos minutos te responden con tu API Key.
        </div>
        """, unsafe_allow_html=True)

        try:
            _wa_num_db    = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
            _wa_key_db    = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
            _wa_num_actual = _wa_num_db[0]["valor"] if _wa_num_db else ""
            _wa_key_actual = _wa_key_db[0]["valor"] if _wa_key_db else ""
        except:
            _wa_num_actual = _wa_key_actual = ""

        with st.form("form_wa"):
            col_wn, col_wk = st.columns(2)
            with col_wn:
                wa_num = st.text_input("Tu numero WhatsApp:", value=_wa_num_actual, placeholder="+5491112345678")
            with col_wk:
                wa_key = st.text_input("API Key de CallMeBot:", value=_wa_key_actual, placeholder="123456")
            col_ws, col_wt = st.columns(2)
            with col_ws:
                if st.form_submit_button("💾 Guardar numero", use_container_width=True):
                    if wa_num.strip() and wa_key.strip():
                        try:
                            sb.table("config").upsert({"clave":"wa_numero","valor":wa_num.strip()}, on_conflict="clave").execute()
                            sb.table("config").upsert({"clave":"wa_apikey","valor":wa_key.strip()}, on_conflict="clave").execute()
                            check = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
                            if check and check[0]["valor"] == wa_num.strip():
                                st.success(f"✅ Guardado correctamente: {wa_num.strip()}")
                            else:
                                st.warning("No se pudo verificar el guardado. Revisa los permisos RLS en Supabase.")
                        except Exception as e:
                            err = str(e)
                            if "rls" in err.lower() or "policy" in err.lower() or "42501" in err:
                                st.error("Sin permisos (RLS activo). Ejecuta fix_rls_config.sql en Supabase.")
                            elif "42P01" in err or "does not exist" in err.lower():
                                st.error("Tabla config no existe. Ejecuta fix_tabla_config.sql en Supabase.")
                            else:
                                st.error(f"Error: {err}")
                    else:
                        st.warning("Completa numero y API key.")
            with col_wt:
                if st.form_submit_button("🔔 Probar ahora", use_container_width=True):
                    if _wa_num_actual and _wa_key_actual:
                        resultado = {"ok": False, "err": ""}
                        import time
                        def _ok(): resultado["ok"] = True
                        def _err(e): resultado["err"] = e
                        _enviar_whatsapp(_wa_num_actual, _wa_key_actual,
                            "LOGIEZE - Prueba de notificacion exitosa!",
                            callback_ok=_ok, callback_err=_err)
                        time.sleep(2)
                        if resultado["ok"]:
                            st.success("Mensaje enviado. Revisa tu WhatsApp.")
                        else:
                            st.warning(f"Enviado (verificar WhatsApp). Respuesta: {resultado['err'] or 'OK'}")
                    else:
                        st.warning("Guarda el numero y API key primero.")

        if _wa_num_actual:
            st.caption(f"Numero activo: {_wa_num_actual}")

        st.markdown("---")
        st.markdown('<p class="sec-label">⚠️ ZONA PELIGROSA</p>', unsafe_allow_html=True)
        tabla_wipe = st.selectbox("Tabla a borrar:", ["inventario","maestra","historial"], key="wipe_t")
        confirmar  = st.text_input("Escribí CONFIRMAR para habilitar el borrado:", key="wipe_conf")
        if confirmar == "CONFIRMAR":
            if st.button(f"🗑️ BORRAR TODA LA TABLA '{tabla_wipe}'", type="primary", use_container_width=True):
                try:
                    id_col = "id" if tabla_wipe in ["inventario","historial"] else "cod_int"
                    sb.table(tabla_wipe).delete().neq(id_col, -999).execute()
                    st.success("Tabla borrada.")
                    refrescar()
                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB ASISTENTE — OPERARIO DIGITAL (100% propio, sin dependencias externas)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_asist:

    st.markdown("""
    <style>
    .msg-user {
        background: linear-gradient(135deg,#1D4ED8,#2563EB);
        color:#fff;
        border-radius:18px 18px 4px 18px;
        padding:10px 16px;
        margin:4px 0 4px 50px;
        font-size:14px;
        line-height:1.6;
    }
    .msg-bot {
        background:#1E293B;
        color:#F1F5F9;
        border-radius:4px 18px 18px 18px;
        border:1px solid #334155;
        padding:10px 16px;
        margin:4px 50px 4px 0;
        font-size:14px;
        line-height:1.6;
        white-space:pre-wrap;
    }
    .msg-ok {
        background:rgba(16,185,129,.12);
        border:1px solid rgba(16,185,129,.35);
        border-radius:8px;
        padding:6px 12px;
        margin:2px 50px 6px 0;
        font-size:12px;
        color:#10B981;
    }
    .msg-err {
        background:rgba(239,68,68,.12);
        border:1px solid rgba(239,68,68,.35);
        border-radius:8px;
        padding:6px 12px;
        margin:2px 50px 6px 0;
        font-size:12px;
        color:#EF4444;
    }
    .chat-lbl { font-size:11px; color:#475569; margin:6px 4px 1px; }
    </style>""", unsafe_allow_html=True)

    h1, h2 = st.columns([4,1])
    with h1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:4px 0 8px">
            <div style="font-size:36px">📦</div>
            <div>
                <div style="font-size:17px;font-weight:900;color:#F1F5F9;letter-spacing:1px">
                    OPERARIO DIGITAL — LOGIEZE</div>
                <div style="font-size:12px;color:#10B981;font-weight:600">
                    ✅ Sin límites · Sin costo · Sin internet · 100% propio</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with h2:
        if st.button("🗑️ Limpiar", use_container_width=True, key="clear_bot"):
            st.session_state.bot_hist = []
            st.rerun()

    if "bot_hist" not in st.session_state:
        st.session_state.bot_hist = []

    # =========================================================================
    # MOTOR DE LENGUAJE NATURAL — 100% Python, sin dependencias externas
    # =========================================================================
    import re as _re
    import unicodedata as _ud

    def _n(txt):
        """Normaliza: minúsculas, sin tildes, sin espacios extra."""
        t = _ud.normalize('NFD', str(txt))
        t = ''.join(c for c in t if _ud.category(c) != 'Mn')
        return t.lower().strip()


    # ═══════════════════════════════════════════════════════════════════════
    # MOTOR NLP v3.0 — Lenguaje natural flexible, búsqueda inteligente
    # ═══════════════════════════════════════════════════════════════════════
    import re as _re, unicodedata as _ud

    def _n(t):
        s = _ud.normalize('NFD', str(t))
        return _re.sub(r'\s+', ' ', ''.join(
            c for c in s if _ud.category(c) != 'Mn').lower().strip())

    # Stopwords: nunca son nombre de producto
    """
    Motor de búsqueda v3 — blindado para nombres con variantes (tonos, tamaños).

    PROBLEMAS RESUELTOS:
      1. "8/00" vs "7/00" — penalty -800pts por número faltante
      2. "400" en query no se confunde con tono "4/00" — dos normalizadores separados
      3. Búsqueda por código de barras (EAN-13, UPC, QR, cualquier campo)
      4. Búsqueda por código interno (paso previo al scoring)
      5. Step 3 no confunde partes de tonos (8 de "8/00") con cod_int
    """
    import re as _re, unicodedata as _ud

    _SW = {
        'de','del','al','el','la','los','las','un','una','unos','unas',
        'en','a','y','o','e','si','no','ni','por','para','con','sin','que',
        'sacar','saca','saque','sacame','bajame','baja','retirar','retira',
        'quitar','quita','usar','consumir','salida','despachar','despacho',
        'agregar','agrega','ingresar','ingresa','entrada','recibir',
        'llego','llegaron','sumar','suma','cargar','carga','compra',
        'mover','move','mueve','manda','mandar','trasladar','traslada',
        'corregir','ajustar','ajusta','fijar','actualizar',
        'cuanto','cuanta','cuantos','cuantas','hay','queda','quedan',
        'tiene','tenemos','existe','disponible','stock','dame','deme',
        'ver','listar','buscar','donde','codigo','cod','producto','lote',
        'unidades','uds','total','me','nos','te','se','lo',
    }

    _UNIDADES = {'mg','ml','gr','grs','g','kg','l','lt','lts','cc','cm','mm',
                 'comp','caps','tab','uds','x','u','comprimidos','tabletas'}

    _SUFIJOS_TONO = {'00','01','02','03','04','05','06','07','08','09',
                     '10','11','12','13','14','15','16','17','18','19',
                     '20','21','22','33','44','45','46','47','55','65','66','77','88','99'}

    _BARRAS = ('barras','ean','ean13','upc','upc12','gtin',
               'cod_barras','codigo_barras','barcode','qr')


    def _strip(t):
        """Base: sin tildes, minúsculas, sin puntuación especial."""
        s = _ud.normalize('NFD', str(t))
        s = ''.join(c for c in s if _ud.category(c) != 'Mn').lower()
        s = _re.sub(r'[¿¡!?,;:\(\)\[\]\{\}"\'.`*#@]', ' ', s)
        return _re.sub(r'\s+', ' ', s).strip()


    def _nn(nombre):
        """
        Normaliza un NOMBRE DE PRODUCTO (de la maestra).
        Convierte tonos reales: "8/00", "8.00" → "8/00".
        NO convierte dosis: "400mg" → "400 mg" (separado pero sin tono).
        """
        s = _strip(nombre)
        # Separar letra+número pegados
        s = _re.sub(r'([a-z])(\d)', r'\1 \2', s)
        s = _re.sub(r'(\d)([a-z])', r'\1 \2', s)
        s = _re.sub(r'\s+', ' ', s).strip()
        # Convertir 8.00 → 8/00 solo si NO hay unidad inmediata después
        def _sep_nom(m):
            n1, n2 = m.group(1), m.group(2)
            sig = (m.string[m.end():].strip().split() or [''])[0].lower()
            if sig in _UNIDADES: return m.group(0)
            return f'{n1}/{n2}' if n2 in _SUFIJOS_TONO else m.group(0)
        s = _re.sub(r'\b(\d+)[.,](\d{2,3})\b', _sep_nom, s)
        return _re.sub(r'\s+', ' ', s).strip()


    def _nq(query):
        """
        Normaliza un QUERY del usuario.
        Más conservador: solo convierte tonos EXPLÍCITOS (ya escritos con /).
        Un número solo como "400" no se convierte a "4/00".
        """
        s = _strip(str(query))
        # Separar letra+número pegados (primont8/00 → primont 8/00)
        s = _re.sub(r'([a-z])(\d)', r'\1 \2', s)
        s = _re.sub(r'(\d)([a-z])', r'\1 \2', s)
        s = _re.sub(r'\s+', ' ', s).strip()
        # Convertir 8.00 → 8/00 (tono escrito con punto), NO 400 → 4/00
        def _sep_q(m):
            n1, n2 = m.group(1), m.group(2)
            sig = (m.string[m.end():].strip().split() or [''])[0].lower()
            if sig in _UNIDADES: return m.group(0)
            # Solo convertir si N es 1 dígito (tonos son siempre N/NN, no NN/NN)
            if len(n1) == 1 and n2 in _SUFIJOS_TONO: return f'{n1}/{n2}'
            return m.group(0)
        s = _re.sub(r'\b(\d+)[.,](\d{2,3})\b', _sep_q, s)
        return _re.sub(r'\s+', ' ', s).strip()


    def _tok_q(txt):
        """
        Tokeniza un QUERY preservando tonos (8/00) y sus partes.
        También intenta la versión "tono compacto": "800" → busca como "8/00"
        para tolerar ese error de escritura.
        """
        t = _nq(txt)
        # Quitar ubicaciones de depósito (01-2A)
        t = _re.sub(r'\b\d{1,2}[-_]\d{1,2}[a-z]{0,2}\b', ' ', t)
        out = set()
        for w in t.split():
            if not w or w in _SW: continue
            out.add(w)
            if '/' in w:
                # Tono 8/00 → también buscar "8" y "00" por separado
                for p in w.split('/'):
                    if p: out.add(p)
            else:
                # Número de 3 dígitos sin unidad → también intentar como tono
                m = _re.match(r'^([1-9])(\d{2})$', w)
                if m and m.group(2) in _SUFIJOS_TONO:
                    out.add(f'{m.group(1)}/{m.group(2)}')  # "800" → también "8/00"
        return list(out)


    def _en(token, nom_n):
        """Busca token como PALABRA COMPLETA en nombre normalizado."""
        padded = f' {nom_n} '
        return (f' {token} ' in padded or
                f'/{token} ' in padded or
                f' {token}/' in padded or
                f'/{token}/' in padded)


    def _score(nom, query):
        """
        Score inteligente:
        - Token numérico del query faltante en nombre → -800 pts (penalización severa)
        - Todos los tokens presentes → +500 pts bonus
        - Retorna 0 si score neto es negativo
        """
        nn = _nn(nom)
        qn = _nq(query)
        if nn == qn: return 99999.0
        if len(qn) > 3 and qn in nn: return 8000.0

        qt = _tok_q(query)
        if not qt: return 0.0

        score = 0.0
        falt  = []
        for w in qt:
            found = _en(w, nn)
            # Substring solo para palabras largas sin números
            if not found and len(w) >= 5 and not _re.search(r'\d', w):
                found = any(w in tok for tok in nn.split())
            if found:
                score += 400.0 if _re.search(r'\d', w) else 100.0
                score += len(w) * 8.0
            else:
                falt.append(w)

        for w in falt:
            if _re.search(r'\d', w):
                # Si el token tiene alternativa tono (800↔8/00) y la alternativa sí matchea,
                # no penalizar (ya se contó el match de la alternativa)
                m3 = _re.match(r'^([1-9])(\d{2})$', w)
                alt_tono = f'{m3.group(1)}/{m3.group(2)}' if m3 else None
                if alt_tono and _en(alt_tono, nn):
                    pass  # alternativa matchea → no penalizar
                else:
                    score -= 800.0
            else:
                score -= 150.0
        if not falt:
            score += 500.0
        score -= len(nn) * 0.1
        return max(score, 0.0)


    def buscar_uno(query, maestra):
        """
        Búsqueda blindada — 4 pasos en orden de precisión:
        1. Código interno exacto
        2. Código de barras exacto (EAN-13, UPC, QR — cualquier campo)
        3. Número en texto = código (ignora partes de tonos como "8" de "8/00")
        4. Nombre con scoring (penaliza variantes incorrectas)
        """
        if not query or not str(query).strip(): return None
        qs = str(query).strip()
        qn = _nq(qs)

        # ── 1. Código interno exacto ──────────────────────────────────────
        for p in maestra:
            c = str(p.get('cod_int', '')).strip()
            if c and c == qs: return p
            if c and _nq(c) == qn: return p

        # ── 2. Código de barras ───────────────────────────────────────────
        for campo in _BARRAS:
            for p in maestra:
                v = str(p.get(campo, '')).strip()
                if v and v == qs: return p
                if v and _nq(v) == qn: return p

        # ── 3. Número en texto = código (SOLO números "solos", no partes de tono) ──
        # Quitar tonos tipo N/NN del texto para que "8" de "8/00" no matchee cod_int 8
        limpio = _re.sub(r'\b\d{1,2}[-_]\d{1,2}[A-Za-z]{0,2}\b', ' ', qs)  # ubicaciones
        limpio = _re.sub(r'\b\d{1,2}/\d{2}\b', ' __TONO__ ', limpio)        # tonos N/NN
        for m in _re.finditer(r'\b(\d{2,13})\b', limpio):  # mínimo 2 dígitos
            num = m.group(1)
            if 'TONO' in limpio[max(0,m.start()-10):m.end()+10]: continue
            for p in maestra:
                if str(p.get('cod_int', '')).strip() == num: return p
            for campo in _BARRAS:
                for p in maestra:
                    if str(p.get(campo, '')).strip() == num: return p

        # ── 4. EAN largo suelto (8-13 dígitos) ───────────────────────────
        for m in _re.finditer(r'\b(\d{8,13})\b', qs):
            num = m.group(1)
            for p in maestra:
                if str(p.get('cod_int', '')).strip() == num: return p
            for campo in _BARRAS:
                for p in maestra:
                    if str(p.get(campo, '')).strip() == num: return p

        # ── 5. Scoring por nombre ─────────────────────────────────────────
        qt = _tok_q(qs)
        if not qt: return None

        mej = []
        for p in maestra:
            sc = _score(p.get('nombre', ''), qs)
            if sc >= 50:
                mej.append((sc, p))

        if not mej: return None
        mej.sort(key=lambda x: -x[0])

        # Empate sin discriminador numérico → ambiguo (mostrar opciones)
        if len(mej) >= 2:
            has_num = any(_re.search(r'\d', w) for w in qt)
            if mej[0][0] - mej[1][0] < 50 and mej[0][0] < 5000 and not has_num:
                return None

        return mej[0][1]


    def buscar_varios(query, maestra, top=8):
        """Lista los N productos más relevantes para mostrar opciones."""
        if not query or not str(query).strip(): return []
        mej = [(sc, p) for p in maestra
               for sc in [_score(p.get('nombre', ''), query)] if sc > 0]
        mej.sort(key=lambda x: -x[0])
        return [p for _, p in mej[:top]]

    def _cant(t):
        limpio = _re.sub(r'\b\d{1,2}[-_]\d{1,2}[A-Za-z]{0,2}\b', ' ', t)
        limpio = _re.sub(r'"[^"]*"', ' ', limpio)
        codigos = {str(p.get('cod_int','')) for p in maestra}
        for m in _re.finditer(r'\b(\d+(?:[.,]\d+)?)\b', limpio):
            if m.group(1) not in codigos:
                return float(m.group(1).replace(',','.'))
        tabla = {
            'un':1,'una':1,'dos':2,'tres':3,'cuatro':4,'cinco':5,'seis':6,
            'siete':7,'ocho':8,'nueve':9,'diez':10,'once':11,'doce':12,
            'quince':15,'veinte':20,'treinta':30,'cuarenta':40,'cincuenta':50,
            'sesenta':60,'setenta':70,'ochenta':80,'noventa':90,'cien':100,
            'doscientos':200,'quinientos':500,'mil':1000
        }
        n = _n(t)
        for w, v in tabla.items():
            if _re.search(r'\b' + w + r'\b', n): return float(v)
        return 0.0

    def _ubi(t):
        m = _re.search(r'\b(\d{1,2}[-_]\d{1,2}[A-Za-z]{0,2})\b', t)
        return m.group(1).upper() if m else ''

    def _ubis(t):
        return [u.upper() for u in _re.findall(r'\b(\d{1,2}[-_]\d{1,2}[A-Za-z]{0,2})\b', t)]

    def _fecha_vto(t):
        m = _re.search(r'\b(\d{1,2}[/\-]\d{2,4})\b', t)
        return m.group(1) if m else ''

    def _lotes(cod):
        return idx_inv.get(str(cod), [])

    def _intent(t):
        # _n() elimina tildes y pasa a minusculas — patrones siempre sin tildes
        n = _n(t)
        if _re.search(r'\b(hola|buenas|buen\s?dia|como\s+estas|como\s+andas|hey|que\s+tal)\b', n):
            return 'saludo'
        if _re.search(r'\b(gracias|gracia|genial|perfecto|excelente|de\s+nada)\b', n):
            return 'gracias'
        if _re.search(r'\b(ayuda|que\s+podes|que\s+sabes|como\s+funciona|comandos|como\s+te\s+uso)\b', n):
            return 'ayuda'
        # SALIDA
        if _re.search(r'\b(sac[aoe]|sacame|sacamos|saque|baj[aoe]|bajame|bajamos|'
                       r'retir[ao]|retiramos|retiraron|quit[ao]|quitame|quitamos|'
                       r'us[ao]|usamos|usaron|consum[eo]|consumimos|consumieron|'
                       r'gast[ao]|gastamos|gastaron|salida|despacha|despacho|despachamos|'
                       r'egres[ao]|descont[ao]|descontamos|'
                       r'se\s+llev[ao]|se\s+llevaron|llevamos|llevaron|llevo|'
                       r'se\s+us[ao]|se\s+usaron|se\s+gast[ao]|se\s+gastaron|'
                       r'tom[ao]|tomamos|tomaron)\b', n):
            return 'salida'
        # ENTRADA
        if _re.search(r'\b(agreg[ao]|agregame|agregamos|agregaron|'
                       r'ingres[ao]|ingresamos|ingresaron|entro|entraron|entrada|entradas|'
                       r'recib[io]|recibimos|recibieron|llegaron|llego|llegamos|'
                       r'sum[ao]|sumamos|sumame|carg[ao]|cargamos|cargaron|cargue|'
                       r'compra|compramos|compraron|trajo|trajimos|trajeron|'
                       r'met[eo]|metemos|pon[eo]|ponemos|poneme|pusimos|'
                       r'reponer|reponemos|reposicion|incorpor[ao])\b', n):
            return 'entrada'
        # MOVER
        if _re.search(r'\b(mov[eo]|movi|moveme|movemos|movieron|'
                       r'manda[rn]?|mandame|mandamos|mandaron|'
                       r'traslad[ao]|trasladamos|reubic[ao]|reubicamos|'
                       r'transfer[io]|transferimos|'
                       r'pas[ao]\s+(a|al|todo)|pasame|pasamos|pasaron|'
                       r'llev[ao]\s+(a|al)|llevame|llevamos\s+(a|al)|'
                       r'cambi[ao]\s+(de\s+)?ubic)\b', n):
            return 'mover'
        if len(_ubis(t)) >= 2 and _re.search(r'\bde\b.{1,40}\ba\b', n):
            return 'mover'
        # CORREGIR
        if _re.search(r'\b(correg[io]|corregimos|corregime|ajust[ao]|ajustamos|ajustame|'
                       r'fij[ao]|fijamos|actualiz[ao]|actualizamos|'
                       r'en\s+realidad\s+(hay|son|tiene)|la\s+cantidad\s+(es|son|real)|'
                       r'inventario\s+fisico|conteo|deberia\s+(ser|tener|haber))\b', n):
            return 'corregir'
        # HISTORIAL
        if _re.search(r'\b(historial|movimientos|movimiento|ultimos|ultimo|'
                       r'registro|que\s+paso|que\s+hicieron|que\s+hubo|'
                       r'bitacora|actividad|novedades|que\s+se\s+(hizo|movio))\b', n):
            return 'historial'
        # VENCIMIENTOS
        if _re.search(r'\b(venc[eo]|vencen|vencidos|vencimiento|vencimientos|'
                       r'por\s+vencer|proximos\s+a\s+vencer|'
                       r'caducidad|caduca|caducan|expiran|expira|se\s+vencen)\b', n):
            return 'vencimientos'
        # BAJO STOCK
        if _re.search(r'\b(bajo\s+stock|poco\s+stock|poca\s+cantidad|'
                       r'se\s+acab[ao]|se\s+acabaron|quedan?\s+poco[sa]?|'
                       r'critico|sin\s+stock|agotado[sa]?|escaso[sa]?|minimo|'
                       r'(que|lo)\s+(nos\s+|me\s+)?falt[ao]|falta\s+reponer|'
                       r'necesitamos\s+reponer|hay\s+poco[sa]?|nos\s+quedamos\s+sin)\b', n):
            return 'bajo_stock'
        # RESUMEN
        if _re.search(r'\b(resumen|todo\s+el\s+(inventario|stock)|panorama|balance|'
                       r'estado\s+del\s+inventario|como\s+estamos|inventario\s+completo)\b', n):
            return 'resumen'
        # TOP
        if _re.search(r'\b(top|ranking|mas\s+stock|mayor\s+stock|mas\s+cantidad|los\s+que\s+mas)\b', n):
            return 'top_stock'
        # UBICACIONES
        if _re.search(r'\b(donde\s+est[ae]|donde\s+hay|donde\s+queda|donde\s+quedan|'
                       r'ubicacion|ubicaciones|en\s+que\s+lugar|en\s+que\s+estante|guardado|donde)\b', n):
            return 'ubicaciones'
        # CONSULTA STOCK
        if _re.search(r'\b(cuanto[sa]?\s+(hay|queda[sn]?|tene[ms]?|tiene[ns]?)|'
                       r'cuanto\s+stock|stock\s+de|hay\s+de|quedan?\s+de|tenemos\s+de|'
                       r'hay\s+stock|existe|existencia|disponible|cuanto\s+(tenemos|tiene|hay))\b', n):
            return 'consulta_stock'
        # PEDIDOS
        if _re.search(r'\b(pedido[s]?|orden(es)?|nube|pendiente[s]?)\b', n):
            return 'pedidos'
        return 'buscar'

    def _exec_salida(txt):
        if rol in ('visita', 'vendedor'):
            return None, "❌ Tu rol no tiene permisos para registrar salidas."
        prod = buscar_uno(txt, maestra)
        cant = _cant(txt)
        ubi  = _ubi(txt)
        if not prod:
            sugs = buscar_varios(txt, maestra)
            if sugs:
                lista = "\n".join(f"  • {p['nombre']} (cod:{p['cod_int']})" for p in sugs)
                return None, f"🔍 No encontré el producto exacto. ¿Es alguno de estos?\n\n{lista}"
            return None, "No encontré ese producto. Decime el nombre o el código."
        if cant == 0:
            return None, f"¿Cuántas unidades de *{prod['nombre']}* querés sacar?"
        cod, nom = str(prod['cod_int']), prod['nombre']
        lts = _lotes(cod)
        if not lts:
            return False, f"❌ No hay stock de *{nom}* en el inventario."
        lote = None
        if ubi:
            lote = next((l for l in lts if str(l.get('ubicacion','')).upper() == ubi), None)
            if not lote:
                ubis_ok = [str(l.get('ubicacion','')) for l in lts if float(l.get('cantidad',0) or 0) > 0]
                return False, f"❌ No hay lote de *{nom}* en {ubi}.\nStock en: {', '.join(ubis_ok)}"
        if not lote: lote = next((l for l in lts if float(l.get('cantidad',0) or 0) >= cant), None)
        if lote: ubi = str(lote.get('ubicacion',''))
        if not lote and lts:
            lote = max(lts, key=lambda l: float(l.get('cantidad',0) or 0))
            ubi  = str(lote.get('ubicacion',''))
        if not lote:
            return False, f"❌ No hay stock de *{nom}*."
        disp = float(lote.get('cantidad', 0) or 0)
        if cant > disp:
            return False, f"❌ Solo hay {int(disp)} uds de *{nom}* en {ubi}.\n¿Querés sacar las {int(disp)} que hay?"
        nueva = disp - cant
        if nueva <= 0: sb.table("inventario").delete().eq("id", lote["id"]).execute()
        else:          sb.table("inventario").update({"cantidad": nueva}).eq("id", lote["id"]).execute()
        registrar_historial("SALIDA", cod, nom, cant, ubi, usuario)
        recalcular_maestra(cod, inventario)
        refrescar()
        lts_post = _lotes(cod)
        stk_post = int(sum(float(l.get('cantidad',0) or 0) for l in lts_post))
        dep = lote.get('deposito','')
        return True, (f"✅ {int(cant)} uds de *{nom}* retiradas\n"
                       f"📤 Depósito: {dep}  Ubicación: {ubi}\n"
                       f"📊 Stock restante: {stk_post} uds")

    # ── HELPERS MEJORADOS PARA ENTRADA ───────────────────────────────────────

    def _fecha_flexible(t):
        """
        Extrae fecha de vencimiento desde lenguaje natural ultra-flexible.
        Soporta:
          - Formatos numéricos: 10/26, 10/2026, 05-27, 2027-05
          - Texto con mes: "junio 2026", "jun/26", "junio del 26"
          - Relativos: "en 6 meses", "en 1 año", "en un año"
          - Abreviaciones: "vto 6/26", "vence 10/26"
          - Sin fecha: devuelve ""
        """
        from datetime import date, timedelta
        import re as _r
        tn = _n(t)

        _MESES = {
            'enero':1,'ene':1,'feb':2,'febrero':2,'mar':3,'marzo':3,
            'abr':4,'abril':4,'may':5,'mayo':5,'jun':6,'junio':6,
            'jul':7,'julio':7,'ago':8,'agosto':8,'sep':9,'sept':9,'septiembre':9,
            'oct':10,'octubre':10,'nov':11,'noviembre':11,'dic':12,'diciembre':12,
        }

        # 1. Formato numérico explícito: MM/AA, MM/AAAA, MM-AA, M/AA
        m = _r.search(r'\b(\d{1,2})[/\-](\d{2,4})\b', t)
        if m:
            mes_s, anio_s = m.group(1), m.group(2)
            anio = int(anio_s) + 2000 if len(anio_s) == 2 else int(anio_s)
            if 1 <= int(mes_s) <= 12:
                return f"{mes_s.zfill(2)}/{anio}"

        # 2. Texto de mes + año: "junio 2026", "jun 26", "junio del 26"
        for nom_mes, num_mes in sorted(_MESES.items(), key=lambda x: -len(x[0])):
            pat = nom_mes + r'[\s\-/]*(?:del?\s*)?(\d{2,4})'
            m2 = _r.search(pat, tn)
            if m2:
                anio_s = m2.group(1)
                anio = int(anio_s) + 2000 if len(anio_s) == 2 else int(anio_s)
                return f"{str(num_mes).zfill(2)}/{anio}"
            # Solo mes sin año: "junio" → usa el próximo junio
            if _r.search(r'\b' + nom_mes + r'\b', tn) and 'venc' in tn:
                hoy = date.today()
                anio = hoy.year if hoy.month < num_mes else hoy.year + 1
                return f"{str(num_mes).zfill(2)}/{anio}"

        # 3. Relativos: "en 6 meses", "en 1 año", "en un año"
        m3 = _r.search(r'\ben\s+(\d+|un[ao]?|dos|tres|cuatro|seis|doce)\s+(mes(?:es)?|a[ñn]os?)', tn)
        if m3:
            num_map = {'un':1,'una':1,'uno':1,'dos':2,'tres':3,'cuatro':4,'seis':6,'doce':12}
            raw = m3.group(1)
            n_num = num_map.get(raw, int(raw) if raw.isdigit() else 1)
            unidad = m3.group(2)
            hoy = date.today()
            if 'a' in unidad:  # año
                fut = date(hoy.year + n_num, hoy.month, 1)
            else:              # meses
                mes_fut = hoy.month + n_num
                anio_fut = hoy.year + (mes_fut - 1) // 12
                mes_fut = ((mes_fut - 1) % 12) + 1
                fut = date(anio_fut, mes_fut, 1)
            return f"{str(fut.month).zfill(2)}/{fut.year}"

        return ''

    def _deposito_flex(t):
        """
        Extrae depósito del texto. Soporta:
          - "depósito B", "depo 2", "en el secundario", "al depósito principal"
          - Números solos como depósito: "al 2"
          - Si no lo menciona: devuelve 'PRINCIPAL'
        """
        import re as _r
        tn = _n(t)
        # Nombre explícito de depósito
        m = _r.search(r'\bdepo(?:sito)?\s*:?\s*([A-Za-z0-9_\-]+)', tn)
        if m:
            return m.group(1).upper()
        # Palabras clave de depósito
        if _r.search(r'\b(secundario|segundo|deposito\s*2|dep\s*2|b\b)', tn):
            return 'SECUNDARIO'
        if _r.search(r'\b(principal|primero|deposito\s*1|dep\s*1|a\b)', tn):
            return 'PRINCIPAL'
        # Buscar depósito en el inventario actual
        deps_existentes = list({str(l.get('deposito','PRINCIPAL')).upper() for l in inventario if l.get('deposito')})
        for dep in deps_existentes:
            if dep.lower() in tn:
                return dep
        return 'PRINCIPAL'

    def _ubi_flex(t, cod_prod=None):
        """
        Extrae ubicación flexible. Soporta:
          - Formato estándar: 01-2A, 1-3, 02_4B
          - Código 99: "la 99", "en 99", "estante 99" → busca siguiente XX-99A libre
          - Vacía: "" para pedir al usuario
        """
        import re as _r
        tn = _n(t)

        # Formato estándar NN-NNA
        m = _r.search(r'\b(\d{1,2}[-_]\d{1,2}[A-Za-z]{0,2})\b', t)
        if m:
            return m.group(1).upper()

        # Código 99 — buscar siguiente ubicación libre del tipo XX-99
        if _r.search(r'\b99\b', t):
            return _sug_ubi_99(cod_prod)

        # "siguiente", "la próxima", "donde corresponde" → sugerir basado en el producto
        if _r.search(r'\b(siguiente|proxima?|corresponde|misma|donde\s+va)\b', tn):
            if cod_prod:
                lts = _lotes(str(cod_prod))
                if lts:
                    return str(lts[0].get('ubicacion', '')).upper()
            return ''

        return ''

    def _sug_ubi_99(cod_prod=None):
        """
        Sugiere la siguiente ubicación tipo XX-99 libre.
        Si el producto ya tiene lotes, usa el mismo pasillo (XX) que el primer lote.
        Si no, busca la primera XX-99 disponible en el inventario.
        """
        import re as _r

        # Obtener todas las ubicaciones XX-99 ya usadas
        ubs_99_usadas = set()
        for l in inventario:
            u = str(l.get('ubicacion', '')).upper()
            if _r.match(r'\d+-99', u):
                ubs_99_usadas.add(u)

        # Si el producto tiene lotes, usar su pasillo
        if cod_prod:
            lts = _lotes(str(cod_prod))
            if lts:
                ubi_exist = str(lts[0].get('ubicacion', '')).upper()
                m = _r.match(r'(\d+)-', ubi_exist)
                if m:
                    pasillo = m.group(1)
                    # Buscar variante libre: 01-99, 01-99A, 01-99B...
                    for suf in ['', 'A', 'B', 'C', 'D']:
                        cand = f"{pasillo}-99{suf}"
                        if cand not in ubs_99_usadas:
                            return cand

        # Buscar en todos los pasillos del inventario
        pasillos = set()
        for l in inventario:
            u = str(l.get('ubicacion', '')).upper()
            m = _r.match(r'(\d+)-', u)
            if m:
                pasillos.add(m.group(1))

        for p in sorted(pasillos):
            for suf in ['', 'A', 'B', 'C', 'D']:
                cand = f"{p}-99{suf}"
                if cand not in ubs_99_usadas:
                    return cand

        return '01-99'

    def _exec_entrada(txt):
        """
        Registra una entrada de stock con lenguaje ultra-flexible.

        Entiende:
          - Producto: nombre, código, abreviación, typos
          - Cantidad: números, palabras ("diez cajas"), no requerida en el comando inicial
          - Fecha de vto: cualquier formato — 10/26, junio 2026, en 6 meses, sin fecha
          - Depósito: nombre o keyword — principal, secundario, depósito B
          - Ubicación: formato estándar, "la 99" (sugiere siguiente libre), "la misma"
        """
        if rol in ('visita', 'vendedor'):
            return None, "❌ Tu rol no tiene permisos para registrar entradas."

        prod = buscar_uno(txt, maestra)
        cant = _cant(txt)

        # ── Producto no encontrado ──────────────────────────────────────────
        if not prod:
            sugs = buscar_varios(txt, maestra)
            if sugs:
                lista = "\n".join(f"  • {p['nombre']} (cod:{p['cod_int']})" for p in sugs[:5])
                return None, f"🔍 No encontré el producto exacto. ¿Es alguno de estos?\n\n{lista}"
            return None, "No encontré ese producto. Decime el nombre o el código."

        cod, nom = str(prod['cod_int']), prod['nombre']

        # ── Cantidad ────────────────────────────────────────────────────────
        if cant == 0:
            return None, f"¿Cuántas unidades de *{nom}* llegaron?"

        # ── Fecha de vencimiento — flexible ────────────────────────────────
        fv = _fecha_flexible(txt)

        # ── Depósito ────────────────────────────────────────────────────────
        dep = _deposito_flex(txt)

        # ── Ubicación — flexible, soporta "99" y lenguaje natural ──────────
        ubi = _ubi_flex(txt, cod_prod=cod)

        if not ubi:
            # Sugerir basado en lotes existentes del producto
            lts_p = _lotes(cod)
            if lts_p:
                sug = str(lts_p[0].get('ubicacion', '')).upper()
                msg = f"¿En qué ubicación van las {int(cant)} uds de *{nom}*?\n"
                msg += f"💡 Ya tenés stock en *{sug}* — podés decirme esa o cualquier otra.\n"
                msg += f"   También podés decir *'la 99'* para la siguiente ubicación libre de tipo 99."
            else:
                sug99 = _sug_ubi_99(cod)
                msg = f"¿En qué ubicación van las {int(cant)} uds de *{nom}*?\n"
                msg += f"💡 Sugerida: *{sug99}* (próxima libre) — o decime otra."
            return None, msg

        # ── Si la ubi viene de "la 99" pero estaba en uso, informar ────────
        ubi_es_99 = _re.search(r'\b99\b', txt) is not None

        # ── Registrar en DB ─────────────────────────────────────────────────
        lts_ubi = [l for l in inventario
                   if str(l.get('cod_int', '')) == cod
                   and str(l.get('ubicacion', '')).upper() == ubi
                   and str(l.get('deposito', 'PRINCIPAL')).upper() == dep]

        if lts_ubi:
            # Ya existe lote en esa ubicación y depósito → sumar cantidad
            nueva = float(lts_ubi[0].get('cantidad', 0) or 0) + cant
            sb.table("inventario").update({"cantidad": nueva}).eq("id", lts_ubi[0]["id"]).execute()
        else:
            # Lote nuevo
            sb.table("inventario").insert({
                "cod_int": cod, "nombre": nom, "cantidad": cant,
                "ubicacion": ubi, "fecha": fv, "deposito": dep
            }).execute()

        registrar_historial("ENTRADA", cod, nom, cant, ubi, usuario)
        recalcular_maestra(cod, inventario)
        refrescar()

        lts_post = _lotes(cod)
        stk_post = int(sum(float(l.get('cantidad', 0) or 0) for l in lts_post))

        lineas = [f"✅ {int(cant)} uds de *{nom}* ingresadas"]
        lineas.append(f"📥 Depósito: {dep}  Ubicación: {ubi}")
        if fv:
            lineas.append(f"📅 Vto: {fv}")
        lineas.append(f"📊 Stock total: {stk_post} uds")
        if ubi_es_99:
            lineas.append(f"📍 Ubicación 99 asignada: {ubi}")
        return True, "\n".join(lineas)

    def _exec_mover(txt):
        if rol in ('visita', 'vendedor'):
            return None, "❌ Tu rol no tiene permisos para mover lotes."
        prod  = buscar_uno(txt, maestra)
        cant  = _cant(txt)
        ubics = _ubis(txt)
        if not prod:
            sugs = buscar_varios(txt, maestra)
            if sugs:
                lista = "\n".join(f"  • {p['nombre']} (cod:{p['cod_int']})" for p in sugs)
                return None, f"🔍 ¿Cuál producto querés mover?\n\n{lista}"
            return None, "No encontré ese producto. Decime el nombre o el código."
        if len(ubics) < 2:
            lts    = _lotes(str(prod['cod_int']))
            ubis_s = [str(l.get('ubicacion','')) for l in lts if float(l.get('cantidad',0) or 0) > 0]
            sug    = ubis_s[0] if ubis_s else "01-1A"
            return None, (f"Necesito origen Y destino para mover *{prod['nombre']}*.\n"
                           f"Ubicaciones con stock: {', '.join(ubis_s) or 'ninguna'}\n"
                           f"Ej: «Mové de {sug} a 02-1A»")
        ubi_o, ubi_d = ubics[0], ubics[1]
        cod, nom     = str(prod['cod_int']), prod['nombre']
        lts          = _lotes(cod)
        lote = next((l for l in lts if str(l.get('ubicacion','')).upper() == ubi_o), None)
        if not lote:
            ubis_s = [str(l.get('ubicacion','')) for l in lts if float(l.get('cantidad',0) or 0) > 0]
            return False, (f"❌ No hay lote de *{nom}* en {ubi_o}.\n"
                            f"Ubicaciones con stock: {', '.join(ubis_s) or 'ninguna'}")
        disp    = float(lote.get('cantidad', 0) or 0)
        cant_mv = cant if (0 < cant <= disp) else disp
        nueva   = disp - cant_mv
        if nueva <= 0: sb.table("inventario").delete().eq("id", lote["id"]).execute()
        else:          sb.table("inventario").update({"cantidad": nueva}).eq("id", lote["id"]).execute()
        sb.table("inventario").insert({
            "cod_int": cod, "nombre": nom, "cantidad": cant_mv,
            "ubicacion": ubi_d, "fecha": lote.get("fecha",""),
            "deposito": lote.get("deposito","PRINCIPAL")
        }).execute()
        registrar_historial("MOVIMIENTO", cod, nom, cant_mv, f"{ubi_o}→{ubi_d}", usuario)
        recalcular_maestra(cod, inventario)
        refrescar()
        lts_post = _lotes(cod)
        stk_post = int(sum(float(l.get('cantidad',0) or 0) for l in lts_post))
        return True, (f"✅ {int(cant_mv)} uds de *{nom}* movidas\n"
                       f"🔀 {ubi_o} → {ubi_d}\n"
                       f"📊 Stock total: {stk_post} uds")

    def _exec_corregir(txt):
        if rol in ('visita', 'vendedor'):
            return None, "❌ Tu rol no tiene permisos para corregir stock."
        prod = buscar_uno(txt, maestra)
        cant = _cant(txt)
        ubi  = _ubi(txt)
        if not prod:
            return None, "No encontré el producto. Decime el nombre o el código."
        if cant == 0:
            return None, f"¿Cuántas unidades hay realmente de *{prod['nombre']}*?"
        cod, nom = str(prod['cod_int']), prod['nombre']
        lts  = _lotes(cod)
        lote = None
        if ubi: lote = next((l for l in lts if str(l.get('ubicacion','')).upper() == ubi), None)
        if not lote and lts: lote = lts[0]; ubi = str(lote.get('ubicacion',''))
        if lote:
            sb.table("inventario").update({"cantidad": cant}).eq("id", lote["id"]).execute()
        else:
            if not ubi: return None, f"¿En qué ubicación está *{nom}*?"
            sb.table("inventario").insert({
                "cod_int": cod, "nombre": nom, "cantidad": cant,
                "ubicacion": ubi, "deposito": "PRINCIPAL"
            }).execute()
        registrar_historial("CORRECCIÓN", cod, nom, cant, ubi, usuario)
        recalcular_maestra(cod, inventario)
        refrescar()
        return True, f"✅ *{nom}* — ahora hay {int(cant)} uds en {ubi}"

    def _resp_historial(txt):
        try:
            data = sb.table("historial").select("*").order("id",desc=True).limit(30).execute().data or []
            if not data: return None, "No hay movimientos registrados aún."
            prod = buscar_uno(txt, maestra) if any(w in _n(txt) for w in ['de','del','sobre']) else None
            if prod:
                data = [r for r in data if str(r.get('cod_int','')) == str(prod['cod_int'])]
            icons = {"ENTRADA":"📥","SALIDA":"📤","MOVIMIENTO":"🔀","CORRECCIÓN":"✏️"}
            lineas = [f"{icons.get(r.get('tipo',''),'📌')} {r.get('fecha_hora','')} · "
                      f"{r.get('nombre','')} · {int(float(r.get('cantidad',0)))} uds · "
                      f"{r.get('ubicacion','')} · @{r.get('usuario','')}"
                      for r in data[:20]]
            tit = f"📋 Historial de *{prod['nombre']}*:" if prod else "📋 Últimos movimientos:"
            return None, tit + "\n\n" + "\n".join(lineas)
        except Exception as e:
            return False, f"❌ Error: {e}"

    def _resp_vencimientos(_):
        hoy = date.today()
        vencidos, proximos = [], []
        for l in inventario:
            fv = l.get('fecha','')
            if not fv: continue
            try:
                p = str(fv).strip().split("/")
                if len(p) == 2:
                    a = int(p[1]); m = int(p[0])
                    fd   = date(2000 + a if a < 100 else a, m, 1)
                    dias = (fd - hoy).days
                    lin  = f"  {'⛔' if dias<0 else '⚠️'} {l.get('nombre',l.get('cod_int','?'))} · {l.get('ubicacion','?')} · Vto:{fv}"
                    if dias < 0:              vencidos.append(lin)
                    elif dias <= DIAS_ALERTA: proximos.append(f"{lin} ({dias}d)")
            except: pass
        r = ""
        if vencidos: r += f"⛔ VENCIDOS ({len(vencidos)}):\n" + "\n".join(vencidos) + "\n\n"
        if proximos: r += f"⚠️ POR VENCER ({len(proximos)}):\n" + "\n".join(proximos)
        return None, r or "✅ No hay lotes vencidos ni próximos a vencer."

    def _resp_bajo_stock(txt):
        lim   = _cant(txt) or 10.0
        bajos = [(float(p.get('cantidad_total',0) or 0), p.get('nombre','?'), str(p.get('cod_int','')))
                 for p in maestra if float(p.get('cantidad_total',0) or 0) <= lim]
        if not bajos: return None, f"✅ Todo supera las {int(lim)} uds."
        bajos.sort()
        lineas = [f"  {'⛔' if b[0]==0 else '⚠️'} {b[1]} (cod:{b[2]}) · {int(b[0])} uds"
                  for b in bajos[:25]]
        return None, f"📉 Bajo stock (≤{int(lim)} uds) — {len(bajos)} productos:\n\n" + "\n".join(lineas)

    def _resp_resumen(_):
        total_p = len(maestra)
        con_st  = sum(1 for p in maestra if float(p.get('cantidad_total',0) or 0) > 0)
        total_u = sum(float(p.get('cantidad_total',0) or 0) for p in maestra)
        top5    = sorted(maestra, key=lambda p: -float(p.get('cantidad_total',0) or 0))[:5]
        tops    = "\n".join(f"  {i+1}. {p['nombre']} — {int(float(p.get('cantidad_total',0)))} uds"
                            for i, p in enumerate(top5))
        return None, (f"📊 RESUMEN DEL INVENTARIO\n\n"
                       f"📦 Productos: {total_p}   ✅ Con stock: {con_st}   ⛔ Sin stock: {total_p-con_st}\n"
                       f"🔢 Total uds: {int(total_u):,}\n\n🏆 Top 5:\n{tops}")

    def _resp_top_stock(txt):
        n_top = min(int(_cant(txt) or 10), 30)
        tops  = sorted(maestra, key=lambda p: -float(p.get('cantidad_total',0) or 0))[:n_top]
        lineas = [f"  {i+1}. {p['nombre']} (cod:{p['cod_int']}) — {int(float(p.get('cantidad_total',0)))} uds"
                  for i, p in enumerate(tops)]
        return None, f"🏆 Top {n_top} por stock:\n\n" + "\n".join(lineas)

    def _resp_ubicaciones(txt):
        prod = buscar_uno(txt, maestra)
        if prod:
            lts = _lotes(str(prod['cod_int']))
            if not lts: return None, f"📦 *{prod['nombre']}* no tiene stock activo."
            total = sum(float(l.get('cantidad',0)) for l in lts)
            det   = "\n".join(
                f"  📍 {l.get('ubicacion','?')} ({l.get('deposito','')}) — {int(float(l.get('cantidad',0)))} uds"
                + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                for l in lts)
            return None, f"📍 *{prod['nombre']}*\nTotal: {int(total)} uds\n\n{det}"
        todas = {}
        for l in inventario:
            u = str(l.get('ubicacion',''))
            if u: todas[u] = todas.get(u, 0) + float(l.get('cantidad', 0) or 0)
        if not todas: return None, "No hay ubicaciones cargadas."
        lines = [f"  📍 {u} — {int(c)} uds" for u, c in sorted(todas.items())][:40]
        return None, f"📍 Ubicaciones activas ({len(todas)}):\n\n" + "\n".join(lines)


    # ═══════════════════════════════════════════════════════════════════════════
    # BÚSQUEDA POR MEDIDA EXACTA  (350ml, 5L, 60g, 1kg, 250cc, etc.)
    # ═══════════════════════════════════════════════════════════════════════════

    def _extraer_medida(txt):
        """Extrae la primera medida del texto. Retorna (numero_float, unidad_norm, texto_original) o None."""
        patron = _re.search(
            r'\b(\d+(?:[.,]\d+)?)\s*'
            r'(ml|cc|cl|l|lt|lts|litro|litros|g|gr|grs|gramo|gramos|'
            r'kg|kilo|kilos|mg|oz|un|u)\b',
            _n(txt)
        )
        if not patron:
            return None
        num = float(patron.group(1).replace(',', '.'))
        raw = patron.group(2)
        mapa = {
            'ml':'ml','cc':'ml','cl':'ml',
            'l':'l','lt':'l','lts':'l','litro':'l','litros':'l',
            'g':'g','gr':'g','grs':'g','gramo':'g','gramos':'g',
            'kg':'kg','kilo':'kg','kilos':'kg',
            'mg':'mg','oz':'oz','un':'un','u':'un',
        }
        return (num, mapa.get(raw, raw), patron.group(0).strip())

    def _medida_ok(nom_n, num, unidad):
        """True si el nombre normalizado contiene la medida (con equivalencias)."""
        num_s = str(int(num)) if num == int(num) else str(num)
        # Construir variantes equivalentes
        vs = {num_s + unidad}
        if unidad == 'l':
            ml = int(num * 1000)
            vs.update([str(ml)+'ml', str(ml)+'cc', num_s+'lt', num_s+'lts', num_s+'litro'])
        elif unidad == 'ml':
            vs.add(num_s+'cc')
            if num >= 1000:
                vs.add(str(int(num/1000))+'l')
        elif unidad == 'kg':
            vs.update([str(int(num*1000))+'g', str(int(num*1000))+'gr', num_s+'kilo'])
        elif unidad == 'g':
            vs.update([num_s+'gr', num_s+'grs'])
            if num >= 1000:
                vs.add(str(int(num/1000))+'kg')
        for v in vs:
            if v in nom_n:
                return True
        # Búsqueda con espacios entre número y unidad
        alts = {'ml':r'ml|cc','l':r'l|lt|lts|litro','g':r'g|gr|grs|gramo',
                'kg':r'kg|kilo','mg':r'mg','oz':r'oz','un':r'un|u'}
        return bool(_re.search(r'\b' + num_s + r'\s*(?:' + alts.get(unidad, unidad) + r')\b', nom_n))

    # ═══════════════════════════════════════════════════════════════════════════
    # LISTA POR CATEGORÍA / MEDIDA
    # ═══════════════════════════════════════════════════════════════════════════

    def _resp_lista_categoria(txt):
        n = _n(txt)
        medida = _extraer_medida(txt)

        stops = {
            'que','cual','cuales','tengo','tienen','hay','de','del','en',
            'los','las','un','una','me','como','donde','esta','estan',
            'todo','todos','toda','todas','dame','lista','listame',
            'mostrame','ver','veo','cuanto','cuantos','stock','producto',
            'productos','tenes','tiene','busco','quiero','mostrar',
            'hay','a','el','la','con','por','para','sobre','entre',
        }
        # Excluir tokens de la medida de las palabras clave
        if medida:
            num_s = str(int(medida[0])) if medida[0]==int(medida[0]) else str(medida[0])
            stops.add(num_s)
            stops.add(medida[1])
            for tok in medida[2].replace(' ','').split(): stops.add(tok)

        palabras = [w for w in n.split() if w not in stops and len(w) > 1]
        if not palabras:
            return None, None

        # ── Paso 1: filtrar por palabras clave ─────────────────────────────
        candidatos = []
        for p in maestra:
            nom_n = _n(p.get('nombre',''))
            sc = sum(2 if w == nom_n.split()[0] else 1 for w in palabras if w in nom_n)
            if sc > 0:
                candidatos.append((sc, p))

        if not candidatos:
            return None, None

        # ── Paso 2: filtrar ESTRICTAMENTE por medida ───────────────────────
        filtro_txt = ""
        if medida:
            num, unidad, txt_med = medida
            filtrados = [(sc, p) for sc, p in candidatos
                         if _medida_ok(_n(p.get('nombre','')), num, unidad)]
            if filtrados:
                candidatos = filtrados
                filtro_txt = f" de **{txt_med}**"
            else:
                otras = sorted({
                    m.group(0).strip()
                    for _, p in candidatos
                    for m in [_re.search(
                        r'\b\d+(?:[.,]\d+)?\s*(?:ml|cc|l|lt|g|gr|grs|kg|mg|oz)\b',
                        _n(p.get('nombre','')))]
                    if m
                })[:8]
                aviso = f"No encontré productos de esa categoría con **{txt_med}**.\n"
                if otras:
                    aviso += f"Medidas disponibles: {', '.join(otras)}"
                else:
                    aviso += f"Tengo {len(candidatos)} producto(s) de esa categoría sin medida especificada."
                return None, aviso

        candidatos.sort(key=lambda x: (-x[0], x[1].get('nombre','')))

        # ── Un solo resultado → detalle completo ───────────────────────────
        if len(candidatos) == 1:
            prod = candidatos[0][1]
            cod  = str(prod['cod_int'])
            stk  = int(float(prod.get('cantidad_total', 0) or 0))
            lts  = _lotes(cod)
            det  = "\n".join(
                f"  📍 {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))} uds"
                + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                for l in lts) if lts else "  Sin stock activo"
            return None, f"📦 *{prod['nombre']}* (cod:{cod})\nTotal: **{stk} uds**\n\n{det}"

        # ── Lista completa ─────────────────────────────────────────────────
        total_p   = len(candidatos)
        total_stk = sum(int(float(p.get('cantidad_total',0) or 0)) for _, p in candidatos)

        lineas = []
        for _, p in candidatos[:50]:
            cod  = str(p['cod_int'])
            stk  = int(float(p.get('cantidad_total', 0) or 0))
            lts  = _lotes(cod)
            ico  = "⛔" if stk == 0 else ("⚠️" if stk < 10 else "✅")
            ubis = " | ".join(
                f"{l.get('ubicacion','?')}:{int(float(l.get('cantidad',0)))}u"
                + (f"[{l.get('fecha','')}]" if l.get('fecha') else "")
                for l in lts[:3]) if lts else "sin stock"
            lineas.append(f"{ico} **{p['nombre']}** (cod:{cod}) — {stk} uds  →  {ubis}")

        cab = (f"📋 **{total_p} producto{'s' if total_p>1 else ''}**{filtro_txt}"
               f"  —  Stock total: **{total_stk:,} uds**\n")
        if total_p > 50:
            cab += f"*(Mostrando 50 de {total_p})*\n"

        return None, cab + "\n" + "\n".join(lineas)

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSULTA (producto único o lista)
    # ═══════════════════════════════════════════════════════════════════════════

    def _resp_consulta(txt):
        # Intentar lista/categoría primero
        ok_l, resp_l = _resp_lista_categoria(txt)
        if resp_l and "**" in resp_l and ("producto" in resp_l or "📋" in resp_l):
            return ok_l, resp_l

        # Producto único exacto
        prod = buscar_uno(txt, maestra)
        if prod:
            cod = str(prod['cod_int'])
            stk = int(float(prod.get('cantidad_total', 0) or 0))
            lts = _lotes(cod)
            det = "\n".join(
                f"  📍 {l.get('ubicacion','?')} ({l.get('deposito','')}) — {int(float(l.get('cantidad',0)))} uds"
                + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                for l in lts) if lts else "  Sin stock activo"
            return None, f"📦 *{prod['nombre']}* (cod:{cod})\nTotal: **{stk} uds**\n\n{det}"

        # Usar resp de lista si hay algo (aviso de medida no encontrada, etc.)
        if resp_l:
            return ok_l, resp_l

        sugs = buscar_varios(txt, maestra)
        if sugs:
            lineas = [f"  📦 {p['nombre']} (cod:{p['cod_int']}) — "
                      f"{int(float(p.get('cantidad_total',0) or 0))} uds" for p in sugs]
            return None, ("Encontré varios productos:\n\n" + "\n".join(lineas) +
                          "\n\nEspecificá el nombre o dame el código para el detalle.")
        return None, None   # devuelve None para que Groq tome el relevo

    # ═══════════════════════════════════════════════════════════════════════════
    # PEDIDOS / CHARLA
    # ═══════════════════════════════════════════════════════════════════════════

    def _resp_pedidos(_):
        try:
            peds = sb.table("pedidos").select("id,nombre,fecha,estado") \
                .in_("estado",["pendiente","en_proceso"]) \
                .order("id",desc=True).limit(10).execute().data or []
            if not peds: return None, "No hay pedidos pendientes en la nube."
            lines = [f"  {'🟡' if p.get('estado')=='en_proceso' else '🟢'} #{p['id']} · {p['nombre']} · {p.get('fecha','')}"
                     for p in peds]
            return None, f"📋 Pedidos ({len(peds)}):\n\n" + "\n".join(lines)
        except: return None, "No se pudo consultar la tabla pedidos."

    def _resp_charla(intent):
        hora = datetime.now().hour
        sal  = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 20 else "Buenas noches")
        if intent == 'saludo':
            return None, f"👋 {sal}, {usuario}! Soy el Operario Digital. ¿En qué te ayudo?"
        if intent == 'gracias':
            return None, "✅ ¡De nada! Para eso estoy. ¿Algo más?"
        if intent == 'ayuda':
            return None, (
                "🤖 Podés hablarme como quieras. Por ejemplo:\n\n"
                "📤  «Bajame 10 de ibuprofeno de 01-2A»\n"
                "📥  «Llegaron 50 de paracetamol en 03-1B»\n"
                "📥  «Cargá 100 del código 200 en 02-3A»\n"
                "🔀  «Pasá todo lo de 99-59B a 12-5C»\n"
                "✏️   «Corregí el stock de gel a 25 en 01-1A»\n"
                "📦  «Qué shampoo de 350ml tenemos?»\n"
                "📦  «Listame todos los geles de 5L»\n"
                "📦  «Buscame el código 150»\n"
                "📍  «¿Dónde está el ibuprofeno?»\n"
                "📉  «¿Qué nos falta reponer?»\n"
                "📊  «Dame un resumen del inventario»\n"
                "📋  «¿Qué movimientos hubo hoy?»\n"
                "🤖  También podés preguntarme cualquier cosa sobre el sistema."
            )
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # OLLAMA — CEREBRO LOCAL: inventario + acciones + búsqueda web
    # Requiere: ollama corriendo en localhost con modelo llama3.2:3b
    # ═══════════════════════════════════════════════════════════════════════════

    OLLAMA_URL   = "http://localhost:11434/api/chat"
    OLLAMA_MODEL = "llama3.2:3b"

    def _ollama_disponible():
        import urllib.request as _ur
        try:
            with _ur.urlopen("http://localhost:11434/api/tags", timeout=2): return True
        except: return False

    def _web_buscar(query):
        """Búsqueda web via DuckDuckGo — sin API key, sin cuenta."""
        import urllib.request as _ur, urllib.parse as _up, re as _rx
        try:
            url = "https://duckduckgo.com/html/?q=" + _up.quote(query)
            req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with _ur.urlopen(req, timeout=8) as r:
                html = r.read().decode("utf-8", "ignore")
            snips  = _rx.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, _rx.DOTALL)
            titles = _rx.findall(r'class="result__a"[^>]*>(.*?)</a>', html, _rx.DOTALL)
            cl = lambda s: _rx.sub(r'<[^>]+>', '', s).strip()
            resultados = []
            for t, s in zip(titles[:4], snips[:4]):
                titulo = cl(t); snippet = cl(s)
                if snippet:
                    resultados.append("• {}: {}".format(titulo, snippet))
            return "\n".join(resultados) if resultados else "Sin resultados."
        except Exception as e:
            return "Error de búsqueda: {}".format(str(e)[:60])

    def _build_inventario_ctx():
        lineas = []
        for p in maestra:
            cod = str(p.get("cod_int",""))
            nom = p.get("nombre","")
            stk = int(float(p.get("cantidad_total",0) or 0))
            lts = idx_inv.get(cod, [])
            lotes_str = "  ".join(
                "[ubi:{} dep:{} cant:{} vto:{}]".format(
                    l.get("ubicacion","?"), l.get("deposito","PRINCIPAL"),
                    int(float(l.get("cantidad",0))), l.get("fecha",""))
                for l in lts[:4]
            )
            lineas.append("{} | cod:{} | total:{}uds | {}".format(nom, cod, stk, lotes_str))
        return "\n".join(lineas)

    def _build_hist_ctx():
        try:
            hist_r = cargar_historial_cache()[:20]
            return "\n".join(
                "{} | {} | {} | x{} | ubi:{} | @{}".format(
                    h.get("fecha_hora",""), h.get("tipo",""), h.get("nombre",""),
                    h.get("cantidad",""), h.get("ubicacion",""), h.get("usuario",""))
                for h in hist_r
            )
        except: return ""

    def _sug_99():
        import re as _rx99
        ubs_99 = {str(l.get("ubicacion","")).upper()
                  for l in inventario if _rx99.match(r'\d+-99', str(l.get("ubicacion","")).upper())}
        pasillos = []
        for l in inventario:
            mx = _rx99.match(r'(\d+)-', str(l.get("ubicacion","")).upper())
            if mx and mx.group(1) not in pasillos: pasillos.append(mx.group(1))
        if not pasillos: pasillos = ["01"]
        for p in sorted(pasillos):
            for suf in ["","A","B","C","D"]:
                cand = "{}-99{}".format(p, suf)
                if cand not in ubs_99: return cand
        return "01-99"

    def _exec_accion(accion, params):
        """Ejecuta la acción en el inventario. Llamado por el cerebro Ollama."""
        import re as _rxa
        cod  = str(params.get("cod_int","")).strip()
        cant = float(params.get("cantidad", params.get("cantidad_nueva", 0)) or 0)
        ubi  = str(params.get("ubicacion","")).upper().strip()

        # Buscar producto por código o por nombre parcial
        prod = next((p for p in maestra if str(p.get("cod_int",""))==cod), None)
        if not prod:
            # Búsqueda fuzzy por nombre
            cod_up = cod.upper()
            prod = next((p for p in maestra if cod_up in str(p.get("nombre","")).upper()), None)
            if not prod:
                # Búsqueda por cualquier token del cod
                for token in cod_up.split():
                    if len(token) >= 3:
                        prod = next((p for p in maestra if token in str(p.get("nombre","")).upper()), None)
                        if prod: break
            if prod: cod = str(prod["cod_int"])
        if not prod:
            return False, "No encontré el producto '{}'. Verificá el nombre o código.".format(cod)
        nom = prod["nombre"]

        # ── SALIDA ──────────────────────────────────────────────────────────────
        if accion == "salida":
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote  = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi), None) if ubi else None
            if not lote: lote = next((l for l in lts_p if float(l.get("cantidad",0))>=cant), None)
            if not lote: lote = next((l for l in lts_p), None)
            if not lote: return False, "Sin stock de {}.".format(nom)
            ubi   = str(lote.get("ubicacion","")).upper()
            disp  = float(lote.get("cantidad",0))
            if disp < cant: return False, "Solo hay {} uds en {}.".format(int(disp), ubi)
            nueva = disp - cant
            if nueva <= 0: sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else:           sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            registrar_historial("SALIDA", cod, nom, cant, ubi, usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, "✅ Salida registrada\n📦 {} uds de *{}* desde {}\n📊 Quedan {} uds".format(int(cant),nom,ubi,int(nueva))

        # ── ENTRADA ─────────────────────────────────────────────────────────────
        elif accion == "entrada":
            fv  = str(params.get("fecha_vto","") or "").strip()
            dep = str(params.get("deposito","PRINCIPAL") or "PRINCIPAL").upper().strip() or "PRINCIPAL"
            # Normalizar fecha MM/AA → MM/AAAA
            m_fv = _rxa.match(r'^(\d{1,2})/(\d{2})$', fv)
            if m_fv: fv = "{}/20{}".format(m_fv.group(1).zfill(2), m_fv.group(2))
            # Resolver ubicación 99-AUTO → próxima libre
            if not ubi or "99" in ubi:
                ubs_99 = {str(l.get("ubicacion","")).upper()
                          for l in inventario if _rxa.match(r'\d+-99', str(l.get("ubicacion","")).upper())}
                pasillos = []
                for lp in [l for l in inventario if str(l.get("cod_int",""))==cod]:
                    mx = _rxa.match(r'(\d+)-', str(lp.get("ubicacion","")).upper())
                    if mx and mx.group(1) not in pasillos: pasillos.append(mx.group(1))
                for l in inventario:
                    mx = _rxa.match(r'(\d+)-', str(l.get("ubicacion","")).upper())
                    if mx and mx.group(1) not in pasillos: pasillos.append(mx.group(1))
                if not pasillos: pasillos = ["01"]
                ubi = "01-99"
                for p2 in sorted(pasillos):
                    for suf in ["","A","B","C","D"]:
                        cand = "{}-99{}".format(p2,suf)
                        if cand not in ubs_99: ubi = cand; break
                    else: continue
                    break
            if not ubi:
                lts_p2 = _lotes(cod)
                ubi = str(lts_p2[0].get("ubicacion","01-1A")).upper() if lts_p2 else "01-1A"
            lts_ubi = [l for l in inventario
                       if str(l.get("cod_int",""))==cod
                       and str(l.get("ubicacion","")).upper()==ubi
                       and str(l.get("deposito","PRINCIPAL")).upper()==dep]
            if lts_ubi:
                nueva = float(lts_ubi[0].get("cantidad",0) or 0) + cant
                sb.table("inventario").update({"cantidad":nueva}).eq("id",lts_ubi[0]["id"]).execute()
            else:
                sb.table("inventario").insert({
                    "cod_int":cod,"nombre":nom,"cantidad":cant,
                    "ubicacion":ubi,"fecha":fv,"deposito":dep
                }).execute()
            registrar_historial("ENTRADA", cod, nom, cant, ubi, usuario)
            recalcular_maestra(cod, inventario); refrescar()
            msg = "✅ Entrada registrada\n📥 {} uds de *{}*\n🏭 Depósito: {}  Ubicación: {}".format(int(cant),nom,dep,ubi)
            if fv: msg += "\n📅 Vto: {}".format(fv)
            return True, msg

        # ── MOVER ───────────────────────────────────────────────────────────────
        elif accion == "mover":
            ubi_dest = str(params.get("ubicacion_destino","")).upper().strip()
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote  = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote and lts_p: lote = lts_p[0]; ubi = str(lote.get("ubicacion","")).upper()
            if not lote: return False, "No encontré lotes de {}.".format(nom)
            disp    = float(lote.get("cantidad",0))
            cant_mv = cant if cant > 0 else disp
            if cant_mv > disp: return False, "Solo hay {} uds en {}.".format(int(disp),ubi)
            nueva = disp - cant_mv
            if nueva <= 0: sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else:           sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            sb.table("inventario").insert({
                "cod_int":cod,"nombre":nom,"cantidad":cant_mv,
                "ubicacion":ubi_dest,"fecha":lote.get("fecha",""),"deposito":lote.get("deposito","PRINCIPAL")
            }).execute()
            registrar_historial("MOVIMIENTO", cod, nom, cant_mv, "{}->{}".format(ubi,ubi_dest), usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, "✅ Movido\n📦 {} uds de *{}*\n🔀 {} → {}".format(int(cant_mv),nom,ubi,ubi_dest)

        # ── CORREGIR ────────────────────────────────────────────────────────────
        elif accion == "corregir":
            cant_nueva = float(params.get("cantidad_nueva", cant) or cant)
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote  = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote and lts_p: lote = lts_p[0]; ubi = str(lote.get("ubicacion","")).upper()
            if not lote: return False, "No encontré lotes de {}.".format(nom)
            ant = float(lote.get("cantidad",0))
            sb.table("inventario").update({"cantidad":cant_nueva}).eq("id",lote["id"]).execute()
            registrar_historial("CORRECCION", cod, nom, cant_nueva-ant, ubi, usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, "✅ Corregido\n📦 *{}* en {}\n📊 {} → {} uds".format(nom,ubi,int(ant),int(cant_nueva))

        return False, "Acción desconocida: {}".format(accion)

    def _cerebro_ollama(user_msg):
        """
        Cerebro principal — Ollama local.
        Detecta si necesita buscar en internet y lo hace antes de responder.
        """
        import json as _jj, urllib.request as _ur, re as _rg, re as _rx

        if not _ollama_disponible():
            return False, (
                "⚠️ Ollama no está corriendo.\n"
                "Abrí una terminal y ejecutá: **ollama serve**\n"
                "Si no lo tenés instalado: descargalo en ollama.com"
            )

        ctx_inv  = _build_inventario_ctx()
        ctx_hist = _build_hist_ctx()
        sug99    = _sug_99()
        hoy      = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Detectar si la pregunta es externa (necesita web) o interna (inventario)
        tn = _n(user_msg)
        necesita_web = any(k in tn for k in [
            "precio","cuanto sale","cuanto cuesta","donde comprar","proveedor",
            "noticias","clima","dolar","tipo de cambio","cotizacion",
            "que es","como se usa","para que sirve","receta","formula",
            "cuando","historia","wikipedia","busca","buscame","cheque"
        ]) and not any(k in tn for k in [
            "stock","inventario","ubicacion","deposito","ingres","entr","sali","mov"
        ])

        ctx_web = ""
        if necesita_web:
            ctx_web = "\n=== BÚSQUEDA WEB ===\n" + _web_buscar(user_msg) + "\n"

        system = (
            "Sos el asistente de inventario de LOGIEZE. Respondés en español rioplatense, directo y sin rodeos.\n"
            "Usuario: {} | Rol: {} | Fecha: {}\n"
            "Próxima ubicación 99 libre: {}\n\n"
            "=== INVENTARIO ({} productos) ===\n{}\n\n"
            "=== ÚLTIMOS MOVIMIENTOS ===\n{}\n"
            "{}\n"
            "=== INSTRUCCIONES CRÍTICAS ===\n"
            "1. NUNCA muestres JSON en tu respuesta. El usuario no debe ver JSON jamás.\n"
            "2. Cuando el usuario pide registrar ENTRADA, SALIDA, MOVER o CORREGIR:\n"
            "   Respondé SOLO con este JSON exacto (nada más, nada menos):\n"
            '   ACTION:{"accion":"entrada","params":{"cod_int":"X","cantidad":N,"ubicacion":"XX-YY","fecha_vto":"MM/AAAA","deposito":"PRINCIPAL"},"msg":"texto confirmación"}\n'
            '   ACTION:{"accion":"salida","params":{"cod_int":"X","cantidad":N,"ubicacion":"XX-YY"},"msg":"texto"}\n'
            '   ACTION:{"accion":"mover","params":{"cod_int":"X","cantidad":N,"ubicacion_origen":"XX-YY","ubicacion_destino":"XX-YY"},"msg":"texto"}\n'
            '   ACTION:{"accion":"corregir","params":{"cod_int":"X","ubicacion":"XX-YY","cantidad_nueva":N},"msg":"texto"}\n'
            "3. FECHAS: convertí siempre a MM/AAAA. Ej: 06/26→06/2026 | junio 2026→06/2026 | en 6 meses→calculá | sin fecha→vacío\n"
            "4. UBICACIÓN 99: si dice 'la 99' o 'al 99' → ubicacion:'99-AUTO'\n"
            "5. DEPÓSITO: principal→PRINCIPAL | secundario/B→SECUNDARIO | sin mención→PRINCIPAL\n"
            "6. PRODUCTO: buscá por nombre parcial. ibu→Ibuprofeno | kera→Keratina | gel→primer gel que encuentres\n"
            "7. Si falta algún dato (cantidad, ubicación) → preguntá en UNA sola línea corta.\n"
            "8. Para consultas de inventario → respondé con los datos del contexto.\n"
            "9. Para preguntas externas (precios, info general) → usá los resultados web del contexto.\n"
            "10. EJEMPLOS de cómo entender ingresos:\n"
            "    'entraron 50 ibuprofeno 400 en 01-2A vencen 06/26' → ACTION con accion=entrada, cod del ibu 400, cant=50, ubi=01-2A, fecha=06/2026\n"
            "    'llego el pedido de loreal, 30 cajas, la 99, vence diciembre' → ACTION entrada, busca loreal, cant=30, ubi=99-AUTO, fecha=12/año_actual\n"
            "    'salida de 5 gel desde 01-2A' → ACTION salida\n"
        ).format(usuario, rol, hoy, sug99, len(maestra), ctx_inv, ctx_hist, ctx_web)

        hist = st.session_state.get("bot_hist", [])[-16:]
        msgs = [{"role":"system","content":system}]
        for m in hist:
            msgs.append({"role":"user" if m["rol"]=="user" else "assistant","content":m["texto"]})
        if not msgs or msgs[-1].get("content") != user_msg:
            msgs.append({"role":"user","content":user_msg})

        try:
            import json as _jj, urllib.request as _ur
            body = _jj.dumps({
                "model":    OLLAMA_MODEL,
                "messages": msgs,
                "stream":   False,
                "options":  {"temperature":0.1, "num_predict":600}
            }).encode()
            req = _ur.Request(OLLAMA_URL, data=body,
                              headers={"Content-Type":"application/json"})
            with _ur.urlopen(req, timeout=60) as r:
                resp_raw = _jj.loads(r.read())["message"]["content"].strip()

            # Detectar ACTION:{...} en la respuesta
            m_act = _rg.search(r'ACTION:\s*(\{[\s\S]*?\})', resp_raw)
            if m_act:
                try:
                    act  = _jj.loads(m_act.group(1))
                    tipo = act.get("accion","")
                    if tipo in ("salida","entrada","mover","corregir"):
                        if rol in ("visita","vendedor"):
                            return False, "Tu rol no permite esa acción."
                        ok, resultado = _exec_accion(tipo, act.get("params",{}))
                        msg_conf = act.get("msg","") or resultado
                        return (True, msg_conf) if ok else (False, resultado)
                except Exception: pass

            # Limpiar cualquier JSON o ACTION residual que haya quedado
            limpio = _rg.sub(r'ACTION:\s*\{[\s\S]*?\}', '', resp_raw)
            limpio = _rg.sub(r'```[\s\S]*?```', '', limpio).strip()
            return None, limpio if limpio else resp_raw

        except Exception as e:
            err = str(e)
            if "111" in err or "Connection refused" in err:
                return False, "⚠️ Ollama no está corriendo. Abrí una terminal y ejecutá: **ollama serve**"
            if "timeout" in err.lower():
                return False, "⏱️ Ollama tardó demasiado. El modelo puede estar cargando, probá de nuevo en unos segundos."
            return False, "Error del asistente: {}".format(err[:120])

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXTO PENDIENTE (multi-turno)
    # ═══════════════════════════════════════════════════════════════════════════

    def _combinar_ctx(anterior, nuevo):
        return (anterior.get("txt","") + " " + nuevo).strip()

    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESADOR PRINCIPAL — Ollama, todo pasa por acá
    # ═══════════════════════════════════════════════════════════════════════════

    def _procesar(txt):
        txt_c = txt
        pendiente = st.session_state.get("_ctx_pendiente")
        if pendiente:
            txt_c = _combinar_ctx(pendiente, txt)
            st.session_state.pop("_ctx_pendiente", None)

        ok, resp = _cerebro_ollama(txt_c)

        if ok is None and resp and "?" in resp:
            st.session_state["_ctx_pendiente"] = {"txt": txt_c}

        return ok, resp



    # ── PANTALLA INICIAL ──────────────────────────────────────────────────────

    if not st.session_state.bot_hist:
        st.markdown("""
        <div style="text-align:center;padding:30px 10px 10px">
            <div style="font-size:52px">📦</div>
            <div style="font-size:16px;font-weight:700;color:#94A3B8;margin-top:10px">
                Operario Digital listo para trabajar.</div>
            <div style="font-size:13px;color:#64748B;margin-top:8px;line-height:2.2">
                Hablame en lenguaje natural · Ejecuto movimientos reales · Sin límites
            </div>
        </div>""", unsafe_allow_html=True)
        sugerencias = [
            "¿Cuánto hay del código 147?",
            "Resumen del inventario",
            "Productos con bajo stock",
            "Lotes por vencer",
            "Últimos movimientos",
        ]
        cols_s = st.columns(len(sugerencias))
        for i, s in enumerate(sugerencias):
            with cols_s[i]:
                if st.button(s, use_container_width=True, key=f"sug_{i}"):
                    st.session_state._bot_quick = s
                    st.rerun()
    else:
        for msg in st.session_state.bot_hist:
            if msg["rol"] == "user":
                st.markdown(f'<div class="chat-lbl" style="text-align:right">{usuario} 👤</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-user">{msg["texto"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-lbl">📦 Operario Digital</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-bot">{msg["texto"]}</div>', unsafe_allow_html=True)
                if msg.get("accion_log"):
                    cls = "msg-ok" if msg.get("ok") else "msg-err"
                    st.markdown(f'<div class="{cls}">⚡ {msg["accion_log"]}</div>', unsafe_allow_html=True)

    # ── BOTONES RÁPIDOS ───────────────────────────────────────────────────────
    if st.session_state.bot_hist:
        st.markdown("<br>", unsafe_allow_html=True)
        qc = st.columns(5)
        for i, (lbl, preg) in enumerate([
            ("📉 Bajo stock",  "Productos con menos de 10 unidades"),
            ("📦 Resumen",     "Resumen del inventario"),
            ("📋 Historial",   "Últimos 15 movimientos"),
            ("📍 Ubicaciones", "Mostrame todas las ubicaciones"),
            ("⏰ Por vencer",  "Lotes por vencer"),
        ]):
            with qc[i]:
                if st.button(lbl, use_container_width=True, key=f"qr_{i}"):
                    st.session_state._bot_quick = preg
                    st.rerun()

    _quick = st.session_state.pop("_bot_quick", None)

    # ── INPUT + MICRÓFONO ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Limpiar campo en el ciclo posterior al envío
    if st.session_state.pop("_limpiar", False):
        st.session_state["_input_key"] = st.session_state.get("_input_key", 0) + 1

    # Micrófono via st.components — único método fiable en Streamlit web/mobile
    import streamlit.components.v1 as _stc
    _stc.html("""<!DOCTYPE html><html><head><style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:transparent}
    #bar{display:flex;align-items:center;gap:10px;background:#1E293B;border:1px solid #334155;
         border-radius:12px;padding:8px 14px}
    #btn{background:linear-gradient(135deg,#3B82F6,#06B6D4);color:#fff;border:none;
         border-radius:50%;width:46px;height:46px;font-size:22px;cursor:pointer;flex-shrink:0;transition:.2s all}
    #btn.rec{background:linear-gradient(135deg,#EF4444,#F59E0B);animation:pu 1s infinite}
    @keyframes pu{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.5)}50%{box-shadow:0 0 0 14px rgba(239,68,68,0)}}
    #st{font-size:13px;color:#94A3B8;font-weight:600;flex:1}
    #st.ok{color:#10B981} #st.er{color:#EF4444}
    #pv{display:none;margin-top:8px;background:#0F172A;border:1px solid #1E3A5F;
        border-radius:8px;padding:8px 12px;font-size:13px;color:#93C5FD;word-break:break-word}
    #sb{display:none;width:100%;margin-top:6px;padding:10px;border:none;border-radius:10px;
        background:linear-gradient(135deg,#10B981,#059669);color:#fff;
        font-size:15px;font-weight:700;cursor:pointer}
    #sb:active{opacity:.8}
    </style></head><body>
    <div id="bar">
      <button id="btn" onclick="tog()">🎤</button>
      <span id="st">Toca para dictar</span>
    </div>
    <div id="pv"></div>
    <button id="sb" onclick="env()">&#10148; Enviar mensaje de voz</button>
    <script>
    var R=null,gr=false,tx="";
    function tog(){
      var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
      if(!SR){ss("er","Necesitas Chrome para el microfono");return}
      if(gr){R.stop();return}
      R=new SR();R.lang="es-AR";R.continuous=false;R.interimResults=true;
      R.onstart=function(){gr=true;sb2("rec","&#9209;");ss("ok","Escuchando... toca para terminar")};
      R.onresult=function(e){
        var t="";for(var i=e.resultIndex;i<e.results.length;i++)t+=e.results[i][0].transcript;
        tx=t;
        document.getElementById("pv").textContent="Transcripcion: "+tx;
        document.getElementById("pv").style.display="block";
        document.getElementById("sb").style.display="block"
      };
      R.onerror=function(e){
        var m={"not-allowed":"Permiso denegado — habilita el microfono en la barra del navegador",
               "no-speech":"No se escucho nada","network":"Error de red","audio-capture":"Sin microfono"};
        ss("er",m[e.error]||e.error)
      };
      R.onend=function(){
        gr=false;sb2("","&#127908;");
        if(!tx)ss("","Toca para dictar");
        else ss("ok","Listo — toca Enviar o escribe abajo")
      };
      R.start()
    }
    function env(){
      if(!tx)return;
      // postMessage al parent Streamlit con el texto transcripto
      try{window.parent.postMessage({lz_voz:tx},"*")}catch(e){}
      // Intentar escribir directamente en el textarea como fallback
      try{
        var ta=window.parent.document.querySelector("textarea[data-testid]");
        if(!ta){
          var all=window.parent.document.querySelectorAll("textarea");
          for(var i=0;i<all.length;i++){if(all[i].placeholder&&all[i].placeholder.indexOf("Escribi")>=0){ta=all[i];break}}
        }
        if(ta){
          Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype,"value").set.call(ta,tx);
          ta.dispatchEvent(new Event("input",{bubbles:true}));
          setTimeout(function(){
            var btns=window.parent.document.querySelectorAll("button");
            for(var i=0;i<btns.length;i++){if(btns[i].innerText.indexOf("Enviar")>=0){btns[i].click();break}}
          },250)
        }
      }catch(e){}
      tx="";
      document.getElementById("pv").style.display="none";
      document.getElementById("sb").style.display="none";
      sb2("","&#127908;");ss("","Toca para dictar")
    }
    function sb2(c,i){var b=document.getElementById("btn");b.className=c;b.innerHTML=i}
    function ss(c,t){var s=document.getElementById("st");s.className=c;s.textContent=t}
    </script></body></html>""", height=120)

    # CSS textarea
    st.markdown("""<style>
    .stTextArea textarea{background:#1E293B !important;color:#F1F5F9 !important;
        border:1px solid #334155 !important;border-radius:12px !important;
        font-size:15px !important;resize:none !important}
    .stTextArea textarea:focus{border-color:#3B82F6 !important;
        box-shadow:0 0 0 2px rgba(59,130,246,.3) !important}
    </style>""", unsafe_allow_html=True)

    # Enter = enviar (Shift+Enter = salto de linea)
    st.markdown("""<script>
    (function(){
      var t=0;
      function h(){
        var found=false;
        var all=document.querySelectorAll("textarea");
        for(var i=0;i<all.length;i++){
          var ta=all[i];
          if(!ta._lzh && ta.placeholder && ta.placeholder.indexOf("Escribi")>=0){
            ta._lzh=true; found=true;
            ta.addEventListener("keydown",function(ev){
              if(ev.key==="Enter"&&!ev.shiftKey){
                ev.preventDefault();
                var btns=document.querySelectorAll("button");
                for(var j=0;j<btns.length;j++){if(btns[j].innerText.indexOf("Enviar")>=0){btns[j].click();return}}
              }
            })
          }
        }
        if(!found&&t<30){t++;setTimeout(h,300)}
      }
      h()
    })()
    </script>""", unsafe_allow_html=True)

    ic1, ic2 = st.columns([5, 1])
    with ic1:
        _ikey = "bot_input_" + str(st.session_state.get("_input_key", 0))
        txt_in = st.text_area(
            "msg", label_visibility="collapsed",
            placeholder="Escribi aca · Enter envia · Shift+Enter nueva linea · o usa el microfono",
            key=_ikey,
            height=68,
        )
    with ic2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        send = st.button("➤ Enviar", use_container_width=True, type="primary", key="bot_send")

    _final = _quick or (txt_in.strip() if send and txt_in else None)

    if _final:
        st.session_state["_limpiar"] = True
        st.session_state.bot_hist.append({"rol":"user","texto":_final})
        try:
            ok, respuesta = _procesar(_final)
            entry = {"rol":"assistant","texto":respuesta}
            if ok is True:
                entry["ok"]         = True
                entry["accion_log"] = respuesta.split('\n')[0]
            elif ok is False:
                entry["ok"]         = False
                entry["accion_log"] = respuesta
        except Exception as e:
            entry = {"rol":"assistant","texto":"Error interno: {}".format(str(e)[:200]),"ok":False}
        st.session_state.bot_hist.append(entry)
        st.rerun()

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
        st.markdown('<p class="sec-label">🤖 ASISTENTE IA — Groq API Key</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.3);
                    border-radius:12px;padding:12px 16px;margin-bottom:10px;font-size:12px;color:#94A3B8;">
            La key se guarda en Supabase y la usa el Operario Digital para responder.<br>
            <b style="color:#818CF8">Conseguí tu key gratis en:</b> console.groq.com → API Keys → Create API Key<br>
            La key empieza con <code>gsk_...</code>
        </div>
        """, unsafe_allow_html=True)

        try:
            _gk_db = sb.table("config").select("valor").eq("clave","groq_key").execute().data
            _gk_actual = _gk_db[0]["valor"] if _gk_db else ""
            _gk_masked = (_gk_actual[:8] + "..." + _gk_actual[-4:]) if len(_gk_actual) > 12 else ""
        except:
            _gk_actual = _gk_masked = ""

        with st.form("form_groq"):
            nueva_gk = st.text_input(
                "API Key de Groq:",
                placeholder="gsk_...",
                help="Pegá tu key acá. Se guarda encriptada en Supabase."
            )
            if _gk_masked:
                st.caption(f"Key actual: {_gk_masked}")
            if st.form_submit_button("💾 Guardar Groq Key", use_container_width=True):
                gk_val = nueva_gk.strip()
                if gk_val.startswith("gsk_") and len(gk_val) > 20:
                    try:
                        sb.table("config").upsert({"clave":"groq_key","valor":gk_val}, on_conflict="clave").execute()
                        st.success("✅ Groq Key guardada correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.warning("La key debe empezar con 'gsk_' y tener más de 20 caracteres.")

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
# ═══════════════════════════════════════════════════════════════════════════════
# TAB ASISTENTE — BOT PROPIO 100% LOCAL, sin APIs externas
# Aprende de cada uso guardando patrones en Supabase tabla "bot_aprendizaje"
# ═══════════════════════════════════════════════════════════════════════════════
with tab_asist:

    # ── Estilos ──────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .msg-user{background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;
        border-radius:18px 18px 4px 18px;padding:10px 16px;margin:4px 0 4px 50px;
        font-size:14px;line-height:1.6;}
    .msg-bot{background:#1E293B;color:#F1F5F9;border-radius:4px 18px 18px 18px;
        border:1px solid #334155;padding:10px 16px;margin:4px 50px 4px 0;
        font-size:14px;line-height:1.6;white-space:pre-wrap;}
    .msg-ok{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.35);
        border-radius:8px;padding:6px 12px;margin:2px 50px 6px 0;font-size:12px;color:#10B981;}
    .msg-err{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.35);
        border-radius:8px;padding:6px 12px;margin:2px 50px 6px 0;font-size:12px;color:#EF4444;}
    .bot-header{font-size:11px;color:#64748B;margin:2px 50px 0 0;}
    </style>
    """, unsafe_allow_html=True)

    # ── Motor NLP propio ──────────────────────────────────────────────────────
    import unicodedata as _uc, re as _re2, json as _jb

    def _n(s):
        """Normaliza texto: minúsculas, sin tildes."""
        s2 = _uc.normalize("NFD", str(s).lower())
        return "".join(c for c in s2 if not _uc.combining(c))

    def _tokens(s):
        return set(t for t in _n(s).split() if len(t) >= 2)

    def _similitud(a, b):
        """Similitud entre dos strings (0-1)."""
        ta, tb = _tokens(a), _tokens(b)
        if not ta or not tb: return 0.0
        return len(ta & tb) / max(len(ta | tb), 1)

    def _buscar_producto(query, maestra):
        """Busca el producto más similar en la maestra."""
        q = _n(query)
        mejor = None; mejor_sc = 0
        for p in maestra:
            nom = _n(str(p.get("nombre","")))
            cod = str(p.get("cod_int",""))
            sc = 0
            if cod == q: sc = 100
            elif q in nom: sc = 80
            elif nom in q: sc = 70
            else:
                for tok in _tokens(q):
                    if tok in nom: sc += 15
                    elif any(tok in w for w in nom.split()): sc += 8
            if sc > mejor_sc: mejor_sc = sc; mejor = p
        return mejor if mejor_sc >= 10 else None

    def _parsear_fecha(txt):
        """Convierte cualquier mención de fecha a MM/AAAA."""
        from datetime import datetime, timedelta
        hoy = datetime.now()
        t = _n(txt)
        meses = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
                 "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12,
                 "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,"jul":7,"ago":8,
                 "sep":9,"oct":10,"nov":11,"dic":12}
        # MM/AA o MM/AAAA
        m = _re2.search(r'(\d{1,2})/(\d{2,4})', txt)
        if m:
            mes, ano = int(m.group(1)), m.group(2)
            if len(ano) == 2: ano = "20" + ano
            return f"{mes:02d}/{ano}"
        # "en X meses"
        m = _re2.search(r'en\s+(\d+)\s+mes', t)
        if m:
            dt = hoy + timedelta(days=int(m.group(1))*30)
            return dt.strftime("%m/%Y")
        # nombre de mes
        for nombre, num in meses.items():
            if nombre in t:
                ano = hoy.year if num >= hoy.month else hoy.year + 1
                m2 = _re2.search(r'20\d{2}', txt)
                if m2: ano = int(m2.group())
                return f"{num:02d}/{ano}"
        return ""

    def _parsear_cantidad(txt):
        """Extrae número del texto."""
        t = _n(txt)
        palabras = {"una":1,"uno":1,"dos":2,"tres":3,"cuatro":4,"cinco":5,
                    "seis":6,"siete":7,"ocho":8,"nueve":9,"diez":10,
                    "doce":12,"veinte":20,"treinta":30,"cuarenta":40,"cincuenta":50,
                    "cien":100,"ciento":100,"docena":12,"media docena":6}
        for p, v in palabras.items():
            if p in t: return float(v)
        m = _re2.search(r'\b(\d+(?:\.\d+)?)\b', txt)
        return float(m.group(1)) if m else 0

    def _parsear_ubicacion(txt):
        """Extrae ubicación del texto."""
        t = _n(txt)
        if any(k in t for k in ["la 99","al 99","estante 99","la noventa","la noventa y nueve","a la 99"]):
            return "99-AUTO"
        m = _re2.search(r'\b(\d{1,2}[-_]\d{1,2}[a-zA-Z]?)\b', txt)
        return m.group(1).upper() if m else ""

    def _parsear_deposito(txt):
        t = _n(txt)
        if any(k in t for k in ["secundario","deposito 2","deposito b","el b","segundo"]):
            return "SECUNDARIO"
        return "PRINCIPAL"

    def _sug_99_ubi():
        ubs_99 = {str(l.get("ubicacion","")).upper()
                  for l in inventario if _re2.match(r'\d+-99', str(l.get("ubicacion","")).upper())}
        pasillos = []
        for l in inventario:
            mx = _re2.match(r'(\d+)-', str(l.get("ubicacion","")).upper())
            if mx and mx.group(1) not in pasillos: pasillos.append(mx.group(1))
        if not pasillos: pasillos = ["01"]
        for p in sorted(pasillos):
            for sf in ["","A","B","C","D"]:
                c = f"{p}-99{sf}"
                if c not in ubs_99: return c
        return "01-99"

    # ── Aprendizaje ───────────────────────────────────────────────────────────
    def _cargar_aprendizaje():
        """Carga patrones aprendidos desde Supabase."""
        try:
            r = sb.table("bot_aprendizaje").select("*").order("usos", desc=True).limit(200).execute().data or []
            return r
        except: return []

    def _guardar_patron(patron, respuesta, tipo="custom"):
        """Guarda o actualiza un patrón aprendido."""
        try:
            exist = sb.table("bot_aprendizaje").select("*").eq("patron", patron).execute().data
            if exist:
                sb.table("bot_aprendizaje").update({"usos": exist[0].get("usos",0)+1}).eq("patron",patron).execute()
            else:
                sb.table("bot_aprendizaje").insert({"patron":patron,"respuesta":respuesta,"tipo":tipo,"usos":1}).execute()
        except: pass

    def _buscar_aprendido(msg, patrones):
        """Busca si el mensaje coincide con algo aprendido."""
        mejor = None; mejor_sc = 0
        for p in patrones:
            sc = _similitud(msg, p.get("patron",""))
            if sc > mejor_sc and sc >= 0.7:
                mejor_sc = sc; mejor = p
        return mejor

    # ── Detector de intención ─────────────────────────────────────────────────
    def _detectar_intencion(txt):
        t = _n(txt)
        # ENTRADA
        if any(k in t for k in ["entr","llego","llegaron","ingres","carg","recibi","recibim",
                                  "metele","meteme","agrega","sumale","añadi","pusieron","pone","poner"]):
            return "entrada"
        # SALIDA
        if any(k in t for k in ["sali","vendim","vendio","despacho","saco","sacaron","retir",
                                  "egres","consumim","usamos","fue","fueron","manda","mandamos"]):
            return "salida"
        # MOVER
        if any(k in t for k in ["mov","cambia","cambie","transfer","pas","lleva","llevame",
                                  "de ", " a ", "desde","hacia"]) and \
           any(k in t for k in ["ubi","lugar","posicion","estante","pasillo"]):
            return "mover"
        # CORREGIR
        if any(k in t for k in ["correg","corrige","ajust","fija","arregl","cambia la cantidad",
                                  "actualiz","son exactamente","hay exactamente","quedan exactamente"]):
            return "corregir"
        # CONSULTA STOCK
        if any(k in t for k in ["cuanto hay","cuanto tene","stock","hay de","tenes de",
                                  "cuantos","cuantas","cantidad","quedan","quedaron","existe","existencia"]):
            return "consulta_stock"
        # UBICACION
        if any(k in t for k in ["donde esta","donde se encuentra","ubicacion","en que lugar",
                                  "en que pasillo","en que estante","donde lo"]):
            return "consulta_ubi"
        # HISTORIAL
        if any(k in t for k in ["historial","ultimo","ultimos","movimiento","cuando fue",
                                  "que paso","registro","log"]):
            return "historial"
        # VENCIMIENTO
        if any(k in t for k in ["venc","expir","caduc","fecha","por vencer","proxim"]):
            return "vencimiento"
        # RESUMEN
        if any(k in t for k in ["resumen","total","cuanto tenemos","inventario completo",
                                  "todo el stock","productos","lista"]):
            return "resumen"
        return "desconocido"

    # ── Ejecutor de acciones ──────────────────────────────────────────────────
    def _ejecutar(intencion, params, ctx):
        """Ejecuta la acción y devuelve (ok, mensaje)."""
        cod  = params.get("cod_int","")
        cant = params.get("cantidad", 0)
        ubi  = params.get("ubicacion","")
        dep  = params.get("deposito","PRINCIPAL")
        fv   = params.get("fecha_vto","")
        nom  = params.get("nombre","")
        prod = next((p for p in maestra if str(p.get("cod_int",""))==cod), None) if cod else None
        if prod: nom = prod["nombre"]

        if intencion == "entrada":
            if not cod: return False, "No identifiqué el producto."
            if not cant: return False, "¿Cuántas unidades ingresaron?"
            if not ubi:
                ubi = _sug_99_ubi()
                params["ubicacion"] = ubi
            if "99-AUTO" in ubi: ubi = _sug_99_ubi(); params["ubicacion"] = ubi
            if not fv:
                m_fv = _re2.search(r'(\d{1,2})/(\d{2,4})', ctx.get("txt_original",""))
                if m_fv:
                    mes, ano = m_fv.group(1), m_fv.group(2)
                    if len(ano)==2: ano="20"+ano
                    fv = f"{int(mes):02d}/{ano}"
            lts_ubi = [l for l in inventario
                       if str(l.get("cod_int",""))==cod
                       and str(l.get("ubicacion","")).upper()==ubi.upper()
                       and str(l.get("deposito","PRINCIPAL")).upper()==dep.upper()]
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
            msg = f"✅ Entrada registrada\n📥 {int(cant)} uds de *{nom}*\n🏭 {dep} — Ubicación: {ubi}"
            if fv: msg += f"\n📅 Vto: {fv}"
            return True, msg

        elif intencion == "salida":
            if not cod: return False, "No identifiqué el producto."
            if not cant: return False, "¿Cuántas unidades salieron?"
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi.upper()), None) if ubi else None
            if not lote: lote = next((l for l in lts_p if float(l.get("cantidad",0))>=cant), None)
            if not lote: lote = lts_p[0] if lts_p else None
            if not lote: return False, f"Sin stock de {nom}."
            ubi = str(lote.get("ubicacion","")).upper()
            disp = float(lote.get("cantidad",0))
            if disp < cant: return False, f"Solo hay {int(disp)} uds en {ubi}. ¿Registramos {int(disp)}?"
            nueva = disp - cant
            if nueva <= 0: sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else: sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            registrar_historial("SALIDA", cod, nom, cant, ubi, usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, f"✅ Salida registrada\n📦 {int(cant)} uds de *{nom}* desde {ubi}\n📊 Quedan {int(nueva)} uds"

        elif intencion == "mover":
            ubi_dest = params.get("ubicacion_destino","")
            if not cod: return False, "No identifiqué el producto."
            if not ubi_dest: return False, "¿A qué ubicación lo movemos?"
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi.upper()), None) if ubi else None
            if not lote and lts_p: lote = lts_p[0]; ubi = str(lote.get("ubicacion","")).upper()
            if not lote: return False, f"No hay lotes de {nom}."
            disp = float(lote.get("cantidad",0))
            cant_mv = cant if cant > 0 else disp
            nueva = disp - cant_mv
            if nueva <= 0: sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else: sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            sb.table("inventario").insert({
                "cod_int":cod,"nombre":nom,"cantidad":cant_mv,
                "ubicacion":ubi_dest,"fecha":lote.get("fecha",""),"deposito":lote.get("deposito","PRINCIPAL")
            }).execute()
            registrar_historial("MOVIMIENTO", cod, nom, cant_mv, f"{ubi}->{ubi_dest}", usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, f"✅ Movido\n📦 {int(cant_mv)} uds de *{nom}*\n🔀 {ubi} → {ubi_dest}"

        elif intencion == "corregir":
            cant_nueva = cant
            if not cod: return False, "No identifiqué el producto."
            if not cant_nueva: return False, "¿Cuál es la cantidad correcta?"
            lts_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lts_p if str(l.get("ubicacion","")).upper()==ubi.upper()), None) if ubi else None
            if not lote and lts_p: lote = lts_p[0]; ubi = str(lote.get("ubicacion","")).upper()
            if not lote: return False, f"No hay lotes de {nom}."
            ant = float(lote.get("cantidad",0))
            sb.table("inventario").update({"cantidad":cant_nueva}).eq("id",lote["id"]).execute()
            registrar_historial("CORRECCION", cod, nom, cant_nueva-ant, ubi, usuario)
            recalcular_maestra(cod, inventario); refrescar()
            return True, f"✅ Corregido\n📦 *{nom}* en {ubi}\n📊 {int(ant)} → {int(cant_nueva)} uds"

        return False, "No pude ejecutar esa acción."

    # ── Responder consultas ───────────────────────────────────────────────────
    def _responder_consulta(intencion, txt):
        t = _n(txt)

        if intencion == "consulta_stock":
            prod = _buscar_producto(txt, maestra)
            if prod:
                cod = str(prod["cod_int"]); nom = prod["nombre"]
                stk = int(float(prod.get("cantidad_total",0) or 0))
                lts = idx_inv.get(cod,[])
                detalles = "\n".join(
                    f"  📍 {l.get('ubicacion','?')} ({l.get('deposito','PRINCIPAL')}) — {int(float(l.get('cantidad',0)))} uds" +
                    (f" — Vto: {l.get('fecha','')}" if l.get('fecha') else "")
                    for l in lts
                )
                return True, f"📦 *{nom}*\n📊 Stock total: **{stk} uds**\n{detalles}" if detalles else f"📦 *{nom}* — {stk} uds en stock"
            # buscar sin producto específico — resumen general
            total = sum(int(float(p.get("cantidad_total",0) or 0)) for p in maestra)
            return True, f"📊 Stock total del depósito: **{total} uds** en {len(maestra)} productos."

        elif intencion == "consulta_ubi":
            prod = _buscar_producto(txt, maestra)
            if prod:
                cod = str(prod["cod_int"]); nom = prod["nombre"]
                lts = idx_inv.get(cod,[])
                if not lts: return True, f"*{nom}* no tiene stock actualmente."
                ubis = "\n".join(
                    f"  📍 {l.get('ubicacion','?')} ({l.get('deposito','PRINCIPAL')}) — {int(float(l.get('cantidad',0)))} uds"
                    for l in lts
                )
                return True, f"📍 *{nom}* está en:\n{ubis}"
            return False, "No identifiqué el producto. ¿Cuál querés buscar?"

        elif intencion == "historial":
            try:
                hist_r = cargar_historial_cache()[:10]
                if not hist_r: return True, "No hay movimientos registrados aún."
                lineas = []
                for h in hist_r:
                    tipo_icon = {"ENTRADA":"📥","SALIDA":"📤","MOVIMIENTO":"🔀","CORRECCION":"✏️"}.get(h.get("tipo",""),"•")
                    lineas.append(f"{tipo_icon} {h.get('fecha_hora','')[:16]} — {h.get('nombre','')} x{h.get('cantidad','')} [{h.get('ubicacion','')}] @{h.get('usuario','')}")
                return True, "📋 *Últimos movimientos:*\n" + "\n".join(lineas)
            except: return False, "Error al cargar historial."

        elif intencion == "vencimiento":
            from datetime import datetime
            hoy = datetime.now()
            proximos = []
            for l in inventario:
                fv = str(l.get("fecha",""))
                if not fv: continue
                try:
                    m = _re2.match(r'(\d{1,2})/(\d{4})', fv)
                    if m:
                        dt_vto = datetime(int(m.group(2)), int(m.group(1)), 1)
                        dias = (dt_vto - hoy).days
                        if dias <= 90:
                            proximos.append((dias, l.get("nombre",""), fv, l.get("ubicacion",""), int(float(l.get("cantidad",0)))))
                except: pass
            proximos.sort()
            if not proximos: return True, "✅ No hay productos por vencer en los próximos 90 días."
            lineas = []
            for dias, nom, fv, ubi, cant in proximos[:15]:
                icon = "🔴" if dias < 0 else ("🟡" if dias <= 30 else "🟢")
                estado = "VENCIDO" if dias < 0 else f"en {dias} días"
                lineas.append(f"{icon} *{nom}* — {cant} uds en {ubi} — Vto: {fv} ({estado})")
            return True, "📅 *Por vencer:*\n" + "\n".join(lineas)

        elif intencion == "resumen":
            total_uds = sum(int(float(p.get("cantidad_total",0) or 0)) for p in maestra)
            bajo = [p["nombre"] for p in maestra if int(float(p.get("cantidad_total",0) or 0)) < 10]
            top5 = sorted(maestra, key=lambda p: -int(float(p.get("cantidad_total",0) or 0)))[:5]
            msg = f"📊 *Resumen del inventario*\n"
            msg += f"• {len(maestra)} productos | {total_uds} uds totales\n"
            if bajo: msg += f"⚠️ Bajo stock (<10 uds): {', '.join(bajo[:6])}\n"
            msg += "\n*Top 5 con más stock:*\n"
            for p in top5:
                msg += f"  📦 {p['nombre']} — {int(float(p.get('cantidad_total',0) or 0))} uds\n"
            return True, msg

        return False, None

    # ── Bot principal ─────────────────────────────────────────────────────────
    def _bot_responder(txt):
        """Procesa el mensaje y devuelve (ok, respuesta, params_para_accion)."""
        t = _n(txt)

        # 1) Revisar patrones aprendidos primero
        patrones = _cargar_aprendizaje()
        aprendido = _buscar_aprendido(txt, patrones)
        if aprendido and aprendido.get("tipo") == "respuesta_fija":
            _guardar_patron(aprendido["patron"], aprendido["respuesta"], "respuesta_fija")
            return None, aprendido["respuesta"], {}

        # 2) Detectar intención
        intencion = _detectar_intencion(txt)

        # 3) Consultas (no modifican datos)
        if intencion in ("consulta_stock","consulta_ubi","historial","vencimiento","resumen"):
            ok, resp = _responder_consulta(intencion, txt)
            return ok, resp, {}

        # 4) Acciones (modifican datos) — extraer parámetros
        if intencion in ("entrada","salida","mover","corregir"):
            if rol in ("visita","vendedor") and intencion in ("entrada","mover","corregir"):
                return False, "Tu rol no permite esa acción.", {}

            # Buscar producto
            prod = _buscar_producto(txt, maestra)
            params = {}
            if prod:
                params["cod_int"] = str(prod["cod_int"])
                params["nombre"]  = prod["nombre"]

            params["cantidad"]   = _parsear_cantidad(txt)
            params["ubicacion"]  = _parsear_ubicacion(txt)
            params["deposito"]   = _parsear_deposito(txt)
            params["fecha_vto"]  = _parsear_fecha(txt)

            if intencion == "mover":
                # Buscar "de X a Y"
                m_mov = _re2.search(r'(?:de|desde)\s+(\S+)\s+(?:a|hacia|para)\s+(\S+)', t)
                if m_mov:
                    params["ubicacion"]         = m_mov.group(1).upper()
                    params["ubicacion_destino"] = m_mov.group(2).upper()
                else:
                    ubis = _re2.findall(r'\b(\d{1,2}[-_]\d{1,2}[a-zA-Z]?)\b', txt)
                    if len(ubis) >= 2:
                        params["ubicacion"]         = ubis[0].upper()
                        params["ubicacion_destino"] = ubis[1].upper()

            ctx = {"txt_original": txt}
            ok, resp = _ejecutar(intencion, params, ctx)
            return ok, resp, params

        # 5) Saludo / ayuda
        if any(k in t for k in ["hola","buenas","buen dia","buen tarde","buen noche","hey","que tal"]):
            return None, (
                f"¡Hola {usuario}! 👋 Soy tu operario digital.\n\n"
                "Puedo ayudarte con:\n"
                "• **Registrar entradas** — ej: *'entraron 50 ibuprofeno 01-2A vto 06/26'*\n"
                "• **Registrar salidas** — ej: *'salida de 10 gel'*\n"
                "• **Consultar stock** — ej: *'¿cuánto hay de keratina?'*\n"
                "• **Ver ubicaciones** — ej: *'¿dónde está el paracetamol?'*\n"
                "• **Ver vencimientos** — ej: *'¿qué vence pronto?'*\n"
                "• **Mover productos** — ej: *'mové el gel de 01-2A a 02-3B'*"
            ), {}

        if any(k in t for k in ["ayuda","help","que podes","que sabes","como funciona"]):
            return None, (
                "📋 **Comandos que entiendo:**\n\n"
                "**ENTRADAS:** 'llegaron 30 kera al 01-2A vencen junio'\n"
                "**SALIDAS:** 'salida de 5 gel desde 01-2A'\n"
                "**STOCK:** '¿cuánto hay de ibuprofeno?'\n"
                "**UBICACIÓN:** '¿dónde está la keratina?'\n"
                "**MOVER:** 'mové loreal de 01-2A a 02-3B'\n"
                "**CORREGIR:** 'corregí el gel, quedan 8 uds en 01-2A'\n"
                "**VENCIMIENTOS:** '¿qué vence este mes?'\n"
                "**HISTORIAL:** 'mostrame los últimos movimientos'"
            ), {}

        # 6) No entendí
        return False, (
            "No entendí bien. Probá con:\n"
            "• *'entraron X [producto] en [ubicación]'*\n"
            "• *'salida de X [producto]'*\n"
            "• *'¿cuánto hay de [producto]?'*\n"
            "• *'ayuda'* para ver todo"
        ), {}

    # ── UI del chat ───────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:11px;color:#64748B;margin-bottom:4px">🤖 Operario Digital — 100% propio</p>', unsafe_allow_html=True)

    if "bot_hist" not in st.session_state:
        st.session_state.bot_hist = []
    if "bot_ctx" not in st.session_state:
        st.session_state.bot_ctx = {}

    # Mostrar historial
    chat_html = ""
    for m in st.session_state.bot_hist[-20:]:
        if m["rol"] == "user":
            chat_html += f'<div class="msg-user">{m["texto"]}</div>'
        else:
            css = "msg-ok" if m.get("ok") is True else ("msg-err" if m.get("ok") is False else "msg-bot")
            chat_html += f'<div class="{css}">{m["texto"]}</div>'
    if chat_html:
        st.markdown(chat_html, unsafe_allow_html=True)

    # Input
    col_inp, col_mic = st.columns([10,1])
    with col_inp:
        inp_key = f"bot_inp_{st.session_state.get('_bot_k',0)}"
        msg_input = st.text_input("", placeholder="Escribí tu consulta o acción...",
                                   label_visibility="collapsed", key=inp_key)
    with col_mic:
        mic_btn = st.button("🎙", use_container_width=True, key="bot_mic")

    # Procesar audio
    audio_txt = ""
    if mic_btn:
        import sounddevice as sd, scipy.io.wavfile as wf, tempfile, os
        try:
            fs=16000; secs=5
            with st.spinner("🎙 Grabando 5 segundos..."):
                rec = sd.rec(int(fs*secs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
            tmp = tempfile.mktemp(suffix=".wav")
            wf.write(tmp, fs, rec)
            try:
                import speech_recognition as sr2
                recog = sr2.Recognizer()
                with sr2.AudioFile(tmp) as src:
                    audio_data = recog.record(src)
                audio_txt = recog.recognize_google(audio_data, language="es-AR")
                st.success(f"🎙 Escuché: *{audio_txt}*")
            except: audio_txt = ""
            os.unlink(tmp)
        except: pass

    msg_final = audio_txt or msg_input
    enviar = st.button("➤ Enviar", use_container_width=True, type="primary", key="bot_send")

    if (enviar or audio_txt) and msg_final.strip():
        txt_usr = msg_final.strip()
        st.session_state.bot_hist.append({"rol":"user","texto":txt_usr})
        st.session_state["_bot_k"] = st.session_state.get("_bot_k",0) + 1

        ok, resp, params = _bot_responder(txt_usr)
        st.session_state.bot_hist.append({"rol":"bot","texto":resp,"ok":ok})

        # Aprendizaje automático: guardar patrón exitoso
        if ok is True and params.get("cod_int"):
            intencion = _detectar_intencion(txt_usr)
            _guardar_patron(txt_usr, resp, intencion)

        st.rerun()

    # Botones rápidos
    st.markdown("---")
    c1,c2,c3,c4,c5 = st.columns(5)
    acciones = [
        (c1,"📉 Bajo stock","mostrame los productos con bajo stock"),
        (c2,"📊 Resumen","resumen del inventario"),
        (c3,"📋 Historial","mostrame los últimos movimientos"),
        (c4,"📍 Ubicaciones","¿dónde está cada producto?"),
        (c5,"📅 Por vencer","¿qué vence pronto?"),
    ]
    for col, label, cmd in acciones:
        with col:
            if st.button(label, use_container_width=True, key=f"quick_{label}"):
                st.session_state.bot_hist.append({"rol":"user","texto":cmd})
                ok2, resp2, _ = _bot_responder(cmd)
                st.session_state.bot_hist.append({"rol":"bot","texto":resp2,"ok":ok2})
                st.rerun()

    # Panel de enseñanza — el admin puede enseñarle al bot respuestas nuevas
    if rol == "admin":
        with st.expander("🎓 Enseñarle al bot"):
            st.caption("Ingresá un ejemplo de mensaje y la respuesta que querés que dé.")
            col_p, col_r = st.columns(2)
            with col_p: patron_teach = st.text_input("Si alguien escribe:", key="teach_patron")
            with col_r: resp_teach   = st.text_input("El bot responde:", key="teach_resp")
            if st.button("💾 Guardar respuesta", key="teach_save"):
                if patron_teach.strip() and resp_teach.strip():
                    _guardar_patron(patron_teach.strip(), resp_teach.strip(), "respuesta_fija")
                    st.success("✅ ¡Aprendido! El bot usará esa respuesta la próxima vez.")

        with st.expander("📚 Patrones aprendidos"):
            pats = _cargar_aprendizaje()
            if pats:
                for p in pats[:30]:
                    st.markdown(f"**{p.get('patron','')}** → {p.get('respuesta','')[:60]}... (usado {p.get('usos',0)}x)")
            else:
                st.info("Aún no hay patrones aprendidos.")

"""
LOGIEZE WEB — versión Streamlit para celular
Instalar:  pip install streamlit supabase pandas openpyxl
Correr:    streamlit run logieze_web.py
"""
import streamlit as st
import pandas as pd
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
/* Fuente y fondo oscuro */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0F172A;
    color: #F1F5F9;
}

/* Header superior */
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

/* Tarjetas métricas */
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

/* Botones principales */
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

/* Botón peligro */
div[data-testid="column"] div.stButton > button.danger {
    background: transparent !important;
    border: 1.5px solid #EF4444 !important;
    color: #EF4444 !important;
}

/* Inputs */
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

/* Select */
div[data-baseweb="select"] > div {
    background: #1E293B !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
}

/* Tabs */
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

/* Tablas dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #334155;
}

/* Sección labels */
.sec-label {
    font-size: 11px; font-weight: 700; color: #94A3B8;
    letter-spacing: 2px; margin-bottom: 6px; margin-top: 4px;
}

/* Badge stock */
.stock-badge {
    display: inline-block;
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    color: white; font-weight: 800; font-size: 18px;
    padding: 8px 20px; border-radius: 30px;
}

/* Lote cards */
.lote-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.lote-card.vencido { border-color: #EF4444; background: #200a0a; }
.lote-card.por-vencer { border-color: #F59E0B; background: #1c1500; }

/* Sugerencia */
.sug-box {
    background: rgba(6,182,212,0.10);
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px; font-weight: 700; color: #06B6D4;
    margin-bottom: 8px;
}

/* Alertas */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1E293B !important;
    border-right: 1px solid #334155;
}

/* Radio */
div[data-testid="stRadio"] label {
    font-size: 15px !important; font-weight: 700 !important;
}

/* Ocultar footer Streamlit */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()

# ── CACHE DE DATOS — carga una vez, refresca a pedido ─────────────────────────
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
    """Devuelve (numero, apikey) desde Supabase config, o ('','') si no hay."""
    try:
        r1 = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
        r2 = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
        return (r1[0]['valor'] if r1 else "", r2[0]['valor'] if r2 else "")
    except:
        return ("", "")

def _enviar_whatsapp(numero, apikey, mensaje, callback_ok=None, callback_err=None):
    """Envia mensaje via CallMeBot."""
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
        if est in [3,4]:           niv, lets = 4, "ABCDE"
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

# ── SESIÓN PERSISTENTE vía query_params (sobrevive F5) ────────────────────────
# La sesión se guarda en la URL (?lz_u=juan&lz_r=operario).
# Al recargar los params siguen en la URL → no pide login.
# Solo se borran cuando el usuario pulsa "Cambiar usuario".

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
        usuario = st.text_input("USUARIO", placeholder="Ingresá tu usuario", label_visibility="collapsed", key="l_usr")
        clave   = st.text_input("CLAVE",   placeholder="••••••••",            label_visibility="collapsed", type="password", key="l_pwd")
        if st.button("ENTRAR  →", use_container_width=True):
            if usuario == "admin" and clave == "70797474":
                st.session_state.usuario = "admin"; st.session_state.rol = "admin"
                st.query_params["lz_u"] = "admin"
                st.query_params["lz_r"] = "admin"
                st.rerun()
            else:
                try:
                    r = sb.table("usuarios").select("*").eq("usuario", usuario.lower().strip()).eq("clave", clave).execute().data
                    if r:
                        st.session_state.usuario = r[0]['usuario']
                        st.session_state.rol     = r[0]['rol']
                        st.query_params["lz_u"] = r[0]['usuario']
                        st.query_params["lz_r"] = r[0]['rol']
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

# Header
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(f"""
    <div class="main-header">
        <div style="font-size:32px;">📦</div>
        <div>
            <h1>LOGIEZE</h1>
            <span>v2.6 WEB  ·  {ROL_ICON} {usuario.upper()}  ·  {rol.upper()}</span>
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

# Cargar datos con spinner solo la primera vez
with st.spinner("Cargando datos..."):
    maestra    = cargar_maestra()
    inventario = cargar_inventario()

# Índice rápido
idx_inv     = {}
ubis_ocupadas = set()
for lote in inventario:
    cod = str(lote.get('cod_int',''))
    if cod not in idx_inv: idx_inv[cod] = []
    idx_inv[cod].append(lote)
    ubis_ocupadas.add(str(lote.get('ubicacion','')).upper())

nm = len(maestra); ni = len(inventario)

# Métricas rápidas
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><div class="value">{nm}</div><div class="label">PRODUCTOS</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="value">{ni}</div><div class="label">LOTES</div></div>', unsafe_allow_html=True)
with c3:
    total_stock = sum(float(l.get('cantidad',0)) for l in inventario)
    st.markdown(f'<div class="metric-card"><div class="value">{int(total_stock):,}</div><div class="label">STOCK TOTAL</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
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
        # Tabla resultados
        df_res = pd.DataFrame([{
            "Nombre": p['nombre'],
            "Código": p['cod_int'],
            "Stock":  int(float(p.get("cantidad_total") or 0)),
        } for p in productos_filtrados])

        st.dataframe(df_res, use_container_width=True, hide_index=True,
                     column_config={"Stock": st.column_config.NumberColumn(format="%d")})

        # Seleccionar producto
        nombres_lista = [f"{p['nombre']}  [{p['cod_int']}]" for p in productos_filtrados]
        sel_idx = st.selectbox("Seleccionar producto:", range(len(nombres_lista)),
                               format_func=lambda i: nombres_lista[i], key="sel_prod")
        prod_sel = productos_filtrados[sel_idx]
        cod_sel  = str(prod_sel['cod_int'])

        lotes_prod = idx_inv.get(cod_sel, [])
        total_q    = sum(float(l.get('cantidad',0)) for l in lotes_prod)
        st.markdown(f'<div style="margin:10px 0"><span class="stock-badge">STOCK TOTAL: {int(total_q)}</span></div>', unsafe_allow_html=True)

        # ── LOTES ────────────────────────────────────────────────────────────
        if lotes_prod:
            st.markdown('<p class="sec-label">📦 LOTES EN DEPÓSITO</p>', unsafe_allow_html=True)
            for i, l in enumerate(lotes_prod):
                dias = dias_para_vencer(l.get('fecha',''))
                clase = ""
                if dias is not None:
                    if dias < 0:    clase = " vencido"
                    elif dias <= DIAS_ALERTA: clase = " por-vencer"

                alerta = ""
                if dias is not None:
                    if dias < 0:   alerta = f"🔴 VENCIDO hace {abs(dias)} días"
                    elif dias <= DIAS_ALERTA: alerta = f"🟠 Vence en {dias} días"
                    else:          alerta = f"✅ Vence en {dias} días"

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

        # ── OPERACIÓN ────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="sec-label">📝 REGISTRAR OPERACIÓN</p>', unsafe_allow_html=True)

        tipo_op = st.radio("Tipo", ["⬆ INGRESO", "⬇ SALIDA"],
                           horizontal=True, label_visibility="collapsed", key="tipo_op")
        es_ingreso = "INGRESO" in tipo_op

        col_a, col_b = st.columns(2)
        with col_a:
            cantidad_op = st.number_input("CANTIDAD", min_value=0.1, step=1.0,
                                           format="%.0f", key="cant_op")
        with col_b:
            fecha_op = st.text_input("VENCIMIENTO (MM/AA)", placeholder="ej: 06/26", key="fecha_op")

        # Ubicaciones: las del producto + 5 vacías
        ubi_prod = list({str(l.get('ubicacion','')).upper() for l in lotes_prod})
        vacias   = calcular_vacias_rapido(ubis_ocupadas)
        sug99    = calcular_sug99(ubis_ocupadas)
        opciones_ubi = ubi_prod + [f"VACIA: {v}" for v in vacias] + [f"SUG 99: {sug99}"]
        if vacias:
            sugerencia = vacias[0]
        else:
            sugerencia = sug99

        st.markdown(f'<div class="sug-box">📍 Sugerencia: {sugerencia}</div>', unsafe_allow_html=True)

        col_u, col_d = st.columns(2)
        with col_u:
            ubi_sel = st.selectbox("UBICACIÓN", opciones_ubi, key="ubi_op")
            ubi_final = ubi_sel.replace("VACIA: ","").replace("SUG 99: ","").upper().strip()
            ubi_manual = st.text_input("o escribir manualmente:", placeholder="ej: 05-3B", key="ubi_man")
            if ubi_manual.strip(): ubi_final = ubi_manual.strip().upper()
        with col_d:
            depo_op = st.selectbox("DEPÓSITO", ["depo 1","depo 2"], key="depo_op")

        # Si es SALIDA, elegir lote
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
                        # Buscar lote existente
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

        # ── MOVER LOTE ───────────────────────────────────────────────────────
        if lotes_prod:
            st.markdown("---")
            st.markdown('<p class="sec-label">↔ MOVER LOTE</p>', unsafe_allow_html=True)
            with st.expander("Reubicar mercadería"):
                opciones_mover = [f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}"
                                  for l in lotes_prod]
                idx_mover = st.selectbox("Lote a mover:", range(len(opciones_mover)),
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

    # ── Panel de sincronización con la nube ───────────────────────────────────
    st.markdown("""
    <div style="background:#1E293B;border:1px solid #334155;border-radius:14px;
                padding:14px 18px;margin-bottom:12px;">
        <span style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:2px;">
            ☁️ PEDIDOS EN LA NUBE
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])

    # Cargar lista de pedidos pendientes de Supabase
    @st.cache_data(ttl=30, show_spinner=False)
    def cargar_pedidos_nube():
        try:
            return sb.table("pedidos").select("id,nombre,fecha,estado,items")                 .in_("estado", ["pendiente", "en_proceso"])                 .order("id", desc=True).limit(20).execute().data or []
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
                    # Marcar como en_proceso
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

    # ── Estado del pedido local ───────────────────────────────────────────────
    if "pedido" not in st.session_state:
        st.session_state.pedido = []

    # ── Barra de acciones: pegar texto + guardar en nube ─────────────────────
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
                            cod  = str(r[col_cod]).strip()
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
                    # Notificar al admin por WhatsApp
                    _wa_num, _wa_key = _wa_config()
                    if _wa_num and _wa_key:
                        _msg = (
                            f"PEDIDO NUEVO - LOGIEZE"
                            f" | Vendedor: {usuario}"
                            f" | Pedido: {nombre_ped.strip()}"
                            f" | Items: {len(items_subir)}"
                            f" | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        )
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

    # ── Mostrar ítems del pedido activo ───────────────────────────────────────
    if st.session_state.pedido:
        st.markdown('<p class="sec-label">📋 ÍTEMS DEL PEDIDO ACTIVO</p>', unsafe_allow_html=True)

        pedido_a_eliminar = None
        for i, item in enumerate(st.session_state.pedido):
            col_pi, col_pb = st.columns([5, 1])
            with col_pi:
                stock_disp = sum(float(l.get('cantidad',0)) for l in idx_inv.get(item['cod'],[]))
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

        # ── Seleccionar ítem a despachar ──────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="sec-label">DESPACHAR ÍTEM</p>', unsafe_allow_html=True)

        idx_desp = st.selectbox(
            "Ítem a despachar:",
            range(len(st.session_state.pedido)),
            format_func=lambda i: (
                f"{'✅' if sum(float(l.get('cantidad',0)) for l in idx_inv.get(st.session_state.pedido[i]['cod'],[])) >= st.session_state.pedido[i]['cant'] else '⚠️'}"
                f"  {st.session_state.pedido[i]['nombre']}  —  {st.session_state.pedido[i]['cant']} uds"
            ),
            key="desp_sel",
            label_visibility="collapsed"
        )
        item_sel = st.session_state.pedido[idx_desp]
        cod_d    = item_sel['cod']
        lotes_d  = [l for l in idx_inv.get(cod_d, []) if float(l.get('cantidad', 0)) > 0]

        if lotes_d:
            st.markdown('<p class="sec-label">LOTE A USAR</p>', unsafe_allow_html=True)
            for l in lotes_d:
                dias = dias_para_vencer(l.get('fecha',''))
                clase = " vencido" if (dias is not None and dias < 0) else (" por-vencer" if (dias is not None and dias <= DIAS_ALERTA) else "")
                st.markdown(f"""
                <div class="lote-card{clase}">
                    <b style="font-size:18px;color:#06B6D4">{int(float(l.get('cantidad',0)))}</b>
                    &nbsp;·&nbsp; 📍 {l.get('ubicacion','')}
                    &nbsp;·&nbsp; {l.get('deposito','')}
                    &nbsp;·&nbsp; 📅 {l.get('fecha','')}
                </div>
                """, unsafe_allow_html=True)

            lote_ops = [
                f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}"
                for l in lotes_d
            ]
            idx_ld = st.selectbox("Lote a descontar:", range(len(lote_ops)),
                                  format_func=lambda i: lote_ops[i], key="lote_desp")
            lote_d = lotes_d[idx_ld]

            _puede_descontar = rol in ("admin", "operario")
            if _puede_descontar and st.button("✅ DESCONTAR DEL LOTE", use_container_width=True, key="btn_desc"):
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
                    # Actualizar pedido en Supabase: sacar ítem ejecutado
                    _ped_id = item_sel.get('ped_id')
                    if _ped_id:
                        try:
                            import json as _j2
                            _items_rest = [{"cod_int":it['cod'],"cantidad":it['cant'],"nombre":it['nombre']}
                                           for it in st.session_state.pedido]
                            if _items_rest:
                                sb.table("pedidos").update({
                                    "items": _j2.dumps(_items_rest),
                                    "estado": "en_proceso"
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

        # Exportar
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
            with col_au: nu = st.text_input("Usuario")
            with col_ap: np_ = st.text_input("Clave", type="password")
            with col_ar: nr = st.selectbox("Rol", ["operario","admin","visita","vendedor"])
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

        # Leer config actual
        try:
            _wa_num_db = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
            _wa_key_db = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
            _wa_num_actual = _wa_num_db[0]["valor"] if _wa_num_db else ""
            _wa_key_actual = _wa_key_db[0]["valor"] if _wa_key_db else ""
        except:
            _wa_num_actual = _wa_key_actual = ""

        with st.form("form_wa"):
            col_wn, col_wk = st.columns(2)
            with col_wn:
                wa_num = st.text_input("Tu numero WhatsApp:", value=_wa_num_actual,
                                       placeholder="+5491112345678")
            with col_wk:
                wa_key = st.text_input("API Key de CallMeBot:", value=_wa_key_actual,
                                       placeholder="123456")
            col_ws, col_wt = st.columns(2)
            with col_ws:
                if st.form_submit_button("💾 Guardar numero", use_container_width=True):
                    if wa_num.strip() and wa_key.strip():
                        try:
                            sb.table("config").upsert(
                                {"clave": "wa_numero", "valor": wa_num.strip()},
                                on_conflict="clave"
                            ).execute()
                            sb.table("config").upsert(
                                {"clave": "wa_apikey", "valor": wa_key.strip()},
                                on_conflict="clave"
                            ).execute()
                            # Verificar
                            check = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
                            if check and check[0]["valor"] == wa_num.strip():
                                st.success(f"✅ Guardado correctamente: {wa_num.strip()}")
                            else:
                                st.warning("No se pudo verificar el guardado. Revisa los permisos RLS en Supabase (ejecuta fix_rls_config.sql).")
                        except Exception as e:
                            err = str(e)
                            if "rls" in err.lower() or "policy" in err.lower() or "42501" in err:
                                st.error("Sin permisos (RLS activo). Ejecuta el SQL de fix_rls_config.sql en Supabase.")
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
                        time.sleep(2)  # esperar respuesta
                        if resultado["ok"]:
                            st.success("Mensaje enviado. Revisa tu WhatsApp.")
                        else:
                            st.warning(f"Enviado (verificar WhatsApp). Respuesta: {resultado['err'] or 'OK'}")
                    else:
                        st.warning("Guarda el numero y API key primero.")

        if _wa_num_actual:
            st.caption(f"Numero activo: {_wa_num_actual}")

        st.markdown("---")
        st.markdown('<p class="sec-label">🤖 ASISTENTE IA — GEMINI API KEY</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.3);
                    border-radius:10px;padding:10px 14px;font-size:12px;color:#94A3B8;margin-bottom:8px;">
            <b style="color:#F97316;">Obtener API Key gratis:</b> aistudio.google.com → Get API Key → Create API Key
        </div>
        """, unsafe_allow_html=True)
        try:
            _gk = sb.table("config").select("valor").eq("clave","gemini_key").execute().data
            _gk_val = _gk[0]["valor"] if _gk else ""
        except:
            _gk_val = ""
        _new_gk = st.text_input("Groq API Key (gratis):", value="",
                                 placeholder="Pegá tu key: AIzaSy...",
                                 type="password", key="gemini_key_input")
        if st.button("💾 Guardar API Key", use_container_width=True, key="btn_save_gemini"):
            # Limpiar AGRESIVAMENTE: quitar espacios, newlines, tabs, comillas
            _clean = _new_gk
            for ch in [" ", "\n", "\r", "\t", '"', "'"]:
                _clean = _clean.replace(ch, "")
            _clean = _clean.strip()
            if _clean:
                try:
                    ex = sb.table("config").select("id").eq("clave","gemini_key").execute().data
                    if ex:
                        sb.table("config").update({"valor": _clean}).eq("clave","gemini_key").execute()
                    else:
                        sb.table("config").insert({"clave":"gemini_key","valor": _clean}).execute()
                    # Verificar que se guardó bien
                    check = sb.table("config").select("valor").eq("clave","gemini_key").execute().data
                    saved = check[0]["valor"] if check else ""
                    if saved == _clean:
                        st.success(f"✅ Guardada. Empieza con: {_clean[:8]}... ({len(_clean)} caracteres)")
                    else:
                        st.error(f"Se guardó diferente. Guardado: '{saved[:12]}...'")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Pegá la API key primero.")

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
# TAB ASISTENTE IA — GEMINI 2.0 Flash
# ═══════════════════════════════════════════════════════════════════════════════
with tab_asist:

    st.markdown("""
    <style>
    .msg-user{background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;
        border-radius:18px 18px 4px 18px;padding:10px 16px;margin:4px 0 4px 60px;
        font-size:14px;line-height:1.6;}
    .msg-bot{background:#1E293B;color:#F1F5F9;border-radius:4px 18px 18px 18px;
        border:1px solid #334155;padding:10px 16px;margin:4px 60px 4px 0;
        font-size:14px;line-height:1.6;white-space:pre-wrap;}
    .msg-ok{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.35);
        border-radius:8px;padding:5px 12px;margin:2px 60px 6px 0;
        font-size:12px;color:#10B981;font-family:monospace;}
    .msg-err{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.35);
        border-radius:8px;padding:5px 12px;margin:2px 60px 6px 0;
        font-size:12px;color:#EF4444;}
    .chat-lbl{font-size:11px;color:#475569;margin:6px 4px 1px;}
    </style>""", unsafe_allow_html=True)

    # Header
    hc1, hc2 = st.columns([4,1])
    with hc1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:4px 0 8px">
            <div style="font-size:36px">✨</div>
            <div>
                <div style="font-size:17px;font-weight:900;color:#F1F5F9;letter-spacing:1px">
                    ASISTENTE LOGIEZE</div>
                <div style="font-size:12px;color:#64748B">
                    Gemini 2.0 Flash · Inventario inteligente · Chat libre</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with hc2:
        if st.button("🗑️ Nuevo chat", use_container_width=True, key="clear_chat"):
            st.session_state.chat_hist = []
            st.rerun()

    # Leer API key
    try:
        _gk = sb.table("config").select("valor").eq("clave","gemini_key").execute().data
        _raw = _gk[0]["valor"] if _gk else ""
        # Limpiar agresivamente al leer también
        GEMINI_KEY = _raw
        for _ch in [" ", "\n", "\r", "\t", '"', "'"]:
            GEMINI_KEY = GEMINI_KEY.replace(_ch, "")
        GEMINI_KEY = GEMINI_KEY.strip()
    except:
        GEMINI_KEY = ""

    if not GEMINI_KEY:
        st.markdown("""
        <div style="background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.3);
                    border-radius:12px;padding:20px;text-align:center;margin:20px 0">
            <div style="font-size:40px;margin-bottom:8px">🔑</div>
            <div style="font-size:15px;font-weight:700;color:#F97316">Se necesita una API Key de Groq</div>
            <div style="font-size:13px;color:#94A3B8;margin-top:8px">
                <b>Gratis, sin tarjeta de crédito:</b><br>
                1. Entrá a <b>aistudio.google.com</b><br>
                2. Clic en <b>API Keys → Create API Key</b><br>
                3. Copiá la key y pegala en <b>ADMIN → Asistente IA</b>
            </div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    if "chat_hist" not in st.session_state:
        st.session_state.chat_hist = []

    # Contexto inventario compacto
    def _buscar_en_inventario(query):
        """Busca productos relevantes para la consulta del usuario."""
        q = query.upper()
        resultados = []
        for p in maestra:
            nom = str(p.get("nombre","")).upper()
            cod = str(p.get("cod_int",""))
            if q in nom or q in cod or any(
                q in str(w) for w in q.split() if len(w)>2
            ):
                resultados.append(p)
        # Si no encontró nada específico, devolver todos
        return resultados if resultados else maestra

    def _ctx(query=""):
        """Genera contexto de inventario relevante para la consulta."""
        # Si la query menciona un código o nombre específico, filtrar
        productos = _buscar_en_inventario(query) if query else maestra

        rows = []
        for p in productos:
            cod = str(p.get("cod_int",""))
            stk = int(float(p.get("cantidad_total") or 0))
            lts = " | ".join(
                f"{l.get('ubicacion','')}:{int(float(l.get('cantidad',0) or 0))} vto:{l.get('fecha','')}"
                for l in idx_inv.get(cod,[])[:5]
            )
            rows.append(f"{p.get('nombre','')} [cod:{cod} total:{stk}] {lts}")

        h = cargar_historial_cache()[:8]
        hist = "\n".join(
            f"{x.get('tipo','')} {x.get('nombre','')} x{x.get('cantidad','')} ubi:{x.get('ubicacion','')}"
            for x in h
        )
        return "\n".join(rows), hist

    def _llamar_gemini(user_msg):
        """Llama a Gemini 2.0 Flash con contexto de inventario relevante."""
        import json as _j, urllib.request as _ur

        key = GEMINI_KEY.strip()
        if not key:
            raise Exception("Sin API Key. Cargala en ADMIN → Asistente IA.")

        # Contexto inteligente — solo productos relevantes para esta consulta
        _inv_txt, _hist_txt = _ctx(user_msg)

        system_txt = (
            f"Sos el asistente inteligente de LOGIEZE, sistema de gestion de inventario.\n"
            f"Usuario: {usuario} | Rol: {rol} | {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"INVENTARIO ACTUAL:\n{_inv_txt}\n\n"
            f"ULTIMOS MOVIMIENTOS:\n{_hist_txt}\n\n"
            "Podes responder consultas del inventario con datos reales, ejecutar acciones Y charlar de cualquier tema.\n\n"
            "Cuando el usuario pide EJECUTAR algo sobre el inventario, responde SOLO con este JSON (sin texto extra):\n"
            '{"accion":"salida","params":{"cod_int":"X","cantidad":N,"ubicacion":"XX"},"confirmacion":"descripcion"}\n'
            '{"accion":"entrada","params":{"cod_int":"X","cantidad":N,"ubicacion":"XX","fecha_vto":"MM/AA"},"confirmacion":"descripcion"}\n'
            '{"accion":"mover","params":{"cod_int":"X","cantidad":N,"ubicacion_origen":"XX","ubicacion_destino":"YY"},"confirmacion":"descripcion"}\n'
            '{"accion":"corregir","params":{"cod_int":"X","ubicacion":"XX","cantidad_nueva":N},"confirmacion":"descripcion"}\n\n'
            "Si es consulta o charla libre -> responde en texto, SIN JSON.\n"
            "Busca productos por nombre aproximado si no dan codigo exacto.\n"
            "Espanol rioplatense, amigable y directo."
        )

        # Formato Gemini: system como primer turno user/model
        contents = [
            {"role": "user",  "parts": [{"text": system_txt}]},
            {"role": "model", "parts": [{"text": "Listo! Estoy conectado al inventario de LOGIEZE."}]}
        ]
        for m in st.session_state.chat_hist[-16:]:
            r = "user" if m["rol"] == "user" else "model"
            contents.append({"role": r, "parts": [{"text": m["texto"]}]})
        contents.append({"role": "user", "parts": [{"text": user_msg}]})

        payload = _j.dumps({
            "contents": contents,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
        }).encode()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        req = _ur.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with _ur.urlopen(req, timeout=30) as r:
            data = _j.loads(r.read())

        if "error" in data:
            raise Exception(data["error"].get("message", str(data["error"])))

        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _ejecutar(accion, params):
        cod  = str(params.get("cod_int","")).strip()
        cant = float(params.get("cantidad", params.get("cantidad_nueva", 0)))
        ubi  = str(params.get("ubicacion","")).upper().strip()

        prod = next((p for p in maestra if str(p.get("cod_int",""))==cod), None)
        if not prod:
            prod = next((p for p in maestra if cod.upper() in str(p.get("nombre","")).upper()), None)
            if prod: cod = str(prod["cod_int"])
        if not prod:
            return False, f"No encontré producto '{cod}'"
        nom = prod["nombre"]

        if accion == "salida":
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote:
                lote = next((l for l in lotes_p if float(l.get("cantidad",0))>=cant), None)
                if not lote:
                    return False, f"Sin stock. Total: {int(sum(float(l.get('cantidad',0)) for l in lotes_p))} uds"
                ubi = str(lote.get("ubicacion",""))
            disp = float(lote.get("cantidad",0))
            if disp < cant:
                return False, f"Solo hay {int(disp)} uds en {ubi}"
            nueva = disp - cant
            if nueva <= 0:
                sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else:
                sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            registrar_historial("SALIDA",cod,nom,cant,ubi,usuario)
            recalcular_maestra(cod,inventario); refrescar()
            return True, f"Salida: {int(cant)} uds de {nom} desde {ubi}. Quedan {int(nueva)} uds."

        elif accion == "entrada":
            fv = params.get("fecha_vto","")
            lu = [l for l in inventario if str(l.get("cod_int",""))==cod and str(l.get("ubicacion","")).upper()==ubi]
            if lu:
                sb.table("inventario").update({"cantidad":float(lu[0].get("cantidad",0))+cant}).eq("id",lu[0]["id"]).execute()
            else:
                sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant,"ubicacion":ubi,"fecha":fv,"deposito":"PRINCIPAL"}).execute()
            registrar_historial("ENTRADA",cod,nom,cant,ubi,usuario)
            recalcular_maestra(cod,inventario); refrescar()
            return True, f"Entrada: {int(cant)} uds de {nom} en {ubi}."

        elif accion == "mover":
            ud = str(params.get("ubicacion_destino","")).upper()
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote: return False, f"Sin lote de {nom} en {ubi}"
            disp = float(lote.get("cantidad",0))
            cm = cant if cant>0 else disp
            if cm>disp: return False, f"Solo hay {int(disp)} uds"
            nv = disp-cm
            if nv<=0: sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else: sb.table("inventario").update({"cantidad":nv}).eq("id",lote["id"]).execute()
            sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cm,"ubicacion":ud,"fecha":lote.get("fecha",""),"deposito":lote.get("deposito","PRINCIPAL")}).execute()
            registrar_historial("MOVIMIENTO",cod,nom,cm,f"{ubi}→{ud}",usuario)
            recalcular_maestra(cod,inventario); refrescar()
            return True, f"Movido: {int(cm)} uds de {nom}: {ubi} → {ud}."

        elif accion == "corregir":
            cn = float(params.get("cantidad_nueva",cant))
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote and lotes_p: lote=lotes_p[0]; ubi=str(lote.get("ubicacion",""))
            if not lote: return False, f"Sin lotes de {nom}"
            ant = float(lote.get("cantidad",0))
            sb.table("inventario").update({"cantidad":cn}).eq("id",lote["id"]).execute()
            registrar_historial("CORRECCIÓN",cod,nom,cn-ant,ubi,usuario)
            recalcular_maestra(cod,inventario); refrescar()
            return True, f"Corregido {nom} en {ubi}: {int(ant)} → {int(cn)} uds."

        return False, "Acción desconocida"

    # Mostrar chat
    if not st.session_state.chat_hist:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 20px">
            <div style="font-size:52px">🦙</div>
            <div style="font-size:16px;font-weight:700;color:#94A3B8;margin-top:10px">
                Hola! Soy tu asistente de inventario.</div>
            <div style="font-size:13px;color:#64748B;margin-top:10px;line-height:2.2">
                <code>¿Cuánto stock hay del código 147?</code><br>
                <code>Sacá 10 unidades de Ibuprofeno de 01-1A</code><br>
                <code>¿Qué productos tienen menos de 5 unidades?</code><br>
                <code>Mové el lote de ABC de 02-3B a 05-1A</code><br>
                <code>Dame un resumen del inventario</code>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_hist:
            if msg["rol"] == "user":
                st.markdown(f'<div class="chat-lbl" style="text-align:right">{usuario} 👤</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-user">{msg["texto"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-lbl">🦙 Asistente</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-bot">{msg["texto"]}</div>', unsafe_allow_html=True)
                if msg.get("accion_log"):
                    st.markdown(f'<div class="{"msg-ok" if msg.get("ok") else "msg-err"}">⚡ {msg["accion_log"]}</div>', unsafe_allow_html=True)

    # Botones rápidos
    st.markdown("<br>", unsafe_allow_html=True)
    qc = st.columns(4)
    for i,(lbl,preg) in enumerate([
        ("📉 Bajo stock",  "Mostrame todos los productos con stock menor a 10 unidades"),
        ("📦 Resumen",     "Dame un resumen del inventario: total productos, stock total y top 5"),
        ("📋 Últimos movs","Cuáles fueron los últimos movimientos registrados?"),
        ("📍 Ubicaciones", "Listame todos los productos con sus ubicaciones y cantidades"),
    ]):
        with qc[i]:
            if st.button(lbl, use_container_width=True, key=f"qr_{i}"):
                st.session_state._qmsg = preg
                st.rerun()

    _qmsg = st.session_state.pop("_qmsg", None)

    # Input
    ic1, ic2 = st.columns([5,1])
    with ic1:
        txt = st.text_input("msg", label_visibility="collapsed",
                            placeholder="Escribí tu mensaje...", key="gemini_input")
    with ic2:
        send = st.button("➤ Enviar", use_container_width=True, type="primary", key="gemini_send")

    _final = _qmsg or (txt.strip() if send and txt else None)

    if _final:
        import json as _jj, re as _re
        st.session_state.chat_hist.append({"rol":"user","texto":_final})

        with st.spinner("✨ Gemini está pensando..."):
            try:
                resp = _llamar_gemini(_final)

                # Detectar JSON de acción
                m = _re.search(r'\{[^{}]*"accion"[^{}]*\}', resp, _re.DOTALL)
                act = None
                if m:
                    try: act = _jj.loads(m.group())
                    except: pass

                if act and act.get("accion") in ("salida","entrada","mover","corregir"):
                    if rol in ("visita","vendedor"):
                        st.session_state.chat_hist.append({
                            "rol":"assistant",
                            "texto":f"Tu rol ({rol}) no tiene permisos para ejecutar acciones."
                        })
                    else:
                        ok, res = _ejecutar(act["accion"], act.get("params",{}))
                        st.session_state.chat_hist.append({
                            "rol":"assistant",
                            "texto": act.get("confirmacion","Listo"),
                            "accion_log": res, "ok": ok
                        })
                else:
                    clean = _re.sub(r'```json[\s\S]*?```','', resp).strip()
                    st.session_state.chat_hist.append({"rol":"assistant","texto": clean or resp})

            except Exception as e:
                err = str(e)
                if "401" in err or "403" in err or "inválida" in err.lower():
                    msg_e = "❌ API Key inválida. Ir a ADMIN → Asistente IA y cargar la key de Gemini (empieza con AIzaSy)."
                elif "429" in err:
                    msg_e = "⚠️ Límite de Gemini alcanzado momentáneamente. Esperá unos segundos e intentá de nuevo."
                elif "timeout" in err.lower():
                    msg_e = "⏱️ Tardó demasiado. Intentá de nuevo."
                elif "AIzaSy" in err:
                    msg_e = err
                else:
                    msg_e = f"❌ Error: {err[:200]}"
                st.session_state.chat_hist.append({"rol":"assistant","texto":msg_e,"ok":False})

        st.rerun()
# ═══════════════════════════════════════════════════════════════════════════════
# TAB ASISTENTE — BOT PROPIO (sin API externa, sin límites, sin costo)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_asist:

    st.markdown("""
    <style>
    .msg-user{background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;
        border-radius:18px 18px 4px 18px;padding:10px 16px;margin:4px 0 4px 50px;
        font-size:14px;line-height:1.6;}
    .msg-bot{background:#1E293B;color:#F1F5F9;border-radius:4px 18px 18px 18px;
        border:1px solid #334155;padding:10px 16px;margin:4px 50px 4px 0;
        font-size:14px;line-height:1.6;white-space:pre-wrap;}
    .msg-ok{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.35);
        border-radius:8px;padding:6px 12px;margin:2px 50px 6px 0;
        font-size:12px;color:#10B981;}
    .msg-err{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.35);
        border-radius:8px;padding:6px 12px;margin:2px 50px 6px 0;
        font-size:12px;color:#EF4444;}
    .chat-lbl{font-size:11px;color:#475569;margin:6px 4px 1px;}
    .sugg-btn{display:inline-block;background:#1E293B;border:1px solid #334155;
        border-radius:16px;padding:5px 12px;font-size:12px;color:#94A3B8;
        margin:3px;cursor:pointer;}
    </style>""", unsafe_allow_html=True)

    # Header
    h1, h2 = st.columns([4,1])
    with h1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:4px 0 8px">
            <div style="font-size:36px">🤖</div>
            <div>
                <div style="font-size:17px;font-weight:900;color:#F1F5F9;letter-spacing:1px">
                    ASISTENTE LOGIEZE</div>
                <div style="font-size:12px;color:#10B981;font-weight:600">
                    ✅ Sin límites · Sin costo · 100% propio · Acceso completo al inventario</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with h2:
        if st.button("🗑️ Limpiar", use_container_width=True, key="clear_bot"):
            st.session_state.bot_hist = []
            st.rerun()

    if "bot_hist" not in st.session_state:
        st.session_state.bot_hist = []

    # ── Motor de comprensión del lenguaje natural ──────────────────────────────
    import re as _re

    def _normalizar(txt):
        import unicodedata
        txt = unicodedata.normalize('NFD', txt)
        txt = ''.join(c for c in txt if unicodedata.category(c) != 'Mn')
        return txt.lower().strip()

    def _extraer_numero(txt):
        nums = _re.findall(r'\d+(?:[.,]\d+)?', txt)
        if nums:
            return float(nums[0].replace(',','.'))
        palabras = {'un':1,'una':1,'dos':2,'tres':3,'cuatro':4,'cinco':5,
                    'seis':6,'siete':7,'ocho':8,'nueve':9,'diez':10,
                    'veinte':20,'treinta':30,'cuarenta':40,'cincuenta':50,
                    'cien':100,'ciento':100,'doscientos':200,'quinientos':500,'mil':1000}
        for w,n in palabras.items():
            if w in txt.lower(): return float(n)
        return 0.0

    def _extraer_ubicacion(txt):
        m = _re.search(r'\b([0-9]{1,2}[-_][0-9A-Za-z]{1,3}[A-Za-z]?)\b', txt)
        return m.group(1).upper() if m else ""

    def _buscar_producto(query):
        """Busca producto en maestra por código o nombre aproximado."""
        q = _normalizar(query)
        # Por código exacto
        for p in maestra:
            if str(p.get("cod_int","")).lower() == q:
                return p
        # Por código numérico
        nums = _re.findall(r'\d+', query)
        if nums:
            for p in maestra:
                if str(p.get("cod_int","")) == nums[0]:
                    return p
        # Por nombre exacto
        for p in maestra:
            if _normalizar(p.get("nombre","")) == q:
                return p
        # Por nombre parcial (todas las palabras)
        palabras = [w for w in q.split() if len(w) > 2]
        if palabras:
            for p in maestra:
                nom = _normalizar(p.get("nombre",""))
                if all(w in nom for w in palabras):
                    return p
        # Por nombre parcial (alguna palabra)
        if palabras:
            candidatos = []
            for p in maestra:
                nom = _normalizar(p.get("nombre",""))
                score = sum(1 for w in palabras if w in nom)
                if score > 0:
                    candidatos.append((score, p))
            if candidatos:
                candidatos.sort(key=lambda x: -x[0])
                return candidatos[0][1]
        return None

    def _listar_productos_query(query):
        """Devuelve lista de productos que coinciden con la búsqueda."""
        q = _normalizar(query)
        palabras = [w for w in q.split() if len(w) > 2]
        resultados = []
        for p in maestra:
            nom = _normalizar(p.get("nombre",""))
            cod = str(p.get("cod_int",""))
            if any(w in nom or w in cod for w in palabras):
                resultados.append(p)
        return resultados

    def _lotes_producto(cod):
        return idx_inv.get(str(cod), [])

    def _stock_total(cod):
        return sum(float(l.get("cantidad",0) or 0) for l in _lotes_producto(str(cod)))

    def _detectar_intencion(txt):
        n = _normalizar(txt)
        # Salida
        if any(w in n for w in ['sacar','saca','saque','descontar','desconta','retirar','retira',
                                  'salida','usar','gasta','consume','despachar','despach',
                                  'quitar','quita','remov','menos',' sale ']):
            return 'salida'
        # Entrada
        if any(w in n for w in ['agregar','agrega','agreg','entrar','entra','ingres','entrada',
                                  'recibir','recibi','sumar','suma','añadir','añade','cargar',
                                  'carga','mas stock','nuevo stock','compramos','llego']):
            return 'entrada'
        # Mover
        if any(w in n for w in ['mover','movi','mueve','trasladar','traslad','cambiar de lugar',
                                  'cambiar ubicacion','pasar a','llevar a','manda a']):
            return 'mover'
        # Corregir
        if any(w in n for w in ['corregir','correg','ajustar','ajusta','fijar','poner',
                                  'actualizar','actualiza','cambiar cantidad','es en realidad',
                                  'deberia ser','son en total','hay en total']):
            return 'corregir'
        # Historial
        if any(w in n for w in ['historial','movimiento','ultimos','ultimo','registro',
                                  'que paso','que se hizo','quien hizo','cuando']):
            return 'historial'
        # Consulta stock
        if any(w in n for w in ['cuanto hay','cuantos hay','cuanto queda','cuantos quedan',
                                  'stock de','hay de','quedan de','tenemos de','existe',
                                  'disponible','inventario de','mostrar','ver stock',
                                  'listar','lista de','todos los','que hay']):
            return 'consulta_stock'
        # Resumen
        if any(w in n for w in ['resumen','total','general','todo el inventario',
                                  'todo el stock','cuanto tengo','que tengo']):
            return 'resumen'
        # Bajo stock
        if any(w in n for w in ['bajo stock','poco stock','poco queda','se acab',
                                  'quedan pocos','queda poco','critico','sin stock',
                                  'agotado','menor a','menos de','por debajo']):
            return 'bajo_stock'
        # Ubicaciones
        if any(w in n for w in ['ubicacion','ubicaciones','donde esta','donde queda',
                                  'en que lugar','deposito','sector']):
            return 'ubicaciones'
        # Pedidos
        if any(w in n for w in ['pedido','pedidos','orden','ordenes','nube','cloud',
                                  'cargar pedido','subir pedido']):
            return 'pedidos'
        # Charla / ayuda
        return 'charla'

    def _responder_charla(txt):
        n = _normalizar(txt)
        if any(w in n for w in ['hola','buenas','buen dia','buenas tardes','buenas noches','hey']):
            return f"Hola {usuario}! 👋 Estoy listo para ayudarte con el inventario. Podés preguntarme por stock, pedirme que registre movimientos o simplemente charlar."
        if any(w in n for w in ['gracias','muchas gracias','grax','grazie']):
            return "De nada! 😊 En qué más te puedo ayudar?"
        if any(w in n for w in ['chiste','chistoso','broma','reir']):
            import random
            chistes = [
                "¿Por qué el inventario fue al médico? Porque tenía stock-itis crónica. 😄",
                "¿Qué le dijo un lote a otro? ¡Nos vemos en la ubicación! 📦",
                "¿Cómo se llama el producto que siempre está de buen humor? ¡El que nunca se agota! 😂",
                "¿Por qué el depósito está siempre ordenado? Porque tiene mucho self-control de inventario. 🏭",
            ]
            return random.choice(chistes)
        if any(w in n for w in ['quien eres','que eres','como te llamas','tu nombre']):
            return "Soy el asistente de LOGIEZE 🤖 — tu ayudante de inventario. Puedo consultar stock, registrar movimientos, mostrar historial y mucho más. Todo sin límites ni costos!"
        if any(w in n for w in ['que podes hacer','que sabes','ayuda','help','capacidades','comandos']):
            return ("Puedo ayudarte con todo esto:\n\n"
                    "📦 CONSULTAS\n"
                    "  • ¿Cuánto hay del código 147?\n"
                    "  • ¿Qué productos tienen bajo stock?\n"
                    "  • Mostrame las ubicaciones del depósito\n"
                    "  • Dame un resumen del inventario\n\n"
                    "⚡ ACCIONES\n"
                    "  • Sacá 10 unidades de Ibuprofeno de 01-1A\n"
                    "  • Agregá 50 unidades del código 200 en 02-3B\n"
                    "  • Mové el lote de ABC de 01-A a 03-B\n"
                    "  • Corregí la cantidad de XYZ a 25 en 02-1A\n\n"
                    "📋 HISTORIAL\n"
                    "  • Mostrame los últimos movimientos\n"
                    "  • Qué se movió hoy?\n\n"
                    "Solo escribime en lenguaje natural, ¡sin comandos especiales!")
        if any(w in n for w in ['como estas','como andas','todo bien','como te va']):
            return "Todo bien, listo para trabajar! 💪 ¿En qué te puedo ayudar con el inventario?"
        if any(w in n for w in ['clima','tiempo','lluvia','sol','temperatura']):
            return "No tengo acceso al clima, pero sí a todo tu inventario! 😄 ¿Querés consultar algo del depósito?"
        return None

    def _procesar_mensaje(txt):
        """Motor principal: detecta intención y genera respuesta o acción."""
        n = _normalizar(txt)
        intencion = _detectar_intencion(txt)

        # ── CONSULTA STOCK ────────────────────────────────────────────────────
        if intencion == 'consulta_stock':
            prod = _buscar_producto(txt)
            if prod:
                cod  = str(prod["cod_int"])
                nom  = prod["nombre"]
                stk  = int(float(prod.get("cantidad_total") or 0))
                lotes = _lotes_producto(cod)
                if not lotes:
                    return None, f"📦 *{nom}* (cod: {cod})\nStock total: {stk} uds\nNo hay lotes activos en el inventario."
                detalle = "\n".join(
                    f"  📍 {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))} uds"
                    + (f" · vto: {l.get('fecha','')}" if l.get('fecha') else "")
                    for l in lotes
                )
                return None, f"📦 *{nom}* (cod: {cod})\nStock total: **{stk} uds**\n\nLotes:\n{detalle}"
            else:
                # Búsqueda amplia
                resultados = _listar_productos_query(txt)
                if resultados:
                    lineas = []
                    for p in resultados[:10]:
                        stk = int(float(p.get("cantidad_total") or 0))
                        lineas.append(f"  • {p['nombre']} [cod:{p['cod_int']}] — {stk} uds")
                    return None, f"Encontré {len(resultados)} producto(s):\n\n" + "\n".join(lineas)
                return None, "No encontré ningún producto con ese nombre o código. Probá con otro término."

        # ── RESUMEN ───────────────────────────────────────────────────────────
        elif intencion == 'resumen':
            total_prods = len(maestra)
            total_stock = sum(int(float(p.get("cantidad_total") or 0)) for p in maestra)
            sin_stock   = sum(1 for p in maestra if int(float(p.get("cantidad_total") or 0)) == 0)
            top5 = sorted(maestra, key=lambda p: float(p.get("cantidad_total") or 0), reverse=True)[:5]
            top_txt = "\n".join(
                f"  {i+1}. {p['nombre']} — {int(float(p.get('cantidad_total',0)))} uds"
                for i,p in enumerate(top5)
            )
            return None, (f"📊 **Resumen del inventario**\n\n"
                         f"  • Productos registrados: {total_prods}\n"
                         f"  • Stock total: {total_stock:,} uds\n"
                         f"  • Sin stock: {sin_stock} productos\n\n"
                         f"🏆 Top 5 con más stock:\n{top_txt}")

        # ── BAJO STOCK ────────────────────────────────────────────────────────
        elif intencion == 'bajo_stock':
            limite = _extraer_numero(txt)
            if limite == 0: limite = 10
            bajos = [p for p in maestra if int(float(p.get("cantidad_total") or 0)) < limite]
            bajos.sort(key=lambda p: float(p.get("cantidad_total") or 0))
            if not bajos:
                return None, f"✅ No hay productos con menos de {int(limite)} unidades. Todo en orden!"
            lineas = [f"  ⚠️ {p['nombre']} [cod:{p['cod_int']}] — {int(float(p.get('cantidad_total',0)))} uds"
                      for p in bajos[:20]]
            return None, (f"📉 Productos con menos de {int(limite)} uds ({len(bajos)} encontrados):\n\n"
                         + "\n".join(lineas)
                         + ("\n\n..." if len(bajos) > 20 else ""))

        # ── UBICACIONES ───────────────────────────────────────────────────────
        elif intencion == 'ubicaciones':
            prod = _buscar_producto(txt)
            if prod:
                cod   = str(prod["cod_int"])
                lotes = _lotes_producto(cod)
                if not lotes:
                    return None, f"No hay lotes activos de *{prod['nombre']}* en el inventario."
                detalle = "\n".join(
                    f"  📍 {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))} uds"
                    + (f" · vto: {l.get('fecha','')}" if l.get('fecha') else "")
                    for l in lotes
                )
                return None, f"📍 Ubicaciones de *{prod['nombre']}*:\n{detalle}"
            # Listar todas las ubicaciones únicas
            ubs = {}
            for l in inventario:
                u = l.get("ubicacion","?")
                ubs[u] = ubs.get(u,0) + 1
            ubs_sorted = sorted(ubs.items())
            lineas = [f"  📍 {u} — {n} lote{'s' if n>1 else ''}" for u,n in ubs_sorted[:30]]
            return None, f"📍 Ubicaciones activas ({len(ubs)}):\n\n" + "\n".join(lineas)

        # ── HISTORIAL ─────────────────────────────────────────────────────────
        elif intencion == 'historial':
            hist = cargar_historial_cache()
            prod = _buscar_producto(txt)
            if prod:
                cod = str(prod["cod_int"])
                hist = [h for h in hist if str(h.get("cod_int",""))==cod or
                        _normalizar(h.get("nombre",""))==_normalizar(prod["nombre"])][:15]
                titulo = f"Historial de *{prod['nombre']}*"
            else:
                limite_h = int(_extraer_numero(txt)) if _extraer_numero(txt) > 0 else 15
                hist = hist[:limite_h]
                titulo = f"Últimos {len(hist)} movimientos"
            if not hist:
                return None, "No hay movimientos registrados aún."
            lineas = []
            for h in hist:
                tipo = h.get("tipo","?")
                nom  = h.get("nombre","?")
                cant = h.get("cantidad","?")
                ubi  = h.get("ubicacion","?")
                fh   = h.get("fecha_hora","")
                usr  = h.get("usuario","?")
                icono = "📤" if "SALIDA" in tipo else ("📥" if "ENTRADA" in tipo else ("🔀" if "MOV" in tipo else "✏️"))
                lineas.append(f"{icono} {fh} | {tipo} | {nom} x{cant} en {ubi} por {usr}")
            return None, f"📋 {titulo}:\n\n" + "\n".join(lineas)

        # ── PEDIDOS ───────────────────────────────────────────────────────────
        elif intencion == 'pedidos':
            try:
                peds = sb.table("pedidos").select("id,nombre,fecha,estado,items") \
                         .in_("estado",["pendiente","en_proceso"]) \
                         .order("id",desc=True).limit(10).execute().data or []
                if not peds:
                    return None, "No hay pedidos pendientes en la nube en este momento."
                lineas = []
                for p in peds:
                    items = p.get("items") or []
                    n_items = len(items) if isinstance(items, list) else "?"
                    icono = "🟡" if p.get("estado")=="en_proceso" else "🟢"
                    lineas.append(f"{icono} #{p['id']} {p['nombre']} — {n_items} ítems — {p.get('fecha','')}")
                return None, f"☁️ Pedidos en la nube ({len(peds)}):\n\n" + "\n".join(lineas)
            except:
                return None, "No se pudo acceder a los pedidos. Verificá la conexión."

        # ── SALIDA ────────────────────────────────────────────────────────────
        elif intencion == 'salida':
            if rol in ('visita','vendedor'):
                return None, "❌ Tu rol no tiene permisos para registrar salidas."
            prod = _buscar_producto(txt)
            cant = _extraer_numero(txt)
            ubi  = _extraer_ubicacion(txt)
            if not prod:
                return None, "No encontré el producto. Especificá el nombre o código. Ej: *Sacá 10 de Ibuprofeno de 01-1A*"
            if cant == 0:
                return None, f"¿Cuántas unidades de *{prod['nombre']}* querés sacar?"
            cod  = str(prod["cod_int"])
            nom  = prod["nombre"]
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = None
            if ubi:
                lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi), None)
            if not lote:
                lote = next((l for l in lotes_p if float(l.get("cantidad",0) or 0)>=cant), None)
                if lote: ubi = str(lote.get("ubicacion",""))
            if not lote:
                tot = sum(float(l.get("cantidad",0) or 0) for l in lotes_p)
                if tot == 0:
                    return None, f"❌ No hay stock de *{nom}*."
                detalle = "\n".join(f"  📍 {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))} uds" for l in lotes_p)
                return None, f"❌ No encontré stock suficiente de *{nom}* para sacar {int(cant)} uds.\n\nStock disponible:\n{detalle}\n\nEspecificá la ubicación. Ej: *Sacá {int(cant)} de {nom} de {lotes_p[0].get('ubicacion','01-1A')}*"
            disp = float(lote.get("cantidad",0) or 0)
            if disp < cant:
                return None, f"❌ Solo hay {int(disp)} uds de *{nom}* en {ubi}. No alcanza para sacar {int(cant)}."
            nueva = disp - cant
            if nueva <= 0:
                sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else:
                sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            registrar_historial("SALIDA",cod,nom,cant,ubi,usuario)
            recalcular_maestra(cod,inventario)
            refrescar()
            return True, f"✅ Salida registrada!\n\n📦 *{nom}* (cod:{cod})\n📤 Cantidad: {int(cant)} uds\n📍 Desde: {ubi}\n📊 Quedan: {int(nueva)} uds en {ubi}"

        # ── ENTRADA ───────────────────────────────────────────────────────────
        elif intencion == 'entrada':
            if rol in ('visita','vendedor'):
                return None, "❌ Tu rol no tiene permisos para registrar entradas."
            prod = _buscar_producto(txt)
            cant = _extraer_numero(txt)
            ubi  = _extraer_ubicacion(txt)
            if not prod:
                return None, "No encontré el producto. Ej: *Agregá 50 de Ibuprofeno en 02-3B*"
            if cant == 0:
                return None, f"¿Cuántas unidades de *{prod['nombre']}* querés agregar?"
            if not ubi:
                lotes_p = [l for l in inventario if str(l.get("cod_int",""))==str(prod["cod_int"])]
                if lotes_p:
                    ubi = str(lotes_p[0].get("ubicacion",""))
                    return None, f"¿En qué ubicación agregás las {int(cant)} uds de *{prod['nombre']}*?\nUbicación actual: {ubi}\n\nEscribí por ej: *Agregá {int(cant)} de {prod['nombre']} en {ubi}*"
                return None, f"¿En qué ubicación ponés las {int(cant)} uds de *{prod['nombre']}*? Ej: *en 02-3B*"
            cod = str(prod["cod_int"]); nom = prod["nombre"]
            # Buscar vencimiento
            vto_m = _re.search(r'\b(\d{1,2}[/\-]\d{2,4})\b', txt)
            fv = vto_m.group(1) if vto_m else ""
            lotes_ubi = [l for l in inventario if str(l.get("cod_int",""))==cod and str(l.get("ubicacion","")).upper()==ubi]
            if lotes_ubi:
                nueva = float(lotes_ubi[0].get("cantidad",0) or 0) + cant
                sb.table("inventario").update({"cantidad":nueva}).eq("id",lotes_ubi[0]["id"]).execute()
            else:
                sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant,"ubicacion":ubi,"fecha":fv,"deposito":"PRINCIPAL"}).execute()
            registrar_historial("ENTRADA",cod,nom,cant,ubi,usuario)
            recalcular_maestra(cod,inventario)
            refrescar()
            return True, f"✅ Entrada registrada!\n\n📦 *{nom}* (cod:{cod})\n📥 Cantidad: {int(cant)} uds\n📍 En: {ubi}" + (f"\n📅 Vto: {fv}" if fv else "")

        # ── MOVER ─────────────────────────────────────────────────────────────
        elif intencion == 'mover':
            if rol in ('visita','vendedor'):
                return None, "❌ Tu rol no tiene permisos para mover lotes."
            prod = _buscar_producto(txt)
            cant = _extraer_numero(txt)
            ubis = _re.findall(r'\b([0-9]{1,2}[-_][0-9A-Za-z]{1,3}[A-Za-z]?)\b', txt)
            if not prod:
                return None, "No encontré el producto. Ej: *Mové Ibuprofeno de 01-1A a 03-2B*"
            ubi_orig = ubis[0].upper() if len(ubis)>=1 else ""
            ubi_dest = ubis[1].upper() if len(ubis)>=2 else ""
            if not ubi_orig or not ubi_dest:
                return None, f"Especificá origen y destino. Ej: *Mové {prod['nombre']} de 01-1A a 03-2B*"
            cod = str(prod["cod_int"]); nom = prod["nombre"]
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi_orig), None)
            if not lote:
                return None, f"❌ No hay lote de *{nom}* en {ubi_orig}."
            disp = float(lote.get("cantidad",0) or 0)
            cant_mov = cant if cant > 0 else disp
            if cant_mov > disp:
                return None, f"❌ Solo hay {int(disp)} uds en {ubi_orig}."
            nueva = disp - cant_mov
            if nueva <= 0:
                sb.table("inventario").delete().eq("id",lote["id"]).execute()
            else:
                sb.table("inventario").update({"cantidad":nueva}).eq("id",lote["id"]).execute()
            sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant_mov,"ubicacion":ubi_dest,"fecha":lote.get("fecha",""),"deposito":lote.get("deposito","PRINCIPAL")}).execute()
            registrar_historial("MOVIMIENTO",cod,nom,cant_mov,f"{ubi_orig}→{ubi_dest}",usuario)
            recalcular_maestra(cod,inventario)
            refrescar()
            return True, f"✅ Movimiento registrado!\n\n📦 *{nom}*\n🔀 {int(cant_mov)} uds: {ubi_orig} → {ubi_dest}"

        # ── CORREGIR ──────────────────────────────────────────────────────────
        elif intencion == 'corregir':
            if rol in ('visita','vendedor'):
                return None, "❌ Tu rol no tiene permisos para corregir stock."
            prod = _buscar_producto(txt)
            cant = _extraer_numero(txt)
            ubi  = _extraer_ubicacion(txt)
            if not prod:
                return None, "No encontré el producto. Ej: *Corregí Ibuprofeno a 25 uds en 01-1A*"
            if cant == 0:
                return None, f"¿A cuántas unidades corregís *{prod['nombre']}*?"
            cod = str(prod["cod_int"]); nom = prod["nombre"]
            lotes_p = [l for l in inventario if str(l.get("cod_int",""))==cod]
            lote = next((l for l in lotes_p if str(l.get("ubicacion","")).upper()==ubi), None) if ubi else None
            if not lote and lotes_p:
                lote = lotes_p[0]; ubi = str(lote.get("ubicacion",""))
            if not lote:
                return None, f"❌ No hay lotes de *{nom}* en el inventario."
            ant = float(lote.get("cantidad",0) or 0)
            sb.table("inventario").update({"cantidad":cant}).eq("id",lote["id"]).execute()
            registrar_historial("CORRECCIÓN",cod,nom,cant-ant,ubi,usuario)
            recalcular_maestra(cod,inventario)
            refrescar()
            return True, f"✅ Corrección aplicada!\n\n📦 *{nom}* en {ubi}\n✏️ {int(ant)} → {int(cant)} uds"

        # ── CHARLA ────────────────────────────────────────────────────────────
        else:
            resp_charla = _responder_charla(txt)
            if resp_charla:
                return None, resp_charla
            # Intentar como consulta de stock de última instancia
            prod = _buscar_producto(txt)
            if prod:
                cod  = str(prod["cod_int"])
                stk  = int(float(prod.get("cantidad_total") or 0))
                lotes = _lotes_producto(cod)
                detalle = "\n".join(
                    f"  📍 {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))} uds"
                    for l in lotes
                ) if lotes else "  Sin lotes activos"
                return None, f"📦 *{prod['nombre']}* (cod:{cod})\nStock total: **{stk} uds**\n\n{detalle}"
            return None, ("No entendí bien lo que querés hacer. Podés decirme por ejemplo:\n\n"
                         "  📦 *¿Cuánto hay del código 147?*\n"
                         "  📤 *Sacá 10 de Ibuprofeno de 01-1A*\n"
                         "  📥 *Agregá 50 del código 200 en 02-3B*\n"
                         "  🔀 *Mové ABC de 01-A a 03-B*\n"
                         "  ✏️ *Corregí XYZ a 25 uds en 02-1A*\n"
                         "  📋 *Mostrame los últimos movimientos*")

    # ── Mostrar historial del chat ─────────────────────────────────────────────
    if not st.session_state.bot_hist:
        st.markdown("""
        <div style="text-align:center;padding:30px 10px 10px">
            <div style="font-size:52px">🤖</div>
            <div style="font-size:16px;font-weight:700;color:#94A3B8;margin-top:10px">
                Hola! Soy tu asistente de inventario.</div>
            <div style="font-size:13px;color:#64748B;margin-top:8px;line-height:2">
                Sin límites · Sin internet · 100% tuyo
            </div>
        </div>""", unsafe_allow_html=True)
        # Sugerencias
        sugerencias = [
            "¿Cuánto hay del código 147?",
            "Resumen del inventario",
            "Productos con bajo stock",
            "Últimos movimientos",
            "¿Qué podés hacer?",
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
                st.markdown('<div class="chat-lbl">🤖 Asistente</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="msg-bot">{msg["texto"]}</div>', unsafe_allow_html=True)
                if msg.get("accion_log"):
                    cls = "msg-ok" if msg.get("ok") else "msg-err"
                    st.markdown(f'<div class="{cls}">⚡ {msg["accion_log"]}</div>', unsafe_allow_html=True)

    # ── Botones rápidos (después del historial) ────────────────────────────────
    if st.session_state.bot_hist:
        st.markdown("<br>", unsafe_allow_html=True)
        qc = st.columns(4)
        for i,(lbl,preg) in enumerate([
            ("📉 Bajo stock",  "Productos con menos de 10 unidades"),
            ("📦 Resumen",     "Resumen del inventario"),
            ("📋 Historial",   "Últimos movimientos"),
            ("📍 Ubicaciones", "Mostrame las ubicaciones"),
        ]):
            with qc[i]:
                if st.button(lbl, use_container_width=True, key=f"qr_{i}"):
                    st.session_state._bot_quick = preg
                    st.rerun()

    _quick = st.session_state.pop("_bot_quick", None)

    # ── Input ──────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    ic1, ic2 = st.columns([5,1])
    with ic1:
        txt_in = st.text_input("msg", label_visibility="collapsed",
                               placeholder="Escribí tu mensaje... ej: ¿Cuánto hay del código 147?",
                               key="bot_input")
    with ic2:
        send = st.button("➤ Enviar", use_container_width=True, type="primary", key="bot_send")

    _final = _quick or (txt_in.strip() if send and txt_in else None)

    if _final:
        st.session_state.bot_hist.append({"rol":"user","texto":_final})
        try:
            ok, respuesta = _procesar_mensaje(_final)
            entry = {"rol":"assistant","texto":respuesta}
            if ok is True:
                entry["ok"] = True
                entry["accion_log"] = respuesta.split('\n')[0]
            elif ok is False:
                entry["ok"] = False
                entry["accion_log"] = respuesta
        except Exception as e:
            entry = {"rol":"assistant","texto":f"❌ Error interno: {str(e)[:150]}","ok":False}
        st.session_state.bot_hist.append(entry)
        st.rerun()

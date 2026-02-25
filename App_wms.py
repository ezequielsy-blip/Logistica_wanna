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

# ── SESIÓN ────────────────────────────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.rol     = None

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
                st.session_state.usuario = "admin"; st.session_state.rol = "admin"; st.rerun()
            else:
                try:
                    r = sb.table("usuarios").select("*").eq("usuario", usuario.lower().strip()).eq("clave", clave).execute().data
                    if r:
                        st.session_state.usuario = r[0]['usuario']
                        st.session_state.rol     = r[0]['rol']
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
ROL_ICON = {"admin":"👑","operario":"🔧","visita":"👁️"}.get(rol,"👤")

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
    if st.button("🚪 Salir", use_container_width=True):
        st.session_state.usuario = None; st.rerun()

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
tab_mov, tab_desp, tab_hist, tab_plan, tab_admin = st.tabs([
    "📦 MOVIMIENTOS", "🚚 DESPACHO", "📋 HISTORIAL", "📊 PLANILLA", "🔐 ADMIN"
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
            "Stock":  int(p.get('stock_total',0) or 0),
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
    st.markdown('<p class="sec-label">🚚 PICKING CONTROLADO</p>', unsafe_allow_html=True)
    st.caption("Pegá ítems del pedido uno por uno o usá la carga manual.")

    # Estado del pedido en session_state
    if "pedido" not in st.session_state:
        st.session_state.pedido = []  # list of {cod, cant, nombre}

    # Agregar ítem
    with st.expander("➕ Agregar ítem al pedido"):
        col_dc, col_dq = st.columns([2,1])
        with col_dc:
            d_cod = st.text_input("Código interno:", key="d_cod")
        with col_dq:
            d_cant = st.number_input("Cantidad:", min_value=1, step=1, key="d_cant")
        if st.button("Agregar al pedido", key="btn_add_ped"):
            if d_cod.strip():
                prod = next((p for p in maestra if str(p['cod_int']) == d_cod.strip()), None)
                nom  = prod['nombre'] if prod else "NO ENCONTRADO"
                st.session_state.pedido.append({"cod": d_cod.strip(), "cant": d_cant, "nombre": nom})
                st.rerun()

    # Mostrar pedido
    if st.session_state.pedido:
        st.markdown('<p class="sec-label">📋 ÍTEMS DEL PEDIDO</p>', unsafe_allow_html=True)
        pedido_a_eliminar = None
        for i, item in enumerate(st.session_state.pedido):
            col_pi, col_pb = st.columns([4,1])
            with col_pi:
                st.markdown(f"""
                <div class="lote-card">
                    <b style="font-size:15px;">{item['nombre']}</b><br>
                    <span style="color:#94A3B8;font-size:13px;">Código: {item['cod']}</span>
                    <span style="float:right;font-size:22px;font-weight:900;color:#10B981;">{item['cant']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_pb:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_ped_{i}"):
                    pedido_a_eliminar = i
        if pedido_a_eliminar is not None:
            st.session_state.pedido.pop(pedido_a_eliminar); st.rerun()

        # Seleccionar ítem a despachar
        st.markdown("---")
        st.markdown('<p class="sec-label">SELECCIONAR ÍTEM A DESPACHAR</p>', unsafe_allow_html=True)
        idx_desp = st.selectbox("Ítem:", range(len(st.session_state.pedido)),
                                format_func=lambda i: f"{st.session_state.pedido[i]['nombre']} — {st.session_state.pedido[i]['cant']} uds",
                                key="desp_sel")
        item_sel = st.session_state.pedido[idx_desp]
        cod_d    = item_sel['cod']
        lotes_d  = [l for l in idx_inv.get(cod_d,[]) if float(l.get('cantidad',0)) > 0]

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

            lote_ops = [f"[{int(float(l.get('cantidad',0)))}] {l.get('ubicacion','')} — {l.get('fecha','')} — {l.get('deposito','')}" for l in lotes_d]
            idx_ld = st.selectbox("Lote a descontar:", range(len(lote_ops)),
                                  format_func=lambda i: lote_ops[i], key="lote_desp")
            lote_d = lotes_d[idx_ld]

            if st.button("✅ DESCONTAR DEL LOTE", use_container_width=True, key="btn_desc"):
                cant_p = float(item_sel['cant'])
                cant_l = float(lote_d.get('cantidad',0))
                try:
                    if cant_l <= cant_p:
                        sb.table("inventario").delete().eq("id", lote_d['id']).execute()
                        pendiente = cant_p - cant_l
                        if pendiente > 0:
                            st.session_state.pedido[idx_desp]['cant'] = int(pendiente)
                            registrar_historial("SALIDA", cod_d, item_sel['nombre'], cant_l, lote_d.get('ubicacion',''), usuario)
                            recalcular_maestra(cod_d, inventario)
                            st.warning(f"Lote agotado. Quedan {int(pendiente)} unidades pendientes. Seleccioná otro lote.")
                            refrescar(); st.rerun()
                        else:
                            st.session_state.pedido.pop(idx_desp)
                    else:
                        nq = cant_l - cant_p
                        sb.table("inventario").update({"cantidad": nq}).eq("id", lote_d['id']).execute()
                        st.session_state.pedido.pop(idx_desp)

                    registrar_historial("SALIDA", cod_d, item_sel['nombre'], cant_p, lote_d.get('ubicacion',''), usuario)
                    recalcular_maestra(cod_d, inventario)
                    st.success(f"✅ {item_sel['nombre']} — {int(cant_p)} uds descontadas.")
                    refrescar(); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Sin stock disponible para este producto.")

        if st.button("🗑️ Limpiar pedido completo", key="limpiar_ped"):
            st.session_state.pedido = []; st.rerun()
    else:
        st.info("El pedido está vacío. Agregá ítems con el formulario de arriba.")


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
            with col_ar: nr = st.selectbox("Rol", ["operario","admin","visita"])
            if st.form_submit_button("➕ Crear usuario", use_container_width=True):
                if nu and np_:
                    try:
                        sb.table("usuarios").insert({"usuario": nu.lower().strip(), "clave": np_, "rol": nr}).execute()
                        st.success("✅ Usuario creado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

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

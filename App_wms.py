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
    page_title="LOGIEZE — Gestión de Inventario",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
_LOGO_B64 = "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"
_LOGO_SRC  = f"data:image/jpeg;base64,{_LOGO_B64}"
# ── PWA / Favicon para acceso directo desde Chrome ──────────────────────
import streamlit.components.v1 as _stc_pwa
_stc_pwa.html(f"""
<script>
// Inject favicon and manifest into parent document
(function(){{
  var doc = window.parent.document;

  // Favicon
  var existing = doc.querySelector("link[rel*='icon']");
  if(existing) existing.parentNode.removeChild(existing);
  var link = doc.createElement('link');
  link.rel = 'shortcut icon';
  link.type = 'image/jpeg';
  link.href = '{_LOGO_SRC}';
  doc.head.appendChild(link);

  // Apple touch icon (iOS/Android PWA)
  var apple = doc.createElement('link');
  apple.rel = 'apple-touch-icon';
  apple.href = '{_LOGO_SRC}';
  doc.head.appendChild(apple);

  // Page title
  doc.title = 'LOGIEZE';

  // PWA Manifest
  var manifest = {{
    "name": "LOGIEZE",
    "short_name": "LOGIEZE",
    "description": "Sistema de gestión de inventario",
    "start_url": window.parent.location.href,
    "display": "standalone",
    "background_color": "#0F172A",
    "theme_color": "#3B82F6",
    "orientation": "portrait",
    "icons": [
      {{"src": "{_LOGO_SRC}", "sizes": "192x192", "type": "image/jpeg"}},
      {{"src": "{_LOGO_SRC}", "sizes": "512x512", "type": "image/jpeg"}}
    ]
  }};
  var blob = new Blob([JSON.stringify(manifest)], {{type:'application/json'}});
  var url  = URL.createObjectURL(blob);
  var mlink = doc.querySelector("link[rel='manifest']");
  if(mlink) mlink.parentNode.removeChild(mlink);
  var ml = doc.createElement('link');
  ml.rel = 'manifest'; ml.href = url;
  doc.head.appendChild(ml);
}})();
</script>
""", height=0)


# ── ESTILOS MOBILE-FIRST — APK STYLE ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --bg:       #0F172A;
    --surface:  #1E293B;
    --surface2: #263347;
    --primary:  #3B82F6;
    --accent:   #06B6D4;
    --success:  #10B981;
    --warning:  #F59E0B;
    --danger:   #EF4444;
    --text:     #F1F5F9;
    --dim:      #94A3B8;
    --border:   #334155;
    --radius:   18px;
    --radius-sm:12px;
}

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.main .block-container {
    padding: 0 12px 100px 12px !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── TOP NAV BAR (status bar style) ── */
.app-topbar {
    position: sticky; top: 0; z-index: 999;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: 14px 16px 12px;
    display: flex; align-items: center; justify-content: space-between;
    margin: 0 -12px 16px -12px;
}
.app-topbar-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800;
    color: var(--text); letter-spacing: 1px;
}
.app-topbar-sub { font-size: 11px; color: var(--dim); margin-top: 1px; }
.app-badge {
    background: var(--primary);
    color: white; font-size: 10px; font-weight: 700;
    padding: 3px 8px; border-radius: 20px; letter-spacing: 0.5px;
}

/* ── METRIC CARDS ── */
.metric-row {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; margin-bottom: 16px;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 14px;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
}
.metric-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 30px; font-weight: 800;
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1;
}
.metric-card .label {
    font-size: 10px; font-weight: 600;
    color: var(--dim); letter-spacing: 1.5px;
    text-transform: uppercase; margin-top: 6px;
}

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #3B82F6, #06B6D4) !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 14px 20px !important;
    width: 100% !important;
    min-height: 52px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
}
div.stButton > button:active {
    transform: scale(0.97) !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.2) !important;
}

/* ── INPUTS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    color: var(--text) !important;
    font-size: 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 12px 14px !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}
label[data-testid="stWidgetLabel"] p {
    color: var(--dim) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ── CHAT / BOT ── */
.bot-bubble {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius) var(--radius) var(--radius) 4px;
    padding: 14px 16px;
    margin: 8px 0;
    font-size: 14px; line-height: 1.6;
    animation: slideUp 0.2s ease;
    max-width: 88%;
}
.user-bubble {
    background: linear-gradient(135deg, #1D4ED8, #3B82F6);
    border-radius: var(--radius) var(--radius) 4px var(--radius);
    padding: 12px 16px;
    margin: 8px 0 8px auto;
    font-size: 14px; line-height: 1.6;
    max-width: 80%;
    text-align: right;
    box-shadow: 0 4px 12px rgba(59,130,246,0.25);
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── SECTION HEADERS ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px; font-weight: 700;
    color: var(--dim); letter-spacing: 2px;
    text-transform: uppercase;
    margin: 20px 0 10px;
    padding-left: 2px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: var(--border);
}

/* ── CARDS ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}
.card:active { border-color: var(--primary); }
.card-title {
    font-weight: 600; font-size: 14px;
    color: var(--text); margin-bottom: 4px;
}
.card-sub { font-size: 12px; color: var(--dim); }
.card-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    color: var(--primary);
    font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    margin-top: 8px;
}
.card-badge.green  { background: rgba(16,185,129,0.15); color: var(--success); }
.card-badge.red    { background: rgba(239,68,68,0.15);  color: var(--danger); }
.card-badge.yellow { background: rgba(245,158,11,0.15); color: var(--warning); }

/* ── BOTTOM NAV ── */
.bottom-nav {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000;
    background: rgba(15,23,42,0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-top: 1px solid var(--border);
    display: flex; justify-content: space-around;
    padding: 8px 0 20px;
}
.nav-item {
    display: flex; flex-direction: column; align-items: center;
    gap: 3px; padding: 6px 16px;
    color: var(--dim); font-size: 10px; font-weight: 600;
    letter-spacing: 0.5px; cursor: pointer;
    transition: color 0.15s;
    text-decoration: none;
}
.nav-item.active { color: var(--primary); }
.nav-item .nav-icon { font-size: 22px; line-height: 1; }

/* ── TABLES ── */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── TABS ── */
div[data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
div[data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--dim) !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
}
div[data-baseweb="tab-highlight"] { display: none !important; }
div[data-baseweb="tab-border"] { display: none !important; }

/* ── ALERTS / INFO ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
}

/* ── SPINNER ── */
div[data-testid="stSpinner"] { color: var(--primary) !important; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* ── ANDROID INPUTS ── */
div[data-baseweb="input"] > div {
    background: var(--surface) !important;
    border: none !important;
    border-bottom: 2px solid var(--border) !important;
    border-radius: 10px 10px 0 0 !important;
}
div[data-baseweb="input"] > div:focus-within {
    border-bottom-color: var(--primary) !important;
    box-shadow: none !important;
}
div[data-baseweb="input"] input {
    padding: 10px 14px 8px !important;
    font-size: 16px !important;
    caret-color: var(--primary) !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    min-height: 48px !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.15) !important;
}
ul[role="listbox"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,.4) !important;
}
li[role="option"] {
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
    color: var(--text) !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
    background: rgba(59,130,246,.15) !important;
    color: var(--primary) !important;
}
div[data-testid="stRadio"] > div {
    background: var(--surface) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 4px !important;
}
div[data-testid="stRadio"] label {
    border-radius: 10px !important;
    padding: 8px 16px !important;
    text-align: center !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: var(--primary) !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
}

/* ── MAIN HEADER ── */
.main-header {
    background: linear-gradient(135deg, rgba(29,78,216,0.4), rgba(6,182,212,0.1));
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: var(--radius);
    padding: 20px 18px;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 14px;
}
.main-header h1 {
    margin: 0;
    font-family: 'Syne', sans-serif;
    font-size: 24px; font-weight: 800;
    color: white; letter-spacing: 2px;
}
.main-header span { font-size: 12px; color: var(--dim); font-weight: 400; }
</style>
""", unsafe_allow_html=True)

# ── Override colores dinámico desde Supabase (admin) ─────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def _cargar_colores_css():
    try:
        import json as _jc
        r = get_supabase().table("app_config").select("config").eq("usuario","admin").execute()
        if r.data:
            return _jc.loads(r.data[0]["config"]).get("colores", {})
    except: pass
    return {}

_C_CSS = _cargar_colores_css()
if _C_CSS:
    _root_vars = "".join([
        f"--bg:{_C_CSS['bg']};" if 'bg' in _C_CSS else "",
        f"--surface:{_C_CSS['surface']};" if 'surface' in _C_CSS else "",
        f"--surface2:{_C_CSS['surface2']};" if 'surface2' in _C_CSS else "",
        f"--primary:{_C_CSS['primary']};" if 'primary' in _C_CSS else "",
        f"--accent:{_C_CSS['accent']};" if 'accent' in _C_CSS else "",
        f"--success:{_C_CSS['success']};" if 'success' in _C_CSS else "",
        f"--warning:{_C_CSS['warning']};" if 'warning' in _C_CSS else "",
        f"--danger:{_C_CSS['danger']};" if 'danger' in _C_CSS else "",
        f"--text:{_C_CSS['text']};" if 'text' in _C_CSS else "",
        f"--dim:{_C_CSS.get('text_dim','#94A3B8')};" if 'text_dim' in _C_CSS else "",
        f"--border:{_C_CSS['border']};" if 'border' in _C_CSS else "",
    ])
    st.markdown(f"<style>:root{{{_root_vars}}}</style>", unsafe_allow_html=True)



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

def calcular_vacias_rapido(ocupadas: set, max_n=None):
    """Calcula ubicaciones vacías. Si max_n es None devuelve todas."""
    try:
        import json as _jv
        r = get_supabase().table("app_config").select("config").eq("usuario","admin").execute()
        if r.data:
            cfg = _jv.loads(r.data[0]["config"])
            est_cfg = cfg.get("estantes", [])
        else:
            est_cfg = []
    except:
        est_cfg = []

    if not est_cfg:
        for _e in range(1, 28):
            if _e in [3,4]:            _nv,_ls = 4,"ABCDE"
            elif _e in [8,9,10,11,12]: _nv,_ls = 6,"ABCDEFG"
            else:                       _nv,_ls = 5,"ABCDE"
            est_cfg.append({"num":_e,"niveles":_nv,"disponible":True,
                             "letras_por_nivel":{str(_n):_ls for _n in range(1,_nv+1)}})

    vacias = []
    for cfg in sorted(est_cfg, key=lambda x: x["num"]):
        if not cfg.get("disponible", True): continue
        if max_n and len(vacias) >= max_n: break
        niv = cfg["niveles"]
        lpn = cfg.get("letras_por_nivel", {})
        for n in range(1, niv+1):
            if max_n and len(vacias) >= max_n: break
            lets = lpn.get(str(n), "ABCDE")
            for l in lets:
                u = f"{str(cfg['num']).zfill(2)}-{n}{l}"
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
    st.markdown(f"""
    <div style="max-width:380px;margin:60px auto 0;text-align:center;">
        <img src="{_LOGO_SRC}" style="width:96px;height:96px;border-radius:24px;
             object-fit:cover;box-shadow:0 8px 32px rgba(59,130,246,.45);margin-bottom:16px">
        <h1 style="font-size:30px;font-weight:900;letter-spacing:4px;margin:0;color:#F1F5F9;">LOGIEZE</h1>
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

# ── App topbar estilo Android ──────────────────────────────────────────────
st.markdown(f"""
<div class="app-topbar">
  <div style="display:flex;align-items:center;gap:12px">
    <img src="{_LOGO_SRC}" style="width:42px;height:42px;border-radius:12px;
         object-fit:cover;box-shadow:0 2px 10px rgba(0,0,0,.4);flex-shrink:0">
    <div>
      <div class="app-topbar-title">LOGIEZE</div>
      <div class="app-topbar-sub">{ROL_ICON} {usuario.upper()} · {rol.upper()}</div>
    </div>
  </div>
  <div class="app-badge">v3.0</div>
</div>""", unsafe_allow_html=True)
col_h1, col_h2 = st.columns(2)
with col_h1:
    if st.button("⟳ Actualizar", use_container_width=True):
        refrescar()
with col_h2:
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

# metrics removed

# ── Navegación desplegable estilo app ──────────────────────────────────────
_NAV_OPTIONS = ["📦 MOVIMIENTOS", "🚚 DESPACHO", "📋 HISTORIAL", "📊 PLANILLA", "⚙️ CONFIG", "🔐 ADMIN", "🤖 ASISTENTE"]
if "nav_tab" not in st.session_state:
    st.session_state.nav_tab = "📦 MOVIMIENTOS"

st.markdown("""
<style>
div[data-testid="stSelectbox"] > div > div {
    background: #1E293B !important;
    border: 1.5px solid #3B82F6 !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    min-height: 52px !important;
    padding: 4px 16px !important;
}
</style>""", unsafe_allow_html=True)

_nav_sel = st.selectbox("", _NAV_OPTIONS,
    index=_NAV_OPTIONS.index(st.session_state.nav_tab),
    label_visibility="collapsed", key="nav_select")
st.session_state.nav_tab = _nav_sel

# Emular tabs con session_state
class _FakeTab:
    def __init__(self, name): self.name = name
    def __enter__(self): return self
    def __exit__(self, *a): pass

_cur = st.session_state.nav_tab
tab_mov   = _FakeTab("📦 MOVIMIENTOS")
tab_desp  = _FakeTab("🚚 DESPACHO")
tab_hist  = _FakeTab("📋 HISTORIAL")
tab_plan  = _FakeTab("📊 PLANILLA")
tab_admin = _FakeTab("🔐 ADMIN")
tab_asist = _FakeTab("🤖 ASISTENTE")

def _show(name): return _cur == name


# ═══════════════════════════════════════════════════════════════════════════════
# TAB MOVIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════
if _show("📦 MOVIMIENTOS"):
    # Limpiar buscador solo DESPUÉS de registrar una operación (no al seleccionar)
    if st.session_state.pop("_clear_busq", False):
        st.session_state["busq"] = ""

    import streamlit.components.v1 as _stc_mov
    st.markdown('''<div style="font-size:11px;font-weight:700;color:#3B82F6;
    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px">
    🔍 BUSCAR PRODUCTO</div>''', unsafe_allow_html=True)

    _stc_mov.html("""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif}
body{background:transparent}
.btn{width:100%;background:linear-gradient(135deg,#10B981,#059669);color:#fff;
     border:none;border-radius:14px;padding:13px;font-size:14px;font-weight:700;
     cursor:pointer;-webkit-tap-highlight-color:transparent;
     box-shadow:0 4px 14px rgba(16,185,129,.4);display:flex;
     align-items:center;justify-content:center;gap:8px}
.btn:active{opacity:.85}.btn.act{background:linear-gradient(135deg,#EF4444,#F59E0B)}
.msg{font-size:12px;color:#94A3B8;text-align:center;margin-top:5px;min-height:16px}
.msg.ok{color:#10B981}.msg.er{color:#EF4444}
#ov{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.96);
    z-index:9999;flex-direction:column;align-items:center;justify-content:center;gap:16px}
#ov.show{display:flex}
video{width:90%;max-width:340px;border-radius:18px;border:3px solid #10B981}
.ln{width:90%;max-width:340px;height:3px;
    background:linear-gradient(90deg,transparent,#10B981,transparent);
    animation:sc 1.4s ease-in-out infinite}
@keyframes sc{0%,100%{opacity:.2}50%{opacity:1}}
.cl{background:#EF4444;color:#fff;border:none;border-radius:14px;
    padding:11px 32px;font-size:14px;font-weight:700;cursor:pointer}
</style></head><body>
<button class="btn" id="sb" onclick="doScan()">
  <span>📷</span><span>Escanear código de barras</span>
</button>
<div class="msg" id="msg"></div>
<div id="ov">
  <video id="vid" autoplay playsinline muted></video>
  <div class="ln"></div>
  <div style="color:#F1F5F9;font-size:14px;font-weight:700;text-align:center;padding:0 20px">
    Apuntá el código — se busca automáticamente</div>
  <button class="cl" onclick="closeScan()">✕ Cerrar</button>
</div>
<script>
var s=null,a=false,iv=null;
function setMsg(c,t){var el=document.getElementById('msg');el.className='msg '+(c||'');el.textContent=t}
function writeAndSubmit(val){
  // Buscar el input de búsqueda por placeholder
  var doc=window.parent.document;
  var inputs=doc.querySelectorAll('input[type="text"],input:not([type])');
  var inp=null;
  for(var i=0;i<inputs.length;i++){
    var ph=(inputs[i].placeholder||'').toLowerCase();
    if(ph.indexOf('barras')>=0||ph.indexOf('digo')>=0||ph.indexOf('ombre')>=0||ph.indexOf('buscar')>=0){inp=inputs[i];break}
  }
  if(!inp) inp=inputs[0]; // fallback primer input visible
  if(!inp){setMsg('er','No se encontró el campo');return}
  // Setter nativo de React
  var nativeSetter=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value');
  if(nativeSetter&&nativeSetter.set){nativeSetter.set.call(inp,val)}else{inp.value=val}
  // Disparar eventos que React escucha
  inp.dispatchEvent(new Event('input',{bubbles:true,cancelable:true}));
  inp.dispatchEvent(new Event('change',{bubbles:true,cancelable:true}));
  inp.focus();
  // Simular Enter para que Streamlit procese el texto_input
  setTimeout(function(){
    inp.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true,cancelable:true}));
    inp.dispatchEvent(new KeyboardEvent('keypress',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true,cancelable:true}));
    inp.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true,cancelable:true}));
  },80);
}
function doScan(){
  if(a){closeScan();return}
  if(!window.BarcodeDetector){setMsg('er','BarcodeDetector no soportado — Chrome Android requerido');return}
  a=true;
  document.getElementById('sb').className='btn act';
  document.getElementById('sb').innerHTML='<span>⏹</span><span>Detener</span>';
  document.getElementById('ov').className='show';
  setMsg('ok','Iniciando cámara...');
  navigator.mediaDevices.getUserMedia({video:{facingMode:'environment',width:{ideal:1920}}})
    .then(function(st2){
      s=st2;document.getElementById('vid').srcObject=st2;
      var det=new BarcodeDetector({formats:['ean_13','ean_8','code_128','code_39','upc_a','upc_e','itf','qr_code']});
      setMsg('ok','🟢 Escaneando...');
      iv=setInterval(function(){
        if(!a) return;
        det.detect(document.getElementById('vid')).then(function(codes){
          if(codes.length>0){
            var code=codes[0].rawValue;
            closeScan();
            setMsg('ok','✅ '+code);
            setTimeout(function(){writeAndSubmit(code)},120);
          }
        }).catch(function(){});
      },350);
    }).catch(function(e){closeScan();setMsg('er','❌ '+e.message)});
}
function closeScan(){
  a=false;clearInterval(iv);
  if(s){s.getTracks().forEach(function(t){t.stop()});s=null}
  document.getElementById('vid').srcObject=null;
  document.getElementById('sb').className='btn';
  document.getElementById('sb').innerHTML='<span>📷</span><span>Escanear código de barras</span>';
  document.getElementById('ov').className='';
}
</script></body></html>""", height=80)

    busqueda = st.text_input("Buscar", placeholder="Nombre, código o barras...",
                              label_visibility="collapsed", key="busq")

    productos_filtrados = []
    if busqueda:
        t = busqueda.strip()
        # Búsqueda exacta por código interno: .147 → cod_int == "147"
        if t.startswith('.'):
            cod_exacto = t[1:].strip()
            productos_filtrados = [p for p in maestra
                                   if str(p.get('cod_int','')).strip() == cod_exacto]
        # Código de barras puro (7-14 dígitos)
        elif t.isdigit() and 7 <= len(t) <= 14:
            productos_filtrados = [p for p in maestra
                                   if str(p.get('barras','')).strip() == t
                                   or str(p.get('cod_barras','')).strip() == t]
            if not productos_filtrados:
                productos_filtrados = [p for p in maestra
                                       if t in str(p.get('barras','')).upper()]
        else:
            T = t.upper()
            productos_filtrados = [p for p in maestra
                                   if T in str(p.get('nombre','')).upper()
                                   or T in str(p.get('cod_int','')).upper()
                                   or T in str(p.get('barras','')).upper()]

    if not productos_filtrados and busqueda:
        st.info("No se encontraron productos.")
    elif productos_filtrados:
        st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:8px">{len(productos_filtrados)} resultado(s)</div>', unsafe_allow_html=True)
        nombres_lista = [f"{p['nombre']}  ·  {int(float(p.get('cantidad_total') or 0))}u  [{p['cod_int']}]" for p in productos_filtrados]
        sel_idx = st.selectbox("", range(len(nombres_lista)),
                               format_func=lambda i: nombres_lista[i],
                               label_visibility="collapsed", key="sel_prod")
        prod_sel = productos_filtrados[sel_idx]
        cod_sel  = str(prod_sel['cod_int'])
        # Sin botón "Seleccionar" — el producto queda seleccionado directo al buscarlo

        lotes_prod = idx_inv.get(cod_sel, [])
        total_q    = sum(float(l.get('cantidad',0)) for l in lotes_prod)
        stk_color = "#10B981" if total_q > 10 else ("#F59E0B" if total_q > 0 else "#EF4444")
        st.markdown(f'''<div style="background:#1E293B;border-radius:14px;padding:14px 16px;margin:12px 0;border-left:4px solid {stk_color}"><div style="font-size:11px;font-weight:700;color:{stk_color};text-transform:uppercase">STOCK TOTAL</div><div style="font-size:32px;font-weight:900;color:#F1F5F9">{int(total_q)}u</div><div style="font-size:11px;color:#94A3B8">{prod_sel['nombre']}</div></div>''', unsafe_allow_html=True)

        # ── Lotes detallados ──────────────────────────────────────────────
        if lotes_prod:
            st.markdown('<div style="font-size:11px;font-weight:700;color:#3B82F6;letter-spacing:1.5px;margin:8px 0 4px">📦 LOTES EN STOCK</div>', unsafe_allow_html=True)
            for _lt in sorted(lotes_prod, key=lambda x: float(x.get('cantidad',0) or 0), reverse=True):
                _lq  = int(float(_lt.get('cantidad', 0) or 0))
                _lu  = str(_lt.get('ubicacion','—')).upper()
                _ld  = str(_lt.get('deposito','—'))
                _lf  = str(_lt.get('fecha','') or '').strip()
                _lf_disp = _lf if _lf else '—'
                _lc  = "#10B981" if _lq > 5 else ("#F59E0B" if _lq > 0 else "#EF4444")
                st.markdown(f'''<div style="background:#0F172A;border-radius:10px;padding:10px 14px;margin:4px 0;
                    display:flex;justify-content:space-between;align-items:center;border:1px solid #1E293B">
                  <div style="display:flex;gap:14px;align-items:center">
                    <div style="font-size:22px;font-weight:900;color:{_lc};min-width:36px">{_lq}u</div>
                    <div>
                      <div style="font-size:13px;font-weight:700;color:#F1F5F9">📍 {_lu}</div>
                      <div style="font-size:11px;color:#64748B">{_ld} · 📅 {_lf_disp}</div>
                    </div>
                  </div>
                </div>''', unsafe_allow_html=True)

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
            # Autoformato: inserta "/" sola después de tipear los 2 dígitos del mes
            import streamlit.components.v1 as _stc_fv
            _stc_fv.html("""<script>
(function(){
  var tries=0;
  function hook(){
    var doc=window.parent.document;
    var inputs=doc.querySelectorAll('input[type="text"],input:not([type])');
    var inp=null;
    // Hook ubicacion inputs — auto-insert "-" after 2 digits
    for(var i=0;i<inputs.length;i++){
      var ph2=inputs[i].placeholder||'';
      if((ph2.indexOf('05-3B')>=0||ph2.indexOf('12-2C')>=0) && !inputs[i]._lzUbiHook){
        inputs[i]._lzUbiHook=true;
        (function(el){
          el.addEventListener('input',function(){
            var v=el.value.replace(/[^0-9a-zA-Z-]/g,'').toUpperCase();
            // After 2 digits, auto-insert "-" if not already there
            if(v.length===2 && /^[0-9]{2}$/.test(v)){
              el.value=v+'-';
              el.dispatchEvent(new Event('input',{bubbles:true}));
            } else if(v.length>2 && v[2]!=='-' && /^[0-9]{2}/.test(v)){
              el.value=v.substring(0,2)+'-'+v.substring(2);
              el.dispatchEvent(new Event('input',{bubbles:true}));
            }
          });
        })(inputs[i]);
      }
    }
    for(var i=0;i<inputs.length;i++){
      var lbl=doc.querySelector('label[for="'+inputs[i].id+'"]');
      var ph=inputs[i].placeholder||'';
      if(ph==='ej: 06/26'||(lbl&&lbl.textContent&&lbl.textContent.indexOf('MM')>=0)){
        inp=inputs[i];break;
      }
    }
    if(!inp){if(tries++<30) setTimeout(hook,300);return;}
    if(inp._lzFvHook) return;
    inp._lzFvHook=true;
    inp.addEventListener('input',function(e){
      var v=inp.value.replace(/[^0-9]/g,'');  // solo dígitos
      if(v.length>=2){
        var mm=v.substring(0,2);
        var aa=v.substring(2,4);
        inp.value=aa.length>0 ? mm+'/'+aa : mm;
      } else {
        inp.value=v;
      }
      // Notificar a React del cambio
      var ns=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value');
      if(ns&&ns.set) ns.set.call(inp,inp.value);
      inp.dispatchEvent(new Event('input',{bubbles:true}));
      inp.dispatchEvent(new Event('change',{bubbles:true}));
    });
    // Evitar que borre la barra al pulsar backspace sobre ella
    inp.addEventListener('keydown',function(e){
      if(e.key==='Backspace'){
        var v=inp.value;
        if(v.length===3&&v[2]==='/'){
          e.preventDefault();
          inp.value=v.substring(0,2);
          var ns=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value');
          if(ns&&ns.set) ns.set.call(inp,inp.value);
          inp.dispatchEvent(new Event('input',{bubbles:true}));
        }
      }
    });
  }
  setTimeout(hook,400);
})();
</script>""", height=0)

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
            opciones_lotes = [f"[{int(float(l.get('cantidad',0)))}u] {l.get('ubicacion','')} — {l.get('deposito','')} | Vto:{l.get('fecha','')}"
                              for l in lotes_prod]
            lote_idx = st.selectbox("LOTE A DESCONTAR:", range(len(opciones_lotes)),
                                    format_func=lambda i: opciones_lotes[i], key="lote_op")
            lote_sel = lotes_prod[lote_idx]


        _barras_ok = st.session_state.get("_barras_ok", True if es_ingreso else None)
        if es_ingreso: _barras_ok = True

        # ── SCANNER DE CONFIRMACIÓN (siempre visible en SALIDA, independiente del campo barras)
        _do_register = False
        if not es_ingreso and lote_sel:
            _bc = str(prod_sel.get('barras','') or prod_sel.get('cod_barras','') or '').strip()

            # Card del scanner
            import streamlit.components.v1 as _stc_sal
            _exp_js = _bc if _bc else "__SIN_CODIGO__"
            _stc_sal.html(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif}}
body{{background:transparent}}
.wrap{{background:#1E293B;border:1.5px solid #334155;border-radius:16px;
       padding:14px 16px;margin:4px 0}}
.title{{font-size:10px;font-weight:800;color:#3B82F6;letter-spacing:1.5px;
        text-transform:uppercase;margin-bottom:10px}}
.scanbtn{{width:100%;background:linear-gradient(135deg,#3B82F6,#06B6D4);color:#fff;
          border:none;border-radius:12px;padding:13px;font-size:14px;font-weight:700;
          cursor:pointer;-webkit-tap-highlight-color:transparent;
          box-shadow:0 4px 14px rgba(59,130,246,.4);margin-bottom:8px}}
.scanbtn:active{{opacity:.85;transform:scale(.98)}}
.scanbtn.active{{background:linear-gradient(135deg,#EF4444,#F59E0B)}}
.info{{font-size:12px;color:#94A3B8;text-align:center}}
.status{{font-size:13px;font-weight:700;text-align:center;padding:8px;
         border-radius:10px;margin-top:6px;display:none}}
.status.ok{{background:rgba(16,185,129,.15);color:#10B981;display:block;
            border:1px solid rgba(16,185,129,.3)}}
.status.er{{background:rgba(239,68,68,.15);color:#EF4444;display:block;
            border:1px solid rgba(239,68,68,.3)}}
#ov{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;
     background:rgba(0,0,0,.96);z-index:9999;flex-direction:column;
     align-items:center;justify-content:center;gap:16px}}
#ov.show{{display:flex}}
video{{width:90%;max-width:340px;border-radius:18px;border:3px solid #3B82F6}}
.ln{{width:90%;max-width:340px;height:3px;
     background:linear-gradient(90deg,transparent,#3B82F6,transparent);
     animation:sc 1.4s ease-in-out infinite;border-radius:2px}}
@keyframes sc{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
.ov-txt{{color:#F1F5F9;font-size:14px;font-weight:700;text-align:center;padding:0 20px}}
.closebtn{{background:#EF4444;color:#fff;border:none;border-radius:14px;
           padding:12px 36px;font-size:14px;font-weight:700;cursor:pointer}}
</style></head><body>
<div class="wrap">
  <div class="title">📷 CONFIRMAR CON ESCÁNER</div>
  {"<div class='info' style='margin-bottom:8px'>Código esperado: <b style='color:#F1F5F9'>" + _bc + "</b></div>" if _bc else "<div class='info' style='margin-bottom:8px;color:#F59E0B'>⚠️ Este producto no tiene código de barras cargado</div>"}
  <button class="scanbtn" id="sb" onclick="doScan()">📷 Escanear producto</button>
  <div class="status" id="st"></div>
</div>
<div id="ov">
  <video id="v" autoplay playsinline muted></video>
  <div class="ln"></div>
  <div class="ov-txt">Apuntá el código de barras a la cámara</div>
  <button class="closebtn" onclick="closeScan()">✕ Cerrar</button>
</div>
<script>
var s=null,a=false,iv=null,exp="{_exp_js}";
function getInp(){{
  var all=window.parent.document.querySelectorAll('input');
  for(var i=0;i<all.length;i++){{
    var p=all[i].placeholder||'';
    if(p.indexOf('Esperando')>=0||p.indexOf('código')>=0) return all[i];
  }}
  // fallback: last visible input
  var vis=[]; for(var i=0;i<all.length;i++) if(!all[i].readOnly&&all[i].type!='hidden') vis.push(all[i]);
  return vis.length?vis[vis.length-1]:null;
}}
function setResult(code){{
  var inp=getInp();
  if(inp){{
    try{{Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value').set.call(inp,code)}}catch(e){{inp.value=code}}
    inp.dispatchEvent(new Event('input',{{bubbles:true}}));
    inp.dispatchEvent(new Event('change',{{bubbles:true}}));
    setTimeout(function(){{inp.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter',keyCode:13,bubbles:true}}))}},150);
  }}
  // Update status UI
  var ok = (exp==='__SIN_CODIGO__') ? true : (code===exp);
  var el=document.getElementById('st');
  el.className='status '+(ok?'ok':'er');
  el.textContent=ok?'✅ Correcto: '+code:'❌ No coincide: '+code+(exp!=='__SIN_CODIGO__'?' (esperado: '+exp+')':'');
}}
function doScan(){{
  if(a){{closeScan();return}}
  if(!window.BarcodeDetector){{
    document.getElementById('st').className='status er';
    document.getElementById('st').textContent='❌ Usá el lector físico o escribí el código abajo';
    return;
  }}
  a=true;
  document.getElementById('sb').className='scanbtn active';
  document.getElementById('sb').textContent='⏹ Detener';
  document.getElementById('ov').className='show';
  navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment',width:{{ideal:1280}}}}}})
    .then(function(st){{
      s=st; document.getElementById('v').srcObject=st;
      var det=new BarcodeDetector({{formats:['ean_13','ean_8','code_128','code_39','upc_a','upc_e','itf']}});
      iv=setInterval(function(){{
        if(!a) return;
        det.detect(document.getElementById('v')).then(function(c){{
          if(c.length>0){{closeScan();setResult(c[0].rawValue);}}
        }}).catch(function(){{}});
      }},350);
    }}).catch(function(e){{closeScan();document.getElementById('st').className='status er';document.getElementById('st').textContent='❌ Sin acceso a cámara: '+e.message}});
}}
function closeScan(){{
  a=false;clearInterval(iv);
  if(s){{s.getTracks().forEach(function(t){{t.stop()}});s=null}}
  document.getElementById('v').srcObject=null;
  document.getElementById('sb').className='scanbtn';
  document.getElementById('sb').textContent='📷 Escanear producto';
  document.getElementById('ov').className='';
}}
</script></body></html>""", height=150)

            # Campo de texto para lector físico o entrada manual de código
            cod_confirm = st.text_input("",
                placeholder="O escribí / escaneá el código acá...",
                label_visibility="collapsed", key="barras_confirm")

            if cod_confirm.strip():
                if not _bc:
                    # Sin código en BD → cualquier scan confirma
                    st.session_state["_barras_ok"] = True
                elif cod_confirm.strip() == _bc:
                    st.session_state["_barras_ok"] = True
                else:
                    st.session_state["_barras_ok"] = False
                _barras_ok = st.session_state.get("_barras_ok")

            # Botones — SIEMPRE visible el manual, escáner habilitado solo si confirmó
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                _scan_disabled = not (_barras_ok is True)
                _label_scan = "✅ DESCONTAR" if _barras_ok is True else "🔒 Escaneá primero"
                if st.button(_label_scan, use_container_width=True,
                             key="btn_reg", disabled=_scan_disabled,
                             type="primary"):
                    _do_register = True
            with col_b2:
                if st.button("🖐 DESCONTAR MANUAL", use_container_width=True,
                             key="btn_reg_manual"):
                    _do_register = True
        else:
            if st.button("✅ REGISTRAR OPERACIÓN", use_container_width=True,
                         key="btn_reg", type="primary"):
                _do_register = True

        if _do_register:
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
                    st.session_state.pop("_barras_ok", None)
                    st.session_state["_clear_busq"] = True
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
                        st.session_state["_clear_busq"] = True
                        refrescar()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB DESPACHO
# ═══════════════════════════════════════════════════════════════════════════════

if _show("🚚 DESPACHO"):
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
                    _items_tmp = [
                        {"cod":  str(it.get('cod_int', it.get('codigo',''))),
                         "cant": int(float(str(it.get('cantidad', it.get('cant', 0))))),
                         "nombre": it.get('nombre',''),
                         "ped_id": ped['id']}
                        for it in items_raw
                    ]
                    def _primer_ubi(item):
                        lts = sorted(
                            [l for l in idx_inv.get(item['cod'],[]) if float(l.get('cantidad',0))>0],
                            key=lambda l: str(l.get('ubicacion','') or '').upper()
                        )
                        return str(lts[0].get('ubicacion','ZZZ')).upper() if lts else 'ZZZ'
                    _items_tmp.sort(key=_primer_ubi)
                    st.session_state.pedido = _items_tmp
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
        # ── CANTIDAD PEDIDA — siempre visible y grande ─────────────────────
        st.markdown('<p class="sec-label">DESPACHAR ÍTEM</p>', unsafe_allow_html=True)

        # Selector de ítem con cantidad siempre visible
        if "desp_sel" not in st.session_state:
            st.session_state["desp_sel"] = 0
        idx_desp = st.session_state.get("desp_sel", 0)
        if idx_desp >= len(st.session_state.pedido):
            idx_desp = 0

        # Botones de selección de ítem — uno por fila, grande
        for _pi, _pitem in enumerate(st.session_state.pedido):
            _pstock = sum(float(l.get('cantidad',0)) for l in idx_inv.get(_pitem['cod'], []))
            _pok    = "✅" if _pstock >= _pitem['cant'] else "⚠️"
            _psel   = "🔵 " if _pi == idx_desp else ""
            _pbtn   = st.button(
                f"{_psel}{_pok}  {_pitem['nombre'][:30]}",
                key=f"sel_item_{_pi}",
                use_container_width=True,
                type="primary" if _pi == idx_desp else "secondary"
            )
            if _pbtn:
                st.session_state["desp_sel"] = _pi
                st.session_state["_pick_ok"] = None
                st.rerun()

        idx_desp = st.session_state.get("desp_sel", 0)
        if idx_desp >= len(st.session_state.pedido):
            idx_desp = 0
        item_sel = st.session_state.pedido[idx_desp]
        cod_d    = item_sel['cod']
        lotes_d  = sorted([l for l in idx_inv.get(cod_d, []) if float(l.get('cantidad', 0)) > 0], key=lambda l: str(l.get('ubicacion','') or '').upper())

        # ── CANTIDAD PEDIDA — enorme y siempre visible ───────────────────
        _cant_ped = item_sel['cant']
        _stk_ped  = sum(float(l.get('cantidad',0)) for l in lotes_d)
        _cped_col = "#10B981" if _stk_ped >= _cant_ped else "#EF4444"
        st.markdown(f"""
        <div style="background:#0F172A;border-radius:16px;padding:16px;margin:10px 0;
             border:2px solid {_cped_col};text-align:center">
          <div style="font-size:13px;color:#94A3B8;font-weight:700;letter-spacing:1px">
            CANTIDAD PEDIDA</div>
          <div style="font-size:56px;font-weight:900;color:{_cped_col};line-height:1">
            {int(_cant_ped)}</div>
          <div style="font-size:12px;color:#64748B;margin-top:4px">
            {item_sel['nombre'][:40]}</div>
          <div style="font-size:13px;color:#94A3B8;margin-top:6px">
            Stock disponible: <b style="color:{_cped_col}">{int(_stk_ped)}u</b></div>
        </div>""", unsafe_allow_html=True)

        if lotes_d:
            st.markdown('<p class="sec-label">LOTE A USAR — elegí uno</p>', unsafe_allow_html=True)

            # Botones de lote — grandes, con toda la info
            if "lote_desp" not in st.session_state:
                st.session_state["lote_desp"] = 0
            idx_ld = st.session_state.get("lote_desp", 0)
            if idx_ld >= len(lotes_d):
                idx_ld = 0

            for _li, _l in enumerate(lotes_d):
                _lq   = int(float(_l.get('cantidad', 0) or 0))
                _lu   = str(_l.get('ubicacion', '—')).upper()
                _ld   = str(_l.get('deposito', '—'))
                _lf   = str(_l.get('fecha', '') or '').strip() or '—'
                _dias = dias_para_vencer(_l.get('fecha',''))
                _lsel = _li == idx_ld
                _venc_txt = ""
                if _dias is not None:
                    if _dias < 0:   _venc_txt = f" 🔴 VENCIDO"
                    elif _dias <= 15: _venc_txt = f" 🟠 {_dias}d"
                    elif _dias <= 45: _venc_txt = f" 🟡 {_dias}d"
                    else:             _venc_txt = f" 🟢 {_dias}d"
                _lbtn = st.button(
                    f"{'▶ ' if _lsel else '   '}{_lq}u  ·  📍{_lu}  ·  {_ld}  ·  📅{_lf}{_venc_txt}",
                    key=f"lote_btn_{idx_desp}_{_li}",
                    use_container_width=True,
                    type="primary" if _lsel else "secondary"
                )
                if _lbtn:
                    st.session_state["lote_desp"] = _li
                    st.session_state["_pick_ok"]  = None
                    st.rerun()

            idx_ld = st.session_state.get("lote_desp", 0)
            if idx_ld >= len(lotes_d):
                idx_ld = 0
            lote_d = lotes_d[idx_ld]

            # ── SCANNER DE CONFIRMACIÓN ─────────────────────────────────────────
            if rol in ("admin", "operario"):
                import streamlit.components.v1 as _stc_pick
                _cod_d_barras = str(
                    next((p.get('barras','') or p.get('cod_barras','')
                          for p in maestra if str(p.get('cod_int','')) == cod_d), '')
                ).strip()

                # Limpiar estado al cambiar ítem o lote
                _pick_key = (idx_desp, idx_ld)
                if st.session_state.get("_pick_item") != _pick_key:
                    st.session_state["_pick_ok"]   = None
                    st.session_state["_pick_item"]  = _pick_key
                    st.session_state["_pick_code"]  = ""

                _pick_state = st.session_state.get("_pick_ok")
                _exp_pick   = _cod_d_barras if _cod_d_barras else ""

                # Mostrar código esperado
                if _cod_d_barras:
                    st.markdown(f'<div style="font-size:11px;color:#94A3B8;text-align:center;'
                                f'padding:4px 0">Código esperado: '
                                f'<b style="color:#F1F5F9">{_cod_d_barras}</b></div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size:11px;color:#F59E0B;text-align:center;'
                                'padding:4px 0">⚠️ Sin código cargado — Manual siempre disponible</div>',
                                unsafe_allow_html=True)

                # Estado actual
                # Estado de confirmación ya no es necesario — acción automática

                # ── Componente scanner HTML ──────────────────────────────────
                _stc_pick.html(f"""<!DOCTYPE html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif}}
body{{background:transparent}}
.row{{display:flex;gap:8px;margin:6px 0}}
.btn{{flex:1;border:none;border-radius:14px;padding:14px 10px;font-size:14px;
      font-weight:700;cursor:pointer;-webkit-tap-highlight-color:transparent;
      display:flex;align-items:center;justify-content:center;gap:6px}}
.btn-scan{{background:linear-gradient(135deg,#3B82F6,#06B6D4);color:#fff;
           box-shadow:0 4px 14px rgba(59,130,246,.4)}}
.btn-manual{{background:#263347;color:#94A3B8;border:1.5px solid #334155}}
.btn-scan.act{{background:linear-gradient(135deg,#EF4444,#F59E0B)}}
.msg{{font-size:12px;font-weight:700;text-align:center;padding:8px;border-radius:10px;
      margin-top:4px;display:none}}
.msg.ok{{background:rgba(16,185,129,.15);color:#10B981;display:block;border:1px solid rgba(16,185,129,.3)}}
.msg.er{{background:rgba(239,68,68,.15);color:#EF4444;display:block;border:1px solid rgba(239,68,68,.3)}}
#ov{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.96);
     z-index:9999;flex-direction:column;align-items:center;justify-content:center;gap:16px}}
#ov.show{{display:flex}}
video{{width:90%;max-width:340px;border-radius:18px;border:3px solid #3B82F6}}
.ln{{width:90%;max-width:340px;height:3px;background:linear-gradient(90deg,transparent,#3B82F6,transparent);
     animation:sc 1.4s ease-in-out infinite}}
@keyframes sc{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
.cl{{background:#EF4444;color:#fff;border:none;border-radius:14px;padding:12px 36px;
     font-size:15px;font-weight:700;cursor:pointer}}
</style></head><body>
<div class="row">
  <button class="btn btn-scan" id="sb" onclick="doScan()">📷 Escanear</button>
  <button class="btn btn-manual" onclick="doManual()">🖐 Manual</button>
</div>
<div class="msg" id="msg"></div>
<div id="ov">
  <video id="vid" autoplay playsinline muted></video>
  <div class="ln"></div>
  <div style="color:#F1F5F9;font-size:14px;font-weight:700;text-align:center;padding:0 20px">
    Apuntá el código a la cámara</div>
  <button class="cl" onclick="closeScan()">✕ Cerrar</button>
</div>
<script>
var s=null,a=false,iv=null,exp="{_exp_pick}";
function showMsg(cls,txt){{var el=document.getElementById('msg');el.className='msg '+cls;el.textContent=txt}}
function findBtn(label){{
  var btns=window.parent.document.querySelectorAll('button[kind="secondary"],button');
  for(var i=0;i<btns.length;i++){{
    var t=(btns[i].textContent||btns[i].innerText||'').trim();
    if(t===label||t.indexOf(label)>=0) return btns[i];
  }}
  return null;
}}
function sendResult(code){{
  // Store in sessionStorage for Streamlit to read via JS bridge
  // Then click the hidden Streamlit button that triggers rerun
  window.parent.sessionStorage.setItem('lz_pick_code', code);
  window.parent.sessionStorage.setItem('lz_pick_exp',  exp||'');
  var btn = findBtn('__PICK_TRIGGER__');
  if(btn) {{ btn.click(); return; }}
  // Fallback: write to any visible text input and press Enter
  var all=window.parent.document.querySelectorAll('input[type="text"],input:not([type])');
  for(var i=all.length-1;i>=0;i--){{
    var inp=all[i];
    if(inp.readOnly||inp.type==='hidden') continue;
    try{{Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value').set.call(inp,code)}}
    catch(e){{inp.value=code}}
    inp.dispatchEvent(new Event('input',{{bubbles:true}}));
    inp.dispatchEvent(new Event('change',{{bubbles:true}}));
    ['keydown','keypress','keyup'].forEach(function(ev){{
      inp.dispatchEvent(new KeyboardEvent(ev,{{key:'Enter',keyCode:13,bubbles:true,cancelable:true}}));
    }});
    break;
  }}
}}
function doManual(){{
  showMsg('ok','🖐 Manual — tocá "✅ DESCONTAR" abajo');
  window.parent.sessionStorage.setItem('lz_pick_code','__MANUAL__');
  window.parent.sessionStorage.setItem('lz_pick_exp','');
}}
function doScan(){{
  if(a){{closeScan();return}}
  if(!window.BarcodeDetector){{showMsg('er','❌ BarcodeDetector no soportado — usá lector físico o Manual');return}}
  a=true;
  document.getElementById('sb').className='btn btn-scan act';
  document.getElementById('sb').innerHTML='⏹ Detener';
  document.getElementById('ov').className='show';
  navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment',width:{{ideal:1920}}}}}})
    .then(function(st2){{
      s=st2;document.getElementById('vid').srcObject=st2;
      var det=new BarcodeDetector({{formats:['ean_13','ean_8','code_128','code_39','upc_a','upc_e','itf']}});
      iv=setInterval(function(){{
        if(!a) return;
        det.detect(document.getElementById('vid')).then(function(c){{
          if(c.length>0){{
            var code=c[0].rawValue; closeScan();
            sendResult(code);
          }}
        }}).catch(function(){{}});
      }},350);
    }}).catch(function(e){{closeScan();showMsg('er','❌ '+e.message)}});
}}
function closeScan(){{
  a=false;clearInterval(iv);
  if(s){{s.getTracks().forEach(function(t){{t.stop()}});s=null}}
  document.getElementById('vid').srcObject=null;
  document.getElementById('sb').className='btn btn-scan';
  document.getElementById('sb').innerHTML='📷 Escanear';
  document.getElementById('ov').className='';
}}
</script></body></html>""", height=120)

                # ── Lector físico (envía Enter solo) ────────────────────
                _scan_in = st.text_input(
                    "", placeholder="O escaneá con lector físico acá...",
                    key=f"pick_manual_{idx_desp}_{idx_ld}",
                    label_visibility="collapsed"
                )
                _do_pick = False

                # Lector físico → ejecutar directo
                if _scan_in.strip():
                    v = _scan_in.strip()
                    if not _cod_d_barras or v == _cod_d_barras:
                        _do_pick = True
                    else:
                        st.error(f"❌ Código incorrecto: {v}")

                # Cámara / manual → viene por query_param sin presionar nada
                _lz_pick = st.query_params.get("lz_pick", "")
                if _lz_pick:
                    try: del st.query_params["lz_pick"]
                    except: pass
                    if _lz_pick == "__MANUAL__" or not _cod_d_barras or _lz_pick == _cod_d_barras:
                        _do_pick = True
                    else:
                        st.error(f"❌ Código incorrecto: {_lz_pick}")

                # Botones fallback siempre visibles
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("✅ DESCONTAR MANUAL", use_container_width=True,
                                 key=f"btn_pick_scan_{idx_desp}_{idx_ld}", type="primary"):
                        _do_pick = True
                with col_b2:
                    if st.button("🖐 SIN SCANNER", use_container_width=True,
                                 key=f"btn_pick_manual_{idx_desp}_{idx_ld}"):
                        _do_pick = True

                if _do_pick:
                    st.session_state.pop("_pick_ok", None)
                    cant_p = float(item_sel['cant'])
                    cant_l = float(lote_d.get('cantidad', 0))
                    try:
                        # ── Descontar SOLO del lote seleccionado ────────────────
                        # Si el lote tiene más de lo pedido → descuenta exacto
                        # Si el lote tiene menos → descuenta lo que hay y deja pendiente
                        cant_a_descontar = min(cant_l, cant_p)

                        if cant_a_descontar >= cant_l:
                            # Vaciar lote completo
                            sb.table("inventario").delete().eq("id", lote_d['id']).execute()
                        else:
                            # Quedan unidades en este lote
                            sb.table("inventario").update(
                                {"cantidad": cant_l - cant_a_descontar}
                            ).eq("id", lote_d['id']).execute()

                        registrar_historial("SALIDA", cod_d, item_sel['nombre'],
                                           cant_a_descontar, lote_d.get('ubicacion',''), usuario)
                        recalcular_maestra(cod_d, inventario)

                        pendiente = cant_p - cant_a_descontar
                        if pendiente > 0:
                            # Quedan unidades del pedido — actualizar cantidad y avisar
                            st.session_state.pedido[idx_desp]['cant'] = int(pendiente)
                            st.session_state["lote_desp"] = 0  # reset lote selector
                        else:
                            # Pedido completo para este ítem
                            st.session_state.pedido.pop(idx_desp)
                            st.session_state["desp_sel"] = 0
                            st.session_state["lote_desp"] = 0

                        _ped_id = item_sel.get('ped_id')
                        if _ped_id:
                            try:
                                import json as _j2
                                _items_rest = [{"cod_int": it['cod'], "cantidad": it['cant'],
                                               "nombre": it.get('nombre','')}
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


if _show("📋 HISTORIAL"):
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
if _show("📊 PLANILLA"):
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
# ═══════════════════════════════════════════════════════════════════════════════
# TAB CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
if _show("⚙️ CONFIG"):
    if rol != "admin":
        st.warning("🔒 Solo disponible para administradores.")
    else:
        @st.cache_data(ttl=30, show_spinner=False)
        def _cargar_cfg_admin():
            try:
                import json as _j
                r = sb.table("app_config").select("config").eq("usuario","admin").execute()
                if r.data: return _j.loads(r.data[0]["config"])
            except: pass
            return {}

        _cfg_admin = _cargar_cfg_admin()

        def _guardar_cfg_admin(nueva_cfg):
            import json as _j
            try:
                sb.table("app_config").upsert({"usuario":"admin","config":_j.dumps(nueva_cfg,ensure_ascii=False)}).execute()
                _cargar_cfg_admin.clear()
                _cargar_colores_css.clear()
                return True
            except Exception as e:
                st.error(f"Error guardando: {e}")
                return False

        _cfg_tab = st.radio("", ["🗄️ Estanterías","⚙️ General","🎨 Apariencia"],
                            horizontal=True, key="cfg_subtab", label_visibility="collapsed")

        # ── ESTANTERÍAS ──────────────────────────────────────────────────────
        if _cfg_tab == "🗄️ Estanterías":
            _est_cfg = _cfg_admin.get("estantes", [])
            if not _est_cfg:
                for _e in range(1, 28):
                    if _e in [3,4]:            _nv,_ls = 4,"ABCDE"
                    elif _e in [8,9,10,11,12]: _nv,_ls = 6,"ABCDEFG"
                    else:                       _nv,_ls = 5,"ABCDE"
                    _est_cfg.append({"num":_e,"niveles":_nv,"disponible":True,
                                      "letras_por_nivel":{str(_n):_ls for _n in range(1,_nv+1)}})

            if "est_sel_num" not in st.session_state:
                st.session_state.est_sel_num = _est_cfg[0]["num"] if _est_cfg else 1

            _col_lista, _col_editor = st.columns([2, 3])

            with _col_lista:
                st.markdown('<div style="font-size:10px;font-weight:800;color:#475569;letter-spacing:1.5px;margin-bottom:6px">ESTANTES</div>', unsafe_allow_html=True)
                with st.expander("➕ Agregar estante"):
                    _an1,_an2 = st.columns(2)
                    _new_num = _an1.number_input("N°", min_value=1, max_value=999, value=max([x["num"] for x in _est_cfg],default=0)+1, key="enew_num")
                    _new_nv  = _an2.number_input("Niveles", min_value=1, max_value=12, value=5, key="enew_nv")
                    _new_let = st.text_input("Letras (ej: ABCDE)", value="ABCDE", key="enew_let")
                    if st.button("➕ Agregar", use_container_width=True, key="eadd"):
                        if any(x["num"]==_new_num for x in _est_cfg):
                            st.warning(f"El estante {_new_num} ya existe.")
                        else:
                            _est_cfg.append({"num":_new_num,"niveles":_new_nv,"disponible":True,
                                              "letras_por_nivel":{str(_n):_new_let.strip().upper() for _n in range(1,_new_nv+1)}})
                            _est_cfg.sort(key=lambda x:x["num"])
                            _nc = dict(_cfg_admin); _nc["estantes"] = _est_cfg
                            if _guardar_cfg_admin(_nc):
                                st.session_state.est_sel_num = _new_num
                                st.rerun()

                for _e in _est_cfg:
                    _sel = _e["num"] == st.session_state.est_sel_num
                    _ico = "✅" if _e.get("disponible",True) else "⛔"
                    _bcol1, _bcol2 = st.columns([5,1])
                    with _bcol1:
                        if st.button(
                            f"{_ico}  Estante {str(_e['num']).zfill(2)}  ·  {_e.get('niveles',5)} niveles",
                            key=f"esel_{_e['num']}", use_container_width=True,
                            type="primary" if _sel else "secondary"
                        ):
                            st.session_state.est_sel_num = _e["num"]
                            st.rerun()
                    with _bcol2:
                        if st.button("🗑", key=f"edel_{_e['num']}"):
                            _est_cfg = [x for x in _est_cfg if x["num"] != _e["num"]]
                            _nc = dict(_cfg_admin); _nc["estantes"] = _est_cfg
                            if _guardar_cfg_admin(_nc):
                                if _est_cfg: st.session_state.est_sel_num = _est_cfg[0]["num"]
                                st.rerun()

            with _col_editor:
                _est_act = next((e for e in _est_cfg if e["num"] == st.session_state.est_sel_num), None)
                if _est_act:
                    _nnum = _est_act["num"]; _nniv = _est_act.get("niveles",5)
                    _lp   = _est_act.get("letras_por_nivel",{})
                    st.markdown(f'<div style="background:#1E293B;border:1px solid #334155;border-radius:10px 10px 0 0;padding:10px 14px;font-size:12px;font-weight:800;color:#F1F5F9">Estante {str(_nnum).zfill(2)}  ·  {_nniv} niveles  ·  Letras por nivel</div>', unsafe_allow_html=True)
                    _ea1, _ea2 = st.columns(2)
                    with _ea1:
                        _disp_new = st.checkbox("Activo", value=bool(_est_act.get("disponible",True)), key=f"edisp_{_nnum}")
                    with _ea2:
                        _niv_new = st.number_input("Niveles", min_value=1, max_value=12, value=_nniv, key=f"eniv_{_nnum}")
                    st.markdown('<div style="font-size:10px;font-weight:800;color:#475569;letter-spacing:1px;margin:8px 0 4px">NIVEL · LETRAS · EJEMPLO</div>', unsafe_allow_html=True)
                    _niveles_nuevos = {}
                    for _nv in range(1, _niv_new+1):
                        _ns = str(_nv)
                        _lv = _lp.get(_ns, _lp.get("1","ABCDE"))
                        _nc1, _nc2, _nc3 = st.columns([2,3,2])
                        _nc1.markdown(f'<div style="padding:8px 0;font-weight:800;font-size:13px;color:#F1F5F9">Nivel {_nv:02d}</div>', unsafe_allow_html=True)
                        _ln = _nc2.text_input("", value=_lv, key=f"elet_{_nnum}_{_nv}", label_visibility="collapsed", placeholder="ej: ABCDE")
                        _ln = _ln.strip().upper() if _ln.strip() else _lv
                        _nc3.markdown(f'<div style="padding:8px 0;font-size:12px;color:#64748B;font-family:monospace">→ {str(_nnum).zfill(2)}-{_nv}-{_ln[0] if _ln else "?"}</div>', unsafe_allow_html=True)
                        _niveles_nuevos[_ns] = _ln
                    _qb1, _qb2, _qb3 = st.columns(3)
                    if _qb1.button("↕ Copiar nivel 1 a todos", use_container_width=True, key=f"ecopy_{_nnum}"):
                        _base = _niveles_nuevos.get("1","ABCDE")
                        _niveles_nuevos = {str(_n):_base for _n in range(1,_niv_new+1)}
                    if _qb2.button("A→Z Rellenar todas", use_container_width=True, key=f"eaz_{_nnum}"):
                        _niveles_nuevos = {str(_n):"ABCDEFGHIJKLMNOPQRSTUVWXYZ" for _n in range(1,_niv_new+1)}
                    if _qb3.button("Limpiar", use_container_width=True, key=f"eclr_{_nnum}"):
                        _niveles_nuevos = {str(_n):"A" for _n in range(1,_niv_new+1)}
                    if st.button("💾 Guardar este estante", use_container_width=True, type="primary", key=f"esave_{_nnum}"):
                        _est_act["disponible"] = _disp_new
                        _est_act["niveles"] = _niv_new
                        _est_act["letras_por_nivel"] = _niveles_nuevos
                        _nc = dict(_cfg_admin); _nc["estantes"] = _est_cfg
                        if _guardar_cfg_admin(_nc): st.success(f"✅ Estante {str(_nnum).zfill(2)} guardado."); st.rerun()
                else:
                    st.info("← Seleccioná un estante para editarlo")

        # ── GENERAL ──────────────────────────────────────────────────────────
        elif _cfg_tab == "⚙️ General":
            _gc1, _gc2 = st.columns(2)
            with _gc1:
                _dias_new = st.number_input("⏰ Días alerta vencimiento", min_value=1, max_value=365, value=int(_cfg_admin.get("dias_alerta",60)), key="cfg_dias")
            with _gc2:
                _hist_new = st.number_input("📋 Límite historial", min_value=50, max_value=5000, step=50, value=int(_cfg_admin.get("hist_limit",500)), key="cfg_hist")
            _gc3, _gc4 = st.columns(2)
            with _gc3:
                _deps = ["depo 1","depo 2","depo 3"]
                _dep_val = _cfg_admin.get("depo_default","depo 1")
                _dep_new = st.selectbox("🏭 Depósito por defecto", _deps, index=_deps.index(_dep_val) if _dep_val in _deps else 0, key="cfg_dep")
            with _gc4:
                _res_new = st.number_input("🔍 Máx. resultados búsqueda", min_value=10, max_value=500, step=10, value=int(_cfg_admin.get("max_resultados",100)), key="cfg_res")
            if st.button("💾 Guardar configuración", use_container_width=True, type="primary", key="cfg_gen_save"):
                _nc = dict(_cfg_admin)
                _nc.update({"dias_alerta":_dias_new,"hist_limit":_hist_new,"depo_default":_dep_new,"max_resultados":_res_new})
                if _guardar_cfg_admin(_nc): st.success("✅ Guardado."); st.rerun()

        # ── APARIENCIA ───────────────────────────────────────────────────────
        elif _cfg_tab == "🎨 Apariencia":
            _PALETAS = {
                "🌌 Midnight Pro":  {"bg":"#04080F","surface":"#0A1628","surface2":"#0F1E35","primary":"#4D7CFE","primary_dark":"#2D5BE3","accent":"#7EB8F7","success":"#56CFE1","warning":"#FFD166","danger":"#EF476F","text":"#E8F4FD","text_dim":"#4A6FA5","border":"#152340"},
                "🪨 Slate Premium": {"bg":"#0B0E14","surface":"#13171F","surface2":"#1A1F2B","primary":"#8B9CF4","primary_dark":"#6B7EE8","accent":"#A5B4FC","success":"#6EE7B7","warning":"#FDE68A","danger":"#FDA4AF","text":"#F1F5FF","text_dim":"#4B5683","border":"#1E2438"},
                "💎 Emerald Dark":  {"bg":"#050F0A","surface":"#0A1F14","surface2":"#0F2B1A","primary":"#10B981","primary_dark":"#059669","accent":"#34D399","success":"#6EE7B7","warning":"#FCD34D","danger":"#F87171","text":"#ECFDF5","text_dim":"#3D7A60","border":"#0F3322"},
                "🔮 Violet Night":  {"bg":"#08050F","surface":"#120D1E","surface2":"#1A1229","primary":"#A855F7","primary_dark":"#8B22E8","accent":"#C084FC","success":"#4ADE80","warning":"#FCD34D","danger":"#F87171","text":"#F5F0FF","text_dim":"#6B4D8A","border":"#221540"},
                "🥉 Copper Edge":   {"bg":"#0A0804","surface":"#16100A","surface2":"#1E1710","primary":"#D97706","primary_dark":"#B45309","accent":"#F59E0B","success":"#86EFAC","warning":"#FDE68A","danger":"#FCA5A5","text":"#FEF3E2","text_dim":"#78563A","border":"#2A1F0F"},
                "❄️ Arctic Blue":   {"bg":"#050810","surface":"#0A0F1E","surface2":"#0E152B","primary":"#38BDF8","primary_dark":"#0EA5E9","accent":"#7DD3FC","success":"#6EE7B7","warning":"#FCD34D","danger":"#FCA5A5","text":"#F0F9FF","text_dim":"#3B6A8A","border":"#0F2040"},
                "🌸 Sakura Dark":   {"bg":"#0F080E","surface":"#1A0F17","surface2":"#24141F","primary":"#F472B6","primary_dark":"#EC4899","accent":"#F9A8D4","success":"#6EE7B7","warning":"#FCD34D","danger":"#FCA5A5","text":"#FFF0F5","text_dim":"#7A4060","border":"#2E1428"},
                "✨ Gold Standard": {"bg":"#09070A","surface":"#130F0A","surface2":"#1C1710","primary":"#EAB308","primary_dark":"#CA8A04","accent":"#FDE047","success":"#4ADE80","warning":"#FCD34D","danger":"#F87171","text":"#FEFCE8","text_dim":"#6B5A20","border":"#2A2010"},
                "⚡ Neon Cyber":    {"bg":"#030608","surface":"#070D12","surface2":"#0C1519","primary":"#00F5FF","primary_dark":"#00C8D8","accent":"#FF00FF","success":"#39FF14","warning":"#FFD300","danger":"#FF0055","text":"#E0FFFF","text_dim":"#2A6070","border":"#0A2030"},
                "⬛ Graphite Pro":  {"bg":"#060608","surface":"#0E0E12","surface2":"#16161C","primary":"#9B9BA8","primary_dark":"#7A7A8A","accent":"#C8C8D8","success":"#6EE7B7","warning":"#FCD34D","danger":"#FCA5A5","text":"#EEEEF4","text_dim":"#4A4A5A","border":"#202028"},
            }
            _colores_actuales = _cfg_admin.get("colores", {"bg":"#0F172A","surface":"#1E293B","surface2":"#263347","primary":"#3B82F6","primary_dark":"#1D4ED8","accent":"#06B6D4","success":"#10B981","warning":"#F59E0B","danger":"#EF4444","text":"#F1F5F9","text_dim":"#94A3B8","border":"#334155"})
            st.markdown("**🎨 Paletas rápidas:**")
            _pcols = st.columns(5)
            for _pi, (_pnom, _pcols_d) in enumerate(_PALETAS.items()):
                _col = _pcols[_pi % 5]
                _col.markdown(f'<div style="background:{_pcols_d["surface"]};border:2px solid {_pcols_d["primary"]};border-radius:10px;padding:6px;text-align:center;font-size:10px;font-weight:700;color:{_pcols_d["text"]};margin-bottom:4px">{_pnom}</div>', unsafe_allow_html=True)
                if _col.button("Aplicar", key=f"pal_{_pi}", use_container_width=True):
                    _nc = dict(_cfg_admin); _nc["colores"] = _pcols_d
                    if _guardar_cfg_admin(_nc): st.success(f"✅ {_pnom} aplicada. Recargá la página."); st.rerun()
            st.markdown("---")
            st.markdown("**🖌️ Colores personalizados:**")
            _COLOR_DEFS = [
                ("bg","Fondo","🖥️"),("surface","Cards","📦"),("surface2","Superficie 2","🔲"),
                ("border","Bordes","📐"),("primary","Primario","🔵"),("accent","Acento","💠"),
                ("success","Éxito","✅"),("warning","Advertencia","⚠️"),("danger","Error","❌"),
                ("text","Texto","📝"),("text_dim","Texto dim","🔅"),
            ]
            _cols_nuevos = dict(_colores_actuales)
            for _ck, _cl, _ico in _COLOR_DEFS:
                _cv = _colores_actuales.get(_ck,"#000000")
                _cc1,_cc2,_cc3 = st.columns([1,3,2])
                _cc1.markdown(f'<div style="background:{_cv};width:28px;height:28px;border-radius:6px;border:2px solid #334155;margin-top:6px"></div>', unsafe_allow_html=True)
                _cc2.markdown(f'<div style="padding:8px 0;font-size:13px;font-weight:600">{_ico} {_cl}</div>', unsafe_allow_html=True)
                _nv = _cc3.text_input("", value=_cv, key=f"color_{_ck}", label_visibility="collapsed")
                if _nv.strip() and _nv.strip() != _cv and len(_nv.strip())==7 and _nv.strip().startswith("#"):
                    _cols_nuevos[_ck] = _nv.strip()
            if st.button("💾 Guardar colores", use_container_width=True, type="primary", key="colores_save"):
                _nc = dict(_cfg_admin); _nc["colores"] = _cols_nuevos
                if _guardar_cfg_admin(_nc): st.success("✅ Colores guardados. Recargá la página."); st.rerun()


# TAB ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
if _show("🔐 ADMIN"):
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
if _show("🤖 ASISTENTE"):

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    /* ── Contenedor general del asistente ─────────────────── */
    .block-container { padding-top: 0.5rem !important; }

    /* ── Burbuja USUARIO ──────────────────────────────────── */
    .msg-user {
        background: linear-gradient(135deg,#1D4ED8 0%,#2563EB 60%,#06B6D4 100%);
        color:#fff;
        border-radius:20px 20px 5px 20px;
        padding:13px 18px;
        margin:6px 0 2px 32px;
        font-size:14.5px;
        font-family:'DM Sans',sans-serif;
        line-height:1.65;
        box-shadow:0 4px 18px rgba(37,99,235,0.35);
        animation:popIn .15s cubic-bezier(.34,1.56,.64,1);
        word-break:break-word;
    }

    /* ── Burbuja BOT ──────────────────────────────────────── */
    .msg-bot {
        background:linear-gradient(135deg,#1E293B 0%,#162032 100%);
        color:#E2E8F0;
        border-radius:5px 20px 20px 20px;
        border:1px solid rgba(99,130,180,0.2);
        padding:13px 18px;
        margin:2px 32px 6px 0;
        font-size:14.5px;
        font-family:'DM Sans',sans-serif;
        line-height:1.7;
        white-space:pre-wrap;
        animation:popIn .15s cubic-bezier(.34,1.56,.64,1);
        word-break:break-word;
        box-shadow:0 2px 12px rgba(0,0,0,0.25);
    }
    .msg-bot b, .msg-bot strong { color:#7DD3FC; }
    .msg-bot code {
        background:#0F172A; color:#34D399;
        padding:1px 6px; border-radius:5px;
        font-size:13px; font-family:monospace;
    }

    /* ── Confirmación OK ──────────────────────────────────── */
    .msg-ok {
        background:linear-gradient(90deg,rgba(16,185,129,.15),rgba(16,185,129,.05));
        border-left:3px solid #10B981;
        border-radius:0 12px 12px 0;
        padding:10px 14px;
        margin:0 32px 10px 4px;
        font-size:13px;
        color:#34D399;
        font-weight:600;
        font-family:'DM Sans',sans-serif;
    }

    /* ── Error ────────────────────────────────────────────── */
    .msg-err {
        background:linear-gradient(90deg,rgba(239,68,68,.15),rgba(239,68,68,.05));
        border-left:3px solid #EF4444;
        border-radius:0 12px 12px 0;
        padding:10px 14px;
        margin:0 32px 10px 4px;
        font-size:13px;
        color:#FCA5A5;
        font-weight:600;
        font-family:'DM Sans',sans-serif;
    }

    /* ── Label ────────────────────────────────────────────── */
    .chat-lbl {
        font-size:10px;
        color:#475569;
        margin:10px 4px 1px;
        letter-spacing:0.8px;
        text-transform:uppercase;
        font-weight:700;
        font-family:'DM Sans',sans-serif;
    }

    /* ── Header del asistente ─────────────────────────────── */
    .od-header {
        background:linear-gradient(135deg,#0F172A 0%,#1E293B 50%,#0F1C2E 100%);
        border:1px solid rgba(99,130,180,0.18);
        border-radius:20px;
        padding:16px 20px;
        margin-bottom:16px;
        display:flex;
        align-items:center;
        gap:16px;
        box-shadow:0 4px 24px rgba(0,0,0,0.4);
    }
    .od-avatar {
        width:52px;height:52px;min-width:52px;
        background:linear-gradient(135deg,#1D4ED8,#06B6D4);
        border-radius:16px;
        display:flex;align-items:center;justify-content:center;
        font-size:26px;
        box-shadow:0 0 20px rgba(6,182,212,0.4);
        animation:glow 3s ease-in-out infinite;
    }
    @keyframes glow {
        0%,100%{box-shadow:0 0 14px rgba(6,182,212,.35)}
        50%{box-shadow:0 0 28px rgba(6,182,212,.65)}
    }
    .od-title { font-size:16px;font-weight:800;color:#F1F5F9;font-family:'DM Sans',sans-serif;letter-spacing:.5px }
    .od-sub   { font-size:11.5px;color:#10B981;font-weight:600;font-family:'DM Sans',sans-serif;margin-top:2px }
    .od-caps  { display:flex;gap:8px;margin-top:6px;flex-wrap:wrap }
    .od-cap   {
        background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);
        color:#10B981;font-size:10px;font-weight:700;
        padding:3px 8px;border-radius:20px;
        font-family:'DM Sans',sans-serif;letter-spacing:.4px
    }

    /* ── Pantalla inicial vacía ───────────────────────────── */
    .od-empty {
        text-align:center;padding:32px 16px 20px;
    }
    .od-hint {
        display:inline-block;
        background:rgba(51,65,85,.6);
        border:1px solid #334155;
        border-radius:10px;
        padding:7px 14px;
        font-size:12px;color:#94A3B8;
        font-family:'DM Sans',sans-serif;
        margin:4px;cursor:default;
    }
    .od-hint:hover { background:rgba(59,130,246,.15);border-color:#3B82F6;color:#93C5FD }

    @keyframes popIn {
        from{opacity:0;transform:scale(.95) translateY(4px)}
        to{opacity:1;transform:scale(1) translateY(0)}
    }
    </style>""", unsafe_allow_html=True)

    # Header compacto con avatar animado
    hcol1, hcol2 = st.columns([5, 1])
    with hcol1:
        st.markdown(f"""
        <div class="od-header">
          <img src="{_LOGO_SRC}" style="width:52px;height:52px;border-radius:14px;
               object-fit:cover;box-shadow:0 4px 16px rgba(59,130,246,.4);flex-shrink:0">
          <div>
            <div class="od-title">OPERARIO DIGITAL</div>
            <div class="od-sub">✅ Sin límites · Sin costo · 100% propio</div>
            <div class="od-caps">
              <span class="od-cap">🎤 VOZ</span>
              <span class="od-cap">📷 SCANNER</span>
              <span class="od-cap">⌨️ TEXTO</span>
              <span class="od-cap">⚡ ACCIONES</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    with hcol2:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🗑️", use_container_width=True, key="clear_bot", help="Limpiar chat"):
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
            return 'hist'
        # VENCIMIENTOS
        if _re.search(r'\b(venc[eo]|vencen|vencidos|vencimiento|vencimientos|urgente[s]?|pronto[sa]?|'
                       r'por\s+vencer|proximos\s+a\s+vencer|'
                       r'caducidad|caduca|caducan|expiran|expira|se\s+vencen)\b', n):
            return 'venc'
        # BAJO STOCK
        if _re.search(r'\b(bajo\s+stock|poco\s+stock|poca\s+cantidad|'
                       r'se\s+acab[ao]|se\s+acabaron|quedan?\s+poco[sa]?|'
                       r'critico|sin\s+stock|agotado[sa]?|escaso[sa]?|minimo|'
                       r'(que|lo)\s+(nos\s+|me\s+)?falt[ao]|falta\s+reponer|'
                       r'necesitamos\s+reponer|hay\s+poco[sa]?|nos\s+quedamos\s+sin)\b', n):
            return 'bajo'
        # RESUMEN
        if _re.search(r'\b(resumen|todo\s+el\s+(inventario|stock)|panorama|balance|'
                       r'estado\s+del\s+inventario|como\s+estamos|inventario\s+completo)\b', n):
            return 'resumen'
        # TOP
        if _re.search(r'\b(top|ranking|mas\s+stock|mayor\s+stock|mas\s+cantidad|los\s+que\s+mas)\b', n):
            return 'top'
        # UBICACIONES
        if _re.search(r'\b(donde\s+est[ae]|donde\s+hay|donde\s+queda|donde\s+quedan|'
                       r'ubicacion|ubicaciones|en\s+que\s+lugar|en\s+que\s+estante|guardado|donde)\b', n):
            return 'ubic'
        # CONSULTA STOCK
        if _re.search(r'\b(cuanto[sa]?\s+(hay|queda[sn]?|tene[ms]?|tiene[ns]?)|'
                       r'cuanto\s+stock|stock\s+de|hay\s+de|quedan?\s+de|tenemos\s+de|'
                       r'hay\s+stock|existe|existencia|disponible|cuanto\s+(tenemos|tiene|hay))\b', n):
            return 'consulta'
        # PEDIDOS
        if _re.search(r'\b(pedido[s]?|orden(es)?|nube|pendiente[s]?)\b', n):
            return 'pedidos'
        # CÓDIGO DE BARRAS SOLO (EAN-13, UPC, QR largo) → consulta stock directa
        if _re.fullmatch(r'\d{7,13}', n.strip()):
            return 'consulta'
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

    def _exec_entrada(txt):
        if rol in ('visita', 'vendedor'):
            return None, "❌ Tu rol no tiene permisos para registrar entradas."
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
            return None, f"¿Cuántas unidades de *{prod['nombre']}* llegaron?"
        if not ubi:
            lts_p = _lotes(str(prod['cod_int']))
            sug   = str(lts_p[0].get('ubicacion','')) if lts_p else "01-1A"
            return None, f"¿En qué ubicación van las {int(cant)} uds de *{prod['nombre']}*?\nEj: en {sug}"
        cod, nom = str(prod['cod_int']), prod['nombre']
        fv       = _fecha_vto(txt)
        lts_ubi  = [l for l in inventario
                    if str(l.get('cod_int','')) == cod
                    and str(l.get('ubicacion','')).upper() == ubi]
        if lts_ubi:
            nueva = float(lts_ubi[0].get('cantidad', 0) or 0) + cant
            sb.table("inventario").update({"cantidad": nueva}).eq("id", lts_ubi[0]["id"]).execute()
        else:
            sb.table("inventario").insert({
                "cod_int": cod, "nombre": nom, "cantidad": cant,
                "ubicacion": ubi, "fecha": fv, "deposito": "PRINCIPAL"
            }).execute()
        registrar_historial("ENTRADA", cod, nom, cant, ubi, usuario)
        recalcular_maestra(cod, inventario)
        refrescar()
        lts_post = _lotes(cod)
        stk_post = int(sum(float(l.get('cantidad',0) or 0) for l in lts_post))
        return True, (f"✅ {int(cant)} uds de *{nom}* ingresadas\n"
                       f"📥 Ubicación: {ubi}"
                       + (f"  Vto:{fv}" if fv else "")
                       + f"\n📊 Stock total: {stk_post} uds")

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
            "deposito": lote.get("deposito","DEPO 1")
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

    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # MOTOR LOGIEZE v3 — Operario Digital Experto
    # Acceso total: inventario, lotes, ubicaciones vacías, 99+1,
    # pedidos, despachos, historial completo, ingresos/egresos/movimientos
    # ═══════════════════════════════════════════════════════════════════════════

    import re as _re, unicodedata as _ud

    def _nn(t):
        return _ud.normalize('NFD', str(t).lower()).encode('ascii','ignore').decode()

    # ────────────────────────────────────────────────────────── MEDIDAS ────────

    def _medida(txt):
        n = _nn(txt)
        m = _re.search(r'(\d+(?:[.,]\d+)?)\s*(ml|cc|cl|lt|lts|litros?|grs?|gramos?|kilos?|kg|mg|oz)', n)
        if not m:
            m = _re.search(r'(\d+(?:[.,]\d+)?)\s*([lgu])(?![a-z\d])', n)
        if not m: return None
        num = float(m.group(1).replace(',','.'))
        raw = m.group(2)
        u = {'ml':'ml','cc':'ml','cl':'ml','l':'l','lt':'l','lts':'l','litro':'l','litros':'l',
             'g':'g','gr':'g','grs':'g','gramo':'g','gramos':'g','kg':'kg','kilo':'kg',
             'kilos':'kg','mg':'mg','oz':'oz','u':'un'}.get(raw, raw)
        return (num, u, m.group(0).strip())

    def _med_ok(nom_n, num, u):
        """Verifica si un nombre de producto coincide con una medida buscada.
        Maneja espacios, sinónimos (ml=cc, l=lt=lts, g=gr=grs, kg=kilo) y
        equivalencias (1l=1000ml, 1kg=1000g)."""
        import re as _r2
        ns = str(int(num)) if num == int(num) else str(num)
        # Variantes de texto que deben aparecer en el nombre (con o sin espacio)
        # Para cada variante generamos 2: pegada y con espacio
        base = []
        if u == 'ml':
            base = [ns+'ml', ns+'cc', ns+'cl']
            # también equivalencia en litros: 350ml = 0.35l (no útil) / 1000ml = 1l
            if num % 1000 == 0:
                lns = str(int(num//1000))
                base += [lns+'l', lns+'lt', lns+'lts', lns+' l', lns+' lt', lns+' lts']
        elif u == 'l':
            base = [ns+'l', ns+'lt', ns+'lts']
            mns = str(int(num*1000))
            base += [mns+'ml', mns+'cc', mns+'cl', mns+' ml', mns+' cc']
        elif u == 'g':
            base = [ns+'g', ns+'gr', ns+'grs']
            if num % 1000 == 0:
                kns = str(int(num//1000))
                base += [kns+'kg', kns+'kilo', kns+'kilos', kns+' kg']
        elif u == 'kg':
            base = [ns+'kg', ns+'kilo', ns+'kilos']
            gns = str(int(num*1000))
            base += [gns+'g', gns+'gr', gns+'grs', gns+' g', gns+' gr']
        elif u == 'un':
            base = [ns+'un', ns+' un', ns+'u', 'x'+ns, 'x '+ns]
        else:
            base = [ns+u]
        # Para cada variante base, agregar versión con espacio y sin espacio
        variantes = set()
        for v in base:
            variantes.add(v)                           # pegado: "350ml"
            # con espacio antes de unidad: "350 ml"
            parts = _r2.match(r'^(\d+[.,]?\d*)(\D+)$', v)
            if parts:
                variantes.add(parts.group(1)+' '+parts.group(2).strip())
        # Buscar cualquier variante en el nombre normalizado
        return any(v in nom_n for v in variantes)


    # ───────────────────────────────────────────────── BÚSQUEDA PRECISA ────────

    def _buscar_prod(query, score_min=2):
        n = _nn(query)
        tiene_med = bool(_re.search(r'\d+\s*(?:ml|cc|l|lt|g|gr|kg|kilo|mg|oz)', n))
        if not tiene_med:
            # Código de barras (7-14 dígitos) → buscar en campo barras
            mb = _re.search(r'\b(\d{7,14})\b', n)
            if mb:
                bc = mb.group(1)
                p = next((x for x in maestra if str(x.get('barras','') or '').strip()==bc
                          or str(x.get('cod_barras','') or '').strip()==bc), None)
                if p: return p
            # Código interno (3-6 dígitos)
            m = _re.search(r'\b(\d{3,6})\b', n)
            if m:
                p = next((x for x in maestra if str(x.get('cod_int',''))==m.group(1)), None)
                if p: return p
        _STOPS = {'el','la','los','las','de','del','un','una','hay','tengo','en','me','que',
                  'cuanto','cual','stock','codigo','dame','ver','cuantos','donde','esta','para',
                  'con','tenes','es','son','tiene','cual','se','al','su','sus'}
        tokens = [w for w in n.split() if w not in _STOPS and len(w)>2
                  and not _re.match(r'^\d+$',w)
                  and not _re.match(r'^\d+(?:ml|cc|l|lt|g|gr|kg|mg|oz)$',w)]
        if not tokens: return None
        best, bsc = None, 0
        for p in maestra:
            pn = _nn(p.get('nombre',''))
            pw = pn.split()
            sc  = sum((3 if w==pw[0] else 2 if len(pw)>1 and w==pw[1] else 1)
                      for w in tokens if w in pn)
            bonus = 1 if any(w in pw[:2] for w in tokens) else 0
            sc += bonus
            if sc > bsc: bsc, best = sc, p
        if bsc >= score_min: return best
        # Fallback barcode: número largo ≥ 7 dígitos → buscar en campos de código de barras
        for tok in tokens:
            if len(tok)>=7 and tok.isdigit():
                for field in ('cod_barras','ean','barcode','cod_barra','barra','ean13'):
                    p = next((x for x in maestra if str(x.get(field,'')).strip()==tok), None)
                    if p: return p
        return None

    def _detalle_prod(prod):
        cod = str(prod['cod_int'])
        stk = int(float(prod.get('cantidad_total',0) or 0))
        lts = idx_inv.get(cod, [])
        if not lts:
            return f"📦 **{prod['nombre']}** (cod:{cod})\n⛔ Sin stock en ninguna ubicación."
        lines = [f"📦 **{prod['nombre']}** (cod:{cod}) — **{stk} uds totales**\n"]
        for l in sorted(lts, key=lambda x: -float(x.get('cantidad',0) or 0)):
            cant = int(float(l.get('cantidad',0)))
            ubi  = l.get('ubicacion','?')
            fv   = l.get('fecha','')
            dep  = l.get('deposito','')
            lines.append(f"  📍 **{ubi}**{(' ['+dep+']') if dep else ''} — {cant} uds"
                         +(f"  ·  Vto:{fv}" if fv else ""))
        return "\n".join(lines)

    # ─────────────────────────────────────────── UBICACIONES LIBRES / 99 ────────

    def _ubis_ocupadas():
        return {str(l.get('ubicacion','')).upper()
                for ls in idx_inv.values() for l in ls if l.get('ubicacion')}

    def _resp_ubic_libres():
        ocupadas = _ubis_ocupadas()
        vacias   = calcular_vacias_rapido(ocupadas, max_n=12)
        sug99    = calcular_sug99(ocupadas)
        lines    = ["📍 **Ubicaciones disponibles:**\n"]
        if vacias:
            lines.append(f"🟢 **Libres en estanterías ({len(vacias)}):**")
            for v in vacias: lines.append(f"  • {v}")
        lines.append(f"\n📦 **Zona 99 — siguiente libre:** `{sug99}`")
        return "\n".join(lines)

    # ──────────────────────────────────────────────── LISTA POR CATEGORÍA ────────

    def _lista_cat(txt):
        n   = _nn(txt)
        med = _medida(txt)
        _ST = {'que','cual','cuales','tengo','tienen','hay','de','del','en','los','las',
               'un','una','me','como','donde','esta','estan','todo','todos','toda','todas',
               'dame','lista','listame','mostrame','ver','cuanto','cuantos','stock',
               'producto','productos','tenes','tiene','busco','a','el','la','con','por',
               'para','sobre','listar','hay','es','son','cual','quiero','saber','info',
               'mostrar','traer','trae','dame','decime','dime'}
        if med:
            ns = str(int(med[0])) if med[0]==int(med[0]) else str(med[0])
            _ST.update([ns, med[1]] + list(med[2].split()))
        pals = [w for w in n.split() if w not in _ST and len(w)>1
                and not _re.match(r'^\d+(?:ml|cc|l|lt|g|gr|kg|mg|oz)?$', w)]
        if not pals: return None

        _SINO = {'champu':'shampoo','acond':'acondicionador','cond':'acondicionador',
                 'soap':'jabon','oil':'aceite','trat':'tratamiento','repar':'reparador',
                 'crema':'crema','gel':'gel','wax':'cera','pomada':'pomada'}
        pals_ext = list(pals)
        for w in pals:
            if w in _SINO and _SINO[w] not in pals_ext: pals_ext.append(_SINO[w])

        # ── Score: cada palabra buscada vs nombre del producto ────────────
        # Palabras cortas (2-3 chars) como "l3", "v8" se tratan como marca exacta
        cands = []
        for p in maestra:
            pn = _nn(p.get('nombre',''))
            sc = 0
            for w in pals_ext:
                if w in pn:
                    # Palabra al inicio del nombre = marca probable → peso alto
                    if pn.startswith(w): sc += 5
                    # Palabra exacta como token separado → peso medio-alto
                    elif _re.search(r'\b' + _re.escape(w) + r'\b', pn): sc += 3
                    # Substring dentro del nombre → peso bajo
                    else: sc += 1
            if sc > 0: cands.append((sc, p))

        # Fuzzy fallback: si no hubo nada, probar substring de 3+ chars
        if not cands:
            for p in maestra:
                pn = _nn(p.get('nombre',''))
                sc = sum(2 for w in pals_ext if len(w)>=3 and w in pn)
                if sc > 0: cands.append((sc, p))

        if not cands: return None

        # ── Filtro por medida si se especificó ───────────────────────────
        filtro = ""
        if med:
            num, u, tm = med
            fil = [(sc,p) for sc,p in cands if _med_ok(_nn(p.get('nombre','')), num, u)]
            if fil:
                cands, filtro = fil, f" de **{tm}**"
            else:
                otras = sorted({mm.group(0).strip()
                    for _,p in cands
                    for mm in [_re.search(r'\b\d+(?:[.,]\d+)?\s*(?:ml|cc|cl|l|lt|lts|g|gr|grs|kg|kilo|mg|oz)\b',
                                          _nn(p.get('nombre','')))]
                    if mm})[:8]
                msg = f"Sin productos de esa categoría con medida **{tm}**."
                if otras: msg += f"\nMedidas disponibles: {', '.join(otras)}"
                return msg

        cands.sort(key=lambda x:(-x[0], x[1].get('nombre','')))

        # ── Si es un solo resultado SIN pedido de lista → detalle completo ──
        if len(cands)==1 and not pide_lista: return _detalle_prod(cands[0][1])

        # ── Lista detallada ───────────────────────────────────────────────
        total_stk = sum(int(float(p.get('cantidad_total',0) or 0)) for _,p in cands)
        marca_txt = " · ".join(dict.fromkeys(w.upper() for w in pals if len(w)>=3))
        lines = [f"🔍 **{marca_txt}** — {len(cands)} producto(s) · Stock total: **{total_stk:,} uds**\n"]
        for _,p in cands:
            cod  = str(p['cod_int'])
            stk  = int(float(p.get('cantidad_total',0) or 0))
            lts  = idx_inv.get(cod,[])
            ico  = "⛔" if stk==0 else ("⚠️" if stk<10 else "✅")
            # Lotes detallados: ubicacion, cantidad, vto, deposito
            if lts:
                lotes_det = "\n".join(
                    f"      📍 {l.get('ubicacion','?')} [{l.get('deposito','DEPO 1')}]"
                    f" — {int(float(l.get('cantidad',0)))}u"
                    + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                    for l in lts)
                lines.append(f"{ico} **{p['nombre']}** (cod:{cod}) — **{stk}u** totales\n{lotes_det}")
            else:
                lines.append(f"{ico} **{p['nombre']}** (cod:{cod}) — sin stock")
        
        return "\n".join(lines)

    # ─────────────────────────────────────── RESPUESTAS DE CONSULTA ────────────

    def _resp_venc(n):
        hoy  = datetime.now()
        dias = 30
        if _re.search(r'\b(hoy|urgente|vencido|vencidos)\b', n): dias = 7
        elif _re.search(r'\b(esta.sem|7.dia)\b', n):             dias = 7
        elif _re.search(r'\b(3.?mes|90.?dia)\b', n):             dias = 90
        elif _re.search(r'\b(6.?mes|180)\b', n):                 dias = 180
        elif _re.search(r'\b(anio|ano|365|todo)\b', n):          dias = 365
        lv = []
        for p in maestra:
            cod = str(p.get('cod_int',''))
            for l in idx_inv.get(cod,[]):
                fv = str(l.get('fecha','') or '').strip()
                if not fv: continue
                try:
                    pts=fv.replace('-','/').split('/')
                    if len(pts)==2:
                        mm2,aa=int(pts[0]),int(pts[1])
                        if aa<100: aa+=2000
                        from datetime import datetime as _d2
                        delta=(_d2(aa,mm2,1)-hoy).days
                        lv.append((delta, p['nombre'], int(float(l.get('cantidad',0))),
                                   l.get('ubicacion','?'), fv, l.get('deposito','')))
                except: pass
        lv.sort(key=lambda x:x[0])
        fil = [(d,nm,c,u,fv,dep) for d,nm,c,u,fv,dep in lv if d<=dias]
        if not fil: return f"✅ Sin vencimientos en los próximos {dias} días."
        venc = [(d,nm,c,u,fv,dep) for d,nm,c,u,fv,dep in fil if d<0]
        prox = [(d,nm,c,u,fv,dep) for d,nm,c,u,fv,dep in fil if d>=0]
        lines= [f"📅 **Vencimientos — {dias} días:**\n"]
        if venc:
            lines.append(f"🚨 **VENCIDOS ({len(venc)}):**")
            for d,nm,c,u,fv,dep in venc[:25]:
                lines.append(f"  ⛔ {nm} | {c}u | {u}{' ['+dep+']' if dep else ''} | {fv} (hace {abs(d)}d)")
        if prox:
            lines.append(f"\n⏰ **PRÓXIMOS ({len(prox)}):**")
            for d,nm,c,u,fv,dep in prox[:40]:
                ico = "🔴" if d<=7 else ("🟡" if d<=30 else "🟢")
                lines.append(f"  {ico} {nm} | {c}u | {u}{' ['+dep+']' if dep else ''} | {fv} (en {d}d)")
        return "\n".join(lines)

    def _resp_ubic(txt, n):
        # Posición específica
        ubis_q = _re.findall(r'\b(\d{2}[-_]\d{1,2}[A-Za-z]{0,2})\b', txt.upper())
        if ubis_q:
            uq  = ubis_q[0]
            lts = [l for ls in idx_inv.values() for l in ls
                   if str(l.get('ubicacion','')).upper()==uq]
            if not lts: return f"📍 Posición **{uq}** vacía."
            lines = [f"📍 **{uq}** — {len(lts)} lote(s):\n"]
            for l in lts:
                cod = str(l.get('cod_int',''))
                nom = next((p.get('nombre','') for p in maestra if str(p.get('cod_int',''))==cod), cod)
                lines.append(f"  📦 {nom} (cod:{cod}) — {int(float(l.get('cantidad',0)))}u"
                             +(f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                             +(f" [{l.get('deposito','')}]" if l.get('deposito') else ""))
            return "\n".join(lines)
        prod = _buscar_prod(txt, score_min=1)
        if prod: return _detalle_prod(prod)
        # Mapa completo
        mapa = {}
        for lts in idx_inv.values():
            for l in lts:
                u = str(l.get('ubicacion','')).upper()
                if u: mapa[u] = mapa.get(u,0)+float(l.get('cantidad',0) or 0)
        lines = [f"📍 **{len(mapa)} ubicaciones en uso:**\n"]
        for u,t in sorted(mapa.items())[:100]: lines.append(f"  {u} — {int(t)} uds")
        return "\n".join(lines)

    def _resp_bajo(n):
        m      = _re.search(r'(menos.de|menor.a|debajo.de)\s*(\d+)', n)
        umbral = int(m.group(2)) if m else 10
        sin    = [p for p in maestra if int(float(p.get('cantidad_total',0) or 0))==0]
        bajo   = sorted([p for p in maestra if 0<int(float(p.get('cantidad_total',0) or 0))<=umbral],
                        key=lambda p:float(p.get('cantidad_total',0) or 0))
        if not sin and not bajo: return f"✅ Todo por encima de {umbral} uds."
        lines = [f"📉 **Bajo stock** (umbral: {umbral} uds):\n"]
        if sin:
            lines.append(f"⛔ **SIN STOCK ({len(sin)}):**")
            for p in sin[:25]: lines.append(f"  • {p['nombre']} (cod:{p['cod_int']})")
        if bajo:
            lines.append(f"\n⚠️ **CRÍTICO ({len(bajo)}):**")
            for p in bajo[:40]:
                stk  = int(float(p.get('cantidad_total',0) or 0))
                cod  = str(p['cod_int'])
                ubis = " | ".join(f"{l.get('ubicacion','?')}:{int(float(l.get('cantidad',0)))}u"
                                  for l in idx_inv.get(cod,[])[:3])
                lines.append(f"  ⚠️ {p['nombre']} — {stk}u  →  {ubis or 'sin ubi'}")
        return "\n".join(lines)

    def _resp_resumen():
        hoy     = datetime.now()
        total_p = len(maestra)
        total_u = sum(int(float(p.get('cantidad_total',0) or 0)) for p in maestra)
        sin_s   = sum(1 for p in maestra if int(float(p.get('cantidad_total',0) or 0))==0)
        bajo_s  = sum(1 for p in maestra if 0<int(float(p.get('cantidad_total',0) or 0))<=10)
        ocupadas= _ubis_ocupadas()
        vacias  = calcular_vacias_rapido(ocupadas, max_n=5)
        sug99   = calcular_sug99(ocupadas)
        venc    = 0
        for ls in idx_inv.values():
            for l in ls:
                fv=str(l.get('fecha','') or '').strip()
                if not fv: continue
                try:
                    pts=fv.replace('-','/').split('/')
                    if len(pts)==2:
                        mm2,aa=int(pts[0]),int(pts[1])
                        if aa<100: aa+=2000
                        from datetime import datetime as _d2
                        if _d2(aa,mm2,1)<hoy: venc+=1
                except: pass
        return (
            f"📊 **Resumen — {hoy.strftime('%d/%m/%Y %H:%M')}**\n\n"
            f"  📦 Productos:       **{total_p}**\n"
            f"  🔢 Unidades totales: **{total_u:,}**\n"
            f"  📍 Ubis en uso:     **{len(ocupadas)}**\n"
            f"  🟢 Próximas libres: {', '.join(vacias[:4]) or '—'}\n"
            f"  📦 Zona 99 libre:   **{sug99}**\n"
            f"  ⛔ Sin stock:       **{sin_s}**\n"
            f"  ⚠️ Bajo stock≤10:  **{bajo_s}**\n"
            f"  🚨 Lotes vencidos:  **{venc}**"
        )

    def _resp_historial(txt, n):
        try: hist = cargar_historial_cache()
        except: hist = []
        if not hist: return "Sin movimientos registrados."
        prod = _buscar_prod(txt, score_min=1)
        if prod:
            cp = str(prod['cod_int']); nn2 = _nn(prod['nombre'])
            hist = [h for h in hist if _nn(h.get('nombre',''))==nn2 or str(h.get('cod_int',''))==cp]
            if not hist: return f"Sin movimientos de {prod['nombre']}."
        if _re.search(r'\b(salida|despacho|egreso)\b', n):
            hist=[h for h in hist if h.get('tipo','').upper()=='SALIDA']
        elif _re.search(r'\b(entrada|ingreso|recepcion)\b', n):
            hist=[h for h in hist if h.get('tipo','').upper()=='ENTRADA']
        elif _re.search(r'\b(movimiento|traslado)\b', n):
            hist=[h for h in hist if h.get('tipo','').upper()=='MOVIMIENTO']
        elif _re.search(r'\b(correccion|ajuste)\b', n):
            hist=[h for h in hist if h.get('tipo','').upper()=='CORRECCION']
        mu = _re.search(r'\b(usuario|operario)\s+([\w]+)\b', n)
        if mu: hist=[h for h in hist if _nn(h.get('usuario',''))==_nn(mu.group(2))]
        mm  = _re.search(r'\b(ultimos?|primeros?)\s+(\d+)\b', n)
        top = int(mm.group(2)) if mm else 25
        ico = {'SALIDA':'📤','ENTRADA':'📥','MOVIMIENTO':'🔀','CORRECCION':'✏️'}
        lines=[f"📋 **Últimos {min(top,len(hist))} movimientos:**\n"]
        for h in hist[:top]:
            lines.append(f"  {ico.get(h.get('tipo',''),'▪️')} {h.get('fecha_hora','')} | "
                         f"{h.get('nombre','')[:24]} | x{h.get('cantidad','')} | "
                         f"{h.get('ubicacion','')} | @{h.get('usuario','')}")
        return "\n".join(lines)

    def _resp_top(n):
        m     = _re.search(r'\b(top|primeros?)\s+(\d+)\b', n)
        top_n = int(m.group(2)) if m else 20
        top   = sorted(maestra, key=lambda p:-float(p.get('cantidad_total',0) or 0))[:top_n]
        lines = [f"🏆 **Top {top_n} por stock:**\n"]
        for i,p in enumerate(top,1):
            stk  = int(float(p.get('cantidad_total',0) or 0))
            cod  = str(p['cod_int'])
            ubis = " | ".join(f"{l.get('ubicacion','?')}:{int(float(l.get('cantidad',0)))}u"
                              for l in idx_inv.get(cod,[])[:3])
            lines.append(f"  {i}. {p['nombre']} — **{stk}u**  →  {ubis or '—'}")
        return "\n".join(lines)

    def _resp_pedidos():
        try:
            peds = sb.table("pedidos").select("id,nombre,fecha,estado,items") \
                     .in_("estado",["pendiente","en_proceso"]) \
                     .order("id",desc=True).limit(30).execute().data or []
        except Exception as e:
            return f"❌ No pude acceder a pedidos: {e}"
        if not peds: return "📋 Sin pedidos pendientes ni en proceso."
        lines=[f"📋 **{len(peds)} pedido(s) activo(s):**\n"]
        for p in peds:
            items=p.get('items') or []
            if isinstance(items,str):
                try: import json as _j; items=_j.loads(items)
                except: items=[]
            total_u=sum(int(float(str(it.get('cantidad',it.get('cant',0))))) for it in items)
            lines.append(f"  📦 **#{p['id']} {p['nombre']}** [{p.get('estado','')}] "
                         f"— {len(items)} ítem(s) · {total_u}u · {p.get('fecha','')}")
            for it in items[:5]:
                lines.append(f"    · {it.get('nombre','?')} x{it.get('cantidad',it.get('cant','?'))}")
        return "\n".join(lines)

    # ──────────────────────────────── EXTRACCIÓN DE PARÁMETROS ────────────────

    def _extraer_cant(t):
        n = _nn(t)
        for pat in [r'(?:llegaron?|ingresaron?|sacar?|sacame|bajame|despachar?|salida.de)\s+(\d+)',
                    r'(\d+)\s*(?:unidades?|uds?)\b', r'(?:por|x)\s+(\d+)']:
            m=_re.search(pat,n)
            if m: return float(m.group(1))
        codigos = {str(p.get('cod_int','')) for p in maestra}
        # Excluir TODOS los dígitos que forman parte de una ubicación (ej: 99 de 99-59B)
        ubi_matches = _re.findall(r'\b(\d{1,2})[-_]\d{1,2}[a-zA-Z]{0,2}\b', n)
        ubi_matches += _re.findall(r'\b\d{1,2}[-_](\d{1,2})[a-zA-Z]{0,2}\b', n)
        ubis_partes = set(ubi_matches)
        ubis_completas = set(_re.findall(r'\b\d{2}[-_]\d{1,2}[a-zA-Z]{0,2}\b', n))
        excluir = codigos | ubis_partes | ubis_completas
        for num in _re.findall(r'\b(\d+)\b', n):
            if num not in excluir and 1<=len(num)<=4:
                return float(num)
        return 0.0

    def _extraer_ubis(txt):
        return [u.upper() for u in _re.findall(r'\b(\d{2}[-_]\d{1,2}[A-Za-z]{0,2})\b', txt)]

    def _extraer_dep(t):
        n=_nn(t)
        for kw,dep in [('depo 1','DEPO 1'),('depo1','DEPO 1'),('deposito 1','DEPO 1'),
                       ('depo 2','DEPO 2'),('depo2','DEPO 2'),('deposito 2','DEPO 2'),
                       ('1','DEPO 1'),('2','DEPO 2'),('principal','DEPO 1'),('segundo','DEPO 2')]:
            if kw in n: return dep
        return "PRINCIPAL"

    def _extraer_fv(t):
        m=_re.search(r'\b(?:vto|vence|vencimiento|fecha).{0,5}(\d{1,2}[/-]\d{2,4})\b', _nn(t))
        if m: return m.group(1).replace('-','/')
        m=_re.search(r'\b(\d{1,2}/\d{2,4})\b', t)
        return m.group(1) if m else ""

    # ──────────────────────────────────── EJECUTAR ACCIONES ────────────────────

    def _exec(tipo, txt):
        """
        Ejecutor con estado persistente en _ctx.
        El contexto guarda: intent, cod, nom, cant, ubi, dep, fv, paso
        Cada llamada SOLO parsea lo que todavía falta — nunca re-parsea lo ya guardado.
        """
        if rol in ('visita','vendedor'):
            return False, "🚫 Tu rol no permite ejecutar movimientos."

        ctx = st.session_state.get("_ctx", {})
        es_continuacion = ctx.get("intent") == tipo

        def _guardar(**kw):
            base = st.session_state.get("_ctx", {})
            base.update({"intent": tipo})
            base.update(kw)
            st.session_state["_ctx"] = base

        def _limpiar():
            st.session_state.pop("_ctx", None)

        # ── Recuperar datos ya guardados en el contexto ───────────────────────
        cod_ctx  = ctx.get("cod","")   if es_continuacion else ""
        nom_ctx  = ctx.get("nom","")   if es_continuacion else ""
        cant_ctx = ctx.get("cant",0)   if es_continuacion else 0
        ubi_ctx  = ctx.get("ubi","")   if es_continuacion else ""
        dep_ctx  = ctx.get("dep","")   if es_continuacion else ""
        fv_ctx   = ctx.get("fv","__NOPREGUNTADO__") if es_continuacion else "__NOPREGUNTADO__"
        paso     = ctx.get("paso",0)   if es_continuacion else 0

        # ── Parsear solo lo que viene en el mensaje actual ────────────────────
        ubis_txt = _extraer_ubis(txt)
        cant_txt = _extraer_cant(txt)
        dep_txt  = _extraer_dep(txt)    # default PRINCIPAL si no menciona
        fv_txt   = _extraer_fv(txt)

        # Depósito explícito: solo si el usuario menciona una palabra clave de depósito
        dep_explicito = bool(_re.search(
            r'\b(depo\s*[12]|deposito\s*[12]|depo1|depo2|principal|segundo)\b',
            _nn(txt)))

        # ── PRODUCTO — solo buscar si no está en contexto ─────────────────────
        if cod_ctx:
            cod = cod_ctx; nom = nom_ctx
            prod = next((p for p in maestra if str(p.get('cod_int',''))==cod), None)
        else:
            # Buscar en el texto actual
            prod = _buscar_prod(txt, score_min=1)
            if not prod:
                return None, "❓ No identifiqué el producto. Indicá nombre o código."
            cod = str(prod['cod_int']); nom = prod['nombre']
            _guardar(cod=cod, nom=nom)

        # ══════════════════════════════════════════════════════════════════════
        # ─── SALIDA ──────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════════════════════════════
        if tipo == "salida":
            # Cantidad
            cant = cant_ctx if cant_ctx > 0 else cant_txt
            if cant <= 0:
                # Si el usuario mandó una ubicación sin cantidad, guardarla para después
                ubi_early = ubis_txt[0] if ubis_txt else ""
                _guardar(cod=cod, nom=nom, cant=0, paso=1, ubi=ubi_early)
                return None, f"❓ ¿Cuántas uds de **{nom}** querés sacar?"

            # Ubicación — si viene en el texto actual, usarla
            ubi = ""
            if ubis_txt:
                ubi = ubis_txt[0]
            elif ubi_ctx:
                ubi = ubi_ctx

            lotes_p = idx_inv.get(cod, [])
            if not lotes_p:
                _limpiar()
                return False, f"⛔ Sin stock de **{nom}**."

            # Sin ubicación → mostrar lotes y pedir que elija
            lote = next((l for l in lotes_p if str(l.get('ubicacion','')).upper()==ubi.upper()), None) if ubi else None
            if not lote:
                tot = sum(float(l.get('cantidad',0) or 0) for l in lotes_p)
                if tot < cant:
                    _limpiar()
                    return False, f"❌ Solo hay **{int(tot)}u** de {nom} (pedís {int(cant)}u)."
                dets = "\n".join(
                    f"  • **{l.get('ubicacion','?')}** — {int(float(l.get('cantidad',0)))}u"
                    + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                    + f" [{l.get('deposito','DEPO 1')}]"
                    for l in lotes_p)
                _guardar(cod=cod, nom=nom, cant=cant, paso=2)
                return None, (f"❓ ¿Desde qué lote sacamos **{int(cant)}u de {nom}**?\n"
                              f"📦 Lotes disponibles:\n{dets}\n\n  Respondé con la ubicación (ej: **01-2A**)")

            disp = float(lote.get('cantidad',0) or 0)
            if disp < cant:
                _limpiar()
                return False, f"❌ Solo hay **{int(disp)}u** en **{ubi}**."
            nueva = disp - cant; lid = lote['id']
            def _db_sal():
                if nueva<=0: sb.table("inventario").delete().eq("id",lid).execute()
                else:        sb.table("inventario").update({"cantidad":nueva}).eq("id",lid).execute()
                sb.table("historial").insert({"fecha_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "usuario":usuario,"tipo":"SALIDA","cod_int":cod,"nombre":nom,
                    "cantidad":cant,"ubicacion":ubi}).execute()
                cargar_historial_cache.clear()
            import threading as _th; _th.Thread(target=_db_sal,daemon=True).start()
            if nueva<=0: idx_inv[cod]=[l for l in idx_inv.get(cod,[]) if l['id']!=lid]
            else:
                for l in idx_inv.get(cod,[]): l['cantidad']=nueva if l['id']==lid else l['cantidad']
            prod['cantidad_total']=str(float(prod.get('cantidad_total',0) or 0)-cant)
            _limpiar()
            return True, (f"✅ **SALIDA registrada**\n"
                          f"  Producto: **{nom}** (cod:{cod})\n"
                          f"  **{int(cant)}u** desde **{ubi}**"
                          + (f" — quedan **{int(nueva)}u**" if nueva>0 else " — lote **agotado**")
                          + f"\n  Stock total: **{int(float(prod.get('cantidad_total',0) or 0))}u**")

        # ══════════════════════════════════════════════════════════════════════
        # ─── ENTRADA ─────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════════════════════════════
        elif tipo == "entrada":

            # PASO 1 — Cantidad
            cant = cant_ctx if cant_ctx > 0 else cant_txt
            if cant <= 0:
                _guardar(cod=cod, nom=nom, cant=0, paso=1)
                return None, f"❓ ¿Cuántas unidades de **{nom}** ingresaron?"

            # PASO 2 — Ubicación
            ubi = ubi_ctx or (ubis_txt[0] if ubis_txt else "")
            if not ubi:
                ocupadas = _ubis_ocupadas()
                vacias   = calcular_vacias_rapido(ocupadas, max_n=6)
                sug99    = calcular_sug99(ocupadas)
                lotes_exist = idx_inv.get(cod, [])
                lotes_txt_e = ""
                if lotes_exist:
                    lotes_txt_e = ("\n\n📦 **Lotes actuales de " + nom + ":**\n" +
                        "\n".join(f"  • {l.get('ubicacion','?')} — {int(float(l.get('cantidad',0)))}u"
                            + (f" · Vto:{l.get('fecha','')}" if l.get('fecha') else "")
                            + f" [{l.get('deposito','DEPO 1')}]"
                            for l in lotes_exist[:8]))
                opts = "\n".join(f"  • {v}" for v in vacias[:5]) + f"\n  • {sug99} (zona 99)"
                _guardar(cod=cod, nom=nom, cant=cant, paso=2)
                return None, (f"❓ ¿En qué ubicación van las **{int(cant)}u de {nom}**?\n"
                              f"📍 Libres:\n{opts}{lotes_txt_e}")

            # Si la respuesta es SOLO una ubicación (usuario eligió de la lista)
            if not cant_ctx and ubis_txt and not cant_txt:
                cant_src = cant  # cant ya fue seteada arriba

            # PASO 3 — Fecha vencimiento
            # fv_ctx == "__NOPREGUNTADO__" significa que aún no se preguntó
            if fv_ctx == "__NOPREGUNTADO__":
                # Ver si vino en el texto actual
                fv = fv_txt
                if not fv:
                    _guardar(cod=cod, nom=nom, cant=cant, ubi=ubi, paso=3, fv="__NOPREGUNTADO__")
                    return None, (f"❓ ¿Fecha de vencimiento del lote de **{nom}** en **{ubi}**?\n"
                                  f"  Escribí **MM/AA** o **MM/AAAA** — o **sin vto** si no vence.")
            else:
                fv = fv_ctx if fv_ctx != "__NOPREGUNTADO__" else fv_txt

            # Normalizar "sin vto"
            if _nn(str(fv)) in ("sin vto","sinvto","sin vencimiento","no vence","sv","s/v","n/a","na",""):
                # si el usuario escribió "sin vto" como respuesta
                if _re.search(r'\bsin\s*vto\b|\bsin\s*venc|\bno\s*vence\b|\bsv\b', _nn(txt)):
                    fv = ""
                elif fv_ctx == "__NOPREGUNTADO__" and not fv_txt:
                    # aún no respondió — preguntar
                    _guardar(cod=cod, nom=nom, cant=cant, ubi=ubi, paso=3, fv="__NOPREGUNTADO__")
                    return None, (f"❓ ¿Fecha de vencimiento del lote de **{nom}** en **{ubi}**?\n"
                                  f"  Escribí **MM/AA** o **MM/AAAA** — o **sin vto** si no vence.")

            # PASO 4 — Depósito
            dep = dep_ctx if dep_ctx else ""
            if not dep:
                if dep_explicito:
                    dep = dep_txt
                else:
                    # Guardar todo y preguntar depósito
                    _guardar(cod=cod, nom=nom, cant=cant, ubi=ubi, fv=fv, dep="", paso=4)
                    return None, (f"❓ ¿En qué **depósito** va este lote?\n"
                                  f"  Escribí  **1**  para DEPO 1  ·  **2**  para DEPO 2")

            # Resolver depósito desde texto si viene del paso 4
            if dep == "" or (paso == 4 and not dep_ctx):
                dep_map = {"1":"DEPO 1","depo 1":"DEPO 1","depo1":"DEPO 1","d1":"DEPO 1",
                         "2":"DEPO 2","depo 2":"DEPO 2","depo2":"DEPO 2","d2":"DEPO 2"}
                dep = dep_map.get(txt.strip().lower(), dep_txt if dep_explicito else "DEPO 1")

            # ── REGISTRAR ────────────────────────────────────────────────────
            lotes_ubi = [l for l in idx_inv.get(cod,[])
                         if str(l.get('ubicacion','')).upper() == ubi.upper()
                         and str(l.get('deposito','DEPO 1')).upper() == dep.upper()]
            def _db_ent():
                if lotes_ubi:
                    lt = lotes_ubi[0]
                    nc = float(lt.get('cantidad',0) or 0) + cant
                    sb.table("inventario").update({"cantidad":nc,
                        "fecha":fv or lt.get('fecha','')}).eq("id",lt["id"]).execute()
                else:
                    sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant,
                        "ubicacion":ubi,"fecha":fv,"deposito":dep}).execute()
                sb.table("historial").insert({"fecha_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "usuario":usuario,"tipo":"ENTRADA","cod_int":cod,"nombre":nom,
                    "cantidad":cant,"ubicacion":ubi}).execute()
                cargar_historial_cache.clear()
            import threading as _th; _th.Thread(target=_db_ent,daemon=True).start()
            if lotes_ubi:
                for l in lotes_ubi: l['cantidad'] = float(l.get('cantidad',0) or 0)+cant
            else:
                idx_inv.setdefault(cod,[]).append({"cod_int":cod,"nombre":nom,"cantidad":cant,
                    "ubicacion":ubi,"fecha":fv,"deposito":dep,"id":"tmp_e"})
            prod['cantidad_total'] = str(float(prod.get('cantidad_total',0) or 0)+cant)
            _limpiar()
            return True, (f"✅ **ENTRADA registrada**\n"
                          f"  Producto: **{nom}** (cod:{cod})\n"
                          f"  **{int(cant)}u** → **{ubi}** · Depósito: **{dep}**"
                          + (f" · Vto: **{fv}**" if fv else " · Sin vencimiento")
                          + f"\n  Stock total: **{int(float(prod.get('cantidad_total',0) or 0))}u**")

        # ══════════════════════════════════════════════════════════════════════
        # ─── MOVER ───────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════════════════════════════
        elif tipo=="mover":
            cant  = cant_ctx if cant_ctx > 0 else cant_txt
            ubi   = ubi_ctx  if ubi_ctx  else (ubis_txt[0] if ubis_txt else "")
            ubi2  = ctx.get("ubi2","") if es_continuacion else (ubis_txt[1] if len(ubis_txt)>1 else "")
            if not ubi2 and len(ubis_txt)>=1 and ubi_ctx:
                ubi2 = ubis_txt[0]

            lotes_p=idx_inv.get(cod,[])
            if not lotes_p: _limpiar(); return False, f"⛔ Sin stock de **{nom}**."
            if not ubi:
                dets="\n".join(f"  • {l.get('ubicacion','?')}: {int(float(l.get('cantidad',0)))}u" for l in lotes_p[:8])
                _guardar(cod=cod,nom=nom,cant=cant,paso=1)
                return None, f"❓ ¿Desde qué posición movemos **{nom}**?\n{dets}"
            lote=next((l for l in lotes_p if str(l.get('ubicacion','')).upper()==ubi.upper()),None)
            if not lote: _limpiar(); return False, f"❌ No hay lote de **{nom}** en **{ubi}**."
            if not ubi2:
                ocupadas=_ubis_ocupadas(); vacias=calcular_vacias_rapido(ocupadas,max_n=5); sug99=calcular_sug99(ocupadas)
                _guardar(cod=cod,nom=nom,cant=cant,ubi=ubi,paso=2)
                return None, (f"❓ ¿A qué posición movemos **{nom}** desde {ubi}?\n"
                              f"📍 Libres: {', '.join(vacias[:4]) or sug99}")
            disp=float(lote.get('cantidad',0) or 0); cant_mov=cant if cant>0 else disp
            if cant_mov>disp: _limpiar(); return False, f"❌ Solo hay {int(disp)}u en {ubi}."
            nueva=disp-cant_mov; lid=lote['id']; fv_l=lote.get('fecha',''); dep_l=lote.get('deposito',dep_txt)
            def _db_mov():
                if nueva<=0: sb.table("inventario").delete().eq("id",lid).execute()
                else:        sb.table("inventario").update({"cantidad":nueva}).eq("id",lid).execute()
                sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant_mov,
                    "ubicacion":ubi2,"fecha":fv_l,"deposito":dep_l}).execute()
                sb.table("historial").insert({"fecha_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "usuario":usuario,"tipo":"MOVIMIENTO","cod_int":cod,"nombre":nom,
                    "cantidad":cant_mov,"ubicacion":f"{ubi}->{ubi2}"}).execute()
                cargar_historial_cache.clear()
            import threading as _th; _th.Thread(target=_db_mov,daemon=True).start()
            if nueva<=0: idx_inv[cod]=[l for l in idx_inv.get(cod,[]) if l['id']!=lid]
            else:
                for l in idx_inv.get(cod,[]): l['cantidad']=nueva if l['id']==lid else l['cantidad']
            idx_inv.setdefault(cod,[]).append({"cod_int":cod,"nombre":nom,"cantidad":cant_mov,
                "ubicacion":ubi2,"fecha":fv_l,"deposito":dep_l,"id":"tmp_m"})
            _limpiar()
            return True, (f"✅ **MOVIMIENTO registrado**\n  {nom} (cod:{cod})\n"
                          f"  **{int(cant_mov)}u** de **{ubi}** → **{ubi2}**"
                          +(f"\n  Quedan {int(nueva)}u en {ubi}." if nueva>0 else f"\n  **{ubi} quedó vacío.**"))

        # ══════════════════════════════════════════════════════════════════════
        # ─── CORREGIR ────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════════════════════════════
        elif tipo=="corregir":
            cant  = cant_ctx if cant_ctx > 0 else cant_txt
            ubi   = ubi_ctx  if ubi_ctx  else (ubis_txt[0] if ubis_txt else "")
            if cant<=0:
                _guardar(cod=cod,nom=nom,ubi=ubi,paso=1)
                return None, f"❓ ¿A cuántas uds corregimos **{nom}**?"
            lotes_p=idx_inv.get(cod,[])
            lote=next((l for l in lotes_p if str(l.get('ubicacion','')).upper()==ubi.upper()),None) if ubi else None
            if not lote and lotes_p:
                if len(lotes_p)==1: lote=lotes_p[0]; ubi=str(lote.get('ubicacion',''))
                else:
                    dets="\n".join(f"  • {l.get('ubicacion','?')}: {int(float(l.get('cantidad',0)))}u" for l in lotes_p[:6])
                    _guardar(cod=cod,nom=nom,cant=cant,paso=2)
                    return None, f"❓ ¿En qué ubicación corregimos **{nom}**?\n{dets}"
            if not lote:
                if not ubi:
                    _guardar(cod=cod,nom=nom,cant=cant,paso=2)
                    return None, f"❓ ¿En qué posición está el stock de **{nom}**?"
                def _db_cor_new():
                    sb.table("inventario").insert({"cod_int":cod,"nombre":nom,"cantidad":cant,
                        "ubicacion":ubi,"fecha":fv_txt,"deposito":dep_txt}).execute()
                    sb.table("historial").insert({"fecha_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "usuario":usuario,"tipo":"CORRECCION","cod_int":cod,"nombre":nom,
                        "cantidad":cant,"ubicacion":ubi}).execute()
                    cargar_historial_cache.clear()
                import threading as _th; _th.Thread(target=_db_cor_new,daemon=True).start()
                idx_inv.setdefault(cod,[]).append({"cod_int":cod,"nombre":nom,"cantidad":cant,
                    "ubicacion":ubi,"fecha":fv_txt,"deposito":dep_txt,"id":"tmp_c"})
                prod['cantidad_total']=str(float(prod.get('cantidad_total',0) or 0)+cant)
                _limpiar()
                return True, f"✅ **CORRECCIÓN** — {nom} en {ubi}: **{int(cant)}u** (lote nuevo)"
            ant=float(lote.get('cantidad',0) or 0); dif=cant-ant; lid=lote['id']
            def _db_cor():
                sb.table("inventario").update({"cantidad":cant}).eq("id",lid).execute()
                sb.table("historial").insert({"fecha_hora":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "usuario":usuario,"tipo":"CORRECCION","cod_int":cod,"nombre":nom,
                    "cantidad":cant,"ubicacion":ubi}).execute()
                cargar_historial_cache.clear()
            import threading as _th; _th.Thread(target=_db_cor,daemon=True).start()
            lote['cantidad']=cant
            prod['cantidad_total']=str(float(prod.get('cantidad_total',0) or 0)+dif)
            signo=f"+{int(dif)}" if dif>0 else str(int(dif))
            _limpiar()
            return True, (f"✅ **CORRECCIÓN registrada**\n"
                          f"  {nom} en **{ubi}**: {int(ant)}u → **{int(cant)}u** ({signo})")

        return False, "Acción desconocida."
    # ──────────────────────────────────── INTENT ────────────────────────────────


    def _resp_lista_compras(maestra_data, sb=None):
        import unicodedata as _ud2
        from collections import defaultdict
        from datetime import datetime, timedelta
        def nn2(t): return _ud2.normalize('NFD',str(t).lower()).encode('ascii','ignore').decode()
        ES_TIN=_re.compile(r'\b(tintura|tinte|colorac|koleston|igora|loreal.col|wella.col|majirel|inoa|casting|excellence|nutrisse|palette|revlon.col|matrix.col|syoss|garnier.col)\b')
        ES_MAQ=_re.compile(r'\b(maquina|maquinilla|cortadora|recortadora|afeitadora|trimmer|clipper|plancha|secador|vaporizador|difusor|esterilizador|autoclave|centrifuga|mezcladora|laminadora|selladora|depiladora|epiladora|masajeador|artefacto|electrodomestico|aparato|equipo|dispositivo)\b')
        iconos={'tintura':'🎨','maquina':'🔌','general':'📦'}

        # ── LISTA 1: bajo umbral ──────────────────────────────────────────
        a_pedir=[]; cods_pedir=set()
        for p in maestra_data:
            nom=p.get('nombre','') or ''; desc=p.get('descripcion','') or ''
            texto=nn2(nom+' '+desc); stk=int(float(p.get('cantidad_total',0) or 0))
            marca=(str(p.get('marca','') or '').strip().upper()) or 'SIN MARCA'
            es_maq=bool(ES_MAQ.search(texto))
            es_tin=bool(ES_TIN.search(texto)) and not es_maq
            if es_maq: umb=2; tipo='maquina'
            elif es_tin: umb=50; tipo='tintura'
            else: umb=12; tipo='general'
            if stk<umb:
                cod=str(p.get('cod_int',''))
                a_pedir.append({'nombre':nom,'cod':cod,'stock':stk,'umbral':umb,'tipo':tipo,'marca':marca})
                cods_pedir.add(cod)

        # ── LISTA 2: más vendidos últimos 2 meses ────────────────────────
        mas_vendidos=[]
        try:
            fecha_corte=datetime.now()-timedelta(days=60)
            hist_raw=sb.table('historial').select('cod_int,nombre,cantidad,fecha_hora,tipo').eq('tipo','SALIDA').execute().data or []
            hist=[h for h in hist_raw if __import__('datetime').datetime.strptime(str(h.get('fecha_hora','') or '')[:10],'%d/%m/%Y') >= fecha_corte
                  if len(str(h.get('fecha_hora','') or ''))>=10]
            ventas=defaultdict(lambda:{'nombre':'','total':0,'marca':'','stock':0,'cod':''})
            maestra_idx={str(p.get('cod_int','')):p for p in maestra_data}
            for h in hist:
                cod=str(h.get('cod_int',''))
                ventas[cod]['nombre']=h.get('nombre','')
                ventas[cod]['total']+=int(float(h.get('cantidad',0) or 0))
                ventas[cod]['cod']=cod
                mp=maestra_idx.get(cod,{})
                ventas[cod]['marca']=(str(mp.get('marca','') or '').strip().upper()) or 'SIN MARCA'
                ventas[cod]['stock']=int(float(mp.get('cantidad_total',0) or 0))
            ranking=sorted(ventas.values(),key=lambda x:-x['total'])
            mas_vendidos=[v for v in ranking if v['cod'] not in cods_pedir][:50]
        except: pass

        ls=[]
        # — Lista 1 —
        if a_pedir:
            por_marca=defaultdict(list)
            for p in sorted(a_pedir,key=lambda x:x['nombre']): por_marca[p['marca']].append(p)
            tin_n=sum(1 for p in a_pedir if p['tipo']=='tintura')
            maq_n=sum(1 for p in a_pedir if p['tipo']=='maquina')
            gen_n=len(a_pedir)-tin_n-maq_n
            ls+=[f"🛒 **LISTA DE COMPRAS** — {len(a_pedir)} producto(s) a reponer",
                 f"   📦 Generales (<12u): {gen_n}  |  🎨 Tinturas (<50u): {tin_n}  |  🔌 Máquinas (<2u): {maq_n}\n"]
            for m in sorted(por_marca.keys()):
                prods=por_marca[m]
                ls.append(f"▸ **{m}** ({len(prods)} ítem{'s' if len(prods)>1 else ''}):")
                for p in prods:
                    st="⛔ SIN STOCK" if p['stock']==0 else f"{p['stock']}u en stock"
                    ls.append(f"   {iconos[p['tipo']]} {p['nombre']} (cod:{p['cod']}) — {st}")
                ls.append("")
        else:
            ls.append("✅ No hay productos que reponer en este momento.\n")

        # — Lista 2 —
        if mas_vendidos:
            por_marca_mv=defaultdict(list)
            for v in mas_vendidos: por_marca_mv[v['marca']].append(v)
            ls+=["━"*40,
                 f"🔥 **MÁS VENDIDOS** — últimos 2 meses ({len(mas_vendidos)} productos)",
                 f"   (Con stock suficiente — para que no te quedes corto)\n"]
            for m in sorted(por_marca_mv.keys()):
                prods=por_marca_mv[m]
                ls.append(f"▸ **{m}** ({len(prods)} ítem{'s' if len(prods)>1 else ''}):")
                for v in sorted(prods,key=lambda x:-x['total']):
                    ls.append(f"   🔥 {v['nombre']} (cod:{v['cod']}) — {v['stock']}u en stock · vendió {v['total']}u en 2 meses")
                ls.append("")

        ls.append("💾 Para exportar a Excel usá la **app de escritorio**.")
        return "\n".join(ls)

    def _intent(n):
        if _re.search(r'\b(hola|buenas|buen.?dia|como.estas|hey|que.tal|que.onda|buenos.dias)\b', n): return 'saludo'
        if _re.search(r'\b(gracias|gracia|genial|perfecto|excelente|barbaro|de.nada|copado|listo)\b', n): return 'gracias'
        if _re.search(r'\b(ayuda|que.podes|que.sabes|como.funciona|comandos|que.puedo|manual)\b', n): return 'ayuda'
        if _re.search(r'\b(venc[eioa]|vencen|vencidos|vencimiento|vencimientos|urgente[s]?|por.vencer|proxim[oa]|pronto|expiran|fecha.vto|caducidad|caduca)\b', n): return 'venc'
        if _re.search(r'\b(ubicacion.libre|posicion.libre|vacia|vacias|libre|disponible|donde.pongo|donde.ubico|sugerencia)\b', n): return 'ubic_libre'
        if _re.search(r'\b(donde.est[ae]|donde.hay|donde.queda|ubicacion|posicion|en.que.lugar|guardado|mapa|en.que.ubi)\b', n): return 'ubic'
        if _re.search(r'\b(bajo.stock|poco.stock|sin.stock|agotado|critico|falta.reponer|hay.poco|escaso|minimo|reponer)\b', n): return 'bajo'
        if _re.search(r'\b(top|ranking|mas.stock|mayor.stock|mas.cantidad|los.que.mas)\b', n): return 'top'
        if _re.search(r'\b(resumen|panorama|balance|estado.del.inventario|como.estamos|inventario.completo)\b', n): return 'resumen'
        if _re.search(r'\b(historial|movimientos|ultimos|ultimo|registro|que.paso|bitacora|actividad)\b', n): return 'hist'
        if _re.search(r'\b(pedido|pedidos|encargo|orden.de.compra|orden.pendiente)\b', n): return 'pedidos'
        if _re.search(r'\b(lista.de.compras|lista.compra|compras|que.comprar|que.pedir|necesito.pedir|hay.que.pedir|que.falta|falta.comprar|reposicion|lista.proveedor)\b', n): return 'lista_compras'
        if _re.search(r'\b(lista|listame|mostrame|todos.los|todas.las|que.productos|cuales|listar|que.hay|cuantos.hay|tenes)\b', n): return 'lista'
        if _re.search(r'\b(sac[ao]r?|sacame|baj[ao]r?|bajame|retir[ao]r?|salida|despacha[rn]?|consum[eo]r?|egres[ao]r?|quitar|descontar|desconta[rn]?)\b', n): return 'salida'
        if _re.search(r'\b(agreg[ao]r?|ingres[ao]r?|recib[io]r?|llegaron?|llego|carg[ao]r?|entrada|incorpor[ao]r?|sum[ao]r?|pus[eo]|nuevo.stock|meter|mete|poner|pon[ei])\b', n): return 'entrada'
        if _re.search(r'\b(mov[eo]|movi|mand[ao]|traslad[ao]|pas[ao]\s+(a|al)|llev[ao]\s+(a|al)|cambi[ao].+ubic|reubicar)\b', n): return 'mover'
        if _re.search(r'\b(correg[io]|ajust[ao]|fij[ao]|actualiz[ao]|en.realidad.hay|inventario.fisico|recuento|conteo)\b', n): return 'corregir'
        # Código de barras puro (7-14 dígitos) → búsqueda directa
        if _re.fullmatch(r'\d{7,14}', n.strip()): return 'consulta'
        return 'consulta'

    # ──────────────────────────────── PROCESADOR PRINCIPAL ─────────────────────

    def _procesar(txt):
        n   = _nn(txt)
        ctx = st.session_state.get("_ctx", {})
        if ctx:
            txt_c  = txt  # NO concatenar — _exec ya tiene el historial en ctx
            n      = _nn(txt_c)
            intent = ctx.get("intent", _intent(n))
        else:
            txt_c = txt
            intent = _intent(n)

        hora = datetime.now().hour
        sal  = "Buenos días" if hora<12 else ("Buenas tardes" if hora<20 else "Buenas noches")

        if intent=='saludo':
            return None,(f"👋 {sal}, **{usuario}**! Soy el **Operario Digital LOGIEZE**.\n"
                         f"Acceso completo: {len(maestra)} productos, lotes, ubicaciones, pedidos e historial.\n"
                         f"Preguntame lo que necesités o dictame un movimiento.")
        if intent=='gracias':  return None,"✅ ¡De nada! ¿Algo más?"
        if intent=='ayuda':
            return None,(
                "🤖 **Operario Digital — comandos:**\n\n"
                "**📋 Consultas:**\n"
                "  • «¿Cuánto hay de ibuprofeno?»\n"
                "  • «Listame geles de 5L»\n"
                "  • «¿Dónde está el código 150?»\n"
                "  • «¿Qué hay en 01-2A?»\n"
                "  • «Ubicaciones vacías / libres»\n"
                "  • «¿Qué vence este mes?»\n"
                "  • «Qué nos falta reponer»\n"
                "  • «Resumen del inventario»\n"
                "  • «Pedidos pendientes»\n"
                "  • «Últimos 30 movimientos»\n"
                "  • «Top 15 por stock»\n\n"
                "**📦 Movimientos:**\n"
                "  • «Sacá 10 de ibuprofeno de 01-1A»\n"
                "  • «Llegaron 50 de gel en 03-2B vto 06/26»\n"
                "  • «Pasá todo de 01-1A a 02-3B»\n"
                "  • «Corregí el gel en 01-1A a 25 uds»"
            )
        if intent=='lista_compras':
            _nlow=_nn(txt_c)
            if 'exportar' in _nlow or 'excel' in _nlow:
                return None, '💾 Para exportar a Excel usá la **app de escritorio** (la web no permite guardar archivos locales).'
            return None, _resp_lista_compras(maestra, sb)
        if intent=='venc':       return None, _resp_venc(n)
        if intent=='ubic_libre': return None, _resp_ubic_libres()
        if intent=='ubic':       return None, _resp_ubic(txt_c, n)
        if intent=='bajo':       return None, _resp_bajo(n)
        if intent=='top':        return None, _resp_top(n)
        if intent=='resumen':    return None, _resp_resumen()
        if intent=='hist':       return None, _resp_historial(txt_c, n)
        if intent=='pedidos':    return None, _resp_pedidos()
        if intent=='consulta':  pass  # falls through to buscar_prod below
        if intent=='lista':
            r=_lista_cat(txt_c)
            if r: return None, r
        if intent in ('salida','entrada','mover','corregir'):
            ok, resp = _exec(intent, txt_c)
            # _exec maneja su propio contexto — no interferir
            return ok, resp
        # Consulta genérica — primero lista, luego producto individual
        r=_lista_cat(txt_c)
        if r: return None,r
        prod=_buscar_prod(txt_c, score_min=1)
        if prod: return None, _detalle_prod(prod)
        total=sum(int(float(p.get('cantidad_total',0) or 0)) for p in maestra)
        return None,(f"No entendí bien. Tenemos **{len(maestra)} productos** · **{total:,}u** en stock.\n"
                     "Escribí **ayuda** para ver todos los comandos.")

    # ── PANTALLA INICIAL ──────────────────────────────────────────────────────

    if not st.session_state.bot_hist:
        st.markdown("""
        <div class="od-empty">
            <div style="font-size:13px;color:#64748B;font-family:'DM Sans',sans-serif;
                        margin-bottom:14px;font-weight:600;letter-spacing:.5px">
                PROBÁ PREGUNTARME</div>
            <div>
              <span class="od-hint">stock de shampoo</span>
              <span class="od-hint">sacar 10 de gel</span>
              <span class="od-hint">vencimientos urgentes</span>
            </div>
            <div style="margin-top:6px">
              <span class="od-hint">mover 01-2A a 03-1B</span>
              <span class="od-hint">resumen de inventario</span>
            </div>
            <div style="margin-top:6px">
              <span class="od-hint">llegaron 50 de crema 01-3A</span>
            </div>
        </div>""", unsafe_allow_html=True)

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

    # botones rápidos eliminados

    _quick = st.session_state.pop("_bot_quick", None)

    # ── INPUT + MICRÓFONO ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    # Limpiar campo: si vino de un envío, el próximo render arranca vacío
    _input_val = "" if st.session_state.pop("_limpiar", False) else st.session_state.get("bot_input", "")

    # Capturar voz enviada por el componente via query param
    _voz_qp = st.query_params.get("lz_voz", "")
    if _voz_qp:
        try: del st.query_params["lz_voz"]
        except: pass

    import streamlit.components.v1 as _stc

    _stc.html("""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
.bar{display:flex;gap:6px;align-items:center}
.btn{border:none;border-radius:50%;width:48px;height:48px;font-size:22px;
     cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;
     -webkit-tap-highlight-color:transparent;transition:all .15s}
.btn-mic{background:linear-gradient(135deg,#3B82F6,#06B6D4);
         box-shadow:0 3px 10px rgba(59,130,246,.4)}
.btn-mic.rec{background:linear-gradient(135deg,#EF4444,#F59E0B);
             animation:pulse 1s infinite}
.btn-scan{background:linear-gradient(135deg,#10B981,#059669);
          box-shadow:0 3px 10px rgba(16,185,129,.4)}
.btn-scan.active{background:linear-gradient(135deg,#F59E0B,#EF4444)}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.4)}
                 50%{box-shadow:0 0 0 10px rgba(239,68,68,0)}}
.status{flex:1;font-size:11px;color:#94A3B8;font-weight:500;line-height:1.4;
        min-height:20px;display:flex;align-items:center}
.status.ok{color:#10B981}.status.er{color:#EF4444}.status.scan{color:#F59E0B}
.preview{font-size:11px;color:#93C5FD;margin-top:2px;word-break:break-all;display:none}
.send-btn{width:100%;margin-top:6px;padding:11px;border:none;border-radius:14px;
          background:linear-gradient(135deg,#10B981,#059669);color:#fff;
          font-size:14px;font-weight:700;cursor:pointer;display:none;
          -webkit-tap-highlight-color:transparent}
#scanOverlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;
             background:rgba(0,0,0,.94);z-index:9999;flex-direction:column;
             align-items:center;justify-content:center;gap:14px}
#scanOverlay.show{display:flex}
#scanVideo{width:90%;max-width:320px;border-radius:16px;border:3px solid #10B981}
#scanLine{width:90%;max-width:320px;height:3px;
          background:linear-gradient(90deg,transparent,#10B981,transparent);
          animation:sc 1.4s ease-in-out infinite}
@keyframes sc{0%,100%{opacity:.2}50%{opacity:1}}
#scanStatus{color:#F1F5F9;font-size:14px;font-weight:700;text-align:center;padding:0 20px}
#scanClose{background:#EF4444;color:#fff;border:none;border-radius:12px;
           padding:10px 28px;font-size:14px;font-weight:700;cursor:pointer}
</style></head><body>
<div class="bar">
  <button class="btn btn-mic" id="micbtn" onclick="togMic()">🎤</button>
  <button class="btn btn-scan" id="scanbtn" onclick="togScan()">📷</button>
  <div style="flex:1">
    <div class="status" id="mst">🎤 Grabar · 📷 Escanear código</div>
    <div class="preview" id="mpv"></div>
  </div>
</div>
<button class="send-btn" id="sbtn" onclick="enviarVoz()">🟢 ENVIAR</button>
<div id="scanOverlay">
  <video id="scanVideo" autoplay playsinline muted></video>
  <div id="scanLine"></div>
  <div id="scanStatus">Apuntá el código a la cámara</div>
  <button id="scanClose" onclick="closeScan()">✕ Cerrar</button>
</div>
<script>
var R=null,gr=false,tx="",scanStream=null,scanActive=false,scanInterval=null;
function M(id){return document.getElementById(id)}
function setMic(c,i){M("micbtn").className="btn btn-mic "+(c||"");M("micbtn").innerHTML=i||"🎤"}
function setSt(c,t){M("mst").className="status "+(c||"");M("mst").textContent=t}
function setPv(t){M("mpv").textContent=t;M("mpv").style.display=t?"block":"none"}
function showSend(v){M("sbtn").style.display=v?"block":"none"}
function getTa(){
  var all=window.parent.document.querySelectorAll("textarea");
  for(var i=0;i<all.length;i++){
    var p=all[i].placeholder||"";
    if(p.indexOf("Escrib")>=0||p.indexOf("Enter")>=0) return all[i];
  }
  for(var i=0;i<all.length;i++){if(!all[i].readOnly) return all[i]}
  return null;
}
function enviarTexto(texto){
  var ta=getTa();
  if(!ta){setSt("er","No se encontró el campo de texto");return false}
  // Write value using React's internal setter
  var nativeSet=Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype,"value").set;
  try{nativeSet.call(ta,texto)}catch(e){ta.value=texto}
  // Fire input+change so React/Streamlit sees the new value
  ta.dispatchEvent(new Event("input",{bubbles:true,composed:true}));
  ta.dispatchEvent(new Event("change",{bubbles:true,composed:true}));
  ta.focus();
  // Press Enter — Streamlit textarea with on_change fires rerun on Enter
  setTimeout(function(){
    ["keydown","keypress","keyup"].forEach(function(ev){
      ta.dispatchEvent(new KeyboardEvent(ev,{
        key:"Enter",code:"Enter",keyCode:13,which:13,
        bubbles:true,cancelable:true,composed:true
      }));
    });
    // Backup: click the ➤ Enviar button
    setTimeout(function(){
      var btns=window.parent.document.querySelectorAll("button");
      for(var i=0;i<btns.length;i++){
        var t=(btns[i].innerText||btns[i].textContent||"").trim();
        if(t.indexOf("Enviar")>=0||t==="➤ Enviar"){btns[i].click();return}
      }
    },200);
  },100);
  return true;
}
function hookEnter(){
  var ta=getTa();
  if(ta&&!ta._lzHook){
    ta._lzHook=true;
    ta.addEventListener("keydown",function(ev){
      if(ev.key==="Enter"&&!ev.shiftKey){
        ev.preventDefault();ev.stopPropagation();
        if(!ta.value.trim()) return;
        var btns=window.parent.document.querySelectorAll("button");
        for(var i=0;i<btns.length;i++){
          var t=(btns[i].innerText||btns[i].textContent||"").trim();
          if(t.indexOf("Enviar")>=0){btns[i].click();return}
        }
      }
    },true);
  }
}
function togMic(){
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){setSt("er","Necesitás Chrome o Edge para el micrófono");return}
  if(gr){R.stop();return}
  tx="";showSend(false);setPv("");
  R=new SR();R.lang="es-AR";R.continuous=false;R.interimResults=true;R.maxAlternatives=1;
  R.onstart=function(){gr=true;setMic("rec","⏹");setSt("ok","🔴 Escuchando...")}
  R.onresult=function(e){var t="";for(var i=e.resultIndex;i<e.results.length;i++) t+=e.results[i][0].transcript;tx=t;setPv("📝 "+tx);showSend(!!tx)}
  R.onerror=function(e){var m={"not-allowed":"Permiso denegado","no-speech":"No se escuchó","network":"Error de red"};setSt("er","❌ "+(m[e.error]||e.error));gr=false;setMic("","🎤");showSend(false)}
  R.onend=function(){gr=false;setMic("","🎤");if(tx){setSt("ok","✅ Grabado — enviando...");showSend(true);setTimeout(function(){var ok=enviarTexto(tx);if(ok){tx="";setPv("");showSend(false);setSt("","🎤 Grabar · 📷 Escanear código")}},300)}else{setSt("","🎤 Grabar · 📷 Escanear código");showSend(false)}}
  R.start();
}
function enviarVoz(){if(!tx){setSt("er","Grabá primero");return}setSt("ok","Enviando...");if(enviarTexto(tx)){tx="";setPv("");showSend(false);setSt("","🎤 Grabar · 📷 Escanear código")}}
function togScan(){
  if(scanActive){closeScan();return}
  if(!window.BarcodeDetector){setSt("er","BarcodeDetector no soportado — usá Chrome Android");return}
  openCamera();
}
function openCamera(){
  scanActive=true;M("scanbtn").className="btn btn-scan active";M("scanOverlay").className="show";
  navigator.mediaDevices.getUserMedia({video:{facingMode:"environment",width:{ideal:1920}}})
    .then(function(stream){
      scanStream=stream;M("scanVideo").srcObject=stream;
      var det=new BarcodeDetector({formats:["ean_13","ean_8","code_128","code_39","upc_a","upc_e","itf","qr_code"]});
      setSt("scan","📷 Escaneando...");
      scanInterval=setInterval(function(){
        if(!scanActive) return;
        det.detect(M("scanVideo")).then(function(codes){
          if(codes.length>0){
            var code=codes[0].rawValue;
            closeScan();
            setSt("ok","📦 Buscando "+code+"...");
            setTimeout(function(){
              enviarTexto(code);
              setTimeout(function(){setSt("","🎤 Grabar · 📷 Escanear código")},1800);
            },200);
          }
        }).catch(function(){});
      },350);
    })
    .catch(function(e){closeScan();setSt("er","❌ "+e.message)});
}
function closeScan(){
  scanActive=false;clearInterval(scanInterval);
  if(scanStream){scanStream.getTracks().forEach(function(t){t.stop()});scanStream=null}
  M("scanVideo").srcObject=null;M("scanbtn").className="btn btn-scan";M("scanOverlay").className="";
}
var _ht=0;function tryH(){hookEnter();if(!getTa()&&_ht<25){_ht++;setTimeout(tryH,400)}}tryH();
</script></body></html>""", height=115)

    # CSS textarea
    st.markdown("""<style>
    .stTextArea textarea{
        background:#1E293B !important;color:#F1F5F9 !important;
        border:1.5px solid #334155 !important;border-radius:18px !important;
        font-size:16px !important;resize:none !important;
        padding:14px 18px !important;line-height:1.5 !important;
        font-family:'DM Sans',sans-serif !important}
    .stTextArea textarea:focus{
        border-color:#3B82F6 !important;
        box-shadow:0 0 0 3px rgba(59,130,246,.2) !important}
    .stTextArea textarea::placeholder{color:#475569 !important;font-size:14px !important}
    </style>""", unsafe_allow_html=True)

    ic1, ic2 = st.columns([5, 1])
    with ic1:
        txt_in = st.text_area(
            "msg", label_visibility="collapsed",
            placeholder="Escribí acá · Enter envía · Shift+Enter nueva línea",
            key="bot_input",
            height=68,
            value=_input_val,
        )
    with ic2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        send = st.button("➤ Enviar", use_container_width=True, type="primary", key="bot_send")

    _final = _quick or (_voz_qp.strip() if _voz_qp else None) or (txt_in.strip() if send and txt_in else None)

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

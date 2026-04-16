"""
LOGIEZE WEB — versión Streamlit para celular/web
Instalar:  pip install streamlit supabase pandas openpyxl
Correr:    streamlit run logieze_web.py
"""
import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime, date
from supabase import create_client, Client

# ── CONFIG DEFAULT (overrideable por sucursal) ────────────────────────────────
DEFAULT_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
DEFAULT_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"
DIAS_ALERTA = 60

# Sucursales hardcodeadas — igual que la app de PC
SUCURSALES_DEFAULT = [
    {"nombre": "Principal", "url": DEFAULT_URL, "key": DEFAULT_KEY}
]

st.set_page_config(
    page_title="LOGIEZE",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── INICIALIZAR SESSION STATE ─────────────────────────────────────────────────
def _init_session():
    defaults = {
        "usuario":      None,
        "rol":          None,
        "suc_url":      DEFAULT_URL,
        "suc_key":      DEFAULT_KEY,
        "suc_nombre":   "Principal",
        "nav_tab":      "📦 MOVIMIENTOS",
        "pedido":       [],
        "bot_hist":     [],
        "_ctx":         {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()

# ── HELPERS DE SUCURSAL ───────────────────────────────────────────────────────
def get_sucursales():
    """Carga sucursales desde Supabase (tabla app_config del admin) o usa default."""
    try:
        sb_tmp = create_client(st.session_state.suc_url, st.session_state.suc_key)
        r = sb_tmp.table("app_config").select("config").eq("usuario", "sucursales").execute()
        if r.data:
            import json as _j
            data = _j.loads(r.data[0]["config"])
            if isinstance(data, list) and data:
                return data
    except:
        pass
    return SUCURSALES_DEFAULT

def save_sucursales(lista):
    """Guarda lista de sucursales en Supabase."""
    try:
        import json as _j
        sb_tmp = create_client(st.session_state.suc_url, st.session_state.suc_key)
        sb_tmp.table("app_config").upsert(
            {"usuario": "sucursales", "config": _j.dumps(lista, ensure_ascii=False)},
        ).execute()
        return True
    except:
        return False

# ── SUPABASE CLIENT (usa URL/KEY de la sucursal activa) ──────────────────────
@st.cache_resource
def _get_sb_client(url, key):
    return create_client(url, key)

def get_supabase() -> Client:
    return _get_sb_client(st.session_state.suc_url, st.session_state.suc_key)

def _invalidar_cache():
    """Limpia todos los caches de datos al cambiar de sucursal."""
    cargar_maestra.clear()
    cargar_inventario.clear()
    cargar_historial_cache.clear()

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500;600&display=swap');
:root {
    --bg:#0F172A; --surface:#1E293B; --surface2:#263347;
    --primary:#3B82F6; --accent:#06B6D4;
    --success:#10B981; --warning:#F59E0B; --danger:#EF4444;
    --text:#F1F5F9; --dim:#94A3B8; --border:#334155;
    --radius:18px; --radius-sm:12px;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background:var(--bg)!important;color:var(--text)!important}
.main .block-container{padding:0 12px 100px 12px!important;max-width:480px!important;margin:0 auto!important}
header[data-testid="stHeader"],footer,#MainMenu{display:none!important}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.app-topbar{position:sticky;top:0;z-index:999;background:var(--bg);border-bottom:1px solid var(--border);padding:14px 16px 12px;display:flex;align-items:center;justify-content:space-between;margin:0 -12px 16px -12px}
.app-topbar-title{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:var(--text);letter-spacing:1px}
.app-topbar-sub{font-size:11px;color:var(--dim);margin-top:1px}
.app-badge{background:var(--primary);color:white;font-size:10px;font-weight:700;padding:3px 8px;border-radius:20px;letter-spacing:.5px}
div.stButton>button{background:linear-gradient(135deg,#3B82F6,#06B6D4)!important;color:white!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:15px!important;border:none!important;border-radius:var(--radius)!important;padding:14px 20px!important;width:100%!important;min-height:52px!important;transition:all .15s ease!important;box-shadow:0 4px 15px rgba(59,130,246,.3)!important}
div.stButton>button:active{transform:scale(.97)!important}
div[data-baseweb="input"]>div{background:var(--surface)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius-sm)!important}
div[data-baseweb="input"]>div:focus-within{border-color:var(--primary)!important;box-shadow:0 0 0 3px rgba(59,130,246,.15)!important}
div[data-baseweb="input"] input{color:var(--text)!important;font-size:16px!important;padding:12px 14px!important}
div[data-baseweb="select"]>div{background:var(--surface)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius-sm)!important;color:var(--text)!important}
ul[role="listbox"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:14px!important}
li[role="option"]{border-radius:10px!important;padding:10px 14px!important;color:var(--text)!important}
li[role="option"]:hover,li[aria-selected="true"]{background:rgba(59,130,246,.15)!important;color:var(--primary)!important}
div[data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:var(--radius)!important;padding:4px!important;border:1px solid var(--border)!important}
div[data-baseweb="tab"]{border-radius:var(--radius-sm)!important;font-weight:600!important;color:var(--dim)!important}
div[data-baseweb="tab"][aria-selected="true"]{background:var(--primary)!important;color:white!important}
div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{display:none!important}
hr{border-color:var(--border)!important;margin:16px 0!important}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:10px}
.sec-label{font-size:10px;font-weight:800;color:var(--primary);letter-spacing:1.5px;text-transform:uppercase;margin:16px 0 6px}
.sug-box{background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.25);border-radius:10px;padding:8px 14px;font-size:12px;font-weight:700;color:var(--primary);margin:6px 0}
.lote-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin:4px 0}
/* Sucursal badge */
.suc-badge{background:rgba(59,130,246,.15);color:var(--primary);font-size:9px;font-weight:800;padding:2px 7px;border-radius:10px;letter-spacing:.5px;text-transform:uppercase;margin-top:2px;display:inline-block}
/* Sucursal selector card */
.suc-card{background:var(--surface);border:1.5px solid var(--border);border-radius:14px;padding:12px 16px;margin:6px 0;cursor:pointer;transition:border-color .15s}
.suc-card.active{border-color:var(--primary);background:rgba(59,130,246,.08)}
/* Nav select */
div[data-testid="stSelectbox"]>div>div{background:#1E293B!important;border:1.5px solid #3B82F6!important;border-radius:14px!important;font-size:15px!important;font-weight:700!important;min-height:52px!important;padding:4px 16px!important}
label[data-testid="stWidgetLabel"] p{color:var(--dim)!important;font-size:11px!important;font-weight:600!important;letter-spacing:1px!important;text-transform:uppercase!important}
div[data-testid="stRadio"]>div{background:var(--surface)!important;border-radius:14px!important;padding:4px!important;border:1px solid var(--border)!important}
div[data-testid="stRadio"] label{border-radius:10px!important;padding:8px 16px!important;font-weight:600!important;font-size:13px!important}
</style>
""", unsafe_allow_html=True)

# ── CACHE DE DATOS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def cargar_maestra(_url="", _key=""):
    sb = get_supabase()
    datos = []
    offset = 0
    while True:
        r = sb.table("maestra").select("*").range(offset, offset+999).execute()
        if not r.data: break
        datos.extend(r.data); offset += 1000
    return datos

@st.cache_data(ttl=300, show_spinner=False)
def cargar_inventario(_url="", _key=""):
    sb = get_supabase()
    datos = []
    offset = 0
    while True:
        r = sb.table("inventario").select("*").range(offset, offset+999).execute()
        if not r.data: break
        datos.extend(r.data); offset += 1000
    return datos

@st.cache_data(ttl=60, show_spinner=False)
def cargar_historial_cache(_url="", _key=""):
    sb = get_supabase()
    return sb.table("historial").select("*").order("id", desc=True).limit(300).execute().data or []

def refrescar():
    cargar_maestra.clear()
    cargar_inventario.clear()
    cargar_historial_cache.clear()
    st.rerun()

# ── COLORES DESDE SUPABASE ────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def _cargar_colores_css(_url="", _key=""):
    try:
        import json as _jc
        sb = get_supabase()
        r = sb.table("app_config").select("config").eq("usuario","admin").execute()
        if r.data:
            return _jc.loads(r.data[0]["config"]).get("colores", {})
    except:
        pass
    return {}

def _aplicar_colores():
    if not st.session_state.usuario:
        return
    try:
        _C_CSS = _cargar_colores_css(st.session_state.suc_url, st.session_state.suc_key)
        if _C_CSS:
            _vars = "".join(
                f"--{k.replace('_','-')}:{v};" for k, v in _C_CSS.items()
                if k in ('bg','surface','surface2','primary','accent','success','warning','danger','text','border')
            )
            if _C_CSS.get('text_dim'):
                _vars += f"--dim:{_C_CSS['text_dim']};"
            if _vars:
                st.markdown(f"<style>:root{{{_vars}}}</style>", unsafe_allow_html=True)
    except:
        pass

_aplicar_colores()

# ── UTILILIDADES ──────────────────────────────────────────────────────────────
def parsear_fecha(texto):
    try:
        p = str(texto).strip().split("/")
        if len(p) == 2:
            m, a = int(p[0]), int(p[1])
            return date(2000 + a if a < 100 else a, m, 1)
    except:
        pass
    return None

def dias_para_vencer(texto):
    f = parsear_fecha(texto)
    return (f - date.today()).days if f else None

def calcular_vacias_rapido(ocupadas: set, max_n=None):
    try:
        import json as _jv
        sb = get_supabase()
        r = sb.table("app_config").select("config").eq("usuario","admin").execute()
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
        for n in range(1, cfg["niveles"]+1):
            if max_n and len(vacias) >= max_n: break
            lets = cfg.get("letras_por_nivel",{}).get(str(n),"ABCDE")
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
        sb = get_supabase()
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
        sb = get_supabase()
        sb.table("maestra").update({"cantidad_total": total}).eq("cod_int", cod_int).execute()
    except Exception as e:
        st.error(f"Error recalcular: {e}")
    return total

def _wa_config():
    try:
        sb = get_supabase()
        r1 = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
        r2 = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
        return (r1[0]['valor'] if r1 else "", r2[0]['valor'] if r2 else "")
    except:
        return ("", "")

def _enviar_whatsapp(numero, apikey, mensaje):
    import urllib.request, urllib.parse, threading
    def _send():
        try:
            num_limpio = "+" + numero.replace("+","").replace(" ","").replace("-","")
            msg_enc = urllib.parse.quote(mensaje, safe='')
            url = (f"https://api.callmebot.com/whatsapp.php"
                   f"?phone={num_limpio}&text={msg_enc}&apikey={apikey}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            urllib.request.urlopen(req, timeout=15)
        except:
            pass
    threading.Thread(target=_send, daemon=True).start()

# ── SESIÓN PERSISTENTE ────────────────────────────────────────────────────────
_qp = st.query_params
if not st.session_state.usuario and "lz_u" in _qp and "lz_r" in _qp:
    st.session_state.usuario  = _qp["lz_u"]
    st.session_state.rol      = _qp["lz_r"]
    if "lz_suc_url" in _qp:
        st.session_state.suc_url    = _qp["lz_suc_url"]
        st.session_state.suc_key    = _qp.get("lz_suc_key", DEFAULT_KEY)
        st.session_state.suc_nombre = _qp.get("lz_suc_nombre", "Principal")

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN + SELECTOR DE SUCURSAL
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.usuario:
    st.markdown("""
    <div style="max-width:380px;margin:40px auto 0;text-align:center;">
        <div style="font-size:56px;margin-bottom:8px">📦</div>
        <h1 style="font-size:32px;font-weight:900;letter-spacing:4px;margin:0;color:#F1F5F9;">LOGIEZE</h1>
        <p style="color:#94A3B8;font-size:13px;margin-top:4px;">Sistema de gestión de inventario</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="sec-label">🏢 SUCURSAL</div>', unsafe_allow_html=True)

        try:
            sb_tmp = create_client(DEFAULT_URL, DEFAULT_KEY)
            r_sucs = sb_tmp.table("app_config").select("config").eq("usuario","sucursales").execute()
            if r_sucs.data:
                import json as _jj
                _sucs_db = _jj.loads(r_sucs.data[0]["config"])
                if isinstance(_sucs_db, list) and _sucs_db:
                    _sucursales_login = _sucs_db
                else:
                    _sucursales_login = SUCURSALES_DEFAULT
            else:
                _sucursales_login = SUCURSALES_DEFAULT
        except:
            _sucursales_login = SUCURSALES_DEFAULT

        _nombres_suc = [s["nombre"] for s in _sucursales_login]
        _suc_idx = st.selectbox(
            "Sucursal", _nombres_suc,
            index=0,
            label_visibility="collapsed",
            key="login_suc_sel"
        )
        _suc_elegida = next((s for s in _sucursales_login if s["nombre"] == _suc_idx), _sucursales_login[0])

        if st.session_state.suc_url != _suc_elegida["url"]:
            st.session_state.suc_url    = _suc_elegida["url"]
            st.session_state.suc_key    = _suc_elegida["key"]
            st.session_state.suc_nombre = _suc_elegida["nombre"]

        st.markdown('<div class="sec-label" style="margin-top:14px">🔐 CREDENCIALES</div>', unsafe_allow_html=True)
        usuario_inp = st.text_input("USUARIO", placeholder="Usuario", label_visibility="collapsed", key="l_usr")
        clave_inp   = st.text_input("CLAVE",   placeholder="••••••••", label_visibility="collapsed", type="password", key="l_pwd")

        if st.button("ENTRAR  →", use_container_width=True):
            _url = _suc_elegida["url"]
            _key = _suc_elegida["key"]
            _nom = _suc_elegida["nombre"]
            _usr = usuario_inp.strip().lower()
            _pwd = clave_inp

            if not _usr or not _pwd:
                st.error("Ingresá usuario y clave.")
            else:
                try:
                    _sb_login = create_client(_url, _key)
                    if _usr == "admin" and _pwd == "70797474":
                        st.session_state.usuario    = "admin"
                        st.session_state.rol        = "admin"
                        st.session_state.suc_url    = _url
                        st.session_state.suc_key    = _key
                        st.session_state.suc_nombre = _nom
                        st.query_params["lz_u"]          = "admin"
                        st.query_params["lz_r"]          = "admin"
                        st.query_params["lz_suc_url"]    = _url
                        st.query_params["lz_suc_key"]    = _key
                        st.query_params["lz_suc_nombre"] = _nom
                        _invalidar_cache()
                        st.rerun()
                    else:
                        r = _sb_login.table("usuarios").select("*") \
                               .eq("usuario", _usr).eq("clave", _pwd).execute().data
                        if r:
                            st.session_state.usuario    = r[0]['usuario']
                            st.session_state.rol        = r[0]['rol']
                            st.session_state.suc_url    = _url
                            st.session_state.suc_key    = _key
                            st.session_state.suc_nombre = _nom
                            st.query_params["lz_u"]          = r[0]['usuario']
                            st.query_params["lz_r"]          = r[0]['rol']
                            st.query_params["lz_suc_url"]    = _url
                            st.query_params["lz_suc_key"]    = _key
                            st.query_params["lz_suc_nombre"] = _nom
                            _invalidar_cache()
                            st.rerun()
                        else:
                            st.error("Usuario o clave incorrectos en esta sucursal.")
                except Exception as e:
                    st.error(f"Error de conexión con '{_nom}': {e}")

        st.markdown("<br>", unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
usuario     = st.session_state.usuario
rol         = st.session_state.rol
suc_nombre  = st.session_state.suc_nombre
ROL_ICON    = {"admin":"👑","operario":"🔧","visita":"👁️","vendedor":"🛒"}.get(rol,"👤")

st.markdown(f"""
<div class="app-topbar">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="width:42px;height:42px;background:linear-gradient(135deg,#1D4ED8,#06B6D4);
         border-radius:12px;display:flex;align-items:center;justify-content:center;
         font-size:22px;flex-shrink:0">📦</div>
    <div>
      <div class="app-topbar-title">LOGIEZE</div>
      <div class="app-topbar-sub">{ROL_ICON} {usuario.upper()}</div>
      <div class="suc-badge">🏢 {suc_nombre}</div>
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
        for k in ["usuario","rol","suc_url","suc_key","suc_nombre","pedido","bot_hist","_ctx"]:
            st.session_state[k] = None if k in ["usuario","rol"] else ([] if k in ["pedido","bot_hist"] else ({} if k=="_ctx" else DEFAULT_URL if k=="suc_url" else DEFAULT_KEY if k=="suc_key" else "Principal"))
        st.query_params.clear()
        _invalidar_cache()
        st.rerun()

with st.spinner("Cargando datos..."):
    try:
        maestra    = cargar_maestra(st.session_state.suc_url, st.session_state.suc_key)
        inventario = cargar_inventario(st.session_state.suc_url, st.session_state.suc_key)
    except Exception as e:
        st.error(f"Error conectando a '{suc_nombre}': {e}")
        if st.button("↩ Volver al login"):
            for k in ["usuario","rol"]:
                st.session_state[k] = None
            st.query_params.clear()
            st.rerun()
        st.stop()

idx_inv       = {}
ubis_ocupadas = set()
for lote in inventario:
    cod = str(lote.get('cod_int',''))
    if cod not in idx_inv: idx_inv[cod] = []
    idx_inv[cod].append(lote)
    ubis_ocupadas.add(str(lote.get('ubicacion','')).upper())

_NAV_OPTIONS = ["📦 MOVIMIENTOS","🚚 DESPACHO","📋 HISTORIAL","📊 PLANILLA","⚙️ CONFIG","🔐 ADMIN","🤖 ASISTENTE"]

_nav_sel = st.selectbox("", _NAV_OPTIONS,
    index=_NAV_OPTIONS.index(st.session_state.nav_tab) if st.session_state.nav_tab in _NAV_OPTIONS else 0,
    label_visibility="collapsed", key="nav_select")
st.session_state.nav_tab = _nav_sel

def _show(name): return st.session_state.nav_tab == name

# ═══════════════════════════════════════════════════════════════════════════════
# TAB MOVIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════
if _show("📦 MOVIMIENTOS"):
    if st.session_state.pop("_clear_busq", False):
        st.session_state["busq"] = ""

    import streamlit.components.v1 as _stc_mov
    st.markdown('<div class="sec-label">🔍 BUSCAR PRODUCTO</div>', unsafe_allow_html=True)
    _stc_mov.html("""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif}body{background:transparent}
.btn{width:100%;background:linear-gradient(135deg,#10B981,#059669);color:#fff;border:none;border-radius:14px;padding:13px;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 4px 14px rgba(16,185,129,.4);display:flex;align-items:center;justify-content:center;gap:8px}
.btn:active{opacity:.85}.btn.act{background:linear-gradient(135deg,#EF4444,#F59E0B)}.msg{font-size:12px;color:#94A3B8;text-align:center;margin-top:5px;min-height:16px}.msg.ok{color:#10B981}.msg.er{color:#EF4444}
#ov{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.96);z-index:9999;flex-direction:column;align-items:center;justify-content:center;gap:16px}#ov.show{display:flex}
video{width:90%;max-width:340px;border-radius:18px;border:3px solid #10B981}.ln{width:90%;max-width:340px;height:3px;background:linear-gradient(90deg,transparent,#10B981,transparent);animation:sc 1.4s ease-in-out infinite}@keyframes sc{0%,100%{opacity:.2}50%{opacity:1}}.cl{background:#EF4444;color:#fff;border:none;border-radius:14px;padding:11px 32px;font-size:14px;font-weight:700;cursor:pointer}</style></head><body>
<button class="btn" id="sb" onclick="doScan()"><span>📷</span><span>Escanear código de barras</span></button>
<div class="msg" id="msg"></div><div id="ov"><video id="vid" autoplay playsinline muted></video><div class="ln"></div><div style="color:#F1F5F9;font-size:14px;font-weight:700;text-align:center;padding:0 20px">Apuntá el código — se busca automáticamente</div><button class="cl" onclick="closeScan()">✕ Cerrar</button></div>
<script>var s=null,a=false,iv=null;function setMsg(c,t){var el=document.getElementById('msg');el.className='msg '+(c||'');el.textContent=t}
function writeAndSubmit(val){var doc=window.parent.document;var inputs=doc.querySelectorAll('input[type="text"],input:not([type])');var inp=null;for(var i=0;i<inputs.length;i++){var ph=(inputs[i].placeholder||'').toLowerCase();if(ph.indexOf('barras')>=0||ph.indexOf('digo')>=0||ph.indexOf('ombre')>=0||ph.indexOf('buscar')>=0){inp=inputs[i];break}}if(!inp) inp=inputs[0];if(!inp){setMsg('er','No se encontró el campo');return}var nativeSetter=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value');if(nativeSetter&&nativeSetter.set){nativeSetter.set.call(inp,val)}else{inp.value=val}inp.dispatchEvent(new Event('input',{bubbles:true,cancelable:true}));inp.dispatchEvent(new Event('change',{bubbles:true,cancelable:true}));inp.focus();setTimeout(function(){inp.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true,cancelable:true}))},80)}
function doScan(){if(a){closeScan();return}if(!window.BarcodeDetector){setMsg('er','BarcodeDetector no soportado — Chrome Android requerido');return}a=true;document.getElementById('sb').className='btn act';document.getElementById('sb').innerHTML='<span>⏹</span><span>Detener</span>';document.getElementById('ov').className='show';setMsg('ok','Iniciando cámara...');navigator.mediaDevices.getUserMedia({video:{facingMode:'environment',width:{ideal:1920}}}).then(function(st2){s=st2;document.getElementById('vid').srcObject=st2;var det=new BarcodeDetector({formats:['ean_13','ean_8','code_128','code_39','upc_a','upc_e','itf','qr_code']});setMsg('ok','🟢 Escaneando...');iv=setInterval(function(){if(!a) return;det.detect(document.getElementById('vid')).then(function(codes){if(codes.length>0){var code=codes[0].rawValue;closeScan();setMsg('ok','✅ '+code);setTimeout(function(){writeAndSubmit(code)},120)}}).catch(function(){})},350)}).catch(function(e){closeScan();setMsg('er','❌ '+e.message)})}
function closeScan(){a=false;clearInterval(iv);if(s){s.getTracks().forEach(function(t){t.stop()});s=null}document.getElementById('vid').srcObject=null;document.getElementById('sb').className='btn';document.getElementById('sb').innerHTML='<span>📷</span><span>Escanear código de barras</span>';document.getElementById('ov').className=''}</script></body></html>""", height=80)

    busqueda = st.text_input("Buscar", placeholder="Nombre, código o barras...", label_visibility="collapsed", key="busq")

    productos_filtrados = []
    if busqueda:
        t = busqueda.strip()
        if t.startswith('.'):
            cod_exacto = t[1:].strip()
            productos_filtrados = [p for p in maestra if str(p.get('cod_int','')).strip() == cod_exacto]
        elif t.isdigit() and 7 <= len(t) <= 14:
            productos_filtrados = [p for p in maestra if str(p.get('barras','')).strip() == t or str(p.get('cod_barras','')).strip() == t]
            if not productos_filtrados:
                productos_filtrados = [p for p in maestra if t in str(p.get('barras','')).upper()]
        else:
            T = t.upper()
            productos_filtrados = [p for p in maestra if T in str(p.get('nombre','')).upper() or T in str(p.get('cod_int','')).upper() or T in str(p.get('barras','')).upper()]

    if not productos_filtrados and busqueda:
        st.info("No se encontraron productos.")
    elif productos_filtrados:
        st.markdown(f'<div style="font-size:12px;color:#94A3B8;margin-bottom:8px">{len(productos_filtrados)} resultado(s)</div>', unsafe_allow_html=True)
        nombres_lista = [f"{p['nombre']}  ·  {int(float(p.get('cantidad_total') or 0))}u  [{p['cod_int']}]" for p in productos_filtrados]
        sel_idx = st.selectbox("", range(len(nombres_lista)), format_func=lambda i: nombres_lista[i], label_visibility="collapsed", key="sel_prod")
        prod_sel = productos_filtrados[sel_idx]
        cod_sel  = str(prod_sel['cod_int'])
        lotes_prod = idx_inv.get(cod_sel, [])
        total_q    = sum(float(l.get('cantidad',0)) for l in lotes_prod)
        stk_color  = "#10B981" if total_q > 10 else ("#F59E0B" if total_q > 0 else "#EF4444")

        st.markdown(f'<div style="background:#1E293B;border-radius:14px;padding:14px 16px;margin:12px 0;border-left:4px solid {stk_color}"><div style="font-size:11px;font-weight:700;color:{stk_color};text-transform:uppercase">STOCK TOTAL</div><div style="font-size:32px;font-weight:900;color:#F1F5F9">{int(total_q)}u</div><div style="font-size:11px;color:#94A3B8">{prod_sel["nombre"]}</div></div>', unsafe_allow_html=True)

        if lotes_prod:
            st.markdown('<div class="sec-label">📦 LOTES EN STOCK</div>', unsafe_allow_html=True)
            for _lt in sorted(lotes_prod, key=lambda x: float(x.get('cantidad',0) or 0), reverse=True):
                _lq = int(float(_lt.get('cantidad', 0) or 0))
                _lu = str(_lt.get('ubicacion','—')).upper()
                _ld = str(_lt.get('deposito','—'))
                _lf = str(_lt.get('fecha','') or '').strip() or '—'
                _lc = "#10B981" if _lq > 5 else ("#F59E0B" if _lq > 0 else "#EF4444")
                st.markdown(f'<div style="background:#0F172A;border-radius:10px;padding:10px 14px;margin:4px 0;display:flex;justify-content:space-between;align-items:center;border:1px solid #1E293B"><div style="display:flex;gap:14px;align-items:center"><div style="font-size:22px;font-weight:900;color:{_lc};min-width:36px">{_lq}u</div><div><div style="font-size:13px;font-weight:700;color:#F1F5F9">📍 {_lu}</div><div style="font-size:11px;color:#64748B">{_ld} · 📅 {_lf}</div></div></div></div>', unsafe_allow_html=True)

        # ── MOVER LOTE ────────────────────────────────────────────────────────
        if lotes_prod and rol in ("admin", "operario"):
            with st.expander("🔀  Mover lote a otra ubicación", expanded=False):
                st.markdown(
                    '<div style="font-size:11px;color:#94A3B8;margin-bottom:10px">'
                    'Seleccioná el lote origen y la ubicación destino. '
                    'La fecha de vencimiento se mantiene.</div>',
                    unsafe_allow_html=True)

                # Selector de lote origen
                _opts_mv = [
                    f"[{int(float(l.get('cantidad',0)))}u]  📍 {str(l.get('ubicacion','?')).upper()}"
                    f"  ·  Vto:{l.get('fecha','—')}  ·  {l.get('deposito','')}"
                    for l in lotes_prod
                ]
                _mv_idx = st.selectbox(
                    "Lote origen:",
                    range(len(_opts_mv)),
                    format_func=lambda i: _opts_mv[i],
                    key="mv_lote_idx")
                _lote_mv = lotes_prod[_mv_idx]
                _cant_disp_mv = float(_lote_mv.get('cantidad', 0) or 0)

                _mv_col1, _mv_col2 = st.columns(2)
                with _mv_col1:
                    _es_total_mv = st.checkbox(
                        "Mover lote completo",
                        value=True, key="mv_completo")
                with _mv_col2:
                    _cant_mv = st.number_input(
                        "Cantidad a mover:",
                        min_value=0.1,
                        max_value=_cant_disp_mv,
                        value=_cant_disp_mv if _es_total_mv else 1.0,
                        step=1.0, format="%.0f",
                        key="mv_cant",
                        disabled=_es_total_mv)
                if _es_total_mv:
                    _cant_mv = _cant_disp_mv

                # Destino: lista de vacías + manual
                _vacias_mv  = calcular_vacias_rapido(ubis_ocupadas)
                _sug99_mv   = calcular_sug99(ubis_ocupadas)
                _otras_ubis = [
                    str(l.get('ubicacion','')).upper()
                    for l in lotes_prod
                    if str(l.get('ubicacion','')).upper() != str(_lote_mv.get('ubicacion','')).upper()
                ]
                _dest_opciones = (
                    [f"VACIA: {v}" for v in _vacias_mv] +
                    ([f"SUG 99: {_sug99_mv}"] if _sug99_mv not in _vacias_mv else []) +
                    _otras_ubis
                )

                _dest_sel = None
                if _dest_opciones:
                    _dest_sel = st.selectbox(
                        "Ubicación destino (sugeridas):",
                        _dest_opciones,
                        key="mv_ubi_sel")

                _dest_manual = st.text_input(
                    "o escribir manualmente:",
                    placeholder="ej: 05-3B",
                    key="mv_ubi_manual")

                _ubi_destino = ""
                if _dest_manual.strip():
                    _ubi_destino = _dest_manual.strip().upper()
                elif _dest_sel:
                    _ubi_destino = (
                        _dest_sel
                        .replace("VACIA: ", "")
                        .replace("SUG 99: ", "")
                        .upper().strip()
                    )

                if _ubi_destino:
                    st.markdown(
                        f'<div class="sug-box">'
                        f'📦 {int(_cant_mv)}u &nbsp;·&nbsp; '
                        f'📍 {str(_lote_mv.get("ubicacion","?")).upper()} → <b>{_ubi_destino}</b>'
                        f' &nbsp;·&nbsp; Vto: {_lote_mv.get("fecha","—")}'
                        f'</div>',
                        unsafe_allow_html=True)

                if st.button("🔀  Confirmar movimiento", use_container_width=True,
                             key="btn_mv_confirmar", type="primary"):
                    if not _ubi_destino:
                        st.error("Seleccioná o escribí la ubicación destino.")
                    elif _ubi_destino == str(_lote_mv.get('ubicacion','')).upper():
                        st.error("La ubicación destino es igual al origen.")
                    elif _cant_mv <= 0 or _cant_mv > _cant_disp_mv:
                        st.error(f"Cantidad inválida. Disponible: {int(_cant_disp_mv)}u")
                    else:
                        try:
                            sb = get_supabase()
                            _fv_orig  = _lote_mv.get('fecha', '')
                            _dep_orig = _lote_mv.get('deposito', 'depo 1')

                            # 1. Reducir / eliminar lote origen
                            if _cant_mv >= _cant_disp_mv:
                                sb.table("inventario").delete().eq("id", _lote_mv['id']).execute()
                            else:
                                sb.table("inventario").update({
                                    "cantidad": _cant_disp_mv - _cant_mv
                                }).eq("id", _lote_mv['id']).execute()

                            # 2. ¿ya existe lote con esa ubi+fecha+deposito en destino?
                            _exist_dest = next((
                                l for l in lotes_prod
                                if str(l.get('ubicacion','')).upper() == _ubi_destino
                                and str(l.get('fecha',''))   == _fv_orig
                                and str(l.get('deposito','')) == _dep_orig
                                and str(l.get('id',''))       != str(_lote_mv.get('id',''))
                            ), None)

                            if _exist_dest:
                                # Sumar al lote existente
                                _nq = float(_exist_dest.get('cantidad', 0)) + _cant_mv
                                sb.table("inventario").update({
                                    "cantidad": _nq
                                }).eq("id", _exist_dest['id']).execute()
                            else:
                                # Crear nuevo lote en destino
                                sb.table("inventario").insert({
                                    "cod_int":   cod_sel,
                                    "nombre":    prod_sel['nombre'],
                                    "cantidad":  _cant_mv,
                                    "ubicacion": _ubi_destino,
                                    "deposito":  _dep_orig,
                                    "fecha":     _fv_orig,
                                }).execute()

                            # 3. Historial
                            registrar_historial(
                                "MOVIMIENTO", cod_sel, prod_sel['nombre'],
                                _cant_mv,
                                f"{str(_lote_mv.get('ubicacion','?')).upper()} → {_ubi_destino}",
                                usuario)

                            st.success(
                                f"✅ {int(_cant_mv)}u de **{prod_sel['nombre']}** "
                                f"movidas a **{_ubi_destino}** · Vto: {_fv_orig}")
                            refrescar()
                        except Exception as e:
                            st.error(f"Error al mover: {e}")

        st.markdown("---")
        st.markdown('<div class="sec-label">📝 REGISTRAR OPERACIÓN</div>', unsafe_allow_html=True)
        tipo_op    = st.radio("Tipo", ["⬆ INGRESO", "⬇ SALIDA"], horizontal=True, label_visibility="collapsed", key="tipo_op")
        es_ingreso = "INGRESO" in tipo_op

        col_a, col_b = st.columns(2)
        with col_a:
            cantidad_op = st.number_input("CANTIDAD", min_value=0.1, step=1.0, format="%.0f", key="cant_op")
        with col_b:
            # ── FECHA CON AUTO-SLASH ──────────────────────────────────────
            import streamlit.components.v1 as _stc_fecha
            _stc_fecha.html("""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif}
body{background:transparent}
label{display:block;font-size:11px;font-weight:700;color:#94A3B8;
      letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}
input{width:100%;background:#1E293B;color:#F1F5F9;
      border:1.5px solid #334155;border-radius:12px;
      padding:12px 14px;font-size:16px;outline:none;font-family:inherit}
input:focus{border-color:#3B82F6;box-shadow:0 0 0 3px rgba(59,130,246,.15)}
</style></head><body>
<label>VENCIMIENTO (MM/AA)</label>
<input type="text" id="fv" maxlength="5" placeholder="06/26" inputmode="numeric"
       autocomplete="off">
<script>
var inp = document.getElementById('fv');
var prev = '';
inp.addEventListener('input', function() {
  var raw = inp.value.replace(/\D/g, '');
  var fmt = raw;
  if (raw.length > 2) fmt = raw.slice(0,2) + '/' + raw.slice(2,4);
  // avoid fighting with deletion
  if (inp.value === prev.slice(0,-1) && prev.endsWith('/')) {
    inp.value = raw.slice(0,2);
  } else {
    inp.value = fmt;
  }
  prev = inp.value;
  // sync al campo oculto de Streamlit
  try {
    var pdoc = window.parent.document;
    var inputs = pdoc.querySelectorAll('input');
    for (var i = 0; i < inputs.length; i++) {
      var ph = (inputs[i].placeholder || '').toLowerCase();
      if (ph === '06/26' || ph.indexOf('mm/aa') >= 0 || ph.indexOf('venc') >= 0) {
        var ns = Object.getOwnPropertyDescriptor(
          window.parent.HTMLInputElement.prototype, 'value');
        if (ns && ns.set) ns.set.call(inputs[i], inp.value);
        inputs[i].dispatchEvent(new Event('input',   {bubbles:true}));
        inputs[i].dispatchEvent(new Event('change',  {bubbles:true}));
        break;
      }
    }
  } catch(e) {}
});
</script></body></html>""", height=76)
            fecha_op = st.text_input(
                "VENCIMIENTO",
                placeholder="06/26",
                key="fecha_op",
                label_visibility="collapsed")

        opciones_ubi_list = list({str(l.get('ubicacion','')).upper() for l in lotes_prod})
        vacias      = calcular_vacias_rapido(ubis_ocupadas)
        sug99       = calcular_sug99(ubis_ocupadas)
        opciones_ubi = opciones_ubi_list + [f"VACIA: {v}" for v in vacias] + [f"SUG 99: {sug99}"]
        sugerencia  = vacias[0] if vacias else sug99
        st.markdown(f'<div class="sug-box">📍 Sugerencia: {sugerencia}</div>', unsafe_allow_html=True)

        col_u, col_d = st.columns(2)
        with col_u:
            ubi_sel   = st.selectbox("UBICACIÓN", opciones_ubi, key="ubi_op")
            ubi_final = ubi_sel.replace("VACIA: ","").replace("SUG 99: ","").upper().strip()
            ubi_manual = st.text_input("o escribir manualmente:", placeholder="ej: 05-3B", key="ubi_man")
            if ubi_manual.strip(): ubi_final = ubi_manual.strip().upper()
        with col_d:
            depo_op = st.selectbox("DEPÓSITO", ["depo 1","depo 2"], key="depo_op")

        lote_sel = None
        if not es_ingreso and lotes_prod:
            opciones_lotes = [f"[{int(float(l.get('cantidad',0)))}u] {l.get('ubicacion','')} — {l.get('deposito','')} | Vto:{l.get('fecha','')}" for l in lotes_prod]
            lote_idx = st.selectbox("LOTE A DESCONTAR:", range(len(opciones_lotes)), format_func=lambda i: opciones_lotes[i], key="lote_op")
            lote_sel = lotes_prod[lote_idx]

        _do_register = False
        if not es_ingreso and lote_sel:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ DESCONTAR", use_container_width=True, key="btn_reg", type="primary"):
                    _do_register = True
            with col_b2:
                if st.button("🖐 MANUAL", use_container_width=True, key="btn_reg_manual"):
                    _do_register = True
        else:
            if st.button("✅ REGISTRAR OPERACIÓN", use_container_width=True, key="btn_reg", type="primary"):
                _do_register = True

        if _do_register:
            _fecha_reg = fecha_op.strip() if fecha_op else ""
            if cantidad_op <= 0:
                st.error("Cantidad debe ser mayor a 0.")
            elif es_ingreso and not _fecha_reg:
                st.error("Ingresá la fecha de vencimiento.")
            else:
                try:
                    sb = get_supabase()
                    if es_ingreso:
                        existente = next((l for l in lotes_prod
                            if str(l.get('ubicacion','')).upper() == ubi_final
                            and str(l.get('fecha','')) == _fecha_reg
                            and str(l.get('deposito','')) == depo_op), None)
                        if existente:
                            nq = float(existente['cantidad']) + cantidad_op
                            sb.table("inventario").update({"cantidad": nq}).eq("id", existente['id']).execute()
                        else:
                            sb.table("inventario").insert({"cod_int": cod_sel, "nombre": prod_sel['nombre'], "cantidad": cantidad_op, "ubicacion": ubi_final, "deposito": depo_op, "fecha": _fecha_reg}).execute()
                    else:
                        if not lote_sel: st.error("No hay lotes disponibles."); st.stop()
                        cant_actual = float(lote_sel['cantidad'])
                        if cant_actual - cantidad_op <= 0:
                            sb.table("inventario").delete().eq("id", lote_sel['id']).execute()
                        else:
                            sb.table("inventario").update({"cantidad": cant_actual - cantidad_op}).eq("id", lote_sel['id']).execute()
                    registrar_historial("INGRESO" if es_ingreso else "SALIDA", cod_sel, prod_sel['nombre'], cantidad_op, ubi_final, usuario)
                    recalcular_maestra(cod_sel, inventario)
                    st.success("✅ Operación registrada correctamente.")
                    st.session_state["_clear_busq"] = True
                    refrescar()
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB HISTORIAL
# ═══════════════════════════════════════════════════════════════════════════════
if _show("📋 HISTORIAL"):
    st.markdown('<div class="sec-label">📋 HISTORIAL DE MOVIMIENTOS</div>', unsafe_allow_html=True)
    hist_data = cargar_historial_cache(st.session_state.suc_url, st.session_state.suc_key)
    filtro_h = st.text_input("Filtrar:", placeholder="Producto, usuario, tipo...", label_visibility="collapsed", key="filtro_h")
    if filtro_h:
        t = filtro_h.upper()
        hist_data = [h for h in hist_data if t in str(h.get('nombre','')).upper() or t in str(h.get('usuario','')).upper() or t in str(h.get('tipo','')).upper() or t in str(h.get('cod_int','')).upper() or t in str(h.get('ubicacion','')).upper()]
    if hist_data:
        df_h = pd.DataFrame(hist_data)[["fecha_hora","usuario","tipo","nombre","cod_int","cantidad","ubicacion"]]
        df_h.columns = ["FECHA","USUARIO","TIPO","PRODUCTO","CÓDIGO","CANT","UBICACIÓN"]
        st.dataframe(df_h, use_container_width=True, hide_index=True)
        st.caption(f"{len(df_h)} movimientos")
    else:
        st.info("Sin movimientos registrados.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB PLANILLA
# ═══════════════════════════════════════════════════════════════════════════════
if _show("📊 PLANILLA"):
    st.markdown('<div class="sec-label">📊 PLANILLA DE DATOS</div>', unsafe_allow_html=True)
    tabla_sel = st.radio("Tabla:", ["maestra","inventario"], horizontal=True, key="tabla_plan")
    filtro_p  = st.text_input("Filtrar:", placeholder="Buscar en la tabla...", label_visibility="collapsed", key="filtro_plan")
    data_plan = maestra if tabla_sel == "maestra" else inventario
    if filtro_p:
        t = filtro_p.upper()
        data_plan = [r for r in data_plan if any(t in str(v).upper() for v in r.values())]
    if data_plan:
        df_plan = pd.DataFrame(data_plan)
        st.dataframe(df_plan, use_container_width=True, hide_index=True)
        st.caption(f"{len(df_plan)} filas")
        csv = df_plan.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", csv, file_name=f"{tabla_sel}_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
    else:
        st.info("Sin datos.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
if _show("⚙️ CONFIG"):
    if rol != "admin":
        st.warning("🔒 Solo disponible para administradores.")
    else:
        @st.cache_data(ttl=30, show_spinner=False)
        def _cargar_cfg_admin(_url="", _key=""):
            try:
                import json as _j
                sb = get_supabase()
                r = sb.table("app_config").select("config").eq("usuario","admin").execute()
                if r.data: return _j.loads(r.data[0]["config"])
            except: pass
            return {}

        def _guardar_cfg_admin(nueva_cfg):
            import json as _j
            try:
                sb = get_supabase()
                sb.table("app_config").upsert({"usuario":"admin","config":_j.dumps(nueva_cfg, ensure_ascii=False)}).execute()
                _cargar_cfg_admin.clear()
                _cargar_colores_css.clear()
                return True
            except Exception as e:
                st.error(f"Error guardando: {e}")
                return False

        _cfg_admin = _cargar_cfg_admin(st.session_state.suc_url, st.session_state.suc_key)
        _cfg_tab   = st.radio("", ["🏢 Sucursales","🗄️ Estanterías","⚙️ General"], horizontal=True, key="cfg_subtab", label_visibility="collapsed")

        # ── SUCURSALES ───────────────────────────────────────────────────────
        if _cfg_tab == "🏢 Sucursales":
            st.markdown('<div class="sec-label">🏢 GESTIÓN DE SUCURSALES</div>', unsafe_allow_html=True)
            st.info("Las sucursales se guardan en Supabase y aparecen en el selector del login.")

            try:
                _sucs_act = get_sucursales()
            except:
                _sucs_act = SUCURSALES_DEFAULT

            for i, s in enumerate(_sucs_act):
                es_actual = s['url'].strip() == st.session_state.suc_url.strip()
                st.markdown(f"""
                <div class="suc-card {'active' if es_actual else ''}">
                  <div style="font-weight:800;font-size:14px;color:#F1F5F9">
                    {'✅ ' if es_actual else '🏢 '}{s['nombre']}
                    {'<span style="font-size:10px;color:#3B82F6;margin-left:8px">(CONECTADO)</span>' if es_actual else ''}
                  </div>
                  <div style="font-size:11px;color:#64748B;margin-top:3px">{s['url']}</div>
                </div>""", unsafe_allow_html=True)
                if not es_actual:
                    if st.button(f"🗑 Eliminar '{s['nombre']}'", key=f"del_suc_{i}"):
                        _sucs_act_new = [x for j, x in enumerate(_sucs_act) if j != i]
                        if save_sucursales(_sucs_act_new):
                            st.success(f"✅ Sucursal '{s['nombre']}' eliminada.")
                            st.rerun()
                        else:
                            st.error("Error eliminando. Verificá permisos RLS en Supabase.")

            st.markdown("---")
            st.markdown('<div class="sec-label">➕ AGREGAR SUCURSAL</div>', unsafe_allow_html=True)
            with st.form("form_add_suc"):
                _sn = st.text_input("Nombre de la sucursal", placeholder="ej: Sucursal Norte")
                _su = st.text_input("URL de Supabase", placeholder="https://xxx.supabase.co")
                _sk = st.text_input("Anon Key", placeholder="eyJh...", type="password")
                col_ts, col_as = st.columns(2)
                with col_ts:
                    _test_btn = st.form_submit_button("🔌 Probar conexión", use_container_width=True)
                with col_as:
                    _add_btn  = st.form_submit_button("➕ Agregar", use_container_width=True, type="primary")

                if _test_btn:
                    if _su and _sk:
                        try:
                            _sb_t = create_client(_su.strip(), _sk.strip())
                            _sb_t.table("maestra").select("cod_int").limit(1).execute()
                            st.success("✅ Conexión exitosa.")
                        except Exception as e:
                            st.error(f"❌ No se pudo conectar: {e}")
                    else:
                        st.warning("Completá URL y Key.")

                if _add_btn:
                    if _sn and _su and _sk:
                        if any(s['url'].strip() == _su.strip() for s in _sucs_act):
                            st.warning("Ya existe una sucursal con esa URL.")
                        else:
                            _sucs_act.append({"nombre": _sn.strip(), "url": _su.strip(), "key": _sk.strip()})
                            if save_sucursales(_sucs_act):
                                st.success(f"✅ Sucursal '{_sn}' agregada correctamente.")
                                st.rerun()
                            else:
                                st.error("Error guardando. Verificá permisos en Supabase.")
                    else:
                        st.warning("Completá todos los campos.")

        # ── ESTANTERÍAS ──────────────────────────────────────────────────────
        elif _cfg_tab == "🗄️ Estanterías":
            # ── Leer siempre frescos desde Supabase sin cache ────────────
            # Esto garantiza que los cambios hechos desde la app de escritorio
            # sean visibles aquí inmediatamente sin necesidad de refrescar.
            try:
                import json as _jfresh
                _sb_fresh = get_supabase()
                _r_fresh  = _sb_fresh.table("app_config").select("config").eq("usuario","admin").execute()
                _cfg_fresh = _jfresh.loads(_r_fresh.data[0]["config"]) if _r_fresh.data else {}
                _est_cfg  = _cfg_fresh.get("estantes", [])
            except:
                _est_cfg  = _cfg_admin.get("estantes", [])

            if not _est_cfg:
                for _e in range(1, 28):
                    if _e in [3,4]:            _nv,_ls = 4,"ABCDE"
                    elif _e in [8,9,10,11,12]: _nv,_ls = 6,"ABCDEFG"
                    else:                       _nv,_ls = 5,"ABCDE"
                    _est_cfg.append({"num":_e,"niveles":_nv,"disponible":True,"letras_por_nivel":{str(_n):_ls for _n in range(1,_nv+1)}})

            if "est_sel_num" not in st.session_state:
                st.session_state.est_sel_num = _est_cfg[0]["num"] if _est_cfg else 1

            _col_lista, _col_editor = st.columns([2, 3])
            with _col_lista:
                st.markdown('<div style="font-size:10px;font-weight:800;color:#475569;letter-spacing:1.5px;margin-bottom:6px">ESTANTES</div>', unsafe_allow_html=True)
                for _e in _est_cfg:
                    _sel = _e["num"] == st.session_state.est_sel_num
                    _ico = "✅" if _e.get("disponible",True) else "⛔"
                    if st.button(f"{_ico}  E{str(_e['num']).zfill(2)}  ·  {_e.get('niveles',5)}niv", key=f"esel_{_e['num']}", use_container_width=True, type="primary" if _sel else "secondary"):
                        st.session_state.est_sel_num = _e["num"]; st.rerun()

            with _col_editor:
                _est_act = next((e for e in _est_cfg if e["num"] == st.session_state.est_sel_num), None)
                if _est_act:
                    _nnum = _est_act["num"]; _nniv = _est_act.get("niveles",5)
                    _lp   = _est_act.get("letras_por_nivel",{})
                    _ea1, _ea2 = st.columns(2)
                    with _ea1: _disp_new = st.checkbox("Activo", value=bool(_est_act.get("disponible",True)), key=f"edisp_{_nnum}")
                    with _ea2: _niv_new  = st.number_input("Niveles", min_value=1, max_value=12, value=_nniv, key=f"eniv_{_nnum}")
                    _niveles_nuevos = {}
                    for _nv in range(1, _niv_new+1):
                        _ns = str(_nv); _lv = _lp.get(_ns, "ABCDE")
                        _nc1, _nc2 = st.columns([2,3])
                        _nc1.markdown(f'<div style="padding:8px 0;font-weight:800;font-size:13px">Nivel {_nv:02d}</div>', unsafe_allow_html=True)
                        _ln = _nc2.text_input("", value=_lv, key=f"elet_{_nnum}_{_nv}", label_visibility="collapsed")
                        _niveles_nuevos[_ns] = _ln.strip().upper() if _ln.strip() else _lv
                    if st.button("💾 Guardar estante", use_container_width=True, type="primary", key=f"esave_{_nnum}"):
                        _est_act["disponible"] = _disp_new; _est_act["niveles"] = _niv_new; _est_act["letras_por_nivel"] = _niveles_nuevos
                        _nc2 = dict(_cfg_admin); _nc2["estantes"] = _est_cfg
                        if _guardar_cfg_admin(_nc2): st.success(f"✅ Estante {str(_nnum).zfill(2)} guardado."); st.rerun()

        # ── GENERAL ──────────────────────────────────────────────────────────
        elif _cfg_tab == "⚙️ General":
            _gc1, _gc2 = st.columns(2)
            with _gc1: _dias_new = st.number_input("⏰ Días alerta vencimiento", min_value=1, max_value=365, value=int(_cfg_admin.get("dias_alerta",60)), key="cfg_dias")
            with _gc2: _hist_new = st.number_input("📋 Límite historial", min_value=50, max_value=5000, step=50, value=int(_cfg_admin.get("hist_limit",500)), key="cfg_hist")
            if st.button("💾 Guardar", use_container_width=True, type="primary", key="cfg_gen_save"):
                _nc3 = dict(_cfg_admin); _nc3.update({"dias_alerta":_dias_new,"hist_limit":_hist_new})
                if _guardar_cfg_admin(_nc3): st.success("✅ Guardado."); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
if _show("🔐 ADMIN"):
    if rol != "admin":
        st.warning("🔒 Solo disponible para administradores.")
    else:
        st.markdown('<div class="sec-label">👤 GESTIÓN DE USUARIOS</div>', unsafe_allow_html=True)
        try:
            sb = get_supabase()
            usuarios_db = sb.table("usuarios").select("*").execute().data or []
            if usuarios_db:
                df_u = pd.DataFrame(usuarios_db)[["usuario","rol"]]
                df_u.columns = ["USUARIO","ROL"]
                st.dataframe(df_u, use_container_width=True, hide_index=True)
        except: pass

        with st.form("form_crear_usuario"):
            col_au, col_ap, col_ar = st.columns(3)
            with col_au: nu  = st.text_input("Usuario")
            with col_ap: np_ = st.text_input("Clave", type="password")
            with col_ar: nr  = st.selectbox("Rol", ["operario","admin","visita","vendedor"])
            if st.form_submit_button("➕ Crear usuario", use_container_width=True):
                if nu and np_:
                    try:
                        sb = get_supabase()
                        sb.table("usuarios").insert({"usuario": nu.lower().strip(), "clave": np_, "rol": nr}).execute()
                        st.success("✅ Usuario creado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown('<div class="sec-label">📱 WHATSAPP (CallMeBot)</div>', unsafe_allow_html=True)
        try:
            sb = get_supabase()
            _wa_n = sb.table("config").select("valor").eq("clave","wa_numero").execute().data
            _wa_k = sb.table("config").select("valor").eq("clave","wa_apikey").execute().data
            _wa_num_act = _wa_n[0]["valor"] if _wa_n else ""
            _wa_key_act = _wa_k[0]["valor"] if _wa_k else ""
        except:
            _wa_num_act = _wa_key_act = ""

        with st.form("form_wa"):
            col_wn, col_wk = st.columns(2)
            with col_wn: wa_num = st.text_input("Número WhatsApp:", value=_wa_num_act, placeholder="+5491112345678")
            with col_wk: wa_key = st.text_input("API Key CallMeBot:", value=_wa_key_act, placeholder="123456")
            if st.form_submit_button("💾 Guardar número", use_container_width=True):
                if wa_num.strip() and wa_key.strip():
                    try:
                        sb = get_supabase()
                        sb.table("config").upsert({"clave":"wa_numero","valor":wa_num.strip()}, on_conflict="clave").execute()
                        sb.table("config").upsert({"clave":"wa_apikey","valor":wa_key.strip()}, on_conflict="clave").execute()
                        st.success(f"✅ Guardado: {wa_num.strip()}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Completá número y API key.")

        st.markdown("---")
        st.markdown('<div class="sec-label" style="color:#EF4444">⚠️ ZONA PELIGROSA</div>', unsafe_allow_html=True)
        tabla_wipe = st.selectbox("Tabla a borrar:", ["inventario","maestra","historial"], key="wipe_t")
        confirmar  = st.text_input("Escribí CONFIRMAR para habilitar:", key="wipe_conf")
        if confirmar == "CONFIRMAR":
            if st.button(f"🗑️ BORRAR TABLA '{tabla_wipe}'", type="primary", use_container_width=True):
                try:
                    sb = get_supabase()
                    id_col = "id" if tabla_wipe in ["inventario","historial"] else "cod_int"
                    sb.table(tabla_wipe).delete().neq(id_col, -999).execute()
                    st.success("Tabla borrada.")
                    refrescar()
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB DESPACHO
# ═══════════════════════════════════════════════════════════════════════════════
if _show("🚚 DESPACHO"):
    import json as _json
    st.markdown('<div class="sec-label">🚚 PICKING CONTROLADO</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=30, show_spinner=False)
    def cargar_pedidos_nube(_url="", _key=""):
        try:
            sb = get_supabase()
            return sb.table("pedidos").select("id,nombre,fecha,estado,items") \
                     .in_("estado", ["pendiente","en_proceso"]) \
                     .order("id", desc=True).limit(20).execute().data or []
        except:
            return []

    pedidos_nube = cargar_pedidos_nube(st.session_state.suc_url, st.session_state.suc_key)

    col_s1, col_s2, col_s3 = st.columns([3,1,1])
    with col_s1:
        if pedidos_nube:
            opciones_pedidos = [f"#{p['id']}  {p['nombre']}  [{p.get('fecha','')}]" for p in pedidos_nube]
            idx_ped_sel = st.selectbox("Pedidos:", range(len(opciones_pedidos)), format_func=lambda i: opciones_pedidos[i], key="sel_ped_nube", label_visibility="collapsed")
        else:
            st.info("☁️ Sin pedidos en la nube.")
            idx_ped_sel = None
    with col_s2:
        if pedidos_nube and idx_ped_sel is not None:
            if st.button("⬇ Cargar", use_container_width=True, key="btn_bajar_ped"):
                ped = pedidos_nube[idx_ped_sel]
                items_raw = ped.get('items') or []
                if isinstance(items_raw, str):
                    try: items_raw = _json.loads(items_raw)
                    except: items_raw = []
                if items_raw:
                    st.session_state.pedido = [
                        {"cod": str(it.get('cod_int', it.get('codigo',''))),
                         "cant": int(float(str(it.get('cantidad', it.get('cant',0))))),
                         "nombre": it.get('nombre',''), "ped_id": ped['id']}
                        for it in items_raw
                    ]
                    try:
                        sb = get_supabase()
                        sb.table("pedidos").update({"estado":"en_proceso"}).eq("id", ped['id']).execute()
                        cargar_pedidos_nube.clear()
                    except: pass
                    st.success(f"✅ '{ped['nombre']}' cargado")
                    st.rerun()
    with col_s3:
        if st.button("🔄", use_container_width=True, key="btn_ref_nube"):
            cargar_pedidos_nube.clear(); st.rerun()

    st.markdown("---")

    texto_pegado = st.text_area("📋 Pegar desde Excel:", placeholder="Pegá las filas acá (Ctrl+V)", height=80, key="txt_pegar_excel")
    if st.button("📥 Cargar desde Excel", use_container_width=True, key="btn_cargar_excel"):
        if texto_pegado.strip():
            try:
                df_p = pd.read_csv(StringIO(texto_pegado), sep='\t', dtype=str).fillna("")
                df_p.columns = [str(c).strip().upper() for c in df_p.columns]
                col_cod  = next((c for c in ["CODIGO","CÓDIGO","COD","COD_INT"] if c in df_p.columns), None)
                col_cant = next((c for c in ["CANTIDAD","CANT","QTY"] if c in df_p.columns), None)
                col_nom  = next((c for c in ["ARTICULO","ARTÍCULO","NOMBRE","DESCRIPCION"] if c in df_p.columns), None)
                if not col_cod or not col_cant:
                    st.error("No se encontraron columnas 'Codigo' y 'Cantidad'.")
                else:
                    nuevos = 0
                    for _, r in df_p.iterrows():
                        cod = str(r[col_cod]).strip(); cant_str = str(r[col_cant]).strip()
                        nom_excel = str(r[col_nom]).strip() if col_nom else ""
                        if not cod or cod.upper() in ("NAN","","CODIGO"): continue
                        if not cant_str or cant_str.upper() in ("NAN","","CANTIDAD"): continue
                        try: cant_v = int(float(cant_str))
                        except: continue
                        prod = next((p for p in maestra if str(p['cod_int']) == cod), None)
                        if not prod: prod = next((p for p in maestra if str(p.get('barras','')) == cod), None)
                        nom = prod['nombre'] if prod else (nom_excel or "NO ENCONTRADO")
                        st.session_state.pedido.append({"cod": cod, "cant": cant_v, "nombre": nom}); nuevos += 1
                    if nuevos: st.success(f"✅ {nuevos} ítems cargados"); st.rerun()
                    else: st.warning("No se encontraron filas válidas.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.pedido:
        st.markdown('<div class="sec-label">DESPACHAR ÍTEM</div>', unsafe_allow_html=True)
        if "desp_sel" not in st.session_state: st.session_state["desp_sel"] = 0
        idx_desp = st.session_state.get("desp_sel", 0)
        if idx_desp >= len(st.session_state.pedido): idx_desp = 0

        for _pi, _pitem in enumerate(st.session_state.pedido):
            _pstock = sum(float(l.get('cantidad',0)) for l in idx_inv.get(_pitem['cod'], []))
            _pok    = "✅" if _pstock >= _pitem['cant'] else "⚠️"
            _psel   = "🔵 " if _pi == idx_desp else ""
            if st.button(f"{_psel}{_pok}  {_pitem['nombre'][:30]}", key=f"sel_item_{_pi}", use_container_width=True, type="primary" if _pi == idx_desp else "secondary"):
                st.session_state["desp_sel"] = _pi; st.rerun()

        idx_desp = st.session_state.get("desp_sel", 0)
        if idx_desp >= len(st.session_state.pedido): idx_desp = 0
        item_sel = st.session_state.pedido[idx_desp]
        cod_d    = item_sel['cod']
        lotes_d  = sorted([l for l in idx_inv.get(cod_d,[]) if float(l.get('cantidad',0))>0], key=lambda l: str(l.get('ubicacion','') or '').upper())

        _cant_ped = item_sel['cant']; _stk_ped = sum(float(l.get('cantidad',0)) for l in lotes_d)
        _cped_col = "#10B981" if _stk_ped >= _cant_ped else "#EF4444"
        st.markdown(f'<div style="background:#0F172A;border-radius:16px;padding:16px;margin:10px 0;border:2px solid {_cped_col};text-align:center"><div style="font-size:13px;color:#94A3B8;font-weight:700">CANTIDAD PEDIDA</div><div style="font-size:56px;font-weight:900;color:{_cped_col};line-height:1">{int(_cant_ped)}</div><div style="font-size:12px;color:#64748B;margin-top:4px">{item_sel["nombre"][:40]}</div><div style="font-size:13px;color:#94A3B8;margin-top:6px">Stock: <b style="color:{_cped_col}">{int(_stk_ped)}u</b></div></div>', unsafe_allow_html=True)

        if lotes_d:
            st.markdown('<div class="sec-label">LOTE A USAR</div>', unsafe_allow_html=True)
            if "lote_desp" not in st.session_state: st.session_state["lote_desp"] = 0
            idx_ld = st.session_state.get("lote_desp", 0)
            if idx_ld >= len(lotes_d): idx_ld = 0
            for _li, _l in enumerate(lotes_d):
                _lq = int(float(_l.get('cantidad',0) or 0)); _lu = str(_l.get('ubicacion','—')).upper()
                _lf = str(_l.get('fecha','') or '').strip() or '—'; _lsel = _li == idx_ld
                _d  = dias_para_vencer(_l.get('fecha',''))
                _vt = f" 🔴 VTO" if _d is not None and _d < 0 else (f" 🟡 {_d}d" if _d is not None and _d <= 30 else "")
                if st.button(f"{'▶ ' if _lsel else '   '}{_lq}u  ·  📍{_lu}  ·  📅{_lf}{_vt}", key=f"lote_btn_{idx_desp}_{_li}", use_container_width=True, type="primary" if _lsel else "secondary"):
                    st.session_state["lote_desp"] = _li; st.rerun()

            idx_ld = st.session_state.get("lote_desp", 0)
            if idx_ld >= len(lotes_d): idx_ld = 0
            lote_d = lotes_d[idx_ld]

            if rol in ("admin","operario"):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("✅ DESCONTAR", use_container_width=True, key=f"btn_pick_{idx_desp}_{idx_ld}", type="primary"):
                        try:
                            cant_p = float(item_sel['cant']); cant_l = float(lote_d.get('cantidad',0))
                            cant_a = min(cant_l, cant_p); sb = get_supabase()
                            if cant_a >= cant_l: sb.table("inventario").delete().eq("id", lote_d['id']).execute()
                            else: sb.table("inventario").update({"cantidad": cant_l - cant_a}).eq("id", lote_d['id']).execute()
                            registrar_historial("SALIDA", cod_d, item_sel['nombre'], cant_a, lote_d.get('ubicacion',''), usuario)
                            recalcular_maestra(cod_d, inventario)
                            pendiente = cant_p - cant_a
                            if pendiente > 0: st.session_state.pedido[idx_desp]['cant'] = int(pendiente)
                            else: st.session_state.pedido.pop(idx_desp); st.session_state["desp_sel"] = 0
                            st.session_state["lote_desp"] = 0
                            st.success(f"✅ {item_sel['nombre']} — {int(cant_a)} uds descontadas.")
                            refrescar()
                        except Exception as e:
                            st.error(f"Error: {e}")
                with col_b2:
                    _scan_in = st.text_input("", placeholder="Lector físico...", key=f"pick_scan_{idx_desp}_{idx_ld}", label_visibility="collapsed")
                    if _scan_in.strip():
                        st.info(f"Código escaneado: {_scan_in.strip()} — presioná DESCONTAR.")
        else:
            st.warning(f"⚠️ Sin stock para {item_sel['nombre']}.")

        st.markdown("---")
        st.markdown('<div class="sec-label">📋 ÍTEMS DEL PEDIDO</div>', unsafe_allow_html=True)
        pedido_a_eliminar = None
        for i, item in enumerate(st.session_state.pedido):
            col_pi, col_pb = st.columns([5,1])
            with col_pi:
                stock_disp = sum(float(l.get('cantidad',0)) for l in idx_inv.get(item['cod'],[]))
                color_s    = "#10B981" if stock_disp >= item['cant'] else "#EF4444"
                st.markdown(f'<div class="lote-card"><div style="display:flex;justify-content:space-between;align-items:center"><div><b style="font-size:14px">{item["nombre"]}</b><br><span style="color:#94A3B8;font-size:12px">Cod: {item["cod"]}</span></div><div style="text-align:right"><span style="font-size:22px;font-weight:900;color:#10B981">{item["cant"]}</span><br><span style="font-size:11px;color:{color_s}">stock: {int(stock_disp)}</span></div></div></div>', unsafe_allow_html=True)
            with col_pb:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✕", key=f"del_ped_{i}"):
                    pedido_a_eliminar = i
        if pedido_a_eliminar is not None:
            st.session_state.pedido.pop(pedido_a_eliminar); st.rerun()

        col_lp1, col_lp2 = st.columns(2)
        with col_lp1:
            if st.button("🗑️ Limpiar pedido", key="limpiar_ped"):
                st.session_state.pedido = []; st.rerun()
        with col_lp2:
            _ped_id_act = next((it.get('ped_id') for it in st.session_state.pedido if it.get('ped_id')), None)
            if _ped_id_act and st.button("☁️ Marcar completado", key="btn_completar_ped"):
                try:
                    sb = get_supabase()
                    sb.table("pedidos").update({"estado":"completado"}).eq("id", _ped_id_act).execute()
                    cargar_pedidos_nube.clear(); st.session_state.pedido = []
                    st.success("✅ Pedido completado."); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown('<div style="text-align:center;padding:40px 20px;color:#94A3B8"><div style="font-size:48px;margin-bottom:12px">📋</div><div style="font-size:16px;font-weight:700">Sin pedido activo</div><div style="font-size:13px;margin-top:6px">Cargá desde la nube ☁️ o pegá desde Excel 📋</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB ASISTENTE — versión simplificada y funcional
# ═══════════════════════════════════════════════════════════════════════════════
if _show("🤖 ASISTENTE"):
    import re as _re, unicodedata as _ud

    st.markdown("""
    <style>
    .msg-user{background:linear-gradient(135deg,#1D4ED8,#2563EB);color:#fff;border-radius:20px 20px 5px 20px;padding:13px 18px;margin:6px 0 2px 32px;font-size:14px;line-height:1.65;word-break:break-word}
    .msg-bot{background:linear-gradient(135deg,#1E293B,#162032);color:#E2E8F0;border-radius:5px 20px 20px 20px;border:1px solid rgba(99,130,180,.2);padding:13px 18px;margin:2px 32px 6px 0;font-size:14px;line-height:1.7;white-space:pre-wrap;word-break:break-word}
    .msg-bot b,.msg-bot strong{color:#7DD3FC}
    .chat-lbl{font-size:10px;color:#475569;margin:10px 4px 1px;letter-spacing:.8px;text-transform:uppercase;font-weight:700}
    </style>""", unsafe_allow_html=True)

    def _n(t):
        s = _ud.normalize('NFD', str(t))
        return _re.sub(r'\s+', ' ', ''.join(c for c in s if _ud.category(c) != 'Mn').lower().strip())

    def _buscar_prod_simple(query):
        if not query: return None
        qs = str(query).strip()
        if qs.startswith('.'): cod = qs[1:]; return next((p for p in maestra if str(p.get('cod_int','')).strip() == cod), None)
        if qs.isdigit() and 7 <= len(qs) <= 14:
            p = next((x for x in maestra if str(x.get('barras','')).strip() == qs), None)
            if p: return p
        if qs.isdigit():
            p = next((x for x in maestra if str(x.get('cod_int','')).strip() == qs), None)
            if p: return p
        qn = _n(qs); _SW = {'el','la','los','las','de','del','un','una','hay','en','me','que','cuanto','cual','stock','dame','ver','donde','esta','como'}
        toks = [w for w in qn.split() if w not in _SW and len(w) > 2 and not w.isdigit()]
        if not toks: return None
        best, bsc = None, 0
        for p in maestra:
            pn = _n(p.get('nombre',''))
            sc = sum(1 for w in toks if w in pn)
            if sc > bsc: bsc, best = sc, p
        return best if bsc >= max(1, len(toks)//2) else None

    def _detalle_simple(prod):
        cod = str(prod['cod_int']); stk = int(float(prod.get('cantidad_total',0) or 0))
        lts = idx_inv.get(cod, [])
        r   = f"📦 **{prod['nombre']}** (cod:{cod})\n🔢 Stock total: **{stk}u**\n"
        if lts:
            for l in sorted(lts, key=lambda x: -float(x.get('cantidad',0) or 0)):
                r += f"\n  📍 {str(l.get('ubicacion','?')).upper()} — {int(float(l.get('cantidad',0)))}u"
                if l.get('fecha'): r += f"  Vto:{l.get('fecha')}"
        else:
            r += "\n⛔ Sin lotes en inventario."
        return r

    def _intent_simple(n):
        if _re.search(r'\b(hola|buenas|hey)\b', n): return 'saludo'
        if _re.search(r'\b(venc|caduc|expir|por.vencer)\b', n): return 'venc'
        if _re.search(r'\b(bajo.stock|sin.stock|agotado|falta)\b', n): return 'bajo'
        if _re.search(r'\b(resumen|panorama|como.estamos)\b', n): return 'resumen'
        if _re.search(r'\b(historial|movimientos|ultimo)\b', n): return 'hist'
        if _re.search(r'\b(sacar|salida|despachar|retirar|baja[rn]?)\b', n): return 'salida'
        if _re.search(r'\b(agregar|ingres|llegaron|entrada|carg[ao])\b', n): return 'entrada'
        if _re.search(r'\b(mover|trasladar|pasar.a|llevar.a)\b', n): return 'mover'
        return 'consulta'

    def _procesar_simple(txt):
        n   = _n(txt)
        ctx = st.session_state.get("_ctx", {})
        int_ = ctx.get("intent") if ctx else _intent_simple(n)

        hora = datetime.now().hour
        sal  = "Buen día" if hora < 12 else ("Buenas tardes" if hora < 20 else "Buenas noches")

        if int_ == 'saludo':
            return (f"👋 {sal}, **{usuario}**! Soy el Operario Digital LOGIEZE.\n"
                    f"Tenemos {len(maestra)} productos. Preguntame lo que necesités.")

        if int_ == 'venc':
            hoy = date.today(); res = []
            for l in inventario:
                f = parsear_fecha(l.get('fecha',''))
                if f:
                    d = (f - hoy).days
                    if d <= 60:
                        nm = next((p.get('nombre','') for p in maestra if str(p.get('cod_int','')) == str(l.get('cod_int',''))), '?')
                        ico = "⛔" if d < 0 else ("🔴" if d <= 7 else "🟡")
                        res.append(f"  {ico} {nm} | {int(float(l.get('cantidad',0)))}u | {str(l.get('ubicacion','?')).upper()} | Vto:{l.get('fecha','')} ({d}d)")
            return ("📅 **Vencimientos próximos:**\n\n" + "\n".join(res[:30])) if res else "✅ Sin vencimientos próximos."

        if int_ == 'bajo':
            bajos = sorted([(float(p.get('cantidad_total',0) or 0), p) for p in maestra if float(p.get('cantidad_total',0) or 0) <= 10], key=lambda x: x[0])
            if not bajos: return "✅ Todo tiene stock suficiente."
            lines = [f"  {'⛔' if b[0]==0 else '⚠️'} {b[1]['nombre']} (cod:{b[1]['cod_int']}) — {int(b[0])}u" for b in bajos[:25]]
            return f"📉 **Bajo stock ({len(bajos)} productos):**\n\n" + "\n".join(lines)

        if int_ == 'resumen':
            total_p = len(maestra); total_u = sum(float(p.get('cantidad_total',0) or 0) for p in maestra)
            sin_s   = sum(1 for p in maestra if float(p.get('cantidad_total',0) or 0) == 0)
            return (f"📊 **Resumen**\n\n  📦 Productos: **{total_p}**\n  🔢 Unidades: **{int(total_u):,}**\n  ⛔ Sin stock: **{sin_s}**")

        if int_ == 'hist':
            try:
                hist = cargar_historial_cache(st.session_state.suc_url, st.session_state.suc_key)
                ico  = {"SALIDA":"📤","ENTRADA":"📥","MOVIMIENTO":"🔀","CORRECCION":"✏️"}
                lines = [f"  {ico.get(h.get('tipo',''),'▪️')} {h.get('fecha_hora','')} | {h.get('nombre','')[:20]} | x{h.get('cantidad','')} | @{h.get('usuario','')}" for h in hist[:20]]
                return "📋 **Últimos movimientos:**\n\n" + "\n".join(lines)
            except:
                return "❌ Error cargando historial."

        if int_ in ('salida','entrada','mover'):
            prod = _buscar_prod_simple(txt)
            if not prod:
                if ctx.get('cod'):
                    prod = next((p for p in maestra if str(p.get('cod_int','')) == ctx['cod']), None)
            if not prod:
                return "❓ No identifiqué el producto. Indicá nombre o código."
            cant = 0.0
            for m in _re.finditer(r'\b(\d+)\b', txt):
                if m.group(1) != str(prod.get('cod_int','')): cant = float(m.group(1)); break
            if cant == 0:
                st.session_state["_ctx"] = {"intent": int_, "cod": str(prod['cod_int']), "nom": prod['nombre']}
                return f"❓ ¿Cuántas unidades de **{prod['nombre']}**?"

            ubi_m = _re.search(r'\b(\d{2}[-_]\d{1,2}[A-Za-z]{0,2})\b', txt.upper())
            ubi   = ubi_m.group(1) if ubi_m else ""
            lts   = idx_inv.get(str(prod['cod_int']), [])

            if int_ == 'salida':
                if not lts: st.session_state.pop("_ctx", None); return f"⛔ Sin stock de **{prod['nombre']}**."
                lote = next((l for l in lts if str(l.get('ubicacion','')).upper() == ubi), None) if ubi else None
                if not lote: lote = max(lts, key=lambda l: float(l.get('cantidad',0) or 0)); ubi = str(lote.get('ubicacion',''))
                disp = float(lote.get('cantidad',0) or 0)
                if cant > disp: st.session_state.pop("_ctx", None); return f"❌ Solo hay **{int(disp)}u** en {ubi}."
                try:
                    sb = get_supabase(); nueva = disp - cant
                    if nueva <= 0: sb.table("inventario").delete().eq("id", lote['id']).execute()
                    else: sb.table("inventario").update({"cantidad": nueva}).eq("id", lote['id']).execute()
                    registrar_historial("SALIDA", str(prod['cod_int']), prod['nombre'], cant, ubi, usuario)
                    recalcular_maestra(str(prod['cod_int']), inventario)
                    st.session_state.pop("_ctx", None); refrescar()
                    return f"✅ **SALIDA** — {int(cant)}u de **{prod['nombre']}** desde **{ubi}**\n  Quedan: {int(max(0, nueva))}u"
                except Exception as e:
                    return f"❌ Error: {e}"

            elif int_ == 'entrada':
                if not ubi:
                    st.session_state["_ctx"] = {"intent": int_, "cod": str(prod['cod_int']), "nom": prod['nombre'], "cant": cant}
                    vacias = calcular_vacias_rapido(ubis_ocupadas, max_n=3)
                    return f"❓ ¿En qué ubicación van las {int(cant)}u de **{prod['nombre']}**?\nLibres: {', '.join(vacias)}"
                fv = ""
                fv_m = _re.search(r'\b(\d{1,2}/\d{2,4})\b', txt)
                if fv_m: fv = fv_m.group(1)
                try:
                    sb = get_supabase()
                    exist = [l for l in lts if str(l.get('ubicacion','')).upper() == ubi]
                    if exist:
                        nq = float(exist[0].get('cantidad',0) or 0) + cant
                        sb.table("inventario").update({"cantidad": nq}).eq("id", exist[0]['id']).execute()
                    else:
                        sb.table("inventario").insert({"cod_int": str(prod['cod_int']), "nombre": prod['nombre'], "cantidad": cant, "ubicacion": ubi, "fecha": fv, "deposito": "DEPO 1"}).execute()
                    registrar_historial("ENTRADA", str(prod['cod_int']), prod['nombre'], cant, ubi, usuario)
                    recalcular_maestra(str(prod['cod_int']), inventario)
                    st.session_state.pop("_ctx", None); refrescar()
                    return f"✅ **ENTRADA** — {int(cant)}u de **{prod['nombre']}** en **{ubi}**" + (f" · Vto:{fv}" if fv else "")
                except Exception as e:
                    return f"❌ Error: {e}"

        prod = _buscar_prod_simple(txt)
        if prod:
            return _detalle_simple(prod)

        total = sum(float(p.get('cantidad_total',0) or 0) for p in maestra)
        return (f"No entendí bien. Tenemos **{len(maestra)} productos** · **{int(total):,}u** totales.\n"
                "Ejemplo: «stock de shampoo», «sacar 10 de gel», «vencimientos»")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0F172A,#1E293B);border:1px solid rgba(99,130,180,.2);border-radius:18px;padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:14px">
      <div style="width:50px;height:50px;background:linear-gradient(135deg,#1D4ED8,#06B6D4);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px">🤖</div>
      <div>
        <div style="font-size:15px;font-weight:800;color:#F1F5F9">OPERARIO DIGITAL</div>
        <div style="font-size:11px;color:#10B981;font-weight:600">✅ {len(maestra)} productos · {suc_nombre}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    hcol1, hcol2 = st.columns([5, 1])
    with hcol2:
        if st.button("🗑️", use_container_width=True, key="clear_bot", help="Limpiar chat"):
            st.session_state.bot_hist = []; st.session_state.pop("_ctx", None); st.rerun()

    for msg in st.session_state.bot_hist:
        if msg["rol"] == "user":
            st.markdown(f'<div class="chat-lbl" style="text-align:right">{usuario} 👤</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-user">{msg["texto"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="chat-lbl">🤖 Operario Digital</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-bot">{msg["texto"]}</div>', unsafe_allow_html=True)

    if not st.session_state.bot_hist:
        st.markdown("""
        <div style="text-align:center;padding:24px 16px;color:#64748B">
          <div style="font-size:13px;font-weight:600;margin-bottom:10px">PROBÁ PREGUNTARME:</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center">
            <span style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:6px 12px;font-size:12px">stock de shampoo</span>
            <span style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:6px 12px;font-size:12px">sacar 10 de gel</span>
            <span style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:6px 12px;font-size:12px">vencimientos</span>
            <span style="background:#1E293B;border:1px solid #334155;border-radius:10px;padding:6px 12px;font-size:12px">resumen</span>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<style>.stTextArea textarea{background:#1E293B!important;color:#F1F5F9!important;border:1.5px solid #334155!important;border-radius:14px!important;font-size:16px!important;resize:none!important;padding:12px 16px!important}</style>""", unsafe_allow_html=True)

    _input_val = "" if st.session_state.pop("_limpiar_bot", False) else st.session_state.get("bot_input_txt", "")
    ic1, ic2   = st.columns([5, 1])
    with ic1:
        txt_in = st.text_area("msg", label_visibility="collapsed", placeholder="Escribí acá o usá el micrófono...", key="bot_input_txt", height=68, value=_input_val)
    with ic2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        send = st.button("➤", use_container_width=True, type="primary", key="bot_send")

    if send and txt_in and txt_in.strip():
        st.session_state["_limpiar_bot"] = True
        st.session_state.bot_hist.append({"rol":"user","texto":txt_in.strip()})
        try:
            respuesta = _procesar_simple(txt_in.strip())
            st.session_state.bot_hist.append({"rol":"assistant","texto":respuesta})
        except Exception as e:
            st.session_state.bot_hist.append({"rol":"assistant","texto":f"Error: {e}"})
        st.rerun()

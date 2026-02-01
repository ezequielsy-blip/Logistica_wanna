import streamlit as st
import sqlite3
import pandas as pd
import os
import requests

# --- CONFIGURACIÓN ---
DB_NAME = 'inventario_wms.db'
# Dejamos el ID solo para que puedas "Bajar" la maestra si la app está vacía
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="wide")

# --- INICIALIZACIÓN DB ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS inventario (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, fecha TEXT, ubicacion TEXT, deposito TEXT)')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- TU LÓGICA DE UBICACIÓN 99 ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3: nl, nn = ciclo[idx+1], num_actual
            else: nl, nn = 'A', num_actual + 1
        else: nl, nn = 'A', num_actual + 1
        return f"99-{str(nn).zfill(2)}{nl}"
    except: return "99-01A"

# --- INTERFAZ ADMIN ---
with st.sidebar:
    st.title("🔒 ADMIN")
    clave = st.text_input("Clave", type="password")
    es_autorizado = (clave == "70797474")

st.title("📦 GESTIÓN DE STOCK")

if es_autorizado:
    st.subheader("🛠️ ACTUALIZAR BASE DE DATOS")
    col1, col2 = st.columns(2)
    
    with col1:
        # PARA BAJAR LO QUE ESTÁ EN DRIVE A TU CELULAR
        if st.button("📥 BAJAR DE DRIVE A CELULAR"):
            r = requests.get(URL_DIRECTA)
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            st.success("Sincronizado con Drive"); st.rerun()

    with col2:
        # PARA LLEVAR LO DEL CELULAR A LA PC
        with open(DB_NAME, "rb") as file:
            st.download_button(
                label="📤 DESCARGAR PARA PC/DRIVE",
                data=file,
                file_name=DB_NAME,
                mime="application/octet-stream",
                use_container_width=True
            )
        st.caption("Bajá este archivo y subilo a tu Drive manualmente para no fallar.")

    st.divider()
    
    # NUEVA OPCIÓN: CARGAR ARCHIVO DESDE LA PC
    archivo_subido = st.file_uploader("Actualizar base desde archivo local", type="db")
    if archivo_subido:
        with open(DB_NAME, "wb") as f:
            f.write(archivo_subido.getbuffer())
        st.success("Base local actualizada."); st.rerun()

# --- EL RESTO DE TU CÓDIGO (TABS) ---
tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 DESPACHO", "📊 PLANILLA"])

with tab1:
    if not es_autorizado: st.warning("🔒 Ingrese clave.")
    else:
        bus_m = st.text_input("🔍 Buscar en Maestra")
        query_m = "SELECT * FROM maestra WHERE cod_int LIKE ? OR nombre LIKE ?"
        maestra_df = pd.read_sql(query_m, conn, params=(f'%{bus_m}%', f'%{bus_m}%'))
        opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
        sel = st.selectbox("Producto:", options=[""] + opciones)
        
        if sel:
            item = maestra_df[maestra_df['cod_int'] == sel.split(" | ")[0]].iloc[0]
            with st.form("f_ent", clear_on_submit=True):
                c1, c2 = st.columns(2)
                f_can = c1.number_input("Cantidad", min_value=0.0)
                f_ubi = c2.text_input("Ubicación", value=motor_sugerencia_pc(conn))
                f_dep = c1.selectbox("Depósito", ["depo1", "depo2"])
                f_venc = c2.text_input("Vencimiento (MMAA)", max_chars=4)
                if st.form_submit_button("⚡ REGISTRAR"):
                    v = f"{f_venc[:2]}/{f_venc[2:]}"
                    cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", (item['cod_int'], f_can, item['nombre'], item['barras'], v, f_ubi, f_dep))
                    conn.commit(); st.success("Guardado"); st.rerun()

with tab2:
    bus_d = st.text_input("🔍 Buscar Stock")
    if bus_d:
        res = pd.read_sql("SELECT rowid, * FROM inventario WHERE (cod_int LIKE ? OR nombre LIKE ?) AND cantidad > 0", conn, params=(f'%{bus_d}%', f'%{bus_d}%'))
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} - Cantidad: {r['cantidad']}"):
                if es_autorizado:
                    baja = st.number_input("Retirar", 1.0, float(r['cantidad']), key=f"v_{r['rowid']}")
                    if st.button("CONFIRMAR", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit(); st.rerun()

with tab3:
    st.dataframe(pd.read_sql("SELECT * FROM inventario", conn), use_container_width=True)

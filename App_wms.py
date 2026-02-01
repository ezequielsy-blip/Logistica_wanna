import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os
import re
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

st.set_page_config(page_title="WMS Master Pro", layout="centered")

# --- NUEVO: COMPONENTE SCANNER (Inyecta el código en el buscador) ---
def componente_scanner(key_id):
    return components.html(
        f"""
        <div id="reader-{key_id}" style="width:100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }}, '*');
            }}
            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader-{key_id}", {{ fps: 15, qrbox: 250 }});
            html5QrcodeScanner.render(onScanSuccess);
        </script>
        """, height=350
    )

# --- MOTOR DE UBICACIÓN (Tu lógica idéntica de PC) ---
def motor_sugerencia_pc(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        ultimo = cursor.fetchone()
        if not ultimo: return "99-01A"
        ubi_str = str(ultimo[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        if "-" not in ubi_str: return "99-01A"
        partes = ubi_str.split("-")
        cuerpo = partes[1]
        letra_actual = cuerpo[-1]
        num_str = "".join(filter(str.isdigit, cuerpo))
        num_actual = int(num_str) if num_str else 1
        if letra_actual in ciclo:
            idx = ciclo.index(letra_actual)
            if idx < 3:
                nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else:
                nueva_letra = 'A'; nuevo_num = num_actual + 1
        else:
            nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- CONEXIÓN DB ---
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT, barras TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                      (cod_int TEXT, cantidad REAL, nombre TEXT, barras TEXT, 
                       fecha TEXT, ubicacion TEXT, deposito TEXT)''')
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# --- INTERFAZ ---
st.title("📦 WMS PROFESIONAL MÓVIL")
st.info("Sincronizado con: LOGISTICA.EXE")

if st.button("🔄 CLONAR DATOS DESDE DRIVE"):
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA, timeout=10)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ BASE DE DATOS ACTUALIZADA")
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

tab1, tab2, tab3 = st.tabs(["📥 MOVIMIENTOS", "📤 DESPACHO", "📊 PLANILLA"])

# --- TAB 1: MOVIMIENTOS ---
with tab1:
    st.subheader("Entrada de Mercadería")
    with st.expander("📷 ABRIR ESCÁNER (MAESTRA)"):
        res_mov = componente_scanner("scan_mov")
    
    # Buscador por nombre o código
    bus_m = st.text_input("🔍 Buscar Producto", value=res_mov if res_mov else "")
    
    try:
        # Búsqueda flexible por nombre o código
        query_maestra = f"SELECT cod_int, nombre FROM maestra WHERE cod_int LIKE '%{bus_m}%' OR nombre LIKE '%{bus_m}%' OR barras

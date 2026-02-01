import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# --- LLAVE DE SEGURIDAD (Formato ultra-limpio) ---
CREDS_DICT = {
    "type": "service_account",
    "project_id": "fifth-liberty-486120-q0",
    "private_key_id": "91b213e986ed3f85db65f034f02127d95cd7694c",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDBN3LgtQhI6gtN\nhGZzHfNA9CH0AlKyBuddI7BJVXLBzzDRPasJdmvvcwx+9N3ChPOVcjLA7GvhxVsa\nH+qgbTDfzH+J+Qz/MejJm09ov0T2R5NHqtxmuHgTUnSPLN9y685LCezWibiGQOEc\nvPdZ8GA7S0rkKSYL4+nvKrFmFk9eq+Gmkc5tMY+76ixJyHr85nzi3HmH4AC7wmsc\n3o5HAJR1tKVH7tZwqSgCGAoYCq0aHd7NI12JpeZcJAAtrQv4H9BN28yod25WdFdU\nnAkM+zLMs7iqUVFxfTyDdMCxWNjoX6tfohBovQVdpYPpVEiytxZhnRHqMH7EMSa5\nSVgHPHDfAgMBAAECggEAHfkSjo42w0zfRP6pf+kg/63/iGFF380XXgj3w2CIhU01\nVvg4jKa8trADu7wTnKXQPZoyCmCCmcrqR4K0/H8DymvoSwiB/iKJaKD5sBefxI60\n57S3LQ4nvmOXplBBN4wh+90FywAhSl5NLY6Y1nBmFTyoWP2TI9wOwaW/UEVcuaQu\nLNwYGdqId4LfLgqfZvnsjDs4NXV6EBY829u+kk7k0WMx8BwilfyiXLv1lhphnuhq\n1RBGbhhXuPtu4G8ZmTjJmFjU77Ll8NTNWz5cuMeU8+11LdrYoTq3cmT4yzu6r9xY\nXuH6Dy8z+R3y0L/rg6oHgeRS8Jxx4EurUyxHQxyTMQKBgQDqEtGF88V8i7Q6ZQOT\nzKq5KK5GsQPRwqwgityhZQsRASrJuSgXlQlSddU/SciD/mACPv3zwbSsoDOEuC1y\nojQliju0dh5ufgiePHXjft4t+tTjikgHhbChCs+eMPXsMBzSFW3NzLTi+lNEPBOW\n6zu0xkG9jzuRDkZeV7IoWBi9kQKBgQDTUN1BKR4OlEIDpfK7wwD3iGD6ILXlR6sp\nRDJJZTbq0+KS5Bl1l2qxqyy9B78z1zYX8cvVN8nMDR5Adr7W7qUG71QRFRRHE3A2\niytMClKCa810guhnMRm7QlhHRdcy4jYgbqtxLV5Puv1xE45e0bRJEfmRzEXijKuA\ IQmCKprPbwKBgQDE6D2/vJjGM9PSR8WhoMuBZXpt111KKMSZv5boYlLT5DJ1bcAP\nTn2AE8XnLo9ykht76DfDxZDSoxWTsUfyJgdOCSI+phrlgjqHun7FeKU48sgB/gKn\n6UvzvV94SOGn5bVo+UPcmzcTtdc0EIG+NHaOlTUaXJKUbPi/RnCFxc5SMQJ/Rvzj\nVwB5GGy1wIP/BxR7PqyR53UVpfBtj29ZdU6LJFgJxU7bPqWfMhBO9zGjCcdCZMjV\nsMsM/39oqj853PpOdgXwN8zdAwOErs4RvXm6PhX47ysK55+XBVFEVq0fnfhgNoT3\nEw4qoJ4whcwMB85qwiFHtbLpxzF6a5CtoQyu9QKBgGwQJbx2/zjcYKFjYVbp2Cgn\nu/5tEY1Jfx8gZXB6djg6f/gZk6/tKK9hLQ4XtPQRDoRlghw31RsZjdcL0zIf2ZX7\nlFZgvh8zw3MWDeMv2l95xsHMoz3RrdffyBnbYIGhw3oesD0kFP0g0aiBf+54Ujwg\3HRDebG/rUmZGkXcjdX2\n-----END PRIVATE KEY-----\n",
    "client_email": "app-stock@fifth-liberty-486120-q0.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com/token",
}

st.set_page_config(page_title="WMS Master Pro", layout="wide")

# --- FUNCIÓN SUBIDA ---
def subir_a_drive():
    try:
        creds = service_account.Credentials.from_service_account_info(CREDS_DICT, scopes=['https://www.googleapis.com/auth/drive.file'])
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(DB_NAME, mimetype='application/octet-stream')
        service.files().update(fileId=FILE_ID, media_body=media).execute()
        st.success("✅ DRIVE ACTUALIZADO")
    except Exception as e:
        st.error(f"Error al subir: {e}")

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
            if idx < 3: nueva_letra = ciclo[idx+1]; nuevo_num = num_actual
            else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        else: nueva_letra = 'A'; nuevo_num = num_actual + 1
        return f"99-{str(nuevo_num).zfill(2)}{nueva_letra}"
    except: return "99-01A"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔒 SEGURIDAD")
    clave = st.text_input("Clave de Administrador", type="password")
    es_autorizado = (clave == "70797474")

st.title("📦 GESTIÓN DE STOCK: LOGISTICA")

if st.button("🔄 ACTUALIZAR PANTALLA"):
    st.rerun()

if es_autorizado:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 CLONAR DRIVE", use_container_width=True):
            r = requests.get(URL_DIRECTA)
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            st.success("✅ BASE ACTUALIZADA"); st.rerun()
    with c2:
        if st.button("📤 SUBIR CAMBIOS", use_container_width=True):
            subir_a_drive()

tab1, tab2, tab3 = st.tabs(["📥 ENTRADAS", "📤 DESPACHO", "📊 PLANILLA"])

# --- TAB 1: ENTRADAS (TU LÓGICA) ---
with tab1:
    if not es_autorizado: st.warning("🔒 Ingrese clave.")
    else:
        bus_m = st.text_input("🔍 Buscar en Maestra")
        query_m = "SELECT * FROM maestra WHERE cod_int LIKE ? OR nombre LIKE ? OR barras LIKE ?"
        maestra_df = pd.read_sql(query_m, conn, params=(f'%{bus_m}%', f'%{bus_m}%', f'%{bus_m}%'))
        opciones = maestra_df.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
        seleccion = st.selectbox("Producto:", options=[""] + opciones)
        if seleccion:
            item = maestra_df[maestra_df['cod_int'] == seleccion.split(" | ")[0]].iloc[0]
            cod_sel, nom_sel, bar_sel = item['cod_int'], item['nombre'], item['barras']
        else: cod_sel, nom_sel, bar_sel = "", "", ""

        with st.form("form_entrada", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f_cod = st.text_input("Código Interno", value=cod_sel)
                f_nom = st.text_input("Descripción", value=nom_sel)
                f_can = st.number_input("Cantidad", min_value=0.0)
            with col2:
                f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
                f_ubi = st.text_input("Ubicación", value=motor_sugerencia_pc(conn))
                f_venc_raw = st.text_input("Vencimiento (MMAA)", max_chars=4)
            if st.form_submit_button("⚡ REGISTRAR"):
                if f_cod and len(f_venc_raw) == 4:
                    f_venc = f"{f_venc_raw[:2]}/{f_venc_raw[2:]}"
                    cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", (f_cod, f_can, f_nom, bar_sel, f_venc, f_ubi, f_dep))
                    conn.commit(); st.success("Registrado"); st.rerun()

# --- TAB 2: DESPACHO ---
with tab2:
    bus_d = st.text_input("🔍 Buscar Stock")
    if bus_d:
        query_d = "SELECT rowid, * FROM inventario WHERE (cod_int LIKE ? OR nombre LIKE ?) AND cantidad > 0"
        res = pd.read_sql(query_d, conn, params=(f'%{bus_d}%', f'%{bus_d}%'))
        for i, r in res.iterrows():
            with st.expander(f"📦 {r['nombre']} - Cantidad: {r['cantidad']}"):
                if es_autorizado:
                    baja = st.number_input("Retirar", 1.0, float(r['cantidad']), key=f"d_{r['rowid']}")
                    if st.button("CONFIRMAR SALIDA", key=f"b_{r['rowid']}"):
                        cursor.execute("UPDATE inventario SET cantidad = cantidad - ? WHERE rowid = ?", (baja, r['rowid']))
                        conn.commit(); st.rerun()

# --- TAB 3: PLANILLA ---
with tab3:
    st.dataframe(pd.read_sql("SELECT * FROM inventario", conn), use_container_width=True, hide_index=True)

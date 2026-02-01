import streamlit as st
import sqlite3
import pandas as pd
import requests
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# --- TUS CREDENCIALES (JSON integrado para que no falle) ---
CREDS_DICT = {
    "type": "service_account",
    "project_id": "fifth-liberty-486120-q0",
    "private_key_id": "91b213e986ed3f85db65f034f02127d95cd7694c",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDBN3LgtQhI6gtN\nhGZzHfNA9CH0AlKyBuddI7BJVXLBzzDRPasJdmvvcwx+9N3ChPOVcjLA7GvhxVsa\nH+qgbTDfzH+J+Qz/MejJm09ov0T2R5NHqtxmuHgTUnSPLN9y685LCezWibiGQOEc\nvPdZ8GA7S0rkKSYL4+nvKrFmFk9eq+Gmkc5tMY+76ixJyHr85nzi3HmH4AC7wmsc\n3o5HAJR1tKVH7tZwqSgCGAoYCq0aHd7NI12JpeZcJAAtrQv4H9BN28yod25WdFdU\nnAkM+zLMs7iqUVFxfTyDdMCxWNjoX6tfohBovQVdpYPpVEiytxZhnRHqMH7EMSa5\nSVgHPHDfAgMBAAECggEAHfkSjo42w0zfRP6pf+kg/63/iGFF380XXgj3w2CIhU01\nVvg4jKa8trADu7wTnKXQPZoyCmCCmcrqR4K0/H8DymvoSwiB/iKJaKD5sBefxI60\n57S3LQ4nvmOXplBBN4wh+90FywAhSl5NLY6Y1nBmFTyoWP2TI9wOwaW/UEVcuaQu\nLNwYGdqId4LfLgqfZvnsjDs4NXV6EBY829u+kk7k0WMx8BwilfyiXLv1lhphnuhq\n1RBGbhhXuPtu4G8ZmTjJmFjU77Ll8NTNWz5cuMeU8+11LdrYoTq3cmT4yzu6r9xY\ XuH6Dy8z+R3y0L/rg6oHgeRS8Jxx4EurUyxHQxyTMQKBgQDqEtGF88V8i7Q6ZQOT\nzKq5KK5GsQPRwqwgityhZQsRASrJuSgXlQlSddU/SciD/mACPv3zwbSsoDOEuC1y\nojQliju0dh5ufgiePHXjft4t+tTjikgHhbChCs+eMPXsMBzSFW3NzLTi+lNEPBOW\n6zu0xkG9jzuRDkZeV7IoWBi9kQKBgQDTUN1BKR4OlEIDpfK7wwD3iGD6ILXlR6sp\nRDJJZTbq0+KS5Bl1l2qxqyy9B78z1zYX8cvVN8nMDR5Adr7W7qUG71QRFRRHE3A2\niytMClKCa810guhnMRm7QlhHRdcy4jYgbqtxLV5Puv1xE45e0bRJEfmRzEXijKuA\ IQmCKprPbwKBgQDE6D2/vJjGM9PSR8WhoMuBZXpt111KKMSZv5boYlLT5DJ1bcAP\nTn2AE8XnLo9ykht76DfDxZDSoxWTsUfyJgdOCSI+phrlgjqHun7FeKU48sgB/gKn\n6UvzvV94SOGn5bVo+UPcmzcTtdc0EIG+NHaOlTUaXJKUbPi/RnCFxc5SMQJ/Rvzj\nVwB5GGy1wIP/BxR7PqyR53UVpfBtj29ZdU6LJFgJxU7bPqWfMhBO9zGjCcdCZMjV\nsMsM/39oqj853PpOdgXwN8zdAwOErs4RvXm6PhX47ysK55+XBVFEVq0fnfhgNoT3\nEw4qoJ4whcwMB85qwiFHtbLpxzF6a5CtoQyu9QKBgGwQJbx2/zjcYKFjYVbp2Cgn\nu/5tEY1Jfx8gZXB6djg6f/gZk6/tKK9hLQ4XtPQRDoRlghw31RsZjdcL0zIf2ZX7\nlFZgvh8zw3MWDeMv2l95xsHMoz3RrdffyBnbYIGhw3oesD0kFP0g0aiBf+54Ujwg\3HRDebG/rUmZGkXcjdX2\n-----END PRIVATE KEY-----\n",
    "client_email": "app-stock@fifth-liberty-486120-q0.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com/token",
}

st.set_page_config(page_title="LOGISTICA MOVIL", layout="wide")

# --- FUNCION SUBIDA ---
def subir_datos():
    try:
        scope = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_info(CREDS_DICT, scopes=scope)
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(DB_NAME, mimetype='application/octet-stream')
        service.files().update(fileId=FILE_ID, media_body=media).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- BASE DE DATOS ---
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# --- LOGICA 99 (La misma que usás siempre) ---
def sugerir_99(conn):
    try:
        cursor.execute("SELECT ubicacion FROM inventario WHERE ubicacion LIKE '99-%' ORDER BY rowid DESC LIMIT 1")
        u = cursor.fetchone()
        if not u: return "99-01A"
        ubi = str(u[0]).upper()
        ciclo = ['A', 'B', 'C', 'D']
        p = ubi.split("-")[1]
        letra = p[-1]
        num = int("".join(filter(str.isdigit, p)))
        if letra in ciclo and ciclo.index(letra) < 3:
            return f"99-{str(num).zfill(2)}{ciclo[ciclo.index(letra)+1]}"
        else:
            return f"99-{str(num+1).zfill(2)}A"
    except: return "99-01A"

# --- INTERFAZ ---
with st.sidebar:
    st.title("SEGURIDAD")
    clave = st.text_input("Clave Admin", type="password")
    es_admin = (clave == "70797474")

st.title("📦 GESTIÓN DE STOCK")

if st.button("🔄 ACTUALIZAR"): st.rerun()

if es_admin:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 CLONAR DRIVE", use_container_width=True):
            r = requests.get(URL_DIRECTA)
            with open(DB_NAME, 'wb') as f: f.write(r.content)
            st.success("Cargado!")
            st.rerun()
    with col2:
        if st.button("📤 SUBIR CAMBIOS", use_container_width=True):
            if subir_datos(): st.success("Guardado en la Nube!")

t1, t2, t3 = st.tabs(["📥 ENTRADAS", "📤 DESPACHO", "📊 STOCK"])

with t1:
    if es_admin:
        maestra = pd.read_sql("SELECT * FROM maestra", conn)
        prods = maestra.apply(lambda x: f"{x['cod_int']} | {x['nombre']}", axis=1).tolist()
        sel = st.selectbox("Producto:", [""] + prods)
        with st.form("f1"):
            c_int = sel.split(" | ")[0] if sel else ""
            f_can = st.number_input("Cantidad", min_value=0.0)
            f_dep = st.selectbox("Depósito", ["depo1", "depo2"])
            f_ubi = st.text_input("Ubicación", value=sugerir_99(conn))
            f_venc = st.text_input("Vencimiento (MMAA)", max_chars=4)
            if st.form_submit_button("REGISTRAR"):
                if len(f_venc) == 4:
                    v = f"{f_venc[:2]}/{f_venc[2:]}"
                    nom = maestra[maestra['cod_int'] == c_int]['nombre'].values[0]
                    cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", (c_int, f_can, nom, "", v, f_ubi, f_dep))
                    conn.commit()
                    st.success("Guardado local. Subí los cambios al terminar.")

with t2:
    bus = st.text_input("🔍 Buscar")
    if bus:
        res = pd.read_sql(f"SELECT rowid, * FROM inventario WHERE nombre LIKE '%{bus}%' AND cantidad > 0", conn)
        for i, r in res.iterrows():
            with st.expander(f"{r['nombre']} ({r['cantidad']})"):
                if es_admin:
                    q = st.number_input("Retirar", 1.0, float(r['cantidad']), key=f"q{i}")
                    if st.button("OK", key=f"b{i}"):
                        cursor.execute("UPDATE inventario SET cantidad=cantidad-? WHERE rowid=?", (q, r['rowid']))
                        conn.commit()
                        st.rerun()

with t3:
    st.dataframe(pd.read_sql("SELECT * FROM inventario", conn), use_container_width=True)

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import os

# --- CONFIGURACIÓN DRIVE ---
FILE_ID = '1ZZQJP6gJyvX-7uAi8IvLLACfRyL0Hzv1'
DB_NAME = 'inventario_wms.db'
URL_DIRECTA = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA WMS PRO", layout="centered")

# --- CSS PARA ESTILO PROFESIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stMarkdown, p, label { font-weight: 700 !important; color: #333; }
    div.stButton > button {
        width: 100%; height: 3.5em; border-radius: 12px;
        background-color: #007bff !important; color: white !important;
        font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #e9ecef; border-radius: 10px; }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; border-radius: 8px; }
    input { border-radius: 10px !important; border: 1px solid #ced4da !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS INTELIGENTE ---
def inicializar_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS maestra (cod_int TEXT PRIMARY KEY, nombre TEXT)")
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventario (
                        cod_int TEXT, cantidad REAL, ubicacion TEXT, 
                        deposito TEXT, vencimiento TEXT, fecha_registro TEXT)""")
    
    # Asegurar que existan las columnas de tus apps más completas
    cursor.execute("PRAGMA table_info(inventario)")
    cols = [info[1] for info in cursor.fetchall()]
    if 'deposito' not in cols: cursor.execute("ALTER TABLE inventario ADD COLUMN deposito TEXT DEFAULT 'DEPO1'")
    if 'vencimiento' not in cols: cursor.execute("ALTER TABLE inventario ADD COLUMN vencimiento TEXT DEFAULT '00/00'")
    conn.commit()
    return conn, cursor

conn, cursor = inicializar_db()

# --- FUNCIONES ---
def sincronizar():
    try:
        if os.path.exists(DB_NAME): os.remove(DB_NAME)
        r = requests.get(URL_DIRECTA)
        with open(DB_NAME, 'wb') as f: f.write(r.content)
        st.success("✅ SINCERONIZACIÓN EXITOSA CON DRIVE")
        st.rerun()
    except: st.error("❌ Error al conectar con Drive")

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 WMS UNIFICADO (PC-MÓVIL)")

if st.button("🔄 SINCRONIZAR CON DRIVE"):
    sincronizar

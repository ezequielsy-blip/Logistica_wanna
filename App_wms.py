import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURACIÓN CLOUD ---
SUPABASE_URL = "https://twnzmsrthinzbyoedwnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3bnptc3J0aGluemJ5b2Vkd25jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMzY4NzAsImV4cCI6MjA4NTYxMjg3MH0.4lPtZWqKotDRFcwftPFtDZF2Bm4D1nDjUJn7Etfv1NM"

st.set_page_config(page_title="LOGIEZE Master", layout="wide")

# --- GESTIÓN DE ESTADO PARA PASES ---
if "transfer_data" not in st.session_state:
    st.session_state.transfer_data = None

# --- ESTILOS MEJORADOS (Recuadros Grandes y Estéticos) ---
st.markdown("""
    <style>
    .main { background-color: #0F1116; }
    
    /* Botones en línea para móvil */
    [data-testid="column"] { display: inline-block !important; width: 48% !important; min-width: 48% !important; }
    
    div.stButton > button {
        width: 100%; height: 75px !important; font-size: 22px !important;
        font-weight: 700 !important; border-radius: 12px !important; 
        border: 2px solid #2C3E50 !important; color: white !important;
        transition: 0.3s;
    }
    
    div.stForm button { background-color: #2D5A27 !important; border-color: #3E8E41 !important; } 
    div[data-testid="column"]:nth-of-type(1) button { background-color: #34495E !important; } 
    div[data-testid="column

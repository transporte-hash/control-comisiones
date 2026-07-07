import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Control de Comisiones - Conductores",
    page_icon="🚚",
    layout="centered"
)

# Estilo corporativo personalizado
st.markdown("""
    <style>
    .main-title {
        color: #1E3A8A;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-size: 16px;
        width: 100%;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #152E72;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚚 Registro de Comisiones de Conductores</div>', unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN ROBUSTA A GOOGLE SHEETS
# ==========================================
@st.cache_resource
def conectar_gsheets():
    # Extrae el diccionario completo de credenciales desde Streamlit Secrets
    credenciales_dict = st.secrets["connections"]["gsheets"]
    
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Autorización segura con Google
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)
    cliente = gspread.authorize(creds)
    
    # SELECCIÓN POR NOMBRE: Abre el archivo por su nombre oficial en tu Drive
    sheet = cliente.open("Base_Control_Comision_Conductores").sheet1
    return sheet

# Inicializar conexión a la hoja de cálculo
try:
    hoja = conectar_gsheets()
except Exception as e:
    st.error(f"❌ Error crítico de conexión con Google Sheets: {e}")
    st.info("💡 RECUERDA: Verifica que hayas compartido tu archivo de Google Sheets con el correo virtual ('client_email') que aparece en tus Secrets.")
    st.stop()

# ==========================================
# 3. INTERFAZ DEL FORMULARIO DE REGISTRO
# ==========================================
with st.form(key="form_comisiones", clear_on_submit=True):
    st.subheader("📋 Datos del Viaje")
    
    fecha = st.date_input("Fecha del viaje", value=datetime.today())
    conductor = st.text_input("Nombre completo del Conductor").strip()
    cedula = st.text_input("Número de Cédula (sin puntos ni comas)").strip()
    destino = st.text_input("Destino del viaje").strip()
    contenedor = st.text_input("Número de Contenedor").strip()
    zorro = st.text_input("Número de Zorro").strip()
    numero_viaje = st.text_input("Número de Viaje").strip()
    
    # Botón de envío
    boton_guardar = st.form_submit_button(label="💾 Guardar Registro")

# ==========================================
# 4. LÓGICA DE PROCESAMIENTO Y GUARDADO
# ==========================================
if boton_guardar:
    # Validación básica de campos vacíos
    if not conductor or not cedula or not destino or not contenedor or not zorro or not numero_viaje:
        st.warning("⚠️ Por favor, completa todos los campos del formulario antes de guardar.")
    else:
        with st.spinner("Subiendo datos a Google Sheets... Por favor espera."):
            try:
                # Formateamos la fecha a texto (Año-Mes-Día)
                fecha_texto = fecha.strftime("%Y-%m-%d")
                
                # Creamos la fila exactamente en el orden de tus columnas (A hasta G)
                nueva_fila = [
                    fecha_texto,   # Columna A: FECHA
                    conductor,     # Columna B: CONDUCTOR
                    cedula,        # Columna C: CEDULA
                    destino,       # Columna D: DESTINO
                    contenedor,    # Columna E: CONTENEDOR
                    zorro,         # Columna F: ZORRO
                    numero_viaje   # Columna G: NUMERO_VIAJE
                ]
                
                # Inserción directa al final de la tabla
                hoja.append_row(nueva_fila)
                
                st.success(f"✅ ¡Excelente! El viaje N° {numero_viaje} de {conductor} fue registrado con éxito.")
                
            except Exception as error_guardado:
                st.error(f"❌ Ocurrió un error al intentar escribir en la planilla: {error_guardado}")
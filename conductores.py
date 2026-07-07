import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Control de Comisiones - Conductores",
    page_icon="🚚",
    layout="centered"
)

# Estilo corporativo personalizado (Mantiene tu diseño intacto)
st.markdown("""
    <style>
    .main-title {
        color: #1E3A8A;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 🖼️ MUESTRA TU LOGO CORPORATIVO ARRIBA DEL TODO
# Revisa si el archivo existe en tu carpeta y lo coloca antes del título
if os.path.exists("logo_empresa.png"):
    st.image("logo_empresa.png", use_container_width=False, width=200)

st.markdown('<div class="main-title">🚚 Registro de Comisiones de Conductores</div>', unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN DIRECTA Y SEGURA A GOOGLE SHEETS
# ==========================================
@st.cache_resource
def conectar_gsheets():
    # Extrae las credenciales seguras de tus Secrets en Streamlit Cloud
    credenciales_dict = st.secrets["connections"]["gsheets"]
    
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Autorización con la Service Account de Google
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scope)
    cliente = gspread.authorize(creds)
    
    # Abre tu archivo por su nombre oficial exacto
    sheet = cliente.open("Base_Control_Comision_Conductores").sheet1
    return sheet

# Inicializar conexión a la hoja de cálculo
try:
    hoja = conectar_gsheets()
except Exception as e:
    st.error(f"❌ Error de conexión con Google Sheets: {e}")
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
    
    # Botón original para enviar el formulario
    boton_guardar = st.form_submit_button(label="💾 Guardar Registro")

# ==========================================
# 4. LÓGICA DE ALMACENAMIENTO EXCEL
# ==========================================
if boton_guardar:
    if not conductor or not cedula or not destino or not contenedor or not zorro or not numero_viaje:
        st.warning("⚠️ Por favor, completa todos los campos del formulario antes de guardar.")
    else:
        with st.spinner("Guardando registro en Google Sheets..."):
            try:
                # Convierte la fecha seleccionada a texto legible (Año-Mes-Día)
                fecha_texto = fecha.strftime("%Y-%m-%d")
                
                # Estructura ordenada de tus columnas en Excel (De la A hasta la G)
                nueva_fila = [
                    fecha_texto,   # Columna A: FECHA
                    conductor,     # Columna B: CONDUCTOR
                    cedula,        # Columna C: CEDULA
                    destino,       # Columna D: DESTINO
                    contenedor,    # Columna E: CONTENEDOR
                    zorro,         # Columna F: ZORRO
                    numero_viaje   # Columna G: NUMERO_VIAJE
                ]
                
                # Inserta los datos al final de la hoja de cálculo
                hoja.append_row(nueva_fila)
                st.success(f"✅ ¡Excelente! El viaje N° {numero_viaje} de {conductor} fue registrado con éxito.")
                
            except Exception as error_guardado:
                st.error(f"❌ Ocurrió un error al intentar escribir en la planilla: {error_guardado}")
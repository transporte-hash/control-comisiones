import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os

# =========================================================================
# CONFIGURACIÓN DE PÁGINA (Protección contra traducción automática de Chrome)
# =========================================================================
st.set_page_config(
    page_title="Control de Comisiones",
    page_icon="🚛",
    layout="centered"
)

# Parche de seguridad: Evita que extensiones de traducción rompan el DOM de la App
st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            text-align: left !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# GESTIÓN DEL LOGOTIPO CORPORATIVO
# =========================================================================
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(carpeta_actual, "logo_empresa.png")

if os.path.exists(ruta_logo):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(ruta_logo, use_container_width=True)
else:
    st.markdown("<h2 style='text-align: center;'>🚛 CILA FOODS</h2>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>Control de Comisiones - Conductores</h3>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# ENLACE SEGURO A LA BASE DE DATOS (Google Sheets)
# =========================================================================
conexion_establecida = False
df_base_datos = pd.DataFrame()

try:
    # Inicializa el conector nativo de Streamlit
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lectura en tiempo real (ttl=0 asegura traer datos frescos siempre)
    df_base_datos = conn.read(ttl=0)
    conexion_establecida = True
except Exception as e:
    st.error("❌ Error de Infraestructura: No se pudo sincronizar la base de datos.")
    st.info(f"Reporte técnico para TI: {e}")

# =========================================================================
# FORMULARIO CRÍTICO DE PRODUCCIÓN
# =========================================================================
with st.form("formulario_comisiones_empresa", clear_on_submit=True):
    st.subheader("📝 Datos Obligatorios del Viaje")
    
    conductor = st.text_input("Nombre Completo del Conductor")
    cedula = st.text_input("Número de Cédula de Identidad")
    destino = st.text_input("Destino de la Ruta")
    
    st.markdown("---")
    st.subheader("📦 Detalles de la Carga")
    
    contenedor = st.text_input("Número de Contenedor")
    zorro = st.text_input("Identificación del Zorro / Remolque")
    numero_viaje = st.number_input("Número de Viaje", min_value=1, step=1, value=1)
    
    boton_enviar = st.form_submit_button("🚀 Enviar Registro de Comisión")

# =========================================================================
# PROCESAMIENTO Y VALIDACIÓN ANTI-DAÑOS
# =========================================================================
if boton_enviar:
    # Sanitización: Eliminamos espacios accidentales que metan los conductores en el celular
    c_conductor = conductor.strip().upper()
    c_cedula = cedula.strip()
    c_destino = destino.strip().upper()
    c_contenedor = contenedor.strip().upper()
    c_zorro = zorro.strip().upper()

    # Validación 1: Campos obligatorios vacíos
    if not c_conductor or not c_cedula or not c_contenedor:
        st.error("⚠️ Registro Rechazado: Los campos 'Conductor', 'Cédula' y 'Contenedor' son obligatorios para los indicadores.")
    
    # Validación 2: Estado de la red con Google Sheets
    elif not conexion_establecida:
        st.error("❌ Error de Red: El registro no pudo ser guardado porque la conexión con el Excel está caída. Intente de nuevo.")
        
    else:
        try:
            with st.spinner("Guardando de forma segura en la base de datos corporativa..."):
                # Marca de tiempo estándar
                stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Crear la nueva fila respetando estrictamente las columnas del Excel
                nueva_fila = pd.DataFrame([{
                    "FECHA": str(stamp),
                    "CONDUCTOR": str(c_conductor),
                    "CEDULA": str(c_cedula),
                    "DESTINO": str(c_destino),
                    "CONTENEDOR": str(c_contenedor),
                    "ZORRO": str(c_zorro),
                    "NUMERO_VIAJE": int(numero_viaje)
                }])
                
                # Consolidar datos anteriores sin alterar la estructura original
                df_final = pd.concat([df_base_datos, nueva_fila], ignore_index=True)
                
                # Guardar en la nube de Google Sheets
                conn.update(data=df_final)
                
                st.success(f"✅ ¡Éxito! Viaje guardado correctamente para {c_conductor}.")
                st.balloons()
                
        except Exception as error_guardado:
            st.error(f"❌ No se pudieron escribir los datos en el Excel: {error_guardado}")
            st.warning("Asegúrese de que el enlace de Google Sheets no haya perdido los permisos públicos de 'Editor'.")
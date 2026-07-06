import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Control de Comisiones - Transporte",
    page_icon="🚛",
    layout="centered"
)

# Mostrar logo de la empresa si existe en el directorio
try:
    st.image("logo_empresa.png.png", width=200)
except:
    pass

st.title("📋 Registro de Comisiones de Conductores")
st.write("Ingrese los datos del viaje realizado para actualizar la base de datos de forma segura.")

# ---------------------------------------------------------
# CONEXIÓN DIRECTA A GOOGLE SHEETS
# ---------------------------------------------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Leer los datos actuales de la hoja de cálculo
    df_base_datos = conn.read(ttl="0d")  # ttl="0d" evita que la app guarde datos viejos en caché
except Exception as e:
    st.error(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# ---------------------------------------------------------
# FORMULARIO DE ENTRADA DE DATOS
# ---------------------------------------------------------
with st.form(key="formulario_viaje", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        c_conductor = st.text_input("👤 Nombre Completo del Conductor:").strip().upper()
        c_cedula = st.text_input("🪪 Número de Cédula / Identificación:").strip()
        c_destino = st.text_input("📍 Destino del Viaje:").strip().upper()
        
    with col2:
        c_contenedor = st.text_input("📦 Número de Contenedor:").strip().upper()
        c_zorro = st.text_input("🦊 Número de Zorro / Chasis:").strip().upper()
        numero_viaje = st.number_input("🔢 Número de Viaje del Día:", min_value=1, max_value=20, step=1, value=1)

    # Botón de envío del formulario
    submit_button = st.form_submit_button(label="🚀 Registrar Viaje y Comisión")

# ---------------------------------------------------------
# VALIDACIÓN Y PROCESAMIENTO DE DATOS
# ---------------------------------------------------------
if submit_button:
    # Validar que los campos obligatorios no estén vacíos
    if not c_conductor or not c_cedula or not c_destino or not c_contenedor or not c_zorro:
        st.warning("⚠️ Todos los campos son obligatorios. Por favor, rellene el formulario por completo.")
    else:
        try:
            with st.spinner("Guardando de forma segura en la base de datos corporativa..."):
                # Generar fecha y hora exacta del registro
                stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
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
import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection  # <--- CAMBIADO A SU NOMBRE REAL COMPLETO
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA (Títulos y Diseño Corporativo)
st.set_page_config(
    page_title="Registro de Comisiones de Conductores", 
    layout="centered"
)

# Encabezado con formato HTML limpio para presentación visual
st.markdown("<h2 style='text-align: center;'>📝 Registro de Comisiones de Conductores</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Ingrese los datos del viaje realizado para actualizar la base de datos de forma segura.</p>", unsafe_allow_html=True)

# 2. CONEXIÓN INICIAL NATIVA CON GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"⚠️ Error crítico al inicializar los componentes de conexión: {e}")

# 3. INTERFAZ GRÁFICA DEL FORMULARIO (Dos Columnas Simétricas)
with st.form(key="formulario_viaje", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        c_conductor = st.text_input("👤 Nombre Completo del Conductor:")
        c_cedula = st.text_input("🆔 Número de Cédula:")
        c_destino = st.text_input("📍 Destino del Viaje:")
        
    with col2:
        c_contenedor = st.text_input("📦 Número de Contenedor:")
        c_zorro = st.text_input("🚜 Número de Zorro / Placa:")
        c_viaje = st.text_input("🔢 Número de Viaje:")

    # Botón de envío del formulario
    submit_button = st.form_submit_button(label="Guardar Registro de Viaje")

# 4. PROCESAMIENTO Y VALIDACIÓN LOGÍSTICA DE DATOS
if submit_button:
    if not c_conductor or not c_cedula or not c_destino or not c_contenedor or not c_zorro or not c_viaje:
        st.warning("⚠️ Todos los campos son obligatorios. Por favor, rellene el formulario por completo.")
    else:
        try:
            with st.spinner("Conectando de forma segura con la base de datos corporativa..."):
                
                # A. Lectura en tiempo real de la hoja de cálculo
                df_existente = conn.read(ttl=0)
                
                # B. Generación de la marca de tiempo y limpieza de textos
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                nuevo_registro = pd.DataFrame([{
                    "FECHA": fecha_actual,
                    "CONDUCTOR": c_conductor.strip().upper(),
                    "CEDULA": c_cedula.strip(),
                    "DESTINO": c_destino.strip().upper(),
                    "CONTENEDOR": c_contenedor.strip().upper(),
                    "ZORRO": c_zorro.strip().upper(),
                    "NUMERO_VIAJE": c_viaje.strip()
                }])
                
                # C. Combinación de los datos nuevos con el histórico existente
                if df_existente is not None and not df_existente.empty:
                    df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                else:
                    df_actualizado = nuevo_registro
                
                # D. Escritura y actualización final en Google Sheets
                conn.update(data=df_actualizado)
                
                # Notificación de éxito en pantalla
                st.success("✅ ¡Registro guardado exitosamente en Google Sheets!")
                
        except Exception as e:
            st.error(f"❌ Error de comunicación con la API de Google Sheets: {e}")
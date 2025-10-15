import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import sys

# =======================================================
# 1. CONFIGURACIÓN
# =======================================================
# La URL de tu API de Render (la misma utilizada anteriormente)
RENDER_API_URL = "https://radiografia-ia-api.onrender.com/classify"

st.set_page_config(page_title="Clasificador de Radiografías", layout="centered")
st.title("🩺 Clasificador de Radiografías IA")
st.markdown("Sube una imagen de radiografía para obtener la clasificación de nuestra IA.")

# =======================================================
# 2. CAPTURA DE ARCHIVO Y PREVISUALIZACIÓN
# =======================================================

uploaded_file = st.file_uploader(
    "Selecciona la imagen de la radiografía (JPG/PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    try:
        # Abrir y mostrar la imagen subida
        # Utiliza un archivo 'BytesIO' para que Image.open() pueda leer el archivo subido
        image_bytes = BytesIO(uploaded_file.getvalue())
        image = Image.open(image_bytes)
        st.image(image, caption="Radiografía Subida", use_column_width=True)
    except Exception as e:
        # **CÓDIGO CORREGIDO:** Se usa st.stop() en lugar de return
        st.error(f"Error al cargar la imagen. Asegúrate de que el formato sea válido: {e}")
        st.stop()
    
    # Botón para iniciar la clasificación
    if st.button("Clasificar Imagen", key="classify_button"):
        
        # =======================================================
        # 3. CONSUMO DE LA API DE RENDER
        # =======================================================
        
        st.info("Clasificando... por favor espera. Esto puede tardar unos segundos si el servidor de Render está inactivo.")
        
        # Necesitamos restablecer el puntero del archivo a 0 antes de enviarlo
        # para que 'requests' pueda leer el contenido completo del archivo.
        uploaded_file.seek(0)
        
        # Preparar la carga útil (payload) para la petición POST
        # La clave 'file' debe coincidir con request.files['file'] en tu API de Flask
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        
        try:
            # Realizar la petición POST
            response = requests.post(RENDER_API_URL, files=files)
            
            # 4. PROCESAR RESPUESTA
            if response.status_code == 200:
                result = response.json()
                classification = result.get("classification", "No clasificado (Clave 'classification' no encontrada)")
                
                st.success("✅ Clasificación Completada")
                st.markdown(f"## **Resultado de la IA: {classification}**")
                
            else:
                st.error(f"❌ Error al conectar con la API de Render.")
                st.write(f"Código de estado: {response.status_code}")
                
                # Intentar mostrar el error detallado devuelto por Render
                try:
                    st.json(response.json())
                except requests.exceptions.JSONDecodeError:
                    st.code(f"Respuesta de Render (no JSON): {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error("❌ Error de conexión: No se pudo alcanzar la API de Render. Revisa la URL.")
            st.code(f"Detalle del error: {e}")
            
# Fin del código

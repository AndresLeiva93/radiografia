import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time # Para simular un retraso en la carga visual

# =======================================================
# 1. CONFIGURACIÓN
# =======================================================
RENDER_API_URL = "https://radiografia-ia-api.onrender.com/classify"

st.set_page_config(
    page_title="Clasificador de Radiografías IA",
    page_icon="🩺",
    layout="centered", # o "wide" si prefieres más espacio horizontal
    initial_sidebar_state="collapsed" # Esconde la barra lateral por defecto
)

# Estilos CSS personalizados para una apariencia más limpia
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f0f2f6; /* Un color de fondo suave */
    }
    .stButton>button {
        background-color: #4CAF50; /* Un verde vibrante */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #45a049; /* Un poco más oscuro al pasar el ratón */
        transform: translateY(-2px);
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); /* Sombra suave para las imágenes */
    }
    .css-1aum7g5 { /* Ajusta el padding del uploader */
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🩺 Clasificador de Radiografías IA")
st.markdown("### Sube una imagen de radiografía para obtener la clasificación.")
st.write("---") # Separador visual

# =======================================================
# 2. CAPTURA DE ARCHIVO
# =======================================================

uploaded_file = st.file_uploader(
    "Selecciona tu imagen de radiografía (JPG, PNG)",
    type=["jpg", "jpeg", "png"],
    help="Solo se aceptan archivos JPG y PNG."
)

if uploaded_file is not None:
    # Usar columnas para mostrar la imagen más pequeña a la izquierda
    col1, col2 = st.columns([1, 2]) # 1 para la imagen, 2 para el espacio

    with col1:
        try:
            image_bytes = BytesIO(uploaded_file.getvalue())
            image = Image.open(image_bytes)
            # st.image con width para controlar el tamaño
            st.image(image, caption="Imagen subida", width=150) # Tamaño fijo de 150px de ancho
        except Exception as e:
            st.error(f"Error al cargar la imagen. Asegúrate de que el formato sea válido: {e}")
            st.stop()

    with col2:
        st.write("---")
        st.write("Imagen lista para clasificar.")
        
        # Botón de clasificación, ahora alineado y con mejor diseño
        if st.button("🚀 Clasificar Radiografía", key="classify_button"):
            
            st.write("---") # Separador
            st.info("Clasificando... por favor espera. Esto puede tardar unos segundos si el servidor de Render está inactivo.")
            
            # Restablecer el puntero del archivo
            uploaded_file.seek(0)
            
            files = {
                'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }
            
            try:
                # Simular un pequeño delay para una mejor UX si la respuesta es muy rápida
                # time.sleep(1) 
                response = requests.post(RENDER_API_URL, files=files)
                
                # =======================================================
                # 3. PROCESAR Y MOSTRAR RESPUESTA
                # =======================================================
                
                if response.status_code == 200:
                    result = response.json()
                    classification = result.get("classification", "No clasificado (Clave 'classification' no encontrada)")
                    
                    st.success("✅ Clasificación Completada")
                    st.markdown(f"## **Resultado de la IA: {classification}**")
                    
                else:
                    st.error(f"❌ Error al conectar con la API de Render.")
                    st.write(f"Código de estado: {response.status_code}")
                    
                    try:
                        st.json(response.json())
                    except requests.exceptions.JSONDecodeError:
                        st.code(f"Respuesta de Render (no JSON): {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error("❌ Error de conexión: No se pudo alcanzar la API de Render. Revisa la URL.")
                st.code(f"Detalle del error: {e}")

st.write("---")
st.markdown("Desarrollado con ❤️ por tu asistente IA.")

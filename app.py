import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# =======================================================
# 1. CONFIGURACIÓN
# =======================================================
RENDER_API_URL = "https://radiografia-ia-api.onrender.com/classify"

st.set_page_config(
    page_title="Clasificador de Radiografías IA",
    page_icon="🩺",
    layout="wide", # Ancho completo
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown(
    """
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilo del botón */
    .stButton>button {
        background-color: #007ACC; /* Un azul profesional */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.2s ease-in-out;
        width: 100%; 
    }
    .stButton>button:hover {
        background-color: #005f99;
        transform: translateY(-2px);
    }
    /* Estilo del contenedor de la imagen */
    .stImage {
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        display: block; /* Asegura que la imagen sea tratada como bloque */
        margin-left: auto; /* Centrar la imagen en la columna derecha */
        margin-right: auto;
    }
    /* Estilo para el resultado final */
    .result-box {
        background-color: #e6ffe6;
        border-left: 5px solid #4CAF50;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🩺 Clasificador de Radiografías IA")
st.markdown("### Plataforma de Análisis de Imágenes Médicas")
st.write("---") 

# =======================================================
# 2. ESTRUCTURA PRINCIPAL (COLUMNA 1: Carga/Botón | COLUMNA 2: Imagen/Resultado)
# =======================================================

# 3:2 divide el ancho total. La columna 1 (3 partes) será más ancha que la columna 2 (2 partes).
# Esto deja la imagen (columna 2) más pequeña y la separa bien de la izquierda.
col_input, col_display = st.columns([3, 2])

# --- COLUMNA IZQUIERDA: Carga y Botón ---
with col_input:
    st.markdown("#### 1. Carga de Archivo")
    
    uploaded_file = st.file_uploader(
        "Selecciona la imagen de radiografía (JPG, PNG):",
        type=["jpg", "jpeg", "png"],
        help="El archivo será enviado a la API de Render para su análisis."
    )
    
    st.write("---")
    st.markdown("#### 2. Acción")

    # Botón de clasificación
    if st.button("🚀 Iniciar Clasificación", key="classify_button", disabled=(uploaded_file is None)):
        pass # La lógica se maneja en la columna de resultado


# --- COLUMNA DERECHA: Vista Previa y Resultado ---
with col_display:
    st.markdown("#### Vista Previa y Resultado")
    
    # Placeholder para la imagen
    image_placeholder = st.empty()
    
    # Placeholder para el resultado de la clasificación
    result_placeholder = st.empty()
    result_placeholder.info("Sube una imagen y haz clic en 'Iniciar Clasificación'.")
    
    
    if uploaded_file is not None:
        try:
            image_bytes = BytesIO(uploaded_file.getvalue())
            image = Image.open(image_bytes)
            
            # Mostrar la imagen en el placeholder con ancho fijo (más pequeño)
            with image_placeholder:
                # Usamos width=200 para achicarla, y las propiedades CSS la centran
                st.image(image, caption="Imagen Subida", width=200) 
            
            
            # La lógica de clasificación se ejecuta solo si se presiona el botón
            if st.session_state.get('classify_button'):
                
                # Mostrar el mensaje de espera en el placeholder del resultado
                result_placeholder.warning("Analizando imagen... esto puede tardar un momento.") 
                
                # Resetear el puntero del archivo
                uploaded_file.seek(0)
                
                files = {
                    'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
                
                try:
                    # Realizar la petición POST
                    response = requests.post(RENDER_API_URL, files=files)
                    
                    # -----------------------------------------------------------
                    # PROCESAR RESPUESTA
                    # -----------------------------------------------------------
                    if response.status_code == 200:
                        result = response.json()
                        classification = result.get("classification", "No clasificado (Clave no encontrada)")
                        
                        # Actualizar el placeholder con el resultado final atractivo
                        result_html = f"""
                        <div class="result-box">
                            <h3>✅ Clasificación Final</h3>
                            <h2>{classification}</h2>
                        </div>
                        """
                        result_placeholder.markdown(result_html, unsafe_allow_html=True)
                        
                    else:
                        # Si falla Render
                        error_message = f"❌ Error API: Código {response.status_code}"
                        result_placeholder.error(error_message)
                        try:
                            st.json(response.json())
                        except requests.exceptions.JSONDecodeError:
                            st.code(f"Respuesta de Render (no JSON): {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    result_placeholder.error("❌ Error de Conexión: No se pudo alcanzar la API de Render.")
                    st.code(f"Detalle: {e}")

        except Exception as e:
            # Manejo de error de carga/previsualización
            image_placeholder.error(f"Error: {e}")
            st.stop()


# =======================================================
# 4. RESET DE ESTADO
# =======================================================
# Esto asegura que el botón se pueda presionar múltiples veces
if 'classify_button' in st.session_state and st.session_state['classify_button']:
    st.session_state['classify_button'] = False

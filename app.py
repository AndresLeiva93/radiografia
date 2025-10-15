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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stButton>button {
        background-color: #007ACC;
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
    .stImage {
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
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
# 2. ESTRUCTURA PRINCIPAL
# =======================================================

col_input, col_display = st.columns([3, 2])

# --- COLUMNA DERECHA: Vista Previa y Resultado (Se define primero para usar placeholders) ---
with col_display:
    st.markdown("#### Vista Previa y Resultado")
    
    # Placeholders
    image_placeholder = st.empty()
    result_placeholder = st.empty()
    
    # Mensaje inicial
    result_placeholder.info("Sube una imagen y haz clic en 'Iniciar Clasificación'.")


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
    
    # El botón ahora usa un key simple. El estado se verifica abajo.
    is_classify_pressed = st.button("🚀 Iniciar Clasificación", key="classify_button", disabled=(uploaded_file is None))


# =======================================================
# 3. LÓGICA DE CLASIFICACIÓN (Ejecución Central)
# =======================================================

# La lógica se ejecuta solo si hay archivo Y el botón fue presionado
if uploaded_file is not None and is_classify_pressed:
    
    # Mover el mensaje de espera al inicio de la lógica
    with col_display:
        result_placeholder.warning("Analizando imagen... esto puede tardar un momento.") 
    
    try:
        # Previsualización de la imagen
        image_bytes = BytesIO(uploaded_file.getvalue())
        image = Image.open(image_bytes)
        with image_placeholder:
            st.image(image, caption="Imagen Subida", width=200) 
            
        # Resetear el puntero del archivo antes de enviarlo
        uploaded_file.seek(0)
        
        files = {
            'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        
        # Petición a la API de Render
        response = requests.post(RENDER_API_URL, files=files)
        
        with col_display:
            if response.status_code == 200:
                result = response.json()
                classification = result.get("classification", "No clasificado")
                
                # Mostrar resultado final
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
        with col_display:
            result_placeholder.error("❌ Error de Conexión: No se pudo alcanzar la API de Render.")
            st.code(f"Detalle: {e}")
            
    except Exception as e:
        # Manejo de error de carga/previsualización
        with col_display:
            image_placeholder.error(f"Error: {e}")
            st.stop()


# Fin del código (El bloque de reseteo de estado ha sido eliminado)

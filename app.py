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
    layout="wide", # ¡Cambiado a layout="wide"!
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para una apariencia más limpia y controlada
st.markdown(
    """
    <style>
    /* Ocultar el menú de Streamlit (opcional) */
    #MainMenu {visibility: hidden;}
    /* Ocultar el footer de Streamlit (opcional) */
    footer {visibility: hidden;}
    
    /* Estilo del botón */
    .stButton>button {
        background-color: #4CAF50; 
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.2s ease-in-out;
        width: 100%; /* Ajusta el botón al ancho de la columna */
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center; /* Centrar la imagen dentro de su contenedor */
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
st.markdown("### Plataforma de Clasificación de Imágenes Médicas")
st.write("---") 

# =======================================================
# 2. ESTRUCTURA PRINCIPAL (LAYOUT WIDE CON COLUMNAS)
# =======================================================

# Creamos dos columnas de igual ancho para la UI
col_upload, col_result = st.columns([1, 1])

with col_upload:
    st.markdown("#### 1. Sube tu Radiografía")
    
    uploaded_file = st.file_uploader(
        "Selecciona la imagen (JPG, PNG):",
        type=["jpg", "jpeg", "png"],
        help="El archivo será enviado a la API de Render para su análisis."
    )
    
    # Manejar la subida y la previsualización
    if uploaded_file is not None:
        try:
            image_bytes = BytesIO(uploaded_file.getvalue())
            image = Image.open(image_bytes)
            
            # Usar una columna interna para centrar la imagen pequeña
            center_col, img_col, _ = st.columns([1, 4, 1])
            with img_col:
                # Previsualización más grande que antes, pero controlada
                st.image(image, caption="Imagen Subida", width=300) 
            
            st.write("") # Espacio
            st.markdown("#### 2. Clasificar")
            
            # Botón de clasificación, que ocupa el 100% del ancho de su columna
            if st.button("🚀 Clasificar Radiografía", key="classify_button"):
                pass # El código de clasificación va en la columna de resultado
                
        except Exception as e:
            st.error(f"Error al cargar o previsualizar la imagen: {e}")
            st.stop()

# =======================================================
# 3. LÓGICA Y RESULTADO (Columna Derecha)
# =======================================================

with col_result:
    st.markdown("#### 3. Resultado de la Clasificación")
    
    # Crear un placeholder para el resultado inicial y final
    result_placeholder = st.empty()
    result_placeholder.info("Sube una imagen y haz clic en 'Clasificar' para comenzar el análisis.")

    # La lógica de clasificación se ejecuta solo si se presiona el botón Y hay archivo
    if uploaded_file is not None and st.session_state.get('classify_button'):
        
        # Mostrar el mensaje de espera en el placeholder
        result_placeholder.warning("Analizando imagen...") 
        
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
                classification = result.get("classification", "No clasificado (Clave 'classification' no encontrada)")
                
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
                try:
                    error_details = response.json()
                except requests.exceptions.JSONDecodeError:
                    error_details = {"detail": response.text}
                    
                result_placeholder.error(error_message)
                st.json(error_details)
                
        except requests.exceptions.RequestException as e:
            result_placeholder.error("❌ Error de Conexión: No se pudo alcanzar la API de Render.")
            st.code(f"Detalle: {e}")

# =======================================================
# 4. RESET DE ESTADO (Para permitir clasificaciones repetidas)
# =======================================================
# Esto asegura que el botón se pueda presionar múltiples veces sin problemas de estado
if 'classify_button' in st.session_state and st.session_state['classify_button']:
    st.session_state['classify_button'] = False

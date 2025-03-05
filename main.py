import os
import re
import spacy
import pytesseract
import pandas as pd
from joblib import load
import streamlit as st
import time
from libreria.chat_gpt import chat_with_gpt
from libreria.extraction_texto import extraccion_texto
import json

# Configuración de Tesseract
#pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
#os.environ['TESSDATA_PREFIX'] = "/opt/homebrew/share"

pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract" # EN MI CASO TENGO QUE USAR LA VARIABLE ASI
os.environ['TESSDATA_PREFIX'] = "/usr/local/share/tessdata" # EN MI CASO TENGO QUE USAR LA VARIABLE ASI


# Cargar el modelo spaCy para procesamiento de texto en español
nlp = spacy.load("es_core_news_lg")

# Cargar los modelos de Machine Learning entrenados
model_rf = load('./Modelos_Entrenados/Model_RF.pkl')
model_rl = load('./Modelos_Entrenados/Model_RL_R.pkl')

# Cargar los datos de fraude
fraude = pd.read_excel("./Datos/BASE_PARA_PREDICT.xlsx")


def extract_text_from_pdf(file_path):
    """Extrae texto de un archivo PDF usando OCR (Reconocimiento Óptico de Caracteres)."""
    text = extraccion_texto(file_path)
    return text


def extract_with_matcher(text): 
    """Extrae toda la información relevante del texto."""

    peticion = """

    Saca los datos principales de la persona de la siguiente carta laboral:

        nombre (ordenado por nombre, segundo nombre, apellido y segundo apellido),
        cedula (sin puntos ni comas) ponle de titulo CC,
        de_donde_es_la_cedula (ciudad de origen de donde salió el documento),
        tipo_de_contrato,
        cargo,
        nombre_de_la_empresa,
        nit_de_la_empresa,
        salario (sin puntos ni comas decimales, solo pon  valores numericos),
        bonificacion (sin puntos ni comas decimales, solo pon  valores numericos),
        fecha_inicio_labor ,
        fecha_fin_labor (si no tiene fecha fin, pon "actualidad" para saber que actualmente esta laborando),
        fecha_de_expedicion_carta

    quiero que las fechas queden en formato dd/mm/yyyy

    entrega los resultados en json

    """
    text = peticion + text
    results = chat_with_gpt(text)
    try:
        results = json.loads(results)
    except json.JSONDecodeError:
        print("❌ Error: ChatGPT devolvió un JSON no válido. Verifica la respuesta.")
        results = {"error": "Respuesta de ChatGPT no válida"}

    return results


def calcular_probabilidad(fraude_data, cedula, model_rf, model_rl):
    """Calcula la probabilidad de fraude usando los modelos de Machine Learning."""
    caso = fraude_data[fraude_data['CEDULA'] == cedula]
    if caso.empty:
        return None, "Cédula no encontrada en los datos."
    try:
        caso_preparado = caso.drop(['CEDULA', 'N'], axis=1)
    except KeyError:
        return None, "Las columnas 'CEDULA' o 'N' no existen en los datos."

    expected_columns = model_rf.feature_names_in_
    caso_preparado = caso_preparado[expected_columns]

    prob_rf = 1 - model_rf.predict_proba(caso_preparado)[:, 1]
    prob_lr = 1 - model_rl.predict_proba(caso_preparado)[:, 1]

    peso_rf = 0.4
    peso_lr = 0.6
    prob_ensamble = (peso_rf * prob_rf) + (peso_lr * prob_lr)

    return prob_ensamble[0], None


# Interfaz de Streamlit
st.set_page_config(page_title="Fraudubot", page_icon="🤖​")
st.sidebar.markdown("""
    ### Fraudubot
    Detection of possible fraud
    """)

st.image("./img/galgo.png", width=150)
# Show principal functions
show_principal_functions = st.sidebar.checkbox("Show principal functions", value=False)
if show_principal_functions:
    st.sidebar.markdown("""
    ### Principal functions
    - **Procesar documento**: Se procesa el archivo adjunto (pueden ser pdf, docx, jpg o npg).
    - **Extraer información**: Se extrae la información del **texto** encontrado en el archivo.
    - **Validación de fraude**: Se calcula la **probabilidad de fraude** del documento.
    """)

# Show file types
show_file_types = st.sidebar.checkbox("Show supported file types", value=False)
if show_file_types:
    st.sidebar.markdown("""
    ### Supported file types
    - **PDF** (Portable Document Format)
    - **DOCX** (Word Document)
    - **JPG o PNG** (Images)
    """)

# Show types_documents
show_types_documents = st.sidebar.checkbox("Show types of documents", value=False)
if show_types_documents:
    st.sidebar.markdown("""
    ### Types of documents
    - **Cartas Laborales**
    - **Colillas de pago**
    - **Identificación** (CC)
    """)

st.sidebar.markdown("---")
st.sidebar.image("./img/galgo.png", width=250)

st.markdown("""
<style>
.main { background-color: #f5f5f5; }
.title { font-size: 40px; text-align: center; font-weight: bold; }
.subtitleCenter {font-size: 24px; text-align: center; margin-top: -10px; }
.subtitleLeft {font-size: 20px; }
.colorTitle { color: #051B5F; }
.colorContent { color: #051B5F; }
            
.alert-high { color: #FFFFFF; background-color: #ffc319; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; }
.alert-low { color: #FFFFFF; background-color: #2ECC71; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    st.image("./GIF/Fraudubot7.gif", width=600)
with col2:
    st.markdown("<div class='title colorTitle'>Fraudubot 🛡️</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitleCenter colorTitle'>Bot that helps you detect possible fraud</div>", unsafe_allow_html=True)

colCl, colCp = st.columns([2, 2])
with colCl:
    st.markdown("<div class='subtitleCenter colorContent'>Carta Laboral</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a file Carta Laboral", type="pdf, png, jpg", label_visibility="collapsed")
with colCp:
    st.markdown("<div class='subtitleCenter colorContent'>Colillas de Pago</div>", unsafe_allow_html=True)
    uploaded_file_col = st.file_uploader("Upload a file Colillas de Pago", type="pdf, png, jpg", label_visibility="collapsed")

if uploaded_file:
    temp_file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with st.spinner("Processing the file... Please wait.", show_time=False):
        time.sleep(2)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    #st.markdown("<div class='subtitleCenter colorContent'>Processing the file...</div>", unsafe_allow_html=True)
    extracted_text = extract_text_from_pdf(temp_file_path)
    
    st.markdown("<div class='subtitleLeft colorContent'>Document information:</div>", unsafe_allow_html=True)
    st.text_area("Texto del PDF", extracted_text, height=600, disabled=True)#, label_visibility="collapsed")

    st.markdown("<div class='subtitleLeft colorContent'>Extracted information:</div>", unsafe_allow_html=True)
    extracted_results = extract_with_matcher(extracted_text)

    st.text_input("Nombre", extracted_results["nombre"], disabled=True)       
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Identificación", extracted_results["CC"], disabled=True)
    with col2:
        st.text_input("Salario", extracted_results["salario"], disabled=True)
    with col3:
        st.text_input("Bonificación", extracted_results["bonificacion"], disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Fecha inicio trabajo:", extracted_results["fecha_inicio_labor"], disabled=True)
    with col2:
        st.text_input("Fecha fin trabajo:", extracted_results["fecha_fin_labor"], disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Tipo de contrato", extracted_results["tipo_de_contrato"], disabled=True)
    with col2:
        st.text_input("Cargo", extracted_results["cargo"], disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nombre de la empresa", extracted_results["nombre_de_la_empresa"], disabled=True)
    with col2:
        st.text_input("NIT de la empresa", extracted_results["nit_de_la_empresa"], disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Ciudad de origen de la cédula", extracted_results["de_donde_es_la_cedula"], disabled=True)
    with col2:
        st.text_input("Fecha de expedición de la carta", extracted_results["fecha_de_expedicion_carta"], disabled=True)

    cedula_input = extracted_results.get("CC")
    #for key, value in extracted_results.items():
    #    st.write(f"**{key}:** {value}")

    if st.button("Calcular probabilidad de fraude", use_container_width=True, type="primary"):
        if cedula_input:
            try:
                cedula_input = int(cedula_input)
                probabilidad, error = calcular_probabilidad(fraude, cedula_input, model_rf, model_rl)
                if error:
                    st.error(error)
                elif probabilidad is not None:
                    if probabilidad > 0.5:
                        st.markdown(f"<div class='alert-high'>Posible fraude detectado. Probabilidad: {probabilidad*100:.2f}%</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='alert-low'>Sin indicios de fraude. Probabilidad: {probabilidad*100:.2f}%</div>", unsafe_allow_html=True)
            except ValueError:
                st.error("La cédula debe ser un número válido.")
        else:
            st.error("No se pudo extraer una cédula válida.")

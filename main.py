 """
Importante!!!!!!!!!!!!!!!!!!!!
1. Descargar diccionario spacy---> python -m spacy download es_core_news_lg
2. Para desplegar la aplicacion en local ejecutar en la terminal: streamlit run main.py
"""

import os
import re
import spacy
import pytesseract
import pandas as pd
from datetime import datetime
from joblib import load
from word2number import w2n
from pdf2image import convert_from_path
import unicodedata
import streamlit as st
from PIL import Image

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
os.environ['TESSDATA_PREFIX'] = "/opt/homebrew/share"

# Cargar el modelo spaCy para procesamiento de texto en español
nlp = spacy.load("es_core_news_lg")

# Cargar los modelos de Machine Learning entrenados
model_rf = load('./Modelos_Entrenados/Model_RF.pkl')
model_rl = load('./Modelos_Entrenados/Model_RL_R.pkl')

# Cargar los datos de fraude
fraude = pd.read_excel("./Datos/BASE_PARA_PREDICT.xlsx")

# Funciones auxiliares
def remove_accents(text):
    """Elimina los acentos de un texto."""
    return ''.join(
        (c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    )

def extract_text_from_pdf(file_path):
    """Extrae texto de un archivo PDF usando OCR (Reconocimiento Óptico de Caracteres)."""
    pages = convert_from_path(file_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page, lang="spa", config="--tessdata-dir /opt/homebrew/share/tessdata") + "\n"
    return text

def extract_name(text):
    """Extrae el nombre de una persona del texto."""
    stop_words = {"la señora", "el señor", "señor", "señora", "la", "el", "El", "La"}
    text = " ".join(text.split()[3:])  # Eliminar las primeras tres palabras
    doc = nlp(text)
    
    for ent in doc.ents:
        if ent.label_ == "PER":
            cleaned_name = " ".join(word for word in ent.text.split() if word.lower() not in stop_words)
            return cleaned_name.strip()

    # Patrón para nombre con contexto como "el señor [NOMBRE]"
    context_pattern = r"(?i)(?:el\s+señor|la\s+señora|señor(?:a)?|que)\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ]*(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ]*)+)"
    match = re.search(context_pattern, text)
    if match:
        candidate_name = match.group(1).strip()
        cleaned_name = " ".join(word for word in candidate_name.split() if word.lower() not in stop_words)
        return cleaned_name.title()
    
    return None

def extract_cc(text):
    """Extrae la cédula de ciudadanía del texto."""
    text_normalized = remove_accents(text)
    cc_match = re.search(
        r"(?:CC|cedula(?: de ciudadania)?|cedula)(?:\s*(?:numero|num|No\.?|No:)\s*[:\s]*)?([\d\.\s]+)",
        text_normalized, re.IGNORECASE
    )
    if cc_match:
        return re.sub(r"[^\d]", "", cc_match.group(1))
    return None

def extract_salario(text):
    """Extrae información del salario del texto, soportando tanto números como palabras."""
    pattern = r"(?:salario|remuneración)\s*[:de]*\s*([\d.,]+|[a-zA-Z\s]+(?:\s*pesos?|\s*millon|\s*doscientos?|\s*mil)*)|[\$€]\s?[\d.,]+"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        salary_str = match.group(1) if match.group(1) else match.group(0)
        if any(char.isalpha() for char in salary_str):
            try:
                salary_value = w2n.word_to_num(salary_str.replace("UN", "one").replace("MILLON", "million"))
                return salary_value
            except ValueError:
                return salary_str
        else:
            salary_str = re.sub(r"[^\d]", "", salary_str)
            try:
                return int(salary_str)
            except ValueError:
                return salary_str
    return None

def extract_tiempo_laborado(text):
    """Extrae las fechas de inicio y fin del periodo laboral desde el texto."""
    year_pattern = r"\b(\d{4})\b"
    years = re.findall(year_pattern, text)
    current_date = datetime.now()
    is_present = any(term in text.lower() for term in ["hasta hoy", "hoy", "actualidad", "presente", "hasta la fecha"])
    
    from_date, to_date = None, None
    desde_match = re.search(r"desde\s+(\d{4})", text.lower())
    if desde_match:
        from_year = desde_match.group(1)
        from_date = f"{from_year}-01-01"

    if is_present:
        to_date = current_date.strftime('%Y-%m-%d')
    elif len(years) > 1:
        to_date = f"{years[1]}-12-31"

    if not desde_match and years:
        from_date = f"{years[0]}-01-01"

    return from_date, to_date

def extract_with_matcher(text):
    """Extrae toda la información relevante del texto."""
    results = {
        "Nombre": extract_name(text),
        "CC": extract_cc(text),
        "Salario": extract_salario(text),
        "from_tiempo_laborado": None,
        "to_tiempo_laborado": None
    }
    results["from_tiempo_laborado"], results["to_tiempo_laborado"] = extract_tiempo_laborado(text)
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
st.markdown("""
<style>
.main { background-color: #f5f5f5; }
.title { color: #51a9ee; font-size: 36px; text-align: center; font-weight: bold; }
.subtitle { color: #95ccf7; font-size: 24px; text-align: center; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.alert-high { color: white; background-color: #E74C3C; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; }
.alert-low { color: white; background-color: #2ECC71; padding: 10px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    st.image("./GIF/Fraudubot7.gif", width=600)
with col2:
    st.markdown("<div class='title'>Fraudubot 🛡️</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Bot que te ayuda a detectar posibles fraudes</div>", unsafe_allow_html=True)

st.title("Procesamiento Carta Laboral 📄")
uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

if uploaded_file:
    temp_file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Procesando el archivo...")
    extracted_text = extract_text_from_pdf(temp_file_path)
    st.subheader("Texto Extraído")
    st.text_area("Texto del PDF", extracted_text, height=200)

    st.subheader("Información Extraída")
    extracted_results = extract_with_matcher(extracted_text)
    cedula_input = extracted_results.get("CC")

    for key, value in extracted_results.items():
        st.write(f"**{key}:** {value}")

    if st.button("Calcular probabilidad de fraude"):
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

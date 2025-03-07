import os
import time
import json
import pandas as pd
import streamlit as st
from joblib import load
from libreria.extraction_texto import extraccion_texto
from libreria.chat_gpt import chat_with_gpt

# Cargar modelos y base de fraude
model_rf = load('./Modelos_Entrenados/Model_RF.pkl')
model_rl = load('./Modelos_Entrenados/Model_RL_R.pkl')
fraude = pd.read_excel("./Datos/BASE_PARA_PREDICT.xlsx")


def extract_text(file_path):
    return extraccion_texto(file_path)


def compracion_documentos(texto_colilla, texto_carta):
    peticion = """
    Te voy a pasar dos textos uno de colillas de pago y otro de cartas laborales. 
    Quiero que midas el porcentaje de coincidencias en ambos textos midiendo las siguienes variables en ambos textos y al final me des un porcentaje:
        -nombre de la persona
        -empresa en la que trabaja
        -salario
        
    Quiero que tu resultado sea un JSON con los siguientes campos:
        -"porcentaje"
        -"explicacion" (de porque el porcentaje)
        -"no_coincide" (si no coincide algo ponlo aca)

    {
        "porcentaje": "XX%", 
        "explicacion": "Aquí debe ir una explicación breve de por qué se obtuvo ese porcentaje.",
        "no_coincide": {
            "nombre": {
                "colilla_pago": "Nombre extraído de la colilla",
                "carta_laboral": "Nombre extraído de la carta"
            },
            "empresa": {
                "colilla_pago": "Empresa extraída de la colilla",
                "carta_laboral": "Empresa extraída de la carta"
            },
            "salario": {
                "colilla_pago": "Salario extraído de la colilla",
                "carta_laboral": "Salario extraído de la carta"
            }
        }
    }   
    Recurda que ambos textos hacen referencia a cosas totalmente diferente

    QUIERO QUE LA RESPUESTA SEA UNICAMENTE DENTRO DEL JSON QUE SOLICITO
    """

    text = f"{peticion} + colilla_pago: {texto_colilla} carta_laboral: {texto_carta}"
    response = chat_with_gpt(text)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Respuesta de ChatGPT no válida"}   


def extract_with_matcher(text):
    peticion = """
    Saca los datos principales de la persona de la siguiente carta laboral:

        nombre (ordenado por nombre, segundo nombre, apellido y segundo apellido),
        cedula (sin puntos ni comas) ponle de titulo CC,
        de_donde_es_la_cedula (ciudad de origen de donde salió el documento),
        tipo_de_contrato,
        cargo,
        nombre_de_la_empresa,
        nit_de_la_empresa,
        salario (sin puntos ni comas decimales, solo pon valores numericos),
        bonificacion (sin puntos ni comas decimales, solo pon valores numericos),
        fecha_inicio_labor,
        fecha_fin_labor (si no tiene fecha fin, pon "actualidad"),
        fecha_de_expedicion_carta

    Quiero que las fechas queden en formato dd/mm/yyyy
    Entrega el resultado en formato JSON.
    """

    text = peticion + text
    response = chat_with_gpt(text)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Respuesta de ChatGPT no válida"}


def calcular_probabilidad(fraude_data, cedula, model_rf, model_rl):
    caso = fraude_data[fraude_data['CEDULA'] == cedula]
    if caso.empty:
        return None, "Cédula no encontrada."

    caso_preparado = caso.drop(['CEDULA', 'N'], axis=1, errors='ignore')
    expected_columns = model_rf.feature_names_in_
    caso_preparado = caso_preparado[expected_columns]

    prob_rf = 1 - model_rf.predict_proba(caso_preparado)[:, 1]
    prob_lr = 1 - model_rl.predict_proba(caso_preparado)[:, 1]
    prob_ensamble = (0.4 * prob_rf) + (0.6 * prob_lr)

    return prob_ensamble[0], None


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Fraudubot", page_icon="🤖")

st.sidebar.markdown("""
### Fraudubot
Detection of possible fraud
""")

st.sidebar.markdown("""
### Principal functions
- Procesar documento
- Extraer información
- Validación de fraude
""")

st.sidebar.markdown("""
### Supported file types
- PDF
- DOCX
- JPG
- PNG
""")

st.sidebar.markdown("""
### Types of documents
- Cartas Laborales
- Colillas de Pago
- Identificación (CC)
""")

st.sidebar.image("./img/galgo.png", width=250)

col1, col2 = st.columns([1, 3])
with col1:
    st.image("./GIF/Fraudubot7.gif", width=600)

with col2:
    st.markdown("<h1 style='text-align: center; color: #051B5F;'>Fraudubot 🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #051B5F;'>Bot that helps you detect possible fraud</h3>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 2])

with col1:
    st.markdown("#### Carta Laboral")
    uploaded_file_carta = st.file_uploader("Subir Carta Laboral", type=["pdf", "png", "jpg"], label_visibility="collapsed")

with col2:
    st.markdown("#### Colillas de Pago")
    uploaded_file_colilla = st.file_uploader("Subir Colilla de Pago", type=["pdf", "png", "jpg"], label_visibility="collapsed")

# Botón calcular
col1, col2, col3 = st.columns([1,2,1])

with col2:  # La columna central
    procesar = st.button("Calcular", use_container_width=True)

if procesar:
    if not uploaded_file_carta and not uploaded_file_colilla:
        st.warning("⚠️ Debes subir al menos un archivo.")
    else:
        extracted_results = {}
        cedula_input = None

        if uploaded_file_carta:
            st.info("Procesando Carta Laboral...")

            temp_path = os.path.join("temp", uploaded_file_carta.name)
            os.makedirs("temp", exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file_carta.getbuffer())

            text_carta = extract_text(temp_path)
            st.text_area("Texto extraído de la Carta Laboral:", text_carta, height=300)

            extracted_results = extract_with_matcher(text_carta)

        if uploaded_file_colilla:
            st.info("Procesando Colilla de Pago...")

            temp_path_colilla = os.path.join("temp", uploaded_file_colilla.name)
            with open(temp_path_colilla, "wb") as f:
                f.write(uploaded_file_colilla.getbuffer())

            text_colilla = extract_text(temp_path_colilla)
            st.text_area("Texto extraído de la Colilla de Pago:", text_colilla, height=300)

        if uploaded_file_carta and uploaded_file_colilla:
            st.markdown("### Comparación entre Carta Laboral y Colilla de Pago")

            resultado_comparacion = compracion_documentos(text_colilla, text_carta)

            if "error" in resultado_comparacion:
                st.error("❌ Error al comparar documentos: " + resultado_comparacion["error"])
            else:
                st.metric(label="📊 Porcentaje de coincidencia", value=f"{resultado_comparacion['porcentaje']}")
                st.markdown(f"**Explicación:** {resultado_comparacion['explicacion']}")
                no_coincide = resultado_comparacion["no_coincide"]

                texto_no_coincide = f"""
                ### 📊 Detalles de diferencias

                - **Nombre (Colilla de Pago):** {no_coincide['nombre']['colilla_pago']}
                - **Nombre (Carta Laboral):** {no_coincide['nombre']['carta_laboral']}

                - **Empresa (Colilla de Pago):** {no_coincide['empresa']['colilla_pago']}
                - **Empresa (Carta Laboral):** {no_coincide['empresa']['carta_laboral']}

                - **Salario (Colilla de Pago):** {no_coincide['salario']['colilla_pago']}
                - **Salario (Carta Laboral):** {no_coincide['salario']['carta_laboral']}
                """

                st.markdown(texto_no_coincide)

        if extracted_results:
            st.markdown("### Información extraída de la Carta Laboral")
            st.text_input("Nombre", extracted_results.get("nombre", ""), disabled=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_input("Identificación (CC)", extracted_results.get("CC", ""), disabled=True)
            with col2:
                st.text_input("Salario", extracted_results.get("salario", ""), disabled=True)
            with col3:
                st.text_input("Bonificación", extracted_results.get("bonificacion", ""), disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Fecha inicio trabajo", extracted_results.get("fecha_inicio_labor", ""), disabled=True)
            with col2:
                st.text_input("Fecha fin trabajo", extracted_results.get("fecha_fin_labor", ""), disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Tipo de contrato", extracted_results.get("tipo_de_contrato", ""), disabled=True)
            with col2:
                st.text_input("Cargo", extracted_results.get("cargo", ""), disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Nombre empresa", extracted_results.get("nombre_de_la_empresa", ""), disabled=True)
            with col2:
                st.text_input("NIT empresa", extracted_results.get("nit_de_la_empresa", ""), disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Ciudad cédula", extracted_results.get("de_donde_es_la_cedula", ""), disabled=True)
            with col2:
                st.text_input("Fecha expedición carta", extracted_results.get("fecha_de_expedicion_carta", ""), disabled=True)

            cedula_input = extracted_results.get("CC")

            if cedula_input:
                try:
                    cedula_input = int(cedula_input)
                    probabilidad, error = calcular_probabilidad(fraude, cedula_input, model_rf, model_rl)

                    if error:
                        st.error(error)
                    elif probabilidad is not None:
                        color = "#ff4d4d" if probabilidad > 0.5 else "#4CAF50"
                        mensaje = "⚠️ Posible fraude" if probabilidad > 0.5 else "✅ Sin indicios de fraude"
                        st.markdown(f"<div style='background-color:{color};color:white;padding:10px;border-radius:5px;text-align:center;font-size:18px;'>{mensaje} - Probabilidad: {probabilidad*100:.2f}%</div>", unsafe_allow_html=True)
                except ValueError:
                    st.error("La cédula no es válida.")


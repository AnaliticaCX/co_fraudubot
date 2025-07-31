# services/extraccion.py
"""
Módulo para la extracción de texto y datos de documentos.
"""
from libreria.extraction_texto import extraccion_texto
from libreria.modelos_ia import ModeloIA
import streamlit as st  # Asegúrate de que estás usando esto en entorno Streamlit

# TODO: Recibir el modelo como parámetro o inyectar dependencia

def extraer_texto(file_path):
    try:
        return extraccion_texto(file_path)
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {file_path}")
        st.exception(e)
        return None  # o puedes lanzar el error de nuevo si prefieres


def extraer_datos_carta_laboral(modelo, texto):
    return modelo.extraer_datos_carta_laboral(texto)

def extraer_datos_extracto_bancario(modelo, texto):
    return modelo.extraer_datos_extracto_bancario(texto)

def extraer_datos_colilla_pago(modelo, texto):
    return modelo.extraer_datos_colilla_pago(texto) 
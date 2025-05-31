from typing import List, Dict, Any
import streamlit as st
from .modelos_ia import ModeloIA
import PyPDF2
from libreria.extraction_texto import extraccion_texto

def procesar_documentos_subidos(uploaded_files: List[Any], modelo: Any) -> Dict[str, Any]:
    """
    Procesa los documentos subidos y los clasifica.
    """
    documentos_clasificados = []
    for file in uploaded_files:
        texto = file.getvalue().decode('utf-8')
        tipo = modelo.clasificar_documento(texto)
        documentos_clasificados.append({"tipo": tipo, "texto": texto})
    
    return documentos_clasificados

def separar_documentos(documentos_clasificados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Separa los documentos en carta laboral y colillas de pago.
    """
    carta_laboral = None
    colillas_pago = []
    
    for doc in documentos_clasificados:
        if doc["tipo"] == "carta laboral":
            carta_laboral = doc["texto"]
        elif doc["tipo"] == "colilla de pago":
            colillas_pago.append(doc["texto"])
    
    return {
        "carta_laboral": carta_laboral,
        "colillas_pago": colillas_pago
    }

def procesar_documentos_subidos(uploaded_files: List[Any], modelo: ModeloIA) -> Dict[str, Any]:
    """
    Procesa los documentos subidos y realiza las comparaciones necesarias.
    """
    if not uploaded_files:
        return None
    
    # Clasificar documentos
    documentos_clasificados = []
    for file in uploaded_files:
        texto = file.getvalue().decode('utf-8')
        tipo = modelo.clasificar_documento(texto)
        documentos_clasificados.append({"tipo": tipo, "texto": texto})
    
    # Separar carta laboral y colillas de pago
    carta_laboral = None
    colillas_pago = []
    
    for doc in documentos_clasificados:
        if doc["tipo"] == "carta laboral":
            carta_laboral = doc["texto"]
        elif doc["tipo"] == "colilla de pago":
            colillas_pago.append(doc["texto"])
    
    # Comparar documentos si hay carta laboral y colillas
    if carta_laboral and colillas_pago:
        return {
            "carta_laboral": carta_laboral,
            "colillas_pago": colillas_pago,
            "resultado_comparacion": modelo.comparar_documentos(carta_laboral, colillas_pago)
        }
    
    return None

def extraccion_texto(file) -> str:
    """
    Extrae texto de diferentes tipos de archivos usando la librería existente.
    """
    file_type = file.type
    
    try:
        if file_type == "application/pdf":
            # Usar la función de extracción de PDF existente
            return extraer_texto_pdf(file)
            
        elif file_type.startswith("image/"):
            # Usar la función de extracción de imagen existente
            return extraer_texto_imagen(file)
            
        else:
            return file.getvalue().decode('utf-8')
            
    except Exception as e:
        print(f"Error al extraer texto del archivo: {str(e)}")
        return ""

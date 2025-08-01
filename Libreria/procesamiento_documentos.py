from typing import List, Dict, Any
import streamlit as st
from .modelos_ia import ModeloIA
import PyPDF2
from libreria.extraction_texto import extraccion_texto

# === CONFIGURATION ===
TIPOS_DOCUMENTOS = {
    "colilla de pago": {
        "habilitado": True,
        "validaciones": {
            "consistencia_datos": True,
            "analisis_visual": True,
            "metadatos": True,
            "firmas": True,
            "calidad": True
        }
    },
    "carta laboral": {
        "habilitado": True,
        "validaciones": {
            "consistencia_datos": True,
            "analisis_visual": True,
            "metadatos": True,
            "firmas": True,
            "calidad": True
        }
    },
    "extracto bancario": {
        "habilitado": False,
        "validaciones": {
            "consistencia_datos": True,
            "analisis_visual": True,
            "metadatos": True,
            "firmas": False,
            "calidad": True
        }
    }
}

UMBRALES = {
    "riesgo_alto": 0.7,
    "riesgo_medio": 0.5,
    "discrepancia_montos": 10,
    "calidad_minima": 100
}

# === FUNCTIONS THAT USE THE CONFIG ===

def es_tipo_documento_habilitado(tipo_documento: str) -> bool:
    """Verifica si un tipo de documento está habilitado."""
    return TIPOS_DOCUMENTOS.get(tipo_documento, {}).get("habilitado", False)

def obtener_validaciones_documento(tipo_documento: str) -> Dict[str, bool]:
    """Obtiene las validaciones habilitadas para un tipo de documento."""
    return TIPOS_DOCUMENTOS.get(tipo_documento, {}).get("validaciones", {})

def procesar_documentos_subidos(uploaded_files: List[Any], modelo: ModeloIA) -> Dict[str, Any]:
    """
    Procesa los documentos subidos y realiza las comparaciones necesarias.
    """
    if not uploaded_files:
        return None
    
    # Clasificar documentos
    documentos_clasificados = []
    for file in uploaded_files:
        texto = extraccion_texto(file)
        tipo = modelo.clasificar_documento(texto)
        
        # USE TIPOS_DOCUMENTOS: Validar si el tipo está habilitado
        if es_tipo_documento_habilitado(tipo):
            documentos_clasificados.append({"tipo": tipo, "texto": texto})
        else:
            st.warning(f"Tipo de documento '{tipo}' no está habilitado para procesamiento.")
    
    # Separar documentos
    documentos_separados = separar_documentos(documentos_clasificados)
    
    # Comparar si hay carta laboral y colillas
    if documentos_separados["carta_laboral"] and documentos_separados["colillas_pago"]:
        return {
            **documentos_separados,
            "resultado_comparacion": modelo.comparar_documentos(
                documentos_separados["carta_laboral"], 
                documentos_separados["colillas_pago"]
            )
        }
    
    return documentos_separados

def separar_documentos(documentos_clasificados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Separa los documentos en carta laboral y colillas de pago.
    """
    carta_laboral = None
    colillas_pago = []
    
    for doc in documentos_clasificados:
        tipo = doc["tipo"]
        
        # USE TIPOS_DOCUMENTOS: Solo procesar tipos habilitados
        if not es_tipo_documento_habilitado(tipo):
            continue
            
        if tipo == "carta laboral":
            carta_laboral = doc["texto"]
        elif tipo == "colilla de pago":
            colillas_pago.append(doc["texto"])
    
    return {
        "carta_laboral": carta_laboral,
        "colillas_pago": colillas_pago
    }

def validar_calidad_documento(porcentaje_confianza: float) -> str:
    """
    Valida la calidad del documento usando los umbrales configurados.
    """
    if porcentaje_confianza >= UMBRALES["riesgo_alto"]:
        return "Alta confianza"
    elif porcentaje_confianza >= UMBRALES["riesgo_medio"]:
        return "Media confianza"
    else:
        return "Baja confianza"
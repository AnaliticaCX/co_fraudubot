# services/extraccion.py
"""
Módulo para la extracción de texto y datos de documentos.
"""
from libreria.extraction_texto import extraccion_texto
from libreria.modelos_ia import ModeloIA

# TODO: Recibir el modelo como parámetro o inyectar dependencia

def extraer_texto(file_path):
    return extraccion_texto(file_path)

# TODO: Esta función asume que el modelo es global, mejorar para inyectar modelo

def extraer_datos_carta_laboral(modelo, texto):
    return modelo.extraer_datos_carta_laboral(texto)

def extraer_datos_extracto_bancario(modelo, texto):
    return modelo.extraer_datos_extracto_bancario(texto)

def extraer_datos_colilla_pago(modelo, texto):
    return modelo.extraer_datos_colilla_pago(texto) 
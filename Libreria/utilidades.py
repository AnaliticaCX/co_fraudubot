import streamlit as st
from typing import Dict, Any, List
import json
import os
import re
from joblib import load
from libreria.modelos_ia import ModeloIA
from libreria.modelo_local import ModeloDeepSeek

# Carga de modelos de machine learning
RUTA_RF = './Modelos_Entrenados/Model_RF.pkl'
RUTA_RL = './Modelos_Entrenados/Model_RL_R.pkl'

model_rf = load(RUTA_RF)
model_rl = load(RUTA_RL)

# TODO: Permitir seleccionar el modelo desde fuera de este módulo


def formatear_valor_monetario(valor: Any) -> str:
    """
    Formatea un valor monetario con el símbolo de peso y separadores de miles.
    """
    try:
        if isinstance(valor, str):
            # Eliminar caracteres no numéricos
            valor = ''.join(filter(str.isdigit, valor))
            valor = int(valor)
        return f"${valor:,}"
    except:
        return "$0"

def mostrar_resultados_comparacion(resultados: Dict[str, Any]) -> None:
    """
    Muestra los resultados de la comparación en la interfaz de Streamlit.
    """
    st.subheader("Resultados de la Comparación")
    st.write(f"Porcentaje de coincidencia: {resultados['porcentaje']}")
    st.write(f"Explicación: {resultados['explicacion']}")
    
    if 'resultados_individuales' in resultados:
        st.subheader("Resultados por Colilla")
        for i, resultado in enumerate(resultados['resultados_individuales'], 1):
            st.write(f"Colilla {i}:")
            st.write(f"- Porcentaje: {resultado['porcentaje']}")
            st.write(f"- Explicación: {resultado['explicacion']}")
            if resultado['no_coincide']:
                st.write("Diferencias encontradas:")
                for campo, valores in resultado['no_coincide'].items():
                    st.write(f"- {campo}:")
                    st.write(f"  - Carta Laboral: {valores['carta_laboral']}")
                    st.write(f"  - Colilla de Pago: {valores['colilla_pago']}")
            st.write("---")

def mostrar_datos_carta_laboral(datos: Dict[str, str]) -> None:
    """
    Muestra los datos extraídos de la carta laboral en la interfaz de Streamlit.
    """
    if datos:
        st.subheader("Datos de la Carta Laboral")
        
        # Datos personales
        st.write("**Datos Personales:**")
        st.write(f"- Nombre: {datos.get('nombre', 'No disponible')}")
        st.write(f"- Cédula: {datos.get('cedula', 'No disponible')}")
        st.write(f"- Origen Cédula: {datos.get('de_donde_es_la_cedula', 'No disponible')}")
        
        # Datos laborales
        st.write("**Datos Laborales:**")
        st.write(f"- Cargo: {datos.get('cargo', 'No disponible')}")
        st.write(f"- Tipo de Contrato: {datos.get('tipo_de_contrato', 'No disponible')}")
        st.write(f"- Salario: {formatear_valor_monetario(datos.get('salario', '0'))}")
        st.write(f"- Bonificación: {formatear_valor_monetario(datos.get('bonificacion', '0'))}")
        
        # Datos de la empresa
        st.write("**Datos de la Empresa:**")
        st.write(f"- Nombre: {datos.get('nombre_de_la_empresa', 'No disponible')}")
        st.write(f"- NIT: {datos.get('nit_de_la_empresa', 'No disponible')}")
        
        # Fechas
        st.write("**Fechas:**")
        st.write(f"- Inicio: {datos.get('fecha_inicio_labor', 'No disponible')}")
        st.write(f"- Fin: {datos.get('fecha_fin_labor', 'No disponible')}")
        st.write(f"- Expedición: {datos.get('fecha_de_expedicion_carta', 'No disponible')}")


def obtener_modelo_ia(nombre_modelo):
    """Obtiene el modelo de IA seleccionado."""
    if nombre_modelo.lower() == "openai":
        return ModeloIA("openai", os.getenv("OPENAI_API_KEY"))
    elif nombre_modelo.lower() == "gemini":
        return ModeloIA("gemini", os.getenv("GOOGLE_API_KEY"))
    elif nombre_modelo.lower() == "deepseek local":
        return ModeloDeepSeek()
    else:
        raise ValueError("Modelo IA no soportado")

# === UTILIDADES (merged from utilidades.py) ===

def formatear_valor_monetario(valor):
    """
    Formatea un valor monetario para estandarizar su representación.
    
    Args:
        valor (str): Valor monetario a formatear
        
    Returns:
        str: Valor formateado
    """
    if not valor or valor == "No especificado":
        return "No especificado"
    
    # Remover espacios y convertir a string
    valor_str = str(valor).strip()
    
    # Si ya está formateado, devolverlo
    if valor_str.startswith("$"):
        return valor_str
    
    # Remover caracteres no numéricos excepto puntos y comas
    valor_limpio = re.sub(r'[^\d.,]', '', valor_str)
    
    if not valor_limpio:
        return "No especificado"
    
    try:
        # Convertir a float para validar
        valor_float = float(valor_limpio.replace(',', ''))
        
        # Formatear con separadores de miles
        valor_formateado = f"${valor_float:,.0f}"
        
        return valor_formateado
    except ValueError:
        return valor_str

def limpiar_texto(texto):
    """
    Limpia y normaliza texto extraído de documentos.
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if not texto:
        return ""
    
    # Remover caracteres especiales y normalizar espacios
    texto_limpio = re.sub(r'\s+', ' ', texto.strip())
    
    return texto_limpio

def validar_numero_documento(numero):
    """
    Valida que un número de documento tenga un formato correcto.
    
    Args:
        numero (str): Número de documento a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    if not numero:
        return False
    
    # Remover espacios y caracteres especiales
    numero_limpio = re.sub(r'[^\d]', '', str(numero))
    
    # Validar longitud (entre 6 y 12 dígitos para documentos colombianos)
    return 6 <= len(numero_limpio) <= 12

def extraer_nit_de_texto(texto):
    """
    Extrae el NIT de un texto usando expresiones regulares.
    
    Args:
        texto (str): Texto donde buscar el NIT
        
    Returns:
        str: NIT encontrado o None
    """
    if not texto:
        return None
    
    # Patrones para NIT
    patrones_nit = [
        r'NIT[:\s]*(\d{3,12}[-]?\d?)',
        r'Nit[:\s]*(\d{3,12}[-]?\d?)',
        r'nit[:\s]*(\d{3,12}[-]?\d?)',
    ]
    
    for patron in patrones_nit:
        match = re.search(patron, texto)
        if match:
            return match.group(1)
    
    return None

import re

def limpiar_nit(nit):
    """
    Devuelve solo los dígitos antes del guion del NIT.
    Ejemplo: '900.469.873-1' -> '900469873'
    """
    import re
    # Quitar todo lo que no sea dígito o guion
    nit = re.sub(r"[^\d\-]", "", nit)
    # Separar por guion y tomar la primera parte
    nit_base = nit.split('-')[0]
    return nit_base

def extraer_nit_de_texto(texto):
    """
    Extrae el NIT de un texto usando expresiones regulares.
    
    Args:
        texto (str): Texto donde buscar el NIT
        
    Returns:
        str: NIT encontrado o None
    """
    if not texto:
        return None
    
    # Patrones para NIT
    patrones_nit = [
        r'NIT[:\s]*(\d{3,12}[-]?\d?)',
        r'Nit[:\s]*(\d{3,12}[-]?\d?)',
        r'nit[:\s]*(\d{3,12}[-]?\d?)',
    ]
    
    for patron in patrones_nit:
        match = re.search(patron, texto)
        if match:
            return limpiar_nit(match.group(1))
    
    return None
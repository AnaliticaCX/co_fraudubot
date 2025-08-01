# services/utilidades.py
"""
Módulo de utilidades generales para el proyecto.
"""

# TODO: Añadir más utilidades según se requiera

from typing import Dict, Any
import json


def formatear_valor_monetario(valor):
    """
    Formatea un valor monetario, manejando diferentes tipos de entrada.
    """
    try:
        if isinstance(valor, str):
            valor = valor.replace(",", "")  # Elimina las comas
            valor = float(valor)
        valor = int(valor)
        return f"${valor:,}"
    except (ValueError, TypeError):
        return "$0"

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


def formatear_valor_monetario(valor: Any) -> str:
    """
    Formatea un valor monetario con el símbolo de dólar y separadores de miles.
    """
    try:
        if isinstance(valor, str):
            # Eliminar caracteres no numéricos
            valor = ''.join(filter(str.isdigit, valor))
            valor = int(valor) if valor else 0
        elif isinstance(valor, (int, float)):
            valor = int(valor)
        else:
            return "$0"
        
        return f"${valor:,}"
    except:
        return "$0"

def extraer_json_respuesta(respuesta: str) -> Dict[str, Any]:
    """
    Extrae un JSON de una respuesta de texto.
    """
    try:
        inicio_json = respuesta.find('{')
        fin_json = respuesta.rfind('}') + 1
        if inicio_json >= 0 and fin_json > inicio_json:
            json_str = respuesta[inicio_json:fin_json]
            return json.loads(json_str)
    except:
        pass
    return {}

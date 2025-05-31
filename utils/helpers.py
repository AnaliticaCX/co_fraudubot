from typing import Dict, Any
import json

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

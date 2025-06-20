# services/utilidades.py
"""
Módulo de utilidades generales para el proyecto.
"""

# TODO: Añadir más utilidades según se requiera

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
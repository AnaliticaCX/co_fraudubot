# services/comparacion.py
"""
Módulo para la comparación de documentos.
"""
# TODO: Recibir el modelo como parámetro o inyectar dependencia

def comparar_documentos(modelo, texto1, texto2):
    return modelo.comparar_documentos(texto1, texto2)

def calcular_promedio_coincidencias(resultados_colillas):
    """
    Calcula el promedio de coincidencias entre las colillas de pago.
    """
    if not resultados_colillas:
        return {
            "coincidencia": "0%",
            "explicacion": "No hay colillas para comparar",
            "detalles": []
        }
    porcentajes = []
    detalles = []
    for resultado in resultados_colillas:
        if "error" in resultado:
            continue
        try:
            porcentaje = float(resultado["porcentaje"].strip('%'))
            porcentajes.append(porcentaje)
            detalles.append({
                "porcentaje": resultado["porcentaje"],
                "explicacion": resultado["explicacion"],
                "no_coincide": resultado["no_coincide"]
            })
        except (ValueError, KeyError):
            continue
    if not porcentajes:
        return {
            "coincidencia": "0%",
            "explicacion": "No se pudieron procesar los porcentajes",
            "detalles": []
        }
    promedio = sum(porcentajes) / len(porcentajes)
    return {
        "coincidencia": f"{promedio:.2f}%",
        "explicacion": f"coincidencia entre {len(porcentajes)} colillas de pago",
        "detalles": detalles
    } 
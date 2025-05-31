# libreria/config.py

# Configuración de tipos de documentos a validar
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
            "firmas": False,  # Los extractos bancarios no suelen tener firmas
            "calidad": True
        }
    }
}

# Configuración de umbrales
UMBRALES = {
    "riesgo_alto": 0.7,
    "riesgo_medio": 0.5,
    "discrepancia_montos": 10,
    "calidad_minima": 100
}
# servicios/modelos.py
"""
Módulo para la carga y configuración de modelos de IA.
"""
import os
from joblib import load
from libreria.modelos_ia import ModeloIA
from libreria.modelo_local import ModeloDeepSeek

# TODO: Considerar parametrizar las rutas y las API keys en un archivo de configuración
OPENAI_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyAleWdBrBo9G0X9X3HRT2YAxAz2n75-56Y"

# Carga de modelos de machine learning
RUTA_RF = './Modelos_Entrenados/Model_RF.pkl'
RUTA_RL = './Modelos_Entrenados/Model_RL_R.pkl'

model_rf = load(RUTA_RF)
model_rl = load(RUTA_RL)

# TODO: Permitir seleccionar el modelo desde fuera de este módulo

def obtener_modelo_ia(nombre_modelo):
    if nombre_modelo.lower() == "openai":
        return ModeloIA("openai", OPENAI_API_KEY)
    elif nombre_modelo.lower() == "gemini":
        return ModeloIA("gemini", GEMINI_API_KEY)
    elif nombre_modelo.lower() == "deepseek local":
        return ModeloDeepSeek()
    else:
        raise ValueError("Modelo IA no soportado") 
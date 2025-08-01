"""
Módulo para la carga y configuración de modelos de IA.
"""
import os
from joblib import load
from libreria.modelos_ia import ModeloIA
from libreria.modelo_local import ModeloDeepSeek


# Carga de modelos de machine learning
RUTA_RF = './Modelos_Entrenados/Model_RF.pkl'
RUTA_RL = './Modelos_Entrenados/Model_RL_R.pkl'

model_rf = load(RUTA_RF)
model_rl = load(RUTA_RL)

# TODO: Permitir seleccionar el modelo desde fuera de este módulo

import os
from joblib import load
from libreria.modelos_ia import ModeloIA
from libreria.modelo_local import ModeloDeepSeek

# ...existing code...

def obtener_modelo_ia(nombre_modelo):
    if nombre_modelo.lower() == "openai":
        return ModeloIA("openai", os.getenv("OPENAI_API_KEY"))
    elif nombre_modelo.lower() == "gemini":
        return ModeloIA("gemini", os.getenv("GEMINI_API_KEY"))
    elif nombre_modelo.lower() == "deepseek local":
        return ModeloDeepSeek()
    else:
        raise ValueError("Modelo IA no soportado")
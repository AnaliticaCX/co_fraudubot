# services/visual.py
"""
Módulo para el análisis visual de documentos (PDF e imágenes).
"""
import os
import cv2
import numpy as np
from PIL import Image
import pdf2image
import tempfile

# TODO: Considerar separar la lógica de análisis de imágenes y PDF

def convertir_pdf_a_imagen(pdf_path):
    try:
        temp_dir = tempfile.mkdtemp()
        images = pdf2image.convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir, f'page_{i}.png')
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
        return image_paths
    except Exception:
        return []

def analizar_documento_visual(archivo_path):
    try:
        es_pdf = archivo_path.lower().endswith('.pdf')
        if es_pdf:
            image_paths = convertir_pdf_a_imagen(archivo_path)
            if not image_paths:
                return {"error": "No se pudo convertir el PDF a imágenes"}
            resultados_por_pagina = []
            for img_path in image_paths:
                resultado = analizar_imagen(img_path)
                resultados_por_pagina.append(resultado)
            resultado_final = combinar_resultados(resultados_por_pagina)
            for img_path in image_paths:
                try:
                    os.remove(img_path)
                except Exception:
                    pass
            return resultado_final
        else:
            return analizar_imagen(archivo_path)
    except Exception as e:
        return {"error": f"Error en el análisis visual: {str(e)}"}

def analizar_imagen(imagen_path):
    try:
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": "No se pudo cargar la imagen"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        def detectar_sellos(imagen):
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            sellos = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 1000 < area < 10000:
                    sellos.append(cnt)
            return len(sellos)
        def detectar_firmas(imagen):
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            firmas = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 20:
                    firmas.append((x, y, w, h))
            return firmas
        def analizar_calidad(imagen):
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            contrast = np.std(gray)
            return {
                "nitidez": sharpness,
                "contraste": contrast
            }
        def detectar_marcas_agua(imagen):
            if len(imagen.shape) == 3:
                gray_local = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            else:
                gray_local = imagen
            thresh = cv2.adaptiveThreshold(
                gray_local, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            marcas_agua = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 500 < area < 5000:
                    marcas_agua.append(cnt)
            return len(marcas_agua)
        resultados = {
            "numero_sellos": detectar_sellos(img),
            "firmas_detectadas": detectar_firmas(img),
            "calidad": analizar_calidad(img),
            "marcas_agua": detectar_marcas_agua(img),
            "sospechas": []
        }
        if resultados["numero_sellos"] == 0:
            resultados["sospechas"].append("No se detectaron sellos en el documento")
        if len(resultados["firmas_detectadas"]) == 0:
            resultados["sospechas"].append("No se detectaron firmas en el documento")
        if resultados["calidad"]["nitidez"] < 100:
            resultados["sospechas"].append("La calidad de la imagen es baja")
        if resultados["marcas_agua"] == 0:
            resultados["sospechas"].append("No se detectaron marcas de agua")
        return resultados
    except Exception as e:
        return {"error": f"Error en el análisis visual: {str(e)}"}

def combinar_resultados(resultados_por_pagina):
    resultado_final = {
        "numero_sellos": 0,
        "firmas_detectadas": [],
        "calidad": {
            "nitidez": 0,
            "contraste": 0
        },
        "marcas_agua": 0,
        "sospechas": []
    }
    for resultado in resultados_por_pagina:
        if "error" in resultado:
            continue
        resultado_final["numero_sellos"] += resultado["numero_sellos"]
        resultado_final["firmas_detectadas"].extend(resultado["firmas_detectadas"])
        resultado_final["calidad"]["nitidez"] = max(
            resultado_final["calidad"]["nitidez"],
            resultado["calidad"]["nitidez"]
        )
        resultado_final["calidad"]["contraste"] = max(
            resultado_final["calidad"]["contraste"],
            resultado["calidad"]["contraste"]
        )
        resultado_final["marcas_agua"] += resultado["marcas_agua"]
        resultado_final["sospechas"].extend(resultado["sospechas"])
    return resultado_final 
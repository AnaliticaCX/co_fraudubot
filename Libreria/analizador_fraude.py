import cv2
import numpy as np
from PIL import Image
import pytesseract
from scipy import signal
import hashlib
from datetime import datetime
import re
import os

class AnalizadorFraude:
    def __init__(self):
        self.patrones_impresion = {}
        self.firmas_verificadas = set()
        self.umbral_riesgo = 0.7

    def analizar_documento_completo(self, archivo_path, texto_extraido):
        """
        Realiza un análisis completo del documento para detectar fraudes.
        """
        resultados = {
            "puntuacion_riesgo": 0,
            "alertas": [],
            "detalles": {},
            "recomendaciones": []
        }

        # 1. Análisis de consistencia de datos
        consistencia = self.analizar_consistencia_datos(texto_extraido)
        resultados["detalles"]["consistencia"] = consistencia
        resultados["puntuacion_riesgo"] += consistencia["puntuacion"]

        # 2. Análisis de manipulación de imagen
        manipulacion = self.detectar_manipulacion_imagen(archivo_path)
        resultados["detalles"]["manipulacion"] = manipulacion
        resultados["puntuacion_riesgo"] += manipulacion["puntuacion"]

        # 3. Análisis de patrones de impresión
        patrones = self.analizar_patrones_impresion(archivo_path)
        resultados["detalles"]["patrones"] = patrones
        resultados["puntuacion_riesgo"] += patrones["puntuacion"]

        # 4. Verificación de firmas
        firmas = self.verificar_firmas(archivo_path)
        resultados["detalles"]["firmas"] = firmas
        resultados["puntuacion_riesgo"] += firmas["puntuacion"]

        # 5. Análisis de calidad y autenticidad
        calidad = self.analizar_calidad_autenticidad(archivo_path)
        resultados["detalles"]["calidad"] = calidad
        resultados["puntuacion_riesgo"] += calidad["puntuacion"]

        # Normalizar puntuación
        resultados["puntuacion_riesgo"] = min(1.0, resultados["puntuacion_riesgo"] / 5.0)

        # Generar alertas y recomendaciones
        self.generar_alertas_recomendaciones(resultados)

        return resultados

    def analizar_consistencia_datos(self, texto):
        """
        Analiza la consistencia de los datos en el documento.
        """
        resultados = {
            "puntuacion": 0,
            "alertas": [],
            "detalles": {}
        }

        # Extraer fechas
        fechas = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', texto)
        if fechas:
            resultados["detalles"]["fechas"] = fechas
            # Verificar consistencia de fechas
            if len(set(fechas)) != len(fechas):
                resultados["alertas"].append("Se encontraron fechas duplicadas")
                resultados["puntuacion"] += 0.2

        # Extraer montos
        montos = re.findall(r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', texto)
        if montos:
            resultados["detalles"]["montos"] = montos
            # Verificar consistencia de montos
            montos_numericos = [float(m.replace('$', '').replace(',', '')) for m in montos]
            if max(montos_numericos) / min(montos_numericos) > 10:
                resultados["alertas"].append("Hay una gran discrepancia entre los montos")
                resultados["puntuacion"] += 0.2

        # Verificar consistencia de nombres
        nombres = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', texto)
        if nombres:
            resultados["detalles"]["nombres"] = nombres
            if len(set(nombres)) != len(nombres):
                resultados["alertas"].append("Se encontraron nombres duplicados con diferentes formatos")
                resultados["puntuacion"] += 0.2

        return resultados

    def detectar_manipulacion_imagen(self, imagen_path):
        """
        Detecta posibles manipulaciones en la imagen.
        """
        resultados = {
            "puntuacion": 0,
            "alertas": [],
            "detalles": {}
        }

        try:
            # Cargar imagen
            img = cv2.imread(imagen_path)
            if img is None:
                return resultados

            # 1. Análisis de Error Level Analysis (ELA)
            ela_result = self.analizar_ela(img)
            resultados["detalles"]["ela"] = ela_result
            if ela_result["sospechoso"]:
                resultados["alertas"].append("Se detectaron posibles manipulaciones en la imagen")
                resultados["puntuacion"] += 0.3

            # 2. Análisis de ruido
            ruido_result = self.analizar_ruido(img)
            resultados["detalles"]["ruido"] = ruido_result
            if ruido_result["sospechoso"]:
                resultados["alertas"].append("Patrones de ruido inconsistentes detectados")
                resultados["puntuacion"] += 0.2

            # 3. Análisis de compresión
            compresion_result = self.analizar_compresion(img)
            resultados["detalles"]["compresion"] = compresion_result
            if compresion_result["sospechoso"]:
                resultados["alertas"].append("Patrones de compresión inconsistentes")
                resultados["puntuacion"] += 0.2

        except Exception as e:
            resultados["alertas"].append(f"Error en análisis de manipulación: {str(e)}")

        return resultados

    def analizar_ela(self, img):
        """
        Realiza Error Level Analysis para detectar manipulaciones.
        """
        try:
            # Guardar imagen temporalmente con calidad específica
            temp_path = "temp_ela.jpg"
            cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            # Cargar imagen comprimida
            compressed = cv2.imread(temp_path)
            
            # Calcular diferencia
            diff = cv2.absdiff(img, compressed)
            
            # Analizar patrones en la diferencia
            mean_diff = np.mean(diff)
            std_diff = np.std(diff)
            
            # Limpiar archivo temporal
            os.remove(temp_path)
            
            return {
                "sospechoso": mean_diff > 10 or std_diff > 5,
                "mean_diff": mean_diff,
                "std_diff": std_diff
            }
        except:
            return {"sospechoso": False}

    def analizar_ruido(self, img):
        """
        Analiza patrones de ruido en la imagen.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtro de ruido
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Calcular diferencia
            diff = cv2.absdiff(gray, denoised)
            
            # Analizar patrones
            mean_noise = np.mean(diff)
            std_noise = np.std(diff)
            
            return {
                "sospechoso": std_noise > 20,
                "mean_noise": mean_noise,
                "std_noise": std_noise
            }
        except:
            return {"sospechoso": False}

    def analizar_compresion(self, img):
        """
        Analiza patrones de compresión en la imagen.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar DCT
            dct = cv2.dct(np.float32(gray))
            
            # Analizar coeficientes DCT
            dct_mean = np.mean(np.abs(dct))
            dct_std = np.std(dct)
            
            return {
                "sospechoso": dct_std > 100,
                "dct_mean": dct_mean,
                "dct_std": dct_std
            }
        except:
            return {"sospechoso": False}

    def analizar_patrones_impresion(self, imagen_path):
        """
        Analiza patrones de impresión en el documento.
        """
        resultados = {
            "puntuacion": 0,
            "alertas": [],
            "detalles": {}
        }

        try:
            # Cargar imagen
            img = cv2.imread(imagen_path)
            if img is None:
                return resultados

            # 1. Análisis de patrones de puntos
            patrones_puntos = self.analizar_patrones_puntos(img)
            resultados["detalles"]["patrones_puntos"] = patrones_puntos
            if patrones_puntos["sospechoso"]:
                resultados["alertas"].append("Patrones de impresión inconsistentes detectados")
                resultados["puntuacion"] += 0.2

            # 2. Análisis de resolución
            resolucion = self.analizar_resolucion(img)
            resultados["detalles"]["resolucion"] = resolucion
            if resolucion["sospechoso"]:
                resultados["alertas"].append("Resolución de impresión sospechosa")
                resultados["puntuacion"] += 0.2

        except Exception as e:
            resultados["alertas"].append(f"Error en análisis de patrones: {str(e)}")

        return resultados

    def analizar_patrones_puntos(self, img):
        """
        Analiza patrones de puntos en la impresión.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbral adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Analizar distribución de puntos
            areas = [cv2.contourArea(cnt) for cnt in contours]
            mean_area = np.mean(areas)
            std_area = np.std(areas)
            
            return {
                "sospechoso": std_area > mean_area * 0.5,
                "mean_area": mean_area,
                "std_area": std_area
            }
        except:
            return {"sospechoso": False}

    def analizar_resolucion(self, img):
        """
        Analiza la resolución de la imagen.
        """
        try:
            height, width = img.shape[:2]
            dpi = 300  # Asumimos 300 DPI para impresoras estándar
            
            # Calcular resolución efectiva
            resolucion_efectiva = min(width, height) / 8.5  # 8.5 pulgadas es el ancho estándar de una hoja
            
            return {
                "sospechoso": resolucion_efectiva < 200 or resolucion_efectiva > 600,
                "resolucion_efectiva": resolucion_efectiva
            }
        except:
            return {"sospechoso": False}

    def verificar_firmas(self, imagen_path):
        """
        Verifica la autenticidad de las firmas.
        """
        resultados = {
            "puntuacion": 0,
            "alertas": [],
            "detalles": {}
        }

        try:
            # Cargar imagen
            img = cv2.imread(imagen_path)
            if img is None:
                return resultados

            # 1. Detección de firmas
            firmas = self.detectar_firmas(img)
            resultados["detalles"]["firmas_detectadas"] = len(firmas)

            # 2. Análisis de calidad de firmas
            calidad_firmas = self.analizar_calidad_firmas(firmas)
            resultados["detalles"]["calidad_firmas"] = calidad_firmas

            if calidad_firmas["sospechoso"]:
                resultados["alertas"].append("Calidad de firmas sospechosa")
                resultados["puntuacion"] += 0.3

            # 3. Verificación de consistencia
            if len(firmas) > 0:
                consistencia = self.verificar_consistencia_firmas(firmas)
                resultados["detalles"]["consistencia_firmas"] = consistencia
                if consistencia["sospechoso"]:
                    resultados["alertas"].append("Inconsistencia en las firmas detectadas")
                    resultados["puntuacion"] += 0.2

        except Exception as e:
            resultados["alertas"].append(f"Error en verificación de firmas: {str(e)}")

        return resultados

    def detectar_firmas(self, img):
        """
        Detecta firmas en la imagen.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbral adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtrar contornos que podrían ser firmas
            firmas = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 20:  # Ajustar según necesidad
                    firmas.append((x, y, w, h))
            
            return firmas
        except:
            return []

    def analizar_calidad_firmas(self, firmas):
        """
        Analiza la calidad de las firmas detectadas.
        """
        try:
            if not firmas:
                return {"sospechoso": True}

            # Calcular estadísticas de las firmas
            areas = [w * h for x, y, w, h in firmas]
            mean_area = np.mean(areas)
            std_area = np.std(areas)

            return {
                "sospechoso": std_area > mean_area * 0.5,
                "mean_area": mean_area,
                "std_area": std_area
            }
        except:
            return {"sospechoso": True}

    def verificar_consistencia_firmas(self, firmas):
        """
        Verifica la consistencia entre las firmas detectadas.
        """
        try:
            if len(firmas) < 2:
                return {"sospechoso": False}

            # Calcular diferencias entre firmas
            areas = [w * h for x, y, w, h in firmas]
            mean_area = np.mean(areas)
            std_area = np.std(areas)

            return {
                "sospechoso": std_area > mean_area * 0.3,
                "mean_area": mean_area,
                "std_area": std_area
            }
        except:
            return {"sospechoso": True}

    def analizar_calidad_autenticidad(self, imagen_path):
        """
        Analiza la calidad y autenticidad general del documento.
        """
        resultados = {
            "puntuacion": 0,
            "alertas": [],
            "detalles": {}
        }

        try:
            # Cargar imagen
            img = cv2.imread(imagen_path)
            if img is None:
                return resultados

            # 1. Análisis de calidad general
            calidad = self.analizar_calidad_general(img)
            resultados["detalles"]["calidad_general"] = calidad
            if calidad["sospechoso"]:
                resultados["alertas"].append("Calidad general del documento sospechosa")
                resultados["puntuacion"] += 0.2

            # 2. Análisis de elementos de seguridad
            seguridad = self.analizar_elementos_seguridad(img)
            resultados["detalles"]["elementos_seguridad"] = seguridad
            if seguridad["sospechoso"]:
                resultados["alertas"].append("Faltan elementos de seguridad esperados")
                resultados["puntuacion"] += 0.3

        except Exception as e:
            resultados["alertas"].append(f"Error en análisis de calidad: {str(e)}")

        return resultados

    def analizar_calidad_general(self, img):
        """
        Analiza la calidad general de la imagen.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calcular métricas de calidad
            blur = cv2.Laplacian(gray, cv2.CV_64F).var()
            contrast = np.std(gray)
            
            return {
                "sospechoso": blur < 100 or contrast < 50,
                "blur": blur,
                "contrast": contrast
            }
        except:
            return {"sospechoso": True}

    def analizar_elementos_seguridad(self, img):
        """
        Analiza la presencia de elementos de seguridad.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Buscar patrones que podrían ser elementos de seguridad
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Contar elementos de seguridad
            elementos_seguridad = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 100 < area < 1000:  # Ajustar según necesidad
                    elementos_seguridad += 1
            
            return {
                "sospechoso": elementos_seguridad < 3,
                "elementos_detectados": elementos_seguridad
            }
        except:
            return {"sospechoso": True}

    def generar_alertas_recomendaciones(self, resultados):
        """
        Genera alertas y recomendaciones basadas en los resultados del análisis.
        """
        puntuacion = resultados["puntuacion_riesgo"]
        
        if puntuacion > 0.8:
            resultados["alertas"].append("ALTO RIESGO: Se detectaron múltiples indicadores de posible fraude")
            resultados["recomendaciones"].append("Revisar el documento físicamente")
            resultados["recomendaciones"].append("Solicitar documentación adicional")
        elif puntuacion > 0.5:
            resultados["alertas"].append("RIESGO MEDIO: Se detectaron algunos indicadores sospechosos")
            resultados["recomendaciones"].append("Verificar la autenticidad del documento")
            resultados["recomendaciones"].append("Comparar con documentos originales")
        else:
            resultados["alertas"].append("RIESGO BAJO: No se detectaron indicadores claros de fraude")
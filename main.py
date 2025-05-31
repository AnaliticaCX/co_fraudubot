import streamlit as st
# Primero, configurar la página
st.set_page_config(
    page_title="Fraudubot - Análisis de Documentos",
    page_icon="🔍",
    layout="wide"
)

# Luego, importar el resto de las dependencias
import os
import json
import pandas as pd
from joblib import load
from libreria.extraction_texto import extraccion_texto
from libreria.chat_gpt import chat_with_gpt
import cv2
import numpy as np
from PIL import Image
import pdf2image
import tempfile
from datetime import datetime
import PyPDF2
import piexif
import exifread
import magic  # para detectar el tipo de archivo
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from libreria.modelos_ia import ModeloIA
from libreria.modelo_local import ModeloDeepSeek

# --- MODELOS Y BASE DE DATOS ---
model_rf = load('./Modelos_Entrenados/Model_RF.pkl')
model_rl = load('./Modelos_Entrenados/Model_RL_R.pkl')
fraude = pd.read_excel("./Datos/BASE_PARA_PREDICT.xlsx")

# --- FUNCIONES AUXILIARES ---

# Configuración de API keys
OPENAI_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyAleWdBrBo9G0X9X3HRT2YAxAz2n75-56Y"

# Selección del modelo
st.sidebar.title("⚙️ Configuración")
modelo_seleccionado = st.sidebar.radio(
    "Selecciona el modelo de IA:",
    ["OpenAI", "Gemini", "DeepSeek Local"],
    index=0
)

# Inicializar el modelo seleccionado
if modelo_seleccionado == "OpenAI":
    modelo = ModeloIA("openai", OPENAI_API_KEY)
elif modelo_seleccionado == "Gemini":
    modelo = ModeloIA("gemini", GEMINI_API_KEY)
else:  # DeepSeek Local
    modelo = ModeloDeepSeek()

# Mostrar el modelo seleccionado
st.sidebar.info(f"Modelo actual: {modelo_seleccionado}")

def extract_text(file_path):
    return extraccion_texto(file_path)

def clasificar_documento(texto):
    return modelo.clasificar_documento(texto)

def extract_with_matcher(text):
    return modelo.extraer_datos_carta_laboral(text)

def calcular_promedio_coincidencias(resultados_colillas):
    """
    Calcula el promedio de coincidencias entre las colillas de pago.
    
    Args:
        resultados_colillas (list): Lista de resultados de comparación de colillas
        
    Returns:
        dict: Diccionario con el promedio y detalles
    """
    if not resultados_colillas:
        return {
            "promedio": "0%",
            "explicacion": "No hay colillas para comparar",
            "detalles": []
        }
    
    # Extraer porcentajes y convertirlos a números
    porcentajes = []
    detalles = []
    
    for resultado in resultados_colillas:
        if "error" in resultado:
            continue
            
        try:
            # Extraer el número del porcentaje (eliminar el símbolo %)
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
            "promedio": "0%",
            "explicacion": "No se pudieron procesar los porcentajes",
            "detalles": []
        }
    
    # Calcular promedio
    promedio = sum(porcentajes) / len(porcentajes)
    
    return {
        "promedio": f"{promedio:.2f}%",
        "explicacion": f"Promedio de coincidencia entre {len(porcentajes)} colillas de pago",
        "detalles": detalles
    }
# Datos de la empresa
def formatear_valor_monetario(valor):
    """
    Formatea un valor monetario, manejando diferentes tipos de entrada.
    """
    try:
        # Si es string, intentar convertir a float primero
        if isinstance(valor, str):
            valor = float(valor)
        # Convertir a entero
        valor = int(valor)
        return f"${valor:,}"
    except (ValueError, TypeError):
        return "$0"

def compracion_documentos(texto1, texto2):
    """
    Compara dos documentos usando el modelo seleccionado.
    
    Args:
        texto1 (str): Texto del primer documento
        texto2 (str): Texto del segundo documento
    """
    return modelo.comparar_documentos(texto1, texto2)

def calcular_probabilidad(fraude_data, cedula, model_rf, model_rl):
    caso = fraude_data[fraude_data['CEDULA'] == cedula]
    if caso.empty:
        return None, "Cédula no encontrada en base de datos."

    caso_preparado = caso.drop(['CEDULA', 'N'], axis=1, errors='ignore')
    expected_columns = model_rf.feature_names_in_
    caso_preparado = caso_preparado[expected_columns]

    prob_rf = 1 - model_rf.predict_proba(caso_preparado)[:, 1]
    prob_lr = 1 - model_rl.predict_proba(caso_preparado)[:, 1]
    prob_ensamble = (0.4 * prob_rf) + (0.6 * prob_lr)

    return prob_ensamble[0], None

def convertir_pdf_a_imagen(pdf_path):
    """
    Convierte un PDF a una lista de imágenes.
    
    Args:
        pdf_path (str): Ruta al archivo PDF
        
    Returns:
        list: Lista de rutas a las imágenes temporales
    """
    try:
        # Crear directorio temporal si no existe
        temp_dir = tempfile.mkdtemp()
        
        # Convertir PDF a imágenes
        images = pdf2image.convert_from_path(pdf_path)
        
        # Guardar cada página como imagen temporal
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir, f'page_{i}.png')
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
            
        return image_paths
    except Exception as e:
        return []

def analizar_documento_visual(archivo_path):
    """
    Analiza elementos visuales de un documento (PDF o imagen).
    
    Args:
        archivo_path (str): Ruta al archivo (PDF o imagen)
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    try:
        # Determinar si es PDF o imagen
        es_pdf = archivo_path.lower().endswith('.pdf')
        
        if es_pdf:
            # Convertir PDF a imágenes
            image_paths = convertir_pdf_a_imagen(archivo_path)
            if not image_paths:
                return {"error": "No se pudo convertir el PDF a imágenes"}
            
            # Analizar cada página
            resultados_por_pagina = []
            for img_path in image_paths:
                resultado = analizar_imagen(img_path)
                resultados_por_pagina.append(resultado)
                
            # Combinar resultados
            resultado_final = combinar_resultados(resultados_por_pagina)
            
            # Limpiar archivos temporales
            for img_path in image_paths:
                try:
                    os.remove(img_path)
                except:
                    pass
                    
            return resultado_final
        else:
            # Si es imagen, analizar directamente
            return analizar_imagen(archivo_path)
            
    except Exception as e:
        return {"error": f"Error en el análisis visual: {str(e)}"}

def analizar_imagen(imagen_path):
    """
    Analiza una imagen individual.
    
    Args:
        imagen_path (str): Ruta a la imagen
        
    Returns:
        dict: Resultados del análisis
    """
    try:
        # Cargar imagen
        img = cv2.imread(imagen_path)
        if img is None:
            return {"error": "No se pudo cargar la imagen"}
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Detección de sellos
        def detectar_sellos(imagen):
            # Aplicar umbral adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )

            # Encontrar contornos
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Filtrar contornos por área (para detectar sellos)
            sellos = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 1000 < area < 10000:  # Ajustar estos valores según necesidad
                    sellos.append(cnt)

            return len(sellos)

        # 2. Detección de firmas
        def detectar_firmas(imagen):
            # Aplicar umbral para detectar trazos oscuros
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtrar contornos que podrían ser firmas
            firmas = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 20:  # Ajustar según necesidad
                    firmas.append((x, y, w, h))
            
            return firmas

        # 3. Análisis de calidad
        def analizar_calidad(imagen):
            # Calcular la varianza de Laplaciano para medir el enfoque
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # Calcular el contraste
            contrast = np.std(gray)
            
            return {
                "nitidez": sharpness,
                "contraste": contrast
            }

        # 4. Detección de marcas de agua
        def detectar_marcas_agua(imagen):
            # Convertir a escala de grises si no lo está
            if len(imagen.shape) == 3:
                gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            else:
                gray = imagen
                
            # Aplicar umbral adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Buscar patrones que podrían ser marcas de agua
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            marcas_agua = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 500 < area < 5000:  # Ajustar según necesidad
                    marcas_agua.append(cnt)
            
            return len(marcas_agua)

        # Realizar todos los análisis
        resultados = {
            "numero_sellos": detectar_sellos(img),
            "firmas_detectadas": detectar_firmas(img),
            "calidad": analizar_calidad(img),
            "marcas_agua": detectar_marcas_agua(img),
            "sospechas": []
        }

        # Evaluar resultados y generar sospechas
        if resultados["numero_sellos"] == 0:
            resultados["sospechas"].append("No se detectaron sellos en el documento")
        
        if len(resultados["firmas_detectadas"]) == 0:
            resultados["sospechas"].append("No se detectaron firmas en el documento")
            
        if resultados["calidad"]["nitidez"] < 100:  # Ajustar umbral según necesidad
            resultados["sospechas"].append("La calidad de la imagen es baja")
            
        if resultados["marcas_agua"] == 0:
            resultados["sospechas"].append("No se detectaron marcas de agua")

        return resultados

    except Exception as e:
        return {"error": f"Error en el análisis visual: {str(e)}"}

def combinar_resultados(resultados_por_pagina):
    """
    Combina los resultados de múltiples páginas.
    
    Args:
        resultados_por_pagina (list): Lista de resultados por página
        
    Returns:
        dict: Resultados combinados
    """
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
    
    # Combinar resultados
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

def extraer_metadatos(archivo_path):
    """
    Extrae metadatos de un archivo (PDF o imagen).
    
    Args:
        archivo_path (str): Ruta al archivo
        
    Returns:
        dict: Diccionario con los metadatos extraídos
    """
    try:
        # Obtener información básica del archivo
        stats = os.stat(archivo_path)
        metadatos = {
            "nombre_archivo": os.path.basename(archivo_path),
            "tamaño_bytes": stats.st_size,
            "fecha_creacion": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "fecha_modificacion": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "tipo_archivo": magic.from_file(archivo_path),
            "sospechas": []
        }

        # Detectar tipo de archivo
        es_pdf = archivo_path.lower().endswith('.pdf')
        es_imagen = archivo_path.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))

        if es_pdf:
            metadatos_pdf = extraer_metadatos_pdf(archivo_path)
            metadatos.update(metadatos_pdf)
        elif es_imagen:
            metadatos_imagen = extraer_metadatos_imagen(archivo_path)
            metadatos.update(metadatos_imagen)

        # Análisis de sospechas
        analizar_sospechas_metadatos(metadatos)

        return metadatos

    except Exception as e:
        return {"error": f"Error al extraer metadatos: {str(e)}"}

def extraer_metadatos_pdf(pdf_path):
    """
    Extrae metadatos específicos de un archivo PDF.
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            info = pdf.metadata

            metadatos = {
                "tipo_documento": "PDF",
                "numero_paginas": len(pdf.pages),
                "version_pdf": pdf.pdf_header,
                "metadatos_pdf": {
                    "autor": info.get('/Author', 'No disponible'),
                    "creador": info.get('/Creator', 'No disponible'),
                    "productor": info.get('/Producer', 'No disponible'),
                    "fecha_creacion": info.get('/CreationDate', 'No disponible'),
                    "fecha_modificacion": info.get('/ModDate', 'No disponible'),
                    "titulo": info.get('/Title', 'No disponible'),
                    "asunto": info.get('/Subject', 'No disponible'),
                    "palabras_clave": info.get('/Keywords', 'No disponible')
                }
            }
            return metadatos
    except Exception as e:
        return {"error_pdf": f"Error al extraer metadatos PDF: {str(e)}"}

def extraer_metadatos_imagen(imagen_path):
    """
    Extrae metadatos específicos de una imagen.
    """
    try:
        metadatos = {
            "tipo_documento": "Imagen",
            "metadatos_imagen": {}
        }

        # Extraer EXIF data
        try:
            exif_dict = piexif.load(imagen_path)
            if exif_dict:
                metadatos["metadatos_imagen"]["exif"] = {
                    "fecha_creacion": exif_dict.get('0th', {}).get(piexif.ImageIFD.DateTime, 'No disponible'),
                    "software": exif_dict.get('0th', {}).get(piexif.ImageIFD.Software, 'No disponible'),
                    "equipo": exif_dict.get('0th', {}).get(piexif.ImageIFD.Make, 'No disponible'),
                    "modelo_camara": exif_dict.get('0th', {}).get(piexif.ImageIFD.Model, 'No disponible')
                }
        except:
            pass

        # Extraer información adicional con exifread
        try:
            with open(imagen_path, 'rb') as f:
                tags = exifread.process_file(f)
                if tags:
                    metadatos["metadatos_imagen"]["exifread"] = {
                        "fecha_creacion": str(tags.get('EXIF DateTimeOriginal', 'No disponible')),
                        "software": str(tags.get('Software', 'No disponible')),
                        "equipo": str(tags.get('Image Make', 'No disponible')),
                        "modelo_camara": str(tags.get('Image Model', 'No disponible'))
                    }
        except:
            pass

        # Obtener información básica de la imagen
        try:
            with Image.open(imagen_path) as img:
                metadatos["metadatos_imagen"]["basico"] = {
                    "formato": img.format,
                    "modo": img.mode,
                    "tamaño": img.size,
                    "dpi": img.info.get('dpi', 'No disponible')
                }
        except:
            pass

        return metadatos
    except Exception as e:
        return {"error_imagen": f"Error al extraer metadatos de imagen: {str(e)}"}

def analizar_sospechas_metadatos(metadatos):
    """
    Analiza los metadatos en busca de posibles fraudes.
    """
    sospechas = []

    # Verificar fechas
    fecha_creacion = metadatos.get("fecha_creacion")
    fecha_modificacion = metadatos.get("fecha_modificacion")
    
    if fecha_creacion and fecha_modificacion:
        fecha_creacion = datetime.strptime(fecha_creacion, '%Y-%m-%d %H:%M:%S')
        fecha_modificacion = datetime.strptime(fecha_modificacion, '%Y-%m-%d %H:%M:%S')
        
        if fecha_modificacion < fecha_creacion:
            sospechas.append("La fecha de modificación es anterior a la fecha de creación")

    # Verificar software de creación
    if "metadatos_pdf" in metadatos:
        creador = metadatos["metadatos_pdf"]["creador"]
        if "Adobe" in creador and "Photoshop" in creador:
            sospechas.append("El documento PDF fue creado con Photoshop, lo cual es inusual")
    
    if "metadatos_imagen" in metadatos:
        if "exif" in metadatos["metadatos_imagen"]:
            software = metadatos["metadatos_imagen"]["exif"].get("software", "")
            if "Photoshop" in software:
                sospechas.append("La imagen fue editada con Photoshop")

    # Verificar si el archivo es muy reciente
    fecha_actual = datetime.now()
    if fecha_creacion:
        diferencia_dias = (fecha_actual - fecha_creacion).days
        if diferencia_dias < 1:
            sospechas.append("El documento fue creado hace menos de 24 horas")

    metadatos["sospechas"] = sospechas

def generar_pdf_report(documentos_clasificados, resultados_comparaciones):
    """
    Genera un PDF con el reporte completo del análisis usando los datos ya procesados.
    """
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    
    # Lista de elementos del PDF
    elements = []
    
    # Título
    elements.append(Paragraph("Reporte de Análisis de Documentos", title_style))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    # Resumen de documentos analizados
    elements.append(Paragraph("Resumen de Documentos Analizados", heading_style))
    resumen_docs = [
        ["Tipo de Documento", "Cantidad"],
        ["Carta Laboral", str(len(documentos_clasificados["carta laboral"]))],
        ["Colillas de Pago", str(len(documentos_clasificados["colilla de pago"]))],
        ["Extractos Bancarios", str(len(documentos_clasificados["extracto bancario"]))]
    ]
    
    t = Table(resumen_docs, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Resultados de comparaciones
    if resultados_comparaciones:
        elements.append(Paragraph("Resultados de Comparaciones", heading_style))
        
        for comparacion in resultados_comparaciones:
            resultado = comparacion["resultado"]
            elements.append(Paragraph(f"Comparación: {comparacion['tipo']}", styles["Heading3"]))
            
            # Información básica de la comparación
            info_comparacion = [
                ["Porcentaje de Coincidencia:", resultado.get("porcentaje", "N/A")],
                ["Explicación:", resultado.get("explicacion", "N/A")]
            ]
            
            t = Table(info_comparacion, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
            ]))
            elements.append(t)
            
            # Discrepancias encontradas
            if "no_coincide" in resultado:
                elements.append(Paragraph("Discrepancias Encontradas:", styles["Heading4"]))
                for campo, valores in resultado["no_coincide"].items():
                    elementos_discrepancia = [
                        ["Campo", campo.title()],
                        ["Valor 1", str(valores.get('colilla_pago', valores.get('extracto_bancario', 'N/A')))],
                        ["Valor 2", str(valores.get('carta_laboral', valores.get('colilla_pago', 'N/A')))]
                    ]
                    
                    t = Table(elementos_discrepancia, colWidths=[2*inch, 4*inch])
                    t.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ]))
                    elements.append(t)
            
            elements.append(Spacer(1, 20))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

# --- INTERFAZ STREAMLIT ---

# Configuración inicial de la página


# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .sospecha {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .coincidencia {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("🔍 Fraudubot - Análisis de Documentos")
st.markdown("---")

# Sección de carga de archivos
with st.container():
    st.subheader("📤 Carga de Documentos")
uploaded_files = st.file_uploader(
        "Sube los documentos a analizar (carta laboral, colillas, extractos)", 
    type=["pdf", "png", "jpg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Procesamiento de documentos
    documentos_clasificados = {
        "colilla de pago": [],
        "carta laboral": [],
        "extracto bancario": [],
        "otro": []
    }

    # Procesar cada documento
    for i, archivo in enumerate(uploaded_files):
        status_text.text(f"Procesando {archivo.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))

        path = os.path.join("temp", archivo.name)
        with open(path, "wb") as f:
            f.write(archivo.getbuffer())

        # Análisis de texto y visual
        texto = extract_text(path)
        tipo = clasificar_documento(texto)
        analisis_visual = analizar_documento_visual(path)
        metadatos = extraer_metadatos(path)
        
        documentos_clasificados[tipo].append({
            "nombre_archivo": archivo.name,
            "texto": texto,
            "path": path,
            "analisis_visual": analisis_visual,
            "metadatos": metadatos
        })

    # Limpiar barra de progreso
    progress_bar.empty()
    status_text.empty()

    # Mostrar resultados por tipo de documento
    for tipo, docs in documentos_clasificados.items():
        if docs:
            st.markdown(f"## 📄 {tipo.upper()}")
            
            # Crear columnas para cada documento
            cols = st.columns(len(docs))
            
            for i, (doc, col) in enumerate(zip(docs, cols)):
                with col:
                    st.markdown(f"### Documento {i+1}")
                    
                    # Información básica
                    with st.expander("📋 Información Básica", expanded=True):
                        st.write(f"**Nombre:** {doc['nombre_archivo']}")
                        
                        # Mostrar metadatos
                        if "metadatos" in doc:
                            metadatos = doc["metadatos"]
                            st.write("**Fecha de creación:**", metadatos.get("fecha_creacion", "No disponible"))
                            st.write("**Fecha de modificación:**", metadatos.get("fecha_modificacion", "No disponible"))
                    
                    # Análisis visual
                    with st.expander("🔍 Análisis Visual", expanded=True):
                        analisis = doc["analisis_visual"]
                        if "error" not in analisis:
                            # Crear métricas visuales
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Sellos", analisis["numero_sellos"])
                                st.metric("Firmas", len(analisis["firmas_detectadas"]))
                            with col2:
                                st.metric("Marcas de agua", analisis["marcas_agua"])
                                st.metric("Calidad", f"{analisis['calidad']['nitidez']:.2f}")
                            
                            # Mostrar sospechas
                            if analisis["sospechas"]:
                                st.markdown('<div class="sospecha">', unsafe_allow_html=True)
                                st.warning("⚠️ Elementos sospechosos:")
                                for sospecha in analisis["sospechas"]:
                                    st.write(f"- {sospecha}")
                                st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Texto extraído
                    with st.expander("📝 Texto Extraído"):
                        st.text_area("", doc["texto"], height=200)

    # Mostrar resumen de la carta laboral
    if documentos_clasificados["carta laboral"]:
        st.markdown("## 📄 Resumen de la Carta Laboral")
        
        # Extraer datos de la carta laboral
        carta = documentos_clasificados["carta laboral"][0]
        datos_carta = extract_with_matcher(carta["texto"])

        if "error" not in datos_carta:
            # Crear columnas para mostrar la información
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 👤 Datos Personales")
                st.markdown(f"**Nombre:** {datos_carta.get('nombre', 'No disponible')}")
                st.markdown(f"**Cédula:** {datos_carta.get('cedula', 'No disponible')}")
                st.markdown(f"**Ciudad de Origen:** {datos_carta.get('de_donde_es_la_cedula', 'No disponible')}")
            
            with col2:
                st.markdown("### 💼 Datos Laborales")
                st.markdown(f"**Cargo:** {datos_carta.get('cargo', 'No disponible')}")
                st.markdown(f"**Tipo de Contrato:** {datos_carta.get('tipo_de_contrato', 'No disponible')}")
                st.markdown(f"**Fecha Inicio:** {datos_carta.get('fecha_inicio_labor', 'No disponible')}")
                st.markdown(f"**Fecha Fin:** {datos_carta.get('fecha_fin_labor', 'No disponible')}")
            
            with col3:
                st.markdown("### 🏢 Datos de la Empresa")
                st.markdown(f"**Empresa:** {datos_carta.get('nombre_de_la_empresa', 'No disponible')}")
                st.markdown(f"**NIT:** {datos_carta.get('nit_de_la_empresa', 'No disponible')}")
                st.markdown(f"**Salario:** {formatear_valor_monetario(datos_carta.get('salario', 0))}")
                st.markdown(f"**Bonificación:** {formatear_valor_monetario(datos_carta.get('bonificacion', 0))}")

    # Comparación de documentos
    if len(documentos_clasificados["carta laboral"]) > 0 or len(documentos_clasificados["colilla de pago"]) > 0 or len(documentos_clasificados["extracto bancario"]) > 0:
        st.markdown("## 🔄 Comparación de Documentos")
        
        # Realizar todas las comparaciones posibles
        resultados_comparaciones = []
        
        # Si tenemos los tres tipos de documentos, hacer comparaciones triples
        if (documentos_clasificados["carta laboral"] and 
            documentos_clasificados["colilla de pago"] and 
            documentos_clasificados["extracto bancario"]):
            
            carta = documentos_clasificados["carta laboral"][0]
            extracto = documentos_clasificados["extracto bancario"][0]
            
            for colilla in documentos_clasificados["colilla de pago"]:
                # Comparar colilla con carta
                resultado_colilla_carta = compracion_documentos(
                    colilla["texto"],
                    carta["texto"]
                )
                
                # Comparar colilla con extracto
                resultado_colilla_extracto = compracion_documentos(
                    colilla["texto"],
                    extracto["texto"]
                )
                
                # Función auxiliar para obtener valores de forma segura
                def obtener_valor_seguro(resultado, tipo_doc, campo):
                    try:
                        if isinstance(resultado, dict):
                            if "no_coincide" in resultado:
                                if campo in resultado["no_coincide"]:
                                    if tipo_doc in resultado["no_coincide"][campo]:
                                        valor = resultado["no_coincide"][campo][tipo_doc]
                                        if valor is not None and valor != "":
                                            return valor
                        return "N/A"
                    except Exception as e:
                        print(f"Error al obtener valor para {tipo_doc} - {campo}: {str(e)}")
                        return "N/A"
                
                # Calcular porcentaje promedio
                porcentaje_colilla_carta = float(resultado_colilla_carta.get('porcentaje', '0%').strip('%'))
                porcentaje_colilla_extracto = float(resultado_colilla_extracto.get('porcentaje', '0%').strip('%'))
                porcentaje_promedio = (porcentaje_colilla_carta + porcentaje_colilla_extracto) / 2
                
                # Combinar resultados
                resultado_combinado = {
                    "tipo": "Comparación Triple",
                    "resultado": {
                        "porcentaje": f"{porcentaje_promedio:.2f}%",
                        "explicacion": f"Promedio de coincidencia entre documentos: Carta Laboral ({porcentaje_colilla_carta:.2f}%), Extracto Bancario ({porcentaje_colilla_extracto:.2f}%)",
                        "no_coincide": {
                            "nombre": {
                                "carta_laboral": obtener_valor_seguro(resultado_colilla_carta, "carta_laboral", "nombre"),
                                "colilla_pago": obtener_valor_seguro(resultado_colilla_carta, "colilla_pago", "nombre"),
                                "extracto_bancario": obtener_valor_seguro(resultado_colilla_extracto, "extracto_bancario", "nombre")
                            },
                            "empresa": {
                                "carta_laboral": obtener_valor_seguro(resultado_colilla_carta, "carta_laboral", "empresa"),
                                "colilla_pago": obtener_valor_seguro(resultado_colilla_carta, "colilla_pago", "empresa"),
                                "extracto_bancario": obtener_valor_seguro(resultado_colilla_extracto, "extracto_bancario", "empresa")
                            },
                            "salario": {
                                "carta_laboral": obtener_valor_seguro(resultado_colilla_carta, "carta_laboral", "salario"),
                                "colilla_pago": obtener_valor_seguro(resultado_colilla_carta, "colilla_pago", "salario"),
                                "extracto_bancario": obtener_valor_seguro(resultado_colilla_extracto, "extracto_bancario", "salario")
                            }
                        }
                    }
                }
                resultados_comparaciones.append(resultado_combinado)
        
        # Si solo tenemos dos tipos de documentos, hacer comparaciones dobles
        else:
            # Comparar carta laboral con colillas
            if documentos_clasificados["carta laboral"] and documentos_clasificados["colilla de pago"]:
                for colilla in documentos_clasificados["colilla de pago"]:
                    resultado = compracion_documentos(
                        colilla["texto"],
                        documentos_clasificados["carta laboral"][0]["texto"]
                    )
                    resultados_comparaciones.append({
                        "tipo": "Carta Laboral vs Colilla",
                        "resultado": resultado
                    })
            
            # Comparar carta laboral con extractos
            if documentos_clasificados["carta laboral"] and documentos_clasificados["extracto bancario"]:
                for extracto in documentos_clasificados["extracto bancario"]:
                    resultado = compracion_documentos(
                        extracto["texto"],
                        documentos_clasificados["carta laboral"][0]["texto"]
                    )
                    resultados_comparaciones.append({
                        "tipo": "Carta Laboral vs Extracto",
                        "resultado": resultado
                    })
            
            # Comparar colillas con extractos
            if documentos_clasificados["colilla de pago"] and documentos_clasificados["extracto bancario"]:
                for colilla in documentos_clasificados["colilla de pago"]:
                    for extracto in documentos_clasificados["extracto bancario"]:
                        resultado = compracion_documentos(
                            colilla["texto"],
                            extracto["texto"]
                        )
                        resultados_comparaciones.append({
                            "tipo": "Colilla vs Extracto",
                            "resultado": resultado
                        })
        
        # Mostrar resultados de las comparaciones
        if resultados_comparaciones:
            for comparacion in resultados_comparaciones:
                st.markdown(f"### 📊 {comparacion['tipo']}")
                resultado = comparacion['resultado']
                
                # Crear dos columnas para el layout
                col_izq, col_der = st.columns(2)
                
                with col_izq:
                    # Mostrar porcentaje y explicaciones
                    st.markdown("#### 📈 Resumen de Coincidencias")
                    st.metric(
                        "Porcentaje Promedio",
                        resultado["porcentaje"],
                        delta=None
                    )
                    
                    st.markdown("#### 📝 Explicación Detallada")
                    st.markdown("**Análisis de Coincidencias:**")
                    st.markdown("""
                    - Se compararon los documentos para verificar la consistencia de la información
                    - Se analizaron los siguientes campos: nombre, empresa y salario
                    - Se calculó el porcentaje de coincidencia basado en la similitud de los datos
                    """)
                    
                    st.markdown("**Detalle de Coincidencias:**")
                    if "explicacion" in resultado:
                        st.markdown(resultado["explicacion"])
                    
                    st.markdown("**Resultado del Análisis:**")
                    if "explicacion" in resultado:
                        st.markdown(resultado["explicacion"])
                
                with col_der:
                    # Mostrar análisis detallado en una tabla
                    st.markdown("#### 🔍 Análisis Detallado")
                    if "no_coincide" in resultado:
                        for campo, valores in resultado["no_coincide"].items():
                            st.markdown(f"**{campo.title()}:**")
                            # Crear tabla con documentos como columnas
                            headers = []
                            row_data = []
                            
                            # Agregar columnas para cada tipo de documento presente
                            if "extracto_bancario" in valores:
                                headers.append("Extracto Bancario")
                                row_data.append(valores['extracto_bancario'])
                            if "colilla_pago" in valores:
                                headers.append("Colilla de Pago")
                                row_data.append(valores['colilla_pago'])
                            if "carta_laboral" in valores:
                                headers.append("Carta Laboral")
                                row_data.append(valores['carta_laboral'])
                            
                            if headers:
                                df = pd.DataFrame([row_data], columns=headers)
                                st.table(df)
                
                st.markdown("---")

    # Generar reporte PDF
    if resultados_comparaciones:
        pdf_bytes = generar_pdf_report(documentos_clasificados, resultados_comparaciones)
        
        # Botón para descargar el reporte
        st.download_button(
            label="📥 Descargar Reporte PDF",
            data=pdf_bytes,
            file_name="reporte_analisis.pdf",
            mime="application/pdf"
        )

# services/metadatos.py
"""
Módulo para la extracción y análisis de metadatos de archivos.
"""
import os
from datetime import datetime
import magic
import PyPDF2
import piexif
import exifread
from PIL import Image

# TODO: Separar lógica de PDF e imagen si crece mucho

def extraer_metadatos(archivo_path):
    try:
        stats = os.stat(archivo_path)
        metadatos = {
            "nombre_archivo": os.path.basename(archivo_path),
            "tamaño_bytes": stats.st_size,
            "fecha_creacion": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "fecha_modificacion": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "tipo_archivo": magic.from_file(archivo_path),
            "sospechas": []
        }
        es_pdf = archivo_path.lower().endswith('.pdf')
        es_imagen = archivo_path.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))
        if es_pdf:
            metadatos_pdf = extraer_metadatos_pdf(archivo_path)
            metadatos.update(metadatos_pdf)
        elif es_imagen:
            metadatos_imagen = extraer_metadatos_imagen(archivo_path)
            metadatos.update(metadatos_imagen)
        analizar_sospechas_metadatos(metadatos)
        return metadatos
    except Exception as e:
        return {"error": f"Error al extraer metadatos: {str(e)}"}

def extraer_metadatos_pdf(pdf_path):
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
    try:
        metadatos = {
            "tipo_documento": "Imagen",
            "metadatos_imagen": {}
        }
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
    sospechas = []
    fecha_creacion = metadatos.get("fecha_creacion")
    fecha_modificacion = metadatos.get("fecha_modificacion")
    if fecha_creacion and fecha_modificacion:
        fecha_creacion = datetime.strptime(fecha_creacion, '%Y-%m-%d %H:%M:%S')
        fecha_modificacion = datetime.strptime(fecha_modificacion, '%Y-%m-%d %H:%M:%S')
        if fecha_modificacion < fecha_creacion:
            sospechas.append("La fecha de modificación es anterior a la fecha de creación")
    if "metadatos_pdf" in metadatos:
        creador = metadatos["metadatos_pdf"]["creador"]
        if "Adobe" in creador and "Photoshop" in creador:
            sospechas.append("El documento PDF fue creado con Photoshop, lo cual es inusual")
    if "metadatos_imagen" in metadatos:
        if "exif" in metadatos["metadatos_imagen"]:
            software = metadatos["metadatos_imagen"]["exif"].get("software", "")
            if "Photoshop" in software:
                sospechas.append("La imagen fue editada con Photoshop")
    fecha_actual = datetime.now()
    if fecha_creacion:
        diferencia_dias = (fecha_actual - fecha_creacion).days
        if diferencia_dias < 1:
            sospechas.append("El documento fue creado hace menos de 24 horas")
    metadatos["sospechas"] = sospechas 
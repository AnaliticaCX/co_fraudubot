import pdf2image
from PIL import Image
import pytesseract
from docx import Document


def extraccion_texto(file_path):
    """
    Extrae texto de un archivo PDF o imagen utilizando OCR.

    Parámetros:
    file_path (str): Ruta del archivo (PDF o imagen).

    Retorna:
    str: Texto extraído del archivo.
    """
    text = ""

    if file_path.endswith(".pdf"):
        # Convertir PDF a imágenes y extraer texto
        images = pdf2image.convert_from_path(file_path)
        for image in images:
            text += pytesseract.image_to_string(image, lang="eng")
    elif file_path.endswith(".docx"):
        #
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

    else:
        # Extraer texto directamente de la imagen
        text = pytesseract.image_to_string(Image.open(file_path), lang="eng")

    return text

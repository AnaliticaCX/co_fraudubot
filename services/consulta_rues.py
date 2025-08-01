import re
import time
from selenium import webdriver
from libreria.utilidades import limpiar_nit

def extraer_nombre(texto):
    match = re.search(r"\n([A-ZÑ&\s\.\-]{3,})\nIdentificación", texto)
    if match:
        return match.group(1).strip()
    alt_match = re.search(r"Volver atras\n+([A-ZÑ&\s\.\-]{3,})\nIdentificación", texto)
    if alt_match:
        return alt_match.group(1).strip()
    before_id = texto.split("Identificación")[0].split("\n")
    for line in reversed(before_id):
        if line.strip().isupper() and len(line.strip()) > 5:
            return line.strip()
    return "N/A"

def extraer_dato(label, texto):
    pattern = rf"{label}\s+([^\n]+)"
    match = re.search(pattern, texto, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def consultar_empresa_por_nit(nit, driver_path=None, headless=True, timeout=7):
    """
    Consulta los datos de una empresa en RUES por NIT y devuelve un diccionario con los datos extraídos.
    Requiere Selenium y ChromeDriver instalado.
    """
    nit_limpio = limpiar_nit(nit)
    url = f"https://ruesfront.rues.org.co/buscar/RM/{nit_limpio}"
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    if driver_path:
        driver = webdriver.Chrome(driver_path, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    datos = {}
    try:
        driver.get(url)
        time.sleep(timeout)
        texto = driver.execute_script("return document.body.innerText")
        datos = {
            "nombre": extraer_nombre(texto),
            "identificacion": extraer_dato("Identificación", texto),
            "estado": extraer_dato("Estado", texto),
            "matricula": extraer_dato("Número de Matrícula", texto),
            "camara": extraer_dato("Cámara de Comercio", texto),
            "categoria": extraer_dato("Categoria", texto)
        }
    except Exception as e:
        datos = {"error": str(e)}
    finally:
        driver.quit()
    return datos

# Ejemplo de uso (descomentar para probar manualmente)
# resultado = consultar_empresa_por_nit('900.469.873-1')
# print(resultado) 
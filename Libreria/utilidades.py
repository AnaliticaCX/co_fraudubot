from word2number import w2n
from pdf2image import convert_from_path
import unicodedata
from PIL import Image


def extract_name(text): 
    """Extrae el nombre de una persona del texto."""
    stop_words = {"la señora", "el señor", "señor", "señora", "la", "el", "El", "La"}
    text = " ".join(text.split()[3:])  # Eliminar las primeras tres palabras
    doc = nlp(text)
    
    for ent in doc.ents:
        if ent.label_ == "PER":
            cleaned_name = " ".join(word for word in ent.text.split() if word.lower() not in stop_words)
            return cleaned_name.strip()

    # Patrón para nombre con contexto como "el señor [NOMBRE]"
    context_pattern = r"(?i)(?:el\s+señor|la\s+señora|señor(?:a)?|que)\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ]*(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ]*)+)"
    match = re.search(context_pattern, text)
    if match:
        candidate_name = match.group(1).strip()
        cleaned_name = " ".join(word for word in candidate_name.split() if word.lower() not in stop_words)
        return cleaned_name.title()
    
    return None


def extract_cc(text): 
    """Extrae la cédula de ciudadanía del texto."""
    text_normalized = remove_accents(text)
    cc_match = re.search(
        r"(?:CC|cedula(?: de ciudadania)?|cedula)(?:\s*(?:numero|num|No\.?|No:)\s*[:\s]*)?([\d\.\s]+)",
        text_normalized, re.IGNORECASE
    )
    if cc_match:
        return re.sub(r"[^\d]", "", cc_match.group(1))
    return None


def extract_salario(text): 
    """Extrae información del salario del texto, soportando tanto números como palabras."""
    pattern = r"(?:salario|remuneración)\s*[:de]*\s*([\d.,]+|[a-zA-Z\s]+(?:\s*pesos?|\s*millon|\s*doscientos?|\s*mil)*)|[\$€]\s?[\d.,]+"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        salary_str = match.group(1) if match.group(1) else match.group(0)
        if any(char.isalpha() for char in salary_str):
            try:
                salary_value = w2n.word_to_num(salary_str.replace("UN", "one").replace("MILLON", "million"))
                return salary_value
            except ValueError:
                return salary_str
        else:
            salary_str = re.sub(r"[^\d]", "", salary_str)
            try:
                return int(salary_str)
            except ValueError:
                return salary_str
    return None


def extract_tiempo_laborado(text): 
    """Extrae las fechas de inicio y fin del periodo laboral desde el texto."""
    year_pattern = r"\b(\d{4})\b"
    years = re.findall(year_pattern, text)
    current_date = datetime.now()
    is_present = any(term in text.lower() for term in ["hasta hoy", "hoy", "actualidad", "presente", "hasta la fecha"])
    
    from_date, to_date = None, None
    desde_match = re.search(r"desde\s+(\d{4})", text.lower())
    if desde_match:
        from_year = desde_match.group(1)
        from_date = f"{from_year}-01-01"

    if is_present:
        to_date = current_date.strftime('%Y-%m-%d')
    elif len(years) > 1:
        to_date = f"{years[1]}-12-31"

    if not desde_match and years:
        from_date = f"{years[0]}-01-01"

    return from_date, to_date


def remove_accents(text): #DESAPARECE
    """Elimina los acentos de un texto."""
    return ''.join(
        (c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    )
import google.generativeai as genai
from typing import Dict, Any, List
import json

class GeminiService:
    def __init__(self, api_key: str):
        """
        Inicializa el servicio de Gemini.
        
        Args:
            api_key (str): API key de Google Gemini
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
        
    def clasificar_documento(self, texto: str) -> str:
        """
        Clasifica el tipo de documento usando Gemini.
        """
        prompt = f"""
        Analiza el siguiente texto y determina si es una colilla de pago, carta laboral o extracto bancario.
        Responde SOLO con una de estas opciones: "colilla de pago", "carta laboral", "extracto bancario" o "otro".
        
        Texto:
        {texto}
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip().lower()
    
    def extraer_datos_carta_laboral(self, texto: str) -> Dict[str, str]:
        """
        Extrae datos relevantes de una carta laboral usando Gemini.
        """
        prompt = f"""
        Analiza el siguiente texto de una carta laboral y extrae la siguiente información en formato JSON:
        - nombre: Nombre completo de la persona
        - cedula: Número de cédula o documento de identidad
        - cargo: Cargo o posición
        - salario: Salario o remuneración
        - fecha_inicio: Fecha de inicio de labores
        - empresa: Nombre de la empresa
        - nit: Número de identificación tributaria de la empresa

        Responde SOLO con el JSON, sin texto adicional.

        Texto:
        {texto}
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {}
    
    def comparar_documentos(self, texto1: str, texto2: str) -> Dict[str, Any]:
        """
        Compara dos documentos usando Gemini.
        """
        prompt = f"""
        Compara los siguientes dos documentos y proporciona un análisis detallado en formato JSON con la siguiente estructura:
        {{
            "porcentaje": "XX%",
            "explicacion": "Explicación detallada de la comparación",
            "diferencias": {{
                "campo1": {{
                    "valor1": "valor en documento 1",
                    "valor2": "valor en documento 2"
                }},
                ...
            }}
        }}

        Documento 1 (Carta Laboral):
        {texto1}

        Documento 2 (Colilla de Pago):
        {texto2}

        Responde SOLO con el JSON, sin texto adicional.
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {
                "porcentaje": "0%",
                "explicacion": "Error al procesar la comparación",
                "diferencias": {}
            }

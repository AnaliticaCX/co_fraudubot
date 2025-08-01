import google.generativeai as genai
from typing import Dict, Any, List
import json
import time
from .gemini_logger import gemini_logger, log_gemini_operation

class GeminiService:
    def __init__(self, api_key: str):
        """
        Inicializa el servicio de Gemini.
        
        Args:
            api_key (str): API key de Google Gemini
        """
        genai.configure(api_key=api_key)
        # Use the model from environment configuration
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-002')
        self.model = genai.GenerativeModel(model_name)
        
    @log_gemini_operation("clasificar_documento")
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
        
        start_time = time.time()
        response = self.model.generate_content(prompt)
        execution_time = time.time() - start_time
        
        # Log manual para capturar información adicional
        gemini_logger.log_request(
            operation="clasificar_documento",
            prompt=prompt,
            response=response.text,
            execution_time=execution_time,
            metadata={"texto_original": texto[:200] + "..." if len(texto) > 200 else texto}
        )
        
        return response.text.strip().lower()
    
    @log_gemini_operation("extraer_datos_carta_laboral")
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
        
        start_time = time.time()
        response = self.model.generate_content(prompt)
        execution_time = time.time() - start_time
        
        try:
            result = json.loads(response.text)
            error_message = None
        except Exception as e:
            result = {}
            error_message = f"Error parsing JSON: {str(e)}"
        
        # Log manual para capturar información adicional
        gemini_logger.log_request(
            operation="extraer_datos_carta_laboral",
            prompt=prompt,
            response=response.text,
            execution_time=execution_time,
            error_message=error_message,
            metadata={
                "texto_original": texto[:200] + "..." if len(texto) > 200 else texto,
                "json_parsing_success": error_message is None
            }
        )
        
        return result
    
    @log_gemini_operation("comparar_documentos")
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
        
        start_time = time.time()
        response = self.model.generate_content(prompt)
        execution_time = time.time() - start_time
        
        try:
            result = json.loads(response.text)
            error_message = None
        except Exception as e:
            result = {
                "porcentaje": "0%",
                "explicacion": "Error al procesar la comparación",
                "diferencias": {}
            }
            error_message = f"Error parsing JSON: {str(e)}"
        
        # Log manual para capturar información adicional
        gemini_logger.log_request(
            operation="comparar_documentos",
            prompt=prompt,
            response=response.text,
            execution_time=execution_time,
            error_message=error_message,
            metadata={
                "texto1_length": len(texto1),
                "texto2_length": len(texto2),
                "json_parsing_success": error_message is None
            }
        )
        
        return result

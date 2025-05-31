import openai
from typing import Dict, Any, List
import json

API_KEY = "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"

class ChatGPTHandler:
    def __init__(self, api_key: str):
        """
        Inicializa el manejador de ChatGPT.
        """
        self.client = openai.OpenAI(api_key=api_key)
    
    def clasificar_documento(self, texto: str) -> str:
        """
        Clasifica el tipo de documento usando ChatGPT.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en clasificar documentos."},
                    {"role": "user", "content": f"""Analiza el siguiente texto y determina si es una colilla de pago, carta laboral o extracto bancario.
                    Responde SOLO con una de estas opciones: "colilla de pago", "carta laboral", "extracto bancario" o "otro".
                    
                    Texto:
                    {texto}"""}
                ],
                temperature=0.3
            )
            
            respuesta = response.choices[0].message.content.strip().lower()
            
            # Validar la respuesta
            for tipo in ["colilla de pago", "carta laboral", "extracto bancario", "otro"]:
                if tipo in respuesta:
                    return tipo
            
            return "otro"
            
        except Exception as e:
            print(f"Error en clasificación: {str(e)}")
            return "otro"
    
    def extraer_datos_carta_laboral(self, texto: str) -> Dict[str, str]:
        """
        Extrae datos relevantes de una carta laboral usando ChatGPT.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en extraer información de cartas laborales."},
                    {"role": "user", "content": f"""Analiza el siguiente texto de una carta laboral y extrae la siguiente información en formato JSON:
                    {{
                        "nombre": "Nombre completo de la persona",
                        "cedula": "Número de cédula o documento de identidad",
                        "de_donde_es_la_cedula": "Ciudad de origen de donde salió el documento",
                        "tipo_de_contrato": "Tipo de contrato",
                        "cargo": "Cargo o posición",
                        "nombre_de_la_empresa": "Nombre de la empresa",
                        "nit_de_la_empresa": "Número de identificación tributaria de la empresa",
                        "salario": "Salario o remuneración (solo números)",
                        "bonificacion": "Bonificación (solo números)",
                        "fecha_inicio_labor": "Fecha de inicio de labores (dd/mm/yyyy)",
                        "fecha_fin_labor": "Fecha de fin de labores (dd/mm/yyyy) o 'actualidad'",
                        "fecha_de_expedicion_carta": "Fecha de expedición de la carta (dd/mm/yyyy)"
                    }}

                    Texto:
                    {texto}"""}
                ],
                temperature=0.3
            )
            
            respuesta = response.choices[0].message.content.strip()
            
            # Intentar extraer el JSON
            try:
                inicio_json = respuesta.find('{')
                fin_json = respuesta.rfind('}') + 1
                if inicio_json >= 0 and fin_json > inicio_json:
                    json_str = respuesta[inicio_json:fin_json]
                    return json.loads(json_str)
            except:
                pass
            
            return {}
            
        except Exception as e:
            print(f"Error en extracción de datos: {str(e)}")
            return {}
    
    def comparar_documentos(self, texto1: str, texto2: str) -> Dict[str, Any]:
        """
        Compara dos documentos usando ChatGPT.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en comparar documentos."},
                    {"role": "user", "content": f"""Compara los siguientes dos documentos y proporciona un análisis detallado en formato JSON:
                    {{
                        "porcentaje": "XX%",
                        "explicacion": "Explicación detallada de la comparación",
                        "no_coincide": {{
                            "nombre": {{ "colilla_pago": "...", "carta_laboral": "..." }},
                            "empresa": {{ "colilla_pago": "...", "carta_laboral": "..." }},
                            "salario": {{ "colilla_pago": "...", "carta_laboral": "..." }}
                        }}
                    }}

                    Documento 1 (Carta Laboral):
                    {texto1}

                    Documento 2 (Colilla de Pago):
                    {texto2}"""}
                ],
                temperature=0.3
            )
            
            respuesta = response.choices[0].message.content.strip()
            
            # Intentar extraer el JSON
            try:
                inicio_json = respuesta.find('{')
                fin_json = respuesta.rfind('}') + 1
                if inicio_json >= 0 and fin_json > inicio_json:
                    json_str = respuesta[inicio_json:fin_json]
                    return json.loads(json_str)
            except:
                pass
            
            return {
                "porcentaje": "0%",
                "explicacion": "Error al procesar la comparación",
                "no_coincide": {}
            }
            
        except Exception as e:
            print(f"Error en comparación: {str(e)}")
            return {
                "porcentaje": "0%",
                "explicacion": f"Error en comparación: {str(e)}",
                "no_coincide": {}
            }

def chat_with_gpt(prompt):
    client = openai.OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


#chat_with_gpt('cual es el numero de la empresa Celerix en la ciudad de itagui')
import openai
from google.generativeai import GenerativeModel
import google.generativeai as genai
from typing import Dict, Any
import json
import re

class ModeloIA:
    def __init__(self, tipo_modelo: str, api_key: str):
        self.tipo_modelo = tipo_modelo.lower()

        if self.tipo_modelo == 'openai':
            import openai
            openai.api_key = api_key
            self.client = openai
        elif self.tipo_modelo == 'gemini':
            genai.configure(api_key=api_key)
            self.modelo = GenerativeModel('gemini-1.5-flash-002')
        else:
            raise ValueError("Tipo de modelo no soportado. Use 'openai' o 'gemini'")

    def limpiar_respuesta_json(self, texto: str) -> str:
        """
        Elimina bloques de código tipo ```json ... ``` y deja solo el JSON puro.
        """
        texto = re.sub(r"```(?:json)?", "", texto)
        texto = texto.replace("```", "")
        return texto.strip()

    def clasificar_documento(self, texto: str) -> str:
        prompt = f"""
        Analiza el siguiente texto y determina si es una colilla de pago, carta laboral o extracto bancario.
        Responde SOLO con una de estas opciones: "colilla de pago", "carta laboral", "extracto bancario" o "otro".
        SOLO RESPONDE EL TIPO DE DOCUMENTO, NADA MAS

        Texto:
        {texto}
        """

        if self.tipo_modelo == 'openai':
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en análisis de documentos."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip().lower()
        else:
            response = self.modelo.generate_content(prompt)
            return response.text.strip().lower()

    def extraer_datos_carta_laboral(self, texto: str) -> Dict[str, str]:
        prompt = """
        Analiza el siguiente texto de una carta laboral y extrae la siguiente información en formato JSON:
        - nombre
        - cedula
        - de_donde_es_la_cedula
        - tipo_de_contrato
        - cargo
        - nombre_de_la_empresa
        - nit_de_la_empresa
        - salario
        - bonificacion
        - fecha_inicio_labor
        - fecha_fin_labor
        - fecha_de_expedicion_carta

        Quiero que las fechas queden en formato dd/mm/yyyy.
        Entrega el resultado en formato JSON.
        """

        try:
            if self.tipo_modelo == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente especializado en extracción de datos de documentos."},
                        {"role": "user", "content": prompt + "\n\n" + texto}
                    ]
                )
                contenido = response.choices[0].message.content
            else:
                response = self.modelo.generate_content(prompt + "\n\n" + texto)
                contenido = response.text

            contenido_limpio = self.limpiar_respuesta_json(contenido)

            try:
                return json.loads(contenido_limpio)
            except Exception as e:
                print("⚠️ Error al cargar JSON:", e)
                print("Contenido limpio:", contenido_limpio)
                return {}

        except Exception as e:
            print(f"⚠️ Error total al procesar: {e}")
            return {
                "nombre": "Jefferson Estrada",
                "cedula": "123456789",
                "de_donde_es_la_cedula": "Bogotá",
                "tipo_de_contrato": "Indefinido",
                "cargo": "Analista de Datos",
                "nombre_de_la_empresa": "TechSoluciones S.A.S.",
                "nit_de_la_empresa": "900123456",
                "salario": "4500000",
                "bonificacion": "500000",
                "fecha_inicio_labor": "10/01/2020",
                "fecha_fin_labor": "actualidad",
                "fecha_de_expedicion_carta": "01/05/2025"
            }

    def extraer_datos_extracto_bancario(self, texto: str) -> Dict[str, str]:
        prompt = """
        Analiza el siguiente texto de un extracto bancario y extrae la siguiente información en formato JSON:
        - nombre_titular
        - numero_cuenta
        - promedio_ingresos
        - tipo_ingreso (por ejemplo: 'nómina', 'abono domi', etc.)

        Entrega el resultado en formato JSON.
        """

        try:
            if self.tipo_modelo == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente especializado en extracción de datos de extractos bancarios."},
                        {"role": "user", "content": prompt + "\n\n" + texto}
                    ]
                )
                contenido = response.choices[0].message.content
            else:
                response = self.modelo.generate_content(prompt + "\n\n" + texto)
                contenido = response.text

            contenido_limpio = self.limpiar_respuesta_json(contenido)
            return json.loads(contenido_limpio)
        except Exception as e:
            print("⚠️ Error al extraer datos de extracto bancario:", e)
            return {}

    def extraer_datos_colilla_pago(self, texto: str) -> Dict[str, str]:
        prompt = """
        Analiza el siguiente texto de una colilla de pago y extrae la siguiente información en formato JSON:
        - nombre_empleado
        - cargo
        - salario_base
        - bonificaciones
        - deducciones
        - salario (esto tiene que ser el valor total que le pagaron)
        - periodo_pago
        - empresa


        Entrega el resultado en formato JSON.
        """

        try:
            if self.tipo_modelo == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente especializado en extracción de datos de colillas de pago."},
                        {"role": "user", "content": prompt + "\n\n" + texto}
                    ]
                )
                contenido = response.choices[0].message.content
            else:
                response = self.modelo.generate_content(prompt + "\n\n" + texto)
                contenido = response.text

            contenido_limpio = self.limpiar_respuesta_json(contenido)
            return json.loads(contenido_limpio)
        except Exception as e:
            print("⚠️ Error al extraer datos de colilla de pago:", e)
            return {}

    def comparar_documentos(self, texto1: str, texto2: str) -> Dict[str, Any]:
        prompt = f"""
        Compara los siguientes dos documentos y proporciona un análisis detallado en formato JSON:

        {{
            "porcentaje": "XX%",
            "explicacion": "Explicación detallada de la comparación",
            "no_coincide": {{
                "nombre": {{ "colilla_pago": "...", "carta_laboral": "..." }},
                "empresa": {{ "colilla_pago": "...", "carta_laboral": "..." }},
                "salario": {{ "colilla_pago": "...", "carta_laboral": "..." }}
            }}
        }}

        Documento 1 (Carta Laboral) el valor sel salario en formado X.000.000 sin signo peso:
        {texto2}

        Documento 2 (Colilla de Pago) el valor sel salario en formado X.000.000 sin signo peso:
        {texto1}

        Responde SOLO con el JSON, sin texto adicional.
        """

        try:
            if self.tipo_modelo == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente especializado en comparación de documentos."},
                        {"role": "user", "content": prompt}
                    ]
                )
                contenido = response.choices[0].message.content
            else:
                response = self.modelo.generate_content(prompt)
                contenido = response.text

            contenido_limpio = self.limpiar_respuesta_json(contenido)
            return json.loads(contenido_limpio)

        except Exception as e:
            print("⚠️ Error en comparación:", e)
            return {
                "porcentaje": "0%",
                "explicacion": "Error al procesar la comparación",
                "no_coincide": {}
            }

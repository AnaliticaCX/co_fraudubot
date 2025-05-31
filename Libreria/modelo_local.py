from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Dict, Any, List
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModeloDeepSeek:
    def __init__(self):
        """
        Inicializa el modelo DeepSeek.
        """
        logger.info("Iniciando carga del modelo...")
        
        # Usar un modelo más confiable
        self.modelo_path = "distilgpt2"  # Modelo muy ligero
        
        try:
            logger.info("Cargando tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.modelo_path,
                trust_remote_code=True
            )
            
            logger.info("Configurando dispositivo...")
            if torch.backends.mps.is_available():
                device = torch.device("mps")
                logger.info("Usando dispositivo MPS")
            else:
                device = torch.device("cpu")
                logger.info("Usando dispositivo CPU")
            
            logger.info("Cargando modelo...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.modelo_path,
                torch_dtype=torch.float32,
                device_map=device,
                trust_remote_code=True,
                use_safetensors=True,
                low_cpu_mem_usage=True
            )
            
            logger.info("Moviendo modelo al dispositivo...")
            self.model = self.model.to(device)
            self.model.eval()
            logger.info("Modelo cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {str(e)}")
            raise
    
    def _generar_respuesta(self, prompt: str) -> str:
        """
        Genera una respuesta usando el modelo DeepSeek.
        """
        try:
            logger.info("Generando respuesta...")
            
            # Prompt más directo
            formatted_prompt = f"""Tarea: {prompt}
            Responde de manera concisa y estructurada.
            """
            
            logger.info("Tokenizando prompt...")
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024  # Aumentar para documentos más largos
            )
            
            if torch.backends.mps.is_available():
                inputs = {k: v.to("mps") for k, v in inputs.items()}
            
            logger.info("Generando texto...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,  # Aumentar para respuestas más largas
                    num_return_sequences=1,
                    temperature=0.7,  # Aumentar para más creatividad
                    do_sample=True,  # Activar muestreo
                    top_p=0.95,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            logger.info("Decodificando respuesta...")
            respuesta = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extraer solo la parte de la respuesta después de "Tarea:"
            if "Tarea:" in respuesta:
                respuesta = respuesta.split("Tarea:")[-1].strip()
            
            logger.info(f"Respuesta generada: {respuesta}")
            return respuesta
            
        except Exception as e:
            logger.error(f"Error en generación: {str(e)}")
            return ""
    
    def clasificar_documento(self, texto: str) -> str:
        """
        Clasifica el tipo de documento usando DeepSeek.
        """
        logger.info("Clasificando documento...")
        
        # Prompt más directo y simple
        prompt = f"""Clasifica este documento. Responde SOLO con una de estas opciones: "colilla de pago", "carta laboral", "extracto bancario" o "otro".

        Documento:
        {texto}"""
        
        respuesta = self._generar_respuesta(prompt)
        logger.info(f"Respuesta de clasificación: {respuesta}")
        
        # Limpiar y validar la respuesta
        respuesta = respuesta.lower().strip()
        
        # Primero buscar coincidencias exactas en el texto original
        if "CERTIFICADO LABORAL" in texto.upper():
            logger.info("Documento clasificado como: carta laboral (por coincidencia exacta)")
            return "carta laboral"
        elif "COLILLA DE PAGO" in texto.upper():
            logger.info("Documento clasificado como: colilla de pago (por coincidencia exacta)")
            return "colilla de pago"
        elif "EXTRACTO BANCARIO" in texto.upper():
            logger.info("Documento clasificado como: extracto bancario (por coincidencia exacta)")
            return "extracto bancario"
        
        # Si no hay coincidencia exacta, buscar en la respuesta del modelo
        for tipo in ["colilla de pago", "carta laboral", "extracto bancario", "otro"]:
            if tipo in respuesta:
                logger.info(f"Documento clasificado como: {tipo}")
                return tipo
        
        # Si aún no hay coincidencia, buscar palabras clave
        if "carta" in respuesta or "laboral" in respuesta or "certificado" in respuesta:
            logger.info("Documento clasificado como: carta laboral (por palabras clave)")
            return "carta laboral"
        elif "colilla" in respuesta or "pago" in respuesta or "nómina" in respuesta:
            logger.info("Documento clasificado como: colilla de pago (por palabras clave)")
            return "colilla de pago"
        elif "extracto" in respuesta or "bancario" in respuesta or "cuenta" in respuesta:
            logger.info("Documento clasificado como: extracto bancario (por palabras clave)")
            return "extracto bancario"
        
        logger.info("Documento clasificado como: otro")
        return "otro"
    
    def extraer_datos_carta_laboral(self, texto: str) -> Dict[str, str]:
        """
        Extrae datos relevantes de una carta laboral usando DeepSeek.
        """
        prompt = f"""Analiza el siguiente texto de una carta laboral y extrae la siguiente información en formato JSON:
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
        {texto}"""
        
        respuesta = self._generar_respuesta(prompt)
        try:
            # Intentar extraer el JSON de la respuesta
            inicio_json = respuesta.find('{')
            fin_json = respuesta.rfind('}') + 1
            if inicio_json >= 0 and fin_json > inicio_json:
                json_str = respuesta[inicio_json:fin_json]
                return json.loads(json_str)
            return {}
        except:
            return {}
    
    def comparar_documentos(self, texto1: str, texto2: str, tipo_doc1: str = None, tipo_doc2: str = None) -> Dict[str, Any]:
        """
        Compara dos documentos usando DeepSeek.
        
        Args:
            texto1 (str): Texto del primer documento
            texto2 (str): Texto del segundo documento
            tipo_doc1 (str): Tipo del primer documento (carta laboral, colilla de pago, extracto bancario)
            tipo_doc2 (str): Tipo del segundo documento (carta laboral, colilla de pago, extracto bancario)
        """
        logger.info("Comparando documentos...")
        
        # Prompt más directo y estructurado
        prompt = f"""Analiza y compara estos dos documentos:

        Documento 1 ({tipo_doc1 or 'Primer documento'}):
        {texto1}

        Documento 2 ({tipo_doc2 or 'Segundo documento'}):
        {texto2}

        Responde con un JSON que contenga:
        1. El porcentaje de coincidencia
        2. Una explicación de la comparación
        3. Los campos que no coinciden (nombre, empresa, salario, fechas, montos)
        4. Un análisis de las discrepancias encontradas
        """
        
        respuesta = self._generar_respuesta(prompt)
        logger.info(f"Respuesta de comparación: {respuesta}")
        
        try:
            # Intentar extraer el JSON de la respuesta
            inicio_json = respuesta.find('{')
            fin_json = respuesta.rfind('}') + 1
            if inicio_json >= 0 and fin_json > inicio_json:
                json_str = respuesta[inicio_json:fin_json]
                return json.loads(json_str)
            
            # Si no se encuentra JSON, crear uno con la información disponible
            return {
                "porcentaje": "0%",
                "explicacion": "No se pudo procesar la comparación",
                "no_coincide": {
                    "nombre": {"doc1": "", "doc2": ""},
                    "empresa": {"doc1": "", "doc2": ""},
                    "salario": {"doc1": "", "doc2": ""},
                    "fechas": {"doc1": "", "doc2": ""},
                    "montos": {"doc1": "", "doc2": ""}
                },
                "analisis_discrepancias": "No se pudo realizar el análisis de discrepancias"
            }
        except Exception as e:
            logger.error(f"Error al procesar la comparación: {str(e)}")
            return {
                "porcentaje": "0%",
                "explicacion": f"Error al procesar la comparación: {str(e)}",
                "no_coincide": {
                    "nombre": {"doc1": "", "doc2": ""},
                    "empresa": {"doc1": "", "doc2": ""},
                    "salario": {"doc1": "", "doc2": ""},
                    "fechas": {"doc1": "", "doc2": ""},
                    "montos": {"doc1": "", "doc2": ""}
                },
                "analisis_discrepancias": f"Error en el análisis: {str(e)}"
            }

import openai
from config.config import API_KEY
import json

class GPTService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=API_KEY)

    def chat_with_gpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def extract_with_matcher(self, text):
        peticion = """
        Saca los datos principales de la persona de la siguiente carta laboral:
        ... (resto del prompt)
        """
        prompt = peticion + text
        response = self.chat_with_gpt(prompt)
        try:
            return json.loads(response)
        except:
            return {"error": "Respuesta no válida"}

    def compracion_documentos(self, texto_colilla, texto_carta):
        # ... (código de comparación)

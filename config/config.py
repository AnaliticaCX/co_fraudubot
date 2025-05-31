import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configuración de la aplicación
APP_TITLE = "FrauduBot - Detector de Fraudes"
APP_ICON = "🔍"
APP_LAYOUT = "wide"

# Configuración de PDF
PDF_FONT_SIZE = 12
PDF_MARGIN = 50

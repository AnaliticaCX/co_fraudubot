import PyPDF2

# Ruta del archivo PDF
archivo_pdf = '/Users/jeffersonestradajaramillo/Library/CloudStorage/OneDrive-CX/Escritorio/Jefferson/Pruebas Python/cambios-proyecto-ia/co_fraudubot/Datos/extractos NAILY MARIANA RUBIO (1).pdf'

# Abrir el archivo en modo binario
with open(archivo_pdf, 'rb') as f:
    lector = PyPDF2.PdfReader(f)
    
    # Obtener los metadatos
    metadatos = lector.metadata

# Imprimir los metadatos
for clave, valor in metadatos.items():
    print(f'{clave}: {valor}')

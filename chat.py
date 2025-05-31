import openai
import time


client = openai.OpenAI(api_key="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")

# 1. Crear un archivo

# 1. Subir archivo PDF
file = client.files.create(
    file=open("/Users/jeffersonestradajaramillo/Library/CloudStorage/OneDrive-CX/Escritorio/Jefferson/Pruebas Python/cambios-proyecto-ia/co_fraudubot/Datos/extractos NAILY MARIANA RUBIO.pdf", "rb"),
    purpose="assistants"
)

# 2. Crear el assistant con file_search
assistant = client.beta.assistants.create(
    name="Lector de Documentos",
    instructions="Resume el contenido del documento cargado.",
    model="gpt-4-turbo",
    tools=[{"type": "file_search"}]
)

# 3. Crear un nuevo thread
thread = client.beta.threads.create()

# ✅ 4. Crear mensaje del usuario y asociar archivo al thread
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Resume el contenido del archivo adjunto.",
    attachments=[
        {
            "file_id": file.id,
            "tools": [{"type": "file_search"}]
        }
    ]
)


# ✅ 5. Ejecutar el assistant (ya no uses additional_file_ids)
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    tool_choice="auto"
)

# 6. Ejecutar el assistant, asociando el archivo aquí
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    tool_choice="auto"
)

# 7. Esperar a que la ejecución termine
while True:
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    if run_status.status == "completed":
        break
    time.sleep(1)

# 8. Recuperar los mensajes del hilo y mostrar respuesta del assistant
messages = client.beta.threads.messages.list(thread_id=thread.id)

print("\n📄 Respuesta del assistant:\n")
for message in messages.data:
    if message.role == "assistant":
        print(message.content[0].text.value)
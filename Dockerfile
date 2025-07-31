# Usa imagen base oficial de Python 3.9
FROM python:3.9-slim

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema necesarias para Chromium + Selenium + libmagic
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    ca-certificates \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxi6 \
    libgl1 \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Establece variable de entorno para que Selenium encuentre Chromium
ENV CHROME_BIN=/usr/bin/chromium

# Actualiza pip, wheel y setuptools para evitar errores con paquetes grandes
RUN pip install --upgrade pip setuptools wheel

# Copia el archivo de requerimientos antes del código para aprovechar la cache de Docker
COPY requirements-docker.txt .

# Install uv
RUN pip install uv

# Install dependencies with uv (modo sistema)
RUN uv pip install --system -r requirements-docker.txt

# Copia el código fuente
COPY . /app
WORKDIR /app

# Comando por defecto (modifica si usas Streamlit u otro)
CMD ["streamlit", "run", "main.py"]





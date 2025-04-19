FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y \
    curl wget gnupg unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm-dev libgtk-3-0 xdg-utils libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores para Playwright
RUN python -m playwright install --with-deps chromium

# Copiar el resto del código fuente
COPY . .

# Exponer puerto de Streamlit
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

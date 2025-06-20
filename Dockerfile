# Dockerfile para FastAPI backend (desarrollo)
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema (si necesitas)
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Actualiza pip e instala dependencias Python
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# No copies el código fuente, el volumen lo montará

# Expón el puerto de FastAPI
EXPOSE 8000

# Comando por defecto: ejecuta el backend con Uvicorn
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

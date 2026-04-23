# ─────────────────────────────────────────────────────────────
#  Dockerfile  –  ServiGuía API
#  Imagen ligera de Python 3.11 con FastAPI + uvicorn
# ─────────────────────────────────────────────────────────────

# Imagen base: Python 3.11 versión mínima (sin extras innecesarios)
FROM python:3.11-slim

# Carpeta de trabajo DENTRO del contenedor (no toca tu PC)
WORKDIR /app

# Primero copiamos solo requirements para aprovechar caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Puerto que expone la API (solo disponible cuando corres el contenedor)
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

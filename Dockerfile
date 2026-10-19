# ==========================================
# Etapa 1: Compilación de la aplicación en Go
# ==========================================
FROM golang:1.22-alpine AS go-builder

WORKDIR /app

# Copiamos todo el proyecto para asegurar que Go encuentre su archivo go.mod / código
COPY . .

# Nos movemos a la carpeta TRANSFORMACION y compilamos el binario
WORKDIR /app/TRANSFORMACION
RUN go mod init transformacion 2>/dev/null || true
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/bin/transformacion-go transformacion.go


# ==========================================
# Etapa 2: Imagen Final (Python + Binario de Go)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias del sistema necesarias si tuvieras librerías pesadas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos los requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el binario compilado de Go desde la primera etapa
COPY --from=go-builder /app/bin/transformacion-go /app/bin/transformacion-go

# Copiamos todo el código fuente del proyecto (INGESTA, LTM, TRANSFORMACION, .env, main.py)
COPY . /app

# Variable para evitar buffering en los logs de Python
ENV PYTHONUNBUFFERED=1

# Comando por defecto que ejecuta tu orquestador principal en la raíz
CMD ["python", "main.py"]
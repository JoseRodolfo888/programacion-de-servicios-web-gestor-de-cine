# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias de sistema (para el driver de MySQL)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos comunes desde la raíz del proyecto
COPY requirements.txt .
COPY shared ./shared
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de ESTE servicio
COPY ./services/products/ .

# Crear directorio de uploads
RUN mkdir -p uploads/products

# Expone el puerto de ESTE servicio
EXPOSE 8003

# Comando para iniciar ESTE servicio con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
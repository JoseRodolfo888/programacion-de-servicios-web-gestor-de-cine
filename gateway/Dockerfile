# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos comunes desde la raíz del proyecto 
COPY requirements.txt .
COPY shared ./shared
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de ESTE servicio
COPY ./gateway/ .

# Crear directorio de uploads
RUN mkdir -p static uploads

# Expone el puerto de ESTE servicio
EXPOSE 8000

# Comando para iniciar ESTE servicio con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
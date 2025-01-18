FROM python:3.9-slim

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación y el archivo de requerimientos
COPY requirements.txt .
COPY pipeline.py .

# Copiar la carpeta "videos" al contenedor
COPY videos /app/videos

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt


# Exponer el puerto en el contenedor
EXPOSE 8000

# Ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "pipeline:app", "--host", "0.0.0.0", "--port", "8000"]





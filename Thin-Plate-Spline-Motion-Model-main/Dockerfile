# Usar la imagen existente que ya tiene las dependencias del modelo
FROM my_thin_plate_final_image_with_files

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /workspace

# Copiar el archivo del microservicio en el contenedor
COPY thin_plate_api.py /workspace/

# Instalar FastAPI y Uvicorn si no están ya instalados en la imagen preexistente
RUN pip install fastapi uvicorn

# Exponer el puerto 8000 para la API
EXPOSE 8000

# Comando para ejecutar el servicio con Uvicorn
CMD ["uvicorn", "thin_plate_api:app", "--host", "0.0.0.0", "--port", "8000"]

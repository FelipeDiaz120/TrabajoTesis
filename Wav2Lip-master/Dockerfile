# Usa la imagen existente como base
FROM my_wav2lip_final_image_with_files

# Establece el directorio de trabajo
WORKDIR /workspace

# Copia el archivo FastAPI al contenedor
COPY wav2lip_api.py /workspace/

# Instala las dependencias necesarias para FastAPI
RUN pip install fastapi uvicorn python-multipart

# Expone el puerto donde correrá FastAPI
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "wav2lip_api:app", "--host", "0.0.0.0", "--port", "8000"]


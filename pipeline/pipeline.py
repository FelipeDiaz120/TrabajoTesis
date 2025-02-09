from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
import requests
import os
import shutil

app = FastAPI()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
THIN_PLATE_URL = "http://thinplate-service:8000/thin_plate/"
WAV2LIP_URL = "http://wav2lip-service:8000/wav2lip/"


# Función para validar el tipo de archivo de imagen
def validate_image(file: UploadFile):
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        return False
    return True


# Función para validar el tipo de archivo de audio
def validate_audio(file: UploadFile):
    allowed_extensions = ["wav", "mp3"]
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        return False
    return True


@app.post("/pipeline/")
async def run_pipeline(
        video_name: str = Form(...),  # Nombre del video recibido en form-data
        audio: UploadFile = File(...),  # Archivo de audio recibido
        image: UploadFile = File(...),  # Archivo de imagen recibido
):
    # Verificar si el video existe
    video_path = os.path.join(VIDEO_DIR, video_name)
    if not os.path.exists(video_path):
        return {
            "error": f"El archivo de video '{video_name}' no existe en la carpeta de videos. Por favor, verifica el nombre e inténtalo de nuevo."}

    # Validar tipo de imagen
    if not validate_image(image):
        return {"error": "El archivo de imagen no es válido. Por favor, sube un archivo PNG, JPG o JPEG."}

    # Validar tipo de audio
    if not validate_audio(audio):
        return {"error": "El archivo de audio no es válido. Por favor, sube un archivo WAV o MP3."}

    # Crear carpeta temporal
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Guardar archivos
    shutil.copy(video_path, os.path.join(TEMP_DIR, video_name))  # Copiar video a carpeta temporal
    video_path = os.path.join(TEMP_DIR, video_name)

    # Guardar imagen
    image_path = os.path.join(TEMP_DIR, image.filename)
    with open(image_path, "wb") as f:
        f.write(await image.read())

    # Guardar audio
    audio_path = os.path.join(TEMP_DIR, audio.filename)
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Paso 1: Llamar a Thin Plate
    with open(video_path, "rb") as dv, open(image_path, "rb") as si:
        thin_plate_response = requests.post(
            THIN_PLATE_URL,
            files={"driving_video": dv, "source_image": si},
        )
    if thin_plate_response.status_code != 200:
        raise HTTPException(
            status_code=500, detail=f"Error en Thin Plate: {thin_plate_response.text}"
        )

    # Guardar salida de Thin Plate
    thin_plate_output_path = os.path.join(TEMP_DIR, "thin_plate_output.mp4")
    with open(thin_plate_output_path, "wb") as f:
        f.write(thin_plate_response.content)

    # Paso 2: Llamar a Wav2Lip
    with open(thin_plate_output_path, "rb") as tp_out, open(audio_path, "rb") as af:
        wav2lip_response = requests.post(
            WAV2LIP_URL,
            files={"face_video": tp_out, "audio_file": af},
        )
    if wav2lip_response.status_code != 200:
        raise HTTPException(
            status_code=500, detail=f"Error en Wav2Lip: {wav2lip_response.text}"
        )

    # Guardar salida final
    final_output_path = os.path.join(TEMP_DIR, "final_output.mp4")
    with open(final_output_path, "wb") as f:
        f.write(wav2lip_response.content)

    # Verificar que el archivo final se haya creado correctamente
    if not os.path.exists(final_output_path):
        raise HTTPException(status_code=500, detail="El archivo final no existe.")

    # Devolver el archivo como respuesta
    response = FileResponse(final_output_path, media_type="video/mp4", filename="final_output.mp4")

    # Limpiar carpeta temporal después de la respuesta
    #shutil.rmtree(TEMP_DIR)

    return response













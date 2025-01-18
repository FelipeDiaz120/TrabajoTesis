from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import shutil

app = FastAPI()

# Paths
BASE_DIR = "/workspace/"
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
output_video = "output_final.mp4"

@app.post("/wav2lip/")
async def run_wav2lip(
    face_video: UploadFile = File(...),
    audio_file: UploadFile = File(...),
):
    # Limpiar y crear directorio temporal (sin afectar la carpeta temp existente)
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Guardar archivos en UPLOAD_DIR
    face_video_path = os.path.join(UPLOAD_DIR, face_video.filename)
    audio_file_path = os.path.join(UPLOAD_DIR, audio_file.filename)
    output_path = os.path.join(BASE_DIR, output_video)  # Ruta completa para la salida

    with open(face_video_path, "wb") as f:
        f.write(await face_video.read())
    with open(audio_file_path, "wb") as f:
        f.write(await audio_file.read())

    # Debug: Confirmar rutas
    print(f"Face video saved at: {face_video_path}")
    print(f"Audio file saved at: {audio_file_path}")

    try:
        # Ejecutar el comando de Wav2Lip
        subprocess.run(
            [
                "python", os.path.join(BASE_DIR, "inference.py"),
                "--checkpoint_path", os.path.join(BASE_DIR, "checkpoints", "wav2lip.pth"),
                "--face", face_video_path,
                "--audio", audio_file_path,
                "--outfile", output_path,  # Usamos la ruta completa de salida
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        # Eliminar directorio temporal en caso de error
        shutil.rmtree(UPLOAD_DIR)
        raise HTTPException(status_code=500, detail=f"Error al ejecutar Wav2Lip: {str(e)}")

    # Limpieza del directorio temporal
    shutil.rmtree(UPLOAD_DIR)

    # Devolver el video generado como respuesta
    return FileResponse(output_path, media_type="video/mp4", headers={"Content-Disposition": f"attachment; filename={output_video}"})


@app.get("/")
def read_root():
    return {"message": "Wav2Lip Microservice is running"}






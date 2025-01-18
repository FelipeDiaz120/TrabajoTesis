from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import shutil

app = FastAPI()

# Paths
BASE_DIR = "/workspace/"
TEMP_DIR = os.path.join(BASE_DIR, "temp")

@app.post("/thin_plate/")
async def run_thin_plate(
    driving_video: UploadFile = File(...),
    source_image: UploadFile = File(...),
):
    # Limpiar y crear directorio temporal
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Guardar archivos en TEMP_DIR
    driving_path = os.path.join(TEMP_DIR, driving_video.filename)
    source_path = os.path.join(TEMP_DIR, source_image.filename)
    output_path = os.path.join(TEMP_DIR, "output_fom.mp4")

    with open(driving_path, "wb") as f:
        f.write(await driving_video.read())
    with open(source_path, "wb") as f:
        f.write(await source_image.read())

    # Debug: Confirmar rutas
    print(f"Driving video saved at: {driving_path}")
    print(f"Source image saved at: {source_path}")

    try:
        # Ejecutar el modelo Thin Plate
        subprocess.run(
            [
                "python", os.path.join(BASE_DIR, "demo.py"),
                "--config", os.path.join(BASE_DIR, "config", "vox-256.yaml"),
                "--cpu", "--driving_video", driving_path,
                "--source_image", source_path,
                "--checkpoint", os.path.join(BASE_DIR, "checkpoints", "vox.pth.tar"),
                "--result_video", output_path,
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        # Eliminar directorio temporal en caso de error
        shutil.rmtree(TEMP_DIR)
        raise HTTPException(status_code=500, detail=f"Error al ejecutar Thin Plate: {str(e)}")

    # Verificar si el archivo de salida se generó correctamente
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="video/mp4", filename="output_fom.mp4")
    else:
        # Manejar el caso donde el archivo de salida no se generó
        shutil.rmtree(TEMP_DIR)
        raise HTTPException(status_code=500, detail="El archivo de salida no se generó correctamente.")

    # Limpieza del directorio temporal (opcional)
    shutil.rmtree(TEMP_DIR)



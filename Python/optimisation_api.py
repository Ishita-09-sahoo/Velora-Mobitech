from fastapi import FastAPI, UploadFile, File
import shutil
import os
from main import run_optimisation

app = FastAPI()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/optimise")
async def optimise(file: UploadFile = File(...)):

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_optimisation(path)

    return result
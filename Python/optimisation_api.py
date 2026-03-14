from fastapi import FastAPI, UploadFile, File
import shutil
import os
import uuid
from main import run_optimisation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "/tmp/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def health():
    return {"status": "API running"}

@app.post("/optimise")
async def optimise(file: UploadFile = File(...)):

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_optimisation(path)
    os.remove(path)

    return result
from fastapi import APIRouter, UploadFile, File
import os

from backend.extraction.pdf_extractor import extract_text_from_pdf
from backend.extraction.medical_extraction import extract_medical_data

from backend.database.crud import save_medical_report

router = APIRouter()

UPLOAD_DIR = "data"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)

    structured_data = extract_medical_data(extracted_text)

    save_result = save_medical_report(
        medical_report=structured_data,
        raw_text=extracted_text
    )

    return {
        "structured_data": structured_data.model_dump(),
        "database_result": save_result
    }

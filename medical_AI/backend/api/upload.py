from fastapi import APIRouter, UploadFile, File
import os

from ..extraction.pdf_extractor import PDFExtractor
from ..extraction.medical_extraction import extract_medical_data

from ..database.crud import save_medical_report, save_analysis
from ..analysis.medical_analyzer import analyze_medical_report

router = APIRouter()

import sys

print("=" * 60)
print("FASTAPI PYTHON:", sys.executable)
print("=" * 60)

UPLOAD_DIR = "data"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # extracted_text = extract_text_from_pdf(file_path)
    extractor = PDFExtractor()
    text = extractor.extract(file_path)
    
    structured_data = extract_medical_data(text)

    save_result = save_medical_report(
        medical_report=structured_data,
        raw_text= text
    )

    # If saved successfully, run AI analysis and persist it
    analysis= None
    analysis_result = None
    if save_result.get("status") == "success":
        analysis = analyze_medical_report(structured_data)
        analysis_result = save_analysis(
            report_id=save_result["report_id"],
            analysis=analysis
        )
    
    return {
        "structured_data": structured_data.model_dump(),
        "database_result": save_result,
        "analysis": analysis,
        "analysis_database_result": analysis_result
    }
from fastapi import FastAPI
import uvicorn

app= FastAPI()

from backend.api.upload import router as upload_router

@app.get("/")
def home():
    return {"message": "Medical AI backend running"}

app.include_router(upload_router)

if __name__== "__main__":
    uvicorn.run(app, host="http://127.0.0.1:8000", port=8000)

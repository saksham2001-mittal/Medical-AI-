from fastapi import FastAPI
import uvicorn

from backend.database.connections import Base, engine
from backend.api.upload import router as upload_router

# Import models so SQLAlchemy knows about them
from backend.database import models

Base.metadata.create_all(bind=engine)

app= FastAPI()

@app.get("/")
def home():
    return {"message": "Medical AI backend running"}

app.include_router(upload_router)

if __name__== "__main__":
    uvicorn.run(app, host="http://127.0.0.1", port=8000)

from dotenv import load_dotenv
load_dotenv()


import os

print("GROQ_API_KEY at startup:", os.getenv("GROQ_API_KEY"))
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil

from app.services.ingestion import process_pdf
from app.models import IngestionResponse, ChatResponse
from app.services.rag import get_chat_response


app = FastAPI(title=" RAG Project")

# Ensure a temporary directory exists for uploads
os.makedirs("temp", exist_ok=True)

@app.post("/ingest", response_model=IngestionResponse)
async def ingest_pdf(
    file: UploadFile = File(...), 
    strategy: str = Form("recursive") # default to recursive
):
    # Validate file type
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and Text files are supported.")

    # Save file temporarily
    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Call our service
        num_chunks = process_pdf(temp_path, strategy)
        return IngestionResponse(
            message="Successfully ingested",
            filename=file.filename,
            chunks_count=num_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up: delete temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
@app.get("/chat", response_model=ChatResponse)
async def chat(query: str, session_id: str = "default_user"):
    try:
        answer, sources = get_chat_response(query, session_id)
        return ChatResponse(answer=answer, sources=list(set(sources)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
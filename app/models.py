from pydantic import BaseModel, EmailStr
from typing import List, Optional

# This defines what info we need to book an interview
class BookingRequest(BaseModel):
    name: str
    email: EmailStr
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM

# This defines the response after uploading a PDF
class IngestionResponse(BaseModel):
    message: str
    filename: str
    chunks_count: int

# This defines the chat response
class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
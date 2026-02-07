# Banking RAG & Interview Booking System

A modular, production-ready backend built with FastAPI that leverages Large Language Models (LLM) to answer questions from a Banking Guide and automate interview bookings.


## Overview
This project implements a Retrieval-Augmented Generation (RAG) pipeline to provide accurate information based on a provided Banking PDF. It features a "Booking Specialist" that uses LLM Tool Calling to capture user details and store them in a database.

## Tech Stack
- **Framework:** FastAPI (Python)
- **LLM:** Groq (Llama 3.3 70B)
- **Vector Database:** Qdrant (Docker)
- **Memory/Cache:** Redis (Docker)
- **Database:** SQLite (Booking Persistence)
- **Orchestration:** Docker Compose
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)

## Key Features
- **Document Ingestion:** Supports `.pdf` and `.txt` files with selectable chunking strategies (Fixed vs. Recursive).
- **Contextual Retrieval:** Custom RAG logic (no `RetrievalQAChain`) for precise context injection.
- **Multi-turn Memory:** Powered by Redis to maintain conversation state across queries.
- **Automated Bookings:** Intelligent Tool Calling to detect and process interview requests.
- **Industry Standards:** Fully type-annotated code, Pydantic V2 models, and modular service architecture.

## Prerequisites
- Docker & Docker Desktop
- Groq API Key

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/ayu-collab/banking_rag_system>
   cd palm-mind-task

  
2. **Configure Environment Variables: Create a .env file in the root directory:**
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    QDRANT_URL=http://qdrant:6333
    REDIS_HOST=redis

3. **Run with Docker:**
    ```bash
    docker-compose up --build
The API will be available at http://localhost:8000

---

## API Usage

### 1. Ingest a Document

**POST** `/ingest`

Upload the `Banking.pdf` to populate the vector database found in the data/ folder.

**Parameters**:

- `file`: (Upload PDF)
- `strategy`: `"recursive"` or `"fixed"`

![Ingestion Demo](./images/ingest_demo.png)

### 2. Chat & Book

**GET** `/chat`

Ask questions about the PDF or request an interview booking.

**Parameters**:

- `query`: `"What is a savings account?"` or `"I want to book an interview"`
- `session_id`: `"unique_user_id"` (to maintain memory)

![Normal Chat](./images/chat.png)

![Booking Chat](./images/chat_booking.png)

![Booking Chat](./images/chat_booking1.png)

**Example Request**:

## Project Structure

```plaintext
├── app/
│   ├── main.py            # FastAPI Entry Point & Routes
│   ├── models.py          # Pydantic Schemas (Data Contracts)
│   └── services/
│       ├── ingestion.py   # PDF Processing & Vector Upload
│       ├── rag.py         # RAG Logic & Tool Calling
│       └── booking.py     # SQLite Database Operations
├── data/                  # Sample Documents
├── .dockerignore          # Docker ignore rules
├── Dockerfile             # App Containerization
├── docker-compose.yml     # Multi-container Setup
└── requirements.txt       # Project Dependencies

```

---

## Design Decisions

- **Recursive Splitting**: 
  Chosen to preserve semantic meaning in banking documents by splitting at paragraph and sentence boundaries.

- **Tool Calling**:  
  Used instead of Regex to ensure the LLM intelligently understands and handles natural language booking requests.

- **Redis Memory**:  
  Decoupled conversation memory allows the API to remain stateless, scalable, and production-ready.

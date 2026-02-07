import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize the embedding model (This turns text into vectors)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_pdf(file_path: str, strategy: str):
    # 1. Load the file (PDF or TXT)
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    docs = loader.load()

    # 2. Choose chunking strategy
    if strategy == "recursive":
        # Professional way: respects paragraphs and sentences
        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    else:
        # Basic way: splits strictly by character count
        splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=50)

    chunks = splitter.split_documents(docs)

    # 3. Upload to Qdrant
    url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    
    vector_store = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=url,
        collection_name="banking_docs",
    )

    return len(chunks)

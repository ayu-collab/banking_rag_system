import os
import json
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from app.services.booking import save_booking, init_db
from app.models import BookingRequest

# Load API key for Groq from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set.")

# Initialize DB on startup
init_db()

# Embeddings + Vector Store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="banking_docs",
    url=os.getenv("QDRANT_URL", "http://localhost:6333")
)

# THE BOOKING TOOL 
@tool
def book_interview(name: str, email: str, date: str, time: str) -> str:
    """
    Call this tool when the user wants to book an interview or appointment.
    'date' should be in YYYY-MM-DD format and 'time' in HH:MM format.
    """
    try:
        booking_data = BookingRequest(name=name, email=email, date=date, time=time)
        save_booking(booking_data)
        return f"SUCCESS: Interview booked for {name} on {date} at {time}."
    except Exception as e:
        return f"ERROR: Could not book interview. {str(e)}"

# LLM with tools
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)
llm_with_tools = llm.bind_tools([book_interview])

def get_chat_response(user_query: str, session_id: str):
    # Retrieve conversation history from Redis
    history = RedisChatMessageHistory(
        session_id=session_id,
        url=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/0"
    )

    # Search Qdrant for relevant banking context
    docs = vector_store.similarity_search(user_query, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    # Build the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful Banking Assistant. 
        
        STRICT RULES:
        1. Use the provided context to answer banking questions.
        2. If the user wants to book an interview, you MUST ask for their Name, Email, Date, and Time.
        3. DO NOT call the 'book_interview' tool until the user has provided ALL 4 pieces of information.
        4. DO NOT make up or guess any information.
        
        Context: {context}"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    # Execute LLM with tools
    chain = prompt | llm_with_tools
    response = chain.invoke({
        "input": user_query,
        "chat_history": history.messages,
        "context": context
    })

    # Handle tool calls
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "book_interview":
                result = book_interview.invoke(tool_call["args"])
                # Add the tool result back to history
                history.add_user_message(user_query)
                history.add_ai_message(f"I have successfully booked your appointment. {result}")
                return f"I have successfully booked your appointment. {result}", ["SQLite Database"]

    # Default: save normal conversation
    history.add_user_message(user_query)
    history.add_ai_message(response.content)
    return response.content, [doc.metadata.get("source", "Banking.pdf") for doc in docs]

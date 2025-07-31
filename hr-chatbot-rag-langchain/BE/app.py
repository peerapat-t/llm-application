import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict

# Import necessary LangChain and vector store packages
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Zilliz
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# --- 1. Load Environment Variables and Initialize Constants ---
load_dotenv()
ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")
API_KEY = os.environ.get("API_KEY")

# --- 2. Initialize Models and Vector Store ---
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
LLM = ChatOpenAI(temperature=0.7, openai_api_key=API_KEY, model_name="gpt-3.5-turbo")
vector_store = Zilliz(
    embedding_function=EMBEDDING_MODEL,
    connection_args={"uri": ZILLIZ_URI, "token": ZILLIZ_TOKEN},
    collection_name='hr_policy',
    text_field="page_content"  # <-- ADD THIS LINE
)
RETRIEVER = vector_store.as_retriever()

# --- 3. Session Management ---
session_memory_store: Dict[str, ConversationBufferMemory] = {}

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Retrieves or creates a memory buffer for a given session."""
    if session_id not in session_memory_store:
        session_memory_store[session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
    return session_memory_store[session_id]

# --- 4. FastAPI Application Setup ---
app = FastAPI(
    title="HR Policy Chatbot API",
    description="An API for interacting with the HR policy chatbot with session management.",
    version="1.0.0"
)

# Define allowed origins for CORS
origins = ["*"]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests and responses
class ChatRequest(BaseModel):
    question: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# --- 5. API Endpoints ---
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint to check if the server is running."""
    return {"message": "Server is running."}

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """Handles a chat request from a user."""

    # Get the memory for the current session
    memory = get_or_create_memory(request.session_id)

    # Create a new conversational chain for this request, using the session's memory.
    session_chat_chain = ConversationalRetrievalChain.from_llm(
        llm=LLM,
        retriever=RETRIEVER,
        memory=memory
    )
    
    # Invoke the chain with the user's question to get the result
    result = session_chat_chain.invoke({"question": request.question})
    
    # Return the answer and session ID
    return ChatResponse(answer=result["answer"], session_id=request.session_id)

# --- 6. Main Execution Block ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
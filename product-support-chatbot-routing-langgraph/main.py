# main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from graph import get_graph
from config import OPENAI_API_KEY

# Create the FastAPI app
app_fastapi = FastAPI()

# --- CORS Middleware Setup ---
# This allows your Streamlit frontend (running on a different port)
# to communicate with your FastAPI backend.
origins = [
    "http://localhost",
    "http://localhost:8501",  # Default Streamlit port
    # Add any other origins you might use for development/production
]

app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Get the compiled LangGraph app
langgraph_app = get_graph()

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str

@app_fastapi.get("/")
async def read_root():
    """A simple hello world endpoint to check if the server is running."""
    return {"message": "Hello from the DOGBRAIN666 API!"}

@app_fastapi.post("/invoke", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to interact with the chatbot.
    Receives a message and a thread_id, invokes the graph, and returns the response.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_API_KEY_HERE":
        return ChatResponse(response="API Key not configured on the server.")

    config = {"configurable": {"thread_id": request.thread_id}}
    
    messages = [HumanMessage(content=request.message)]
    
    result = langgraph_app.invoke({"messages": messages}, config)
    
    ai_response = result["messages"][-1].content
    
    return ChatResponse(response=ai_response)

@app_fastapi.get("/history/{thread_id}")
async def get_history(thread_id: str):
    """
    Endpoint to retrieve the conversation history for a given thread_id.
    """
    config = {"configurable": {"thread_id": thread_id}}
    try:
        history = langgraph_app.get_state(config)
        return history.values.get('messages', [])
    except Exception:
        return []


if __name__ == "__main__":
    uvicorn.run(app_fastapi, host="0.0.0.0", port=8000)
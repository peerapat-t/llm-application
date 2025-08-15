from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from graph import app

# Initialize the FastAPI app
api = FastAPI(
    title="Multi-Agent Chatbot API",
    description="An API for interacting with a multi-agent chatbot built with LangGraph.",
    version="1.0.0",
)
origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API ---
class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    query: str
    # In a real app, you might include a session_id to manage conversation history
    # session_id: str 

# --- API Endpoint ---
@api.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to stream responses from the LangGraph agent.
    """
    async def event_stream():
        # The input to the graph is a dictionary with a 'messages' key
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        # Stream events from the graph
        async for event in app.astream(inputs, {"recursion_limit": 15}):
            for node_name, node_output in event.items():
                # We are interested in the final messages from the nodes
                if "messages" in node_output:
                    # The 'messages' key contains a list; we get the last message
                    last_message = node_output["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        # Yield the content of the AI's response
                        yield f"data: {last_message.content}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# To run this API, save it as main.py and run:
# uvicorn main:api --reload

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)

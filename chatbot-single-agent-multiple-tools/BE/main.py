import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub

from agent_simple import get_company_info
from agent_rag import answer_leave_question, answer_salary_question, answer_resignation_question
from agent_search import search_floor_item
from agent_certificate import generate_certificate_of_employment

load_dotenv()
OPENAI_API_KEY = os.environ.get("API_KEY")

app = FastAPI(
    title="HR Policy Chatbot Backend",
    description="API Server for the LangChain HR Chatbot Agent",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tools = [
    get_company_info,
    answer_leave_question,
    answer_salary_question,
    answer_resignation_question,
    search_floor_item,
    generate_certificate_of_employment
]

prompt_template = hub.pull("hwchase17/react-chat")

llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o",
    openai_api_key=OPENAI_API_KEY
)

agent = create_react_agent(llm, tools, prompt_template)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

class ChatRequest(BaseModel):
    prompt: str
    chat_history: List[Dict[str, Any]] = Field(default_factory=list, description="A list of previous messages")

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"status": "HR Chatbot backend is running"}

@app.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    try:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        for message in request.chat_history:
            if message.get("role") == "user":
                memory.chat_memory.add_user_message(message.get("content"))
            elif message.get("role") == "assistant":
                memory.chat_memory.add_ai_message(message.get("content"))
        
        response = agent_executor.invoke({
            "input": request.prompt,
            "chat_history": memory.chat_memory.messages
        })

        return ChatResponse(response=response.get('output', 'ขออภัยค่ะ พบข้อผิดพลาดบางอย่าง'))
    except Exception as e:
        return ChatResponse(response=f"An error occurred on the backend: {e}")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
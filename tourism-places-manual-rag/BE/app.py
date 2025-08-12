import warnings
warnings.filterwarnings("ignore")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict
from functions import classify_question, bangkok_question_with_rag, \
                      chiangmai_question_with_rag, phuket_question_with_rag, get_top_k

app = FastAPI(
    title="Thailand Tourism API",
    description="An API to get travel recommendations for various locations in Thailand.",
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

class Question(BaseModel):
    user_question: str
    
@app.get("/", response_model=Dict[str, str])
async def greet():
    return {"message": "Welcome to the Thailand Tourism API!"}

@app.post("/ask", response_model=Dict[str, str])
async def handle_question(question: Question):

    user_question = question.user_question
    router = classify_question(user_question)

    answer = ""

    if router == 'Bangkok location':
        knowledge = get_top_k(user_question, 'bangkok_tourism_places')
        answer = bangkok_question_with_rag(user_question, knowledge)

    elif router == 'Chiang Mai location':
        knowledge = get_top_k(user_question, 'chiangmai_tourism_places')
        answer = chiangmai_question_with_rag(user_question, knowledge)

    elif router == 'Phuket location':
        knowledge = get_top_k(user_question, 'phuket_tourism_places')
        answer = phuket_question_with_rag(user_question, knowledge)

    else:
        answer = 'ฉันไม่แน่ใจคำถาม กรุณาถามใหม่อีกครั้ง'

    if not answer:
         raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    return {"answer": answer + knowledge}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# main.py

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from translator import translate_with_langchain

load_dotenv()

app = FastAPI(
    title="Translation API",
    description="An API to translate text using LangChain and OpenAI.",
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

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Receives text and a target language, returns the translation.
    """
    # Now os.getenv will be able to find the variable loaded from .env
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key is not configured on the server."
        )

    translation_result = translate_with_langchain(
        text=request.text,
        target_language=request.target_language,
        api_key=api_key
    )

    if translation_result:
        return TranslationResponse(translated_text=translation_result.strip())
    else:
        raise HTTPException(
            status_code=503,
            detail="Failed to get a response from the OpenAI translation service."
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
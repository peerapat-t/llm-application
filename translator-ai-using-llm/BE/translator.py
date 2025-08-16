# translator.py

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

def get_translation_chain(api_key: str) -> Runnable:
    """
    Creates and returns a LangChain chain for translation.
    """
    # 1. Define the Prompt Template
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert multilingual translator.
        First, automatically detect the language of the text below.
        Then, translate it to {target_language}.
        Provide only the translated text as the output, with no additional explanations or preamble.
        Ensure the translation is accurate and natural-sounding.

        Text to translate:
        ---
        {text}
        """
    )

    # 2. Instantiate the Chat Model
    # LangChain's ChatOpenAI has built-in retry logic (max_retries)
    chat_model = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=api_key,
        temperature=0.1,
        max_retries=3  # Robust retry mechanism
    )

    # 3. Define the Output Parser
    output_parser = StrOutputParser()

    # 4. Create the Chain using LangChain Expression Language (LCEL)
    chain = prompt_template | chat_model | output_parser
    
    return chain

def translate_with_langchain(text: str, target_language: str, api_key: str) -> str | None:
    """
    Performs translation using a LangChain chain.
    Returns the translated text on success, None on failure.
    """
    try:
        # Get the compiled chain
        translation_chain = get_translation_chain(api_key)
        
        # Invoke the chain with the required inputs
        result = translation_chain.invoke({
            "text": text,
            "target_language": target_language
        })
        return result
    except Exception as e:
        # Catch potential API errors (e.g., authentication, rate limits)
        print(f"An error occurred while using LangChain: {e}")
        return None
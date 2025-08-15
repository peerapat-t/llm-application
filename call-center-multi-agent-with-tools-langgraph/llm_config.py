import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# --- Environment Setup ---
# Load environment variables from a .env file
load_dotenv()

# Check if the API key is available. 
# This is a good practice to avoid errors.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# --- LLM Initialization ---
# Initialize the language model with a temperature of 0 for deterministic outputs.
try:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    print("ChatOpenAI model initialized successfully!")
    
    # You can now use the 'llm' object to make calls, for example:
    # response = llm.invoke("Hello, how are you?")
    # print(response.content)

except Exception as e:
    print(f"An error occurred during model initialization: {e}")
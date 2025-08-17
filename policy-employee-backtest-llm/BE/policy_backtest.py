# policy_backtest.py

import os
import sys # Import sys to exit gracefully
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# --- 1. Load Environment Variables & Define Data Structures ---
load_dotenv()
OPENAI_API_KEY = os.environ.get("API_KEY")

class PolicyResponse(BaseModel):
    """Data structure for the LLM's response."""
    sentiment: Literal["agree", "disagree", "neutral"] = Field(description="The employee's sentiment towards the policy (agree, disagree, or neutral).")
    comment: str = Field(description="A brief, in-character comment from the employee explaining their sentiment.")

# --- 2. Load Employee Data from CSV File ---
try:
    employee_df = pd.read_csv("employee.csv")
except FileNotFoundError:
    print("Error: 'employee.csv' not found. Please ensure the file is in the correct directory.")
    sys.exit(1) # Exit the script if the data can't be loaded

def run_policy_simulation(policy_text: str) -> pd.DataFrame:
    """
    Runs a simulation for a given policy text against a predefined list of employees.
    
    Args:
        policy_text: The full text of the policy to simulate.
        
    Returns:
        A pandas DataFrame containing employee data and their simulated feedback.
    """
    if not policy_text or not policy_text.strip():
        raise ValueError("Policy text cannot be empty.")
    
    # --- LangChain Implementation ---
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
    parser = JsonOutputParser(pydantic_object=PolicyResponse)
    
    prompt_template = """
    You are simulating an employee's reaction to a new company policy.
    Based on the employee profile provided, generate a realistic response.

    **Company Policy:** "{policy_text}"

    **Employee Profile:**
    - Position: {position}
    - Level: {level}
    - Age: {age}
    - MBTI Type: {mbti}

    **Your Task:**
    Based *only* on the persona described above, provide your feedback on the new policy.

    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["policy_text", "position", "level", "age", "mbti"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser

    # --- Loop and Process ---
    results = []
    print(" Simulating feedback for custom policy ".center(80, "="))
    
    for _, row in employee_df.iterrows():
        print(f"--- Processing Employee: {row['employee_id']} ---")
        try:
            response = chain.invoke({
                "policy_text": policy_text,
                "position": row['position'],
                "level": row['level'],
                "age": row['age'],
                "mbti": row['mbti_type']
            })
            results.append(response)
        except Exception as e:
            print(f"An error occurred for employee {row['employee_id']}: {e}")
            results.append({"sentiment": "error", "comment": str(e)})

    # --- Final Output ---
    results_df = pd.DataFrame(results)
    final_df = pd.concat([employee_df, results_df], axis=1)
    
    print("✅ Simulation complete.")
    return final_df
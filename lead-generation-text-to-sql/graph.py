import os
import io
import logging
from typing import TypedDict, List, Tuple, Optional

import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langgraph.graph import StateGraph, END
from start_db_engine import setup_database

# --- SETUP ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Make sure it's in your .env file.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ENGINE = setup_database()

# --- CORE FUNCTIONS ---
def text_to_sql_and_export(
    natural_language_query: str,
    db_engine: sqlalchemy.engine.Engine
) -> Optional[Tuple[io.BytesIO, io.BytesIO]]:
    """
    Converts a natural language query to SQL, executes it, and returns the result
    as in-memory Excel and SQL script files.
    """
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)
        db = SQLDatabase(
            engine=db_engine,
            include_tables=['customer', 'transaction_purchase', 'product_name'],
            sample_rows_in_table_info=3
        )

        logging.info("Generating SQL query from natural language...")
        query_chain = create_sql_query_chain(llm, db)
        sql_query = query_chain.invoke({"question": natural_language_query})

        if "SELECT" in sql_query.upper():
            select_pos = sql_query.upper().find("SELECT")
            sql_query = sql_query[select_pos:]
        
        sql_query = sql_query.replace("```sql", "").replace("```", "").replace("plaintext", "").strip()
        
        logging.info(f"Cleaned SQL Query:\n{sql_query}")

        logging.info("Executing SQL query...")
        with db_engine.connect() as connection:
            result_df = pd.read_sql_query(sqlalchemy.text(sql_query), connection)
        logging.info(f"Query executed successfully, fetched {len(result_df)} rows.")

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Query_Result', index=False)
        excel_buffer.seek(0)

        sql_buffer = io.BytesIO()
        sql_buffer.write(sql_query.encode('utf-8'))
        sql_buffer.seek(0)

        return excel_buffer, sql_buffer

    except Exception as e:
        logging.error(f"An error occurred in the text-to-SQL process: {e}", exc_info=True)
        return None, None

# --- GRAPH STATE & MODELS ---
class GraphState(TypedDict):
    """Represents the state of our graph."""
    query: str
    is_lead_request: bool
    conditions: List[str]
    final_response: str
    excel_file: Optional[io.BytesIO]
    sql_file: Optional[io.BytesIO]

class LeadRequestClassifier(BaseModel):
    """Classifies whether the user is asking for a list of leads."""
    is_lead_request: bool = Field(description="Set to True if the user is asking for a list of customers/leads/users, False otherwise.")

class ConditionExtractor(BaseModel):
    """Extracts a list of valid filtering conditions from the user query."""
    conditions: List[str] = Field(description="A list of extracted filtering conditions based on the rules provided.")

# --- GRAPH NODES & EDGES ---
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

def node_ask_for_lead(state: GraphState):
    """Determines if the user's query is a lead generation request."""
    print("---NODE: Checking if this is a lead request---")
    query = state['query']
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert classifier. Your task is to determine if the user's query is asking for a list of customers, leads, or users. Respond with only True or False."),
        ("user", "Query: {query}")
    ])
    structured_llm = llm.with_structured_output(LeadRequestClassifier)
    chain = prompt | structured_llm
    classification_result = chain.invoke({"query": query})
    print(f"Is lead request: {classification_result.is_lead_request}")
    return {"is_lead_request": classification_result.is_lead_request}

def node_extract_conditions(state: GraphState):
    """Extracts valid, processable conditions from the query."""
    print("---NODE: Extracting valid conditions---")
    query = state['query']
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst. Your job is to extract filtering conditions from a user's query based on these strict rules:
- You can ONLY process conditions related to 'age', 'product_purchased' (valid products: [Laptop, Mouse, Keyboard, Monitor, Webcam, USB Cable, Headphones, Docking Station]), and 'wealth_status'.
- You MUST IGNORE any other conditions.
- If no valid conditions are found, return an empty list.
"""),
        ("user", "Extract the valid conditions from this query: {query}")
    ])
    structured_llm = llm.with_structured_output(ConditionExtractor)
    chain = prompt | structured_llm
    extraction_result = chain.invoke({"query": query})
    print(f"Extracted Conditions: {extraction_result.conditions}")
    return {"conditions": extraction_result.conditions}

def node_generate_report(state: GraphState):
    """Generates a SQL query from conditions, executes it, and returns files."""
    print("---NODE: Generating SQL and fetching data---")
    conditions = state.get('conditions', [])

    if not conditions or conditions == ['no condition']:
        response = "No valid conditions were found. I can only filter by 'age', 'product purchased', and 'wealth_status'."
        print(f"Final Response: \n{response}")
        return {"final_response": response, "excel_file": None, "sql_file": None}

    natural_language_query = "Find customers where " + " and ".join(conditions)
    print(f"Reconstructed NLQ for SQL generation: '{natural_language_query}'")

    excel_buffer, sql_buffer = text_to_sql_and_export(natural_language_query, ENGINE)

    if excel_buffer and sql_buffer:
        response = f"Success! I have generated a lead"
        print("Final Response: \nSuccess! Report and SQL query generated.")
        return {"final_response": response, "excel_file": excel_buffer, "sql_file": sql_buffer}
    else:
        response = "I'm sorry, an error occurred while trying to generate the report from the database."
        print(f"Final Response: \n{response}")
        return {"final_response": response, "excel_file": None, "sql_file": None}

def edge_should_continue(state: GraphState):
    """Decides if the process should continue after classification."""
    print("---DECISION: Should we continue?---")
    if state['is_lead_request']:
        print("Decision: Yes, it's a lead request. Continuing to extraction.")
        return "continue"
    else:
        print("Decision: No, not a lead request. Ending graph.")
        return "end"

# --- BUILD & COMPILE GRAPH ---
workflow = StateGraph(GraphState)

workflow.add_node("ask_for_lead", node_ask_for_lead)
workflow.add_node("extract_conditions", node_extract_conditions)
workflow.add_node("generate_report", node_generate_report)

workflow.set_entry_point("ask_for_lead")

workflow.add_conditional_edges(
    "ask_for_lead",
    edge_should_continue,
    {"continue": "extract_conditions", "end": END},
)

workflow.add_edge("extract_conditions", "generate_report")
workflow.add_edge("generate_report", END)

app = workflow.compile()
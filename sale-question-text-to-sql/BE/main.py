import os
import datetime
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query_functions import text_to_sql_and_export
from start_db_engine import setup_database

# --- Environment and Database Setup ---
load_dotenv()
API_KEY = os.environ.get("API_KEY")
ENGINE = setup_database()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Text-to-SQL API",
    description="An API that converts natural language to a SQL query, executes it, and saves the results.",
    version="1.0.0"
)

# --- CORS Middleware Configuration ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for Request Body ---
class QueryRequest(BaseModel):
    query: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    """Provides a simple welcome message for the root endpoint."""
    return {"message": "Welcome to the Text-to-SQL API. Send a POST request to /generate-and-save-query/."}

@app.post("/generate-and-save-query/")
async def generate_and_save(request: QueryRequest):
    """
    Accepts a natural language query, generates SQL, executes it,
    and saves the output files to ./QUERY/ and ./SQL_LOG/.
    """
    # 1. Check for API Key
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY environment variable not set."
        )

    # 2. Call the core processing function
    excel_file, sql_log = text_to_sql_and_export(
        natural_language_query=request.query,
        openai_api_key=API_KEY,
        db_engine=ENGINE
    )

    # 3. Handle the result from the processing function
    if not excel_file or not sql_log:
        raise HTTPException(
            status_code=500,
            detail="Failed to process the query. Check server logs for details."
        )

    # 4. Define output directories and create them if they don't exist
    excel_dir = "QUERY"
    sql_dir = "SQL_LOG"
    os.makedirs(excel_dir, exist_ok=True)
    os.makedirs(sql_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_excel_path = os.path.join(excel_dir, f"query_result_{timestamp}.xlsx")
    output_sql_path = os.path.join(sql_dir, f"query_log_{timestamp}.txt")

    # 5. Write the in-memory files to disk
    try:
        with open(output_excel_path, "wb") as f:
            f.write(excel_file.getbuffer())
        with open(output_sql_path, "wb") as f:
            f.write(sql_log.getbuffer())
    except IOError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write output files to disk: {e}"
        )
        
    # 6. Return a success response with file paths
    return {
        "message": "Query processed successfully!",
        "query_received": request.query,
        "files_saved": {
            "excel_result": output_excel_path,
            "sql_log": output_sql_path
        }
    }

# --- Main Execution Block ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
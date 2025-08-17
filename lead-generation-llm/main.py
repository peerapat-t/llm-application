import io
import base64
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the compiled graph app from your graph.py file
from graph import app

# Initialize FastAPI app
api = FastAPI(
    title="Lead Generation API",
    description="An API to generate lead lists from natural language queries.",
    version="1.0.0"
)

# --- CORS Configuration ---
origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    """Request model for the user's query."""
    query: str

@api.get("/")
async def root():
    """A simple endpoint to check if the API is running."""
    return {"status": "ok", "message": "API is running!"}

@api.post("/generate_report")
async def generate_report(request: QueryRequest):
    """
    Accepts a natural language query, saves the output files to the server,
    and returns a JSON object with the results for the front-end.
    """
    try:
        inputs = {"query": request.query}
        result = app.invoke(inputs)

        # Prepare the JSON response payload
        response_data = {
            "message": result.get('final_response'),
            "conditions": result.get('conditions'),
            "sql": None,
            "excel_file_b64": None,
            "filename": None, # Add filename field
        }

        # Create a timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # --- Server-Side File Saving ---
        # Create directories if they don't exist
        os.makedirs("./LOG/LEAD_FILE", exist_ok=True)
        os.makedirs("./LOG/SQL_LOG", exist_ok=True)

        # Extract, save, and process SQL file
        sql_file = result.get('sql_file')
        if sql_file:
            sql_file.seek(0)
            sql_content = sql_file.read()
            # Save to disk
            sql_filename = f"./LOG/SQL_LOG/query_{timestamp}.txt"
            with open(sql_filename, "wb") as f:
                f.write(sql_content)
            # Add to JSON response
            response_data["sql"] = sql_content.decode('utf-8')

        # Extract, save, and process Excel file
        excel_file = result.get('excel_file')
        if excel_file:
            excel_file.seek(0)
            excel_bytes = excel_file.read()
            
            # Create the dynamic filename
            excel_base_filename = f"lead_list_{timestamp}.xlsx"
            
            # Save to disk with full path
            excel_full_path = f"./LOG/LEAD_FILE/{excel_base_filename}"
            with open(excel_full_path, "wb") as f:
                f.write(excel_bytes)
            
            # Add base filename and base64 data to JSON response
            response_data["filename"] = excel_base_filename
            response_data["excel_file_b64"] = base64.b64encode(excel_bytes).decode('utf-8')

        return JSONResponse(content=response_data)

    except Exception as e:
        # Handle unexpected errors during graph execution
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(api, host="0.0.0.0", port=8000)
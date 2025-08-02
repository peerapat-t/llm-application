import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

# Assuming your functions are in a file named 'functions.py'
from functions import load_and_split_pdf, map_reduce_summarize

# Initialize the FastAPI app
app = FastAPI(
    title="PDF Summarization API",
    description="Upload a PDF and get a bullet-point summary using LangChain and OpenAI.",
    version="1.0.0"
)

# Define allowed origins for CORS
origins = ["*"]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize/", 
          summary="Summarize a PDF document",
          description="Upload a PDF file to generate a concise, bulleted summary.")
async def create_upload_file(file: UploadFile = File(...)):
    # Ensure the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Create a temporary directory to safely store the file
    temp_dir = "temp_pdf_storage"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file to the temporary path
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # --- Processing using your functions ---
        # 1. Load the PDF and split it into processable chunks
        print(f"Processing {file.filename}...")
        docs = load_and_split_pdf(pdf_path=temp_file_path)

        # 2. Perform the map-reduce summarization
        summary = map_reduce_summarize(docs)
        print("Summary generated successfully.")

        # Return the successful response
        return JSONResponse(
            status_code=200,
            content={"filename": file.filename, "summary": summary}
        )

    except Exception as e:
        # Raise a generic server error if anything goes wrong
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {e}")

    finally:
        # --- Cleanup ---
        # Close the file stream
        await file.close()
        # Remove the temporary file and directory to free up space
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the PDF Summarizer API. Go to /docs for the API documentation."}

# To run the server, use the command: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
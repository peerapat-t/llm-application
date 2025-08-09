from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid

from img_extract import encode_image, item_extraction, info_extraction, combine_all_data
from doc_create import create_quotation

os.makedirs("OUTPUTS", exist_ok=True)

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Quotation generation API is running!"}

@app.post("/generate-quotation/")
async def generate_quotation(file: UploadFile = File(...)):
    temp_file_path = f"temp_{uuid.uuid4().hex}.png"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        os.makedirs("outputs", exist_ok=True)

        base64_image = encode_image(temp_file_path)
        info_json = info_extraction(base64_image)
        item_json = item_extraction(base64_image)
        customer_info, items = combine_all_data(info_json, item_json)

        output_path = f"outputs/quotation_{uuid.uuid4().hex}.pdf"
        create_quotation(output_path, customer_info, items)

        return FileResponse(output_path, filename=os.path.basename(output_path), media_type='application/pdf')

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(temp_file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
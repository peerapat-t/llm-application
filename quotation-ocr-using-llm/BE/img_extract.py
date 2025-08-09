import os
import base64
import json
import openai
import instructor
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("API_KEY")
client = openai.OpenAI(api_key=API_KEY)
instructor.patch(client)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

######## Item extraction ########

class Item(BaseModel):
    item_name: str = Field(..., description="The name of the purchased item.")
    amount: int = Field(..., description="The quantity of the item purchased.")
    unit: str = Field(..., description="The unit for the amount (e.g., 'pcs', 'kg'). Default is 'หน่วย'.")
    price: float = Field(..., description="The total price for the specified amount of the item.")

class Receipt(BaseModel):
    items: List[Item]

def item_extraction(base64_image: str) -> Receipt:
    """
    Extracts items from a receipt image and returns a validated Pydantic object.
    """
    receipt: Receipt = client.chat.completions.create(
        model="gpt-4o",
        response_model=Receipt,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract each item from the receipt image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=2000,
    )
    return receipt.model_dump()

######## Info extraction ########

class CustomerInfo(BaseModel):
    name: Optional[str] = Field(None, description="The customer's full name or company name.")
    address: Optional[str] = Field(None, description="The customer's full mailing address.")
    email: Optional[str] = Field(None, description="The customer's email address.")
    telephone_number: Optional[str] = Field(None, description="The customer's telephone number.")

def info_extraction(base64_image: str) -> CustomerInfo:
    PROMPT_TEXT = """
    Please extract the customer's contact information. 
    IMPORTANT: You must ONLY extract the customer's address (recipient/Bill To), 
    not the sender's address. If a field isn't present, its value will be null.
    """
    customer_info: CustomerInfo = client.chat.completions.create(
        model="gpt-4o",
        response_model=CustomerInfo,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_TEXT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=2000,
    )
    return customer_info.model_dump()

######## Combine ########

def combine_all_data(info_data, item_data):
    customer_info = {
        'name': info_data['name'],
        'address': info_data['address'],
        'email': info_data['email'],
        'telephone_number': info_data['telephone_number'],
    }

    items = []
    for idx, item in enumerate(item_data['items'], start=1):
        item_name = item['item_name']
        amount = item['amount']
        unit_price = item['price']
        total_price = unit_price * amount
        items.append((idx, item_name, amount, unit_price, total_price))

    return customer_info, items
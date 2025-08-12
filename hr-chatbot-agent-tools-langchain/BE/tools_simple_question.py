import pandas as pd
import re
from langchain.agents import tool

COMPANY_DATA = {
    "name": "DOGBRAIN666",
    "description": "ผู้ให้บริการชั้นนำด้านโซลูชันเชิงนวัตกรรมในอุตสาหกรรมเทคโนโลยี",
    "mission": "เรามุ่งมั่นที่จะสร้างสรรค์ผลิตภัณฑ์ที่ล้ำสมัยเพื่อยกระดับคุณภาพชีวิตของผู้คนให้ดีขึ้น",
    "expertise": [
        "ปัญญาประดิษฐ์ (AI)",
        "คลาวด์คอมพิวติ้ง (cloud computing)",
        "เทคโนโลยีที่ยั่งยืน"
    ],
}

@tool
def get_company_info(query: str) -> str:
    """
    Use this tool to get a general summary about our company,
    including its name, mission, and what it does.
    It will always return the same full description.
    """
    expertise_string = ", ".join(COMPANY_DATA["expertise"])
    
    return (
        f"เราคือ '{COMPANY_DATA['name']}', {COMPANY_DATA['description']}. "
        f"{COMPANY_DATA['mission']}, โดยมีความเชี่ยวชาญด้าน {expertise_string}."
    )
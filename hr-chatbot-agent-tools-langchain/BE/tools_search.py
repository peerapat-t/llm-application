import pandas as pd
import re
from langchain.agents import tool
from pydantic import BaseModel, Field

DF_FLOOR_DETAIL = pd.read_excel('./db/db_item_floor.xlsx')
DF_FLOOR_DETAIL_INDEXED = DF_FLOOR_DETAIL.set_index('Floor')
FLOOR_DATA = DF_FLOOR_DETAIL_INDEXED['List of Item'].to_dict()

class FloorSearchInput(BaseModel):
    query: str = Field(description="The floor number (e.g., '5') or the item name \
                       (e.g., 'printer') to search for.")

@tool(args_schema=FloorSearchInput)
def search_floor_item(query: str) -> str:
    """
    Searches for items on a specific floor or finds which floor an item is located on.
    The input can be a floor number (e.g., "floor 5") or an item name (e.g., "printer").
    """
    query_lower = query.lower()
    
    floor_numbers = re.findall(r'\d+', query_lower)
    if floor_numbers:
        floor_num = int(floor_numbers[0])
        if floor_num in FLOOR_DATA:
            return f"On Floor {floor_num}, you can find: {FLOOR_DATA[floor_num]}."

    for floor, items in FLOOR_DATA.items():
        if query_lower in items.lower():
            return f"You can find '{query}' on Floor {floor}. The items on this floor are: {items}."
    
    return "I'm sorry, I couldn't find information for that item or floor."
from langchain_core.tools import tool

# --- Tool Definitions ---

@tool
def get_space_details(query: str) -> str:
    """Provides detailed specifications and dimensions of a product."""
    print(f"---TOOL: Getting space details for: {query}---")
    if "sofa" in query.lower():
        return "The Grand Comfort Sofa is 220cm wide, 95cm deep, and 80cm high."
    elif "desk" in query.lower():
        return "The Executive Desk is 150cm wide, 75cm deep, and 78cm high."
    else:
        return "Could not find space details for the specified product."

@tool
def get_product_origin(query: str) -> str:
    """Provides information about the origin and materials of a product."""
    print(f"---TOOL: Getting origin details for: {query}---")
    if "sofa" in query.lower():
        return "The Grand Comfort Sofa is handcrafted in Italy using premium leather."
    elif "desk" in query.lower():
        return "The Executive Desk is made from sustainable American oak."
    else:
        return "Could not find origin details for the specified product."

@tool
def get_price_details(product_name: str) -> str:
    """Provides the current price of a specific product."""
    print(f"---TOOL: Getting price for: {product_name}---")
    if "sofa" in product_name.lower():
        return "The Grand Comfort Sofa is priced at $1,500."
    elif "desk" in product_name.lower():
        return "The Executive Desk is priced at $800."
    else:
        return "Product not found. Please specify the product name."

@tool
def get_available_discounts(product_name: str) -> str:
    """Checks for any available discounts or promotions for a product."""
    print(f"---TOOL: Checking discounts for: {product_name}---")
    if "sofa" in product_name.lower():
        return "There is a 10% summer sale discount on the Grand Comfort Sofa."
    else:
        return "There are currently no special discounts for the Executive Desk."

@tool
def get_warranty_policy(product_name: str) -> str:
    """Provides the warranty policy details for a specific product."""
    print(f"---TOOL: Getting warranty policy for: {product_name}---")
    return f"All our products, including the {product_name}, come with a 2-year standard warranty covering manufacturing defects."

@tool
def get_warranty_form(product_name: str, invoice_id: str) -> str:
    """
    Provides a link to the warranty claim form, which requires a product name and an invoice ID.
    If the invoice ID is missing from the user's query, you must ask the user for it.
    """
    print(f"---TOOL: Attempting to get warranty form for: {product_name} with Invoice ID: {invoice_id}---")
    
    if not product_name or not invoice_id:
        return "The product name and invoice ID are both required to get the warranty form link. Please ask the user for the missing information."
        
    return (f"To file a warranty claim for your {product_name} (Invoice #{invoice_id}), "
            f"please visit our website at example.com/warranty-claim?product={product_name.replace(' ', '+')}&invoice={invoice_id}")

# --- Tool Lists for Agents ---
# Grouping tools for easy assignment to each agent.
product_detail_tools = [get_space_details, get_product_origin]
pricing_tools = [get_price_details, get_available_discounts]
warranty_tools = [get_warranty_policy, get_warranty_form]


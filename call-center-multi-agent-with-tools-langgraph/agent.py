from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from llm_config import llm
from tools import product_detail_tools, pricing_tools, warranty_tools

# --- Agent Creation Helper ---
def create_agent(llm: ChatOpenAI, tools: list, system_message: str):
    """
    Helper function to create a ReAct agent with a custom system prompt.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    agent = create_react_agent(llm, tools, prompt=prompt)
    return agent

# --- Agent Definitions ---
product_detail_agent = create_agent(
    llm,
    tools=product_detail_tools,
    system_message="You are an expert in product specifications and origins. Use your tools to answer questions about product details like dimensions, materials, and where it's made. Be concise in your responses."
)

pricing_agent = create_agent(
    llm,
    tools=pricing_tools,
    system_message="You are a pricing and promotions specialist. Use your tools to answer questions about product prices and available discounts."
)

warranty_agent = create_agent(
    llm,
    tools=warranty_tools,
    system_message="You are a warranty support agent. Use your tools to answer questions about warranty policies and how to file a claim. If you need an invoice ID to file a claim, you must ask the user for it."
)

# --- Agent Runnable Dictionary ---
# This dictionary maps agent names to their runnable instances for the graph.
agent_runnables = {
    "ProductDetailAgent": product_detail_agent,
    "PricingAgent": pricing_agent,
    "WarrantyAgent": warranty_agent,
}
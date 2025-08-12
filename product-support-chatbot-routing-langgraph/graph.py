# graph.py

from typing import TypedDict, Literal, Annotated, List
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import setup_environment

# Set up the environment with the API key
setup_environment()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

class GraphState(TypedDict):
    """
    Represents the state of our graph, including conversation memory.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    is_product: bool

def classify_request_type(state: GraphState) -> dict:
    """Classifies if the user's question is about products."""
    question = state["messages"][-1].content

    prompt = ChatPromptTemplate.from_template(
        """Determine if the user's question is about our company products.
        Our company name is "DOGBRAIN666".
        If yes, respond with 'True'. If no, respond with 'False'.
        If the user is asking about a product but not ours, respond with 'False'.

        User Question: "{question}"
        Answer:"""
    )
    classification_chain = prompt | llm | StrOutputParser()
    response = classification_chain.invoke({"question": question}).strip()
    is_product = response.lower() == "true"
    return {"is_product": is_product}

def decide_to_continue_or_end(state: GraphState) -> Literal["answer_product_question", "handle_off_topic"]:
    """Decides the next step based on product relevance."""
    if state.get("is_product"):
        return "answer_product_question"
    else:
        return "handle_off_topic"

def answer_product_question(state: GraphState) -> dict:
    """Answers customer questions about DOGBRAIN666 products."""
    product_knowledge = """
    DOGBRAIN666 Product Catalog:
    1. DOGBRAIN666 Alpha Headset - Wireless gaming headset with 7.1 surround sound, 40hr battery, RGB lights.
    2. DOGBRAIN666 Gamma Mouse - Ultra-light 55g gaming mouse with adjustable DPI up to 26,000.
    3. DOGBRAIN666 Titan Keyboard - Mechanical keyboard with hot-swappable switches and customizable macros.
    4. DOGBRAIN666 CloudPad - Game controller compatible with PC, mobile, and cloud gaming platforms.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful product support assistant for DOGBRAIN666."
         "Use ONLY the information below to answer the customer question, but use the conversation history for context."
         "If the answer is not in the product details, politely say you don't have that information.\n\n"
         "Product Details:\n{product_info}"),
        ("placeholder", "{messages}")
    ])

    answer_chain = prompt | llm
    answer = answer_chain.invoke({
        "product_info": product_knowledge,
        "messages": state['messages']
    })
    return {"messages": [answer]}

def handle_off_topic(state: GraphState) -> dict:
    """Handles questions that are not about DOGBRAIN666 products."""
    response = AIMessage(content="I'm sorry, I can only answer questions about DOGBRAIN666 products. How can I help you with our product line?")
    return {"messages": [response]}

def get_graph():
    """Defines and compiles the LangGraph application."""
    graph = StateGraph(GraphState)
    graph.add_node("classify_request_type", classify_request_type)
    graph.add_node("answer_product_question", answer_product_question)
    graph.add_node("handle_off_topic", handle_off_topic)

    graph.add_edge(START, "classify_request_type")
    graph.add_conditional_edges("classify_request_type", decide_to_continue_or_end)
    graph.add_edge("answer_product_question", END)
    graph.add_edge("handle_off_topic", END)

    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    return app
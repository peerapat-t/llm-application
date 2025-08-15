from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm_config import llm

# --- Pydantic Models for Structured Output ---

class TopicClassifier(BaseModel):
    """Classify the user's query as on-topic or off-topic."""
    decision: Literal["on_topic", "off_topic"] = Field(
        ...,
        description="Classify the query as 'on_topic' if it is about furniture products, or 'off_topic' if it is about anything else."
    )

class QueryClassifier(BaseModel):
    """Classify the user's query as containing a single or multiple questions."""
    decision: Literal["single_question", "multi_question"] = Field(
        ...,
        description="Classify the query as either containing a single question or multiple distinct questions."
    )

class Router(BaseModel):
    """Route a user request to the appropriate agent or finish the conversation."""
    next: Literal["ProductDetailAgent", "PricingAgent", "WarrantyAgent", "FINISH"] = Field(
        ...,
        description="Given the user's request, select the next agent to route to or 'FINISH' if the conversation is over."
    )

# --- LLM Chains for Supervision ---

# Chain for checking if the query is on-topic
topic_check_system_message = (
    "You are a topic analyzer. Your task is to determine if the user's query is related to furniture products "
    "(like sofas, desks, dimensions, price, warranty, origin). If the query is about these topics, classify it as 'on_topic'. "
    "If it is about anything else (e.g., weather, general conversation, greetings), classify it as 'off_topic'. "
    "The user's message will be the last in the list."
)
topic_check_chain = (
    ChatPromptTemplate.from_messages([("system", topic_check_system_message), MessagesPlaceholder(variable_name="messages")])
    | llm.with_structured_output(schema=TopicClassifier)
)

# Chain for checking for multiple questions
filter_system_message = (
    "You are a query analyzer. Your task is to determine if the user's message "
    "contains more than one distinct question. The user's message will be the last in the list. "
    "Respond with 'multi_question' if it does, and 'single_question' if it does not."
)
filter_chain = (
    ChatPromptTemplate.from_messages([("system", filter_system_message), MessagesPlaceholder(variable_name="messages")])
    | llm.with_structured_output(schema=QueryClassifier)
)

# Chain for routing to the correct agent
supervisor_system_message = (
    "You are a supervisor managing a team of expert agents. "
    "Based on the user's request, you will route them to the appropriate agent: "
    "ProductDetailAgent, PricingAgent, or WarrantyAgent. "
    "If the user is just making conversation, respond by choosing 'FINISH'. "
    "The user's message will be the last one in the list."
)
supervisor_chain = (
    ChatPromptTemplate.from_messages([("system", supervisor_system_message), MessagesPlaceholder(variable_name="messages")])
    | llm.with_structured_output(schema=Router)
)
import os
import openai
from dotenv import load_dotenv
from langchain.agents import tool
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Zilliz
from pydantic import BaseModel, Field

load_dotenv()

ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")
OPENAI_API_KEY = os.environ.get("API_KEY")
CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

LEAVE_POLICY_VECTOR_STORE = Zilliz(
    embedding_function=EMBEDDING_MODEL,
    connection_args={"uri": ZILLIZ_URI, "token": ZILLIZ_TOKEN},
    collection_name='leave_policy',
    text_field="page_content"
)

SALARY_POLICY_VECTOR_STORE = Zilliz(
    embedding_function=EMBEDDING_MODEL,
    connection_args={"uri": ZILLIZ_URI, "token": ZILLIZ_TOKEN},
    collection_name='salary_policy',
    text_field="page_content"
)

RESIGN_POLICY_VECTOR_STORE = Zilliz(
    embedding_function=EMBEDDING_MODEL,
    connection_args={"uri": ZILLIZ_URI, "token": ZILLIZ_TOKEN},
    collection_name='resign_policy',
    text_field="page_content"
)

LEAVE_POLICY_RETRIEVER = LEAVE_POLICY_VECTOR_STORE.as_retriever(search_kwargs={"k": 5})
SALARY_POLICY_RETRIEVER = SALARY_POLICY_VECTOR_STORE.as_retriever(search_kwargs={"k": 5})
RESIGN_POLICY_RETRIEVER = RESIGN_POLICY_VECTOR_STORE.as_retriever(search_kwargs={"k": 5})

class PolicyQuestionInput(BaseModel):
    question: str = Field(description="The user's question about a specific HR policy.")

@tool(args_schema=PolicyQuestionInput)
def answer_leave_question(question: str) -> str:
    """
    Answers an HR leave policy question. Use for any questions about
    vacation, sick leave, holidays, etc.
    """
    print(f"\n---> [Tool Called] Searching for answer to: '{question}'")
    
    retrieved_docs: list[Document] = LEAVE_POLICY_RETRIEVER.invoke(question)
    
    knowledge = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    print(f"---> [Context Retrieved] Found {len(retrieved_docs)} relevant document(s).")

    system_prompt = (
        "You are a professional HR assistant. Your role is to answer employee questions "
        "about the company's leave policy. "
        "Base your answer strictly on the context provided below. "
        "If the answer is not found in the provided context, clearly state that "
        "the information is not available in the policy documents and advise the user "
        "to contact the HR department directly."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    print("---> [LLM] Sending request to generate final answer...")
    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()


@tool(args_schema=PolicyQuestionInput)
def answer_salary_question(question: str) -> str:
    """
    Answers an HR salary policy question. Use for any questions about
    compensation, payroll, bonuses, pay grades, etc.
    """
    print(f"\n---> [Tool Called] Searching for answer to: '{question}'")
    
    retrieved_docs: list[Document] = SALARY_POLICY_RETRIEVER.invoke(question)
    
    knowledge = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    print(f"---> [Context Retrieved] Found {len(retrieved_docs)} relevant document(s).")

    system_prompt = (
        "You are a professional HR assistant. Your role is to answer employee questions "
        "about the company's salary policy. "
        "Base your answer strictly on the context provided below. "
        "If the answer is not found in the provided context, clearly state that "
        "the information is not available in the policy documents and advise the user "
        "to contact the HR department directly."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    print("---> [LLM] Sending request to generate final answer...")
    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()


@tool(args_schema=PolicyQuestionInput)
def answer_resignation_question(question: str) -> str:
    """

    Answers an HR resignation policy question. Use for any questions about
    notice periods, final pay, exit procedures, returning company property, etc.
    """
    print(f"\n---> [Tool Called] Searching for answer to: '{question}'")
    
    retrieved_docs: list[Document] = RESIGN_POLICY_RETRIEVER.invoke(question)
    
    knowledge = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    print(f"---> [Context Retrieved] Found {len(retrieved_docs)} relevant document(s).")

    system_prompt = (
        "You are a professional HR assistant. Your role is to answer employee questions "
        "about the company's resignation policy. "
        "Base your answer strictly on the context provided below. "
        "If the answer is not found in the provided context, clearly state that "
        "the information is not available in the policy documents and advise the user "
        "to contact the HR department directly."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    print("---> [LLM] Sending request to generate final answer...")
    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()
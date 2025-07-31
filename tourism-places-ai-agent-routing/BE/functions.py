import warnings
warnings.filterwarnings("ignore")
import os
import json
import openai
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from dotenv import load_dotenv

load_dotenv()
ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")
API_KEY = os.environ.get("API_KEY")

EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
CLIENT = openai.OpenAI(api_key=API_KEY)
DB_CLIENT = MilvusClient(
    uri=os.environ["ZILLIZ_URI"],
    token=os.environ["ZILLIZ_TOKEN"]
)

def classify_question(question: str):

    system_prompt = (
        "You are a helpful classification assistant.\n"
        "Classify the following question into one of these categories:\n"
        "Bangkok location, Chiang Mai location, Phuket location, or Unclassified."
    )
    user_content = f"Question: {question}\n\nClassification:"

    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0,
        max_tokens=15
    )
    
    classification = response.choices[0].message.content
    return classification.strip()

def get_top_k(question, collection):

    question_vector = EMBEDDING_MODEL.encode(question).tolist()

    search_results = DB_CLIENT.search(
        collection_name=collection,
        data=[question_vector],
        limit=10,
        output_fields=['content','metadata']
    )[0]

    knowledge = "".join(c['entity']['metadata'] for c in search_results)

    return knowledge

def bangkok_question_with_rag(question: str, knowledge: str):

    system_prompt = (
        "You are a helpful assistant for Bangkok tourism. "
        "You can answer questions about tourist attractions, travel planning, transportation, food, culture, and more related to Bangkok. "
        "Use the provided context below when relevant."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.5,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()

def chiangmai_question_with_rag(question: str, knowledge: str):

    system_prompt = (
        "You are a helpful assistant for Chiang mai tourism. "
        "You can answer questions about tourist attractions, travel planning, transportation, food, culture, and more related to Bangkok. "
        "Use the provided context below when relevant."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.5,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()

def phuket_question_with_rag(question: str, knowledge: str):

    system_prompt = (
        "You are a helpful assistant for Phuket tourism. "
        "You can answer questions about tourist attractions, travel planning, transportation, food, culture, and more related to Bangkok. "
        "Use the provided context below when relevant."
    )

    user_content = (
        f"--- CONTEXT ---\n"
        f"{knowledge}\n"
        f"--- END CONTEXT ---\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    response = CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.5,
    )
    
    answer = response.choices[0].message.content
    return answer.strip()
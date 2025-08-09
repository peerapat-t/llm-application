import os
import json
import openai
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
DB_CLIENT = MilvusClient(
    uri=os.environ["ZILLIZ_URI"],
    token=os.environ["ZILLIZ_TOKEN"]
)

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
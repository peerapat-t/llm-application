import os
from langchain_community.vectorstores import Zilliz
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")
API_KEY = os.environ.get("API_KEY")
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def get_retrival(collection_name):
    vector_store = Zilliz(
        embedding_function=EMBEDDING_MODEL,
        connection_args={
            "uri": ZILLIZ_URI,
            "token": ZILLIZ_TOKEN,
        },
        collection_name=collection_name,
    )

    return vector_store
import pdfplumber
import pandas as pd
import json
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def pdf_to_df(pdf_path, title):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                data.append({
                    'title': title,
                    'page_number': page_num + 1,
                    'page_content': text
                })
    df = pd.DataFrame(data)
    return df

def chunk_df(df, chunk_size=1000, overlap=200):
    chunked_data = []
    for _, row in df.iterrows():
        content = row['page_content']
        start = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk = content[start:end]
            chunked_data.append({
                'title': row['title'],
                'page_number': row['page_number'],
                'page_content': chunk.strip()
            })
            start += chunk_size - overlap

    return pd.DataFrame(chunked_data)

def embedding_and_to_list(df):
    title_list = df['title'].tolist()
    page_number_list = df['page_number'].tolist()
    page_content_list = df['page_content'].tolist()
    vector_list = []
    for content in page_content_list:
        embedding = EMBEDDING_MODEL.encode(str(content))
        vector_list.append(embedding)

    return [title_list, page_number_list, page_content_list, vector_list]

def setup_milvus_collection(zilliz_uri, token, collection_name):
    connections.connect("default", uri=zilliz_uri, token=token)

    page_number_field = FieldSchema(name="page_number", dtype=DataType.INT64, is_primary=True, auto_id=False)
    title_field = FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=4000)
    page_content_field = FieldSchema(name="page_content", dtype=DataType.VARCHAR, max_length=65535)
    vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)

    schema = CollectionSchema(
        fields=[title_field, page_number_field, page_content_field, vector_field],
        description="Collection"
    )

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    collection = Collection(name=collection_name, schema=schema, using='default')

    index_params = {
        "metric_type": "L2",
        "index_type": "AUTOINDEX",
        "params": {}
    }

    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    return collection

def insert_data_to_milvus(collection, data_to_insert):
    result = collection.insert(data_to_insert)
    collection.flush()
    return result
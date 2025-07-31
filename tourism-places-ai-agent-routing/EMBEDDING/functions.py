import json
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def split_text(text, chunk_size=1000, chunk_overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def prepare_data(data):
    ids, embeddings, contents, metadatas = [], [], [], []
    
    for i, item in enumerate(data):
        content_for_embedding = (
            f"The location's name is {item.get('name', 'N/A')}. "
            f"It is a {item.get('type', 'N/A')} located in the {item.get('district', 'N/A')} district. "
            f"{item.get('description', 'No description available.')}"
        )

        chunks = split_text(content_for_embedding)

        metadata_str = json.dumps(item)

        for chunk_index, chunk in enumerate(chunks):
            item_id = f"loc_{i+1:03d}_chunk_{chunk_index}"
            chunk_embedding = EMBEDDING_MODEL.encode(str(chunk))

            ids.append(item_id)
            embeddings.append(chunk_embedding)
            contents.append(chunk)
            metadatas.append(metadata_str)

    return [ids, embeddings, contents, metadatas]

def setup_milvus_collection(zilliz_uri, token, collection_name):
    connections.connect("default", uri=zilliz_uri, token=token)

    id_field = FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100)
    embedding_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)
    content_field = FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4000)
    metadata_field = FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)

    schema = CollectionSchema(
        fields=[id_field, embedding_field, content_field, metadata_field],
        description="Collection for storing location embeddings"
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
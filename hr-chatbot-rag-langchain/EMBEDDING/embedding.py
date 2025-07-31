import warnings
warnings.filterwarnings("ignore")
import os
import json
from dotenv import load_dotenv
from functions import pdf_to_df, chunk_df, embedding_and_to_list, setup_milvus_collection, \
insert_data_to_milvus, setup_milvus_collection, insert_data_to_milvus

load_dotenv()
ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")

policy_file_path = 'db/thai_leave_policy.pdf'
title = 'HR leave policy'

policy_pdf = pdf_to_df(policy_file_path, title)
policy_pdf_chunked = chunk_df(policy_pdf)
policy_data = embedding_and_to_list(policy_pdf_chunked)

policy_collection = setup_milvus_collection(ZILLIZ_URI, ZILLIZ_TOKEN, 'hr_policy')

insert_data_to_milvus(policy_collection, policy_data)
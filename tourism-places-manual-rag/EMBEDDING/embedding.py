import warnings
warnings.filterwarnings("ignore")
import os
import json
from dotenv import load_dotenv
from functions import pdf_to_df, chunk_df, embedding_and_to_list, \
setup_milvus_collection, insert_data_to_milvus

load_dotenv()
ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")

hr_policy_path = 'db/thai_leave_policy.pdf'
title = 'HR leave policy'

hr_policy_pdf = pdf_to_df(hr_policy_path, title)
hr_policy_pdf_chunked = chunk_df(hr_policy_pdf, chunk_size=500, overlap=50)
hr_policy_data = embedding_and_to_list(hr_policy_pdf_chunked)

hr_policy_collection = setup_milvus_collection(ZILLIZ_URI, ZILLIZ_TOKEN, 'bangkok_tourism_places')
insert_data_to_milvus(hr_policy_collection, hr_policy_data)
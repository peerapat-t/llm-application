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

leave_file_path = 'db/leave_policy.pdf'
resign_file_path = 'db/resignment.pdf'
salary_file_path = 'db/salary_policy.pdf'

leave_pdf = pdf_to_df(leave_file_path, 'leave policy')
resign_pdf = pdf_to_df(resign_file_path, 'resign policy')
salary_pdf = pdf_to_df(salary_file_path, 'salary policy')

leave_pdf_chunked = chunk_df(leave_pdf)
resign_pdf_chunked = chunk_df(resign_pdf)
salary_pdf_chunked = chunk_df(salary_pdf)

leave_data = embedding_and_to_list(leave_pdf_chunked)
resign_data = embedding_and_to_list(resign_pdf_chunked)
salary_data = embedding_and_to_list(salary_pdf_chunked)

leave_collection = setup_milvus_collection(ZILLIZ_URI, ZILLIZ_TOKEN, 'leave_policy')
resign_collection = setup_milvus_collection(ZILLIZ_URI, ZILLIZ_TOKEN, 'resign_policy')
salary_collection = setup_milvus_collection(ZILLIZ_URI, ZILLIZ_TOKEN, 'salary_policy')

insert_data_to_milvus(leave_collection, leave_data)
insert_data_to_milvus(resign_collection, resign_data)
insert_data_to_milvus(salary_collection, salary_data)
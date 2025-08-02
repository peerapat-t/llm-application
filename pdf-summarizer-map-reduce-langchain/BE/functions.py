import os
import openai
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("API_KEY")
MODEL = ChatOpenAI(temperature=0.3, openai_api_key=API_KEY, model_name='gpt-4o')

MAP_TEMPLATE = """
You will be given a single passage from a document. Create a concise summary of this passage.
Passage: {text}
CONCISE SUMMARY:
"""

COMBINE_TEMPLATE = """
You will be given a series of summaries from a document. Create a consolidated, final summary in 5 bullet points that covers all key topics.
Summaries: {text}
FINAL BULLETED SUMMARY:
"""

MAP_PROMPT_TEMPLATE = PromptTemplate(template=MAP_TEMPLATE, input_variables=["text"])
COMBINE_PROMPT_TEMPLATE = PromptTemplate(template=COMBINE_TEMPLATE, input_variables=["text"])

def load_and_split_pdf(pdf_path):

    print(f"Loading and splitting document: {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    text = ''.join(page.page_content for page in pages)
    text = text.replace('\t', ' ')

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], 
        chunk_size=1000, 
        chunk_overlap=200
    )
    docs = text_splitter.create_documents([text])
    print(f"Document split into {len(docs)} chunks.")
    return docs

def map_reduce_summarize(docs):
   
    summary_chain = load_summarize_chain(
        llm=MODEL,
        chain_type='map_reduce',
        map_prompt=MAP_PROMPT_TEMPLATE,
        combine_prompt=COMBINE_PROMPT_TEMPLATE
    )
    output = summary_chain.run(docs)
    return output
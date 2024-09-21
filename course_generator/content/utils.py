# content/utils.py

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

CHROMA_PATH = "chroma"

# Initialize Chroma DB
embedding_function = OpenAIEmbeddings(openai_api_key="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")
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

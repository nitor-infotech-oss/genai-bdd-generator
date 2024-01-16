from config import persistDirectory_child, persistDirectory_parent
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
import os
from langchain.storage._lc_store import create_kv_docstore



    

def get_docs(question):
    """Combine both the docs retrieved from confluence and azure.
Store them into Chromadb.
All the docs are stored as a parent documents (key value pair) using LocalStorage into local disk.
These docs are divided into chunks and these chunks are embedded and stored into Chromadb using OpenAIEmbeding().
When we query Chromadb using the question parameters it will first fetch all relevant child chunks from DB and
then fetch the parent docs using those chunks.
"""

    embedding_function = OpenAIEmbeddings()
    fs = LocalFileStore(persistDirectory_parent)

    # Storage layer for parent documents
    store = create_kv_docstore(fs)
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
    vectorstore = Chroma(collection_name="split_parents", 
                         embedding_function=embedding_function, 
                         persist_directory=persistDirectory_child)
    
    retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                        docstore=store,
                                        child_splitter=child_splitter,
                                        parent_splitter=parent_splitter,
                                        search_type="mmr",
                                        search_kwargs={"k": 30},
                                        lambda_mult = 1)
    
    relevant_docs = retriever.get_relevant_documents(question)
    return relevant_docs



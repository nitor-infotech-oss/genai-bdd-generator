from dotenv import load_dotenv
load_dotenv()

import time
import os

import streamlit as st

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from services.document import DocumentHelper

def refresh_database():
    persistDirectory_parent = os.getenv('persistDirectory_parent')
    persistDirectory_child = os.getenv('persistDirectory_child')
    name_of_collection = os.getenv('COLLECTION_NAME')
    helper = DocumentHelper()
    filtered_docs = None

    with st.spinner(text="Refreshing Database...") as s:
        # embedding_function = OpenAIEmbeddings()
        _embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        # Delete all parent documents from docstore
        fs = LocalFileStore(persistDirectory_parent)
        store = create_kv_docstore(fs)
        store.mdelete(keys=list(fs.yield_keys()))

        # Delete all child chunks collection data from chromadb vector database
        vectorstore = Chroma(collection_name=name_of_collection, collection_metadata={"hnsw:space": "cosine"},
                             embedding_function=_embedding_function, persist_directory=persistDirectory_child)
        
        for collection in vectorstore._client.list_collections():
            if collection.name == name_of_collection:
                ids = collection.get()['ids']
                if ids:
                    collection.delete(ids=ids)
                break

        # Get documents and remove duplicates
        docs = helper.get_confluence_data()
        docs.extend(helper.prepare_azure_docs())
        filtered_docs  = helper.remove_duplicates_docs(docs)

    if filtered_docs:
        with st.spinner("Hold on for a while..."):
            # Split the parent documents into small chunks to store in chromadb vectordb
            parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
            retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                                docstore=store,
                                                child_splitter=child_splitter,
                                                parent_splitter=parent_splitter)

            # Add documents to docstore(parent) and chromadb(child chunks)
            retriever.add_documents(filtered_docs, ids=None)
        
    with st.spinner("Done"):
        time.sleep(1)


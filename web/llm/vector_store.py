from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from llm.preprocessor import remove_duplicates_docs
import streamlit as st
import time
import os
from data.confluence_data import get_all_spaces_docs
from data.azure_data import prepare_azure_docs


def job_scheduler_refresh_database():
    persistDirectory_parent = os.getenv('persistDirectory_parent')
    persistDirectory_child = os.getenv('persistDirectory_child')

    with st.spinner(text="Refreshing Database...") as s:
        embedding_function = OpenAIEmbeddings()
        # Delete all parent documents from docstore
        fs = LocalFileStore(persistDirectory_parent)
        parent_docs_keys = []

        for key in fs.yield_keys():
            parent_docs_keys.append(key)

        store = create_kv_docstore(fs)
        store.mdelete(keys=parent_docs_keys)

        # Delete all child chunks collection data from chromadb vector database
        vectorstore = Chroma(collection_name="split_parents", 
                             embedding_function=embedding_function, 
                             persist_directory=persistDirectory_child)

        for collection in vectorstore._client.list_collections():
            if collection.name == "split_parents":
                ids = collection.get()['ids']
                if len(ids)>0:
                    collection.delete(ids=ids)
                break

        # Get documents
        docs =[]
        confluence_docs = get_all_spaces_docs()
        work_items = prepare_azure_docs()
        docs.extend(confluence_docs)
        docs.extend(work_items)
        filtered_docs  = remove_duplicates_docs(docs)
        
    with st.spinner("Hold on for a while..."):
        # create docstore for parent document storage in Key-Value pairs
        fs = LocalFileStore(persistDirectory_parent)
        store = create_kv_docstore(fs)
        #Split the parent documents into small chunks to store in chromadb vectordb
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
        retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                            docstore=store,
                                            child_splitter=child_splitter,
                                            parent_splitter=parent_splitter,
                                            search_type="mmr",
                                            search_kwargs={"k": 25},
                                            lambda_mult = 1)

        # Add documents to docstore(parent) and chromadb(child chunks)
        retriever.add_documents(filtered_docs, ids=None)
        
    with st.spinner("Done"):
        time.sleep(1)


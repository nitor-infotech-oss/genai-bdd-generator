import streamlit as st
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import  LocalFileStore
import clipboard
import os

from llm.docs_retriever import get_docs
from llm.vector_store import job_scheduler_refresh_database

st.set_page_config(page_title="Search Documents",
                   initial_sidebar_state="collapsed")

persistDirectory_parent = os.getenv('persistDirectory_parent')
col1,col2,col3 = st.columns([3,2,2])

with col3:
    st.button(label="Refresh Database",
              on_click=job_scheduler_refresh_database,
              type="primary",
              help=""" Refresh Database will do following operations:
              1. Remove all documents from DB, 
              2. Retrieve all docs (from confluence and azure devops)
              3. Filter out unique documents
              4. Embed filtered documents and store into doctore and vectorestore
              """)

fs = LocalFileStore(persistDirectory_parent)
store = create_kv_docstore(fs)

keys = []
for key in fs.yield_keys():
    keys.append(key)
    
query = st.text_input(label="Search",
                      placeholder='Enter text to search documents & press "Enter"')

relevant_docs = list()


if query:
    relevant_docs = get_docs(query)
else:
    my_docs = store.mget(keys=keys)
    relevant_docs = my_docs
        

def copyText(doc):
    clipboard.copy(str(doc))
    st.toast(doc.metadata['title']+ " - copied!")


st.header("Documents: ")


for i, doc in enumerate(relevant_docs):
    col1, col2 = st.columns([3.5, 1])
    with col2:
        st.button(label="copy",
                  key=i,
                  on_click=copyText,args=((doc),),
                  help="copy text to clipboard!")
        
    with col1:
        st.markdown(str(i+1)+": "+doc.metadata['title'] + " ( id: "+doc.metadata['id']+" )")

    st.markdown(doc.page_content)
    st.markdown('-'*10)
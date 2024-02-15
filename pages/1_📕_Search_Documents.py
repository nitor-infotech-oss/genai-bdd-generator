from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd
import streamlit as st
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import  LocalFileStore

from services.document import DocumentHelper
from tasks import refresh_database

col1,col2,col3 = st.columns([3,2,2])
with col3:
    st.button(label="Refresh Database",
              on_click=refresh_database,
              type="primary",
              help="Deletes records & Sync from source")

query = st.text_input(label="Search Story", placeholder='Enter text to search documents & press "Enter"')
print("Query is", query)
if query:
    helper = DocumentHelper()
    relevant_docs = helper.get_relevant_docs(query)
else:
    persistDirectory_parent = os.getenv('persistDirectory_parent')
    fs = LocalFileStore(persistDirectory_parent)
    store = create_kv_docstore(fs)
    relevant_docs = store.mget(keys=list(fs.yield_keys()))

if relevant_docs:
    with st.chat_message("assistant"):
        for i,doc in enumerate(relevant_docs):
            is_expanded = True if i < 5 else False
            with st.expander(f":blue[**{doc.metadata['title'].strip().upper()}**]", expanded=is_expanded):
                st.caption(f":gray[ID: {doc.metadata['id'].strip()}]")
                st.markdown(f"*{doc.page_content.strip()}*")
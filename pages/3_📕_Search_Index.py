from dotenv import load_dotenv
load_dotenv()

import os
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
show_sort = False
if query:
    helper = DocumentHelper()
    relevant_docs = helper.get_relevant_index_docs(query)
    show_sort = True
else:
    fs = LocalFileStore("documents/new")
    store = create_kv_docstore(fs)
    relevant_docs = store.mget(keys=list(fs.yield_keys()))

options, sort_order_asc, sort_order_desc  = None, None, None
if relevant_docs:
    if show_sort:
        col4,col5,col6 = st.columns([5,3,2])
        with col4:
            options = st.multiselect(
                'Sort By',
                ['Title', 'Relevance'],
                ['Relevance',], max_selections=1)
        with col6:
            if options:
                sort_order_desc = st.button(':small_red_triangle:')
                sort_order_asc = st.button(':small_red_triangle_down:')
    
    st.caption("No of Documents: %d" % len(relevant_docs))
    print(options, sort_order_asc, sort_order_desc)
    if options:
        if sort_order_asc or sort_order_desc:
            relevant_docs = helper.get_sorted_documents(relevant_docs, options, sort_order_desc)
        else:
            relevant_docs = helper.get_sorted_documents(relevant_docs, options, True)

    with st.chat_message("assistant"):
        for i,doc in enumerate(relevant_docs):
            is_expanded = True if i < 7 else False
            with st.expander(f":blue[**{doc.metadata['title'].strip().upper()}**]", expanded=is_expanded):
                st.caption(f":gray[ID: {doc.metadata['id'].strip()} Source: {doc.metadata['requirement_source'].title()}]")
                st.caption(f":gray[Score: {doc.score}]")
                st.markdown(f"*{doc.get_text().strip()}*")
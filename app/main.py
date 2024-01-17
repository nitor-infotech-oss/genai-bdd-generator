import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="Home",
                   page_icon="🤖",
                   initial_sidebar_state="expanded")

st.write("# Welcome to Test Cases Generator App!  🤖")

st.markdown("""
            This app generate the test cases in Standard BDD format using OpenAI.

            To generate test cases lick on the 'test cases' page link from the sidebar menu.

            To view all the docs (requirements) click on the 'documents' page link from the sidebar menu.
            """)

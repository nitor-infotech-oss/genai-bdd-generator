import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="Home",
                   page_icon="🤖",
                   initial_sidebar_state="expanded")

st.write("# Welcome to Test Cases Generator App!  🤖")

st.markdown("""
            This app generate the test cases in Standard BDD format using OpenAI.

            Click on the 'get_airesponse' page link from the sidebar menu.

            To view all the docs (requirements) click on the 'QueryData' page link from the sidebar menu.
            """)

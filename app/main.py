import streamlit as st
from dotenv import load_dotenv
from st_pages import Page, add_page_title, show_pages

load_dotenv()


show_pages([
            Page("main.py","Home","🏠"),
            Page("pages/documents.py","Documents"),
            Page("pages/test_cases.py","Test Cases")
          ])
add_page_title()

st.write("# Welcome to Test Cases Generator App!  🤖")

st.markdown("""
            This app generate the test cases in Standard BDD format using OpenAI.

            To generate test cases click on the 'Test Cases' page link from the sidebar menu.

            To view all the docs (requirements) click on the 'Documents' page link from the sidebar menu.
            """)

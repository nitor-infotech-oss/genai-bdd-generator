from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from services.document import DocumentHelper
from services.ai_model import get_llm_response_with_temperature, get_gemai_response
from constants import new_prompt_template

col1,col2,col3 = st.columns([0.4,0.2,0.4])
with col1:
    display_gemini_results = st.toggle(label="Display Gemini Results too")
with col3:
    is_btn_toggled = st.toggle(label="Display old requirements")

new_requirement = st.text_area(label="New requirements",
                                    placeholder='type or paste new requirements here')
new_requirement_docs = new_requirement.strip() if new_requirement else ''

old_requirement_docs = None
if is_btn_toggled:
    old_requirements = ''
    if new_requirement_docs != '':
        helper = DocumentHelper()
        relevant_docs = helper.get_relevant_docs(new_requirement_docs)
        old_requirements = '\n\n'.join([f"{doc.page_content.strip()}" for doc in relevant_docs])

    with st.expander(f"Earlier Requirements", expanded=False):
        old_requirement_docs = st.text_area(label="Old requirements",
                disabled=True, height=500, value= old_requirements if is_btn_toggled == True else "")


is_btn_clicked = st.button(label="Get Test Cases",
                           disabled= new_requirement_docs == '',
                           help='To get test cases first enter new requirements' 
                                    if new_requirement_docs =='' 
                                    else 'Click button to generate test cases')


if new_requirement_docs and is_btn_clicked :
    with st.status('Preparing request...', expanded=False, state='running') as s:
        s.update(label = "Generating Test cases please wait...")
        _prompt = new_prompt_template % (
                            old_requirement_docs, new_requirement_docs)
        print(_prompt)
        if display_gemini_results:
            gemini_response = get_gemai_response(_prompt)

        openai_response = get_llm_response_with_temperature(_prompt)
        openai_response = openai_response.replace("```","")

        s.update(label = "Request Completed", expanded=True, state='complete')
        st.subheader(":rainbow[OpenAI- GPT-3.5]")
        st.markdown(openai_response)
        if display_gemini_results:
            st.markdown('-'*10)
            st.subheader(":rainbow[Gemini-pro]")
            st.markdown(gemini_response)

        

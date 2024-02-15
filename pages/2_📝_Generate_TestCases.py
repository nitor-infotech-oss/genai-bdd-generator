from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from services.document import DocumentHelper
from services.ai_model import get_llm_response, get_gemai_response
from constants import prompt_template

col1,col2,col3 = st.columns([0.3,0.3,0.4])
with col3:
    is_btn_toggled = st.toggle(label="Display old requirements")

new_requirement = st.text_area(label="New requirements",
                                    placeholder='type or paste new requirements here')
new_requirement_docs = new_requirement.strip() if new_requirement else ''

old_requirement_docs = ''
if is_btn_toggled:
    old_requirements = ''
    if new_requirement_docs != '':
        helper = DocumentHelper()
        relevant_docs = helper.get_relevant_docs(new_requirement_docs)
        old_requirements = '\n\n'.join([f"- {doc}" for doc in relevant_docs])

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
        # messages =[]
        # messages.append({"role": "user", "content": prompt_template})
        # response = chat(messages) # Chat with Ollama Locally

        gemini_response = get_gemai_response(prompt_template % (
                            old_requirement_docs, new_requirement_docs))
        openai_response = get_llm_response(prompt_template % (
                            old_requirement_docs, new_requirement_docs))
        s.update(label = "Test Cases Generated", expanded=True, state='complete')
        
        print(gemini_response)
        print(openai_response)
        st.subheader(":rainbow[Gemini-pro]")
        st.markdown(gemini_response)
        st.markdown('-'*10)
        st.subheader(":rainbow[OpenAI- gpt-3.5]")
        st.markdown(openai_response)
        

from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from llm.docs_retriever import get_docs
import openai


def get_response(prompt,model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(messages=messages,
                                            model=model,
                                            temperature=0)
    return response.choices[0].message["content"]


new_requirement_docs = st.text_area(label="new requirements",
                                    placeholder='type or paste new requirements here')

relevant_docs = []
earlier_requirements = ''


if new_requirement_docs.strip() != '':
    relevant_docs = get_docs(new_requirement_docs)
    for i,doc in enumerate(relevant_docs):
        earlier_requirements = earlier_requirements + '- '+ str(doc) +"\n\n"
else:
    earlier_requirements = ''


is_btn_toggled = st.toggle(label="Switch button ON, if you don't want to give earlier requirements")


earlier_requirement_docs = st.text_area(label="Earlier requirements",
                                        disabled=True,
                                        value= '' if is_btn_toggled == True else earlier_requirements,
                                        height=500)



prompt_template=f"""
You are an expert test case generator and your task is to generate test cases based on the given earlier and new requirements for software development.
Earlier and new requirements are provided below in tripple backticks.

Carefully analyze both the earlier and new requirements and generate test cases for the "new requirements" ONLY.

Make sure to follow instructions given below for generating test cases:

1. If any short form is used in the requirements content, first check if the long form is provided. Do not guess the long form. If the long form is not provided, display a message requesting the long form for that particular short form.
2. Identify any dependencies of the new requirements on the functionality introduced in the earlier requirements. Take note of these dependencies.
3. Include test cases that cover the interaction between the earlier and new requirements to ensure overall functionality is validated.
4. Thoroughly review the given earlier and new requirements, paying close attention to any modifications or additions that have been introduced.
5. Carefully analyze the role or the action owner mentioned in the requirements. Do not make assumptions; use the information provided.
6. In case of conflicts or contradictions between the earlier and new requirements, prioritize the new requirements and generate test cases accordingly.
7. Must Ensure that the test cases also handle invalid or incomplete data inputs.
8. If any one of the earlier and new requirements are not provide, consider the provided docs and accordingly generate test cases.
9. Do not include documents from the earlier requirements that are irrelevant in both contextual and functional aspects when generating test cases for the new requirements.
10. Organize the generated test cases in a clear, concise, and logical manner.
11. Take your time to thoroughly understand all the requirements, think step by step before generating the test cases.

Provide your response in the standard BDD (Behavior Driven Development) format. The key elements of test cases should be shown in bold format.
e.g. **Scenario 1: Title**\n
            - **context**
            - **actions**
            - (if needed further actions) 
            - **outcomes**  



Earlier Requirements:
```{earlier_requirement_docs}```

New Requirements:
```{new_requirement_docs }```

Ensure that all the scenarios mentioned in the "new requirements" are covered in the test cases.
"""  


is_btn_clicked = st.button(label="Get Test Cases",
                         disabled= True if new_requirement_docs.strip() == ''  else False,
                         help='To get test cases first enter new requirements' if new_requirement_docs =='' 
                                                                               else 'Click button to generate test cases')


if (earlier_requirement_docs or new_requirement_docs) and is_btn_clicked :
    with st.status('Preparing request...',
                    expanded=False,
                    state='running') as s:
        s.update(label = "Generating Test cases please wait...")
        response = get_response(prompt_template)
        s.update(label = "Done",
                 expanded=True,
                 state='complete')
        st.markdown(response)


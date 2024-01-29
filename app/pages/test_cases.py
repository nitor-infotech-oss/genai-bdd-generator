from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from llm.docs_retriever import get_docs
import openai
import json
import requests
from openai import OpenAI

def get_response(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def chat(messages):
    """ Chat with Ollama Locally """
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": "llama2", "messages": messages, "stream": True},
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
        if body.get("done", False):
            message["content"] = output
            return message


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

1. If you encountered any short form in the requirements context provided to you, first check if the long form is provided or not in the information. 
   Do not make assumptions;use the information provided.
2. Avoid generating test cases. Focus on providing the message 'Please provide full form' if the long form is not provided.
3. Identify any dependencies of the new requirements on the functionality introduced in the earlier requirements. Take note of these dependencies.
4. Include test cases that cover the interaction between the earlier and new requirements to ensure overall functionality is validated.
5. Thoroughly review the given earlier and new requirements, paying close attention to any modifications or additions that have been introduced.
6. Carefully analyze the role or the action owner mentioned in the requirements. Do not make assumptions; use the information provided.
7. In case of conflicts or contradictions between the earlier and new requirements, prioritize the new requirements and generate test cases accordingly.
8. Must Ensure that the test cases also handle invalid or incomplete data inputs.
9. Also must pay close attention to metadata of the requirements and sagregate the test cases based on tag.
10. If any one of the earlier and new requirements are not provided, consider the provided docs and accordingly generate test cases.
11. MUST include the pre-requisite from earlier requirements in test cases i.e. overall flow starting from login in each test cases.
12. Do not include documents from the earlier requirements that are irrelevant in both contextual and functional aspects when generating test cases for the new requirements.
13. Organize the generated test cases in a clear, concise, and logical manner.
14. Take your time to thoroughly understand all the requirements, think step by step before generating the test cases. MUST include each step
    right from login of user and based on role how user should navigate (each step) in details.
    
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
        # messages =[]
        # messages.append({"role": "user", "content": prompt_template})
        # response = chat(messages) # Chat with Ollama Locally
        response = get_response(prompt_template)
        s.update(label = "Done",
                 expanded=True,
                 state='complete')
        st.markdown(response)


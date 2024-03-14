from dotenv import load_dotenv
load_dotenv()

import json
import requests
import os
import time
from openai import OpenAI
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# def generate_full_form_prompt(text):
#     # Construct a prompt asking the user for full forms
#     prompt = f"Given the text:\n{text}\n\nPlease provide the full forms for any abbreviations or short forms mentioned above:"
#     client = OpenAI()
#     # Call OpenAI API with the generated prompt
#     response = client.chat.completions.create(
#         engine="text-davinci-003",
#         prompt=prompt,
#         temperature=0.7,
#         max_tokens=100
#     )

#     # Extract the generated message
#     user_message = response['choices'][0]['text'].strip()

#     return user_message

def get_llm_response(prompt, delay=False):
    client = OpenAI()
    if delay:
        time.sleep(20)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response)
    return response.choices[0].message.content.strip()

def get_llm_response_with_temperature(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # gpt-4-0125-preview
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}    
        ]
    )
    print(response)
    return response.choices[0].message.content.strip()

def get_gemai_response(prompt):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    # model = genai.GenerativeModel(model_name = "gemini-pro")
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    # return model.generate_content(prompt).text
    return model.invoke(prompt).content


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


from dotenv import load_dotenv
load_dotenv()

import json
import requests
import os
import time
from openai import OpenAI
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm_response(prompt, delay=False):
    client = OpenAI()
    if delay:
        time.sleep(20)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
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


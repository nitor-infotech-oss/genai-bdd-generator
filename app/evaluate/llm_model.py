from dotenv import load_dotenv

load_dotenv()
import streamlit as st
from openai import OpenAI
import time
from langchain.llms import Ollama
import time

client = OpenAI()

def get_response(prompt):
    time.sleep(20)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

from dotenv import load_dotenv
load_dotenv()

import os

from datasets import Dataset
import google.generativeai as genai
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLM
from langchain_google_genai import ChatGoogleGenerativeAI

from services.ai_model import get_llm_response
from services.document import DocumentHelper
from constants import prompt_template, questions

# from langchain.llms import Ollama
# from langchain.llms import OpenAI
# from langchain_openai import OpenAI
# from langchain.chat_models import ChatOpenAI


# llm = ChatOpenAI(model_name="gpt-3.5-turbo")
# llm = Ollama(model="llama2", temperature=0)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# llm = genai.GenerativeModel(model_name = "gemini-pro")
llm = ChatGoogleGenerativeAI(model="gemini-pro")
vllm = LangchainLLM(llm=llm)
faithfulness.llm = vllm
answer_relevancy.llm = vllm
context_precision.llm = vllm

answers, contexts, prompts = [], [], []

helper = DocumentHelper()
for query in questions:
    earlier_docs = helper.get_relevant_docs(query)
    prompt = prompt_template % (query, earlier_docs)
    prompts.append(prompt)
    answers.append(get_llm_response(prompt=prompt))
    contexts.append([doc.page_content for doc in earlier_docs])

# # To dict
data = {
        "question": prompts,
        "answer": answers,
        "contexts": contexts,
     }
data2 = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
     }


# Convert dict to dataset
dataset = Dataset.from_dict(data)
dataset2 = Dataset.from_dict(data2)

firstresult = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
            ])

secondresult = evaluate(
    dataset = dataset2, 
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
            ])

print("first...")
print(firstresult)
print("second...")
print(secondresult)



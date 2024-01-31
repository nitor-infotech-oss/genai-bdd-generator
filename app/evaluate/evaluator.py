from dotenv import load_dotenv

load_dotenv()
from langchain_together import Together
from datasets import Dataset, Features, Sequence, Value,DatasetDict
from querries import questions
from llm_model import get_response
from doc_retriever import get_docs
from prompt import get_prompt
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
)
from ragas.llms import LangchainLLM
from langchain.llms import Ollama
# from langchain.llms import OpenAI
# from langchain_openai import OpenAI
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-3.5-turbo")
# llm = Ollama(model="llama2", temperature=0)
vllm = LangchainLLM(llm=llm)
faithfulness.llm = vllm
answer_relevancy.llm = vllm
context_precision.llm = vllm

answers = []
contexts =[]
prompts = []

for query in questions:
    earlier_docs = get_docs(query)
    new_docs = query
    prompt = get_prompt(new_requirements=new_docs, earlier_requirements=earlier_docs)
    prompts.append(prompt)
    answers.append(get_response(prompt=prompt))
    contexts.append([doc.page_content for doc in get_docs(query)])

# # To dict
data = {
        "question": prompts,
        "answer": answers,
        "contexts": contexts,
     }

# Convert dict to dataset
dataset = Dataset.from_dict(data)

result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
            ])

df = result.to_pandas()
print(result)


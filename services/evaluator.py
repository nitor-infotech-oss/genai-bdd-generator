from dotenv import load_dotenv

load_dotenv()
from langchain_openai import ChatOpenAI
from datasets import Dataset
from ragas import evaluate
# from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.metrics import (faithfulness, answer_relevancy,
            context_precision, context_relevancy, 
            context_recall, answer_similarity, 
            answer_correctness)
from ragas.llms import LangchainLLM

from .ai_model import get_llm_response
from .document import DocumentHelper
from constants import prompt_template, questions

llm = ChatOpenAI(model_name="gpt-3.5-turbo")
# llm = Ollama(model="llama2", temperature=0)
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

data = {"question": prompts, "answer": answers}
if contexts:
    data["contexts"] = contexts

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_relevancy
            ])

print("Result is...")
print(result)


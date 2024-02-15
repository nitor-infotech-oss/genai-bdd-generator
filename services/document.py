from dotenv import load_dotenv
load_dotenv()

import re
import os

from sentence_transformers import SentenceTransformer, util

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql
from langchain.docstore.document import Document
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

from constants import AZURE_QUERY, SIMILARITY_THRESHOLD


class DocumentHelper:

    def remove_html_tags(self, text):
        """
            This function removes html tags from a string since azure docs are comming with html tags
        """
        clean = re.compile('<.*?>|&nbsp;|\n|\t')
        return re.sub(clean, '', text)


    def prepare_azure_docs(self):
        """
            This function prepares the work items, in documents format, to store into chromadb as 
            parent documents
            
            e.g. Document(page_content={work item 1 content here},
                        metadata={"title": work_item1.title...}),
            Document(page_content={work item 2 content here},
                        metadata={"title": work_item2.title...})
        """
        azure_docs =[]
        for work_item in self.get_azure_data():
            if 'System.Description' in work_item.fields.keys():
                page_content = self.remove_html_tags(work_item.fields['System.Description'])
                doc = Document(page_content= page_content,
                            metadata={'title': work_item.fields['System.Title'], 
                                        "id":str(work_item.id),
                                        "tag":work_item.fields["System.Tags"] if "System.Tags" in work_item.fields.keys()
                                                                else ''
                                        })
                azure_docs.append(doc)
        return azure_docs


    def get_azure_data(self):
        """
            Access azure devops work items and get all work items based on Wiql query provided
        """
        personal_access_token = os.getenv('personal_access_token')
        organization_url = os.getenv('organization_url')

        # Create a connection to the org
        credentials = BasicAuthentication(os.getenv('email'), personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)

        # Get a client (the "core" client provides access to projects, teams, etc)
        work_client = connection.clients.get_work_item_tracking_client()
        wiql = Wiql(query=AZURE_QUERY)
        
        wiql_results = work_client.query_by_wiql(wiql, top=60).work_items
        if wiql_results:
            work_items = (work_client.get_work_item(int(res.id)) for res in wiql_results)
            return [item for item in work_items]


    def get_confluence_data(self):
        """
            This function will access/retrieve confluence docs 
            (spaces and pages)
        """
        loader = ConfluenceLoader(url=os.getenv('confluence_url'), 
                    username=os.getenv('email'), api_key=os.getenv('api_key')) 
        documents = loader.load(space_key=os.getenv('space_key'), limit=50)
        docs =[
                Document(page_content= doc.page_content,
                            metadata={
                                    'title': doc.metadata['title'], 
                                    'id':doc.metadata['id']
                                    } 
                    ) for doc in documents
        ]
        return docs
    

    def get_relevant_docs(self, question):
        """
            Combine both the docs retrieved from confluence and azure.
            Store them into Chromadb.
            All the docs are stored as a parent documents (key value pair) using LocalStorage into local disk.
            These docs are divided into chunks and these chunks are embedded and stored into Chromadb using OpenAIEmbeding().
            When we query Chromadb using the question parameters it will first fetch all relevant child chunks from DB and
            then fetch the parent docs using those chunks.
        """
        persistDirectory_parent = os.getenv('persistDirectory_parent')
        persistDirectory_child = os.getenv('persistDirectory_child')
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        fs = LocalFileStore(persistDirectory_parent)
        store = create_kv_docstore(fs)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
        vectorstore = Chroma(collection_name="split_parents", 
                            embedding_function=embedding_function, 
                            persist_directory=persistDirectory_child)
        retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                            docstore=store,
                                            child_splitter=child_splitter,
                                            parent_splitter=parent_splitter,
                                            search_type="mmr",
                                            search_kwargs={"k": 30} )
        relevant_docs = retriever.get_relevant_documents(question)
        return relevant_docs


    def remove_duplicates_docs(self, docs):
        # Load a pre-trained BERT model for sentence embeddings
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 
        # Extract document content and titles
        doc_contents = [doc.page_content for doc in docs]
        # Compute embeddings for document content
        doc_embeddings = model.encode(doc_contents)
        # Calculate cosine similarity matrix
        similarity_matrix = util.pytorch_cos_sim(doc_embeddings, doc_embeddings)
        # Identify redundant documents
        redundant_indices = []

        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity_matrix[i, j] > SIMILARITY_THRESHOLD:
                    redundant_indices.append(j)
        
        # Remove redundant documents
        filtered_docs = [doc for i, doc in enumerate(docs) if i not in redundant_indices]
        return filtered_docs





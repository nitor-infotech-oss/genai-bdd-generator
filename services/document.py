from dotenv import load_dotenv
load_dotenv()

import re
import os
import chromadb
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
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.core import Document as LlamaDocument
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo
from llama_index.core.node_parser import SentenceSplitter

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
                _metadata = {'title': work_item.fields['System.Title'], 
                                "id":str(work_item.id),
                                "tag":work_item.fields["System.Tags"] if "System.Tags" in work_item.fields.keys()
                                                        else '',
                                "requirement_source": "azure",
                                "score": 0
                        }
                doc = Document(page_content= page_content, metadata=_metadata)
                azure_docs.append(doc)
        return azure_docs
    
    def prepare_azure_llama_docs(self):
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
                _metadata = {'title': work_item.fields['System.Title'], 
                                "id":str(work_item.id),
                                "tag":work_item.fields["System.Tags"] if "System.Tags" in work_item.fields.keys()
                                                        else '',
                                "requirement_source": "azure",
                                "score": 0
                        }

                doc = TextNode(text=page_content, metadata=_metadata,
                            excluded_embed_metadata_keys=[
                                'id', 'score', 'requirement_source']
                        )
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
                                    "requirement_source": "confluence",
                                    'title': doc.metadata['title'], 
                                    'id':doc.metadata['id'],
                                    'score': 0
                                    } 
                    ) for doc in documents
        ]
        return docs
    
    def get_confluence_llama_data(self):
        """
            This function will access/retrieve confluence docs 
            (spaces and pages)
        """
        loader = ConfluenceLoader(url=os.getenv('confluence_url'), 
                    username=os.getenv('email'), api_key=os.getenv('api_key')) 
        documents = loader.load(space_key=os.getenv('space_key'), limit=50)
        docs =[
                TextNode(text= doc.page_content,
                    metadata={
                            "requirement_source": "confluence",
                            'title': doc.metadata['title'], 
                            'id':doc.metadata['id'],
                            'score': 0
                            },
                    excluded_embed_metadata_keys=['id', 'score', 'requirement_source']
                    ) for doc in documents
        ]
        return docs
    

    def get_relevant_docs(self, question):
        """
            Combine both the docs retrieved from confluence and azure.
            Store them into Chromadb.
            All the docs are stored as a parent documents (key value pair) using LocalStorage into local disk.
            These docs are divided into chunks and these chunks are embedded and stored into Chromadb using SentenceTransformerEmbeddings().
            When we query Chromadb using the question parameters it will first fetch all relevant child chunks from DB and
            then fetch the parent docs using those chunks.
        """
        PERSIST_PARENTDIR = os.getenv('PERSIST_PARENTDIR')
        PERSIST_CHILDDIR = os.getenv('PERSIST_CHILDDIR')
        name_of_collection = os.getenv('COLLECTION_NAME')
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        fs = LocalFileStore(PERSIST_PARENTDIR)
        store = create_kv_docstore(fs)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
        vectorstore = Chroma(collection_name=name_of_collection, collection_metadata={"hnsw:space": "cosine"},
                            embedding_function=embedding_function, persist_directory=PERSIST_CHILDDIR)
        retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                            docstore=store,
                                            child_splitter=child_splitter,
                                            parent_splitter=parent_splitter,
                                            search_type="mmr", search_kwargs={'k':30, 'fetch_k':10}, #k 30
                                            lambda_mult = 0.2)

        # Get relevance score
        relevance_score_chunks = retriever.vectorstore.similarity_search_with_relevance_scores(question, k=30)
        temp = { e[0].metadata["title"]: e[1] for e in relevance_score_chunks }
        relevance_threshold = round(sum(temp.values())/len(temp),2)
        relevance_score_card = { int(e[0].metadata["id"]): {**e[0].metadata, 'score': e[1]} 
                                    for e in relevance_score_chunks if e[1] > relevance_threshold
                            }
        relevant_docs = []
        # if relevance_score_card:
        _docs = retriever.get_relevant_documents(question)
        for doc in _docs:
            _id = int(doc.metadata['id'])
            if _id in relevance_score_card:
                    doc.metadata['score'] = relevance_score_card[_id]['score']
            relevant_docs.append(doc)
            # if _id in relevance_score_card and relevance_score_card[_id]['score']<= relevance_threshold:
            #     continue
            # else:
            #     if _id in relevance_score_card:
            #         doc.metadata['score'] = relevance_score_card[_id]['score']
            #     relevant_docs.append(doc)

        return relevant_docs
    
    def get_relevant_index_docs(self, question):
        """
            Combine both the docs retrieved from confluence and azure.
            Store them into Chromadb.
            All the docs are stored as a parent documents (key value pair) using LocalStorage into local disk.
            These docs are divided into chunks and these chunks are embedded and stored into Chromadb using OpenAIEmbeding().
            When we query Chromadb using the question parameters it will first fetch all relevant child chunks from DB and
            then fetch the parent docs using those chunks.
        """
        index_directory = os.getenv('PERSIS_INDEX_DIR')
        helper = DocumentHelper()
        if not os.path.exists(index_directory):
            docs = helper.get_confluence_llama_data()
            docs.extend(helper.prepare_azure_llama_docs())
            nodes = helper.remove_duplicates_llama_docs(docs)
            index = VectorStoreIndex(nodes,
                    transformations=[
                        SentenceSplitter(chunk_size=2000, chunk_overlap=50)])
            # store it for later
            index.storage_context.persist(persist_dir=index_directory)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=index_directory)
            index = load_index_from_storage(storage_context)
        
        vector_store_info = VectorStoreInfo(
            content_info="Requirements of Stories",
            metadata_info=[
                MetadataInfo(
                    name="title",
                    type="str",
                    description=(
                        "Title of the requirement"
                    ),
                ),
            ],
        )

        retriever = VectorIndexAutoRetriever(
            index, vector_store_info=vector_store_info,
            similarity_top_k=12
        )

        relevant_docs = retriever.retrieve(question)
        relevance_threshold = sum([n.score for n in relevant_docs])/len(relevant_docs)
        return relevant_docs
    
    def get_relevant_llama_docs(self, question):
        """
            Combine both the docs retrieved from confluence and azure.
            Store them into Chromadb.
            All the docs are stored as a parent documents (key value pair) using LocalStorage into local disk.
            These docs are divided into chunks and these chunks are embedded and stored into Chromadb using OpenAIEmbeding().
            When we query Chromadb using the question parameters it will first fetch all relevant child chunks from DB and
            then fetch the parent docs using those chunks.
        """
        PERSIST_PARENTDIR = os.getenv('PERSIST_PARENTDIR')
        PERSIST_CHILDDIR = os.getenv('PERSIST_CHILDDIR')
        name_of_collection = os.getenv('COLLECTION_NAME')
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        fs = LocalFileStore(PERSIST_PARENTDIR)
        store = create_kv_docstore(fs)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400,chunk_overlap=20)
        vectorstore = Chroma(collection_name=name_of_collection, collection_metadata={"hnsw:space": "cosine"},
                            embedding_function=embedding_function, persist_directory=PERSIST_CHILDDIR)
        retriever = ParentDocumentRetriever(vectorstore=vectorstore,
                                            docstore=store,
                                            child_splitter=child_splitter,
                                            parent_splitter=parent_splitter,
                                            search_type="mmr", search_kwargs={'k':30, 'fetch_k':10}, #k 30
                                            lambda_mult = 0.2)

        # Get relevance score
        relevance_score_chunks = retriever.vectorstore.similarity_search_with_relevance_scores(question, k=30)
        temp = { e[0].metadata["title"]: e[1] for e in relevance_score_chunks }
        print("relevance_score_chunks:", temp)
        relevance_threshold = round(sum(temp.values())/len(temp),2)
        print('relevance_threshold',relevance_threshold)
        relevance_score_card = { int(e[0].metadata["id"]): {**e[0].metadata, 'score': e[1]} 
                                    for e in relevance_score_chunks if e[1] > relevance_threshold
                            }
        print("relevance_score_card:",relevance_score_card)
        relevant_docs = []
        # if relevance_score_card:
        _docs = retriever.get_relevant_documents(question)
        for doc in _docs:
            _id = int(doc.metadata['id'])
            if _id in relevance_score_card:
                    doc.metadata['score'] = relevance_score_card[_id]['score']
            relevant_docs.append(doc)
            # if _id in relevance_score_card and relevance_score_card[_id]['score']<= relevance_threshold:
            #     continue
            # else:
            #     if _id in relevance_score_card:
            #         doc.metadata['score'] = relevance_score_card[_id]['score']
            #     relevant_docs.append(doc)

        return relevant_docs
    
    def get_sorted_documents(self, docs, sort_by, sort_desc):
        key_mapping = {"Relevance": "score", "Title": "title"}
        sort_by = sort_by[0]
        sorted_list = sorted(docs, key=lambda d: d.metadata.get(key_mapping.get(sort_by), 0), reverse=sort_desc)
        return sorted_list

    def remove_duplicates_docs(self, docs):
        # Load a pre-trained BERT model for sentence embeddings
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 
        # Compute embeddings for document content
        doc_embeddings = model.encode([doc.page_content for doc in docs])
        # Calculate cosine similarity matrix
        similarity_matrix = util.pytorch_cos_sim(doc_embeddings, doc_embeddings)
        # Identify redundant documents ######  check if sentence_transformers.util.semantic_search can be used
        redundant_indices = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if j not in redundant_indices and similarity_matrix[i, j] > SIMILARITY_THRESHOLD:
                    redundant_indices.add(j)
        
        # Remove redundant documents
        return [doc for i, doc in enumerate(docs) if ((i not in redundant_indices) and doc.page_content != '')]

    def remove_duplicates_llama_docs(self, docs):
        # Load a pre-trained BERT model for sentence embeddings
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 
        # Compute embeddings for document content
        doc_embeddings = model.encode([doc.get_text() for doc in docs])
        # Calculate cosine similarity matrix
        similarity_matrix = util.pytorch_cos_sim(doc_embeddings, doc_embeddings)
        # Identify redundant documents ######  check if sentence_transformers.util.semantic_search can be used
        redundant_indices = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if j not in redundant_indices and similarity_matrix[i, j] > SIMILARITY_THRESHOLD:
                    redundant_indices.add(j)

        # Remove redundant documents
        return [doc for i, doc in enumerate(docs) if ((i not in redundant_indices) and doc.get_text() != '')]





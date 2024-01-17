from langchain.document_loaders import ConfluenceLoader
from langchain.docstore.document import Document
import os


def get_all_spaces_docs():
    """this function will access/retrieve confluence docs (spaces and pages)"""
    loader = ConfluenceLoader(url=os.getenv('confluence_url'), 
                              username=os.getenv('email'), 
                              api_key=os.getenv('api_key'))
    
    documents = loader.load(space_key=os.getenv('space_key'), 
                            limit=50)

    docs =[]
    for doc in documents:
        docs.append(Document(page_content= doc.page_content,
                             metadata={
                                       'title': doc.metadata['title'], 
                                       'id':doc.metadata['id']
                                       } 
                            )
                    )
    return docs
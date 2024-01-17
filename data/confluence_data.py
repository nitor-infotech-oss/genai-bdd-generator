from config import api_key
from langchain.document_loaders import ConfluenceLoader
from langchain.docstore.document import Document
import os


def get_all_spaces_docs():
    """this function will access/retrieve confluence docs (spaces and pages)"""

    loader = ConfluenceLoader(url="https://mysite-trial-97.atlassian.net/wiki", 
                              username="pushpak.nemade@nitorinfotech.com", 
                              api_key=api_key)
    
    documents = loader.load(space_key="~5570588dddbe0b02de4e8088a67297b691e197", 
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
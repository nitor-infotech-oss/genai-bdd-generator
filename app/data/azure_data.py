from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql
from langchain.docstore.document import Document
import re
import os


def remove_html_tags(text):
    """Remove html tags from a string since azure docs are comming with html tags"""
    clean = re.compile('<.*?>|&nbsp;|\n|\t')
    return re.sub(clean, '', text)


def get_azure_work_items():
    """Access azure devops work items and get all work items based on Wiql query provided"""
    personal_access_token = os.getenv('personal_access_token')
    organization_url = os.getenv('organization_url')

    # Create a connection to the org
    credentials = BasicAuthentication(os.getenv('email'), personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Get a client (the "core" client provides access to projects, teams, etc)
    work_client = connection.clients.get_work_item_tracking_client()

    wiql = Wiql(query="""
                select [System.Id],
                       [System.WorkItemType],
                       [System.Title],
                       [System.AreaPath],
                       [System.State],
                       [System.Description]
                from WorkItems
                where [System.WorkItemType] = 'User Story' 
                and [System.AreaPath] = 'BIRA91 - Dooze App'
                and [System.TeamProject] = 'BIRA91 - Dooze App'
                order by [System.ChangedDate] desc""")
    
    wiql_results = work_client.query_by_wiql(wiql, top=60).work_items

    work_items_list =[]

    if wiql_results:
        work_items = (work_client.get_work_item(int(res.id)) for res in wiql_results)

        for work_item in work_items:
            work_items_list.append(work_item)

        return work_items_list


def prepare_azure_docs():
    """This fun will prepare the work items, in documents format, to store into chromadb as 
    parent documents
    
    e.g. Document(page_content={work item 1 content here},
                  metadata={"title": work_item1.title...}),
    Document(page_content={work item 2 content here},
                  metadata={"title": work_item2.title...})
    """

    work_items = get_azure_work_items()
    azure_docs =[]
    
    for work_item in work_items:
        if 'System.Description' in work_item.fields.keys():
            page_content = remove_html_tags(work_item.fields['System.Description'])
            doc = Document(page_content= page_content,
                           metadata={'title': work_item.fields['System.Title'], "id":str(work_item.id)})
            azure_docs.append(doc)
    return azure_docs
    
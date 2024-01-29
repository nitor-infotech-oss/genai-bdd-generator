# ai-bdd-generator
Implementation of GenAI based BDD Tests Generator

# python version
python version should be >= 3.9 to install all dependencies

# need to create .env file inside 'ai-bdd-generator/app' folder with following environment variables to run app
OPENAI_API_KEY = "your openai_api_key"
persistDirectory_parent = "path to store parent docs into docstore"
persistDirectory_child = "path to store child chunks into vectorstore"
api_key = "Confluence api key to access confluence pages"
personal_access_token = "personal access token to access azure work items" 
organization_url = "url of your azure board organization to get work items"
email="your email for authentication to azure and confluence data"
confluence_url="your confluence url" # e.g. "https://yoursite.atlassian.net/wiki"
space_key= "your confluence spaces key"

# To install all packages 
pip install -r requirements.txt

# To run the app on browser go to app folder and run using
streamlit run main.py






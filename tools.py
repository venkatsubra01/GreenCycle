#region imports
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain.tools import BaseTool, StructuredTool, tool  # noqa: F401
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

#region keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID") 
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY") 
#endregion

#region Google search tool
search = GoogleSearchAPIWrapper()
def search_with_links(query: str):
    # Assuming `search` is a module that provides the `run` method to perform the search
    results = search.results(query, 5)
    
    # Parse results to extract URLs (assuming results is a list of dictionaries)
    links = []
    for result in results:
        link = result.get('link')  # Extracting the 'link' field from each result
        if link:
            links.append({
                'title': result.get('title'),
                'snippet': result.get('snippet'),
                'link': link
            })
    
    return links

search_tool = Tool(
    name="google_search",
    description="Search Google for recent results and gets links as well.",
    func=search_with_links,
)
#endregion

#region Website scraper tool
def visit_website(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract meaningful content
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        headers = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
        content = ' '.join(headers + paragraphs)
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        content = "Content could not be extracted"
        print(f"Error retrieving the page: {e}")
    return str(content)

website_scrape = StructuredTool.from_function(
    func=visit_website,
    name="website_scrape",
    description="Scrape and extract the content of a website.",
)
#endregion
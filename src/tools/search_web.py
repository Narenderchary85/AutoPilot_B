import os
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup

class SearchWebInput(BaseModel):
    query: str = Field(description="The search query string")

@tool("SearchWeb", args_schema=SearchWebInput)
@traceable(run_type="tool", name="SearchWeb")
def search_web(query: str):
    """
    Search Wikipedia (no API key).
    """
    search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    response = requests.get(search_url, timeout=10)

    if response.status_code != 200:
        return "No results found."

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")

    content = ""
    for p in paragraphs[:5]:
        content += p.get_text() + "\n"

    return content.strip() or "No readable content."
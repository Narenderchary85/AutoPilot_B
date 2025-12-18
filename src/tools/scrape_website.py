import re
import html2text
import requests
from bs4 import BeautifulSoup
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class ScrapeWebsiteInput(BaseModel):
    url: str = Field(description="The URL of the website to scrape.")

@tool("ScrapeWebsite", args_schema=ScrapeWebsiteInput)
@traceable(run_type="tool", name="ScrapeWebsite")
def scrape_website_to_markdown(url: str) -> str:
    """
    Fetch Google Calendar events between a start date and end date
    for the authenticated user.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate"
    }


    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")


    soup = BeautifulSoup(response.text, "html.parser")
    html_content = soup.prettify() 

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = True
    markdown_content = h.handle(html_content)

    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
    markdown_content = markdown_content.strip()

    return markdown_content
import re
import requests
import html2text
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langsmith import traceable


class ScrapeWebsiteInput(BaseModel):
    url: str = Field(description="The URL of the website to scrape")


@tool("scrape_website", args_schema=ScrapeWebsiteInput)
@traceable(run_type="tool", name="ScrapeWebsite")
def scrape_website(url: str) -> str:
    """
    Scrape readable text from a website and convert it to Markdown.
    Works best for static HTML pages.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        return f"Request failed: {e}"

    if response.status_code != 200:
        return f"Failed to fetch URL. Status code: {response.status_code}"

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # Extract meaningful text
    text = soup.get_text(separator="\n")

    # Clean whitespace
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = text.strip()

    if not text or len(text) < 200:
        return "Scraping blocked or page content not accessible."

    # Convert to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = True
    h.body_width = 0

    markdown = h.handle(text)

    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    return markdown

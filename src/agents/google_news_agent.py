import feedparser
from src.core.llm import PerplexityLLM
from src.agents.base import Agent
from urllib.parse import quote
import re

GOOGLE_NEWS_AGENT_PROMPT = """
You are the Google News Agent.

You MUST return ONLY valid JSON in this format:

{
  "action": "fetch_news",
  "data": {
    "query": "<news topic or keywords>",
    "max_results": <number of articles>
  }
}

Do NOT explain anything.
User request:
{input}
"""
def extract_clean_news(snippet):
    # Extract headline (inside <a>)
    headline_match = re.search(r'>(.*?)</a>', snippet)
    headline = headline_match.group(1).strip() if headline_match else ""

    # Extract source (inside <font>)
    source_match = re.search(r'<font.*?>(.*?)</font>', snippet)
    source = source_match.group(1).strip() if source_match else ""

    return headline, source

def format_news(articles):
    clean_articles = []

    for a in articles:
        snippet = a.get("snippet", "")

        headline, source = extract_clean_news(snippet)

        clean_articles.append({
            "headline": a.get("title", ""),
            "source": source,
            "published": a.get("published", ""),
            "summary": headline  # short clean text from snippet
        })

    return clean_articles

class GoogleNewsAgent:
    def __init__(self):
        # The LLM is only used to interpret user input and extract query
        llm = PerplexityLLM()
        self.agent = Agent(llm, GOOGLE_NEWS_AGENT_PROMPT)

    def invoke(self, message):
        response = self.agent.invoke(message)
        text = response["candidates"][0]["content"]["parts"][0]["text"]
        text = re.sub(r"```json|```", "", text).strip()
        return text
    
    def fetch_news(self, query: str, max_results: int = 5):
        """Fetch latest news articles from Google RSS."""
        encoded_query = quote(query)
        print(f"Encoded query: {encoded_query}")
        print(f"Fetching news for query: '{query}' with max results: {max_results}")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        print(f"Constructed RSS URL: {rss_url}")
        feed = feedparser.parse(rss_url)
        print(f"Feed title: {feed.feed.get('title', 'N/A')}, Total entries: {len(feed.entries)}")
        articles = []
        for entry in feed.entries[:max_results]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": getattr(entry, 'published', ''),
                "snippet": getattr(entry, 'summary', '')
            })
        print(f"Fetched {len(articles)} articles for query: '{query}'")
        print("Articles:", articles)
        formatted_articles = format_news(articles)
        print("Formatted articles:", formatted_articles)
        return formatted_articles

import feedparser
from src.core.llm import PerplexityLLM
from src.agents.base import Agent

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

class GoogleNewsAgent:
    def __init__(self):
        # The LLM is only used to interpret user input and extract query
        llm = PerplexityLLM()
        self.agent = Agent(llm, GOOGLE_NEWS_AGENT_PROMPT)

    def invoke(self, message):
        response = self.agent.invoke(message)
        return response["choices"][0]["message"]["content"]

    def fetch_news(self, query: str, max_results: int = 5):
        """Fetch latest news articles from Google RSS."""
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        articles = []
        for entry in feed.entries[:max_results]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": getattr(entry, 'published', ''),
                "snippet": getattr(entry, 'summary', '')
            })

        return articles

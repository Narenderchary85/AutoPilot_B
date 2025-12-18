import feedparser
from src.core.llm import PerplexityLLM
from src.agents.base import Agent
import json
import requests

GOOGLE_NEWS_AGENT_PROMPT = """
You are a Google News routing agent.

Your job is to analyze the user's request and decide
whether news needs to be fetched.

If the user asks for news, headlines, updates, or current events,
return ONLY valid JSON in this format:

{
  "action": "fetch_news",
  "data": {
    "query": "<clean news topic>",
    "max_results": <integer between 5 and 10>
  }
}

If the user is NOT asking for news, return ONLY:

{
  "action": "none"
}

Do NOT explain anything.
Do NOT add extra text.

User request:
{input}
"""


class GoogleNewsAgent:
    def __init__(self):
        self.llm = PerplexityLLM()
        self.agent = Agent(self.llm, GOOGLE_NEWS_AGENT_PROMPT)

    def invoke(self, message):
        """
        Wrapper so PersonalAssistant can call invoke()
        """
        return self.route(message)

    def route(self, message):
        response = self.agent.invoke(message)
        return response["choices"][0]["message"]["content"]

    def fetch_news(self, query):
        headers = {
            "Authorization": f"Bearer {self.llm.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "user", "content": f"Latest news about {query}"}
            ],
            "temperature": 0,
            "search": True
        }

        response = requests.post(self.llm.url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def search_news_with_llm(self, query: str):
        """
        Calls Perplexity / Sonar model and returns RAW LLM response
        """
        return self.agent.llm.call_perplexity_api(
            prompt=f"Latest news about {query}"
        )

    def extract_articles_from_search(self, llm_response, max_results=7):
        results = llm_response.get("search_results", [])
        articles = []

        for r in results[:max_results]:
            articles.append({
                "title": r.get("title"),
                "link": r.get("url"),
                "snippet": r.get("snippet", ""),
                "date": r.get("date", "")
            })

        return articles


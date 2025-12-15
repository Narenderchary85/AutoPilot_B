from src.agents.base import Agent
from src.core.llm import PerplexityLLM

RESEARCHER_AGENT_PROMPT = """
You are a Researcher Agent.

You MUST output only JSON.

Possible actions:
1. search_web
2. scrape_website
3. search_linkedin

Formats:

Search:
{
  "action": "search_web",
  "data": {
    "query": "<search query>"
  }
}

Scrape website:
{
  "action": "scrape_website",
  "data": {
    "url": "<website url>"
  }
}

LinkedIn:
{
  "action": "search_linkedin",
  "data": {
    "person_name": "<optional>",
    "company_name": "<company>"
  }
}

Rules:
- If user asks for news, research, info → search_web
- If user provides a URL or says scrape → scrape_website
- If user asks about a person/company LinkedIn → search_linkedin

Only JSON. No explanations.
"""

class ResearcherAgent:
    def __init__(self):
        llm = PerplexityLLM()
        self.agent = Agent(llm, RESEARCHER_AGENT_PROMPT)

    def invoke(self, message):
        response = self.agent.invoke(message)
        return response["choices"][0]["message"]["content"]


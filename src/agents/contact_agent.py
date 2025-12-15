from src.core.llm import PerplexityLLM
from src.agents.base import Agent
from src.tools.find_contact_email import find_contact_email  # your tool
import json

CONTACTS_AGENT_PROMPT = """
You are the Contacts Agent.

You MUST return ONLY valid JSON.
Do NOT explain anything.

Supported actions:

1) Find contact:
{
  "action": "find_contact_email",
  "data": {
    "name": "full name of the contact"
  }
}

Rules:
- Always return JSON only.
- Use the find_contact_email tool to get results.
- Do not include text outside JSON.

User request:
{input}
"""

class ContactsAgent:
    def __init__(self):
        llm = PerplexityLLM()
        self.agent = Agent(llm, CONTACTS_AGENT_PROMPT)

    def invoke(self, message):
        response = self.agent.invoke(message)
        return response["choices"][0]["message"]["content"]

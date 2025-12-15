import json
from src.core.llm import PerplexityLLM
from src.agents.base import Agent
from src.agents.executor import execute_action

CALENDAR_AGENT_PROMPT = """
You are a Calendar Manager Agent.

Your job is to extract event details from the user request
and return ONLY valid JSON in the following format:

{
  "action": "create_schedule",
  "data": {
    "title": "<short event title>",
    "date": "<date like today | tomorrow | 2025-01-15>",
    "time": "<time like 9 PM | 11:30 AM>",
    "description": "<optional description>"
  }
}

Rules:
- Fill values dynamically from the user message
- If date or time is missing, make a reasonable assumption
- DO NOT explain
- DO NOT add text
- ONLY return JSON
"""

class CalendarAgent:
    def __init__(self):
        llm = PerplexityLLM()
        self.agent = Agent(llm, CALENDAR_AGENT_PROMPT)

    def invoke(self, message: str):
        # 1️⃣ Call LLM
        response = self.agent.invoke(message)

        # 2️⃣ Extract ONLY the model content
        try:
            content = response["choices"][0]["message"]["content"]
        except Exception:
            return {
                "error": "Invalid LLM response format",
                "raw": response
            }

        # 3️⃣ Parse JSON
        try:
            data = json.loads(content)
        except Exception:
            return {
                "error": "LLM did not return valid JSON",
                "raw": content
            }

        # 4️⃣ Execute calendar action
        if "action" in data:
            return execute_action(content)

        return {
            "error": "No action found in response",
            "raw": data
        }

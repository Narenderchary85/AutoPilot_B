from src.core.llm import PerplexityLLM
from src.agents.base import Agent
from src.agents.email_agent import EmailAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.executor import execute_action
import json

MANAGER_PROMPT = """
You are a router.

You MUST output only JSON:
{{
  "agent": "<email_agent | calendar_agent | none>",
  "message": "<same user message>"
}}

Rules:
- If the user wants to schedule something, create an event, or set a reminder → agent = "calendar_agent"
- If the user wants to send an email, reply to an email, draft an email → agent = "email_agent"
- Otherwise → agent = "none"

Do NOT explain anything. Do NOT add text. Only return valid JSON.
"""


class PersonalAssistant:
    def __init__(self):
        llm = PerplexityLLM()

        # Router agent
        self.agent = Agent(llm, MANAGER_PROMPT)

        # Action agents
        self.email_agent = EmailAgent()
        self.calendar_agent = CalendarAgent()

    def try_execute_action(self, reply_text):
        """
        If the agent returns JSON with an action, execute it.
        Example expected:
        {
          "action": "create_event",
          "parameters": {...}
        }
        """
        try:
            data = json.loads(reply_text)
            if "action" in data:
                return execute_action(data)
        except Exception:
            pass  # Not JSON or no action

        return reply_text

    def invoke(self, message):
        """
        Main routing function.
        Sends user message → router → finds agent → executes agent.
        """

        # Router call
        router_output = self.agent.invoke(message)

        # Extract Perplexity text
        raw_text = router_output["choices"][0]["message"]["content"]

        print("\n--- ROUTER RAW TEXT ---")
        print(raw_text)
        print("-----------------------\n")

        # Parse router JSON
        try:
            router_json = json.loads(raw_text)
        except Exception:
            return {
                "error": "Router returned invalid JSON",
                "raw": raw_text
            }

        agent = router_json["agent"]
        user_message = router_json["message"]

        # Route based on agent
        if agent == "calendar_agent":
            reply = self.calendar_agent.invoke(user_message)
            return self.try_execute_action(reply)

        if agent == "email_agent":
            reply = self.email_agent.invoke(user_message)
            return self.try_execute_action(reply)

        # No agent needed
        return {
            "response": "No agent required",
            "raw": router_json
        }

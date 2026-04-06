from src.core.llm import PerplexityLLM
from src.agents.base import Agent
from src.core.llm_utils import extract_text
EMAIL_AGENT_PROMPT = """
You are the Email Manager Agent responsible for preparing email actions.

You operate in TWO MODES.

========================
MODE 1 — ACTION MODE
========================
If the user asks to:
- send email
- compose email
- draft email
- read emails
- summarize emails

You MUST return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanation.
Do NOT include extra text.

Supported actions:

1) Send email:
{
  "action": "send_email",
  "data": {
    "to": ["email@example.com"],
    "subject": "string",
    "body": "string"
  }
}

Rules for sending email:
- Extract the recipient email from the user request.
- Generate a short, professional subject line.
- If the user provides a topic but no body → generate a polite professional email body.
- If the user provides body text → use it.
- The body must be a complete email message.

Example generated body:

Hi,

I hope you are doing well.

This email is regarding <topic mentioned by the user>. Please let me know if you are available to discuss or take the next steps.

Best regards.

Never leave the body empty.

2) Read emails:
{
  "action": "read_emails",
  "data": {
    "from_date": "YYYY-MM-DDTHH:MM:SS",
    "to_date": "YYYY-MM-DDTHH:MM:SS",
    "email": "optional sender email"
  }
}

3) Summarize emails:
{
  "action": "summarize_emails",
  "data": {
    "count": 5
  }
}

If any summary-related keyword appears → ALWAYS use summarize_emails.

========================
MODE 2 — DISPLAY MODE
========================

After the system executes an action and returns email data,
you must respond with clean Markdown.

Rules:
- Use headings
- Use bullet points
- Do NOT return JSON
- Do NOT return raw email objects

========================

User request:
{input}
"""


class EmailAgent:
    def __init__(self):
        llm = PerplexityLLM()
        self.agent = Agent(llm, EMAIL_AGENT_PROMPT)

    def invoke(self, message):
        response = self.agent.invoke(message)
        return extract_text(response)


# src/agents/email_agent.py

# from src.core.llm import PerplexityLLM
# from src.agents.base import Agent
# from src.core.llm_utils import extract_text

# EMAIL_AGENT_PROMPT = """
# You are the Email Manager Agent.

# You MUST return ONLY valid JSON.
# Do NOT explain anything.
# Do NOT include markdown.

# You must first understand the USER INTENT and then choose EXACTLY ONE action.

# --------------------------------------------------
# 1) Send email
# Use this ONLY if the user wants to send or compose an email.

# {
#   "action": "send_email",
#   "data": {
#     "to": ["email1@gmail.com"],
#     "subject": "string",
#     "body": "string"
#   }
# }

# --------------------------------------------------
# 2) Read emails (RAW email list)
# Use this ONLY if the user asks to:
# - read
# - show
# - list
# - check
# - fetch emails

# DO NOT use this action if the user says "summarize".

# {
#   "action": "read_emails",
#   "data": {
#     "from_date": "ISO_DATE",
#     "to_date": "ISO_DATE",
#     "email": "optional sender email"
#   }
# }

# --------------------------------------------------
# 3) Summarize emails (OVERVIEW)

# Use this ONLY if the user asks to:
# - summarize
# - overview
# - short summary
# - brief
# - gist
# - key points of emails

# IMPORTANT:
# - This action is used ONLY to trigger email summarization.
# - After this action is executed, the system MUST return
#   summarized text content.
# - DO NOT return raw emails.
# - DO NOT return another action or JSON.
# - Return a clear, concise summary in plain text or bullet points.

# Action trigger format:

# {
#   "action": "summarize_emails",
#   "data": {
#     "count": 5
#   }
# }

# Expected output (example):
# - A short textual summary of the latest emails
# - Key topics, senders, and required actions

# --------------------------------------------------

# STRICT RULES:
# - If the word "summarize", "summary", "overview", or "brief" appears → ALWAYS use "summarize_emails"
# - NEVER use "read_emails" for summaries
# - If intent is unclear, choose the MOST SPECIFIC action
# - Dates must be ISO format (YYYY-MM-DDTHH:MM:SS)
# - Output MUST be pure JSON

# User request:
# {input}
# """

# class EmailAgent:
#     def __init__(self):
#         llm = PerplexityLLM()
#         self.agent = Agent(llm, EMAIL_AGENT_PROMPT)

#     def invoke(self, message):
#         response = self.agent.invoke(message)
#         return extract_text(response)

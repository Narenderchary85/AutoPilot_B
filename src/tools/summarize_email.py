# from langchain_core.tools import tool
# from langsmith import traceable
# from typing import List, Dict
# from pydantic import BaseModel, Field
# from datetime import datetime

# from src.tools.read_emails import read_emails
# from src.core.llm import PerplexityLLM


# class SummarizeEmailsInput(BaseModel):
#     from_date: str
#     to_date: str
#     count: int = 5
#     user_id: str


# @tool("SummarizeEmails", args_schema=SummarizeEmailsInput)
# @traceable(run_type="tool", name="SummarizeEmails")
# def summarize_emails(from_date: str, to_date: str, count: int, user_id: str):
#     """
#     Returns summarized overview of emails:
#     - From
#     - Subject
#     - One-line AI summary
#     - Date
#     """

#     emails = read_emails.invoke({
#         "from_date": from_date,
#         "to_date": to_date,
#         "email": None,
#         "user_id": user_id
#     })
#     print("Fetched emails:", emails)

#     if isinstance(emails, dict) and "error" in emails:
#         return {"error": emails["error"]}

#     llm = PerplexityLLM()

#     SYSTEM_PROMPT = """
# You are an email summarization assistant.
# Your task is to summarize emails clearly and concisely.

# Rules:
# - Return ONLY one short sentence
# - Do NOT add explanations
# - Do NOT use markdown
# - Do NOT return JSON
# """

#     summaries: List[Dict] = []

#     for mail in emails[:count]:
#         USER_PROMPT = f"""
# From: {mail.get("from")}
# Subject: {mail.get("subject")}
# Email Content: {mail.get("snippet")}
# """

#         llm_response = llm.generate(
#             system_prompt=SYSTEM_PROMPT,
#             user_message=USER_PROMPT
#         )

#         summary_text = (
#             llm_response["choices"][0]["message"]["content"]
#             .strip()
#             .replace("\n", " ")
#         )

#         summaries.append({
#             "from": mail.get("from"),
#             "subject": mail.get("subject"),
#             "summary": summary_text,
#             "date": mail.get("date")
#         })

#     return {
#         "total_emails": len(emails),
#         "returned": len(summaries),
#         "emails": summaries
#     }


from langchain_core.tools import tool
from langsmith import traceable
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from src.tools.read_emails import read_emails
from src.core.llm import PerplexityLLM


# -------------------------------
# INPUT SCHEMA
# -------------------------------
class SummarizeEmailsInput(BaseModel):
    from_date: str
    to_date: str
    count: int = 5
    user_id: str


# -------------------------------
# TOOL
# -------------------------------
@tool("SummarizeEmails", args_schema=SummarizeEmailsInput)
@traceable(run_type="tool", name="SummarizeEmails")
def summarize_emails(from_date: str, to_date: str, count: int, user_id: str):
    """
    Returns summarized overview of emails
    """

    print("\n========== SummarizeEmails TOOL START ==========")
    print("from_date:", from_date)
    print("to_date:", to_date)
    print("count:", count)
    print("user_id:", user_id)

    # -------------------------------
    # STEP 1: CALL READ EMAILS TOOL
    # -------------------------------
    print("\n[STEP 1] Calling read_emails tool...")

    emails = read_emails.invoke({
        "from_date": from_date,
        "to_date": to_date,
        "email": None,
        "user_id": user_id
    })

    print("[STEP 1] read_emails returned:")
    print(emails)
    print("Type:", type(emails))

    # -------------------------------
    # STEP 2: ERROR CHECK
    # -------------------------------
    print("\n[STEP 2] Checking for errors...")

    if emails is None:
        print("❌ ERROR: read_emails returned None")
        return {"error": "read_emails returned None"}

    if isinstance(emails, dict) and "error" in emails:
        print("❌ ERROR FROM read_emails:", emails["error"])
        return {"error": emails["error"]}

    if not isinstance(emails, list):
        print("❌ ERROR: read_emails did not return a list")
        return {"error": "Invalid email data format"}

    if len(emails) == 0:
        print("⚠️ No emails found in the given date range")
        return {
            "total_emails": 0,
            "returned": 0,
            "emails": []
        }

    print(f"✅ Emails fetched successfully: {len(emails)} emails")

    # -------------------------------
    # STEP 3: INIT LLM
    # -------------------------------
    print("\n[STEP 3] Initializing LLM...")

    llm = PerplexityLLM()

    print("✅ LLM initialized")

    SYSTEM_PROMPT = """
You are an email summarization assistant.
Your task is to summarize emails clearly and concisely.

Rules:
- Return ONLY one short sentence
- Do NOT add explanations
- Do NOT use markdown
- Do NOT return JSON
"""

    summaries: List[Dict] = []

    # -------------------------------
    # STEP 4: SUMMARIZATION LOOP
    # -------------------------------
    print("\n[STEP 4] Starting summarization loop...")

    for idx, mail in enumerate(emails[:count], start=1):
        print(f"\n--- Processing email {idx} ---")
        print("From:", mail.get("from"))
        print("Subject:", mail.get("subject"))
        print("Snippet:", mail.get("snippet"))

        USER_PROMPT = f"""
From: {mail.get("from")}
Subject: {mail.get("subject")}
Email Content: {mail.get("snippet")}
"""

        print("[STEP 4] Sending prompt to LLM...")

        llm_response = llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=USER_PROMPT
        )

        print("[STEP 4] Raw LLM response:")
        print(llm_response)

        try:
            summary_text = (
                llm_response["choices"][0]["message"]["content"]
                .strip()
                .replace("\n", " ")
            )
        except Exception as e:
            print("❌ ERROR parsing LLM response:", e)
            summary_text = "Summary generation failed"

        print("✅ Summary:", summary_text)

        summaries.append({
            "from": mail.get("from"),
            "subject": mail.get("subject"),
            "summary": summary_text,
            "date": mail.get("date")
        })

    # -------------------------------
    # STEP 5: FINAL RESPONSE
    # -------------------------------
    print("\n[STEP 5] Returning final response")
    print("Total emails:", len(emails))
    print("Returned summaries:", len(summaries))

    print("========== SummarizeEmails TOOL END ==========\n")

    return {
        "total_emails": len(emails),
        "returned": len(summaries),
        "emails": summaries
    }

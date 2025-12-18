import json
from datetime import datetime, timedelta
from src.tools.add_event_calendar import add_event_to_calendar
from src.tools.get_calendar_events import get_calendar_events
from src.tools.send_email import send_email
from src.tools.read_emails import read_emails
from src.tools.search_web import search_web
from src.tools.scrape_website import scrape_website_to_markdown
from src.tools.find_contact_email import find_contact_email
from src.agents.google_news_agent import GoogleNewsAgent
from src.tools.news_agent import summarize_news
from src.utils.presentation_builder import PresentationBuilder


def parse_date_time(date_str: str, time_str: str):
    """
    date_str: 'today' | 'tomorrow' | '2025-12-12'
    time_str: '9:00 PM' | '21:00'
    returns ISO 8601 string (local tz)
    """
    now = datetime.now()

    # Resolve date
    if not date_str:
        day = now.date()
    elif date_str.lower() == "today":
        day = now.date()
    elif date_str.lower() == "tomorrow":
        day = (now + timedelta(days=1)).date()
    else:
        day = datetime.fromisoformat(date_str).date()

    # Resolve time
    if not time_str:
        dt_time = now.time()
    else:
        try:
            dt_time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
        except ValueError:
            try:
                dt_time = datetime.strptime(time_str.strip(), "%I %p").time()
            except ValueError:
                dt_time = datetime.strptime(time_str.strip(), "%H:%M").time()

    local_dt = datetime.combine(day, dt_time)
    return local_dt.astimezone().isoformat()

def parse_agent_response(llm_response: dict):
    """
    Extract ONLY the assistant JSON from the LLM response
    """
    try:
        content = llm_response["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        raise ValueError(f"Invalid agent JSON: {e}")

def execute_action(reply):
    """
    Accepts LLM output as dict OR JSON string and executes the action.
    """

    if isinstance(reply, dict):
        data = reply
    else:
        try:
            data = json.loads(reply)
        except Exception:
            try:
                cleaned = reply.strip().strip('"')
                data = json.loads(cleaned)
            except Exception:
                return {
                    "error": "Invalid JSON from agent",
                    "raw": reply
                }

    action = data.get("action")
    payload = data.get("data") or data.get("parameters") or {}

    if not action:
        return {
            "error": "No action provided by agent",
            "raw": data
        }

    if action == "create_schedule":
        title = payload.get("title", "Untitled Event")
        description = payload.get("description", "")
        date = payload.get("date", "today")
        time = payload.get("time", "9:00 AM")

        start_iso = parse_date_time(date, time)

        result = add_event_to_calendar.invoke({
            "title": title,
            "description": description,
            "start_time": start_iso
        })

        return {
            "status": "event_created",
            "details": result
        }

    elif action == "list_events":
        start = action["start_date"]
        end = action["end_date"]

        events = get_calendar_events.invoke({
            "start_date": start,
            "end_date": end
        })

        return {
            "status": "calendar_events",
            "events": events
        }


    elif action == "send_email":
        recipients = payload.get("to", [])
        subject = payload.get("subject", "No Subject")
        body = payload.get("body", "")

        if isinstance(recipients, str):
            recipients = [recipients]

        results = []
        for recipient in recipients:
            result = send_email.invoke({
                "to": recipient,
                "subject": subject,
                "body": body
            })
            results.append({
                "to": recipient,
                "result": result
            })

        return {
            "status": "emails_sent",
            "results": results
        }


    elif action == "read_emails":
        result = read_emails.invoke({
            "from_date": payload.get("from_date"),
            "to_date": payload.get("to_date"),
            "email": payload.get("email")
        })

        human_text = PresentationBuilder.build(result)

        return {
            "status": "emails_fetched",
            "emails": human_text
        }


    elif action == "summarize_emails":
        count = payload.get("count", 5)

        now = datetime.now()
        from_date = (now - timedelta(hours=24)).isoformat()
        to_date = now.isoformat()

        emails = read_emails.invoke({
            "from_date": from_date,
            "to_date": to_date,
            "email": None
        })

        human_text = PresentationBuilder.build(emails)

        if isinstance(emails, dict) and "error" in emails:
            return {
                "status": "emails_summary",
                "error": emails["error"]
            }

        return {
            "status": "emails_summary",
            "count": min(count, len(emails)),
            "summary": human_text[:count]
        }

    elif action == "search_web":
        query = payload.get("query")
        result = search_web.invoke({"query": query})

        return {
            "status": "web_search",
            "query": query,
            "results": result
        }


    elif action == "scrape_website":
        url = payload.get("url")
        result = scrape_website_to_markdown.invoke({"url": url})

        return {
            "status": "website_scraped",
            "url": url,
            "content": result
        }
    
    elif action == "find_contact_email":
        name = payload.get("name")
        result = find_contact_email(name)
        return {
            "status": "success",
            "action": "find_contact_email",
            "result": result
        }
    
    elif action == "fetch_news":

            news_agent = GoogleNewsAgent()
            print("new agent",news_agent)
            # 1. Search news via Perplexity (RAW response)
            llm_response = news_agent.search_news_with_llm(
                payload["data"]["query"]
            )
            print("llm",llm_response)
            # 2. Extract articles from search_results
            articles = news_agent.extract_articles_from_search(
                llm_response,
                max_results=payload["data"].get("max_results", 7)
            )
            print("articles",articles)
            if not articles:
                return {
                    "status": "error",
                    "message": "No news found"
                }

            # 3. Summarize
            summary = summarize_news(articles, max_points=7)
            print("summary",summary)
            return {
                "status": "success",
                "query": payload["data"]["query"],
                "summary": summary,
                "articles": articles
            }



    # -----------------------
    # Unknown action
    # -----------------------
    return {
        "error": "Unknown action",
        "action": action
    }

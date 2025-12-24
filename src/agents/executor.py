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
from src.tools.summarize_email import summarize_emails


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



def execute_action(reply,user_id:str):
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
            "start_time": start_iso,
            "user_id": user_id   
        })

        return {
            "status": "event_created",
            "details": result
        }

    elif action == "list_events":
        start = payload.get("start_date")
        end = payload.get("end_date")

        events = get_calendar_events(start, end)

        return {
            "status": "events_fetched",
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
                "body": body,
                "user_id": user_id
            })
            results.append({
                "to": recipient,
                "result": result
            })
        print("results:",results)
        return {
            "status": "emails_sent",
            "results": results
        }


    elif action == "read_emails":
        print('read emails action invoked')
        result = read_emails.invoke({
            "from_date": payload.get("from_date"),
            "to_date": payload.get("to_date"),
            "email": payload.get("email"),
            "user_id": user_id
        })

        return {
            "status": "emails_fetched",
            "emails": result
        }


    elif action == "summarize_emails":
        count = payload.get("count", 5)
        print('summarize emails action invoked')
        now = datetime.now()
        from_date = (now - timedelta(hours=24)).isoformat()
        to_date = now.isoformat()
        result = summarize_emails.invoke({
            "from_date": from_date,
            "to_date": to_date,
            "count": count,
            "user_id": user_id
        })

        return {
            "status": "emails_summary",
            "result": result
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
        # Directly define query and max_results without invoking the agent recursively
        query = "Artificial Intelligence"
        max_results = 10

        # Initialize your news agent
        news_agent = GoogleNewsAgent()

        # Fetch articles directly
        articles = news_agent.fetch_news(query, max_results)

        # Summarize the fetched news
        summary = summarize_news(articles, max_points=7)

        return {
            "status": "news_fetched_summarized",
            "query": query,
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

from typing import Any, List, Dict


class PresentationBuilder:

    @staticmethod
    def build(response: Any) -> str:
        print("response", response)

        # 1️⃣ EMAILS → list of dicts with "from" & "subject"
        if PresentationBuilder._is_email_list(response):
            return PresentationBuilder._emails_view(response)

        # 2️⃣ CALENDAR → dict with event_id/html_link
        if PresentationBuilder._is_calendar_event(response):
            return PresentationBuilder._calendar_view(response)

        return "Action completed successfully."

    # ---------------- DETECTORS ----------------

    @staticmethod
    def _is_email_list(data: Any) -> bool:
        return (
            isinstance(data, list)
            and len(data) > 0
            and isinstance(data[0], dict)
            and "from" in data[0]
            and "subject" in data[0]
        )

    @staticmethod
    def _is_calendar_event(data: Any) -> bool:
        return (
            isinstance(data, dict)
            and "event_id" in data
            and "html_link" in data
        )

    # ---------------- EMAIL VIEW ----------------

    @staticmethod
    def _emails_view(emails: List[Dict]) -> str:
        lines = [f"📬 You have {len(emails)} unread emails:\n"]

        for i, mail in enumerate(emails, start=1):
            sender = PresentationBuilder._clean_sender(mail.get("from"))
            subject = mail.get("subject", "No subject")
            date = PresentationBuilder._format_date(mail.get("date"))
            snippet = PresentationBuilder._clean_snippet(mail.get("snippet", ""))

            lines.append(
                f"{i}. From: {sender}\n"
                f"   Subject: {subject}\n"
                f"   Received: {date}\n"
                f"   Preview: {snippet}\n"
            )

        return "\n".join(lines)

    # ---------------- CALENDAR VIEW ----------------

    @staticmethod
    def _calendar_view(event: Dict) -> str:
        return (
            "📅 Event created successfully!\n\n"
            f"🔹 Event ID: {event['event_id']}\n"
            f"🔗 Open in Calendar: {event['html_link']}"
        )

    # ---------------- HELPERS ----------------

    @staticmethod
    def _clean_sender(sender: str) -> str:
        if "<" in sender:
            return sender.split("<")[0].strip()
        return sender

    @staticmethod
    def _clean_snippet(text: str) -> str:
        return " ".join(text.split())[:200] + "..."

    @staticmethod
    def _format_date(date_str: str) -> str:
        from datetime import datetime
        try:
            return datetime.fromisoformat(date_str).strftime(
                "%d %b %Y, %I:%M %p"
            )
        except Exception:
            return date_str

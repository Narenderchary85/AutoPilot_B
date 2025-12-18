class PresentationBuilder:

    @staticmethod
    def build(response: dict) -> str:
        response_type = response.get("type")

        if response_type == "emails":
            return PresentationBuilder._emails_view(response)

        if response_type == "calendar_event":
            return PresentationBuilder._calendar_view(response)

        return "Action completed successfully."

    # ---------------- EMAILS ----------------

    @staticmethod
    def _emails_view(data: dict) -> str:
        if data["count"] == 0:
            return "You have no unread emails in this period."

        lines = [f"📬 You have {data['count']} unread emails:\n"]

        for i, mail in enumerate(data["items"], start=1):
            lines.append(
                f"{i}. From: {mail['sender']}\n"
                f"   Subject: {mail['subject']}\n"
                f"   Received: {mail['received_at']}\n"
                f"   Preview: {mail['preview']}\n"
            )

        return "\n".join(lines)

    # ---------------- CALENDAR ----------------

    @staticmethod
    def _calendar_view(data: dict) -> str:
        return (
            "📅 Event created successfully!\n\n"
            f"🔹 Event ID: {data['event']['id']}\n"
            f"🔗 Open in Calendar: {data['event']['link']}"
        )

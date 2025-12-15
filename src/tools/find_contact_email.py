import re
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.google_auth import get_contacts_credentials  # <-- updated

class FindContactEmailInput(BaseModel):
    name: str = Field(description="Name of the contact")

@tool("FindContactEmail", args_schema=FindContactEmailInput)
@traceable(run_type="tool", name="FindContactEmail")
def find_contact_email(name: str):
    "Get a contact's email and phone number from Google Contacts"
    try:
        creds = get_contacts_credentials()  # <-- use the new contacts creds
        service = build('people', 'v1', credentials=creds)

        results = service.people().searchContacts(
            query=name,
            readMask='names,phoneNumbers,emailAddresses'
        ).execute()

        connections = results.get('results', [])
        if not connections:
            return {"message": f"No contact found with the name: {name}"}

        matching_contacts = []
        for connection in connections:
            contact = connection.get('person', {})
            names = contact.get('names', [])
            if not names:
                continue

            unstructured_name = names[0].get('unstructuredName', '').lower()
            if name.lower() in unstructured_name:
                full_name = names[0].get('displayName', 'N/A')
                phone_numbers = [phone.get('value', 'N/A') for phone in contact.get('phoneNumbers', [])]
                emails = [email.get('value', 'N/A') for email in contact.get('emailAddresses', [])]

                matching_contacts.append({
                    'name': full_name,
                    'phone_numbers': phone_numbers,
                    'emails': emails
                })

        if not matching_contacts:
            return {"message": f"No contact found with the matching criteria: {name}"}

        return {"contacts": matching_contacts}

    except HttpError as error:
        return {"error": str(error)}

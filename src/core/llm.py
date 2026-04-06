# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# PPLX_API_KEY = os.getenv("PPLX_API_KEY")

# class PerplexityLLM:

#     def __init__(self):
#         if not PPLX_API_KEY:
#             raise ValueError("PPLX_API_KEY missing in environment variables")

#         self.api_key = PPLX_API_KEY
#         self.url = "https://api.perplexity.ai/chat/completions"


#     def call_perplexity_api(self, system_prompt, user_message):
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "model": "sonar-pro",
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_message}
#             ],
#             "temperature": 0,
#             "search": False
#         }

#         response = requests.post(self.url, json=payload, headers=headers)

#         print("\n--- RAW RESPONSE ---")
#         print(response.status_code)
#         print(response.text)
#         print("--------------------\n")

#         response.raise_for_status()

#         return response.json()

#     def generate(self, system_prompt, user_message):
#         return self.call_perplexity_api(system_prompt, user_message)

# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# PPLX_API_KEY = os.getenv("PPLX_API_KEY")

# class PerplexityLLM:

#     def __init__(self):
#         self.url = "http://localhost:11434/v1/chat/completions"


#     def call_perplexity_api(self, system_prompt, user_message):
#         headers = {
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "model": "mistral",
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_message}
#             ],
#             "temperature": 0,
#         }

#         response = requests.post(self.url, json=payload, headers=headers)

#         print("\n--- RAW RESPONSE ---")
#         print(response.status_code)
#         print(response.text)
#         print("--------------------\n")

#         response.raise_for_status()

#         return response.json()

#     def generate(self, system_prompt, user_message):
#         return self.call_perplexity_api(system_prompt, user_message)

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class PerplexityLLM:

    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY missing in environment variables")

        self.api_key = GOOGLE_API_KEY

        # Gemini endpoint
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"


    def call_google_api(self, system_prompt, user_message):

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\nUser: {user_message}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0
            }
        }

        response = requests.post(self.url, json=payload, headers=headers)

        # print("\n--- RAW RESPONSE ---")
        # print(response.status_code)
        # print(response.text)
        # print("--------------------\n")

        response.raise_for_status()

        return response.json()


    def generate(self, system_prompt, user_message):
        return self.call_google_api(system_prompt, user_message)
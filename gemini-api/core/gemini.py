from google.genai import Client, types

from core.config import settings

client = Client(api_key=settings.gemini_api_key)

gemini_types = types

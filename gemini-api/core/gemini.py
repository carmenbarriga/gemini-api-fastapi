import os

from dotenv import load_dotenv
from google.genai import Client, types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = Client(api_key=GEMINI_API_KEY)

gemini_types = types

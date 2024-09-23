import os
from dotenv import load_dotenv

load_dotenv()
TELGRAM_API_TOKEN = os.getenv('TELGRAM_API_TOKEN')

if not TELGRAM_API_TOKEN:
    print("Error: No token found!")
    exit(1)

import os
from dotenv import load_dotenv

load_dotenv()
TELGRAM_API_TOKEN = os.getenv('TELGRAM_API_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

if not TELGRAM_API_TOKEN:
    print("Error: No TG token found!")
    exit(1)

if not GROUP_ID:
    print("Error: No group id found!")
    exit(1)

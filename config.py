import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

if not EMAIL or not PASSWORD:
    raise RuntimeError("EMAIL_USER or EMAIL_PASS not set in environment variables")

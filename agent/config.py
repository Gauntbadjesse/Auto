import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "ollama")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")

ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "newlifesmp.com").lower()

SITE_USERNAME = os.environ.get("SITE_USERNAME", "")
SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")

BROWSER_HEADED = os.environ.get("BROWSER_HEADED", "false").lower() == "true"

MAX_STEPS = int(os.environ.get("MAX_STEPS", "25"))

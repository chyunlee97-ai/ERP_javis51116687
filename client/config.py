import os
from dotenv import load_dotenv

# Load client/.env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
SHOW_DEVELOPER_PANELS = os.getenv("SHOW_DEVELOPER_PANELS", "False").lower() in ("true", "1", "yes")

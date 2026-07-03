import os
from dotenv import load_dotenv

# Load server/.env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Database Configuration
DB_SERVER = os.getenv("DB_SERVER", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Server Configuration
API_PORT = int(os.getenv("API_PORT", 8001))

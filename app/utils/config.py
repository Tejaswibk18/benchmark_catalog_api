from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS"))


MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "benchmark_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "benchmark_catalog")

if not MONGO_URL:
    raise ValueError("MONGO_URL is not set in .env")
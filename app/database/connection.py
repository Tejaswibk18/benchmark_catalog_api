from pymongo import MongoClient
from app.utils.config import MONGO_URL, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URL)

db = client[DB_NAME]

benchmark_collection = db[COLLECTION_NAME]
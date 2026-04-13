from pymongo import MongoClient
from app.utils.config import MONGO_URL, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URL)

db = client[DB_NAME]

benchmark_collection = db[COLLECTION_NAME]

benchmark_execution_collection = db["benchmark_execution"]
workflow_runs_collection = db["workflow_runs"]
workflow_catalog_collection = db["workflow_catalog"]
platform_pool_collection = db["platform_pool"]
jobs_collection = db["jobs"]
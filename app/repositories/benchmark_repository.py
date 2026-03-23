from app.database.connection import benchmark_collection
from bson import ObjectId

def insert_benchmark(data):

    return benchmark_collection.insert_one(data)


def fetch_benchmarks(query):

    cursor = benchmark_collection.find(query)

    return list(cursor)

def fetch_one(id):

    return benchmark_collection.find_one({"_id": ObjectId(id)})


def update_benchmark(id, payload):

    return benchmark_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": payload}
    )


def archive_benchmark(id):

    return benchmark_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "ARCHIVED"}}
    )
from app.database.connection import benchmark_collection
import time

from app.repositories.benchmark_repository import fetch_benchmarks , archive_benchmark
from app.repositories.benchmark_repository import fetch_one, update_benchmark

from bson import ObjectId
from datetime import datetime
import re


def create_benchmark(payload):

    payload = payload.dict()

    existing = benchmark_collection.find_one({
        "catalog_name": payload["catalog_name"],
        "benchmark_name": payload["benchmark_name"]
    })

    if existing:
        raise ValueError("Benchmark already exists")

    payload["name"] = f"{payload['catalog_name']}_{int(time.time())}"

    payload["status"] = "DRAFT"

    payload["created_by"] = "system"

    payload["history"] = []

    result = benchmark_collection.insert_one(payload)

    payload["_id"] = str(result.inserted_id)

    return payload
    

def get_benchmarks(id=None, benchmark_name=None, benchmark_category=None):

    try:

        query = {}

        id and query.update({"_id": ObjectId(id)})

        benchmark_name and validate_text(benchmark_name)

        benchmark_category and validate_text(benchmark_category)

        benchmark_name and query.update({"benchmark_name": benchmark_name})

        benchmark_category and query.update({"benchmark_category": benchmark_category})

        data = fetch_benchmarks(query)

        data or (_ for _ in ()).throw(ValueError("no benchmark found"))

        list(map(lambda x: x.update({"_id": str(x["_id"])}), data))

        return data

    except Exception as e:

        raise Exception(str(e))


def validate_text(value):

    if not re.fullmatch(r"[A-Za-z_]+", value):
        raise ValueError("only alphabets and underscore allowed")
    


ALLOWED_STATUS = [
    "DRAFT",
    "PENDING-APPROVAL",
    "APPROVED",
    "REJECTED",
    "PUBLISHED"
]


def update_benchmark_service(id, payload, user="system"):

    try:

        ObjectId(id)

    except:

        raise ValueError("invalid benchmark id")

    existing = fetch_one(id)

    existing or (_ for _ in ()).throw(ValueError("benchmark not found"))

    payload = payload.dict(exclude_unset=True)

    payload.get("benchmark_name") and validate_text(payload["benchmark_name"])

    payload.get("benchmark_category") and validate_text(payload["benchmark_category"])

    payload.get("status") and validate_status(payload["status"])

    changes = list(
        map(
            lambda k: {
                "path": k,
                "old_value": existing.get(k),
                "new_value": payload.get(k)
            },
            filter(lambda k: existing.get(k) != payload.get(k), payload.keys())
        )
    )

    version = str(len(existing.get("history", [])) + 1)

    history_entry = {
        "catalog_version": version,
        "changed_on": datetime.utcnow(),
        "changed_by": user,
        "change_type": "UPDATE",
        "summary": "Benchmark updated",
        "changes": changes
    }

    history = existing.get("history", [])

    history.append(history_entry)

    payload.update({"history": history})

    update_benchmark(id, payload)

    return payload


def validate_text(value):

    if not re.fullmatch(r"[A-Za-z_]+", value):
        raise ValueError("only alphabets and underscore allowed")


def validate_status(value):

    if value not in ALLOWED_STATUS:
        raise ValueError("invalid status value")
    

    
def patch_benchmark_service(id, payload, user="system"):

    try:
        ObjectId(id)
    except:
        raise ValueError("invalid benchmark id")

    existing = fetch_one(id)

    existing or (_ for _ in ()).throw(ValueError("benchmark not found"))

    payload = payload.dict(exclude_unset=True)

    payload.get("benchmark_name") and validate_text(payload["benchmark_name"])

    payload.get("benchmark_category") and validate_text(payload["benchmark_category"])

    payload.get("status") and validate_status(payload["status"])

    changes = list(
        map(
            lambda k: {
                "path": k,
                "old_value": existing.get(k),
                "new_value": payload.get(k)
            },
            filter(lambda k: existing.get(k) != payload.get(k), payload.keys())
        )
    )

    changes or (_ for _ in ()).throw(ValueError("no changes detected"))

    version = str(len(existing.get("history", [])) + 1)

    history_entry = {
        "catalog_version": version,
        "changed_on": datetime.utcnow(),
        "changed_by": user,
        "change_type": "UPDATE",
        "summary": "Benchmark patched",
        "changes": changes
    }

    history = existing.get("history", [])

    history.append(history_entry)

    payload.update({"history": history})

    update_benchmark(id, payload)

    return payload


def validate_text(value):

    if not re.fullmatch(r"[A-Za-z_]+", value):
        raise ValueError("only alphabets and underscore allowed")


def validate_status(value):

    if value not in ALLOWED_STATUS:
        raise ValueError("invalid status value")
    

ALLOWED_DELETE_STATUS = [
    "DRAFT",
    "PENDING-APPROVAL",
    "REJECTED"
]


def delete_benchmark_service(id, user):

    try:
        ObjectId(id)
    except:
        raise ValueError("invalid benchmark id")

    data = fetch_one(id)

    if not data:
        raise ValueError("benchmark not found")

    user_name = user.get("user") if user else "system"

    if data.get("created_by") != user_name:
        raise ValueError("only owner can delete benchmark")

    if data.get("status") not in ALLOWED_DELETE_STATUS:
        raise ValueError("benchmark cannot be deleted in current status")

    archive_benchmark(id)

    return {"status": "ARCHIVED"}



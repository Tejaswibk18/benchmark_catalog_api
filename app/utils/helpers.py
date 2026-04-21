from bson import ObjectId
from datetime import datetime


def serialize_doc(doc):
    if not doc:
        return doc

    doc["_id"] = str(doc["_id"])

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

        elif isinstance(value, datetime):
            doc[key] = value.isoformat()

    return doc
from bson import ObjectId


def serialize_doc(doc):
    if not doc:
        return None

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

    return doc
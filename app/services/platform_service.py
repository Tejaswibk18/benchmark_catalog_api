from datetime import datetime
from app.database.connection import platform_pool_collection
from bson import ObjectId


def serialize_doc(doc):

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

    return doc


# -------------------------------
# CREATE SERVER
# -------------------------------
def create_platform_server(payload):

    try:

        data = payload.dict()

        data["created_on"] = datetime.utcnow()
        data["status"] = "ACTIVE"

        result = platform_pool_collection.insert_one(data)

        data["_id"] = result.inserted_id

        return serialize_doc(data)

    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# GET ALL SERVERS
# -------------------------------

def get_platform_servers_service(
    id=None,
    os=None,
    ip_address=None,
    server_name=None
):

    try:

        query = {
            "status": {"$ne": "DELETED"}
        }

        # -------------------------------
        # ID FILTER
        # -------------------------------
        if id:
            try:
                query["_id"] = ObjectId(id)
            except:
                raise ValueError("invalid server id")

        # -------------------------------
        # OTHER FILTERS
        # -------------------------------
        os and query.update({"os": os})
        ip_address and query.update({"ip_address": ip_address})
        server_name and query.update({"server_name": server_name})

        # -------------------------------
        # FETCH DATA
        # -------------------------------
        data = list(platform_pool_collection.find(query))

        data or (_ for _ in ()).throw(ValueError("no servers found"))

        return [serialize_doc(doc) for doc in data]

    except ValueError as e:
        raise ValueError(str(e))

    except Exception as e:
        raise Exception(str(e))
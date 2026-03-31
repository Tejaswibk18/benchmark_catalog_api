from app.database.connection import (
    benchmark_execution_collection,
    workflow_runs_collection,
    workflow_catalog_collection
)

from bson import ObjectId
from datetime import datetime


# -------------------------------
# COMMON
# -------------------------------
def serialize_doc(doc):
    if not doc:
        return None

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

    return doc


def check_duplicate_execution(payload):
    existing = benchmark_execution_collection.find_one({
        "benchmark_name": payload["benchmark_name"],
        "catalog_name": payload["catalog_name"]
    })

    if existing:
        raise ValueError("benchmark already exists")


# -------------------------------
# CREATE
# -------------------------------
def create_benchmark_execution_service(payload):
    try:
        payload = payload.dict()

        check_duplicate_execution(payload)

        # -------------------------------
        # EXTRACT workflow separately
        # -------------------------------
        workflow = payload.pop("workflow")   # REMOVE from payload
        save_flag = payload.pop("save_to_workflow_catalog")

        current_time = datetime.utcnow()

        # -------------------------------
        # CREATE execution WITHOUT workflow
        # -------------------------------
        execution_data = {
            **payload,   # now clean (no workflow)
            "created_on": current_time,
            "created_by": "system"
        } 

        result = benchmark_execution_collection.insert_one(execution_data)
        execution_id = result.inserted_id       #extracts the auto-generated _id

        # -------------------------------
        # 2. CREATE workflow_runs
        # -------------------------------
        workflow_runs_data = {
            **payload,
            "execution_id": execution_id,
            "workflow": workflow,
            "created_on": current_time,
            "created_by": "system"
        }

        workflow_result = workflow_runs_collection.insert_one(workflow_runs_data)
        workflow_run_id = workflow_result.inserted_id

        # -------------------------------
        # 3. UPDATE execution with workflow_run_id
        # -------------------------------
        benchmark_execution_collection.update_one(
            {"_id": execution_id},
            {"$set": {"workflow_run_id": workflow_run_id}}
        )

        # -------------------------------
        # 4. OPTIONAL workflow_catalog
        # -------------------------------
        if save_flag:
            workflow_catalog_collection.insert_one({
                "execution_id": execution_id,
                "workflow_name": payload.get("workflow_name"),
                "workflow": workflow,
                "created_on": current_time,
                "created_by": "system"
            })

        # -------------------------------
        # 5. RETURN FULL RESPONSE
        # -------------------------------
        execution_data["_id"] = execution_id
        execution_data["workflow_run_id"] = workflow_run_id

        # ADD THIS LINE (THIS IS WHAT YOU ASKED)
        execution_data["workflow"] = workflow

        return serialize_doc(execution_data)

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# GET
# -------------------------------
def get_benchmark_execution_service(id=None, benchmark_name=None, benchmark_category=None):
    try:
        query = {}
        execution_id = None

        # -------------------------------
        # HANDLE ID
        # -------------------------------
        if id:
            try:
                obj_id = ObjectId(id)
            except:
                raise ValueError("invalid id")

            execution = benchmark_execution_collection.find_one({"_id": obj_id})
            workflow_run = workflow_runs_collection.find_one({"_id": obj_id})
            catalog = workflow_catalog_collection.find_one({"_id": obj_id})

            execution_id = (
                execution and execution["_id"]
                or workflow_run and workflow_run.get("execution_id")
                or catalog and catalog.get("execution_id")
            )

            if not execution_id:
                raise ValueError("no execution data found")

        # -------------------------------
        # FILTERS
        # -------------------------------
        if benchmark_name:
            query["benchmark_name"] = benchmark_name

        if benchmark_category:
            query["benchmark_category"] = benchmark_category

        # -------------------------------
        # FETCH DATA
        # -------------------------------
        data = list(workflow_runs_collection.find({
            **query,
            **({"execution_id": execution_id} if execution_id else {}),
            "status": {"$ne": "DELETED"}
        }))

        if not data:
            raise ValueError("no execution data found")

        response = []

        for doc in data:

            exec_id = doc.get("execution_id")

            execution = benchmark_execution_collection.find_one({"_id": exec_id})
            catalog = workflow_catalog_collection.find_one({"execution_id": exec_id})

            # -------------------------------
            # SORT STAGES (ASC)
            # -------------------------------
            if doc.get("workflow") and doc["workflow"].get("stages"):
                doc["workflow"]["stages"] = sorted(
                    doc["workflow"]["stages"],
                    key=lambda x: x.get("stage_order", 0)
                )

            # serialize
            doc = serialize_doc(doc)
            execution = serialize_doc(execution)
            catalog = serialize_doc(catalog)

            response.append({
                "workflow_run": doc,
                "benchmark_execution": execution,
                "workflow_catalog": catalog
            })

        return response

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# PATCH
# -------------------------------
def patch_benchmark_execution_service(id, payload):
    try:
        try:
            obj_id = ObjectId(id)
        except:
            raise ValueError("invalid execution id")

        # -------------------------------
        # FIND execution_id
        # -------------------------------
        execution = benchmark_execution_collection.find_one({"_id": obj_id})
        workflow_run = workflow_runs_collection.find_one({"_id": obj_id})
        catalog = workflow_catalog_collection.find_one({"_id": obj_id})

        execution_id = (
            execution and execution["_id"]
            or workflow_run and workflow_run.get("execution_id")
            or catalog and catalog.get("execution_id")
        )

        if not execution_id:
            raise ValueError("execution not found")

        update_data = payload.dict(exclude_unset=True)

        if not update_data:
            raise ValueError("no fields to update")

        # -------------------------------
        # HANDLE WORKFLOW UPDATE
        # -------------------------------
        if "workflow" in update_data:
            workflow_runs_collection.update_many(
                {"execution_id": execution_id},
                {"$set": {"workflow": update_data["workflow"]}}
            )
            update_data.pop("workflow")

        # -------------------------------
        # UPDATE benchmark_execution
        # -------------------------------
        benchmark_execution_collection.update_one(
            {"_id": execution_id},
            {"$set": update_data}
        )

        # -------------------------------
        # SYNC workflow_runs
        # -------------------------------
        workflow_runs_collection.update_many(
            {"execution_id": execution_id},
            {"$set": update_data}
        )

        updated = benchmark_execution_collection.find_one({"_id": execution_id})

        return serialize_doc(updated)

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# DELETE
# -------------------------------
def delete_benchmark_execution_service(id):
    try:
        try:
            obj_id = ObjectId(id)
        except:
            raise ValueError("invalid execution id")

        execution = benchmark_execution_collection.find_one({"_id": obj_id})
        workflow_run = workflow_runs_collection.find_one({"_id": obj_id})
        catalog = workflow_catalog_collection.find_one({"_id": obj_id})

        execution_id = (
            execution and execution["_id"]
            or workflow_run and workflow_run.get("execution_id")
            or catalog and catalog.get("execution_id")
        )

        if not execution_id:
            raise ValueError("execution not found")

        current_time = datetime.utcnow()

        benchmark_execution_collection.update_one(
            {"_id": execution_id},
            {"$set": {"status": "DELETED", "deleted_on": current_time}}
        )

        workflow_runs_collection.update_many(
            {"execution_id": execution_id},
            {"$set": {"status": "DELETED", "deleted_on": current_time}}
        )

        workflow_catalog_collection.update_many(
            {"execution_id": execution_id},
            {"$set": {"status": "DELETED", "deleted_on": current_time}}
        )

        return {
            "execution_id": str(execution_id),
            "status": "DELETED"
        }

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))
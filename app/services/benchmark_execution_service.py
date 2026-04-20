from app.database.connection import (
    benchmark_execution_collection,
    workflow_runs_collection,
    workflow_catalog_collection,
    jobs_collection
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

        jobs = build_jobs_from_workflow(workflow, execution_id)

        if jobs:
            jobs_collection.insert_many(jobs)

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
def get_benchmark_execution_service(
    id=None,
    status=None,
    search=None,
    page=1,
    limit=10
):
    try:
        skip = (page - 1) * limit

        job_query = {}

        # -------------------------------
        # ID FILTER (HIGHEST PRIORITY)
        # -------------------------------
        if id:
            try:
                obj_id = ObjectId(id)
            except:
                raise ValueError("invalid id")

            # ensure execution exists
            execution = benchmark_execution_collection.find_one({"_id": obj_id})

            if not execution:
                raise ValueError("no execution data found")

            job_query["execution_id"] = obj_id

        # -------------------------------
        # STATUS FILTER
        # -------------------------------
        if status:
            job_query["status"] = {
                "$regex": f"^{status}$",
                "$options": "i"
            }

        # -------------------------------
        # SEARCH FILTER (ONLY IF NO ID)
        # -------------------------------
        if search and not id:
            import re
            search = re.escape(search)

            workflow_matches = workflow_runs_collection.find({
                "$or": [
                    {"workflow.stages.stage_name": {"$regex": search, "$options": "i"}},
                    {"workflow.stages.task_name": {"$regex": search, "$options": "i"}},
                    {"workflow.stages.task_type": {"$regex": search, "$options": "i"}},
                    {"workflow.stages.parameters.action": {"$regex": search, "$options": "i"}}
                ]
            }, {"execution_id": 1})

            execution_ids = [doc["execution_id"] for doc in workflow_matches]

            if not execution_ids:
                raise ValueError("no execution data found")

            job_query["execution_id"] = {"$in": execution_ids}

        # -------------------------------
        # FETCH JOBS
        # -------------------------------
        jobs = list(
            jobs_collection.find(job_query)
            .skip(skip)
            .limit(limit)
        )

        if not jobs:
            raise ValueError("no execution data found")

        # -------------------------------
        # FETCH RELATED DATA
        # -------------------------------
        execution_ids = list({job["execution_id"] for job in jobs})

        executions = {
            str(doc["_id"]): serialize_doc(doc)
            for doc in benchmark_execution_collection.find(
                {"_id": {"$in": execution_ids}}
            )
        }

        workflows = {
            str(doc["execution_id"]): serialize_doc(doc)
            for doc in workflow_runs_collection.find(
                {"execution_id": {"$in": execution_ids}}
            )
        }

        catalogs = {
            str(doc["execution_id"]): serialize_doc(doc)
            for doc in workflow_catalog_collection.find(
                {"execution_id": {"$in": execution_ids}}
            )
        }

        response = [
            {
                "job": serialize_doc(job),
                "benchmark_execution": executions.get(str(job["execution_id"])),
                "workflow_run": workflows.get(str(job["execution_id"])),
                "workflow_catalog": catalogs.get(str(job["execution_id"]))
            }
            for job in jobs
        ]

        total = jobs_collection.count_documents(job_query)

        return {
            "items": response,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

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
    

def build_jobs_from_workflow(workflow, execution_id):
    try:
        stages = workflow.get("stages", [])

        jobs = [
            {
                "execution_id": execution_id,

                # STAGE
                "stage_type": stage.get("stage_type"),
                "stage_name": stage.get("stage_name"),
                "stage_order": stage.get("stage_order"),

                # TASK
                "task_type": stage.get("task_type"),
                "task_name": stage.get("task_name"),
                "task_order": stage.get("task_order"),

                # SUT (IMPORTANT)
                "sut_id": sut,

                # STATUS
                "status": "QUEUED",
                "started_at": None,
                "finished_at": None,

                # RESULT (SINGLE)
                "result": None,

                # METADATA
                "created_on": datetime.utcnow(),
                "updated_on": None
            }

            for stage in stages
            for sut in stage.get("target_sut", [])
        ]

        return jobs

    except Exception as e:
        raise Exception(str(e))
    


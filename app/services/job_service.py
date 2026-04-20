from bson import ObjectId
from datetime import datetime

from app.database.connection import jobs_collection
from app.utils.helpers import serialize_doc


VALID_TRANSITIONS = {
    "QUEUED": ["RUNNING"],
    "RUNNING": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": []
}


def update_job_status_service(job_id, status):

    
    try:
        try:
            obj_id = ObjectId(job_id)
        except:
            raise ValueError("invalid job id")

        # -------------------------------
        # NORMALIZE STATUS
        # -------------------------------
        status = status.upper()

        if status not in VALID_TRANSITIONS:
            raise ValueError("invalid status")

        # -------------------------------
        # FETCH JOB
        # -------------------------------
        job = jobs_collection.find_one({"_id": obj_id})

        if not job:
            raise ValueError("job not found")

        current_status = job.get("status", "QUEUED").upper()

        # -------------------------------
        # VALIDATE TRANSITION
        # -------------------------------
        allowed_next = VALID_TRANSITIONS.get(current_status, [])

        if status not in allowed_next:
            raise ValueError(
                f"invalid status transition: {current_status} → {status}"
            )

        # -------------------------------
        # PREPARE UPDATE
        # -------------------------------
        update_data = {
            "status": status,
            "updated_on": datetime.utcnow()
        }

        # -------------------------------
        # AUTO TIMESTAMPS
        # -------------------------------
        if status == "RUNNING" and not job.get("started_at"):
            update_data["started_at"] = datetime.utcnow()

        if status == "COMPLETED" and not job.get("finished_at"):
            update_data["finished_at"] = datetime.utcnow()

        # -------------------------------
        # UPDATE DB
        # -------------------------------
        result = jobs_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise ValueError("job not found")

        updated_job = jobs_collection.find_one({"_id": obj_id})

        return serialize_doc(updated_job)

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# GET ALL JOB IDS + STATUS
# -------------------------------
def get_jobs_summary_service():
    try:
        jobs = jobs_collection.find({}, {"_id": 1, "status": 1, "result": 1})

        return [
            {
                "id": str(job["_id"]),
                "status": job.get("status"),
                "result": job["result"] if "result" in job else None
            }
            for job in jobs
        ]

    except Exception as e:
        raise Exception(str(e))
    

# -------------------------------
# GET JOBS
# -------------------------------
def get_job_by_id_service(job_id=None):
    try:
        # -------------------------------
        # IF ID PROVIDED → SINGLE JOB
        # -------------------------------
        if job_id:
            try:
                obj_id = ObjectId(job_id)
            except:
                raise ValueError("invalid job id")

            job = jobs_collection.find_one({"_id": obj_id})

            if not job:
                raise ValueError("job not found")

            return serialize_doc(job)

        # -------------------------------
        # NO ID → RETURN ALL JOBS
        # -------------------------------
        jobs = list(jobs_collection.find())

        if not jobs:
            raise ValueError("no jobs found")

        return [serialize_doc(job) for job in jobs]

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))
    
    
VALID_TRANSITIONS = {
    "QUEUED": ["RUNNING"],
    "RUNNING": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": []
}


def update_job_status_service(job_id, status):
    try:
        obj_id = ObjectId(job_id)

        job = jobs_collection.find_one({"_id": obj_id})
        if not job:
            raise ValueError("job not found")

        current_status = job.get("status", "QUEUED").upper()
        new_status = status.upper()

        # -------------------------------
        # VALIDATE STATUS VALUE
        # -------------------------------
        if new_status not in VALID_TRANSITIONS:
            raise ValueError("invalid status")

        # -------------------------------
        # PREVENT SAME STATUS
        # -------------------------------
        if new_status == current_status:
            raise ValueError(f"job already in {new_status}")

        # -------------------------------
        # VALIDATE TRANSITION
        # -------------------------------
        allowed_next = VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next:
            raise ValueError(
                f"invalid transition: {current_status} → {new_status}"
            )

        # -------------------------------
        # UPDATE DATA
        # -------------------------------
        update_data = {
            "status": new_status,
            "updated_on": datetime.utcnow()
        }

        # timestamps
        if new_status == "RUNNING":
            update_data["started_at"] = datetime.utcnow()

        if new_status in ["COMPLETED", "FAILED"]:
            update_data["finished_at"] = datetime.utcnow()

        # -------------------------------
        # UPDATE DB
        # -------------------------------
        jobs_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        return serialize_doc(
            jobs_collection.find_one({"_id": obj_id})
        )

    except Exception as e:
        raise Exception(str(e))


def update_job_result_service(job_id, payload):
    try:
        obj_id = ObjectId(job_id)

        job = jobs_collection.find_one({"_id": obj_id})
        if not job:
            raise ValueError("job not found")

        status = job.get("status")
        results = payload.result

        formatted_results = []
        success_list = []

        # -------------------------------
        # FORMAT + COLLECT SUCCESS
        # -------------------------------
        for item in results:
            temp = {}

            for ip, value in item.items():
                temp[ip] = {
                    "success": value.success,
                    "message": value.message,
                    "error": value.error
                }
                success_list.append(value.success)

            formatted_results.append(temp)

        # -------------------------------
        # VALIDATE BASED ON EXISTING STATUS
        # -------------------------------
        if status == "COMPLETED":
            if not all(success_list):
                raise ValueError("COMPLETED requires all success = true")

        elif status == "FAILED":
            if any(success_list):
                raise ValueError("FAILED requires all success = false")

        elif status == "RUNNING":
            if not any(success_list) or all(success_list):
                raise ValueError(
                    "RUNNING requires at least one success=true and one success=false")

        elif status == "QUEUED":
            raise ValueError("cannot attach result for QUEUED job")

        else:
            raise ValueError("invalid job status")

        # -------------------------------
        # UPDATE RESULT
        # -------------------------------
        jobs_collection.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "result": formatted_results,
                    "updated_on": datetime.utcnow()
                }
            }
        )

        return serialize_doc(
            jobs_collection.find_one({"_id": obj_id})
        )

    except Exception as e:
        raise Exception(str(e))
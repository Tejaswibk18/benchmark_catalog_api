from bson import ObjectId
from datetime import datetime

from app.database.connection import jobs_collection
from app.services.benchmark_execution_service import serialize_doc


# -------------------------------
# UPDATE JOB STATUS
# -------------------------------
def update_job_status_service(job_id, status):
    try:
        try:
            obj_id = ObjectId(job_id)
        except:
            raise ValueError("invalid job id")

        valid_status = ["QUEUED", "RUNNING", "COMPLETED", "FAILED", "running" , "completed"]

        if status not in valid_status:
            raise ValueError("invalid status")

        update_data = {
            "status": status,
            "updated_on": datetime.utcnow()
        }

        # -------------------------------
        # AUTO TIMESTAMPS
        # -------------------------------
        if status == "RUNNING" or status == "running":
            update_data["started_at"] = datetime.utcnow()

        if status == "COMPLETED" or status == "completed":
            update_data["finished_at"] = datetime.utcnow()

        jobs_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        job = jobs_collection.find_one({"_id": obj_id})

        return serialize_doc(job)

    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(str(e))


# -------------------------------
# GET ALL JOB IDS + STATUS
# -------------------------------
def get_jobs_summary_service():
    try:
        jobs = jobs_collection.find({}, {"status": 1})

        return [
            {
                "id": str(job["_id"]),
                "status": job.get("status")
            }
            for job in jobs
        ]

    except Exception as e:
        raise Exception(str(e))
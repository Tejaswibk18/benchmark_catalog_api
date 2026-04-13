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

        # -------------------------------
        # VALIDATE STATUS (normalize)
        # -------------------------------
        status = status.upper()

        valid_status = {"QUEUED", "RUNNING", "COMPLETED", "FAILED"}

        if status not in valid_status:
            raise ValueError("invalid status")

        # -------------------------------
        # CHECK JOB EXISTS
        # -------------------------------
        job = jobs_collection.find_one({"_id": obj_id})

        if not job:
            raise ValueError("job not found")

        # -------------------------------
        # PREPARE UPDATE
        # -------------------------------
        update_data = {
            "status": status,
            "updated_on": datetime.utcnow()
        }

        # AUTO TIMESTAMPS (clean)
        if status == "RUNNING" and not job.get("started_at"):
            update_data["started_at"] = datetime.utcnow()

        if status == "COMPLETED" and not job.get("finished_at"):
            update_data["finished_at"] = datetime.utcnow()

        # -------------------------------
        # UPDATE
        # -------------------------------
        result = jobs_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise ValueError("job not found")

        # -------------------------------
        # RETURN UPDATED DOC
        # -------------------------------
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
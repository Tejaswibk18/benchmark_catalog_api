import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.database.connection import jobs_collection


LOG_FILE = "/mnt/c/Users/User/Desktop/code/benchmark_catalog_api/scheduler_log.txt"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")


def run_scheduler():
    try:
        log("\n=== SCHEDULER RUNNING ===")

        # -------------------------------
        # FIND QUEUED JOB
        # -------------------------------
        job = jobs_collection.find_one(
            {"status": "QUEUED"},
            sort=[("created_on", 1)]
        )

        if not job:
            log("No queued jobs found")
            return

        # -------------------------------
        # UPDATE TO RUNNING
        # -------------------------------
        jobs_collection.update_one(
            {"_id": job["_id"]},
            {
                "$set": {
                    "status": "RUNNING",
                    "started_at": datetime.utcnow(),
                    "updated_on": datetime.utcnow()
                }
            }
        )

        log(f"Job {job['_id']} → RUNNING")

    except Exception as e:
        log(f"Error: {str(e)}")


if __name__ == "__main__":
    run_scheduler()


import zipfile
import os
import json
from datetime import datetime
from app.database.connection import benchmark_results_collection
from app.utils.platform_profiler_validator import validate_platform_profile
from app.utils.helpers import serialize_doc


def process_platform_profiler_service(file):
    try:
        # -------------------------------
        # SAVE ZIP TEMP
        # -------------------------------
        upload_dir = "uploads"                                #upload
        os.makedirs(upload_dir, exist_ok=True)

        zip_path = os.path.join(upload_dir, file.filename)    #path

        with open(zip_path, "wb") as f:                       #save to disk
            f.write(file.file.read())

        # -------------------------------
        # EXTRACT ZIP
        # -------------------------------
        extract_path = zip_path.replace(".zip", "")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # -------------------------------
        # BENCHMARK NAME
        # -------------------------------
        benchmark_name = os.path.splitext(file.filename)[0]

        # -------------------------------
        # FILE PATHS
        # -------------------------------
        platform_json_path = os.path.join(
            extract_path, "platform_profiler", "platformprofile.json"
        )

        workload_html_path = os.path.join(
            extract_path, "workload_profile", "workloadprofile.html"
        )

        results_log_path = os.path.join(
            extract_path, "results", "results.log"
        )

        # -------------------------------
        # READ FILES
        # -------------------------------
        with open(platform_json_path) as f:
            platform_profile = json.load(f)

        validate_platform_profile(platform_profile)

        with open(results_log_path) as f:
            results_data = json.load(f)

        # -------------------------------
        # STORE IN DB
        # -------------------------------
        document = {
            "benchmark_name": benchmark_name,
            "platform_profile": platform_profile,
            "workload_profile_path": workload_html_path,
            "results": results_data,
            "created_on": datetime.utcnow()
        }

        # ONLY ONE INSERT
        result = benchmark_results_collection.insert_one(document)

        saved_doc = benchmark_results_collection.find_one({"_id": result.inserted_id})

        return serialize_doc(saved_doc)

    except Exception as e:
        raise Exception(str(e))
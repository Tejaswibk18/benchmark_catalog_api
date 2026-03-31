# import json
# import re
# from app.utils.groq_client import ask_ai



# def extract_json(response: str):
#     """
#     Extract JSON object from LLM response safely
#     """
#     response = response.replace("```json", "").replace("```", "").strip()

#     match = re.search(r"\{.*\}", response, re.DOTALL)

#     if match:
#         return match.group()

#     return response


# def safe_json_parse(response: str):
#     """
#     Parse JSON safely with auto-fix attempts
#     """

#     try:
#         return json.loads(response)
#     except json.JSONDecodeError:
#         pass

#     #  Fix common issues

#     # remove newlines inside strings
#     response = response.replace("\n", " ")

#     # fix trailing commas
#     response = re.sub(r",\s*}", "}", response)
#     response = re.sub(r",\s*]", "]", response)

#     # fix lowercase visibility
#     response = response.replace('"public"', '"Public"')

#     # fix unclosed quotes (best effort)
#     response = re.sub(r'(?<!\\)"\s*(?=[,}])', '"', response)

#     try:
#         return json.loads(response)
#     except:
#         return None


# def clean_suggestions(data):

#     suggestions = data.get("suggestions", [])
#     cleaned = []

#     for s in suggestions:
#         if isinstance(s, str):
#             s = s.replace('\\"', '"').strip()
#             cleaned.append(s)

#     data["suggestions"] = cleaned
#     return data


# # ---------------- NORMALIZER ---------------- #

# def normalize_payload(payload: dict):

#     # -------- REQUIRED FIELDS -------- #
#     payload["catalog_name"] = payload.get("catalog_name", "default_catalog")
#     payload["benchmark_name"] = payload.get("benchmark_name", "generated_benchmark")
#     payload["benchmark_category"] = payload.get("benchmark_category", "performance")
#     payload["description"] = payload.get("description", "Auto-generated benchmark")

#     # -------- scripts -------- #
#     scripts = payload.get("scripts", {})
#     payload["scripts"] = {
#         "sut_setup": scripts.get("sut_setup") or "sudo apt install nginx -y",
#         "sut_teardown": scripts.get("sut_teardown") or "sudo systemctl stop nginx"
#     }

#     # -------- metrics -------- #
#     metrics = payload.get("metrics", [])

#     if isinstance(metrics, list):
#         payload["metrics"] = [
#             str(m.get("name") if isinstance(m, dict) else m).lower()
#             for m in metrics if m
#         ] or ["latency", "throughput"]
#     else:
#         payload["metrics"] = ["latency", "throughput"]

#     # -------- visibility -------- #
#     payload["visibility"] = payload.get("visibility", "Public")

#     # -------- run_parameters -------- #
#     rp = payload.get("run_parameters", {})

#     payload["run_parameters"] = {
#         "threads": rp.get("threads", {
#             "data_type": "integer",
#             "value_type": "range",
#             "min": 1,
#             "max": 16,
#             "default": 8,
#             "description": "Number of threads"
#         }),
#         "connections": rp.get("connections", {
#             "data_type": "integer",
#             "value_type": "range",
#             "min": 1,
#             "max": 1000,
#             "default": 100,
#             "description": "Number of connections"
#         })
#     }

#     return payload


# # ---------------- VALIDATION ---------------- #

# def validate_benchmark(payload: dict):

#     prompt = f"""
# You are an expert benchmark configuration validator.

# Analyze the benchmark configuration below.

# Payload:
# {json.dumps(payload, indent=2)}

# Return STRICT JSON:

# {{
#   "suggestions": [
#     "text suggestion 1",
#     "text suggestion 2"
#   ]
# }}

# Rules:
# - ONLY plain strings
# - NO nested JSON
# - NO markdown
# """

#     response = ask_ai(prompt)

#     cleaned = extract_json(response)
#     parsed = safe_json_parse(cleaned)

#     if parsed:
#         parsed = clean_suggestions(parsed)

#         return {
#             "suggestions": parsed.get("suggestions", [])
#         }

#     return {
#         "suggestions": [],
#         "error": "AI response invalid",
#         "raw_response": cleaned
#     }


# # ---------------- GENERATE ---------------- #

# def generate_benchmark_from_text(user_prompt: str):

#     prompt = f"""
# Convert user instruction into VALID benchmark_catalog JSON.

# Instruction:
# {user_prompt}

# STRICT schema:
# - catalog_name
# - benchmark_name
# - benchmark_category
# - description
# - scripts (sut_setup, sut_teardown)
# - run_parameters (threads, connections)
# - metrics (list of strings)
# - visibility

# Rules:
# - Return ONLY JSON
# - NO explanation
# - NO markdown
# """

#     response = ask_ai(prompt)

#     cleaned = extract_json(response)
#     parsed = safe_json_parse(cleaned)

#     if not parsed:
#         return {
#             "errors": ["AI response invalid"],
#             "warnings": [],
#             "suggestions": [],
#             "raw_ai_response": cleaned
#         }

#     corrected = normalize_payload(parsed)

#     return {
#         "errors": [],
#         "warnings": [],
#         "suggestions": [],
#         "corrected_payload": corrected
#     }


# # ---------------- AUTO FIX ---------------- #

# def auto_fix_benchmark(payload: dict):

#     prompt = f"""
# Fix the benchmark payload strictly.

# Payload:
# {json.dumps(payload, indent=2)}

# Return STRICT JSON:

# {{
#   "errors": [],
#   "warnings": [],
#   "suggestions": [],
#   "corrected_payload": {{ VALID_SCHEMA_OBJECT }}
# }}

# Rules:
# - DO NOT change schema
# - DO NOT add fields
# - RETURN ONLY JSON
# """

#     response = ask_ai(prompt)

#     cleaned = extract_json(response)
#     parsed = safe_json_parse(cleaned)

#     if parsed:
#         corrected = normalize_payload(parsed.get("corrected_payload", {}))

#         return {
#             "errors": parsed.get("errors", []),
#             "warnings": parsed.get("warnings", []),
#             "suggestions": parsed.get("suggestions", []),
#             "corrected_payload": corrected
#         }

#     return {
#         "errors": ["AI could not fix payload"],
#         "warnings": [],
#         "suggestions": [],
#         "raw_ai_response": cleaned
#     }




# from groq import Groq
# import json
# import os
# import re
# from dotenv import load_dotenv

# # -------------------------------
# # LOAD ENV
# # -------------------------------
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# MODEL = os.getenv("AI_MODEL", "llama-3.1-8b-instant")

# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY not found in .env")

# client = Groq(api_key=GROQ_API_KEY)


# # -------------------------------
# # EXTRACT JSON
# # -------------------------------
# def extract_json(content: str):
#     content = re.sub(r"```json|```", "", content).strip()

#     start = content.find("{")
#     end = content.rfind("}")

#     if start == -1 or end == -1:
#         raise ValueError("No JSON found in AI response")

#     return json.loads(content[start:end + 1])


# # -------------------------------
# # NORMALIZE TEXT
# # -------------------------------
# def normalize_text(value: str):
#     if not isinstance(value, str):
#         return value

#     value = value.strip().replace(" ", "_")
#     value = re.sub(r"[^A-Za-z0-9_]", "", value)

#     return value


# # -------------------------------
# # FIX STRUCTURE (CRITICAL)
# # -------------------------------
# def normalize_keys(data: dict):

#     if not isinstance(data, dict):
#         return data

#     # flatten top-level if needed
#     if len(data) == 1:
#         key = list(data.keys())[0]
#         if isinstance(data[key], dict):
#             data = data[key]

#     fixed = {}

#     key_map = {
#         "name": "benchmark_name",
#         "benchmark": "benchmark_name",
#         "category": "benchmark_category",
#         "catalog": "catalog_name",
#         "group": "group_id",
#         "env": "environment"
#     }

#     for k, v in data.items():
#         new_key = k.lower().strip()

#         new_key = key_map.get(new_key, new_key)

#         if isinstance(v, dict):
#             v = normalize_keys(v)

#         fixed[new_key] = v

#     return fixed


# # -------------------------------
# # FORCE REQUIRED STRUCTURE
# # -------------------------------
# def enforce_required_fields(data: dict):

#     data.setdefault("benchmark_name", "default_benchmark")
#     data.setdefault("benchmark_category", "default_category")
#     data.setdefault("catalog_name", "default_catalog")
#     data.setdefault("group_id", "default_group")
#     data.setdefault("environment", "dev")

#     data.setdefault("schedule_test", {"test_name": "default_test"})

#     data.setdefault("schedule_details", {
#         "date": "2026-01-01T00:00:00Z",
#         "time": "2026-01-01T00:00:00Z",
#         "no_of_runs": 1,
#         "iteration_per_run": 1,
#         "cores_per_instance": 1
#     })

#     data.setdefault("no_of_sut", 1)

#     data.setdefault("workflow", {"stages": []})

#     data.setdefault("save_to_workflow_catalog", True)
#     data.setdefault("workflow_name", "default_workflow")
#     data.setdefault("workflow_visibility", "PRIVATE")

#     data.setdefault("custom_tags", ["default"])

#     return data


# # -------------------------------
# # FIX STAGES
# # -------------------------------
# def fix_stages(data: dict):

#     stages = data.get("workflow", {}).get("stages", [])

#     fixed_stages = []

#     for i, stage in enumerate(stages):

#         fixed_stage = {
#             "stage_type": normalize_text(stage.get("stage_type", f"stage_{i}")),
#             "stage_name": normalize_text(stage.get("stage_name", f"Stage_{i}")),
#             "stage_order": stage.get("stage_order", i + 1),

#             "task_type": normalize_text(stage.get("task_type", f"task_{i}")),
#             "task_name": normalize_text(stage.get("task_name", f"Task_{i}")),
#             "task_order": stage.get("task_order", i + 1),

#             "executor": stage.get("executor", {
#                 "type": "http_rest",
#                 "protocol": "https",
#                 "target": "agent",
#                 "timeout_sec": 60,
#                 "retry": 1
#             }),

#             "parameters": stage.get("parameters", {}),
#             "parameters_schema": stage.get("parameters_schema", {}),

#             "visibility": stage.get("visibility", ["UI"]),
#             "target_sut": stage.get("target_sut", ["sut1"])
#         }

#         if not isinstance(fixed_stage["target_sut"], list):
#             fixed_stage["target_sut"] = [str(fixed_stage["target_sut"])]

#         fixed_stages.append(fixed_stage)

#     data["workflow"]["stages"] = fixed_stages

#     return data


# # -------------------------------
# # MAIN FUNCTION
# # -------------------------------
# def generate_workflow_from_prompt(prompt: str):

#     system_prompt = """
# Generate STRICT JSON only.

# Rules:
# - No text, only JSON
# - All keys must be lowercase
# - Use underscore instead of spaces
# - Do NOT nest keys like "Benchmark": {}
# - Follow exact schema
# """

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.2
#     )

#     content = response.choices[0].message.content

#     try:
#         data = extract_json(content)

#         # 🔥 FULL FIX PIPELINE
#         data = normalize_keys(data)
#         data = enforce_required_fields(data)
#         data = fix_stages(data)

#         return data

#     except Exception as e:
#         raise ValueError(f"AI processing failed: {str(e)}")
    


    

    